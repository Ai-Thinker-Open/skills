# CKS API Reference (BL616/BL618)

> **Source:** `bouffalo_sdk/drivers/lhal/include/bflb_cks.h`  
> **Implementation:** `bouffalo_sdk/drivers/lhal/src/bflb_cks.c`  
> **Register Header:** `bouffalo_sdk/drivers/lhal/include/hardware/cks_reg.h`

## Overview

The CKS (Clock Security System / Checksum) module provides hardware checksum computation. It is a simple byte-by-byte accumulation checksum engine supporting configurable endianness (byte swap), suitable for fast data integrity verification.

**Key Features:**
- Hardware byte-by-byte accumulation checksum
- Configurable endianness (Little-Endian / Big-Endian)
- 16-bit checksum output
- ROM API invocation support (supports `romapi_` fast path)

## Base Address

| Peripheral | Base Address |
|------------|-------------|
| CKS | `0x2000A700` |

---

## Endianness Definitions

```c
#define CKS_LITTLE_ENDIAN 0   // Little-endian mode
#define CKS_BIG_ENDIAN    1   // Big-endian mode
```

---

## LHAL API Functions

### bflb_cks_reset

Reset the checksum module (clear internal accumulator).

```c
void bflb_cks_reset(struct bflb_device_s *dev);
```

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `dev` | `struct bflb_device_s *` | Device handle |

**Note:** Writes 1 to the `CKS_CR_CKS_CLR` bit of the `CKS_CONFIG` register to clear the accumulator state.

---

### bflb_cks_set_endian

Set the checksum byte order (endianness mode).

```c
void bflb_cks_set_endian(struct bflb_device_s *dev, uint8_t endian);
```

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `dev` | `struct bflb_device_s *` | Device handle |
| `endian` | `uint8_t` | Byte order: `CKS_LITTLE_ENDIAN` (0) or `CKS_BIG_ENDIAN` (1) |

**Note:** Controls the `CKS_CR_CKS_BYTE_SWAP` bit (bit 1).

---

### bflb_cks_compute

Perform hardware checksum computation on a data buffer.

```c
uint16_t bflb_cks_compute(struct bflb_device_s *dev, uint8_t *data, uint32_t length);
```

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `dev` | `struct bflb_device_s *` | Device handle |
| `data` | `uint8_t *` | Pointer to input data buffer |
| `length` | `uint32_t` | Data length (in bytes) |

**Returns:** `uint16_t` — 16-bit checksum value

**Note:** Writes data byte by byte into the `CKS_DATA_IN` register, the hardware automatically accumulates, and finally reads the lower 16 bits of the result from the `CKS_OUT` register.

---

## Usage Examples

### Example 1: Basic Checksum Computation

```c
#include "bflb_cks.h"

void cks_basic_example(void)
{
    struct bflb_device_s *cks;

    // Get CKS device handle
    cks = bflb_device_get_by_name("cks");

    // Set little-endian byte order
    bflb_cks_set_endian(cks, CKS_LITTLE_ENDIAN);

    // Data to be verified
    uint8_t data[] = {0x12, 0x34, 0x56, 0x78, 0x9A, 0xBC, 0xDE, 0xF0};

    // Compute checksum
    uint16_t checksum = bflb_cks_compute(cks, data, sizeof(data));
    printf("Checksum: 0x%04X\n", checksum);
}
```

### Example 2: Multi-Block Accumulation Checksum

```c
#include "bflb_cks.h"

void cks_accumulate_example(void)
{
    struct bflb_device_s *cks;
    cks = bflb_device_get_by_name("cks");

    bflb_cks_set_endian(cks, CKS_BIG_ENDIAN);

    // Reset accumulator
    bflb_cks_reset(cks);

    // Accumulate in blocks
    uint8_t block1[] = {0x01, 0x02, 0x03, 0x04};
    uint8_t block2[] = {0x05, 0x06, 0x07, 0x08};

    bflb_cks_compute(cks, block1, sizeof(block1)); // Accumulate block1
    bflb_cks_compute(cks, block2, sizeof(block2)); // Accumulate block2

    // Note: compute returns the accumulated result; call reset first to start over
}
```

