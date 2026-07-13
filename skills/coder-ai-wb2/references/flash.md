# Flash API Reference

> Source file: `components/platform/hosal/include/hosal_flash.h`

## Macro Definitions

```c
#define HOSAL_FLASH_FLAG_ADDR_0     0       // Use partition table address 0
#define HOSAL_FLASH_FLAG_ADDR_1     (1<<0)  // Use partition table address 1
#define HOSAL_FLASH_FLAG_BUSADDR    (1<<1)   // Use bus physical address
```

## Type Definitions

### `hosal_logic_partition_t` — Flash Partition Information Structure

```c
typedef struct {
    const char  *partition_description; // Partition name
    uint32_t     partition_start_addr; // Partition start address
    uint32_t     partition_length;      // Partition length (bytes)
    uint32_t     partition_options;     // Options
} hosal_logic_partition_t;
```

### `hosal_flash_dev_t` — Flash Device Handle

```c
typedef struct hosal_flash_dev {
    void *flash_dev;
} hosal_flash_dev_t;
```

> Obtained via `hosal_flash_open()`. Do not access internal members directly.

## Function Interface

### `hosal_flash_open`

Opens a Flash partition and obtains a device handle.

```c
hosal_flash_dev_t *hosal_flash_open(const char *name, unsigned int flags);
```

| Parameter | Description |
|-----------|-------------|
| `name` | Partition name string, such as `"app"`, `"wifi"`, `"boot"`, etc. |
| `flags` | Address flags: `HOSAL_FLASH_FLAG_ADDR_0`, `HOSAL_FLASH_FLAG_ADDR_1`, `HOSAL_FLASH_FLAG_BUSADDR` |

**Return value**: Returns device handle on success, `NULL` on failure

> The specific partition table definition is in the SDK's `partition.csv` file.

---

### `hosal_flash_info_get`

Gets partition information.

```c
int hosal_flash_info_get(hosal_flash_dev_t *p_dev,
                         hosal_logic_partition_t *partition);
```

| Parameter | Description |
|-----------|-------------|
| `p_dev` | Device handle returned by `hosal_flash_open` |
| `partition` | Output parameter, stores partition information |

---

### `hosal_flash_erase`

Erases a partition.

```c
int hosal_flash_erase(hosal_flash_dev_t *p_dev,
                       uint32_t off_set,
                       uint32_t size);
```

| Parameter | Description |
|-----------|-------------|
| `p_dev` | Device handle |
| `off_set` | Offset within partition (bytes) |
| `size` | Size to erase (bytes) |

> Erasing is performed by sector. `size` will be aligned to sector boundaries.

---

### `hosal_flash_write`

Writes to Flash (does not auto-erase).

```c
int hosal_flash_write(hosal_flash_dev_t *p_dev,
                      uint32_t *off_set,
                      const void *in_buf,
                      uint32_t in_buf_size);
```

| Parameter | Description |
|-----------|-------------|
| `p_dev` | Device handle |
| `off_set` | Input/output parameter: write start position, returns last unwritten address |
| `in_buf` | Data buffer |
| `in_buf_size` | Number of bytes to write |

> Target area must be `0xFF` before writing, otherwise data will be corrupted. It is recommended to use `hosal_flash_erase_write`.

---

### `hosal_flash_erase_write`

Erases and writes (common usage).

```c
int hosal_flash_erase_write(hosal_flash_dev_t *p_dev,
                            uint32_t *off_set,
                            const void *in_buf,
                            uint32_t in_buf_size);
```

| Parameter | Description |
|-----------|-------------|
| `off_set` | Input/output parameter: start position, returns last unwritten address |

---

### `hosal_flash_read`

Reads Flash.

```c
int hosal_flash_read(hosal_flash_dev_t *p_dev,
                     uint32_t *off_set,
                     void *out_buf,
                     uint32_t out_buf_size);
```

---

### `hosal_flash_raw_read`

Directly reads Flash physical address.

```c
int hosal_flash_raw_read(void *buffer, uint32_t address, uint32_t length);
```

---

### `hosal_flash_raw_write`

