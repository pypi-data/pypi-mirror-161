# -*- coding: utf-8 -*-

__author__ = r'wsb310@gmail.com'

import aio_pika


class RabbitMQConsumer(aio_pika.RobustConnection):
    """RabbitMQ消费者
    """

    def __init__(self, url, **kwargs):

        super().__init__(url, **kwargs)

        self._channel = None
        self._queue = None

        self._channel_qos_config = None

        self._queue_name = None
        self._queue_config = None

        self._consume_func = None
        self._consume_no_ack = None

    @property
    def current_channel(self):

        return self._channel

    @property
    def current_queue(self):

        return self._queue

    def config(
            self, queue_name, consume_func, consume_no_ack=False,
            *, channel_qos_config=None, queue_config=None
    ):

        self._channel_qos_config = channel_qos_config if channel_qos_config else {r'prefetch_count': 1}

        self._queue_name = queue_name
        self._queue_config = queue_config if queue_config else {}

        self._consume_func = consume_func
        self._consume_no_ack = consume_no_ack

    async def connect(self, *args, **kwargs) -> None:

        self._RobustConnection__channels.clear()

        await super().connect(*args, **kwargs)
        await self.ready()

        self._channel = await self.channel()

        await self._channel.set_qos(**self._channel_qos_config)

        self._queue = await self._channel.declare_queue(self._queue_name, **self._queue_config)

        if self._consume_func is not None:
            await self._queue.consume(self._consume_func, no_ack=self._consume_no_ack)

    async def close(self):

        await self._channel.close()
        await super().close()

    async def get(self, *, no_ack=False, timeout=1):

        await self._queue.get(no_ack=no_ack, timeout=timeout)


class RabbitMQConsumerForExchange(RabbitMQConsumer):
    """RabbitMQ注册到交换机的消费者(默认生成排它队列注册)
    """

    def __init__(self, url, **kwargs):
        
        super().__init__(url, **kwargs)

        self._exchange = None

        self._exchange_name = None
        self._routing_key = None

    @property
    def current_exchange(self):

        return self._exchange

    def config(
            self, exchange_name, consume_func, consume_no_ack=False,
            *, channel_qos_config=None, queue_config=None, routing_key=None
    ):

        queue_name = None

        if queue_config is None:
            queue_config = {r'exclusive': True}
        elif r'name' in queue_config:
            queue_name = queue_config.pop(r'name')

        super().config(
            queue_name, consume_func, consume_no_ack,
            channel_qos_config=channel_qos_config, queue_config=queue_config
        )

        self._exchange_name = exchange_name
        self._routing_key = routing_key

    async def connect(self, *args, **kwargs) -> None:

        self._exchange = None

        await super().connect(*args, **kwargs)

        self._exchange = await self._channel.get_exchange(self._exchange_name)

        await self._queue.bind(self._exchange, self._routing_key)
