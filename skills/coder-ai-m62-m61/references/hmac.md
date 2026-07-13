# HMAC-SHA256 Hardware Acceleration (BL616/BL618)

## Important Finding

**The BL616/BL618 does NOT have a dedicated HMAC hardware block.** HMAC-SHA256 must be implemented in software using the SHA hardware accelerator (`sec_sha`). The `sec_aes` block provides AES encryption but no native HMAC or GCM mode.

---

## Architecture Overview

The Security Engine (SEC_ENG) on BL616/BL618 provides:

| Block | Offset | Purpose | Native HMAC |
|-------|--------|---------|-------------|
| SHA | 0x000-0x0FC | SHA-1, SHA-224, SHA-256, SHA-512 | No (raw hash only) |
| AES | 0x100-0x1FC | AES-128/192/256 ECB/CTR/CBC/XTS | No |
| GMAC | 0x500-0x5FC | Ethernet MAC (NOT Galois MAC) | No |

**HMAC Implementation Strategy:** Use `sec_sha` (SHA hardware) to implement HMAC-SHA256 in software using the nested hash technique.

---

## HMAC Algorithm

HMAC-SHA256 is defined as:

```
HMAC-SHA256(key, message) = SHA256((key' ⊕ opad) || SHA256((key' ⊕ ipad) || message))
```

Where:
- `key'` = key padded/truncated to 64 bytes
- `ipad` = 0x36 repeated 64 times
- `opad` = 0x5C repeated 64 times

### Standard HMAC Constants

```c
#define HMAC_IPAD_VALUE  0x36
#define HMAC_OPAD_VALUE  0x5C
#define HMAC_BLOCK_SIZE  64   // SHA-256 block size in bytes
#define SHA256_DIGEST_SIZE 32 // SHA-256 output size in bytes
```

---

## Register-Level Access (SEC_ENG_BASE = 0x20004000)

### SHA Registers (Used for HMAC)

| Offset | Register | Description |
|--------|----------|-------------|
| 0x00 | `se_sha_0_ctrl` | SHA control (enable, mode, trigger) |
| 0x04 | `se_sha_0_msa` | Memory source address |
| 0x08 | `se_sha_0_status` | SHA status (BUSY flag) |
| 0x0C | `se_sha_0_endian` | Endianness configuration |
| 0x10-0x2C | `se_sha_0_hash_l_0` to `se_sha_0_hash_l_7` | Hash result low (bits [31:0] per register) |
| 0x30-0x4C | `se_sha_0_hash_h_0` to `se_sha_0_hash_h_7` | Hash result high (bits [255:224] for SHA-512) |
| 0x50 | `se_sha_0_link` | Link mode address |
| 0xFC | `se_sha_0_ctrl_prot` | Access control |

### SHA Control Register Bitfields (0x00)

```c
#define SEC_ENG_SE_SHA_0_BUSY           (1 << 0U)  // Busy flag
#define SEC_ENG_SE_SHA_0_TRIG_1T        (1 << 1U)  // Trigger operation
#define SEC_ENG_SE_SHA_0_MODE_SHIFT     (2U)        // SHA mode shift
#define SEC_ENG_SE_SHA_0_MODE_MASK      (0x7 << 2U) // SHA mode mask
#define SEC_ENG_SE_SHA_0_EN             (1 << 5U)   // SHA enable
#define SEC_ENG_SE_SHA_0_HASH_SEL       (1 << 6U)   // 0=new, 1=accumulate
#define SEC_ENG_SE_SHA_0_INT            (1 << 8U)   // Interrupt flag
#define SEC_ENG_SE_SHA_0_INT_CLR_1T     (1 << 9U)   // Clear interrupt
#define SEC_ENG_SE_SHA_0_LINK_MODE      (1 << 15U)  // Link mode enable
#define SEC_ENG_SE_SHA_0_MSG_LEN_SHIFT  (16U)        // Message length shift
#define SEC_ENG_SE_SHA_0_MSG_LEN_MASK   (0xFFFFU << 16U) // Message length mask
```

### SHA Mode Values

