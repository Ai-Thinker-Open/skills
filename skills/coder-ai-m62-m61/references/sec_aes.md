# AES Encryption Driver Documentation (BL616/BL618)

## Overview

The Security Engine (SEC_ENG) on BL616/BL618 provides hardware-accelerated AES encryption/decryption. The AES block supports multiple block cipher modes and key sizes.

**Base Address:** `SEC_ENG_BASE = 0x20004000`

## Supported Modes

| Mode | Value | Description |
|------|-------|-------------|
| ECB | 0 | Electronic Codebook - each block encrypted independently |
| CTR | 1 | Counter Mode - uses counter for stream cipher |
| CBC | 2 | Cipher Block Chaining - XORs previous ciphertext with next plaintext |
| XTS | 3 | XEX-based Tweaked Codebook Mode - used for disk encryption |

## Key Sizes

- **AES-128**: 16 bytes (128 bits)
- **AES-192**: 24 bytes (192 bits)
- **AES-256**: 32 bytes (256 bits)

## Important Constraints

- **Data length must be a multiple of 16 bytes** (one AES block)
- IV is 16 bytes (used for CBC, CTR modes)
- Keys and IV are stored in little-endian format in registers (except XTS mode IV uses big-endian)

---

## API Reference

### 1. `bflb_aes_init()`
```c
void bflb_aes_init(struct bflb_device_s *dev);
```
Initialize the AES engine. Enables the AES block and configures endianness.

### 2. `bflb_aes_deinit()`
```c
void bflb_aes_deinit(struct bflb_device_s *dev);
```
Disable the AES engine.

### 3. `bflb_aes_set_mode()`
```c
void bflb_aes_set_mode(struct bflb_device_s *dev, uint8_t mode);
```
Set the AES block cipher mode.

**Parameters:**
- `mode`: `AES_MODE_ECB` (0), `AES_MODE_CTR` (1), `AES_MODE_CBC` (2), `AES_MODE_XTS` (3)

### 4. `bflb_aes_setkey()`
```c
void bflb_aes_setkey(struct bflb_device_s *dev, const uint8_t *key, uint16_t keybits);
```
Set the encryption key.

**Parameters:**
- `key`: Pointer to key bytes (NULL for hardware key)
- `keybits`: 128, 192, or 256

### 5. `bflb_aes_encrypt()`
```c
int bflb_aes_encrypt(struct bflb_device_s *dev,
                     const uint8_t *input,
                     const uint8_t *iv,
                     uint8_t *output,
                     uint32_t len);
```
Encrypt data.

**Parameters:**
- `input`: Plaintext buffer (must be 16-byte aligned, multiple of 16 bytes)
- `iv`: Initialization vector (16 bytes), NULL to reuse last IV
- `output`: Ciphertext output buffer
- `len`: Length in bytes (must be multiple of 16)

**Returns:** 0 on success, negative errno on failure

### 6. `bflb_aes_decrypt()`
```c
int bflb_aes_decrypt(struct bflb_device_s *dev,
                     const uint8_t *input,
                     const uint8_t *iv,
                     uint8_t *output,
                     uint32_t len);
```
Decrypt data.

**Parameters:** Same as encrypt

**Returns:** 0 on success, negative errno on failure

### 7. Hardware Key Support
```c
void bflb_aes_setkey(struct bflb_device_s *dev, NULL, 0);  // Use hardware key
void bflb_aes_select_hwkey(struct bflb_device_s *dev, uint8_t keysel0, uint8_t keysel1);
void bflb_aes_set_hwkey_source(struct bflb_device_s *dev, uint8_t source);
```

### 8. Link Mode (DMA-style)
```c
void bflb_aes_link_init(struct bflb_device_s *dev);
void bflb_aes_link_deinit(struct bflb_device_s *dev);
int bflb_aes_link_update(struct bflb_device_s *dev,
                         uint32_t link_addr,
                         const uint8_t *input,
                         uint8_t *output,
                         uint32_t len);
```
Link mode requires `link_addr` to be in 0x2xxxxxxx address range.

---

## Register Map (SEC_ENG_BASE = 0x20004000)

### AES Control and Status

| Offset | Register | Description |
|--------|----------|-------------|
| 0x100 | `se_aes_0_ctrl` | AES control register |
| 0x104 | `se_aes_0_msa` | Memory source address |
| 0x108 | `se_aes_0_mda` | Memory destination address |
| 0x10C | `se_aes_0_status` | AES status register |

### AES IV Registers

