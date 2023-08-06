def is_pending(hub, ret: dict, state: str = None) -> bool:
    """
    Default implementation of pending plugin
    Returns 'True' when the state is still 'pending' and reconciliation is required.

    If the state implements is_pending() call the state's implementation,
    otherwise state is pending until 'result' is 'True' and there are no 'changes'.

    :param hub: The hub
    :param ret: (dict) Returned structure of a run
    :param state: (Text, Optional) The name of the state
    :return: bool
    """

    if (
        state is not None
        and hub.states[state] is not None
        and callable(getattr(hub.states[state], "is_pending", None))
    ):
        return hub.states[state].is_pending(ret=ret)

    return not ret["result"] is True or bool(ret["changes"])
