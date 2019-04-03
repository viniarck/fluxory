#!/usr/bin/env python
# -*- coding: utf-8 -*-

from aio_pika.patterns import RPC
import json
from typing import Dict, Any


class ResponseRPC(object):

    """Abstract a RPC Response. """

    def __init__(self, result: Any, error: str = "") -> None:
        """Constructor of ResponseRPC."""

        self.result = result
        self.error = error

    def to_json(self) -> str:
        """Convert to json."""
        return json.dumps(self.to_dict())

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dict."""
        return {"result": self.result, "error": self.error}

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> object:
        """Build a ResponseRPC from a dict."""
        try:
            return ResponseRPC(result=d["result"], error=d["error"])
        except KeyError:
            raise Exception(
                "The RPC dictionary must have both the 'result' and 'error' keys"
            )


class JsonRPC(RPC):

    """JsonRPC serializer. """

    SERIALIZER = json
    CONTENT_TYPE = "application/json"

    def serialize(self, data: Any) -> bytes:
        return self.SERIALIZER.dumps(data).encode()

    def deserialize(self, data: bytes) -> Any:
        return self.SERIALIZER.loads(data)
