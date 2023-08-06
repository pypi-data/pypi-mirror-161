from typing import Any
from typing import Dict
from typing import List


async def gather(
    hub,
    profile: Dict[str, Any],
    providers: List[str],
    hard_fail: bool = False,
):
    """
    Get the metadata for the given profile, which probably comes from an idem state's ctx.acct

    :param hub:
    :param profile: A dictionary containing login credentials for the provider
    :param providers: A list of providers that may be related to this sub
    :param hard_fail: Raise exceptions instead of catching them
    """
    for provider in providers:
        if provider in hub.acct.metadata:
            try:
                return await hub.acct.metadata[provider].gather(profile)
            except Exception as e:
                hub.log.error(
                    f"Error gathering metadata from {provider}: {e.__class__.__name__}: {e}"
                )
                if hard_fail:
                    raise
    else:
        for provider in providers:
            hub.log.debug(
                f"No metadata gather function found in 'hub.acct.metadata.{provider}.gather'"
            )
        return {}
