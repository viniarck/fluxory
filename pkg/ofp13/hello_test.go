package ofp13

import (
	"testing"

	"github.com/stretchr/testify/assert"
	"github.com/viniarck/fluxory/pkg/ofp"
)

func TestHeader(t *testing.T) {
	assert := assert.New(t)

	h := ofp.NewHeader(OFPP_V13, OFPT_HELLO, 8, 1000)
	expected := []byte{OFPP_V13, 0, 0, 8, 0, 0, 3, 232}
	assert.Equal(expected, h.Encode())
}

func TestHello(t *testing.T) {
	assert := assert.New(t)

	xid := uint32(0)
	h := NewHello(xid)
	h.Encode()

	data := []byte{OFPP_V13, OFPT_HELLO, 0, ofp.OFP_HEADER_SIZE + 8, 0, 0, 0, 0, 0, 1, 0, 8, 0, 0, 0, 1 << OFPP_V13}
	assert.Equal(uint16(ofp.OFP_HEADER_SIZE)+8, h.Size())
	assert.Equal(data, h.Encode())
}
