import asyncio
import copy


def sig(hub, ctx, name, *args, **kwargs):
    ...


def pre(hub, ctx):
    """
    Before every state, fire an event with the ref and sanitized parameters
    """
    raw_kwargs = ctx.get_arguments()
    # Fire an event with kwargs without actually modifying kwargs
    # Copying the hub will cause a recursion error
    kwargs = {k: copy.copy(v) for k, v in raw_kwargs.items() if k != "hub"}
    name = kwargs.get("name", None)

    # Don't include credentials in the fired event
    kwargs.get("ctx", {}).pop("acct", None)
    acct_details = kwargs.get("ctx", {}).get("acct_details")
    # Remove 'states.' from the ref so that it looks like the sls file
    shortened_ref = ".".join(ctx.ref.split(".")[1:])

    # This state fires the event its own way
    # If there are any more exceptions we should find a more pluggable solution
    if ctx.ref.startswith("states.exec"):
        return

    hub.idem.event.put_nowait(
        profile="idem-state",
        body={name: {f"{shortened_ref}.{ctx.func.__name__}": kwargs}},
        tags={
            "ref": f"{ctx.ref}.{ctx.func.__name__}",
            "type": "state-pre",
            "acct_details": acct_details,
        },
    )


def post(hub, ctx):
    """
    Fire an event at the end of every state
    """
    kwargs = ctx.get_arguments()
    acct_details = kwargs.get("ctx", {}).get("acct_details")

    # This state fires the event its own way
    # If there are any more exceptions we should find a more pluggable solution
    if ctx.ref.startswith("states.exec"):
        return ctx.ret

    if asyncio.iscoroutine(ctx.ret):

        async def _return_coro():
            ret = await hub.pop.loop.unwrap(ctx.ret)
            await hub.idem.event.put(
                profile="idem-state",
                body=ret,
                tags={
                    "ref": f"{ctx.ref}",
                    "type": "state-post",
                    "acct_details": acct_details,
                },
            )
            return ret

        return _return_coro()
    else:
        hub.idem.event.put_nowait(
            body=ctx.ret,
            profile="idem-state",
            tags={
                "ref": f"{ctx.ref}.{ctx.func.__name__}",
                "type": "state-post",
                "acct_details": acct_details,
            },
        )
        return ctx.ret
