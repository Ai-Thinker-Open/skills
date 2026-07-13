# libSRTP2 Technical Reference Document

## Overview

libSRTP2 is an open-source SRTP (Secure Real-time Transport Protocol) library that provides encryption, authentication, and integrity protection for RTP/RTCP data. Developed by Cisco Systems, it is widely used in real-time communication scenarios such as VoIP, video conferencing, and WebRTC.

libSRTP2 supports two main encryption modes:

- **AES-CM (AES Counter Mode)**: AES encryption based on counter mode, combined with HMAC-SHA1 for message authentication
- **AES-GCM (AES Galois Counter Mode)**: AEAD (Authenticated Encryption with Associated Data) mode, performing encryption and authentication simultaneously

## Key Constants

libSRTP2 defines the following core constants:

| Constant Name | Value | Description |
|---------|-----|------|
| `SRTP_MASTER_KEY_LEN` | 30 | Nominal length of the Master Key |
| `SRTP_MAX_KEY_LEN` | 64 | Maximum supported key length (bytes) |
| `SRTP_MAX_TAG_LEN` | 16 | Maximum authentication tag length (bytes) |
| `SRTP_MAX_TRAILER_LEN` | 144 | Maximum trailer extension length (including tag and MKI) |
| `SRTP_SALT_LEN` | 14 | Key salt length (bytes) |
| `SRTP_AEAD_SALT_LEN` | 12 | GCM mode salt length (bytes) |

### AES Key Length Definitions

```c
#define SRTP_AES_128_KEY_LEN 16    // 128-bit AES key
#define SRTP_AES_192_KEY_LEN 24    // 192-bit AES key
#define SRTP_AES_256_KEY_LEN 32    // 256-bit AES key

// Full key length including salt
#define SRTP_AES_ICM_128_KEY_LEN_WSALT 30  // 14 + 16
#define SRTP_AES_ICM_256_KEY_LEN_WSALT 46  // 14 + 32
#define SRTP_AES_GCM_128_KEY_LEN_WSALT 28  // 12 + 16
#define SRTP_AES_GCM_256_KEY_LEN_WSALT 44  // 12 + 32
```

## Error Codes

libSRTP2 uses the `srtp_err_status_t` enum to define all error states:

```c
typedef enum {
    srtp_err_status_ok = 0,             // Operation succeeded
    srtp_err_status_fail = 1,           // Unspecified failure
    srtp_err_status_bad_param = 2,      // Unsupported parameter
    srtp_err_status_alloc_fail = 3,      // Memory allocation failed
    srtp_err_status_dealloc_fail = 4,    // Memory deallocation failed
    srtp_err_status_init_fail = 5,       // Initialization failed
    srtp_err_status_terminus = 6,        // Insufficient data length
    srtp_err_status_auth_fail = 7,       // Authentication failed
    srtp_err_status_cipher_fail = 8,     // Encryption failed
    srtp_err_status_replay_fail = 9,     // Replay attack detection failed (bad index)
    srtp_err_status_replay_old = 10,     // Replay attack detection failed (index too old)
    srtp_err_status_algo_fail = 11,      // Algorithm test failed
    srtp_err_status_no_such_op = 12,      // Unsupported operation
    srtp_err_status_no_ctx = 13,          // No suitable context found
    srtp_err_status_key_expired = 15,     // Key has expired
    srtp_err_status_bad_mki = 25,         // Invalid MKI
    srtp_err_status_pkt_idx_old = 26,     // Packet index too old
    srtp_err_status_pkt_idx_adv = 27      // Packet index advanced, reset needed
} srtp_err_status_t;
```

## Core Data Structures

### srtp_crypto_policy_t

Crypto policy structure, defining specific encryption and authentication parameters:

```c
typedef struct srtp_crypto_policy_t {
    srtp_cipher_type_id_t cipher_type;  // Cipher algorithm type
    int cipher_key_len;                  // Cipher key length
    srtp_auth_type_id_t auth_type;       // Authentication algorithm type
    int auth_key_len;                    // Authentication key length
    int auth_tag_len;                    // Authentication tag length
    srtp_sec_serv_t sec_serv;           // Security service flags
} srtp_crypto_policy_t;
```

### SSRC Type

