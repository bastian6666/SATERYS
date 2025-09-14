# saterys/core.py
from __future__ import annotations
from typing import Any, Dict, List, Optional, Callable
import asyncio
import io
import json
import contextlib
import importlib
import os
import sys
from pathlib import Path

# ---- helpers to shape responses your UI expects ----
def _ok(output: Any = None, logs: List[str] | None = None, stdout: str | None = None) -> Dict[str, Any]:
    return {"ok": True, "output": output, "logs": logs or [], "stdout": stdout or ""}

def _err(msg: str) -> Dict[str, Any]:
    return {"ok": False, "error": msg, "logs": [], "stdout": ""}

# ---- built-ins (hello / sum / script / raster.input) ----
async def _run_script(code: str, _args: Dict[str, Any], _inputs: Dict[str, Any]) -> Dict[str, Any]:
    stdout_buf = io.StringIO()

    def _exec():
        g = {"args": _args, "inputs": _inputs, "__name__": "__main__"}
        l: Dict[str, Any] = {}
        with contextlib.redirect_stdout(stdout_buf):
            exec(compile(code, "<node-script>", "exec"), g, l)
        return l.get("result", g.get("result", None))

    try:
        result = await asyncio.to_thread(_exec)
        return _ok(output=result, stdout=stdout_buf.getvalue())
    except Exception as e:
        return _err(f"script error: {e!s}")

# ---- dynamic node loader (so 'manual_labeler' works) ----
_ALIASES = {
    # short name -> real module path
    "manual_labeler": "saterys.nodes.raster.manual_labeler",
    # add more aliases here if you like
}

def _import_run_callable(type_name: str) -> Optional[Callable[[Dict[str, Any], Dict[str, Any], Dict[str, Any]], Any]]:
    """
    Try to resolve a node's `run(args, inputs, context)` function by type string.
    Resolution order:
      1) alias mapping (e.g., 'manual_labeler' -> 'saterys.nodes.raster.manual_labeler')
      2) import as typed:              import <type_name>
      3) under saterys.nodes.:         import saterys.nodes.<type_name>
      4) fallback with underscores:    import saterys.nodes.<type_name.replace('.', '_')>
      5) search SATERYS_NODE_PATH for a module file and load it
    """
    candidates: List[str] = []
    if type_name in _ALIASES:
        candidates.append(_ALIASES[type_name])

    # typed module (if user supplies a dotted path)
    candidates.append(type_name)

    # saterys.nodes.<type>
    candidates.append(f"saterys.nodes.{type_name}")

    # saterys.nodes.<type_with_underscores>
    if "." in type_name:
        candidates.append(f"saterys.nodes.{type_name.replace('.', '_')}")

    # try importing module candidates
    for modname in candidates:
        try:
            mod = importlib.import_module(modname)
            if hasattr(mod, "run"):
                return getattr(mod, "run")
        except Exception:
            pass

    # search external node paths (raw files)
    node_paths = os.environ.get("SATERYS_NODE_PATH", "")
    if node_paths:
        for base in node_paths.split(os.pathsep):
            base_path = Path(base).expanduser()
            if not base_path.exists():
                continue
            # try file like "<base>/<type_name>.py" or respect dotted path
            rel = Path(*type_name.split("."))  # e.g. "raster/manual_labeler.py"
            for cand in (base_path / (type_name + ".py"), base_path / rel.with_suffix(".py")):
                if cand.exists():
                    spec = importlib.util.spec_from_file_location(f"extnode__{type_name.replace('.','_')}", cand)
                    if spec and spec.loader:
                        mod = importlib.util.module_from_spec(spec)
                        sys.modules[spec.name] = mod
                        spec.loader.exec_module(mod)  # type: ignore[attr-defined]
                        if hasattr(mod, "run"):
                            return getattr(mod, "run")

    return None

# ---- central runner used by REST + scheduler ----
async def run_node(*, node_id: str, type: str, args: Dict[str, Any], inputs: Dict[str, Any]) -> Dict[str, Any]:
    """
    Return shape:
      { ok: bool, output: Any, logs?: [str], stdout?: str, error?: str }
    """
    try:
        # built-ins first
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
            path = args.get("path") or ""
            if not isinstance(path, str) or not path:
                return _err("raster.input requires args.path")
            return _ok({"type": "raster", "path": path})

        # dynamic plug-ins (e.g., 'manual_labeler' or 'raster.manual_labeler')
        run_callable = _import_run_callable(type)
        if run_callable:
            # optional: capture prints from plugin run
            stdout_buf = io.StringIO()
            def _call():
                with contextlib.redirect_stdout(stdout_buf):
                    return run_callable(args, inputs, {"node_id": node_id, "type": type})
            try:
                result = await asyncio.to_thread(_call)
            except Exception as e:
                return _err(f"runner exception: {e!s}")

            # if plugin returned a plain value, wrap it; if it returned dict with ok, pass-through
            if isinstance(result, dict) and ("ok" in result):
                # ensure stdout surfaced too
                if stdout_buf.tell():
                    result = {**result, "stdout": result.get("stdout", "") + stdout_buf.getvalue()}
                return result
            else:
                return _ok(output=result, stdout=stdout_buf.getvalue())

        # Unknown type
        return _err(f"Unknown node type: {type!r}")

    except Exception as e:
        return _err(f"runner exception: {e!s}")
