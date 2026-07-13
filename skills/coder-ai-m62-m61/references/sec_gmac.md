# Security GMAC API Reference (BL616/BL618)

> **Source:** `bouffalo_sdk/drivers/lhal/include/bflb_sec_gmac.h`  
> **Implementation:** `bouffalo_sdk/drivers/lhal/src/bflb_sec_gmac.c`  
> **Register Header:** `bouffalo_sdk/drivers/lhal/include/hardware/sec_eng_reg.h`

## Overview

The Security GMAC (Galois Message Authentication Code) is a hardware accelerator within the SEC_ENG (Security Engine) module. It computes the GHASH-based message authentication tag as defined in GCM (Galois/Counter Mode) of AES. The GMAC engine uses a link-mode architecture where the caller provides a link configuration structure in memory, and the hardware performs the GHASH computation via DMA.

GMAC produces a 128-bit (16-byte) authentication tag. It operates on 128-bit blocks and requires input data to be 16-byte aligned.

The GMAC is a shared resource managed through the SEC_ENG's group protection mechanism. Before using GMAC, the caller must request access via `bflb_group0_request_gmac_access()` or `bflb_group1_request_gmac_access()`, and release it after use.

**Common Use Cases:**
- AES-GCM authenticated encryption (tag verification)
- Message integrity verification
- Key derivation with GHASH

## Base Address

| Peripheral | Base Address |
|------------|-------------|
| SEC_ENG | `0x20004000` |
| GMAC (within SEC_ENG) | `SEC_ENG_BASE + 0x500` |

---

## Configuration Structure

### bflb_sec_gmac_link_s

Link-mode configuration structure for GMAC operations. Must be placed in a memory region accessible by the SEC_ENG DMA. **Must be 4-byte aligned.**

```c
struct bflb_sec_gmac_link_s {
    uint32_t                : 9;   /*!< [8:0] reserved */
    uint32_t gmac_int_clear : 1;   /*!< [9] Clear interrupt */
    uint32_t gmac_int_set   : 1;   /*!< [10] Set interrupt */
    uint32_t                : 5;   /*!< [15:11] reserved */
    uint32_t gmac_msg_len   : 16;  /*!< [31:16] Number of 128-bit blocks */
    uint32_t gmac_src_addr;        /*!< Message source address */
    uint32_t gmac_key0;            /*!< GMAC key word 0 */
    uint32_t gmac_key1;            /*!< GMAC key word 1 */
    uint32_t gmac_key2;            /*!< GMAC key word 2 */
    uint32_t gmac_key3;            /*!< GMAC key word 3 */
    uint32_t result[4];            /*!< Result of GMAC (128-bit tag) */
} __attribute__((aligned(4)));
```

**Field Descriptions:**

| Field | Offset | Description |
|-------|--------|-------------|
| `gmac_msg_len` | `+0 [31:16]` | Number of 128-bit (16-byte) blocks in the message |
| `gmac_src_addr` | `+4` | Physical address of the source message data |
| `gmac_key0` | `+8` | GMAC/HASH key word 0 (bits 31:0) |
| `gmac_key1` | `+12` | GMAC/HASH key word 1 (bits 63:32) |
| `gmac_key2` | `+16` | GMAC/HASH key word 2 (bits 95:64) |
| `gmac_key3` | `+20` | GMAC/HASH key word 3 (bits 127:96) |
| `result[4]` | `+24` | Result buffer: 4 × 32-bit words (128-bit GMAC tag) |

---

## LHAL API Functions

### bflb_sec_gmac_le_enable

Configure GMAC for little-endian mode. Clears the T_ENDIAN, H_ENDIAN, and X_ENDIAN bits so all data transfers use little-endian byte order.

```c
void bflb_sec_gmac_le_enable(struct bflb_device_s *dev);
```

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `dev` | `struct bflb_device_s *` | Device handle |

**Note:** Must be called before any GMAC operations if little-endian data format is used.

---

### bflb_sec_gmac_link_enable

Enable or disable the GMAC engine.