```c
typedef enum {
    ssrc_undefined = 0,    // Undefined SSRC
    ssrc_specific = 1,     // Specific SSRC value
    ssrc_any_inbound = 2, // Any inbound SSRC (used by srtp_unprotect)
    ssrc_any_outbound = 3 // Any outbound SSRC (used by srtp_protect)
} srtp_ssrc_type_t;
```

### srtp_policy_t

SRTP session policy structure, defining the policy for a single SRTP stream:

```c
typedef struct srtp_policy_t {
    srtp_ssrc_t ssrc;               // SSRC value or wildcard type
    srtp_crypto_policy_t rtp;        // RTP crypto policy
    srtp_crypto_policy_t rtcp;      // RTCP crypto policy
    unsigned char *key;              // Master key pointer
    srtp_master_key_t **keys;       // Array of multiple master keys
    unsigned long num_master_keys;   // Number of master keys
    srtp_ekt_policy_t ekt;          // EKT policy pointer
    unsigned long window_size;       // Replay protection window size
    int allow_repeat_tx;            // Whether to allow repeat transmission
    int *enc_xtn_hdr;               // List of extension header IDs to encrypt
    int enc_xtn_hdr_count;          // Number of extension headers
    struct srtp_policy_t *next;     // Pointer to next policy
} srtp_policy_t;
```

### srtp_t (srtp_session_t)

Session handle type, pointer to the internal session context:

```c
typedef srtp_ctx_t *srtp_t;  // SRTP session handle
```

## Cipher Suites

libSRTP2 supports multiple predefined cipher suites, initialized via the following functions:

### AES-CM Series

| Cipher Suite | Function | Description |
|---------|------|------|
| AES_CM_128_HMAC_SHA1_80 | `srtp_crypto_policy_set_aes_cm_128_hmac_sha1_80()` | AES-128 Counter Mode + HMAC-SHA1-80 bit auth |
| AES_CM_128_HMAC_SHA1_32 | `srtp_crypto_policy_set_aes_cm_128_hmac_sha1_32()` | AES-128 + HMAC-SHA1-32 bit auth (RTP only) |
| AES_CM_256_HMAC_SHA1_80 | `srtp_crypto_policy_set_aes_cm_256_hmac_sha1_80()` | AES-256 + HMAC-SHA1-80 bit auth |
| AES_CM_256_HMAC_SHA1_32 | `srtp_crypto_policy_set_aes_cm_256_hmac_sha1_32()` | AES-256 + HMAC-SHA1-32 bit auth |
| AES_CM_192_HMAC_SHA1_80 | `srtp_crypto_policy_set_aes_cm_192_hmac_sha1_80()` | AES-192 + HMAC-SHA1-80 bit auth |

### AES-GCM Series

| Cipher Suite | Function | Description |
|---------|------|------|
| AES_GCM_128_16 | `srtp_crypto_policy_set_aes_gcm_128_16_auth()` | AES-128-GCM + 16-byte auth tag |
| AES_GCM_256_16 | `srtp_crypto_policy_set_aes_gcm_256_16_auth()` | AES-256-GCM + 16-byte auth tag |
| AES_GCM_128_8 | `srtp_crypto_policy_set_aes_gcm_128_8_auth()` | AES-128-GCM + 8-byte auth tag |
| AES_GCM_256_8 | `srtp_crypto_policy_set_aes_gcm_256_8_auth()` | AES-256-GCM + 8-byte auth tag |

### Security Service Flags

```c
typedef enum {
    sec_serv_none = 0,         // No security services enabled
    sec_serv_conf = 1,         // Encryption only (confidentiality)
    sec_serv_auth = 2,        // Authentication only
    sec_serv_conf_and_auth = 3 // Encryption + Authentication
} srtp_sec_serv_t;
```

## ROC (Roll-over Counter) Synchronization Mechanism

The ROC is SRTP's core synchronization mechanism for handling RTP sequence number (16-bit) wrap-around.

### How It Works

1. **Sequence Number Wrap-around**: RTP sequence numbers are only 16-bit (0-65535); when exceeding 65535, they wrap to 0
2. **ROC Extension**: SRTP uses a 32-bit ROC to extend the 16-bit sequence number, forming a complete 48-bit packet index
3. **Synchronization Condition**: When the received sequence number is more than 32768 (2^15) smaller than the previous one, the sequence number has wrapped, and ROC needs to be incremented by 1

### ROC Maintenance

