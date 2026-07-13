# SEC_ECDSA API Reference (BL616/BL618)

> **Source:** `bouffalo_sdk/drivers/lhal/include/bflb_sec_ecdsa.h`  
> **Implementation:** `bouffalo_sdk/drivers/lhal/src/pka/libpka_bl616.a` (pre-compiled PKA library)  
> **Hardware:** SEC_ENG PKA (Public Key Accelerator) @ `0x20004300`  
> **Register Header:** `bouffalo_sdk/drivers/lhal/include/hardware/sec_eng_reg.h`

## Overview

The SEC_ECDSA module provides elliptic curve digital signature and verification based on **ECDSA (Elliptic Curve Digital Signature Algorithm)**, as well as **ECDH (Elliptic Curve Diffie-Hellman)** key exchange functionality. It leverages the **PKA (Public Key Accelerator)** hardware accelerator in SEC_ENG for elliptic curve point multiplication.

**Key Features:**
- ECDSA signature generation (`bflb_sec_ecdsa_sign`)
- ECDSA signature verification (`bflb_sec_ecdsa_verify`)
- ECDH key exchange (`bflb_sec_ecdh_get_encrypt_key`)
- Key pair generation and management (`bflb_sec_ecdsa_get_private_key`, `bflb_sec_ecdsa_get_public_key`)
- Hardware random number generation (`bflb_sec_ecc_get_random_value`)
- Support for multiple standard elliptic curves
- Implemented via the `libpka_bl616.a` pre-compiled library

## Base Address

| Peripheral | Offset | Address |
|------------|--------|---------|
| SEC_ENG_BASE | — | `0x20004000` |
| SEC_ENG PKA | `0x300` | `0x20004300` |

---

## Elliptic Curve Definitions

```c
#define ECP_SECP256R1 0    // NIST P-256 / secp256r1
#define ECP_SECP256K1 1    // secp256k1 (Bitcoin curve)
#define ECP_SECP384R1 2    // NIST P-384 / secp384r1 (requires ECP_SUPPORT_384=1)
```

| Macro | Value | Curve | Key Size |
|-------|-------|-------|----------|
| `ECP_SECP256R1` | 0 | NIST P-256 | 256-bit |
| `ECP_SECP256K1` | 1 | secp256k1 | 256-bit |
| `ECP_SECP384R1` | 2 | NIST P-384 | 384-bit |

> **Note:** `ECP_SECP384R1` is only available when `ECP_SUPPORT_384` is enabled (defined as 1).

---

## Configuration Structures

### bflb_ecdsa_s

ECDSA operation handle, holding key pointers and curve selection.

```c
struct bflb_ecdsa_s {
    uint8_t ecpId;           // Elliptic curve ID (ECP_SECP256R1 / ECP_SECP256K1 / ECP_SECP384R1)
    uint8_t pad[3];          // Alignment padding
    uint32_t *privateKey;    // Private key pointer (32-bit word array)
    uint32_t *publicKeyx;    // Public key X coordinate pointer
    uint32_t *publicKeyy;    // Public key Y coordinate pointer
};
```

| Field | Type | Description |
|-------|------|-------------|
| `ecpId` | `uint8_t` | Elliptic curve ID |
| `pad[3]` | `uint8_t[3]` | Memory alignment padding |
| `privateKey` | `uint32_t *` | Private key buffer pointer |
| `publicKeyx` | `uint32_t *` | Public key X coordinate buffer pointer |
| `publicKeyy` | `uint32_t *` | Public key Y coordinate buffer pointer |

### bflb_ecdh_s

ECDH key exchange handle.

```c
struct bflb_ecdh_s {
    uint8_t ecpId;    // Elliptic curve ID
};
```

| Field | Type | Description |
|-------|------|-------------|
| `ecpId` | `uint8_t` | Elliptic curve ID |

---

## LHAL API Functions

### ECDSA Functions

#### bflb_sec_ecdsa_init

Initialize the ECDSA handle and allocate PKA hardware resources.

```c
int bflb_sec_ecdsa_init(struct bflb_ecdsa_s *handle, uint8_t id);
```

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `handle` | `struct bflb_ecdsa_s *` | ECDSA handle pointer |
| `id` | `uint8_t` | Elliptic curve ID (`ECP_SECP256R1`, etc.) |

