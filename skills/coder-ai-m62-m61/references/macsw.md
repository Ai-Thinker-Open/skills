# MACSW (MAC Software) Technical Documentation

## Overview

MACSW (MAC Software) is the core software layer in Bouffalo Lab's wireless SDK, positioned between the Host CPU and the wireless baseband (Modem), responsible for handling all software logic of the IEEE 802.11 MAC layer. As a bridge connecting the upper-layer network protocol stack to the low-level hardware, MACSW provides key functions such as frame transmission/reception, encryption engine management, and power management.

MACSW is designed to implement a hardware-decoupled MAC layer software framework, allowing upper-layer protocol stacks (e.g., Wi-Fi Mgmr, wl80211) to control the wireless hardware through a unified interface without needing to understand specific hardware implementation details.

### Core Features

- **Version**: v6.10.0.0
- **Protocol Support**: 802.11a/b/g/n/ac/ax (Wi-Fi 6)
- **Multi-Interface Support**: Up to 4 virtual interfaces (VIF)
- **Security Engine**: Hardware AES-CCMP/TKIP acceleration
- **Power Management**: Supports Legacy PS, UAPSD, TWT

---

## Architecture

```
┌─────────────────────────────────┐
│    Upper-layer Apps / Network   │
│   Protocol Stack                │
│   (wifi_mgmr / wl80211 / TCPIP) │
└───────────────┬─────────────────┘
                │
┌───────────────▼─────────────────┐
│         MACSW Layer             │
│   (MAC Software - this doc)     │
│  - Frame processing             │
│  - Encryption engine mgmt       │
│  - Power management             │
│  - MIMO/MU-MIMO control         │
└───────────────┬─────────────────┘
                │
┌───────────────▼─────────────────┐
│       MAC HW / Modem            │
│   (Wireless baseband HW         │
│    abstraction layer)           │
└─────────────────────────────────┘
```

In the software architecture, MACSW sits at a lower level than wifi_mgmr and wl80211. wifi_mgmr handles Wi-Fi connection management (e.g., scanning, authentication, association), while MACSW directly interacts with hardware to handle MAC layer specifics.

---

## Header File Overview

| Header File | Description |
|--------|----------|
| `macsw.h` | Main header, contains version, config macros, core API declarations |
| `macsw_plat.h` | Platform-related interfaces (init, frame tx/rx, RTOS task management) |
| `ieee80211.h` | IEEE 802.11 frame format definitions (Frame Control, Address, Sequence, etc.) |
| `mac_types.h` | MAC layer data type definitions (frame types, cipher suites, rate sets, etc.) |
| `macsw_bridge_config.h` | Wi-Fi bridge configuration parameters |
| `bl_fw_api.h` | Firmware API wrapper |

---

## macsw_plat.h - Platform Abstraction Interface

`macsw_plat.h` defines the core interfaces for MACSW interaction with low-level hardware and RTOS, including initialization, frame tx/rx, and task management.

### Core Functions

#### macsw_init()

Initializes the MACSW software layer. Called at system startup to initialize internal data structures, configure hardware parameters, and create RTOS tasks.

#### macsw_send_frame()

Sends raw 802.11 frames to the wireless channel. This function receives complete MAC frame data, fills necessary hardware descriptors, and transmits the frame to the air interface.

#### macsw_recv_frame()

Receives 802.11 frames from the wireless channel. When hardware detects a valid frame, data is passed to the upper-layer protocol stack through this function.

### RTOS Task Management

```c
// Create Wi-Fi task
void wifi_task_create(void);

// Suspend Wi-Fi task
void wifi_task_suspend(void);

// Resume Wi-Fi task (typically called from interrupt context)
void wifi_task_resume(bool isr);

// Get system uptime (milliseconds)
uint32_t wifi_sys_now_ms(bool isr);
```

### Interrupt Management

MACSW uses critical sections to protect shared resources:

```c
#define GLOBAL_INT_DISABLE()      // Disable global interrupts
#define GLOBAL_INT_RESTORE()      // Restore global interrupts
```

### Logging Interface

```c
void wifi_syslog(int priority, const char *fmt, ...);
```

---

