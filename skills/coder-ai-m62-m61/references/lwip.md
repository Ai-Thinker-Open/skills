# LwIP TCP/IP Stack API Reference (BL616/BL618)

## Overview

LwIP (Lightweight IP) is a widely used open-source TCP/IP stack designed for embedded systems. This document covers the key APIs from `bouffalo_sdk/components/net/lwip/lwip/include/lwip/` for BL616/BL618 chips.

## Header Files

| Header | Purpose |
|--------|---------|
| `lwip/tcpip.h` | TCP/IP thread initialization and synchronization |
| `lwip/netif.h` | Network interface definition and management |
| `lwip/netifapi.h` | Thread-safe netif operations (from non-TCPIP threads) |
| `lwip/sockets.h` | Berkeley-style socket API |
| `lwip/udp.h` | UDP protocol control block |
| `lwip/tcp.h` | TCP protocol control block |
| `lwip/ip_addr.h` | IP address types (IPv4/IPv6) |

---

## 1. TCP/IP Stack Initialization

### tcpip_init()

```c
void tcpip_init(tcpip_init_done_fn tcpip_init_done, void *arg);
```

Initializes the LwIP TCP/IP stack and creates the TCPIP thread.

**Parameters:**
- `tcpip_init_done` - Callback function called after initialization completes
- `arg` - User argument passed to the callback

**Example:**
```c
static void lwip_init_done(void *arg)
{
    printf("LwIP initialized\r\n");
    // Start network operations here
}

void app_main(void)
{
    tcpip_init(lwip_init_done, NULL);
}
```

### Core Locking Macros

```c
LOCK_TCPIP_CORE();   // Lock lwIP core mutex
UNLOCK_TCPIP_CORE(); // Unlock lwIP core mutex
```
**Note:** Requires `LWIP_TCPIP_CORE_LOCKING := 1` in lwipopts.h

---

## 2. Network Interface API

### netif_add()

Adds a network interface to the stack.

```c
struct netif *netif_add(struct netif *netif,
                        const ip4_addr_t *ipaddr, 
                        const ip4_addr_t *netmask, 
                        const ip4_addr_t *gw,
                        void *state, 
                        netif_init_fn init, 
                        netif_input_fn input);
```

**Parameters:**
| Parameter | Description |
|-----------|-------------|
| `netif` | Pointer to netif structure to populate |
| `ipaddr` | IP address (e.g., `IP4_ADDR(192, 168, 1, 100)`) |
| `netmask` | Subnet mask (e.g., `IP4_ADDR(255, 255, 255, 0)`) |
| `gw` | Gateway IP address |
| `state` | User-specific state pointer (e.g., device handle) |
| `init` | Initialization function for the interface |
| `input` | Input function to pass received packets to stack |

**Returns:** Pointer to the newly added netif, or NULL on failure.

### netifapi_netif_add() (Thread-Safe)

Thread-safe version for calling from non-TCPIP threads:

```c
err_t netifapi_netif_add(struct netif *netif,
#if LWIP_IPV4
                         const ip4_addr_t *ipaddr, 
                         const ip4_addr_t *netmask, 
                         const ip4_addr_t *gw,
#endif
                         void *state, 
                         netif_init_fn init, 
                         netif_input_fn input);
```

### Key netif Functions

| Function | Description |
|----------|-------------|
| `netif_set_default(struct netif *netif)` | Set interface as default route |
| `netif_set_up(struct netif *netif)` | Enable interface |
| `netif_set_down(struct netif *netif)` | Disable interface |
| `netif_set_link_up(struct netif *netif)` | Mark link as up |
| `netif_set_link_down(struct netif *netif)` | Mark link as down |
| `netif_remove(struct netif *netif)` | Remove interface |
| `netif_find(const char *name)` | Find interface by name (e.g., "et0") |

### netif Flags

```c
#define NETIF_FLAG_UP           0x01U  // Interface is enabled
#define NETIF_FLAG_BROADCAST    0x02U  // Broadcast capability
#define NETIF_FLAG_LINK_UP      0x04U  // Link is up
#define NETIF_FLAG_ETHARP       0x08U  // Ethernet with ARP
#define NETIF_FLAG_ETHERNET     0x10U  // Ethernet device
#define NETIF_FLAG_IGMP         0x20U  // IGMP capable
#define NETIF_FLAG_MLD6         0x40U  // MLD6 capable
```

---

## 3. Socket API

The socket API provides Berkeley-style sockets for application networking.

