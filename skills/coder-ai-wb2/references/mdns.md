# mDNS Responder API Reference

> Source file: `components/network/lwip_mdns/mdns_server.h`  
> Multicast DNS (mDNS) responder, supports local network service discovery.

---

## Overview

mDNS is used to discover services and devices on a local area network without a DNS server. Through mDNS, devices can discover each other via `hostname.local` domain names without requiring a centralized configuration server.

---

## Header Files

```c
#include "lwip/apps/mdns_opts.h"
#include "lwip/netif.h"
```

> Requires `LWIP_MDNS_RESPONDER=1` to be enabled in `lwipopts.h`.

---

## Type Definitions

### `mdns_name_result_cb_t`

Name probing result callback:

```c
typedef void (*mdns_name_result_cb_t)(struct netif *netif, u8_t result);
// result: MDNS_PROBING_CONFLICT(0) or MDNS_PROBING_SUCCESSFUL(1)
```

### `service_get_txt_fn_t`

Service TXT record callback:

```c
typedef void (*service_get_txt_fn_t)(struct mdns_service *service, void *txt_userdata);
```

---

## Function Interface

### `mdns_resp_init`

Initialize the mDNS responder.

```c
void mdns_resp_init(void);
```

---

### `mdns_resp_deinit`

Deinitialize mDNS.

```c
void mdns_resp_deinit(void);
```

---

### `mdns_resp_register_name_result_cb`

Register name conflict detection callback.

```c
void mdns_resp_register_name_result_cb(mdns_name_result_cb_t cb);
```

---

### `mdns_resp_add_netif`

Register a hostname for a network interface.

```c
err_t mdns_resp_add_netif(struct netif *netif, const char *hostname, u32_t dns_ttl);
```

| Parameter | Description |
|-----------|-------------|
| `netif` | Network interface |
| `hostname` | Hostname (e.g., `"my-device"`) |
| `dns_ttl` | DNS record TTL (seconds) |

---

### `mdns_resp_remove_netif`

Remove mDNS from an interface.

```c
err_t mdns_resp_remove_netif(struct netif *netif);
```

---

### `mdns_resp_rename_netif`

Change the hostname of an interface.

```c
err_t mdns_resp_rename_netif(struct netif *netif, const char *hostname);
```

---

### `mdns_resp_add_service`

Register an mDNS service.

```c
s8_t mdns_resp_add_service(struct netif *netif,
                           const char *name,
                           const char *service,
                           enum mdns_sd_proto proto,
                           u16_t port,
                           u32_t dns_ttl,
                           service_get_txt_fn_t txt_fn,
                           void *txt_userdata);
```

| Parameter | Description |
|-----------|-------------|
| `netif` | Network interface |
| `name` | Service instance name (e.g., `"My HTTP Server"`) |
| `service` | Service type (e.g., `"_http"`) |
| `proto` | Protocol: `MDNS_SD_PROTO_TCP` or `MDNS_SD_PROTO_UDP` |
| `port` | Service port |
| `dns_ttl` | TTL |
| `txt_fn` | TXT record callback (can be NULL) |
| `txt_userdata` | User data passed to callback |

**Return value**: >=0=service slot number (for deletion/modification), <0=failure

---

### `mdns_resp_del_service`

Delete a registered service.

```c
err_t mdns_resp_del_service(struct netif *netif, s8_t slot);
```

---

### `mdns_resp_rename_service`

Change the service instance name.

```c
err_t mdns_resp_rename_service(struct netif *netif, s8_t slot, const char *name);
```

---

### `mdns_resp_add_service_txtitem`

Add a TXT record entry to a service.

```c
err_t mdns_resp_add_service_txtitem(struct mdns_service *service,
                                    const char *txt, u8_t txt_len);
```

---

### `mdns_responder_start`

Start the mDNS responder.

```c
int mdns_responder_start(struct netif *netif);
```

---

### `mdns_responder_stop`

Stop the mDNS responder.

```c
int mdns_responder_stop(struct netif *netif);
```

---

### `mdns_resp_restart`

Restart the mDNS responder (triggers re-probing).

```c
void mdns_resp_restart(struct netif *netif);
```

---

### `mdns_resp_announce`

Broadcast proactively (notify the network of setting changes).

```c
void mdns_resp_announce(struct netif *netif);
```

---

## Usage Examples

### Basic HTTP Service Registration

```c
#include "lwip/apps/mdns_opts.h"
#include "lwip/netif.h"

static void http_txt_callback(struct mdns_service *service, void *txt_userdata)
{
    (void)service; (void)txt_userdata;
    mdns_resp_add_service_txtitem(service, "path=/", 7);
    mdns_resp_add_service_txtitem(service, "version=1.0", 12);
}

void mdns_http_example(struct netif *netif)
{
    mdns_resp_init();

    // Register device name
    mdns_resp_add_netif(netif, "my-wb2", 120);

    // Register HTTP service
    mdns_resp_add_service(netif,
                          "My HTTP Server",
                          "_http",
                          MDNS_SD_PROTO_TCP,
                          80,
                          120,
                          http_txt_callback,
                          NULL);

    mdns_responder_start(netif);
}
```

### Starting After Wi-Fi Connection

```c
void wifi_connected_callback(struct netif *netif)
{
    if (!netif_is_up(netif)) return;

    mdns_resp_add_netif(netif, "ai-wb2", 120);
    mdns_resp_add_service(netif, "WB2 Device", "_device-info",
                          MDNS_SD_PROTO_TCP, 8080, 120, NULL, NULL);
    mdns_responder_start(netif);
}
```
