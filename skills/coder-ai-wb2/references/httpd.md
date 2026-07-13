# HTTP Server (HTTPD) API Reference

> Source file: `components/network/httpd/include/httpd.h`  
> BL602 built-in lightweight HTTP server, supporting CGI scripts and static file serving.

---

## Overview

BL602 HTTPD working mode:

```
Browser/Client  ──HTTP──▶  BL602 HTTPD  ──▶  CGI Script Processing
                              │
                              └──▶  Static Files (SPI Flash)
```

**Features**:
- Integrated on top of LwIP protocol stack (based on `altcp`)
- Supports CGI (Common Gateway Interface) callbacks
- Supports URI routing registration
- Supports POST data processing

---

## Header File

```c
#include "httpd.h"
```

---

## CGI Callbacks

### `tCGI`

CGI handler function type definition.

```c
typedef err_t (*tCGI)(struct httpd_state *pVars, char *pBuffer, int iBufferLen);
```

| Parameter | Description |
|-----------|-------------|
| `pVars` | HTTP request state structure (contains request method, URI, parameters, POST data, etc.) |
| `pBuffer` | Output buffer, used to write response content |
| `iBufferLen` | Buffer size |

**Return value**: `ERR_OK` (success) or other LwIP err_t

---

### `httpd_register_cgi`

Registers a CGI route.

```c
void httpd_register_cgi(const char *pcMyURI, tCGI pFunction);
```

| Parameter | Description |
|-----------|-------------|
| `pcMyURI` | URI path, such as `"/api/led"` |
| `pFunction` | CGI function that handles this URI |

---

## SSI Callbacks

### `tSSIHandler`

SSI (Server Side Include) handler function type.

```c
typedef u16_t (*tSSIHandler)(const char *pcInsert, char *pBuffer, u16_t iBufferLen);
```

---

### `httpd_register_ssi_handler`

Registers an SSI handler function.

```c
void httpd_register_ssi_handler(tSSIHandler pHandler,
                                const char **ppcTags,
                                u16_t uiNumTags);
```

| Parameter | Description |
|-----------|-------------|
| `pHandler` | SSI handler function |
| `ppcTags` | SSI tag array (e.g., `{"temp", "humidity"}`) |
| `uiNumTags` | Number of tags |

---

## Initialization

### `httpd_init`

Initializes and starts the HTTP server.

```c
void httpd_init(void);
```

> Default listener is `0.0.0.0:80`. After calling this function, HTTPD begins receiving HTTP requests.

---

### `httpd_set_port`

Sets the listening port (must be called before `httpd_init`).

```c
void httpd_set_port(uint16_t port);
```

---

## CGI Usage Example

### CGI Callback Function Implementation

```c
#include "httpd.h"

static err_t cgi_led_handler(struct httpd_state *pVars,
                              char *pBuffer, int iBufferLen)
{
    const char *method = pVars->request_method; // "GET" or "POST"

    if (strcmp(method, "GET") == 0) {
        // GET /api/led: Return current LED status
        snprintf(pBuffer, iBufferLen,
                 "HTTP/1.1 200 OK\r\n"
                 "Content-Type: application/json\r\n"
                 "Connection: close\r\n"
                 "\r\n"
                 "{\"led\":%d}",
                 led_state);
    } else if (strcmp(method, "POST") == 0) {
        // POST /api/led: Parse body to set LED status
        char *body = pVars->pcPostData; // POST request body
        // Parse body, set LED
        snprintf(pBuffer, iBufferLen,
                 "HTTP/1.1 200 OK\r\n"
                 "Content-Type: text/plain\r\n"
                 "\r\n"
                 "OK");
    }

    return ERR_OK;
}

static err_t cgi_sensor_handler(struct httpd_state *pVars,
                                 char *pBuffer, int iBufferLen)
{
    // Read sensor data
    int temp = read_temperature();
    int humi = read_humidity();

    snprintf(pBuffer, iBufferLen,
             "HTTP/1.1 200 OK\r\n"
             "Content-Type: application/json\r\n"
             "Cache-Control: no-cache\r\n"
             "\r\n"
             "{\"temp\":%d,\"humidity\":%d}",
             temp, humi);

    return ERR_OK;
}
```

### Register CGI and Start

```c
void app_main(void)
{
    // Other initialization...

    // Register CGI routes
    httpd_register_cgi("/api/led", cgi_led_handler);
    httpd_register_cgi("/api/sensor", cgi_sensor_handler);

    // Start HTTP server
    httpd_init();
    printf("HTTP server started on port 80\r\n");
}
```

## SSI Usage Example

```c
static u16_t ssi_handler(const char *pcInsert, char *pBuffer, u16_t iBufferLen)
{
    if (strcmp(pcInsert, "temp") == 0) {
        return snprintf(pBuffer, iBufferLen, "%d", read_temperature());
    } else if (strcmp(pcInsert, "humidity") == 0) {
        return snprintf(pBuffer, iBufferLen, "%d", read_humidity());
    }
    return 0;
}

static const char *tags[] = {"temp", "humidity"};

void app_main(void)
{
    httpd_register_ssi_handler(ssi_handler, tags, 2);
    httpd_init();
}
```

Using `<!--#temp-->` in an HTML template will be replaced with the actual temperature value.

## httpd_state Key Fields

| Field | Type | Description |
|-------|------|-------------|
| `request_method` | `char *` | Request method: "GET" or "POST" |
| `uri` | `char *` | Request URI path |
| `pcGetVars` | `char *` | URL query parameters (GET request) |
| `pcPostData` | `char *` | POST request body data |
| `iPostDataLen` | `int` | POST data length |
| `remote_ip` | `u32_t` | Client IP address |
| `remote_port` | `u16_t` | Client port |
