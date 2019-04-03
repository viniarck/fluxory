package ofp13

import (
	"github.com/viniarck/fluxory/pkg/ofp"
)

func NewEchoRequest(xid uint32) *ofp.EchoRequest {
	return &ofp.EchoRequest{ofp.Header{OFPP_V13, OFPT_ECHO_REQUEST, ofp.OFP_HEADER_SIZE, xid}}
}
