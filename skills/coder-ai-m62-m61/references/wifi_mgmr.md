# WiFi Manager (wifi_mgmr) API Reference

WiFi Manager (wifi_mgmr) is the high-level API for WiFi operations on BL616/BL618 chips. It provides Station (STA) and Access Point (AP) mode support with WPA/WPA2/WPA3 authentication.

## Header File

```c
#include "wifi_mgmr.h"
```

---

## Initialization

### `wifi_mgmr_init()`

```c
void wifi_mgmr_init(void);
```

Initialize the WiFi manager and register event handlers. This must be called before any other WiFi operations.

---

## STA Connection

### `wifi_mgmr_sta_connect()`

```c
int wifi_mgmr_sta_connect(const wifi_mgmr_sta_connect_params_t *conn_param);
```

Connect to a WiFi access point.

**Parameters:**
- `conn_param` - Connection parameters structure

**Returns:** `0` on success, negative error code on failure

**Connection Parameters Structure:**
```c
typedef struct wifi_mgmr_sta_connect_params {
    char ssid[MGMR_SSID_LEN + 1];      // SSID (max 32 chars)
    char key[MGMR_KEY_LEN + 1];        // Password (max 64 chars)
    char bssid_str[MGMR_BSSID_LEN + 1]; // BSSID (e.g., "AA:BB:CC:DD:EE:FF")
    char akm_str[MGMR_AKM_LEN + 1];     // Authentication mode
    uint16_t freq1;                     // Target frequency (MHz)
    uint16_t freq2;                     // Secondary frequency
    uint8_t pmf_cfg;                    // PMF configuration (0-2)
    uint8_t use_dhcp;                   // Use DHCP (1=yes, 0=no)
    uint16_t listen_interval;           // Beacon listen interval (1-100)
    uint8_t scan_mode;                  // Scan mode (0=all channels, 1=quick)
    uint8_t quick_connect;              // Quick connect mode
    int timeout_ms;                     // Connection timeout (ms)
    int wpa_flags;                      // WPA flags
    uint16_t duration;                  // Scan duration (TUs)
    uint16_t probe_cnt;                 // Probe request count
    uint8_t auth_timeout;               // Auth timeout (sec)
    uint8_t eapol_1_timeout;            // EAPOL 1 timeout (sec)
    uint8_t eapol_rem_timeout;          // EAPOL remaining timeout (sec)
} wifi_mgmr_sta_connect_params_t;
```

### `wifi_mgmr_sta_disconnect()`

```c
int wifi_mgmr_sta_disconnect(void);
```

Disconnect from the current WiFi access point.

**Returns:** `0` on success, negative error code on failure

---

## STA Scan Operations

### `wifi_mgmr_sta_scan()`

```c
int wifi_mgmr_sta_scan(const wifi_mgmr_scan_params_t *config);
```

Start a WiFi scan with specified parameters.

**Parameters:**
- `config` - Scan configuration

**Scan Parameters Structure:**
```c
typedef struct wifi_mgmr_scan_params {
    uint8_t ssid_length;
    uint8_t ssid_array[MGMR_SSID_LEN];  // SSID to scan for
    uint8_t bssid[6];                    // Specific BSSID (optional)
    uint8_t bssid_set_flag;              // BSSID filter enable
    uint8_t probe_cnt;                    // Probe request count
    int channels_cnt;                    // Number of channels
    uint8_t channels[MAX_FIXED_CHANNELS_LIMIT]; // Channel list
    uint32_t duration;                   // Scan duration
    bool passive;                        // 0=active scan, 1=passive scan
} wifi_mgmr_scan_params_t;
```

### `wifi_mgmr_sta_scanlist_nums_get()`

```c
uint32_t wifi_mgmr_sta_scanlist_nums_get(void);
```

Get the number of scan results in the scan list.

**Returns:** Number of scan results

### `wifi_mgmr_sta_scanlist_dump()`

```c
uint32_t wifi_mgmr_sta_scanlist_dump(void *results, uint32_t resultNums);
```

Copy scan results to a buffer.

