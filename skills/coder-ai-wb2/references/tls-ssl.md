# TLS/SSL API Reference

> Source file: `components/network/axk_protocol_stack/axk_tls/axk_tls.h`  
> Based on mbedTLS with TLS 1.2/TLS 1.3 support, providing certificate verification, PSK authentication, session resumption, and more.

---

## Overview

AXK-TLS is the transport layer security library for BL602, based on mbedTLS, supporting:
- TLS client/server
- Certificate authentication + PSK authentication
- Mutual (two-way) client authentication
- TLS session resumption
- Global CA certificate pool

---

## Header File

```c
#include "axk_tls.h"
```

---

## Connection States

```c
typedef enum axk_tls_conn_state {
    AXK_TLS_INIT = 0,       // Initialized
    AXK_TLS_CONNECTING,      // Connecting
    AXK_TLS_HANDSHAKE,       // Handshaking
    AXK_TLS_FAIL,            // Failed
    AXK_TLS_DONE,            // Completed
} axk_tls_conn_state_t;
```

---

## TLS Configuration Structures

### `axk_tls_cfg_t` — Client Configuration

```c
typedef struct axk_tls_cfg {
    // ALPN protocol list (for HTTP/2)
    const char **alpn_protos;

    // CA certificate (PEM or DER)
    union {
        const unsigned char *cacert_buf;
        const unsigned char *cacert_pem_buf;  // Backward compatible alias
    };
    union {
        unsigned int cacert_bytes;
        unsigned int cacert_pem_bytes;
    };

    // Client certificate (for mutual authentication)
    union {
        const unsigned char *clientcert_buf;
        const unsigned char *clientcert_pem_buf;
    };
    union {
        unsigned int clientcert_bytes;
        unsigned int clientcert_pem_bytes;
    };

    // Client private key
    union {
        const unsigned char *clientkey_buf;
        const unsigned char *clientkey_pem_buf;
    };
    union {
        unsigned int clientkey_bytes;
        unsigned int clientkey_pem_bytes;
    };

    const unsigned char *clientkey_password;  // Private key password
    unsigned int clientkey_password_len;

    bool non_block;                          // Non-blocking mode
    bool use_secure_element;                 // Use ATECC608A secure chip
    int timeout_ms;                          // Timeout (milliseconds)
    bool use_global_ca_store;                // Use global CA certificate pool
    const char *common_name;                 // Server CN verification
    bool skip_common_name;                   // Skip CN verification
    tls_keep_alive_cfg_t *keep_alive_cfg;   // TCP Keep-Alive
    const psk_hint_key_t *psk_hint_key;    // PSK authentication
    axk_err_t (*crt_bundle_attach)(void *conf); // Certificate bundle
    void *ds_data;                           // Digital signature parameters
    bool is_plain_tcp;                       // Plain TCP (unencrypted)
    struct ifreq *if_name;                   // Network interface
} axk_tls_cfg_t;
```

### `psk_hint_key_t` — PSK Authentication

```c
typedef struct psk_key_hint {
    const uint8_t *key;      // PSK key (binary)
    const size_t key_size;   // Key length
    const char *hint;       // PSK hint string
} psk_hint_key_t;
```

---

## Function Interface

### `axk_tls_init`

Creates a TLS context.

```c
axk_tls_t *axk_tls_init(void);
```

**Return value**: Returns TLS handle on success, NULL on failure.

---

### `axk_tls_conn_new_sync`

Creates a TLS connection synchronously (blocking).

```c
int axk_tls_conn_new_sync(const char *hostname,
                          int hostlen,
                          int port,
                          const axk_tls_cfg_t *cfg,
                          axk_tls_t *tls);
```

| Parameter | Description |
|-----------|-------------|
| `hostname` | Server domain name |
| `hostlen` | Domain name length |
| `port` | Port number |
| `cfg` | TLS configuration (can be NULL for plain TCP) |
| `tls` | TLS handle |

**Return value**: 1=success, 0=connection in progress, -1=failure

---

### `axk_tls_conn_http_new_sync`

Creates a TLS connection from a URL (synchronous).

```c
int axk_tls_conn_http_new_sync(const char *url,
                               const axk_tls_cfg_t *cfg,
                               axk_tls_t *tls);
```

---

### `axk_tls_conn_new_async`

Creates a TLS connection asynchronously (non-blocking).

```c
int axk_tls_conn_new_async(const char *hostname,
                           int hostlen,
                           int port,
                           const axk_tls_cfg_t *cfg,
                           axk_tls_t *tls);
```

---

### `axk_tls_conn_http_new_async`

Creates a TLS connection from a URL asynchronously.

```c
int axk_tls_conn_http_new_async(const char *url,
                                const axk_tls_cfg_t *cfg,
                                axk_tls_t *tls);
```

