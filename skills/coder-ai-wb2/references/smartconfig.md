# SmartConfig / AirKiss Network Provisioning API Reference

> Source file: `components/network/smartconfig_airkiss/smartconfig.h`  
> SmartConfig is a Wi-Fi one-click provisioning protocol from Espressif/Ai-Thinker, and AirKiss is the provisioning protocol from WeChat. BL602 supports both methods to transmit SSID/password via broadcast packets.

---

## Overview

Provisioning flow:

```
Mobile APP (UDP broadcast) ──▶ BL602 listening on channels 1-13 ──▶ Parse SSID/password ──▶ Connect to hotspot
                              ↑
                         sniffer mode
```

**Provisioning principle**: The mobile APP sends broadcast packets containing encoded SSID/password on UDP port 9999, and BL602 captures and decodes the over-the-air packets in sniffer mode.

---

## Type Definitions

### `libwifi_frame` — Raw Frame Structure

```c
struct libwifi_frame {
    struct libwifi_frame_ctrl frame_control;  // Frame control
    uint16_t duration;
    uint8_t  addr1[6];   // BSSID / Destination
    uint8_t  addr2[6];   // Source
    uint8_t  addr3[6];   // BSSID / Filtering
    struct libwifi_seq_control seq_control;
} __attribute__((packed));
```

### `libwifi_frame_ctrl` — Frame Control Field

```c
struct libwifi_frame_ctrl {
    unsigned int version : 2;   // Protocol version
    unsigned int type : 2;      // Frame type
    unsigned int subtype : 4;   // Frame subtype
    struct libwifi_frame_ctrl_flags flags;
};
```

---

## Function API

### `wifi_smartconfig_v1_start`

Start SmartConfig v1 provisioning.

```c
int wifi_smartconfig_v1_start(void);
```

**Return value**: `0` success, others failure

> After calling, BL602 enters sniffer mode, listens on all channels, and waits for the mobile APP to send provisioning data.

---

### `wifi_smartconfig_v1_stop`

Stop SmartConfig provisioning.

```c
int wifi_smartconfig_v1_stop(void);
```

**Return value**: `0` success, others failure

> This function must be called after successful provisioning to restore normal Wi-Fi mode.

---

## Usage Example

```c
#include "smartconfig.h"

// Provisioning task
static void smartconfig_task(void *arg)
{
    printf("SmartConfig started, waiting for SSID...\r\n");

    // Start provisioning
    int ret = wifi_smartconfig_v1_start();
    if (ret != 0) {
        printf("SmartConfig start failed: %d\r\n", ret);
        vTaskDelete(NULL);
        return;
    }

    // Wait for provisioning success (usually triggered by Wi-Fi connection event)
    // In real projects, judge provisioning result in Wi-Fi connection callback

    // Stop provisioning
    wifi_smartconfig_v1_stop();
    printf("SmartConfig stopped\r\n");

    vTaskDelete(NULL);
}

void app_main(void)
{
    // System initialization...

    // Create provisioning task (high priority)
    xTaskCreate(smartconfig_task, "smartconfig", 4096, NULL, 5, NULL);
}
```

## Provisioning Steps (APP Side)

Mobile APP provisioning steps (for reference):

1. Mobile phone connects to target Wi-Fi (used for sending broadcast)
2. APP encodes SSID/password into UDP data packet
3. APP sends UDP broadcast packets on each channel (port 9999)
4. BL602 sniffer mode receives and decodes
5. BL602 connects to target hotspot
6. Report connection result (MQTT/TCP)

> **Note**: SmartConfig relies on plaintext broadcast, which has low security. For production environments, BLUFI (BLE encrypted channel) provisioning is recommended.
