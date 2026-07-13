# MbedTLS SSL/TLS Programming Guide for BL616/BL618

This document covers MbedTLS SSL/TLS programming for Bouffalo Lab BL616/BL618 chips using the Bouffalo SDK. The SDK includes mbedtls v3.x in `components/crypto/mbedtls/`.

## Header Files

```c
#include "mbedtls/net_sockets.h"    // Network socket abstraction
#include "mbedtls/ssl.h"            // SSL/TLS core
#include "mbedtls/x509_crt.h"      // Certificate parsing
#include "mbedtls/pk.h"            // Public key (for client certs)
#include "mbedtls/entropy.h"        // Entropy for RNG
#include "mbedtls/ctr_drbg.h"      // Deterministic RNG
```

---

## 1. SSL Context Initialization

### 1.1 Initialize SSL Context

```c
void mbedtls_ssl_init(mbedtls_ssl_context *ssl);
```

**Example:**
```c
mbedtls_ssl_context ssl;
mbedtls_ssl_init(&ssl);
```

### 1.2 Initialize SSL Configuration

```c
void mbedtls_ssl_config_init(mbedtls_ssl_config *conf);
```

### 1.3 Load Default Configuration

```c
int mbedtls_ssl_config_defaults(mbedtls_ssl_config *conf,
                                int endpoint,        // MBEDTLS_SSL_IS_CLIENT or MBEDTLS_SSL_IS_SERVER
                                int transport,       // MBEDTLS_SSL_TRANSPORT_STREAM (TLS) or DATAGRAM (DTLS)
                                int preset);        // MBEDTLS_SSL_PRESET_DEFAULT or SUITEB
```

**Example - TLS Client:**
```c
mbedtls_ssl_config conf;
mbedtls_ssl_config_init(&conf);

int ret = mbedtls_ssl_config_defaults(&conf,
                                       MBEDTLS_SSL_IS_CLIENT,
                                       MBEDTLS_SSL_TRANSPORT_STREAM,
                                       MBEDTLS_SSL_PRESET_DEFAULT);
if (ret != 0) {
    // Handle error
}
```

### 1.4 Setup SSL Context

```c
int mbedtls_ssl_setup(mbedtls_ssl_context *ssl, const mbedtls_ssl_config *conf);
```

---

## 2. Network I/O Setup

### 2.1 Set Callback-Based I/O

```c
void mbedtls_ssl_set_bio(mbedtls_ssl_context *ssl,
                         void *p_bio,
                         mbedtls_ssl_send_t *f_send,
                         mbedtls_ssl_recv_t *f_recv,
                         mbedtls_ssl_recv_timeout_t *f_recv_timeout);
```

**Callback Types:**
```c
typedef int (*mbedtls_ssl_send_t)(void *ctx, const unsigned char *buf, size_t len);
typedef int (*mbedtls_ssl_recv_t)(void *ctx, unsigned char *buf, size_t len);
typedef int (*mbedtls_ssl_recv_timeout_t)(void *ctx, unsigned char *buf, size_t len, uint32_t timeout);
```

### 2.2 Using mbedtls_net_socket (BSD-like)

```c
// Initialize net context
mbedtls_net_context server_fd;
mbedtls_net_init(&server_fd);

// Connect to server (TCP)
int ret = mbedtls_net_connect(&server_fd, "hostname", "443", MBEDTLS_NET_PROTO_TCP);

// Set blocking I/O callbacks
mbedtls_ssl_set_bio(&ssl, &server_fd,
                     mbedtls_net_send,   // f_send
                     mbedtls_net_recv,   // f_recv
                     mbedtls_net_recv_timeout);  // f_recv_timeout
```

---

## 3. Certificate Verification

### 3.1 Set Hostname (SNI)

```c
void mbedtls_ssl_set_hostname(mbedtls_ssl_context *ssl, const char *hostname);
```

**Example:**
```c
mbedtls_ssl_set_hostname(&ssl, "example.com");
```

