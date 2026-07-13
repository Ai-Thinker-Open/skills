# BLE GAP/GATT API Reference

> Source files: `components/network/ble/blestack/src/host/hci_core.h` etc.  
> BL602 uses the open-source blestack to implement BLE 5.0 Host protocol stack (GAP and GATT layers).

---

## Overview

BLE protocol stack layers:

```
┌──────────────────────────────────────┐
│         Application (GATT Client/Server) │
├──────────────────────────────────────┤
│         GATT Server / Client          │
│  (Service/Characteristic/Descriptor)  │
├──────────────────────────────────────┤
│         GAP (Advertising/Connection)  │
│   (Broadcast/Connect/Discover/Security) │
├──────────────────────────────────────┤
│         HCI (Host-Controller Interface)│
├──────────────────────────────────────┤
│         BLE Controller (LL)           │
└──────────────────────────────────────┘
```

---

## GAP — Broadcasting and Connection

### Advertising Parameters

```c
struct bt_le_adv_param {
    uint8_t id;          // Advertising set ID (BT_ID_DEFAULT = 0)
    uint8_t sid;         // Advertising set ID
    uint8_t freq;        // Advertising channel (BT_GAP_SCAN_FAST_INTERVAL = 0x0060)
    uint16_t interval_min;  // Minimum advertising interval (slots)
    uint16_t interval_max;  // Maximum advertising interval (slots)
    uint8_t  type;          // Advertising type
    uint8_t  chan_map;      // Channel map
    uint8_t  filter_policy; // Advertising filter policy
    uint8_t  tier;          // Advertising power level
};
```

**Advertising types** (`type`):

| Value | Advertising Type | Description |
|-------|------------------|-------------|
| `BT_GAP_ADV_TYPE_ADV_IND` | Connectable advertising | Most commonly used |
| `BT_GAP_ADV_TYPE_ADV_DIRECT_IND` | Directed advertising | Fast connection to specific device |
| `BT_GAP_ADV_TYPE_ADV_SCAN_IND` | Scannable advertising | Allows scan requests |
| `BT_GAP_ADV_TYPE_ADV_NONCONN_IND` | Non-connectable advertising | Data broadcast only |

### `bt_enable`

Initialize the BLE protocol stack.

```c
int bt_enable(void);
```

> This function must be called before using any other BLE API.

---

### `bt_le_adv_start`

Start advertising.

```c
int bt_le_adv_start(const struct bt_le_adv_param *param,
                     const struct bt_data *ad,
                     size_t ad_len,
                     const struct bt_data *scan_rsp,
                     size_t scan_rsp_len);
```

| Parameter | Description |
|-----------|-------------|
| `param` | Advertising parameters |
| `ad` | Advertising data (AD Structure) |
| `ad_len` | Number of advertising data entries |
| `scan_rsp` | Scan response data (can be NULL) |
| `scan_rsp_len` | Number of scan response data entries |

---

### `bt_le_adv_stop`

Stop advertising.

```c
int bt_le_adv_stop(void);
```

---

### `bt_le_scan_start`

Start scanning.

```c
int bt_le_scan_start(uint8_t scan_type,
                     const struct bt_le_scan_param *param);
```

---

### `bt_le_scan_stop`

Stop scanning.

```c
int bt_le_scan_stop(void);
```

---

## GATT — Generic Attribute Profile

### Common Attributes

### `bt_gatt_service_register`

Register a GATT Service.

```c
uint8_t bt_gatt_service_register(const struct bt_gatt_service *svc);
```

---

### `bt_gatt_notify`

Send a notification to the client (no response required).

```c
int bt_gatt_notify(struct bt_conn *conn,
                   const struct bt_gatt_attr *attr,
                   const void *data,
                   uint16_t len);
```

---

### `bt_gatt_indicate`

Send an indication to the client (acknowledgment required).

```c
int bt_gatt_indicate(struct bt_conn *conn,
                     struct bt_gatt_attr *attr,
                     const void *data,
                     uint16_t len);
```

---

### `bt_gatt_read`

Read an attribute value.

```c
ssize_t bt_gatt_read(struct bt_conn *conn,
                      uint8_t flags,
                      const struct bt_gatt_attr *attr,
                      void *buf,
                      uint16_t buf_len,
                      uint16_t offset);
```

---

### `bt_gatt_write`

Write an attribute value (with response).

```c
int bt_gatt_write(struct bt_conn *conn,
                   uint8_t flags,
                   const struct bt_gatt_attr *attr,
                   const void *data,
                   uint16_t len,
                   bt_gatt_write_func_t func,
                   void *user_data);
```

---

### `bt_gatt_write_without_response`

Write an attribute value (no response).

```c
uint8_t bt_gatt_write_without_response(struct bt_conn *conn,
                                        const struct bt_gatt_attr *attr,
                                        const void *data,
                                        uint16_t len,
                                        bool sign);
```

---

## Connection Management

### `bt_conn_connect`

Establish a BLE connection.

```c
struct bt_conn *bt_conn_connect(const struct bt_conn_info *info);
```

---

### `bt_conn_disconnect`

Disconnect.

```c
int bt_conn_disconnect(struct bt_conn *conn, uint8_t reason);
```

---

### `bt_conn_get_info`

Get connection information.

```c
int bt_conn_get_info(const struct bt_conn *conn, struct bt_conn_info *info);
```

---

## Usage Examples

### BLE Advertising (Peripheral)

```c
#include "bluetooth.h"

static const struct bt_data ad[] = {
    BT_DATA(BT_DATA_FLAGS, (uint8_t[]){ BT_LE_AD_LIMITED }, 1),
    BT_DATA(BT_DATA_NAME_COMPLETE, "BL602", 5),
};

static const struct bt_data sd[] = {
    BT_DATA(BT_DATA_UUID128_SOME, ...),
};

int ble_adv_start(void)
{
    struct bt_le_adv_param param = {
        .id = 0,
        .type = BT_GAP_ADV_TYPE_ADV_IND,
        .interval_min = 0x0020,
        .interval_max = 0x0020,
    };

    return bt_le_adv_start(&param, ad, ARRAY_SIZE(ad),
                           sd, ARRAY_SIZE(sd));
}
```

### GATT Service Registration

```c
static ssize_t read_temp(struct bt_conn *conn,
                         const struct bt_gatt_attr *attr,
                         void *buf, uint16_t len, uint16_t offset)
{
    uint16_t temp = read_temperature();
    return bt_gatt_attr_read(conn, attr, buf, len, offset, &temp, sizeof(temp));
}

static struct bt_gatt_attr attrs[] = {
    BT_GATT_PRIMARY_SERVICE(UUID_SENSOR_SVC),
    BT_GATT_CHARACTERISTIC(UUID_TEMP,
                           BT_GATT_CHRC_READ,
                           BT_GATT_PERM_READ,
                           read_temp, NULL, NULL),
};

static struct bt_gatt_service sensor_svc =
    BT_GATT_SERVICE(attrs);

bt_gatt_service_register(&sensor_svc);
```

### Sending Notifications

```c
extern struct bt_conn *conn;

static void notify_callback(struct bt_conn *conn,
                            struct bt_gatt_attr *attr,
                            void *context)
{
    // Notify client when value changes
    uint8_t data = get_sensor_value();
    bt_gatt_notify(conn, attr, &data, sizeof(data));
}
```
