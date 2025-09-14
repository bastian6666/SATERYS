# saterys/core.py
from __future__ import annotations
from typing import Any, Dict, List
import asyncio
import io
import json
import contextlib
import importlib, inspect, os, sys
from importlib.metadata import entry_points

# ------------------------
# Helpers: OK / ERR shape
# ------------------------
def _ok(output: Any = None, logs: List[str] | None = None, stdout: str | None = None) -> Dict[str, Any]:
    return {"ok": True, "output": output, "logs": logs or [], "stdout": stdout or ""}

def _err(msg: str) -> Dict[str, Any]:
    return {"ok": False, "error": msg, "logs": [], "stdout": ""}

# ------------------------
# Built-in: script runner
# ------------------------
async def _run_script(code: str, _args: Dict[str, Any], _inputs: Dict[str, Any]) -> Dict[str, Any]:
    """
    Executes Python code provided in args['code'].
    Exposes 'args' and 'inputs' in the script globals.
    If the script sets a variable named 'result', we return it as output.
    All prints are captured and returned as stdout.
    """
    stdout_buf = io.StringIO()

    def _exec():
        g = {"args": _args, "inputs": _inputs, "__name__": "__main__"}
        l: Dict[str, Any] = {}
        with contextlib.redirect_stdout(stdout_buf):
            exec(compile(code, "<node-script>", "exec"), g, l)
        # prefer explicit 'result' from locals, else from globals
        return l.get("result", g.get("result", None))

    try:
        result = await asyncio.to_thread(_exec)
        return _ok(output=result, stdout=stdout_buf.getvalue())
    except Exception as e:
        return _err(f"script error: {e!s}")

# -----------------------------------
# Dynamic loader for external nodes
# -----------------------------------
# Optional: allow external plugin dirs; separate using os.pathsep
#   export SATERYS_NODE_PATH=/abs/path/to/my_nodes:/another/path
_PLUGIN_DIRS = [p for p in (os.environ.get("SATERYS_NODE_PATH") or "").split(os.pathsep) if p]

def _load_node_module(node_type: str):
    """
    Resolve a node type string to a Python module exposing `run(args, inputs, context)`.
    Resolution order:
      1) Fully-qualified module path (as-is)
      2) saterys.nodes.<node_type>
      3) saterys.nodes.<node_type with '.' replaced by '_'>
      4) External plugin dirs (SATERYS_NODE_PATH) trying node_type and dot→underscore
      5) Entry points group 'saterys_nodes' (name == node_type)
    """
    candidates = [
        node_type,
        f"saterys.nodes.{node_type}",
        f"saterys.nodes.{node_type.replace('.', '_')}",
    ]

    # 1–3: direct import attempts
    for modname in candidates:
        try:
            return importlib.import_module(modname)
        except Exception:
            pass

    # 4: search in plugin dirs
    for d in _PLUGIN_DIRS:
        if d and os.path.isdir(d):
            added = False
            if d not in sys.path:
                sys.path.insert(0, d)
                added = True
            try:
                for modname in (node_type, node_type.replace('.', '_')):
                    try:
                        return importlib.import_module(modname)
                    except Exception:
                        pass
            finally:
                if added:
                    try:
                        sys.path.remove(d)
                    except ValueError:
                        pass

    # 5: pkg entry points
    try:
        for ep in entry_points(group="saterys_nodes"):
            if ep.name == node_type:
                return ep.load()
    except Exception:
        pass

    raise KeyError(f"Unknown node type: {node_type!r}")

def _coerce_result(res: Any, stdout_text: str = "") -> Dict[str, Any]:
    """
    Normalize various node returns to the UI shape.
    - If dict with 'ok' provided by the node, pass it through (ensure stdout field).
    - Else wrap as ok/output.
    """
    if isinstance(res, dict) and "ok" in res:
        if "stdout" not in res:
            res = {**res, "stdout": stdout_text}
        return res
    return _ok(output=res, stdout=stdout_text)

async def _run_dynamic(type: str, args: Dict[str, Any], inputs: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
    mod = _load_node_module(type)
    fn = getattr(mod, "run", None)
    if not callable(fn):
        raise RuntimeError(f"Node '{type}' has no callable run(args, inputs, context)")

    stdout_buf = io.StringIO()
    if inspect.iscoroutinefunction(fn):
        with contextlib.redirect_stdout(stdout_buf):
            res = await fn(args or {}, inputs or {}, context)
        return _coerce_result(res, stdout_buf.getvalue())

    # sync function — run in thread, still capture prints
    def _call():
        with contextlib.redirect_stdout(stdout_buf):
            return fn(args or {}, inputs or {}, context)

    res = await asyncio.to_thread(_call)
    return _coerce_result(res, stdout_buf.getvalue())

# ------------------------------
# Central runner (API/Scheduler)
# ------------------------------
async def run_node(*, node_id: str, type: str, args: Dict[str, Any], inputs: Dict[str, Any]) -> Dict[str, Any]:
    """
    Central runner used by both:
      - POST /run_node (manual runs)
      - scheduler (_call_run_node in scheduling.py)

    Return shape:
      { ok: bool, output: Any, logs?: [str], stdout?: str, error?: str }
    """
    try:
        # ---- Built-in nodes ----
        if type == "hello":
            name = str(args.get("name", "world"))
            return _ok({"text": f"Hello {name}"})

        if type == "sum":
            nums = args.get("nums", [])
            if not isinstance(nums, list):
                return _err("sum.nums must be a list")
            try:
                total = sum(float(x) for x in nums)
            except Exception:
                return _err("sum.nums must be numbers")
            return _ok(total)

        if type == "script":
            code = str(args.get("code", ""))
            return await _run_script(code, args, inputs)

        if type == "raster.input":
            # Minimal output so your map preview can find .type and .path
            path = args.get("path") or ""
            if not isinstance(path, str) or not path:
                return _err("raster.input requires args.path")
            return _ok({"type": "raster", "path": path})

        # ---- Dynamic / external nodes ----
        context = {"node_id": node_id, "type": type}
        return await _run_dynamic(type, args, inputs, context)

    except KeyError as e:
        # unknown dynamic node
        return _err(str(e))

    except Exception as e:
        return _err(f"runner exception: {e!s}")
