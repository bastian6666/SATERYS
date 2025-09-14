# saterys/core.py
from __future__ import annotations
from typing import Any, Dict, List
import asyncio
import io
import json
import contextlib

# Shape the response your UI expects
def _ok(output: Any = None, logs: List[str] | None = None, stdout: str | None = None) -> Dict[str, Any]:
    return {"ok": True, "output": output, "logs": logs or [], "stdout": stdout or ""}

def _err(msg: str) -> Dict[str, Any]:
    return {"ok": False, "error": msg, "logs": [], "stdout": ""}

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

async def run_node(*, node_id: str, type: str, args: Dict[str, Any], inputs: Dict[str, Any]) -> Dict[str, Any]:
    """
    Central runner used by both:
      - POST /run_node (manual runs)
      - scheduler (_call_run_node in scheduling.py)

    Return shape:
      { ok: bool, output: Any, logs?: [str], stdout?: str, error?: str }
    """
    try:
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

        # Unknown type
        return _err(f"Unknown node type: {type}")

    except Exception as e:
        return _err(f"runner exception: {e!s}")