### socket()

```c
int lwip_socket(int domain, int type, int protocol);
```

**Parameters:**
- `domain` - `AF_INET` (IPv4) or `AF_INET6` (IPv6)
- `type` - `SOCK_STREAM` (TCP), `SOCK_DGRAM` (UDP), `SOCK_RAW`
- `protocol` - Usually `0`, or specific protocol like `IPPROTO_TCP`

**Returns:** Socket file descriptor, or negative on error.

### bind()

```c
int lwip_bind(int s, const struct sockaddr *name, socklen_t namelen);
```

Binds socket to a local address and port.

**Example:**
```c
struct sockaddr_in local_addr;
memset(&local_addr, 0, sizeof(local_addr));
local_addr.sin_family = AF_INET;
local_addr.sin_port = htons(8080);
local_addr.sin_addr.s_addr = INADDR_ANY;

int ret = bind(sock, (struct sockaddr *)&local_addr, sizeof(local_addr));
```

### connect()

```c
int lwip_connect(int s, const struct sockaddr *name, socklen_t namelen);
```

Connects to a remote address (for UDP) or initiates TCP connection.

**Example (TCP):**
```c
struct sockaddr_in server_addr;
memset(&server_addr, 0, sizeof(server_addr));
server_addr.sin_family = AF_INET;
server_addr.sin_port = htons(80);
inet_aton("192.168.1.1", &server_addr.sin_addr);

int ret = connect(sock, (struct sockaddr *)&server_addr, sizeof(server_addr));
```

### send()

```c
ssize_t lwip_send(int s, const void *dataptr, size_t size, int flags);
```

Sends data on a connected socket.

**Parameters:**
- `s` - Socket descriptor
- `dataptr` - Pointer to data buffer
- `size` - Number of bytes to send
- `flags` - Usually `0`, or `MSG_DONTWAIT` for non-blocking

**Returns:** Number of bytes sent, or negative on error.

### recv()

```c
ssize_t lwip_recv(int s, void *mem, size_t len, int flags);
```

Receives data from a socket.

**Parameters:**
- `s` - Socket descriptor
- `mem` - Buffer to store received data
- `len` - Maximum bytes to receive
- `flags` - Usually `0`, or `MSG_PEEK` to peek without consuming

**Returns:** Number of bytes received, 0 on connection close, or negative on error.

### sendto() / recvfrom()

For unconnected sockets (UDP):

```c
ssize_t lwip_sendto(int s, const void *dataptr, size_t size, int flags,
                    const struct sockaddr *to, socklen_t tolen);

ssize_t lwip_recvfrom(int s, void *mem, size_t len, int flags,
                      struct sockaddr *from, socklen_t *fromlen);
```

### listen() / accept() (TCP Server)

```c
int lwip_listen(int s, int backlog);  // Enable listening, backlog = pending connections
int lwip_accept(int s, struct sockaddr *addr, socklen_t *addrlen);  // Accept connection
```

### close()

```c
int lwip_close(int s);  // or closesocket(s)
```

Closes a socket.

### setsockopt() / getsockopt()

```c
int lwip_setsockopt(int s, int level, int optname, const void *optval, socklen_t optlen);
int lwip_getsockopt(int s, int level, int optname, void *optval, socklen_t *optlen);
```

**Common Options:**

| Level | Option | Description |
|-------|--------|-------------|
| `SOL_SOCKET` | `SO_REUSEADDR` | Allow address reuse |
| `SOL_SOCKET` | `SO_KEEPALIVE` | Keep connections alive |
| `SOL_SOCKET` | `SO_RCVTIMEO` | Receive timeout |
| `SOL_SOCKET` | `SO_SNDTIMEO` | Send timeout |
| `IPPROTO_TCP` | `TCP_NODELAY` | Disable Nagle algorithm |

---

## 4. UDP API

Direct UDP PCB (Protocol Control Block) API for lower-level control.

### UDP PCB Functions

| Function | Description |
|----------|-------------|
| `udp_new()` | Create new UDP PCB |
| `udp_remove(struct udp_pcb *pcb)` | Remove UDP PCB |
| `udp_bind(struct udp_pcb *pcb, const ip_addr_t *ipaddr, u16_t port)` | Bind to local IP/port |
| `udp_connect(struct udp_pcb *pcb, const ip_addr_t *ipaddr, u16_t port)` | Set remote address |
| `udp_disconnect(struct udp_pcb *pcb)` | Clear remote address |
| `udp_send(struct udp_pcb *pcb, struct pbuf *p)` | Send UDP datagram |
| `udp_recv(struct udp_pcb *pcb, udp_recv_fn recv, void *recv_arg)` | Set receive callback |

