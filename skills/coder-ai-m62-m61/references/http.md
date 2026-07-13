# HTTP/HTTPS Client API Reference

## Overview

The Bouffalo SDK provides HTTP and HTTPS client functionality built on top of lwIP and mbedtls. The HTTP client API is derived from Zephyr's net/http library, while HTTPS support is implemented through a TLS wrapper.

## Header Files

- `http/client.h` - HTTP client API
- `http/method.h` - HTTP methods enum
- `http/status.h` - HTTP status codes
- `http/parser.h` - HTTP parser
- `https_client.h` - HTTPS client wrapper
- `https_wrapper.h` - TLS/SSL wrapper interface

## HTTP Methods

Defined in `http/method.h`:

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
    HTTP_PATCH = 28,
    /* ... more methods */
};
```

## Core Data Structures

### http_request

```c
struct http_request {
    struct http_client_internal_data internal;  // Internal use
    
    /* User-fillable fields */
    enum http_method method;              // HTTP method (GET, POST, etc.)
    http_response_cb_t response;          // Response callback (required)
    const struct http_parser_settings *http_cb;  // Parser callbacks (optional)
    uint8_t *recv_buf;                   // Response buffer (required)
    size_t recv_buf_len;                 // Buffer length (required)
    const char *url;                     // URL path (e.g., "/index.html")
    const char *protocol;                // Protocol (e.g., "HTTP/1.1")
    const char **header_fields;           // NULL-terminated header list
    const char *content_type_value;       // Content-Type value
    const char *host;                    // Hostname (required)
    const char *port;                    // Port (optional, e.g., "80")
    http_payload_cb_t payload_cb;         // Payload send callback
    const char *payload;                 // Payload data
    size_t payload_len;                  // Payload length
    http_header_cb_t optional_headers_cb;// Optional headers callback
    const char **optional_headers;        // Optional headers list
    http_cancel_cb_t cancel;              // Cancel callback
};
```

### http_response

```c
struct http_response {
    const struct http_parser_settings *http_cb;
    http_response_cb_t cb;
    uint8_t *body_frag_start;           // Body data start
    size_t body_frag_len;               // Body fragment length
    uint8_t *recv_buf;                  // Receive buffer
    size_t recv_buf_len;                // Buffer length
    size_t data_len;                    // Total data received
    size_t content_length;              // Content-Length header
    size_t processed;                   // Bytes processed so far
    char http_status[32];               // Status string
    uint16_t http_status_code;          // Numeric status code
    struct http_content_range content_range;
    uint8_t cl_present : 1;            // Content-Length present
    uint8_t body_found : 1;            // Body found
    uint8_t message_complete : 1;       // Message complete
    uint8_t cr_present : 1;            // Content-Range present
};
```

### Callbacks

```c
// Called when response data is received
typedef void (*http_response_cb_t)(struct http_response *rsp,
                                   enum http_final_call final_data,
                                   void *user_data);

// Called when payload needs to be sent
typedef int (*http_payload_cb_t)(int sock, struct http_request *req, void *user_data);

// Called to add optional headers
typedef int (*http_header_cb_t)(int sock, struct http_request *req, void *user_data);

// Called to check if request should be canceled
typedef int (*http_cancel_cb_t)(void *user_data);
```

### https_client_request

```c
struct https_client_request {
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
    
    /* TLS/SSL certificates (PEM format) */
    const char *ca_pem;              // Server CA certificate
    size_t ca_len;
    const char *client_cert_pem;     // Client certificate
    size_t client_cert_len;
    const char *client_key_pem;      // Client private key
    size_t client_key_len;
    size_t buffer_size;              // HTTP buffer size
};

// Main HTTPS request function
int https_client_request(const struct https_client_request *request, 
                        uint32_t timeout, void *user_data);
```

## HTTP API Functions

### http_client_req

```c
int http_client_req(int sock, struct http_request *req,
                    int32_t timeout, void *user_data);
