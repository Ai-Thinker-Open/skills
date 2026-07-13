# BLE Controller Documentation (BL616/BL618)

This document covers the BLE Controller API for BL616/BL618 chips using the bouffalo_sdk.

## Table of Contents
- [Header Files](#header-files)
- [Controller Initialization](#controller-initialization)
- [Advertising (Beacon Only Mode)](#advertising-beacon-only-mode)
- [GAP Connection/Disconnection](#gap-connectiondisconnection)
- [GATT Server](#gatt-server)
- [Notifications and Indications](#notifications-and-indications)
- [Working Code Examples](#working-code-examples)

---

## Header Files

```c
// BLE Controller (BL616/BL618)
#include "btble_lib_api.h"     // Main BLE controller API
#include "btble_adv_api.h"     // Advertising API (beacon mode)
#include "hci_onchip.h"        // HCI interface

// BLE Host Stack (for full GATT/GAP)
#include "bluetooth.h"
#include "conn.h"
#include "gatt.h"
#include "gap.h"
```

---

## Controller Initialization

### btble_controller_init

Initializes the BLE controller task.

```c
void btble_controller_init(uint8_t task_priority);
```

**Parameters:**
- `task_priority` - FreeRTOS task priority (typically `configMAX_PRIORITIES - 1`)

**Example:**
```c
// Initialize BLE controller
btble_controller_init(configMAX_PRIORITIES - 1);
```

### Resource Configuration (Optional)

For dynamic resource configuration (before `btble_controller_init`):

```c
struct btblecontroller_resource_conf {
    uint32_t em_size;         // EM area size
    uint8_t ble_observer;     // 1: allocate observer resource
    uint8_t ble_central;      // 1: allocate central resource
    uint8_t ble_ext_adv;      // 1: allocate extended adv resource
    uint8_t ble_activity_max;  // Max activities
    uint8_t ble_conn_max;     // Max BLE links
    uint8_t ble_ral_max;      // Max devices in resolving list
    uint8_t ble_rx_desc_nb;   // RX descriptors
    uint8_t ble_acl_buf_nb_tx;// TX ACL buffers
};

// Configure resources before init
void btble_controller_resource_config(struct btblecontroller_resource_conf *conf);

// Set custom task stack size (default: 2K for BLE-only, 4K for BT/BLE)
void btble_controller_set_task_stack_size(uint16_t stack_size);
```

### Controller State Management

```c
// Get controller state
uint8_t btble_controller_get_state();
// Returns: BTBLE_IN_ACTIVE_STATE (0), BTBLE_IN_SLEEP_STATE (1), BTBLE_IN_WAKEUP_ONGOING_STATE (2)

// Sleep control
int32_t btble_controller_sleep(int32_t max_sleep_cycles);
void btble_controller_sleep_restore();

// Deinitialize
void btble_controller_deinit(void);
```

---

## Advertising (Beacon Only Mode)

Requires `CONFIG_BLE_BEACON_ONLY=y` in Kconfig.

### Advertising API

```c
// Initialize advertising subsystem (after btble_controller_init)
int btble_adv_init(void);

// Deinitialize advertising
void btble_adv_deinit(void);

// Set advertising parameters
int btble_adv_set_parameter(struct btble_adv_params *params);

// Set advertising data (max 31 bytes)
int btble_adv_set_data(uint8_t *data, uint8_t len);

// Set scan response data (max 31 bytes)
int btble_adv_set_scan_rsp_data(uint8_t *data, uint8_t len);

// Start advertising
int btble_adv_start(void);

// Stop advertising
int btble_adv_stop(void);

// Update data while advertising is active
int btble_adv_update_data(uint8_t *data, uint8_t len);
int btble_adv_update_scan_rsp_data(uint8_t *data, uint8_t len);

// Check if advertising is active
int btble_adv_is_active(void);

// Set random address
int btble_adv_set_random_addr(uint8_t *random_addr);

// Get public BD address
int btble_adv_get_public_addr(uint8_t *addr);
```

### Advertising Parameters Structure

```c
struct btble_adv_params {
    uint16_t adv_interval_min;     // Min interval (0.625ms units)
    uint16_t adv_interval_max;     // Max interval (0.625ms units)
    uint8_t  adv_type;             // Advertising type
    uint8_t  own_addr_type;        // Own address type
    uint8_t  peer_addr_type;       // Peer address type (directed adv)
    uint8_t  peer_addr[6];        // Peer address
    uint8_t  adv_channel_map;     // Channel map
    uint8_t  adv_filter_policy;    // Filter policy
};
```

### Advertising Type Definitions

```c
#define BTBLE_ADV_TYPE_CONNECTABLE_UNDIRECTED     0x00  // ADV_IND
#define BTBLE_ADV_TYPE_CONNECTABLE_DIRECTED        0x01  // ADV_DIRECT_IND
#define BTBLE_ADV_TYPE_SCANNABLE_UNDIRECTED       0x02  // ADV_SCAN_IND
#define BTBLE_ADV_TYPE_NON_CONNECTABLE_UNDIRECTED 0x03  // ADV_NONCONN_IND (Beacon)
```

### Address Types

```c
#define BTBLE_ADDR_TYPE_PUBLIC      0x00
#define BTBLE_ADDR_TYPE_RANDOM      0x01
#define BTBLE_ADDR_TYPE_RPA_OR_RANDOM 0x02
#define BTBLE_ADDR_TYPE_RPA_OR_PUBLIC 0x03
```

### Channel Map

```c
#define BTBLE_ADV_CHANNEL_37       0x01
#define BTBLE_ADV_CHANNEL_38       0x02
#define BTBLE_ADV_CHANNEL_39       0x04
#define BTBLE_ADV_CHANNEL_ALL      0x07
```

### Filter Policy

```c
#define BTBLE_ADV_FILTER_ALLOW_ALL             0x00
#define BTBLE_ADV_FILTER_WHITE_LIST_SCAN        0x01
#define BTBLE_ADV_FILTER_WHITE_LIST_CONN        0x02
#define BTBLE_ADV_FILTER_WHITE_LIST_ALL         0x03
```

---

## GAP Connection/Disconnection

For full GAP operations, use the blestack host API.

### Connection Callbacks

```c
static void ble_connected(struct bt_conn *conn, u8_t err)
{
    if (err || conn->type != BT_CONN_TYPE_LE) {
        return;
    }
    printf("Connected\n");
}

static void ble_disconnected(struct bt_conn *conn, u8_t reason)
{
    if (conn->type != BT_CONN_TYPE_LE) {
        return;
    }
    printf("Disconnected: reason %u\n", reason);
    
    // Restart advertising
    set_adv_enable(true);
}

static struct bt_conn_cb ble_conn_callbacks = {
    .connected    = ble_connected,
    .disconnected = ble_disconnected,
};

// Register callbacks
bt_conn_cb_register(&ble_conn_callbacks);
```

### Start Advertising (Peripheral)

```c
static void ble_start_adv(void)
{
    struct bt_le_adv_param param;
    int err;
    struct bt_data adv_data[1] = {
        BT_DATA_BYTES(BT_DATA_FLAGS, BT_LE_AD_NO_BREDR | BT_LE_AD_GENERAL)
    };
    struct bt_data adv_rsp[1] = {
        BT_DATA_BYTES(BT_DATA_MANUFACTURER_DATA, "BL616")
    };

    memset(&param, 0, sizeof(param));
    param.interval_min = BT_GAP_ADV_FAST_INT_MIN_2;
    param.interval_max = BT_GAP_ADV_FAST_INT_MAX_2;
    param.options = (BT_LE_ADV_OPT_CONNECTABLE | BT_LE_ADV_OPT_USE_NAME | BT_LE_ADV_OPT_ONE_TIME);

    err = bt_le_adv_start(&param, adv_data, ARRAY_SIZE(adv_data), 
                          adv_rsp, ARRAY_SIZE(adv_rsp));
    if (err) {
        printf("Failed to start advertising (err %d)\n", err);
    }
}
```

### Start Scanning (Central)

```c
static bool data_cb(struct bt_data *data, void *user_data)
{
    char *name = user_data;
    if (data->type == BT_DATA_NAME_SHORTENED || data->type == BT_DATA_NAME_COMPLETE) {
        memcpy(name, data->data, data->data_len);
        return false;
    }
    return true;
}

static void device_found(const bt_addr_le_t *addr, s8_t rssi, u8_t evtype,
                        struct net_buf_simple *buf)
{
    char name[30] = {0};
    bt_data_parse(buf, data_cb, name);
    
    if (!strcmp(name, "TargetDevice")) {
        // Stop scan
        bt_le_scan_stop();
        
        // Connect
        struct bt_le_conn_param param = {
            .interval_min = BT_GAP_INIT_CONN_INT_MIN,
            .interval_max = BT_GAP_INIT_CONN_INT_MAX,
            .latency = 0,
            .timeout = 400,
        };
        bt_conn_create_le(addr, &param);
    }
}

static void ble_start_scan(void)
{
    struct bt_le_scan_param scan_param = {
        .type = BT_HCI_LE_SCAN_ACTIVE,
        .filter_dup = BT_HCI_LE_SCAN_FILTER_DUP_DISABLE,
        .interval = BT_GAP_SCAN_FAST_INTERVAL,
        .window = BT_GAP_SCAN_FAST_WINDOW,
    };

    bt_le_scan_start(&scan_param, device_found);
}
```

### Disconnect

```c
// Get connection destination address
const bt_addr_le_t *dst = bt_conn_get_dst(conn);

// Disconnect
int bt_conn_disconnect(struct bt_conn *conn, uint8_t reason);

// Or disconnect all connections
void bt_conn_cleanup_all(void);
```

---

## GATT Server

### GATT Attributes

```c
// GATT Service Declaration
BT_GATT_SERVICE_DEFINE(service_name, attributes...);

// Example: Custom Service
static const struct bt_uuid_128 my_service_uuid = BT_UUID_INIT_128(
    0x01, 0x12, 0x23, 0x34, 0x45, 0x56, 0x67, 0x78,
    0x89, 0x9A, 0xAB, 0xBC, 0xCD, 0xDE, 0xEF, 0xF0
);

static int my_read_callback(struct bt_conn *conn,
                           const struct bt_gatt_attr *attr,
                           void *buf, u16_t len, u16_t offset)
{
    const char *data = "Hello BLE";
    return bt_gatt_attr_read(conn, attr, buf, len, offset, data, strlen(data));
}

static void my_write_callback(struct bt_conn *conn,
                              const struct bt_gatt_attr *attr,
                              const void *buf, u16_t len,
                              u16_t offset, u8_t flags)
{
    printf("Received: %.*s\n", len, (char *)buf);
}

static struct bt_gatt_attr gatt_attrs[] = {
    // Service Declaration
    BT_GATT_PRIMARY_SERVICE(&my_service_uuid),
    
    // Characteristic Declaration
    BT_GATT_CHARACTERISTIC(&my_service_uuid,
                          BT_GATT_CHRC_READ | BT_GATT_CHRC_NOTIFY,
                          BT_GATT_PERM_READ,
                          my_read_callback, NULL, NULL),
    
    // Client Characteristic Configuration Descriptor (CCCD)
    BT_GATT_CCC(NULL, BT_GATT_PERM_READ | BT_GATT_PERM_WRITE),
};

BT_GATT_SERVICE_DEFINE(my_service, gatt_attrs);
```

### GATT Permission Flags

```c
#define BT_GATT_PERM_NONE           0
#define BT_GATT_PERM_READ           BIT(0)
#define BT_GATT_PERM_WRITE          BIT(1)
#define BT_GATT_PERM_READ_ENCRYPT   BIT(2)
#define BT_GATT_PERM_WRITE_ENCRYPT  BIT(3)
#define BT_GATT_PERM_READ_AUTHEN    BIT(4)
#define BT_GATT_PERM_WRITE_AUTHEN   BIT(5)
#define BT_GATT_PERM_PREPARE_WRITE  BIT(6)
#define BT_GATT_PERM_READ_LESC      BIT(7)
#define BT_GATT_PERM_WRITE_LESC     BIT(8)
```

### GATT Characteristic Properties

```c
#define BT_GATT_CHRC_BROADCAST              BIT(0)
#define BT_GATT_CHRC_READ                   BIT(1)
#define BT_GATT_CHRC_WRITE                  BIT(2)
#define BT_GATT_CHRC_WRITE_WITHOUT_RESP     BIT(3)
#define BT_GATT_CHRC_NOTIFY                 BIT(4)
#define BT_GATT_CHRC_INDICATE              BIT(5)
#define BT_GATT_CHRC_AUTH                   BIT(6)
#define BT_GATT_CHRC_EXT_PROP               BIT(7)
```

---

## Notifications and Indications

### Send Notification

```c
// Notify connected peer
int bt_gatt_notify(struct bt_conn *conn,
                   const struct bt_gatt_attr *attr,
                   const void *data, u16_t len);

// Example: Send notification
static const struct bt_gatt_attr *attr = &gatt_attrs[2]; // Characteristic
uint8_t notify_data[] = {0x01, 0x02, 0x03, 0x04};
bt_gatt_notify(conn, attr, notify_data, sizeof(notify_data));
```

### Send Indication

```c
// Send indication (requires acknowledgment)
int bt_gatt_indicate(struct bt_conn *conn,
                     struct bt_gatt_attr *attr,
                     const void *data, u16_t len);
```

### Subscribe to Notifications

```c
static u8_t notify_func(struct bt_conn *conn,
                       struct bt_gatt_subscribe_params *params,
                       const void *data, u16_t length)
{
    if (!params->value) {
        printf("Unsubscribed\n");
        return BT_GATT_ITER_STOP;
    }
    printf("Received notification: %.*s\n", length, (char *)data);
    return BT_GATT_ITER_CONTINUE;
}

// Subscribe
struct bt_gatt_subscribe_params subscribe_params = {
    .ccc_handle = ccc_handle,    // Handle of CCCD
    .value = BT_GATT_CCC_NOTIFY,
    .value_handle = char_handle, // Characteristic value handle
    .notify = notify_func,
};

int err = bt_gatt_subscribe(conn, &subscribe_params);
if (err) {
    printf("Subscribe failed (err %d)\n", err);
}
```

### CCCD Values

```c
#define BT_GATT_CCC_NOTIFY     0x0001
#define BT_GATT_CCC_INDICATE   0x0002
```

### GATT Discovery

```c
static struct bt_gatt_discover_params discover_params;

static u8_t discover_func(struct bt_conn *conn,
                          const struct bt_gatt_attr *attr,
                          struct bt_gatt_discover_params *params)
{
    if (!attr) {
        printf("Discovery complete\n");
        return BT_GATT_ITER_STOP;
    }
    
    // Handle discovered attributes
    struct bt_gatt_service_val *gatt_service = attr->user_data;
    struct bt_gatt_chrc *gatt_chrc = attr->user_data;
    
    return BT_GATT_ITER_CONTINUE;
}

// Start discovery
discover_params.func = discover_func;
discover_params.start_handle = 0x0001;
discover_params.end_handle = 0xffff;
discover_params.type = BT_GATT_DISCOVER_PRIMARY;
discover_params.uuid = NULL;

bt_gatt_discover(conn, &discover_params);
```

### Discovery Types

```c
#define BT_GATT_DISCOVER_PRIMARY         0x01
#define BT_GATT_DISCOVER_SECONDARY       0x02
#define BT_GATT_DISCOVER_INCLUDE         0x03
#define BT_GATT_DISCOVER_CHARACTERISTIC  0x04
#define BT_GATT_DISCOVER_DESCRIPTOR      0x05
```

---

## Working Code Examples

### Full Beacon Example (BL616CL)

```c
#include "btble_lib_api.h"
#include "bl616cl_glb.h"
#include "rfparam_adapter.h"

#define BEACON_COMPANY_ID    0x004C  // Apple
#define BEACON_TYPE          0x0215  // iBeacon
#define BEACON_MAJOR         0x0001
#define BEACON_MINOR         0x0002
#define BEACON_TX_POWER      0xC5    // -59 dBm

static const uint8_t beacon_uuid[16] = {
    0x01, 0x12, 0x23, 0x34, 0x45, 0x56, 0x67, 0x78,
    0x89, 0x9A, 0xAB, 0xBC, 0xCD, 0xDE, 0xEF, 0xF0
};

static int build_ibeacon_data(uint8_t *buf, size_t buf_size)
{
    if (buf_size < 28) return -1;
    
    uint8_t *p = buf;
    *p++ = 0x02; *p++ = 0x01; *p++ = 0x06;  // Flags
    *p++ = 26; *p++ = 0xFF;                   // Manufacturer Data
    *p++ = (BEACON_COMPANY_ID & 0xFF);
    *p++ = ((BEACON_COMPANY_ID >> 8) & 0xFF);
    *p++ = ((BEACON_TYPE >> 8) & 0xFF);
    *p++ = (BEACON_TYPE & 0xFF);
    *p++ = 0x15;
    memcpy(p, beacon_uuid, 16); p += 16;
    *p++ = ((BEACON_MAJOR >> 8) & 0xFF);
    *p++ = (BEACON_MAJOR & 0xFF);
    *p++ = ((BEACON_MINOR >> 8) & 0xFF);
    *p++ = (BEACON_MINOR & 0xFF);
    *p++ = BEACON_TX_POWER;
    
    return (int)(p - buf);
}

void beacon_task(void *pvParameters)
{
    uint8_t adv_data[BTBLE_ADV_DATA_MAX_LEN];
    int adv_data_len = build_ibeacon_data(adv_data, sizeof(adv_data));
    
    struct btble_adv_params params = {
        .adv_interval_min  = 0x00A0,  // 100 ms
        .adv_interval_max  = 0x00F0,  // 150 ms
        .adv_type          = BTBLE_ADV_TYPE_NON_CONNECTABLE_UNDIRECTED,
        .own_addr_type     = BTBLE_ADDR_TYPE_PUBLIC,
        .adv_channel_map   = BTBLE_ADV_CHANNEL_ALL,
        .adv_filter_policy = BTBLE_ADV_FILTER_ALLOW_ALL,
    };
    
    btble_controller_init(configMAX_PRIORITIES - 1);
    btble_adv_init();
    btble_adv_set_parameter(&params);
    btble_adv_set_data(adv_data, adv_data_len);
    btble_adv_start();
    
    while (1) {
        vTaskDelay(pdMS_TO_TICKS(1000));
    }
}
```

### Full Peripheral Example (GATT Server)

```c
#include "bluetooth.h"
#include "conn.h"
#include "gatt.h"

static struct bt_conn *default_conn;

// GATT Service UUID
static const struct bt_uuid_128 my_svc_uuid = BT_UUID_INIT_128(
    0x01, 0x12, 0x23, 0x34, 0x45, 0x56, 0x67, 0x78,
    0x89, 0x9A, 0xAB, 0xBC, 0xCD, 0xDE, 0xEF, 0xF0
);

// Characteristic read callback
static ssize_t read_callback(struct bt_conn *conn,
                            const struct bt_gatt_attr *attr,
                            void *buf, u16_t len, u16_t offset)
{
    const char *data = "Hello";
    return bt_gatt_attr_read(conn, attr, buf, len, offset, data, 5);
}

// Characteristic write callback
static void write_callback(struct bt_conn *conn,
                          const struct bt_gatt_attr *attr,
                          const void *buf, u16_t len,
                          u16_t offset, u8_t flags)
{
    printf("Wrote: %.*s\n", len, (char *)buf);
}

// GATT attributes
static struct bt_gatt_attr my_attrs[] = {
    BT_GATT_PRIMARY_SERVICE(&my_svc_uuid),
    BT_GATT_CHARACTERISTIC(&my_svc_uuid, BT_GATT_CHRC_READ | BT_GATT_CHRC_NOTIFY,
                          BT_GATT_PERM_READ, read_callback, write_callback, NULL),
    BT_GATT_CCC(NULL, BT_GATT_PERM_READ | BT_GATT_PERM_WRITE),
};

BT_GATT_SERVICE_DEFINE(my_service, my_attrs);

// Connection callbacks
static void connected(struct bt_conn *conn, u8_t err)
{
    if (err) return;
    default_conn = bt_conn_ref(conn);
}

static void disconnected(struct bt_conn *conn, u8_t reason)
{
    if (default_conn == conn) {
        bt_conn_unref(default_conn);
        default_conn = NULL;
    }
}

static struct bt_conn_cb conn_callbacks = {
    .connected = connected,
    .disconnected = disconnected,
};

// Send notification
void send_notification(void)
{
    if (default_conn) {
        uint8_t data[] = {0x01, 0x02, 0x03};
        bt_gatt_notify(default_conn, &my_attrs[1], data, sizeof(data));
    }
}

// App task
void app_task(void *pvParameters)
{
    btble_controller_init(configMAX_PRIORITIES - 1);
    hci_driver_init();
    bt_enable(bt_enable_cb);
    bt_conn_cb_register(&conn_callbacks);
    
    while (1) {
        vTaskDelay(pdMS_TO_TICKS(1000));
        send_notification();
    }
}
```

### Full Central Example (Scanner/Connector)

```c
#include "bluetooth.h"
#include "conn.h"

static struct bt_conn *default_conn;
static u16_t gatt_mtu_size;

// Device found callback
static void device_found(const bt_addr_le_t *addr, s8_t rssi, u8_t evtype,
                        struct net_buf_simple *buf)
{
    char name[30] = {0};
    char addr_str[BT_ADDR_LE_STR_LEN];
    
    // Parse device name from adv data
    struct bt_data data;
    while (bt_data_parse(buf, &data)) {
        if (data.type == BT_DATA_NAME_COMPLETE) {
            memcpy(name, data.data, data.data_len);
        }
    }
    
    bt_addr_le_to_str(addr, addr_str, sizeof(addr_str));
    printf("Found: %s (RSSI %d) %s\n", addr_str, rssi, name);
    
    // Connect to specific device
    if (!strcmp(name, "MyDevice")) {
        struct bt_le_conn_param param = {
            .interval_min = BT_GAP_INIT_CONN_INT_MIN,
            .interval_max = BT_GAP_INIT_CONN_INT_MAX,
            .latency = 0,
            .timeout = 400,
        };
        
        bt_le_scan_stop();
        default_conn = bt_conn_create_le(addr, &param);
    }
}

// Connection callbacks
static void connected(struct bt_conn *conn, u8_t err)
{
    char addr[BT_ADDR_LE_STR_LEN];
    bt_addr_le_to_str(bt_conn_get_dst(conn), addr, sizeof(addr));
    
    if (err) {
        printf("Connect failed: %s (err %u)\n", addr, err);
        return;
    }
    
    printf("Connected: %s\n", addr);
    default_conn = conn;
    gatt_mtu_size = bt_gatt_get_mtu(conn);
}

static void disconnected(struct bt_conn *conn, u8_t reason)
{
    printf("Disconnected (reason %u)\n", reason);
    if (default_conn == conn) {
        default_conn = NULL;
        ble_start_scan(); // Restart scan
    }
}

static struct bt_conn_cb conn_callbacks = {
    .connected = connected,
    .disconnected = disconnected,
};

// Start scanning
static void ble_start_scan(void)
{
    struct bt_le_scan_param scan_param = {
        .type = BT_HCI_LE_SCAN_ACTIVE,
        .filter_dup = BT_HCI_LE_SCAN_FILTER_DUP_DISABLE,
        .interval = BT_GAP_SCAN_FAST_INTERVAL,
        .window = BT_GAP_SCAN_FAST_WINDOW,
    };
    
    bt_le_scan_start(&scan_param, device_found);
}

// GATT write task
static void ble_write_task(void *pvParameters)
{
    while (default_conn) {
        uint8_t data[20];
        for (int i = 0; i < sizeof(data); i++) {
            data[i] = i;
        }
        
        int err = bt_gatt_write_without_response(
            default_conn, 0x0001, data, sizeof(data), false);
        
        if (err) {
            printf("Write failed (err %d)\n", err);
        }
        
        vTaskDelay(pdMS_TO_TICKS(1000));
    }
    
    vTaskDelete(NULL);
}

// App task
void app_task(void *pvParameters)
{
    btble_controller_init(configMAX_PRIORITIES - 1);
    hci_driver_init();
    bt_enable(bt_enable_cb);
    bt_conn_cb_register(&conn_callbacks);
    
    ble_start_scan();
    
    xTaskCreate(ble_write_task, "ble_write", 256, NULL, 
                configMAX_PRIORITIES - 5, NULL);
    
    while (1) {
        vTaskDelay(pdMS_TO_TICKS(1000));
    }
}
```

---

## Build Configuration

In `defconfig` or Kconfig:

```makefile
CONFIG_BLE_BEACON_ONLY=y    # For beacon-only mode
CONFIG_BT_CENTRAL=y         # For central role
CONFIG_BT_PERIPHERAL=y      # For peripheral role
CONFIG_BT_OBSERVER=y        # For scanner
CONFIG_BT_GATT_CLIENT=y      # For GATT client
CONFIG_BT_GATT_SERVER=y     # For GATT server
```

---

## Quick Reference Summary

| Function | Purpose |
|----------|---------|
| `btble_controller_init(prio)` | Initialize BLE controller |
| `btble_adv_init()` | Initialize advertising (beacon mode) |
| `btble_adv_set_parameter()` | Set advertising parameters |
| `btble_adv_set_data()` | Set advertising payload |
| `btble_adv_start()` | Start advertising |
| `btble_adv_stop()` | Stop advertising |
| `btble_controller_deinit()` | Deinitialize controller |
| `bt_le_adv_start()` | Start connectable advertising (host stack) |
| `bt_le_scan_start()` | Start scanning (central) |
| `bt_conn_create_le()` | Create LE connection |
| `bt_gatt_notify()` | Send notification |
| `bt_gatt_indicate()` | Send indication |
| `bt_gatt_subscribe()` | Subscribe to notifications |
| `bt_gatt_discover()` | Discover GATT attributes |
