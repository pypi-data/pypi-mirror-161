import asyncio


def post(hub, ctx):
    """
    Convert the dict return to an immutable namespace addressable format
    """
    ref = f"{ctx.ref}.{ctx.func.__name__}"
    kwargs = ctx.get_arguments()
    if asyncio.iscoroutine(ctx.ret):
        return hub.tool.idem.exec.format_async_return(
            ret=ctx.ret, ref=ref, kwargs=kwargs
        )
    else:
        return hub.tool.idem.exec.format_return(ret=ctx.ret, ref=ref, kwargs=kwargs)
