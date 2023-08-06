# -*- coding: utf-8 -*-

__author__ = r'wsb310@gmail.com'

import asyncio
import aiomysql
import sqlalchemy

from contextvars import ContextVar

from aiomysql.sa import SAConnection, Engine
from aiomysql.sa.engine import _dialect as dialect

from pymysql.err import Warning, DataError, IntegrityError, ProgrammingError

from sqlalchemy.sql.selectable import Select
from sqlalchemy.sql.dml import Insert, Update, Delete

from .base import Utils, WeakContextVar, AsyncCirculator

from ..error import catch_error, MySQLReadOnlyError, MySQLClientDestroyed
from ..interface import AsyncContextManager


MYSQL_ERROR_RETRY_COUNT = 0x10
MYSQL_POLL_WATER_LEVEL_WARNING_LINE = 0x10


class MySQLPool:
    """MySQL连接管理
    """

    class _Connection(SAConnection):

        def __init__(self, connection, engine, compiled_cache=None):

            super().__init__(connection, engine, compiled_cache)

            if not hasattr(connection, r'build_time'):
                setattr(connection, r'build_time', Utils.loop_time())

        @property
        def build_time(self):

            return getattr(self._connection, r'build_time', 0)

        async def destroy(self):

            if self._connection is None:
                return

            if self._transaction is not None:
                await self._transaction.rollback()
                self._transaction = None

            self._connection.close()

            self._engine.release(self)
            self._connection = None
            self._engine = None

    def __init__(
            self, host, port, db, user, password,
            *, name=None, minsize=8, maxsize=32, echo=False, pool_recycle=21600,
            charset=r'utf8', autocommit=True, cursorclass=aiomysql.DictCursor,
            readonly=False, conn_life=43200,
            **settings
    ):

        self._name = name if name is not None else (Utils.uuid1()[:8] + (r'_ro' if readonly else r'_rw'))
        self._pool = None
        self._engine = None
        self._readonly = readonly
        self._conn_life = conn_life

        self._settings = settings

        self._settings[r'host'] = host
        self._settings[r'port'] = port
        self._settings[r'db'] = db

        self._settings[r'user'] = user
        self._settings[r'password'] = password

        self._settings[r'minsize'] = minsize
        self._settings[r'maxsize'] = maxsize

        self._settings[r'echo'] = echo
        self._settings[r'pool_recycle'] = pool_recycle
        self._settings[r'charset'] = charset
        self._settings[r'autocommit'] = autocommit
        self._settings[r'cursorclass'] = cursorclass

    @property
    def name(self):

        return self._name

    @property
    def readonly(self):

        return self._readonly

    @property
    def conn_life(self):

        return self._conn_life

    def __await__(self):

        self._pool = yield from aiomysql.create_pool(**self._settings).__await__()
        self._engine = Engine(dialect, self._pool)

        Utils.log.info(
            f"MySQL [{self._settings[r'host']}:{self._settings[r'port']}] {self._settings[r'db']}"
            f" ({self._name}) initialized: {self._pool.size}/{self._pool.maxsize}"
        )

        return self

    async def close(self):

        if self._pool is not None:

            self._pool.close()
            await self._pool.wait_closed()

            self._pool = None

    def _echo_pool_info(self):

        if self.health:
            Utils.log.debug(
                f'MySQL connection pool info ({self._name}): '
                f'{self._pool.freesize}({self._pool.size}/{self._pool.maxsize})'
            )
        else:
            Utils.log.warning(
                f'MySQL connection pool not enough ({self._name}): '
                f'{self._pool.freesize}({self._pool.size}/{self._pool.maxsize})'
            )

    @property
    def health(self):

        global MYSQL_POLL_WATER_LEVEL_WARNING_LINE

        return (self._pool.maxsize - self._pool.size + self._pool.freesize) > MYSQL_POLL_WATER_LEVEL_WARNING_LINE

    async def reset(self):

        if self._pool is not None:

            await self._pool.clear()

            Utils.log.info(
                f'MySQL connection pool reset ({self._name}): {self._pool.size}/{self._pool.maxsize}'
            )

    async def get_sa_conn(self):

        self._echo_pool_info()

        conn = await self._pool.acquire()

        return self._Connection(conn, self._engine)

    def get_client(self):

        return DBClient(self)

    def get_transaction(self):

        if self._readonly:
            raise MySQLReadOnlyError()

        return DBTransaction(self)


