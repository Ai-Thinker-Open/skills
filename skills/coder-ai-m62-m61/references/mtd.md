# MTD (Memory Technology Device) Technical Documentation

## Overview

MTD (Memory Technology Device) is a unified Flash partition abstraction layer provided by the BL618/BL616 series chips. This module is located in the `bouffalo_sdk/components/utils/bflb_mtd/` directory and provides a standardized access interface for Flash storage, allowing developers to perform data read, write, and erase operations without worrying about the physical characteristics of the underlying Flash hardware.

The core functions of the MTD module include:

- **Partition Abstraction**: Divides Flash into multiple logical partitions, each with an independent name, offset address, and size
- **XIP Address Access**: Supports directly reading code or data through the Flash-mapped XIP (eXecute In Place) address without copying data to RAM
- **Backup Partition Support**: Supports A/B dual-partition mechanism, allowing opening of backup partitions for firmware upgrades or data backup
- **PSM Persistent Storage**: Provides a dedicated PSM (Persistent Storage Memory) partition for saving configuration parameters that need to survive power loss
- **Unified Error Handling**: All API return values follow a unified error code convention, where 0 indicates success and negative values indicate errors

The MTD layer sits between the low-level Flash driver and high-level file systems, suitable for scenarios requiring direct access to storage space, such as firmware upgrades, parameter storage, media data read/write, etc.

## Core Data Structures

### bflb_mtd_handle_t Handle Type

```c
typedef void *bflb_mtd_handle_t;
```

`bflb_mtd_handle_t` is the opaque handle type for the MTD module, used to identify an opened Flash partition. Users obtain this handle after calling `bflb_mtd_open()` successfully, and all subsequent partition operations (read, write, erase) must pass this handle. The handle is managed internally by MTD; users should not attempt to dereference or modify its value.

Usage flow:

1. Call `bflb_mtd_init()` to initialize the MTD subsystem
2. Call `bflb_mtd_open()` to open the target partition and obtain a handle
3. Use the handle for read/write operations
4. Call `bflb_mtd_close()` to close the partition when operations are complete

### bflb_mtd_info_t Partition Information Structure

```c
typedef struct {
    char name[16];       /*!< Partition name */
    unsigned int offset; /*!< Partition offset address in Flash */
    unsigned int size;   /*!< Partition size (bytes) */
    void *xip_addr;      /*!< XIP mapped address of the partition */
} bflb_mtd_info_t;
```

Call `bflb_mtd_info()` to obtain detailed information for a specified partition. The `xip_addr` field provides the starting address of the partition in the Flash mapped region, which can be used directly for XIP read scenarios.

## Open Flags

The `bflb_mtd_open()` function supports the following open flags:

| Flag Name | Value | Description |
|---------|-----|------|
| `BFLB_MTD_OPEN_FLAG_NONE` | 0 | Open partition in default mode |
| `BFLB_MTD_OPEN_FLAG_BACKUP` | (1 << 0) | Open backup partition (dual-partition scenario) |
| `BFLB_MTD_OPEN_FLAG_BUSADDR` | (1 << 1) | Return Flash bus address instead of XIP address |

In OTA upgrade and other dual-partition scenarios, the `BFLB_MTD_OPEN_FLAG_BACKUP` flag can be used to open the currently inactive backup partition for downloading and verifying new firmware.

## Core API

### bflb_mtd_init

```c
void bflb_mtd_init(void);
```

Initialize the MTD subsystem. This function must be called before any other MTD API calls. It reads the Flash partition table, initializes internal data structures, and prepares the partition management environment.

**Example**:

```c
bflb_mtd_init();
```

### bflb_mtd_open

```c
int bflb_mtd_open(const char *name, bflb_mtd_handle_t *handle, unsigned int flags);
```

Open a Flash partition by name and obtain an operation handle.

**Parameter Description**:

- `name`: Partition name string, e.g., `"PSM"`, `"FW"`, `"media"`
- `handle`: Output parameter, stores the handle address upon successful open
- `flags`: Open flags, see the "Open Flags" section above for details

**Returns**: 0 on success, negative error code on failure

**Example**:

```c
bflb_mtd_handle_t handle;
int ret = bflb_mtd_open("PSM", &handle, BFLB_MTD_OPEN_FLAG_NONE);
if (ret != 0) {
    printf("Failed to open PSM partition\r\n");
    return ret;
}
```

### bflb_mtd_close

```c
int bflb_mtd_close(bflb_mtd_handle_t handle);
```

Close an opened Flash partition and release associated resources.

**Parameter Description**:

- `handle`: Partition handle to close

**Returns**: 0 on success, negative error code on failure

### bflb_mtd_info

```c
int bflb_mtd_info(bflb_mtd_handle_t handle, bflb_mtd_info_t *info);
```

Get detailed information for a specified partition, including name, offset address, size, and XIP address.

**Parameter Description**:

- `handle`: Partition handle
- `info`: Output parameter, stores the partition information structure

**Returns**: 0 on success, negative error code on failure

**Example**:

```c
bflb_mtd_info_t info;
bflb_mtd_info(handle, &info);
printf("Partition: %s, Offset: 0x%x, Size: %u bytes, XIP: %p\r\n",
       info.name, info.offset, info.size, info.xip_addr);
```

### bflb_mtd_erase

```c
int bflb_mtd_erase(bflb_mtd_handle_t handle, unsigned int addr, unsigned int size);
```

Erase Flash content within a specified address range in the partition. Flash must be erased before writing; erase operations are performed in sector units, and the actual erase range may be aligned to sector boundaries.

**Parameter Description**:

- `handle`: Partition handle
- `addr`: Offset relative to the partition start address (bytes)
- `size`: Number of bytes to erase

**Returns**: 0 on success, negative error code on failure

**Note**: Erase address and size are automatically aligned to the Flash sector size.

### bflb_mtd_erase_all

```c
int bflb_mtd_erase_all(bflb_mtd_handle_t handle);
```

Erase the entire content of the partition. This operation takes considerable time and should not be called from interrupt context.

**Parameter Description**:

- `handle`: Partition handle

**Returns**: 0 on success, negative error code on failure

### bflb_mtd_write

```c
int bflb_mtd_write(bflb_mtd_handle_t handle, unsigned int addr, unsigned int size, const uint8_t *data);
```

Write data to the partition. Before writing, ensure that the target area has been erased; otherwise, the write may fail or produce incorrect data.

**Parameter Description**:

- `handle`: Partition handle
- `addr`: Write offset relative to the partition start address (bytes)
- `size`: Length of data to write (bytes)
- `data`: Pointer to the data buffer to be written

**Returns**: 0 on success, negative error code on failure

### bflb_mtd_read

```c
int bflb_mtd_read(bflb_mtd_handle_t handle, unsigned int addr, unsigned int size, uint8_t *data);
```

Read data from the partition. This operation does not require prior erasure and can read data at any position at any time.

**Parameter Description**:

- `handle`: Partition handle
- `addr`: Read offset relative to the partition start address (bytes)
- `size`: Length of data to read (bytes)
- `data`: Pointer to the buffer where read data will be stored

**Returns**: 0 on success, negative error code on failure

### bflb_mtd_size

```c
int bflb_mtd_size(bflb_mtd_handle_t handle, unsigned int *size);
```

Get the total size of the partition (bytes).

**Parameter Description**:

- `handle`: Partition handle
- `size`: Output parameter, stores the partition size

**Returns**: 0 on success, negative error code on failure

## Predefined Partition Names

The BL618/BL616 SDK predefines the following commonly used partition names:

| Partition Name Constant | String Value | Usage Description |
|-----------|---------|---------|
| `BFLB_MTD_PARTITION_NAME_PSM` | `"PSM"` | Persistent storage partition, used to save device configuration parameters, calibration data, and other information that needs to survive power loss |
| `BFLB_MTD_PARTITION_NAME_FW_DEFAULT` | `"FW"` | Default firmware partition, stores the main application code |
| `BFLB_MTD_PARTITION_NAME_ROMFS` | `"media"` | Media partition, used to store media resource files such as images and audio |

These partition names correspond one-to-one with entries in the partition table, which is read by the bootloader at startup. The specific partition size and address are determined by the chip model and SDK configuration, and can be viewed and modified in the `partition.toml` or `partition.h` files.

## Differences Between MTD and File Systems

Many developers wonder: since file systems exist, why is MTD needed? The positioning and applicable scenarios of the two are significantly different:

| Feature | MTD | File System |
|-----|-----|---------|
| Layer | Raw Flash read/write interface (block device driver layer) | High-level abstraction (files/directories/paths) |
| Typical Examples | bflb_mtd_* family API | FATFS, LittleFS, ROMFS |
| Data Organization | Linear address space, no structure | Tree directory structure |
| Random Access | Requires manual address calculation | Direct access via filename and offset |
| Applicable Scenarios | Firmware storage, PSM parameters, raw data blocks | Log recording, configuration files, multimedia resources |
| Implementation Complexity | Simple | Complex (needs to manage directory entries, cluster chains, metadata) |
| Resource Overhead | Very low | Requires additional RAM/ROM |

In short:

- **MTD** is a low-level interface that directly operates on Flash physical addresses, suitable for scenarios requiring precise control over storage layout
- **File System** is a high-level abstraction that provides a PC-like file system user experience, suitable for managing large numbers of small files and complex data structures

In actual projects, the typical architecture is: the Bootloader uses MTD to directly read/write Flash partition tables and firmware images; the application uses a file system to manage user data; and critical configuration areas such as PSM are accessed directly through MTD to ensure reliability and low latency.

## Code Example: PSM Partition Read/Write

The following example demonstrates how to open a PSM partition and read/write persistent data:

```c
#include "bflb_mtd.h"
#include <stdio.h>
#include <string.h>

#define PSM_CONFIG_ADDR  0
#define PSM_CONFIG_SIZE  64

typedef struct {
    uint32_t magic;
    uint32_t version;
    char device_name[32];
    uint8_t reserved[24];
} psm_config_t;

static const psm_config_t default_config = {
    .magic = 0x50534D00,  /* "PSM\0" */
    .version = 1,
    .device_name = "BL618-Dev",
};

/**
 * @brief Load configuration from PSM partition
 */
int psm_load_config(psm_config_t *config)
{
    bflb_mtd_handle_t handle;
    int ret;

    ret = bflb_mtd_open(BFLB_MTD_PARTITION_NAME_PSM, &handle, BFLB_MTD_OPEN_FLAG_NONE);
    if (ret != 0) {
        printf("Failed to open PSM partition: %d\r\n", ret);
        return ret;
    }

    ret = bflb_mtd_read(handle, PSM_CONFIG_ADDR, sizeof(psm_config_t), (uint8_t *)config);
    if (ret != 0) {
        printf("Failed to read PSM config: %d\r\n", ret);
        bflb_mtd_close(handle);
        return ret;
    }

    /* Check if magic matches, use defaults if not */
    if (config->magic != default_config.magic) {
        printf("PSM config not found, using defaults\r\n");
        memcpy(config, &default_config, sizeof(psm_config_t));
        ret = -1;  /* Indicates default config was used */
    }

    bflb_mtd_close(handle);
    return ret;
}

/**
 * @brief Save configuration to PSM partition
 */
int psm_save_config(const psm_config_t *config)
{
    bflb_mtd_handle_t handle;
    unsigned int partition_size;
    int ret;

    ret = bflb_mtd_open(BFLB_MTD_PARTITION_NAME_PSM, &handle, BFLB_MTD_OPEN_FLAG_NONE);
    if (ret != 0) {
        printf("Failed to open PSM partition: %d\r\n", ret);
        return ret;
    }

    /* Ensure write position is within partition range */
    bflb_mtd_size(handle, &partition_size);
    if (PSM_CONFIG_ADDR + sizeof(psm_config_t) > partition_size) {
        printf("PSM config out of partition range\r\n");
        bflb_mtd_close(handle);
        return -1;
    }

    /* Erase target area before writing */
    ret = bflb_mtd_erase(handle, PSM_CONFIG_ADDR, sizeof(psm_config_t));
    if (ret != 0) {
        printf("Failed to erase PSM: %d\r\n", ret);
        bflb_mtd_close(handle);
        return ret;
    }

    ret = bflb_mtd_write(handle, PSM_CONFIG_ADDR, sizeof(psm_config_t), (const uint8_t *)config);
    if (ret != 0) {
        printf("Failed to write PSM: %d\r\n", ret);
    }

    bflb_mtd_close(handle);
    return ret;
}

/**
 * @brief Application initialization example
 */
void app_main(void)
{
    psm_config_t config;
    int ret;

    /* Initialize MTD subsystem */
    bflb_mtd_init();

    /* Load configuration */
    ret = psm_load_config(&config);
    if (ret == 0) {
        printf("Loaded config: device_name=%s, version=%u\r\n",
               config.device_name, config.version);
    }

    /* Modify configuration */
    config.version++;
    strcpy(config.device_name, "BL618-Production");

    /* Save configuration */
    ret = psm_save_config(&config);
    if (ret == 0) {
        printf("Config saved successfully\r\n");
    }
}
```

**Code Explanation**:

1. Use `bflb_mtd_init()` to initialize the MTD subsystem
2. Open the PSM partition via `bflb_mtd_open()` with the partition name `BFLB_MTD_PARTITION_NAME_PSM`
3. Reading does not require prior erasure, but writing requires calling `bflb_mtd_erase()` to erase the target area first
4. Always call `bflb_mtd_close()` to release the handle after operations are complete
5. The example uses the `magic` field to identify whether the configuration has been written; on first power-up, defaults are automatically used

## Error Codes

The MTD module uses standard error codes, with the following return value semantics:

| Return Value | Meaning |
|-------|------|
| 0 | Operation successful |
| -1 | General error |
| -2 | Parameter error |
| -3 | Partition does not exist |
| -4 | Read/write failure |
| -5 | Erase failure |
| -6 | Flash busy or timeout |

For specific error code definitions, refer to the `bflb_mtd.h` header file or the SDK error code documentation.

## Thread Safety

The MTD module itself is **not thread-safe**. When using MTD in a multi-tasking (RTOS) environment, observe the following principles:

- Avoid multiple tasks operating on the same partition simultaneously
- If partition access must be shared among multiple tasks, use a mutex for protection
- Do not call time-consuming MTD operations (such as `bflb_mtd_erase_all`) from interrupt context

## References

- [bflb_mtd.h Source](../workspase/BL618Claw/bouffalo_sdk/components/utils/bflb_mtd/include/bflb_mtd.h) - MTD module header file
- [bflb_boot2.h Source](../workspase/BL618Claw/bouffalo_sdk/components/utils/bflb_mtd/include/bflb_boot2.h) - Boot2 partition management header file
- [BL618/BL616 SDK Documentation](../workspase/BL618Claw/bouffalo_sdk/CLAUDE.md) - Bouffalo SDK overall architecture
- Partition table configuration - `partition.h` / `partition.toml`
