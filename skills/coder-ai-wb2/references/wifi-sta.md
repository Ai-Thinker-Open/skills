# Wi-Fi API Reference (STA Mode)

> Source file: `components/network/wifi_manager/bl60x_wifi_driver/include/wifi_mgmr_ext.h`  
> Another file: `components/network/wifi_manager/bl60x_wifi_driver/wifi_mgmr_api.h`

> The Wi-Fi module supports two modes: Station (STA) and Access Point (AP). In STA mode, the module acts as a client to connect to a router; in AP mode, the module acts as a hotspot for other devices to connect.

---

## Initialization and Enable

### `wifi_mgmr_drv_init`

Driver initialization (called once at system startup).

```c
int wifi_mgmr_drv_init(wifi_conf_t *conf);
```

| Parameter | Description |
|-----------|-------------|
| `conf` | Wi-Fi country code and channel configuration, see `wifi_conf_t` |

**Return value**: `0` on success

---

### `wifi_mgmr_init`

Wi-Fi manager initialization.

```c
int wifi_mgmr_init(void);
```

---

### `wifi_mgmr_sta_enable`

Enables STA mode and gets the Wi-Fi interface handle.

```c
wifi_interface_t wifi_mgmr_sta_enable(void);
```

**Return value**: Wi-Fi interface handle (`wifi_interface_t`), used for subsequent connection operations

---

### `wifi_mgmr_sta_disable`

Disables STA mode.

```c
int wifi_mgmr_sta_disable(wifi_interface_t *interface);
```

---

## Connection Operations

### `wifi_mgmr_sta_connect`

Connects to a Wi-Fi hotspot (basic version).

```c
int wifi_mgmr_sta_connect(wifi_interface_t *wifi_interface,
                          char *ssid,
                          char *psk,
                          char *pmk,
                          uint8_t *mac,
                          uint8_t band,
                          uint8_t chan_id);
```

| Parameter | Description |
|-----------|-------------|
| `wifi_interface` | Handle returned by `wifi_mgmr_sta_enable` |
| `ssid` | Hotspot name |
| `psk` | Password (can be NULL for open network) |
| `pmk` | PSK key (can be NULL, auto-calculated) |
| `mac` | Target AP MAC address (can be NULL) |
| `band` | Frequency band (0 = 2.4G) |
| `chan_id` | Channel number (0 = auto) |

**Return value**: `0` on success

---

### `wifi_mgmr_sta_connect_ext`

Connects to a hotspot (extended version, supports advanced parameters).

```c
int wifi_mgmr_sta_connect_ext(wifi_interface_t *wifi_interface,
                              char *ssid,
                              char *passphr,
                              const ap_connect_adv_t *conn_adv_param);
```

---

### `wifi_mgmr_sta_disconnect`

Disconnects from Wi-Fi.

```c
int wifi_mgmr_sta_disconnect(void);
```

---

## Auto Reconnect

### `wifi_mgmr_sta_autoconnect_enable`

Enables auto reconnect.

```c
int wifi_mgmr_sta_autoconnect_enable(void);
```

---

### `wifi_mgmr_sta_autoconnect_disable`

Disables auto reconnect.

```c
int wifi_mgmr_sta_autoconnect_disable(void);
```

---

### `wifi_mgmr_sta_autoconnect_set`

Configures auto reconnect interval and retry count.

```c
int wifi_mgmr_sta_autoconnect_set(int interval_second, int repeat_count);
```

---

## IP Address

### `wifi_mgmr_sta_ip_set`

Sets the STA IP address (manual mode).

```c
int wifi_mgmr_sta_ip_set(uint32_t ip, uint32_t mask, uint32_t gw,
                         uint32_t dns1, uint32_t dns2);
```

---

### `wifi_mgmr_sta_ip_get`

Gets the STA current IP address.

```c
int wifi_mgmr_sta_ip_get(uint32_t *ip, uint32_t *gw, uint32_t *mask);
```

---

### `wifi_mgmr_sta_ip_unset`

Clears the STA IP (restores DHCP).

```c
int wifi_mgmr_sta_ip_unset(void);
```

---

### `wifi_mgmr_sta_netif_get`

Gets the STA netif interface (for LwIP stack).

```c
struct netif *wifi_mgmr_sta_netif_get(void);
```

