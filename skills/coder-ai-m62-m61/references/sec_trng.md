# TRNG API Reference (BL616/BL618)

> **Source:** `bouffalo_sdk/drivers/lhal/include/bflb_sec_trng.h`  
> **Implementation:** `bouffalo_sdk/drivers/lhal/src/bflb_sec_trng.c`  
> **Register Header:** `bouffalo_sdk/drivers/lhal/include/hardware/sec_eng_reg.h`

## Overview

The TRNG (True Random Number Generator) is a hardware peripheral within the SEC_ENG (Security Engine) module. It generates 256-bit (32-byte) true random numbers using a physical entropy source (ring oscillator based). The TRNG output is suitable for cryptographic key generation, nonces, initialization vectors, and other security-critical applications requiring non-deterministic random values.

The TRNG is a shared resource managed through the SEC_ENG's group protection mechanism. Before using the TRNG, the caller must request access via `bflb_group0_request_trng_access()` or `bflb_group1_request_trng_access()`, and release it after use.

## Base Address

| Peripheral | Base Address |
|------------|-------------|
| SEC_ENG | `0x20004000` |
| TRNG (within SEC_ENG) | `SEC_ENG_BASE + 0x200` |

---

## LHAL API Functions

### bflb_trng_read

Read 32 bytes (256 bits) of true random data from the TRNG hardware.

```c
int bflb_trng_read(struct bflb_device_s *dev, uint8_t data[32]);
```

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `dev` | `struct bflb_device_s *` | Device handle (can be NULL for direct HW access) |
| `data` | `uint8_t[32]` | Output buffer for 32 bytes of random data |

**Returns:** `0` on success, negative errno (`-ETIMEDOUT`) on timeout.

**Behavior:**
1. Enables the TRNG hardware
2. Clears any pending interrupt
3. Triggers the TRNG generation
4. Waits for BUSY flag to clear (with 100ms timeout)
5. Copies 8 × 32-bit data output registers to the buffer in little-endian
6. Disables the TRNG hardware

**Example:**
```c
uint8_t random_bytes[32];
int ret = bflb_trng_read(NULL, random_bytes);
if (ret == 0) {
    // 32 bytes of true random data ready
}
```

---

### bflb_trng_readlen

Read arbitrary length of random data by repeatedly calling `bflb_trng_read()`.

```c
int bflb_trng_readlen(uint8_t *data, uint32_t len);
```

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `data` | `uint8_t *` | Output buffer for random data |
| `len` | `uint32_t` | Number of bytes to read |

**Returns:** `0` on success, negative errno (`-ETIMEDOUT`) on timeout.

**Behavior:** Internally allocates a 32-byte temporary buffer, calls `bflb_trng_read()` repeatedly, and copies the required bytes to the output buffer.

**Example:**
```c
uint8_t key[256];
// Read 256 bytes (2048 bits) of random data
if (bflb_trng_readlen(key, sizeof(key)) == 0) {
    // Use as cryptographic key
}
```

---

### random

Standard C library `random()` function, backed by the TRNG hardware. Returns a single 32-bit random word.

```c
long random(void);
```

**Returns:** A 32-bit random value (from the first word of TRNG output).

**Note:** This function is declared `__WEAK`, allowing application-level override. It internally calls `bflb_trng_read()` and returns the first 32-bit word. Interrupts are disabled during the TRNG read for atomicity.

**Example:**
```c
uint32_t seed = (uint32_t)random();
srand(seed);
```

---

### bflb_group0_request_trng_access

Request TRNG access for security group 0. Must be called before using TRNG from group 0 context.

```c
int bflb_group0_request_trng_access(struct bflb_device_s *dev);
```

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `dev` | `struct bflb_device_s *` | Device handle |

**Returns:** `0` on success, `-1` on failure (TRNG not available or already claimed by another group).

---

### bflb_group1_request_trng_access

Request TRNG access for security group 1. Must be called before using TRNG from group 1 context.

```c
int bflb_group1_request_trng_access(struct bflb_device_s *dev);
```

**Returns:** `0` on success, `-1` on failure.

---

### bflb_group0_release_trng_access

Release TRNG access for security group 0. Call after TRNG operations are complete.

```c
void bflb_group0_release_trng_access(struct bflb_device_s *dev);
```

---

### bflb_group1_release_trng_access

Release TRNG access for security group 1. Call after TRNG operations are complete.

```c
void bflb_group1_release_trng_access(struct bflb_device_s *dev);
```

---

## Usage Examples

### Example 1: Basic Random Number Generation

