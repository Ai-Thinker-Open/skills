# BL616/BL618 OTA Firmware Upgrade Documentation

OTA (Over-The-Air) firmware upgrade allows devices to update their firmware wirelessly. The Bouffalo SDK provides three OTA mechanisms:

- **Base OTA** (`ota.h`) - Core OTA functionality
- **TCP OTA** (`tcp_fota.h`) - Firmware download via TCP
- **HTTPS OTA** (`https_fota.h`) - Firmware download via HTTPS

---

## Table of Contents

1. [OTA Header Structure](#ota-header-structure)
2. [Core OTA API](#core-ota-api)
3. [TCP OTA API](#tcp-ota-api)
4. [HTTPS OTA API](#https-ota-api)
5. [Working Examples](#working-examples)

---

## OTA Header Structure

The OTA firmware image must have a specific header format:

```c
typedef struct ota_header {
    union {
        struct {
            uint8_t header[16];
            uint8_t type[4];           // "RAW" or "XZ" compression type
            uint32_t len;              // body length
            uint8_t pad0[8];
            uint8_t ver_hardware[16];  // hardware version
            uint8_t ver_software[16]; // software version
            uint8_t sha256[32];       // SHA256 hash of firmware
        } s;
        uint8_t _pad[512];
    } u;
} ota_header_t;
```

---

## Core OTA API

### `ota_start()`

Initializes and starts an OTA session.

```c
ota_handle_t ota_start(void);
```

**Returns:** OTA handle on success, NULL on failure.

### `ota_update()`

Writes firmware data to the OTA partition.

```c
int ota_update(ota_handle_t handle, uint8_t *buf, uint32_t buf_len);
```

**Parameters:**
- `handle` - OTA handle from `ota_start()`
- `buf` - Buffer containing firmware data
- `buf_len` - Length of data in buffer

**Returns:** 0 on success, negative error code on failure.

### `ota_verify_hash()`

Verifies the firmware SHA256 hash.

```c
int ota_verify_hash(ota_handle_t handle);
```

**Returns:** 0 on success, negative error code on failure.

### `ota_finish()`

Completes the OTA process and optionally reboots.

```c
int ota_finish(ota_handle_t handle, uint8_t check_hash, uint8_t reboot);
```

**Parameters:**
- `handle` - OTA handle
- `check_hash` - 1 to verify hash before finishing
- `reboot` - 1 to reboot after successful update

**Returns:** 0 on success, negative error code on failure.

### `ota_abort()`

Aborts the OTA process.

```c
int ota_abort(ota_handle_t handle);
```

### `ota_rollback()`

Rolls back to the previous firmware partition.

```c
int ota_rollback(void);
```

---

## TCP OTA API

### Status Codes

```c
typedef enum {
    TCP_FOTA_SUCCESS = 0,           // Operation completed successfully
    TCP_FOTA_START,                 // FOTA process started
    TCP_FOTA_SERVER_CONNECT_FAIL,   // Failed to connect to server
    TCP_FOTA_PROCESS_TRANSFER,      // Firmware transfer in progress
    TCP_FOTA_TRANSFER_FINISH,       // Firmware transfer completed
    TCP_FOTA_IMAGE_VERIFY,          // Firmware image verification started
    TCP_FOTA_IMAGE_VERIFY_FAIL,     // Firmware image verification failed
    TCP_FOTA_ABORT,                 // FOTA process aborted
} tcp_fota_status_t;
```

### Callback Type

```c
typedef void (*pfn_tcp_fota_t)(void *arg, tcp_fota_status_t event);
```

### Configuration Structure

```c
struct tcp_fota_config {
    pfn_tcp_fota_t callback;  // Status callback function
    void *user_arg;           // User context passed to callback
};
```

### `tcp_fota_init()`

Initializes a TCP FOTA session.

```c
tcp_fota_handle_t tcp_fota_init(const char *ip, const char *port, const struct tcp_fota_config *config);
```

**Parameters:**
- `ip` - Server IP address or hostname
- `port` - Server port string (NULL for default 3365)
- `config` - Configuration parameters (can be NULL)

**Returns:** FOTA session handle on success, NULL on failure.

### `tcp_fota_start()`

Starts the firmware update process (runs in FreeRTOS task).

```c
int tcp_fota_start(tcp_fota_handle_t fota);
```

**Parameters:**
- `fota` - FOTA session handle

**Returns:** 0 on success, negative error code on failure.

### `tcp_fota_finish()`

Finalizes the FOTA process.

```c
int tcp_fota_finish(tcp_fota_handle_t fota, bool reboot);
```

### `tcp_fota_abort()`

Aborts the FOTA process.

```c
int tcp_fota_abort(tcp_fota_handle_t fota);
```

### `tcp_fota()` - Convenience Function

Single-call convenience function combining init, start, finish, and reboot.

```c
int tcp_fota(const char *ip, const char *port, const struct tcp_fota_config *config);
```

### `tcp_ota_rollback()`

Rolls back to the firmware version in the backup partition.

```c
int tcp_ota_rollback(void);
```

---

## HTTPS OTA API

### Status Codes

```c
typedef enum {
    HTTPS_FOTA_SUCCESS = 0,         // Operation completed successfully
    HTTPS_FOTA_START,               // FOTA process started
    HTTPS_FOTA_SERVER_CONNECTE_FAIL,// Failed to connect to server
    HTTPS_FOTA_PROCESS_TRANSFER,    // Firmware transfer in progress
    HTTPS_FOTA_TRANSFER_FINISH,     // Firmware transfer completed
    HTTPS_FOTA_IMAGE_VERIFY,        // Firmware image verification started
    HTTPS_FOTA_IMAGE_VERIFY_FAIL,   // Firmware image verification failed
    HTTPS_FOTA_ABORT,               // FOTA process aborted
} https_fota_status_t;
```

### Callback Type

```c
typedef void (*pfn_https_fota_t)(void *arg, https_fota_status_t event);
```

### Configuration Structure

```c
struct https_fota_config {
    pfn_https_fota_t callback;      // Status callback function
    void *user_arg;                 // User context passed to callback
    
    const char *ca_pem;             // SSL server CA certificate (PEM format)
    size_t      ca_len;             // Length of CA certificate
    const char *client_cert_pem;    // SSL client certificate (for mutual TLS)
    size_t      client_cert_len;    // Length of client certificate
    const char *client_key_pem;     // SSL client private key
    size_t      client_key_len;     // Length of client private key
};
```

### `https_fota_init()`

Initializes an HTTPS FOTA session.

```c
https_fota_handle_t https_fota_init(const char *url, const struct https_fota_config *config);
```

**Parameters:**
- `url` - HTTPS URL of the firmware image
- `config` - Configuration parameters

**Returns:** FOTA session handle on success, NULL on failure.

### `https_fota_start()`

Starts the firmware update process.

```c
int https_fota_start(https_fota_handle_t fota);
```

**Parameters:**
- `fota` - FOTA session handle

**Returns:** 0 on success, negative error code on failure.

### `https_fota_callback_register()`

Registers a callback for status updates.

```c
int https_fota_callback_register(https_fota_handle_t fota, pfn_https_fota_t pfn, void *arg);
```

### `https_fota_finish()`

Finalizes the FOTA process.

```c
int https_fota_finish(https_fota_handle_t fota, bool reboot);
```

### `https_fota_abort()`

Aborts the FOTA process.

```c
int https_fota_abort(https_fota_handle_t fota);
```

### `https_fota()` - Convenience Function

Single-call convenience function combining init, start, and finish.

```c
int https_fota(const char *url, const struct https_fota_config *config);
```

### `https_ota_rollback()`

Rolls back to the firmware version in the backup partition.

```c
int https_ota_rollback(void);
```

**Note:** Requires manual reboot after calling rollback.

---

## Working Examples

### HTTPS OTA Example

```c
#include "https_fota.h"
#include "FreeRTOS.h"
#include "task.h"

static void ota_status_callback(void *arg, https_fota_status_t event)
{
    uint8_t *ota_progress = (uint8_t *)arg;
    
    switch (event) {
        case HTTPS_FOTA_START:
            printf("OTA started\r\n");
            break;
        case HTTPS_FOTA_SERVER_CONNECTE_FAIL:
            *ota_progress = 0;
            printf("Server connection failed\r\n");
            break;
        case HTTPS_FOTA_PROCESS_TRANSFER:
            printf("Transfer in progress...\r\n");
            break;
        case HTTPS_FOTA_TRANSFER_FINISH:
            printf("Transfer finished\r\n");
            break;
        case HTTPS_FOTA_IMAGE_VERIFY:
            printf("Verifying image...\r\n");
            break;
        case HTTPS_FOTA_IMAGE_VERIFY_FAIL:
            *ota_progress = 0;
            printf("Image verification failed\r\n");
            break;
        case HTTPS_FOTA_SUCCESS:
            printf("OTA SUCCESS - rebooting\r\n");
            *ota_progress = 0;
            vTaskDelay(pdMS_TO_TICKS(100));
            bl_sys_reset_por();  // Reboot
            break;
        case HTTPS_FOTA_ABORT:
            *ota_progress = 0;
            printf("OTA aborted\r\n");
            break;
    }
}

int start_https_ota(const char *url)
{
    int ret;
    static uint8_t ota_progress = 0;
    
    struct https_fota_config config = {0};
    
    if (ota_progress) {
        printf("OTA already in progress\r\n");
        return -1;
    }
    
    ota_progress = 1;
    config.callback = ota_status_callback;
    config.user_arg = &ota_progress;
    
    // Optional: Set CA certificate for server verification
    // config.ca_pem = server_ca_pem;
    // config.ca_len = server_ca_len;
    
    // Optional: Set client certificate for mutual TLS
    // config.client_cert_pem = client_cert_pem;
    // config.client_cert_len = client_cert_len;
    // config.client_key_pem = client_key_pem;
    // config.client_key_len = client_key_len;
    
    ret = https_fota(url, &config);
    if (ret < 0) {
        printf("https_fota failed: %d\r\n", ret);
        ota_progress = 0;
        return ret;
    }
    
    return 0;
}

// Usage:
// start_https_ota("https://192.168.1.100:8443/firmware.bin.ota");
```

### TCP OTA Example

```c
#include "tcp_fota.h"

static void tcp_ota_callback(void *arg, tcp_fota_status_t event)
{
    switch (event) {
        case TCP_FOTA_START:
            printf("TCP OTA started\r\n");
            break;
        case TCP_FOTA_SERVER_CONNECT_FAIL:
            printf("Server connection failed\r\n");
            break;
        case TCP_FOTA_PROCESS_TRANSFER:
            printf("Transfer in progress...\r\n");
            break;
        case TCP_FOTA_TRANSFER_FINISH:
            printf("Transfer finished\r\n");
            break;
        case TCP_FOTA_IMAGE_VERIFY:
            printf("Verifying image...\r\n");
            break;
        case TCP_FOTA_IMAGE_VERIFY_FAIL:
            printf("Image verification failed\r\n");
            break;
        case TCP_FOTA_SUCCESS:
            printf("TCP OTA SUCCESS\r\n");
            break;
        case TCP_FOTA_ABORT:
            printf("TCP OTA aborted\r\n");
            break;
    }
}

int start_tcp_ota(const char *ip, const char *port)
{
    struct tcp_fota_config config = {0};
    
    config.callback = tcp_ota_callback;
    config.user_arg = NULL;
    
    // Using default port (3365) if port is NULL
    return tcp_fota(ip, port, &config);
}

// Usage:
// start_tcp_ota("192.168.1.100", "3365");  // Specific port
// start_tcp_ota("192.168.1.100", NULL);     // Default port
```

### Shell Commands

The SDK provides shell commands for testing:

```
https_ota_start https://192.168.1.100/firmware.bin.ota
tcp_ota_start 192.168.1.100 3365
https_ota_rollback
tcp_ota_rollback
```

### Rollback Process

The rollback mechanism works as follows:

1. Call `ota_rollback()` (or `https_ota_rollback()` / `tcp_ota_rollback()`)
2. The function writes boot flags to bootloader
3. Device will boot from backup partition on next restart
4. **Manual reboot is required** after calling rollback

```c
// Example rollback usage
if (ota_rollback() == 0) {
    printf("Rollback scheduled. Rebooting...\r\n");
    vTaskDelay(pdMS_TO_TICKS(100));
    bl_sys_reset_por();
}
```

---

## Partition Requirements

OTA requires a dual-partition system:

- **Partition A (active)** - Current firmware
- **Partition B (backup)** - Firmware update target / rollback source

The bootloader manages partition switching based on boot flags written during OTA finish/rollback operations.

---

## Build Configuration

Ensure `CONFIG_FAST_OTA` is enabled (default) and partition table is properly configured:

```c
#define CONFIG_FAST_OTA   (1)
#define OTA_SLICE_SIZE    (4096)
```
