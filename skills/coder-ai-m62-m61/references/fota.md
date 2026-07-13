# BL616/BL618 FOTA Firmware Over-The-Air Upgrade

FOTA (Firmware Over-The-Air) is an important feature of the BL616/BL618 series chips, allowing devices to receive and update firmware wirelessly during operation without physical interface flashing. The Bouffalo SDK provides three OTA mechanisms:

- **Basic OTA** (`ota.h`) — Core OTA read/write and verification logic
- **TCP FOTA** (`tcp_fota.h`) — Download firmware via TCP protocol
- **HTTPS FOTA** (`https_fota.h`) — Download firmware via HTTPS protocol, supporting TLS mutual authentication

All FOTA modes are based on a **dual-partition (A/B)** design, supporting automatic or manual rollback to the backup partition upon upgrade failure, ensuring the device is always in a bootable state.

## Header Files

```c
#include "ota.h"         /* Core OTA */
#include "tcp_fota.h"    /* TCP FOTA */
#include "https_fota.h"   /* HTTPS FOTA */
```

---

## Dual-Partition Design

BL616/BL618 uses an A/B dual-partition layout:

| Partition | Role | Description |
|------|------|------|
| Partition A | Runtime partition | The partition where the device's currently running firmware resides |
| Partition B | Backup partition | Receives new firmware and stores old firmware copies |

The upgrade flow is as follows:

```
[Currently running Partition A]  -->  [Connect to OTA server]  -->  [Download firmware to Partition B]
        |                                                |
        |                                                v
        |                                    [Verify SHA256 + OTA Header]
        |                                                |
        v                                                v
[Reboot, system boots from Partition B]  <--  [Update partition table, switch boot flag to B]
        |
 (If Partition B boot fails)
        v
[Rollback to Partition A]
```

The partition table records each partition's address, size, type, and age information, read by the bootloader at startup to determine which partition to boot from. The `ota_handle_t` manages partition table context through the `pt_table_stuff_config` structure.

---

## OTA Header Structure

All OTA firmware images must contain a 512-byte OTA Header:

```c
typedef struct ota_header {
    union {
        struct {
            uint8_t  header[16];         /* Fixed magic number */
            uint8_t  type[4];            /* Compression type: "RAW" or "XZ" */
            uint32_t len;                /* Body length */
            uint8_t  pad0[8];
            uint8_t  ver_hardware[16]; /* Hardware version */
            uint8_t  ver_software[16];  /* Software version */
            uint8_t  sha256[32];        /* Firmware SHA256 checksum */
        } s;
        uint8_t _pad[512];
    } u;
} ota_header_t;
```

---

## Basic OTA Interface

Basic OTA (`ota.h`) provides low-level partition operations and firmware write interfaces, used internally by TCP/HTTPS FOTA.

### `ota_start()`

```c
ota_handle_t ota_start(void);
```

Initialize an OTA session, get current active partition information, and prepare the OTA target partition (write to backup partition). Returns an `ota_handle_t` handle.

### `ota_update()`

```c
int ota_update(ota_handle_t handle, uint8_t *buf, uint32_t buf_len);
```

Write firmware data to the backup partition, internally handling Flash erase/write operations. Returns 0 on success, negative value on error.

### `ota_verify_hash()`

```c
int ota_verify_hash(ota_handle_t handle);
```

Calculate SHA256 for the firmware written to the backup partition, compare with the expected value stored in the OTA Header, and verify integrity.

### `ota_finish()`

```c
int ota_finish(ota_handle_t handle, uint8_t check_hash, uint8_t reboot);
```

Complete the OTA process: update the partition table to mark the backup partition as the new active partition. When `reboot` is non-zero, automatically restart.

### `ota_abort()`

```c
int ota_abort(ota_handle_t handle);
```

Abort the current OTA process, discard the written firmware data, and restore to the pre-upgrade state.

### `ota_rollback()`

```c
int ota_rollback(void);
```

Manually rollback to the old firmware in the backup partition. Writes a specific flag to the bootloader, and on the next reboot, the system will boot from the backup partition. After calling, **you must manually reboot the device** to complete the rollback switch.

---

## TCP FOTA

TCP FOTA downloads firmware from an OTA server via TCP connection, suitable for intranet or scenarios with lower security requirements.

### `tcp_fota_status_e` Status Codes

```c
typedef enum {
    TCP_FOTA_SUCCESS = 0,           /* OTA completed successfully */
    TCP_FOTA_START,                  /* FOTA process started */
    TCP_FOTA_SERVER_CONNECT_FAIL,   /* Server connection failed */
    TCP_FOTA_PROCESS_TRANSFER,       /* Transferring firmware data */
    TCP_FOTA_TRANSFER_FINISH,        /* Firmware transfer complete */
    TCP_FOTA_IMAGE_VERIFY,           /* Verifying firmware image */
    TCP_FOTA_IMAGE_VERIFY_FAIL,      /* Firmware image verification failed */
    TCP_FOTA_ABORT,                  /* FOTA process aborted */
} tcp_fota_status_t;
```