## ieee80211.h - 802.11 Frame Format Definitions

`ieee80211.h` defines the frame structure specified by the IEEE 802.11 standard, including Frame Control, Duration, Address, Sequence Control, QoS Control, and other fields.

### Frame Control Field

```c
#define WIRELESS_80211_FCTL_FTYPE     0x000c  // Frame type mask
#define WIRELESS_80211_FCTL_STYPE     0x00f0  // Subtype mask

#define WIRELESS_80211_FTYPE_MGMT     0x0000  // Management frame
#define WIRELESS_80211_FTYPE_DATA     0x0008  // Data frame

/* Management frame subtypes */
#define WIRELESS_80211_STYPE_PROBE_REQ    0x0040  // Probe request
#define WIRELESS_80211_STYPE_PROBE_RESP   0x0050  // Probe response
#define WIRELESS_80211_STYPE_BEACON       0x0080  // Beacon frame
#define WIRELESS_80211_STYPE_DISASSOC     0x00A0  // Disassociation
#define WIRELESS_80211_STYPE_AUTH         0x00B0  // Authentication
#define WIRELESS_80211_STYPE_DEAUTH       0x00C0  // Deauthentication
#define WIRELESS_80211_STYPE_ACTION       0x00D0  // Action frame

/* Data frame subtypes */
#define WIRELESS_80211_STYPE_QOS_DATA     0x0080  // QoS Data frame
```

### Frame Type Detection Helper Functions

```c
// Check if beacon frame
static inline bool wireless_80211_is_beacon(__le16 fc);

// Check if deauthentication frame
static inline bool wireless_80211_is_deauth(__le16 fc);

// Check if disassociation frame
static inline bool wireless_80211_is_disassoc(__le16 fc);

// Check if Action frame
static inline bool wireless_80211_is_action(__le16 fc);

// Check if probe response frame
static inline int wireless_80211_is_probe_resp(__le16 fc);

// Check if probe request frame
static inline bool wireless_80211_is_probe_req(__le16 fc);

// Check if data frame
static inline bool wireless_80211_is_data(__le16 fc);

// Check if QoS data frame
static inline bool wireless_80211_is_data_qos(__le16 fc);
```

### Sequence Control

```c
#define WIRELESS_80211_SCTL_SEQ         0xFFF0  // Sequence number mask
#define WIRELESS_80211_SN_MASK          ((WIRELESS_80211_SCTL_SEQ) >> 4)
#define WIRELESS_80211_MAX_SN           WIRELESS_80211_SN_MASK
#define WIRELESS_80211_SN_MODULO       (WIRELESS_80211_MAX_SN + 1)
```

### 802.11 Reason Codes

```c
enum wireless_80211_reasoncode {
    WIRELESS_REASONCODE_UNSPECIFIED = 1,
    WIRELESS_REASONCODE_PRE_AUTH_NOT_VALID = 2,
    WIRELESS_REASONCODE_DEAUTH_LEAVING = 3,
    WIRELESS_REASONCODE_DISASSOC_DUE_TO_INACTIVITY = 4,
    WIRELESS_REASONCODE_DISASSOC_AP_BUSY = 5,
    WIRELESS_REASONCODE_CLASS2_FRAME_FROM_NONAUTH_STA = 6,
    WIRELESS_REASONCODE_CLASS3_FRAME_FROM_NONASSOC_STA = 7,
    WIRELESS_REASONCODE_DISASSOC_STA_HAS_LEFT = 8,
    WIRELESS_REASONCODE_STA_REQ_ASSOC_WITHOUT_AUTH = 9,
};
```

---

## mac_types.h - MAC Layer Data Types

`mac_types.h` defines all core data structures used by MACSW, including interface types, MAC addresses, SSIDs, channel definitions, cipher suites, and rate sets.

### Virtual Interface Types

```c
enum mac_vif_type {
    VIF_STA,           // ESS STA interface
    VIF_IBSS,          // IBSS STA interface
    VIF_AP,            // AP interface
    VIF_MESH_POINT,    // Mesh Point interface
    VIF_MONITOR,       // Monitor interface
    VIF_UNKNOWN
};
```