```c
void bflb_sec_gmac_link_enable(struct bflb_device_s *dev, uint8_t enable);
```

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `dev` | `struct bflb_device_s *` | Device handle |
| `enable` | `uint8_t` | `0` = disable, non-zero = enable |

---

### bflb_sec_gmac_link_work

Perform a GMAC link-mode operation: compute the GHASH authentication tag for the given message using the pre-configured link structure.

```c
int bflb_sec_gmac_link_work(struct bflb_device_s *dev, uint32_t addr, const uint8_t *in, uint32_t len, uint8_t *out);
```

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `dev` | `struct bflb_device_s *` | Device handle |
| `addr` | `uint32_t` | Physical address of the `bflb_sec_gmac_link_s` structure (must be word-aligned) |
| `in` | `const uint8_t *` | Pointer to input message data |
| `len` | `uint32_t` | Length of input data in bytes (must be multiple of 16) |
| `out` | `uint8_t *` | Output buffer for 16-byte GMAC tag |

**Returns:** `0` on success, `-EINVAL` if address not word-aligned or length not multiple of 16, `-ETIMEDOUT` on timeout.

**Behavior:**
1. Validates that `addr` is word-aligned and `len` is a multiple of 16
2. Sets the link configuration address in the GMAC LCA register
3. Updates the source address field in the link structure
4. Sets the message block count (`len / 16`) in the link structure
5. Triggers the GMAC engine via `SEC_ENG_SE_GMAC_0_TRIG_1T`
6. Polls the BUSY flag (with 100ms timeout)
7. Copies the 16-byte result from the link structure to the output buffer

**Example:**
```c
struct bflb_sec_gmac_link_s gmac_cfg __attribute__((aligned(4)));
uint8_t message[64];  // Must be 16-byte aligned
uint8_t tag[16];

// ... fill gmac_cfg with key and configure link ...

int ret = bflb_sec_gmac_link_work(dev, (uint32_t)&gmac_cfg, message, sizeof(message), tag);
```

---

### bflb_group0_request_gmac_access

Request GMAC access for security group 0. Must be called before using GMAC from group 0 context.

```c
int bflb_group0_request_gmac_access(struct bflb_device_s *dev);
```

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `dev` | `struct bflb_device_s *` | Device handle |

**Returns:** `0` on success, `-1` on failure (GMAC not available or already claimed).

---

### bflb_group1_request_gmac_access

Request GMAC access for security group 1.

```c
int bflb_group1_request_gmac_access(struct bflb_device_s *dev);
```

**Returns:** `0` on success, `-1` on failure.

---

### bflb_group0_release_gmac_access

Release GMAC access for security group 0. Call after GMAC operations are complete.

```c
void bflb_group0_release_gmac_access(struct bflb_device_s *dev);
```

---

### bflb_group1_release_gmac_access

Release GMAC access for security group 1.

```c
void bflb_group1_release_gmac_access(struct bflb_device_s *dev);
```

---

## Usage Examples

### Example 1: Basic GMAC Tag Computation

```c
#include "bflb_sec_gmac.h"
#include <string.h>

void gmac_basic_example(void)
{
    struct bflb_device_s *sec_eng;
    int ret;

    // GMAC link structure (must be 4-byte aligned, accessible by DMA)
    static struct bflb_sec_gmac_link_s gmac_cfg __attribute__((aligned(4)));

    // 128-bit GMAC key (derived from AES encrypt of zero-block)
    uint8_t gmac_key[16] = {
        0x00, 0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07,
        0x08, 0x09, 0x0a, 0x0b, 0x0c, 0x0d, 0x0e, 0x0f
    };

    // Message data (must be 16-byte aligned and length multiple of 16)
    static uint8_t message[32] __attribute__((aligned(16))) = {
        // 32 bytes of data to authenticate
    };

    uint8_t tag[16];

    sec_eng = bflb_device_get_by_name("sec_eng");

    // Initialize GMAC link structure
    memset(&gmac_cfg, 0, sizeof(gmac_cfg));
    memcpy(&gmac_cfg.gmac_key0, gmac_key, 16);

    // Request access
    ret = bflb_group0_request_gmac_access(sec_eng);
    if (ret != 0) {
        printf("Failed to acquire GMAC access\r\n");
        return;
    }

    // Enable little-endian mode
    bflb_sec_gmac_le_enable(sec_eng);

    // Enable GMAC engine
    bflb_sec_gmac_link_enable(sec_eng, 1);

    // Compute GMAC tag
    ret = bflb_sec_gmac_link_work(sec_eng, (uint32_t)&gmac_cfg,
                                   message, sizeof(message), tag);
    if (ret == 0) {
        printf("GMAC tag: ");
        for (int i = 0; i < 16; i++) {
            printf("%02x ", tag[i]);
        }
        printf("\r\n");
    }

    // Disable GMAC engine
    bflb_sec_gmac_link_enable(sec_eng, 0);

    // Release access
    bflb_group0_release_gmac_access(sec_eng);
}
```

