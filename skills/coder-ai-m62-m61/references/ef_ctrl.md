# EF_CTRL (eFuse Controller) API Reference (BL616/BL618)

> **Source:** `bouffalo_sdk/drivers/lhal/include/bflb_ef_ctrl.h`  
> **Implementation:** `bouffalo_sdk/drivers/lhal/src/bflb_ef_ctrl.c`  
> **Register Header:** `bouffalo_sdk/drivers/soc/bl616/std/include/hardware/ef_ctrl_reg.h`  
> **Chip Support:** BL602, BL702/BL702L, BL616/BL616CL, BL618DG

## Overview

The EF_CTRL (eFuse Controller) module provides read/write control interfaces for the chip's eFuse (one-time programmable memory). The eFuse is used to store immutable information such as factory calibration data, security keys, and function configuration bits. The controller offers two operating modes—automatic mode and manual mode—and supports two data access abstractions: direct read/write and common trim (general calibration parameters).

**Key Features:**
- Direct mode: Raw eFuse data read/write based on offset
- Common Trim mode: Name-based calibration parameter read/write (e.g., ADC trim, voltage trim, etc.)
- Auto-load detection (Auto-Load Done)
- eFuse programming (burning) support
- Multi-Region support (some chips have Region 0 and Region 1)
- Configurable timing parameters
- Busy state detection
- Utility functions: parity calculation, bit detection, zero count

---

## Base Address

| Chip | EF_CTRL Base Address | eFuse Region 0 Size | eFuse Region 1 Size |
|------|---------------|-------------------|-------------------|
| BL616 | `0x20056000` | 512 bytes (16×32-bit) | — |
| BL618DG (A0) | `0x2000C000` | 256 bytes (8×32-bit) | — |
| BL618DG (non-A0) | `0x2000C000` | 256 bytes | 256 bytes |
| BL616CL | `0x20056000` | 128 bytes (4×32-bit) | — |
| BL702/BL702L | `0x40007000` | 128 bytes | — |
| BL602 | `0x40007000` | 128 bytes | — |

---

## Data Types

### bflb_ef_ctrl_com_trim_cfg_t

eFuse Common Trim configuration descriptor (for trim list).

```c
typedef struct {
    char *name;           /* trim name */
    uint16_t en_addr;     /* enable bit address (bit offset) */
    uint16_t parity_addr; /* parity bit address (bit offset) */
    uint16_t value_addr;  /* value bit address (bit offset) */
    uint16_t value_len;   /* value bit length */
} bflb_ef_ctrl_com_trim_cfg_t;
```

---

### bflb_ef_ctrl_com_trim_t

eFuse Common Trim data (returned after reading by name).

```c
typedef struct {
    uint8_t en;     /* Enable status */
    uint8_t parity; /* Trim parity bit */
    uint8_t empty;  /* Whether trim is empty */
    uint8_t len;    /* Trim value bit length */
    uint32_t value; /* Trim value */
} bflb_ef_ctrl_com_trim_t;
```

---

### bflb_ef_ctrl_para_t

eFuse controller timing parameters (for timing adjustment during read/write).

```c
typedef struct {
    uint16_t pd_1st;   /* settling time */
    uint16_t pd_cs_s;  /* CS setup time (>500ns) */
    uint16_t cs;       /* CS width (>6.6ns) */
    uint16_t rd_adr;   /* address read time (>6.3ns) */
    uint16_t rd_dat;   /* data read time (>199ns) */
    uint16_t rd_dmy;   /* dummy cycle (>14.9ns) */
    uint16_t pd_cs_h;  /* CS hold time (>1ns) */
    uint16_t ps_cs;    /* CS interval (>50ns) */
    uint16_t wr_adr;   /* address write time (>6.3ns) */
    uint16_t pp;       /* programming pulse width (>11-13us) */
    uint16_t pi;       /* programming interval (>14.9ns) */
} bflb_ef_ctrl_para_t;
```

---

## AES Encryption Mode Macros

BL616CL / BL618DG only:

