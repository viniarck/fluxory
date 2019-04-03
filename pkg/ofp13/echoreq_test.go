package ofp13

import (
	"testing"

	"github.com/stretchr/testify/assert"
	"github.com/viniarck/fluxory/pkg/ofp"
)

func TestEchoRequest(t *testing.T) {
	assert := assert.New(t)

	xid := uint32(0)
	h := NewEchoRequest(xid)
	h.Encode()

	data := []byte{OFPP_V13, OFPT_ECHO_REQUEST, 0, ofp.OFP_HEADER_SIZE, 0, 0, 0, 0}
	assert.Equal(uint16(ofp.OFP_HEADER_SIZE), h.Size())
	assert.Equal(data, h.Encode())

	msg := ofp.EchoRequest{}
	err := msg.Decode(data)
	assert.Nil(err)
	assert.Equal(*h, msg)
}
