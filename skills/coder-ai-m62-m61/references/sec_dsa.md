# SEC_DSA API Reference (BL616/BL618)

> **Source:** `bouffalo_sdk/drivers/lhal/include/bflb_sec_dsa.h`  
> **Implementation:** `bouffalo_sdk/drivers/lhal/src/pka/libpka_bl616.a` (pre-compiled PKA library)  
> **Hardware:** SEC_ENG PKA (Public Key Accelerator) @ `0x20004300`  
> **Register Header:** `bouffalo_sdk/drivers/lhal/include/hardware/sec_eng_reg.h`

## Overview

The SEC_DSA module provides digital signature and verification functionality based on **DSA (Digital Signature Algorithm)**. It leverages the **PKA (Public Key Accelerator)** hardware accelerator in SEC_ENG (Security Engine) for large-number modular exponentiation, supporting CRT (Chinese Remainder Theorem) optimized RSA/DSA private key operations.

**Key Features:**
- Hardware PKA-based large-number modular exponentiation acceleration
- DSA signature generation (`bflb_sec_dsa_sign`)
- DSA signature verification (`bflb_sec_dsa_verify`)
- CRT mode support for accelerating private key operations (`bflb_dsa_crt_s`)
- Configurable key length (`size` / `crtSize`)
- Implemented via the `libpka_bl616.a` pre-compiled library

## Base Address

| Peripheral | Offset | Address |
|------------|--------|---------|
| SEC_ENG_BASE | — | `0x20004000` |
| SEC_ENG PKA | `0x300` | `0x20004300` |

---

## Configuration Structures

### bflb_dsa_s

DSA key and operation handle.

```c
struct bflb_dsa_s {
    uint32_t size;               // Key size (in 32-bit words)
    uint32_t crtSize;            // CRT parameter size (in 32-bit words)
    uint32_t *n;                 // Modulus n pointer
    uint32_t *e;                 // Public key exponent e pointer
    uint32_t *d;                 // Private key exponent d pointer
    struct bflb_dsa_crt_s crtCfg; // CRT configuration
};
```

| Field | Type | Description |
|-------|------|-------------|
| `size` | `uint32_t` | Key size (in 32-bit words) |
| `crtSize` | `uint32_t` | CRT parameter size (in 32-bit words) |
| `n` | `uint32_t *` | Modulus n (shared by public and private keys) |
| `e` | `uint32_t *` | Public key exponent e |
| `d` | `uint32_t *` | Private key exponent d |
| `crtCfg` | `struct bflb_dsa_crt_s` | CRT acceleration parameter configuration |

### bflb_dsa_crt_s

CRT (Chinese Remainder Theorem) parameter structure for accelerating private key operations.

```c
struct bflb_dsa_crt_s {
    uint32_t *dP;        // CRT exponent d mod (p-1)
    uint32_t *dQ;        // CRT exponent d mod (q-1)
    uint32_t *qInv;      // Modular inverse of q: q^(-1) mod p
    uint32_t *p;         // Prime p
    uint32_t *invR_p;    // Inverse of Montgomery R mod p
    uint32_t *primeN_p;  // Prime N of p (Montgomery parameter)
    uint32_t *q;         // Prime q
    uint32_t *invR_q;    // Inverse of Montgomery R mod q
    uint32_t *primeN_q;  // Prime N of q (Montgomery parameter)
};
```

---

## LHAL API Functions

### bflb_sec_dsa_init

Initialize the DSA handle, allocate hardware PKA resources, and configure key parameters.

```c
int bflb_sec_dsa_init(struct bflb_dsa_s *handle, uint32_t size);
```

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `handle` | `struct bflb_dsa_s *` | DSA handle pointer (with key parameters) |
| `size` | `uint32_t` | Key length (in 32-bit words) |

**Returns:** `0` on success, negative value on error

**Note:** Before calling, populate key parameters such as `handle->n`, `handle->e`, `handle->d`, and `handle->crtCfg`.

---

### bflb_sec_dsa_sign

Sign a message hash using the DSA private key.

```c
int bflb_sec_dsa_sign(struct bflb_dsa_s *handle, const uint32_t *hash,
                       uint32_t hashLenInWord, uint32_t *s);
```

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `handle` | `struct bflb_dsa_s *` | Initialized DSA handle |
| `hash` | `const uint32_t *` | Message hash value (32-bit word array) |
| `hashLenInWord` | `uint32_t` | Hash length (in 32-bit words) |
| `s` | `uint32_t *` | Output signature buffer |