| Offset | Register | Description |
|--------|----------|-------------|
| 0x110 | `se_aes_0_iv_0` | IV bits [31:0] |
| 0x114 | `se_aes_0_iv_1` | IV bits [63:32] |
| 0x118 | `se_aes_0_iv_2` | IV bits [95:64] |
| 0x11C | `se_aes_0_iv_3` | IV bits [127:96] (CTR: counter init) |

### AES Key Registers

| Offset | Register | Description |
|--------|----------|-------------|
| 0x120 | `se_aes_0_key_0` | Key bits [31:0] |
| 0x124 | `se_aes_0_key_1` | Key bits [63:32] |
| 0x128 | `se_aes_0_key_2` | Key bits [95:64] |
| 0x12C | `se_aes_0_key_3` | Key bits [127:96] |
| 0x130 | `se_aes_0_key_4` | Key bits [159:128] |
| 0x134 | `se_aes_0_key_5` | Key bits [191:160] |
| 0x138 | `se_aes_0_key_6` | Key bits [223:192] |
| 0x13C | `se_aes_0_key_7` | Key bits [255:224] |

### AES Key Selection

| Offset | Register | Description |
|--------|----------|-------------|
| 0x140 | `se_aes_0_key_sel` | Hardware key selection |
| 0x144 | `se_aes_1_key_sel` | AES1 hardware key selection |

### AES Endian and Link

| Offset | Register | Description |
|--------|----------|-------------|
| 0x148 | `se_aes_0_endian` | Endianness configuration |
| 0x14C | `se_aes_0_sboot` | Secure boot configuration |
| 0x150 | `se_aes_0_link` | Link mode address |
| 0x1FC | `se_aes_0_ctrl_prot` | Access control |

---

## Control Register Bitfields (0x100)

```
Bits:
[0]     SEC_ENG_SE_AES_0_BUSY         - AES busy flag
[1]     SEC_ENG_SE_AES_0_TRIG_1T      - Trigger operation
[2]     SEC_ENG_SE_AES_0_EN           - AES enable
[4:3]   SEC_ENG_SE_AES_0_MODE         - Key mode (0=128, 1=256, 2=192, 3=double128)
[5]     SEC_ENG_SE_AES_0_DEC_EN        - Decryption enable
[6]     SEC_ENG_SE_AES_0_DEC_KEY_SEL  - CTR mode key select
[7]     SEC_ENG_SE_AES_0_HW_KEY_EN    - Hardware key enable
[8]     SEC_ENG_SE_AES_0_INT          - Interrupt flag
[9]     SEC_ENG_SE_AES_0_INT_CLR_1T   - Interrupt clear
[10]    SEC_ENG_SE_AES_0_INT_SET_1T    - Interrupt set
[11]    SEC_ENG_SE_AES_0_INT_MASK      - Interrupt mask
[13:12] SEC_ENG_SE_AES_0_BLOCK_MODE   - Block mode (0=ECB,1=CTR,2=CBC,3=XTS)
[14]    SEC_ENG_SE_AES_0_IV_SEL        - IV select (0=new, 1=last)
[15]    SEC_ENG_SE_AES_0_LINK_MODE     - Link mode enable
[31:16] SEC_ENG_SE_AES_0_MSG_LEN      - Message length in 16-byte blocks
```

---

## Working Code Examples

### Example 1: AES-128 ECB Encryption

```c
#include "bflb_sec_aes.h"
#include "bflb_gpio.h"

#define AES_KEY_SIZE 16

void aes_ecb_encrypt_example(void)
{
    struct bflb_device_s *aes_dev;
    uint8_t key[AES_KEY_SIZE] = {0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07, 0x08,
                                 0x09, 0x0A, 0x0B, 0x0C, 0x0D, 0x0E, 0x0F, 0x10};
    uint8_t plaintext[16] = "Hello AES ECB!";
    uint8_t ciphertext[16];
    int ret;

    /* Get AES device handle */
    aes_dev = bflb_device_get_by_name("aes");
    if (aes_dev == NULL) {
        printf("AES device not found\r\n");
        return;
    }

    /* Initialize AES */
    bflb_aes_init(aes_dev);

    /* Set ECB mode */
    bflb_aes_set_mode(aes_dev, AES_MODE_ECB);

    /* Set 128-bit key */
    bflb_aes_setkey(aes_dev, key, 128);

    /* Encrypt (16 bytes, ECB doesn't use IV) */
    ret = bflb_aes_encrypt(aes_dev, plaintext, NULL, ciphertext, 16);
    if (ret == 0) {
        printf("Encryption successful\r\n");
        printf("Ciphertext: ");
        for (int i = 0; i < 16; i++) {
            printf("%02x ", ciphertext[i]);
        }
        printf("\r\n");
    }

    /* Decrypt */
    uint8_t decrypted[16];
    ret = bflb_aes_decrypt(aes_dev, ciphertext, NULL, decrypted, 16);
    if (ret == 0) {
        printf("Decrypted: %s\r\n", decrypted);
    }

    bflb_aes_deinit(aes_dev);
}
```

