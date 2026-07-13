# RNG (TRNG) API Reference (BL616/BL618)

> True Random Number Generator via the Security Engine

**Source:** `bouffalo_sdk/drivers/lhal/include/bflb_sec_trng.h`  
**Implementation:** `bouffalo_sdk/drivers/lhal/src/bflb_sec_trng.c`  
**Hardware Base:** `SEC_ENG_BASE = 0x20004000` (part of the Security Engine block)  
**Device Name:** `BFLB_NAME_SEC_TRNG = "sec_trng"`  
**Device Type:** `BFLB_DEVICE_TYPE_TRNG` (per `bflb_core.h`)

---

## Overview

The BL616/BL618 integrates a **True Random Number Generator (TRNG)** as part of the Security Engine (SEC_ENG). The TRNG uses analog noise sources to produce cryptographically secure random numbers suitable for key generation, IV creation, nonces, and other security-critical operations.

The TRNG provides:
- **256-bit (32-byte) random words** per read operation
- **Built-in post-processing** (entropy conditioning built into hardware)
- **Timeout protection** (100 ms timeout prevents hang on hardware failure)
- **Group-based access control** — multiple masters (CPU, WiFi, BLE) can request TRNG access

### TRNG Hardware Architecture

The TRNG is part of the Security Engine at `SEC_ENG_BASE`. On BL616/BL616CL, `SEC_ENG_BASE = 0x20004000`. On BL618DG (dual-core), the base is `0x20080000`.

The TRNG operation sequence:
1. Enable the TRNG block
2. Clear any pending interrupts
3. Trigger a generation cycle
4. Poll for `BUSY` flag deassertion
5. Read 32 bytes from `DOUT_0` through `DOUT_7` registers
6. Disable the TRNG

The TRNG returns 32 bytes per trigger. The `bflb_trng_readlen()` function automatically handles looping for smaller or larger requests.

---

## Function Reference

### `bflb_trng_read()`

```c
int bflb_trng_read(struct bflb_device_s *dev, uint8_t data[32]);
```

Read 32 bytes of random data from the TRNG.

**Parameters:**
- `dev`  — Device handle (not used on BL616, can be `NULL` or obtained from `bflb_device_get_by_name("sec_trng")`)
- `data` — Pointer to a 32-byte buffer to receive the random data

**Returns:** `0` on success, `-ETIMEDOUT` (-110) if TRNG did not respond within 100 ms.

**Example:**
```c
uint8_t random_bytes[32];
int ret = bflb_trng_read(NULL, random_bytes);
if (ret == 0) {
    printf("Random: %02x%02x%02x%02x...\n",
           random_bytes[0], random_bytes[1],
           random_bytes[2], random_bytes[3]);
}
```

---

### `bflb_trng_readlen()`

```c
int bflb_trng_readlen(uint8_t *data, uint32_t len);
```

Read an arbitrary number of random bytes (up to any length). Internally calls `bflb_trng_read()` as many times as needed to satisfy the request.

**Parameters:**
- `data` — Pointer to destination buffer
- `len`  — Number of random bytes to read

**Returns:** `0` on success, `-ETIMEDOUT` if TRNG failed to respond.

**Example:**
```c
/* Generate a 128-bit random AES key */
uint8_t aes_key[16];
int ret = bflb_trng_readlen(aes_key, sizeof(aes_key));

/* Generate a random IV for CBC mode */
uint8_t iv[16];
bflb_trng_readlen(iv, sizeof(iv));
```

---

### `random()`

```c
long random(void);
```

A simplified random number function that returns a single 32-bit random word. Uses `bflb_trng_read()` internally with interrupt protection.

**Returns:** 32-bit unsigned random value.

**Example:**
```c
/* Generate a random integer */
long r = random();
printf("Random value: %ld\n", r);

/* Random in a range */
int dice = (random() % 6) + 1;
printf("Dice roll: %d\n", dice);
```

---

### `bflb_group0_request_trng_access()` / `bflb_group1_request_trng_access()`

```c
int bflb_group0_request_trng_access(struct bflb_device_s *dev);
int bflb_group1_request_trng_access(struct bflb_device_s *dev);
```

Request exclusive TRNG access for a specific hardware group. The BL616 has two TRNG access groups (Group 0 and Group 1) that can be granted to different system masters (e.g., CPU vs. wireless subsystem).

**Parameters:**
- `dev` — Device handle for the TRNG device

**Returns:** `0` on success, `-1` if access could not be granted.

**Note:** Group-based access is an advanced feature for multi-master systems. Most applications should use the direct `bflb_trng_read()` API without explicit access management.

---

### `bflb_group0_release_trng_access()` / `bflb_group1_release_trng_access()`

```c
void bflb_group0_release_trng_access(struct bflb_device_s *dev);
void bflb_group1_release_trng_access(struct bflb_device_s *dev);
```

Release previously granted TRNG access group, returning it to the pool for other masters.

---

## Complete Usage Examples

### Basic Random Number Generation

```c
#include "bflb_sec_trng.h"
#include "bflb_device.h"
#include <stdio.h>

void trng_basic_demo(void)
{
    uint8_t rnd[32];
    int ret;

    /* Read 32 random bytes */
    ret = bflb_trng_read(NULL, rnd);
    if (ret != 0) {
        printf("TRNG read failed: %d\n", ret);
        return;
    }

    printf("32-byte random: ");
    for (int i = 0; i < 32; i++) {
        printf("%02x", rnd[i]);
    }
    printf("\n");
}
```

### Generate Cryptographic Keys

