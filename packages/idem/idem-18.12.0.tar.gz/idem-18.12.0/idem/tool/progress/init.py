import copy
from typing import Iterable


def create(hub, iterable: Iterable, **kwargs) -> Iterable:
    """
    Create a progress bar that updates as the iterable is iterated.
    """
    # Only show this progress bar if the "--progress" flag was set
    enabled = hub.OPT.get("idem", {}).get("progress", False)
    if not enabled:
        return iterable

    progress_plugin = hub.OPT.get("idem", {}).get("progress_plugin", "tqdm")

    # Add other options to the progress bar from config
    opts = copy.copy(hub.OPT.get("idem", {}).get("progress_options", {}))

    # Merge config options with explicitly passed options
    opts.update(kwargs)

    progress_bar = hub.tool.progress[progress_plugin].create(
        iterable,
        **opts,
    )

    return progress_bar


def update(hub, progress_bar: Iterable, **kwargs):
    """
    Update the progress bar through the progress plugin
    """
    # Only show this progress bar if the "--progress" flag was set
    enabled = hub.OPT.get("idem", {}).get("progress", False)
    if not enabled:
        return

    progress_plugin = hub.OPT.get("idem", {}).get("progress_plugin", "tqdm")

    hub.tool.progress[progress_plugin].update(
        progress_bar,
        **kwargs,
    )
