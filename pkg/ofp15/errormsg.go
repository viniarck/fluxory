package ofp15

import (
	"github.com/viniarck/fluxory/pkg/ofp"
)

func NewErrorMsg(xid uint32, errType uint16, code uint16, data uint8) *ofp.ErrorMsg {
	m := new(ofp.ErrorMsg)
	m.Header = ofp.Header{OFPP_V15, OFPT_ERROR, m.Size(), xid}
	m.Type = errType
	m.Code = code
	m.Data = data
	return m
}