```c
#include "bflb_sec_trng.h"

void trng_basic_example(void)
{
    struct bflb_device_s *sec_eng;
    uint8_t rand_data[32];
    int ret;

    sec_eng = bflb_device_get_by_name("sec_eng");

    // Request access (group 0)
    ret = bflb_group0_request_trng_access(sec_eng);
    if (ret != 0) {
        printf("Failed to acquire TRNG access\r\n");
        return;
    }

    // Read random data
    ret = bflb_trng_read(sec_eng, rand_data);
    if (ret == 0) {
        printf("Random: ");
        for (int i = 0; i < 32; i++) {
            printf("%02x ", rand_data[i]);
        }
        printf("\r\n");
    } else {
        printf("TRNG read timeout\r\n");
    }

    // Release access
    bflb_group0_release_trng_access(sec_eng);
}
```

### Example 2: Generate Cryptographic Key

```c
void trng_key_gen_example(void)
{
    struct bflb_device_s *sec_eng;
    uint8_t aes_key[16];  // 128-bit AES key
    uint8_t aes_iv[16];   // 128-bit IV

    sec_eng = bflb_device_get_by_name("sec_eng");

    bflb_group0_request_trng_access(sec_eng);

    // Generate AES-128 key
    bflb_trng_readlen(aes_key, 16);

    // Generate IV
    bflb_trng_readlen(aes_iv, 16);

    bflb_group0_release_trng_access(sec_eng);

    // Use aes_key and aes_iv for encryption
}
```

### Example 3: Using random() for Non-Crypto Use

```c
#include "bflb_sec_trng.h"

void random_seed_example(void)
{
    // Get a random seed from TRNG
    uint32_t seed = (uint32_t)random();

    // Use for software PRNG seeding
    srand(seed);

    // Now use rand() for non-critical purposes
    int pin = rand() % 4;
    int delay_ms = 100 + (rand() % 900);
}
```

### Example 4: Proper Acquire/Release Pattern

```c
void trng_safe_usage(struct bflb_device_s *sec_eng)
{
    int ret;

    // Try group 0 first
    ret = bflb_group0_request_trng_access(sec_eng);
    if (ret != 0) {
        // Try group 1 if group 0 is occupied
        ret = bflb_group1_request_trng_access(sec_eng);
        if (ret != 0) {
            printf("TRNG not available\r\n");
            return;
        }

        // Use with group 1
        uint8_t buf[32];
        bflb_trng_read(sec_eng, buf);

        bflb_group1_release_trng_access(sec_eng);
    } else {
        // Use with group 0
        uint8_t buf[32];
        bflb_trng_read(sec_eng, buf);

        bflb_group0_release_trng_access(sec_eng);
    }
}
```

---

## Register-Level Reference

> The TRNG is part of the SEC_ENG peripheral. Direct register access is possible but the LHAL API is recommended for normal usage.

### TRNG Register Offsets (from SEC_ENG_BASE)

| Register | Offset | Address | Description |
|----------|--------|---------|-------------|
| `SEC_ENG_SE_TRNG_0_CTRL_0` | `0x200` | `0x20004200` | TRNG Control Register 0 |
| `SEC_ENG_SE_TRNG_0_STATUS` | `0x204` | `0x20004204` | TRNG Status Register |
| `SEC_ENG_SE_TRNG_0_DOUT_0` | `0x208` | `0x20004208` | Random Output Word 0 |
| `SEC_ENG_SE_TRNG_0_DOUT_1` | `0x20C` | `0x2000420C` | Random Output Word 1 |
| `SEC_ENG_SE_TRNG_0_DOUT_2` | `0x210` | `0x20004210` | Random Output Word 2 |
| `SEC_ENG_SE_TRNG_0_DOUT_3` | `0x214` | `0x20004214` | Random Output Word 3 |
| `SEC_ENG_SE_TRNG_0_DOUT_4` | `0x218` | `0x20004218` | Random Output Word 4 |
| `SEC_ENG_SE_TRNG_0_DOUT_5` | `0x21C` | `0x2000421C` | Random Output Word 5 |
| `SEC_ENG_SE_TRNG_0_DOUT_6` | `0x220` | `0x20004220` | Random Output Word 6 |
| `SEC_ENG_SE_TRNG_0_DOUT_7` | `0x224` | `0x20004224` | Random Output Word 7 |
| `SEC_ENG_SE_TRNG_0_TEST` | `0x228` | `0x20004228` | TRNG Test Control |
| `SEC_ENG_SE_TRNG_0_CTRL_1` | `0x22C` | `0x2000422C` | TRNG Control Register 1 (Reseed N LSB) |
| `SEC_ENG_SE_TRNG_0_CTRL_2` | `0x230` | `0x20004230` | TRNG Control Register 2 (Reseed N MSB) |
| `SEC_ENG_SE_TRNG_0_CTRL_3` | `0x234` | `0x20004234` | TRNG Control Register 3 (H-Test params) |
| `SEC_ENG_SE_TRNG_0_TEST_OUT_0` | `0x240` | `0x20004240` | Test Output Word 0 |
| `SEC_ENG_SE_TRNG_0_TEST_OUT_1` | `0x244` | `0x20004244` | Test Output Word 1 |
| `SEC_ENG_SE_TRNG_0_TEST_OUT_2` | `0x248` | `0x20004248` | Test Output Word 2 |
| `SEC_ENG_SE_TRNG_0_TEST_OUT_3` | `0x24C` | `0x2000424C` | Test Output Word 3 |
| `SEC_ENG_SE_TRNG_0_CTRL_PROT` | `0x2FC` | `0x200042FC` | TRNG Control Protection Register |

