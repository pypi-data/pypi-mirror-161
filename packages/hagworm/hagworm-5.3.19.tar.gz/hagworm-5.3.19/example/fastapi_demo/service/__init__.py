# -*- coding: utf-8 -*-

__author__ = r'wsb310@gmail.com'

from hagworm.extend.trace import get_trace_id
from hagworm.extend.error import Ignore, catch_error
from hagworm.extend.metaclass import Singleton
from hagworm.extend.asyncio.base import Utils, FuncCache, ShareFuture, MultiTasks
from hagworm.extend.asyncio.redis import RedisDelegate
from hagworm.extend.asyncio.mongo import MongoDelegate
from hagworm.extend.asyncio.mysql import MySQLDelegate
from hagworm.extend.process import HeartbeatChecker

from setting import ConfigStatic, ConfigDynamic


class DataSource(Singleton, RedisDelegate, MongoDelegate, MySQLDelegate):

    def __init__(self):

        RedisDelegate.__init__(self)
        MongoDelegate.__init__(self)
        MySQLDelegate.__init__(self)

        self._health_checker = HeartbeatChecker(ConfigDynamic.ServerName)

    @classmethod
    async def initialize(cls):

        inst = cls()

        (await inst.init_redis_single(
            ConfigStatic.RedisHost[0], ConfigStatic.RedisHost[1], password=ConfigStatic.RedisPasswd,
            min_connections=ConfigStatic.RedisMinConn, max_connections=ConfigStatic.RedisMaxConn
        )).set_key_prefix(ConfigStatic.RedisKeyPrefix)

        inst.init_mongo(
            ConfigStatic.MongoHost, ConfigStatic.MongoUser, ConfigStatic.MongoPasswd,
            auth_source=ConfigStatic.MongoAuth,
            min_pool_size=ConfigStatic.MongoMinConn, max_pool_size=ConfigStatic.MongoMaxConn, max_idle_time=3600
        )

        if ConfigStatic.MySqlMasterServer:

            await inst.init_mysql_rw(
                ConfigStatic.MySqlMasterServer[0], ConfigStatic.MySqlMasterServer[1], ConfigStatic.MySqlName,
                ConfigStatic.MySqlUser, ConfigStatic.MySqlPasswd,
                minsize=ConfigStatic.MySqlMasterMinConn, maxsize=ConfigStatic.MySqlMasterMaxConn,
                echo=ConfigDynamic.Debug, pool_recycle=21600, conn_life=43200
            )

        if ConfigStatic.MySqlSlaveServer:

            await inst.init_mysql_ro(
                ConfigStatic.MySqlSlaveServer[0], ConfigStatic.MySqlSlaveServer[1], ConfigStatic.MySqlName,
                ConfigStatic.MySqlUser, ConfigStatic.MySqlPasswd,
                minsize=ConfigStatic.MySqlSlaveMinConn, maxsize=ConfigStatic.MySqlSlaveMaxConn,
                echo=ConfigDynamic.Debug, pool_recycle=21600, readonly=True, conn_life=43200
            )

    @classmethod
    async def release(cls):

        inst = cls()

        inst._health_checker.release()

        inst.close_mongo_pool()

        await inst.async_close_redis()
        await inst.close_mysql()

    @classmethod
    async def check_health(cls):

        return await cls().health()

    @property
    def online(self):

        return self._health_checker.check()

    @ShareFuture()
    @FuncCache(ttl=30)
    async def health(self):

        result = False

        with catch_error():

            tasks = MultiTasks()

            tasks.append(self.redis_health())
            tasks.append(self.mysql_health())
            tasks.append(self.mongo_health())

            await tasks

            result = all(tasks)

            if result is True:
                self._health_checker.refresh()

        return result


class ServiceBase(Singleton, Utils):

    def __init__(self):

        self._data_source = DataSource()

    @property
    def trace_id(self):

        return get_trace_id()

    def Break(self, *args, layers=1):

        raise Ignore(*args, layers=layers)