```c
#define SHA_MODE_SHA256     0   // SHA-256 (used for HMAC-SHA256)
#define SHA_MODE_SHA224     1   // SHA-224
#define SHA_MODE_SHA1       2   // SHA-1
#define SHA_MODE_SHA512     4   // SHA-512
#define SHA_MODE_SHA384     5   // SHA-384
#define SHA_MODE_SHA512T224 6   // SHA-512/224
#define SHA_MODE_SHA512T256 7   // SHA-512/256
```

---

## HMAC-SHA256 Implementation Using sec_sha

### Software HMAC Structure

```c
struct bflb_hmac_sha256_ctx_s {
    struct bflb_sha256_ctx_s inner_sha;  // For inner hash
    struct bflb_sha256_ctx_s outer_sha;  // For outer hash
    uint8_t key[64];                     // Padded key (64 bytes)
    uint8_t ipad[64];                    // Inner padding
    uint8_t opad[64];                    // Outer padding
    uint8_t digest[32];                  // Final HMAC output
};
```

### Working Code: HMAC-SHA256 Using sec_sha

```c
#include "bflb_sec_sha.h"
#include "bflb_sec_eng.h"
#include <string.h>

#define HMAC_BLOCK_SIZE   64
#define SHA256_BLOCK_SIZE  64
#define SHA256_DIGEST_SIZE 32

/**
 * @brief Prepare key (pad to 64 bytes, hash if longer than 64)
 */
static void hmac_sha256_prepare_key(const uint8_t *key, uint32_t key_len, uint8_t *key_padded)
{
    memset(key_padded, 0, HMAC_BLOCK_SIZE);
    
    if (key_len > HMAC_BLOCK_SIZE) {
        // If key > 64 bytes, hash it first
        struct bflb_device_s *sha = bflb_device_get_by_name("sha");
        struct bflb_sha256_ctx_s sha_ctx;
        
        bflb_sha_init(sha, SHA_MODE_SHA256);
        bflb_sha256_start(sha, &sha_ctx);
        bflb_sha256_update(sha, &sha_ctx, key, key_len);
        bflb_sha256_finish(sha, &sha_ctx, key_padded);
    } else {
        memcpy(key_padded, key, key_len);
    }
}

/**
 * @brief Compute HMAC-SHA256 using hardware SHA
 */
int hmac_sha256_compute(const uint8_t *key, uint32_t key_len,
                        const uint8_t *message, uint32_t msg_len,
                        uint8_t *hmac_out)
{
    struct bflb_device_s *sha;
    struct bflb_sha256_ctx_s inner_ctx, outer_ctx;
    uint8_t key_padded[64];
    uint8_t ipad[64];
    uint8_t opad[64];
    uint8_t inner_hash[32];
    uint8_t i;
    
    if (key == NULL || message == NULL || hmac_out == NULL) {
        return -1;
    }
    
    sha = bflb_device_get_by_name("sha");
    if (sha == NULL) {
        return -1;
    }
    
    /* Step 1: Prepare the key */
    hmac_sha256_prepare_key(key, key_len, key_padded);
    
    /* Step 2: Create ipad and opad */
    for (i = 0; i < HMAC_BLOCK_SIZE; i++) {
        ipad[i] = key_padded[i] ^ 0x36;  /* XOR with ipad value */
        opad[i] = key_padded[i] ^ 0x5C;  /* XOR with opad value */
    }
    
    /* Step 3: Inner hash - SHA256((key ⊕ ipad) || message) */
    bflb_sha_init(sha, SHA_MODE_SHA256);
    bflb_sha256_start(sha, &inner_ctx);
    bflb_sha256_update(sha, &inner_ctx, ipad, HMAC_BLOCK_SIZE);
    bflb_sha256_update(sha, &inner_ctx, message, msg_len);
    bflb_sha256_finish(sha, &inner_ctx, inner_hash);
    
    /* Step 4: Outer hash - SHA256((key ⊕ opad) || inner_hash) */
    bflb_sha_init(sha, SHA_MODE_SHA256);
    bflb_sha256_start(sha, &outer_ctx);
    bflb_sha256_update(sha, &outer_ctx, opad, HMAC_BLOCK_SIZE);
    bflb_sha256_update(sha, &outer_ctx, inner_hash, SHA256_DIGEST_SIZE);
    bflb_sha256_finish(sha, &outer_ctx, hmac_out);
    
    return 0;
}

/**
 * @brief Example usage of HMAC-SHA256
 */
void hmac_sha256_example(void)
{
    const uint8_t key[] = "ThisIsASecretKey123456789012345";  // 32 bytes
    const uint8_t message[] = "Hello, HMAC-SHA256!";
    uint8_t hmac[32];
    int ret;
    
    ret = hmac_sha256_compute(key, strlen((char *)key), 
                              message, strlen((char *)message),
                              hmac);
    
    if (ret == 0) {
        printf("HMAC-SHA256 computed successfully:\r\n");
        for (int i = 0; i < 32; i++) {
            printf("%02x ", hmac[i]);
        }
        printf("\r\n");
    }
}
```

