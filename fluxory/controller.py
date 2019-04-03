#!/usr/bin/env python
# -*- coding: utf-8 -*-

import asyncio
import logging
import time

from aio_pika import connect, Message, DeliveryMode, ExchangeType, IncomingMessage
from fluxory.rpc import JsonRPC, ResponseRPC
from fluxory.queue_events import CtlOFPEvent, AppOFPEvent, CtlTEvent
from fluxory.broker_interface import BrokerInterface
from fluxory.tcp_con import OpenFlowServerCon
from fluxory.switch_con import SwitchCon, Handshake
from fluxory.ofproto import ofproto_parser
from fluxory.ofproto.ofproto_parser import MsgBase
from fluxory.ofproto.ofproto_common import expected_reply_type, is_assymetric_msg
from typing import Dict, Any, Set, Tuple, List
from aiormq.exceptions import ConnectionClosed
import json

log = logging.getLogger(__name__)


class OpenFlowController(BrokerInterface):
    def __init__(
        self,
        version: int,
        *versions: Set[int],
        local_addr="localhost",
        port: int = 6653,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.port = port
        self.local_addr = "localhost"
        self.server = None
        self.loop = asyncio.get_event_loop()
        self.switches: Dict[Tuple[str, int], SwitchCon] = {}
        self.dpids: Dict[int, SwitchCon] = {}
        self._tasks = []
        self.versions = {version}
        for version in versions:
            self.versions.add(version)

        # asyncio.Queue instances have to be created when the loop is running
        # Queue for handling incoming OFP messages from switches
        self.of_in_queue: asyncio.Queue = None
        # Outgoing xids
        self.xids_out: Dict[Tuple[str, int, int], int] = {}
        self.xids_future: Dict[Tuple[str, int, int], asyncio.Task] = {}

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.local_addr}, {self.port})"

    async def monitor_broker_con(self):
        """Monitor broker connection status."""
        log.info("Broker connection monitor status started")
        logged = False
        while True:
            if self._broker_connection.is_closed:
                if not logged:
                    log.error("Broker connection is closed")
                    logged = True
            else:
                if logged:
                    logged = False
            await asyncio.sleep(1)

    async def handle_in_queue(self):
        """Handle incoming messages from self.of_in_queue."""
        log.debug("Handling OpenFlow incoming messages")
        while True:
            (peername, data) = await self.of_in_queue.get()
            (version, msg_type, msg_len, xid) = ofproto_parser.header(data)
            log.debug(
                f"in queue message from peername {peername} version {version} msg_type {msg_type} xid {xid}"
            )
            switch = self.switches[peername]
            xid_tuple = switch.xid_tuple(xid)
            log.debug(f"of_in_queue xid_tuple {xid_tuple}")
            if self.xids_out.get(xid_tuple):
                switch.set_reponse_latency(time.time())
                log.debug(f"switch mean {switch.response_secs:.3f} seconds")
                future = self.xids_future.get(xid_tuple)
                if future:
                    self.xids_future[xid_tuple].set_result((msg_type, time.time()))
            if not switch.version:
                if version in self.versions:
                    log.info(f"Trying to negotiate version {version}")
                    switch.set_version(version)
                else:
                    err_str = f"OF version {version} isn't on supported versions list {self.versions}"
                    log.error(err_str)
                    continue
            if switch.status == Handshake.incomplete:
                if msg_type == switch.ofproto.OFPT_HELLO:
                    self.loop.create_task(self.do_handshake(switch))
                elif msg_type == switch.ofproto.OFPT_ECHO_REQUEST:
                    echo_reply = switch.ofparser.OFPEchoReply(b"")
                    self._write_switch(switch, echo_reply)
                elif msg_type == switch.ofproto.OFPT_FEATURES_REPLY:
                    fea_reply = switch.ofparser.OFPSwitchFeatures.parser(
                        msg_len, xid, data[:msg_len]
                    )
                    log.info(fea_reply)
                    switch.dpid = fea_reply.datapath_id
                    self.dpids[switch.dpid] = switch
            elif switch.status == Handshake.complete:
                # TODO provide easier way to derive dpid in the routing key
                if is_assymetric_msg(msg_type):
                    routing_key = f"CtlOFPEvent.{version}.{msg_type}"
                    if switch.dpid:
                        routing_key += f".{switch.dpid}"
                    log.debug(f"Publishing {routing_key} event")
                    await self.publish(data, routing_key)

    async def _echo_req_loop(
        self, switch: SwitchCon, interval_secs: int = 2, max_missed: int = 3
    ) -> None:
        """OpenFlow Echo Request loop for checking keepalive and to measure latency."""
        try:
            log.info(f"Starting echo request loop for {switch.peername}")
            while True:
                missed_count = max_missed
                while missed_count > 0:
                    await asyncio.sleep(interval_secs)
                    echo_req = switch.ofparser.OFPEchoRequest()
                    got_hello = await self.write_switch_wait(switch, echo_req)
                    if got_hello:
                        break
                    else:
                        missed_count -= 1
                        if not missed_count:
                            log.error("Maximum hellos {max_hellos} reached.")
                            return
        except asyncio.CancelledError:
            log.info(f"Stopping echo request loop for {switch.peername}")

    async def do_handshake(
        self, switch: SwitchCon, interval_secs: int = 2, max_echo_req_missed: int = 3
    ) -> None:
        """Perform OpenFlow connection setup handshake."""
        log.info(f"OpenFlow handshake {switch.peername} started")
        hello = switch.ofparser.OFPHello()
        self._write_switch(switch, hello)
        fea_req = switch.ofparser.OFPFeaturesRequest()
        got_fea = await self.write_switch_wait(switch, fea_req)
        if got_fea:
            switch.status = Handshake.complete
            log.info(f"OpenFlow handshake {switch.peername} completed")
            await self.publish_dict({"dpid": switch.dpid}, "CtlTEvent.switch.connected")
        else:
            log.error(f"OpenFlow handshake failed. Never got features reply.")
            return
        echo_req_t = self.loop.create_task(
            self._echo_req_loop(switch, interval_secs, max_echo_req_missed)
        )
        switch._echo_loop_task = echo_req_t

    async def list_switches(self) -> Dict[str, List[int]]:
        """List all switches dpid."""
        await asyncio.sleep(0)
        dpids = {"dpids": list(self.dpids.keys())}
        return dpids

    async def _register_rpc_methods(self):
        """Register all RPC methods of this instance."""
        # TODO maybe create an async decorator for registering each method
        methods = [self.list_switches, self.write_dpid, self.write_json]
        log.debug(f"Registering RPC methods {[method.__name__ for method in methods]}")
        channel = await self._broker_connection.channel()
        rpc = await JsonRPC.create(channel)
        for method in methods:
            await rpc.register(method.__name__, method, auto_delete=True)

    async def publish(self, msg: bytes, routing_key: str) -> None:
        """Send message to broker."""
        message = Message(msg, delivery_mode=DeliveryMode.PERSISTENT)
        await self._broker_exchange.publish(message, routing_key=routing_key)

    async def publish_dict(self, payload: Dict[Any, Any], routing_key: str) -> None:
        """Send message to broker."""
        payload_bytes = json.dumps(payload, ensure_ascii=False).encode("gbk")
        message = Message(payload_bytes, delivery_mode=DeliveryMode.PERSISTENT)
        await self._broker_exchange.publish(message, routing_key=routing_key)

    async def run(self) -> None:
        """Entry point to run the OpenFlowController."""
        log.info("Controller just started")
        self.loop = asyncio.get_event_loop()
        self.of_in_queue = asyncio.Queue()

        broker_coro = self.loop.create_task(self.broker_con())
        await asyncio.wait({broker_coro})
        if broker_coro.exception():
            raise broker_coro.exception()
        else:
            await self._register_rpc_methods()
            of_in_queue_coro = self.loop.create_task(self.handle_in_queue())
            self.server = await self.loop.create_server(
                lambda: OpenFlowServerCon(self), self.local_addr, self.port
            )
            log.info(f"TCP server is listening at {self.local_addr}:{self.port}")

            async with self.server:
                await self.server.serve_forever()

    def add_switch(self, switch_con: SwitchCon) -> None:
        """Add a SwitchCon."""
        self.switches[switch_con.peername] = switch_con

    def del_switch(self, peername: Tuple[str, int]) -> None:
        """Delete a SwitchCon."""
        switch = self.switches.get(peername)
        if switch:
            if switch._echo_loop_task:
                switch._echo_loop_task.cancel()
            if switch.dpid:
                del self.dpids[switch.dpid]
                self.loop.create_task(
                    self.publish_dict(
                        {"dpid": switch.dpid}, "CtlTEvent.switch.disconnected"
                    )
                )
            del self.switches[peername]

    def _write_switch(self, switch_con: SwitchCon, msg: MsgBase) -> (int, asyncio.Task):
        """Write OpenFlow message to a SwitchCon."""
        xid: int = switch_con.write(msg)
        log.debug(f"xid_out msg_type {msg.msg_type} xid {msg.xid}")
        xid_tuple = switch_con.xid_tuple(xid)

        self.xids_out[xid_tuple] = msg.msg_type
        future = self.loop.create_future()
        self.xids_future[xid_tuple] = future
        return (xid, future)

    def _del_future(self, xid_tuple: Tuple[str, int, int]) -> None:
        """Delete future and xids_outs given a xid_tuple key."""
        if self.xids_future.get(xid_tuple):
            del self.xids_future[xid_tuple]
        if self.xids_out.get(xid_tuple):
            del self.xids_out[xid_tuple]

    async def write_switch_wait(
        self,
        switch_con: SwitchCon,
        msg: MsgBase,
        timeout_factor: float = 1.5,
        fail_open: bool = True,
    ) -> bool:
        """Write OpenFlow message to a SwitchCon and wait."""
        (xid, future) = self._write_switch(switch_con, msg)
        xid_tuple = switch_con.xid_tuple(xid)
        msg_type_t = -1
        try:
            ts_created = time.time()
            timeout = switch_con.response_secs
            if not timeout:
                timeout = 3
            (msg_type_t, ts_sent) = await asyncio.wait_for(
                future, timeout=timeout * timeout_factor
            )
            diff = ts_sent - ts_created
            log.debug(f"Got msg_type_t {msg_type_t} latency {diff:.3f} seconds")
            self._del_future(xid_tuple)
            if expected_reply_type(msg.msg_type) != msg_type_t:
                return False
            return True
        except asyncio.TimeoutError:
            log.debug(f"message {msg.msg_type} xid {xid} timeout")
            self._del_future(xid_tuple)
            if fail_open:
                return True
            else:
                return False

    async def write_json(self, dpid: int, msg: Dict[str, Any]) -> Dict[str, Any]:
        """Write OpenFlow message to a switch_con."""
        result = False
        error = ""
        switch_con = self.dpids.get(dpid)
        if not switch_con:
            error = f"Inexistent dpid: {dpid}"
            return ResponseRPC(result, error).to_dict()
        if not msg.keys():
            error = f"JSON message payload doesn't have any keys"
            return ResponseRPC(result, error).to_dict()
        key = list(msg.keys())[0]
        cls: object = None
        try:
            cls = getattr(switch_con.ofparser, key)
        except AttributeError:
            error = f"This '{key}' doesn't map to an OpenFlow abstraction"
            return ResponseRPC(result, error).to_dict()
        sent = await self.write_switch_wait(switch_con, cls.from_jsondict(msg[key]))
        if not sent:
            error = "Wrong OpenFlow message reply received"
            return ResponseRPC(sent, error).to_dict()
        await asyncio.sleep(0)
        return ResponseRPC(sent, error).to_dict()

    async def write_dpid(self, dpid: int, msg: MsgBase) -> (Any, str):
        """Write OpenFlow message to a switch_con."""
        result = False
        error = ""
        switch_con = self.dpids.get(dpid)
        if not switch_con:
            error = f"Inexistent dpid: {dpid}"
            return (result, error)
        sent = await self.write_switch_wait(switch_con, msg)
        if not sent:
            error = "Wrong OpenFlow message reply received"
            return (sent, error)
        await asyncio.sleep(0)
        return (sent, error)
