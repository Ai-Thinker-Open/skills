# HTTPS Client API Reference

## Overview

The HTTPS client for BL616/BL618 is implemented based on mbedTLS, supporting TLS 1.2 and TLS 1.3 protocols, compatible with HTTP/1.1 keep-alive persistent connections. This module encapsulates the underlying TLS handshake, encrypted data transmission, and HTTP protocol parsing, providing secure and reliable HTTPS communication capabilities for embedded devices.

The HTTPS client architecture is divided into two layers:

- **HTTP layer**: Based on the Zephyr net/http library, implementing HTTP/1.1 protocol parsing and request construction
- **TLS layer**: Wraps mbedTLS through https_wrapper, providing an SSL/TLS encrypted channel

## Header Files

```c
#include "http/client.h"      // HTTP client core API
#include "http/parser.h"      // HTTP message parser
#include "https_client.h"     // HTTPS client wrapper
#include "https_wrapper.h"    // mbedTLS wrapper interface
```

## Constants and Enumerations

### HTTP_CRLF

```c
#define HTTP_CRLF "\r\n"
```

HTTP protocol line terminator, used to separate individual fields in HTTP headers.

### HTTP_STATUS_STR_SIZE

```c
#define HTTP_STATUS_STR_SIZE 32
```

HTTP status code string array size, sufficient to store standard status descriptions such as "200 OK" and "404 Not Found".

### enum http_final_call

Response data callback flag, indicating whether the current data is the last part of the message:

```c
enum http_final_call {
    HTTP_DATA_MORE = 0,   // More data to be received
    HTTP_DATA_FINAL = 1   // This is the last data of the message
};
```

### enum http_method

Supported HTTP methods:

```c
enum http_method {
    HTTP_DELETE = 0,
    HTTP_GET = 1,
    HTTP_HEAD = 2,
    HTTP_POST = 3,
    HTTP_PUT = 4,
    HTTP_CONNECT = 5,
    HTTP_OPTIONS = 6,
    HTTP_TRACE = 7,
    HTTP_PATCH = 28
};
```

## Core Data Structures

### struct http_request

HTTP request structure, describing all parameters of an HTTP/HTTPS request:

```c
struct http_request {
    /* Internal data, application layer should not directly manipulate */
    struct http_client_internal_data internal;

    /* === The following fields must be filled by the user === */

    /** HTTP method: GET, POST, PUT, etc. */
    enum http_method method;

    /** Response callback function, called when server response is received (required) */
    http_response_cb_t response;

    /** HTTP parser callback settings, for obtaining detailed parsing information (optional) */
    const struct http_parser_settings *http_cb;

    /** User-provided receive buffer for storing response data (required) */
    uint8_t *recv_buf;

    /** Receive buffer length (required) */
    size_t recv_buf_len;

    /** Request URL path, e.g., "/index.html" or "/api/data" */
    const char *url;

    /** Protocol version, typically "HTTP/1.1" */
    const char *protocol;

    /** NULL-terminated HTTP header field list */
    const char **header_fields;

    /** Content-Type header value, e.g., "application/json" */
    const char *content_type_value;

    /** Target hostname, e.g., "api.example.com" (required) */
    const char *host;

    /** Port number string, e.g., "443" or "8080" (optional) */
    const char *port;

    /** Payload send callback, used when sending large amounts of data (optional) */
    http_payload_cb_t payload_cb;

    /** Request payload data, e.g., POST request body (optional) */
    const char *payload;

    /** Payload length; set to 0 for chunked transfer */
    size_t payload_len;

    /** Optional header send callback (optional) */
    http_header_cb_t optional_headers_cb;

    /** NULL-terminated optional header list (optional) */
    const char **optional_headers;

    /** Cancel callback, can be used to abort an in-progress request (optional) */
    http_cancel_cb_t cancel;
};
```

### struct http_response

HTTP response structure, passed to the application layer via callback functions:

