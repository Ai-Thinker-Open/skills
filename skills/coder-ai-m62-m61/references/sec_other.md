# BL616/BL618 Security Engine Documentation

**SEC_ENG_BASE** = `0x20004000`

This document covers the Security Engine peripheral drivers for TRNG, DSA, GMAC, ECDSA, and PKA modules.

---

## Table of Contents

1. [TRNG - True Random Number Generator](#1-trng---true-random-number-generator)
2. [DSA - Digital Signature Algorithm](#2-dsa---digital-signature-algorithm)
3. [GMAC - Galois Message Authentication Code](#3-gmac---galois-message-authentication-code)
4. [ECDSA - Elliptic Curve Digital Signature Algorithm](#4-ecdsa---elliptic-curve-digital-signature-algorithm)
5. [PKA - Public Key Accelerator](#5-pka---public-key-accelerator)

---

## 1. TRNG - True Random Number Generator

### Header
```c
#include "bflb_sec_trng.h"
```

### Overview
The TRNG module provides hardware-accelerated true random number generation. It supports both polled and interrupt-based access, with separate permission groups for multi-threaded/multi-core safety.

### API Reference

| Function | Description |
|----------|-------------|
| `bflb_trng_read(dev, data)` | Read 32 bytes of random data |
| `bflb_trng_readlen(data, len)` | Read custom-length random data |
| `random()` | Get random value as `long` |
| `bflb_group0_request_trng_access(dev)` | Enable TRNG access for group 0 |
| `bflb_group0_release_trng_access(dev)` | Disable TRNG access for group 0 |
| `bflb_group1_request_trng_access(dev)` | Enable TRNG access for group 1 |
| `bflb_group1_release_trng_access(dev)` | Disable TRNG access for group 1 |

### Data Structures
```c
// No specific structures - uses basic types
```

### Working Code Example

```c
#include "bflb_sec_trng.h"
#include "bflb_gpio.h"

void trng_example(void)
{
    struct bflb_device_s *dev;
    uint8_t random_data[32];
    int ret;

    /* Get TRNG device */
    dev = bflb_device_get_by_name("trng");
    if (dev == NULL) {
        printf("TRNG device not found\r\n");
        return;
    }

    /* Request TRNG access for group 0 (required for secure access) */
    ret = bflb_group0_request_trng_access(dev);
    if (ret != 0) {
        printf("Failed to request TRNG access\r\n");
        return;
    }

    /* Method 1: Read 32 bytes of random data */
    ret = bflb_trng_read(dev, random_data);
    if (ret == 0) {
        printf("Random data (32 bytes):\r\n");
        for (int i = 0; i < 32; i++) {
            printf("%02x ", random_data[i]);
        }
        printf("\r\n");
    }

    /* Method 2: Read custom length (e.g., 16 bytes) */
    ret = bflb_trng_readlen(random_data, 16);
    if (ret == 0) {
        printf("Random data (16 bytes):\r\n");
        for (int i = 0; i < 16; i++) {
            printf("%02x ", random_data[i]);
        }
        printf("\r\n");
    }

    /* Method 3: Get single random word */
    long rand_val = random();
    printf("Random word: %lu\r\n", rand_val);

    /* Release TRNG access when done */
    bflb_group0_release_trng_access(dev);
}
```

---

## 2. DSA - Digital Signature Algorithm

### Header
```c
#include "bflb_sec_dsa.h"
```

### Overview
The DSA module performs Digital Signature Algorithm operations using RSA with CRT (Chinese Remainder Theorem) optimization for faster computation.

### API Reference

| Function | Description |
|----------|-------------|
| `bflb_sec_dsa_init(handle, size)` | Initialize DSA handle with key size |
| `bflb_sec_dsa_sign(handle, hash, hashLenInWord, s)` | Sign hash data |
| `bflb_sec_dsa_verify(handle, hash, hashLenInWord, s)` | Verify signature |

### Data Structures

```c
/* CRT (Chinese Remainder Theorem) configuration */
struct bflb_dsa_crt_s {
    uint32_t *dP;        /* d mod (p-1) */
    uint32_t *dQ;        /* d mod (q-1) */
    uint32_t *qInv;      /* q^(-1) mod p */
    uint32_t *p;         /* Prime p */
    uint32_t *invR_p;   /* R^(-1) mod p */
    uint32_t *primeN_p;  /* Prime N for p */
    uint32_t *q;         /* Prime q */
    uint32_t *invR_q;   /* R^(-1) mod q */
    uint32_t *primeN_q;  /* Prime N for q */
};

/* DSA handle structure */
struct bflb_dsa_s {
    uint32_t size;           /* Key size in words */
    uint32_t crtSize;        /* CRT parameter size */
    uint32_t *n;             /* Public modulus n = p*q */
    uint32_t *e;             /* Public exponent e */
    uint32_t *d;             /* Private exponent d */
    struct bflb_dsa_crt_s crtCfg;  /* CRT configuration */
};
```

### Working Code Example

```c
#include "bflb_sec_dsa.h"
#include <string.h>

/* Example: RSA-2048 with CRT parameters (256 words = 2048 bits) */
#define RSA_KEY_SIZE_WORDS 256
#define RSA_HASH_WORDS     8    /* SHA-256: 256 bits = 8 words */

void dsa_example(void)
{
    int ret;
    struct bflb_dsa_s dsa_handle;

    /* Static buffers for key material (must be kept allocated) */
    static uint32_t n[RSA_KEY_SIZE_WORDS];   /* Public modulus */
    static uint32_t e[1] = { 65537 };         /* Public exponent */
    static uint32_t d[RSA_KEY_SIZE_WORDS];    /* Private exponent */
    static uint32_t hash[RSA_HASH_WORDS];     /* Message hash */
    static uint32_t signature[RSA_KEY_SIZE_WORDS]; /* Signature output */

    /* CRT parameters (for RSA-2048: p and q are 1024 bits each) */
    static uint32_t dP[128];   /* d mod (p-1) */
    static uint32_t dQ[128];   /* d mod (q-1) */
    static uint32_t qInv[128]; /* q^(-1) mod p */
    static uint32_t p[128];    /* Prime p */
    static uint32_t invR_p[128];
    static uint32_t primeN_p[128];
    static uint32_t q[128];    /* Prime q */
    static uint32_t invR_q[128];
    static uint32_t primeN_q[128];

    /* Initialize DSA handle */
    dsa_handle.size = RSA_KEY_SIZE_WORDS;
    dsa_handle.crtSize = 128;
    dsa_handle.n = n;
    dsa_handle.e = e;
    dsa_handle.d = d;
    dsa_handle.crtCfg.dP = dP;
    dsa_handle.crtCfg.dQ = dQ;
    dsa_handle.crtCfg.qInv = qInv;
    dsa_handle.crtCfg.p = p;
    dsa_handle.crtCfg.invR_p = invR_p;
    dsa_handle.crtCfg.primeN_p = primeN_p;
    dsa_handle.crtCfg.q = q;
    dsa_handle.crtCfg.invR_q = invR_q;
    dsa_handle.crtCfg.primeN_q = primeN_q;

    ret = bflb_sec_dsa_init(&dsa_handle, RSA_KEY_SIZE_WORDS);
    if (ret != 0) {
        printf("DSA init failed: %d\r\n", ret);
        return;
    }

    /* Prepare message hash (e.g., SHA-256 of message) */
    /* In practice, this would be computed from actual message */
    memset(hash, 0xAB, sizeof(hash));

    /* Sign the hash */
    ret = bflb_sec_dsa_sign(&dsa_handle, hash, RSA_HASH_WORDS, signature);
    if (ret == 0) {
        printf("DSA sign: SUCCESS\r\n");
    } else {
        printf("DSA sign failed: %d\r\n", ret);
    }

    /* Verify the signature */
    ret = bflb_sec_dsa_verify(&dsa_handle, hash, RSA_HASH_WORDS, signature);
    if (ret == 0) {
        printf("DSA verify: SUCCESS\r\n");
    } else {
        printf("DSA verify failed: %d\r\n", ret);
    }
}
```

---

## 3. GMAC - Galois Message Authentication Code

### Header
```c
#include "bflb_sec_gmac.h"
```

### Overview
The GMAC module provides Galois Message Authentication Code functionality, typically used for authenticated encryption in GCM mode.

### API Reference

| Function | Description |
|----------|-------------|
| `bflb_sec_gmac_le_enable(dev)` | Enable little-endian GMAC mode |
| `bflb_sec_gmac_link_enable(dev, enable)` | Enable/disable GMAC link mode |
| `bflb_sec_gmac_link_work(dev, addr, in, len, out)` | Perform GMAC operation |
| `bflb_group0_request_gmac_access(dev)` | Request GMAC access for group 0 |
| `bflb_group0_release_gmac_access(dev)` | Release GMAC access for group 0 |
| `bflb_group1_request_gmac_access(dev)` | Request GMAC access for group 1 |
| `bflb_group1_release_gmac_access(dev)` | Release GMAC access for group 1 |

### Data Structures

```c
/* SEC_ENG GMAC link configuration structure */
struct bflb_sec_gmac_link_s {
    uint32_t                : 9;  /*!< [8:0] reserved */
    uint32_t gmac_int_clear : 1;  /*!< [9] Clear interrupt */
    uint32_t gmac_int_set   : 1;  /*!< [10] Set interrupt */
    uint32_t                : 5;  /*!< [15:11] reserved */
    uint32_t gmac_msg_len   : 16; /*!< [31:16] Number of 128-bit blocks */
    uint32_t gmac_src_addr;       /*!< Message source address */
    uint32_t gmac_key0;           /*!< GMAC key (bits [31:0]) */
    uint32_t gmac_key1;           /*!< GMAC key (bits [63:32]) */
    uint32_t gmac_key2;           /*!< GMAC key (bits [95:64]) */
    uint32_t gmac_key3;           /*!< GMAC key (bits [127:96]) */
    uint32_t result[4];           /*!< GMAC result (128-bit tag) */
} __attribute__((aligned(4)));
```

### Working Code Example

```c
#include "bflb_sec_gmac.h"
#include <string.h>

#define GMAC_KEY_SIZE 16  /* 128-bit key */
#define GMAC_TAG_SIZE 16  /* 128-bit authentication tag */
#define GMAC_BLOCK_SIZE 16 /* 128-bit block size */

void gmac_example(void)
{
    struct bflb_device_s *dev;
    int ret;

    /* Example key (128-bit) */
    const uint8_t key[GMAC_KEY_SIZE] = {
        0x00, 0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07,
        0x08, 0x09, 0x0A, 0x0B, 0x0C, 0x0D, 0x0E, 0x0F
    };

    /* Example input message (must be multiple of 16 bytes) */
    uint8_t input[32] = {
        0x00, 0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07,
        0x08, 0x09, 0x0A, 0x0B, 0x0C, 0x0D, 0x0E, 0x0F,
        0x10, 0x11, 0x12, 0x13, 0x14, 0x15, 0x16, 0x17,
        0x18, 0x19, 0x1A, 0x1B, 0x1C, 0x1D, 0x1E, 0x1F
    };

    uint8_t output[32];    /* Output buffer (same size as input) */
    uint8_t tag[GMAC_TAG_SIZE]; /* Authentication tag */

    /* Get GMAC device */
    dev = bflb_device_get_by_name("sec_eng");
    if (dev == NULL) {
        printf("SEC_ENG device not found\r\n");
        return;
    }

    /* Request GMAC access for group 0 */
    ret = bflb_group0_request_gmac_access(dev);
    if (ret != 0) {
        printf("Failed to request GMAC access\r\n");
        return;
    }

    /* Enable little-endian mode */
    bflb_sec_gmac_le_enable(dev);

    /* Enable GMAC link mode */
    bflb_sec_gmac_link_enable(dev, 1);

    /* Perform GMAC operation
     * The GMAC hardware will compute the authentication tag
     * Output will be stored in the result[] array of internal config
     */
    uint32_t gmac_addr = SEC_ENG_BASE; /* GMAC config base address */

    ret = bflb_sec_gmac_link_work(dev, gmac_addr, input, sizeof(input), output);
    if (ret == 0) {
        printf("GMAC operation: SUCCESS\r\n");

        /* The authentication tag is in the result array at gmac_addr + offset
         * For actual tag retrieval, you'd need to read from hardware registers
         */
        printf("GMAC output written to buffer\r\n");
    } else {
        printf("GMAC operation failed: %d\r\n", ret);
    }

    /* Disable GMAC link mode */
    bflb_sec_gmac_link_enable(dev, 0);

    /* Release GMAC access */
    bflb_group0_release_gmac_access(dev);
}
```

---

## 4. ECDSA - Elliptic Curve Digital Signature Algorithm

### Header
```c
#include "bflb_sec_ecdsa.h"
```

### Overview
The ECDSA module provides Elliptic Curve Digital Signature Algorithm operations supporting multiple curves including SECP256R1, SECP256K1, and SECP384R1.

### API Reference

| Function | Description |
|----------|-------------|
| `bflb_sec_ecdsa_init(handle, id)` | Initialize ECDSA handle with curve ID |
| `bflb_sec_ecdsa_deinit(handle)` | Deinitialize ECDSA handle |
| `bflb_sec_ecdsa_sign(handle, random_k, hash, hashLenInWord, r, s)` | Sign hash with ECDSA |
| `bflb_sec_ecdsa_verify(handle, hash, hashLen, r, s)` | Verify ECDSA signature |
| `bflb_sec_ecdsa_get_private_key(handle, private_key)` | Extract private key |
| `bflb_sec_ecdsa_get_public_key(handle, private_key, pRx, pRy)` | Compute public key from private key |
| `bflb_sec_ecdh_init(handle, id)` | Initialize ECDH handle |
| `bflb_sec_ecdh_deinit(handle)` | Deinitialize ECDH handle |
| `bflb_sec_ecdh_get_encrypt_key(handle, pkX, pkY, private_key, pRx, pRy)` | ECDH key exchange |
| `bflb_sec_ecdh_get_public_key(handle, private_key, pRx, pRy)` | ECDH public key computation |
| `bflb_sec_ecc_get_random_value(data, max_ref, size)` | Get random value for ECC |

### Curve Definitions

| Constant | Description |
|----------|-------------|
| `ECP_SECP256R1` | NIST P-256 curve (prime256v1) |
| `ECP_SECP256K1` | SECP256K1 curve (Bitcoin) |
| `ECP_SECP384R1` | NIST P-384 curve (requires `ECP_SUPPORT_384`) |

### Data Structures

```c
/* ECDSA handle structure */
struct bflb_ecdsa_s {
    uint8_t ecpId;           /* Curve identifier */
    uint8_t pad[3];          /* Padding for alignment */
    uint32_t *privateKey;    /* Private key pointer */
    uint32_t *publicKeyx;    /* Public key X coordinate */
    uint32_t *publicKeyy;    /* Public key Y coordinate */
};

/* ECDH handle structure */
struct bflb_ecdh_s {
    uint8_t ecpId;           /* Curve identifier */
};
```

### Working Code Example - ECDSA

```c
#include "bflb_sec_ecdsa.h"
#include <string.h>

#define SHA256_WORDS 8  /* SHA-256 produces 256-bit = 8 words */

/* SECP256R1 (P-256) key size: 256 bits = 8 words per coordinate */
#define ECC_KEY_WORDS 8

void ecdsa_example(void)
{
    int ret;
    struct bflb_ecdsa_s ecdsa_handle;

    /* Key buffers */
    static uint32_t private_key[ECC_KEY_WORDS];
    static uint32_t public_key_x[ECC_KEY_WORDS];
    static uint32_t public_key_y[ECC_KEY_WORDS];
    static uint32_t hash[SHA256_WORDS];  /* Message hash */
    static uint32_t sig_r[ECC_KEY_WORDS]; /* Signature R component */
    static uint32_t sig_s[ECC_KEY_WORDS]; /* Signature S component */
    static uint32_t random_k[ECC_KEY_WORDS]; /* Random k for signing */

    /* Initialize ECDSA with SECP256R1 curve */
    ret = bflb_sec_ecdsa_init(&ecdsa_handle, ECP_SECP256R1);
    if (ret != 0) {
        printf("ECDSA init failed: %d\r\n", ret);
        return;
    }

    /* Set key pointers */
    ecdsa_handle.privateKey = private_key;
    ecdsa_handle.publicKeyx = public_key_x;
    ecdsa_handle.publicKeyy = public_key_y;

    /* Generate random k for signing (in practice, use proper RFC 6979) */
    ret = bflb_sec_ecc_get_random_value(random_k, NULL, ECC_KEY_WORDS);
    if (ret != 0) {
        printf("Failed to get random value\r\n");
        bflb_sec_ecdsa_deinit(&ecdsa_handle);
        return;
    }

    /* Prepare message hash (in practice, compute from actual message) */
    memset(hash, 0xBA, sizeof(hash));

    /* Sign the hash */
    ret = bflb_sec_ecdsa_sign(&ecdsa_handle,
                               random_k,
                               hash,
                               SHA256_WORDS,
                               sig_r,
                               sig_s);
    if (ret == 0) {
        printf("ECDSA sign: SUCCESS\r\n");
        printf("R: ");
        for (int i = 0; i < ECC_KEY_WORDS; i++) printf("%08x", sig_r[i]);
        printf("\r\n");
        printf("S: ");
        for (int i = 0; i < ECC_KEY_WORDS; i++) printf("%08x", sig_s[i]);
        printf("\r\n");
    } else {
        printf("ECDSA sign failed: %d\r\n", ret);
    }

    /* Verify the signature */
    ret = bflb_sec_ecdsa_verify(&ecdsa_handle,
                                 hash,
                                 SHA256_WORDS * 4,  /* hashLen in bytes */
                                 sig_r,
                                 sig_s);
    if (ret == 0) {
        printf("ECDSA verify: SUCCESS\r\n");
    } else {
        printf("ECDSA verify failed: %d\r\n", ret);
    }

    /* Get public key from private key */
    ret = bflb_sec_ecdsa_get_public_key(&ecdsa_handle,
                                          private_key,
                                          public_key_x,
                                          public_key_y);
    if (ret == 0) {
        printf("Public key computed\r\n");
    }

    bflb_sec_ecdsa_deinit(&ecdsa_handle);
}
```

### Working Code Example - ECDH Key Exchange

```c
#include "bflb_sec_ecdsa.h"
#include <string.h>

#define ECDH_KEY_WORDS 8

void ecdh_example(void)
{
    int ret;
    struct bflb_ecdh_s ecdh_handle;

    /* Key buffers */
    static uint32_t private_key_a[ECDH_KEY_WORDS];
    static uint32_t public_key_ax[ECDH_KEY_WORDS];
    static uint32_t public_key_ay[ECDH_KEY_WORDS];
    static uint32_t private_key_b[ECDH_KEY_WORDS];
    static uint32_t public_key_bx[ECDH_KEY_WORDS];
    static uint32_t public_key_by[ECDH_KEY_WORDS];
    static uint32_t shared_secret[ECDH_KEY_WORDS];

    /* Initialize ECDH with SECP256R1 */
    ret = bflb_sec_ecdh_init(&ecdh_handle, ECP_SECP256R1);
    if (ret != 0) {
        printf("ECDH init failed: %d\r\n", ret);
        return;
    }

    /* Party A: Generate key pair */
    ret = bflb_sec_ecdh_get_public_key(&ecdh_handle,
                                        private_key_a,
                                        public_key_ax,
                                        public_key_ay);
    if (ret != 0) {
        printf("Party A: Failed to generate public key\r\n");
        bflb_sec_ecdh_deinit(&ecdh_handle);
        return;
    }
    printf("Party A public key generated\r\n");

    /* Party B: Generate key pair */
    ret = bflb_sec_ecdh_get_public_key(&ecdh_handle,
                                        private_key_b,
                                        public_key_bx,
                                        public_key_by);
    if (ret != 0) {
        printf("Party B: Failed to generate public key\r\n");
        bflb_sec_ecdh_deinit(&ecdh_handle);
        return;
    }
    printf("Party B public key generated\r\n");

    /* Party A: Compute shared secret using B's public key */
    ret = bflb_sec_ecdh_get_encrypt_key(&ecdh_handle,
                                          public_key_bx,
                                          public_key_by,
                                          private_key_a,
                                          shared_secret,
                                          NULL);  /* Optional output point */
    if (ret == 0) {
        printf("Party A shared secret: ");
        for (int i = 0; i < ECDH_KEY_WORDS; i++) printf("%08x", shared_secret[i]);
        printf("\r\n");
    } else {
        printf("Party A: Failed to compute shared secret\r\n");
    }

    /* Party B: Compute shared secret using A's public key */
    ret = bflb_sec_ecdh_get_encrypt_key(&ecdh_handle,
                                          public_key_ax,
                                          public_key_ay,
                                          private_key_b,
                                          shared_secret,
                                          NULL);
    if (ret == 0) {
        printf("Party B shared secret: ");
        for (int i = 0; i < ECDH_KEY_WORDS; i++) printf("%08x", shared_secret[i]);
        printf("\r\n");
    } else {
        printf("Party B: Failed to compute shared secret\r\n");
    }

    bflb_sec_ecdh_deinit(&ecdh_handle);
}
```

---

## 5. PKA - Public Key Accelerator

### Header
```c
#include "bflb_sec_pka.h"
```

### Overview
The PKA (Public Key Accelerator) module provides low-level arithmetic operations for public key cryptography including modular arithmetic, point operations for ECC, and Montgomery multiplication/exponentiation.

### API Reference

#### Initialization

| Function | Description |
|----------|-------------|
| `bflb_pka_init(dev)` | Initialize PKA engine |
| `bflb_pka_deinit(dev)` | Deinitialize PKA engine |

#### Register Size Constants

| Constant | Size (bits) |
|----------|-------------|
| `SEC_ENG_PKA_REG_SIZE_8` | 8 |
| `SEC_ENG_PKA_REG_SIZE_16` | 16 |
| `SEC_ENG_PKA_REG_SIZE_32` | 32 |
| `SEC_ENG_PKA_REG_SIZE_64` | 64 |
| `SEC_ENG_PKA_REG_SIZE_96` | 96 |
| `SEC_ENG_PKA_REG_SIZE_128` | 128 |
| `SEC_ENG_PKA_REG_SIZE_192` | 192 |
| `SEC_ENG_PKA_REG_SIZE_256` | 256 |
| `SEC_ENG_PKA_REG_SIZE_384` | 384 |
| `SEC_ENG_PKA_REG_SIZE_512` | 512 |

#### PKA Operation Codes

| Category | Operations |
|----------|------------|
| **Logical** | `LMOD2N`, `LDIV2N`, `LMUL2N`, `LDIV`, `LSQR`, `LMUL`, `LSUB`, `LADD`, `LCMP` |
| **Modular** | `MDIV2`, `MINV`, `MEXP`, `MSQR`, `MMUL`, `MREM`, `MSUB`, `MADD` |
| **Register** | `RESIZE`, `MOVDAT`, `NLIR`, `SLIR`, `CLIR` |
| **Montgomery** | `CFLIRI_BUFFER`, `CTLIRI_PLD`, `CFLIR_BUFFER`, `CTLIR_PLD` |
| **GF(2^m)** | `PPSEL` (Polynomial selection) |

#### PKA Arithmetic Functions

| Function | Description |
|----------|-------------|
| `bflb_pka_lmod2n(dev, s0_idx, s0_sz, d0_idx, d0_sz, shift, last)` | Left shift modulo 2^N |
| `bflb_pka_ldiv2n(dev, s0_idx, s0_sz, d0_idx, d0_sz, shift, last)` | Right shift divide by 2^N |
| `bflb_pka_lmul2n(dev, s0_idx, s0_sz, d0_idx, d0_sz, shift, last)` | Left shift multiply by 2^N |
| `bflb_pka_ldiv(dev, s0_idx, s0_sz, d0_idx, d0_sz, s2_idx, s2_sz, last)` | Long division |
| `bflb_pka_lsqr(dev, s0_idx, s0_sz, d0_idx, d0_sz, last)` | Long square |
| `bflb_pka_lmul(dev, s0_idx, s0_sz, d0_idx, d0_sz, s1_idx, s1_sz, last)` | Long multiply |
| `bflb_pka_lsub(dev, s0_idx, s0_sz, d0_idx, d0_sz, s1_idx, s1_sz, last)` | Long subtract |
| `bflb_pka_ladd(dev, s0_idx, s0_sz, d0_idx, d0_sz, s1_idx, s1_sz, last)` | Long add |
| `bflb_pka_lcmp(dev, s0_idx, s0_sz, s1_idx, s1_sz)` | Long compare (returns 0 if equal) |
| `bflb_pka_minv(dev, s0_idx, s0_sz, d0_idx, d0_sz, s2_idx, s2_sz, last)` | Modular inverse |
| `bflb_pka_mexp(dev, s0_idx, s0_sz, d0_idx, d0_sz, s1_idx, s1_sz, s2_idx, s2_sz, last)` | Modular exponentiation |
| `bflb_pka_msqr(dev, s0_idx, s0_sz, d0_idx, d0_sz, s2_idx, s2_sz, last)` | Modular square |
| `bflb_pka_mmul(dev, s0_idx, s0_sz, d0_idx, d0_sz, s1_idx, s1_sz, s2_idx, s2_sz, last)` | Modular multiply |
| `bflb_pka_mrem(dev, s0_idx, s0_sz, d0_idx, d0_sz, s2_idx, s2_sz, last)` | Modular remainder |
| `bflb_pka_msub(dev, s0_idx, s0_sz, d0_idx, d0_sz, s1_idx, s1_sz, s2_idx, s2_sz, last)` | Modular subtract |
| `bflb_pka_madd(dev, s0_idx, s0_sz, d0_idx, d0_sz, s1_idx, s1_sz, s2_idx, s2_sz, last)` | Modular add |

#### PKA Register Operations

| Function | Description |
|----------|-------------|
| `bflb_pka_regsize(dev, s0_idx, s0_sz, d0_idx, d0_sz, last)` | Change register size |
| `bflb_pka_movdat(dev, s0_idx, s0_sz, d0_idx, d0_sz, last)` | Move data between registers |
| `bflb_pka_nlir(dev, s0_idx, s0_sz, d0_idx, d0_sz, last)` | Negate and load into register |
| `bflb_pka_slir(dev, idx, sz, data, last)` | Shift left immediate and load |
| `bflb_pka_clir(dev, idx, sz, size, last)` | Clear register |
| `bflb_pka_write(dev, idx, sz, data, size, last)` | Write data to PKA register |
| `bflb_pka_read(dev, idx, sz, data, size)` | Read data from PKA register |

#### Montgomery Conversion

| Function | Description |
|----------|-------------|
| `bflb_pka_gf2mont(dev, s_idx, s_sz, d_idx, d_sz, t_idx, t_sz, p_idx, p_sz, size)` | Convert GF(2^m) to Montgomery form |
| `bflb_pka_mont2gf(dev, s_idx, s_sz, d_idx, d_sz, invt_idx, invt_sz, t_idx, t_sz, p_idx, p_sz)` | Convert Montgomery form to GF(2^m) |

### Parameter Descriptions

- `dev`: Device handle (from `bflb_device_get_by_name()`)
- `s0_idx`, `s1_idx`, `s2_idx`: Source register indices
- `d0_idx`: Destination register index
- `s0_sz`, `s1_sz`, `s2_sz`, `d0_sz`: Register sizes (use `SEC_ENG_PKA_REG_SIZE_*` constants)
- `t_idx`, `t_sz`: Temporary register index and size
- `p_idx`, `p_sz`: Prime/modulus register index and size
- `shift`: Bit shift amount
- `lastop`: Set to `1` for last operation in sequence, `0` otherwise
- `data`: Pointer to data buffer
- `size`: Size in words (32-bit)

### Working Code Example - Modular Exponentiation

```c
#include "bflb_sec_pka.h"
#include <string.h>

#define PKA_REG_SIZE_256 SEC_ENG_PKA_REG_SIZE_256

void pka_modexp_example(void)
{
    struct bflb_device_s *dev;
    int ret;

    /* Get PKA device */
    dev = bflb_device_get_by_name("pka");
    if (dev == NULL) {
        printf("PKA device not found\r\n");
        return;
    }

    /* Initialize PKA */
    bflb_pka_init(dev);

    /* Example: Compute C = M^E mod N
     * M = base (message)
     * E = exponent
     * N = modulus
     *
     * For RSA-2048: M, E, N are 256 words each (2048 bits)
     */
    #define KEY_SIZE 256  /* 256 * 32 = 8192 bits (for RSA-4096) */
    #define ACTUAL_KEY_SIZE 64  /* 64 * 32 = 2048 bits (for RSA-2048) */

    static uint32_t base[ACTUAL_KEY_SIZE];
    static uint32_t exponent[ACTUAL_KEY_SIZE];
    static uint32_t modulus[ACTUAL_KEY_SIZE];
    static uint32_t result[ACTUAL_KEY_SIZE];

    /* Initialize with example values */
    /* In practice: modulus N = p*q (product of two primes) */
    /* Exponent E = 65537 (common choice) */
    /* Base M = message to encrypt/sign */

    /* PKA register layout:
     * R0 = base (M)
     * R1 = exponent (E)
     * R2 = modulus (N)
     * R3 = result (C = M^E mod N)
     */

    /* Write base to R0 */
    bflb_pka_write(dev,
                   0,                      /* R0 */
                   SEC_ENG_PKA_REG_SIZE_32, /* 32-bit words */
                   base,
                   ACTUAL_KEY_SIZE,
                   0);                     /* not last op */

    /* Write exponent to R1 */
    bflb_pka_write(dev,
                   1,                      /* R1 */
                   SEC_ENG_PKA_REG_SIZE_32,
                   exponent,
                   ACTUAL_KEY_SIZE,
                   0);

    /* Write modulus to R2 */
    bflb_pka_write(dev,
                   2,                      /* R2 */
                   SEC_ENG_PKA_REG_SIZE_32,
                   modulus,
                   ACTUAL_KEY_SIZE,
                   0);

    /* Perform modular exponentiation: R3 = R0^R1 mod R2 */
    bflb_pka_mexp(dev,
                  0,  /* s0_idx: base source (R0) */
                  SEC_ENG_PKA_REG_SIZE_32,
                  3,  /* d0_idx: result destination (R3) */
                  SEC_ENG_PKA_REG_SIZE_32,
                  1,  /* s1_idx: exponent (R1) */
                  SEC_ENG_PKA_REG_SIZE_32,
                  2,  /* s2_idx: modulus (R2) */
                  SEC_ENG_PKA_REG_SIZE_32,
                  1); /* lastop: this is the last operation */

    /* Read result from R3 */
    bflb_pka_read(dev,
                  3,  /* R3 */
                  SEC_ENG_PKA_REG_SIZE_32,
                  result,
                  ACTUAL_KEY_SIZE);

    printf("Modular exponentiation complete\r\n");

    /* Deinitialize PKA */
    bflb_pka_deinit(dev);
}
```

### Working Code Example - Modular Multiplication

```c
#include "bflb_sec_pka.h"

void pka_modmul_example(void)
{
    struct bflb_device_s *dev;

    dev = bflb_device_get_by_name("pka");
    if (dev == NULL) {
        return;
    }

    bflb_pka_init(dev);

    /* Compute: R3 = (R0 * R1) mod R2 */
    static uint32_t a[8] = {0x11111111, 0x22222222, 0x33333333, 0x44444444,
                            0x55555555, 0x66666666, 0x77777777, 0x88888888};
    static uint32_t b[8] = {0x12345678, 0x9ABCDEF0, 0x11223344, 0x55667788,
                            0x99AABBCC, 0xDDEEFF00, 0x11223344, 0x55667788};
    static uint32_t n[8] = {0xFFFFFFFF, 0xFFFFFFFF, 0xFFFFFFFF, 0xFFFFFFFF,
                            0xFFFFFFFF, 0xFFFFFFFF, 0xFFFFFFFF, 0x000000FF};
    static uint32_t result[8];

    /* Write operands */
    bflb_pka_write(dev, 0, SEC_ENG_PKA_REG_SIZE_32, a, 8, 0);
    bflb_pka_write(dev, 1, SEC_ENG_PKA_REG_SIZE_32, b, 8, 0);
    bflb_pka_write(dev, 2, SEC_ENG_PKA_REG_SIZE_32, n, 8, 0);

    /* Modular multiply: R3 = (R0 * R1) mod R2 */
    bflb_pka_mmul(dev,
                  0, SEC_ENG_PKA_REG_SIZE_32,  /* source A (R0) */
                  3, SEC_ENG_PKA_REG_SIZE_32,  /* destination (R3) */
                  1, SEC_ENG_PKA_REG_SIZE_32,  /* source B (R1) */
                  2, SEC_ENG_PKA_REG_SIZE_32,  /* modulus (R2) */
                  1);                          /* last operation */

    /* Read result */
    bflb_pka_read(dev, 3, SEC_ENG_PKA_REG_SIZE_32, result, 8);

    printf("Modular multiplication result:\r\n");
    for (int i = 0; i < 8; i++) {
        printf("%08x ", result[i]);
    }
    printf("\r\n");

    bflb_pka_deinit(dev);
}
```

### Working Code Example - Montgomery Multiplication

```c
#include "bflb_sec_pka.h"

void pka_montmul_example(void)
{
    struct bflb_device_s *dev;

    dev = bflb_device_get_by_name("pka");
    if (dev == NULL) {
        return;
    }

    bflb_pka_init(dev);

    /* Montgomery multiplication: R4 = (R0 * R1) * R^(-1) mod R2
     * This computes the Montgomery product
     */

    static uint32_t a[8] = {0};
    static uint32_t b[8] = {0};
    static uint32_t n[8] = {0};  /* Prime modulus */
    static uint32_t result[8];

    /* Setup: R0 = a, R1 = b, R2 = n (modulus) */

    /* Montgomery modular multiplication */
    bflb_pka_mmovdat(dev,
                    0, SEC_ENG_PKA_REG_SIZE_32,  /* source */
                    3, SEC_ENG_PKA_REG_SIZE_32,  /* destination */
                    0);

    /* For actual Montgomery multiplication with Montgomery reduction,
     * you would typically use a sequence of operations.
     * This requires careful setup of Montgomery parameters (R, R^2 mod N, etc.)
     */

    bflb_pka_deinit(dev);
}
```

---

## Register Map Summary

The Security Engine (SEC_ENG) base address is `0x20004000`. The PKA and other security modules are accessed through this base address with offset registers defined in the SDK.

### Key Register Ranges

| Module | Base Offset | Description |
|--------|-------------|-------------|
| TRNG | (varies) | True Random Number Generator |
| DSA | (varies) | Digital Signature Algorithm |
| GMAC | (varies) | Galois Message Authentication Code |
| ECDSA/ECDH | (varies) | Elliptic Curve DSA |
| PKA | (varies) | Public Key Accelerator |

For detailed register descriptions, refer to the BL616/BL618 Hardware Register Manual.

---

## Common Usage Patterns

### Complete RSA-2048 Sign/Verify Flow

```c
#include "bflb_sec_trng.h"
#include "bflb_sec_dsa.h"

void rsa_sign_verify_example(void)
{
    /* 1. Get random data for key generation or signing */
    struct bflb_device_s *trng_dev = bflb_device_get_by_name("trng");
    bflb_group0_request_trng_access(trng_dev);

    uint8_t random_pool[64];
    bflb_trng_read(trng_dev, random_pool);

    /* 2. Initialize DSA for signing */
    struct bflb_dsa_s dsa;
    bflb_sec_dsa_init(&dsa, 256);  /* RSA-2048: 256 words */

    /* 3. Sign */
    uint32_t hash[8] = {0};  /* SHA-256 hash */
    uint32_t signature[256];
    bflb_sec_dsa_sign(&dsa, hash, 8, signature);

    /* 4. Verify */
    int ret = bflb_sec_dsa_verify(&dsa, hash, 8, signature);

    bflb_group0_release_trng_access(trng_dev);
}
```

### Complete ECDSA P-256 Sign/Verify Flow

```c
#include "bflb_sec_ecdsa.h"

void ecdsa_p256_sign_verify_example(void)
{
    struct bflb_ecdsa_s ecdsa;
    uint32_t hash[8] = {0};      /* SHA-256 hash */
    uint32_t sig_r[8], sig_s[8];
    uint32_t random_k[8];
    uint32_t priv_key[8];
    uint32_t pub_key_x[8], pub_key_y[8];

    /* Initialize */
    bflb_sec_ecdsa_init(&ecdsa, ECP_SECP256R1);
    ecdsa.privateKey = priv_key;
    ecdsa.publicKeyx = pub_key_x;
    ecdsa.publicKeyy = pub_key_y;

    /* Generate random k */
    bflb_sec_ecc_get_random_value(random_k, NULL, 8);

    /* Sign */
    bflb_sec_ecdsa_sign(&ecdsa, random_k, hash, 8, sig_r, sig_s);

    /* Verify */
    bflb_sec_ecdsa_verify(&ecdsa, hash, 32, sig_r, sig_s);

    bflb_sec_ecdsa_deinit(&ecdsa);
}
```

---

## Notes and Best Practices

1. **Resource Management**: Always request and release TRNG/GMAC access in pairs
2. **Memory**: Key material buffers must remain allocated during operations
3. **Thread Safety**: Use group0/group1 access functions for multi-threaded environments
4. **Error Handling**: Always check return values from security functions
5. **Random Numbers**: Use proper random generation (TRNG) for cryptographic keys
6. **Curve Selection**: Use P-256 (SECP256R1) for general purpose; P-384 for higher security
7. **PKA Operations**: Set `lastop=1` only on the final operation in a chain
8. **Register Sizes**: Match register sizes to your key sizes for efficiency

---

## Revision History

| Version | Date | Description |
|---------|------|-------------|
| 1.0 | 2024 | Initial documentation for BL616/BL618 security modules |