**Parameters:**
- `results` - Buffer to store scan results
- `resultNums` - Maximum number of results to copy

**Returns:** Number of results copied

### `wifi_mgmr_sta_scanlist_free()`

```c
int wifi_mgmr_sta_scanlist_free(void);
```

Free the scan results memory.

**Returns:** `0` on success

### `wifi_mgmr_scan_ap_all()`

```c
int wifi_mgmr_scan_ap_all(void *env, void *arg, scan_item_cb_t cb);
```

Iterate through all scan results with a callback function.

**Parameters:**
- `env` - Environment pointer passed to callback
- `arg` - Argument pointer passed to callback
- `cb` - Callback function of type `scan_item_cb_t`

**Callback Type:**
```c
typedef void (*scan_item_cb_t)(void *env, void *arg, wifi_mgmr_scan_item_t *item);
```

**Scan Item Structure:**
```c
typedef struct wifi_mgmr_scan_item {
    uint32_t mode;               // WiFi mode
    uint32_t timestamp_lastseen; // Last seen timestamp
    int ssid_len;                // SSID length
    uint8_t channel;             // Channel number
    int8_t rssi;                 // RSSI (signal strength in dBm)
    char ssid[32];                // SSID string
    uint8_t bssid[6];            // BSSID (MAC address)
    int8_t ppm_abs;              // Absolute power margin
    int8_t ppm_rel;              // Relative power margin
    uint8_t auth;                // Authentication type
    uint8_t cipher;              // Cipher type
    uint8_t is_used;             // Entry in use
    uint8_t wps;                  // WPS supported
    uint8_t best_antenna;        // Best antenna index
} wifi_mgmr_scan_item_t;
```

---

## Signal Strength (RSSI)

### `wifi_mgmr_sta_rssi_get()`

```c
int wifi_mgmr_sta_rssi_get(int *rssi);
```

Get the current RSSI (Received Signal Strength Indicator) value.

**Parameters:**
- `rssi` - Pointer to store RSSI value (in dBm)

**Returns:** `0` on success, negative error code on failure

**Typical RSSI Values:**
| RSSI (dBm) | Signal Quality |
|------------|----------------|
| -30 to -50 | Excellent |
| -50 to -60 | Good |
| -60 to -70 | Fair |
| -70 to -80 | Weak |
| < -80 | Very Weak |

---

## Country Code

### `wifi_mgmr_set_country_code()`

```c
int wifi_mgmr_set_country_code(char *country_code);
```

Set the regulatory country code.

**Parameters:**
- `country_code` - 2-character country code (e.g., "CN", "US", "EU", "JP")

**Returns:** `0` on success, negative error code on failure

### `wifi_mgmr_get_country_code()`

```c
int wifi_mgmr_get_country_code(char *country_code);
```

Get the current regulatory country code.

**Parameters:**
- `country_code` - Buffer to store country code (must be at least 3 bytes)

**Returns:** `0` on success, negative error code on failure

### `wifi_mgmr_get_channel_nums()`

```c
int wifi_mgmr_get_channel_nums(const char *country_code, uint8_t *c24G_cnt, uint8_t *c5G_cnt);
```

Get the number of available channels for a country code.

**Parameters:**
- `country_code` - 2-character country code
- `c24G_cnt` - Pointer to store 2.4GHz channel count
- `c5G_cnt` - Pointer to store 5GHz channel count

**Returns:** `0` on success, negative error code on failure

### `wifi_mgmr_get_channel_list()`

```c
int wifi_mgmr_get_channel_list(const char *country_code, uint8_t **c24G_list, uint8_t **c5G_list);
```

Get the list of available channels for a country code.

**Parameters:**
- `country_code` - 2-character country code
- `c24G_list` - Pointer to store 2.4GHz channel list
- `c5G_list` - Pointer to store 5GHz channel list

**Returns:** `0` on success, negative error code on failure

---

## Auto-Reconnect

### `wifi_mgmr_sta_autoconnect_enable()`

```c
int wifi_mgmr_sta_autoconnect_enable(void);
```

Enable automatic reconnection when WiFi is disconnected.

