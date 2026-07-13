# TCP Transport API Reference

> Source file: `components/network/axk_protocol_stack/tcp_transport/include/axk_transport.h`  
> Transport layer abstraction, unified management of TCP/SSL/WS/WSS multiple transport methods.

---

## Overview

TCP Transport is the transport layer abstraction of the BL602 network protocol stack, providing a unified interface to manage TCP, SSL, WebSocket and other transport methods. It is the foundation of MQTT, HTTP and other higher-level protocols.

```
Application Layer (MQTT / HTTP / Custom Protocol)
         ↓
  TCP Transport (Unified Interface)
         ↓
  ┌─────────┬──────────┬─────────┬──────────┐
  ↓         ↓          ↓         ↓          ↓
  TCP     SSL        WS        WSS      Other Transports
```

---

## Header File

```c
#include "axk_transport.h"
```

---

## Type Definitions

### Keep-Alive Configuration

```c
typedef struct axk_transport_keepalive {
    bool keep_alive_enable;      // Enable
    int  keep_alive_idle;       // Idle timeout (seconds)
    int  keep_alive_interval;   // Probe interval (seconds)
    int  keep_alive_count;      // Retry count
} axk_transport_keep_alive_t;
```

---

## Function API

### `axk_transport_list_init`

Create a transport list (for multi-protocol management).

```c
axk_transport_list_handle_t axk_transport_list_init(void);
```

---

### `axk_transport_list_destroy`

Destroy transport list and all child transports.

```c
axk_err_t axk_transport_list_destroy(axk_transport_list_handle_t list);
```

---

### `axk_transport_list_add`

Add transport to list and bind scheme.

```c
axk_err_t axk_transport_list_add(axk_transport_list_handle_t list,
                                  axk_transport_handle_t t,
                                  const char *scheme);
```

| Parameter | Description |
|-----------|-------------|
| `list` | Transport list handle |
| `t` | Transport handle |
| `scheme` | Protocol identifier (e.g. `"mqtt"` `"wss"`) |

---

### `axk_transport_list_get_transport`

Get corresponding transport by scheme.

```c
axk_transport_handle_t axk_transport_list_get_transport(
    axk_transport_list_handle_t list,
    const char *scheme);
```

---

### `axk_transport_connect`

Connect to server.

```c
int axk_transport_connect(axk_transport_handle_t t,
                           const char *host,
                           int port,
                           int timeout_ms);
```

| Parameter | Description |
|-----------|-------------|
| `host` | Server address (domain name or IP) |
| `port` | Port number |
| `timeout_ms` | Connection timeout (milliseconds) |

**Return value**: 0=success, -1=failure

---

### `axk_transport_read`

Read data.

```c
int axk_transport_read(axk_transport_handle_t t,
                        char *buffer,
                        int len,
                        int timeout_ms);
```

| Parameter | Description |
|-----------|-------------|
| `buffer` | Receive buffer |
| `len` | Buffer size |
| `timeout_ms` | Timeout |

**Return value**: >0=bytes read, -1=error, 0=peer closed

---

### `axk_transport_write`

Send data.

```c
int axk_transport_write(axk_transport_handle_t t,
                         const char *buffer,
                         int len,
                         int timeout_ms);
```

**Return value**: >=0=bytes sent, -1=error

---

### `axk_transport_poll_read`

Wait for readable event.

```c
int axk_transport_poll_read(axk_transport_handle_t t, int timeout_ms);
```

| Return value | Description |
|--------------|-------------|
| 0 | Timeout |
| -1 | Error |
| >0 | Readable |

---

### `axk_transport_poll_write`

Wait for writable event.

```c
int axk_transport_poll_write(axk_transport_handle_t t, int timeout_ms);
```

---

### `axk_transport_close`

Close transport connection.

```c
int axk_transport_close(axk_transport_handle_t t);
```

---

### `axk_transport_destroy`

Destroy transport handle.

```c
int axk_transport_destroy(axk_transport_handle_t t);
```

---

### `axk_transport_get_context_data`

Get user context data.

```c
void *axk_transport_get_context_data(axk_transport_handle_t t);
```

