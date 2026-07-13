# WebSocket API Reference

> Source file: `components/network/axk_protocol_stack/tcp_transport/include/axk_transport_ws.h`  
> WebSocket protocol wrapper, based on TCP Transport, supporting text/binary frames, Ping/Pong, and handshake upgrade.

---

## Overview

The WebSocket protocol is built on top of HTTP and switches to a WebSocket connection via the HTTP Upgrade mechanism. BL602 supports:
- WS (WebSocket plain text)
- WSS (WebSocket over TLS)
- Text/binary frame sending and receiving
- Ping/Pong heartbeat
- Custom HTTP headers (User-Agent, Sub-Protocol)
- Connection close detection

---

## Header File

```c
#include "axk_transport_ws.h"
```

---

## Frame Types

```c
typedef enum ws_transport_opcodes {
    WS_TRANSPORT_OPCODES_CONT =  0x00,   // Continuation frame
    WS_TRANSPORT_OPCODES_TEXT =  0x01,   // Text frame
    WS_TRANSPORT_OPCODES_BINARY = 0x02, // Binary frame
    WS_TRANSPORT_OPCODES_CLOSE = 0x08,   // Close frame
    WS_TRANSPORT_OPCODES_PING = 0x09,    // Ping frame
    WS_TRANSPORT_OPCODES_PONG = 0x0a,    // Pong frame
    WS_TRANSPORT_OPCODES_FIN = 0x80,     // FIN flag
    WS_TRANSPORT_OPCODES_NONE = 0x100,   // Invalid opcode
} ws_transport_opcodes_t;
```

---

## Configuration Structure

### `axk_transport_ws_config_t`

```c
typedef struct {
    const char *ws_path;                    // WebSocket path (e.g., "/ws")
    const char *sub_protocol;              // Sub-protocol (e.g., "mqtt")
    const char *user_agent;                // User-Agent header
    const char *headers;                    // Extra HTTP headers (each line ends with \r\n)
    bool propagate_control_frames;         // true=control frames passed to reader, false=auto handled
} axk_transport_ws_config_t;
```

---

## Function Interface

### `axk_transport_ws_init`

Creates a WebSocket transport layer.

```c
axk_transport_handle_t axk_transport_ws_init(axk_transport_handle_t parent_handle);
```

| Parameter | Description |
|-----------|-------------|
| `parent_handle` | Parent TCP/SSL transport handle |

**Return value**: WebSocket transport handle

---

### `axk_transport_ws_set_path`

Sets the WebSocket path.

```c
void axk_transport_ws_set_path(axk_transport_handle_t t, const char *path);
```

---

### `axk_transport_ws_set_subprotocol`

Sets the sub-protocol.

```c
axk_err_t axk_transport_ws_set_subprotocol(axk_transport_handle_t t,
                                            const char *sub_protocol);
```

---

### `axk_transport_ws_set_user_agent`

Sets the User-Agent header.

```c
axk_err_t axk_transport_ws_set_user_agent(axk_transport_handle_t t,
                                           const char *user_agent);
```

---

### `axk_transport_ws_set_headers`

Sets extra HTTP headers.

```c
axk_err_t axk_transport_ws_set_headers(axk_transport_handle_t t,
                                       const char *headers);
```

---

### `axk_transport_ws_set_config`

Batch sets WebSocket configuration.

```c
axk_err_t axk_transport_ws_set_config(axk_transport_handle_t t,
                                       const axk_transport_ws_config_t *config);
```

---

### `axk_transport_ws_send_raw`

Sends a raw frame with a custom opcode.

```c
int axk_transport_ws_send_raw(axk_transport_handle_t t,
                               ws_transport_opcodes_t opcode,
                               const char *buffer,
                               int len,
                               int timeout_ms);
```

| Parameter | Description |
|-----------|-------------|
| `opcode` | Frame type (TEXT/BINARY/PING/PONG/CLOSE) |
| `buffer` | Data buffer |
| `len` | Data length (0=send Ping) |
| `timeout_ms` | Timeout (milliseconds, -1=block forever) |

---

### `axk_transport_ws_get_fin_flag`

Gets the FIN flag of the last received frame.

```c
bool axk_transport_ws_get_fin_flag(axk_transport_handle_t t);
```

---

### `axk_transport_ws_get_read_opcode`

Gets the opcode of the last received frame.

```c
ws_transport_opcodes_t axk_transport_ws_get_read_opcode(axk_transport_handle_t t);
```

---

### `axk_transport_ws_get_read_payload_len`

Gets the payload length of the last received frame.

```c
int axk_transport_ws_get_read_payload_len(axk_transport_handle_t t);
```

---

### `axk_transport_ws_poll_connection_closed`

Waits for a connection close event.

```c
int axk_transport_ws_poll_connection_closed(axk_transport_handle_t t,
                                            int timeout_ms);
```

| Return value | Description |
|--------------|-------------|
| 0 | Timeout |
| 1 | Connection FIN closed or RST received |
| -1 | Failure |

---

## Usage Examples

### WebSocket Client

```c
#include "axk_transport_ws.h"

static void ws_task(void *arg)
{
    // Create TCP transport
    axk_transport_handle_t parent = axk_transport_tcp_init();

    // Create WebSocket transport
    axk_transport_handle_t ws = axk_transport_ws_init(parent);

    // Set WebSocket configuration
    axk_transport_ws_set_path(ws, "/echo");
    axk_transport_ws_set_subprotocol(ws, "echo");

    // Connect to server
    axk_transport_connect(ws, "echo.websocket.org", 80, 5000);

    // Send text message
    const char *msg = "Hello WebSocket";
    axk_transport_ws_send_raw(ws, WS_TRANSPORT_OPCODES_TEXT,
                              msg, strlen(msg), 5000);

    // Read response
    char buf[512];
    int len = axk_transport_read(ws, buf, sizeof(buf), 5000);
    if (len > 0) {
        printf("Received: %.*s\r\n", len, buf);

        // Check opcode
        ws_transport_opcodes_t opcode = axk_transport_ws_get_read_opcode(ws);
        if (opcode == WS_TRANSPORT_OPCODES_TEXT) {
            printf("Text frame\r\n");
        } else if (opcode == WS_TRANSPORT_OPCODES_BINARY) {
            printf("Binary frame\r\n");
        }
    }

    // Send Ping (len=0 sends Ping frame)
    axk_transport_ws_send_raw(ws, WS_TRANSPORT_OPCODES_PING, NULL, 0, 5000);

    // Close connection
    axk_transport_ws_send_raw(ws, WS_TRANSPORT_OPCODES_CLOSE, NULL, 0, 5000);
    axk_transport_close(ws);

    vTaskDelete(NULL);
}
```

### WebSocket with TLS (WSS)

```c
axk_transport_handle_t ssl = axk_transport_ssl_init();
axk_transport_handle_t ws = axk_transport_ws_init(ssl);

axk_transport_ssl_set_cert_data(ssl, ca_cert_pem, strlen(ca_cert_pem) + 1);
axk_transport_ws_set_path(ws, "/wss");

axk_transport_connect(ws, "secure-websocket.example.com", 443, 10000);
```

---

## Difference from MQTT over WebSocket

| Feature | WebSocket | MQTT over WS |
|---------|-----------|--------------|
| Use case | General bidirectional communication | MQTT protocol carrier |
| Sub-protocol | Optional custom | `mqtt` |
| Frame type | TEXT/BINARY | BINARY |
| Library | axk_transport_ws | mqtt_client (transport=WS/WSS) |
