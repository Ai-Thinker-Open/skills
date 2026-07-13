# Wi-Fi 4 (802.11n) Technical Reference

## Overview

Wi-Fi 4 is a wireless networking protocol based on the IEEE 802.11n standard, also known as HT (High Throughput) mode. This mode is primarily used for compatibility with legacy 802.11b/g devices, or as a fallback mode in Wi-Fi 6 (802.11ax) environments. In the Bouffalo Lab SDK, Wi-Fi 4 is implemented by the `wifi4` component, supporting both 2.4GHz and 5GHz dual-band operation.

802.11n introduces several enhancement technologies at the physical layer, significantly improving throughput and coverage. Compared to 802.11g's theoretical rate of 54Mbps, 802.11n can reach 150Mbps (single spatial stream) with 40MHz bandwidth and Short GI. For embedded devices, Wi-Fi 4 offers good cost-effectiveness — meeting mainstream IoT device bandwidth demands while maintaining low hardware cost and power consumption.

## 802.11n Core Features

### MIMO 1x1 and Spatial Streams

802.11n introduces MIMO (Multiple Input Multiple Output) technology, achieving spatial multiplexing through multiple antennas. This chip platform uses only a single spatial stream (1x1 MIMO) in Wi-Fi 4 mode, meaning one antenna for transmission and one for reception. While multi-spatial-stream peak rate enhancement is unavailable, MIMO still provides diversity gain, improving signal stability and coverage.

If the system is configured with multiple antennas, 2x2 or higher-order MIMO can be enabled in Wi-Fi 6 mode. Wi-Fi 4's 1x1 constraint makes it more suitable for power-sensitive battery-powered devices.

### Short GI (Short Guard Interval)

The guard interval is the time buffer between OFDM symbols, used to avoid inter-symbol interference. Standard GI is 800ns, while Short GI is shortened to 400ns, reducing each symbol's transmission time from 4μs to 3.6μs. Short GI can improve throughput by approximately 11%, but requires better channel conditions and is suitable for short-range, low-interference scenarios.

In the SDK, Short GI is controlled via the `bl_mod_params.sgi` parameter:

```c
// Enable Short GI
bl_mod_params.sgi = true;

// Disable Short GI (use standard 800ns GI)
bl_mod_params.sgi = false;
```

### 40MHz Bandwidth

802.11n supports bundling two 20MHz channels into a single 40MHz bandwidth, increasing the number of subcarriers from 52 to 108, thereby raising the single spatial stream rate from 72.2Mbps to 150Mbps. 40MHz bandwidth is only recommended on uncongested 2.4GHz channels (to avoid conflicts with adjacent 20MHz channels) and is more commonly used in the 5GHz band.

40MHz configuration is enabled via the `bl_mod_params.use_2040` parameter:

```c
// Enable 40MHz bandwidth support
bl_mod_params.use_2040 = true;
```

Note that 40MHz operation requires negotiation success with both AP and STA supporting it to take effect.

### MCS Modulation and Coding Scheme

The MCS (Modulation and Coding Scheme) index defines modulation type and code rate combinations in 802.11n. Wi-Fi 4 supports MCS 0 through MCS 15, with each index corresponding to a specific modulation order and code rate:

| MCS Index | Modulation | Code Rate | 40MHz Single Stream Rate |
|-----------|------------|-----------|--------------------------|
| MCS 0     | BPSK       | 1/2       | 15 Mbps                  |
| MCS 1     | QPSK       | 1/2       | 30 Mbps                  |
| MCS 2     | QPSK       | 3/4       | 45 Mbps                  |
| MCS 3     | 16-QAM     | 1/2       | 60 Mbps                  |
| MCS 4     | 16-QAM     | 3/4       | 90 Mbps                  |
| MCS 5     | 64-QAM     | 2/3       | 120 Mbps                 |
| MCS 6     | 64-QAM     | 3/4       | 135 Mbps                 |
| MCS 7     | 64-QAM     | 5/6       | 150 Mbps                 |
| MCS 8     | 256-QAM    | 3/4       | 180 Mbps (chip support required) |
| MCS 9     | 256-QAM    | 5/6       | 200 Mbps (chip support required) |

The default MCS mapping is configured via `bl_mod_params.mcs_map`. MCS 8 and MCS 9 rely on 256-QAM modulation and are only enabled in high-SNR environments.

## bl_wifi_driver Architecture

### LMAC Message Queue Overview

The Wi-Fi driver uses the LMAC (Lower MAC) architecture, dividing the protocol stack into Host (driver) side and Firmware side. The two sides communicate via message queues: the Host side sends request messages (REQ), and the Firmware side returns confirmation messages (CFM) or asynchronous indication messages (IND).

The message structure is defined in `lmac_msg.h`:

```c
struct lmac_msg {
    ke_msg_id_t     id;         // Message ID
    ke_task_id_t    dest_id;    // Destination task ID
    ke_task_id_t    src_id;     // Source task ID
    u32             param_len;  // Parameter length
    u32             param[];    // Parameter array (word-aligned)
};
```

The message ID is parsed by the macros `MSG_T(msg)` and `MSG_I(msg)`, which extract the message type and instance number respectively. The driver task ID is predefined as `DRV_TASK_ID (100)`.

### Key Message Types

#### MM_START_REQ / MM_START_CFM

MAC layer start request, used to initialize Wi-Fi firmware. Contains PHY configuration, timeout parameters, and local clock accuracy:

```c
struct mm_start_req {
    struct phy_cfg_tag phy_cfg;     // PHY config
    u32_l              uapsd_timeout; // UAPSD timeout (ms)
    u16_l              lp_clk_accuracy; // LP clock accuracy (ppm)
};
```

#### MM_SET_CHANNEL_REQ

Set operating channel and bandwidth type. Channel type definitions include 20MHz, 40MHz, 80MHz, etc.:

```c
struct mm_set_channel_req {
    u8_l    band;        // Band: 2.4GHz or 5GHz
    u8_l    type;        // Channel type: 20/40/80/160MHz
    u16_l   prim20_freq; // Primary 20MHz channel frequency (MHz)
    u16_l   center1_freq; // Center frequency 1
    u16_l   center2_freq; // Center frequency 2 (for 80+80)
    u8_l    index;       // RF index (primary or secondary)
    s8_l    tx_power;    // Max TX power (dBm)
};
```

#### MM_SET_PS_MODE_REQ

Power management mode switch. Parameter `new_state` can be `MM_PS_MODE_OFF`, `MM_PS_MODE_ON`, or `MM_PS_MODE_ON_DYN` (dynamic).

#### SCAN_START_REQ / SCANU_START_REQ

Initiate a network scan request, supporting multi-channel, multi-SSID passive or active scanning:

```c
struct scan_start_req {
    struct scan_chan_tag chan[SCAN_CHANNEL_MAX]; // Channel list
    struct mac_ssid      ssid[SCAN_SSID_MAX];    // SSID list
    struct mac_addr      bssid;                  // BSSID filter
    struct mac_addr      mac;                   // Source MAC for transmission
    u32_l                add_ies;               // Additional IEs pointer
    u16_l                add_ie_len;            // Additional IEs length
    u8_l                 vif_idx;               // VIF index
    u8_l                 chan_cnt;              // Channel count
    u8_l                 ssid_cnt;              // SSID count
    bool                 no_cck;                // Disable CCK rates
};
```

### Interface Types

The system supports multiple interface types, specified by the `type` field in the `mm_add_if_req` structure:

- `MM_STA`: Basic Service Set (ESS) Station interface, most common mode
- `MM_IBSS`: Independent Basic Service Set (Ad-Hoc) interface
- `MM_AP`: Access Point interface
- `MM_MESH_POINT`: Mesh node interface

## bl_mod_params_t Parameter Configuration

The `bl_mod_params` structure centrally manages Wi-Fi 4 feature switches and performance parameters, located in `bl_mod_params.h`:

```c
struct bl_mod_params {
    bool ht_on;           // HT (802.11n) enable
    bool vht_on;          // VHT (802.11ac) enable (not supported by this chip)
    int  mcs_map;         // MCS mapping configuration
    int  phy_cfg;         // PHY config index
    int  uapsd_timeout;   // UAPSD timeout (ms)
    bool sgi;             // Short GI enable
    bool sgi80;           // 80MHz Short GI enable
    bool use_2040;        // 40MHz bandwidth enable
    int  listen_itv;      // Listen interval
    bool listen_bcmc;     // Listen for broadcast/multicast frames
    int  lp_clk_ppm;      // LP clock accuracy (ppm)
    bool ps_on;           // Power management enable
    int  tx_lft;          // Transmit frame lifetime (TUs)
    int  amsdu_maxnb;     // A-MSDU max count
    int  uapsd_queues;    // UAPSD queue mask
};
```

### Power Configuration

TX power is dynamically adjusted via the `mm_set_power_req` message:

```c
struct mm_set_power_req {
    u8_l inst_nbr;  // Interface number
    s8_l power;     // TX power (dBm)
};
```

Typical values range from 0dBm to 20dBm, depending on hardware capabilities and regulatory limits.

### Rate Configuration

The basic rate set is configured via `mm_set_basic_rates_req`, used to control management frame and broadcast frame transmission rates:

```c
struct mm_set_basic_rates_req {
    u32_l rates;     // Basic rate mask (maps to bssBasicRateSet register)
    u8_l  inst_nbr;  // Interface number
    u8_l  band;      // Band
};
```

### Antenna Configuration

