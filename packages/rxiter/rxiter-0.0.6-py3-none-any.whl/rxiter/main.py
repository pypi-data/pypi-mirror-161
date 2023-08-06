import functools
from typing import AsyncIterable, AsyncIterator, Callable, Union

from .tools import SharableAsyncIterable, ReplayAsyncIterable


def share(obj: Union(AsyncIterable, Callable)):
    """share can be applied to either an AsyncIterable or a Callable that returns an AsyncIterable.

    Args:
        obj (AsyncIterable | Callable): the object to share.

    Returns:
        SharableAsyncIterable: returns an SharableAsyncIterable or a Function that returns an AsyncIterable.
    """
    if callable(obj):
        return _async_share_dec(obj)
    elif hasattr(obj, "__aiter__"):
        return _async_share(obj)
    else:
        raise Exception("share can only be applied to an AsyncIterable object.")


def repeat(obj: Union(AsyncIterator, Callable)):
    """converts a AsyncIterator back into a AsyncIterable that will repeat the same pattern.

    Args:
        obj (AsyncIterator | Callable): the object to repeat.

    Returns:
        AsyncIterable: returns an async iterable that generates this async iterator.
    """
    if callable(obj):
        return _async_replay_dec(obj)
    elif hasattr(obj, "__anext__"):
        return _async_replay(obj)
    else:
        raise Exception("repeat can only be applied to an AsyncIterator object.")


def _async_share(async_iterable: AsyncIterable):
    return SharableAsyncIterable(async_iterable)


def _async_replay(async_iterator: AsyncIterable):
    return ReplayAsyncIterable(async_iterator)


def _async_share_dec(async_iterable_fn: Callable):
    @functools.wraps(async_iterable_fn)
    def wrapper(*args, **kwargs):
        obj = async_iterable_fn(*args, **kwargs)
        if not hasattr(obj, "__aiter__"):
            raise Exception("share can only be applied to an AsyncIterable object.")
        return SharableAsyncIterable(obj)
    return functools.lru_cache(maxsize = None)(wrapper)


def _async_replay_dec(async_iterator_fn: Callable):
    @functools.wraps(async_iterator_fn)
    def wrapper(*args, **kwargs):
        obj = async_iterator_fn(*args, **kwargs)
        if not hasattr(obj, "__anext__"):
            raise Exception("repeat can only be applied to an AsyncIterator object.")
        return ReplayAsyncIterable(obj)
    return functools.lru_cache(maxsize = None)(wrapper)