Directly writes to Flash physical address (requires prior erase).

```c
int hosal_flash_raw_write(void *buffer, uint32_t address, uint32_t length);
```

---

### `hosal_flash_raw_erase`

Directly erases Flash physical address.

```c
int hosal_flash_raw_erase(uint32_t start_addr, uint32_t length);
```

---

### `hosal_flash_close`

Closes Flash partition and releases device handle.

```c
int hosal_flash_close(hosal_flash_dev_t *p_dev);
```

## Usage Example

```c
#include "hal_flash.h"

#define FLASH_ADDR  0x1A0000
#define FLASH_SIZE  0x1000

// Open app partition
hosal_flash_dev_t *flash = hosal_flash_open("app", HOSAL_FLASH_FLAG_ADDR_0);
if (flash == NULL) {
    printf("Flash open failed\r\n");
    return;
}

// Read partition info
hosal_logic_partition_t info;
hosal_flash_info_get(flash, &info);
printf("Partition: start=0x%x, size=0x%x\r\n",
       info.partition_start_addr, info.partition_length);

// Erase + write (safe method)
uint8_t data[256] = {0x12, 0x34, 0x56, 0x78};
uint32_t offset = 0;
int ret = hosal_flash_erase_write(flash, &offset, data, sizeof(data));
if (ret != 0) {
    printf("Write failed\r\n");
}

// Read
uint8_t read_buf[256];
offset = 0;
hosal_flash_read(flash, &offset, read_buf, sizeof(read_buf));

// Close
hosal_flash_close(flash);
```

---

## Register-Level Programming

> Register Header: `components/platform/soc/bl602/bl602_std/bl602_std/Device/Bouffalo/BL602/Peripherals/sf_ctrl_reg.h`  
> Base Address: `0x4000B000`

### Register Overview

| Offset | Name | Description |
|--------|------|-------------|
| 0x00 | SF_CTRL_CFG | SPI flash configuration (mode, direction) |
| 0x04 | SF_CTRL_STATUS | Flash status register |
| 0x08 | SF_CTRL_CMD | Flash command value |
| 0x0C | SF_CTRL_ADDR | Flash address (up to 24 bits) |
| 0x10 | SF_CTRL_TXDATA | TX data FIFO |
| 0x14 | SF_CTRL_RXDATA | RX data FIFO |
| 0x18 | SF_CTRL_CTRL | Control (start, manual mode) |
| 0x1C | SF_CTRL_INT_STATUS | Interrupt status |
| 0x20 | SF_CTRL_INT_MASK | Interrupt mask |
| 0x24 | SF_CTRL_TIMING | Flash timing configuration |
| 0x28 | SF_CTRL_SEMAPHORE | Semaphore for flash access |

### Key Register Fields

**SF_CTRL_CFG (0x00)**

| Bits | Name | Description |
|------|------|-------------|
| 0 | spi_mode | SPI mode (0=read, 1=write) |
| 4 | direct_mode | Direct mode enable |
| 8 | wp_mode | Write protect mode |

**SF_CTRL_CMD (0x08)**

| Bits | Name | Description |
|------|------|-------------|
| [7:0] | cmd | Command value (0x03=read, 0x02=write, 0x9F=JEDEC ID) |

**SF_CTRL_ADDR (0x0C)**

| Bits | Name | Description |
|------|------|-------------|
| [23:0] | addr | Flash address |

**SF_CTRL_CTRL (0x18)**

| Bits | Name | Description |
|------|------|-------------|
| 0 | start | Start operation (write 1) |
| 4 | manual_en | Manual mode enable |

**SF_CTRL_INT_STATUS (0x1C)**

| Bits | Name | Description |
|------|------|-------------|
| 0 | tx_done | TX done |
| 1 | rx_done | RX done |
| 2 | error | Operation error |

### Register-Level Code Example