```c
// ROC update logic example
if (incoming_seq > last_seq) {
    if (incoming_seq - last_seq > 32768) {
        roc--;  // Sequence number wrapped backwards
    } else {
        // Normal order
    }
} else {
    if (last_seq - incoming_seq > 32768) {
        roc++;  // Sequence number wrapped forward
    }
}
```

### Replay Protection

libSRTP2 provides window-based replay protection:

- `window_size`: Defines the replay detection window size, default 128 bits
- Packets older than the left edge of the window are rejected
- Supports configuring `allow_repeat_tx` to allow retransmission with the same sequence number

## Core API

### Library Initialization and Shutdown

```c
// Initialize the SRTP library (must be called before any other SRTP functions)
srtp_err_status_t srtp_init(void);

// Shut down the SRTP library (call after all SRTP operations are complete)
srtp_err_status_t srtp_shutdown(void);
```

### Session Creation and Deallocation

```c
// Create an SRTP session
// session: output parameter, returns session handle
// policy: input parameter, session policy configuration
srtp_err_status_t srtp_create(srtp_t *session, const srtp_policy_t *policy);

// Deallocate an SRTP session
srtp_err_status_t srtp_dealloc(srtp_t s);
```

### Adding/Removing Streams

```c
// Add a new SRTP stream to an existing session
srtp_err_status_t srtp_add_stream(srtp_t session, const srtp_policy_t *policy);

// Remove a stream with the specified SSRC from the session
srtp_err_status_t srtp_remove_stream(srtp_t session, uint32_t ssrc);

// Update keys for all streams in the session (preserving ROC values)
srtp_err_status_t srtp_update(srtp_t session, const srtp_policy_t *policy);

// Update the key for a specific stream
srtp_err_status_t srtp_update_stream(srtp_t session, const srtp_policy_t *policy);
```

### RTP Protection

```c
// Protect an RTP packet (sender side)
// ctx: session handle
// rtp_hdr: input RTP packet, output as SRTP packet
// len_ptr: input packet length, output protected length
srtp_err_status_t srtp_protect(srtp_t ctx, void *rtp_hdr, int *len_ptr);

// Protect version with MKI
srtp_err_status_t srtp_protect_mki(srtp_ctx_t *ctx,
                                    void *rtp_hdr,
                                    int *pkt_octet_len,
                                    unsigned int use_mki,
                                    unsigned int mki_index);

// Unprotect (receiver side)
// ctx: session handle
// srtp_hdr: input SRTP packet, output as RTP packet
// len_ptr: input packet length, output unprotected length
srtp_err_status_t srtp_unprotect(srtp_t ctx, void *srtp_hdr, int *len_ptr);

// Unprotect version with MKI
srtp_err_status_t srtp_unprotect_mki(srtp_t ctx,
                                      void *srtp_hdr,
                                      int *len_ptr,
                                      unsigned int use_mki);
```

### RTCP Protection

```c
// Protect an RTCP packet
srtp_err_status_t srtp_protect_rtcp(srtp_t ctx, void *rtcp_hdr, int *len_ptr);

// Unprotect RTCP
srtp_err_status_t srtp_unprotect_rtcp(srtp_t ctx, void *srtcp_hdr, int *len_ptr);
```

### Policy Helper Functions

```c
// Set default RTP policy (AES_CM_128_HMAC_SHA1_80)
void srtp_crypto_policy_set_rtp_default(srtp_crypto_policy_t *p);

// Set default RTCP policy
void srtp_crypto_policy_set_rtcp_default(srtp_crypto_policy_t *p);

// Set policy from SRTP Profile
srtp_err_status_t srtp_crypto_policy_set_from_profile_for_rtp(
    srtp_crypto_policy_t *policy,
    srtp_profile_t profile);

srtp_err_status_t srtp_crypto_policy_set_from_profile_for_rtcp(
    srtp_crypto_policy_t *policy,
    srtp_profile_t profile);

// Get the master key length for a Profile
unsigned int srtp_profile_get_master_key_length(srtp_profile_t profile);

// Get the master salt length for a Profile
unsigned int srtp_profile_get_master_salt_length(srtp_profile_t profile);
```

## Code Examples

### Basic Usage Flow

