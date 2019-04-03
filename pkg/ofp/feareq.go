package ofp

type FeaturesRequest struct {
	Header
}

func NewFeaturesRequest(version uint8, xid uint32) *FeaturesRequest {
	return &FeaturesRequest{Header{version, OFPT_FEATURES_REQUEST, OFP_HEADER_SIZE, xid}}
}