**Returns:** `0` on success, negative error code on failure

### `wifi_mgmr_sta_autoconnect_disable()`

```c
int wifi_mgmr_sta_autoconnect_disable(void);
```

Disable automatic reconnection.

**Returns:** `0` on success, negative error code on failure

---

## AP Mode

### `wifi_mgmr_ap_start()`

```c
int wifi_mgmr_ap_start(const wifi_mgmr_ap_params_t *config);
```

Start an access point (AP).

**Parameters:**
- `config` - AP configuration parameters

**Returns:** `0` on success, `-1` on failure

**AP Parameters Structure:**
```c
typedef struct wifi_mgmr_ap_params {
    char *ssid;              // SSID (required)
    char *key;               // Password (optional, default "12345678")
    char *akm;               // Auth mode (OPEN/WPA/WPA2, default WPA2)
    uint8_t channel;         // Channel (default 6)
    uint8_t type;            // Channel type
    bool use_ipcfg;          // Use IP configuration
    bool use_dhcpd;          // Use DHCP server
    int start;               // DHCP pool start IP
    int limit;               // DHCP pool size
    uint32_t ap_ipaddr;      // AP IP address
    uint32_t ap_mask;        // Subnet mask
    uint32_t ap_max_inactivity; // Max STA inactivity
    bool hidden_ssid;        // Hidden SSID
    bool isolation;          // STA isolation
    int bcn_interval;        // Beacon interval (TU)
    char *ap_vendor_elements; // Vendor-specific IEs
    uint8_t bcn_mode;        // Beacon mode (0=auto, 1=no beacons, 2=always on)
    int bcn_timer;           // Beacon timer (seconds)
    bool disable_wmm;        // Disable WMM
} wifi_mgmr_ap_params_t;
```

### `wifi_mgmr_ap_stop()`

```c
int wifi_mgmr_ap_stop(void);
```

Stop the access point.

**Returns:** `0` on success, `-1` on failure

### `wifi_mgmr_ap_state_get()`

```c
int wifi_mgmr_ap_state_get(void);
```

Get AP state.

**Returns:** AP state (not implemented, returns -1)

### `wifi_mgmr_ap_mac_get()`

```c
int wifi_mgmr_ap_mac_get(uint8_t mac[6]);
```

Get AP MAC address.

**Parameters:**
- `mac` - Buffer to store MAC address

**Returns:** `0` on success, `-1` on failure

---

## STA Status and Information

### `wifi_mgmr_sta_state_get()`

```c
int wifi_mgmr_sta_state_get(void);
```

Get STA connection state.

**Returns:** `1` if connected, `0` if disconnected

### `wifi_mgmr_sta_get_bssid()`

```c
int wifi_mgmr_sta_get_bssid(uint8_t bssid[6]);
```

Get the BSSID (MAC address) of the connected AP.

**Parameters:**
- `bssid` - Buffer to store BSSID (6 bytes)

**Returns:** `0` on success, negative error code on failure

### `wifi_mgmr_sta_mac_get()`

```c
int wifi_mgmr_sta_mac_get(uint8_t mac[6]);
```

Get STA MAC address.

**Parameters:**
- `mac` - Buffer to store MAC address (6 bytes)

**Returns:** `0` on success, negative error code on failure

### `wifi_mgmr_sta_channel_get()`

```c
int wifi_mgmr_sta_channel_get(uint8_t *channel);
```

Get the current WiFi channel.

**Parameters:**
- `channel` - Pointer to store channel number

**Returns:** `0` on success, negative error code on failure

### `wifi_mgmr_sta_aid_get()`

```c
int wifi_mgmr_sta_aid_get(void);
```

Get the Association ID allocated by the AP.

**Returns:** AID value

### `wifi_mgmr_sta_connect_ind_stat_get()`

```c
int wifi_mgmr_sta_connect_ind_stat_get(wifi_mgmr_connect_ind_stat_info_t *wifi_mgmr_ind_stat);
```

Get detailed connection status and parameters.

**Parameters:**
- `wifi_mgmr_ind_stat` - Pointer to connection status structure

