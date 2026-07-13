# Bluetooth SDP (Service Discovery Protocol) Technical Documentation

## 1. Overview

SDP (Service Discovery Protocol) is the core protocol in the Bluetooth stack used to query services supported by remote devices. SDP operates over the L2CAP (Logical Link Control and Adaptation Protocol) transport layer, providing a standardized mechanism for Bluetooth devices to discover services and their attributes offered by each other.

When two Bluetooth devices establish a connection, SDP allows a client device to send query requests to a server device to obtain the list of supported services, service attributes, and service characteristic information. Through SDP, applications can determine which Bluetooth profiles (such as headset, serial port, audio source, etc.) a remote device supports, and thereby decide how to interact with that device.

### 1.1 SDP Protocol Architecture

SDP operates using a client-server model:

- **SDP Server**: Maintains a database of service records, each containing information such as service type and service attributes
- **SDP Client**: Sends SDP query requests to the server to discover available services

SDP itself does not establish communication sessions; it only provides a service discovery mechanism. Actual data transfer relies on the protocol corresponding to the discovered service (such as RFCOMM, AVDTP, etc.).

## 2. Service Class Identifiers

Bluetooth assigned numbers define standardized Service Class Identifiers used to uniquely identify various Bluetooth services. Below are common core service class macro definitions:

### 2.1 Basic Service Classes

| Macro | Value | Description |
|--------|-----|------|
| `BT_SDP_SDP_SERVER_SVCLASS` | 0x1000 | SDP Server itself |
| `BT_SDP_BROWSE_GRP_DESC_SVCLASS` | 0x1001 | Browse Group Descriptor service |
| `BT_SDP_PUBLIC_BROWSE_GROUP` | 0x1002 | Public Browse Group |
| `BT_SDP_GENERIC_ACCESS_SVCLASS` | 0x1800 | Generic Access service |
| `BT_SDP_GENERIC_ATTRIB_SVCLASS` | 0x1801 | Generic Attribute service |

### 2.2 Common Audio/Media Service Classes

| Macro | Value | Description |
|--------|-----|------|
| `BT_SDP_SERIAL_PORT_SVCLASS` | 0x1101 | Serial Port service (SPP) |
| `BT_SDP_HEADSET_SVCLASS` | 0x1108 | Headset service (HSP) |
| `BT_SDP_AUDIO_SOURCE_SVCLASS` | 0x110a | Audio Source service (A2DP Source) |
| `BT_SDP_AUDIO_SINK_SVCLASS` | 0x110b | Audio Sink service (A2DP Sink) |
| `BT_SDP_ADVANCED_AUDIO_SVCLASS` | 0x110d | Advanced Audio service (A2DP) |
| `BT_SDP_AV_REMOTE_SVCLASS` | 0x110e | AV Remote Control service (AVRCP) |
| `BT_SDP_AV_REMOTE_TARGET_SVCLASS` | 0x110c | AV Remote Target service |
| `BT_SDP_AV_REMOTE_CONTROLLER_SVCLASS` | 0x110f | AV Remote Controller service |
| `BT_SDP_VIDEO_SOURCE_SVCLASS` | 0x1303 | Video Source service |
| `BT_SDP_VIDEO_SINK_SVCLASS` | 0x1304 | Video Sink service |

### 2.3 Other Common Service Classes

| Macro | Value | Description |
|--------|-----|------|
| `BT_SDP_HANDSFREE_SVCLASS` | 0x111e | Hands-Free service (HFP) |
| `BT_SDP_HANDSFREE_AGW_SVCLASS` | 0x111f | Hands-Free Audio Gateway service |
| `BT_SDP_HID_SVCLASS` | 0x1124 | Human Interface Device service (HID) |
| `BT_SDP_PBAP_PCE_SVCLASS` | 0x112e | Phone Book Access Client (PBAP) |
| `BT_SDP_PBAP_PSE_SVCLASS` | 0x112f | Phone Book Access Server (PBAP) |
| `BT_SDP_MAP_MCE_SVCLASS` | 0x1133 | Message Access Client (MAP) |
| `BT_SDP_MAP_MSE_SVCLASS` | 0x1132 | Message Access Server (MAP) |
| `BT_SDP_PNP_INFO_SVCLASS` | 0x1200 | Plug and Play Information service |