```c
struct http_response {
    /** HTTP parser settings */
    const struct http_parser_settings *http_cb;

    /** User response callback function */
    http_response_cb_t cb;

    /** Response body data start address (relative to recv_buf) */
    uint8_t *body_frag_start;

    /** Response body fragment length */
    size_t body_frag_len;

    /** Receive buffer pointer */
    uint8_t *recv_buf;

    /** Receive buffer maximum length */
    size_t recv_buf_len;

    /** Total length of received data (may exceed recv_buf_len indicating truncation) */
    size_t data_len;

    /** Content-Length header value */
    size_t content_length;

    /** Bytes processed (delivered to callback) */
    size_t processed;

    /** HTTP status description string, e.g., "200 OK" */
    char http_status[HTTP_STATUS_STR_SIZE];

    /** HTTP status code, 3-digit number, e.g., 200, 404, 500 */
    uint16_t http_status_code;

    /** Content-Range information */
    struct http_content_range content_range;

    /** Flag bits */
    uint8_t cl_present : 1;        // Content-Length header present
    uint8_t body_found : 1;        // Message body found
    uint8_t message_complete : 1;   // HTTP message parsing complete
    uint8_t cr_present : 1;        // Content-Range header present
};
```

### struct https_client_request

HTTPS-specific request structure, extending TLS certificate configuration:

```c
struct https_client_request {
    /* HTTP-related fields (same as http_request) */
    enum http_method method;
    http_response_cb_t response;
    const struct http_parser_settings *http_cb;
    const char *url;
    const char *protocol;
    const char **header_fields;
    const char *content_type_value;
    http_payload_cb_t payload_cb;
    const char *payload;
    size_t payload_len;
    http_header_cb_t optional_headers_cb;
    const char **optional_headers;
    http_cancel_cb_t cancel;

    /* === TLS Certificate Configuration === */

    /** Server CA certificate (PEM format string), used to verify server identity */
    const char *ca_pem;
    size_t ca_len;

    /** Client certificate (PEM format), used for mutual authentication */
    const char *client_cert_pem;
    size_t client_cert_len;

    /** Client private key (PEM format), used for mutual authentication */
    const char *client_key_pem;
    size_t client_key_len;

    /** HTTP buffer size (shared for sending and receiving) */
    size_t buffer_size;
};
```

### struct http_wrapper_ssl_param_t

TLS underlying configuration parameters:

```c
typedef struct {
    const char *ca_cert;       // CA certificate
    int ca_cert_len;           // CA certificate length
    const char *own_cert;      // Own certificate
    int own_cert_len;          // Own certificate length
    const char *private_cert;  // Private key
    int private_cert_len;      // Private key length

    const char **alpn;         // ALPN protocol list
    int alpn_num;              // ALPN protocol count

    const char *psk;           // Pre-shared key
    int psk_len;
    const char *pskhint;       // PSK identity hint
    int pskhint_len;

    char *sni;                 // Server Name Indication
} http_wrapper_ssl_param_t;
```

## Callback Function Types

### http_response_cb_t

Response data callback, triggered each time the server returns a piece of data after sending an HTTP request:

```c
typedef void (*http_response_cb_t)(struct http_response *rsp,
                                   enum http_final_call final_data,
                                   void *user_data);
```

**Parameter descriptions:**
- `rsp`: Pointer to structure containing response data
- `final_data`: `HTTP_DATA_MORE` indicates more data available, `HTTP_DATA_FINAL` indicates this is the last batch of data
- `user_data`: Private data passed by the caller

### http_payload_cb_t

Payload send callback, used for sending large amounts of data in chunks:

```c
typedef int (*http_payload_cb_t)(int sock,
                                 struct http_request *req,
                                 void *user_data);
```

**Return values:**
- `>= 0`: Bytes sent, continue sending
- `< 0`: Error code, terminate the request

### http_header_cb_t

Optional header send callback:

```c
typedef int (*http_header_cb_t)(int sock,
                                struct http_request *req,
                                void *user_data);
```

### http_cancel_cb_t

Cancel callback, can terminate the request mid-way:

```c
typedef int (*http_cancel_cb_t)(void *user_data);
```