**Returns:** `0` on success, negative value on error

---

#### bflb_sec_ecdsa_deinit

Release PKA hardware resources held by the ECDSA handle.

```c
int bflb_sec_ecdsa_deinit(struct bflb_ecdsa_s *handle);
```

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `handle` | `struct bflb_ecdsa_s *` | ECDSA handle pointer |

**Returns:** `0` on success, negative value on error

---

#### bflb_sec_ecdsa_sign

Sign a message hash using the ECDSA private key.

```c
int bflb_sec_ecdsa_sign(struct bflb_ecdsa_s *handle, const uint32_t *random_k,
                         const uint32_t *hash, uint32_t hashLenInWord,
                         uint32_t *r, uint32_t *s);
```

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `handle` | `struct bflb_ecdsa_s *` | Initialized ECDSA handle |
| `random_k` | `const uint32_t *` | Random number k required for ECDSA signing |
| `hash` | `const uint32_t *` | Message hash value (32-bit word array) |
| `hashLenInWord` | `uint32_t` | Hash length (in 32-bit words) |
| `r` | `uint32_t *` | Output: signature r component |
| `s` | `uint32_t *` | Output: signature s component |

**Returns:** `0` on success, negative value on error

**Note:** `random_k` must be a secure random number and must be unique for each signature. It can be generated using `bflb_sec_ecc_get_random_value()`.

---

#### bflb_sec_ecdsa_verify

Verify a signature using the ECDSA public key.

```c
int bflb_sec_ecdsa_verify(struct bflb_ecdsa_s *handle, const uint32_t *hash,
                           uint32_t hashLen, const uint32_t *r, const uint32_t *s);
```

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `handle` | `struct bflb_ecdsa_s *` | Initialized ECDSA handle |
| `hash` | `const uint32_t *` | Message hash value |
| `hashLen` | `uint32_t` | Hash length (in 32-bit words) |
| `r` | `const uint32_t *` | Signature r component |
| `s` | `const uint32_t *` | Signature s component |

**Returns:** `0` verification passed, negative value on verification failure

---

#### bflb_sec_ecdsa_get_private_key

Get or generate an ECDSA private key.

```c
int bflb_sec_ecdsa_get_private_key(struct bflb_ecdsa_s *handle, uint32_t *private_key);
```

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `handle` | `struct bflb_ecdsa_s *` | Initialized ECDSA handle |
| `private_key` | `uint32_t *` | Output buffer (receives the private key) |

**Returns:** `0` on success

---

#### bflb_sec_ecdsa_get_public_key

Compute the ECDSA public key from the private key.

```c
int bflb_sec_ecdsa_get_public_key(struct bflb_ecdsa_s *handle,
                                   const uint32_t *private_key,
                                   const uint32_t *pRx, const uint32_t *pRy);
```

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `handle` | `struct bflb_ecdsa_s *` | Initialized ECDSA handle |
| `private_key` | `const uint32_t *` | Private key |
| `pRx` | `const uint32_t *` | Output: public key X coordinate |
| `pRy` | `const uint32_t *` | Output: public key Y coordinate |

**Returns:** `0` on success

> **Note:** Parameters are declared as `const uint32_t *` but are actually used for output. Pass writable buffers when calling.

---

### ECDH Functions

#### bflb_sec_ecdh_init

Initialize the ECDH key exchange handle.

```c
int bflb_sec_ecdh_init(struct bflb_ecdh_s *handle, uint8_t id);
```

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `handle` | `struct bflb_ecdh_s *` | ECDH handle pointer |
| `id` | `uint8_t` | Elliptic curve ID |

**Returns:** `0` on success

---

#### bflb_sec_ecdh_deinit

Release ECDH handle resources.

```c
int bflb_sec_ecdh_deinit(struct bflb_ecdh_s *handle);
```

**Returns:** `0` on success

---

#### bflb_sec_ecdh_get_encrypt_key

Perform ECDH key exchange and compute the shared key.

