from typing import Any
from typing import Awaitable
from typing import Dict

from idem.exec.init import ExecReturn


def format_return(hub, ret, ref: str, kwargs: Dict[str, Any]) -> ExecReturn:
    """
    Format the return of an exec module to be an ExecReturn class

    :param hub:
    :param ret: The data returned from the exec module
    :param ref: The reference to the exec module function on the hub
    :param kwargs: The arguments that were passed to the exec module
    """
    if isinstance(ret, ExecReturn):
        return ret

    # Get the acct metadata from ctx if it exists
    acct_details = None
    ctx = kwargs.get("ctx", {})
    if isinstance(ctx, dict):
        acct_details = ctx.get("acct_details")

    # Publish an event with the return data from the function
    hub.idem.event.put_nowait(
        body=ret,
        profile="idem-exec",
        tags={"ref": ref, "type": "exec-post", "acct_details": acct_details},
    )

    try:
        return ExecReturn(
            **ret,
            ref=ref,
        )
    except TypeError:
        raise TypeError(
            f"Exec module '{ref}' did not return a dictionary: "
            "\n{'result': True|False, 'comment': Any, 'ret': Any}"
        )


async def format_async_return(
    hub, ret: Awaitable, ref: str, kwargs: Dict[str, Any]
) -> ExecReturn:
    """
    Format the return of an async exec module to be an ExecReturn class.

    :param hub:
    :param ret: The data returned from the exec module
    :param ref: The reference to the exec module function on the hub
    :param kwargs: The arguments that were passed to the exec module
    """
    ret = await hub.pop.loop.unwrap(ret)
    return hub.tool.idem.exec.format_return(ret=ret, ref=ref, kwargs=kwargs)
