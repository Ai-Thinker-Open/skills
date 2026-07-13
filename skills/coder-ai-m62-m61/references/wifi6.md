# BL616/BL618 Wi-Fi 6 (802.11ax) Technical Documentation

## Overview

The BL616 and BL618 are high-performance Wi-Fi 6 wireless chips from Bouffalo, fully supporting the IEEE 802.11ax standard (Wi-Fi 6). Compared to the previous generation 802.11ac (Wi-Fi 5), Wi-Fi 6 delivers significant improvements in throughput, latency, power consumption, and dense network environment performance.

Key features of the BL616/BL618 Wi-Fi 6 solution include:

| Feature | Description |
|---------|-------------|
| **MU-MIMO** | Multi-User Multiple Input Multiple Output, supporting uplink/downlink multi-user data transmission |
| **OFDMA** | Orthogonal Frequency Division Multiple Access, dividing channels into smaller resource units to improve spectrum efficiency |
| **BSS Color** | Basic Service Set coloring, effectively reducing co-channel interference |
| **TWT** | Target Wake Time, significantly reducing device power consumption |
| **1024-QAM** | Higher-order modulation, ~25% peak rate improvement |
| **8 spatial streams** | Supports up to 8 concurrent spatial streams |

## Wi-Fi 6 Key Features in Detail

### Modulation and Rate

Wi-Fi 6 uses 1024-QAM (1024 Quadrature Amplitude Modulation), carrying 10 bits of data per symbol, a 25% improvement over Wi-Fi 5's 256-QAM (8 bits/symbol). With 80 MHz channel bandwidth, the theoretical peak rate reaches 1.2 Gbps; with 160 MHz channel bandwidth, it reaches 2.4 Gbps.

### MU-MIMO and OFDMA

**MU-MIMO (Multi-User Multiple Input Multiple Output)** allows the AP to communicate with multiple terminals simultaneously. In the BL616/BL618 implementation, both downlink MU-MIMO and uplink MU-MIMO are supported. Wi-Fi 6 extends MU-MIMO to 8x8 antenna configurations, supporting 8 spatial streams.

**OFDMA (Orthogonal Frequency Division Multiple Access)** divides the channel into multiple Resource Units (RUs), each of which can be assigned to a different user. OFDMA significantly improves system capacity and spectrum efficiency in multi-user concurrent scenarios, making it especially suitable for low-power, high-density terminal environments like IoT and smart homes.

### BSS Color

BSS Color (Basic Service Set Coloring) is a co-channel interference identification mechanism introduced in Wi-Fi 6. The AP carries a 6-bit color identifier during transmission, allowing terminals to identify signals from different BSSs and quickly switch to idle channels when co-channel interference is detected.

### Target Wake Time (TWT)

TWT (Target Wake Time) allows terminals to negotiate a precise wake schedule with the AP, enabling terminals to remain in low-power sleep mode most of the time. TWT technology is particularly critical for battery-powered IoT devices, potentially reducing power consumption by up to 90%.

## Wi-Fi Manager (wifi_mgmr) API

Wi-Fi Manager (wifi_mgmr) is the core management module of the BL616/BL618 Wi-Fi 6 driver, responsible for wireless connection, scanning, state management, and AP control operations.

### Header Files

```c
#include "wifi_mgmr.h"
#include "wifi_mgmr_ext.h"
```

### Initialization

```c
int wifi_mgmr_init(void);
int wifi_mgmr_task_start(void);
```

`wifi_mgmr_init()` initializes the Wi-Fi Manager system; `wifi_mgmr_task_start()` starts the Wi-Fi management task to begin processing wireless events.

### Connection Parameters