For complete Bluetooth service class definitions, refer to the Bluetooth Assigned Numbers specification.

## 3. SDP Data Structures

### 3.1 Data Element Structure

```c
struct bt_sdp_data_elem {
    uint8_t        type;       // Data type descriptor
    uint32_t       data_size;  // Actual data size
    uint32_t       total_size; // Total element size
    const void    *data;       // Pointer to data
};
```

The data type descriptor (type field) consists of a data type (upper 5 bits) and a size descriptor (lower 3 bits), mainly including:

- `BT_SDP_UINT8` / `BT_SDP_UINT16` / `BT_SDP_UINT32` / `BT_SDP_UINT64` / `BT_SDP_UINT128`: Unsigned integers
- `BT_SDP_INT8` / `BT_SDP_INT16` / `BT_SDP_INT32`: Signed integers
- `BT_SDP_UUID16` / `BT_SDP_UUID32` / `BT_SDP_UUID128`: UUID identifiers
- `BT_SDP_TEXT_STR8` / `BT_SDP_TEXT_STR16`: Text strings
- `BT_SDP_SEQ8` / `BT_SDP_SEQ16`: Data sequences
- `BT_SDP_BOOL`: Boolean type
- `BT_SDP_URL_STR8`: URL string

### 3.2 SDP Attribute Structure

```c
struct bt_sdp_attribute {
    uint16_t                id;    // Attribute ID
    struct bt_sdp_data_elem val;   // Attribute data value
};
```

Common attribute ID definitions:

| Attribute ID | Description |
|--------|------|
| `BT_SDP_ATTR_RECORD_HANDLE` | Service Record Handle |
| `BT_SDP_ATTR_SVCLASS_ID_LIST` | Service Class ID List |
| `BT_SDP_ATTR_RECORD_STATE` | Record State |
| `BT_SDP_ATTR_SERVICE_ID` | Service ID |
| `BT_SDP_ATTR_PROTO_DESC_LIST` | Protocol Descriptor List |
| `BT_SDP_ATTR_BROWSE_GRP_LIST` | Browse Group List |
| `BT_SDP_ATTR_PROFILE_DESC_LIST` | Profile Descriptor List |
| `BT_SDP_ATTR_SUPPORTED_FEATURES` | Supported Features |
| `BT_SDP_ATTR_SVCNAME_PRIMARY` | Primary Service Name |
| `BT_SDP_ATTR_SVCDESC_PRIMARY` | Primary Service Description |

### 3.3 SDP Service Record Structure

```c
struct bt_sdp_record {
    uint32_t                    handle;      // Service record handle
    struct bt_sdp_attribute    *attrs;       // Pointer to attribute array
    size_t                      attr_count;  // Number of attributes
    uint8_t                     index;       // Record index
    struct bt_sdp_record       *next;        // Pointer to next record
};
```

### 3.4 SDP Client Query Result Structure

```c
struct bt_sdp_client_result {
    struct net_buf        *resp_buf;           // Buffer containing unparsed SDP record results
    bool                   next_record_hint;  // Indicates whether more results exist
    const struct bt_uuid  *uuid;              // UUID object being queried
};
```

### 3.5 SDP Discovery Parameters Structure

```c
struct bt_sdp_discover_params {
    sys_snode_t            _node;
    const struct bt_uuid  *uuid;              // Service UUID to discover
    bt_sdp_discover_func_t  func;             // Discovery result callback function
    struct net_buf_pool    *pool;             // Memory pool for SDP query results
};
```

## 4. UUID and Connection Association

Bluetooth UUIDs are used to uniquely identify various services and profiles. The SDP protocol uses the `bt_uuid_t` structure to represent UUIDs, and communicates SDP with remote devices via connections represented by the `bt_conn_t` structure.

### 4.1 UUID Structure Types

```c
struct bt_uuid {
    u8_t type;  // UUID type: BT_UUID_TYPE_16, BT_UUID_TYPE_32, or BT_UUID_TYPE_128
};

struct bt_uuid_16 {
    struct bt_uuid uuid;
    u16_t val;   // 16-bit UUID value
};

struct bt_uuid_128 {
    struct bt_uuid uuid;
    u8_t val[16]; // 128-bit UUID value
};
```

