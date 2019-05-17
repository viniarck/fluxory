[![pipeline status](https://gitlab.com/viniarck/fluxory/badges/master/pipeline.svg)](https://gitlab.com/viniarck/fluxory/commits/master)

![fluxory](
https://lh3.googleusercontent.com/uccVAZW63u72EAUsQ-SSGIuQD8bf7-2lITgrhXQ6X2ZwyT0hN3yH2DJwZ43kJTLp5JDXzYD-_XQkddc5UCoeRyVvlqgx5X_UtnXndyGVKYAIJrRsnzP9vVyNRlmM4nDl1IuXCCLXUj9WZRrYqzJZ0g8FK_FbNphNkEvuKNiv2I4A_uflpF2euuEjtLWuwm18GB9uoByvhWxVUmEgZHKBMWkFw_aR0sNgRbjtgKCJlQOqjAWyvdgZbhhh5SYJ2IXQk3XV814cTq419wyZtX1SDEWX_bpAjqB1HyAzVJEbdEsp-R5qPHG6eLYcpJXJ8Td1VG1Kg_Mal6uGzIw7MOBKash3_E0XEjlnNdV3EDRNgiXzn9WId5UQm7InkeHFjvn-onG13v0NMr_nf9BRLgQNbycahiEmCyaJfOtobBcNXi5MYpfQ77ICZ7VJTeMNiy7js4pgHACDkCw6rXmmKlNJj1lxFs4ZsvFXyX77yZGQdEX_cJnU834sjDhyO1GKihDcFY0QUHfoBwcNPsRstnN8osbnvTWhHFsl5HvF5Fp_oQZHigSX4kk-IANA6v8ds63CgC7K1qHdIKBSWmOEonqbUgsqwAnUnKEJxQuU9cciAfVAxyGT4y3gJMOnHZnDG5jzAUEd-m1eF8jb05WGuEjWRg5KiaHpHA=w500-h180-no)

Asynchronous high-performance distributed OpenFlow 1.3/1.5 framework in Go and Python.

## Goals

- Distributed OpenFlow framework leveraging multiple CPU cores.
- Be faster than Ryu in terms of serialization/deserialization of messages.

## Major Features

- Distributed computing
- Reliable queueing and asynchronous OpenFlow events notification
- Applications are written in either Go or Python (asyncio)

## Examples

- [simple_switch.py](./examples/simple_switch.py)

## Running the server OpenFlow (fluxory)

- Build the binary first:

```
mkdir bin
go build -ldflags "-s -w" -o bin/fluxory
```

- Compose up rabbitmq:

```
docker-compose up -d
```

- Run it:

```
./bin/fluxory
```

## Benchmarks

The following benchmarks compare these two code snippets written in Go and Python, they both serialize 10 million OpenFlow Hello messages:

```go
package main

import "github.com/viniarck/fluxory/pkg/ofp15"

func main() {
	for i := 0; i < 1000*10000; i++ {
		ofp15.NewHello(ofp15.OFPP_V15).Encode()
	}
}
```

```python
#!/usr/bin/env python
# -*- coding: utf-8 -*-
from ryu.ofproto import ofproto_v1_5_parser


def main() -> None:
    """Main function."""
    for i in range(1000 * 10000):
        ofproto_v1_5_parser.OFPHello().serialize()


if __name__ == "__main__":
    main()
```

The benchmark was run with [hyperfine](https://github.com/sharkdp/hyperfine), Go 1.12, and Python 3.7.3, on my laptop, as you can see the Go code is more than 3 times faster as expected:

```
❯ hyperfine './bench'
  Time (mean ± σ):      9.608 s ±  0.474 s    [User: 9.694 s, System: 0.035 s]
  Range (min … max):    9.085 s … 10.395 s    10 runs
```

```
❯ hyperfine 'python bench.py'
  Time (mean ± σ):     35.028 s ±  0.959 s    [User: 34.938 s, System: 0.021 s]
  Range (min … max):   34.015 s … 36.617 s    10 runs
```