```c
#include "bflb_sec_trng.h"
#include <string.h>

void generate_crypto_keys(void)
{
    int ret;

    /* AES-128 key (16 bytes) */
    uint8_t aes128_key[16];
    ret = bflb_trng_readlen(aes128_key, sizeof(aes128_key));
    if (ret != 0) { /* handle error */ }

    /* AES-256 key (32 bytes) */
    uint8_t aes256_key[32];
    bflb_trng_readlen(aes256_key, sizeof(aes256_key));

    /* HMAC key (24 bytes) */
    uint8_t hmac_key[24];
    bflb_trng_readlen(hmac_key, sizeof(hmac_key));

    printf("AES-128 key: %02x%02x...%02x%02x\n",
           aes128_key[0], aes128_key[1],
           aes128_key[14], aes128_key[15]);
}
```

### Generate Random MAC Address

```c
#include "bflb_sec_trng.h"

void generate_random_mac(uint8_t mac[6])
{
    bflb_trng_readlen(mac, 6);
    /* Ensure unicast and not reserved multicast */
    mac[0] &= ~0x01;
    mac[0] |= 0x02; /* Locally administered address */
}
```

### Monte Carlo Simulation (Simple)

```c
#include "bflb_sec_trng.h"
#include <stdio.h>

void monte_carlo_pi(void)
{
    uint32_t inside = 0;
    uint32_t total = 1000000;

    for (uint32_t i = 0; i < total; i++) {
        /* Generate random x, y in [0, 1) using 16-bit fraction */
        uint8_t buf[4];
        bflb_trng_readlen(buf, 4);
        double x = (double)*(uint16_t *)&buf[0] / 65535.0;
        double y = (double)*(uint16_t *)&buf[2] / 65535.0;

        /* Check if point (x,y) is inside unit circle */
        if ((x*x + y*y) <= 1.0) {
            inside++;
        }
    }

    double pi_estimate = 4.0 * (double)inside / (double)total;
    printf("Pi estimate: %.6f (real: %.6f)\n", pi_estimate, 3.141593);
}
```

### Simple Random Game

```c
#include "bflb_sec_trng.h"
#include <stdio.h>

void number_guessing_game(void)
{
    /* Generate random target 1-100 */
    uint8_t rnd[1];
    bflb_trng_readlen(rnd, 1);
    int target = (rnd[0] % 100) + 1;

    printf("Guess a number between 1 and 100\n");
    for (int guess = 0; guess < 10; guess++) {
        /* In practice, you'd read from UART here */
        int user_guess = (random() % 100) + 1;
        printf("Attempt %d: guessed %d - ", guess + 1, user_guess);

        if (user_guess < target) {
            printf("too low!\n");
        } else if (user_guess > target) {
            printf("too high!\n");
        } else {
            printf("CORRECT!\n");
            break;
        }
    }
}
```

---

## Register-Level Reference

The TRNG registers are within the Security Engine at `SEC_ENG_BASE = 0x20004000`:

| Offset | Register | Description |
|--------|----------|-------------|
| `0x200` | SEC_ENG_SE_TRNG_0_CTRL_0 | TRNG control/status register |
| `0x204` | SEC_ENG_SE_TRNG_0_STATUS | TRNG status (busy, errors) |
| `0x208-0x224` | SEC_ENG_SE_TRNG_0_DOUT_0-7 | 32 bytes of TRNG output data |
| `0x228` | SEC_ENG_SE_TRNG_0_TEST | Test mode control |
| `0x22C-0x234` | SEC_ENG_SE_TRNG_0_CTRL_1-3 | Additional TRNG control |
| `0x2FC` | SEC_ENG_SE_TRNG_0_CTRL_PROT | Access protection control |

### Key TRNG Control Bits (SEC_ENG_SE_TRNG_0_CTRL_0)

```c
#define SEC_ENG_SE_TRNG_0_EN             (1 << 2)   /* TRNG enable */
#define SEC_ENG_SE_TRNG_0_TRIG_1T        (1 << 1)   /* Trigger (write 1 to start) */
#define SEC_ENG_SE_TRNG_0_BUSY           (1 << 0)   /* TRNG busy (read) */
#define SEC_ENG_SE_TRNG_0_DOUT_CLR_1T    (1 << 3)   /* Clear output data */
#define SEC_ENG_SE_TRNG_0_INT_CLR_1T     (1 << 9)   /* Clear interrupt flag */
#define SEC_ENG_SE_TRNG_0_HT_ERROR       (1 << 4)   /* Health test error flag */
```

### TRNG Read Procedure (Register-Level)

```
1. Write 0x04 to SEC_ENG_SE_TRNG_0_CTRL_0     /* Enable TRNG */
2. Write 0x200 to SEC_ENG_SE_TRNG_0_CTRL_0   /* Clear interrupt */
3. NOP × 4                                    /* Wait 1 cycle */
4. Poll SEC_ENG_SE_TRNG_0_CTRL_0[0]==0        /* Wait until not BUSY */
5. Write 0x202 to SEC_ENG_SE_TRNG_0_CTRL_0   /* Trigger generation */
6. NOP × 4
7. Poll SEC_ENG_SE_TRNG_0_CTRL_0[0]==0
8. Read 32 bytes from DOUT_0..DOUT_7
9. Write 0x00 to SEC_ENG_SE_TRNG_0_CTRL_0    /* Disable */
```

> **Note:** The `bflb_trng_read()` function abstracts this entire sequence. The TRNG outputs 256 bits (32 bytes) per trigger via 8 × 32-bit `DOUT` registers at offsets `0x208` through `0x224`.
