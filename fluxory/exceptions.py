#!/usr/bin/env python
# -*- coding: utf-8 -*-


class FluxoryError(Exception):

    """Fluxory Base Error class"""

    def __init__(self, msg: str) -> None:
        """Constructor of FluxoryError."""

        super().__init__(msg)
        self.msg = msg


class FluxoryAppError(FluxoryError):

    """docstring for FluxoryAppError. """

    def __init__(self, msg: str) -> None:
        """Constructor of FluxoryAppError."""
        super().__init__(msg)


class RyuException(Exception):
    message = 'An unknown exception'

    def __init__(self, msg=None, **kwargs):
        self.kwargs = kwargs
        if msg is None:
            msg = self.message

        try:
            msg = msg % kwargs
        except Exception:
            msg = self.message

        super(RyuException, self).__init__(msg)


class OFPUnknownVersion(RyuException):
    message = 'unknown version %(version)x'


class OFPMalformedMessage(RyuException):
    message = 'malformed message'


class OFPTruncatedMessage(RyuException):
    message = 'truncated message: %(orig_ex)s'

    def __init__(self, ofpmsg, residue, original_exception,
                 msg=None, **kwargs):
        self.ofpmsg = ofpmsg
        self.residue = residue
        self.original_exception = original_exception
        kwargs['orig_ex'] = str(original_exception)

        super(OFPTruncatedMessage, self).__init__(msg, **kwargs)


class OFPInvalidActionString(RyuException):
    message = 'unable to parse: %(action_str)s'


class NetworkNotFound(RyuException):
    message = 'no such network id %(network_id)s'


class NetworkAlreadyExist(RyuException):
    message = 'network id %(network_id)s already exists'


class PortNotFound(RyuException):
    message = 'no such port (%(dpid)s, %(port)s) in network %(network_id)s'


class PortAlreadyExist(RyuException):
    message = 'port (%(dpid)s, %(port)s) in network %(network_id)s ' \
              'already exists'


class PortUnknown(RyuException):
    message = 'unknown network id for port (%(dpid)s %(port)s)'


class MacAddressDuplicated(RyuException):
    message = 'MAC address %(mac)s is duplicated'