### MAC Address

```c
#define MAC_ADDR_LEN 6

struct mac_addr {
    uint16_t array[MAC_ADDR_LEN/2];  // 3 x 16-bit words forming a 6-byte address
};
```

### SSID

```c
#define MAC_SSID_LEN 32

struct mac_ssid {
    uint8_t length;                  // Actual SSID length
    uint8_t array[MAC_SSID_LEN];     // SSID character array
};
```

### Channel Definition

```c
// Band
enum mac_chan_band {
    PHY_BAND_2G4 = 0,    // 2.4 GHz band
    PHY_BAND_5G,         // 5 GHz band
    PHY_BAND_MAX
};

// Bandwidth
enum mac_chan_bandwidth {
    PHY_CHNL_BW_20,      // 20 MHz
    PHY_CHNL_BW_40,      // 40 MHz
    PHY_CHNL_BW_80,      // 80 MHz
    PHY_CHNL_BW_160,     // 160 MHz
    PHY_CHNL_BW_80P80,   // 80+80 MHz
    PHY_CHNL_BW_OTHER
};

// Channel flags
enum mac_chan_flags {
    CHAN_NO_IR = CO_BIT(0),        // No transmission allowed
    CHAN_DISABLED = CO_BIT(1),     // Channel disabled
    CHAN_RADAR = CO_BIT(2),        // Radar detection required
    CHAN_DISABLE_VHT = CO_BIT(6),  // VHT disabled
    CHAN_DISABLE_HE = CO_BIT(7),   // HE disabled
};

// Channel definition
struct mac_chan_def {
    uint16_t freq;                 // Frequency (MHz)
    uint8_t band;                  // Band
    uint8_t flags;                 // Flags
    int8_t tx_power;               // Max TX power (dBm)
};

// Channel operating parameters
struct mac_chan_op {
    uint8_t band;
    uint8_t type;                  // Bandwidth type
    uint16_t prim20_freq;          // Primary 20 MHz frequency
    uint16_t center1_freq;         // Center frequency 1
    uint16_t center2_freq;         // Center frequency 2
    int8_t tx_power;
    uint8_t flags;
};
```

### Cipher Suites

```c
enum mac_cipher_suite {
    MAC_CIPHER_WEP40 = 1,          // WEP-40
    MAC_CIPHER_TKIP = 2,           // TKIP
    MAC_CIPHER_CCMP = 4,           // CCMP-128
    MAC_CIPHER_WEP104 = 5,         // WEP-104
    MAC_CIPHER_WPI_SMS4 = 6,       // WAPI
    MAC_CIPHER_BIP_CMAC_128 = 6,  // AES_CMAC
    MAC_CIPHER_GCMP_128 = 8,       // GCMP-128
    MAC_CIPHER_GCMP_256 = 9,      // GCMP-256
    MAC_CIPHER_CCMP_256 = 10,      // CCMP-256
    MAC_CIPHER_BIP_GMAC_128 = 11,
    MAC_CIPHER_BIP_GMAC_256 = 12,
    MAC_CIPHER_BIP_CMAC_256 = 13,
    MAC_CIPHER_INVALID = 0xFF
};
```

### Authentication and Key Management (AKM)

```c
enum mac_akm_suite {
    MAC_AKM_NONE = 0,               // No security
    MAC_AKM_PRE_RSN = 1,            // Pre-RSNA (WEP/WPA)
    MAC_AKM_8021X = 2,             // 802.1X
    MAC_AKM_PSK = 3,               // PSK
    MAC_AKM_FT_8021X = 4,          // FT 802.1X
    MAC_AKM_FT_PSK = 5,            // FT PSK
    MAC_AKM_8021X_SHA256 = 6,      // 802.1X + SHA256
    MAC_AKM_PSK_SHA256 = 7,        // PSK + SHA256
    MAC_AKM_TDLS = 8,              // TDLS
    MAC_AKM_SAE = 9,               // SAE
    MAC_AKM_FT_OVER_SAE = 10,      // FT over SAE
    MAC_AKM_8021X_SUITE_B = 11,    // 802.1X Suite B
    MAC_AKM_8021X_SUITE_B_192 = 12,
    MAC_AKM_FILS_SHA256 = 14,      // FILS + SHA256
    MAC_AKM_FILS_SHA384 = 15,      // FILS + SHA384
    MAC_AKM_FT_FILS_SHA256 = 16,
    MAC_AKM_FT_FILS_SHA384 = 17,
    MAC_AKM_OWE = 18,              // OWE
    MAC_AKM_WAPI_CERT = 256,       // WAPI Certificate
    MAC_AKM_WAPI_PSK = 257,        // WAPI PSK
};
```