### UDP Callback Type

```c
typedef void (*udp_recv_fn)(void *arg, struct udp_pcb *pcb, struct pbuf *p,
                            const ip_addr_t *addr, u16_t port);
```

### UDP Flags

```c
#define UDP_FLAGS_NOCHKSUM       0x01U  // Skip checksum
#define UDP_FLAGS_UDPLITE       0x02U  // UDP-Lite mode
#define UDP_FLAGS_CONNECTED     0x04U  // Remote address set
#define UDP_FLAGS_MULTICAST_LOOP 0x08U // Loopback multicast
```

---

## 5. TCP API

Direct TCP PCB API for connection-oriented communication.

### TCP PCB Functions

| Function | Description |
|----------|-------------|
| `tcp_new()` | Create new TCP PCB |
| `tcp_close(struct tcp_pcb *pcb)` | Close connection gracefully |
| `tcp_abort(struct tcp_pcb *pcb)` | Abort connection immediately |
| `tcp_bind(struct tcp_pcb *pcb, const ip_addr_t *ipaddr, u16_t port)` | Bind to local IP/port |
| `tcp_connect(struct tcp_pcb *pcb, const ip_addr_t *ipaddr, u16_t port, tcp_connected_fn connected)` | Connect to remote host |
| `tcp_listen(struct tcp_pcb *pcb)` | Start listening (returns listen PCB) |
| `tcp_write(struct tcp_pcb *pcb, const void *dataptr, u16_t len, u8_t apiflags)` | Queue data for sending |
| `tcp_output(struct tcp_pcb *pcb)` | Send queued data |
| `tcp_recved(struct tcp_pcb *pcb, u16_t len)` | Acknowledge received data |

### TCP Callback Types

```c
typedef err_t (*tcp_accept_fn)(void *arg, struct tcp_pcb *newpcb, err_t err);
typedef err_t (*tcp_recv_fn)(void *arg, struct tcp_pcb *tpcb, struct pbuf *p, err_t err);
typedef err_t (*tcp_sent_fn)(void *arg, struct tcp_pcb *tpcb, u16_t len);
typedef err_t (*tcp_poll_fn)(void *arg, struct tcp_pcb *tpcb);
typedef void  (*tcp_err_fn)(void *arg, err_t err);
typedef err_t (*tcp_connected_fn)(void *arg, struct tcp_pcb *tpcb, err_t err);
```

### Setting TCP Callbacks

```c
void tcp_arg(struct tcp_pcb *pcb, void *arg);      // Set user argument
void tcp_accept(struct tcp_pcb *pcb, tcp_accept_fn accept);   // Accept callback
void tcp_recv(struct tcp_pcb *pcb, tcp_recv_fn recv);         // Receive callback
void tcp_sent(struct tcp_pcb *pcb, tcp_sent_fn sent);         // Sent callback
void tcp_err(struct tcp_pcb *pcb, tcp_err_fn err);            // Error callback
void tcp_poll(struct tcp_pcb *pcb, tcp_poll_fn poll, u8_t interval); // Poll callback
```

### TCP Flags

```c
#define TF_ACK_DELAY   0x01U   // Delayed ACK
#define TF_ACK_NOW     0x02U   // Immediate ACK
#define TF_INFR        0x04U   // In fast recovery
#define TF_NODELAY     0x40U   // Disable Nagle algorithm
#define TF_WND_SCALE   0x0100U // Window scaling enabled
#define TF_TIMESTAMP   0x0400U // Timestamp option enabled
```

### TCP Write Flags

```c
#define TCP_WRITE_FLAG_COPY      0x00  // Copy data to pbuf
#define TCP_WRITE_FLAG_MORE      0x01  // More data to follow
```

---

## 6. IP Address Macros

### IPv4 Address Macros

```c
#define IP4_ADDR(ipaddr, a,b,c,d)  ((ipaddr)->addr = htonl(((u32_t)(a) | ((u32_t)(b) << 8) | ((u32_t)(c) << 16) | ((u32_t)(d) << 24)))

// Example:
ip4_addr_t ipaddr;
IP4_ADDR(&ipaddr, 192, 168, 1, 100);
```

### IP Address Constants

