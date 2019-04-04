package pkg

import (
	"encoding/json"
	"time"

	log "github.com/sirupsen/logrus"
	"github.com/streadway/amqp"
	"github.com/viniarck/fluxory/pkg/ofp"
	"github.com/viniarck/fluxory/pkg/ofp13"
	"github.com/viniarck/fluxory/pkg/ofp15"
)

type Controller struct {
	TCPServer
	versions  map[int]int
	xidsOut   map[XidPair]XidResp
	bh        BrokerHandler
	enableRPC bool
}

func NewController(enableRPC bool, netAddress string, versions ...int) Controller {
	vmap := make(map[int]int, len(versions))
	for _, v := range versions {
		vmap[v] = v
	}
	const (
		xidInitialCap int = 1000
	)
	xidsOut := make(map[XidPair]XidResp, xidInitialCap)
	return Controller{NewTCPServer(netAddress), vmap, xidsOut, NewBrokerHandler(), enableRPC}
}

func (c *Controller) Versions() []int {
	keys := make([]int, len(c.versions))
	count := 0
	for k := range c.versions {
		keys[count] = k
		count += 1
	}
	return keys
}

func (c *Controller) GetDpids() []uint64 {
	keys := make([]uint64, len(c.Dpids))
	count := 0
	for i := range c.Dpids {
		keys[count] = i
		count += 1
	}
	return keys
}

func (c *Controller) startHandshake(sw *SwitchConn, version uint8) {
	log.Infof("Starting OFP Handshake with %v", sw.NetAddress)
	c.sendHello(sw, version)
	c.sendFeaReq(sw, version)
}

func (c *Controller) sendHello(sw *SwitchConn, version uint8) {
	xid, msgType, err := sw.Write(ofp.NewHello(version, uint32(0)))
	c.writeXidsOut(xid, msgType, sw, err)
}

func (c *Controller) sendFeaReq(sw *SwitchConn, version uint8) {
	xid, msgType, err := sw.Write(ofp.NewFeaturesRequest(version, uint32(0)))
	c.writeXidsOut(xid, msgType, sw, err)
}

func (c *Controller) sendEcho(sw *SwitchConn, version uint8) {
	xid, msgType, err := sw.Write(ofp.NewEchoReply(version, uint32(0)))
	c.writeXidsOut(xid, msgType, sw, err)
}

func (c *Controller) writeXidsOut(xid uint32, msgType uint8, sw *SwitchConn, err error) (chan bool, error) {
	if err != nil {
		return nil, err
	}
	ch := make(chan bool, 1)
	c.xidsOut[XidPair{sw.NetAddress, xid}] = XidResp{ofp.ExpectedType(msgType), time.Now(), ch}
	return ch, nil
}

func (c *Controller) handleFeaReply(sw *SwitchConn, version uint8, data []byte) {
	if version == ofp.OFPP_V13 {
		h := ofp13.NewFeaturesReply(uint32(0))
		err := h.Decode(data)
		if err != nil {
			log.Error(err)
			return
		}
		sw.Dpid = h.Dpid
		sw.HSStatus = Complete
	} else if version == ofp.OFPP_V15 {
		h := ofp15.NewFeaturesReply(uint32(0))
		err := h.Decode(data)
		if err != nil {
			log.Error(err)
			return
		}
		sw.Dpid = h.Dpid
		sw.HSStatus = Complete
	}
	c.Dpids[sw.Dpid] = sw
	log.Infof("Completed OFP Handshake with %v dpid %v", sw.NetAddress, sw.Dpid)
}

func (c Controller) Run() error {
	log.Infof("Starting OpenFlow Controller supporting versions:  %v", c.Versions())
	go c.fetchInQueue()
	var err error
	if c.enableRPC {
		err = c.registerRPCMethods()
	}
	if err != nil {
		log.Fatalf("%v", err)
	}
	err = c.ServeForever()
	// TODO stop goroutines..
	return err
}

func (c Controller) registerRPCMethods() error {
	log.Info("Registering RPC methods")
	err := c.listSwitchesRPC()
	if err != nil {
		return err
	}
	err = c.WriteDpidRPC()
	if err != nil {
		return err
	}
	return nil
}

func (c Controller) listSwitchesRPC() error {
	name := "list_switches"
	ch, msgs, err := c.bh.NewRPCQueue(name)
	if err != nil {
		log.Errorf("RPC method %s failedto register", name)
		return err
	}
	go func() {
		for d := range msgs {
			log.Debugf("Body: %s", string(d.Body))
			log.Debugf("ReplyTo: %s", string(d.ReplyTo))
			respData := make(map[string][]uint64)
			respData["dpids"] = c.GetDpids()
			log.Debug("Dpids: ", c.GetDpids())
			jsonResponse, err := json.Marshal(RPCResponse{Result: respData})
			if err != nil {
				log.Error(err)
			}
			log.Debugf("resp: %s", string(jsonResponse))
			err = ch.Publish(
				"",        // exchange
				d.ReplyTo, // routing key
				true,      // mandatory
				false,     // immediate
				amqp.Publishing{
					ContentType:   "application/json",
					CorrelationId: d.CorrelationId,
					Body:          jsonResponse,
					ReplyTo:       d.ReplyTo,
					DeliveryMode:  1,
					Type:          "result",
				})
			if err != nil {
				log.Errorf("RPC method %s failed to publish a message", name)
			}
			d.Ack(false)
		}
	}()
	return nil
}