Antenna selection is done within the PHY configuration, supporting multi-path mapping and diversity. Antenna configuration is defined by the `phy_trd_cfg_tag` or `phy_karst_cfg_tag` structure, including RF path mapping and IQ compensation parameters.

## Wi-Fi 4 Power Saving Mechanisms

### APSD (Automatic Power Save Delivery)

U-APSD (Unscheduled Automatic Power Save Delivery) is the recommended power saving mechanism for 802.11n, allowing the AP to wake the STA via trigger frames to receive downlink traffic. U-APSD is particularly suitable for latency-sensitive applications such as VoIP and video streaming.

APSD configuration is controlled by the following parameters:

- `bl_mod_params.uapsd_timeout`: U-APSD timeout, determines how long the STA waits after no data interaction before returning to sleep
- `bl_mod_params.uapsd_queues`: AC queue mask enabling U-APSD (bit0=VO, bit1=VI, bit2=BK, bit3=BE)
- `bl_mod_params.ps_on`: Global power management switch

```c
// Configure U-APSD: enable automatic power saving for VO and VI queues
bl_mod_params.uapsd_queues = 0x03;  // VO(0x01) | VI(0x02)
bl_mod_params.uapsd_timeout = 300;  // Enter sleep after 300ms of no data
bl_mod_params.ps_on = true;
```

### Dynamic Power Management

The `MM_PS_MODE_ON_DYN` mode supports dynamic switching: the STA automatically transitions between active and sleep states based on traffic. When no data arrives, it enters sleep to save power; when traffic is detected, it quickly wakes up.

Listen Interval controls how often the STA wakes up to receive Beacons:

```c
struct mm_set_ps_options_req {
    u8_l  vif_index;           // VIF index
    u16_l listen_interval;     // Listen interval (Beacon periods, 0 means DTIM-based)
    bool_l dont_listen_bc_mc;  // Whether to ignore broadcast/multicast
};
```

Longer listen intervals reduce power consumption but may miss downlink broadcast/multicast data.

### Power Management State Indication

The Firmware notifies the Host of peer STA power state changes via the `mm_ps_change_ind` message:

```c
struct mm_ps_change_ind {
    u8_l sta_idx;     // Station index
    u8_l ps_state;    // Power state: 0=active, 1=sleep
};
```

## Relationship Between Wi-Fi 4 and Wi-Fi 6

Wi-Fi 6 (802.11ax) is implemented as a separate `wifi6` component in this platform's SDK, while the `wifi4` component serves as the foundational implementation layer of the entire wireless stack. Their relationship is reflected in the following aspects:

### Code Reuse

Wi-Fi 4's LMAC message queues, scanning mechanisms, and power management framework are directly reused by Wi-Fi 6. Wi-Fi 6 adds new features such as OFDMA, 1024-QAM, and BSS Coloring on top of this, but the underlying frame exchange and PHY configuration flow remain consistent with Wi-Fi 4.

### Negotiation Fallback

When a Wi-Fi 6 STA associates with an AP that only supports Wi-Fi 4, the system automatically negotiates down to 802.11n mode. Conversely, in high-density deployment environments, to accommodate legacy devices or reduce power consumption, a Wi-Fi 6 AP can be configured to only allow Wi-Fi 4 client associations.

### Parameter Inheritance

`bl_mod_params.ht_on` controls 802.11n functionality. In Wi-Fi 6 mode, `ht_on = true` should be maintained (because 802.11ax must be backward compatible with 802.11n). The `mcs_map` parameter also affects Wi-Fi 6's basic rate configuration.

### Coexistence Mechanism

Wi-Fi 4 and Wi-Fi 6 can coexist via Dual-Band Concurrent operation: one band operates in Wi-Fi 4 mode to connect legacy devices, while another band provides high-speed access via Wi-Fi 6. This requires RF hardware support for dual front-ends.

## Code Examples

### Wi-Fi 4 Mode Connection Example

The following code demonstrates how to configure and start a Wi-Fi 4 (802.11n) connection:

