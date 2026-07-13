# eFuse API Reference (BL616/BL618)

> One-Time Programmable memory for secure keys, MAC addresses, and trim data

**Source:** `bouffalo_sdk/drivers/lhal/include/bflb_efuse.h`  
**Control Header:** `bouffalo_sdk/drivers/lhal/include/bflb_ef_ctrl.h`  
**Hardware Base:** `EF_CTRL_BASE = 0x20056000` (same as `EFUSE_BASE`)  
**IRQ:** `EFUSE_IRQn = IRQ_NUM_BASE + 26` (BL616)  
**Device Name:** `BFLB_NAME_EF_CTRL = "ef_ctrl"`  

---

## Overview

The BL616/BL618 contains **eFuse (electronic fuse)** storage — a small array of one-time programmable non-volatile memory bits. Once a fuse bit is programmed (blown), it cannot be reversed. This makes eFuse ideal for storing:

- **Chip ID** — unique identifier for each chip
- **MAC addresses** — WiFi and Bluetooth MAC addresses
- **AES keys** — secure boot and flash encryption keys
- **Secure boot configuration** — sign and AES mode settings
- **ADC calibration trim** — factory calibration values for analog blocks
- **Device info** — package type, flash info, process corner, etc.

### eFuse Device Info Structure

```c
typedef struct {
    uint8_t  package;           /* Package type code */
    uint8_t  flash_info;        /* Flash information code */
#if defined(BL602)
    uint8_t  ext_info;          /* Extension info (BL602) */
    uint8_t  mcu_info;          /* MCU info (BL602) */
#else
    uint8_t  psram_info;        /* PSRAM information */
#endif
#if defined(BL702) || defined(BL702L)
    uint8_t  sf_swap_cfg;       /* SF swap config */
#else
    uint8_t  version;           /* Version information */
#endif
#if defined(BL616)
    uint16_t process_corner;    /* Process corner (PVT) */
#endif
    const char *package_name;    /* Human-readable package name */
    const char *flash_info_name; /* Human-readable flash info */
#if !defined(BL602)
    const char *psram_info_name; /* Human-readable PSRAM info */
#endif
#if defined(BL616)
    char process_corner_name[16]; /* Human-readable process corner */
#endif
} bflb_efuse_device_info_type;
```

---

## Function Reference

### `bflb_efuse_get_chipid()`

```c
int bflb_efuse_get_chipid(uint8_t chipid[8]);
```

Read the 64-bit unique chip identifier from eFuse.

**Parameters:**
- `chipid` — Pointer to an 8-byte buffer to receive the chip ID

**Returns:** `0` on success, `-1` on failure.

**Example:**
```c
uint8_t chipid[8];
int ret = bflb_efuse_get_chipid(chipid);
if (ret == 0) {
    printf("Chip ID: %02X%02X%02X%02X%02X%02X%02X%02X\n",
           chipid[0], chipid[1], chipid[2], chipid[3],
           chipid[4], chipid[5], chipid[6], chipid[7]);
}
```

---

### `bflb_efuse_get_device_info()`

```c
void bflb_efuse_get_device_info(bflb_efuse_device_info_type *device_info);
```

Read and decode device information from eFuse, including package type, flash info, PSRAM info, and process corner (for BL616).

**Parameters:**
- `device_info` — Pointer to structure to receive decoded device info

**Example:**
```c
bflb_efuse_device_info_type dev_info;
bflb_efuse_get_device_info(&dev_info);
printf("Package: %s\n", dev_info.package_name);
printf("Flash: %s\n", dev_info.flash_info_name);
#if defined(BL616)
printf("Process corner: %s\n", dev_info.process_corner_name);
#endif
```

---

### `bflb_efuse_read_mac_address()`

```c
int bflb_efuse_read_mac_address(uint8_t mac[6], uint8_t reload);
```

Read a stored MAC address from eFuse.

**Parameters:**
- `mac`    — Pointer to a 6-byte buffer to receive the MAC address
- `reload` — If `1`, re-read from eFuse; if `0`, use cached value

**Returns:** `0` on success, `-1` if no MAC address is programmed.

---

### `bflb_efuse_write_mac_address_opt()`

```c
int bflb_efuse_write_mac_address_opt(uint8_t slot, uint8_t mac[6], uint8_t program);
```

Program a MAC address into a specific eFuse slot.

**Parameters:**
- `slot`    — MAC address slot (0-based, typically 0 or 1)
- `mac`    — Pointer to 6-byte MAC address to program
- `program` — If `1`, actually program (blow fuses); if `0`, just verify layout

**Returns:** `0` on success, `-1` on failure.

---

### `bflb_efuse_read_mac_address_opt()`

```c
int bflb_efuse_read_mac_address_opt(uint8_t slot, uint8_t mac[6], uint8_t reload);
```

Read MAC address from a specific slot.

**Parameters:**
- `slot`   — MAC address slot to read from
- `mac`    — Pointer to 6-byte buffer
- `reload` — If `1`, re-read from eFuse; if `0`, use cached

**Returns:** `0` on success, `-1` on failure.

---

