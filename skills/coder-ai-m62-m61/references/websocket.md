# librws WebSocket Client Library

## Overview

librws is a lightweight WebSocket client library designed specifically for resource-constrained embedded environments, supporting single-threaded asynchronous I/O mode. The library is suitable for bidirectional communication scenarios between IoT devices and cloud servers, featuring small footprint, concise interfaces, and minimal dependencies. The library integrates mbedTLS support internally and can directly establish wss (WebSocket Secure) encrypted connections.

Current version: **1.2.4**

## Basic Types

### rws_bool Boolean Type

librws defines a custom boolean type `rws_bool` as an alias for unsigned char.

```c
typedef unsigned char rws_bool;
#define rws_true  1
#define rws_false 0
```

All functions returning boolean status use this type. When checking, use `if (result == rws_true)` or simply `if (result)`.

### rws_handle Type

All object handles in the library are defined as `void *` types, including:

- `rws_socket` - Socket handle
- `rws_error` - Error object handle
- `rws_mutex` - Mutex handle
- `rws_thread` - Thread handle

## Socket Connection Management

### Creation and Connection

**rws_socket_create()**

Creates a new WebSocket Socket object and returns a handle for subsequent operations. After creation, URL parameters must be set and `rws_socket_connect()` called to initiate the connection.

```c
rws_socket rws_socket_create(void);
```

**rws_socket_set_url() / rws_socket_connect()**

Sets the connection target and initiates the connection. The URL consists of four parts: scheme, host, port, and path.

```c
void rws_socket_set_url(rws_socket socket,
                         const char * scheme,    // "ws" or "wss"
                         const char * host,       // Server domain or IP
                         const int port,          // Port number
                         const char * path);      // Path, e.g. "/"

rws_bool rws_socket_connect(rws_socket socket);
```

Parameters can also be set individually:

```c
rws_socket_set_scheme(socket, "wss");       // Set protocol scheme
rws_socket_set_host(socket, "example.com"); // Set host
rws_socket_set_port(socket, 8443);          // Set port
rws_socket_set_path(socket, "/ws");         // Set path
```

**Connection Status Query**

```c
rws_bool rws_socket_is_connected(rws_socket socket);
// Returns rws_true if connection is established and handshake is complete
```

### Disconnection and Release

**rws_socket_disconnect_and_release() / rws_socket_delete()**

Closes the Socket connection and releases resources. After calling, the Socket handle must no longer be used.

```c
void rws_socket_disconnect_and_release(rws_socket socket);
void rws_socket_delete(rws_socket socket);
```

## Message Sending

librws provides multiple send interfaces, supporting both text and binary data.

### Text Message Sending

**rws_socket_send_text() / rws_socket_send_text2()**

Sends a text frame to the connected server. `send_text2` allows specifying the length.

```c
rws_bool rws_socket_send_text(rws_socket socket, const char * text);
rws_bool rws_socket_send_text2(rws_socket socket, const char * text, size_t len);
```

### Binary Message Sending

Binary data sending uses a framing interface with three phases: start, continue, and finish, suitable for large data transfer scenarios:

```c
// Start sending binary data (send frame header)
rws_bool rws_socket_send_bin_start(rws_socket socket, const char * bin, size_t len);

// Continue sending binary data
rws_bool rws_socket_send_bin_continue(rws_socket socket, const char * bin, size_t len);

// Finish sending (send frame trailer)
rws_bool rws_socket_send_bin_finish(rws_socket socket, const char * bin, size_t len);
```

### Send-Related Constants

**RWS_MAX_SEND_APPEND_SIZE**

Defines the maximum buffer size for a single send operation:

```c
#define RWS_MAX_SEND_APPEND_SIZE (1024 * 640)  // 640KB
```

Internally, `send_append_size` defaults to this value, indicating the upper limit of the send queue buffer.

### Low-Level Send Interface

The internal `rws_socket_send()` function provides raw data sending capability:

```c
rws_bool rws_socket_send(rws_socket socket, const void * data, const size_t data_size);
```

## Message Reception

librws uses a callback pattern to handle received data; callback functions must be registered in advance.