```c
#define EF_CTRL_SF_AES_NONE  (0)  /* No AES encryption */
#define EF_CTRL_SF_AES_128   (1)  /* AES-128 */
#define EF_CTRL_SF_AES_192   (2)  /* AES-192 */
#define EF_CTRL_SF_AES_256   (3)  /* AES-256 */
```

---

## API Functions

### 1. Trim List and Auto-Load

#### bflb_ef_ctrl_get_common_trim_list

Get the eFuse Common Trim configuration list.

```c
uint32_t bflb_ef_ctrl_get_common_trim_list(const bflb_ef_ctrl_com_trim_cfg_t **trim_list);
```

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `trim_list` | `const bflb_ef_ctrl_com_trim_cfg_t **` | Output: pointer to trim list |

**Returns:** Number of entries in the trim list

**Description:** Returns the list of eFuse trim parameters supported by the chip (such as ADC offset, bandgap trim, LDO trim, etc.). This list is used by `bflb_ef_ctrl_read_common_trim()` and `bflb_ef_ctrl_write_common_trim()` for name-based indexing.

---

#### bflb_ef_ctrl_autoload_done

Check whether eFuse auto-load has completed.

```c
int bflb_ef_ctrl_autoload_done(struct bflb_device_s *dev);
```

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `dev` | `struct bflb_device_s *` | eFuse device handle |

**Returns:**

| Return Value | Description |
|--------|------|
| `1` | Auto-load completed |
| `0` | Auto-load not completed |

**Description:** After system power-up, the eFuse controller automatically loads eFuse data into the Shadow Register. This function checks the `EF_CTRL_EF_IF_0_AUTOLOAD_DONE_MASK` status bit.

---

### 2. Timing Parameters

#### bflb_ef_ctrl_set_para

Set the read/write timing parameters of the eFuse controller.

```c
int bflb_ef_ctrl_set_para(bflb_ef_ctrl_para_t *para);
```

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `para` | `bflb_ef_ctrl_para_t *` | Pointer to timing parameter struct |

**Returns:** `0` on success

**Description:** Writes timing parameters to the `EF_IF_CYC_0` and `EF_IF_CYC_1` registers for adjusting eFuse programming/read timing. BL616 uses default parameters; BL616CL dynamically calculates the `pp` value based on system clock.

---

### 3. Direct Read/Write

#### bflb_ef_ctrl_write_direct

Directly write eFuse data (optionally program/burn).

```c
void bflb_ef_ctrl_write_direct(struct bflb_device_s *dev, uint32_t offset, uint32_t *pword, uint32_t count, uint8_t program);
```

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `dev` | `struct bflb_device_s *` | eFuse device handle |
| `offset` | `uint32_t` | eFuse write offset address (bytes) |
| `pword` | `uint32_t *` | Data buffer to write (word-aligned) |
| `count` | `uint32_t` | Number of words to write |
| `program` | `uint8_t` | `1` = write Shadow Register and program to eFuse; `0` = write Shadow Register only |

**Description:** 
- Executed under interrupt protection
- Automatically handles cross-Region writes
- When `program=1`, executes the full programming flow (power-up → program → wait busy → power-down)
- Automatically calls `bflb_ef_ctrl_update_para()` to update timing parameters
- Boundary check: if out of range and `program=1`, only triggers the programming operation

---

#### bflb_ef_ctrl_read_direct

Directly read eFuse data.

```c
void bflb_ef_ctrl_read_direct(struct bflb_device_s *dev, uint32_t offset, uint32_t *pword, uint32_t count, uint8_t reload);
```

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `dev` | `struct bflb_device_s *` | eFuse device handle |
| `offset` | `uint32_t` | eFuse read offset address (bytes) |
| `pword` | `uint32_t *` | Read data buffer (word-aligned) |
| `count` | `uint32_t` | Number of words to read |
| `reload` | `uint8_t` | `1` = reload from eFuse before reading; `0` = read from Shadow Register |

