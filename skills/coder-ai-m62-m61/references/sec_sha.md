# BL616/BL618 SHA Hardware Acceleration

SHA hardware accelerator in the Security Engine (SEC_ENG). Base address: `0x20004000`.

## Supported Algorithms

| Mode | Value | Description | Hash Size |
|------|-------|-------------|-----------|
| `SHA_MODE_SHA256` | 0 | SHA-256 | 256 bits |
| `SHA_MODE_SHA224` | 1 | SHA-224 | 224 bits |
| `SHA_MODE_SHA1` | 2 | SHA-1 | 160 bits |
| `SHA_MODE_SHA512` | 4 | SHA-512 | 512 bits |
| `SHA_MODE_SHA384` | 5 | SHA-384 | 384 bits |
| `SHA_MODE_SHA512T224` | 6 | SHA-512/224 | 224 bits |
| `SHA_MODE_SHA512T256` | 7 | SHA-512/256 | 256 bits |

## API Reference

### `bflb_sha_init(dev, mode)`

Initialize SHA engine with specified algorithm mode.

```c
void bflb_sha_init(struct bflb_device_s *dev, uint8_t mode);
```

**Parameters:**
- `dev` - SEC_ENG device handle
- `mode` - One of `SHA_MODE_SHA256`, `SHA_MODE_SHA224`, `SHA_MODE_SHA1`, `SHA_MODE_SHA512`, etc.

### `bflb_sha1_start(dev, ctx)`, `bflb_sha256_start(dev, ctx)`, `bflb_sha512_start(dev, ctx)`

Start SHA operation with fresh context.

```c
void bflb_sha1_start(struct bflb_device_s *dev, struct bflb_sha1_ctx_s *ctx);
void bflb_sha256_start(struct bflb_device_s *dev, struct bflb_sha256_ctx_s *ctx);
void bflb_sha512_start(struct bflb_device_s *dev, struct bflb_sha512_ctx_s *ctx);
```

### `bflb_sha1_update(dev, ctx, input, len)`, `bflb_sha256_update(dev, ctx, input, len)`, `bflb_sha512_update(dev, ctx, input, len)`

Feed data into SHA engine. Handles buffering for block alignment.

```c
int bflb_sha1_update(struct bflb_device_s *dev, struct bflb_sha1_ctx_s *ctx,
                    const uint8_t *input, uint32_t len);
int bflb_sha256_update(struct bflb_device_s *dev, struct bflb_sha256_ctx_s *ctx,
                       const uint8_t *input, uint32_t len);
int bflb_sha512_update(struct bflb_device_s *dev, struct bflb_sha512_ctx_s *ctx,
                       const uint8_t *input, uint64_t len);
```

**Returns:** 0 on success, -ETIMEDOUT on timeout (100ms).

### `bflb_sha1_finish(dev, ctx, output)`, `bflb_sha256_finish(dev, ctx, output)`, `bflb_sha512_finish(dev, ctx, output)`

Complete SHA operation and retrieve digest.

```c
void bflb_sha1_finish(struct bflb_device_s *dev, struct bflb_sha1_ctx_s *ctx, uint8_t *output);
void bflb_sha256_finish(struct bflb_device_s *dev, struct bflb_sha256_ctx_s *ctx, uint8_t *output);
void bflb_sha512_finish(struct bflb_device_s *dev, struct bflb_sha512_ctx_s *ctx, uint8_t *output);
```

## Register Map (SEC_ENG_BASE = 0x20004000)

| Offset | Register | Description |
|--------|----------|-------------|
| 0x00 | `se_sha_0_ctrl` | SHA control register |
| 0x04 | `se_sha_0_msa` | SHA memory source address |
| 0x08 | `se_sha_0_status` | SHA status |
| 0x0C | `se_sha_0_endian` | SHA endian control |
| 0x10-0x2C | `se_sha_0_hash_l_0` to `se_sha_0_hash_l_7` | SHA hash low registers (bits [31:0] of 256-bit hash) |
| 0x30-0x4C | `se_sha_0_hash_h_0` to `se_sha_0_hash_h_7` | SHA hash high registers (bits [255:224] of 512-bit hash) |
| 0x50 | `se_sha_0_link` | SHA link configuration address |
| 0xFC | `se_sha_0_ctrl_prot` | SHA access protection |

### SHA Control Register (0x00)

| Bits | Name | Description |
|------|------|-------------|
| 0 | `BUSY` | SHA engine busy flag |
| 1 | `TRIG_1T` | Trigger one-shot operation |
| [4:2] | `MODE` | SHA mode (SHA-1/SHA-224/SHA-256) |
| 5 | `EN` | SHA enable |
| 6 | `HASH_SEL` | 0=new hash, 1=accumulate previous hash |
| 8 | `INT` | Interrupt flag |
| 9 | `INT_CLR_1T` | Clear interrupt |
| 10 | `INT_SET_1T` | Set interrupt |
| 11 | `INT_MASK` | Interrupt mask |
| [13:12] | `MODE_EXT` | Extended mode (SHA-512 variants) |
| 15 | `LINK_MODE` | Link mode enable |
| [31:16] | `MSG_LEN` | Message length in blocks |

