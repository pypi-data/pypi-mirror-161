# -*- coding: utf-8 -*-

__author__ = r'wsb310@gmail.com'

from typing import Callable
from multiprocessing import Queue

from ... import hagworm_slogan
from ... import __version__ as hagworm_version

from .base import install_uvloop, Utils

from ..error import catch_error
from ..interface import RunnableInterface
from ..process import Daemon


class MainProcessAbstract(Daemon):

    def __init__(
            self, target: Callable, sub_process_num: int, *,
            keep_live: bool = False, queue_maxsize=0xffff, **kwargs
    ):

        self._queue = Queue(queue_maxsize)

        super().__init__(target, sub_process_num, keep_live=keep_live, queue=self._queue, **kwargs)

    async def _on_message(self, message):
        raise NotImplementedError()

    async def _run(self):

        while self.is_active():

            self._check_process()

            try:
                while True:
                    await self._on_message(
                        self._queue.get(True, 0.1)
                    )
            except:
                pass

    def run(self):

        environment = Utils.environment()

        Utils.log.info(
            f'{hagworm_slogan}'
            f'hagworm {hagworm_version}\n'
            f'python {environment["python"]}\n'
            f'system {" ".join(environment["system"])}'
        )

        install_uvloop()

        self._fill_process()

        with catch_error():
            Utils.run_until_complete(self._run())


class SubProcessAbstract(RunnableInterface):

    @classmethod
    def create(cls, queue):

        cls(queue).run()

    def __init__(self, queue: Queue):

        self._queue = queue

        self._process_id = Utils.getpid()

    async def _run(self):
        raise NotImplementedError()

    def run(self):

        Utils.log.success(f'Started worker process [{self._process_id}]')

        install_uvloop()

        Utils.run_until_complete(self._run())

        Utils.log.success(f'Stopped worker process [{self._process_id}]')
