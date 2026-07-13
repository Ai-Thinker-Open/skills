# Efuse API Reference

> Source file: `components/platform/hosal/include/hosal_efuse.h`

> Efuse (electronic fuse) is a one-time programmable storage area inside the BL602 chip, used to store non-modifiable hardware configuration data (such as MAC address, encryption keys, calibration parameters, etc.). Read operations can be performed multiple times; write operations are typically only possible once, and some bits are permanently locked.

## Function API

### `hosal_efuse_read`

Read data from Efuse.

```c
int hosal_efuse_read(uint32_t addr, uint32_t *data, uint32_t len);
```

| Parameter | Description |
|------|------|
| `addr` | Efuse address (byte offset) |
| `data` | Read data storage buffer |
| `len` | Read length (bytes), 4-byte alignment recommended |

**Return value**: `0` success, `EIO` failure

---

### `hosal_efuse_write`

Write data to Efuse (typically one-time).

```c
int hosal_efuse_write(uint32_t addr, uint32_t *data, uint32_t len);
```

| Parameter | Description |
|------|------|
| `addr` | Efuse address (byte offset) |
| `data` | Data buffer to write |
| `len` | Write length (bytes), 4-byte alignment recommended |

**Return value**: `0` success, `EIO` failure

> **Note**: Write operations are irreversible and cannot be undone after execution. It is recommended to first read and confirm the current value, ensuring it is all `0xFF` (blank) before writing.

## Usage Example

```c
#include "hal_efuse.h"

uint32_t data[2] = {0};

// Read 8 bytes of data from Efuse address 0x10
int ret = hosal_efuse_read(0x10, data, 8);
if (ret == 0) {
    printf("Efuse[0x10]: 0x%08X\r\n", data[0]);
}

// Write 4 bytes of data to Efuse address 0x20 (cautious operation)
uint32_t write_data = 0x12345678;
ret = hosal_efuse_write(0x20, &write_data, 4);
if (ret == 0) {
    printf("Efuse write success\r\n");
}
```

## Common Efuse Addresses (BL602)

| Address | Content | Description |
|------|------|------|
| 0x00 | Chip ID | Chip batch number |
| 0x10 | MAC Address[0] | Wi-Fi MAC address lower 32 bits |
| 0x14 | MAC Address[1] | Wi-Fi MAC address upper 16 bits + others |
| 0x20 | Security Key | Key data |

> Address definitions may vary across different firmware versions. Please refer to the official SDK documentation or `bl_efuse.h`.