---

## Status and Information

### `wifi_mgmr_state_get`

Gets the Wi-Fi connection state.

```c
int wifi_mgmr_state_get(int *state);
```

> State enum: `WIFI_STATE_IDLE`, `WIFI_STATE_CONNECTING`, `WIFI_STATE_CONNECTED_IP_GOT`, `WIFI_STATE_DISCONNECT`, etc.

---

### `wifi_mgmr_rssi_get`

Gets the current signal strength.

```c
int wifi_mgmr_rssi_get(int *rssi);
```

> Return value: Negative dBm value, e.g., `-65` means -65dBm

---

### `wifi_mgmr_channel_get`

Gets the current channel.

```c
int wifi_mgmr_channel_get(int *channel);
```

---

### `wifi_mgmr_sta_mac_get`

Gets the STA MAC address.

```c
int wifi_mgmr_sta_mac_get(uint8_t mac[6]);
```

---

### `wifi_mgmr_set_country_code`

Sets the country code (affects available channels).

```c
int wifi_mgmr_set_country_code(char *country_code);
```

> Example: `wifi_mgmr_set_country_code("CN")`

---

### `wifi_mgmr_get_country_code`

Gets the current country code.

```c
int wifi_mgmr_get_country_code(char *country_code);
```

---

## Scanning

### `wifi_mgmr_scan`

Scans for available hotspots.

```c
int wifi_mgmr_scan(void *data, scan_complete_cb_t cb);
```

| Parameter | Description |
|-----------|-------------|
| `data` | User private data, passed to the callback |
| `cb` | Scan complete callback `scan_complete_cb_t` |

---

### `wifi_mgmr_scan_adv`

Advanced scan (specify channel, SSID, etc.).

```c
int wifi_mgmr_scan_adv(void *data,
                       scan_complete_cb_t cb,
                       uint16_t *channels,
                       uint16_t channel_num,
                       const uint8_t bssid[6],
                       const char *ssid,
                       uint8_t scan_mode,
                       uint32_t duration_scan);
```

---

### `wifi_mgmr_all_ap_scan`

Gets all scan results.

```c
int wifi_mgmr_all_ap_scan(wifi_mgmr_ap_item_t **ap_ary, uint32_t *num);
```

---

### `wifi_mgmr_cli_scanlist`

Prints the scan list to the log.

```c
int wifi_mgmr_cli_scanlist(void);
```

---

## Power Management

### `wifi_mgmr_sta_ps_enter`

Enters low power mode.

```c
int wifi_mgmr_sta_ps_enter(uint32_t ps_level);
```

> `ps_level`: `PS_MODE_OFF` (off), `PS_MODE_ON` (normal), `PS_MODE_ON_DYN` (dynamic)

---

### `wifi_mgmr_sta_ps_exit`

Exits low power mode.

```c
int wifi_mgmr_sta_ps_exit(void);
```

---

### `wifi_mgmr_set_wifi_active_time`

Sets the active time.

```c
int wifi_mgmr_set_wifi_active_time(uint32_t ms);
```

---

### `wifi_mgmr_set_listen_interval`

Sets the listen interval.

```c
int wifi_mgmr_set_listen_interval(uint16_t itv);
```

---

## Usage Example

```c
#include "wifi_mgmr_ext.h"

// Wi-Fi initialization
wifi_conf_t conf = {
    .country_code = "CN",
    .channel_nums = 0,
};
wifi_mgmr_drv_init(&conf);
wifi_mgmr_init();

// Enable STA mode
wifi_interface_t wifi_if = wifi_mgmr_sta_enable();

// Connect to hotspot (password NULL means open network)
int ret = wifi_mgmr_sta_connect(wifi_if, "MySSID", "password", NULL, NULL, 0, 0);
if (ret == 0) {
    printf("Connecting...\r\n");
}

// Get connection state
int state;
wifi_mgmr_state_get(&state);
printf("Wi-Fi state: %d\r\n", state);

// Get signal strength
int rssi;
wifi_mgmr_rssi_get(&rssi);
printf("RSSI: %d dBm\r\n", rssi);

// Disconnect
wifi_mgmr_sta_disconnect();

// Disable STA
wifi_mgmr_sta_disable(&wifi_if);
```