### 3.2 Set CA Certificate Chain

```c
void mbedtls_ssl_conf_ca_chain(mbedtls_ssl_config *conf,
                                mbedtls_x509_crt *ca_chain,
                                mbedtls_x509_crl *ca_crl);
```

### 3.3 Set Certificate Verification Mode

```c
void mbedtls_ssl_conf_authmode(mbedtls_ssl_config *conf, int authmode);
```

**Modes:**
- `MBEDTLS_SSL_VERIFY_NONE` - No verification (insecure)
- `MBEDTLS_SSL_VERIFY_OPTIONAL` - Verify if certificate provided, continue on failure
- `MBEDTLS_SSL_VERIFY_REQUIRED` - Require valid certificate (recommended for clients)

### 3.4 Parse Certificate

```c
int mbedtls_x509_crt_parse(mbedtls_x509_crt *chain, const unsigned char *buf, size_t buflen);
int mbedtls_x509_crt_parse_file(mbedtls_x509_crt *chain, const char *path);
```

### 3.5 Get Verification Result

```c
uint32_t mbedtls_ssl_get_verify_result(const mbedtls_ssl_context *ssl);
```

**Check Flags:**
```c
if (mbedtls_ssl_get_verify_result(&ssl) != 0) {
    // Verification failed
    uint32_t flags = mbedtls_ssl_get_verify_result(&ssl);
    if (flags & MBEDTLS_X509_BADCERT_EXPIRED) { /* expired */ }
    if (flags & MBEDTLS_X509_BADCERT_REVOKED) { /* revoked */ }
    if (flags & MBEDTLS_X509_BADCERT_NOT_TRUSTED) { /* not trusted */ }
    if (flags & MBEDTLS_X509_BADCERT_CN_MISMATCH) { /* CN mismatch */ }
}
```

---

## 4. Client Certificate Authentication

### 4.1 Set Own Certificate and Key

```c
int mbedtls_ssl_set_own_cert(mbedtls_ssl_context *ssl,
                              mbedtls_x509_crt *own_cert,
                              mbedtls_pk_context *pk_key);
```

### 4.2 Set CA Chain for Client Cert Verification (Server)

```c
void mbedtls_ssl_set_hs_ca_chain(mbedtls_ssl_context *ssl,
                                  mbedtls_x509_crt *ca_chain,
                                  mbedtls_x509_crl *ca_crl);
```

### 4.3 Complete Example - Client with Certificate

```c
// Initialize contexts
mbedtls_ssl_context ssl;
mbedtls_ssl_config conf;
mbedtls_x509_crt cacert;
mbedtls_x509_crt clicert;
mbedtls_pk_context pkey;
mbedtls_entropy_context entropy;
mbedtls_ctr_drbg_context ctr_drbg;

mbedtls_ssl_init(&ssl);
mbedtls_ssl_config_init(&conf);
mbedtls_x509_crt_init(&cacert);
mbedtls_x509_crt_init(&clicert);
mbedtls_pk_init(&pkey);
mbedtls_entropy_init(&entropy);
mbedtls_ctr_drbg_init(&ctr_drbg);

// Setup entropy and RNG
const char *pers = "ssl_client";
mbedtls_ctr_drbg_seed(&ctr_drbg, mbedtls_entropy_func, &entropy,
                       (const unsigned char *)pers, strlen(pers));

// Load CA certificate
mbedtls_x509_crt_parse_file(&cacert, "/path/to/ca_cert.pem");

// Load client certificate and key
mbedtls_x509_crt_parse_file(&clicert, "/path/to/client_cert.pem");
mbedtls_pk_parse_keyfile(&pkey, "/path/to/client_key.pem", NULL);

// Configure SSL
mbedtls_ssl_config_defaults(&conf, MBEDTLS_SSL_IS_CLIENT,
                            MBEDTLS_SSL_TRANSPORT_STREAM,
                            MBEDTLS_SSL_PRESET_DEFAULT);
mbedtls_ssl_conf_authmode(&conf, MBEDTLS_SSL_VERIFY_REQUIRED);
mbedtls_ssl_conf_ca_chain(&conf, &cacert, NULL);
mbedtls_ssl_conf_rng(&conf, mbedtls_ctr_drbg_random, &ctr_drbg);

mbedtls_ssl_setup(&ssl, &conf);
mbedtls_ssl_set_hostname(&ssl, "server.example.com");
mbedtls_ssl_set_own_cert(&ssl, &clicert, &pkey);
mbedtls_ssl_set_bio(&ssl, &server_fd,
                     mbedtls_net_send, mbedtls_net_recv, mbedtls_net_recv_timeout);
```