```c
const ip_addr_t ip_addr_any;      // INADDR_ANY (0.0.0.0)
const ip_addr_t IP4_ADDR_ANY;      // &ip_addr_any
```

### Address Conversion

```c
// String to IP address
int inet_aton(const char *cp, struct in_addr *inp);

// IP address to string
const char *inet_ntoa(struct in_addr in);

// Advanced (supports IPv6)
int lwip_inet_pton(int af, const char *src, void *dst);  // "192.168.1.1" -> binary
const char *lwip_inet_ntop(int af, const void *src, char *dst, socklen_t size);  // binary -> string
```

---

## 7. Working Examples

### UDP Client Example

```c
#include "lwip/sockets.h"
#include "lwip/udp.h"
#include <string.h>

#define UDP_SERVER_IP   "192.168.1.100"
#define UDP_SERVER_PORT  5000
#define LOCAL_PORT       6000

void udp_client_task(void *param)
{
    int sock;
    struct sockaddr_in server_addr;
    char tx_buf[] = "Hello UDP Server!";
    char rx_buf[1024];
    
    // Create UDP socket
    sock = socket(AF_INET, SOCK_DGRAM, 0);
    if (sock < 0) {
        printf("Socket creation failed\r\n");
        return;
    }
    
    // Configure server address
    memset(&server_addr, 0, sizeof(server_addr));
    server_addr.sin_family = AF_INET;
    server_addr.sin_port = htons(UDP_SERVER_PORT);
    inet_aton(UDP_SERVER_IP, &server_addr.sin_addr);
    
    // Send data to server
    int ret = sendto(sock, tx_buf, strlen(tx_buf), 0,
                     (struct sockaddr *)&server_addr, sizeof(server_addr));
    if (ret < 0) {
        printf("Send failed\r\n");
        close(sock);
        return;
    }
    printf("Sent: %s\r\n", tx_buf);
    
    // Receive response
    struct sockaddr_in from_addr;
    socklen_t from_len = sizeof(from_addr);
    ret = recvfrom(sock, rx_buf, sizeof(rx_buf) - 1, 0,
                   (struct sockaddr *)&from_addr, &from_len);
    if (ret > 0) {
        rx_buf[ret] = '\0';
        printf("Received from %s:%d: %s\r\n",
               inet_ntoa(from_addr.sin_addr),
               ntohs(from_addr.sin_port),
               rx_buf);
    }
    
    close(sock);
    vTaskDelete(NULL);
}
```

### UDP Server Example (with PCB API)

```c
#include "lwip/udp.h"
#include "lwip/pbuf.h"
#include <string.h>

static struct udp_pcb *udp_server_pcb;
static char rx_buf[1024];

static void udp_recv_callback(void *arg, struct udp_pcb *pcb, struct pbuf *p,
                              const ip_addr_t *addr, u16_t port)
{
    if (p != NULL) {
        // Copy data (pbuf may be freed after this)
        size_t len = p->len < sizeof(rx_buf) - 1 ? p->len : sizeof(rx_buf) - 1;
        memcpy(rx_buf, p->payload, len);
        rx_buf[len] = '\0';
        
        printf("UDP from %s:%d: %s\r\n", ipaddr_ntoa(addr), port, rx_buf);
        
        // Echo back to sender
        udp_sendto(pcb, p, addr, port);
        
        // Free the pbuf
        pbuf_free(p);
    }
}

void udp_server_init(void)
{
    err_t err;
    
    // Create UDP PCB
    udp_server_pcb = udp_new();
    if (udp_server_pcb == NULL) {
        printf("UDP PCB creation failed\r\n");
        return;
    }
    
    // Bind to any IP, port 5000
    err = udp_bind(udp_server_pcb, IP_ADDR_ANY, 5000);
    if (err != ERR_OK) {
        printf("UDP bind failed: %d\r\n", err);
        udp_remove(udp_server_pcb);
        return;
    }
    
    // Set receive callback
    udp_recv(udp_server_pcb, udp_recv_callback, NULL);
    
    printf("UDP server listening on port 5000\r\n");
}
```

### TCP Client Example