func (c Controller) WriteDpidRPC() error {
	name := "write_dpid"
	ch, msgs, err := c.bh.NewRPCQueue(name)
	if err != nil {
		log.Errorf("RPC method %s failedto register", name)
		return err
	}
	go func() {
		for d := range msgs {
			log.Debugf("Body: %s", string(d.Body))
			log.Debugf("ReplyTo: %s", string(d.ReplyTo))

			var rpcRes RPCRequest
			err = json.Unmarshal(d.Body, &rpcRes)
			if err != nil {
				log.Errorf("Couldn't Unmarshal %v", d.Body)
				continue
			}
			dpid := rpcRes.Dpid
			var swConn *SwitchConn
			if sw, ok := c.Dpids[uint64(dpid)]; ok {
				swConn = sw
			} else {
				log.Errorf("Dpid %v not found", dpid)
				continue
			}
			ofpMsg := ofp.Header{}
			err := ofpMsg.Decode(rpcRes.Payload)
			if err != nil {
				log.Errorf("Couldn't decode message %v", d.Body)
				continue
			}

			log.Infof("Header %v jsonRes %v", ofpMsg, rpcRes)
			err = swConn.WriteRaw(rpcRes.Payload)
			if err != nil {
				log.Errorf("Couldn't write raw bytes, error: %v", err)
				continue
			}
			wCh, err := c.writeXidsOut(ofpMsg.Xid, ofpMsg.Type, swConn, err)
			if err != nil {
				continue
			}

			rpcResponse := RPCResponse{Result: "", Error: ""}
			var resFinal bool
			select {
			case resFinal = <-wCh:
				if !resFinal {
					rpcResponse.Error = "Timeout"
				}
			case <-time.After(swConn.LowestRes + swConn.LowestRes):
				rpcResponse.Error = "Timeout"
			}
			jsonResponse, err := json.Marshal(rpcResponse)
			if err != nil {
				log.Error(err)
			}

			err = ch.Publish(
				"",        // exchange
				d.ReplyTo, // routing key
				true,      // mandatory
				false,     // immediate
				amqp.Publishing{
					ContentType:   "application/json",
					CorrelationId: d.CorrelationId,
					Body:          jsonResponse,
					ReplyTo:       d.ReplyTo,
					DeliveryMode:  1,
					Type:          "result",
				})
			if err != nil {
				log.Errorf("RPC method %s failed to publish a message", name)
			}
			d.Ack(false)
		}
	}()
	return nil
}

func (c Controller) showSwitches() {
	for k, v := range c.Clients {
		log.Debugf("Switch %v, Status %s LowestRes %v", k, v.HSStatus, v.LowestRes)
	}
}

func (c Controller) fetchInQueue() {
	log.Info("Starting to fetch OpenFlow messages")
	var (
		ofpMsg  ofp.Header
		sw      *SwitchConn
		err     error
		ok      bool
		xidPair *XidPair
	)
	xidPair = &XidPair{}
	for {
		msg := <-c.inQueue
		log.Debugf("Got message %v", msg)
		err = ofpMsg.Decode(msg.Data)
		if err != nil {
			log.Errorf("Couldn't decode %v from %v ", msg.Data, msg.Client)
			continue
		}
		if sw, ok = c.Clients[msg.Client]; !ok {
			continue
		}
		xidPair.NetAddress, xidPair.Xid = msg.Client, ofpMsg.Xid
		switch ofpMsg.Type {
		case ofp.OFPT_HELLO:
			if sw.HSStatus == Incomplete {
				c.startHandshake(sw, ofpMsg.Version)
			}
		case ofp.OFPT_ECHO_REQUEST:
			c.sendEcho(sw, ofpMsg.Version)
		case ofp.OFPT_FEATURES_REPLY:
			c.handleFeaReply(sw, ofpMsg.Version, msg.Data)
		default:
			log.Debugf("Message type %v doesn't have a parser yet. Received from %v", ofpMsg.Type, msg.Client)
		}
		if res, ok := c.xidsOut[*xidPair]; ok {
			if ofpMsg.Type == res.Type {
				res.Chan <- true
			} else {
				res.Chan <- false
			}
			log.Debugf("Found it %v!", res)
			sw.UpdateRespTime(&res.Sent)
			delete(c.xidsOut, *xidPair)
		}
		sw.LastSeen = time.Now()
		c.showSwitches()
	}
}