---

## 5. Handshake

### 5.1 Perform Handshake

```c
int mbedtls_ssl_handshake(mbedtls_ssl_context *ssl);
```

**Example - Blocking Handshake:**
```c
int ret;
while ((ret = mbedtls_ssl_handshake(&ssl)) != 0) {
    if (ret != MBEDTLS_ERR_SSL_WANT_READ && ret != MBEDTLS_ERR_SSL_WANT_WRITE) {
        printf("Handshake failed: -0x%04x\n", (unsigned int)(-ret));
        goto cleanup;
    }
}
printf("Handshake successful!\n");
```

**Example - Event-Driven (Non-blocking):**
```c
int do_handshake(mbedtls_ssl_context *ssl) {
    int ret = mbedtls_ssl_handshake(ssl);
    if (ret == 0) {
        return HANDSHAKE_DONE;
    } else if (ret == MBEDTLS_ERR_SSL_WANT_READ || ret == MBEDTLS_ERR_SSL_WANT_WRITE) {
        return HANDSHAKE_IN_PROGRESS;  // Wait for I/O ready
    } else {
        return HANDSHAKE_FAILED;      // Error
    }
}
```

---

## 6. Read/Write Data

### 6.1 Read Data

```c
int mbedtls_ssl_read(mbedtls_ssl_context *ssl, unsigned char *buf, size_t len);
```

**Return Values:**
- `> 0`: Number of bytes read
- `0`: Peer closed connection
- `MBEDTLS_ERR_SSL_WANT_READ`: Non-blocking, would block (retry)
- `MBEDTLS_ERR_SSL_WANT_WRITE`: Want write (check socket writable)
- Negative: Error code

**Example:**
```c
unsigned char buf[1024];
int ret;
while ((ret = mbedtls_ssl_read(&ssl, buf, sizeof(buf))) < 0) {
    if (ret == MBEDTLS_ERR_SSL_WANT_READ || ret == MBEDTLS_ERR_SSL_WANT_WRITE) {
        continue;  // Retry
    }
    if (ret == MBEDTLS_ERR_SSL_CONN_EOF) {
        printf("Connection closed by peer\n");
        break;
    }
    printf("Read error: -0x%04x\n", (unsigned int)(-ret));
    break;
}
if (ret > 0) {
    printf("Received %d bytes: %.*s\n", ret, ret, buf);
}
```

### 6.2 Write Data

```c
int mbedtls_ssl_write(mbedtls_ssl_context *ssl, const unsigned char *buf, size_t len);
```

**Note:** May do partial writes. Must retry with `buf + ret, len - ret` until all data written.

**Example:**
```c
const char *msg = "Hello, TLS!";
size_t len = strlen(msg);
size_t off = 0;
while (len > 0) {
    int ret = mbedtls_ssl_write(&ssl, (unsigned char *)msg + off, len);
    if (ret < 0) {
        if (ret == MBEDTLS_ERR_SSL_WANT_READ || ret == MBEDTLS_ERR_SSL_WANT_WRITE) {
            continue;  // Retry
        }
        printf("Write error: -0x%04x\n", (unsigned int)(-ret));
        break;
    }
    off += ret;
    len -= ret;
}
printf("Sent %zu bytes\n", off);
```

