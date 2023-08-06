# -*- coding: utf-8 -*-

__author__ = r'wsb310@gmail.com'

import time

from texttable import Texttable

from ..extend.base import Utils
from ..extend.asyncio.command import MainProcessAbstract, SubProcessAbstract


class TimerMS:

    __slots__ = [r'_timer']

    def __init__(self, timer=None):
        self._timer = time.time() if timer is None else timer

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.done()

    def done(self):
        self._timer = (time.time() - self._timer) * 1000

    @property
    def value(self):
        return self._timer


class Report:

    class _Report:

        def __init__(self):
            self.success = []
            self.failure = []

        @property
        def total(self):
            return len(self.success) + len(self.failure)

        @property
        def ratio(self):
            return len(self.success) / self.total if self.total > 0 else 0

        @property
        def min_success(self):
            return min(self.success)

        @property
        def max_success(self):
            return max(self.success)

        @property
        def avg_success(self):
            return sum(self.success) / len(self.success) if len(self.success) > 0 else 0

    def __init__(self):

        self._reports = {}

        self._timer = None

    def __enter__(self):

        self._timer = TimerMS()

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):

        self._timer.done()

        _time = round(self._timer.value / 1000)
        _count = sum([item.total for item in self._reports.values()])

        table = Texttable()

        table.header(
            [
                r'Event Name',
                r'Success Total',
                r'Failure Total',
                r'Success Ratio',
                r'Success AveTime',
                r'Success MinTime',
                r'Success MaxTime',
            ]
        )

        for key, val in self._reports.items():
            table.add_row(
                [
                    key,
                    len(val.success),
                    len(val.failure),
                    r'{:.2%}'.format(val.ratio),
                    r'{:.3f}ms'.format(val.avg_success),
                    r'{:.3f}ms'.format(val.min_success),
                    r'{:.3f}ms'.format(val.max_success),
                ]
            )

        Utils.log.info(f'\nTotal: {_count}, Time: {_time}s, Qps: {round(_count / _time)}\n{table.draw()}\n')

    def _get_report(self, name: str) -> _Report:

        if name not in self._reports:
            self._reports[name] = self._Report()

        return self._reports[name]

    def add(self, name, result, resp_time):

        if result == r'success':
            self._get_report(name).success.append(resp_time)
        elif result == r'failure':
            self._get_report(name).failure.append(resp_time)


class RunnerAbstract(SubProcessAbstract):

    async def _run(self):
        raise NotImplementedError()

    def success(self, name: str, resp_time: int):

        self._queue.put_nowait(
            Utils.msgpack_encode(
                [name, r'success', resp_time]
            )
        )

    def failure(self, name: str, resp_time: int):

        self._queue.put_nowait(
            Utils.msgpack_encode(
                [name, r'failure', resp_time]
            )
        )


class Launcher(MainProcessAbstract):

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

        self._report = Report()

    async def _on_message(self, message):

        self._report.add(
            *Utils.msgpack_decode(
                message
            )
        )

    async def _run(self):

        with self._report:
            await super()._run()
