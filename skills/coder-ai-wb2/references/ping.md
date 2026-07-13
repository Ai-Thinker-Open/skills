# Ping (ICMP) API Reference

> Source file: `components/network/netutils/include/ping.h`  
> lwIP built-in ICMP ping utility for network diagnostics.

---

## Overview

The Ping utility is based on lwIP's ICMP implementation, used to check network connectivity and round-trip delay (RTT) between the device and the target host.

---

## Header Files

```c
#include "ping.h"
```

---

## Type Definitions

### `ping_option`

Ping options configuration:

```c
typedef struct {
    uint32_t count;        // Ping count (0=infinite)
    uint32_t interval;      // Interval (seconds)
    uint32_t timeout;       // Timeout (seconds)
    uint32_t data_size;    // Data payload size (bytes)
    ip_addr_t target;       // Target IP address
} ping_option_t;
```

---

### `ping_result`

Ping result:

```c
typedef struct {
    uint32_t total_count;       // Total sent count
    uint32_t total_success;     // Successful responses
    uint32_t total_fail;        // Failed count
    uint32_t avg_time;          // Average RTT (ms)
    uint32_t min_time;          // Minimum RTT (ms)
    uint32_t max_time;          // Maximum RTT (ms)
} ping_result_t;
```

---

## Function Interface

### `ping_init`

Initialize the Ping module.

```c
int ping_init(void);
```

---

### `ping_send`

Send a single Ping request.

```c
int ping_send(const char *host);
```

| Parameter | Description |
|-----------|-------------|
| `host` | Target host (domain name or IP) |

**Return value**: 0=send successful

---

### `ping_raw_send`

Send raw ICMP Ping (need to manually set target IP).

```c
int ping_raw_send(ip_addr_t *addr);
```

---

### `ping_set_option`

Set Ping options.

```c
int ping_set_option(ping_option_t *option);
```

---

### `ping_get_result`

Get Ping statistics result.

```c
int ping_get_result(ping_result_t *result);
```

---

### `ping_register_result_callback`

Register result callback (called each time a response is received).

```c
int ping_register_result_callback(void (*callback)(void *arg));
```

---

## Usage Examples

### Simple Ping

```c
#include "ping.h"

void ping_test(void)
{
    ping_init();

    // Ping 3 times
    for (int i = 0; i < 3; i++) {
        int ret = ping_send("192.168.1.1");
        if (ret == 0) {
            printf("Ping %d: OK\r\n", i + 1);
        } else {
            printf("Ping %d: Failed\r\n", i + 1);
        }
        vTaskDelay(pdMS_TO_TICKS(1000));
    }
}
```

### Ping with Statistics

```c
void ping_with_stats(const char *target)
{
    ping_init();

    ping_option_t opt = {
        .count = 5,
        .interval = 1,
        .timeout = 3,
        .data_size = 32,
    };
    ping_set_option(&opt);

    ping_send(target);

    // Wait for all responses
    vTaskDelay(pdMS_TO_TICKS(6000));

    ping_result_t result;
    ping_get_result(&result);

    printf("Ping stats:\r\n");
    printf("  Sent: %u, Success: %u, Fail: %u\r\n",
           result.total_count, result.total_success, result.total_fail);
    printf("  RTT: avg=%ums min=%ums max=%ums\r\n",
           result.avg_time, result.min_time, result.max_time);
}
```
