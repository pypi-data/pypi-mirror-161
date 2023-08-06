from typing import Iterable

from tqdm.auto import tqdm


def create(hub, iterable: Iterable, **kwargs) -> Iterable:
    """
    Create a tqdm progress bar that updates as the iterable is iterated
    """
    progress_bar = tqdm(
        iterable,
        **kwargs,
    )

    return progress_bar


def update(hub, progress_bar: Iterable, **kwargs):
    progress_bar.update(**kwargs)
    progress_bar.refresh()
