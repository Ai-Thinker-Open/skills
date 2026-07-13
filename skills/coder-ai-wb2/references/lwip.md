# LwIP Socket API Reference

> Source file: `components/network/lwip/src/include/lwip/sockets.h`  
> LwIP is a lightweight TCP/IP protocol stack. BL602 uses it to provide a standard BSD Socket interface.

---

## Overview

The LwIP Socket API is compatible with the standard POSIX socket interface, supporting TCP, UDP, and RAW IP protocols. BL602 default configuration supports TCP/UDP, but does not support ICMP (ping is implemented via `netutils/ping`).

---

## Common Header Files

```c
#include <lwip/sockets.h>
#include <lwip/netdb.h>
#include <lwip/errno.h>
```

---

## Socket Creation and Destruction

### `socket`

Creates a socket.

```c
int socket(int domain, int type, int protocol);
```

| Parameter | Description |
|-----------|-------------|
| `domain` | `AF_INET` (IPv4) |
| `type` | `SOCK_STREAM` (TCP), `SOCK_DGRAM` (UDP), `SOCK_RAW` (RAW) |
| `protocol` | `0` (auto-select) |

**Return value**: Returns socket descriptor on success, `-1` on failure

---

### `close`

Closes a socket.

```c
int close(int s);
```

---

## Address Binding

### `bind`

Binds an IP address and port.

```c
int bind(int s, const struct sockaddr *name, socklen_t namelen);
```

---

## TCP Connections

### `connect`

Connects to a remote server (TCP).

```c
int connect(int s, const struct sockaddr *name, socklen_t namelen);
```

---

### `listen`

Listens on a port (TCP server).

```c
int listen(int s, int backlog);
```

---

### `accept`

Accepts a client connection.

```c
int accept(int s, struct sockaddr *addr, socklen_t *addrlen);
```

---

## Data Transmission

### `send`

Sends data (TCP).

```c
int send(int s, const void *data, size_t size, int flags);
```

---

### `recv`

Receives data (TCP).

```c
int recv(int s, void *mem, size_t len, int flags);
```

**Return value**: Returns number of bytes on success, `0` means peer closed, `-1` means error

---

### `sendto`

Sends data (UDP).

```c
int sendto(int s, const void *data, size_t size, int flags,
           const struct sockaddr *to, socklen_t tolen);
```

---

### `recvfrom`

Receives data (UDP, can obtain sender address).

```c
int recvfrom(int s, void *mem, size_t len, int flags,
             struct sockaddr *from, socklen_t *fromlen);
```

---

## Read/Write

### `read`

Reads data (TCP/UDP).

```c
int read(int s, void *buf, size_t len);
```

---

### `write`

Writes data (TCP/UDP).

```c
int write(int s, const void *buf, size_t len);
```

---

## Connection Shutdown

### `shutdown`

Closes read/write channels.

```c
int shutdown(int s, int how);
```

| `how` | Description |
|-------|-------------|
| `0` | Close read channel |
| `1` | Close write channel |
| `2` | Close both read and write channels |

---

## Address Conversion

### `inet_pton`

Converts string IP to binary format.

```c
int inet_pton(int af, const char *src, void *dst);
```

| `af` | Description |
|------|-------------|
| `AF_INET` | IPv4 |

---

### `inet_ntop`

Converts binary IP to string format.

```c
const char *inet_ntop(int af, const void *src, char *dst, socklen_t size);
```

---

## Domain Name Resolution

### `gethostbyname`

Gets IP address from domain name.

```c
struct hostent *gethostbyname(const char *name);
```

**Return value**: `struct hostent *`, after success `h_addr_list[0]` is the IP address

---

## Option Settings

### `setsockopt`

Sets socket options.

```c
int setsockopt(int s, int level, int optname, const void *optval, socklen_t optlen);
```

Common options:

| level | optname | Description |
|-------|---------|-------------|
| `SOL_SOCKET` | `SO_KEEPALIVE` | TCP keep-alive |
| `SOL_SOCKET` | `SO_RCVTIMEO` | Receive timeout |
| `SOL_SOCKET` | `SO_SNDTIMEO` | Send timeout |
| `IPPROTO_TCP` | `TCP_NODELAY` | Disable Nagle algorithm |

---

## select Multiplexing

### `select`

Monitors multiple sockets for read/write status.

```c
int select(int nfds, fd_set *readfds, fd_set *writefds,
           fd_set *exceptfds, struct timeval *timeout);
```

---

## Usage Examples

### TCP Client

```c
#include <lwip/sockets.h>

int sock = socket(AF_INET, SOCK_STREAM, 0);
if (sock < 0) return -1;

struct sockaddr_in server;
server.sin_family = AF_INET;
server.sin_port = htons(8080);
inet_pton(AF_INET, "192.168.1.100", &server.sin_addr);

if (connect(sock, (struct sockaddr *)&server, sizeof(server)) < 0) {
    close(sock);
    return -1;
}

// Send data
const char *msg = "Hello\r\n";
send(sock, msg, strlen(msg), 0);

// Receive response
char buf[256];
int len = recv(sock, buf, sizeof(buf) - 1, 0);
if (len > 0) {
    buf[len] = '\0';
    printf("Response: %s\r\n", buf);
}

close(sock);
```

### TCP Server

```c
int server_sock = socket(AF_INET, SOCK_STREAM, 0);

struct sockaddr_in local;
local.sin_family = AF_INET;
local.sin_port = htons(8080);
local.sin_addr.s_addr = INADDR_ANY;
bind(server_sock, (struct sockaddr *)&local, sizeof(local));

listen(server_sock, 5);

while (1) {
    struct sockaddr_in client;
    socklen_t len = sizeof(client);
    int client_sock = accept(server_sock, (struct sockaddr *)&client, &len);

    char buf[256];
    int n = recv(client_sock, buf, sizeof(buf), 0);
    if (n > 0) {
        send(client_sock, buf, n, 0); // Echo back
    }
    close(client_sock);
}
```

### UDP Client

```c
int sock = socket(AF_INET, SOCK_DGRAM, 0);

struct sockaddr_in server;
server.sin_family = AF_INET;
server.sin_port = htons(8888);
inet_pton(AF_INET, "192.168.1.100", &server.sin_addr);

const char *msg = "UDP test\r\n";
sendto(sock, msg, strlen(msg), 0, (struct sockaddr *)&server, sizeof(server));

char buf[256];
struct sockaddr_in from;
socklen_t fromlen = sizeof(from);
int len = recvfrom(sock, buf, sizeof(buf), 0, (struct sockaddr *)&from, &fromlen);

close(sock);
```
