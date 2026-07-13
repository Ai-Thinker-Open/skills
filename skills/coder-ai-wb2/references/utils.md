# utils - Utility Components

## Overview

The utils component provides a collection of general-purpose utility functions for embedded systems, including encoding/decoding, cryptographic primitives, data structures, and logging. It is designed for resource-constrained environments.

## Location

```
components/utils/
```

## Key Files

### Headers (include/)

| File | Description |
|------|-------------|
| `utils_base64.h` | Base64 encoding/decoding |
| `utils_crc.h` | CRC16/CRC32 checksums |
| `utils_sha1.h` | SHA-1 hash |
| `utils_sha256.h` | SHA-256 hash |
| `utils_md5.h` | MD5 hash |
| `utils_hmac.h` | HMAC operations |
| `utils_hex.h` | Binary to hex conversion |
| `utils_hexdump.h` | Hex dump utilities |
| `utils_string.h` | String/memory operations |
| `utils_list.h` | Linked list data structures |
| `utils_rbtree.h` | Red-black tree |
| `utils_ringblk.h` | Ring block buffer |
| `utils_memp.h` | Memory pool |
| `utils_fec.h` | Forward error correction |
| `utils_bitmap_window.h` | Bitmap window |
| `utils_time.h` | Time/date utilities |
| `utils_notifier.h` | Notifier events |
| `utils_tlv_bl.h` | TLV format |
| `utils_log.h` | Logging framework |
| `utils_debug.h` | Debug utilities |
| `utils_dns.h` | DNS utilities |
| `utils_getopt.h` | Command-line option parsing |
| `utils_psk_fast.h` | Pre-shared key fast path |

### Implementation (src/)

| File | Description |
|------|-------------|
| `utils_log.c` | Logging implementation |
| `utils_sha256.c` | SHA-256 implementation |
| `utils_sha1.c` | SHA-1 implementation |
| `utils_ringblk.c` | Ring block buffer |
| `utils_memp.c` | Memory pool |
| `utils_fec.c` | FEC implementation |

---

## Data Structures

### List (utils_list.h)

Single linked list node:

```c
struct utils_list_hdr {
    struct utils_list_hdr *next;
};
```

List container:

```c
struct utils_list {
    struct utils_list_hdr *first;
    struct utils_list_hdr *last;
};
```

Double linked list node:

```c
typedef struct utils_dlist_s {
    struct utils_dlist_s *prev;
    struct utils_dlist_s *next;
} utils_dlist_t;
```

Single linked list node (for ringblk):

```c
typedef struct utils_slist_s {
    struct utils_slist_s *next;
} utils_slist_t;
```

### Ring Block Buffer (utils_ringblk.h)

Block statuses:

```c
enum utils_rbb_status {
    RBB_BLK_UNUSED,   // Unused after init or blk_free()
    RBB_BLK_INITED,   // After blk_alloc()
    RBB_BLK_PUT,      // After blk_put()
    RBB_BLK_GET,      // After blk_get()
};
```

Ring block buffer:

```c
struct utils_rbb {
    uint8_t *buf;
    uint32_t buf_size;
    utils_rbb_blk_t blk_set;       // All blocks
    uint32_t blk_max_num;
    utils_slist_t blk_list;        // Init'd and put blocks
};
typedef struct utils_rbb *utils_rbb_t;
```

Block queue for contiguous memory access:

```c
struct utils_rbb_blk_queue {
    utils_rbb_blk_t blocks;
    uint32_t blk_num;
};
```

### Time/Date (utils_time.h)

```c
typedef struct {
    unsigned char ntp_hour;
    unsigned char ntp_minute;
    unsigned char ntp_second;
    unsigned char ntp_week_day;
    unsigned char ntp_date;
    unsigned char ntp_month;
    unsigned char leap_days;
    unsigned char leap_year_ind;
    unsigned int ntp_year;
    unsigned int days_since_epoch;
    unsigned int day_of_year; 
} utils_time_date_t;
```

---

## Core API

### Base64 (utils_base64.h)

```c
iotx_err_t utils_base64encode(const uint8_t *data, uint32_t inputLength, 
                              uint32_t outputLenMax, uint8_t *encodedData, 
                              uint32_t *outputLength);

iotx_err_t utils_base64decode(const uint8_t *data, uint32_t inputLength, 
                              uint32_t outputLenMax, uint8_t *decodedData, 
                              uint32_t *outputLength);
```

### CRC (utils_crc.h)

