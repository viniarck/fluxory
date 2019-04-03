package ofp

import (
	"encoding/binary"
)

type Hello struct {
	Header
	Elements [1]HelloElement
}

type HelloElement struct {
	Type   uint16
	Length uint16
	Bitmap uint32
}

func NewHello(version uint8, xid uint32) *Hello {
	// TODO replace this init
	hello := new(Hello)
	hello.Elements[0] = *NewHelloElement(version)
	hello.Header = Header{version, OFPT_HELLO, hello.Size(), xid}
	return hello
}

func (h *Hello) Encode() []byte {
	data := make([]byte, h.Size())
	hData := h.Header.Encode()
	copy(data[0:], hData)
	copy(data[h.Header.Size():], h.Elements[0].Encode())
	return data
}

func (m *Hello) Decode(data []byte) error {
	// TODO fix.
	// m.Header.Encode()
	// index := 8

	// for index < len(packet) {
	// 	e := NewHelloElement()
	// 	e.Encode(packet[index:])
	// 	index += e.Size()
	// m.Elements = append(m.Elements, e)
	// }
	// return
	return nil
}

func (m *Hello) Size() uint16 {
	size := m.Header.Size()
	for _, e := range m.Elements {
		size += e.Size()
	}
	return size
}

func NewHelloElement(highestVer uint8) *HelloElement {
	h := new(HelloElement)
	h.Type = 1
	h.Length = uint16(binary.Size(h))
	h.Bitmap = 1 << highestVer
	return h
}

func (h *HelloElement) Encode() []byte {
	data := make([]byte, h.Size())
	binary.BigEndian.PutUint16(data[0:2], h.Type)
	binary.BigEndian.PutUint16(data[2:4], h.Length)
	binary.BigEndian.PutUint32(data[4:8], h.Bitmap)
	return data
}

func (h *HelloElement) Decode(data []byte) {
	h.Type = binary.BigEndian.Uint16(data[0:])
	h.Length = binary.BigEndian.Uint16(data[2:])
}

func (h *HelloElement) Size() uint16 {
	return h.Length
}
