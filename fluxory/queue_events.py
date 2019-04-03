#!/usr/bin/env python
# -*- coding: utf-8 -*-

from typing import Union
from fluxory.ofproto.ofproto_parser import MsgBase
from struct import pack, unpack


class QueueEvent(object):

    """
    Base QueueEvent class. It represents a generic event, which has
    a name with a specific separator and a payload.

    """

    _separator = "."

    def __init__(self, class_name: str, *sub_names: str, payload: bytes = None) -> None:
        """Constructor of QueueEvent."""
        self.name = self._make_name(class_name, *sub_names)
        self.payload = payload
        self._name = self.name.split(QueueEvent._separator)

    def _make_name(self, class_name: str, *sub_names: str) -> str:
        """Make a string name."""
        if not len(sub_names):
            return class_name

        for sub_name in sub_names:
            class_name += f"{QueueEvent._separator}{sub_name}"
        return class_name

    def __len__(self) -> int:
        return len(self.payload)

    def __repr__(self) -> str:
        return f"{self.name}"

    def __iter__(self) -> str:
        for item in self.payload:
            yield item

    def __getitem__(self, i: int) -> Union[bytes, None]:
        if i < 0:
            i = -1 * i
            return self.payload[len(self.payload) - i]
        return self.payload[i]


class CtlOFPEvent(QueueEvent):

    """OpenFlow messages from the Controller to Ryum Apps. """

    def __init__(self, version: int, msg_type: int, dpid: int = 0) -> None:
        """Constructor of CtlOFPEvent."""
        super().__init__(
            f"{self.__class__.__name__}.{str(version)}.{str(msg_type)}"
        )

    @classmethod
    def decode(self, payload: bytes) -> (int, bytes):
        """Decode the dpid number and serialized message (payload)."""
        return (int(unpack("!Q", payload[:8])[0]), payload[8:])

    @classmethod
    def queue_wildcard(self, version: int = 0) -> str:
        """Get queue wildcard."""
        if version:
            return (
                f"CtlOFPEvent{QueueEvent._separator}{version}{QueueEvent._separator}#"
            )
        else:
            return f"CtlOFPEvent{QueueEvent._separator}#"


class AppOFPEvent(QueueEvent):

    """OpenFlow messagges from Ryum Apps to the Controller. """

    def __init__(self, msg: MsgBase, dpid: int = 0) -> None:
        """Constructor of AppOFPEvent."""
        assert msg.buf
        payload = bytearray(pack("!Q", dpid) + msg.buf)
        super().__init__(
            f"{self.__class__.__name__}.{str(msg.version)}.{str(msg.msg_type)}",
            payload=payload,
        )

    @classmethod
    def decode(self, payload: bytes) -> (int, bytes):
        """Decode the dpid number and serialized message (payload)."""
        return (int(unpack("!Q", payload[:8])[0]), payload[8:])

    @classmethod
    def queue_wildcard(self, version: int = 0) -> str:
        """Get queue wildcard."""
        if version:
            return (
                f"AppOFPEvent{QueueEvent._separator}{version}.{QueueEvent._separator}#"
            )
        else:
            return f"AppOFPEvent{QueueEvent._separator}#"


class CtlTEvent(QueueEvent):

    """Generic T messages from the Controller to Ryum Apps. """

    def __init__(self, event_name: str, payload: bytes = b"") -> None:
        """Constructor of CtlTEvent."""
        super().__init__(f"{self.__class__.__name__}.{event_name}", payload=payload)

    @classmethod
    def queue_wildcard(self) -> str:
        """Get queue wildcard."""
        return f"CtlTEvent{QueueEvent._separator}#"


class AppTEvent(QueueEvent):

    """Generic T messages from Ryum Apps to other Ryum Apps. """

    def __init__(self, event_name: str, payload: bytes = b"") -> None:
        """Constructor of AppTEvent."""
        super().__init__(f"{self.__class__.__name__}.{event_name}", payload=payload)

    @classmethod
    def queue_wildcard(self) -> str:
        """Get queue wildcard."""
        return f"AppTEvent{QueueEvent._separator}#"