**Connection Status Structure:**
```c
typedef struct wifi_mgmr_connect_ind_stat_info {
    uint16_t status_code;    // Status code
    uint16_t reason_code;    // Reason code
    char ssid[MGMR_SSID_LEN + 1];
    char passphr[MGMR_KEY_LEN + 1];
    uint8_t bssid[6];        // BSSID
    uint8_t type_ind;
    uint8_t chan_band;       // Channel band
    uint8_t channel;         // Channel number
    uint8_t security;        // Security type
    uint16_t aid;            // Association ID
    uint8_t vif_idx;         // VIF index
    uint8_t ap_idx;          // AP index
    uint8_t ch_idx;          // Channel index
    bool qos;                // QoS supported
} wifi_mgmr_connect_ind_stat_info_t;
```

### `wifi_mgmr_sta_info_status_code_get()`

```c
uint16_t wifi_mgmr_sta_info_status_code_get(void);
```

Get WiFi connection status code.

**Returns:** Status code

### `wifi_mgmr_sta_info_reason_code_get()`

```c
uint16_t wifi_mgmr_sta_info_reason_code_get(void);
```

Get WiFi disconnection reason code.

**Returns:** Reason code

---

## Power Saving

### `wifi_mgmr_sta_ps_enter()`

```c
void wifi_mgmr_sta_ps_enter(void);
```

Enter power saving mode for STA. Requires prior WiFi connection.

### `wifi_mgmr_sta_ps_exit()`

```c
void wifi_mgmr_sta_ps_exit(void);
```

Exit power saving mode for STA.

---

## IP Configuration

### `wifi_mgmr_sta_ip_set()`

```c
int wifi_mgmr_sta_ip_set(uint32_t ip, uint32_t mask, uint32_t gw, uint32_t dns);
```

Set static IP configuration.

**Parameters:**
- `ip` - IP address
- `mask` - Subnet mask
- `gw` - Gateway address
- `dns` - DNS server address

**Returns:** `-1` (not implemented)

### `wifi_mgmr_sta_ip_get()`

```c
int wifi_mgmr_sta_ip_get(uint32_t *addr, uint32_t *mask, uint32_t *gw, uint32_t *dns);
```

Get current IP configuration.

**Parameters:**
- `addr` - Pointer to store IP address
- `mask` - Pointer to store subnet mask
- `gw` - Pointer to store gateway
- `dns` - Pointer to store DNS server

**Returns:** `0` on success, negative error code on failure

---

## Utility Functions

### `wifi_mgmr_mode_to_str()`

```c
char *wifi_mgmr_mode_to_str(uint32_t mode);
```

Convert WiFi mode to string (e.g., "BGN", "BGNAX").

### `wifi_mgmr_auth_to_str()`

```c
char *wifi_mgmr_auth_to_str(uint8_t auth);
```

Convert authentication type to string (e.g., "WPA2-PSK", "WPA3-SAE").

### `wifi_mgmr_cipher_to_str()`

```c
char *wifi_mgmr_cipher_to_str(uint8_t cipher);
```

Convert cipher type to string (e.g., "AES", "TKIP/AES").

### `wifi_mgmr_mac_str_to_addr()`

```c
int wifi_mgmr_mac_str_to_addr(const char *str, uint8_t addr[]);
```

Convert MAC address string to byte array.

**Parameters:**
- `str` - MAC address string (e.g., "AA:BB:CC:DD:EE:FF")
- `addr` - Buffer to store MAC address (6 bytes)

**Returns:** `0` on success, negative error code on failure

---

## Event Codes

WiFi events are posted via the async event system using `EV_WIFI`:

```c
#define EV_WIFI ((uintptr_t)wifi_mgmr_init)
```

