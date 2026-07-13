# lwIP HTTPD Server API Reference (BL616/BL618)

## Overview

The bouffalo_sdk for BL616/BL618 includes the lwIP HTTPD Server built into `components/net/lwip/`, supporting a full range of features including **HTTP server**, **CGI dynamic routing**, **SSI tag replacement**, and **POST data reception**. This implementation is based on the lightweight HTTPd from the Swedish Institute of Computer Science, extended by Texas Instruments with SSI/CGI capabilities.

**Location:** `components/net/lwip/lwip/src/include/lwip/apps/`

---

## Header Files

| File | Description |
|------|------|
| `lwip/apps/httpd.h` | HTTPD core API (CGI/SSI/HTTP Server) |
| `lwip/apps/httpd_opts.h` | Feature switches and configuration macros |
| `lwip/apps/fs.h` | Filesystem abstraction layer (fs_open/fs_read/fs_close) |
| `lwip/apps/fs.c` | Default RAM filesystem implementation |

---

## Initialization

### httpd_init()

Start the HTTP server (listening on port 80):

```c
#include "lwip/apps/httpd.h"

void httpd_init(void);
```

**Example:**

```c
void app_main(void)
{
    // Initialize LwIP protocol stack (see lwip.md)
    tcpip_init(lwip_init_done, NULL);
}

static void lwip_init_done(void *arg)
{
    // Start HTTP server after LwIP initialization is complete
    httpd_init();
    printf("HTTP server started on port 80\r\n");
}
```

### httpd_inits() — HTTPS Server

Start an HTTPS server with TLS encryption:

```c
#include "lwip/apps/httpd.h"
#include "lwip/apps/altcp_tls.h"

void httpd_inits(struct altcp_tls_config *conf);
```

**Parameters:**
- `conf` — mbedtls TLS configuration (created via `altcp_tls_create_config_server()`)

---

## CGI — Common Gateway Interface (Dynamic URLs)

CGI is used to handle **dynamic URL routing**, such as `/api/led/on`, `/api/sensor/read`.

### tCGIHandler — CGI Handler Function Type

```c
typedef const char *(*tCGIHandler)(int iIndex,
                                   int iNumParams,
                                   char *pcParam[],
                                   char *pcValue[]);
```

**Parameters:**
- `iIndex` — CGI handler index (corresponding to registration order)
- `iNumParams` — Number of URI parameters
- `pcParam[]` — Parameter name array (e.g., `"state"`)
- `pcValue[]` — Parameter value array (e.g., `"on"`)

**Return value:** Page path to return, such as `"/thanks.html"` or `"/response/error.ssi"`

**Example:**

```c
const char *handle_led_control(int iIndex, int iNumParams,
                                 char *pcParam[], char *pcValue[])
{
    for (int i = 0; i < iNumParams; i++) {
        if (strcmp(pcParam[i], "state") == 0) {
            if (strcmp(pcValue[i], "on") == 0) {
                bflb_gpio_set(gpio, GPIO_PIN_0);  // LED on
            } else {
                bflb_gpio_reset(gpio, GPIO_PIN_0);  // LED off
            }
        }
    }
    return "/led_response.html";
}
```

### tCGI — CGI Route Structure

```c
typedef struct {
    const char *pcCGIName;     // URL path, e.g., "/api/led"
    tCGIHandler pfnCGIHandler; // Handler function
} tCGI;
```

### http_set_cgi_handlers() — Register CGI Routes

```c
void http_set_cgi_handlers(const tCGI *pCGIs, int iNumHandlers);
```

**Example:**

```c
const tCGI httpRouter[] = {
    { "/api/led",      handle_led_control },
    { "/api/sensor",   handle_sensor_read },
    { "/api/relay",    handle_relay },
};

void app_main(void)
{
    // ...
    httpd_init();
    http_set_cgi_handlers(httpRouter, sizeof(httpRouter) / sizeof(httpRouter[0]));
}
```

---

## SSI — Server Side Include (Embedded Tags)

SSI is used to **embed dynamic variables in HTML files**, with tags in the form `<!--#varname-->`.

### tSSIHandler — SSI Tag Callback Type

```c
typedef u16_t (*tSSIHandler)(
#if LWIP_HTTPD_SSI_RAW
    const char *ssi_tag_name,  // Tag name (not array index)
#else
    int iIndex,               // Tag index in array
#endif
    char *pcInsert,           // Output buffer (fill with replacement text)
    int iInsertLen           // Output buffer length
    /* ... optional parameters ... */
);
```

**Return values:**
- Number of characters written to `pcInsert` (excluding `\0`)
- `HTTPD_SSI_TAG_UNKNOWN (0xFFFF)` — Tag not recognized

**Example:**

