// Copyright © 2019 Vinicius Arcanjo viniarck@gmail.com
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//     http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

package cmd

import (
	"fmt"
	"log"
	"strconv"
	"strings"

	"github.com/spf13/cobra"
	"github.com/viniarck/fluxory/pkg"
)

// serveCmd represents the serve command
var serveCmd = &cobra.Command{
	Use:   "serve",
	Short: "Start the OpenFlow Controller",
	Long:  `Start the OpenFlow Controller`,
	Run: func(cmd *cobra.Command, args []string) {
		versions := make([]int, 0)
		for _, v := range strings.Split(cmd.Flag("versions").Value.String(), ",") {
			val, _ := strconv.Atoi(v)
			versions = append(versions, val)
		}
		rpcEnabled := true
		if cmd.Flag("rpc").Value.String() != "enabled" {
			rpcEnabled = false
		}
		c := pkg.NewController(rpcEnabled, fmt.Sprintf("%s:%s", cmd.Flag("address").Value, cmd.Flag("port").Value.String()), versions...)
		err := c.Run()
		if err != nil {
			log.Fatal(err)
		}
	},
}

func init() {
	rootCmd.AddCommand(serveCmd)

	serveCmd.PersistentFlags().StringP("address", "a", "localhost", "OpenFlow TCP address")
	serveCmd.PersistentFlags().UintP("port", "p", 6653, "OpenFlow TCP port")
	serveCmd.PersistentFlags().StringP("versions", "v", "4,6", "Supported versions")
	// for some reason BoolP was not working as expected, investigate later, using StringP for now
	serveCmd.PersistentFlags().StringP("rpc", "r", "enabled", "RPC methods")
}
