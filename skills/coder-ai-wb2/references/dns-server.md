# DNS Server API Reference

> Source file: `components/network/dns_server/include/dns_server.h`  
> BL602 local DNS server, supports resolving specific domain names to a local IP (used for Captive Portal, domain redirection, and similar scenarios).

---

## Overview

DNS Server is used when BL602 is in AP mode to hijack all DNS queries and return a specified IP address. Typical applications:
- Captive Portal (forced portal)
- Domain name redirection
- IoT local control (domain name fixed to device address)

---

## Header File

```c
#include "dns_server.h"
```

---

## Function API

### `dns_server_init`

Start the DNS server.

```c
void *dns_server_init(void);
```

**Return value**: DNS server handle (returns NULL on failure)

---

### `dns_server_deinit`

Stop and destroy the DNS server.

```c
void dns_server_deinit(void *server);
```

| Parameter | Description |
|------|------|
| `server` | Handle returned by `dns_server_init` |

---

## Usage Examples

### Captive Portal Scenario

```c
#include "dns_server.h"

static void *g_dns_server = NULL;

void captive_portal_start(const char *redirect_ip)
{
    // Start DNS server (resolves all domain names to redirect_ip)
    g_dns_server = dns_server_init();
    if (g_dns_server == NULL) {
        printf("DNS server init failed\r\n");
        return;
    }
    printf("DNS server started, redirecting to %s\r\n", redirect_ip);
}

void captive_portal_stop(void)
{
    if (g_dns_server) {
        dns_server_deinit(g_dns_server);
        g_dns_server = NULL;
        printf("DNS server stopped\r\n");
    }
}

// Start in app_main
void app_main(void)
{
    // Enable AP mode...
    // Start DNS redirection (resolve all domain names to AP's IP)
    captive_portal_start("192.168.4.1");
}
```

### Local IoT Control

```c
void iot_control_start(void)
{
    // Device acts as AP; after phone connects, access mydevice.local domain
    // DNS Server resolves mydevice.local to 192.168.4.1
    g_dns_server = dns_server_init();
}
```

---

## Notes

- DNS Server can only be used in AP mode
- All DNS queries outside the local network will be hijacked
- To precisely control which domain names are hijacked, SDK source code modifications are required
