package ofp13

import (
	"github.com/viniarck/fluxory/pkg/ofp"
)

func NewFeaturesRequest(xid uint32) *ofp.FeaturesRequest {
	return &ofp.FeaturesRequest{ofp.Header{OFPP_V13, OFPT_FEATURES_REQUEST, ofp.OFP_HEADER_SIZE, xid}}
}
