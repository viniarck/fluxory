package ofp15

import (
	"testing"

	"github.com/stretchr/testify/assert"
	"github.com/viniarck/fluxory/pkg/ofp"
)

func TestEchoReply(t *testing.T) {
	assert := assert.New(t)

	xid := uint32(0)
	h := NewEchoReply(xid)
	h.Encode()

	data := []byte{OFPP_V15, OFPT_ECHO_REPLY, 0, ofp.OFP_HEADER_SIZE, 0, 0, 0, 0}
	assert.Equal(h.Size(), uint16(ofp.OFP_HEADER_SIZE))
	assert.Equal(h.Encode(), data)

	msg := ofp.EchoReply{}
	err := msg.Decode(data)
	assert.Nil(err)
	assert.Equal(*h, msg)
}