```

Send an HTTP request on an existing socket.

**Parameters:**
- `sock` - Connected socket file descriptor
- `req` - HTTP request structure
- `timeout` - Timeout in milliseconds (0 = no timeout)
- `user_data` - User data passed to callbacks

**Returns:** Number of bytes sent on success, negative errno on failure

**Requirements:**
- Socket must be already connected
- `req->response` callback must be set
- `req->recv_buf` must be provided
- `req->host` should be set

## HTTPS/TLS Wrapper API

### https_wrapper_ssl_param_t

```c
typedef struct {
    const char *ca_cert;       // CA certificate (PEM)
    int ca_cert_len;
    const char *own_cert;      // Own certificate (PEM)
    int own_cert_len;
    const char *private_cert;  // Private key (PEM)
    int private_cert_len;
    const char **alpn;         // ALPN protocols
    int alpn_num;
    const char *psk;           // Pre-shared key
    int psk_len;
    const char *pskhint;       // PSK identity hint
    int pskhint_len;
    char *sni;                // Server Name Indication
} http_wrapper_ssl_param_t;
```

### https_wrapper_connect

```c
https_wrapper_handle_t https_wrapper_connect(const char *host_name, 
                                             uint16_t port, 
                                             http_wrapper_ssl_param_t *param);
```

Create a TLS connection to host.

### https_wrapper_destroy

```c
int https_wrapper_destroy(https_wrapper_handle_t https);
```

Close and free TLS connection.

### https_wrapper_send/recv

```c
int https_wrapper_send(https_wrapper_handle_t https, 
                       const void *data, uint16_t size, int flags);

int https_wrapper_recv(https_wrapper_handle_t https, 
                       uint8_t *data, uint32_t size, int flags);
```

Send/receive data over TLS.

### https_wrapper_socketfd_get

```c
int https_wrapper_socketfd_get(https_wrapper_handle_t https);
```

Get underlying socket file descriptor for use with `http_client_req()`.

## HTTP Status Codes

```c
enum http_status {
    HTTP_200_OK = 200,
    HTTP_201_CREATED = 201,
    HTTP_204_NO_CONTENT = 204,
    HTTP_301_MOVED_PERMANENTLY = 301,
    HTTP_302_FOUND = 302,
    HTTP_400_BAD_REQUEST = 400,
    HTTP_401_UNAUTHORIZED = 401,
    HTTP_403_FORBIDDEN = 403,
    HTTP_404_NOT_FOUND = 404,
    HTTP_500_INTERNAL_SERVER_ERROR = 500,
    HTTP_503_SERVICE_UNAVAILABLE = 503,
    /* ... more codes */
};
```

## Working Code Examples

### HTTP GET Request

```c
#include <http/client.h>
#include <net/socket.h>

static uint8_t recv_buf[2048];

static void http_response_cb(struct http_response *rsp,
                             enum http_final_call final_data,
                             void *user_data)
{
    if (final_data == HTTP_DATA_MORE) {
        printf("Received %zu bytes, body: %.*s\n",
               rsp->body_frag_len,
               (int)rsp->body_frag_len,
               rsp->body_frag_start);
    } else {
        printf("Response complete, status: %s (%d)\n",
               rsp->http_status, rsp->http_status_code);
    }
}

int http_get_example(int sock)
{
    struct http_request req = {0};
    int ret;

    req.method = HTTP_GET;
    req.url = "/api/data";
    req.protocol = "HTTP/1.1";
    req.host = "example.com";
    req.response = http_response_cb;
    req.recv_buf = recv_buf;
    req.recv_buf_len = sizeof(recv_buf);
    
    /* Optional: add custom headers */
    const char *headers[] = {
        "User-Agent: BL618-HTTP-Client/1.0",
        "Accept: application/json",
        NULL
    };
    req.header_fields = headers;

    ret = http_client_req(sock, &req, 30000, NULL);
    if (ret < 0) {
        printf("HTTP request failed: %d\n", ret);
        return ret;
    }
    
    return 0;
}
```

### HTTP POST Request with JSON Payload

```c
#include <http/client.h>
#include <net/socket.h>