### Example 2: AES-128 CBC Encryption with IV

```c
#include "bflb_sec_aes.h"

#define AES_KEY_SIZE 16
#define AES_IV_SIZE 16

void aes_cbc_example(void)
{
    struct bflb_device_s *aes_dev;
    uint8_t key[AES_KEY_SIZE] = {0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07, 0x08,
                                 0x09, 0x0A, 0x0B, 0x0C, 0x0D, 0x0E, 0x0F, 0x10};
    uint8_t iv[AES_IV_SIZE] = {0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                               0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x01};
    uint8_t plaintext[32] = "This is 32 bytes for 2 AES blocks!";
    uint8_t ciphertext[32];
    uint8_t decrypted[32];

    aes_dev = bflb_device_get_by_name("aes");
    if (aes_dev == NULL) {
        return;
    }

    bflb_aes_init(aes_dev);
    bflb_aes_set_mode(aes_dev, AES_MODE_CBC);  /* CBC mode */
    bflb_aes_setkey(aes_dev, key, 128);

    /* Encrypt with IV */
    int ret = bflb_aes_encrypt(aes_dev, plaintext, iv, ciphertext, 32);
    if (ret != 0) {
        printf("Encryption failed: %d\r\n", ret);
        return;
    }

    /* For CBC decryption, use the SAME IV that was used for encryption */
    ret = bflb_aes_decrypt(aes_dev, ciphertext, iv, decrypted, 32);
    if (ret == 0) {
        printf("Decrypted: %s\r\n", decrypted);
    }

    bflb_aes_deinit(aes_dev);
}
```

### Example 3: AES-256 CTR Mode

```c
#include "bflb_sec_aes.h"

void aes_ctr_example(void)
{
    struct bflb_device_s *aes_dev;
    uint8_t key[32] = {0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07, 0x08,
                      0x09, 0x0A, 0x0B, 0x0C, 0x0D, 0x0E, 0x0F, 0x10,
                      0x11, 0x12, 0x13, 0x14, 0x15, 0x16, 0x17, 0x18,
                      0x19, 0x1A, 0x1B, 0x1C, 0x1D, 0x1E, 0x1F, 0x20};
    uint8_t iv[16] = {0};  /* CTR counter starts at 0 */
    uint8_t data[64];
    uint8_t encrypted[64];
    uint8_t decrypted[64];

    aes_dev = bflb_device_get_by_name("aes");
    if (aes_dev == NULL) {
        return;
    }

    bflb_aes_init(aes_dev);
    bflb_aes_set_mode(aes_dev, AES_MODE_CTR);  /* CTR mode */
    bflb_aes_setkey(aes_dev, key, 256);

    /* Generate or load your data */
    memset(data, 0xAA, sizeof(data));

    /* CTR encryption (same operation for decrypt) */
    int ret = bflb_aes_encrypt(aes_dev, data, iv, encrypted, 64);

    /* CTR decryption uses same function (stream cipher) */
    ret = bflb_aes_decrypt(aes_dev, encrypted, iv, decrypted, 64);

    bflb_aes_deinit(aes_dev);
}
```

### Example 4: Using Link Mode for Large Data