### Receive Callback Registration

**rws_socket_on_received_text() / rws_socket_on_received_bin()**

```c
typedef void (*rws_on_socket_recvd_text)(rws_socket socket,
                                         const char * text,
                                         const unsigned int length,
                                         bool is_finished);

typedef void (*rws_on_socket_recvd_bin)(rws_socket socket,
                                         const void * data,
                                         const unsigned int length,
                                         bool is_finished);

void rws_socket_set_on_received_text(rws_socket socket, rws_on_socket_recvd_text callback);
void rws_socket_set_on_received_bin(rws_socket socket, rws_on_socket_recvd_bin callback);
```

The callback parameter `is_finished` indicates whether the current frame is the last frame of the message (used for fragmented transmission scenarios).

## Connection Status Callbacks

### Connection Established Callback

**rws_socket_on_connected()**

Triggered when the WebSocket handshake completes successfully.

```c
typedef void (*rws_on_socket)(rws_socket socket);

void rws_socket_set_on_connected(rws_socket socket, rws_on_socket callback);
```

### Disconnection Callback

**rws_socket_on_disconnected()**

Triggered when the connection is closed, including both intentional disconnection and abnormal disconnection.

```c
void rws_socket_set_on_disconnected(rws_socket socket, rws_on_socket callback);
```

### Pong Callback

Triggered when a server Pong response is received (used for heartbeat detection):

```c
typedef void (*rws_on_socket_recvd_pong)(rws_socket socket);
void rws_socket_set_on_received_pong(rws_socket socket, rws_on_socket_recvd_pong callback);
```

## Thread Management

librws internally uses worker threads for network I/O processing. The library also provides a thread creation interface for application layer use.

### rws_thread_create()

Creates and immediately starts a new thread:

```c
typedef void (*rws_thread_funct)(void * user_object);

RWS_API(rws_thread) rws_thread_create(rws_thread_funct thread_function, void * user_object);
```

### rws_thread_join()

Waits for a thread to finish and retrieves the return value:

```c
RWS_API(int) rws_thread_join(rws_thread thread, void ** retval);
```

### rws_thread_sleep()

Thread sleep (millisecond granularity):

```c
RWS_API(void) rws_thread_sleep(const unsigned int millisec);
```

## Error Handling

### Getting Errors

```c
rws_error rws_socket_get_error(rws_socket socket);
int rws_error_get_code(rws_error error);
const char * rws_error_get_description(rws_error error);
int rws_error_get_http_error(rws_error error);
```

### Error Code Definitions

| Error Code | Meaning |
|------------|---------|
| rws_error_code_none | No error |
| rws_error_code_missed_parameter | Missing required parameter |
| rws_error_code_send_handshake | Handshake send failed |
| rws_error_code_parse_handshake | Handshake response parse failed |
| rws_error_code_read_write_socket | Socket read/write error |
| rws_error_code_connect_to_host | Host connection failed |
| rws_error_code_connection_closed | Connection closed |

## SSL/TLS Support

When SSL is enabled (`WEBSOCKET_SSL_ENABLE`), the server certificate can be set:

```c
void rws_socket_set_server_cert(rws_socket socket,
                                const char * server_cert,
                                int server_cert_len);
```

## Timeout Settings

```c
// Set read timeout (milliseconds)
int rws_socket_set_read_timeout(rws_socket socket, int timeout_ms);

// Set write timeout (milliseconds)
int rws_socket_set_write_timeout(rws_socket socket, int timeout_ms);
```

## User Object Binding

Sockets support binding custom user objects, making it easy to identify context in callbacks:

```c
void rws_socket_set_user_object(rws_socket socket, void * user_object);
void * rws_socket_get_user_object(rws_socket socket);
```

## WebSocket vs MQTT Protocol Comparison

