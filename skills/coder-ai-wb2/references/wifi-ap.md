# Wi-Fi API Reference (AP Mode)

> Source file: `components/network/wifi_manager/bl60x_wifi_driver/include/wifi_mgmr_ext.h`

---

## Enable and Start

### `wifi_mgmr_ap_enable`

Enables AP mode and gets the interface handle.

```c
wifi_interface_t wifi_mgmr_ap_enable(void);
```

**Return value**: Wi-Fi interface handle

---

### `wifi_mgmr_ap_stop`

Stops the AP.

```c
int wifi_mgmr_ap_stop(wifi_interface_t *interface);
```

---

### `wifi_mgmr_ap_start`

Starts the AP hotspot.

```c
int wifi_mgmr_ap_start(wifi_interface_t *interface,
                       char *ssid,
                       int hidden_ssid,
                       char *passwd,
                       int channel);
```

| Parameter | Description |
|-----------|-------------|
| `interface` | Handle returned by `wifi_mgmr_ap_enable` |
| `ssid` | Hotspot name |
| `hidden_ssid` | `1` = hidden SSID, `0` = broadcast SSID |
| `passwd` | Password (NULL for open network) |
| `channel` | Channel (1~13) |

---

### `wifi_mgmr_ap_start_adv`

Starts the AP (advanced version, supports DHCP configuration).

```c
int wifi_mgmr_ap_start_adv(wifi_interface_t *interface,
                           char *ssid,
                           int hidden_ssid,
                           char *passwd,
                           int channel,
                           uint8_t use_dhcp);
```

---

### `wifi_mgmr_ap_start_atcmd`

Starts the AP via AT command.

```c
int wifi_mgmr_ap_start_atcmd(wifi_interface_t *interface,
                             char *ssid,
                             int hidden_ssid,
                             char *passwd,
                             int channel,
                             int max_sta_supported);
```

---

## AP IP Configuration

### `wifi_mgmr_ap_ip_set`

Sets the AP IP address.

```c
int wifi_mgmr_ap_ip_set(uint32_t ip, uint32_t gw, uint32_t mask);
```

---

### `wifi_mgmr_ap_ip_get`

Gets the AP IP address.

```c
int wifi_mgmr_ap_ip_get(uint32_t *ip, uint32_t *gw, uint32_t *mask);
```

---

### `wifi_mgmr_ap_mac_get`

Gets the AP MAC address.

```c
int wifi_mgmr_ap_mac_get(uint8_t mac[6]);
```

---

## DHCP Server

### `wifi_mgmr_ap_dhcp_enable`

Enables the built-in AP DHCP server.

```c
int wifi_mgmr_ap_dhcp_enable(void);
```

---

### `wifi_mgmr_ap_dhcp_disable`

Disables the built-in AP DHCP server.

```c
int wifi_mgmr_ap_dhcp_disable(void);
```

---

### `wifi_mgmr_ap_dhcp_range_set`

Configures the DHCP address pool range.

```c
int wifi_mgmr_ap_dhcp_range_set(uint32_t ip, uint32_t mask, int start, int end);
```

---

### `wifi_mgmr_ap_dhcp_range_get`

Gets the DHCP address pool configuration.

```c
int wifi_mgmr_ap_dhcp_range_get(uint32_t *ip, uint32_t *mask, int *start, int *end);
```

---

## Connected Station Management

### `wifi_mgmr_ap_sta_cnt_get`

Gets the number of connected stations.

```c
int wifi_mgmr_ap_sta_cnt_get(uint8_t *sta_cnt);
```

---

### `wifi_mgmr_ap_sta_info_get`

Gets information about a specified station.

```c
int wifi_mgmr_ap_sta_info_get(struct wifi_sta_basic_info *sta_info, uint8_t idx);
```

---

### `wifi_mgmr_ap_sta_delete`

Disconnects a specified station.

```c
int wifi_mgmr_ap_sta_delete(uint8_t sta_idx);
```

---

### `wifi_mgmr_ap_set_gateway`

Sets the AP upstream gateway.

```c
int wifi_mgmr_ap_set_gateway(char *gateway);
```

---

## Channel Switching

### `wifi_mgmr_ap_chan_switch`

Switches the AP channel.

```c
int wifi_mgmr_ap_chan_switch(wifi_interface_t *interface, int channel, uint8_t cs_count);
```

---

## Other Configuration

### `wifi_mgmr_conf_max_sta`

Sets the maximum number of connected stations.

```c
int wifi_mgmr_conf_max_sta(uint8_t max_sta_supported);
```

---

### `wifi_mgmr_beacon_interval_set`

Sets the Beacon interval.

```c
int wifi_mgmr_beacon_interval_set(uint16_t beacon_int);
```

---

## Usage Example

```c
#include "wifi_mgmr_ext.h"

// Enable AP mode
wifi_interface_t ap_if = wifi_mgmr_ap_enable();

// Set AP IP (must set IP before starting DHCP)
wifi_mgmr_ap_ip_set(0xC0A80101, 0xC0A80101, 0xFFFFFF00); // 192.168.1.1

// Enable DHCP
wifi_mgmr_ap_dhcp_enable();
wifi_mgmr_ap_dhcp_range_set(0xC0A80101, 0xFFFFFF00, 100, 200);

// Start hotspot: SSID="BL602_AP", channel 6, password "12345678"
int ret = wifi_mgmr_ap_start(ap_if, "BL602_AP", 0, "12345678", 6);
if (ret == 0) {
    printf("AP started on channel 6\r\n");
}

// Check connected stations
uint8_t sta_cnt = 0;
wifi_mgmr_ap_sta_cnt_get(&sta_cnt);
printf("Connected stations: %d\r\n", sta_cnt);

// Get station info
struct wifi_sta_basic_info sta_info;
for (int i = 0; i < sta_cnt; i++) {
    wifi_mgmr_ap_sta_info_get(&sta_info, i);
    printf("STA[%d] MAC: %02X:%02X:... RSSI: %d\r\n",
           i, sta_info.sta_mac[0], sta_info.sta_mac[1], sta_info.rssi);
}

// Stop AP
wifi_mgmr_ap_stop(&ap_if);
```