```c
static const char *ssi_tags[] = { "UPTIME", "TEMP", "LED_STATE" };

u16_t ssi_handler(int iIndex, char *pcInsert, int iInsertLen)
{
    switch (iIndex) {
        case 0: // UPTIME
            return snprintf(pcInsert, iInsertLen, "%lu seconds",
                            xTaskGetTickCount() / configTICK_RATE_HZ);
        case 1: // TEMP
            return snprintf(pcInsert, iInsertLen, "%.1f", read_temperature());
        case 2: // LED_STATE
            return snprintf(pcInsert, iInsertLen, "%s",
                            led_is_on() ? "ON" : "OFF");
        default:
            return HTTPD_SSI_TAG_UNKNOWN;
    }
}

void app_main(void)
{
    httpd_init();
    http_set_ssi_handler(ssi_handler, ssi_tags,
                         sizeof(ssi_tags) / sizeof(ssi_tags[0]));
}
```

**Usage in HTML:**

```html
<!-- index.shtml -->
<html>
<body>
  <p>Uptime: <!--#UPTIME--></p>
  <p>Temperature: <!--#TEMP--> °C</p>
  <p>LED: <!--#LED_STATE--></p>
  <form action="/api/led" method="get">
    <button name="state" value="on">LED ON</button>
    <button name="state" value="off">LED OFF</button>
  </form>
</body>
</html>
```

### http_set_ssi_handler() — Register SSI Handler

```c
void http_set_ssi_handler(tSSIHandler pfnSSIHandler,
                          const char **ppcTags,
                          int iNumTags);
```

---

## POST Request Handling

### httpd_post_begin() — POST Request Begin

```c
err_t httpd_post_begin(void *connection,
                       const char *uri,
                       const char *http_request,
                       u16_t http_request_len,
                       int content_len,
                       char *response_uri,
                       u16_t response_uri_len,
                       u8_t *post_auto_wnd);
```

**Return value:** `ERR_OK` to accept the request, otherwise reject.

### httpd_post_receive_data() — Receive POST Data

```c
err_t httpd_post_receive_data(void *connection, struct pbuf *p);
```

**Note:** After receiving data, you **must release the pbuf yourself**:

```c
err_t httpd_post_receive_data(void *connection, struct pbuf *p)
{
    // Process data in p->payload
    pbuf_free(p);  // Must release
    return ERR_OK;
}
```

### httpd_post_finished() — POST Complete

```c
void httpd_post_finished(void *connection,
                         char *response_uri,
                         u16_t response_uri_len);
```

**Description:** Fill `response_uri` with the response page path, such as `"/upload_ok.html"`.

---

## Filesystem Abstraction Layer (fs.h)

HTTPD serves static files through the filesystem abstraction layer. CGI/SSI processing also needs to return files to the client upon completion.

### fs_open() — Open File

```c
#include "lwip/apps/fs.h"

struct fs_file {
    const void *data;   // File data pointer
    size_t len;         // File length
    int index;          // Current read position
    void *state;       // State pointer (for custom data)
    // ...
};

err_t fs_open(struct fs_file *file, const char *name);
```

**Returns:** `ERR_OK` on success, otherwise failure.

### fs_read() — Read File

```c
int fs_read(struct fs_file *file, char *buffer, int count);
```

**Returns:** Actual number of bytes read, 0 indicates end of file, -1 indicates error.

### fs_close() — Close File

```c
void fs_close(struct fs_file *file);
```

### Sending Files Using netconn

Common SDK pattern (sending files after CGI processing):

```c
#include "lwip/apps/fs.h"
#include "lwip/netconn.h"

struct netconn *http_active_conn;  // Global or passed via connection_state

void send_file_to_client(const char *path)
{
    struct fs_file file;
    if (fs_open(&file, path) == ERR_OK) {
        netconn_write(http_active_conn,
                      file.data,
                      file.len,
                      NETCONN_NOCOPY);
        fs_close(&file);
    }
}
```

---

## Configuration Options (lwipopts_user.h)

Enable HTTPD-related features in `lwipopts_user.h`:

```c
// ==================== HTTPD Configuration ====================

// Enable CGI (dynamic URLs)
#define LWIP_HTTPD_CGI           1

// Enable SSI (server-side tags)
#define LWIP_HTTPD_SSI           1

// Enable POST request support
#define LWIP_HTTPD_SUPPORT_POST   1

// POST manual window management (throttle receive speed)
#define LWIP_HTTPD_POST_MANUAL_WND  1

// Maximum number of CGI parameters
#define LWIP_HTTPD_MAX_CGI_PARAMETERS  16

// SSI maximum tag count
#define LWIP_HTTPD_MAX_SSI_TAGS        8

// HTTP server listening port
#define LWIP_HTTPD_SERVER_PORT          80

// Enable HTTPS
#define HTTPD_ENABLE_HTTPS              1

// Filesystem root directory (for RAM filesystem)
#define LWIP_HTTPD_FSDATA_TYPE          1

// Maximum URI length
#define LWIP_HTTPD_MAX_URI_LENGTH       256

// TCP send buffer (affects large file transfers)
#define HTTP_MAX_OUTPUT_LEN             4096
```