---

### `axk_transport_set_context_data`

Set user context data.

```c
axk_err_t axk_transport_set_context_data(axk_transport_handle_t t,
                                          void *data);
```

---

### `axk_transport_get_payload_transport_handle`

Get payload transport handle (e.g. get underlying TCP from SSL).

```c
axk_transport_handle_t axk_transport_get_payload_transport_handle(
    axk_transport_handle_t t);
```

---

### `axk_transport_get_error_handle`

Get error descriptor.

```c
axk_tls_error_handle_t axk_transport_get_error_handle(axk_transport_handle_t t);
```

---

### `axk_transport_get_errno`

Get and clear last socket error code.

```c
int axk_transport_get_errno(axk_transport_handle_t t);
```

---

### `axk_transport_set_func`

Set transport layer function pointers (advanced usage).

```c
axk_err_t axk_transport_set_func(axk_transport_handle_t t,
                                  connect_func _connect,
                                  io_read_func _read,
                                  io_func _write,
                                  trans_func _close,
                                  poll_func _poll_read,
                                  poll_func _poll_write,
                                  trans_func _destroy);
```

---

### `axk_transport_set_async_connect_func`

Set asynchronous connect function.

```c
axk_err_t axk_transport_set_async_connect_func(
    axk_transport_handle_t t,
    connect_async_func _connect_async_func);
```

---

## SSL Transport (axk_transport_ssl.h)

```c
#include "axk_transport_ssl.h"

// Create SSL transport
axk_transport_handle_t axk_transport_ssl_init(void);

// Set server CA certificate (PEM)
void axk_transport_ssl_set_cert_data(axk_transport_handle_t t,
                                      const char *data, int len);

// Set DER format certificate
void axk_transport_ssl_set_cert_data_der(axk_transport_handle_t t,
                                          const char *data, int len);

// Enable global CA certificate store
void axk_transport_ssl_enable_global_ca_store(axk_transport_handle_t t);

// Set client certificate (mutual authentication)
void axk_transport_ssl_set_client_cert_data(axk_transport_handle_t t,
                                             const char *data, int len);

// Set client private key
void axk_transport_ssl_set_client_key_data(axk_transport_handle_t t,
                                             const char *data, int len);

// Set private key password
void axk_transport_ssl_set_client_key_password(axk_transport_handle_t t,
                                                const char *password,
                                                int password_len);

// Set ALPN protocols
void axk_transport_ssl_set_alpn_protocol(axk_transport_handle_t t,
                                           const char **alpn_protos);

// Skip CN verification (not recommended)
void axk_transport_ssl_skip_common_name_check(axk_transport_handle_t t);

// Use secure element (ATECC608A)
void axk_transport_ssl_use_secure_element(axk_transport_handle_t t);

// Set Keep-Alive
void axk_transport_ssl_set_keep_alive(axk_transport_handle_t t,
                                        axk_transport_keep_alive_t *cfg);
```

---

## Usage Example

### Multi-Protocol Transport List

```c
axk_transport_list_handle_t list = axk_transport_list_init();

// Add TCP transport
axk_transport_handle_t tcp = axk_transport_tcp_init();
axk_transport_list_add(list, tcp, "tcp");

// Add SSL transport
axk_transport_handle_t ssl = axk_transport_ssl_init();
axk_transport_ssl_set_cert_data(ssl, ca_cert, strlen(ca_cert) + 1);
axk_transport_list_add(list, ssl, "ssl");

// Get and use by scheme
axk_transport_handle_t transport = axk_transport_list_get_transport(list, "ssl");
axk_transport_connect(transport, "example.com", 443, 5000);
axk_transport_write(transport, "Hello", 5, 5000);
```

### Basic TCP Connection

```c
axk_transport_handle_t tcp = axk_transport_tcp_init();
int ret = axk_transport_connect(tcp, "192.168.1.100", 8080, 5000);
if (ret == 0) {
    char buf[256];
    int len = axk_transport_read(tcp, buf, sizeof(buf), 3000);
    if (len > 0) {
        // Process data
    }
    axk_transport_close(tcp);
}
```