---

## Direct Register-Level HMAC-SHA256

For maximum performance and control, bypass the HAL:

```c
#include "bflb_sec_eng.h"

#define SEC_ENG_BASE  0x20004000
#define SEC_ENG_SHA_CTRL   (SEC_ENG_BASE + 0x00)
#define SEC_ENG_SHA_MSA    (SEC_ENG_BASE + 0x04)
#define SEC_ENG_SHA_STATUS (SEC_ENG_BASE + 0x08)
#define SEC_ENG_SHA_HASH(n) (SEC_ENG_BASE + 0x10 + (n) * 4)

/* SHA Control register */
#define SHA_EN           (1 << 5)
#define SHA_TRIG         (1 << 1)
#define SHA_MODE_SHA256  (0 << 2)
#define SHA_MODE_SHA224  (1 << 2)
#define SHA_MODE_SHA1    (2 << 2)
#define SHA_BUSY         (1 << 0)

/**
 * @brief Direct register-level SHA256 single block
 */
static void sha256_block_direct(const uint8_t *block, uint8_t *hash_out)
{
    uint32_t *hash_reg;
    int i;
    
    /* Set source address */
    *(volatile uint32_t *)SEC_ENG_SHA_MSA = (uint32_t)block;
    
    /* Configure and trigger SHA */
    *(volatile uint32_t *)SEC_ENG_SHA_CTRL = SHA_EN | SHA_TRIG | SHA_MODE_SHA256;
    
    /* Wait for completion */
    while (*(volatile uint32_t *)SEC_ENG_SHA_STATUS & SHA_BUSY);
    
    /* Read hash result (little-endian) */
    hash_reg = (uint32_t *)hash_out;
    for (i = 0; i < 8; i++) {
        hash_reg[i] = *(volatile uint32_t *)SEC_ENG_SHA_HASH(i);
    }
}

/**
 * @brief Direct register-level HMAC-SHA256
 */
int hmac_sha256_direct(const uint8_t *key, uint32_t key_len,
                       const uint8_t *message, uint32_t msg_len,
                       uint8_t *hmac_out)
{
    uint8_t key_padded[64];
    uint8_t ipad[64];
    uint8_t opad[64];
    uint8_t inner_hash[32];
    uint8_t inner_block[128];  /* For inner hash: ipad(64) || message */
    uint8_t outer_block[96];   /* For outer hash: opad(64) || inner_hash(32) */
    uint32_t i;
    
    /* Prepare key */
    if (key_len > 64) {
        sha256_block_direct(key, key_padded);  /* Hash long keys */
        memset(key_padded + 32, 0, 32);
    } else {
        memset(key_padded, 0, 64);
        memcpy(key_padded, key, key_len);
    }
    
    /* Create pads */
    for (i = 0; i < 64; i++) {
        ipad[i] = key_padded[i] ^ 0x36;
        opad[i] = key_padded[i] ^ 0x5C;
    }
    
    /* Inner hash: SHA256(ipad || message) */
    memcpy(inner_block, ipad, 64);
    memcpy(inner_block + 64, message, msg_len);
    sha256_block_direct(inner_block, inner_hash);
    
    /* Outer hash: SHA256(opad || inner_hash) */
    memcpy(outer_block, opad, 64);
    memcpy(outer_block + 64, inner_hash, 32);
    sha256_block_direct(outer_block, hmac_out);
    
    return 0;
}
```

