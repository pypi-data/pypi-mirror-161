from typing import Any
from typing import Dict


async def sig_gather(hub, profile: Dict[str, Any]):
    """
    Get the metadata for the given profile.
    The profile contains the login information for a provider, similar to ctx.acct in idem states
    """
