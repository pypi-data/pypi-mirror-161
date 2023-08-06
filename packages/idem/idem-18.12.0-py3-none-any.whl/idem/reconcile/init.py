from typing import Any
from typing import Dict


async def run(
    hub,
    plugin: str = "basic",
    pending_plugin: str = "default",
    name: str = None,
    apply_kwargs: Dict[str, Any] = None,
):
    if apply_kwargs is None:
        apply_kwargs = {}
    apply_kwargs["name"] = name
    try:
        ret = await hub.reconcile[plugin].loop(
            pending_plugin,
            name=name,
            apply_kwargs=apply_kwargs,
        )
    finally:
        hub.idem.state.update_status(name, hub.idem.state.Status.FINISHED)

    return ret
