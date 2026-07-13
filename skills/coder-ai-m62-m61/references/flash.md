# Flash API Reference (BL616/BL618)

> External SPI NOR Flash driver with XIP (Execute-In-Place) support

**Source:** `bouffalo_sdk/drivers/lhal/include/bflb_flash.h`  
**Hardware Base:** `SF_CTRL_BASE = 0x2000B000` (part of GLB at 0x20000000+)  
**XIP Base:** `FLASH_XIP_BASE = 0xA0000000` (maps to external flash via cache)  
**XIP End:** `FLASH_XIP_BASE + 64 MB`

---

## Overview

The BL616/BL618 Flash API provides low-level access to external SPI NOR Flash memory via the Serial Flash Controller (SF_CTRL). The chip supports **XIP (Execute-In-Place)**, allowing CPU instruction fetches directly from external flash through the cache controller, with the flash mapped at virtual address `0xA0000000`.

Flash operations include erase (sector/page), write, read, and encrypted access via AES. The flash is organized as:
- **Typical sector size:** 4 KB
- **Typical page size:** 256 B
- **Supported I/O modes:** Normal (1-bit), Dual Output, Quad Output, Dual I/O, Quad I/O

---

## IO Mode Definitions

```c
#define FLASH_IOMODE_NIO  0  /* Normal 1-bit SPI */
#define FLASH_IOMODE_DO   1  /* Dual Output (DO: 2-bit read) */
#define FLASH_IOMODE_QO   2  /* Quad Output (QO: 4-bit read) */
#define FLASH_IOMODE_DIO  3  /* Dual I/O (DIO: 2-bit read/write) */
#define FLASH_IOMODE_QIO  4  /* Quad I/O (QIO: 4-bit read/write) */
```

### AES Key Types

```c
#define FLASH_AES_KEY_128BITS        0
#define FLASH_AES_KEY_192BITS        2
#define FLASH_AES_KEY_256BITS        1
#define FLASH_AES_KEY_DOUBLE_128BITS  3
```

---

## Flash AES Configuration Structure

```c
struct bflb_flash_aes_config_s {
    uint8_t  region;          /* AES region index (0-3) */
    uint8_t  region_enable;   /* Enable region matching */
    uint8_t  lock_enable;     /* Lock region config after write */
    const uint8_t *key;       /* AES key (128/192/256-bit) */
    uint8_t  keybits;         /* Key length in bits */
    uint8_t  *iv;             /* Initialization vector (for XTS mode) */
    uint32_t start_addr;      /* Region start flash address */
    uint32_t end_addr;        /* Region end flash address */
};
```

---

## Function Reference

### `bflb_flash_init()`

```c
int bflb_flash_init(void);
```

Initialize the flash controller and auto-detect flash parameters. Must be called before any other flash operation.

**Returns:** `0` on success, negative errno on failure.

---

### `bflb_flash_erase()`

```c
int bflb_flash_erase(uint32_t addr, uint32_t len);
```

Erase flash sectors covering the specified address range. Erase is performed at sector granularity (typically 4 KB sectors).

**Parameters:**
- `addr` — Flash physical address (0-based, not XIP virtual address)
- `len`  — Number of bytes to erase (will be rounded up to sector boundary)

**Returns:** `0` on success, negative errno on failure.

**Example:**
```c
/* Erase 4 KB sector at flash address 0x10000 */
int ret = bflb_flash_erase(0x10000, 4096);
if (ret < 0) {
    printf("Flash erase failed: %d\n", ret);
}
```

---

### `bflb_flash_write()`

```c
int bflb_flash_write(uint32_t addr, uint8_t *data, uint32_t len);
```

Write data to flash. Flash must be erased before writing (write programs 0-bits only). Alignment requirements depend on flash type.

**Parameters:**
- `addr` — Flash physical target address
- `data` — Pointer to data buffer to write
- `len`  — Number of bytes to write

**Returns:** `0` on success, negative errno on failure.

**Example:**
```c
uint8_t config_data[] = { 0x01, 0x02, 0x03, 0x04 };
int ret = bflb_flash_write(0x10000, config_data, sizeof(config_data));
if (ret < 0) {
    printf("Flash write failed: %d\n", ret);
}
```

---

### `bflb_flash_read()`

```c
int bflb_flash_read(uint32_t addr, uint8_t *data, uint32_t len);
```

Read data from flash into a buffer.

**Parameters:**
- `addr` — Flash physical source address
- `data` — Pointer to destination buffer
- `len`  — Number of bytes to read

**Returns:** `0` on success, negative errno on failure.

**Example:**
```c
uint8_t read_buf[16];
int ret = bflb_flash_read(0x10000, read_buf, sizeof(read_buf));
if (ret == 0) {
    printf("Read: %02x %02x %02x %02x...\n",
           read_buf[0], read_buf[1], read_buf[2], read_buf[3]);
}
```

---

### `bflb_flash_set_iomode()`

```c
void bflb_flash_set_iomode(uint8_t iomode);
```

Set the flash I/O mode for read operations. This configures the serial flash controller's signal mode ( Normal SPI / Dual / Quad ).

**Parameters:**
- `iomode` — One of `FLASH_IOMODE_NIO`, `FLASH_IOMODE_DO`, `FLASH_IOMODE_QO`, `FLASH_IOMODE_DIO`, `FLASH_IOMODE_QIO`

---

### `bflb_flash_get_jedec_id()`

```c
uint32_t bflb_flash_get_jedec_id(void);
```

