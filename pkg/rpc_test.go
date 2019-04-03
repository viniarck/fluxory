package pkg

import (
	"encoding/json"
	"testing"

	"github.com/stretchr/testify/assert"
)

func TestRPCResponse(t *testing.T) {
	assert := assert.New(t)

	m := make(map[string]interface{})
	m["foo"] = float64(1)
	resp := RPCResponse{m, ""}
	marshalled, err := json.Marshal(resp)
	assert.Nil(err)

	var rpcResp RPCResponse
	err = json.Unmarshal(marshalled, &rpcResp)
	assert.Nil(err)
	assert.Equal(resp.Error, rpcResp.Error)
	if res, ok := resp.Result.(map[string][]uint64); ok {
		assert.Equal(m["foo"], res["foo"])
	}
}
