package ofp

import (
	"encoding/binary"
	"errors"
)

/**
* OpenFlow constants values
 */
const (
	OFPP_MAX        = 0xffffff00
	OFPP_IN_PORT    = 0xfffffff8
	OFPP_TABLE      = 0xfffffff9
	OFPP_NORMAL     = 0xfffffffa
	OFPP_FLOOD      = 0xfffffffb
	OFPP_ALL        = 0xfffffffc
	OFPP_CONTROLLER = 0xfffffffd
	OFPP_LOCAL      = 0xfffffffe
	OFPP_ANY        = 0xffffffff
)

const (
	OFP_HEADER_SIZE = 8
)

/**
 * Header struct
 */
type Header struct {
	Version uint8
	Type    uint8
	Length  uint16
	Xid     uint32
}

/**
 * OFPMessage interface
 */
type OFPMessage interface {
	Encode() []byte
	Decode(data []byte) error
	Size() uint16
	GetXid() uint32
	SetXid(xid uint32)
	GetType() uint8
}

/*****************************************************/
/* Header
/*****************************************************/

func NewHeader(version uint8, msgType uint8, length uint16, xid uint32) *Header {
	return &Header{version, msgType, length, xid}
}

func (h *Header) Encode() []byte {
	data := make([]byte, OFP_HEADER_SIZE)
	data[0] = h.Version
	data[1] = h.Type
	binary.BigEndian.PutUint16(data[2:4], h.Length)
	binary.BigEndian.PutUint32(data[4:8], h.Xid)
	return data
}

func (h *Header) Decode(data []byte) error {
	l := len(data)
	if l < OFP_HEADER_SIZE {
		return errors.New("bad minimum length size " + string(l))
	}
	h.Version = data[0]
	h.Type = data[1]
	h.Length = binary.BigEndian.Uint16(data[2:4])
	h.Xid = binary.BigEndian.Uint32(data[4:8])
	return nil
}

func (h *Header) Size() uint16 {
	return uint16(binary.Size(h))
}

func (h *Header) SetXid(xid uint32) {
	h.Xid = xid
}

func (h *Header) GetXid() uint32 {
	return h.Xid
}

func (h *Header) GetType() uint8 {
	return h.Type
}