```c
#include "srtp.h"
#include <stdio.h>
#include <string.h>

#define RTP_PAYLOAD_LEN 160
#define RTP_HEADER_LEN 12

// RTP packet structure (simplified)
typedef struct {
    uint8_t version_p_x_cc;    // V, P, X, CC fields
    uint8_t m_pt;              // M and Payload Type
    uint16_t seq;               // Sequence number (network byte order)
    uint32_t ts;                // Timestamp
    uint32_t ssrc;              // SSRC
    uint8_t payload[RTP_PAYLOAD_LEN];
} rtp_packet_t;

// AES-GCM 256 encryption example
int example_aes_gcm_256()
{
    srtp_err_status_t err;
    srtp_t session;
    srtp_policy_t policy;

    // Master key: includes key and salt
    // GCM-256 mode: key 32 bytes + salt 12 bytes = 44 bytes
    unsigned char key[SRTP_AES_GCM_256_KEY_LEN_WSALT] = {
        0x00, 0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07,
        0x08, 0x09, 0x0a, 0x0b, 0x0c, 0x0d, 0x0e, 0x0f,
        0x10, 0x11, 0x12, 0x13, 0x14, 0x15, 0x16, 0x17,
        0x18, 0x19, 0x1a, 0x1b, 0x1c, 0x1d, 0x1e, 0x1f,
        // Salt (used for GCM IV)
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00
    };

    // Initialize library
    err = srtp_init();
    if (err != srtp_err_status_ok) {
        printf("srtp_init failed: %d\n", err);
        return -1;
    }

    // Initialize policy structure
    memset(&policy, 0, sizeof(policy));

    // Configure SSRC (any inbound)
    policy.ssrc.type = ssrc_any_inbound;
    policy.ssrc.value = 0;

    // Set RTP crypto policy: AES-GCM-256 + 16-byte auth tag
    srtp_crypto_policy_set_aes_gcm_256_16_auth(&policy.rtp);

    // Set RTCP crypto policy
    srtp_crypto_policy_set_aes_gcm_256_16_auth(&policy.rtcp);

    // Set key
    policy.key = key;

    // Set replay protection window
    policy.window_size = 128;

    // Allow retransmission
    policy.allow_repeat_tx = 0;

    // Create session
    err = srtp_create(&session, &policy);
    if (err != srtp_err_status_ok) {
        printf("srtp_create failed: %d\n", err);
        return -1;
    }

    // Prepare RTP packet
    rtp_packet_t rtp_pkt;
    memset(&rtp_pkt, 0, sizeof(rtp_pkt));
    rtp_pkt.version_p_x_cc = 0x80;  // RTP version 2
    rtp_pkt.m_pt = 0x00;           // PT = 0 (PCM u-law)
    rtp_pkt.seq = 1;               // Sequence number
    rtp_pkt.ts = 160;              // Timestamp
    rtp_pkt.ssrc = 0x12345678;     // SSRC

    // Fill payload data
    memset(rtp_pkt.payload, 0x55, RTP_PAYLOAD_LEN);

    // Protect RTP packet
    int len = RTP_HEADER_LEN + RTP_PAYLOAD_LEN;
    err = srtp_protect(session, &rtp_pkt, &len);
    if (err != srtp_err_status_ok) {
        printf("srtp_protect failed: %d\n", err);
        srtp_dealloc(session);
        return -1;
    }

    printf("Protected RTP packet, new length: %d\n", len);
    printf("SRTP header + encrypted payload + auth tag (16 bytes)\n");

    // Unprotect RTP packet
    int unprotect_len = len;
    err = srtp_unprotect(session, &rtp_pkt, &unprotect_len);
    if (err != srtp_err_status_ok) {
        printf("srtp_unprotect failed: %d\n", err);
        srtp_dealloc(session);
        return -1;
    }

    printf("Unprotected RTP packet, length: %d\n", unprotect_len);

    // Deallocate session
    srtp_dealloc(session);

    return 0;
}

// AES-CM 128 Encryption Example
int example_aes_cm_128()
{
    srtp_err_status_t err;
    srtp_t session;
    srtp_policy_t policy;

    // Master key: 30 bytes
    // CM mode: key 16 bytes + salt 14 bytes = 30 bytes
    unsigned char key[SRTP_MASTER_KEY_LEN] = {
        0x00, 0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07,
        0x08, 0x09, 0x0a, 0x0b, 0x0c, 0x0d, 0x0e, 0x0f,
        // Salt
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00
    };

    // Initialize library
    err = srtp_init();
    if (err != srtp_err_status_ok) {
        return -1;
    }

    // Initialize policy
    memset(&policy, 0, sizeof(policy));
    policy.ssrc.type = ssrc_any_outbound;
    policy.ssrc.value = 0;

    // Use default policy: AES-CM-128 + HMAC-SHA1-80
    srtp_crypto_policy_set_aes_cm_128_hmac_sha1_80(&policy.rtp);
    srtp_crypto_policy_set_aes_cm_128_hmac_sha1_80(&policy.rtcp);

    policy.key = key;
    policy.window_size = 128;
    policy.allow_repeat_tx = 0;

    // Create session
    err = srtp_create(&session, &policy);
    if (err != srtp_err_status_ok) {
        return -1;
    }

    // Prepare and protect RTP packet
    rtp_packet_t rtp_pkt = {0};
    rtp_pkt.version_p_x_cc = 0x80;
    rtp_pkt.m_pt = 0x60;  // PT = 96 (dynamic type)
    rtp_pkt.seq = 100;
    rtp_pkt.ts = 1000;
    rtp_pkt.ssrc = 0x87654321;

    int len = RTP_HEADER_LEN + RTP_PAYLOAD_LEN;
    err = srtp_protect(session, &rtp_pkt, &len);
    if (err != srtp_err_status_ok) {
        printf("Protect failed: %d\n", err);
        srtp_dealloc(session);
        return -1;
    }

    printf("Protected packet size: %d bytes (includes 10-byte auth tag)\n", len);

    // Unprotect verification
    int unprotect_len = len;
    err = srtp_unprotect(session, &rtp_pkt, &unprotect_len);
    if (err != srtp_err_status_ok) {
        printf("Unprotect failed: %d\n", err);
    }

    srtp_dealloc(session);
    return 0;
}

// Multi-Stream Configuration Example
int example_multi_stream()
{
    srtp_err_status_t err;
    srtp_t session;
    srtp_policy_t policy[3];  // Three policies
    srtp_policy_t *policy_list = NULL;

    err = srtp_init();
    if (err != srtp_err_status_ok) {
        return -1;
    }

    // Stream 1: SSRC = 0x11111111
    memset(&policy[0], 0, sizeof(policy[0]));
    policy[0].ssrc.type = ssrc_specific;
    policy[0].ssrc.value = 0x11111111;
    srtp_crypto_policy_set_aes_cm_128_hmac_sha1_80(&policy[0].rtp);
    policy[0].key = (unsigned char *)"0123456789abcdef0123456789abcdef";  // 30 bytes
    policy[0].next = &policy[1];

    // Stream 2: SSRC = 0x22222222
    memset(&policy[1], 0, sizeof(policy[1]));
    policy[1].ssrc.type = ssrc_specific;
    policy[1].ssrc.value = 0x22222222;
    srtp_crypto_policy_set_aes_gcm_128_16_auth(&policy[1].rtp);
    policy[1].key = (unsigned char *)"fedcba9876543210fedcba9876543210";  // 30 bytes
    policy[1].next = &policy[2];

    // Stream 3: wildcard (matches all other SSRCs)
    memset(&policy[2], 0, sizeof(policy[2]));
    policy[2].ssrc.type = ssrc_any_inbound;
    policy[2].ssrc.value = 0;
    srtp_crypto_policy_set_aes_cm_128_hmac_sha1_80(&policy[2].rtp);
    policy[2].key = (unsigned char *)"aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa";  // 30 bytes
    policy[2].next = NULL;  // End of list

    // Create session (pass in policy linked list)
    err = srtp_create(&session, policy);
    if (err != srtp_err_status_ok) {
        return -1;
    }

    printf("Multi-stream SRTP session created\n");

    srtp_dealloc(session);
    return 0;
}
```

