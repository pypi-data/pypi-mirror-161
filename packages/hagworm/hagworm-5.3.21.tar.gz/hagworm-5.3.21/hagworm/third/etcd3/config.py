# -*- coding: utf-8 -*-

__author__ = r'wsb310@gmail.com'

from threading import Thread

from etcd3gw.client import Etcd3Client

from ...extend.config import ConfigureBase
from ...extend.error import catch_error


class Etcd3Configure(ConfigureBase):
    """基于etcd3的配置类
    """

    __slots__ = [r'_client', r'_key_prefix', r'_watch_iterator', r'_watch_cancel', r'_task']

    def __init__(self, host, port=2379, *, key_prefix, api_path=r'/v3/', **kwargs):

        super().__init__()

        self._client = Etcd3Client(host, port, **kwargs, api_path=api_path)

        self._key_prefix = key_prefix
        self._watch_iterator, self._watch_cancel = self._client.watch_prefix(self._key_prefix)

        self._task = Thread(target=self._do_task)
        self._task.start()

    def _do_task(self):

        for _item in self._watch_iterator:

            with catch_error():

                if r'value' not in _item[r'kv']:
                    continue

                _key_section = _item[r'kv'][r'key'].decode()

                if _key_section.find(self._key_prefix) == 0:
                    _key_section = _key_section.replace(self._key_prefix, r'', 1)

                if _key_section not in self._key_section:
                    continue

                _key, _section, _type = self._key_section.get(_key_section)

                if _type in (str, int, float, bool):
                    self.__setattr__(_key, _type(_item[r'kv'][r'value'].decode()))
                else:
                    self.__setattr__(_key, _type.decode(_item[r'kv'][r'value'].decode()))

    def close(self):

        self._watch_cancel()
        self._task.join(1)

    def load(self):

        setting = {}

        _resp = self._client.get_prefix(self._key_prefix)

        for _item in _resp:

            _key = _item[1][r'key'].decode()

            if _key.find(self._key_prefix) == 0:
                _key = _key.replace(self._key_prefix, r'', 1)

            setting[_key] = _item[0].decode()

        for _key, _section, _type in self._key_section.values():

            if _type in (str, int, float, bool):
                self.__setattr__(_key, _type(setting[f'{_section}/{_key}']))
            else:
                self.__setattr__(_key, _type.decode(setting[f'{_section}/{_key}']))

        return self