```c
#include "bl_wifi_driver.h"
#include "bl_mod_params.h"
#include "lmac_msg.h"

// Initialize Wi-Fi 4 parameters
void wifi4_connect_init(void)
{
    // Enable 802.11n, disable 802.11ac
    bl_mod_params.ht_on = true;
    bl_mod_params.vht_on = false;

    // Configure MCS mapping: allow MCS 0-7 (up to 64-QAM)
    bl_mod_params.mcs_map = 0xFFF2;  // MCS 0-7 supported, MCS 8-9 not supported

    // Enable Short GI
    bl_mod_params.sgi = true;

    // Disable 40MHz (use 20MHz channel for better compatibility)
    bl_mod_params.use_2040 = false;

    // Configure listen interval: wake every 3 Beacon periods
    bl_mod_params.listen_itv = 3;

    // Enable power management
    bl_mod_params.ps_on = true;

    // Configure U-APSD: enable voice and video queues
    bl_mod_params.uapsd_queues = 0x03;
    bl_mod_params.uapsd_timeout = 100;
}

// Connect to Wi-Fi 4 AP
int wifi4_sta_connect(const char *ssid, const char *psk)
{
    wifi4_connect_init();

    // Add Station interface
    struct mm_add_if_req add_if_req = {
        .type = MM_STA,
        .p2p = false,
    };
    // mac_addr should be populated with the actual MAC address
    // Send MM_ADD_IF_REQ message to LMAC

    // Configure channel (using 2.4GHz channel 6 as example)
    struct mm_set_channel_req chan_req = {
        .band = 0,              // 2.4GHz
        .type = 20,             // 20MHz bandwidth
        .prim20_freq = 2437,    // 2437 MHz
        .center1_freq = 2437,
        .tx_power = 18,         // 18 dBm
    };
    // Send MM_SET_CHANNEL_REQ message

    // Initiate scan
    struct scan_start_req scan_req = {
        .vif_idx = 0,
        .chan_cnt = 1,
        // Fill channel info
    };
    // Send SCAN_START_REQ message

    // After scan results return, invoke connection flow
    // Connection flow involves 802.11 authentication and association frame exchange

    return 0;
}
```

### 40MHz Bandwidth Configuration Example

The following code demonstrates how to configure Wi-Fi 4 for 40MHz bandwidth mode:

```c
void wifi4_enable_40MHz(void)
{
    // Enable 40MHz channel bandwidth
    bl_mod_params.use_2040 = true;

    // Configure primary channel and center frequency
    // Using 2.4GHz channel 6 (primary) + channel 10 (secondary) as example
    struct mm_set_channel_req chan_req = {
        .band = 0,                // 2.4GHz band
        .type = 40,               // 40MHz bandwidth
        .prim20_freq = 2437,      // Primary 20MHz channel: 2437 MHz (CH 6)
        .center1_freq = 2447,     // Center frequency: 2447 MHz
        .center2_freq = 0,        // Used for 80+80 mode
        .tx_power = 18,           // TX power
    };

    // Send MM_SET_CHANNEL_REQ to LMAC
    // Firmware will negotiate HT 40MHz operation
}

void wifi4_disable_40MHz(void)
{
    // Disable 40MHz, fall back to 20MHz
    bl_mod_params.use_2040 = false;

    // Reconfigure channel for 20MHz
    struct mm_set_channel_req chan_req = {
        .band = 0,
        .type = 20,
        .prim20_freq = 2437,
        .center1_freq = 2437,
        .tx_power = 18,
    };

    // Send MM_SET_CHANNEL_REQ
}
```

### Power Management Configuration Example

```c
void wifi4_power_save_config(void)
{
    // Enable global power management
    bl_mod_params.ps_on = true;

    // Configure listen interval: wake every 10 Beacon periods
    bl_mod_params.listen_itv = 10;

    // Ignore broadcast/multicast (save receive power)
    bl_mod_params.listen_bcmc = false;

    // Configure U-APSD
    bl_mod_params.uapsd_queues = 0x0F;  // Enable U-APSD for all queues
    bl_mod_params.uapsd_timeout = 200;  // 200ms timeout

    // Set LP clock accuracy (affects DTIM calculation)
    bl_mod_params.lp_clk_ppm = 100;  // 100 ppm

    // Send MM_SET_PS_MODE_REQ, enable dynamic power management
    struct mm_set_ps_mode_req ps_req = {
        .new_state = MM_PS_MODE_ON_DYN,
    };
    // Send message to LMAC
}
```

## Limitations and Notes

1. **40MHz in 2.4GHz band**: The 2.4GHz band has only 3 non-overlapping channels (1, 6, 11). 40MHz bandwidth occupies adjacent channels, so ensure the channel is interference-free in actual deployment.

2. **Short GI reliability**: Short GI is sensitive to multipath and may cause increased packet error rates in complex indoor environments. If the connection is unstable, disable Short GI.

3. **MCS negotiation**: The actual MCS index used is determined by capability set negotiation between AP and STA; the Host-side configuration is only a requested value.

4. **Power management and latency**: Enabling deep power saving introduces additional wake-up latency, which is detrimental to low-latency applications such as real-time voice or gaming.

5. **VHT parameters**: This chip's `vht_on` should always remain `false`, as the hardware does not support 802.11ac VHT.

## References

- IEEE Std 802.11n-2009: Amendment 5: Enhancements for Higher Throughput
- `lmac_msg.h`: LMAC message structures and enum definitions
- `bl_mod_params.h`: Wi-Fi driver parameter configuration structure
- `bl_platform.h`: Platform hardware abstraction layer definitions