### Example 2: AES-GCM Style Authentication

```c
// In AES-GCM, the GMAC key (H) is obtained by encrypting a zero-block with AES
// Then GMAC authenticates: AAD || ciphertext || len(AAD) || len(CT)
void gmac_aes_gcm_auth_example(void)
{
    struct bflb_device_s *sec_eng;
    static struct bflb_sec_gmac_link_s gmac_cfg __attribute__((aligned(4)));

    // H = AES_K(0^128) — assumed pre-computed
    uint8_t H[16] = { /* AES encrypt of zero block */ };

    // AAD + ciphertext as contiguous 16-byte aligned buffer
    static uint8_t auth_data[48] __attribute__((aligned(16)));
    uint8_t tag[16];

    sec_eng = bflb_device_get_by_name("sec_eng");

    memset(&gmac_cfg, 0, sizeof(gmac_cfg));
    memcpy(&gmac_cfg.gmac_key0, H, 16);

    bflb_group0_request_gmac_access(sec_eng);
    bflb_sec_gmac_le_enable(sec_eng);
    bflb_sec_gmac_link_enable(sec_eng, 1);

    int ret = bflb_sec_gmac_link_work(sec_eng, (uint32_t)&gmac_cfg,
                                       auth_data, sizeof(auth_data), tag);
    if (ret == 0) {
        // tag now contains the GHASH(H, AAD, C, len(AAD), len(C))
    }

    bflb_sec_gmac_link_enable(sec_eng, 0);
    bflb_group0_release_gmac_access(sec_eng);
}
```

### Example 3: Multi-Block Message Authentication

```c
void gmac_multiblock_example(void)
{
    struct bflb_device_s *sec_eng;
    static struct bflb_sec_gmac_link_s gmac_cfg __attribute__((aligned(4)));
    uint8_t gmac_key[16] = { /* 128-bit key */ };

    // Large message: 1024 bytes (64 × 128-bit blocks)
    static uint8_t large_msg[1024] __attribute__((aligned(16)));
    uint8_t tag[16];

    sec_eng = bflb_device_get_by_name("sec_eng");

    memset(&gmac_cfg, 0, sizeof(gmac_cfg));
    memcpy(&gmac_cfg.gmac_key0, gmac_key, 16);

    bflb_group0_request_gmac_access(sec_eng);
    bflb_sec_gmac_le_enable(sec_eng);
    bflb_sec_gmac_link_enable(sec_eng, 1);

    int ret = bflb_sec_gmac_link_work(sec_eng, (uint32_t)&gmac_cfg,
                                       large_msg, sizeof(large_msg), tag);

    bflb_sec_gmac_link_enable(sec_eng, 0);
    bflb_group0_release_gmac_access(sec_eng);
}
```

### Example 4: Check Result from Link Structure

