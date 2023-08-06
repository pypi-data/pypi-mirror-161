import re


async def resolve(hub, arg_bind: str):
    """
    Parse arg_bind template ${cloud:state:attribute} and resolve the arg-bind template into a value
    using the hub's RUNNING data.
    """

    if arg_bind:
        result = re.search(r"\${([^${}]*)}", arg_bind)
        arg_bind_expr = result.group(1)

    resolved_data = None

    if arg_bind_expr:

        (
            resolved_data,
            is_data_available,
        ) = await hub.tool.idem.arg_bind_utils.find_arg_reference_data(arg_bind_expr)

        if not is_data_available:
            raise ValueError(
                f"Arg_bind template '{arg_bind}' could not be resolved to any value"
            )

    return resolved_data