```c
typedef struct wifi_mgmr_sta_connect_params {
    char ssid[MGMR_SSID_LEN];          // SSID, max 32 bytes
    uint8_t ssid_len;                   // SSID length
    char key[MGMR_KEY_LEN];             // Password, max 64 bytes
    uint8_t key_len;                     // Password length
    char bssid_str[MGMR_BSSID_LEN];     // BSSID (optional)
    char akm_str[MGMR_AKM_LEN];         // AKM suite
    uint8_t pmf_cfg;                     // PMF configuration
    uint16_t freq1;                      // Primary frequency
    uint16_t freq2;                      // Secondary frequency (optional)
    uint8_t use_dhcp;                    // Whether to use DHCP
    uint8_t listen_interval;             // Listen interval [1, 100]
    uint8_t scan_mode;                   // Scan mode
    uint8_t quick_connect;               // Quick connect flag
    int timeout_ms;                       // Timeout (ms)
    uint16_t duration;                   // Scan duration (TU)
    uint16_t probe_cnt;                  // Probe count
    uint8_t auth_timeout;                 // Auth timeout (seconds)
} wifi_mgmr_sta_connect_params_t;
```

### STA Connection

```c
int wifi_mgmr_sta_connect(const wifi_mgmr_sta_connect_params_t *config);
```

Establishes a connection to an AP. The connection parameter structure must be pre-populated, including SSID, password, channel, etc.

**Example: Wi-Fi 6 STA Connection**

```c
#include "wifi_mgmr.h"
#include "wifi_mgmr_ext.h"

void wifi6_sta_connect_example(void)
{
    wifi_mgmr_sta_connect_params_t conn_params = {0};

    // Configure SSID
    memcpy(conn_params.ssid, "WiFi6_AP", 9);
    conn_params.ssid_len = 9;

    // Configure password
    memcpy(conn_params.key, "password123", 11);
    conn_params.key_len = 11;

    // Configure BSSID (optional)
    memcpy(conn_params.bssid_str, "aa:bb:cc:dd:ee:ff", 17);
    conn_params.bssid_str[17] = '\0';

    // Configure 5GHz band
    conn_params.freq1 = 5180;  // Channel 36

    // Enable DHCP
    conn_params.use_dhcp = 1;

    // Connection timeout 30 seconds
    conn_params.timeout_ms = 30000;

    // Initiate connection
    int ret = wifi_mgmr_sta_connect(&conn_params);
    if (ret == 0) {
        printf("Wi-Fi 6 connection request sent\r\n");
    }
}
```

### STA Disconnection

```c
void wifi_mgmr_sta_disconnect(void);
```

Actively disconnects the current STA connection.

### Scan API

```c
int wifi_mgmr_sta_scan(const wifi_mgmr_scan_params_t *config);
int wifi_mgmr_scan_beacon_save(wifi_mgmr_scan_item_t *scan);
int wifi_mgmr_scan_ap_all(void *env, void *arg, scan_item_cb_t cb);
```

Scan parameter structure definition:

```c
typedef struct wifi_mgmr_scan_params {
    uint8_t ssid_length;
    uint8_t ssid_array[MGMR_SSID_LEN];  // Specified SSID
    uint8_t bssid[6];                     // Specified BSSID
    uint8_t bssid_set_flag;               // BSSID set flag
    uint8_t probe_cnt;                    // Probe request count
    int channels_cnt;                      // Channel count
    uint8_t channels[MAX_FIXED_CHANNELS_LIMIT]; // Channel list
    uint32_t duration;                     // Scan duration
    bool passive;                          // Passive scan mode
} wifi_mgmr_scan_params_t;
```

Scan result item structure:

```c
typedef struct wifi_mgmr_scan_item {
    uint32_t mode;
    uint32_t timestamp_lastseen;
    int ssid_len;
    uint8_t channel;
    int8_t rssi;               // Signal strength (dBm)
    char ssid[32];             // SSID
    uint8_t bssid[6];          // BSSID
    int8_t ppm_abs;            // Absolute power offset
    int8_t ppm_rel;            // Relative power offset
    uint8_t auth;              // Auth type
    uint8_t cipher;            // Cipher type
    uint8_t is_used;           // Whether in use
    uint8_t wps;               // WPS support
    uint8_t best_antenna;      // Best antenna
} wifi_mgmr_scan_item_t;
```