```c
uint16_t utils_crc16(void *dataIn, uint32_t len);
uint32_t utils_crc32(void *dataIn, uint32_t len);
uint16_t utils_crc16_ccitt(void *dataIn, uint32_t len);

// Streaming CRC32
void utils_crc32_stream_init(struct crc32_stream_ctx *ctx);
void utils_crc32_stream_feed(struct crc32_stream_ctx *ctx, uint8_t data);
void utils_crc32_stream_feed_block(struct crc32_stream_ctx *ctx, uint8_t *data, uint32_t len);
uint32_t utils_crc32_stream_results(struct crc32_stream_ctx *ctx);
```

### SHA-256 (utils_sha256.h)

```c
void utils_sha256_init(iot_sha256_context *ctx);
void utils_sha256_free(iot_sha256_context *ctx);
void utils_sha256_clone(iot_sha256_context *dst, const iot_sha256_context *src);
void utils_sha256_starts(iot_sha256_context *ctx);
void utils_sha256_update(iot_sha256_context *ctx, const unsigned char *input, uint32_t ilen);
void utils_sha256_finish(iot_sha256_context *ctx, uint8_t output[32]);
void utils_sha256(const uint8_t *input, uint32_t ilen, uint8_t output[32]);
```

### MD5 (utils_md5.h)

```c
void utils_md5_init(iot_md5_context *ctx);
void utils_md5_free(iot_md5_context *ctx);
void utils_md5_clone(iot_md5_context *dst, const iot_md5_context *src);
void utils_md5_starts(iot_md5_context *ctx);
void utils_md5_update(iot_md5_context *ctx, const unsigned char *input, size_t ilen);
void utils_md5_finish(iot_md5_context *ctx, unsigned char output[16]);
void utils_md5(const unsigned char *input, size_t ilen, unsigned char output[16]);
```

### Hex Conversion (utils_hex.h)

```c
char *utils_bin2hex(char *dst, const void *src, size_t count);
size_t utils_hex2bin(const char *hex, size_t hexlen, uint8_t *buf, size_t buflen);
```

### Time (utils_time.h)

```c
int utils_time_date_from_epoch(unsigned int epoch, utils_time_date_t *date);
```

### String/Memory (utils_string.h)

```c
// Parsing utilities
void get_bytearray_from_string(char** params, uint8_t *result, int array_size);
void get_uint8_from_string(char** params, uint8_t *result);
void get_uint16_from_string(char** params, uint16_t *result);
void get_uint32_from_string(char** params, uint32_t *result);
void utils_parse_number(const char *str, char sep, uint8_t *buf, int buflen, int base);

// Aligned memory operations
void utils_memcpy8(void *dst, void *src, size_t len);
void utils_memcpy16(void *dst, void *src, size_t len);
void utils_memcpy32(void *dst, void *src, size_t len);
void utils_memcpy64(void *dst, void *src, size_t len);
void utils_memset8(void *src, uint8_t n, size_t len);
void utils_memset16(void *src, uint16_t n, size_t len);
void utils_memset32(void *src, uint32_t n, size_t len);
void utils_memset64(void *src, uint64_t n, size_t len);
void utils_memset8_with_seq(void *src, uint8_t seq, size_t len);
// ... similar for 16/32/64 variants

// Memory drain with pattern check
void *utils_memdrain8_with_check(void *src, size_t len, uint8_t seq);
void *utils_memdrain16_with_check(void *src, size_t len, uint16_t seq);
void *utils_memdrain32_with_check(void *src, size_t len, uint32_t seq);
void *utils_memdrain64_with_check(void *src, size_t len, uint64_t seq);
```

### Ring Block Buffer (utils_ringblk.h)

```c
// Create/destroy
utils_rbb_t utils_rbb_create(uint32_t buf_size, uint32_t blk_max_num);
void utils_rbb_destroy(utils_rbb_t rbb);

// Block allocation
utils_rbb_blk_t utils_rbb_blk_alloc(utils_rbb_t rbb, uint32_t blk_size);
void utils_rbb_blk_put(utils_rbb_blk_t block);
utils_rbb_blk_t utils_rbb_blk_get(utils_rbb_t rbb);
uint32_t utils_rbb_blk_size(utils_rbb_blk_t block);
uint8_t *utils_rbb_blk_buf(utils_rbb_blk_t block);
void utils_rbb_blk_free(utils_rbb_t rbb, utils_rbb_blk_t block);

// Queue operations (for contiguous memory access)
uint32_t utils_rbb_blk_queue_get(utils_rbb_t rbb, uint32_t queue_data_len, 
                                  utils_rbb_blk_queue_t blk_queue);
uint32_t utils_rbb_blk_queue_len(utils_rbb_blk_queue_t blk_queue);
uint8_t *utils_rbb_blk_queue_buf(utils_rbb_blk_queue_t blk_queue);
void utils_rbb_blk_queue_free(utils_rbb_t rbb, utils_rbb_blk_queue_t blk_queue);
```