static uint8_t recv_buf[2048];
static const char *json_payload = "{\"temperature\": 25.5, \"humidity\": 60}";

static void http_response_cb(struct http_response *rsp,
                             enum http_final_call final_data,
                             void *user_data)
{
    if (final_data == HTTP_DATA_MORE) {
        printf("Received body: %.*s\n",
               (int)rsp->body_frag_len,
               rsp->body_frag_start);
    } else {
        printf("POST complete, status: %s (%d)\n",
               rsp->http_status, rsp->http_status_code);
    }
}

int http_post_example(int sock)
{
    struct http_request req = {0};
    int ret;

    req.method = HTTP_POST;
    req.url = "/api/sensors";
    req.protocol = "HTTP/1.1";
    req.host = "example.com";
    req.response = http_response_cb;
    req.recv_buf = recv_buf;
    req.recv_buf_len = sizeof(recv_buf);
    req.payload = json_payload;
    req.payload_len = strlen(json_payload);
    req.content_type_value = "application/json";

    ret = http_client_req(sock, &req, 30000, NULL);
    if (ret < 0) {
        printf("HTTP POST failed: %d\n", ret);
        return ret;
    }
    
    return 0;
}
```

### HTTPS GET Request (with mbedtls)

```c
#include <https_client.h>
#include <https_wrapper.h>

static uint8_t recv_buf[4096];

static void https_response_cb(struct http_response *rsp,
                              enum http_final_call final_data,
                              void *user_data)
{
    if (final_data == HTTP_DATA_MORE) {
        printf("HTTPS body received: %.*s\n",
               (int)rsp->body_frag_len,
               rsp->body_frag_start);
    } else {
        printf("HTTPS response complete: %s (%d)\n",
               rsp->http_status, rsp->http_status_code);
    }
}

int https_get_example(void)
{
    struct https_client_request req = {0};
    int ret;

    /* Server CA certificate for verification */
    const char *ca_pem = 
        "-----BEGIN CERTIFICATE-----\n"
        "MIIDXTCCAkWgAwIBAgIJAKJ...\n"
        "-----END CERTIFICATE-----\n";

    req.method = HTTP_GET;
    req.url = "/secure/api";
    req.protocol = "HTTP/1.1";
    req.response = https_response_cb;
    req.recv_buf = recv_buf;
    req.recv_buf_len = sizeof(recv_buf);
    req.host = "secure.example.com";
    
    /* TLS configuration */
    req.ca_pem = ca_pem;
    req.ca_len = strlen(ca_pem);
    req.buffer_size = 2048;

    ret = https_client_request(&req, 30000, NULL);
    if (ret < 0) {
        printf("HTTPS request failed: %d\n", ret);
        return ret;
    }
    
    return 0;
}
```

### HTTPS with Client Certificate Authentication

```c
int https_mutual_auth_example(void)
{
    struct https_client_request req = {0};
    int ret;

    /* Server CA */
    const char *ca_pem = "-----BEGIN CERTIFICATE-----\n...";
    
    /* Client certificate and key */
    const char *client_cert_pem = "-----BEGIN CERTIFICATE-----\n...";
    const char *client_key_pem = "-----BEGIN RSA PRIVATE KEY-----\n...";

    req.method = HTTP_POST;
    req.url = "/api/protected";
    req.protocol = "HTTP/1.1";
    req.response = https_response_cb;
    req.recv_buf = recv_buf;
    req.recv_buf_len = sizeof(recv_buf);
    req.host = "api.example.com";
    req.payload = "data=test";
    req.payload_len = 9;
    req.content_type_value = "application/x-www-form-urlencoded";
    
    /* TLS certificates */
    req.ca_pem = ca_pem;
    req.ca_len = strlen(ca_pem);
    req.client_cert_pem = client_cert_pem;
    req.client_cert_len = strlen(client_cert_pem);
    req.client_key_pem = client_key_pem;
    req.client_key_len = strlen(client_key_pem);
    req.buffer_size = 2048;

    ret = https_client_request(&req, 30000, NULL);
    return ret;
}
```

### Using https_wrapper for Manual TLS Control

```c
#include <https_wrapper.h>

