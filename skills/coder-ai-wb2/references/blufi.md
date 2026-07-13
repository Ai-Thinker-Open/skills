# BLUFI Provisioning API Reference

> Source file: `components/network/blufi/blufi_api.h`  
> BLUFI is a Wi-Fi provisioning and control protocol implemented by Ai-Thinker based on BLE channel. The mobile app sends SSID/password via BLE, and BL602 receives and automatically connects to the specified hotspot.

---

## Overview

BLUFI provisioning flow:

```
Mobile App (BLE) ──▶ BL602 (BLUFI) ──▶ Connect to specified Wi-Fi hotspot
                         │
                         ├── Parse SSID/password
                         ├── Configure AP mode (optional)
                         ├── Connect to Wi-Fi
                         └── Report connection result
```

**Event types**:

| Event | Description |
|-------|-------------|
| `AXK_BLUFI_EVENT_INIT_FINISH` | BLUFI initialization complete |
| `AXK_BLUFI_EVENT_BLE_CONNECT` | Mobile BLE connection success |
| `AXK_BLUFI_EVENT_BLE_DISCONNECT` | Mobile BLE disconnected |
| `AXK_BLUFI_EVENT_RECV_STA_SSID` | Received STA SSID |
| `AXK_BLUFI_EVENT_RECV_STA_PASSWD` | Received STA password |
| `AXK_BLUFI_EVENT_REQ_CONNECT_TO_AP` | Request to connect to hotspot |
| `AXK_BLUFI_EVENT_GET_WIFI_STATUS` | Query Wi-Fi status |
| `AXK_BLUFI_EVENT_RECV_SOFTAP_SSID` | Received AP SSID |
| `AXK_BLUFI_EVENT_RECV_CUSTOM_DATA` | Received custom data |

---

## Type Definitions

### `_blufi_cb_event_t` — BLUFI Event Types

```c
typedef enum {
    AXK_BLUFI_EVENT_INIT_FINISH = 0,
    AXK_BLUFI_EVENT_DEINIT_FINISH,
    AXK_BLUFI_EVENT_BLE_CONNECT,
    AXK_BLUFI_EVENT_BLE_DISCONNECT,
    AXK_BLUFI_EVENT_SET_WIFI_OPMODE,
    AXK_BLUFI_EVENT_REQ_CONNECT_TO_AP,
    AXK_BLUFI_EVENT_REQ_DISCONNECT_FROM_AP,
    AXK_BLUFI_EVENT_GET_WIFI_STATUS,
    AXK_BLUFI_EVENT_RECV_STA_BSSID,
    AXK_BLUFI_EVENT_RECV_STA_SSID,
    AXK_BLUFI_EVENT_RECV_STA_PASSWD,
    AXK_BLUFI_EVENT_RECV_SOFTAP_SSID,
    AXK_BLUFI_EVENT_RECV_SOFTAP_PASSWD,
    AXK_BLUFI_EVENT_RECV_CUSTOM_DATA,
    // ... more events
} _blufi_cb_event_t;
```

### `_blufi_callbacks_t` — BLUFI Callback Structure

```c
typedef struct {
    _blufi_event_cb_t             event_cb;             // Event callback
    _blufi_negotiate_data_handler_t negotiate_data_handler; // Key negotiation
    _blufi_encrypt_func_t         encrypt_func;         // Encryption function
    _blufi_decrypt_func_t         decrypt_func;         // Decryption function
    _blufi_checksum_func_t        checksum_func;        // Checksum function
} _blufi_callbacks_t;
```

---

## Function API

### `axk_blufi_register_callbacks`

Register BLUFI callback functions.

```c
int axk_blufi_register_callbacks(_blufi_callbacks_t *callbacks);
```

| Parameter | Description |
|-----------|-------------|
| `callbacks` | Callback function structure pointer |

---

### `axk_blufi_profile_init`

Initialize BLUFI protocol layer.

```c
int axk_blufi_profile_init(void);
```

---

### `axk_blufi_profile_deinit`

Deinitialize BLUFI.

```c
int axk_blufi_profile_deinit(void);
```

---

### `axk_blufi_send_wifi_conn_report`

Report Wi-Fi connection status to mobile.

```c
int axk_blufi_send_wifi_conn_report(wifi_mode_t opmode,
                                     axk_blufi_sta_conn_state_t sta_conn_state,
                                     uint8_t softap_conn_num,
                                     axk_blufi_extra_info_t *extra_info);
```

