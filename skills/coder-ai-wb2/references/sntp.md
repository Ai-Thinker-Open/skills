# SNTP Time Synchronization API Reference

> Source file: `components/network/sntp/include/sntp.h`  
> Based on standard lwIP SNTP client, supports NTP server polling and callback notifications.

---

## Overview

The SNTP client is used to synchronize the system time from NTP servers, supporting:
- Unicast/broadcast mode
- Multiple server configuration
- Server reachability monitoring
- Synchronization callback notifications

---

## Header File

```c
#include "sntp.h"
```

---

## Type Definitions

### `ntp_sync_cb`

Time synchronization callback function type:

```c
typedef void (*ntp_sync_cb)(void);
```

---

## Function API

### `sntp_setoperatingmode`

Set SNTP operating mode (must be called before `sntp_init`).

```c
void sntp_setoperatingmode(u8_t operating_mode);
```

| Mode | Value | Description |
|------|-------|-------------|
| `SNTP_OPMODE_POLL` | 0 | Polling mode (default) |
| `SNTP_OPMODE_LISTENONLY` | 1 | Listen to broadcast only |

---

### `sntp_getoperatingmode`

Get current operating mode:

```c
u8_t sntp_getoperatingmode(void);
```

---

### `sntp_init`

Initialize and start the SNTP client.

```c
void sntp_init(void);
```

---

### `sntp_stop`

Stop the SNTP client.

```c
void sntp_stop(void);
```

---

### `sntp_enabled`

Query whether SNTP is enabled.

```c
u8_t sntp_enabled(void);
```

**Return value**: 1=enabled, 0=disabled

---

### `sntp_setserver`

Set NTP server address (by index).

```c
void sntp_setserver(u8_t idx, const ip_addr_t *addr);
```

| Parameter | Description |
|-----------|-------------|
| `idx` | Server index (0~3) |
| `addr` | IP address |

---

### `sntp_getserver`

Get NTP server address.

```c
const ip_addr_t *sntp_getserver(u8_t idx);
```

---

### `sntp_setservername`

Set NTP server via domain name (requires `SNTP_SERVER_DNS=1`).

```c
void sntp_setservername(u8_t idx, const char *server);
```

---

### `sntp_getservername`

Get NTP server domain name.

```c
const char *sntp_getservername(u8_t idx);
```

---

### `sntp_getreachability`

Get server reachability status (requires `SNTP_MONITOR_SERVER_REACHABILITY=1`).

```c
u8_t sntp_getreachability(u8_t idx);
```

**Return value**: 0=unreachable, non-zero=reachable

---

### `sntp_get_time`

Get current time (high resolution).

```c
int sntp_get_time(uint32_t *seconds, uint32_t *frags);
```

| Parameter | Description |
|-----------|-------------|
| `seconds` | Epoch seconds (output) |
| `frags` | Fractional seconds (output) |

**Return value**: 0=success

---

### `sntp_settimesynccb`

Set time synchronization callback (automatically called on successful sync).

```c
void sntp_settimesynccb(ntp_sync_cb cb);
```

---

### `sntp_setupdatedelay`

Set synchronization interval.

```c
void sntp_setupdatedelay(uint32_t delay);
```

---

### `sntp_cli_init`

Initialize SNTP CLI commands (operable via CLI).

```c
int sntp_cli_init(void);
```

---

## Usage Example

### Basic Initialization

```c
#include "sntp.h"
#include "lwip/apps/sntp_opts.h"

void sntp_example(void)
{
    // Set operating mode
    sntp_setoperatingmode(SNTP_OPMODE_POLL);

    // Set NTP servers (domain names are supported)
    sntp_setservername(0, "pool.ntp.org");
    sntp_setservername(1, "time.google.com");

    // Initialize
    sntp_init();
}
```

### Initialization with Callback

```c
static void on_time_synced(void)
{
    uint32_t sec, frags;
    sntp_get_time(&sec, &frags);
    printf("Time synced: %u.%u\r\n", sec, frags);
}

void sntp_with_callback(void)
{
    sntp_setoperatingmode(SNTP_OPMODE_POLL);
    sntp_setservername(0, "pool.ntp.org");
    sntp_settimesynccb(on_time_synced);
    sntp_init();
}
```