---

## 7. Complete TLS Client Example

```c
#include "mbedtls/net_sockets.h"
#include "mbedtls/ssl.h"
#include "mbedtls/x509_crt.h"
#include "mbedtls/pk.h"
#include "mbedtls/entropy.h"
#include "mbedtls/ctr_drbg.h"

#define SERVER_HOST "example.com"
#define SERVER_PORT "443"
#define CA_CERT_FILE "/path/to/ca_cert.pem"

int tls_client_example(void)
{
    int ret;
    mbedtls_net_context server_fd;
    mbedtls_ssl_context ssl;
    mbedtls_ssl_config conf;
    mbedtls_x509_crt cacert;
    mbedtls_entropy_context entropy;
    mbedtls_ctr_drbg_context ctr_drbg;
    unsigned char buf[1024];

    // Initialize
    mbedtls_net_init(&server_fd);
    mbedtls_ssl_init(&ssl);
    mbedtls_ssl_config_init(&conf);
    mbedtls_x509_crt_init(&cacert);
    mbedtls_entropy_init(&entropy);
    mbedtls_ctr_drbg_init(&ctr_drbg);

    // Seed RNG
    const char *pers = "ssl_client";
    ret = mbedtls_ctr_drbg_seed(&ctr_drbg, mbedtls_entropy_func, &entropy,
                                  (const unsigned char *)pers, strlen(pers));
    if (ret != 0) {
        printf("Failed to seed RNG: -0x%04x\n", (unsigned int)(-ret));
        return ret;
    }

    // Load CA certificate
    ret = mbedtls_x509_crt_parse_file(&cacert, CA_CERT_FILE);
    if (ret < 0) {
        printf("Failed to parse CA cert: -0x%04x\n", (unsigned int)(-ret));
        return ret;
    }

    // Configure SSL
    ret = mbedtls_ssl_config_defaults(&conf,
                                       MBEDTLS_SSL_IS_CLIENT,
                                       MBEDTLS_SSL_TRANSPORT_STREAM,
                                       MBEDTLS_SSL_PRESET_DEFAULT);
    if (ret != 0) {
        printf("Failed to set config defaults: -0x%04x\n", (unsigned int)(-ret));
        return ret;
    }

    mbedtls_ssl_conf_authmode(&conf, MBEDTLS_SSL_VERIFY_REQUIRED);
    mbedtls_ssl_conf_ca_chain(&conf, &cacert, NULL);
    mbedtls_ssl_conf_rng(&conf, mbedtls_ctr_drbg_random, &ctr_drbg);

    // Setup SSL context
    ret = mbedtls_ssl_setup(&ssl, &conf);
    if (ret != 0) {
        printf("Failed to setup SSL: -0x%04x\n", (unsigned int)(-ret));
        return ret;
    }

    // Set hostname (SNI)
    ret = mbedtls_ssl_set_hostname(&ssl, SERVER_HOST);
    if (ret != 0) {
        printf("Failed to set hostname: -0x%04x\n", (unsigned int)(-ret));
        return ret;
    }

    // Connect to server
    ret = mbedtls_net_connect(&server_fd, SERVER_HOST, SERVER_PORT, MBEDTLS_NET_PROTO_TCP);
    if (ret != 0) {
        printf("Failed to connect: -0x%04x\n", (unsigned int)(-ret));
        return ret;
    }

    // Set I/O callbacks
    mbedtls_ssl_set_bio(&ssl, &server_fd,
                         mbedtls_net_send,
                         mbedtls_net_recv,
                         mbedtls_net_recv_timeout);

    // Handshake
    ret = mbedtls_ssl_handshake(&ssl);
    if (ret != 0) {
        printf("Handshake failed: -0x%04x\n", (unsigned int)(-ret));
        return ret;
    }
    printf("TLS handshake successful!\n");

    // Verify peer certificate
    uint32_t flags = mbedtls_ssl_get_verify_result(&ssl);
    if (flags != 0) {
        printf("Certificate verification failed\n");
        // Continue anyway if desired
    }

    // Write HTTP request
    const char *http_req = "GET / HTTP/1.1\r\nHost: " SERVER_HOST "\r\n\r\n";
    ret = mbedtls_ssl_write(&ssl, (unsigned char *)http_req, strlen(http_req));
    if (ret < 0) {
        printf("Write failed: -0x%04x\n", (unsigned int)(-ret));
        return ret;
    }

    // Read response
    while ((ret = mbedtls_ssl_read(&ssl, buf, sizeof(buf) - 1)) > 0) {
        buf[ret] = '\0';
        printf("%s", (char *)buf);
    }
    if (ret < 0 && ret != MBEDTLS_ERR_SSL_CONN_EOF) {
        printf("Read failed: -0x%04x\n", (unsigned int)(-ret));
    }

    // Cleanup
    mbedtls_ssl_free(&ssl);
    mbedtls_ssl_config_free(&conf);
    mbedtls_net_free(&server_fd);
    mbedtls_x509_crt_free(&cacert);
    mbedtls_ctr_drbg_free(&ctr_drbg);
    mbedtls_entropy_free(&entropy);

    return 0;
}
```

