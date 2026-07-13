# Flash Partition Management (BL_MTD) API Reference

> Source file: `components/sys/blmtd/include/bl_mtd.h`  
> Unified management of read/write/erase operations for Flash partitions (PSM, FW, media, etc.).

---

## Overview

BL_MTD (Memory Technology Device) is a Flash partition abstraction layer that encapsulates unified access interfaces for Flash partitions, providing open/read/write/erase semantics.

Predefined partition names:
- `BL_MTD_PARTITION_NAME_PSM` — PSM persistent storage area
- `BL_MTD_PARTITION_NAME_FW_DEFAULT` — Firmware area
- `BL_MTD_PARTITION_NAME_ROMFS` — ROMFS multimedia area

---

## Header File

```c
#include "bl_mtd.h"
```

---

## Type Definitions

### `bl_mtd_handle_t`

Partition operation handle:

```c
typedef void *bl_mtd_handle_t;
```

### `bl_mtd_info_t`

Partition information structure:

```c
typedef struct {
    char name[16];         // Partition name
    unsigned int offset;   // Flash offset address
    unsigned int size;     // Partition size in bytes
    void *xip_addr;        // XIP mapped address (read-only)
} bl_mtd_info_t;
```

---

## Macros

### Open Flags

```c
#define BL_MTD_OPEN_FLAG_NONE     (0)       // Normal open
#define BL_MTD_OPEN_FLAG_BACKUP   (1 << 0)  // Open backup partition
#define BL_MTD_OPEN_FLAG_BUSADDR  (1 << 1)  // Use bus address (bypass XIP)
```

---

## Function API

### `bl_mtd_open`

Open a partition.

```c
int bl_mtd_open(const char *name, bl_mtd_handle_t *handle, unsigned int flags);
```

| Parameter | Description |
|-----------|-------------|
| `name` | Partition name |
| `handle` | Output handle |
| `flags` | Open flags |

**Return value**: 0=success

---

### `bl_mtd_close`

Close a partition.

```c
int bl_mtd_close(bl_mtd_handle_t handle);
```

---

### `bl_mtd_info`

Get partition information.

```c
int bl_mtd_info(bl_mtd_handle_t handle, bl_mtd_info_t *info);
```

---

### `bl_mtd_erase`

Erase a specified address range.

```c
int bl_mtd_erase(bl_mtd_handle_t handle, unsigned int addr,
                 unsigned int size);
```

| Parameter | Description |
|-----------|-------------|
| `addr` | Offset within partition (starting from 0) |
| `size` | Erase size |

---

### `bl_mtd_erase_all`

Erase the entire partition.

```c
int bl_mtd_erase_all(bl_mtd_handle_t handle);
```

---

### `bl_mtd_write`

Write data (automatic erase).

```c
int bl_mtd_write(bl_mtd_handle_t handle, unsigned int addr,
                 unsigned int size, const uint8_t *data);
```

---

### `bl_mtd_read`

Read data.

```c
int bl_mtd_read(bl_mtd_handle_t handle, unsigned int addr,
                unsigned int size, uint8_t *data);
```

---

### `bl_mtd_size`

Get partition size.

```c
int bl_mtd_size(bl_mtd_handle_t handle, unsigned int *size);
```

---

## Usage Examples

### Reading PSM Partition

```c
#include "bl_mtd.h"

int read_psm_calibration(void)
{
    bl_mtd_handle_t handle;
    int ret = bl_mtd_open(BL_MTD_PARTITION_NAME_PSM, &handle,
                           BL_MTD_OPEN_FLAG_NONE);
    if (ret != 0) {
        printf("Failed to open PSM\r\n");
        return -1;
    }

    bl_mtd_info_t info;
    bl_mtd_info(handle, &info);
    printf("PSM: offset=0x%x size=%u\r\n", info.offset, info.size);

    uint8_t data[32];
    ret = bl_mtd_read(handle, 0, sizeof(data), data);
    bl_mtd_close(handle);

    return ret;
}
```

### Read/Write Firmware Configuration Area

```c
int save_config(uint8_t *config, size_t len)
{
    bl_mtd_handle_t handle;
    int ret = bl_mtd_open("FW", &handle, BL_MTD_OPEN_FLAG_NONE);
    if (ret != 0) return -1;

    // Erase before writing
    ret = bl_mtd_erase(handle, 0, len);
    if (ret == 0) {
        ret = bl_mtd_write(handle, 0, len, config);
    }

    bl_mtd_close(handle);
    return ret;
}
```