### Wi-Fi Mode

```c
typedef enum {
    WIFI_MODE_802_11B = 0x01,       // 802.11b
    WIFI_MODE_802_11A = 0x02,       // 802.11a
    WIFI_MODE_802_11G = 0x04,       // 802.11g
    WIFI_MODE_802_11N_2_4 = 0x08,  // 802.11n @ 2.4GHz
    WIFI_MODE_802_11N_5 = 0x10,     // 802.11n @ 5GHz
    WIFI_MODE_802_11AC_5 = 0x20,   // 802.11ac @ 5GHz
    WIFI_MODE_802_11AC_2_4 = 0x40, // 802.11ac @ 2.4GHz
    WIFI_MODE_802_11AX_2_4 = 0x80, // 802.11ax @ 2.4GHz (Wi-Fi 6)
    WIFI_MODE_802_11AX_5 = 0x100,  // 802.11ax @ 5GHz (Wi-Fi 6)
} WiFi_Mode_t;

// Common combined modes
#define WIFI_MODE_BGN (WIFI_MODE_802_11B | WIFI_MODE_802_11G | WIFI_MODE_802_11N_2_4)
#define WIFI_MODE_BGNAX (WIFI_MODE_802_11B | WIFI_MODE_802_11G | WIFI_MODE_802_11N_2_4 | WIFI_MODE_802_11AX_2_4)
```

### Access Categories and TID

```c
enum mac_ac {
    AC_BK = 0,      // Background
    AC_BE = 1,      // Best-effort
    AC_VI = 2,      // Video
    AC_VO = 3,      // Voice
    AC_MAX
};

enum mac_tid {
    TID_0 = 0, TID_1, TID_2, TID_3, TID_4, TID_5, TID_6, TID_7,
    TID_MGT,        // Management TID
    TID_MAX
};
```

### Rate Definition

```c
enum mac_legacy_rates {
    MAC_RATE_1MBPS = 2,
    MAC_RATE_2MBPS = 4,
    MAC_RATE_5_5MBPS = 11,
    MAC_RATE_11MBPS = 22,
    MAC_RATE_6MBPS = 12,
    MAC_RATE_9MBPS = 18,
    MAC_RATE_12MBPS = 24,
    MAC_RATE_18MBPS = 36,
    MAC_RATE_24MBPS = 48,
    MAC_RATE_36MBPS = 72,
    MAC_RATE_48MBPS = 96,
    MAC_RATE_54MBPS = 108
};

struct mac_rateset {
    uint8_t length;                  // Number of rates
    uint8_t array[MAC_RATESET_LEN];  // Rate array
};
```

### Security Key

```c
#define MAC_SEC_KEY_LEN 32

struct mac_sec_key {
    uint8_t length;                  // Key length
    uint32_t array[MAC_SEC_KEY_LEN/4]; // Key data
};
```

### Scan Results

```c
struct mac_scan_result {
    bool valid_flag;                  // Result valid flag
    struct mac_addr bssid;           // BSSID
    struct mac_ssid ssid;            // SSID
    uint16_t bsstype;                // BSS type
    struct mac_chan_def *chan;       // Channel info
    uint32_t akm;                    // Supported AKM suites
    uint16_t group_cipher;           // Group cipher suite
    uint16_t pairwise_cipher;        // Pairwise cipher suite
    int8_t rssi;                     // Signal strength
    uint8_t multi_bssid_index;
    uint8_t max_bssid_indicator;
    bool ftm_support;                // FTM support
    void *rxu_mgmt_ind;
};
```

---

## macsw_bridge_config.h - Bridge Configuration