int manual_https_example(void)
{
    http_wrapper_ssl_param_t ssl_param = {0};
    https_wrapper_handle_t https;
    int sock;
    int ret;
    
    /* Configure TLS */
    ssl_param.ca_cert = server_ca_pem;
    ssl_param.ca_cert_len = strlen(server_ca_pem);
    ssl_param.sni = "api.example.com";
    
    /* Connect with TLS */
    https = https_wrapper_connect("api.example.com", 443, &ssl_param);
    if (!https) {
        printf("TLS connection failed\n");
        return -1;
    }
    
    /* Get socket for HTTP request */
    sock = https_wrapper_socketfd_get(https);
    
    /* Now use sock with http_client_req() */
    struct http_request req = {0};
    req.method = HTTP_GET;
    req.url = "/api/data";
    req.protocol = "HTTP/1.1";
    req.host = "api.example.com";
    req.response = my_response_cb;
    req.recv_buf = recv_buf;
    req.recv_buf_len = sizeof(recv_buf);
    
    ret = http_client_req(sock, &req, 30000, NULL);
    
    /* Or use https_wrapper_send/recv directly */
    const char *get_request = 
        "GET /api/data HTTP/1.1\r\n"
        "Host: api.example.com\r\n"
        "\r\n";
    
    ret = https_wrapper_send(https, get_request, strlen(get_request), 0);
    if (ret > 0) {
        uint8_t buf[1024];
        ret = https_wrapper_recv(https, buf, sizeof(buf), 0);
    }
    
    https_wrapper_destroy(https);
    return ret;
}
```

### HTTP Request with Dynamic Headers Callback

```c
static int header_callback(int sock, struct http_request *req, void *user_data)
{
    const char *auth_header = "Authorization: Bearer token123\r\n";
    int len = strlen(auth_header);
    
    /* Send directly on socket */
    return send(sock, auth_header, len, 0);
}

int http_with_dynamic_headers(int sock)
{
    struct http_request req = {0};

    req.method = HTTP_GET;
    req.url = "/api/protected";
    req.protocol = "HTTP/1.1";
    req.host = "example.com";
    req.response = http_response_cb;
    req.recv_buf = recv_buf;
    req.recv_buf_len = sizeof(recv_buf);
    
    /* Use callback for dynamic headers */
    req.optional_headers_cb = header_callback;

    return http_client_req(sock, &req, 30000, NULL);
}
```

### HTTP Request with Payload Callback (Streaming)

```c
static int payload_callback(int sock, struct http_request *req, void *user_data)
{
    FILE *fp = (FILE *)user_data;
    char chunk[512];
    int bytes_read;
    int total_sent = 0;
    
    while ((bytes_read = fread(chunk, 1, sizeof(chunk), fp)) > 0) {
        int ret = send(sock, chunk, bytes_read, 0);
        if (ret < 0) return ret;
        total_sent += ret;
    }
    
    return total_sent;
}

int http_upload_file(int sock, FILE *fp)
{
    struct http_request req = {0};

    req.method = HTTP_POST;
    req.url = "/api/upload";
    req.protocol = "HTTP/1.1";
    req.host = "example.com";
    req.response = http_response_cb;
    req.recv_buf = recv_buf;
    req.recv_buf_len = sizeof(recv_buf);
    req.payload_cb = payload_callback;
    req.payload_len = 0;  /* Use 0 for chunked transfer */
    req.content_type_value = "application/octet-stream";

    return http_client_req(sock, &req, 60000, fp);
}
```

### HTTP Request with Cancel Capability

```c
static volatile bool cancel_request = false;