**Example: Full-Channel Active Scan**

```c
void wifi6_scan_all_channels_example(void)
{
    wifi_mgmr_scan_params_t scan_params = {0};

    scan_params.ssid_length = 0;        // Scan all SSIDs
    scan_params.bssid_set_flag = 0;     // Don't specify BSSID
    scan_params.probe_cnt = 3;           // 3 probes per channel
    scan_params.passive = false;         // Active scan
    scan_params.duration = 100;          // Scan duration 100 TU

    int ret = wifi_mgmr_sta_scan(&scan_params);
    if (ret == 0) {
        printf("Scan started\r\n");
    }
}
```

### State Query

```c
int wifi_mgmr_state_get(void);
int wifi_mgmr_sta_connect_ind_stat_get(wifi_mgmr_connect_ind_stat_info_t *info);
```

Connection state info structure:

```c
typedef struct wifi_mgmr_connect_ind_stat_info {
    uint16_t status_code;    // Status code
    uint16_t reason_code;    // Reason code
    char ssid[33];           // Current SSID
    char passphr[65];        // Password
    uint8_t bssid[6];        // BSSID
    uint8_t channel;         // Channel
    uint8_t security;        // Security type
    uint16_t aid;            // Association ID
    uint8_t vif_idx;         // Virtual interface index
    uint8_t ap_idx;          // AP index
    uint8_t ch_idx;          // Channel index
    bool qos;                // QoS support
    uint8_t bss_mode;        // BSS mode
} wifi_mgmr_connect_ind_stat_info_t;
```

### Country Code Configuration

```c
int wifi_mgmr_get_channel_nums(const char *country_code, uint8_t *c24G_cnt, uint8_t *c5G_cnt);
void wifi_mgmr_print_channel_info(const char *country_code);
```

**Wi-Fi Event Definitions (wifi_mgmr_ext.h)**

```c
#define EV_WIFI                   0x0002
#define CODE_WIFI_ON_INIT_DONE    1   // Initialization complete
#define CODE_WIFI_ON_MGMR_DONE    2   // Manager ready
#define CODE_WIFI_CMD_RECONNECT   3   // Reconnect command
#define CODE_WIFI_ON_CONNECTED    4   // Connected
#define CODE_WIFI_ON_DISCONNECT   5   // Disconnected
#define CODE_WIFI_ON_PRE_GOT_IP   6   // Before getting IP
#define CODE_WIFI_ON_GOT_IP       7   // Got IP
#define CODE_WIFI_ON_CONNECTING   8   // Connecting
#define CODE_WIFI_ON_SCAN_DONE    9   // Scan complete
#define CODE_WIFI_ON_AP_STARTED   11  // AP started
#define CODE_WIFI_ON_AP_STOPPED   12  // AP stopped
#define CODE_WIFI_ON_GOT_IP6      25  // Got IPv6
```

### TWT (Target Wake Time) Configuration

Wi-Fi 6 supports TWT functionality, allowing devices to negotiate precise wake times with the AP.

```c
void cmd_wifi_mgmr_sta_twt_setup(int argc, char **argv);
void cmd_wifi_mgmr_sta_twt_teardown(int argc, char **argv);
void cmd_wifi_mgmr_sta_twt_statusget(int argc, char **argv);
```

**TWT Parameter Structure (cfgmacsw.h)**

```c
struct cfgmacsw_twt_setup_req {
    uint16_t fhost_vif_idx;       // Virtual interface index
    uint8_t setup_type;            // Setup type
    uint8_t flow_type;             // Flow type (0: Announced, 1: Unannounced)
    uint8_t wake_int_exp;         // Wake interval exponent
    bool wake_dur_unit;            // Wake duration unit
    uint8_t min_twt_wake_dur;      // Minimum TWT wake duration
    uint16_t wake_int_mantissa;   // Wake interval mantissa
};
```