**Description:**
- Executed under interrupt protection
- Automatically handles cross-Region reads
- When `reload=1`, triggers the full Load flow and waits for auto-load done
- When `reload=0`, switches to AHB Clock only and reads directly
- Automatically calls `bflb_ef_ctrl_update_para()` to update timing parameters

---

### 4. Common Trim Read/Write

#### bflb_ef_ctrl_read_common_trim

Read eFuse Common Trim parameters by name.

```c
void bflb_ef_ctrl_read_common_trim(struct bflb_device_s *dev, char *name, bflb_ef_ctrl_com_trim_t *trim, uint8_t reload);
```

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `dev` | `struct bflb_device_s *` | eFuse device handle |
| `name` | `char *` | Trim parameter name (string match) |
| `trim` | `bflb_ef_ctrl_com_trim_t *` | Output: read trim data |
| `reload` | `uint8_t` | `1` = reload; `0` = read Shadow Register directly |

**Description:**
- Obtains trim list via `bflb_ef_ctrl_get_common_trim_list()`
- Searches for the matching trim config by exact `name` string match
- Automatically parses the value field across 32-bit boundaries (supports 64-bit concatenation)
- Reads en, parity, value bit segments and determines empty status
- Executed under interrupt protection

---

#### bflb_ef_ctrl_write_common_trim

Write eFuse Common Trim parameters by name.

```c
void bflb_ef_ctrl_write_common_trim(struct bflb_device_s *dev, char *name, uint32_t value, uint8_t program);
```

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `dev` | `struct bflb_device_s *` | eFuse device handle |
| `name` | `char *` | Trim parameter name |
| `value` | `uint32_t` | Trim value to write |
| `program` | `uint8_t` | `1` = program to eFuse (one-time); `0` = write Shadow Register only |

**Description:**
- Automatically calculates and writes the parity bit
- Sets the enable bit to mark the trim as valid
- Handles value writes across 32-bit boundaries
- When `program=1`, executes the eFuse programming flow (power-up → program → wait → power-down)
- Executed under interrupt protection

---

### 5. Status and Utility Functions

#### bflb_ef_ctrl_busy

Check whether eFuse Region 0 is busy.

```c
int bflb_ef_ctrl_busy(struct bflb_device_s *dev);
```

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `dev` | `struct bflb_device_s *` | eFuse device handle |

**Returns:**

| Return Value | Description |
|--------|------|
| `1` | eFuse busy |
| `0` | eFuse idle |

**Description:** Checks the `EF_CTRL_EF_IF_0_BUSY_MASK` status bit. After programming, you must wait for busy to clear.

---

#### bflb_ef_ctrl_busy_r1

Check whether eFuse Region 1 is busy.

```c
int bflb_ef_ctrl_busy_r1(struct bflb_device_s *dev);
```

> ⚠️ **Condition:** Only available for `BL618DG && !CPU_MODEL_A0`

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `dev` | `struct bflb_device_s *` | eFuse device handle |

**Returns:**

| Return Value | Description |
|--------|------|
| `1` | eFuse Region 1 busy |
| `0` | eFuse Region 1 idle |

---

#### bflb_ef_ctrl_is_all_bits_zero

Check whether a specified bit segment within a value is all zeros.

```c
uint8_t bflb_ef_ctrl_is_all_bits_zero(uint32_t val, uint8_t start, uint8_t len);
```

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `val` | `uint32_t` | Value to check |
| `start` | `uint8_t` | Start bit position |
| `len` | `uint8_t` | Bit length to check |

**Returns:** `1` = all zeros, `0` = non-zero bits present

---

#### bflb_ef_ctrl_get_byte_zero_cnt

Count the number of zero bits in a byte.

```c
uint32_t bflb_ef_ctrl_get_byte_zero_cnt(uint8_t val);
```

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `val` | `uint8_t` | Byte to count |

**Returns:** Number of zero bits (0-8)

---

#### bflb_ef_ctrl_get_trim_parity

Calculate the parity bit for a Trim value.

```c
uint8_t bflb_ef_ctrl_get_trim_parity(uint32_t val, uint8_t len);
```

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `val` | `uint32_t` | Trim value |
| `len` | `uint8_t` | Bit length for parity calculation |

