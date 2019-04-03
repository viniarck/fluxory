package ofp15

import (
	"testing"

	"github.com/stretchr/testify/assert"
	"github.com/viniarck/fluxory/pkg/ofp"
)

func TestErrorMsg(t *testing.T) {
	assert := assert.New(t)

	xid := uint32(0)
	errType := uint16(1)
	errCode := uint16(2)
	dat := uint8(0)
	h := NewErrorMsg(xid, errType, errCode, dat)
	h.Encode()

	size := h.Header.Size() + uint16(5)
	data := []byte{OFPP_V15, OFPT_ERROR, 0, uint8(size), 0, 0, 0, 0, 0, 1, 0, 2, 0}
	assert.Equal(size, h.Size())
	assert.Equal(data, h.Encode())

	errMsg := ofp.ErrorMsg{}
	err := errMsg.Decode(data)
	assert.Nil(err)
	assert.Equal(*h, errMsg)
}
