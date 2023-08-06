from typing import Any
from typing import Dict
from typing import List
from typing import Tuple


SKIP_ESM = True


async def run(
    hub,
    ctx,
    name: str,
    *,
    path: str = None,
    acct_profile: str,
    acct_data=None,
    args: List[Any] = None,
    kwargs: Dict[str, Any] = None,
):
    """
    Call an exec module by path reference

    Args:
        hub:
        ctx:
        name(Text): The name of the state or the exec module reference path
        path(Text): The exec module reference path to call
        acct_profile(Text): The acct profile to use on the exec module call
        acct_data(Dict): The acct_data to use with the exec module call
        args(List): A list of args to pass to the exec module
        kwargs(Dict): The keyword arguments to pass to the exec module

    Returns:
        {"result": True|False, "comment": ["A message"], "new_state": The return from the exec module}


    .. code-block:: yaml

        exec_func:
          exec.run:
            - path: test.ping
            - acct_profile: default
            - args:
              - arg1
              - arg2
              - arg3
            - kwargs:
                kwarg_1: val_1
                kwarg_2: val_2
                kwarg_3: val_3
    """
    result = dict(comment=[], new_state=None, old_state=None, name=name, result=True)

    # Get defaults for each argument
    if path is None:
        path = name
    if args is None:
        args = []
    if kwargs is None:
        kwargs = {}

    func_ctx = await hub.idem.acct.ctx(
        path,
        acct_profile=acct_profile,
        acct_data=acct_data,
    )

    # Other states have acct_data consumed already, but exec.run passes it forward to the exec module
    # ctx and ctx.acct have not been created yet from acct_data for the exec module.
    # At this point it is "acct_data" that needs to be removed rather than ctx or ctx.acct
    sanitized_kwargs = {k: v for k, v in kwargs.items() if k != "acct_data"}
    await hub.idem.event.put(
        profile="idem-state",
        body={name: {path: sanitized_kwargs}},
        tags={
            "ref": f"exec.{path}",
            "type": "state-pre",
            "acct_details": func_ctx.acct_details,
        },
    )

    # Report the cli command of the exec module being called
    cli_call = f"idem exec {path} --acct-profile={acct_profile}"
    if args:
        cli_call += " " + " ".join(args)
    if kwargs:
        cli_call += " " + " ".join(f"{k}={v}" for k, v in kwargs.items())

    result["comment"] += [cli_call]

    # Get the acct_data from the current run
    acct_data = acct_data or hub.idem.RUNS[ctx.run_name]["acct_data"]

    # Run the exec module!
    try:
        ret = await hub.idem.ex.run(
            path=path,
            args=args,
            kwargs=kwargs,
            acct_data=acct_data,
            acct_profile=acct_profile,
        )
        result["result"] &= ret.result
        result["new_state"] = ret.ret
        # Avoid ESM by reporting changes directly
        result["changes"] = {"new": ret.ret}
        if ret.comment:
            if isinstance(ret.comment, List):
                result["comment"] += ret.comment
            elif isinstance(ret.comment, Tuple):
                result["comment"] += list(ret.comment)
            else:
                result["comment"].append(ret.comment)
    except Exception as e:
        # Float up the errors
        result["result"] = False
        result["comment"] += [f"{e.__class__.__name__}: {e}"]

    # Fire an event using the exec module's path instead of the exec.run
    await hub.idem.event.put(
        profile="idem-state",
        body=result,
        tags={
            "ref": f"exec.{path}",
            "type": "state-post",
            "acct_details": func_ctx.acct_details,
        },
    )
    return result


def is_pending(hub, ret):
    """
    Pending implementation of exec.run
    Pending if the 'result' is False.

    :return: True if reconciliation is required. If result is True do not reconcile.
    """
    return not ret["result"]