class MySQLDelegate:
    """MySQL功能组件
    """

    def __init__(self):

        self._mysql_rw_pool = None
        self._mysql_ro_pool = None

    @property
    def mysql_rw_pool(self):

        return self._mysql_rw_pool

    @property
    def mysql_ro_pool(self):

        return self._mysql_ro_pool

    async def init_mysql_rw(self, *args, **kwargs):

        self._mysql_rw_pool = await MySQLPool(*args, **kwargs)

    async def init_mysql_ro(self, *args, **kwargs):

        self._mysql_ro_pool = await MySQLPool(*args, **kwargs)

    async def close_mysql(self):

        if self._mysql_rw_pool is not None:
            await self._mysql_rw_pool.close()

        if self._mysql_ro_pool is not None:
            await self._mysql_ro_pool.close()

    async def mysql_health(self):

        result = await self._check_health(self._mysql_rw_pool)
        result &= await self._check_health(self._mysql_ro_pool)

        return result

    async def _check_health(self, pool):

        if pool is None:
            return True

        async with pool.get_client() as client:

            await client.safe_execute(r'select version();')

            return True

        return False

    async def reset_mysql_pool(self):

        if self._mysql_rw_pool:
            await self._mysql_rw_pool.reset()

        if self._mysql_ro_pool:
            await self._mysql_ro_pool.reset()

    def get_db_client(self, readonly=False):

        if readonly:
            if self._mysql_ro_pool:
                return self._mysql_ro_pool.get_client()
            else:
                return self._mysql_rw_pool.get_client()
        else:
            return self._mysql_rw_pool.get_client()

    def get_db_transaction(self):

        return self._mysql_rw_pool.get_transaction()


class _ClientBase:
    """MySQL客户端基类
    """

    @staticmethod
    def safestr(val):

        cls = type(val)

        if cls is str:
            val = aiomysql.escape_string(val)
        elif cls is dict:
            val = aiomysql.escape_dict(val)
        else:
            val = str(val)

        return val

    def __init__(self, pool):

        self._pool = pool

        self._conn = None
        self._trx = None

        self._readonly = pool.readonly

        self._lock = asyncio.Lock()

    @property
    def readonly(self):

        return self._readonly

    @property
    def insert_id(self):

        if self._conn:
            return self._conn.connection.insert_id()
        else:
            return None

    async def _get_conn(self):

        if self._pool is None:
            raise MySQLClientDestroyed()

        if self._conn is None:
            self._conn = await self._pool.get_sa_conn()

        return self._conn

    async def _close_conn(self, discard=False):

        if self._conn is not None:

            _conn, self._conn = self._conn, None

            if discard:
                await _conn.destroy()
            elif (Utils.loop_time() - _conn.build_time) > self._pool.conn_life:
                await _conn.destroy()
            else:
                await _conn.close()

    async def _execute(self, clause):

        raise NotImplementedError()

    async def execute(self, clause):

        result = None

        async with self._lock:
            result = await self._execute(clause)

        return result

    async def safe_execute(self, clause):

        async with self._lock:

            proxy = await self._execute(clause)
            await proxy.close()

            await self._close_conn()

    async def select(self, query, *multiparams, **params):

        result = []

        if not isinstance(query, Select):
            raise TypeError(r'Not sqlalchemy.sql.selectable.Select object')

        async with self._lock:

            proxy = await self._execute(query, *multiparams, **params)

            if proxy is not None:

                records = await proxy.cursor.fetchall()

                if records:
                    result.extend(records)

                if not proxy.closed:
                    await proxy.close()

            if not self._trx:
                await self._close_conn()

        return result

    async def find(self, query, *multiparams, **params):

        result = None

        if not isinstance(query, Select):
            raise TypeError(r'Not sqlalchemy.sql.selectable.Select object')

        async with self._lock:

            proxy = await self._execute(query.limit(1), *multiparams, **params)

            if proxy is not None:

                record = await proxy.cursor.fetchone()

                if record:
                    result = record

                if not proxy.closed:
                    await proxy.close()

            if not self._trx:
                await self._close_conn()

        return result

    async def count(self, table_col, select_where=None):

        _select = sqlalchemy.select([sqlalchemy.func.count(table_col).label(r'tbl_row_count')])

        if select_where is not None:
            _select = _select.where(select_where)

        result = await self.find(_select)

        return result[r'tbl_row_count']

    async def insert(self, query, *multiparams, **params):

        result = 0

        if self._readonly:
            raise MySQLReadOnlyError()

        if not isinstance(query, Insert):
            raise TypeError(r'Not sqlalchemy.sql.dml.Insert object')

        async with self._lock:

            proxy = await self._execute(query, *multiparams, **params)

            if proxy is not None:

                result = self.insert_id

                if not proxy.closed:
                    await proxy.close()

            if not self._trx:
                await self._close_conn()

        return result

    async def update(self, query, *multiparams, **params):

        result = 0

        if self._readonly:
            raise MySQLReadOnlyError()

        if not isinstance(query, Update):
            raise TypeError(r'Not sqlalchemy.sql.dml.Update object')

        async with self._lock:

            proxy = await self._execute(query, *multiparams, **params)

            if proxy is not None:

                result = proxy.rowcount

                if not proxy.closed:
                    await proxy.close()

            if not self._trx:
                await self._close_conn()

        return result

    async def delete(self, query, *multiparams, **params):

        result = 0

        if self._readonly:
            raise MySQLReadOnlyError()

        if not isinstance(query, Delete):
            raise TypeError(r'Not sqlalchemy.sql.dml.Delete object')

        async with self._lock:

            proxy = await self._execute(query, *multiparams, **params)

            if proxy is not None:

                result = proxy.rowcount

                if not proxy.closed:
                    await proxy.close()

            if not self._trx:
                await self._close_conn()

        return result


