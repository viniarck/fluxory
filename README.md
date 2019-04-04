
![fluxory](
https://lh3.googleusercontent.com/uccVAZW63u72EAUsQ-SSGIuQD8bf7-2lITgrhXQ6X2ZwyT0hN3yH2DJwZ43kJTLp5JDXzYD-_XQkddc5UCoeRyVvlqgx5X_UtnXndyGVKYAIJrRsnzP9vVyNRlmM4nDl1IuXCCLXUj9WZRrYqzJZ0g8FK_FbNphNkEvuKNiv2I4A_uflpF2euuEjtLWuwm18GB9uoByvhWxVUmEgZHKBMWkFw_aR0sNgRbjtgKCJlQOqjAWyvdgZbhhh5SYJ2IXQk3XV814cTq419wyZtX1SDEWX_bpAjqB1HyAzVJEbdEsp-R5qPHG6eLYcpJXJ8Td1VG1Kg_Mal6uGzIw7MOBKash3_E0XEjlnNdV3EDRNgiXzn9WId5UQm7InkeHFjvn-onG13v0NMr_nf9BRLgQNbycahiEmCyaJfOtobBcNXi5MYpfQ77ICZ7VJTeMNiy7js4pgHACDkCw6rXmmKlNJj1lxFs4ZsvFXyX77yZGQdEX_cJnU834sjDhyO1GKihDcFY0QUHfoBwcNPsRstnN8osbnvTWhHFsl5HvF5Fp_oQZHigSX4kk-IANA6v8ds63CgC7K1qHdIKBSWmOEonqbUgsqwAnUnKEJxQuU9cciAfVAxyGT4y3gJMOnHZnDG5jzAUEd-m1eF8jb05WGuEjWRg5KiaHpHA=w500-h180-no)

Asynchronous high-performance distributed OpenFlow 1.3/1.5 platform in Go and Python.

## Major Features

- Distributed computing
- Reliable queueing and asynchronous OpenFlow events notification
- Applications are written in either Go or Python (asyncio)

## Docs

Fluxory is still under heavy development I'm working in the CI/CD pipeline and docs. Meanwhile, you can check the source code or the examples below:

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