---

## 8. TLS Server Example

```c
#include "mbedtls/net_sockets.h"
#include "mbedtls/ssl.h"
#include "mbedtls/x509_crt.h"
#include "mbedtls/pk.h"
#include "mbedtls/entropy.h"
#include "mbedtls/ctr_drbg.h"

#define SERVER_PORT "8443"
#define SERVER_CERT_FILE "/path/to/server_cert.pem"
#define SERVER_KEY_FILE "/path/to/server_key.pem"
#define CA_CERT_FILE "/path/to/ca_cert.pem"  // For client cert verification

int tls_server_example(void)
{
    int ret;
    mbedtls_net_context listen_fd, client_fd;
    mbedtls_ssl_context ssl;
    mbedtls_ssl_config conf;
    mbedtls_x509_crt server_cert, client_cert;
    mbedtls_pk_context pkey;
    mbedtls_entropy_context entropy;
    mbedtls_ctr_drbg_context ctr_drbg;

    // Initialize
    mbedtls_net_init(&listen_fd);
    mbedtls_net_init(&client_fd);
    mbedtls_ssl_init(&ssl);
    mbedtls_ssl_config_init(&conf);
    mbedtls_x509_crt_init(&server_cert);
    mbedtls_x509_crt_init(&client_cert);
    mbedtls_pk_init(&pkey);
    mbedtls_entropy_init(&entropy);
    mbedtls_ctr_drbg_init(&ctr_drbg);

    // Seed RNG
    const char *pers = "ssl_server";
    ret = mbedtls_ctr_drbg_seed(&ctr_drbg, mbedtls_entropy_func, &entropy,
                                  (const unsigned char *)pers, strlen(pers));

    // Load server certificate and key
    ret = mbedtls_x509_crt_parse_file(&server_cert, SERVER_CERT_FILE);
    ret = mbedtls_pk_parse_keyfile(&pkey, SERVER_KEY_FILE, NULL);

    // Configure SSL
    ret = mbedtls_ssl_config_defaults(&conf,
                                         MBEDTLS_SSL_IS_SERVER,
                                         MBEDTLS_SSL_TRANSPORT_STREAM,
                                         MBEDTLS_SSL_PRESET_DEFAULT);
    mbedtls_ssl_conf_rng(&conf, mbedtls_ctr_drbg_random, &ctr_drbg);

    // Optional: Require client certificate
    // mbedtls_ssl_conf_authmode(&conf, MBEDTLS_SSL_VERIFY_REQUIRED);
    // mbedtls_x509_crt_parse_file(&client_cert, CA_CERT_FILE);
    // mbedtls_ssl_conf_ca_chain(&conf, &client_cert, NULL);

    ret = mbedtls_ssl_setup(&ssl, &conf);
    mbedtls_ssl_set_own_cert(&ssl, &server_cert, &pkey);

    // Bind and listen
    ret = mbedtls_net_bind(&listen_fd, NULL, SERVER_PORT, MBEDTLS_NET_PROTO_TCP);
    ret = mbedtls_net_listen(&listen_fd, 1);

    while (1) {
        // Accept connection
        ret = mbedtls_net_accept(&listen_fd, &client_fd, NULL, 0, NULL);
        if (ret != 0) continue;

        // Setup client SSL
        mbedtls_ssl_setup(&ssl, &conf);
        mbedtls_ssl_set_bio(&ssl, &client_fd,
                             mbedtls_net_send, mbedtls_net_recv, mbedtls_net_recv_timeout);

        // Handshake
        ret = mbedtls_ssl_handshake(&ssl);
        if (ret != 0) {
            printf("Handshake failed: -0x%04x\n", (unsigned int)(-ret));
            goto close_client;
        }
        printf("Client connected!\n");

        // Read/Write loop here
        // ...

close_client:
        mbedtls_ssl_free(&ssl);
        mbedtls_net_free(&client_fd);
    }

    // Cleanup
    mbedtls_net_free(&listen_fd);
    mbedtls_ssl_config_free(&conf);
    mbedtls_ctr_drbg_free(&ctr_drbg);
    mbedtls_entropy_free(&entropy);

    return 0;
}
```

