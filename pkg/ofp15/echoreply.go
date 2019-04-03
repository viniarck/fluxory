package ofp15

import (
	"github.com/viniarck/fluxory/pkg/ofp"
)

func NewEchoReply(xid uint32) *ofp.EchoReply {
	return &ofp.EchoReply{ofp.Header{OFPP_V15, OFPT_ECHO_REPLY, ofp.OFP_HEADER_SIZE, xid}}
}
