# -*- coding: utf-8 -*-

__author__ = r'wsb310@gmail.com'

import uuid
import time
import functools

from asyncio import iscoroutinefunction
from contextvars import ContextVar
from loguru import logger


TRACE_ID_CONTEXT = ContextVar(r'trace_id', default=None)
TRACE_NO_CONTEXT = ContextVar(r'trace_no', default=None)


def get_trace_id():

    return TRACE_ID_CONTEXT.get()


def refresh_trace_id(trace_id=None, trace_no=None):

    if trace_id is None:
        trace_id = str(uuid.uuid1())

    TRACE_ID_CONTEXT.set(trace_id)
    TRACE_NO_CONTEXT.set(trace_no)

    return trace_id


def inc_trace_no():

    trace_no = TRACE_NO_CONTEXT.get()
    trace_no = 0 if trace_no is None else trace_no + 1

    TRACE_NO_CONTEXT.set(trace_no)

    return trace_no


def trace_wrapper(func):

    if iscoroutinefunction(func):
        @functools.wraps(func)
        async def _wrapper(*args, **kwargs):
            refresh_trace_id()
            return await func(*args, **kwargs)
    else:
        @functools.wraps(func)
        async def _wrapper(*args, **kwargs):
            refresh_trace_id()
            return func(*args, **kwargs)

    return _wrapper


def tracing(func):

    @functools.wraps(func)
    def _wrapper(*args, **kwargs):

        _time = time.time() * 1000

        try:
            return func(*args, **kwargs)
        except Exception as err:
            raise err
        finally:
            logger.bind(
                trace_id=get_trace_id(), trace_no=inc_trace_no(),
                trace_time=(trace_time := "{:.3f}".format(time.time() * 1000 - _time))
            ).info(
                f'tracing <{func.__module__}.{func.__qualname__}> {trace_time}ms\n'
                f'args: {args}, kwargs: {kwargs}'
            )

    return _wrapper


def async_tracing(func):

    @functools.wraps(func)
    async def _wrapper(*args, **kwargs):

        _time = time.time() * 1000

        try:
            return await func(*args, **kwargs)
        except Exception as err:
            raise err
        finally:
            logger.bind(
                trace_id=get_trace_id(), trace_no=inc_trace_no(),
                trace_time=(trace_time := "{:.3f}".format(time.time() * 1000 - _time))
            ).info(
                f'tracing <{func.__module__}.{func.__qualname__}> {trace_time}ms\n'
                f'args: {args}, kwargs: {kwargs}'
            )

    return _wrapper

