#!/usr/bin/env python
# -*- coding: utf-8 -*-

import asyncio
from logging import getLogger
from aio_pika import Message, DeliveryMode, ExchangeType, IncomingMessage
from fluxory.broker_interface import BrokerInterface
from abc import abstractmethod
from typing import Dict
from collections import defaultdict
from fluxory.queue_events import CtlOFPEvent, CtlTEvent
from fluxory.ofproto.ofproto_parser import MsgBase
from fluxory.exceptions import FluxoryAppError
from fluxory.rpc import JsonRPC, ResponseRPC
from typing import List


class App(BrokerInterface):

    """The base class for Fluxory applications"""

    apps: Dict[str, str] = defaultdict(str)

    def __init__(self, name: str = "") -> None:
        """Constructor of App."""
        super().__init__()
        self.name = name or self.__class__.__name__
        self._ensure_unique_name()
        self.log = getLogger(self.name)
        self.loop = asyncio.get_event_loop()
        self.log.info(f"{self.name} just started")

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.name})"

    def _ensure_unique_name(self) -> None:
        """Ensure this App has an unique name."""
        if self.name in App.apps:
            raise FluxoryAppError(f"This Apps's name {self.name} is not unique")
        App.apps[self.name] = self.name

    async def connect(self) -> None:
        """Connect to message broker."""
        await self.broker_con()
        for routing_key, func in zip(
            [CtlOFPEvent.queue_wildcard(), CtlTEvent.queue_wildcard()],
            [self.on_ofp_message, self.on_t_message],
        ):
            channel = await self._broker_connection.channel()
            queue = await channel.declare_queue(
                self.name + routing_key.split(CtlOFPEvent._separator)[0], durable=True
            )
            self.log.info(f"{self} subscribing to {routing_key}")
            await queue.bind(self._broker_exchange, routing_key=routing_key)
            await queue.consume(func)

    async def run(self) -> None:
        """App Entry point."""
        connect_coro = self.loop.create_task(self.connect())
        await asyncio.wait({connect_coro})

    async def list_switches(self) -> List[int]:
        """docstring for ."""
        # TODO handle when the broker isn't available.
        channel = await self._broker_connection.channel()
        rpc = await JsonRPC.create(channel)
        t = await rpc.proxy.list_switches()
        resp = ResponseRPC.from_dict(t)
        # TODO raise if there's an error
        return resp.result["dpids"]

    @abstractmethod
    def on_ofp_message(self, message: IncomingMessage) -> None:
        """Message broker incoming messages callback."""
        pass

    @abstractmethod
    def on_t_message(self, message: IncomingMessage) -> None:
        """Message broker incoming messages callback."""
        pass