### 4.2 UUID Macro Definitions

```c
// Initialize a 16-bit UUID
#define BT_UUID_INIT_16(value) { .uuid = { BT_UUID_TYPE_16 }, .val = (value) }

// Declare a 16-bit UUID
#define BT_UUID_DECLARE_16(value) ((struct bt_uuid *)((struct bt_uuid_16[]) {BT_UUID_INIT_16(value)}))

// Get bt_uuid_16 struct from bt_uuid pointer
#define BT_UUID_16(__u) CONTAINER_OF(__u, struct bt_uuid_16, uuid)
```

### 4.3 UUID and Connection Association

SDP queries are associated with a remote device through the `bt_conn_t` connection object. When calling `bt_sdp_discover()`, a valid `bt_conn` pointer must be passed to specify the remote device to query. Query results are returned via callback functions; developers can access `bt_conn` information in the callback to identify which device's query results have arrived.

## 5. SDP Client API

### 5.1 bt_sdp_discover() - Start Service Discovery

```c
int bt_sdp_discover(struct bt_conn *conn,
                    const struct bt_sdp_discover_params *params);
```

**Description**: Initiates an SDP service discovery session for a remote device.

**Parameters**:
- `conn`: Pointer to an object identifying the connection to the remote device
- `params`: SDP discovery parameters, including the UUID to query, callback function, and result buffer pool

**Returns**: 0 on success, negative error code on failure.

**Usage Notes**:
- This function performs an asynchronous SDP query; the user-provided callback is invoked upon completion
- If there is an ongoing SDP transaction, new requests are queued for processing
- The return value of the callback function can control whether to continue fetching more records

**Callback Function Type**:

```c
typedef uint8_t (*bt_sdp_discover_func_t)
        (struct bt_conn *conn, struct bt_sdp_client_result *result);
```

Callback return values:
- `BT_SDP_DISCOVER_UUID_STOP`: Stop fetching more records
- `BT_SDP_DISCOVER_UUID_CONTINUE`: Continue fetching the next record

### 5.2 bt_sdp_discover_cancel() - Cancel Service Discovery

```c
int bt_sdp_discover_cancel(struct bt_conn *conn,
                           const struct bt_sdp_discover_params *params);
```

**Description**: Cancels a pending SDP discovery request.

**Parameters**:
- `conn`: Pointer to an object identifying the connection to the remote device
- `params`: SDP discovery parameters to cancel

**Returns**: 0 on success, negative error code on failure.

### 5.3 bt_sdp_get_proto_param() - Get Protocol Parameters

```c
int bt_sdp_get_proto_param(const struct net_buf *buf, enum bt_sdp_proto proto,
                           uint16_t *param);
```

**Description**: Extracts parameter values for a specific protocol from an SDP record.

**Supported Protocols**:
- `BT_SDP_PROTO_RFCOMM = 0x0003`: RFCOMM protocol
- `BT_SDP_PROTO_L2CAP = 0x0100`: L2CAP protocol

**Parameters**:
- `buf`: Buffer containing raw SDP record data
- `proto`: The protocol type to query
- `param`: Filled with the found parameter value on success

**Returns**: 0 on success, negative error code on failure.

### 5.4 bt_sdp_get_profile_version() - Get Profile Version

```c
int bt_sdp_get_profile_version(const struct net_buf *buf, uint16_t profile,
                               uint16_t *version);
```

**Description**: Extracts the profile version number for a remote device from an SDP record.

**Parameters**:
- `buf`: Raw SDP record data buffer
- `profile`: Profile family identifier
- `version`: Filled with the found version number on success

**Returns**: 0 on success, negative error code on failure.

### 5.5 bt_sdp_get_features() - Get Supported Features

```c
int bt_sdp_get_features(const struct net_buf *buf, uint16_t *features);
```

**Description**: Retrieves the list of features supported by the remote device from an SDP record.

**Parameters**:
- `buf`: Buffer containing raw SDP record data
- `features`: Filled with the SupportedFeature attribute mask on success