**Returns:** Odd parity bit (0 or 1) — LSB of the count of 1s

**Description:** Counts the number of 1s in bits `[0, len)` of `val` and returns the LSB. Used to auto-fill the parity bit during eFuse trim writes.

---

## Register Reference

### Region 0 Control Register (BL616: offset 0x800 from base)

**`EF_CTRL_EF_IF_CTRL_0` (0x800)**

| Bits | Field | Description |
|------|-------|-------------|
| 0 | `AUTOLOAD_P1_DONE` | Phase 1 auto-load complete |
| 1 | `AUTOLOAD_DONE` | Auto-load complete |
| 2 | `BUSY` | eFuse busy status |
| 3 | `RW` | Read/write select (0=read, 1=write) |
| 4 | `TRIG` | Trigger operation |
| 5 | `MANUAL_EN` | Manual mode enable (0=auto mode) |
| 6 | `CYC_MODIFY` | Timing parameter modify enable |
| 8-15 | `PROT_CODE_CTRL` | Control register protection code (must write 0xBF) |
| 16 | `POR_DIG` | Digital POR control |
| 17 | `PCLK_FORCE_ON` | Force PCLK on |
| 18 | `AUTO_RD_EN` | Auto read enable |
| 19 | `CYC_MODIFY_LOCK` | Timing modify lock |
| 20 | `INT` | Interrupt status |
| 21 | `INT_CLR` | Interrupt clear |
| 22 | `INT_SET` | Interrupt set |
| 24-31 | `PROT_CODE_CYC` | Timing register protection code (must write 0xBF) |

### Timing Configuration Registers

**`EF_CTRL_EF_IF_CYC_0` (0x804)**

| Bits | Field | Description |
|------|-------|-------------|
| 0-5 | `RD_DMY` | Read dummy cycles |
| 6-11 | `RD_DAT` | Read data cycles |
| 12-17 | `RD_ADR` | Read address cycles |
| 18-23 | `CS` | CS signal width |
| 24-31 | `PD_CS_S` | CS setup time |

**`EF_CTRL_EF_IF_CYC_1` (0x808)**

| Bits | Field | Description |
|------|-------|-------------|
| 0-5 | `PI` | Programming interval |
| 6-13 | `PP` | Programming pulse width |
| 14-19 | `WR_ADR` | Write address cycles |
| 20-25 | `PS_CS` | CS interval |
| 26-31 | `PD_CS_H` | CS hold time |

### eFuse Configuration Register (BL616)

**`EF_CTRL_EF_IF_CFG_0` (0x814)**

| Bits | Field | Description |
|------|-------|-------------|
| 0-1 | `SF_AES_MODE` | AES encryption mode |
| 2 | `AI_DIS` | AI function disable |
| 3 | `CPU0_DIS` | CPU0 disable |
| 4-5 | `SBOOT_EN` | Secure Boot enable |
| 6-9 | `UART_DIS` | UART disable |
| 10 | `BUS_RMP_SW_EN` | Bus Remap software enable |
| 11 | `BUS_RMP_DIS` | Bus Remap disable |
| 12-13 | `SF_KEY_RE_SEL` | Flash Key Region select |
| 14 | `SDU_DIS` | SDU disable |
| 15 | `BTDM_DIS` | BTDM disable |
| 16 | `WIFI_DIS` | WiFi disable |
| 17 | `KEY_ENC_EN` | Key encryption enable |
| 18 | `CAM_DIS` | Camera disable |
| 19 | `M154_DIS` | 802.15.4 disable |
| 20 | `CPU1_DIS` | CPU1 (NP) disable |
| 21 | `CPU_RST_DBG_DIS` | CPU Reset Debug disable |
| 22 | `SE_DBG_DIS` | SE Debug disable |
| 23 | `EFUSE_DBG_DIS` | eFuse Debug disable |
| 24-25 | `DBG_JTAG_1_DIS` | JTAG1 Debug disable |
| 26-27 | `DBG_JTAG_0_DIS` | JTAG0 Debug disable |
| 28-31 | `DBG_MODE` | Debug mode |