```c
#include "lwip/sockets.h"
#include <string.h>

#define SERVER_IP   "192.168.1.100"
#define SERVER_PORT  8080

void tcp_client_task(void *param)
{
    int sock;
    struct sockaddr_in server_addr;
    char tx_buf[] = "Hello TCP Server!";
    char rx_buf[1024];
    
    // Create TCP socket
    sock = socket(AF_INET, SOCK_STREAM, 0);
    if (sock < 0) {
        printf("Socket creation failed\r\n");
        return;
    }
    
    // Configure server
    memset(&server_addr, 0, sizeof(server_addr));
    server_addr.sin_family = AF_INET;
    server_addr.sin_port = htons(SERVER_PORT);
    inet_aton(SERVER_IP, &server_addr.sin_addr);
    
    // Connect to server
    if (connect(sock, (struct sockaddr *)&server_addr, sizeof(server_addr)) < 0) {
        printf("Connect failed\r\n");
        close(sock);
        return;
    }
    printf("Connected to %s:%d\r\n", SERVER_IP, SERVER_PORT);
    
    // Send data
    if (send(sock, tx_buf, strlen(tx_buf), 0) < 0) {
        printf("Send failed\r\n");
        close(sock);
        return;
    }
    printf("Sent: %s\r\n", tx_buf);
    
    // Receive response
    int ret = recv(sock, rx_buf, sizeof(rx_buf) - 1, 0);
    if (ret > 0) {
        rx_buf[ret] = '\0';
        printf("Received: %s\r\n", rx_buf);
    }
    
    close(sock);
    vTaskDelete(NULL);
}
```

### TCP Server Example (with select)

```c
#include "lwip/sockets.h"
#include <string.h>

#define LISTEN_PORT  8080
#define MAX_CLIENTS  5

static int listen_fd;

void tcp_server_task(void *param)
{
    struct sockaddr_in server_addr, client_addr;
    int client_fd;
    fd_set read_fds;
    struct timeval timeout;
    char rx_buf[1024];
    
    // Create listening socket
    listen_fd = socket(AF_INET, SOCK_STREAM, 0);
    if (listen_fd < 0) {
        printf("Listen socket failed\r\n");
        return;
    }
    
    // Set reuse address
    int opt = 1;
    setsockopt(listen_fd, SOL_SOCKET, SO_REUSEADDR, &opt, sizeof(opt));
    
    // Bind
    memset(&server_addr, 0, sizeof(server_addr));
    server_addr.sin_family = AF_INET;
    server_addr.sin_addr.s_addr = INADDR_ANY;
    server_addr.sin_port = htons(LISTEN_PORT);
    
    if (bind(listen_fd, (struct sockaddr *)&server_addr, sizeof(server_addr)) < 0) {
        printf("Bind failed\r\n");
        close(listen_fd);
        return;
    }
    
    // Listen
    if (listen(listen_fd, MAX_CLIENTS) < 0) {
        printf("Listen failed\r\n");
        close(listen_fd);
        return;
    }
    printf("TCP server listening on port %d\r\n", LISTEN_PORT);
    
    while (1) {
        FD_ZERO(&read_fds);
        FD_SET(listen_fd, &read_fds);
        
        timeout.tv_sec = 1;
        timeout.tv_usec = 0;
        
        int ret = select(listen_fd + 1, &read_fds, NULL, NULL, &timeout);
        if (ret > 0 && FD_ISSET(listen_fd, &read_fds)) {
            // Accept connection
            socklen_t client_len = sizeof(client_addr);
            client_fd = accept(listen_fd, (struct sockaddr *)&client_addr, &client_len);
            if (client_fd >= 0) {
                printf("Client connected: %s:%d\r\n",
                       inet_ntoa(client_addr.sin_addr),
                       ntohs(client_addr.sin_port));
                
                // Echo loop
                while (1) {
                    ret = recv(client_fd, rx_buf, sizeof(rx_buf) - 1, 0);
                    if (ret <= 0) break;
                    rx_buf[ret] = '\0';
                    printf("Received: %s\r\n", rx_buf);
                    send(client_fd, rx_buf, ret, 0);
                }
                close(client_fd);
            }
        }
    }
}
```

### TCP Server Example (with PCB API and Callbacks)

