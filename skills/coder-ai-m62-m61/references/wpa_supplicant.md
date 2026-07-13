# Wi-Fi WPA Supplicant (WPA2/WPA3) Documentation

Reference: `bouffalo_sdk/components/wireless/bl_wpa_supplicant/` (BL618/BL616)

---

## 1. Overview

The BL616/BL618 Wi-Fi stack uses a wpa_supplicant backend for secure station connectivity. This document covers initialization, WPA2-Personal/Enterprise, WPS, DPP (Wi-Fi Easy Connect), and RRM/WNM features.

Header files:
- `bl_supplicant/bl_wpa.h` - Core supplicant init/deinit
- `bl_supplicant/bl_wps.h` - Wi-Fi Protected Setup
- `bl_supplicant/esp_dpp.h` - DPP (Wi-Fi Easy Connect)
- `bl_supplicant/esp_wpa2.h` - WPA2-Enterprise (EAP)
- `bl_supplicant/esp_wnm.h` - Wireless Network Management
- `bl_supplicant/esp_rrm.h` - Radio Resource Management

---

## 2. Supplicant Initialization

```c
#include "bl_supplicant/bl_wpa.h"

int ret = bl_supplicant_init();
if (ret != 0) {
    // handle error
}

 // ... use Wi-Fi ...

bl_supplicant_deinit();
```

`bl_supplicant_init()` registers WPA callbacks with the Wi-Fi driver and initializes internal structures. Must be called after Wi-Fi driver is loaded but before station connect.

---

## 3. Station Connect/Disconnect (WPA2-Personal)

Standard PSK-based connection using `esp_wifi` API:

```c
#include "esp_wifi.h"

wifi_config_t wifi_config = {
    .sta = {
        .threshold = {
            .authmode = WIFI_AUTH_WPA2_PSK,
        },
        .pmf_cfg = {
            .capable = true,
            .required = false,
        },
    },
};
memcpy(wifi_config.sta.ssid, "MySSID", 6);
memcpy(wifi_config.sta.password, " passphrase", 9);
wifi_config.sta.ssid_len = 6;

ESP_ERROR_CHECK(esp_wifi_set_mode(WIFI_MODE_STA));
ESP_ERROR_CHECK(esp_wifi_set_config(WIFI_IF_STA, &wifi_config));
ESP_ERROR_CHECK(esp_wifi_start());
ESP_ERROR_CHECK(esp_wifi_connect());
```

For WPA3-Personal (SAE):

```c
wifi_config.sta.threshold.authmode = WIFI_AUTH_WPA3_PSK;
// SAE is automatically used if the AP advertises WPA3 and SAE is enabled in Kconfig
```

---

## 4. WPA2-Enterprise (EAP/TLS)

### 4.1 Enable Enterprise Authentication

```c
#include "esp_wpa2.h"
#include "esp_wifi.h"

ESP_ERROR_CHECK(esp_wifi_sta_wpa2_ent_enable());
```

### 4.2 Set Identity (for PEAP/TTLS)

```c
const unsigned char identity[] = "user@domain.com";
ESP_ERROR_CHECK(esp_wifi_sta_wpa2_ent_set_identity(identity, strlen(identity)));
```

### 4.3 Set Username

```c
const unsigned char username[] = "testuser";
ESP_ERROR_CHECK(esp_wifi_sta_wpa2_ent_set_username(username, strlen(username)));
```

### 4.4 Set Password

```c
const unsigned char password[] = "userpassword";
ESP_ERROR_CHECK(esp_wifi_sta_wpa2_ent_set_password(password, strlen(password)));
```

### 4.5 Set CA Certificate (for TLS/PEAP/TTLS)

```c
const unsigned char ca_cert[] = "-----BEGIN CERTIFICATE-----\n...";
ESP_ERROR_CHECK(esp_wifi_sta_wpa2_ent_set_ca_cert(ca_cert, strlen(ca_cert)));
```

### 4.6 Set Client Certificate and Key (for TLS-EAP)

```c
const unsigned char client_cert[] = "-----BEGIN CERTIFICATE-----\n...";
const unsigned char private_key[] = "-----BEGIN RSA PRIVATE KEY-----\n...";
const unsigned char *password = NULL; // or password for encrypted key

ESP_ERROR_CHECK(esp_wifi_sta_wpa2_ent_set_cert_key(
    client_cert, strlen(client_cert),
    private_key, strlen(private_key),
    password, password ? strlen(password) : 0
));
```

### 4.7 Set TTLS Phase2 Method

