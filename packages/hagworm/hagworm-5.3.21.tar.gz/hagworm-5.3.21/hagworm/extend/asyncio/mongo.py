# -*- coding: utf-8 -*-

__author__ = r'wsb310@gmail.com'

from motor.motor_asyncio import AsyncIOMotorClient

from .base import Utils

from ..error import catch_error


MONGO_POLL_WATER_LEVEL_WARNING_LINE = 0x10


class MongoPool:
    """Mongo连接管理
    """

    def __init__(
            self, host, username=None, password=None,
            *, name=None, auth_source=r'admin', min_pool_size=8, max_pool_size=32, max_idle_time=3600, wait_queue_timeout=10,
            compressors=r'zlib', zlib_compression_level=6,
            **settings
    ):

        self._name = name if name is not None else Utils.uuid1()[:8]

        settings[r'host'] = host
        settings[r'authSource'] = auth_source
        settings[r'minPoolSize'] = min_pool_size
        settings[r'maxPoolSize'] = max_pool_size
        settings[r'maxIdleTimeMS'] = max_idle_time * 1000
        settings[r'waitQueueTimeoutMS'] = wait_queue_timeout * 1000
        settings[r'compressors'] = compressors
        settings[r'zlibCompressionLevel'] = zlib_compression_level

        if username and password:
            settings[r'username'] = username
            settings[r'password'] = password

        self._pool = AsyncIOMotorClient(**settings)

        for server in self._servers.values():
            server.pool.remove_stale_sockets()

        self._pool_options = self._pool.options.pool_options

        Utils.log.info(
            f"Mongo {host} ({self._name}) initialized: "
            f"{self._pool_options.min_pool_size}/{self._pool_options.max_pool_size}"
        )

    @property
    def _servers(self):

        return self._pool.delegate._topology._servers

    def _echo_pool_info(self):

        global MONGO_POLL_WATER_LEVEL_WARNING_LINE

        for address, server in self._servers.items():

            free_size = len(server.pool.sockets)
            pool_size = free_size + server.pool.active_sockets
            max_pool_size = server.pool.max_pool_size

            if (max_pool_size - server.pool.active_sockets) < MONGO_POLL_WATER_LEVEL_WARNING_LINE:
                Utils.log.warning(
                    f'Mongo connection pool not enough ({self._name}){address}: '
                    f'{free_size}({pool_size}/{max_pool_size})'
                )
            else:
                Utils.log.debug(
                    f'Mongo connection pool info ({self._name}){address}: '
                    f'{free_size}({pool_size}/{max_pool_size})'
                )

    def reset(self):

        for address, server in self._servers.items():

            server.pool.reset()
            server.pool.remove_stale_sockets()

            Utils.log.info(
                f'Mongo connection pool reset {address}: {len(server.pool.sockets)}/{self._pool.max_pool_size}'
            )

    def close(self):

        if self._pool is not None:
            self._pool.close()
            self._pool = None

    def get_database(self, db_name):

        self._echo_pool_info()

        result = None

        with catch_error():
            result = self._pool[db_name]

        return result


class MongoDelegate:
    """Mongo功能组件
    """

    def __init__(self):

        self._mongo_pool = None

    def init_mongo(self, *args, **kwargs):

        self._mongo_pool = MongoPool(*args, **kwargs)

    @property
    def mongo_pool(self):

        return self._mongo_pool

    async def mongo_health(self):

        result = False

        with catch_error():
            result = bool(await self._mongo_pool._pool.server_info())

        return result

    def reset_mongo_pool(self):

        self._mongo_pool.reset()

    def close_mongo_pool(self):

        self._mongo_pool.close()

    def get_mongo_database(self, db_name):

        return self._mongo_pool.get_database(db_name)

    def get_mongo_collection(self, db_name, collection):

        return self.get_mongo_database(db_name)[collection]
