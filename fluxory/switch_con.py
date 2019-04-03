#!/usr/bin/env python
# -*- coding: utf-8 -*-
import asyncio
import logging
import time
from typing import Tuple
from fluxory.ofproto import ofproto_protocol
from fluxory.ofproto.ofproto_parser import MsgBase
from sys import maxsize as max_int
from enum import Enum

log = logging.getLogger(__name__)


class Handshake(Enum):
    """OpenFlow Handshake status valus. """

    complete = "complete"
    incomplete = "incomplete"


class Switch(object):

    """Switch abstraction"""

    def __init__(self, dpid: int = 0, version: int = 0) -> None:
        """Constructor of Switch."""
        # The dpid is only determined after completing the handshake.
        self.dpid = dpid
        self.version = version
        self.last_seen = time.time()
        self.status = Handshake.incomplete


class SwitchCon(Switch):

    """OpenFlow Switch Connection Protocol abstraction.

    The OpenFlow version is set once the handshake is completed.
    """

    def __init__(self, peername: Tuple[str, int], transport: asyncio.Transport) -> None:
        """Constructor of SwitchCon."""
        super().__init__()
        self.peername = peername
        self.transport = transport
        self.ofproto = None
        self.ofparser = None
        self.xid = 1
        self.response_secs = 0
        self._echo_loop_task: asyncio.Task = None

    def xid_tuple(self, xid) -> Tuple[str, int, int]:
        """Get xid unique tuple."""
        return (self.peername[0], self.peername[1], xid)

    def set_reponse_latency(self, ts: float) -> None:
        """Set timestamp latency."""
        diff = ts - self.last_seen
        if not self.response_secs:
            self.response_secs = diff
        else:
            if diff < self.response_secs:
                self.response_secs = diff
        self.last_seen = ts

    def set_version(self, version: int) -> None:
        """Set runtime negotiated version."""
        self.version = version
        (self.ofproto, self.ofparser) = ofproto_protocol._versions[self.version]
        # TODO remove this. Gotta refactor MsgBase though.
        self.dp = ofproto_protocol.ProtocolDesc(self.version)

    def write(self, msg: MsgBase) -> int:
        """Write an OpenFlow message to this switch."""
        msg.xid = self.xid
        self.xid += 1 % max_int
        msg.serialize()
        log.debug(f"Writing msg.type {msg.msg_type} msg.xid {msg.xid}")
        # transport is async, it doesn't block.
        self.transport.write(msg.buf)
        return msg.xid