```c
#include "bflb_sec_aes.h"

void aes_link_mode_example(void)
{
    struct bflb_device_s *aes_dev;
    uint8_t key[16] = {0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07, 0x08,
                       0x09, 0x0A, 0x0B, 0x0C, 0x0D, 0x0E, 0x0F, 0x10};
    uint8_t iv[16] = {0};
    uint8_t plaintext[256] __attribute__((aligned(4)));
    uint8_t ciphertext[256] __attribute__((aligned(4)));

    /* Link structure must be in 0x2xxxxxxx memory region */
    static uint32_t aes_link[18] __attribute__((aligned(4)));

    aes_dev = bflb_device_get_by_name("aes");
    if (aes_dev == NULL) {
        return;
    }

    /* Initialize link mode */
    bflb_aes_link_init(aes_dev);
    bflb_aes_set_mode(aes_dev, AES_MODE_CBC);
    bflb_aes_setkey(aes_dev, key, 128);

    /* Configure link structure */
    aes_link[0] = 0;  /* control: key selection, mode, etc */
    aes_link[1] = ((uint32_t)plaintext & 0x0FFFFFFF) | 0x20000000;  /* src addr */
    aes_link[2] = ((uint32_t)ciphertext & 0x0FFFFFFF) | 0x20000000; /* dst addr */
    aes_link[3] = ((uint32_t)iv[3] << 24) | ((uint32_t)iv[2] << 16) |
                  ((uint32_t)iv[1] << 8) | iv[0];  /* IV MSB */
    aes_link[4] = ((uint32_t)iv[7] << 24) | ((uint32_t)iv[6] << 16) |
                  ((uint32_t)iv[5] << 8) | iv[4];
    aes_link[5] = ((uint32_t)iv[11] << 24) | ((uint32_t)iv[10] << 16) |
                  ((uint32_t)iv[9] << 8) | iv[8];
    aes_link[6] = ((uint32_t)iv[15] << 24) | ((uint32_t)iv[14] << 16) |
                  ((uint32_t)iv[13] << 8) | iv[12];  /* IV LSB */

    /* Process data using link mode */
    int ret = bflb_aes_link_update(aes_dev, (uint32_t)aes_link,
                                    plaintext, ciphertext, 256);

    bflb_aes_link_deinit(aes_dev);
}
```

### Example 5: Multi-block CBC Encryption

```c
#include "bflb_sec_aes.h"

void aes_multiblock_example(void)
{
    struct bflb_device_s *aes_dev;
    uint8_t key[16] = {0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07, 0x08,
                       0x09, 0x0A, 0x0B, 0x0C, 0x0D, 0x0E, 0x0F, 0x10};
    uint8_t iv[16] = {0};

    /* Multi-block data (must be multiple of 16) */
    uint8_t plaintext[48] = "This is a 48-byte message!With 3 AES blocks!";
    uint8_t ciphertext[48];
    uint8_t decrypted[48];

    aes_dev = bflb_device_get_by_name("aes");
    if (aes_dev == NULL) {
        return;
    }

    bflb_aes_init(aes_dev);
    bflb_aes_set_mode(aes_dev, AES_MODE_CBC);
    bflb_aes_setkey(aes_dev, key, 128);

    /* CBC encrypt - IV is only used for first block, subsequent blocks
       use previous ciphertext as "IV" (chaining) */
    int ret = bflb_aes_encrypt(aes_dev, plaintext, iv, ciphertext, 48);

    /* Decrypt with same IV - returns blocks in chain order */
    ret = bflb_aes_decrypt(aes_dev, ciphertext, iv, decrypted, 48);

    bflb_aes_deinit(aes_dev);
}
```

---

## Notes on AES Modes

### ECB (Electronic Codebook)
- **Security**: Weak - identical plaintext blocks produce identical ciphertext
- **Use case**: Testing, not recommended for real encryption
- **IV**: Not used (pass NULL)

### CBC (Cipher Block Chaining)
- **Security**: Good - each block depends on all previous blocks
- **Use case**: General-purpose encryption, file encryption
- **IV**: Required for first block, must be random/unpredictable

### CTR (Counter)
- **Security**: Good - stream cipher mode
- **Use case**: Stream encryption, network protocols
- **IV**: Counter initialization value (nonces can be included)
- **Note**: Encrypt and decrypt are the same operation

### XTS (XEX-based Tweaked Codebook)
- **Security**: Good - designed for disk encryption
- **Use case**: Full-disk encryption, storage encryption
- **IV**: Tweak value (typically sector/location identifier)

---

## GCM Mode Note

The BL616/BL618 does **not** have native GCM mode in the AES block. For authenticated encryption (GCM), you would need to:
1. Use the SHA block for GHASH (via GMAC)
2. Implement GMAC manually (see `sec_eng_reg.h` GMAC registers at 0x500)
3. Or use software AES-CTR + hardware GHASH combination

The GMAC block at offset 0x500 provides Galois MAC functionality for this purpose, but it requires manual implementation of the GCM specification.

---

## Troubleshooting

| Issue | Cause | Solution |
|-------|-------|----------|
| `EINVAL` error | Data length not multiple of 16 | Ensure `len % 16 == 0` |
| Timeout | Hardware not responding | Check clock enable, reset AES |
| Wrong output | Key/IV endianness | Keys/IV are little-endian in registers |
| CBC decryption wrong | Wrong IV used | Must use same IV as encryption |
| Link mode fails | Address not in 0x2xxxxxxx | Link structure must be in DMA-capable memory |
