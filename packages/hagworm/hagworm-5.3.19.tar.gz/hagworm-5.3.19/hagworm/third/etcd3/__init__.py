# -*- coding: utf-8 -*-

__author__ = r'wsb310@gmail.com'

from etcd3gw.client import Etcd3Client

from ...extend.asyncio.pool import ObjectPool


class Etcd3ClientPool(ObjectPool):

    def __init__(self, host, port=2379, *, maxsize=100, api_path=r'/v3/', **kwargs):

        self._setting = dict(host=host, port=port, api_path=api_path, **kwargs)

        super().__init__(maxsize)

    def _create_obj(self):

        return Etcd3Client(**self._setting)


