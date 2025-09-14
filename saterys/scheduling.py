# scheduling.py
from __future__ import annotations

"""
SATERYS – Pipeline Scheduling

- Persists jobs in SQLite via APScheduler's SQLAlchemyJobStore
- Executes the active graph in topological order
- Uses the SAME /run_node HTTP endpoint that the UI uses, so any custom node
  resolvable by SATERYS (e.g., files under ./nodes) also works when scheduled.
- Simple in-memory run history with logs for recent runs per job.

Env:
  SATERYS_API_BASE  (default: http://127.0.0.1:8000)
    Set this if your API is served on another host/port or under a prefix,
    e.g. http://127.0.0.1:8000/api
"""

import os
import asyncio
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Literal, Callable, Awaitable
from collections import defaultdict, deque
from uuid import uuid4

import httpx
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.triggers.date import DateTrigger
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.cron import CronTrigger


# --------------------------------------------------------------------
# Scheduler (global, persisted jobs, UTC)
# --------------------------------------------------------------------
jobstores = {"default": SQLAlchemyJobStore(url="sqlite:///./saterys_jobs.sqlite")}
scheduler = AsyncIOScheduler(jobstores=jobstores, timezone="UTC")


# --------------------------------------------------------------------
# Models (pipeline graph + scheduling payloads)
# --------------------------------------------------------------------
class PNode(BaseModel):
    id: str
    type: str
    args: Dict[str, Any] = Field(default_factory=dict)


class PEdge(BaseModel):
    source: str
    target: str


class Graph(BaseModel):
    nodes: List[PNode]
    edges: List[PEdge]


class PipelineScheduleCreate(BaseModel):
    mode: Literal["once", "interval", "cron"]
    # when
    run_at: Optional[datetime] = None          # for "once" (UTC)
    seconds: Optional[int] = None              # for "interval"
    minutes: Optional[int] = None
    hours: Optional[int] = None
    cron: Optional[str] = None                 # for "cron" (standard 5-field OK)
    # what
    graph: Graph


class ScheduleOut(BaseModel):
    id: str
    next_run_time: Optional[datetime] = None


# --------------------------------------------------------------------
# Run history (in-memory ring per job)
# --------------------------------------------------------------------
class RunStatus(str, Enum):
    running = "running"
    success = "success"
    error = "error"


class RunSummary(BaseModel):
    id: str
    job_id: str
    started_at: datetime
    finished_at: Optional[datetime] = None
    status: RunStatus


class RunDetail(RunSummary):
    logs: List[str] = Field(default_factory=list)


# newest-first ring buffer (per job), and a map of run_id -> run
_RUNS: Dict[str, RunDetail] = {}
_RUNS_BY_JOB: Dict[str, deque[str]] = defaultdict(lambda: deque(maxlen=50))
_RUNS_LOCK = asyncio.Lock()


async def _new_run(job_id: str) -> RunDetail:
    rec = RunDetail(
        id=uuid4().hex,
        job_id=job_id,
        started_at=datetime.utcnow(),
        status=RunStatus.running,
        logs=[],
    )
    async with _RUNS_LOCK:
        _RUNS[rec.id] = rec
        _RUNS_BY_JOB[job_id].appendleft(rec.id)
    return rec


async def _append(rec: RunDetail, msg: str):
    async with _RUNS_LOCK:
        rec.logs.append(msg)


async def _finish(rec: RunDetail, ok: bool):
    async with _RUNS_LOCK:
        rec.status = RunStatus.success if ok else RunStatus.error
        rec.finished_at = datetime.utcnow()