### SHA Control Register Bitfield Definitions

```c
#define SEC_ENG_SE_SHA_0_BUSY           (1 << 0U)
#define SEC_ENG_SE_SHA_0_TRIG_1T        (1 << 1U)
#define SEC_ENG_SE_SHA_0_MODE_SHIFT     (2U)
#define SEC_ENG_SE_SHA_0_MODE_MASK      (0x7 << SEC_ENG_SE_SHA_0_MODE_SHIFT)
#define SEC_ENG_SE_SHA_0_EN             (1 << 5U)
#define SEC_ENG_SE_SHA_0_HASH_SEL       (1 << 6U)
#define SEC_ENG_SE_SHA_0_INT            (1 << 8U)
#define SEC_ENG_SE_SHA_0_INT_CLR_1T     (1 << 9U)
#define SEC_ENG_SE_SHA_0_INT_SET_1T     (1 << 10U)
#define SEC_ENG_SE_SHA_0_INT_MASK       (1 << 11U)
#define SEC_ENG_SE_SHA_0_MODE_EXT_SHIFT (12U)
#define SEC_ENG_SE_SHA_0_MODE_EXT_MASK  (0x3 << SEC_ENG_SE_SHA_0_MODE_EXT_SHIFT)
#define SEC_ENG_SE_SHA_0_LINK_MODE      (1 << 15U)
#define SEC_ENG_SE_SHA_0_MSG_LEN_SHIFT  (16U)
#define SEC_ENG_SE_SHA_0_MSG_LEN_MASK   (0xffff << SEC_ENG_SE_SHA_0_MSG_LEN_SHIFT)
```

## Context Structures

### SHA-1/SHA-224/SHA-256 Context

```c
struct bflb_sha256_ctx_s {
    uint32_t total[2];                         /*!< Bytes processed */
    uint8_t sha_buf[64] __attribute__((aligned(32)));     /*!< Unprocessed data buffer */
    uint8_t sha_padding[64] __attribute__((aligned(32))); /*!< Padding buffer */
    uint8_t sha_feed;                                      /*!< Feed flag */
};
```

### SHA-512 Context

```c
struct bflb_sha512_ctx_s {
    uint64_t total[2];                          /*!< Bytes processed */
    uint8_t sha_buf[128] __attribute__((aligned(32)));     /*!< Unprocessed data buffer */
    uint8_t sha_padding[128] __attribute__((aligned(32))); /*!< Padding buffer */
    uint8_t sha_feed;                                       /*!< Feed flag */
};
```

## Usage Examples

### SHA-256 Single-Pass

```c
#include "bflb_sec_sha.h"
#include "bflb_sec_eng.h"

void sha256_example(void)
{
    struct bflb_device_s *sha;
    struct bflb_sha256_ctx_s ctx;
    uint8_t digest[32];

    /* Get SHA device */
    sha = bflb_device_get_by_name("sha");
    
    /* Initialize for SHA-256 */
    bflb_sha_init(sha, SHA_MODE_SHA256);
    
    /* Start fresh hash */
    bflb_sha256_start(sha, &ctx);
    
    /* Feed data (can be called multiple times) */
    const char *message = "Hello, World!";
    bflb_sha256_update(sha, &ctx, (uint8_t *)message, strlen(message));
    
    /* Complete and get digest */
    bflb_sha256_finish(sha, &ctx, digest);
    
    /* digest now contains 32-byte SHA-256 hash */
}
```

### SHA-512 Single-Pass

```c
void sha512_example(void)
{
    struct bflb_device_s *sha;
    struct bflb_sha512_ctx_s ctx;
    uint8_t digest[64];

    sha = bflb_device_get_by_name("sha");
    
    bflb_sha_init(sha, SHA_MODE_SHA512);
    bflb_sha512_start(sha, &ctx);
    
    bflb_sha512_update(sha, &ctx, (uint8_t *)"Hello", 5);
    
    bflb_sha512_finish(sha, &ctx, digest);
    /* digest now contains 64-byte SHA-512 hash */
}
```

### SHA-1 Incremental Hash

```c
void sha1_incremental(void)
{
    struct bflb_device_s *sha;
    struct bflb_sha1_ctx_s ctx;
    uint8_t digest[20];

    sha = bflb_device_get_by_name("sha");
    
    bflb_sha_init(sha, SHA_MODE_SHA1);
    bflb_sha1_start(sha, &ctx);
    
    /* Feed data in chunks */
    bflb_sha1_update(sha, &ctx, (uint8_t *)"Hello ", 6);
    bflb_sha1_update(sha, &ctx, (uint8_t *)"World!", 6);
    
    bflb_sha1_finish(sha, &ctx, digest);
    /* Same as SHA-1 of "Hello World!" */
}
```