```c
#include <stdint.h>

#define SF_CTRL_BASE  0x4000B000

/* Register offsets (32-bit) */
#define SF_CTRL_CFG       0x00
#define SF_CTRL_STATUS    0x04
#define SF_CTRL_CMD       0x08
#define SF_CTRL_ADDR      0x0C
#define SF_CTRL_TXDATA    0x10
#define SF_CTRL_RXDATA    0x14
#define SF_CTRL_CTRL      0x18
#define SF_CTRL_INT_STATUS  0x1C

/* Bit masks */
#define SF_CTRL_START     (1 << 0)
#define SF_CTRL_MANUAL_EN (1 << 4)
#define SF_CTRL_TX_DONE   (1 << 0)
#define SF_CTRL_RX_DONE   (1 << 1)
#define SF_CTRL_ERROR     (1 << 2)

/* Flash commands */
#define FLASH_CMD_READ    0x03
#define FLASH_CMD_WRITE   0x02
#define FLASH_CMD_JEDEC   0x9F
#define FLASH_CMD_WREN    0x06
#define FLASH_CMD_RDSR    0x05

static volatile uint32_t * const SF = (volatile uint32_t *)SF_CTRL_BASE;

/* Wait for flash operation to complete */
static int flash_wait_done(void) {
    uint32_t timeout = 100000;
    while (timeout--) {
        uint32_t status = SF[SF_CTRL_INT_STATUS / 4];
        if (status & SF_CTRL_TX_DONE)
            return 0;
        if (status & SF_CTRL_ERROR)
            return -1;
    }
    return -1;
}

/* Read jedec ID via register-level access */
int flash_read_jedec_id(uint8_t *jedec_id) {
    /* Set up manual mode for read */
    SF[SF_CTRL_CFG / 4] = 0;
    SF[SF_CTRL_CMD / 4] = FLASH_CMD_JEDEC;
    SF[SF_CTRL_ADDR / 4] = 0;
    SF[SF_CTRL_CTRL / 4] = SF_CTRL_MANUAL_EN | SF_CTRL_START;

    if (flash_wait_done() != 0)
        return -1;

    /* Read 3 bytes (JEDEC ID: manufacturer, device type, capacity) */
    jedec_id[0] = (uint8_t)(SF[SF_CTRL_RXDATA / 4] & 0xFF);
    jedec_id[1] = (uint8_t)((SF[SF_CTRL_RXDATA / 4] >> 8) & 0xFF);
    jedec_id[2] = (uint8_t)((SF[SF_CTRL_RXDATA / 4] >> 16) & 0xFF);

    return 0;
}

/* Read flash memory (simplified, single byte per operation) */
int flash_read_reg(uint32_t addr, uint8_t *data, uint32_t len) {
    uint32_t i;

    for (i = 0; i < len; i++) {
        SF[SF_CTRL_CFG / 4] = 0;  /* read mode */
        SF[SF_CTRL_CMD / 4] = FLASH_CMD_READ;
        SF[SF_CTRL_ADDR / 4] = addr + i;
        SF[SF_CTRL_CTRL / 4] = SF_CTRL_MANUAL_EN | SF_CTRL_START;

        if (flash_wait_done() != 0)
            return -1;

        data[i] = (uint8_t)(SF[SF_CTRL_RXDATA / 4] & 0xFF);
    }
    return 0;
}

/* Write flash enable (WREN) */
void flash_write_enable(void) {
    SF[SF_CTRL_CFG / 4] = 0;
    SF[SF_CTRL_CMD / 4] = FLASH_CMD_WREN;
    SF[SF_CTRL_ADDR / 4] = 0;
    SF[SF_CTRL_CTRL / 4] = SF_CTRL_MANUAL_EN | SF_CTRL_START;
    flash_wait_done();
}

/* Example: read 4 bytes from flash address 0x1000 */
void flash_example(void) {
    uint8_t id[3];
    uint8_t buf[4];

    if (flash_read_jedec_id(id) == 0) {
        printf("JEDEC ID: %02X %02X %02X\r\n", id[0], id[1], id[2]);
    }

    if (flash_read_reg(0x1000, buf, 4) == 0) {
        printf("Data: %02X %02X %02X %02X\r\n", buf[0], buf[1], buf[2], buf[3]);
    }
}
```
