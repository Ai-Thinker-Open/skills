# HTTPS API Reference (Concise Version)

> Source file: `components/network/https/include/https.h`  
> BL602 simplified HTTPS client interface, providing encrypted TCP data transmission based on TLS connections.

---

## Overview

`https.h` provides a simplified HTTPS interface that internally wraps the TLS connection process, suitable for quickly implementing HTTPS request scenarios. Compared to the full axk_tls API, this interface is easier to use but has limited functionality.

**Note**: For complex HTTPS scenarios (such as custom HTTP headers, certificate verification), it is recommended to use `axk_tls.h` or `http_client.h`.

---

## Header File

```c
#include "https.h"
```

---

## Function Interface

### `blTcpSslConnect`

Establishes an encrypted TCP connection.

```c
int32_t blTcpSslConnect(const char *dst, uint16_t port);
```

| Parameter | Description |
|-----------|-------------|
| `dst` | Target server address (domain name or IP) |
| `port` | Port number |

| Return Value | Description |
|--------------|-------------|
| >0 | Success, returns socket descriptor |
| `BL_TCP_CREATE_CONNECT_ERR` | Connection creation failed |
| `BL_TCP_ARG_INVALID` | Invalid parameter (dst is NULL) |

> After returning the socket, use `blTcpSslState()` to check if TLS handshake is complete.

---

### `blTcpSslState`

Queries the encrypted connection state.

```c
int32_t blTcpSslState(int32_t fd);
```

| Return Value | Description |
|--------------|-------------|
| `BL_TCP_STATE_CONNECTED` | TLS handshake complete, can send/receive data |
| `BL_TCP_STATE_CONNECTING` | Handshake in progress |
| `BL_TCP_STATE_FAILED` | Connection failed |
| Others | Error code |

---

### `blTcpSslDisconnect`

Disconnects the encrypted connection.

```c
void blTcpSslDisconnect(int32_t fd);
```

---

### `blTcpSslSend`

Sends encrypted data (non-blocking).

```c
int32_t blTcpSslSend(int32_t fd, const uint8_t *buf, uint16_t len);
```

| Parameter | Description |
|-----------|-------------|
| `fd` | Socket returned by `blTcpSslConnect` |
| `buf` | Send data buffer |
| `len` | Data length (range 0~512) |

| Return Value | Description |
|--------------|-------------|
| >=0 | Actual bytes sent |
| Error code | Send failed |

---

### `blTcpSslRead`

Reads encrypted data (non-blocking).

```c
int32_t blTcpSslRead(int32_t fd, uint8_t *buf, uint16_t len);
```

| Parameter | Description |
|-----------|-------------|
| `fd` | Socket returned by `blTcpSslConnect` |
| `buf` | Receive data buffer |
| `len` | Maximum buffer length (range 0~512) |

| Return Value | Description |
|--------------|-------------|
| >=0 | Actual bytes read |
| Error code | Read failed |

---

## Usage Examples

### Simple HTTPS GET

```c
#include "https.h"

void https_get_example(void)
{
    // Establish HTTPS connection
    int32_t fd = blTcpSslConnect("www.example.com", 443);
    if (fd < 0) {
        printf("Connect failed: %ld\r\n", fd);
        return;
    }

    // Wait for TLS handshake to complete
    while (blTcpSslState(fd) == BL_TCP_STATE_CONNECTING) {
        vTaskDelay(pdMS_TO_TICKS(10));
    }

    // Send HTTP request
    const char *request =
        "GET / HTTP/1.1\r\n"
        "Host: www.example.com\r\n"
        "User-Agent: BL602\r\n"
        "Connection: close\r\n"
        "\r\n";

    int32_t sent = blTcpSslSend(fd, (const uint8_t *)request,
                                  strlen(request));
    if (sent < 0) {
        printf("Send failed\r\n");
        blTcpSslDisconnect(fd);
        return;
    }

    // Read response
    uint8_t buf[512];
    int32_t len;
    while ((len = blTcpSslRead(fd, buf, sizeof(buf))) > 0) {
        printf("%.*s", (int)len, buf);
    }

    blTcpSslDisconnect(fd);
}
```

### With Timeout Detection

```c
int32_t wait_for_ssl_connected(int32_t fd, uint32_t timeout_ms)
{
    uint32_t start = xTaskGetTickCount();
    while (blTcpSslState(fd) == BL_TCP_STATE_CONNECTING) {
        if ((xTaskGetTickCount() - start) * portTICK_PERIOD_MS > timeout_ms) {
            return -1; // Timeout
        }
        vTaskDelay(pdMS_TO_TICKS(10));
    }
    return 0;
}
```

---

## Error Code Reference

| Error Code | Description |
|------------|-------------|
| `BL_TCP_ARG_INVALID` | Invalid parameter |
| `BL_TCP_CREATE_CONNECT_ERR` | Failed to create connection |
| `BL_TCP_STATE_CONNECTED` | Connected |
| `BL_TCP_STATE_CONNECTING` | Connecting |
| `BL_TCP_STATE_FAILED` | Connection failed |

---

## Differences from axk_tls

| Feature | `https.h` | `axk_tls.h` |
|---------|------------|-------------|
| API complexity | Simple | Complex |
| Non-blocking mode | Supported | Supported |
| Certificate configuration | Limited | Full (CA/client certificates/PSK) |
| Error handling | Simplified | Detailed |
| Use case | Simple HTTPS requests | Mutual authentication, PSK, etc. |