### Key Update Example

```c
// Dynamically Update Session Key
int example_key_update()
{
    srtp_err_status_t err;
    srtp_t session;
    srtp_policy_t policy;
    unsigned char new_key[SRTP_MASTER_KEY_LEN];

    // Initialization (omitted...)
    // err = srtp_init();
    // err = srtp_create(&session, &policy);

    // Generate a new key (in practice, use a secure random number generator)
    memset(new_key, 0xAB, SRTP_MASTER_KEY_LEN);

    // Update key (preserve ROC value for seamless switchover)
    memset(&policy, 0, sizeof(policy));
    policy.ssrc.type = ssrc_any_inbound;
    srtp_crypto_policy_set_aes_cm_128_hmac_sha1_80(&policy.rtp);
    policy.key = new_key;

    err = srtp_update(session, &policy);
    if (err != srtp_err_status_ok) {
        printf("Key update failed: %d\n", err);
        return -1;
    }

    printf("Session key updated successfully\n");
    return 0;
}
```

## AES-GCM Mode in Detail

AES-GCM is an AEAD (Authenticated Encryption with Associated Data) algorithm that simultaneously provides, in a single encryption operation:

- **Encryption**: Using Galois Counter Mode
- **Authentication**: Using GMAC (Galois Message Authentication Code)

