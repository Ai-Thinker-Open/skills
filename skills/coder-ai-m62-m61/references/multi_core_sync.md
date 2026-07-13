# Multi-Core Sync API Reference (BL618DG)

> **Source:** `bouffalo_sdk/drivers/lhal/include/bflb_multi_core_sync.h`  
> **Implementation:** `bouffalo_sdk/drivers/lhal/src/bflb_multi_core_sync.c`  
> **Dependencies:** `drivers/lhal/include/hardware/ipc_reg.h`, `components/ipc/ipm.h`
>
> **⚠️ Chip Support:** The multi-core sync API is only available on the **BL618DG** multi-core chip and requires the `CONFIG_IPC` configuration to be enabled. The BL616 single-core chip does not have this peripheral.

## Overview

The Multi-Core Sync module provides an inter-core synchronization mechanism for the BL618DG multi-core system (AP + NP cores) during Flash operations. When the AP core needs to perform Flash erase, write, or read operations, it first suspends the NP core via the IPC synchronization mechanism, then resumes the NP core after the operation is complete, ensuring atomicity and data consistency of Flash operations.

**Key Features:**
- NP core synchronization protection for Flash erase/write/read operations
- IPC sync protocol: Suspend → Operation → Resume
- Timeout handling (3-second Suspend wait, 1-second Resume wait)
- Safe NP core suspension during system reset

**Workflow:**

```
AP Core                                NP Core
  │                                       │
  ├─ IPC_SYNC_SUSPEND_CMD ──────────────►│  Suspend NP
  │  ◄────────────── IPC_SYNC_SUSPEND_ACK │
  │                                       │
  ├─ Flash Erase / Write / Read           │  NP paused
  │                                       │
  ├─ IPC_SYNC_RESUME_CMD ───────────────►│  Resume NP
  │  ◄────────────── IPC_SYNC_RESUME_ACK  │
  │                                       │
```

---

## API Functions

### bflb_flash_erase_mcs

Multi-core safe Flash erase operation.

```c
int bflb_flash_erase_mcs(uint32_t erase_addr, uint32_t len);
```

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `erase_addr` | `uint32_t` | Flash erase start address |
| `len` | `uint32_t` | Erase length (bytes) |

**Returns:**

| Return Value | Description |
|--------|------|
| `0` | Erase successful |
| `-1` | IPC sync timeout or failure |

**Note:** Operation flow:
1. Send `IPC_SYNC_SUSPEND_CMD` and wait for NP core `IPC_SYNC_SUSPEND_ACK` (3-second timeout)
2. Call `bflb_flash_erase()` to perform the actual erase
3. Send `IPC_SYNC_RESUME_CMD` and wait for NP core `IPC_SYNC_RESUME_ACK` (3-second timeout)
4. If step 2 fails, it still sends Resume to recover the NP core (1-second timeout)

---

### bflb_flash_write_mcs

Multi-core safe Flash write operation.

```c
int bflb_flash_write_mcs(uint32_t write_addr, const uint8_t *data, uint32_t len);
```

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `write_addr` | `uint32_t` | Flash write start address |
| `data` | `const uint8_t *` | Pointer to data buffer to write |
| `len` | `uint32_t` | Write length (bytes) |

**Returns:**

| Return Value | Description |
|--------|------|
| `0` | Write successful |
| `-1` | IPC sync timeout or failure |

**Note:** The operation flow is the same as `bflb_flash_erase_mcs`; it calls `bflb_flash_write()` after IPC sync protection.

---

### bflb_flash_read_mcs

Multi-core safe Flash read operation.

```c
int bflb_flash_read_mcs(uint32_t addr, uint8_t *data, uint32_t len);
```

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `addr` | `uint32_t` | Flash read start address |
| `data` | `uint8_t *` | Read data buffer pointer |
| `len` | `uint32_t` | Read length (bytes) |

**Returns:**

| Return Value | Description |
|--------|------|
| `0` | Read successful |
| `-1` | IPC sync timeout or failure |

**Note:** The operation flow is the same as write; it calls `bflb_flash_read()` after IPC sync protection.

---

### bflb_sys_reboot_mcs

Multi-core safe system reset.

```c
void bflb_sys_reboot_mcs(void);
```

**Note:** Operation flow:
1. Send `IPC_SYNC_SUSPEND_CMD` to suspend the NP core (3-second timeout)
2. Call `bl_sys_reset_por()` to perform a system power-on reset
3. Send `IPC_SYNC_RESUME_CMD` to attempt to resume the NP core

> **Note:** After system reset, the AP core will restart, so the Resume operation is effectively only executed if the reset does not take effect immediately.

---

## IPC Sync Constants