### Configuration Structure

```c
struct tcp_fota_config {
    pfn_tcp_fota_t callback;  /* Status callback function */
    void *user_arg;           /* User context */
};
```

### `tcp_fota_init()`

```c
tcp_fota_handle_t tcp_fota_init(const char *ip, const char *port,
                                 const struct tcp_fota_config *config);
```

Create and initialize a TCP FOTA session. `ip` must not be NULL. Pass NULL for `port` to use default port 3365.

### `tcp_fota_start()`

```c
int tcp_fota_start(tcp_fota_handle_t fota);
```

Start the firmware download process in a FreeRTOS task (non-blocking). Internally creates a dedicated task to execute TCP connection, firmware reception, and OTA writing.

### `tcp_fota_finish()` / `tcp_fota_abort()`

```c
int tcp_fota_finish(tcp_fota_handle_t fota, bool reboot);
int tcp_fota_abort(tcp_fota_handle_t fota);
```

`finish` completes OTA and updates the partition table. When `reboot` is true, auto-reboot. `abort` terminates the ongoing FOTA process.

### One-stop Interface `tcp_fota()`

```c
int tcp_fota(const char *ip, const char *port,
             const struct tcp_fota_config *config);
```

Encapsulates the complete flow of `init` → `start` (blocking wait) → `finish` (auto-reboot). Automatically retries up to 10 times on connection failure, with 1-second intervals.

### `tcp_ota_rollback()`

```c
int tcp_ota_rollback(void);
```

Rollback to the backup partition. Requires manual device reboot after calling.

### Constants

| Constant | Value | Description |
|------|----|------|
| `TCP_FOTA_DEFAULT_PORT` | "3365" | Default port |
| `TCP_FOTA_MAX_RETRY` | 10 | Maximum retry count |
| `TCP_FOTA_RETRY_DELAY_MS` | 1000 | Retry interval (ms) |

---

## HTTPS FOTA

HTTPS FOTA downloads firmware via the HTTPS protocol, supporting server-side certificate verification and TLS mutual authentication (mTLS), suitable for production environments with high security requirements.

### `https_fota_status_e` Status Codes

```c
typedef enum {
    HTTPS_FOTA_SUCCESS = 0,          /* OTA completed successfully */
    HTTPS_FOTA_START,                /* FOTA process started */
    HTTPS_FOTA_SERVER_CONNECTE_FAIL, /* Server connection failed */
    HTTPS_FOTA_PROCESS_TRANSFER,      /* Transferring firmware data */
    HTTPS_FOTA_TRANSFER_FINISH,      /* Firmware transfer complete */
    HTTPS_FOTA_IMAGE_VERIFY,          /* Verifying firmware image */
    HTTPS_FOTA_IMAGE_VERIFY_FAIL,    /* Firmware image verification failed */
    HTTPS_FOTA_ABORT,                /* FOTA process aborted */
} https_fota_status_t;
```

### Configuration Structure

```c
struct https_fota_config {
    pfn_https_fota_t callback;       /* Status callback function */
    void *user_arg;                  /* User context */
    const char *ca_pem;              /* Server CA certificate (PEM format) */
    size_t      ca_len;              /* CA certificate length */
    const char *client_cert_pem;    /* Client certificate (for mTLS) */
    size_t      client_cert_len;    /* Client certificate length */
    const char *client_key_pem;     /* Client private key (for mTLS) */
    size_t      client_key_len;     /* Client private key length */
};
```

- Server certificate verification only: set `ca_pem` + `ca_len`.
- mTLS mutual authentication: additionally set `client_cert_pem` / `client_key_pem` fields.

### `https_fota_init()`

```c
https_fota_handle_t https_fota_init(const char *url,
                                      const struct https_fota_config *config);
```

Create and initialize an HTTPS FOTA session. `url` is the complete HTTPS URL for firmware download (must not be NULL). `config` can be NULL.

### `https_fota_start()`

```c
int https_fota_start(https_fota_handle_t fota);
```

Start the HTTPS firmware download process in a FreeRTOS task (non-blocking).

### `https_fota_callback_register()`

```c
int https_fota_callback_register(https_fota_handle_t fota,
                                  pfn_https_fota_t pfn, void *arg);
```

Register a FOTA status callback function. Can be called after `init` and before `start`.

### `https_fota_finish()` / `https_fota_abort()`

```c
int https_fota_finish(https_fota_handle_t fota, bool reboot);
int https_fota_abort(https_fota_handle_t fota);
```