---

### `axk_tls_conn_write`

Sends data over a TLS connection.

```c
ssize_t axk_tls_conn_write(axk_tls_t *tls, const void *data, size_t datalen);
```

---

### `axk_tls_conn_read`

Receives data over a TLS connection.

```c
ssize_t axk_tls_conn_read(axk_tls_t *tls, void *data, size_t datalen);
```

---

### `axk_tls_conn_destroy`

Closes a TLS connection and frees resources.

```c
int axk_tls_conn_destroy(axk_tls_t *tls);
```

**Return value**: 0 on success, -1 on failure

---

### `axk_tls_get_bytes_avail`

Gets the number of readable bytes remaining in the current record layer.

```c
ssize_t axk_tls_get_bytes_avail(axk_tls_t *tls);
```

---

### `axk_tls_get_conn_sockfd`

Gets the underlying socket descriptor of a TLS connection.

```c
axk_err_t axk_tls_get_conn_sockfd(axk_tls_t *tls, int *sockfd);
```

---

### `axk_tls_plain_tcp_connect`

Creates a plain TCP connection (through the TLS layer).

```c
axk_err_t axk_tls_plain_tcp_connect(const char *host,
                                    int hostlen,
                                    int port,
                                    const axk_tls_cfg_t *cfg,
                                    axk_tls_error_handle_t error_handle,
                                    int *sockfd);
```

---

## Global CA Certificate Pool

### `axk_tls_init_global_ca_store`

Initializes the global CA certificate pool.

```c
axk_err_t axk_tls_init_global_ca_store(void);
```

---

### `axk_tls_set_global_ca_store`

Sets the global CA certificate (PEM format).

```c
axk_err_t axk_tls_set_global_ca_store(const unsigned char *cacert_pem_buf,
                                      const unsigned int cacert_pem_bytes);
```

---

### `axk_tls_free_global_ca_store`

Frees the global CA certificate pool.

```c
void axk_tls_free_global_ca_store(void);
```

---

### `axk_tls_get_global_ca_store`

Gets a pointer to the current global CA certificate pool.

```c
mbedtls_x509_crt *axk_tls_get_global_ca_store(void);
```

---

## Error Handling

### `axk_tls_get_and_clear_last_error`

Gets and clears the last TLS error.

```c
axk_err_t axk_tls_get_and_clear_last_error(axk_tls_error_handle_t h,
                                            int *axk_tls_code,
                                            int *axk_tls_flags);
```

---

### `axk_tls_get_and_clear_error_type`

Gets and clears an error of a specified type.

```c
axk_err_t axk_tls_get_and_clear_error_type(axk_tls_error_handle_t h,
                                            axk_tls_error_type_t err_type,
                                            int *error_code);
```

---

## Usage Examples

### Simple HTTPS Request

```c
#include "axk_tls.h"

static const char *request =
    "GET / HTTP/1.1\r\n"
    "Host: www.example.com\r\n"
    "User-Agent: BL602\r\n"
    "Connection: close\r\n"
    "\r\n";

void https_get_example(void)
{
    axk_tls_t *tls = axk_tls_init();
    if (!tls) return;

    axk_tls_cfg_t cfg = {
        .cacert_buf = (const unsigned char *)ca_cert_pem,
        .cacert_bytes = strlen(ca_cert_pem) + 1,
        .timeout_ms = 10000,
    };

    int ret = axk_tls_conn_new_sync("www.example.com", 16, 443, &cfg, tls);
    if (ret != 1) {
        printf("TLS connect failed: %d\r\n", ret);
        axk_tls_conn_destroy(tls);
        return;
    }

    // Send request
    axk_tls_conn_write(tls, request, strlen(request));

    // Read response
    char buf[1024];
    ssize_t len;
    while ((len = axk_tls_conn_read(tls, buf, sizeof(buf) - 1)) > 0) {
        buf[len] = '\0';
        printf("%s", buf);
    }

    axk_tls_conn_destroy(tls);
}
```

### PSK Authentication Mode

```c
static const uint8_t psk_key[] = { 0x01, 0x02, 0x03, 0x04 };
static const char psk_hint[] = "BL602_DEVICE";

psk_hint_key_t psk = {
    .key = psk_key,
    .key_size = sizeof(psk_key),
    .hint = psk_hint,
};

axk_tls_cfg_t cfg = {
    .psk_hint_key = &psk,
};
```

---

## TLS Keep-Alive Configuration

```c
typedef struct tls_keep_alive_cfg {
    bool keep_alive_enable;       // Enable
    int keep_alive_idle;         // Idle timeout (seconds)
    int keep_alive_interval;     // Probe interval (seconds)
    int keep_alive_count;         // Retry count
} tls_keep_alive_cfg_t;
```