---

## Comparison: sec_sha vs sec_aes vs HMAC

| Feature | sec_sha | sec_aes | HMAC-SHA256 |
|---------|---------|---------|-------------|
| **Purpose** | Raw hash | Raw encryption | Message authentication |
| **Hardware** | Yes (SHA engine) | Yes (AES engine) | **Software using sec_sha** |
| **Supported** | SHA-1, SHA-224/256, SHA-384/512 | AES-128/192/256, ECB/CTR/CBC/XTS | HMAC-SHA256 (via software) |
| **Output Size** | 20-64 bytes | 16+ bytes (block aligned) | 32 bytes (HMAC-SHA256) |
| **Key Input** | No | Yes (128/192/256-bit) | Yes (any length) |
| **Authentication** | No | No | Yes (integrity + authenticity) |
| **Registers** | 0x00-0xFC | 0x100-0x1FC | Uses SHA registers |
| **Interrupt** | Yes | Yes | Uses SHA interrupt |

### When to Use Each

| Use Case | Recommended |
|----------|-------------|
| Compute hash of data | `sec_sha` (SHA-256) |
| Encrypt/decrypt data | `sec_aes` (AES-CBC/CTR/etc.) |
| Authenticate messages (TLS, HMAC) | **HMAC-SHA256** (using sec_sha) |
| Authenticated encryption (GCM) | **AES + HMAC** combination |
| Generate random numbers | TRNG (0x200-0x2FC) |

---

## Authenticated Encryption: AES + HMAC-SHA256

For authenticated encryption (like AES-256-GCM), combine AES and HMAC:

```c
/**
 * @brief AES-256-CBC encryption with HMAC-SHA256 authentication
 */
int aes_cbc_hmac_sha256_encrypt(const uint8_t *aes_key, const uint8_t *hmac_key,
                                 const uint8_t *iv, const uint8_t *plaintext, uint32_t pt_len,
                                 uint8_t *ciphertext, uint8_t *hmac_tag)
{
    struct bflb_device_s *aes_dev;
    struct bflb_device_s *sha_dev;
    int ret;
    uint32_t msg_len;
    
    /* Validate inputs */
    if (pt_len % 16 != 0) {
        return -1;  /* Length must be multiple of 16 */
    }
    
    aes_dev = bflb_device_get_by_name("aes");
    sha_dev = bflb_device_get_by_name("sha");
    
    if (aes_dev == NULL || sha_dev == NULL) {
        return -1;
    }
    
    /* Step 1: Encrypt plaintext with AES-CBC */
    bflb_aes_init(aes_dev);
    bflb_aes_set_mode(aes_dev, AES_MODE_CBC);
    bflb_aes_setkey(aes_dev, aes_key, 256);
    ret = bflb_aes_encrypt(aes_dev, plaintext, iv, ciphertext, pt_len);
    if (ret != 0) {
        return ret;
    }
    
    /* Step 2: Compute HMAC over IV || ciphertext */
    /* Format: IV (16 bytes) || ciphertext */
    uint8_t auth_data[16 + pt_len];
    memcpy(auth_data, iv, 16);
    memcpy(auth_data + 16, ciphertext, pt_len);
    
    /* Compute HMAC-SHA256 */
    ret = hmac_sha256_compute(hmac_key, 32, auth_data, 16 + pt_len, hmac_tag);
    
    bflb_aes_deinit(aes_dev);
    
    return ret;
}

/**
 * @brief AES-256-CBC decryption with HMAC-SHA256 verification
 */
int aes_cbc_hmac_sha256_decrypt(const uint8_t *aes_key, const uint8_t *hmac_key,
                                 const uint8_t *iv, const uint8_t *ciphertext, uint32_t ct_len,
                                 const uint8_t *hmac_tag,  /* Received tag */
                                 uint8_t *plaintext)
{
    struct bflb_device_s *aes_dev;
    struct bflb_device_s *sha_dev;
    int ret;
    uint8_t computed_tag[32];
    uint8_t auth_data[16 + ct_len];
    
    if (ct_len % 16 != 0) {
        return -1;
    }
    
    aes_dev = bflb_device_get_by_name("aes");
    sha_dev = bflb_device_get_by_name("sha");
    
    if (aes_dev == NULL || sha_dev == NULL) {
        return -1;
    }
    
    /* Step 1: Verify HMAC first */
    memcpy(auth_data, iv, 16);
    memcpy(auth_data + 16, ciphertext, ct_len);
    
    ret = hmac_sha256_compute(hmac_key, 32, auth_data, 16 + ct_len, computed_tag);
    if (ret != 0) {
        return ret;
    }
    
    /* Constant-time comparison to prevent timing attacks */
    ret = 0;
    for (int i = 0; i < 32; i++) {
        ret |= computed_tag[i] ^ hmac_tag[i];
    }
    if (ret != 0) {
        return -2;  /* Authentication failed */
    }
    
    /* Step 2: Decrypt ciphertext */
    bflb_aes_init(aes_dev);
    bflb_aes_set_mode(aes_dev, AES_MODE_CBC);
    bflb_aes_setkey(aes_dev, aes_key, 256);
    ret = bflb_aes_decrypt(aes_dev, ciphertext, iv, plaintext, ct_len);
    bflb_aes_deinit(aes_dev);
    
    return ret;
}
```

