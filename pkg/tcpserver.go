package pkg

import (
	"bufio"
	"net"

	log "github.com/sirupsen/logrus"
	"github.com/viniarck/fluxory/pkg/ofp"
)

type Message struct {
	Client string
	Data   []byte
}

type TCPServer struct {
	netAddress string
	Clients    map[string]*SwitchConn
	Dpids      map[uint64]*SwitchConn
	inQueue    chan Message
}

func NewTCPServer(netAddress string) TCPServer {
	const (
		initialCap int = 100
	)
	return TCPServer{netAddress, make(map[string]*SwitchConn, initialCap), make(map[uint64]*SwitchConn), make(chan Message)}
}

func (s TCPServer) ServeForever() (err error) {
	log.Infof("TCP Server is listening at %s", s.netAddress)
	l, err := net.Listen("tcp4", s.netAddress)
	if err != nil {
		defer l.Close()
		log.Error(err)
		return err
	}
	defer l.Close()
	for {
		var c net.Conn
		c, err = l.Accept()
		if err != nil {
			log.Error(err)
			return
		}
		go s.handleConnection(c)
	}
}

func (s *TCPServer) DelSwitch(sw *SwitchConn) {
	delete(s.Dpids, sw.Dpid)
	delete(s.Clients, sw.NetAddress)
	sw.C.Close()
}

func (s TCPServer) handleConnection(c net.Conn) {
	client := c.RemoteAddr().String()
	log.Infof("Client %s connected!\n", client)

	sConn := SwitchConn{Switch: Switch{}, NetAddress: client, C: c}
	s.Clients[client] = &sConn
	// TODO maybe just deactivate and leave as the status as incomplete?
	defer s.DelSwitch(&sConn)
	const (
		OFP_HEADER_SIZE int = 8
		// TODO double check for the highest size...
		OFP_HIGHEST_LEN int = 32
	)
	// TODO release the minimal core asap and finish up typing with pyre monekeypyre on fluxory-py
	// TODO implement duration...
	data := make([]byte, OFP_HIGHEST_LEN)
	var msg *ofp.Header
	for {
		n, err := bufio.NewReader(c).Read(data)
		// log.Debugf("data: %v received from %s", data, client)
		if n < OFP_HEADER_SIZE && err == nil {
			log.Errorf("Bad packet size %d received from %s", n, client)
			return
		}
		if err != nil {
			switch err.Error() {
			case "EOF":
				log.Errorf("Client %s disconnected!\n", client)
			default:
				log.Errorf("%s", err.Error())
			}
			return
		}

		msg = &ofp.Header{}
		err = msg.Decode(data)
		if err != nil {
			log.Errorf("Error: %v, client: %v", err, client)
			continue
		}
		if !(msg.Version == ofp.OFPP_V13 || msg.Version == ofp.OFPP_V15) {
			log.Errorf("Unsupported version: %v, client: %v", msg.Version, client)
			continue
		}
		// TODO check for supported msg types
		go func() {
			s.inQueue <- Message{client, data}
		}()
	}
}
