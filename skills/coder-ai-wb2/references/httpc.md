# HTTP Client (HTTPC) API Reference

> Source file: `components/network/httpd/include/http_client.h`  
> HTTP client implementation based on LwIP altcp, with HTTPS (TLS) support.

---

## Overview

BL602 HTTPC supports:
- HTTP/HTTPS GET and POST requests
- Custom request headers
- Request body sending (POST)
- Response header and body reading
- Connection timeout configuration

---

## Header File

```c
#include "http_client.h"
```

---

## Type Definitions

### `httpc_request_header`

HTTP request header.

```c
typedef struct {
    const char *name;    // Request header name (e.g., "Content-Type")
    const char *value;   // Request header value
} httpc_request_header_t;
```

### `httpc_response`

HTTP response structure.

```c
typedef struct {
    int status_code;          // HTTP status code (e.g., 200, 404)
    uint32_t content_length;  // Content-Length (if present)
    char *header_data;        // Response header data (requires external freeing)
} httpc_response_t;
```

### `httpc_cb`

Response data callback function type.

```c
typedef err_t (*httpc_cb)(void *arg,
                            struct altcp_pcb *pcb,
                            struct pbuf *p,
                            err_t err);
```

---

## Function Interface

### `httpc_get`

Sends an HTTP GET request.

```c
err_t httpc_get(struct altcp_pcb *pcb,
                const char *url,
                const httpc_request_header_t *headers,
                int num_headers,
                void *callback_arg,
                httpc_cb resp_fn,
                httpc_response_t *resp);
```

---

### `httpc_post`

Sends an HTTP POST request.

```c
err_t httpc_post(struct altcp_pcb *pcb,
                 const char *url,
                 const char *content_type,
                 const void *body,
                 size_t body_len,
                 const httpc_request_header_t *headers,
                 int num_headers,
                 void *callback_arg,
                 httpc_cb resp_fn,
                 httpc_response_t *resp);
```

---

### `httpc_request`

General HTTP request (supports custom methods).

```c
err_t httpc_request(struct altcp_pcb *pcb,
                    const char *url,
                    const char *method,
                    const char *content_type,
                    const void *body,
                    size_t body_len,
                    const httpc_request_header_t *headers,
                    int num_headers,
                    void *callback_arg,
                    httpc_cb resp_fn,
                    httpc_response_t *resp);
```

---

## Usage Examples

### Simple GET Request

```c
#include "http_client.h"

static err_t my_resp_cb(void *arg, struct altcp_pcb *pcb,
                        struct pbuf *p, err_t err)
{
    if (p != NULL) {
        // Print response content
        char *data = (char *)p->payload;
        printf("Response (%d bytes): %.*s\r\n", p->len, p->len, data);
        altcp_recved(pcb, p->len); // Notify protocol stack data processed
        pbuf_free(p);
    } else {
        // Response complete
        printf("Response complete\r\n");
    }
    return ERR_OK;
}

void http_get_example(void)
{
    struct altcp_pcb *pcb = altcp_new(NULL); // Use default PCB
    if (!pcb) return;

    httpc_response_t resp;
    err_t err = httpc_get(pcb,
                           "http://httpbin.org/get",
                           NULL, 0,        // No extra headers
                           NULL,           // callback_arg
                           my_resp_cb,     // Response callback
                           &resp);         // Response structure

    if (err != ERR_OK) {
        printf("HTTP request failed: %d\r\n", err);
    }
}
```

### POST Request (JSON Data)

```c
static err_t post_resp_cb(void *arg, struct altcp_pcb *pcb,
                          struct pbuf *p, err_t err)
{
    if (p != NULL) {
        printf("POST response: %.*s\r\n", p->len, (char *)p->payload);
        altcp_recved(pcb, p->len);
        pbuf_free(p);
    } else {
        printf("POST complete\r\n");
    }
    return ERR_OK;
}

void http_post_example(void)
{
    struct altcp_pcb *pcb = altcp_new(NULL);

    const char *json_body = "{\"name\":\"BL602\",\"value\":123}";
    httpc_request_header_t headers[] = {
        {"Content-Type", "application/json"},
        {"Authorization", "Bearer token123"},
    };

    httpc_response_t resp;
    err_t err = httpc_post(pcb,
                            "http://httpbin.org/post",
                            "application/json",
                            json_body,
                            strlen(json_body),
                            headers,
                            2,
                            NULL,
                            post_resp_cb,
                            &resp);

    if (err == ERR_OK) {
        printf("HTTP status: %d\r\n", resp.status_code);
    }
}
```
