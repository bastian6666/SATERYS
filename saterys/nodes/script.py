NAME = "script"
DEFAULT_ARGS = {"code": "print('hello from script')"}

def run(args, inputs, context):
    code = args.get("code", "")
    import io, contextlib
    buf = io.StringIO()
    ns = {"inputs": inputs, "context": context}  # tiny “globals”
    with contextlib.redirect_stdout(buf):
        exec(code, ns, ns)
    out = buf.getvalue()
    # if user put a value into ns["result"], return it too
    return {"text": out.strip(), "result": ns.get("result")}