---

## Access Control Registers

| Offset | Register | Description |
|--------|----------|-------------|
| 0xFC | `se_sha_0_ctrl_prot` | SHA access control |
| 0x1FC | `se_aes_0_ctrl_prot` | AES access control |

```c
/* Access control bits */
#define SEC_ENG_SE_SHA_ID0_EN  (1 << 1)  /* SHA access for ID0 */
#define SEC_ENG_SE_SHA_ID1_EN  (1 << 2)  /* SHA access for ID1 */
#define SEC_ENG_SE_AES_ID0_EN  (1 << 1) /* AES access for ID0 */
#define SEC_ENG_SE_AES_ID1_EN  (1 << 2) /* AES access for ID1 */

/* Request/release SHA access */
int bflb_group0_request_sha_access(struct bflb_device_s *dev);
int bflb_group1_request_sha_access(struct bflb_device_s *dev);
void bflb_group0_release_sha_access(struct bflb_device_s *dev);
void bflb_group1_release_sha_access(struct bflb_device_s *dev);

/* Request/release AES access */
int bflb_group0_request_aes_access(struct bflb_device_s *dev);
int bflb_group1_request_aes_access(struct bflb_device_s *dev);
void bflb_group0_release_aes_access(struct bflb_device_s *dev);
void bflb_group1_release_aes_access(struct bflb_device_s *dev);
```

---

## Troubleshooting

| Issue | Cause | Solution |
|-------|-------|----------|
| HMAC wrong | Key not properly padded | Keys > 64 bytes must be hashed first |
| HMAC wrong | Inner/outer hash order incorrect | Must hash inner first, then outer |
| SHA timeout | Hardware not enabled | Call `bflb_sha_init()` first |
| AES + HMAC mismatch | Tag compared incorrectly | Use constant-time comparison |
| Auth failed | IV mismatch | Use same IV for encrypt/decrypt |

---

## Summary

- **BL616/BL618 has NO dedicated HMAC hardware**
- **HMAC-SHA256 is implemented in software using sec_sha**
- Use `sec_sha` for raw SHA-256 hashing
- Use `sec_aes` for AES encryption (no native GCM)
- For authenticated encryption, combine AES + HMAC-SHA256
- Register base: `0x20004000` (SEC_ENG)
- SHA registers: `0x00` - `0xFC`
- AES registers: `0x100` - `0x1FC`