**Returns:** `0` on success, negative value on error

---

### bflb_sec_dsa_verify

Verify a signature using the DSA public key.

```c
int bflb_sec_dsa_verify(struct bflb_dsa_s *handle, const uint32_t *hash,
                         uint32_t hashLenInWord, const uint32_t *s);
```

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `handle` | `struct bflb_dsa_s *` | Initialized DSA handle |
| `hash` | `const uint32_t *` | Message hash value (32-bit word array) |
| `hashLenInWord` | `uint32_t` | Hash length (in 32-bit words) |
| `s` | `const uint32_t *` | Signature to verify |

**Returns:** `0` verification passed, negative value on verification failure or error

---

## Usage Examples

### Example 1: DSA Sign & Verify (1024-bit)

```c
#include "bflb_sec_dsa.h"
#include "bflb_sha.h"  // for hash generation

void dsa_sign_verify_1024_example(void)
{
    struct bflb_dsa_s dsa_handle;
    int ret;

    // 1024-bit key = 32 32-bit words
    dsa_handle.size = 32;
    dsa_handle.crtSize = 16;  // CRT parameters are 512-bit each

    // Note: In real applications, keys should be loaded from secure storage
    // These are placeholder examples only
    uint32_t n[32]  = { /* modulus n */ };
    uint32_t e[32]  = { /* public key exponent e */ };
    uint32_t d[32]  = { /* private key exponent d */ };

    dsa_handle.n = n;
    dsa_handle.e = e;
    dsa_handle.d = d;

    // CRT parameters (optional, for accelerating private key operations)
    uint32_t p[16]     = { /* ... */ };
    uint32_t q[16]     = { /* ... */ };
    uint32_t dP[16]    = { /* ... */ };
    uint32_t dQ[16]    = { /* ... */ };
    uint32_t qInv[16]  = { /* ... */ };
    uint32_t invR_p[16] = { /* ... */ };
    uint32_t invR_q[16] = { /* ... */ };
    uint32_t primeN_p[16] = { /* ... */ };
    uint32_t primeN_q[16] = { /* ... */ };

    dsa_handle.crtCfg.p        = p;
    dsa_handle.crtCfg.q        = q;
    dsa_handle.crtCfg.dP       = dP;
    dsa_handle.crtCfg.dQ       = dQ;
    dsa_handle.crtCfg.qInv     = qInv;
    dsa_handle.crtCfg.invR_p   = invR_p;
    dsa_handle.crtCfg.invR_q   = invR_q;
    dsa_handle.crtCfg.primeN_p = primeN_p;
    dsa_handle.crtCfg.primeN_q = primeN_q;

    // Initialize DSA
    ret = bflb_sec_dsa_init(&dsa_handle, 32);
    if (ret != 0) {
        printf("DSA init failed: %d\n", ret);
        return;
    }

    // Prepare message hash
    uint8_t message[] = "Hello, DSA!";
    uint32_t hash[32] = {0};  // SHA-256 output
    // In real application: bflb_sha256(hash, message, sizeof(message));

    // Sign
    uint32_t signature[32] = {0};
    ret = bflb_sec_dsa_sign(&dsa_handle, hash, 8, signature);  // SHA-256 = 8 words
    if (ret == 0) {
        printf("DSA sign success\n");
    }

    // Verify
    ret = bflb_sec_dsa_verify(&dsa_handle, hash, 8, signature);
    if (ret == 0) {
        printf("DSA verify PASSED\n");
    } else {
        printf("DSA verify FAILED: %d\n", ret);
    }
}
```

### Example 2: Verify-only mode (using public key)

```c
#include "bflb_sec_dsa.h"

int dsa_verify_only_example(const uint32_t *hash, const uint32_t *signature)
{
    struct bflb_dsa_s dsa_handle;

    // Only public key needed for verification, private key can be NULL
    uint32_t n[32] = { /* public key modulus */ };
    uint32_t e[32] = { /* public key exponent */ };

    dsa_handle.size = 32;
    dsa_handle.n = n;
    dsa_handle.e = e;
    dsa_handle.d = NULL;  // Private key not needed for verify-only

    int ret = bflb_sec_dsa_init(&dsa_handle, 32);
    if (ret != 0) return ret;

    return bflb_sec_dsa_verify(&dsa_handle, hash, 8, signature);
}
```