| Feature | WebSocket (librws) | MQTT |
|---------|--------------------|------|
| Protocol Layer | Application (HTTP upgrade) | Application (standalone) |
| Connection Type | Persistent TCP long connection | Persistent TCP long connection |
| Communication Mode | Bidirectional message stream | Publish/Subscribe (Pub/Sub) |
| Message Model | Point-to-point, client-server | Many-to-many, topic subscription |
| Header Overhead | Small (2-14 bytes/frame) | Very small (2 bytes minimum) |
| Suitable Scenarios | Real-time chat, push, browser games | IoT sensor data collection |
| QoS Support | Application layer implementation needed | Native QoS 0/1/2 support |
| Broker Requirements | Standard WebSocket server | MQTT Broker |
| Complexity | Simple | Moderate |

**Selection Advice**:

- Simple request-response scenarios or web applications that need to traverse firewalls → WebSocket
- Large-scale device data collection, many-to-many message distribution → MQTT
- Need compatibility with existing web technology stack → WebSocket

## Code Examples

The following example demonstrates how to connect to a wss:// server and send/receive messages:

```c
#include "librws.h"
#include <stdio.h>

// Global socket handle
static rws_socket g_socket = NULL;

// Connection established callback
static void on_connected(rws_socket socket) {
    printf("[WS] Connected\r\n");
    
    // Send text message after successful connection
    const char *msg = "Hello, Server!";
    rws_socket_send_text(socket, msg);
}

// Receive text callback
static void on_received_text(rws_socket socket, const char * text, 
                             const unsigned int length, bool is_finished) {
    printf("[WS] Received (%u bytes): %.*s\r\n", length, length, text);
}

// Disconnection callback
static void on_disconnected(rws_socket socket) {
    printf("[WS] Disconnected\r\n");
    g_socket = NULL;
}

// Initialize WebSocket client
int ws_client_init(void) {
    // Create socket object
    g_socket = rws_socket_create();
    if (!g_socket) {
        printf("[WS] Create failed\r\n");
        return -1;
    }
    
    // Set callbacks
    rws_socket_set_on_connected(g_socket, on_connected);
    rws_socket_set_on_disconnected(g_socket, on_disconnected);
    rws_socket_set_on_received_text(g_socket, on_received_text);
    
    // Set connection parameters (wss://echo.websocket.org:443/)
    rws_socket_set_url(g_socket, "wss", "echo.websocket.org", 443, "/");
    
    // Set timeouts (optional)
    rws_socket_set_read_timeout(g_socket, 5000);
    rws_socket_set_write_timeout(g_socket, 5000);
    
    // Initiate connection
    if (rws_socket_connect(g_socket) != rws_true) {
        printf("[WS] Connect failed\r\n");
        rws_socket_delete(g_socket);
        g_socket = NULL;
        return -1;
    }
    
    printf("[WS] Connecting...\r\n");
    return 0;
}

// Disconnect and cleanup
void ws_client_cleanup(void) {
    if (g_socket) {
        rws_socket_disconnect_and_release(g_socket);
        g_socket = NULL;
    }
}
```

### Binary Data Sending Example

```c
// Send binary data (framed)
static void send_binary_data(rws_socket socket, const uint8_t *data, size_t len) {
    size_t chunk_size = 1024;
    size_t offset = 0;
    
    while (offset < len) {
        size_t remain = len - offset;
        size_t send_len = (remain > chunk_size) ? chunk_size : remain;
        
        if (offset == 0) {
            // Start frame
            rws_socket_send_bin_start(socket, (const char *)data, send_len);
        } else if (offset + send_len < len) {
            // Continue frame
            rws_socket_send_bin_continue(socket, (const char *)(data + offset), send_len);
        } else {
            // Finish frame
            rws_socket_send_bin_finish(socket, (const char *)(data + offset), send_len);
        }
        
        offset += send_len;
    }
}
```

## References

- [librws Official Repository](https://github.com/nekopub/librws) - Lightweight WebSocket client library
- [WebSocket Protocol RFC 6455](https://tools.ietf.org/html/rfc6455) - WebSocket standard protocol specification
- Bouffalo SDK xwebsocket component source:
  - `components/multimedia/xwebsocket/include/librws.h`
  - `components/multimedia/xwebsocket/include/rws_socket.h`
  - `components/multimedia/xwebsocket/include/rws_frame.h`
  - `components/multimedia/xwebsocket/include/rws_network.h`
