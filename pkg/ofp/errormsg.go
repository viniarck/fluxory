package ofp

import (
	"encoding/binary"
	"errors"
)

type ErrorMsg struct {
	Header
	Type uint16
	Code uint16
	Data uint8
}

func NewErrorMsg(version uint8, xid uint32, errType uint16, code uint16, data uint8) *ErrorMsg {
	m := new(ErrorMsg)
	m.Header = Header{version, OFPT_ERROR, m.Size(), xid}
	m.Type = errType
	m.Code = code
	m.Data = data
	return m
}

func (m *ErrorMsg) Encode() []byte {
	data := make([]byte, m.Size())
	hLen := m.Header.Size()
	copy(data[:hLen], m.Header.Encode())
	binary.BigEndian.PutUint16(data[hLen:10], m.Type)
	binary.BigEndian.PutUint16(data[10:12], m.Code)
	data[12] = m.Data
	return data
}

func (m *ErrorMsg) Decode(data []byte) error {
	if uint16(len(data)) < m.Size() {
		return errors.New("bad minimum length size " + string(m.Size()))
	}
	err := m.Header.Decode(data[:m.Header.Size()])
	if err != nil {
		return err
	}
	hLen := m.Header.Size()
	m.Type = binary.BigEndian.Uint16(data[hLen:10])
	m.Code = binary.BigEndian.Uint16(data[10:12])
	m.Data = data[12]
	return nil
}

func (m *ErrorMsg) Size() uint16 {
	return uint16(binary.Size(m))
}