### SHA-224, SHA-384, SHA-512/256, SHA-512/224

```c
/* SHA-224 (224-bit / 28-byte output) */
bflb_sha_init(sha, SHA_MODE_SHA224);
bflb_sha256_start(sha, &ctx);
bflb_sha256_update(sha, &ctx, data, len);
bflb_sha256_finish(sha, &ctx, digest);  /* Use first 28 bytes */

/* SHA-384 (384-bit / 48-byte output) */
bflb_sha_init(sha, SHA_MODE_SHA384);
bflb_sha512_start(sha, &ctx);
bflb_sha512_update(sha, &ctx, data, len);
bflb_sha512_finish(sha, &ctx, digest);  /* Use first 48 bytes */

/* SHA-512/256 (256-bit / 32-byte output) */
bflb_sha_init(sha, SHA_MODE_SHA512T256);
bflb_sha512_start(sha, &ctx);
bflb_sha512_update(sha, &ctx, data, len);
bflb_sha512_finish(sha, &ctx, digest);  /* Use first 32 bytes */

/* SHA-512/224 (224-bit / 28-byte output) */
bflb_sha_init(sha, SHA_MODE_SHA512T224);
bflb_sha512_start(sha, &ctx);
bflb_sha512_update(sha, &ctx, data, len);
bflb_sha512_finish(sha, &ctx, digest);  /* Use first 28 bytes */
```

## Link Mode (DMA-Based)

Link mode allows DMA-based SHA operations for better performance with large data.

### Link Configuration Structure

```c
struct bflb_sha_link_s {
    uint32_t sha_mode      : 3;  /*!< SHA mode */
    uint32_t sha_newhash_dis : 1; /*!< 0=new hash, 1=accumulate */
    uint32_t sha_intclr    : 1;  /*!< Clear interrupt */
    uint32_t sha_intset    : 1;  /*!< Set interrupt */
    uint32_t sha_mode_ext  : 2;  /*!< Extended mode */
    uint32_t sha_msglen    : 16; /*!< Message length in 512-bit blocks */
    uint32_t sha_srcaddr;       /*!< Source address */
    uint32_t result[16];          /*!< Result (8 x 32-bit for SHA-256, 16 x 32-bit for SHA-512) */
};
```

### Link Mode Functions

```c
void bflb_sha_link_init(struct bflb_device_s *dev);
void bflb_sha_link_deinit(struct bflb_device_s *dev);
void bflb_sha256_link_start(struct bflb_device_s *dev, struct bflb_sha256_link_ctx_s *ctx, int is224);
void bflb_sha512_link_start(struct bflb_device_s *dev, struct bflb_sha512_link_ctx_s *ctx, int is384);
int bflb_sha256_link_update(struct bflb_device_s *dev, struct bflb_sha256_link_ctx_s *ctx,
                            const uint8_t *input, uint32_t len);
int bflb_sha512_link_update(struct bflb_device_s *dev, struct bflb_sha512_link_ctx_s *ctx,
                            const uint8_t *input, uint64_t len);
void bflb_sha256_link_finish(struct bflb_device_s *dev, struct bflb_sha256_link_ctx_s *ctx, uint8_t *output);
void bflb_sha512_link_finish(struct bflb_device_s *dev, struct bflb_sha512_link_ctx_s *ctx, uint8_t *output);
```

## SHA Access Control

SHA hardware has access control to prevent conflicts between different cores/groups.

```c
/* Request SHA access for group 0 or group 1 */
int bflb_group0_request_sha_access(struct bflb_device_s *dev);
int bflb_group1_request_sha_access(struct bflb_device_s *dev);

/* Release SHA access */
void bflb_group0_release_sha_access(struct bflb_device_s *dev);
void bflb_group1_release_sha_access(struct bflb_device_s *dev);
```

**Access Control Register (0xFC):**
```c
#define SEC_ENG_SE_SHA_ID0_EN (1 << 1U)  /* SHA ID0 enable */
#define SEC_ENG_SE_SHA_ID1_EN (1 << 2U)  /* SHA ID1 enable */
```

## Timing Considerations

- The hardware processes one 512-bit block per trigger
- Timeout for each operation is 100ms
- For large data, use link mode (DMA) for better performance
- SHA-512 operations use 128-byte blocks vs 64-byte for SHA-256/SHA-1

## Direct Register Access

For fine-grained control, registers can be accessed directly:

```c
#define SEC_ENG_BASE 0x20004000
#define SHA_CTRL     (SEC_ENG_BASE + 0x00)
#define SHA_MSA      (SEC_ENG_BASE + 0x04)
#define SHA_STATUS   (SEC_ENG_BASE + 0x08)
#define SHA_HASH(n)  (SEC_ENG_BASE + 0x10 + (n) * 4)  /* n=0-15 */
```
