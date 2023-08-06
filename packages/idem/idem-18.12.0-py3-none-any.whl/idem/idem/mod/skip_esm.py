from typing import Any
from typing import Dict


async def modify(hub, name: str, chunk: Dict[str, Any]) -> Dict[str, Any]:
    """
    Add the "skip_esm' flag from state to ctx
    """
    try:
        mod = getattr(hub, f"states.{chunk['state']}")

        if hasattr(mod, "SKIP_ESM"):
            chunk["ctx"]["skip_esm"] = True
    except AttributeError:
        ...

    return chunk