### `bflb_efuse_is_mac_address_slot_empty()`

```c
uint8_t bflb_efuse_is_mac_address_slot_empty(uint8_t slot, uint8_t reload);
```

Check if a MAC address slot is empty (not programmed).

**Returns:** `1` if slot is empty, `0` if slot contains data.

---

### `bflb_efuse_read_secure_boot()`

```c
void bflb_efuse_read_secure_boot(uint8_t *sign, uint8_t *aes);
```

Read the secure boot configuration from eFuse.

**Parameters:**
- `sign` — Pointer to receive sign type
- `aes`  — Pointer to receive AES type

---

### `bflb_efuse_enable_aes()`

```c
int bflb_efuse_enable_aes(uint8_t aes_type, uint8_t xts_mode);
```

Program the AES key type for secure boot or flash encryption into eFuse.

**Parameters:**
- `aes_type` — AES key type (0=none, 1=AES-128, 2=AES-192, 3=AES-256)
- `xts_mode` — XTS mode enable (0=normal, 1=XTS)

**Returns:** `0` on success.

---

### `bflb_efuse_rw_lock_aes_key()`

```c
int bflb_efuse_rw_lock_aes_key(uint8_t key_index, uint8_t rd_lock, uint8_t wr_lock);
```

Lock read and/or write access to an AES key slot in eFuse.

**Parameters:**
- `key_index` — AES key index (0-3)
- `rd_lock`   — Read lock (1=locked, 0=unlocked)
- `wr_lock`   — Write lock (1=locked, 0=unlocked)

**Returns:** `0` on success.

---

### `bflb_efuse_rw_lock_dbg_key()`

```c
int bflb_efuse_rw_lock_dbg_key(uint8_t rd_lock, uint8_t wr_lock);
```

Lock debug key read/write access in eFuse.

---

### `bflb_efuse_write_lock_pk_hash()`

```c
int bflb_efuse_write_lock_pk_hash(uint32_t pkhash_len);
```

Lock public key hash in eFuse after programming.

---

### `bflb_efuse_write_lock_usb_pid_vid()`

```c
int bflb_efuse_write_lock_usb_pid_vid(void);
```

Lock USB PID/VID in eFuse.

---

### ADC Trim Functions

```c
float bflb_efuse_get_adc_trim(void);                  /* BL616 */
uint32_t bflb_efuse_get_adc_tsen_trim(void);           /* Temperature sensor trim */
uint32_t bflb_efuse_get_adc_vref_trim(struct bflb_device_s *dev); /* ADC Vref trim (BL616CL/BL618DG) */
int32_t bflb_efuse_get_adc_offset_trim(struct bflb_device_s *dev); /* ADC offset trim */
float bflb_efuse_get_adc_gain_trim(struct bflb_device_s *dev);     /* ADC gain trim */
```

Read factory calibration values from eFuse for ADC operations.

---

## Complete Usage Examples

### Read Chip ID and Device Info

```c
#include "bflb_efuse.h"
#include <stdio.h>

void efuse_info_demo(void)
{
    uint8_t chipid[8];
    bflb_efuse_device_info_type dev_info;

    /* Read unique chip ID */
    if (bflb_efuse_get_chipid(chipid) == 0) {
        printf("Chip ID: %02X:%02X:%02X:%02X:%02X:%02X:%02X:%02X\n",
               chipid[0], chipid[1], chipid[2], chipid[3],
               chipid[4], chipid[5], chipid[6], chipid[7]);
    }

    /* Read device information */
    bflb_efuse_get_device_info(&dev_info);
    printf("Package:  %s\n", dev_info.package_name);
    printf("Flash:    %s\n", dev_info.flash_info_name);
    printf("PSRAM:    %s\n", dev_info.psram_info_name);
#if defined(BL616)
    printf("P-CORner: %s\n", dev_info.process_corner_name);
#endif
}
```

### Read MAC Address

```c
#include "bflb_efuse.h"
#include <stdio.h>

void read_mac_demo(void)
{
    uint8_t mac[6];

    /* Try to read MAC address (slot 0) */
    if (bflb_efuse_read_mac_address(mac, 1) == 0) {
        printf("MAC: %02X:%02X:%02X:%02X:%02X:%02X\n",
               mac[0], mac[1], mac[2], mac[3], mac[4], mac[5]);
    } else {
        printf("No MAC address programmed in eFuse\n");
    }

    /* Check specific slot */
    if (!bflb_efuse_is_mac_address_slot_empty(0, 1)) {
        bflb_efuse_read_mac_address_opt(0, mac, 1);
        printf("Slot 0 MAC: %02X:%02X:%02X:%02X:%02X:%02X\n",
               mac[0], mac[1], mac[2], mac[3], mac[4], mac[5]);
    }
}
```

### Program MAC Address (One-Time Write)