**Event Codes:**
| Code | Event |
|------|-------|
| `CODE_WIFI_ON_INIT_DONE` | Initialization complete |
| `CODE_WIFI_ON_MGMR_DONE` | Manager ready |
| `CODE_WIFI_CMD_RECONNECT` | Reconnect command |
| `CODE_WIFI_ON_CONNECTED` | Connected to AP |
| `CODE_WIFI_ON_DISCONNECT` | Disconnected from AP |
| `CODE_WIFI_ON_PRE_GOT_IP` | About to get IP |
| `CODE_WIFI_ON_GOT_IP` | IP address obtained |
| `CODE_WIFI_ON_CONNECTING` | Connection in progress |
| `CODE_WIFI_ON_SCAN_DONE` | Scan completed |
| `CODE_WIFI_ON_AP_STARTED` | AP started |
| `CODE_WIFI_ON_AP_STOPPED` | AP stopped |
| `CODE_WIFI_ON_GOT_IP6` | IPv6 address obtained |

---

## Complete Working Code Examples

### STA Mode - Connect and Scan

```c
#include "wifi_mgmr.h"
#include "event_mgmr.h"

// Event handler for WiFi events
static void wifi_event_cb(uint32_t code, uint32_t value)
{
    switch (code) {
        case CODE_WIFI_ON_INIT_DONE:
            printf("WiFi initialized\r\n");
            break;
        case CODE_WIFI_ON_CONNECTED:
            printf("Connected to AP\r\n");
            break;
        case CODE_WIFI_ON_GOT_IP:
            printf("IP address obtained\r\n");
            break;
        case CODE_WIFI_ON_DISCONNECT:
            printf("Disconnected\r\n");
            break;
        case CODE_WIFI_ON_SCAN_DONE:
            printf("Scan completed\r\n");
            // Process scan results here
            break;
    }
}

void wifi_sta_example(void)
{
    int ret;
    int rssi;
    uint8_t channel;
    uint8_t bssid[6];
    
    // Initialize WiFi manager
    wifi_mgmr_init();
    
    // Set country code
    wifi_mgmr_set_country_code("CN");
    
    // Scan for networks
    wifi_mgmr_scan_params_t scan_params = {0};
    ret = wifi_mgmr_sta_scan(&scan_params);
    if (ret == 0) {
        // Wait for scan to complete (event CODE_WIFI_ON_SCAN_DONE)
        
        // Get number of results
        uint32_t num_results = wifi_mgmr_sta_scanlist_nums_get();
        printf("Found %lu networks\r\n", num_results);
        
        // Iterate through results
        wifi_mgmr_scan_ap_all(NULL, NULL, [](void *env, void *arg, wifi_mgmr_scan_item_t *item) {
            printf("SSID: %s, RSSI: %d dBm, Channel: %d\r\n", 
                   item->ssid, item->rssi, item->channel);
        });
        
        // Free scan list
        wifi_mgmr_sta_scanlist_free();
    }
    
    // Connect to WiFi
    wifi_mgmr_sta_connect_params_t conn_params = {0};
    strncpy(conn_params.ssid, "MyNetwork", 32);
    strncpy(conn_params.key, "password123", 64);
    conn_params.use_dhcp = 1;
    
    ret = wifi_mgmr_sta_connect(&conn_params);
    if (ret == 0) {
        printf("Connection initiated\r\n");
    }
    
    // After connection (in event handler):
    // Get connection info
    wifi_mgmr_sta_get_bssid(bssid);
    printf("Connected to BSSID: %02X:%02X:%02X:%02X:%02X:%02X\r\n",
           bssid[0], bssid[1], bssid[2], bssid[3], bssid[4], bssid[5]);
    
    wifi_mgmr_sta_rssi_get(&rssi);
    printf("Signal strength: %d dBm\r\n", rssi);
    
    wifi_mgmr_sta_channel_get(&channel);
    printf("Channel: %d\r\n", channel);
    
    // Enable auto-reconnect
    wifi_mgmr_sta_autoconnect_enable();
    
    // When done, disconnect
    // wifi_mgmr_sta_disconnect();
}
```

### AP Mode - Start Access Point

