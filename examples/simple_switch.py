#!/usr/bin/env python
# -*- coding: utf-8 -*-

from fluxory.ofproto import ofproto_v1_5_parser
from fluxory.ofproto import ofproto_v1_3_parser
from fluxory.ofproto import ofproto_protocol
from fluxory.lib.packet import packet
from fluxory.lib.packet import ethernet
from fluxory.lib.packet import ether_types
from fluxory.ofproto import ofproto_parser
import logging
import asyncio
from logging.config import fileConfig
from aio_pika import IncomingMessage
from fluxory.rpc import JsonRPC, RequestRawRPC
from fluxory.app import App
import os


parent_dir = os.path.sep.join(os.path.abspath(__file__).split(os.path.sep)[:-2])
log_file = f"{parent_dir}{os.path.sep}logging.ini"
fileConfig(log_file)
log = logging.getLogger("examples.switch")


class SimpleSwitch(App):
    def __init__(self) -> None:
        """Constructor of SimpleSwitch

        SimpleSwitch supports both OpenFlow1.3 and OpenFlow1.5.
        """
        super().__init__()
        self.version = 6
        (self.ofproto, self.ofparser) = ofproto_protocol._versions[self.version]
        self.mac_to_port = {}

    def on_ofp_message(self, message: IncomingMessage) -> None:
        """Message broker incoming messages callback."""
        with message.process():
            log.debug(f"received [x] {message.routing_key}:{message.body}")
            (version, msg_type, msg_len, xid) = ofproto_parser.header(message.body)
            log.debug(
                f"msg {version} {msg_type} {msg_len} {xid} {len(message.body)} {type(message.body)}"
            )
            msg = ofproto_parser.msg(
                version, msg_type, msg_len, xid, message.body[:msg_len]
            )
            if msg_type == self.ofproto.OFPT_PACKET_IN:
                pkt_in = self.ofparser.OFPPacketIn.parser(msg_len, xid, msg.buf)
                pkt_in.serialize()
                dpid = int(message.routing_key.split(".")[-1])
                self.loop.create_task(self.handle_pktin(pkt_in, dpid))

    def on_t_message(self, message: IncomingMessage) -> None:
        """Message broker incoming messages callback."""
        with message.process():
            log.debug(f"received [x] {message.routing_key}:{message.body}")

    async def send_flow_mod_rpc(self, dpid: int, match, port: int, err: bool = False):
        """Send a flow mod."""
        channel = await self._broker_connection.channel()
        rpc = await JsonRPC.create(channel)

        actions = [self.ofparser.OFPActionOutput(port, self.ofproto.OFPCML_NO_BUFFER)]
        inst = [
            self.ofparser.OFPInstructionActions(
                self.ofproto.OFPIT_APPLY_ACTIONS, actions
            )
        ]
        if err:
            match = self.ofparser.OFPMatch(ipv6_src="::1")
        mod = self.ofparser.OFPFlowMod(priority=1001, match=match, instructions=inst)
        mod.serialize()
        ints = [int(f) for f in mod.buf]
        t = await rpc.proxy.write_dpid(
            **RequestRawRPC(dpid=dpid, payload=ints).to_dict()
        )
        log.debug(f"rpc flow mod {(t)}")

    async def handle_pktin(
        self, pkt_in: ofproto_v1_5_parser.OFPPacketIn, dpid: int
    ) -> None:
        """Handle packet in."""
        pkt = packet.Packet(pkt_in.data)
        eth = pkt.get_protocols(ethernet.ethernet)[0]

        # only ipv4 untagged packets are supported for now
        if not (
            eth.ethertype == ether_types.ETH_TYPE_ARP
            or eth.ethertype == ether_types.ETH_TYPE_IP
        ):
            return
        dst = eth.dst
        src = eth.src

        if dpid not in self.mac_to_port:
            self.mac_to_port[dpid] = {}

        in_port = pkt_in.match["in_port"]
        log.debug("packet in {} {} {} {}".format(dpid, src, dst, in_port))

        self.mac_to_port[dpid][src] = in_port
        if dst in self.mac_to_port[dpid]:
            out_port = self.mac_to_port[dpid][dst]
        else:
            out_port = self.ofproto.OFPP_FLOOD

        log.debug(f"mac_to_port {self.mac_to_port}")
        actions = [self.ofparser.OFPActionOutput(out_port)]
        if out_port != self.ofproto.OFPP_FLOOD:
            match = self.ofparser.OFPMatch(in_port=in_port, eth_dst=dst, eth_src=src)
            await self.send_flow_mod_rpc(dpid, match, out_port)
        else:
            match = self.ofparser.OFPMatch(in_port=in_port)
            out: self.ofparser.OFPPacketOut = None
            if self.ofproto.OFP_VERSION == 0x4:
                out = ofproto_v1_3_parser.OFPPacketOut(
                    buffer_id=pkt_in.buffer_id,
                    in_port=match["in_port"],
                    actions=actions,
                    data=pkt_in.data,
                )
            elif self.ofproto.OFP_VERSION == 0x6:
                out = ofproto_v1_5_parser.OFPPacketOut(
                    buffer_id=pkt_in.buffer_id,
                    match=match,
                    actions=actions,
                    data=pkt_in.data,
                )
            channel = await self._broker_connection.channel()
            rpc = await JsonRPC.create(channel)
            out.serialize()
            res = await rpc.proxy.write_dpid(
                dpid=dpid, payload=[int(f) for f in out.buf]
            )
            log.debug(f"res {res}")


async def main() -> None:
    """main async function."""
    s = SimpleSwitch()
    await s.run()
    ret = await s.list_switches()
    log.info(f"dpids: {ret}")
    while True:
        await asyncio.sleep(1)


if __name__ == "__main__":
    asyncio.run(main())