```c
#include "bflb_efuse.h"

int program_mac_demo(void)
{
    uint8_t mac[6] = { 0xA8, 0x5B, 0x78, 0x9C, 0xDE, 0xF0 };

    /* Check if slot is empty first */
    if (!bflb_efuse_is_mac_address_slot_empty(0, 1)) {
        printf("Slot 0 already has data!\n");
        return -1;
    }

    /* Program MAC address (program=1 actually blows the fuses) */
    int ret = bflb_efuse_write_mac_address_opt(0, mac, 1);
    if (ret != 0) {
        printf("Failed to program MAC address\n");
        return ret;
    }

    printf("MAC address programmed successfully\n");
    return 0;
}
```

### Use ADC Factory Trim

```c
#include "bflb_efuse.h"
#include "bflb_adc.h"

void adc_calibrated_read(void)
{
    /* Get ADC trim values from eFuse */
    float adc_trim = bflb_efuse_get_adc_trim();
    uint32_t tsen_trim = bflb_efuse_get_adc_tsen_trim();

    printf("ADC trim coefficient: %.4f\n", adc_trim);
    printf("Temperature sensor trim: %u\n", tsen_trim);

    /* Apply trim to ADC readings in your application */
}
```

### Secure Boot Configuration

```c
#include "bflb_efuse.h"

void secure_boot_setup(void)
{
    uint8_t sign_type, aes_type;

    /* Read current secure boot config */
    bflb_efuse_read_secure_boot(&sign_type, &aes_type);
    printf("Secure boot: sign=%u, aes=%u\n", sign_type, aes_type);

    /* Enable AES-256 for flash encryption */
    /* Note: This is a one-time programmable operation */
    int ret = bflb_efuse_enable_aes(3, 0);  /* AES-256, non-XTS mode */
    if (ret == 0) {
        printf("AES enabled in eFuse\n");
    }

    /* Lock AES key access after programming */
    bflb_efuse_rw_lock_aes_key(0, 1, 1);  /* Lock read and write for key 0 */
}
```

---

## Register-Level Reference

eFuse controller registers are at `EF_CTRL_BASE = 0x20056000`:

| Offset | Register | Description |
|--------|----------|-------------|
| `0x800` | EF_IF_CTRL_0 | Interface control (busy, RW, trigger, auto-load) |
| `0x804` | EF_IF_CTRL_1 | Interface control 1 |
| `0x808` | EF_IF_STATUS_0 | Status register |
| `0x80C` | EF_IF_STATUS_1 | Status register 1 |
| `0x810` | EF_IF_SHIFT | eFuse read shift register |
| `0x814` | EF_IF_CK_DIV | Clock division for programming |
| `0x1000+` | EF_DATA_BASE | eFuse array data (bit-level storage) |

### Key EF_CTRL Interface Bits

```c
/* EF_IF_CTRL_0 (offset 0x800) */
#define EF_CTRL_EF_IF_0_AUTOLOAD_P1_DONE   /* Auto-load phase 1 done */
#define EF_CTRL_EF_IF_0_AUTOLOAD_DONE       /* Auto-load complete */
#define EF_CTRL_EF_IF_0_BUSY                 /* Interface busy flag */
#define EF_CTRL_EF_IF_0_RW                   /* 0=read, 1=write */
#define EF_CTRL_EF_IF_0_TRIG                 /* Trigger operation */
#define EF_CTRL_EF_IF_0_MANUAL_EN             /* Manual mode enable */
#define EF_CTRL_EF_IF_0_CYC_MODIFY            /* Modify timing */
#define EF_CTRL_EF_IF_0_PROT_CODE_CTRL       /* Protection code */
#define EF_CTRL_EF_IF_0_POR_DIG               /* Power-on reset */
#define EF_CTRL_EF_IF_0_AUTO_RD_EN           /* Auto-read enable */
#define EF_CTRL_EF_IF_0_CYC_MODIFY_LOCK       /* Lock timing config */
```

### eFuse Read Procedure (Low-Level)

```c
void bflb_ef_ctrl_read_direct(struct bflb_device_s *dev,
                               uint32_t offset,   // eFuse word address
                               uint32_t *pword,   // output buffer
                               uint32_t count,    // word count
                               uint8_t reload);   // force re-read
```

### eFuse Write Procedure (Low-Level)

```c
void bflb_ef_ctrl_write_direct(struct bflb_device_s *dev,
                                uint32_t offset,
                                uint32_t *pword,
                                uint32_t count,
                                uint8_t program);  // 1=actually program
```

> **Warning:** eFuse programming is **irreversible**. Writing `1` to a fuse bit blows the fuse permanently. Always read back and verify before programming. The eFuse controller handles the high-voltage programming pulses internally — do not exceed timing parameters.

### eFuse Layout (Logical)

The eFuse array contains several reserved and user-programmable regions:

| Address Range | Content |
|---------------|---------|
| `0x00` - `0x0F` | Reserved / Chip ID |
| `0x10` - `0x17` | MAC address slots |
| `0x18` - `0x1F` | AES keys (0-3) |
| `0x20` - `0x27` | Reserved |
| `0x28` - `0x2F` | Security configuration |
| `0x30` - `0xFF` | ADC/DAC trim, calibration data |
| `0x100`+ | User-programmable region |

> **Note:** The exact eFuse bit map is chip-specific. Always refer to the BL616/BL618 datasheet for the complete eFuse map and programming specifications.
