# OTA (Over-The-Air) Update API Reference

> Source file: `components/sys/axk_ota/ai_ota.h`  
> `components/sys/axk_ota/ota_parse.h`  
> `components/sys/axk_ota/ota_hal.h`  
> `components/sys/axk_ota/ota_config.h`  
> AXK OTA cloud firmware update library — HTTP/HTTPS OTA with multi-chip header parsing.

---

## Overview

AXK OTA is a firmware upgrade library that downloads firmware from a remote HTTP/HTTPS server and flashes it in-place. It supports:
- **HTTP and HTTPS modes** with callback-based flash writing
- **Multi-chip header parsing** (ESP, RTL, XW, TG, HI chip types)
- **MD5 verification** of downloaded firmware
- **Boot partition switching** and automatic reboot

The library is designed to work with the 安信可 OTA Config tool which generates the firmware header (AI_PACK_HEAD).

---

## Header Files

```c
#include "ai_ota.h"
#include "ota_parse.h"
#include "ota_hal.h"
```

---

## State Machine

### `at_ota_update_state_t`

```c
typedef enum {
    AT_OTA_STATE_FAIL = -1,          // OTA failed
    AT_OTA_STATE_NONE,                // Initial idle state
    AT_OTA_STATE_FOUND_SERVER,         // Server discovered
    AT_OTA_STATE_CONNECTED,           // TCP connected
    AT_OTA_STATE_GET_VERSION,          // Version check in progress
    AT_OTA_STATE_FINISH,              // OTA completed successfully
} at_ota_update_state_t;
```

### `at_ota_update_mode_t`

```c
typedef enum {
    AT_OTA_MODE_HTTP,    // Use HTTP
    AT_OTA_MODE_HTTPS,   // Use HTTPS (TLS)
    AT_OTA_MODE_ANY,     // Auto-select (HTTP preferred)
} at_ota_update_mode_t;
```

### `at_ota_config_t`

```c
typedef struct {
    uint32_t update_state;   // Current state (output)
    uint32_t nonblocking;    // 1=non-blocking mode
} at_ota_config_t;
```

---

## Core Functions

### `ai_http_update_ota`

Start HTTP OTA update. Downloads firmware via plain HTTP.

```c
void ai_http_update_ota(void *param);
```

| Parameter | Type | Description |
|-----------|------|-------------|
| `param` | `void *` | Pointer to `ota_parame` struct (cast) |

---

### `ai_https_update_ota`

Start HTTPS OTA update. Downloads firmware over TLS-encrypted connection.

```c
void ai_https_update_ota(void *param);
```

| Parameter | Type | Description |
|-----------|------|-------------|
| `param` | `void *` | Pointer to `ota_parame` struct (cast) |

---

### `ai_ota_parame_init`

Initialize OTA parameter structure with server connection info.

```c
ota_parame ai_ota_parame_init(char *host, int port, char *resource);
```

| Parameter | Type | Description |
|-----------|------|-------------|
| `host` | `char *` | OTA server hostname or IP |
| `port` | `int` | TCP port (80 for HTTP, 443 for HTTPS) |
| `resource` | `char *` | Firmware download path on server |

**Returns**: `ota_parame` struct populated with callbacks

---

## Header Parsing

### `ai_pack_head`

Firmware header structure (parsed from the binary header):

```c
typedef struct {
    uint8_t version[6];      // Protocol version
    chip_type_t chip_type;   // Chip vendor (ESP/RTL/XW/TG/HI/UNKNOW)
    uint8_t md5[16];         // MD5 of firmware body
    uint8_t url[129];        // Fallback URL (optional)
} ai_pack_head;
```

### `chip_type_t`

```c
typedef enum {
    ESP,     // Espressif
    RTL,     // Realtek
    XW,      // XW (unknown vendor)
    TG,      // TongGuang
    HI,      // HiSilicon
    UNKNOW   // Unknown
} chip_type_t;
```

### `parse_ai_pack_head`

Parse firmware header from OTA download buffer.

```c
int parse_ai_pack_head(uint8_t *resource, int resource_len, ai_pack_head *pack_head_t);
```

| Parameter | Type | Description |
|-----------|------|-------------|
| `resource` | `uint8_t *` | Raw firmware buffer |
| `resource_len` | `int` | Buffer length |
| `pack_head_t` | `ai_pack_head *` | Output parsed header |

**Returns**: 0=success, <0=error

---

### `ai_parse_http_response`

Parse HTTP response to extract body offset and length.

```c
int ai_parse_http_response(uint8_t *response, int response_len,
                           ai_http_response_result *result);
```

| Parameter | Type | Description |
|-----------|------|-------------|
| `response` | `uint8_t *` | Raw HTTP response |
| `response_len` | `int` | Response length |
| `result` | `ai_http_response_result *` | Output parsed result |

**Returns**: 0=success

---

## Callback Types

### `ota_parame`

Callback structure passed to OTA functions:

```c
typedef struct {
    char *host;                           // Server host
    int port;                              // Server port
    char *resoure;                         // Resource path
    f_write write_cb;                      // Flash write callback
    f_erase erase_cb;                      // Flash erase callback
    f_partition set_boot_partition_cb;     // Set boot partition callback
    f_reboot rebooot_cb;                   // Reboot callback
} ota_parame;
```

### Callback Function Types

```c
typedef int (*f_write)(int dst_offset, const void *src, int size);   // Write to flash
typedef int (*f_erase)(int start_addr, int size);                   // Erase flash
typedef void (*f_partition)(void);                                    // Set boot partition
typedef void (*f_reboot)(_Bool ota_result);                          // Reboot (pass result)
```

---

## HAL Layer

### `ai_paltform_set_calloc_free`

Set custom memory allocation functions.

```c
void ai_paltform_set_calloc_free(void);
```

---

### `partition_write_ota_firmware`

Write firmware data to OTA partition.

```c
int partition_write_ota_firmware(int dst_offset, const void *src, int size);
```

---

### `partition_erase`

Erase OTA flash region.

```c
int partition_erase(int start_addr, int size);
```

---

### `get_next_free_partition`

Get next available OTA partition for dual-bank updates.

```c
struct esp_partition_t *get_next_free_partition(void);
```

---

### `set_boot_partition`

Switch boot selector to the new firmware partition.

```c
void set_boot_partition(void);
```

---

### `set_reboot`

Trigger system reboot.

```c
void set_reboot(_Bool ota_result);
```

| Parameter | Description |
|-----------|-------------|
| `ota_result` | `true`=reboot into new firmware, `false`=reboot into old |

---

## Usage Example

```c
#include "ai_ota.h"
#include "ota_parse.h"
#include "ota_hal.h"

// Flash write callback
static int flash_write(int dst_offset, const void *src, int size)
{
    return partition_write_ota_firmware(dst_offset, src, size);
}

// Flash erase callback
static int flash_erase(int start_addr, int size)
{
    return partition_erase(start_addr, size);
}

// Reboot callback
static void ota_reboot(_Bool ota_result)
{
    (void)ota_result;
    set_reboot(ota_result);
}

void start_ota_update(void)
{
    ota_parame param = {
        .host = "192.168.1.100",
        .port = 8080,
        .resoure = "/firmware/v2.bin",
        .write_cb = flash_write,
        .erase_cb = flash_erase,
        .set_boot_partition_cb = set_boot_partition,
        .rebooot_cb = ota_reboot,
    };

    // Use HTTP OTA
    ai_http_update_ota(&param);
}
```
