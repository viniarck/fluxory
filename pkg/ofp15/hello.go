package ofp15

import (
	"github.com/viniarck/fluxory/pkg/ofp"
)

func NewHello(xid uint32) *ofp.Hello {
	hello := new(ofp.Hello)
	hello.Elements[0] = *ofp.NewHelloElement(OFPP_V15)
	hello.Header = ofp.Header{OFPP_V15, OFPT_HELLO, hello.Size(), xid}
	return hello
}
