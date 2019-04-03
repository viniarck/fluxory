package ofp

type EchoReply struct {
	Header
}

func NewEchoReply(version uint8, xid uint32) *EchoReply {
	return &EchoReply{Header{version, OFPT_ECHO_REPLY, OFP_HEADER_SIZE, xid}}
}