**Example: TWT Setup**

```c
void wifi6_twt_setup_example(void)
{
    // TWT parameters
    // wake_int_exp = 10, wake_int_mantissa = 1000
    // Actual wake interval = 2^10 * 1000 = 1024000 us = 1024 ms

    printf("TWT setup: wake interval 1024ms\r\n");
    // Invoke CLI command or directly call driver API
    // wifi_mgmr_sta_twt_setup(...);
}
```

### Power Control

```c
int wifi_mgmr_ps_on(void);   // Enable power saving
int wifi_mgmr_ps_off(void);  // Disable power saving
int wifi_mgmr_ps_set(int level);  // Set power level
```

### AP Mode

```c
int wifi_mgmr_ap_start(wifi_mgmr_ap_params_t *params);
int wifi_mgmr_ap_stop(void);
int wifi_mgmr_ap_sta_list_get(void);
int wifi_mgmr_ap_sta_delete(uint8_t sta_idx);
```

AP parameter structure:

```c
typedef struct wifi_mgmr_ap_params {
    char *ssid;                    // SSID
    char *key;                     // Password
    char *akm;                     // AKM suite (OPEN/WPA/WPA2)
    uint8_t channel;               // Channel
    uint8_t type;                  // Channel bandwidth type
    bool use_dhcpd;                // Enable DHCP server
    int start;                      // DHCP pool start address
    int limit;                      // DHCP pool size
    uint32_t ap_ipaddr;            // AP IP address
    uint32_t ap_mask;              // Subnet mask
    bool hidden_ssid;              // Hidden SSID
    bool isolation;                // Client isolation
    int bcn_interval;              // Beacon interval (TU)
    uint8_t bcn_mode;              // Beacon mode
    int bcn_timer;                 // Beacon timer
    bool disable_wmm;              // Disable WMM
} wifi_mgmr_ap_params_t;
```

## wifi6_lwip_adapter and MAT Adaptation Layer

`wifi6_lwip_adapter` is the adaptation layer module that connects the Wi-Fi 6 driver with the LWIP network protocol stack. Core functionality includes network interface management, packet transmission/reception, and MAT (MAC Address Translation).

### MAT Module

The MAT (MAC Address Translation) module is responsible for maintaining the mapping relationship between IP addresses and MAC addresses, supporting ARP proxy and ND (Neighbor Discovery) optimization.

**Header File**

```c
#include "mat.h"
```

**MAT Error Codes**

```c
#define MAT_ERR_OK      0   // Success
#define MAT_ERR_INVAL   -1  // Invalid parameter
#define MAT_ERR_STATUS  -2  // Status error
#define MAT_ERR_MEM     -3  // Memory error
#define MAT_ERR_DATA    -4  // Data error
#define MAT_ERR_PROTO   -5  // Protocol error
```

**MAT Tuple Structure**

```c
struct mat_tuple {
    uint8_t hwaddr[6];     // MAC address
    uint8_t used;          // Usage flag
    uint32_t ts;           // Timestamp
    ip_addr_t ipaddr;      // IP address
};
```

**MAT API**

```c
int mat_tuple_add(uint8_t *hwaddr, ip_addr_t *ip);
// Add IP-MAC mapping tuple

int mat_tuple_del(uint8_t *hwaddr, ip_addr_t *ip);
// Delete IP-MAC mapping tuple

int mat_handle_egress(struct netif *netif, struct pbuf *pbuf, struct pbuf **out);
// Process egress packets (before transmission)

int mat_handle_ingress(struct netif *netif, struct pbuf *pbuf);
// Process ingress packets (after reception)

struct mat_tuple *mat_tuple_find(uint8_t *hwaddr, ip_addr_t *ip);
// Find IP-MAC mapping tuple
```