```c
#include "wifi_mgmr.h"

void wifi_ap_example(void)
{
    int ret;
    
    // Initialize WiFi manager
    wifi_mgmr_init();
    
    // Configure AP
    wifi_mgmr_ap_params_t ap_params = {0};
    ap_params.ssid = "MyAP";
    ap_params.key = "password123";  // NULL for open network
    ap_params.channel = 6;
    ap_params.hidden_ssid = false;
    ap_params.use_dhcpd = true;
    ap_params.ap_ipaddr = 0xC0A80101;    // 192.168.1.1
    ap_params.ap_mask = 0xFFFFFF00;      // 255.255.255.0
    ap_params.start = 100;               // DHCP pool: 192.168.1.100
    ap_params.limit = 50;                 // 50 addresses available
    ap_params.bcn_interval = 100;        // 100 TU beacon interval
    
    // Start AP
    ret = wifi_mgmr_ap_start(&ap_params);
    if (ret == 0) {
        printf("AP started: %s\r\n", ap_params.ssid);
    } else {
        printf("Failed to start AP\r\n");
    }
    
    // Get AP MAC address
    uint8_t mac[6];
    wifi_mgmr_ap_mac_get(mac);
    printf("AP MAC: %02X:%02X:%02X:%02X:%02X:%02X\r\n",
           mac[0], mac[1], mac[2], mac[3], mac[4], mac[5]);
    
    // Stop AP when done
    // wifi_mgmr_ap_stop();
}
```

### Country Code Configuration

```c
void wifi_country_code_example(void)
{
    char country_code[3] = {0};
    uint8_t c24g_count, c5g_count;
    uint8_t *c24g_list, *c5g_list;
    
    // Set country code
    int ret = wifi_mgmr_set_country_code("US");
    if (ret == 0) {
        printf("Country code set to US\r\n");
    }
    
    // Get current country code
    ret = wifi_mgmr_get_country_code(country_code);
    if (ret == 0) {
        printf("Current country code: %s\r\n", country_code);
    }
    
    // Get available channels
    ret = wifi_mgmr_get_channel_nums("US", &c24g_count, &c5g_count);
    if (ret == 0) {
        printf("US: %d 2.4GHz channels, %d 5GHz channels\r\n", c24g_count, c5g_count);
    }
    
    // Get channel lists
    ret = wifi_mgmr_get_channel_list("US", &c24g_list, &c5g_list);
    if (ret == 0) {
        printf("2.4GHz channels: ");
        for (int i = 0; i < c24g_count; i++) {
            printf("%d ", c24g_list[i]);
        }
        printf("\r\n");
    }
}
```

---

## Constants

```c
#define MGMR_SSID_LEN    32    // Maximum SSID length
#define MGMR_KEY_LEN     64    // Maximum password length
#define MGMR_BSSID_LEN   18    // BSSID string length (AA:BB:CC:DD:EE:FF)
#define MGMR_AKM_LEN     15    // AKM string length
#define MAX_AP_SCAN      50    // Maximum APs in scan list
#define MAX_FIXED_CHANNELS_LIMIT 42  // Maximum scan channels
```

### Authentication Types
```c
#define WIFI_EVENT_BEACON_IND_AUTH_OPEN          0
#define WIFI_EVENT_BEACON_IND_AUTH_WEP            1
#define WIFI_EVENT_BEACON_IND_AUTH_WPA_PSK        2
#define WIFI_EVENT_BEACON_IND_AUTH_WPA2_PSK       3
#define WIFI_EVENT_BEACON_IND_AUTH_WPA_WPA2_PSK   4
#define WIFI_EVENT_BEACON_IND_AUTH_WPA_ENT         5
#define WIFI_EVENT_BEACON_IND_AUTH_WPA3_SAE        6
#define WIFI_EVENT_BEACON_IND_AUTH_WPA2_PSK_WPA3_SAE 7
```

### Cipher Types
```c
#define WIFI_EVENT_BEACON_IND_CIPHER_NONE         0
#define WIFI_EVENT_BEACON_IND_CIPHER_WEP          1
#define WIFI_EVENT_BEACON_IND_CIPHER_AES          2
#define WIFI_EVENT_BEACON_IND_CIPHER_TKIP         3
#define WIFI_EVENT_BEACON_IND_CIPHER_TKIP_AES     4
```
