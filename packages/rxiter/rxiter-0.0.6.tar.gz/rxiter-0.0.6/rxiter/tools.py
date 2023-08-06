import weakref
from asyncio import Event
from queue import Queue
import functools

class SharableAsyncIterable:

    def __init__(self, async_iterable):
        self._async_iterable = async_iterable
        self._async_iterator = None
        self._weak_ref_child_iterators = []
        self._noone_broadcasting = Event()
        self._noone_broadcasting.set()

    async def _broadcast(self):
        value = await self._async_iterator.__anext__()
        for ref in list(self._weak_ref_child_iterators):
            child = ref()
            if child is None:
                self._weak_ref_child_iterators.remove(ref)
            else:
                child._queue.put(value)

    def __aclose__(self):
        print("what do you know")


    def __aiter__(self):

        class _SharableAsyncIterator:

            def __init__(self, parent):
                self._parent = parent
                self._queue = Queue()

            def __aclose__(self):
                print("another what do you know")

            async def __anext__(self):
                if not self._queue.empty():
                    return self._queue.get()
                else:
                    if self._parent._noone_broadcasting.is_set():
                        self._parent._noone_broadcasting.clear()
                        await self._parent._broadcast()
                        self._parent._noone_broadcasting.set()
                    else:
                        await self._parent._noone_broadcasting.wait()
                    return self._queue.get()

        shar_iter = _SharableAsyncIterator(self)
        weak_ref_ret = weakref.ref(shar_iter)
        if not self._weak_ref_child_iterators:
            self._async_iterator = self._async_iterable.__aiter__()
        self._weak_ref_child_iterators.append(weak_ref_ret)

        return shar_iter

class ReplayAsyncIterable:

    def __init__(self, async_iterator):
        self._async_iterator = async_iterator
        self._values = []
        self._noone_broadcasting = Event()
        self._noone_broadcasting.set()

    async def _broadcast(self):
        self._values.append(await self._async_iterator.__anext__())


    def __aiter__(self):

        class _ReplayAsyncIterator:

            def __init__(self, parent):
                self._parent = parent
                self._count = 0

            async def __anext__(self):
                if self._count < len(self._parent._values):
                    value = self._parent._values[self._count]
                    self._count += 1
                    return value
                else:
                    if self._parent._noone_broadcasting.is_set():
                        self._parent._noone_broadcasting.clear()
                        await self._parent._broadcast()
                        self._parent._noone_broadcasting.set()
                    else:
                        await self._parent._noone_broadcasting.wait()
                    value = self._parent._values[self._count]
                    self._count += 1
                    return value

        shar_iter = _ReplayAsyncIterator(self)

        return shar_iter