**How MAT Works**

On the egress side, the MAT module checks whether the destination IP of a packet already has a corresponding MAC mapping: if so, it directly encapsulates; if not, it triggers the ARP learning process. On the ingress side, MAT records source IP-MAC mappings for subsequent use.

### Network Interface Definitions (net_def.h)

```c
typedef struct netif        inet_if_t;      // Network interface
typedef struct pbuf_custom  inet_buf_rx_t;  // Receive buffer
typedef struct pbuf         inet_buf_tx_t;  // Transmit buffer

#define NET_AL_MAX_IFNAME   4               // Max interface name length
```

### LWIP Integration

The wifi6_lwip_adapter module encapsulates the Wi-Fi 6 driver as a netif interface callable by LWIP, enabling transparent IP-layer transmission. Applications do not need to concern themselves with low-level wireless driver details and can directly use standard LWIP socket APIs for network communication.

**Typical Initialization Flow**

```c
#include "wifi_mgmr.h"
#include "lwip/netif.h"

extern struct netif *netif_get_sta(void);

void wifi6_lwip_init_example(void)
{
    struct netif *sta_netif = netif_get_sta();

    // Wi-Fi initialization
    wifi_mgmr_init();
    wifi_mgmr_task_start();

    // Connect Wi-Fi
    wifi_mgmr_sta_connect(&conn_params);

    // LWIP automatically acquires IP (DHCP)
    // Applications can directly use socket APIs
}
```

## OFDMA Configuration

OFDMA is one of Wi-Fi 6's core technologies. The BL616/BL618 driver supports configuring OFDMA parameters via command line or API.

### OFDMA Parameters

OFDMA configuration primarily involves channel bandwidth and resource unit division. The BL616/BL618 supports 20MHz, 40MHz, 80MHz, and 160MHz channel bandwidths, corresponding to different RU (Resource Unit) division schemes.

### Channel Bandwidth and RU Configuration

| Channel Bandwidth | Max RUs | Min RU Size |
|-------------------|---------|-------------|
| 20 MHz            | 9       | 26-tone     |
| 40 MHz            | 18      | 26-tone     |
| 80 MHz            | 37      | 26-tone     |
| 160 MHz           | 74      | 26-tone     |

### CLI Command Configuration

Wi-Fi 6 OFDMA can be configured via shell commands:

```bash
# Enable Wi-Fi 6 mode
wifi_mode_set ax

# Configure OFDMA parameters
ofdma_config 1  # Enable OFDMA

# View OFDMA status
ofdma_status
```

### Configuring OFDMA in Code

```c
// OFDMA configuration example
void wifi6_ofdma_config_example(void)
{
    // Set channel bandwidth to 80MHz
    uint8_t channel_width = 2;  // 0: 20MHz, 1: 40MHz, 2: 80MHz, 3: 160MHz

    // Enable MU-MIMO
    uint8_t mu_mimo_enable = 1;

    // Enable OFDMA
    uint8_t ofdma_enable = 1;

    printf("Wi-Fi 6 OFDMA configuration complete\r\n");
    printf("Channel bandwidth: %s\r\n",
           channel_width == 2 ? "80MHz" : "Other");
    printf("MU-MIMO: %s\r\n",
           mu_mimo_enable ? "Enabled" : "Disabled");
    printf("OFDMA: %s\r\n",
           ofdma_enable ? "Enabled" : "Disabled");
}
```

## FAQ and Troubleshooting

### Connection Failure

1. **Check SSID and password**: Ensure configuration is correct
2. **Check channel**: Confirm the device-supported channel matches the AP
3. **Check signal strength**: RSSI below -80 dBm may cause unstable connections
4. **Check logs**: View Wi-Fi event code output via serial port

### No Scan Results

1. Confirm Wi-Fi driver is initialized
2. Check country code settings to ensure desired channels are available
3. Try passive scan mode (`passive = true`)