### Example 3: Firmware Integrity Verification

```c
#include "bflb_cks.h"

bool verify_firmware_checksum(uint8_t *fw_data, uint32_t fw_len, uint16_t expected_cks)
{
    struct bflb_device_s *cks;
    cks = bflb_device_get_by_name("cks");

    bflb_cks_set_endian(cks, CKS_LITTLE_ENDIAN);

    uint16_t actual = bflb_cks_compute(cks, fw_data, fw_len);

    if (actual == expected_cks) {
        printf("Firmware checksum OK: 0x%04X\n", actual);
        return true;
    } else {
        printf("Checksum mismatch! Expected: 0x%04X, Got: 0x%04X\n",
               expected_cks, actual);
        return false;
    }
}
```

---

## Register-Level Reference

### CKS Register Offsets

| Offset | Register | Description |
|--------|----------|-------------|
| `0x00` | `CKS_CONFIG` | Control register |
| `0x04` | `CKS_DATA_IN` | Data input register |
| `0x08` | `CKS_OUT` | Checksum output register |

### Register Bitfields

#### CKS_CONFIG (0x00)

| Bit(s) | Field | Description |
|--------|-------|-------------|
| 0 | `CKS_CR_CKS_CLR` | Write 1 to clear accumulator |
| 1 | `CKS_CR_CKS_BYTE_SWAP` | Byte order swap: 0=little-endian, 1=big-endian |

```c
#define CKS_CR_CKS_CLR          (1<<0U)
#define CKS_CR_CKS_BYTE_SWAP    (1<<1U)
```

#### CKS_DATA_IN (0x04)

| Bit(s) | Field | Description |
|--------|-------|-------------|
| 7:0 | `CKS_DATA_IN` | 8-bit data input (write triggers accumulation) |

```c
#define CKS_DATA_IN_SHIFT       (0U)
#define CKS_DATA_IN_MASK        (0xff<<CKS_DATA_IN_SHIFT)
```

#### CKS_OUT (0x08)

| Bit(s) | Field | Description |
|--------|-------|-------------|
| 15:0 | `CKS_OUT` | 16-bit checksum output |

```c
#define CKS_OUT_SHIFT           (0U)
#define CKS_OUT_MASK            (0xffff<<CKS_OUT_SHIFT)
```

### Direct Register Access Example

```c
#include "hardware/cks_reg.h"

// CKS base address: 0x2000A700
#define CKS_BASE_ADDR   0x2000A700

void cks_direct_example(uint8_t *data, uint32_t len)
{
    uint32_t cks_config = CKS_BASE_ADDR + CKS_CONFIG_OFFSET;   // 0x2000A700
    uint32_t cks_data_in = CKS_BASE_ADDR + CKS_DATA_IN_OFFSET; // 0x2000A704
    uint32_t cks_out     = CKS_BASE_ADDR + CKS_OUT_OFFSET;     // 0x2000A708

    // Clear accumulator
    uint32_t regval = *(volatile uint32_t *)cks_config;
    regval |= CKS_CR_CKS_CLR;
    *(volatile uint32_t *)cks_config = regval;

    // Set little-endian mode (clear bit 1)
    regval &= ~CKS_CR_CKS_BYTE_SWAP;
    *(volatile uint32_t *)cks_config = regval;

    // Input data byte by byte
    for (uint32_t i = 0; i < len; i++) {
        *(volatile uint32_t *)cks_data_in = data[i];
    }

    // Read checksum
    uint16_t result = (uint16_t)(*(volatile uint32_t *)cks_out & 0xFFFF);
    printf("Direct checksum: 0x%04X\n", result);
}
```
