package pkg

import (
	"net"
	"time"

	log "github.com/sirupsen/logrus"
	"github.com/viniarck/fluxory/pkg/ofp"
)

type XidPair struct {
	NetAddress string
	Xid        uint32
}

type XidResp struct {
	Type uint8
	Sent time.Time
	Chan chan bool
}

type Switch struct {
	Dpid       uint64
	OFPVersion uint
	LastSeen   time.Time
	LowestRes  time.Duration
	HSStatus   HandshakeStatus
}

type SwitchConn struct {
	Switch
	NetAddress string
	C          net.Conn
	Xid        uint32
	RespSecs   float32
}

func (sw *SwitchConn) Write(m ofp.OFPMessage) (uint32, uint8, error) {
	xid := m.GetXid()
	if xid == 0 {
		sw.Xid += 1 % ofp.OFPP_MAX
		m.SetXid(sw.Xid)
		xid = sw.Xid
	} else {
		m.SetXid(xid)
	}
	_, err := sw.C.Write(m.Encode())
	if err != nil {
		log.Error(err)
	}
	return xid, m.GetType(), err
}

func (sw *SwitchConn) WriteRaw(b []byte) error {
	_, err := sw.C.Write(b)
	return err
}

func (sw *SwitchConn) UpdateRespTime(t *time.Time) {
	dur := time.Since(*t)
	if dur < sw.LowestRes || sw.LowestRes == 0 {
		sw.LowestRes = dur
	}
}

type HandshakeStatus int

const (
	Incomplete HandshakeStatus = iota
	Complete
)

func (s HandshakeStatus) String() string {
	strings := [...]string{"Incomplete", "Complete"}
	if s < Incomplete || s > Complete {
		return "Unknown"
	}
	return strings[s]
}
