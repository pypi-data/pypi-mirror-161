# -*- coding: utf-8 -*-

__author__ = r'wsb310@gmail.com'

import os
import time

from typing import Callable

from multiprocessing import Process
from multiprocessing.shared_memory import SharedMemory

from .base import Utils
from .interface import ContextManager, RunnableInterface
from .struct import ByteArrayAbstract


def fork_processes() -> int:

    pid = os.fork()

    if pid == 0:
        Utils.urandom_seed()

    return pid


class Daemon(RunnableInterface):

    def __init__(self, target: Callable, sub_process_num: int, *, keep_live: bool = False, **kwargs):

        self._target = target
        self._kwargs = kwargs

        self._sub_process = set()
        self._sub_process_num = sub_process_num

        self._keep_live = keep_live

    def _fill_process(self):

        while len(self._sub_process) < self._sub_process_num:

            process = Process(target=self._target, kwargs=self._kwargs)
            process.start()

            self._sub_process.add(process)

    def _check_process(self):

        for process in self._sub_process.copy():

            if not process.is_alive():
                self._sub_process.remove(process)

        if self._keep_live is True:
            self._fill_process()

    def is_active(self):

        return self._keep_live or (len(self._sub_process) > 0)

    def run(self):

        self._fill_process()

        while self.is_active():
            self._check_processes()
            time.sleep(0.1)


class SharedByteArray(SharedMemory, ByteArrayAbstract, ContextManager):

    def __init__(self, name=None, create=False, size=0):

        SharedMemory.__init__(self, name, create, size)
        ByteArrayAbstract.__init__(self)

    def _context_release(self):

        self.release()

    def release(self):

        self.close()

        if (self._flags & os.O_CREAT) != 0:
            self.unlink()

    def read(self, size):

        return self._buf[:size]

    def write(self, buffer):

        self._buf[:len(buffer)] = buffer


class HeartbeatChecker(ContextManager):

    def __init__(self, name=r'default', timeout=60):

        self._name = f'heartbeat_{name}'

        self._timeout = timeout

        try:
            self._byte_array = SharedByteArray(self._name, True, 8)
        except Exception as _:
            self._byte_array = SharedByteArray(self._name)

    def _context_release(self):

        self.release()

    @property
    def refresh_time(self):

        if self._byte_array is not None:
            return self._byte_array.read_unsigned_int()
        else:
            return 0

    def release(self):

        if self._byte_array is not None:
            self._byte_array.release()
            self._byte_array = None

    def check(self):

        return (Utils.timestamp() - self.refresh_time) < self._timeout

    def refresh(self):

        if self._byte_array is not None:
            self._byte_array.write_unsigned_int(Utils.timestamp())
