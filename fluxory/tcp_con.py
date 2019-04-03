#!/usr/bin/env python
# -*- coding: utf-8 -*-

import asyncio
import logging
from fluxory.switch_con import SwitchCon
from typing import Tuple

log = logging.getLogger(__name__)


class OpenFlowServerCon(asyncio.Protocol):

    """Async TCP protocol connection abstraction."""

    def __init__(self, controller) -> None:
        self.transport: asyncio.Transport = None
        self.controller = controller
        self.loop = asyncio.get_running_loop()
        self.peername: Tuple[str, int] = ("", 0)

    def connection_made(self, transport: asyncio.Transport) -> None:
        """Connection made callback."""
        self.peername = transport.get_extra_info("peername")
        log.info('Connection from {}'.format(self.peername))
        ofp_switch = SwitchCon(self.peername, transport)
        self.controller.add_switch(ofp_switch)

    def data_received(self, data: bytes) -> None:
        """Receive data callback. Push onto an async queue."""
        log.debug(f"Data received: {data}")
        self.controller.of_in_queue.put_nowait((self.peername, data,))

    def connection_lost(self, exc: Exception) -> None:
        """Connection lost callback."""
        reason = "Connection lost" or exc
        log.info(f"Connection {self.peername} lost reason: {reason}")
        self.controller.del_switch(self.peername)
