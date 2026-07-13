# DHCP Server API Reference

> Source file: `components/network/lwip_dhcpd/dhcp_server.h`  
> Lightweight DHCPv4 server built on lwIP, assigns IP addresses to clients on the local network.

---

## Overview

BL602 includes a minimal DHCP server (`dhcpd`) based on lwIP's `dhcpd` component. It runs on a specified network interface and automatically assigns IP addresses to connecting clients.

---

## Header File

```c
#include "dhcp_server.h"
```

---

## Functions

### `dhcpd_start`

Start the DHCP server on the specified network interface.

```c
void dhcpd_start(struct netif *netif);
```

| Parameter | Type | Description |
|-----------|------|-------------|
| `netif` | `struct netif *` | Pointer to the network interface to run DHCP server on |

> The `netif` must have a valid IP address assigned before calling this function. The DHCP server will lease IPs from the configured range (typically `.100` to `.200`) on the same subnet.

---

## Usage Example

```c
#include "dhcp_server.h"
#include "lwip/netif.h"
#include "lwip/ip_addr.h"

extern struct netif sta_netif;

void dhcp_server_init(void)
{
    // Ensure the interface has a static IP first
    ip4_addr_t ipaddr = { .addr = htonl(0xC0A80101) };  // 192.168.1.1
    ip4_addr_t netmask = { .addr = htonl(0xFFFFFF00) }; // 255.255.255.0
    ip4_addr_t gw = { .addr = htonl(0xC0A80101) };      // 192.168.1.1

    netif_set_addr(&sta_netif, &ipaddr, &netmask, &gw);

    // Start DHCP server
    dhcpd_start(&sta_netif);
}
```

> **Note**: lwIP's `dhcpd` typically requires configuration via `lwipopts.h` — set `LWIP_DHCP=1` and the DHCP address pool range (e.g. `192.168.1.100-192.168.1.200`) in your build configuration.