---

## Usage Examples

### Example 1: Check eFuse Auto-Load Status

```c
#include "bflb_ef_ctrl.h"
#include "bflb_core.h"

void wait_efuse_autoload(void)
{
    struct bflb_device_s *ef_ctrl;
    
    ef_ctrl = bflb_device_get_by_name("ef_ctrl");
    
    // Poll until eFuse auto-load completes
    while (!bflb_ef_ctrl_autoload_done(ef_ctrl)) {
        bflb_mtimer_delay_ms(1);
    }
    
    printf("eFuse auto-load complete\n");
}
```

### Example 2: Read eFuse Raw Data

```c
#include "bflb_ef_ctrl.h"

void read_efuse_raw_data(void)
{
    struct bflb_device_s *ef_ctrl;
    uint32_t efuse_data[4];  // BL616 R0 = 512 bytes = 128 words
    
    ef_ctrl = bflb_device_get_by_name("ef_ctrl");
    
    // Read first 4 words (offset 0, 16 bytes)
    bflb_ef_ctrl_read_direct(ef_ctrl, 0, efuse_data, 4, 1);
    
    printf("eFuse[0x00]: 0x%08lx\n", efuse_data[0]);
    printf("eFuse[0x04]: 0x%08lx\n", efuse_data[1]);
    printf("eFuse[0x08]: 0x%08lx\n", efuse_data[2]);
    printf("eFuse[0x0C]: 0x%08lx\n", efuse_data[3]);
}
```

### Example 3: Read Common Trim Parameters

```c
#include "bflb_ef_ctrl.h"

void read_adc_trim(void)
{
    struct bflb_device_s *ef_ctrl;
    bflb_ef_ctrl_com_trim_t trim;
    
    ef_ctrl = bflb_device_get_by_name("ef_ctrl");
    
    // Read ADC offset trim by name (actual name depends on chip trim list)
    bflb_ef_ctrl_read_common_trim(ef_ctrl, "adc_offset", &trim, 1);
    
    if (!trim.empty) {
        printf("ADC Offset Trim:\n");
        printf("  Enabled: %d\n", trim.en);
        printf("  Parity:  %d\n", trim.parity);
        printf("  Value:   0x%lx (%lu)\n", trim.value, trim.value);
        printf("  Length:  %d bits\n", trim.len);
    } else {
        printf("ADC Offset Trim is empty (not programmed)\n");
    }
}
```

### Example 4: Iterate All Common Trim Parameters

```c
#include "bflb_ef_ctrl.h"

void list_all_trims(void)
{
    struct bflb_device_s *ef_ctrl;
    const bflb_ef_ctrl_com_trim_cfg_t *trim_list;
    uint32_t trim_count;
    
    ef_ctrl = bflb_device_get_by_name("ef_ctrl");
    
    // Get trim list
    trim_count = bflb_ef_ctrl_get_common_trim_list(&trim_list);
    
    printf("Total %lu common trim parameters:\n", trim_count);
    
    for (uint32_t i = 0; i < trim_count; i++) {
        bflb_ef_ctrl_com_trim_t trim;
        
        bflb_ef_ctrl_read_common_trim(ef_ctrl, trim_list[i].name, &trim, 0);
        
        printf("  [%lu] %-20s en=%d parity=%d empty=%d len=%d value=0x%lx\n",
               i, trim_list[i].name, trim.en, trim.parity, 
               trim.empty, trim.len, trim.value);
    }
}
```

### Example 5: Write and Program eFuse (Development/Factory Use Only)

