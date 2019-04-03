#!/usr/bin/env python
# -*- coding: utf-8 -*-

import asyncio
import logging
from aio_pika import connect, ExchangeType
from aio_pika.connection import Connection
from aio_pika.exchange import Exchange


log = logging.getLogger(__name__)


class BrokerInterface(object):
    __slots__ = [
        "loop"
        "broker_host",
        "broker_port",
        "broker_user",
        "broker_password",
        "_broker_exchange"
        "_broker_exchange_name",
        "_broker_connection"
    ]

    def __init__(
        self,
        host: str = "localhost",
        port: int = 5672,
        user: str = "guest",
        password: str = "guest",
    ) -> None:
        """Constructor of BrokerInterface."""
        self.broker_host = host
        self.broker_port = port
        self.broker_user = user
        self.broker_password = password
        self._broker_exchange: Exchange = None
        self._broker_exchange_name = "fluxory"
        self._broker_connection: Connection = None
        self.loop = asyncio.get_event_loop()

    @property
    def broker_is_closed(self) -> bool:
        """Check if the broker connection is closed."""
        if self._broker_connection:
            return self._broker_connection.is_closed
        return True

    def broker_close(self, exc) -> None:
        """Broker close callback."""
        log.error(f"Broker close reason: {exc}")
        if self._broker_connection:
            self.loop.create_task(self._broker_connection.close())

    async def broker_con(self) -> None:
        """Connect to broker."""
        log.info(f"{str(self)} connecting to message broker")
        self._broker_connection = await connect(
            host=self.broker_host,
            port=self.broker_port,
            user=self.broker_user,
            password=self.broker_password,
            loop=self.loop,
        )
        self._broker_connection.add_close_callback(self.broker_close)
        log.info(f"{str(self)} connected to message broker")

        channel = await self._broker_connection.channel()
        await channel.set_qos(prefetch_count=1)
        self._broker_exchange = await channel.declare_exchange(
            self._broker_exchange_name, ExchangeType.TOPIC
        )

