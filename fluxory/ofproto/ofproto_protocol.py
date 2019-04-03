# Copyright (C) 2014 Nippon Telegraph and Telephone Corporation.
# Copyright (C) 2014 YAMAMOTO Takashi <yamamoto at valinux co jp>
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

from fluxory.ofproto import ofproto_v1_3
from fluxory.ofproto import ofproto_v1_3_parser
from fluxory.ofproto import ofproto_v1_5
from fluxory.ofproto import ofproto_v1_5_parser
from fluxory.exceptions import FluxoryError
from typing import Optional

_versions = {
    ofproto_v1_3.OFP_VERSION: (ofproto_v1_3, ofproto_v1_3_parser),
    ofproto_v1_5.OFP_VERSION: (ofproto_v1_5, ofproto_v1_5_parser),
}


def get(version: int) -> (object, object):
    """Get ofproto and parser

    Raises FluxoryError if the version isn't implemented."""
    try:
        return _versions[version]
    except KeyError:
        raise FluxoryError("Unsupported OFP version: {version}")


class OFProtoFactory(object):

    """Map a OFP version to ofproto definitions and parser"""

    @classmethod
    def get(cls, ofp_version: int) -> (object, object):
        """Get ofproto_version and ofproto_version_parser."""
        return _versions.get(ofp_version)


# OF versions supported by every apps in this process (intersection)
_supported_versions = set(_versions.keys())


def set_app_supported_versions(vers):
    global _supported_versions

    _supported_versions &= set(vers)
    assert _supported_versions, 'No OpenFlow version is available'


class ProtocolDesc(object):
    """
    OpenFlow protocol version flavor descriptor
    """

    def __init__(self, version: Optional[int] = None) -> None:
        if version is None:
            version = max(_supported_versions)
        self.version = version
        self.set_version(version)

    def set_version(self, version: int) -> None:
        assert version in _supported_versions
        (self.ofproto, self.ofproto_parser) = _versions[version]

    @property
    def supported_ofp_version(self):
        return _supported_versions