class DBClient(_ClientBase, AsyncContextManager):
    """MySQL客户端对象，使用with进行上下文管理

    将连接委托给客户端对象管理，提高了整体连接的使用率

    """

    async def _context_release(self):

        await self._close_conn(self._lock.locked())

    async def release(self):

        async with self._lock:
            await self._close_conn()

    async def _execute(self, query, *multiparams, **params):

        global MYSQL_ERROR_RETRY_COUNT

        result = None

        async for times in AsyncCirculator(max_times=MYSQL_ERROR_RETRY_COUNT):

            try:

                conn = await self._get_conn()

                result = await conn.execute(query, *multiparams, **params)

            except (Warning, DataError, IntegrityError, ProgrammingError) as err:

                await self._close_conn(True)

                raise err

            except Exception as err:

                await self._close_conn(True)

                if times < MYSQL_ERROR_RETRY_COUNT:
                    Utils.log.error(err)
                else:
                    raise err

            else:

                break

        return result


class DBTransaction(_ClientBase, AsyncContextManager):
    """MySQL客户端事务对象，使用with进行上下文管理

    将连接委托给客户端对象管理，提高了整体连接的使用率

    """

    async def _get_conn(self):

        if self._trx is None:
            self._conn = await super()._get_conn()
            self._trx = await self._conn.begin()

        return self._conn

    async def _close_conn(self, discard=False):

        if self._trx is not None:

            if self._trx.is_active:
                self._trx.close()

            self._trx = None

        await super()._close_conn(discard)

        self._pool = None

    async def _context_release(self):

        await self.rollback()

    async def release(self):

        await self.rollback()

    async def _execute(self, query, *multiparams, **params):

        result = None

        if self._readonly:
            raise MySQLReadOnlyError()

        try:

            conn = await self._get_conn()

            result = await conn.execute(query, *multiparams, **params)

        except Exception as err:

            await self._close_conn(True)

            raise err

        return result

    async def commit(self):

        async with self._lock:

            if self._trx:
                await self._trx.commit()

            await self._close_conn()

    async def rollback(self):

        async with self._lock:

            if self._trx:
                await self._trx.rollback()

            await self._close_conn()