**Return values:**
- Non-zero: Stop receiving, return `-ECANCELED`
- Zero: Continue normal receiving

## Core API

### http_client_req()

Send HTTP request (asynchronous callback mode):

```c
int http_client_req(int sock, struct http_request *req,
                    int32_t timeout, void *user_data);
```

**Parameters:**
- `sock`: Established socket
- `req`: HTTP request structure pointer
- `timeout`: Timeout in milliseconds; `SYS_FOREVER_MS` means never timeout
- `user_data`: Private data passed to callbacks

**Return values:**
- `< 0`: Error code
- `>= 0`: Number of bytes sent to the server

**Description:**
The caller must first establish a network connection (TCP or TLS). This function is responsible for sending HTTP request headers and payload, then looping to receive server responses and distributing data via callbacks.

### https_client_request()

High-level HTTPS request interface, internally handles TLS connection automatically:

```c
int https_client_request(const struct https_client_request *request,
                         uint32_t timeout, void *user_data);
```

**Parameters:**
- `request`: HTTPS request configuration, including URL, method, TLS certificates, etc.
- `timeout`: Timeout in milliseconds
- `user_data`: Private data passed to callbacks

**Return values:**
- `< 0`: Error code
- `>= 0`: Success

**Description:**
This function encapsulates the entire process of TLS connection establishment, certificate verification, HTTP request sending, and response receiving. It is the most commonly used HTTPS interface.

### https_wrapper_connect()

Establish HTTPS connection:

```c
https_wrapper_handle_t https_wrapper_connect(const char *host_name,
                                             uint16_t port,
                                             http_wrapper_ssl_param_t *param);
```

**Parameters:**
- `host_name`: Target hostname
- `port`: Port number (typically 443)
- `param`: TLS parameters, can be NULL (HTTP mode)

**Return values:**
- Non-NULL: Valid HTTPS connection handle
- NULL: Connection failed

### https_wrapper_destroy()

Close HTTPS connection and release resources:

```c
int https_wrapper_destroy(https_wrapper_handle_t https);
```

### https_wrapper_send()

Send data over TLS:

```c
int https_wrapper_send(https_wrapper_handle_t https,
                      const void *data, uint16_t size, int flags);
```

### https_wrapper_recv()

Receive TLS data:

```c
int https_wrapper_recv(https_wrapper_handle_t https,
                      uint8_t *data, uint32_t size, int flags);
```

### https_wrapper_socketfd_get()

Get underlying socket file descriptor:

```c
int https_wrapper_socketfd_get(https_wrapper_handle_t https);
```

## mbedTLS SSL Context Integration

The HTTPS client indirectly uses mbedTLS through https_wrapper. The underlying mbedTLS configuration is passed through the `http_wrapper_ssl_param_t` structure, supporting the following security features:

### TLS Version Support

- TLS 1.2
- TLS 1.3

### Certificate Verification

**One-way authentication (server verification only):**
```c
ssl_param.ca_cert = server_ca_pem;
ssl_param.ca_cert_len = server_ca_len;
ssl_param.sni = hostname;  // Enable SNI hostname verification
```

**Two-way authentication (also verify client):**
```c
ssl_param.own_cert = client_cert_pem;
ssl_param.own_cert_len = client_cert_len;
ssl_param.private_cert = client_key_pem;
ssl_param.private_cert_len = client_key_len;
```

### PSK Pre-Shared Key Mode

Suitable for resource-constrained scenarios, saving certificate overhead:
```c
ssl_param.psk = psk_data;
ssl_param.psk_len = psk_len;
ssl_param.pskhint = psk_identity_hint;
```

### ALPN Protocol Negotiation

```c
const char *alpn_protos[] = { "http/1.1", "h2" };
ssl_param.alpn = alpn_protos;
ssl_param.alpn_num = 2;
```

## Code Examples

### Example 1: Basic HTTPS GET Request