`macsw_bridge_config.h` defines configuration parameters for Wi-Fi bridge mode, including tx/rx descriptor counts and reorder buffer sizes.

```c
#define CFG_BARX 12                  // RX Block Ack request count
#define CFG_BATX 12                  // TX Block Ack request count
#define CFG_REORD_BUF 12             // Reorder buffer count

// A-MSDU config
#define CFG_AMSDU_8K                 // Enable 8K A-MSDU support

// TX descriptor config
#define CFG_TXDESC0 12
#define CFG_TXDESC1 64
#define CFG_TXDESC2 12
#define CFG_TXDESC3 12
#define CFG_TXDESC4 2

// Receive buffer config
#define CONFIG_FHOST_RX_BUF_SECTION ".psram_noinit"
```

---

## Encryption Engine

MACSW supports multiple cipher suites through hardware acceleration, including:

### AES-CCMP

CCMP (Counter Mode CBC-MAC Protocol) is a mandatory requirement of the 802.11i standard, used to protect frame security in WPA2 networks.

```c
// Get CCMP encryption status
uint8_t inline_macsw_mac_ccmp_getf(void);
```

### TKIP

TKIP (Temporal Key Integrity Protocol) is the WPA standard encryption protocol, providing backward compatibility with WEP.

```c
// Get TKIP encryption status
uint8_t inline_macsw_mac_tkip_getf(void);
```

### GCMP

GCMP (Galois/Counter Mode Protocol) is an efficient encryption protocol for 802.11ad/ax standards.

```c
// Get GCMP encryption status
uint8_t inline_macsw_mac_gcmp_getf(void);
```

The hardware encryption engine sits between the MAC layer and the Modem. When MACSW sends a frame, data automatically passes through the hardware encryption module for encryption; when receiving a frame, it is likewise automatically decrypted before being passed to software for processing.

---

## Relationship with wifi_mgmr / wl80211

MACSW sits at a lower level in the software stack, interacting directly with hardware:

```
┌─────────────────────────┐
│     wifi_mgmr            │  Connection mgmt, scan, auth, assoc
├─────────────────────────┤
│     wl80211              │  802.11 driver abstraction layer
├─────────────────────────┤
│     MACSW (this doc)     │  MAC layer software implementation
├─────────────────────────┤
│     MAC HW / Modem       │  Hardware abstraction layer
└─────────────────────────┘
```

- **wifi_mgmr**: Handles Wi-Fi connection state machine, processes scan results, initiates auth/assoc requests
- **wl80211**: Provides a Linux nl80211-like interface for configuring wireless devices
- **MACSW**: Actually executes MAC layer operations, including frame formatting, hardware descriptor population, and encryption processing

---

## Code Examples

### MACSW Initialization

```c
#include "macsw.h"
#include "macsw_plat.h"

// Called during system init
void system_wifi_init(void)
{
    // Create Wi-Fi task
    wifi_task_create();
}

// Or in standalone init scenario
void macsw_example_init(void)
{
    // Initialize MACSW component
    // Initialize hardware descriptors
    // Configure default channel
    // Enable interrupts
}
```

### Sending Raw 802.11 Frames