**Note:** After enabling CGI/SSI, **corresponding handler functions must be registered**, otherwise accessing those URLs will return 404.

---

## Complete Example: Serving HTML Pages from Flash

### 1. Prepare HTML Files (place in fsdata.c)

Typically, a Python tool is used to package HTML/CSS/JS into `fsdata.c` (refer to `tools/makefsdata`). Simplified approach: use RAM filesystem.

### 2. Code Implementation

```c
#include "FreeRTOS.h"
#include "task.h"
#include "lwip/tcpip.h"
#include "lwip/netif.h"
#include "lwip/apps/httpd.h"
#include "lwip/apps/fs.h"
#include "wifi_mgmr.h"

static struct netif *sta_netif;

// ==================== CGI Handlers ====================
const char *cgi_led_handler(int iIndex, int iNumParams,
                            char *pcParam[], char *pcValue[])
{
    for (int i = 0; i < iNumParams; i++) {
        if (strcmp(pcParam[i], "state") == 0) {
            if (strcmp(pcValue[i], "on") == 0) {
                bflb_gpio_set(gpio, GPIO_PIN_0);
            } else {
                bflb_gpio_reset(gpio, GPIO_PIN_0);
            }
        }
    }
    return "/led_ok.html";
}

const tCGI cgi_handlers[] = {
    { "/api/led", cgi_led_handler },
};

// ==================== SSI Handlers ====================
static const char *ssi_tags[] = { "IP", "STATUS" };

u16_t ssi_handler(int iIndex, char *pcInsert, int iInsertLen)
{
    switch (iIndex) {
        case 0: // IP
            return snprintf(pcInsert, iInsertLen, "%s",
                            ipaddr_ntoa(&sta_netif->ip_addr));
        case 1: // STATUS
            return snprintf(pcInsert, iInsertLen, "Connected");
        default:
            return HTTPD_SSI_TAG_UNKNOWN;
    }
}

// ==================== Task ====================
static void web_server_task(void *param)
{
    vTaskDelay(pdMS_TO_TICKS(500));  // Wait for network readiness

    httpd_init();
    http_set_cgi_handlers(cgi_handlers,
                          sizeof(cgi_handlers) / sizeof(cgi_handlers[0]));
    http_set_ssi_handler(ssi_handler, ssi_tags,
                         sizeof(ssi_tags) / sizeof(ssi_tags[0]));

    printf("HTTP server running at http://%s/\r\n",
           ipaddr_ntoa(&sta_netif->ip_addr));

    vTaskDelete(NULL);
}

void app_main(void)
{
    // ... Wi-Fi connection code ...
    // wifi_mgmr_sta_connect(...);

    // Create HTTP server task
    xTaskCreate(web_server_task, "httpd", 1024, NULL, 5, NULL);
}
```

### 3. HTML Page Example (index.shtml)

```html
<!DOCTYPE html>
<html>
<head>
  <title>BL618 Web Server</title>
  <style>
    body { font-family: Arial; text-align: center; padding: 40px; }
    .status { font-size: 24px; margin: 20px 0; }
    button { padding: 10px 30px; font-size: 18px; margin: 5px; }
    .on { background: #4CAF50; color: white; }
    .off { background: #f44336; color: white; }
  </style>
</head>
<body>
  <h1>BL618 Web Server</h1>
  <p>IP: <!--#IP--></p>
  <p>Status: <!--#STATUS--></p>
  <hr>
  <h2>LED Control</h2>
  <form action="/api/led" method="get">
    <button class="on" name="state" value="on">LED ON</button>
    <button class="off" name="state" value="off">LED OFF</button>
  </form>
</body>
</html>
```

---

## SDK Example Paths

| Example | Path |
|------|------|
| EMAC HTTP Server | `examples/peripherals/emac/lwip_http_server/` |
| Wi-Fi RESTful API | `examples/wifi/sta/http_restful_api/` |

---

## Notes

1. **Must call `httpd_init()` before registering CGI/SSI:** Otherwise routes won't take effect
2. **RAM filesystem limitation:** By default, files in `fsdata.c` are compiled into firmware; files that are too large will fill up Flash
3. **Wi-Fi mode:** Ensure the `netif` is up and has obtained an IP before starting the HTTP server
4. **lwIP thread safety:** HTTPD runs in the TCPIP thread; CGI/SSI registration must be completed before `httpd_init()`
5. **POST requires manual `pbuf_free`:** After receiving data, you must release it or memory will leak