```c
int bflb_sec_ecdh_get_encrypt_key(struct bflb_ecdh_s *handle,
                                   const uint32_t *pkX, const uint32_t *pkY,
                                   const uint32_t *private_key,
                                   const uint32_t *pRx, const uint32_t *pRy);
```

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `handle` | `struct bflb_ecdh_s *` | ECDH handle |
| `pkX` | `const uint32_t *` | Peer's public key X coordinate |
| `pkY` | `const uint32_t *` | Peer's public key Y coordinate |
| `private_key` | `const uint32_t *` | Own private key |
| `pRx` | `const uint32_t *` | Output: shared key X coordinate |
| `pRy` | `const uint32_t *` | Output: shared key Y coordinate |

**Returns:** `0` on success

---

#### bflb_sec_ecdh_get_public_key

Compute the ECDH public key from the private key.

```c
int bflb_sec_ecdh_get_public_key(struct bflb_ecdh_s *handle,
                                  const uint32_t *private_key,
                                  const uint32_t *pRx, const uint32_t *pRy);
```

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `handle` | `struct bflb_ecdh_s *` | ECDH handle |
| `private_key` | `const uint32_t *` | Private key |
| `pRx` | `const uint32_t *` | Output: public key X coordinate |
| `pRy` | `const uint32_t *` | Output: public key Y coordinate |

**Returns:** `0` on success

---

### Random Number Generation

#### bflb_sec_ecc_get_random_value

Generate a secure random number for ECC (used for signature random k, etc.).

```c
int bflb_sec_ecc_get_random_value(uint32_t *data, uint32_t *max_ref, uint32_t size);
```

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `data` | `uint32_t *` | Output random number buffer |
| `max_ref` | `uint32_t *` | Maximum value reference (generated random < max_ref) |
| `size` | `uint32_t` | Data size (in 32-bit words) |

**Returns:** `0` on success

**Note:** This function is used to generate the random number k required for ECDSA signing. Typically, `max_ref` is set to the elliptic curve's order n.

---

## Usage Examples

### Example 1: ECDSA Sign & Verify (secp256r1)

```c
#include "bflb_sec_ecdsa.h"
#include "bflb_sha.h"

void ecdsa_sign_verify_example(void)
{
    struct bflb_ecdsa_s ecdsa;
    int ret;

    // P-256: private/public key each 256-bit = 8 32-bit words
    uint32_t private_key[8] = {0};
    uint32_t public_key_x[8] = {0};
    uint32_t public_key_y[8] = {0};

    // Initialize ECDSA (secp256r1)
    ret = bflb_sec_ecdsa_init(&ecdsa, ECP_SECP256R1);
    if (ret != 0) {
        printf("ECDSA init failed: %d\n", ret);
        return;
    }

    // Generate key pair
    ret = bflb_sec_ecdsa_get_private_key(&ecdsa, private_key);
    if (ret != 0) {
        printf("Generate private key failed\n");
        return;
    }

    ret = bflb_sec_ecdsa_get_public_key(&ecdsa, private_key, public_key_x, public_key_y);
    if (ret != 0) {
        printf("Generate public key failed\n");
        return;
    }

    // Set keys in handle
    ecdsa.privateKey = private_key;
    ecdsa.publicKeyx = public_key_x;
    ecdsa.publicKeyy = public_key_y;

    // Prepare message hash (SHA-256 = 8 words)
    uint8_t message[] = "ECDSA test message";
    uint32_t hash[8] = {0};
    // bflb_sha256(hash, message, sizeof(message));

    // Generate signature random number k
    // Note: secp256r1 order n must be obtained from standard documents; shown here for illustration
    uint32_t n_order[8] = {
        0xFFFFFFFF, 0x00000000, 0xFFFFFFFF, 0xFFFFFFFF,
        0xBCE6FAAD, 0xA7179E84, 0xF3B9CAC2, 0xFC632551
    };
    uint32_t random_k[8] = {0};

    ret = bflb_sec_ecc_get_random_value(random_k, n_order, 8);
    if (ret != 0) {
        printf("Random generation failed\n");
        return;
    }

    // ECDSA sign
    uint32_t r[8] = {0};
    uint32_t s[8] = {0};

    ret = bflb_sec_ecdsa_sign(&ecdsa, random_k, hash, 8, r, s);
    if (ret == 0) {
        printf("ECDSA sign success\n");
        printf("r: 0x%08X...\n", r[0]);
        printf("s: 0x%08X...\n", s[0]);
    } else {
        printf("ECDSA sign failed: %d\n", ret);
    }

    // ECDSA verify
    ret = bflb_sec_ecdsa_verify(&ecdsa, hash, 8, r, s);
    if (ret == 0) {
        printf("ECDSA verify PASSED\n");
    } else {
        printf("ECDSA verify FAILED: %d\n", ret);
    }

    // Release resources
    bflb_sec_ecdsa_deinit(&ecdsa);
}
```

