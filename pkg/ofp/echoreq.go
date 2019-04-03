package ofp

type EchoRequest struct {
	Header
}

func NewEchoRequest(version uint8, xid uint32) *EchoRequest {
	return &EchoRequest{Header{version, OFPT_ECHO_REQUEST, OFP_HEADER_SIZE, xid}}
}