```c
#include "lwip/tcp.h"
#include "lwip/pbuf.h"
#include <string.h>

#define LISTEN_PORT  8080

static struct tcp_pcb *tcp_server_pcb;

static err_t tcp_server_accept(void *arg, struct tcp_pcb *newpcb, err_t err)
{
    printf("TCP connection from %s:%d\r\n",
           ipaddr_ntoa(&newpcb->remote_ip),
           newpcb->remote_port);
    
    // Set callback for new connection
    tcp_arg(newpcb, NULL);
    tcp_recv(newpcb, tcp_server_recv);
    return ERR_OK;
}

static err_t tcp_server_recv(void *arg, struct tcp_pcb *tpcb, struct pbuf *p, err_t err)
{
    if (p != NULL) {
        // Echo back
        tcp_write(tpcb, p->payload, p->len, TCP_WRITE_FLAG_COPY);
        tcp_output(tpcb);
        pbuf_free(p);
    } else {
        // Connection closed
        tcp_close(tpcb);
    }
    return ERR_OK;
}

static void tcp_server_err(void *arg, err_t err)
{
    printf("TCP server error: %d\r\n", err);
}

void tcp_server_init(void)
{
    err_t err;
    
    // Create TCP PCB
    tcp_server_pcb = tcp_new();
    if (tcp_server_pcb == NULL) {
        printf("TCP PCB creation failed\r\n");
        return;
    }
    
    // Bind to port
    err = tcp_bind(tcp_server_pcb, IP_ADDR_ANY, LISTEN_PORT);
    if (err != ERR_OK) {
        printf("TCP bind failed: %d\r\n", err);
        tcp_close(tcp_server_pcb);
        return;
    }
    
    // Set listening state with backlog
    tcp_server_pcb = tcp_listen(tcp_server_pcb);
    if (tcp_server_pcb == NULL) {
        printf("TCP listen failed\r\n");
        return;
    }
    
    // Set accept callback
    tcp_accept(tcp_server_pcb, tcp_server_accept);
    tcp_err(tcp_server_pcb, tcp_server_err);
    
    printf("TCP server listening on port %d\r\n", LISTEN_PORT);
}
```

---

## 8. Network Interface Setup Example

```c
#include "lwip/netif.h"
#include "lwip/netifapi.h"
#include "lwip/ip_addr.h"
#include "lwip/etharp.h"

static struct netif sta_netif;

void network_interface_init(void)
{
    ip4_addr_t ipaddr, netmask, gw;
    
    // Configure static IP
    IP4_ADDR(&ipaddr,  192, 168, 1, 100);
    IP4_ADDR(&netmask, 255, 255, 255, 0);
    IP4_ADDR(&gw,      192, 168, 1, 1);
    
    // Add network interface
    netifapi_netif_add(&sta_netif, &ipaddr, &netmask, &gw,
                       NULL, ethernetif_init, tcpip_input);
    
    // Set as default interface
    netifapi_netif_set_default(&sta_netif);
    
    // Bring interface up
    netifapi_netif_set_up(&sta_netif);
    
    printf("Network interface ready: %s\r\n", ipaddr_ntoa(&ipaddr));
}
```

---

## 9. Common Error Codes

| Error | Value | Description |
|-------|-------|-------------|
| `ERR_OK` | 0 | No error |
| `ERR_MEM` | -1 | Out of memory |
| `ERR_BUF` | -2 | Buffer error |
| `ERR_TIMEOUT` | -3 | Timeout |
| `ERR_RTE` | -4 | Routing problem |
| `ERR_INPROGRESS` | -5 | Operation in progress |
| `ERR_VAL` | -6 | Illegal value |
| `ERR_WOULDBLOCK` | -7 | Operation would block |
| `ERR_ABRT` | -8 | Connection aborted |
| `ERR_RST` | -9 | Connection reset |
| `ERR_CLSD` | -10 | Connection closed |
| `ERR_CONN` | -11 | Not connected |
| `ERR_ARG` | -12 | Illegal argument |
| `ERR_USE` | -13 | Address in use |
| `ERR_IF` | -14 | Network interface error |

---

## 10. Tips and Best Practices

1. **Thread Safety**: Use `netifapi_*` functions from non-TCPIP threads; use `LOCK_TCPIP_CORE()`/`UNLOCK_TCPIP_CORE()` for direct stack access.

2. **Memory**: Always check `pbuf` pointers and free them appropriately. Use `pbuf_free()` to release received buffers.

3. **TCP Best Practices**:
   - Call `tcp_recved()` to advertise window space after processing data
   - Use `tcp_nagle_disable()` for low-latency applications
   - Implement proper error handling in callbacks

4. **UDP Notes**: UDP is connectionless; use `recvfrom()`/`sendto()` for unconnected operation, or `connect()` for connected UDP sockets.

5. **Buffer Sizes**: Default send/receive buffers can be tuned in lwipopts.h via `MEM_SIZE`, `PBUF_POOL_SIZE`, `TCP_SND_BUF`, etc.
