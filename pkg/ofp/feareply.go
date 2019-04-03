package ofp

import (
	"encoding/binary"
	"errors"
)

type FeaturesReply struct {
	Header       Header
	Dpid         uint64
	NBuffers     uint32
	NTables      uint8
	AuxId        uint8
	Pad          uint16
	Capabilities uint32
	Reserved     uint32
}

func NewFeaturesReply(version uint8, xid uint32) *FeaturesReply {
	return &FeaturesReply{Header: Header{version, OFPT_FEATURES_REPLY, OFP_HEADER_SIZE, xid}}
}

func (m *FeaturesReply) Encode() []byte {
	data := make([]byte, m.Size())
	hLen := m.Header.Size()
	copy(data[0:hLen], m.Header.Encode())
	binary.BigEndian.PutUint64(data[hLen:16], m.Dpid)
	binary.BigEndian.PutUint32(data[16:20], m.NBuffers)
	data[21] = m.NTables
	data[22] = m.AuxId
	binary.BigEndian.PutUint16(data[22:24], m.Pad)
	binary.BigEndian.PutUint32(data[24:28], m.Capabilities)
	binary.BigEndian.PutUint32(data[28:32], m.Reserved)
	return data
}

func (m *FeaturesReply) Decode(data []byte) error {
	if uint16(len(data)) < m.Size() {
		return errors.New("bad minimum length size " + string(m.Size()))
	}
	err := m.Header.Decode(data[:m.Header.Size()])
	if err != nil {
		return err
	}
	hLen := m.Header.Size()
	m.Dpid = binary.BigEndian.Uint64(data[hLen:16])
	m.NBuffers = binary.BigEndian.Uint32(data[16:20])
	m.NTables = data[20]
	m.AuxId = data[21]
	m.Pad = binary.BigEndian.Uint16(data[22:24])
	m.Capabilities = binary.BigEndian.Uint32(data[24:28])
	m.Reserved = binary.BigEndian.Uint32(data[28:32])
	return nil
}

func (m *FeaturesReply) Size() uint16 {
	return uint16(binary.Size(m))
}