```c
// Options: ESP_EAP_TTLS_PHASE2_EAP, ESP_EAP_TTLS_PHASE2_MSCHAPV2,
//          ESP_EAP_TTLS_PHASE2_MSCHAP, ESP_EAP_TTLS_PHASE2_PAP, ESP_EAP_TTLS_PHASE2_CHAP
ESP_ERROR_CHECK(esp_wifi_sta_wpa2_ent_set_ttls_phase2_method(ESP_EAP_TTLS_PHASE2_MSCHAPV2));
```

### 4.8 Disable Certificate Time Check

```c
// Set true to disable certificate expiry validation
ESP_ERROR_CHECK(esp_wifi_sta_wpa2_ent_set_disable_time_check(true));
```

### 4.9 Clear Credentials

```c
esp_wifi_sta_wpa2_ent_clear_identity();
esp_wifi_sta_wpa2_ent_clear_username();
esp_wifi_sta_wpa2_ent_clear_password();
esp_wifi_sta_wpa2_ent_clear_ca_cert();
esp_wifi_sta_wpa2_ent_clear_cert_key();
esp_wifi_sta_wpa2_ent_clear_new_password();
```

### 4.10 Complete WPA2-Enterprise Flow

```c
// 1. Configure EAP credentials
esp_wifi_sta_wpa2_ent_set_identity(identity, strlen(identity));
esp_wifi_sta_wpa2_ent_set_username(username, strlen(username));
esp_wifi_sta_wpa2_ent_set_password(password, strlen(password));
esp_wifi_sta_wpa2_ent_set_ca_cert(ca_cert_pem, strlen(ca_cert_pem));

// 2. Enable enterprise auth
esp_wifi_sta_wpa2_ent_enable();

// 3. Connect to enterprise network
esp_wifi_sta_wps_disable(); // ensure WPS is off
esp_wifi_connect();
```

---

## 5. WPS (Wi-Fi Protected Setup)

### 5.1 WPS Events

```c
typedef enum {
    BL_WPS_EVENT_COMPLETE,       // WPS succeeded, credentials received
    BL_WPS_EVENT_PIN,            // PIN is needed
    BL_WPS_EVENT_FAILURE,        // WPS failed
    BL_WPS_EVENT_TIMEOUT,        // WPS timed out
    BL_WPS_EVENT_SESSION_OVERLAP, // Multiple PBC sessions overlap
    BL_WPS_EVENT_SCAN_ERROR,     // Scan error
} bl_wps_event_t;
```

### 5.2 WPS Configuration Structure

```c
typedef struct bl_wps_config {
    wps_type_t type;               // WPS_TYPE_PBC or WPS_TYPE_PIN
    wps_factory_information_t factory_info;  // Device info
    wps_event_callback_t event_cb;  // Event callback
    void *event_cb_arg;            // Callback argument
} bl_wps_config_t;

typedef enum wps_type {
    WPS_TYPE_DISABLE = 0,
    WPS_TYPE_PBC,      // Push Button
    WPS_TYPE_PIN,      // PIN code
    WPS_TYPE_MAX,
} wps_type_t;

typedef struct {
    char manufacturer[WPS_MAX_MANUFACTURER_LEN];
    char model_number[WPS_MAX_MODEL_NUMBER_LEN];
    char model_name[WPS_MAX_MODEL_NAME_LEN];
    char device_name[WPS_MAX_DEVICE_NAME_LEN];
} wps_factory_information_t;
```

### 5.3 WPS Credentials Structure

```c
typedef struct {
    uint8_t ssid[32];
    uint8_t ssid_len;
    uint8_t bssid[6];
    char passphrase[64];
} bl_wps_ap_credential_item_t;

typedef struct {
    uint8_t cnt;
    bl_wps_ap_credential_item_t creds[];
} bl_wps_ap_credential_t;
```

### 5.4 Start WPS-PBC