### TRNG Control Register 0 (CTRL_0) Bitfields

| Bits | Field | Description |
|------|-------|-------------|
| 0 | `SEC_ENG_SE_TRNG_0_BUSY` | TRNG busy flag (1 = generating) |
| 1 | `SEC_ENG_SE_TRNG_0_TRIG_1T` | Trigger generation (1T pulse, self-clears) |
| 2 | `SEC_ENG_SE_TRNG_0_EN` | TRNG enable |
| 3 | `SEC_ENG_SE_TRNG_0_DOUT_CLR_1T` | Clear data output (1T pulse) |
| 4 | `SEC_ENG_SE_TRNG_0_HT_ERROR` | Health test error flag |
| 8 | `SEC_ENG_SE_TRNG_0_INT` | Interrupt status |
| 9 | `SEC_ENG_SE_TRNG_0_INT_CLR_1T` | Clear interrupt (1T pulse) |
| 10 | `SEC_ENG_SE_TRNG_0_INT_SET_1T` | Set interrupt (1T pulse) |
| 11 | `SEC_ENG_SE_TRNG_0_INT_MASK` | Interrupt mask |
| 13 | `SEC_ENG_SE_TRNG_0_MANUAL_FUN_SEL` | Manual function select |
| 14 | `SEC_ENG_SE_TRNG_0_MANUAL_RESEED` | Manual reseed trigger |
| 15 | `SEC_ENG_SE_TRNG_0_MANUAL_EN` | Manual mode enable |

### TRNG Test Register (TEST) Bitfields

| Bits | Field | Description |
|------|-------|-------------|
| 0 | `SEC_ENG_SE_TRNG_0_TEST_EN` | Test mode enable |
| 1 | `SEC_ENG_SE_TRNG_0_CP_TEST_EN` | CP test enable |
| 2 | `SEC_ENG_SE_TRNG_0_CP_BYPASS` | Conditioning pass bypass |
| 3 | `SEC_ENG_SE_TRNG_0_HT_DIS` | Health test disable |
| 4-11 | `SEC_ENG_SE_TRNG_0_HT_ALARM_N` | Health test alarm threshold |

### TRNG Control Register 3 (CTRL_3) Bitfields

| Bits | Field | Description |
|------|-------|-------------|
| 0-7 | `SEC_ENG_SE_TRNG_0_CP_RATIO` | Conditioning pass ratio |
| 8-15 | `SEC_ENG_SE_TRNG_0_HT_RCT_C` | Health test repetition count threshold |
| 16-25 | `SEC_ENG_SE_TRNG_0_HT_APT_C` | Health test adaptive proportion threshold |
| 26 | `SEC_ENG_SE_TRNG_0_HT_OD_EN` | Health test odds ratio enable |
| 31 | `SEC_ENG_SE_TRNG_0_ROSC_EN` | Ring oscillator enable |

### TRNG Control Protection Bitfields

| Bit | Field | Description |
|-----|-------|-------------|
| 1 | `SEC_ENG_SE_TRNG_ID0_EN` | TRNG ID0 enable (group 0) |
| 2 | `SEC_ENG_SE_TRNG_ID1_EN` | TRNG ID1 enable (group 1) |

### Direct Register Access Example