**Returns**: 0 on success, negative error code if no feature information exists in the record or if parsing fails.

## 6. SDP Server API

### 6.1 bt_sdp_register_service() - Register Service Record

```c
int bt_sdp_register_service(struct bt_sdp_record *service);
```

**Description**: Registers a service record in the local SDP database, making the service discoverable by remote devices via SDP queries.

**Parameters**:
- `service`: Service record structure declared using the `BT_SDP_RECORD` macro

**Returns**: 0 on success, negative error code on failure.

### 6.2 bt_sdp_init() - Initialize SDP

```c
void bt_sdp_init(void);
```

**Description**: Initializes the SDP subsystem. Must be called before registering service records or performing client queries.

## 7. SDP Helper Macros

### 7.1 Service Record Declaration Macros

```c
// Declare a new service record with default attributes
#define BT_SDP_NEW_SERVICE { ... }

// Declare a complete service record
#define BT_SDP_RECORD(_attrs) { .attrs = _attrs, .attr_count = ARRAY_SIZE((_attrs)) }
```

### 7.2 Attribute Declaration Macros

```c
// Declare a list-type attribute
#define BT_SDP_LIST(_att_id, _type_size, _data_elem_seq)

// Declare a service ID attribute
#define BT_SDP_SERVICE_ID(_uuid)

// Declare a service name attribute
#define BT_SDP_SERVICE_NAME(_name)

// Declare a supported features attribute
#define BT_SDP_SUPPORTED_FEATURES(_features)
```

### 7.3 Data Element Helper Macros

```c
// Declare an 8-bit array
#define BT_SDP_ARRAY_8(...) ((uint8_t[]) {__VA_ARGS__})

// Declare a 16-bit array
#define BT_SDP_ARRAY_16(...) ((uint16_t[]) {__VA_ARGS__})

// Declare a 32-bit array
#define BT_SDP_ARRAY_32(...) ((uint32_t[]) {__VA_ARGS__})

// Declare a fixed-size data element
#define BT_SDP_TYPE_SIZE(_type)

// Declare a variable-size data element
#define BT_SDP_TYPE_SIZE_VAR(_type, _size)

// Declare a data element list
#define BT_SDP_DATA_ELEM_LIST(...) ((struct bt_sdp_data_elem[]) {__VA_ARGS__})
```

## 8. Code Examples

### 8.1 Service Discovery Example

The following example demonstrates how to discover services supported by a remote device:

```c
#include "bluetooth/sdp.h"
#include "bluetooth/conn.h"
#include "bluetooth/bt_uuid.h"
#include <net/buf.h>

/* Buffer pool for storing discovery results */
static struct net_buf_pool *sdp_result_pool;

/* SDP discovery callback function */
static uint8_t sdp_discover_cb(struct bt_conn *conn,
                               struct bt_sdp_client_result *result)
{
    uint16_t features;
    int err;

    if (!result || !result->resp_buf) {
        printk("SDP discovery complete, no more results\n");
        return BT_SDP_DISCOVER_UUID_STOP;
    }

    printk("Discovered service UUID: 0x%04x\n",
           result->uuid ? ((struct bt_uuid_16 *)result->uuid)->val : 0);

    /* Attempt to get the features supported by this service */
    err = bt_sdp_get_features(result->resp_buf, &features);
    if (err == 0) {
        printk("  Supported features: 0x%04x\n", features);
    }

    /* Decide whether to continue based on next_record_hint */
    if (result->next_record_hint) {
        return BT_SDP_DISCOVER_UUID_CONTINUE;
    }

    return BT_SDP_DISCOVER_UUID_STOP;
}

/* Start SDP service discovery */
int discover_remote_services(struct bt_conn *conn)
{
    struct bt_sdp_discover_params discover_params;
    static const struct bt_uuid_16 sdp_uuid = BT_UUID_INIT_16(
        BT_SDP_PUBLIC_BROWSE_GROUP);

    /* Initialize discovery parameters */
    discover_params.uuid = &sdp_uuid.uuid;
    discover_params.func = sdp_discover_cb;
    discover_params.pool = sdp_result_pool;

    printk("Starting remote device service discovery...\n");

    return bt_sdp_discover(conn, &discover_params);
}
```