---

## Register-Level Reference

DSA operations are performed through the SEC_ENG PKA subsystem. PKA registers are located at `SEC_ENG_BASE + 0x300`.

### PKA Register Offsets

| Offset | Register | Description |
|--------|----------|-------------|
| `0x300` | `SE_PKA_0_CTRL_0` | PKA Control Register 0 |
| `0x30C` | `SE_PKA_0_SEED` | PKA Random Seed |
| `0x310` | `SE_PKA_0_CTRL_1` | PKA Control Register 1 |
| `0x340` | `SE_PKA_0_RW` | PKA Data Read/Write Port |
| `0x360` | `SE_PKA_0_RW_BURST` | PKA Burst Data Read/Write Port |
| `0x3FC` | `SE_PKA_0_CTRL_PROT` | PKA Access Protection |

### PKA Control Register 0 (0x300)

| Bit(s) | Field | Description |
|--------|-------|-------------|
| 0 | `SE_PKA_0_DONE` | Operation complete flag |
| 1 | `SE_PKA_0_DONE_CLR_1T` | Write 1 to clear complete flag |
| 2 | `SE_PKA_0_BUSY` | PKA busy flag |
| 3 | `SE_PKA_0_EN` | PKA enable |
| 7:4 | `SE_PKA_0_PROT_MD` | Protection mode select |
| 8 | `SE_PKA_0_INT` | Interrupt flag |
| 9 | `SE_PKA_0_INT_CLR_1T` | Write 1 to clear interrupt |
| 10 | `SE_PKA_0_INT_SET` | Interrupt enable |
| 11 | `SE_PKA_0_INT_MASK` | Interrupt mask |
| 12 | `SE_PKA_0_ENDIAN` | Endian configuration |
| 13 | `SE_PKA_0_RAM_CLR_MD` | RAM clear mode |
| 15 | `SE_PKA_0_STATUS_CLR_1T` | Write 1 to clear status |
| 31:16 | `SE_PKA_0_STATUS` | PKA status code |

```c
#define SEC_ENG_SE_PKA_0_DONE          (1 << 0U)
#define SEC_ENG_SE_PKA_0_DONE_CLR_1T   (1 << 1U)
#define SEC_ENG_SE_PKA_0_BUSY          (1 << 2U)
#define SEC_ENG_SE_PKA_0_EN            (1 << 3U)
#define SEC_ENG_SE_PKA_0_PROT_MD_SHIFT (4U)
#define SEC_ENG_SE_PKA_0_PROT_MD_MASK  (0xf << 4U)
#define SEC_ENG_SE_PKA_0_INT           (1 << 8U)
#define SEC_ENG_SE_PKA_0_INT_CLR_1T    (1 << 9U)
#define SEC_ENG_SE_PKA_0_INT_SET       (1 << 10U)
#define SEC_ENG_SE_PKA_0_INT_MASK      (1 << 11U)
#define SEC_ENG_SE_PKA_0_ENDIAN        (1 << 12U)
#define SEC_ENG_SE_PKA_0_RAM_CLR_MD    (1 << 13U)
#define SEC_ENG_SE_PKA_0_STATUS_CLR_1T (1 << 15U)
```

### PKA Control Register 1 (0x310)

| Bit(s) | Field | Description |
|--------|-------|-------------|
| 2:0 | `SE_PKA_0_HBURST` | AHB burst transfer length |
| 3 | `SE_PKA_0_HBYPASS` | AHB bypass mode |

---

## Architecture Notes

- **Implementation:** DSA functionality is implemented via the pre-compiled library `libpka_bl616.a`; no public `.c` source is available
- **Hardware Dependency:** Depends on the PKA accelerator in SEC_ENG (`SEC_ENG_BASE + 0x300`)
- **ROM API:** Some chips support `romapi_bflb_sec_dsa_*` fast paths
- **CRT Optimization:** Populating `crtCfg` to enable CRT acceleration is recommended, as it can significantly improve private key signing performance
- **Key Management:** All key data is passed in as 32-bit word arrays; callers are responsible for secure storage
