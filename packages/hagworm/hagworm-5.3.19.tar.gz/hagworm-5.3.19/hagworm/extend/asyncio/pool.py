# -*- coding: utf-8 -*-

__author__ = r'wsb310@gmail.com'

from asyncio import Queue
from contextlib import contextmanager, asynccontextmanager

from hagworm.extend.base import Utils


class ObjectPool:
    """对象池实现
    """

    def __init__(self, maxsize, debug=False):

        self._maxsize = maxsize
        self._debug = debug

        self._queue = Queue(maxsize=maxsize)

        for _ in range(maxsize):
            self._queue.put_nowait(self._create_obj())

        if self._debug:
            Utils.log.debug(f'ObjectPool {type(self)} initialized: {self._queue.qsize()}')

    def _create_obj(self):

        raise NotImplementedError()

    @property
    def maxsize(self):

        return self._maxsize

    @property
    def size(self):

        return self._queue.qsize()

    @asynccontextmanager
    async def get(self):

        if self._debug:
            Utils.log.debug(f'ObjectPool {type(self)} size: {self._queue.qsize()}')

        obj = await self._queue.get()

        try:
            yield obj
        except Exception as err:
            raise err
        finally:
            self._queue.put_nowait(obj)

    @contextmanager
    def get_nowait(self):

        if self._debug:
            Utils.log.debug(f'ObjectPool {type(self)} size: {self._queue.qsize()}')

        obj = self._queue.get_nowait()

        try:
            yield obj
        except Exception as err:
            raise err
        finally:
            self._queue.put_nowait(obj)