### Example 2: ECDH Key Exchange

```c
#include "bflb_sec_ecdsa.h"

void ecdh_key_exchange_example(void)
{
    struct bflb_ecdh_s ecdh_a;  // Party A
    struct bflb_ecdh_s ecdh_b;  // Party B
    int ret;

    // P-256: 256-bit keys = 8 words
    uint32_t priv_a[8] = {0}, pub_ax[8] = {0}, pub_ay[8] = {0};
    uint32_t priv_b[8] = {0}, pub_bx[8] = {0}, pub_by[8] = {0};
    uint32_t shared_ax[8] = {0}, shared_ay[8] = {0};
    uint32_t shared_bx[8] = {0}, shared_by[8] = {0};

    // Initialize ECDH for both parties
    bflb_sec_ecdh_init(&ecdh_a, ECP_SECP256R1);
    bflb_sec_ecdh_init(&ecdh_b, ECP_SECP256R1);

    // Party A generates key pair
    bflb_sec_ecc_get_random_value(priv_a, (uint32_t[8]){
        0xFFFFFFFF, 0x00000000, 0xFFFFFFFF, 0xFFFFFFFF,
        0xBCE6FAAD, 0xA7179E84, 0xF3B9CAC2, 0xFC632551
    }, 8);
    bflb_sec_ecdh_get_public_key(&ecdh_a, priv_a, pub_ax, pub_ay);

    // Party B generates key pair
    bflb_sec_ecc_get_random_value(priv_b, (uint32_t[8]){
        0xFFFFFFFF, 0x00000000, 0xFFFFFFFF, 0xFFFFFFFF,
        0xBCE6FAAD, 0xA7179E84, 0xF3B9CAC2, 0xFC632551
    }, 8);
    bflb_sec_ecdh_get_public_key(&ecdh_b, priv_b, pub_bx, pub_by);

    // ECDH: Party A uses B's public key + A's private key to compute shared key
    ret = bflb_sec_ecdh_get_encrypt_key(&ecdh_a, pub_bx, pub_by,
                                         priv_a, shared_ax, shared_ay);
    if (ret == 0) printf("A: ECDH shared key computed\n");

    // ECDH: Party B uses A's public key + B's private key to compute shared key
    ret = bflb_sec_ecdh_get_encrypt_key(&ecdh_b, pub_ax, pub_ay,
                                         priv_b, shared_bx, shared_by);
    if (ret == 0) printf("B: ECDH shared key computed\n");

    // Verify shared keys match (shared_ax == shared_bx)
    bool match = (memcmp(shared_ax, shared_bx, 32) == 0);
    printf("Shared key match: %s\n", match ? "YES" : "NO");

    // Release
    bflb_sec_ecdh_deinit(&ecdh_a);
    bflb_sec_ecdh_deinit(&ecdh_b);
}
```

### Example 3: Using secp256k1 (Bitcoin curve)

```c
void ecdsa_secp256k1_example(void)
{
    struct bflb_ecdsa_s ecdsa;

    bflb_sec_ecdsa_init(&ecdsa, ECP_SECP256K1);

    uint32_t private_key[8] = {0};
    uint32_t public_key_x[8] = {0};
    uint32_t public_key_y[8] = {0};

    bflb_sec_ecdsa_get_private_key(&ecdsa, private_key);
    bflb_sec_ecdsa_get_public_key(&ecdsa, private_key, public_key_x, public_key_y);

    // secp256k1 order n
    uint32_t n_order[8] = {
        0xFFFFFFFF, 0xFFFFFFFF, 0xFFFFFFFF, 0xFFFFFFFE,
        0xBAAEDCE6, 0xAF48A03B, 0xBFD25E8C, 0xD0364141
    };

    // Sign...
    // ...

    bflb_sec_ecdsa_deinit(&ecdsa);
}
```

