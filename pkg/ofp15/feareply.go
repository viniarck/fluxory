package ofp15

import (
	"github.com/viniarck/fluxory/pkg/ofp"
)

func NewFeaturesReply(xid uint32) *ofp.FeaturesReply {
	return &ofp.FeaturesReply{Header: ofp.Header{OFPP_V15, OFPT_FEATURES_REPLY, ofp.OFP_HEADER_SIZE, xid}}
}
