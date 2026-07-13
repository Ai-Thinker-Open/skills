# System Time API Reference

> Source file: `components/sys/bltime/include/bl_sys_time.h`  
> System time management based on RTC hardware, supports NTP synchronization and time retrieval.

---

## Overview

`bl_sys_time` provides system-level time management based on RTC, supporting:
- Get current Epoch time (seconds)
- Update system time (from NTP or other time sources)
- Automatic NTP synchronization

---

## Header File

```c
#include "bl_sys_time.h"
```

---

## Function API

### `bl_sys_time_get`

Get current system time (Epoch seconds).

```c
int bl_sys_time_get(uint64_t *epoch);
```

| Parameter | Description |
|-----------|-------------|
| `epoch` | Output Epoch time in seconds |

**Return value**: 0=success, -1=failure

---

### `bl_sys_time_update`

Manually update system time.

```c
void bl_sys_time_update(uint64_t epoch);
```

| Parameter | Description |
|-----------|-------------|
| `epoch` | New Epoch time in seconds |

---

### `bl_sys_time_cli_init`

Initialize time CLI commands (can set/query time via CLI).

```c
int bl_sys_time_cli_init(void);
```

---

### `bl_sys_time_sync_init`

Initialize automatic NTP synchronization.

```c
void bl_sys_time_sync_init(void);
```

---

### `bl_sys_time_sync`

Manually trigger an NTP synchronization.

```c
uint32_t bl_sys_time_sync(void);
```

**Return value**: System time after synchronization (Epoch seconds)

---

### `bl_sys_time_sync_state`

Get time synchronization status.

```c
int bl_sys_time_sync_state(uint32_t *xTicksToJump);
```

| Parameter | Description |
|-----------|-------------|
| `xTicksToJump` | Output the last tick jump count |

**Return value**: Synchronization status

---

## Usage Examples

### Basic Time Retrieval

```c
#include "bl_sys_time.h"

void print_current_time(void)
{
    uint64_t epoch;
    if (bl_sys_time_get(&epoch) == 0) {
        printf("Epoch: %llu\r\n", epoch);
        // Convert to human-readable format
        time_t t = (time_t)epoch;
        struct tm *tm_info = localtime(&t);
        printf("Time: %s", asctime(tm_info));
    }
}
```

### Initialize NTP Synchronization

```c
void time_init(void)
{
    // Initialize automatic NTP synchronization
    bl_sys_time_sync_init();

    // Wait for first synchronization
    vTaskDelay(pdMS_TO_TICKS(3000));

    uint64_t now;
    bl_sys_time_get(&now);
    printf("Time synchronized: %llu\r\n", now);
}
```
