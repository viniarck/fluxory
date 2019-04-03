package ofp13

import (
	"github.com/viniarck/fluxory/pkg/ofp"
)

func NewHello(xid uint32) *ofp.Hello {
	// TODO replace this init
	hello := new(ofp.Hello)
	hello.Elements[0] = *ofp.NewHelloElement(OFPP_V13)
	hello.Header = ofp.Header{OFPP_V13, OFPT_HELLO, hello.Size(), xid}
	return hello
}