| Parameter | Description |
|-----------|-------------|
| `opmode` | Wi-Fi mode (STA/AP) |
| `sta_conn_state` | Connection state (`_BLUFI_STA_CONN_SUCCESS` / `_BLUFI_STA_CONN_FAIL`) |
| `softap_conn_num` | Number of connected stations in AP mode |
| `extra_info` | Extra information (SSID, etc.) |

---

### `axk_blufi_send_wifi_list`

Send Wi-Fi list to mobile.

```c
int axk_blufi_send_wifi_list(uint16_t apCount, _blufi_ap_record_t *list);
```

---

### `axk_blufi_send_error_info`

Report BLUFI error information.

```c
int axk_blufi_send_error_info(_blufi_error_state_t state);
```

---

### `axk_blufi_send_custom_data`

Send custom data to mobile.

```c
int axk_blufi_send_custom_data(uint8_t *data, uint32_t data_len);
```

---

## Usage Example

```c
#include "blufi_api.h"

static char s_sta_ssid[32];
static char s_sta_passwd[64];

// BLUFI event callback
static void blufi_event_cb(_blufi_cb_event_t event, _blufi_cb_param_t *param)
{
    switch (event) {
    case AXK_BLUFI_EVENT_INIT_FINISH:
        printf("BLUFI init done\r\n");
        break;

    case AXK_BLUFI_EVENT_BLE_CONNECT:
        printf("Phone BLE connected\r\n");
        break;

    case AXK_BLUFI_EVENT_BLE_DISCONNECT:
        printf("Phone BLE disconnected\r\n");
        break;

    case AXK_BLUFI_EVENT_RECV_STA_SSID:
        memcpy(s_sta_ssid, param->sta_ssid.ssid, param->sta_ssid.ssid_len);
        s_sta_ssid[param->sta_ssid.ssid_len] = '\0';
        printf("STA SSID: %s\r\n", s_sta_ssid);
        break;

    case AXK_BLUFI_EVENT_RECV_STA_PASSWD:
        memcpy(s_sta_passwd, param->sta_passwd.passwd, param->sta_passwd.passwd_len);
        s_sta_passwd[param->sta_passwd.passwd_len] = '\0';
        printf("STA PASSWD received\r\n");
        break;

    case AXK_BLUFI_EVENT_REQ_CONNECT_TO_AP:
        printf("Connecting to AP: %s\r\n", s_sta_ssid);
        // Connect to Wi-Fi using SSID/password received via BLUFI
        wifi_sta_connect(s_sta_ssid, s_sta_passwd);
        // Report connection result
        axk_blufi_send_wifi_conn_report(WIFI_MODE_STA,
                                         _BLUFI_STA_CONN_SUCCESS,
                                         0, NULL);
        break;

    case AXK_BLUFI_EVENT_GET_WIFI_STATUS:
        // Report current Wi-Fi status
        axk_blufi_send_wifi_conn_report(WIFI_MODE_STA,
                                         _BLUFI_STA_CONN_SUCCESS,
                                         0, NULL);
        break;

    case AXK_BLUFI_EVENT_RECV_CUSTOM_DATA:
        printf("Custom data: %.*s\r\n",
               param->custom_data.data_len,
               param->custom_data.data);
        break;
    }
}

// Encryption/decryption/checksum callbacks (can use default implementations)
static void blufi_negotiate_data_handler(uint8_t *data, int len,
                                          uint8_t **output, int *out_len,
                                          bool *need_free)
{
    // Default implementation
    *need_free = false;
}

static int blufi_encrypt(uint8_t iv8, uint8_t *crypt_data, int crypt_len)
{
    return crypt_len; // No encryption by default
}

static int blufi_decrypt(uint8_t iv8, uint8_t *crypt_data, int crypt_len)
{
    return crypt_len; // No decryption by default
}

static uint16_t blufi_checksum(uint8_t iv8, uint8_t *data, int len)
{
    return 0; // Default checksum
}

void blufi_app_init(void)
{
    _blufi_callbacks_t callbacks = {
        .event_cb = blufi_event_cb,
        .negotiate_data_handler = blufi_negotiate_data_handler,
        .encrypt_func = blufi_encrypt,
        .decrypt_func = blufi_decrypt,
        .checksum_func = blufi_checksum,
    };

    axk_blufi_register_callbacks(&callbacks);
    axk_blufi_profile_init();
    printf("BLUFI initialized\r\n");
}
```
