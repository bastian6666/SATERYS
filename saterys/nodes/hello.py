NAME = "hello"
DEFAULT_ARGS = {"name": "world"}

def run(args, inputs, context):
    name = str(args.get("name", "world"))
    return {"text": f"hello {name}"}