`finish` completes OTA and updates the partition table. When `reboot` is true, auto-reboot. `abort` aborts the FOTA process.

### One-stop Interface `https_fota()`

```c
int https_fota(const char *url, const struct https_fota_config *config);
```

Encapsulates the complete flow of `init` → `start` → `finish`, automatically verifies and updates the partition table after transfer completes.

### `https_ota_rollback()`

```c
int https_ota_rollback(void);
```

Rollback to the backup partition. After calling, you must manually reboot the device to complete the rollback switch.

### Constants

| Constant | Value | Description |
|------|----|------|
| `HTTPS_FOTA_BUFFER_SIZE` | 4096 | Default buffer size |
| `HTTPS_FOTA_REQUEST_TIMEOUT_MS` | 8000 | Default HTTP request timeout (ms) |

---

## Code Example: Complete TCP OTA Upgrade

```c
#include "tcp_fota.h"
#include "FreeRTOS.h"
#include "task.h"
#include <stdio.h>

static void fota_callback(void *arg, tcp_fota_status_t event)
{
    (void)arg;
    switch (event) {
    case TCP_FOTA_START:
        printf("[OTA] Upgrade started\r\n"); break;
    case TCP_FOTA_SERVER_CONNECT_FAIL:
        printf("[OTA] Server connection failed\r\n"); break;
    case TCP_FOTA_PROCESS_TRANSFER:
        printf("[OTA] Receiving firmware...\r\n"); break;
    case TCP_FOTA_TRANSFER_FINISH:
        printf("[OTA] Firmware received, verifying...\r\n"); break;
    case TCP_FOTA_IMAGE_VERIFY:
        printf("[OTA] Verifying image\r\n"); break;
    case TCP_FOTA_IMAGE_VERIFY_FAIL:
        printf("[OTA] Image verification failed\r\n"); break;
    case TCP_FOTA_SUCCESS:
        printf("[OTA] Upgrade successful, rebooting soon\r\n"); break;
    case TCP_FOTA_ABORT:
        printf("[OTA] Upgrade aborted\r\n"); break;
    }
}

void start_ota_task(void)
{
    struct tcp_fota_config config = {
        .callback = fota_callback,
        .user_arg = NULL,
    };

    /* One-stop interface: connect to server -> download -> verify -> reboot */
    int ret = tcp_fota("192.168.1.100", "3365", &config);
    if (ret != 0) {
        printf("[OTA] tcp_fota start failed: %d\r\n", ret);
    }
}
```

HTTPS OTA example:

```c
#include "https_fota.h"

struct https_fota_config config = {
    .callback = https_fota_callback,
    .user_arg  = NULL,
    .ca_pem    = server_ca_cert,
    .ca_len    = strlen(server_ca_cert),
};

int ret = https_fota("https://ota.example.com/firmware/v2.0.bin", &config);
```

---

## Rollback Mechanism

### Automatic Rollback

When the device fails to boot from the new firmware (Partition B) (bootloader detects abnormal boot flag), it automatically rolls back to the old firmware (Partition A).

### Manual Rollback

```c
tcp_ota_rollback();   /* TCP FOTA */
https_ota_rollback();  /* HTTPS FOTA */
ota_rollback();        /* Basic OTA */
```

> **Important:** The rollback function only modifies the boot flag. After calling, **you must manually reboot the device** to switch partitions. It is recommended to enable a watchdog timer (~5 seconds) after calling to prevent inconsistent state from unexpected power loss before reboot.

---

## Partition Requirements and Limitations

- **A/B dual-partition design is mandatory:** OTA writes can only target the inactive partition and cannot directly overwrite the currently running partition.
- **Firmware size limit:** `HOSAL_OTA_FILE_SIZE_MAX` defaults to `0x100000` (1 MB), can be customized.
- **XZ compression:** When `ota_header.type` is "XZ", the system automatically decompresses before writing to Flash.
- **Chunked writes:** OTA writes to Flash in 4096-byte (`OTA_SLICE_SIZE`) chunks to control memory usage.

---

## Notes

1. **Do not power off during OTA:** Power loss during Flash writing may brick the device.
2. **Must reboot after rollback:** The rollback function only modifies the boot flag; partition switching occurs on the next reboot.
3. **Version compatibility:** The system only performs SHA256 integrity verification. `ver_hardware`/`ver_software` version compatibility judgment is the application layer's responsibility.

---

## References

- [Bouffalo SDK Official Documentation](../CLAUDE.md)
- Source code:
  - `components/fota/ota/ota.h` — Core OTA interface
  - `components/fota/tcp/tcp_fota.h` — TCP FOTA interface
  - `components/fota/https/https_fota.h` — HTTPS FOTA interface
  - `components/fota/compat/bflb_ota.h` — Compatibility layer interface