```c
#include "bflb_ef_ctrl.h"

int program_efuse_example(void)
{
    struct bflb_device_s *ef_ctrl;
    uint32_t write_data[1] = { 0x12345678 };
    
    ef_ctrl = bflb_device_get_by_name("ef_ctrl");
    
    // ⚠️ Warning: eFuse is one-time programmable memory; programming cannot be undone!

    // Check if eFuse is busy first
    if (bflb_ef_ctrl_busy(ef_ctrl)) {
        printf("eFuse is busy, cannot program now\n");
        return -1;
    }
    
    // Write Shadow Register and program to eFuse (offset=0x20, 1 word)
    bflb_ef_ctrl_write_direct(ef_ctrl, 0x20, write_data, 1, 1);
    
    // Wait for programming to complete
    uint32_t timeout = 100000;
    while (bflb_ef_ctrl_busy(ef_ctrl)) {
        timeout--;
        if (timeout == 0) {
            printf("eFuse program timeout!\n");
            return -1;
        }
        bflb_mtimer_delay_us(10);
    }
    
    // Verify write
    uint32_t verify_data[1] = { 0 };
    bflb_ef_ctrl_read_direct(ef_ctrl, 0x20, verify_data, 1, 1);
    
    if (verify_data[0] == write_data[0]) {
        printf("eFuse program and verify OK\n");
        return 0;
    } else {
        printf("eFuse verify failed: wrote 0x%lx, read 0x%lx\n",
               write_data[0], verify_data[0]);
        return -1;
    }
}
```

### Example 6: Parity Utility Functions

```c
#include "bflb_ef_ctrl.h"

void parity_example(void)
{
    uint32_t value = 0xA5;  // Binary: 1010 0101, 4 ones
    
    // Calculate odd parity
    uint8_t parity = bflb_ef_ctrl_get_trim_parity(value, 8);
    printf("Value 0x%02lx: parity=%d\n", value, parity);
    // Output: parity=0 (even number of ones)
    
    uint32_t value2 = 0x07;  // Binary: 0000 0111, 3 ones
    parity = bflb_ef_ctrl_get_trim_parity(value2, 8);
    printf("Value 0x%02lx: parity=%d\n", value2, parity);
    // Output: parity=1 (odd number of ones, LSB of count)
    
    // Check if specific bit segment is all zero
    uint8_t all_zero = bflb_ef_ctrl_is_all_bits_zero(0x00FF0000, 16, 8);
    printf("Bits [23:16] all zero: %d\n", all_zero);
    // Output: 1 (true)
    
    // Count zero bits
    uint32_t zero_cnt = bflb_ef_ctrl_get_byte_zero_cnt(0xF0);
    printf("0xF0 has %lu zero bits\n", zero_cnt);
    // Output: 4
}
```

---

## Notes

1. **One-Time Programming:** eFuse is one-time programmable memory. Bits can only be programmed from 0 to 1 and cannot be restored from 1 to 0. Exercise caution with programming operations.

2. **Protection Code:** Modifying eFuse control registers requires writing the protection code `0xBF` to the `PROT_CODE_CTRL` and `PROT_CODE_CYC` bit segments to prevent accidental operation.

3. **Interrupt Protection:** All read/write and programming functions are executed under `bflb_irq_save()` / `bflb_irq_restore()` protection to ensure atomicity.

4. **Region Support:** BL616 has only Region 0 (512 bytes). BL618DG non-A0 versions have Region 0 and Region 1. Cross-Region read/write is handled automatically.

5. **Shadow Register:** When `program=0` or `reload=0`, operations target the Shadow Register (cached copy) and will not trigger actual eFuse hardware operations. This is fast but lost on power-down. After power-up, wait for Auto-Load Done.

6. **TCM Section:** All API functions are located in TCM section (`ATTR_TCM_SECTION`), ensuring they are not affected by Flash access latency during execution.

7. **ROM API:** Functions internally prioritize calling ROM API (`romapi_bflb_ef_ctrl_*`) to reduce code size.

| Operation Mode | Parameter Setting | Use Case |
|---------|---------|---------|
| Read only, no reload | `reload=0` | Auto-load already completed; fast read |
| Read + reload | `reload=1` | Uncertain state; ensures reading latest data |
| Write only, no programming | `program=0` | Pre-write, program later in batch |
| Write + program | `program=1` | Directly burn to eFuse (one-time) |