```c
#include "macsw.h"
#include "ieee80211.h"

// Example: sending a raw 802.11 data frame
int send_raw_80211_frame(uint8_t *dest_mac, uint8_t *payload, uint16_t payload_len)
{
    // Frame format:
    // [Frame Control(2)] [Duration(2)] [Address1(6)] [Address2(6)] [Address3(6)] [Sequence Control(2)] [payload]
    //
    // For data frames:
    // - Address1: Receiver MAC (RA)
    // - Address2: Transmitter MAC (TA)
    // - Address3: BSSID or destination address
    
    uint8_t frame[256];
    uint16_t frame_len = 0;
    __le16 fc;
    
    // Construct Frame Control (Data frame, To DS)
    fc = WIRELESS_80211_FTYPE_DATA | WIRELESS_80211_STYPE_QOS_DATA;
    // Set To DS bit
    fc |= cpu_to_le16(0x0001);
    
    frame[0] = fc & 0xFF;
    frame[1] = (fc >> 8) & 0xFF;
    frame_len += 2;
    
    // Duration (16 bits)
    frame[frame_len++] = 0x00;
    frame[frame_len++] = 0x00;
    
    // Address1 (DA)
    memcpy(&frame[frame_len], dest_mac, 6);
    frame_len += 6;
    
    // Address2 (SA) - local MAC
    uint8_t local_mac[6] = {0xAA, 0xBB, 0xCC, 0xDD, 0xEE, 0xFF};
    memcpy(&frame[frame_len], local_mac, 6);
    frame_len += 6;
    
    // Address3 (BSSID)
    uint8_t bssid[6] = {0x11, 0x22, 0x33, 0x44, 0x55, 0x66};
    memcpy(&frame[frame_len], bssid, 6);
    frame_len += 6;
    
    // Sequence Control (12 bits sequence number + 4 bits fragment number)
    frame[frame_len++] = 0x00;
    frame[frame_len++] = 0x10;  // Sequence number = 1
    frame_len += 2;  // QoS Control
    
    // Payload
    memcpy(&frame[frame_len], payload, payload_len);
    frame_len += payload_len;
    
    // FCS (4 bytes) - typically added automatically by hardware
    // frame[frame_len++] = 0x00;
    // frame[frame_len++] = 0x00;
    // frame[frame_len++] = 0x00;
    // frame[frame_len++] = 0x00;
    
    // Call send interface
    // macsw_send_frame(frame, frame_len);
    
    return 0;
}
```

### Parsing 802.11 Frame Types

```c
#include "ieee80211.h"

void handle_incoming_frame(uint8_t *frame, uint16_t frame_len)
{
    if (frame_len < 2) return;
    
    __le16 fc = frame[0] | ((__le16)frame[1] << 8);
    
    if (wireless_80211_is_beacon(fc)) {
        // Handle beacon frame
        // printf("Received Beacon frame\n");
    } else if (wireless_80211_is_probe_req(fc)) {
        // Handle probe request frame
        // printf("Received Probe Request\n");
    } else if (wireless_80211_is_data(fc)) {
        // Handle data frame
        if (wireless_80211_is_data_qos(fc)) {
            // printf("Received QoS Data frame\n");
        } else {
            // printf("Received Data frame\n");
        }
    } else if (wireless_80211_is_deauth(fc)) {
        // Handle deauthentication frame
        // printf("Received Deauth frame\n");
    }
}
```

---

## Configuration Macro Reference

### Version Information

```c
#define MACSW_VERSION_STR "v6.10.0.0"
#define MACSW_VERSION_MAJ 6
#define MACSW_VERSION_MIN 10
#define MACSW_VERSION_REL 0
#define MACSW_VERSION_PAT 0
```

### Feature Switches

| Macro | Description |
|----|------|
| `CFG_BCN` | Beacon support |
| `CFG_PS` | Power management |
| `CFG_UAPSD` | U-APSD power save mode |
| `CFG_MFP` | MFP (Management Frame Protection) |
| `CFG_AMSDU` | A-MSDU aggregation |
| `CFG_AMPDU_TX` | A-MPDU transmit aggregation |
| `CFG_AMPDU_RX` | A-MPDU receive aggregation |
| `CFG_VHT` | VHT (802.11ac) |
| `CFG_HE` | HE (802.11ax/Wi-Fi 6) |
| `CFG_MESH` | Mesh network support |
| `CFG_P2P` | P2P support |

### Limit Parameters

```c
#define MACSW_VIRT_DEV_MAX 4      // Maximum virtual interface count
#define MACSW_REMOTE_STA_MAX     // Maximum associated station count
#define MACSW_MAX_BA_TX          // Maximum TX Block Ack count
#define MACSW_MAX_BA_RX          // Maximum RX Block Ack count
#define MACSW_HEAP_SIZE          // Heap memory size
```

---

## References

- [Bouffalo SDK Documentation](../README.md) - SDK overview
- [Wi-Fi Driver Component Documentation](../wl80211/README.md) - wl80211 Wi-Fi driver details
- IEEE Std 802.11™ - 802.11 protocol standard
- Bouffalo Lab BL618 Product Manual
