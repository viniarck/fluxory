package ofp15

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

	data := []byte{OFPP_V15, OFPT_ECHO_REQUEST, 0, ofp.OFP_HEADER_SIZE, 0, 0, 0, 0}
	assert.Equal(h.Size(), uint16(ofp.OFP_HEADER_SIZE))
	assert.Equal(h.Encode(), data)

	msg := ofp.EchoRequest{}
	err := msg.Decode(data)
	assert.Nil(err)
	assert.Equal(*h, msg)
}