```c
#include "hardware/sec_eng_reg.h"

int trng_read_raw(uint8_t data[32])
{
    uint32_t reg_base = SEC_ENG_BASE;
    uint32_t regval;
    uint64_t start_time;
    uint8_t *p = data;

    /* Enable TRNG */
    regval = getreg32(reg_base + SEC_ENG_SE_TRNG_0_CTRL_0_OFFSET);
    regval |= SEC_ENG_SE_TRNG_0_EN;
    putreg32(regval, reg_base + SEC_ENG_SE_TRNG_0_CTRL_0_OFFSET);

    /* Clear interrupt */
    regval = getreg32(reg_base + SEC_ENG_SE_TRNG_0_CTRL_0_OFFSET);
    regval |= SEC_ENG_SE_TRNG_0_INT_CLR_1T;
    putreg32(regval, reg_base + SEC_ENG_SE_TRNG_0_CTRL_0_OFFSET);

    /* Wait 4 NOPs for hardware setup */
    __ASM volatile("nop"); __ASM volatile("nop");
    __ASM volatile("nop"); __ASM volatile("nop");

    /* Wait for previous operation to complete */
    start_time = bflb_mtimer_get_time_ms();
    while (getreg32(reg_base + SEC_ENG_SE_TRNG_0_CTRL_0_OFFSET) & SEC_ENG_SE_TRNG_0_BUSY) {
        if ((bflb_mtimer_get_time_ms() - start_time) > 100) return -1;
    }

    /* Clear interrupt and trigger generation */
    regval = getreg32(reg_base + SEC_ENG_SE_TRNG_0_CTRL_0_OFFSET);
    regval |= SEC_ENG_SE_TRNG_0_INT_CLR_1T;
    putreg32(regval, reg_base + SEC_ENG_SE_TRNG_0_CTRL_0_OFFSET);

    regval = getreg32(reg_base + SEC_ENG_SE_TRNG_0_CTRL_0_OFFSET);
    regval |= SEC_ENG_SE_TRNG_0_TRIG_1T;
    putreg32(regval, reg_base + SEC_ENG_SE_TRNG_0_CTRL_0_OFFSET);

    /* Wait 4 NOPs */
    __ASM volatile("nop"); __ASM volatile("nop");
    __ASM volatile("nop"); __ASM volatile("nop");

    /* Wait for BUSY to clear */
    start_time = bflb_mtimer_get_time_ms();
    while (getreg32(reg_base + SEC_ENG_SE_TRNG_0_CTRL_0_OFFSET) & SEC_ENG_SE_TRNG_0_BUSY) {
        if ((bflb_mtimer_get_time_ms() - start_time) > 100) return -1;
    }

    /* Read 8 × 32-bit output registers in little-endian */
    for (int i = 0; i < 8; i++) {
        uint32_t val = getreg32(reg_base + SEC_ENG_SE_TRNG_0_DOUT_0_OFFSET + (i * 4));
        p[0] = val & 0xff;
        p[1] = (val >> 8) & 0xff;
        p[2] = (val >> 16) & 0xff;
        p[3] = (val >> 24) & 0xff;
        p += 4;
    }

    /* Clear trigger and disable */
    regval = getreg32(reg_base + SEC_ENG_SE_TRNG_0_CTRL_0_OFFSET);
    regval &= ~SEC_ENG_SE_TRNG_0_TRIG_1T;
    putreg32(regval, reg_base + SEC_ENG_SE_TRNG_0_CTRL_0_OFFSET);

    regval = getreg32(reg_base + SEC_ENG_SE_TRNG_0_CTRL_0_OFFSET);
    regval |= SEC_ENG_SE_TRNG_0_DOUT_CLR_1T;
    putreg32(regval, reg_base + SEC_ENG_SE_TRNG_0_CTRL_0_OFFSET);

    regval = getreg32(reg_base + SEC_ENG_SE_TRNG_0_CTRL_0_OFFSET);
    regval &= ~SEC_ENG_SE_TRNG_0_DOUT_CLR_1T;
    putreg32(regval, reg_base + SEC_ENG_SE_TRNG_0_CTRL_0_OFFSET);

    /* Disable TRNG */
    regval = getreg32(reg_base + SEC_ENG_SE_TRNG_0_CTRL_0_OFFSET);
    regval &= ~SEC_ENG_SE_TRNG_0_EN;
    putreg32(regval, reg_base + SEC_ENG_SE_TRNG_0_CTRL_0_OFFSET);

    regval = getreg32(reg_base + SEC_ENG_SE_TRNG_0_CTRL_0_OFFSET);
    regval |= SEC_ENG_SE_TRNG_0_INT_CLR_1T;
    putreg32(regval, reg_base + SEC_ENG_SE_TRNG_0_CTRL_0_OFFSET);

    return 0;
}
```

### Group Protection Mechanism

The TRNG is a shared resource protected by the SEC_ENG group access mechanism. The protection state is read from `SEC_ENG_SE_CTRL_PROT_RD` (offset `0xF00`):

| Bits | Field | Description |
|------|-------|-------------|
| 4-5 | `SEC_ENG_SE_TRNG_ID0_EN_RD` | TRNG ID0 access state (0b11 = available, 0b01 = group0 owns, 0b10 = group1 owns) |

**Access Sequence:**
1. Read `SEC_ENG_SE_CTRL_PROT_RD` — if TRNG_ID bits are `0b11`, TRNG is available
2. Write `0x02` to `SEC_ENG_SE_TRNG_0_CTRL_PROT` for group0, or `0x04` for group1
3. Use TRNG
4. Write `0x06` to `SEC_ENG_SE_TRNG_0_CTRL_PROT` to release