```c
#include "bl_supplicant/bl_wps.h"
#include "esp_wifi.h"

static void wps_event_handler(bl_wps_event_t event, void *payload, void *cb_arg)
{
    switch (event) {
    case BL_WPS_EVENT_COMPLETE:
        {
            bl_wps_ap_credential_t *creds = (bl_wps_ap_credential_t *)payload;
            printf("WPS succeeded! Got %d credential(s)\n", creds->cnt);
            for (int i = 0; i < creds->cnt; i++) {
                printf("  SSID: %.*s\n", creds->creds[i].ssid_len, creds->creds[i].ssid);
                printf("  Passphrase: %s\n", creds->creds[i].passphrase);
            }
            // Connect using received credentials
            wifi_config_t wifi_config = {0};
            memcpy(wifi_config.sta.ssid, creds->creds[0].ssid, creds->creds[0].ssid_len);
            memcpy(wifi_config.sta.password, creds->creds[0].passphrase, strlen(creds->creds[0].passphrase));
            esp_wifi_set_config(WIFI_IF_STA, &wifi_config);
            esp_wifi_connect();
        }
        break;
    case BL_WPS_EVENT_TIMEOUT:
        printf("WPS timed out\n");
        break;
    case BL_WPS_EVENT_FAILURE:
        printf("WPS failed\n");
        break;
    case BL_WPS_EVENT_SESSION_OVERLAP:
        printf("WPS session overlap detected\n");
        break;
    default:
        break;
    }
}

void start_wps_pbc(void)
{
    bl_wps_config_t config = {
        .type = WPS_TYPE_PBC,
        .factory_info = {
            .manufacturer = "MyCompany",
            .model_number = "Model123",
            .model_name = "MyDevice",
            .device_name = "BL616-Device",
        },
        .event_cb = wps_event_handler,
        .event_cb_arg = NULL,
    };

    esp_wifi_sta_wpa2_ent_disable(); // Disable enterprise for WPS
    bl_wifi_wps_start(&config);
}
```

### 5.5 Start WPS-PIN

```c
void start_wps_pin(void)
{
    bl_wps_config_t config = {
        .type = WPS_TYPE_PIN,
        .factory_info = {
            .manufacturer = "MyCompany",
            .model_number = "Model123",
            .model_name = "MyDevice",
            .device_name = "BL616-Device",
        },
        .event_cb = wps_event_handler,
        .event_cb_arg = NULL,
    };

    bl_wifi_wps_start(&config);
    // When BL_WPS_EVENT_PIN is received, display the PIN to user
}
```

---

## 6. DPP (Wi-Fi Easy Connect)

### 6.1 DPP Events

```c
typedef enum {
    ESP_SUPP_DPP_URI_READY,   // URI ready for QR code display
    ESP_SUPP_DPP_CFG_RECVD,   // Configuration received via DPP
    ESP_SUPP_DPP_FAIL,        // DPP failed
} esp_supp_dpp_event_t;
```

### 6.2 DPP Bootstrap Types

```c
typedef enum dpp_bootstrap_type {
    DPP_BOOTSTRAP_QR_CODE,  // QR Code method
    DPP_BOOTSTRAP_PKEX,     // Proof of Knowledge (PKEX)
    DPP_BOOTSTRAP_NFC_URI,  // NFC URI
} esp_supp_dpp_bootstrap_t;
```

### 6.3 Initialize DPP

```c
#include "esp_dpp.h"

static void dpp_event_handler(esp_supp_dpp_event_t evt, void *data)
{
    switch (evt) {
    case ESP_SUPP_DPP_URI_READY:
        {
            char *uri = (char *)data;
            printf("DPP URI ready: %s\n", uri);
            // Display QR code using the URI
        }
        break;
    case ESP_SUPP_DPP_CFG_RECVD:
        {
            // Configuration received - data contains station credentials
            wifi_config_t *wifi_config = (wifi_config_t *)data;
            printf("DPP config received for SSID: %s\n", wifi_config->sta.ssid);
            // Save and connect
            esp_wifi_set_config(WIFI_IF_STA, wifi_config);
            esp_wifi_connect();
        }
        break;
    case ESP_SUPP_DPP_FAIL:
        printf("DPP failed\n");
        break;
    }
}

void dpp_init(void)
{
    esp_supp_dpp_init(dpp_event_handler);
}
```

### 6.4 Generate DPP Bootstrap (as Enrollee)

```c
// Generate bootstrap info on channels 1, 6, 11
esp_err_t err = esp_supp_dpp_bootstrap_gen("1,6,11", DPP_BOOTSTRAP_QR_CODE, NULL, "BL616-Device");
if (err != ESP_OK) {
    printf("DPP bootstrap gen failed: %d\n", err);
    return;
}
```

### 6.5 Start DPP Listening

```c
// Start listening for DPP configurator
err = esp_supp_dpp_start_listen();
if (err != ESP_OK) {
    printf("DPP listen start failed: %d\n", err);
    return;
}

// User scans QR code with DPP Configurator app
// When ESP_SUPP_DPP_CFG_RECVD is received, connection proceeds
```

### 6.6 Stop DPP Listening

```c
esp_supp_dpp_stop_listen();
```

### 6.7 Deinitialize DPP

```c
esp_supp_dpp_deinit();
```

---

## 7. RRM (Radio Resource Management)

### 7.1 Neighbor Report Callback

```c
#include "esp_rrm.h"

static void neighbor_rep_cb(void *ctx, const uint8_t *report, size_t report_len)
{
    printf("Neighbor report received, len=%d\n", report_len);
    // Parse the report (TLV format)
    for (size_t i = 0; i < report_len; ) {
        uint8_t id = report[i];
        uint8_t len = report[i + 1];
        printf("  Element ID: %d, Len: %d\n", id, len);
        i += 2 + len;
    }
}
```