### Differences Between AES-GCM and AES-CM

| Feature | AES-CM + HMAC | AES-GCM |
|------|---------------|---------|
| Encryption Algorithm | AES Counter Mode | AES Galois Counter Mode |
| Authentication Algorithm | HMAC-SHA1 (separate computation) | GMAC (inline authentication) |
| Auth Tag Location | Trailer | Trailer |
| Additional Data (AD) | Needs separate handling | Built-in support |
| Computational Efficiency | Requires two calls | Single call completes both |
| Typical Tag Length | 80-bit (10 bytes) or 32-bit | 128-bit (16 bytes) or 64-bit (8 bytes) |

### GCM Key Structure

```c
// AES-GCM-128 full key: 16-byte key + 12-byte salt = 28 bytes
typedef struct {
    uint8_t key[16];    // AES key
    uint8_t salt[12];   // GCM IV salt
} aes_gcm_128_key_t;

// AES-GCM-256 full key: 32-byte key + 12-byte salt = 44 bytes
typedef struct {
    uint8_t key[32];    // AES key
    uint8_t salt[12];   // GCM IV salt
} aes_gcm_256_key_t;
```

### GCM IV Construction

The IV (Initialization Vector) construction for GCM mode in SRTP:

```
IV = (salt << 16) | ROC | SEQ
```

- `salt`: 12-byte salt value
- `ROC`: 32-bit roll-over counter
- `SEQ`: 16-bit RTP sequence number

## Thread Safety

libSRTP2 itself is **not thread-safe**. When using it, note the following:

1. **Each SRTP stream is independent**: Different `srtp_t` instances can be used in parallel
2. **Multiple threads on the same session**: It is not recommended for multiple threads to simultaneously call protect/unprotect functions on the same `srtp_t`
3. **Thread isolation**: It is recommended for each thread to use its own `srtp_t` instance, or protect access with a mutex

## Common Error Handling

```c
// Error Handling Example
srtp_err_status_t handle_srtp_error(srtp_err_status_t err)
{
    switch (err) {
        case srtp_err_status_ok:
            return err;
        case srtp_err_status_auth_fail:
            printf("Authentication failed - packet corrupted or tampered\n");
            break;
        case srtp_err_status_replay_fail:
            printf("Replay attack detected\n");
            break;
        case srtp_err_status_pkt_idx_old:
            printf("Packet index too old\n");
            break;
        case srtp_err_status_key_expired:
            printf("Session key expired\n");
            break;
        default:
            printf("SRTP error: %d\n", err);
            break;
    }
    return err;
}
```

## Performance Considerations

1. **Batching**: For high-bandwidth applications, consider batch processing multiple packets
2. **Memory Alignment**: `srtp_protect()` assumes data is aligned on 32-bit boundaries
3. **Buffer Size**: Before calling `srtp_protect()`, ensure the buffer has `SRTP_MAX_TRAILER_LEN` extra space
4. **GCM vs CM**: GCM mode is generally faster than the CM + HMAC combination (single pass encryption + authentication)

## References

- **RFC 3711**: SRTP (Secure Real-time Transport Protocol)
- **RFC 6188**: Additional AES-CTR Modes for SRTP
- **RFC 7714**: AES-GCM Authenticated Encryption for SRTP
- **RFC 4568**: SDP Security Descriptions for Media Streams
- **IANA SRTP Protection Profile**: https://www.iana.org/assignments/srtp-protection/srtp-protection.xhtml
- **libSRTP Official Documentation**: https://github.com/cisco/libsrtp