Get the flash JEDEC ID (Manufacturer ID + Device ID). Useful for identifying the connected flash chip.

**Returns:** 24-bit JEDEC ID (MSB→LSB: manufacturer, device ID high, device ID low).

---

### `bflb_flash_get_size()`

```c
uint32_t bflb_flash_get_size(void);
```

Get the detected flash size in bytes.

**Returns:** Flash size in bytes.

---

### `bflb_flash_get_image_offset()`

```c
uint32_t bflb_flash_get_image_offset(void);
```

Get the flash image offset (boot partition start). This is where the bootloader expects the application to be placed.

**Returns:** Image offset in bytes.

---

### `bflb_flash_set_cache()`

```c
int bflb_flash_set_cache(uint8_t cont_read, uint8_t cache_enable,
                         uint8_t cache_way_disable, uint32_t flash_offset);
```

Configure the flash cache and continuous read mode for XIP operations.

**Parameters:**
- `cont_read`        — Enable continuous read mode (reduces read latency)
- `cache_enable`     — Enable instruction/data cache
- `cache_way_disable` — Number of cache ways to disable (0=all enabled)
- `flash_offset`     — Flash image offset (for cache tag setup)

**Returns:** `0` on success, negative errno on failure.

---

### `bflb_flash_aes_init()` / `bflb_flash_aes_enable()` / `bflb_flash_aes_disable()`

```c
void bflb_flash_aes_init(struct bflb_flash_aes_config_s *config);
void bflb_flash_aes_enable(void);
void bflb_flash_aes_disable(void);
```

Configure and enable/disable AES decryption for encrypted flash reads. Allows encrypted firmware to execute in-place from external flash.

---

### `bflb_flash_jump_app()`

```c
void bflb_flash_jump_app(uint32_t flash_addr);
```

Jump to and execute code at the given flash address (for booting secondary images).

---

## Complete Usage Example

```c
#include "bflb_flash.h"
#include "bflb_sec_eng.h"

void flash_demo(void)
{
    int ret;

    /* Initialize flash controller */
    ret = bflb_flash_init();
    if (ret < 0) {
        printf("Flash init failed\n");
        return;
    }

    /* Read JEDEC ID to identify flash chip */
    uint32_t jedec_id = bflb_flash_get_jedec_id();
    printf("Flash JEDEC ID: %06X\n", jedec_id);

    /* Get flash size */
    uint32_t flash_size = bflb_flash_get_size();
    printf("Flash size: %u bytes\n", flash_size);

    /* Set Quad I/O mode for faster reads */
    bflb_flash_set_iomode(FLASH_IOMODE_QIO);

    /* Configure flash cache for XIP */
    uint32_t img_offset = bflb_flash_get_image_offset();
    bflb_flash_set_cache(1, 1, 0, img_offset);

    /* Erase and write a data structure to flash */
    #define FLASH_DATA_ADDR 0x11000
    uint8_t data_to_write[] = { 0xDE, 0xAD, 0xBE, 0xEF };

    ret = bflb_flash_erase(FLASH_DATA_ADDR, sizeof(data_to_write));
    if (ret == 0) {
        ret = bflb_flash_write(FLASH_DATA_ADDR, data_to_write,
                               sizeof(data_to_write));
    }

    /* Read it back */
    if (ret == 0) {
        uint8_t read_buf[4];
        bflb_flash_read(FLASH_DATA_ADDR, read_buf, sizeof(read_buf));
        printf("Read back: %02X %02X %02X %02X\n",
               read_buf[0], read_buf[1], read_buf[2], read_buf[3]);
    }

    /* Setup AES encrypted region for secure boot */
    struct bflb_flash_aes_config_s aes_cfg = {
        .region = 0,
        .region_enable = 1,
        .lock_enable = 1,
        .key = my_aes_key,
        .keybits = 128,
        .iv = my_aes_iv,
        .start_addr = 0x20000,
        .end_addr = 0x40000,
    };
    bflb_flash_aes_init(&aes_cfg);
    bflb_flash_aes_enable();
}
```

---

## Register-Level Reference

The Flash controller registers are at `SF_CTRL_BASE = 0x2000B000`:

| Offset | Register | Description |
|--------|----------|-------------|
| `0x00` | SF_CTRL_0 | Control register 0 |
| `0x04` | SF_CTRL_1 | Control register 1 |
| `0x08` | SF_IF_SAHB_0 | AHB to SFLASH interface config 0 |
| `0x0C` | SF_IF_SAHB_1 | AHB to SFLASH interface config 1 |
| `0x10` | SF_IF_SAHB_2 | AHB to SFLASH interface config 2 |
| `0x14` | SF_IF_IAHB_0 | Internal AHB config 0 |
| `0x18` | SF_IF_IAHB_1 | Internal AHB config 1 |
| `0x1C` | SF_IF_IAHB_2 | Internal AHB config 2 |
| `0x20` | SF_IF_STATUS_0 | Interface status 0 |
| `0x28` | SF_AES | AES configuration |
| `0x30-0x40` | SF_IF_IO_DLY_0-4 | I/O delay configuration |
| `0xB00` | SF_CTRL_2 | Control register 2 |
| `0xB04` | SF_CTRL_3 | Control register 3 |

> **Note:** The SF_CTRL shares the same base address as QSPI at `0x2000B000`. The controller automatically handles flash protocol conversion (SPI/DSPI/QSPI) based on the configured I/O mode.