```c
void gmac_check_result_direct(void)
{
    static struct bflb_sec_gmac_link_s gmac_cfg __attribute__((aligned(4)));

    // ... after calling bflb_sec_gmac_link_work() ...

    // Read result directly from link structure
    uint32_t tag_words[4];
    tag_words[0] = gmac_cfg.result[0];
    tag_words[1] = gmac_cfg.result[1];
    tag_words[2] = gmac_cfg.result[2];
    tag_words[3] = gmac_cfg.result[3];

    // Check against expected tag
    uint32_t expected[4] = {0xdeadbeef, 0xcafebabe, 0x12345678, 0x0fedcba9};
    if (memcmp(tag_words, expected, 16) == 0) {
        printf("GMAC tag verified\r\n");
    }
}
```

---

## Register-Level Reference

> The GMAC is part of the SEC_ENG peripheral. Direct register access is possible but the LHAL API is recommended for normal usage.

### GMAC Register Offsets (from SEC_ENG_BASE)

| Register | Offset | Address | Description |
|----------|--------|---------|-------------|
| `SEC_ENG_SE_GMAC_0_CTRL_0` | `0x500` | `0x20004500` | GMAC Control Register |
| `SEC_ENG_SE_GMAC_0_LCA` | `0x504` | `0x20004504` | GMAC Link Configuration Address |
| `SEC_ENG_SE_GMAC_0_STATUS` | `0x508` | `0x20004508` | GMAC Status Register |
| `SEC_ENG_SE_GMAC_0_CTRL_PROT` | `0x5FC` | `0x200045FC` | GMAC Control Protection Register |

### GMAC Control Register (CTRL_0) Bitfields

| Bits | Field | Description |
|------|-------|-------------|
| 0 | `SEC_ENG_SE_GMAC_0_BUSY` | GMAC busy flag (1 = processing) |
| 1 | `SEC_ENG_SE_GMAC_0_TRIG_1T` | Trigger GMAC operation (1T pulse, self-clears) |
| 2 | `SEC_ENG_SE_GMAC_0_EN` | GMAC enable |
| 8 | `SEC_ENG_SE_GMAC_0_INT` | Interrupt status flag |
| 9 | `SEC_ENG_SE_GMAC_0_INT_CLR_1T` | Clear interrupt (1T pulse) |
| 10 | `SEC_ENG_SE_GMAC_0_INT_SET_1T` | Set interrupt (1T pulse) |
| 11 | `SEC_ENG_SE_GMAC_0_INT_MASK` | Interrupt mask |
| 12 | `SEC_ENG_SE_GMAC_0_T_ENDIAN` | Tag endian control |
| 13 | `SEC_ENG_SE_GMAC_0_H_ENDIAN` | Hash key endian control |
| 14 | `SEC_ENG_SE_GMAC_0_X_ENDIAN` | Data endian control |

### GMAC Link Configuration Address Register (LCA)

| Bits | Field | Description |
|------|-------|-------------|
| 0-31 | `SEC_ENG_SE_GMAC_0_LCA` | Physical address of `bflb_sec_gmac_link_s` structure |

### GMAC Control Protection Bitfields

| Bit | Field | Description |
|-----|-------|-------------|
| 1 | `SEC_ENG_SE_GMAC_ID0_EN` | GMAC ID0 enable (group 0) |
| 2 | `SEC_ENG_SE_GMAC_ID1_EN` | GMAC ID1 enable (group 1) |

### Direct Register Access Example