---

## Register-Level Reference

ECDSA/ECDH operations are performed through the SEC_ENG PKA subsystem.

### SEC_ENG Architecture

| Block | Offset | Purpose |
|-------|--------|---------|
| SHA | `0x000-0x0FC` | SHA-1/224/256/384/512 |
| AES | `0x100-0x1FC` | AES-128/192/256 ECB/CTR/CBC/XTS |
| TRNG | `0x200-0x2FC` | True Random Number Generator |
| **PKA** | **`0x300-0x3FC`** | **Public Key Accelerator (DSA/ECDSA/ECDH)** |
| CDET | `0x400-0x4FC` | Clock Detection |
| GMAC | `0x500-0x5FC` | Ethernet GMAC |

### PKA Register Offsets

| Offset | Register | Description |
|--------|----------|-------------|
| `0x300` | `SE_PKA_0_CTRL_0` | PKA Control Register 0 (enable/status/interrupt) |
| `0x30C` | `SE_PKA_0_SEED` | PKA Random Seed |
| `0x310` | `SE_PKA_0_CTRL_1` | PKA Control Register 1 (AHB burst/bypass) |
| `0x340` | `SE_PKA_0_RW` | PKA Data Read/Write Port |
| `0x360` | `SE_PKA_0_RW_BURST` | PKA Burst Data Read/Write Port |
| `0x3FC` | `SE_PKA_0_CTRL_PROT` | PKA Access Protection |

### PKA Control Register 0 (0x300)

| Bit(s) | Field | Description |
|--------|-------|-------------|
| 0 | `DONE` | Operation complete flag (RO) |
| 1 | `DONE_CLR_1T` | Write 1 to clear complete flag |
| 2 | `BUSY` | PKA busy flag (RO) |
| 3 | `EN` | PKA enable |
| 7:4 | `PROT_MD` | Protection mode (0x0-0xF) |
| 8 | `INT` | Interrupt flag |
| 9 | `INT_CLR_1T` | Write 1 to clear interrupt |
| 10 | `INT_SET` | Interrupt enable bit |
| 11 | `INT_MASK` | Interrupt mask |
| 12 | `ENDIAN` | Endian configuration |
| 13 | `RAM_CLR_MD` | PKA RAM clear mode |
| 15 | `STATUS_CLR_1T` | Write 1 to clear status |
| 31:16 | `STATUS` | PKA operation status code |

### PKA Control Register 1 (0x310)

| Bit(s) | Field | Description |
|--------|-------|-------------|
| 2:0 | `HBURST` | AHB burst transfer length (0-7) |
| 3 | `HBYPASS` | AHB bypass mode |

---

## Key Size Reference

| Curve | Private Key | Public Key (X) | Public Key (Y) | Hash (SHA) |
|-------|-------------|----------------|---------------|------------|
| secp256r1 (P-256) | 8 words (256-bit) | 8 words | 8 words | SHA-256 = 8 words |
| secp256k1 | 8 words (256-bit) | 8 words | 8 words | SHA-256 = 8 words |
| secp384r1 (P-384) | 12 words (384-bit) | 12 words | 12 words | SHA-384 = 12 words |

## Architecture Notes

- **Implementation:** ECDSA/ECDH functionality is implemented via the pre-compiled library `libpka_bl616.a`; no public `.c` source is available
- **Hardware Dependency:** Depends on the PKA accelerator in SEC_ENG (`SEC_ENG_BASE + 0x300`)
- **Random Number Security:** `bflb_sec_ecc_get_random_value()` uses SEC_ENG's TRNG (True Random Number Generator) to generate secure random numbers
- **ECDSA Signature Random k:** A unique random k must be used for each signature; leaking or reusing k will result in private key compromise
- **ECDSA vs ECDH:** ECDSA is used for signing/verification, ECDH for key exchange; they use different handle types
- **Resource Management:** After use, `deinit` must be called to release PKA hardware resources