```c
#define IPC_SYNC_SUSPEND_CMD   // NP suspend command
#define IPC_SYNC_SUSPEND_ACK   // NP suspend acknowledgment
#define IPC_SYNC_RESUME_CMD    // NP resume command
#define IPC_SYNC_RESUME_ACK    // NP resume acknowledgment
```

**Timeout Configuration:**

| Operation | IPC Timeout |
|------|---------|
| Suspend wait | 3000 ms |
| Resume wait (normal flow) | 3000 ms |
| Resume wait (error recovery) | 1000 ms |

---

## Usage Examples

### Example 1: OTA Firmware Update (Multi-Core Safe)

```c
#include "bflb_multi_core_sync.h"
#include "bflb_flash.h"

int ota_firmware_update_mcs(uint32_t partition_addr, const uint8_t *fw_data, uint32_t fw_size)
{
    int ret;
    uint32_t erase_len = ALIGN_UP(fw_size, 4096); // 4K alignment
    
    // 1. Erase Flash partition (multi-core safe)
    ret = bflb_flash_erase_mcs(partition_addr, erase_len);
    if (ret != 0) {
        printf("[OTA] Erase failed: %d\n", ret);
        return ret;
    }
    
    // 2. Write new firmware (multi-core safe)
    ret = bflb_flash_write_mcs(partition_addr, fw_data, fw_size);
    if (ret != 0) {
        printf("[OTA] Write failed: %d\n", ret);
        return ret;
    }
    
    // 3. Verify write
    uint8_t verify_buf[256];
    ret = bflb_flash_read_mcs(partition_addr, verify_buf, 256);
    if (ret != 0) {
        printf("[OTA] Verify read failed: %d\n", ret);
        return ret;
    }
    
    if (memcmp(verify_buf, fw_data, 256) != 0) {
        printf("[OTA] Verify mismatch!\n");
        return -1;
    }
    
    printf("[OTA] Update successful\n");
    return 0;
}
```

### Example 2: Safe System Reset

```c
#include "bflb_multi_core_sync.h"

void safe_system_reboot(void)
{
    printf("System rebooting with NP sync...\n");
    
    // Ensure NP core is safely suspended before reset
    bflb_sys_reboot_mcs();
    
    // Will not reach here
}
```

### Example 3: Flash Configuration Storage

```c
#include "bflb_multi_core_sync.h"

#define CONFIG_FLASH_ADDR  0x1F0000
#define CONFIG_SECTOR_SIZE 4096

typedef struct {
    uint32_t magic;
    uint32_t version;
    uint8_t  settings[256];
    uint32_t crc;
} device_config_t;

int save_config_mcs(const device_config_t *config)
{
    int ret;
    
    // 1. Erase config sector
    ret = bflb_flash_erase_mcs(CONFIG_FLASH_ADDR, CONFIG_SECTOR_SIZE);
    if (ret != 0) return ret;
    
    // 2. Write config
    ret = bflb_flash_write_mcs(CONFIG_FLASH_ADDR, 
                                (const uint8_t *)config, 
                                sizeof(device_config_t));
    return ret;
}

int load_config_mcs(device_config_t *config)
{
    return bflb_flash_read_mcs(CONFIG_FLASH_ADDR,
                               (uint8_t *)config,
                               sizeof(device_config_t));
}
```

---

## Important Notes

1. **Compilation Condition:** All functions are compiled under `#ifdef CONFIG_IPC`, ensuring that undefined references are not introduced on platforms without IPC.

2. **Timeout Handling:** Suspend/Resume operations have timeout protection (3 seconds). On timeout, an error message is printed and `-1` is returned. The application layer should check the return value and handle timeout conditions appropriately.

3. **Error Recovery:** When a Flash operation fails, the function will still attempt to send a Resume command to recover the NP core, preventing it from being permanently suspended.

4. **Difference from Direct Flash API:** `bflb_flash_erase_mcs()` / `bflb_flash_write_mcs()` / `bflb_flash_read_mcs()` internally call the corresponding `bflb_flash_erase()` / `bflb_flash_write()` / `bflb_flash_read()` functions. The difference is the addition of NP core Suspend/Resume sync protection.

5. **BL616 Single Core:** BL616 does not need this module; directly use `bflb_flash_erase()` / `bflb_flash_write()` / `bflb_flash_read()`.

| Scenario | AP Core (BL618DG) | NP Core (BL618DG) | BL616 |
|------|----------------|-----------------|-------|
| Flash Erase | `bflb_flash_erase_mcs()` | — | `bflb_flash_erase()` |
| Flash Write | `bflb_flash_write_mcs()` | — | `bflb_flash_write()` |
| Flash Read | `bflb_flash_read_mcs()` | — | `bflb_flash_read()` |
| System Reset | `bflb_sys_reboot_mcs()` | — | `bl_sys_reset_por()` |
