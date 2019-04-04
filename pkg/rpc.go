package pkg

import (
	"encoding/json"

	log "github.com/sirupsen/logrus"
	"github.com/streadway/amqp"
)

type BrokerHandler struct {
	fullAddress string
}

type RPCResponse struct {
	Result interface{} `json:"result"`
	Error  string      `json:"error"`
}

type RPCRequest struct {
	Dpid    int    `json:"dpid"`
	Payload []byte `json:"payload"`
}

func EncodeResponse(resp *RPCResponse) ([]byte, error) {
	res, err := json.Marshal(resp)
	return res, err
}

func NewBrokerHandler() BrokerHandler {
	return BrokerHandler{"amqp://guest:guest@localhost:5672/"}
}

func (b BrokerHandler) NewRPCQueue(name string) (*amqp.Channel, <-chan amqp.Delivery, error) {

	log.Infof("Registering RPC method %s", name)
	conn, err := amqp.Dial(b.fullAddress)
	if err != nil {
		return nil, nil, err
	}

	ch, err := conn.Channel()
	if err != nil {
		return nil, nil, err
	}

	q, err := ch.QueueDeclare(
		name,  // name
		false, // durable
		false, // delete when usused
		false, // exclusive
		false, // no-wait
		nil,   // arguments
	)
	if err != nil {
		return nil, nil, err
	}

	err = ch.Qos(
		1,     // prefetch count
		0,     // prefetch size
		false, // global
	)
	if err != nil {
		return nil, nil, err
	}

	msgs, err := ch.Consume(
		q.Name, // queue
		"",     // consumer
		false,  // auto-ack
		false,  // exclusive
		false,  // no-local
		false,  // no-wait
		nil,    // args
	)
	return ch, msgs, err
}