```c
#include "hardware/sec_eng_reg.h"

int gmac_direct_operation(uint32_t link_addr)
{
    uint32_t reg_base = SEC_ENG_BASE;
    uint32_t regval;
    uint64_t start_time;

    /* Set link configuration address */
    putreg32(link_addr, reg_base + SEC_ENG_SE_GMAC_0_LCA_OFFSET);

    /* Enable GMAC in little-endian mode */
    regval = getreg32(reg_base + SEC_ENG_SE_GMAC_0_CTRL_0_OFFSET);
    regval &= ~SEC_ENG_SE_GMAC_0_T_ENDIAN;
    regval &= ~SEC_ENG_SE_GMAC_0_H_ENDIAN;
    regval &= ~SEC_ENG_SE_GMAC_0_X_ENDIAN;
    regval |= SEC_ENG_SE_GMAC_0_EN;
    putreg32(regval, reg_base + SEC_ENG_SE_GMAC_0_CTRL_0_OFFSET);

    /* Trigger GMAC operation */
    regval = getreg32(reg_base + SEC_ENG_SE_GMAC_0_CTRL_0_OFFSET);
    regval |= SEC_ENG_SE_GMAC_0_TRIG_1T;
    putreg32(regval, reg_base + SEC_ENG_SE_GMAC_0_CTRL_0_OFFSET);

    /* Poll BUSY */
    start_time = bflb_mtimer_get_time_ms();
    while (getreg32(reg_base + SEC_ENG_SE_GMAC_0_CTRL_0_OFFSET) & SEC_ENG_SE_GMAC_0_BUSY) {
        if ((bflb_mtimer_get_time_ms() - start_time) > 100) {
            return -1; // Timeout
        }
    }

    /* Result is now in the link structure at link_addr + 0x18 (result[4]) */

    /* Disable GMAC */
    regval = getreg32(reg_base + SEC_ENG_SE_GMAC_0_CTRL_0_OFFSET);
    regval &= ~SEC_ENG_SE_GMAC_0_EN;
    putreg32(regval, reg_base + SEC_ENG_SE_GMAC_0_CTRL_0_OFFSET);

    return 0;
}
```

### Group Protection Mechanism

The GMAC is a shared resource protected by the SEC_ENG group access mechanism. The protection state is read from `SEC_ENG_SE_CTRL_PROT_RD` (offset `0xF00`):

| Bits | Field | Description |
|------|-------|-------------|
| 10-11 | `SEC_ENG_SE_GMAC_ID0_EN_RD` | GMAC ID0 access state (0b11 = available, 0b01 = group0 owns, 0b10 = group1 owns) |

**Access Sequence:**
1. Read `SEC_ENG_SE_CTRL_PROT_RD` — if GMAC_ID bits are `0b11`, GMAC is available
2. Write `0x02` to `SEC_ENG_SE_GMAC_0_CTRL_PROT` for group0, or `0x04` for group1
3. Use GMAC
4. Write `0x06` to `SEC_ENG_SE_GMAC_0_CTRL_PROT` to release

---

## Link Structure Memory Layout

For use with DMA, the `bflb_sec_gmac_link_s` structure must be in non-cached, DMA-accessible memory:

```
Offset  | Field              | Size
--------|--------------------|------
+0x00   | Control Word       | 4 bytes
        | [8:0]   reserved  |
        | [9]     int_clr   |
        | [10]    int_set   |
        | [15:11] reserved  |
        | [31:16] msg_len   |
+0x04   | gmac_src_addr      | 4 bytes
+0x08   | gmac_key0          | 4 bytes
+0x0C   | gmac_key1          | 4 bytes
+0x10   | gmac_key2          | 4 bytes
+0x14   | gmac_key3          | 4 bytes
+0x18   | result[0]          | 4 bytes
+0x1C   | result[1]          | 4 bytes
+0x20   | result[2]          | 4 bytes
+0x24   | result[3]          | 4 bytes
```

> **Total size:** 40 bytes (10 × 32-bit words), 4-byte aligned

### Interrupt Integration

The GMAC supports interrupt-driven operation. The `SEC_ENG_ID0_SHA_AES_TRNG_PKA_GMAC_IRQn` (IRQ_NUM_BASE + 10) and `SEC_ENG_ID1_SHA_AES_TRNG_PKA_GMAC_IRQn` (IRQ_NUM_BASE + 9) interrupts are shared across all SEC_ENG sub-modules. To use GMAC with interrupts:

1. Set `gmac_int_set` bit in the link structure control word
2. Enable GMAC interrupt via `SEC_ENG_SE_GMAC_0_INT_MASK` in CTRL_0
3. In the ISR, check and clear the interrupt via `SEC_ENG_SE_GMAC_0_INT` / `SEC_ENG_SE_GMAC_0_INT_CLR_1T`
4. Read results from the link structure