```c
#include "https_client.h"
#include <stdio.h>
#include <string.h>

#define RECV_BUFFER_SIZE 1024

static uint8_t recv_buf[RECV_BUFFER_SIZE];

/* Response callback function */
static void response_callback(struct http_response *rsp,
                              enum http_final_call final_data,
                              void *user_data)
{
    if (rsp->body_frag_len > 0) {
        printf("[HTTP] Received %zu bytes, status: %s\r\n",
               rsp->body_frag_len, rsp->http_status);

        /* Process response body data */
        printf("Body: %.*s\r\n",
               (int)rsp->body_frag_len,
               rsp->body_frag_start);
    }

    if (final_data == HTTP_DATA_FINAL) {
        printf("[HTTP] Transfer complete, total: %zu bytes\r\n",
               rsp->processed);
    }
}

/* HTTPS GET request */
int https_get_example(void)
{
    int ret;
    struct https_client_request request;

    memset(&request, 0, sizeof(request));

    request.method = HTTP_GET;
    request.url = "https://api.example.com/data";
    request.protocol = "HTTP/1.1";
    request.response = response_callback;

    /* Server certificate verification (optional) */
    request.ca_pem = trusted_ca_pem;
    request.ca_len = trusted_ca_len;

    ret = https_client_request(&request, 30000, NULL);
    if (ret < 0) {
        printf("[HTTPS] Request failed: %d\r\n", ret);
        return ret;
    }

    return 0;
}
```

### Example 2: HTTPS POST Request with Custom Headers

```c
#include "https_client.h"
#include <stdio.h>
#include <string.h>

static uint8_t recv_buf[2048];
static const char *post_headers[] = {
    "X-Api-Key: your-api-key-here",
    "X-Request-Id: 12345",
    NULL
};

/* Response callback */
static void post_response_callback(struct http_response *rsp,
                                   enum http_final_call final_data,
                                   void *user_data)
{
    if (rsp->http_status_code >= 200 && rsp->http_status_code < 300) {
        printf("[HTTPS] Success: %s\r\n", rsp->http_status);
    } else {
        printf("[HTTPS] Error: %s (%d)\r\n",
               rsp->http_status, rsp->http_status_code);
    }

    if (rsp->body_found && rsp->body_frag_len > 0) {
        printf("[Response] %.*s\r\n",
               (int)rsp->body_frag_len,
               rsp->body_frag_start);
    }
}

/* HTTPS POST request example */
int https_post_example(void)
{
    int ret;
    struct https_client_request request;
    const char *json_payload = "{\"name\":\"test\",\"value\":123}";
    const char *content_type = "application/json";

    memset(&request, 0, sizeof(request));

    request.method = HTTP_POST;
    request.url = "https://api.example.com/endpoint";
    request.protocol = "HTTP/1.1";
    request.response = post_response_callback;
    request.recv_buf = recv_buf;
    request.recv_buf_len = sizeof(recv_buf);
    request.content_type_value = content_type;
    request.header_fields = post_headers;
    request.payload = json_payload;
    request.payload_len = strlen(json_payload);

    /* Enable server certificate verification */
    request.ca_pem = trusted_ca_pem;
    request.ca_len = trusted_ca_len;

    ret = https_client_request(&request, 30000, NULL);
    return ret;
}
```

### Example 3: Receiving Large Files in Chunks

```c
#include "https_client.h"
#include <stdio.h>
#include <fcntl.h>

#define CHUNK_SIZE 4096
static uint8_t recv_buf[CHUNK_SIZE];

/* Track download progress */
static size_t total_downloaded = 0;

/* Response callback - stream processing for large files */
static void download_callback(struct http_response *rsp,
                              enum http_final_call final_data,
                              void *user_data)
{
    if (rsp->body_frag_len > 0) {
        /* Process each data chunk */
        total_downloaded += rsp->body_frag_len;

        printf("[Download] Progress: %zu / %zu bytes (%.1f%%)\r\n",
               total_downloaded,
               rsp->content_length,
               (double)total_downloaded / rsp->content_length * 100.0);
    }

    if (final_data == HTTP_DATA_FINAL) {
        printf("[Download] Complete: %zu bytes received\r\n",
               total_downloaded);
        total_downloaded = 0;
    }
}

/* Download file */
int download_file(const char *url, const char *output_path)
{
    int ret;
    struct https_client_request request;

    memset(&request, 0, sizeof(request));

    request.method = HTTP_GET;
    request.url = url;
    request.protocol = "HTTP/1.1";
    request.response = download_callback;
    request.recv_buf = recv_buf;
    request.recv_buf_len = sizeof(recv_buf);
    request.ca_pem = trusted_ca_pem;
    request.ca_len = trusted_ca_len;

    ret = https_client_request(&request, 120000, NULL);
    return ret;
}
```