---

## 9. Key API Summary

| Function | Purpose |
|----------|---------|
| `mbedtls_ssl_init()` | Initialize SSL context |
| `mbedtls_ssl_config_init()` | Initialize SSL config |
| `mbedtls_ssl_config_defaults()` | Load default config |
| `mbedtls_ssl_setup()` | Setup SSL with config |
| `mbedtls_ssl_set_hostname()` | Set SNI hostname |
| `mbedtls_ssl_set_bio()` | Set I/O callbacks |
| `mbedtls_ssl_set_own_cert()` | Set client/server certificate |
| `mbedtls_ssl_conf_ca_chain()` | Set CA chain |
| `mbedtls_ssl_conf_authmode()` | Set verification mode |
| `mbedtls_ssl_handshake()` | Perform TLS handshake |
| `mbedtls_ssl_read()` | Read encrypted data |
| `mbedtls_ssl_write()` | Write encrypted data |
| `mbedtls_ssl_get_verify_result()` | Get cert verification result |
| `mbedtls_ssl_free()` | Free SSL context |
| `mbedtls_ssl_config_free()` | Free SSL config |

---

## 10. Common Error Codes

| Error Code | Meaning |
|------------|---------|
| `MBEDTLS_ERR_SSL_WANT_READ` | Non-blocking: would block on read |
| `MBEDTLS_ERR_SSL_WANT_WRITE` | Non-blocking: would block on write |
| `MBEDTLS_ERR_SSL_TIMEOUT` | Timeout |
| `MBEDTLS_ERR_SSL_HANDSHAKE_FAILURE` | Handshake failed |
| `MBEDTLS_ERR_SSL_BAD_CERTIFICATE` | Invalid certificate |
| `MBEDTLS_ERR_SSL_CERT_VERIFY_FAILED` | Certificate verification failed |
| `MBEDTLS_ERR_SSL_CONN_EOF` | Connection closed |
| `MBEDTLS_ERR_NET_CONNECT_FAILED` | TCP connection failed |

---

## 11. Memory Notes

- `mbedtls_ssl_init()` only initializes the structure - no dynamic allocation
- `mbedtls_ssl_setup()` allocates internal buffers
- Free in reverse order of allocation
- Call `mbedtls_ssl_session_reset()` to reuse context for new connection
- Use `mbedtls_ssl_free()` + `mbedtls_ssl_setup()` for fresh start
