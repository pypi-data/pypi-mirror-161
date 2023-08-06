from typing import Any
from typing import Dict


async def gather(hub, profile: Dict[str, Any]):
    """
    Return the "account_id" key from the profile
    """
    return {"account_id": profile.get("account_id")}