### Example 4: Using Low-Level API for Custom TLS Configuration

```c
#include "https_wrapper.h"
#include "http/client.h"
#include <stdio.h>

/* Custom TLS parameters */
static http_wrapper_ssl_param_t ssl_config = {
    .ca_cert = trusted_ca_pem,
    .ca_cert_len = trusted_ca_len,
    .sni = "api.example.com",
    /* PSK mode (optional) */
    .psk = NULL,
    .psk_len = 0,
    /* ALPN */
    .alpn = (const char*[]){"http/1.1"},
    .alpn_num = 1,
};

/* Response callback */
static void response_cb(struct http_response *rsp,
                       enum http_final_call final_data,
                       void *user_data)
{
    if (rsp->body_frag_len > 0) {
        printf("%.*s", (int)rsp->body_frag_len, rsp->body_frag_start);
    }
    if (final_data == HTTP_DATA_FINAL) {
        printf("\r\n[Done]\r\n");
    }
}

int custom_tls_request(void)
{
    int sock;
    struct http_request req;
    uint8_t recv_buf[1024];

    /* Establish HTTPS connection */
    https_wrapper_handle_t https = https_wrapper_connect(
        "api.example.com", 443, &ssl_config);
    if (!https) {
        printf("Connection failed\r\n");
        return -1;
    }

    sock = https_wrapper_socketfd_get(https);

    /* Build HTTP request */
    memset(&req, 0, sizeof(req));
    req.method = HTTP_GET;
    req.url = "/api/data";
    req.protocol = "HTTP/1.1";
    req.host = "api.example.com";
    req.response = response_cb;
    req.recv_buf = recv_buf;
    req.recv_buf_len = sizeof(recv_buf);

    /* Send request */
    int ret = http_client_req(sock, &req, 30000, NULL);

    /* Close connection */
    https_wrapper_destroy(https);

    return ret;
}
```

## Error Handling

Common error codes:

| Error Code | Meaning |
|--------|------|
| `-EINVAL` | Invalid parameter (null pointer, buffer of 0, etc.) |
| `-ECONNREFUSED` | Connection refused |
| `-ECONNRESET` | Connection reset by peer |
| `-ECANCELED` | Request terminated by cancel callback |
| `-ENOMEM` | Memory allocation failed |
| `-ETIMEDOUT` | Operation timed out |

## Notes

1. **Keep-alive**: HTTP/1.1 enables keep-alive by default, allowing multiple requests on the same connection
2. **Buffer size**: Reasonably set `recv_buf` based on expected response size; for large responses, chunked processing is recommended
3. **TLS certificates**: Always verify server certificates in production environments; may be skipped in testing environments
4. **Timeout settings**: Set reasonable timeout values in unstable network environments
5. **Thread safety**: Callback functions may be invoked in interrupt or dedicated thread contexts; ensure thread safety

---

## References

- Bouffalo SDK `components/net/lib/http/` source code
- `http/client.h` - HTTP client core API definitions
- `https_client.h` - HTTPS client wrapper interface
- `https_wrapper.h` - mbedTLS wrapper interface
- `http/parser.h` - HTTP message parser (based on http_parser v2.7.1)
- [Zephyr net/http library](https://docs.zephyrproject.org/latest/connectivity/networking/api/http_client.html)
- [mbedTLS Documentation](https://mbedtls.readthedocs.io/)