### List Macros (utils_list.h)

```c
// Container_of and offset
#define utils_offsetof(type, member)   ((size_t)&(((type *)0)->member))
#define utils_container_of(ptr, type, member) \
    ((type *) ((char *) (ptr) - utils_offsetof(type, member)))

// Double linked list helpers
#define UTILS_DLIST_HEAD(name)         utils_dlist_t name = UTILS_DLIST_HEAD_INIT(name)
#define utils_dlist_entry(addr, type, member) \
    ((type *)((long)addr - utils_offsetof(type, member)))

// List iteration
#define utils_dlist_for_each(pos, head) \
    for (pos = (head)->next; pos != (head); pos = pos->next)

#define utils_dlist_for_each_entry(queue, node, type, member) \
    for (node = utils_container_of((queue)->next, type, member); \
         &node->member != (queue); \
         node = utils_container_of(node->member.next, type, member))

#define utils_dlist_for_each_entry_safe(queue, n, node, type, member) \
    for (node = utils_container_of((queue)->next, type, member),  \
         n = (queue)->next ? (queue)->next->next : NULL;        \
         &node->member != (queue);                              \
         node = utils_container_of(n, type, member), n = n ? n->next : NULL)
```

### Logging (utils_log.h)

```c
#define log_trace(M, ...)   custom_log("TRACE ", M, ##__VA_ARGS__)
#define log_debug(M, ...)   custom_log("DEBUG ", M, ##__VA_ARGS__)
#define log_info(M, ...)    custom_log("INFO  ", M, ##__VA_ARGS__)
#define log_warn(M, ...)    custom_log("WARN  ", M, ##__VA_ARGS__)
#define log_error(M, ...)   custom_log("ERROR ", M, ##__VA_ARGS__)
#define log_assert(M, ...)  custom_log("ASSERT", M, ##__VA_ARGS__)

#define log_buf(pbuf, len)  log_buf_out(SHORT_FILE, __LINE__, pbuf, len, LOG_BUF_OUT_DATA_TYPE_HEX)
```

---

## Usage Examples

### SHA-256 Hash

```c
#include "utils_sha256.h"

uint8_t hash[32];
const uint8_t data[] = "Hello, world!";

utils_sha256(data, strlen((const char*)data), hash);
```

### Base64 Encode/Decode

```c
#include "utils_base64.h"

uint8_t encoded[64];
uint32_t encoded_len;

utils_base64encode(data, data_len, sizeof(encoded), encoded, &encoded_len);
```

### Using a Ring Block Buffer

```c
#include "utils_ringblk.h"

#define BUF_SIZE 1024
#define MAX_BLOCKS 16

uint8_t buffer[BUF_SIZE];
struct utils_rbb_blk blocks[MAX_BLOCKS];
utils_rbb_t rbb = utils_rbb_create(BUF_SIZE, MAX_BLOCKS);

// Allocate and use a block
utils_rbb_blk_t blk = utils_rbb_blk_alloc(rbb, 64);
if (blk) {
    uint8_t *buf = utils_rbb_blk_buf(blk);
    // write data to buf
    utils_rbb_blk_put(blk);
}

// Get available blocks
utils_rbb_blk_t got = utils_rbb_blk_get(rbb);
```

### Linked List Usage

```c
#include "utils_list.h"

struct my_node {
    int value;
    utils_dlist_t link;
};

UTILS_DLIST_HEAD(my_list);

struct my_node node1 = { .value = 1 };
struct my_node node2 = { .value = 2 };

utils_dlist_add(&node1.link, &my_list);
utils_dlist_add_tail(&node2.link, &my_list);

// Iterate
utils_dlist_t *pos;
utils_dlist_for_each(pos, &my_list) {
    struct my_node *n = utils_dlist_entry(pos, struct my_node, link);
    // use n->value
}
```

### CRC32 Streaming

```c
#include "utils_crc.h"

struct crc32_stream_ctx ctx;
utils_crc32_stream_init(&ctx);

uint8_t data[] = { 0x01, 0x02, 0x03, 0x04 };
utils_crc32_stream_feed_block(&ctx, data, sizeof(data));

uint32_t crc = utils_crc32_stream_results(&ctx);
```