### 7.2 Send Neighbor Report Request

```c
int ret = esp_rfm_send_neighbor_rep_request(neighbor_rep_cb, NULL);
if (ret != 0) {
    printf("Failed to send neighbor report request: %d\n", ret);
}
```

---

## 8. WNM (Wireless Network Management)

### 8.1 BTM Query Reasons

```c
enum btm_query_reason {
    REASON_UNSPECIFIED = 0,
    REASON_FRAME_LOSS = 1,
    REASON_DELAY = 2,
    REASON_QOS_CAPACITY = 3,
    REASON_FIRST_ASSOC = 4,
    REASON_LOAD_BALALNCE = 5,
    REASON_BETTER_AP = 6,
    REASON_CURRENT_DEAUTH = 7,
};
```

### 8.2 Send BSS Transition Query

```c
#include "esp_wnm.h"

// Query AP for BSS transition candidates
int ret = esp_wnm_send_bss_transition_mgmt_query(
    REASON_BETTER_AP,  // query reason
    NULL,              // btm_candidates (NULL to use scan results)
    1                  // cand_list: include candidates from scan cache
);
if (ret != 0) {
    printf("BTM query failed: %d\n", ret);
}
```

---

## 9. Complete Usage Example

```c
#include "esp_wifi.h"
#include "esp_wpa2.h"
#include "bl_supplicant/bl_wpa.h"
#include "bl_supplicant/bl_wps.h"
#include "esp_dpp.h"
#include "esp_wnm.h"
#include "esp_rrm.h"

void wifi_app_init(void)
{
    // 1. Initialize Wi-Fi in station mode
    wifi_init_config_t cfg = WIFI_INIT_CONFIG_DEFAULT();
    esp_wifi_init(&cfg);
    esp_wifi_set_mode(WIFI_MODE_STA);

    // 2. Initialize WPA supplicant
    bl_supplicant_init();

    // 3. Connect (WPA2-PSK example)
    wifi_config_t sta_cfg = {
        .sta = {
            .threshold.authmode = WIFI_AUTH_WPA2_PSK,
        },
    };
    memcpy(sta_cfg.sta.ssid, "MyNetwork", 9);
    memcpy(sta_cfg.sta.password, "MyPassword", 10);
    esp_wifi_set_config(WIFI_IF_STA, &sta_cfg);
    esp_wifi_start();
    esp_wifi_connect();
}
```

---

## 10. API Summary

| Function | Header | Description |
|----------|--------|-------------|
| `bl_supplicant_init()` | bl_wpa.h | Initialize WPA supplicant |
| `bl_supplicant_deinit()` | bl_wpa.h | Deinitialize WPA supplicant |
| `esp_wifi_sta_wpa2_ent_enable()` | esp_wpa2.h | Enable WPA2-Enterprise |
| `esp_wifi_sta_wpa2_ent_disable()` | esp_wpa2.h | Disable WPA2-Enterprise |
| `esp_wifi_sta_wpa2_ent_set_identity()` | esp_wpa2.h | Set EAP identity |
| `esp_wifi_sta_wpa2_ent_set_username()` | esp_wpa2.h | Set EAP username |
| `esp_wifi_sta_wpa2_ent_set_password()` | esp_wpa2.h | Set EAP password |
| `esp_wifi_sta_wpa2_ent_set_ca_cert()` | esp_wpa2.h | Set CA certificate |
| `esp_wifi_sta_wpa2_ent_set_cert_key()` | esp_wpa2.h | Set client cert + key |
| `esp_wifi_sta_wpa2_ent_set_ttls_phase2_method()` | esp_wpa2.h | Set TTLS phase2 type |
| `bl_wifi_wps_start()` | bl_wps.h | Start WPS (PBC or PIN) |
| `esp_supp_dpp_init()` | esp_dpp.h | Initialize DPP |
| `esp_supp_dpp_bootstrap_gen()` | esp_dpp.h | Generate DPP bootstrap URI |
| `esp_supp_dpp_start_listen()` | esp_dpp.h | Start DPP listening |
| `esp_supp_dpp_stop_listen()` | esp_dpp.h | Stop DPP listening |
| `esp_supp_dpp_deinit()` | esp_dpp.h | Deinitialize DPP |
| `esp_rrm_send_neighbor_rep_request()` | esp_rrm.h | Request neighbor report |
| `esp_wnm_send_bss_transition_mgmt_query()` | esp_wnm.h | Send BSS transition query |
