# Copyright (C) 2017 Nippon Telegraph and Telephone Corporation.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import struct

from . import packet_base


class openflow(packet_base.PacketBase):
    """OpenFlow message encoder/decoder class.

    An instance has the following attributes at least.

    ============== =========================================================
    Attribute      Description
    ============== =========================================================
    msg            An instance of OpenFlow message (see :ref:`ofproto_ref`)
                   or an instance of OFPUnparseableMsg if failed to parse
                   packet as OpenFlow message.
    ============== =========================================================
    """

    PACK_STR = "!BBHI"
    _MIN_LEN = struct.calcsize(PACK_STR)

    def __init__(self, msg):
        super(openflow, self).__init__()
        self.msg = msg

    @classmethod
    def parser(cls, buf):
        from fluxory.ofproto import ofproto_parser
        from fluxory.ofproto import ofproto_protocol

        (version, msg_type, msg_len, xid) = ofproto_parser.header(buf)

        (_, msg_parser) = ofproto_protocol.get(version)
        msg = msg_parser.from_type(msg_type, msg_len, xid, buf[:msg_len])

        return cls(msg), cls, buf[msg_len:]

    def serialize(self):
        self.msg.serialize()
        return self.msg.buf