static int cancel_callback(void *user_data)
{
    return cancel_request ? 1 : 0;
}

int http_with_cancel(int sock)
{
    struct http_request req = {0};

    req.method = HTTP_GET;
    req.url = "/api/large-data";
    req.protocol = "HTTP/1.1";
    req.host = "example.com";
    req.response = http_response_cb;
    req.recv_buf = recv_buf;
    req.recv_buf_len = sizeof(recv_buf);
    req.cancel = cancel_callback;

    /* In another thread or timer, set: */
    /* cancel_request = true; */
    
    return http_client_req(sock, &req, 30000, NULL);
}
```

## Socket Setup for HTTP

Before using `http_client_req()`, you must create and connect a socket:

```c
#include <net/socket.h>

int create_tcp_socket(void)
{
    int sock;
    struct sockaddr_in server_addr;
    int ret;

    sock = socket(AF_INET, SOCK_STREAM, 0);
    if (sock < 0) {
        return sock;
    }

    memset(&server_addr, 0, sizeof(server_addr));
    server_addr.sin_family = AF_INET;
    server_addr.sin_port = htons(80);
    inet_pton(AF_INET, "93.184.216.34", &server_addr.sin_addr);

    ret = connect(sock, (struct sockaddr *)&server_addr, sizeof(server_addr));
    if (ret < 0) {
        close(sock);
        return ret;
    }

    return sock;
}
```

## Common Patterns

### Simple Blocking GET

```c
int simple_http_get(const char *host, const char *path)
{
    int sock = socket(AF_INET, SOCK_STREAM, 0);
    struct http_request req = {0};
    uint8_t buf[2048];
    int ret;

    /* Connect to server */
    connect(sock, ...);

    req.method = HTTP_GET;
    req.url = path;
    req.protocol = "HTTP/1.1";
    req.host = host;
    req.response = response_callback;
    req.recv_buf = buf;
    req.recv_buf_len = sizeof(buf);

    ret = http_client_req(sock, &req, 30000, NULL);
    close(sock);
    return ret;
}
```

### Parse Response Body

```c
static void parse_json_response(struct http_response *rsp,
                                 enum http_final_call final_data,
                                 void *user_data)
{
    if (final_data == HTTP_DATA_FINAL && rsp->body_frag_len > 0) {
        /* Ensure null-termination for string parsing */
        char *body = (char *)rsp->body_frag_start;
        size_t len = rsp->body_frag_len;
        
        /* body now contains JSON string of length len */
        printf("JSON response: %.*s\n", (int)len, body);
    }
}
```

## Error Handling

`http_client_req()` returns:
- **Positive value**: Number of bytes sent (success)
- **0**: Connection closed
- **Negative errno**: Error (e.g., -ETIMEDOUT, -ECONNRESET, -EINVAL)

Common errors:
- `-EINVAL` - Invalid parameters (missing callback, buffer, etc.)
- `-ETIMEDOUT` - Request timeout
- `-ECONNRESET` - Connection reset by peer
- `-EAGAIN` - Would block (non-blocking socket)

## Notes

1. The HTTP client requires a **pre-connected socket**. Use lwIP's socket API to establish the TCP connection first.

2. For HTTPS, you can either:
   - Use `https_client_request()` directly (simplest)
   - Use `https_wrapper_connect()` + `http_client_req()` (more control)

3. The response callback is **required** and is called multiple times for chunked responses.

4. Headers are sent in order: Host → Optional Headers → Custom Headers → Content-Type → body

5. For large responses, ensure `recv_buf` is large enough or use callback-based processing to handle data in chunks.