# --------------------------------------------------------------------
# Graph execution
# --------------------------------------------------------------------
def _toposort(nodes: List[PNode], edges: List[PEdge]) -> List[str]:
    ids = [n.id for n in nodes]
    idset = set(ids)
    adj = {i: [] for i in ids}
    indeg = {i: 0 for i in ids}
    for e in edges:
        if e.source in idset and e.target in idset and e.source != e.target:
            adj[e.source].append(e.target)
            indeg[e.target] += 1
    q = [i for i in ids if indeg[i] == 0]
    order: List[str] = []
    while q:
        u = q.pop(0)
        order.append(u)
        for v in adj[u]:
            indeg[v] -= 1
            if indeg[v] == 0:
                q.append(v)
    # If there is a cycle, 'order' will be partial; we just run what we can.
    return order


# --------------------------------------------------------------------
# Call the same /run_node endpoint the UI uses (supports custom nodes)
# --------------------------------------------------------------------
_API_BASE = os.environ.get("SATERYS_API_BASE", "http://127.0.0.1:8000")

async def _call_run_node(
    node_id: str, node_type: str, args: Dict[str, Any], inputs: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Use internal HTTP to POST /run_node so the exact same resolver is used
    (including dynamic nodes from ./nodes).
    """
    payload = {
        "nodeId": node_id,
        "type": node_type,
        "args": args or {},
        "inputs": inputs or {},
    }
    async with httpx.AsyncClient(base_url=_API_BASE, timeout=120.0) as client:
        r = await client.post("/run_node", json=payload)
        if r.status_code == 404:
            raise RuntimeError(
                "POST /run_node returned 404. If your API is served on another base "
                "path/port, set SATERYS_API_BASE, e.g. 'http://127.0.0.1:8000' or "
                "'http://127.0.0.1:8000/api'."
            )
        r.raise_for_status()
        return r.json()


async def _run_pipeline_graph(
    graph: Graph,
    log: Optional[Callable[[str], Awaitable[None]]] = None
) -> None:
    async def L(msg: str):
        if log:
            try:
                await log(msg)
            except Exception:
                pass

    order = _toposort(graph.nodes, graph.edges)
    node_by_id = {n.id: n for n in graph.nodes}
    last_outputs: Dict[str, Any] = {}
    upstream_of: Dict[str, List[str]] = {}
    for e in graph.edges:
        upstream_of.setdefault(e.target, []).append(e.source)

    await L(f"Pipeline: {len(graph.nodes)} nodes, {len(graph.edges)} edges")

    for nid in order:
        n = node_by_id[nid]
        inputs = {up: last_outputs.get(up) for up in upstream_of.get(nid, [])}
        await L(f"[{nid}] ▶ Running…")
        try:
            res = await _call_run_node(n.id, n.type, n.args, inputs)

            # Attach any logs/stdout if your runner returns them
            if isinstance(res, dict):
                for line in (res.get("logs") or []):
                    await L(f"[{nid}] {str(line)}")
                if isinstance(res.get("stdout"), str):
                    for line in res["stdout"].splitlines():
                        if line.strip():
                            await L(f"[{nid}] {line}")

            if res and res.get("ok"):
                out = res.get("output")
                preview = (
                    out if isinstance(out, (str, int, float))
                    else (out.get("text") if isinstance(out, dict) else None)
                )
                await L(f"[{nid}] ✅ {preview!s}" if preview is not None else f"[{nid}] ✅")
                last_outputs[nid] = out
            else:
                err = res.get("error", "Unknown error") if isinstance(res, dict) else "Unknown error"
                await L(f"[{nid}] ❌ {err}")
        except Exception as e:
            await L(f"[{nid}] ❌ Exception: {e!s}")


async def _run_pipeline_job(graph: Graph, job_id: str):
    """
    Wrapper that records a run + logs while executing the graph.
    """
    rec = await _new_run(job_id)
    await _append(rec, "▶ Pipeline started")
    ok = True
    try:
        await _run_pipeline_graph(graph, log=lambda m: _append(rec, m))
    except Exception as e:
        ok = False
        await _append(rec, f"❌ Top-level exception: {e!s}")
    await _finish(rec, ok)


# --------------------------------------------------------------------
# Trigger builder
# --------------------------------------------------------------------
def _trigger_from(s: PipelineScheduleCreate):
    if s.mode == "once":
        if not s.run_at:
            raise HTTPException(400, "run_at (UTC) required for 'once'")
        return DateTrigger(run_date=s.run_at)
    if s.mode == "interval":
        if not any([s.seconds, s.minutes, s.hours]):
            raise HTTPException(400, "interval requires seconds/minutes/hours")
        return IntervalTrigger(
            seconds=s.seconds or 0,
            minutes=s.minutes or 0,
            hours=s.hours or 0,
        )
    if s.mode == "cron":
        if not s.cron:
            raise HTTPException(400, "cron expression required for 'cron'")
        return CronTrigger.from_crontab(s.cron)
    raise HTTPException(400, "unknown mode")


# --------------------------------------------------------------------
# API Router
# --------------------------------------------------------------------
pipeline_router = APIRouter(prefix="/pipeline/schedules", tags=["schedules"])


@pipeline_router.post("", response_model=ScheduleOut)
def create_pipeline_schedule(s: PipelineScheduleCreate):
    trig = _trigger_from(s)
    # Schedule wrapper first with placeholder job_id, then update to real one
    job = scheduler.add_job(
        _run_pipeline_job,
        trigger=trig,
        kwargs=dict(graph=s.graph, job_id="PENDING"),
        jobstore="default",
        coalesce=True,
        max_instances=1,
        misfire_grace_time=300,
    )
    # Let the job know its own id for run recording
    job.modify(kwargs={**job.kwargs, "job_id": job.id})
    return ScheduleOut(id=job.id, next_run_time=job.next_run_time)


@pipeline_router.get("", response_model=List[ScheduleOut])
def list_pipeline_schedules():
    jobs = [j for j in scheduler.get_jobs() if getattr(j, "func", None) == _run_pipeline_job]
    return [ScheduleOut(id=j.id, next_run_time=j.next_run_time) for j in jobs]


@pipeline_router.delete("/{job_id}")
def delete_pipeline_schedule(job_id: str):
    if not scheduler.get_job(job_id):
        raise HTTPException(404, "job not found")
    scheduler.remove_job(job_id)
    return {"ok": True}


@pipeline_router.post("/{job_id}/pause")
def pause_pipeline_schedule(job_id: str):
    if not scheduler.get_job(job_id):
        raise HTTPException(404, "job not found")
    scheduler.pause_job(job_id)
    return {"ok": True}


@pipeline_router.post("/{job_id}/resume")
def resume_pipeline_schedule(job_id: str):
    if not scheduler.get_job(job_id):
        raise HTTPException(404, "job not found")
    scheduler.resume_job(job_id)
    return {"ok": True}


@pipeline_router.post("/{job_id}/run-now")
async def run_pipeline_now(job_id: str):
    job = scheduler.get_job(job_id)
    if not job:
        raise HTTPException(404, "job not found")
    # Fire immediately (non-blocking), preserving the scheduled next_run_time
    asyncio.create_task(job.func(**job.kwargs))
    return {"ok": True}


# -----------------------------
# Run history / log endpoints
# -----------------------------
@pipeline_router.get("/{job_id}/runs", response_model=List[RunSummary])
def list_runs(job_id: str):
    ids = list(_RUNS_BY_JOB.get(job_id, []))
    out: List[RunSummary] = []
    for rid in ids:
        r = _RUNS.get(rid)
        if r:
            out.append(
                RunSummary(
                    id=r.id,
                    job_id=r.job_id,
                    started_at=r.started_at,
                    finished_at=r.finished_at,
                    status=r.status,
                )
            )
    return out  # newest first


@pipeline_router.get("/runs/{run_id}", response_model=RunDetail)
def get_run(run_id: str):
    r = _RUNS.get(run_id)
    if not r:
        raise HTTPException(404, "run not found")
    return r


# Back-compat export name if your app used `from .scheduling import router`
router = pipeline_router
__all__ = ["scheduler", "pipeline_router", "router"]
