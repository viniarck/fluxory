package ofp15

import (
	"github.com/viniarck/fluxory/pkg/ofp"
)

func NewEchoRequest(xid uint32) *ofp.EchoRequest {
	return &ofp.EchoRequest{ofp.Header{OFPP_V15, OFPT_ECHO_REQUEST, ofp.OFP_HEADER_SIZE, xid}}
}