### 8.2 Querying a Specific Service Example

The following example demonstrates how to query a remote device's Serial Port Service (SPP):

```c
#include "bluetooth/sdp.h"
#include "bluetooth/conn.h"
#include "bluetooth/bt_uuid.h"

/* SPP service query callback */
static uint8_t spp_discover_cb(struct bt_conn *conn,
                                struct bt_sdp_client_result *result)
{
    uint16_t rfcomm_channel = 0;
    int err;

    if (!result || !result->resp_buf) {
        return BT_SDP_DISCOVER_UUID_STOP;
    }

    /* Get RFCOMM channel number from SDP record */
    err = bt_sdp_get_proto_param(result->resp_buf, BT_SDP_PROTO_RFCOMM,
                                 &rfcomm_channel);
    if (err == 0) {
        printk("SPP service - RFCOMM channel: %d\n", rfcomm_channel);
    } else {
        printk("SPP service - unable to get RFCOMM channel\n");
    }

    return BT_SDP_DISCOVER_UUID_STOP;
}

/* Query remote device's SPP service */
int discover_spp_service(struct bt_conn *conn)
{
    struct bt_sdp_discover_params params;
    static const struct bt_uuid_16 spp_uuid = BT_UUID_INIT_16(
        BT_SDP_SERIAL_PORT_SVCLASS);

    params.uuid = &spp_uuid.uuid;
    params.func = spp_discover_cb;
    params.pool = sdp_result_pool;

    printk("Querying SPP service...\n");
    return bt_sdp_discover(conn, &params);
}
```

### 8.3 Registering a Local SDP Service Example

The following example demonstrates how to register a custom Bluetooth service locally:

```c
#include "bluetooth/sdp.h"

/* Define service attributes */
static const struct bt_sdp_attribute my_service_attrs[] = {
    /* Basic service declaration - required */
    BT_SDP_NEW_SERVICE,

    /* Service class ID */
    BT_SDP_LIST(BT_SDP_ATTR_SVCLASS_ID_LIST,
                BT_SDP_TYPE_SIZE(BT_SDP_SEQ8),
                BT_SDP_DATA_ELEM_LIST({
                    BT_SDP_TYPE_SIZE(BT_SDP_UUID16),
                    BT_SDP_ARRAY_16(BT_SDP_SERIAL_PORT_SVCLASS)
                })),

    /* Protocol descriptor list */
    BT_SDP_LIST(BT_SDP_ATTR_PROTO_DESC_LIST,
                BT_SDP_TYPE_SIZE(BT_SDP_SEQ8),
                BT_SDP_DATA_ELEM_LIST({
                    BT_SDP_TYPE_SIZE(BT_SDP_SEQ8),
                    BT_SDP_DATA_ELEM_LIST({
                        BT_SDP_TYPE_SIZE(BT_SDP_UUID16),
                        BT_SDP_ARRAY_16(BT_SDP_PROTO_L2CAP)
                    }),
                    BT_SDP_TYPE_SIZE(BT_SDP_UINT16),
                    BT_SDP_ARRAY_16(0x0003)  /* RFCOMM */
                })),

    /* Service name */
    BT_SDP_SERVICE_NAME("My Custom Service"),

    /* Supported features */
    BT_SDP_SUPPORTED_FEATURES(0x0001),
};

/* Declare service record */
static const struct bt_sdp_record my_service_record = {
    BT_SDP_RECORD(my_service_attrs)
};

/* Register service */
int register_my_service(void)
{
    int err;

    err = bt_sdp_register_service(&my_service_record);
    if (err < 0) {
        printk("Service registration failed: %d\n", err);
        return err;
    }

    printk("Custom service registered successfully\n");
    return 0;
}
```

### 8.4 Browsing Service List Example

The following example demonstrates how to browse all services under a browse group:

```c
#include "bluetooth/sdp.h"
#include "bluetooth/bt_uuid.h"

/* Browse callback - print all discovered services */
static uint8_t browse_all_cb(struct bt_conn *conn,
                             struct bt_sdp_client_result *result)
{
    struct bt_uuid_16 *uuid;
    char uuid_str[8];

    if (!result || !result->resp_buf) {
        printk("Browse complete\n");
        return BT_SDP_DISCOVER_UUID_STOP;
    }

    /* Get UUID from callback result */
    if (result->uuid && result->uuid->type == BT_UUID_TYPE_16) {
        uuid = BT_UUID_16(result->uuid);
        snprintf(uuid_str, sizeof(uuid_str), "0x%04x", uuid->val);

        /* Identify common services by UUID value */
        const char *name = "Unknown service";
        switch (uuid->val) {
        case 0x1101: name = "Serial Port (SPP)"; break;
        case 0x1108: name = "Headset (HSP)"; break;
        case 0x110a: name = "Audio Source"; break;
        case 0x110d: name = "Advanced Audio (A2DP)"; break;
        case 0x110e: name = "AV Remote Control"; break;
        case 0x111e: name = "Hands-Free (HFP)"; break;
        }

        printk("Discovered service: %s [%s]\n", name, uuid_str);
    }

    return result->next_record_hint ?
           BT_SDP_DISCOVER_UUID_CONTINUE : BT_SDP_DISCOVER_UUID_STOP;
}

/* Browse all available services */
int browse_all_services(struct bt_conn *conn)
{
    struct bt_sdp_discover_params params;
    static const struct bt_uuid_16 browse_uuid = BT_UUID_INIT_16(
        BT_SDP_BROWSE_GRP_DESC_SVCLASS);

    params.uuid = &browse_uuid.uuid;
    params.func = browse_all_cb;
    params.pool = sdp_result_pool;

    printk("Starting browse of all services...\n");
    return bt_sdp_discover(conn, &params);
}
```

## 9. SDP Workflow

### 9.1 Client Service Discovery Flow

1. **Establish connection**: First establish a Bluetooth connection via an ACL (Asynchronous Connection-Oriented) link
2. **Initialize SDP**: Call `bt_sdp_init()` to ensure the SDP subsystem is ready
3. **Configure discovery parameters**: Set the UUID to query, callback function, and result buffer
4. **Initiate discovery request**: Call `bt_sdp_discover()` to send the SDP query
5. **Process results**: Parse returned SDP records in the callback function
6. **Extract information**: Use helper APIs (such as `bt_sdp_get_proto_param()`) to extract desired attributes

### 9.2 Server-Side Service Registration Flow

1. **Initialize SDP**: Call `bt_sdp_init()` to initialize the SDP subsystem
2. **Define service attributes**: Use helper macros to define the attribute list for the service record
3. **Declare service record**: Use the `BT_SDP_RECORD()` macro to create the service record structure
4. **Register service**: Call `bt_sdp_register_service()` to add the service record to the local SDP database
5. **Await queries**: Remote devices can discover the registered service through SDP queries

## 10. Important Notes

### 10.1 Connection Management

- SDP queries must be based on an established `bt_conn` connection
- SDP query results become invalid after the connection is disconnected
- It is recommended to perform necessary SDP discovery immediately after a connection is successfully established

### 10.2 Memory Management

- SDP discovery results are stored in `net_buf` buffers; a sufficiently large memory pool must be provided
- After the callback function returns, the buffer may have been freed and should not be referenced further
- For large service databases, multiple callbacks may be required to obtain complete results

### 10.3 Error Handling

- Most SDP APIs return negative values to indicate errors and 0 to indicate success
- Helper functions like `bt_sdp_get_proto_param()` and `bt_sdp_get_features()` also return negative values to indicate parsing failures
- Always check return values and handle error conditions

### 10.4 UUID Type Matching

- Ensure the UUID type used for queries matches the type in the remote device's service records
- 16-bit UUIDs are the most commonly used form, corresponding to standard Bluetooth services
- 128-bit UUIDs are used for custom or vendor-specific services

## References

- [Bluetooth Core Specification - SDP Section](https://www.bluetooth.com/specifications/assigned-numbers/service-discovery)
- bouffalo_sdk/components/wireless/bluetooth/btprofile/include/bluetooth/sdp.h
- bouffalo_sdk/components/wireless/bluetooth/blestack/src/include/bluetooth/bt_uuid.h
