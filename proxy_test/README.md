# Proxy test

## Using the docker containers

I've set up a docker-compose script to spin up a few containers:

- **server**: Runs `proxy_test.py` as a server
- **client-a**: Runs `proxy_test.py` as a proxy client, connected to the
  **server**
- **client-b**: Runs `proxy_test.py` as a proxy client, connected to
  **client-a**

The following commands expect to be run from the directory containing the
`docker-compose.yml` file.

**Starting the containers**:
   > `docker-compose up`

**View running containers**:
   > `docker-compose ps`

**Connect tty to a running container**:
   > `docker attach <container-name>`

**Detach tty from a running container**:
   > ctrl+p, ctrl+q

**View the networks**:
   > `docker network ls`

**View container IPs**:
   > `docker network inspect -f '{{range .Containers}}{{println .Name .IPv4Address}}{{end}}' <network-name>`

## Example

### Start the containers

```shell
$ docker-compose up
Starting proxy_test_server_1 ... done
Starting proxy_test_client-a_1 ... done
Starting proxy_test_client-b_1 ... done
Attaching to proxy_test_server_1, proxy_test_client-a_1, proxy_test_client-b_1
client-a_1  | INFO:root:Starting the client.
client-a_1  | INFO:root:Connected to the server.
client-a_1  | INFO:root:Now for some user input.
client-a_1  | Send some data: INFO:root:Creating a socket to listen on 5af56f72e34e:5000
client-a_1  | INFO:root:Waiting for clients on 5af56f72e34e:5000
server_1    | INFO:root:Starting the server.
server_1    | INFO:root:Creating a socket to listen on server:5000
client-b_1  | INFO:root:Starting the client.
client-b_1  | INFO:root:Connected to the server.
client-b_1  | INFO:root:Now for some user input.
client-b_1  | Send some data: INFO:root:Creating a socket to listen on 622159bd1100:5000
client-b_1  | INFO:root:Waiting for clients on 622159bd1100:5000
```

### List running containers (new terminal)

```shell
$ docker-compose ps
        Name                   Command           State           Ports
-------------------------------------------------------------------------------
proxy_test_client-a_1   python3                  Up      0.0.0.0:49273->5000/tc
                        /source/proxy_test ...           p,:::49273->5000/tcp
proxy_test_client-b_1   python3                  Up      0.0.0.0:49274->5000/tc
                        /source/proxy_test ...           p,:::49274->5000/tcp
proxy_test_server_1     python3                  Up      0.0.0.0:49272->5000/tc
                        /source/proxy_test ...           p,:::49272->5000/tcp
```


### Connect to the server container

```shell
$ docker attach proxy_test_server_1

```


### Connect to client-a container (new terminal)

```shell
$ docker attach proxy_test_client-a_1

Send some data:
```

### Send data to the server

```shell
# From the client-a container:
Send some data: Hello from client-a!
Send some data:

# Observe the following from the server container:
('172.20.0.3', 34400):
        Hello from client-a!
```

### List networks

```shell
$ docker network ls
NETWORK ID     NAME                       DRIVER    SCOPE
7e408a43a6da   bridge                     bridge    local
91ee094c4219   host                       host      local
df235ebcc01b   infection_monkey_default   bridge    local
bd2654697cf8   none                       null      local
960a8a81c19d   proxy_test_default         bridge    local
```

### List IPs in the compose network

```shell
$ docker network inspect -f '{{range .Containers}}{{println .Name .IPv4Address}}{{end}}' proxy_test_default
proxy_test_client-a_1 172.20.0.3/16
proxy_test_client-b_1 172.20.0.4/16
proxy_test_server_1 172.20.0.2/16
```

### Use `netcat` to send data to the **server** via **client-a**

```shell
# From docker host machine. Note that we use client-a's IP here:
$ echo "Hello from netcat!" | nc 172.20.0.3 5000

# Observe the following from the server container:
('172.20.0.3', 34400):
        Hello from netcat!
```
