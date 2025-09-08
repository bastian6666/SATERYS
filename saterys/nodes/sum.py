NAME = "sum"
DEFAULT_ARGS = {"nums": [1, 2, 3]}

def run(args, inputs, context):
    nums = args.get("nums", [])
    total = sum(float(x) for x in nums)
    return {"text": str(total), "value": total}
