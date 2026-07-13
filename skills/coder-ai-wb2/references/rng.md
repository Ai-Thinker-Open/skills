# RNG API Reference

> Source file: `components/platform/hosal/include/hosal_rng.h`

## Function Interface

### `hosal_rng_init`

Initialize the random number generator.

```c
int hosal_rng_init(void);
```

**Return value**: `0` success, others failure

> This function must be called before `hosal_random_num_read`.

---

### `hosal_random_num_read`

Read random numbers to fill the buffer.

```c
int hosal_random_num_read(void *buf, uint32_t bytes);
```

| Parameter | Description |
|-----------|-------------|
| `buf` | Valid memory buffer, random numbers will be filled into this memory |
| `bytes` | Buffer length (bytes) |

**Return value**: `0` success, others failure

## Usage Example

```c
#include "hal_rng.h"

// Initialize RNG (usually called once during system initialization)
hosal_rng_init();

// Read 8 bytes of random numbers
uint8_t random_bytes[8];
int ret = hosal_random_num_read(random_bytes, 8);
if (ret == 0) {
    printf("Random: %02X%02X%02X%02X%02X%02X%02X%02X\r\n",
           random_bytes[0], random_bytes[1], random_bytes[2], random_bytes[3],
           random_bytes[4], random_bytes[5], random_bytes[6], random_bytes[7]);
}

// Generate random numbers for keys, random delays, frequency hopping, etc.
uint32_t random_val;
hosal_random_num_read(&random_val, sizeof(random_val));
```

## Application Scenarios

| Scenario | Description |
|----------|-------------|
| Key generation | Session keys for encrypted communication |
| Random delay | Random backoff time to avoid wireless communication conflicts |
| MAC address | Generate random MAC address for testing |
| Frequency hopping seed | Pseudo-random sequence seed for frequency hopping communication |

---

## Register-Level Programming

> Register Header: `components/platform/soc/bl602/bl602_std/bl602_std/Device/Bouffalo/BL602/Peripherals/sec_eng_reg.h`  
> Base Address: `SEC_ENG_BASE = 0x40004000`  
> TRNG Offset: `0x200` (TRNG base = `0x40004200`)

### Register Overview

TRNG (True Random Number Generator) is part of the Security Engine block.

| Offset | Name | Description |
|--------|------|-------------|
| 0x00 | TRNG_CONFIG | TRNG configuration (enable, oscillator, post-process) |
| 0x04 | TRNG_DATA | Random data output (32-bit) |
| 0x08 | TRNG_STATUS | TRNG status (data ready, health test fail) |
| 0x0C | TRNG_INT_CTRL | TRNG interrupt control |

### Key Register Fields

**TRNG_CONFIG (0x00)**

| Bits | Name | Description |
|------|------|-------------|
| 0 | trng_en | TRNG enable (1=enable) |
| 1 | ringosc_en | Ring oscillator enable (1=enable) |
| 2 | post_process_en | Post-processing / health test enable (1=enable) |

**TRNG_STATUS (0x08)**

| Bits | Name | Description |
|------|------|-------------|
| 0 | data_ready | Random data ready (1=ready) |
| 1 | health_test_fail | Health test failed (1=test failed) |

**TRNG_INT_CTRL (0x0C)**

| Bits | Name | Description |
|------|------|-------------|
| 0 | int_enable | TRNG interrupt enable (1=enable) |

### Register-Level Code Example

```c
#include <stdint.h>

/* Security Engine base */
#define SEC_ENG_BASE  0x40004000

/* TRNG offset within SEC_ENG */
#define TRNG_OFFSET   0x200
#define TRNG_BASE     (SEC_ENG_BASE + TRNG_OFFSET)

/* TRNG register offsets */
#define TRNG_CONFIG     0x00
#define TRNG_DATA       0x04
#define TRNG_STATUS     0x08
#define TRNG_INT_CTRL   0x0C

/* Bit masks */
#define TRNG_EN           (1 << 0)
#define TRNG_RINGOSC_EN   (1 << 1)
#define TRNG_POST_PROC_EN (1 << 2)
#define TRNG_DATA_READY   (1 << 0)
#define TRNG_HEALTH_FAIL  (1 << 1)
#define TRNG_INT_EN       (1 << 0)

static volatile uint32_t * const TRNG = (volatile uint32_t *)TRNG_BASE;

/* Initialize TRNG (must be called before reading) */
void rng_init(void) {
    /* Enable ring oscillator and TRNG with post-processing (health test) */
    TRNG[TRNG_CONFIG / 4] = TRNG_EN | TRNG_RINGOSC_EN | TRNG_POST_PROC_EN;
}

/* Poll for random data ready */
int rng_wait_ready(void) {
    uint32_t timeout = 100000;
    while (timeout--) {
        if (TRNG[TRNG_STATUS / 4] & TRNG_DATA_READY)
            return 0;
    }
    return -1;
}

/* Read a single 32-bit random word (blocking) */
uint32_t rng_read_word(void) {
    /* Poll until ready */
    while ((TRNG[TRNG_STATUS / 4] & TRNG_DATA_READY) == 0);
    return TRNG[TRNG_DATA / 4];
}

/* Read multiple random bytes into buffer */
int rng_read_bytes(uint8_t *buf, uint32_t len) {
    uint32_t words, remainder;
    uint32_t i;

    /* Ensure TRNG is initialized */
    if ((TRNG[TRNG_CONFIG / 4] & TRNG_EN) == 0) {
        rng_init();
    }

    words = len / 4;
    remainder = len % 4;

    /* Read full 32-bit words */
    for (i = 0; i < words; i++) {
        if (rng_wait_ready() != 0)
            return -1;
        uint32_t val = TRNG[TRNG_DATA / 4];
        buf[i * 4 + 0] = (uint8_t)(val & 0xFF);
        buf[i * 4 + 1] = (uint8_t)((val >> 8) & 0xFF);
        buf[i * 4 + 2] = (uint8_t)((val >> 16) & 0xFF);
        buf[i * 4 + 3] = (uint8_t)((val >> 24) & 0xFF);
    }

    /* Read remaining bytes */
    if (remainder > 0) {
        if (rng_wait_ready() != 0)
            return -1;
        uint32_t val = TRNG[TRNG_DATA / 4];
        for (i = 0; i < remainder; i++) {
            buf[words * 4 + i] = (uint8_t)((val >> (i * 8)) & 0xFF);
        }
    }

    return 0;
}

/* Check health test status */
int rng_health_ok(void) {
    return (TRNG[TRNG_STATUS / 4] & TRNG_HEALTH_FAIL) == 0;
}

/* Example: read 8 random bytes */
void rng_example(void) {
    uint8_t random_bytes[8];
    uint32_t i;

    /* Initialize TRNG */
    rng_init();

    /* Read 8 bytes */
    if (rng_read_bytes(random_bytes, 8) == 0) {
        printf("Random bytes: ");
        for (i = 0; i < 8; i++)
            printf("%02X", random_bytes[i]);
        printf("\r\n");
    }

    /* Check health */
    if (rng_health_ok())
        printf("RNG health: OK\r\n");
    else
        printf("RNG health: FAILED\r\n");
}
```
