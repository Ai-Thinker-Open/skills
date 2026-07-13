# BLE Mesh and Coexistence Documentation

## BL616/BL618 BLE Mesh & WiFi/BLE Coexistence API Guide

Based on Bouffalo SDK `bouffalo_sdk/components/wireless/bluetooth/blemesh/src/` and `bouffalo_sdk/components/wireless/coex/coex.h`

---

## Table of Contents
1. [BLE Mesh Overview](#ble-mesh-overview)
2. [BLE Mesh API Reference](#ble-mesh-api-reference)
   - [Initialization](#mesh-initialization)
   - [Provisioning](#provisioning)
   - [Model Send](#model-send)
3. [Coexistence API Reference](#coexistence-api-reference)
   - [Coex Init](#coex-init)
   - [Coex Config](#coex-config)
   - [Coex Priority](#coex-priority)
4. [Working Code Examples](#working-code-examples)

---

## BLE Mesh Overview

The BL616/BL618 supports Bluetooth Mesh (BLE Mesh) protocol based on the Zephyr Bluetooth Mesh stack with Bouffalo Lab extensions.

### Key Features
- Supports both Provisioner and Node roles
- PB-ADV (Provisioning Bearer over Advertising) and PB-GATT bearers
- Foundation Models: Configuration Server/Client, Health Server/Client
- Generic Models: OnOff, Level, Lightness, etc.
- Friend Node and Low Power Node (LPN) support
- BLOB Transfer and DFU support

---

## BLE Mesh API Reference

### Header Files
```c
#include "mesh.h"           // Main mesh header
#include "mesh_config.h"    // Mesh configuration defines
#include "access.h"          // Access layer (models)
#include "main.h"           // Provisioning APIs
#include "prov.h"           // Provisioning bearer APIs
```

### Key Configuration (mesh_config.h)
```c
#define CONFIG_BT_MESH_ADV_PRIO           (configMAX_PRIORITIES - 4)
#define CONFIG_BT_MESH_NODE_COUNT          128
#define CONFIG_BT_MESH_MODEL_KEY_COUNT     2
#define CONFIG_BT_MESH_APP_KEY_COUNT       2
#define CONFIG_BT_MESH_SUBNET_COUNT        2
#define CONFIG_BT_MESH_ADV_BUF_COUNT       60
#define CONFIG_BT_MESH_RX_SDU_MAX          108
#define CONFIG_BT_DEVICE_NAME              "bl_mesh"
#define BL_COMP_ID                         0x0A38
#define BL_PRODUCT_ID                      0x0001
```

---

## Mesh Initialization

### `bt_mesh_init()`

Initialize the Bluetooth Mesh stack.

```c
int bt_mesh_init(const struct bt_mesh_prov *prov,
                 const struct bt_mesh_comp *comp);
```

**Parameters:**
- `prov` - Provisioning properties callback structure
- `comp` - Node composition data

**Returns:** 0 on success, negative error code on failure

### `bt_mesh_start()`

Start mesh functionality after initialization.

```c
int bt_mesh_start(void);
```

---

## Provisioning

### `bt_mesh_prov_enable()`

Enable provisioning bearers.

```c
int bt_mesh_prov_enable(bt_mesh_prov_bearer_t bearers);
```

**Bearer types:**
```c
typedef enum {
    BT_MESH_PROV_ADV   = BIT(0),    // PB-ADV bearer
    BT_MESH_PROV_GATT  = BIT(1),    // PB-GATT bearer
    BT_MESH_PROV_GATT_ADV = BIT(0)|BIT(1), // Both bearers
} bt_mesh_prov_bearer_t;
```

### `bt_mesh_provision()`

Manually provision the local node (for testing).

```c
int bt_mesh_provision(const u8_t net_key[16], u16_t net_idx,
                      u8_t flags, u32_t iv_index, u16_t addr,
                      const u8_t dev_key[16]);
```

### `bt_mesh_provision_adv()`

Provision a remote node using PB-ADV.

```c
int bt_mesh_provision_adv(const u8_t uuid[16], u16_t net_idx, 
                          u16_t addr, u8_t attention_duration);
```

### `bt_mesh_is_provisioned()`

Check if node has been provisioned.

```c
bool bt_mesh_is_provisioned(void);
```

---

## Model Send

### `bt_mesh_model_send()`

Send an Access Layer message from a model.

```c
int bt_mesh_model_send(struct bt_mesh_model *model,
                       struct bt_mesh_msg_ctx *ctx,
                       struct net_buf_simple *msg,
                       const struct bt_mesh_send_cb *cb,
                       void *cb_data);
```

### `bt_mesh_model_publish()`

Publish a message via model's publication context.

```c
int bt_mesh_model_publish(struct bt_mesh_model *model);
```

### Message Context Structure

```c
struct bt_mesh_msg_ctx {
    u16_t net_idx;      // NetKey Index
    u16_t app_idx;      // AppKey Index
    u16_t addr;         // Remote address
    u16_t recv_dst;     // Destination address
    s8_t  recv_rssi;    // RSSI (received)
    u8_t  recv_ttl;     // Received TTL
    bool  send_rel;     // Send reliably (with ack)
    u8_t  send_ttl;     // TTL for sending
    u32_t recv_op;      // Received opcode
    struct bt_mesh_model *model;
    bool srv_send;
};
```

### Model Message Buffer Macros

```c
// Define a model message buffer
BT_MESH_MODEL_BUF_DEFINE(buf, opcode, payload_len);

// Initialize message with opcode
bt_mesh_model_msg_init(struct net_buf_simple *msg, u32_t opcode);

// Get buffer length
BT_MESH_MODEL_BUF_LEN(opcode, payload_len)
```

---

## Coexistence API Reference

### Header File
```c
#include "coex.h"
```

### Coex Modes
```c
#define COEX_MODE_TDMA    1   // Time Division Multiple Access
#define COEX_MODE_PTI     2   // Priority Time Interface

// None handling
#define COEX_NONE_NULL    1   // No action
#define COEX_NONE_RF_DOWN 2   // RF down
```

### Coex Roles
```c
enum coex_role {
    COEX_ROLE_BT = 0,
    COEX_ROLE_WIFI,
    COEX_ROLE_THREAD,
    COEX_ROLE_DUMMY,
    COEX_ROLE_MAX,
};
```

### Coex Events
```c
enum coex_event {
    COEX_EVT_INIT = 0,           // Init wireless module
    COEX_EVT_DEINIT,             // Deinit wireless module
    COEX_EVT_SET_ACTIVITY,       // Set activity
    COEX_EVT_GET_ACTIVITY,       // Get coex activity
    COEX_EVT_TMR_ISR_HANDLE,     // Timer ISR event
    COEX_EVT_FUNC_CALL,          // Function call
    COEX_EVT_MAX,
};
```

### Activity Types
```c
enum coex_event_activity {
    // BLE
    ACT_START_ADV,
    
    // BT
    ACT_BT_SCAN_START,
    ACT_BT_SCAN_DONE,
    ACT_BT_CONNECT_START,
    ACT_BT_CONNECT_DONE_OK,
    ACT_BT_CONNECT_DONE_FAIL,
    ACT_BT_DISCONNECT_START,
    ACT_BT_DISCONNECT_DONE,
    ACT_BT_A2DP_START,
    ACT_BT_A2DP_STOP,

    // Wi-Fi
    ACT_STA_SCAN_START,
    ACT_STA_SCAN_DONE,
    ACT_STA_CONNECT_START,
    ACT_STA_CONNECT_DONE_OK,
    ACT_STA_CONNECT_DONE_FAIL,
    ACT_STA_DISCONNECT_START,
    ACT_STA_DISCONNECT_DONE,
    ACT_STA_DPSM_START,
    ACT_STA_DPSM_YIELD,
    ACT_STA_DPSM_STOP,
    ACT_STA_ROC_REQ,
    ACT_STA_TBTT_UPDATE,
    ACT_SOFTAP_START,
    ACT_SOFTAP_STOP,
    ACT_SOFTAP_TBTT_UPDATE,

    // Thread
    ACT_START_PAN,
    ACT_STOP_PAN,

    // Dummy
    ACT_DUMMY_ADD_ACT,
    ACT_DUMMY_DEL_ACT,

    ACT_MAX,
};
```

---

## Coex Init

### `coex_init()`

Initialize the coexistence module.

```c
int coex_init(void);
```

**Returns:** COEX_OK (0) on success, COEX_FAIL (-1) on failure

### `coex_deinit()`

Deinitialize the coexistence module.

```c
int coex_deinit(void);
```

---

## Coex Config

### `coex_event()`

Send event to coex module for coordination.

```c
int coex_event(struct coex_evt_arg* arg);
```

**Event Argument Structure:**
```c
struct coex_evt_arg {
    int role;              // COEX_ROLE_BT, COEX_ROLE_WIFI, etc.
    int type;              // Event type (COEX_EVT_*)
    union evt_arg arg;     // Event-specific arguments
};

// Event argument unions:
union evt_arg {
    // INIT
    struct {
        coex_notify_cb cb;     // Callback function
        void* env;            // Environment data
    } init;

    // DEINIT
    struct {
        int empty;
    } deinit;

    // Set activity
    struct {
        int type;          // Activity type (ACT_*)
        int now;           // Timestamp
    } set_act;

    // Get activity
    struct {
        int empty;
    } get_act;

    // Timer ISR
    struct {
        uint64_t time;
        void* env;
    } tmr_isr;

    // Function call
    struct {
        coex_func_call func;
        int arg[4];
    } func_call;
};
```

---

## Coex Priority

### Priority Handling via Activity Events

The coexistence module uses activity events to determine priority. Higher priority activities get RF time allocation.

### Notify Callback

```c
struct coex_notify_args {
    int event;       // COEX_NTY_* event
    int duration;     // Duration in ms
};

// Callback types:
typedef void (*coex_notify_cb)(void* env, struct coex_notify_args* args);
typedef void (*coex_func_call)(void* args);
```

### Coex Notify Events
```c
enum coex_notify {
    COEX_NTY_INITED = 0,      // Coex initialized
    COEX_NTY_DEINITED,        // Coex deinitialized
    COEX_NTY_RF_PRESENCE,      // RF is present/active
    COEX_NTY_RF_ABSENCE,       // RF is absent/inactive
    COEX_NTY_MAX,
};
```

---

## Working Code Examples

### BLE Mesh Node Initialization Example

```c
#include "mesh.h"
#include "access.h"
#include "main.h"
#include "prov.h"

// Device UUID (16 bytes)
static const uint8_t dev_uuid[16] = { /* your UUID */ };

// Provisioning callback structure
static struct bt_mesh_prov prov = {
    .uuid = dev_uuid,
    .uri = NULL,
    .oob_info = 0,
    .oob_pub_key = false,
    .static_val = NULL,
    .static_val_len = 0,
    .output_size = 0,
    .output_actions = 0,
    .input_size = 0,
    .input_actions = 0,
    
    // Callbacks
    .link_open = prov_link_open_cb,
    .link_close = prov_link_close_cb,
    .complete = prov_complete_cb,
    .node_added = prov_node_added_cb,
    .reset = prov_reset_cb,
};

// Element location
#defineLocationDescriptor 0x0000

// Model opcode handlers
static void gen_onoff_get(struct bt_mesh_model *model,
                          struct bt_mesh_msg_ctx *ctx,
                          struct net_buf_simple *buf);
static void gen_onoff_set(struct bt_mesh_model *model,
                          struct bt_mesh_msg_ctx *ctx,
                          struct net_buf_simple *buf);

static const struct bt_mesh_model_op gen_onoff_ops[] = {
    { BT_MESH_MODEL_OP_2(0x82, 0x01), 0, gen_onoff_get },   // Get
    { BT_MESH_MODEL_OP_2(0x82, 0x02), 2, gen_onoff_set },   // Set
    BT_MESH_MODEL_OP_END,
};

// Publication context
static struct bt_mesh_model_pub gen_onoff_pub = {
    .dev_role = 0,
};

// Generic OnOff Server model
static struct bt_mesh_model gen_onoff_srv = {
    .id = 0x1000,  // BT_MESH_MODEL_ID_GEN_ONOFF_SRV
    .op = gen_onoff_ops,
    .pub = &gen_onoff_pub,
    .keys = { [0 ... (CONFIG_BT_MESH_MODEL_KEY_COUNT - 1)] = BT_MESH_KEY_UNUSED },
    .groups = { [0 ... (CONFIG_BT_MESH_MODEL_GROUP_COUNT - 1)] = BT_MESH_ADDR_UNASSIGNED },
};

// Model opcode handlers implementation
static void gen_onoff_get(struct bt_mesh_model *model,
                          struct bt_mesh_msg_ctx *ctx,
                          struct net_buf_simple *buf)
{
    // Handle GET request - send current state
    BT_MESH_MODEL_BUF_DEFINE rsp, BT_MESH_MODEL_OP_2(0x82, 0x01), 1);
    bt_mesh_model_msg_init(&rsp, BT_MESH_MODEL_OP_2(0x82, 0x01));
    net_buf_simple_add_u8(&rsp, g_onoff_state);  // Add current state
    
    bt_mesh_model_send(model, ctx, &rsp, NULL, NULL);
}

static void gen_onoff_set(struct bt_mesh_model *model,
                          struct bt_mesh_msg_ctx *ctx,
                          struct net_buf_simple *buf)
{
    uint8_t state = net_buf_simple_read_u8(buf);
    g_onoff_state = state;
    
    // Publish state change
    bt_mesh_model_publish(model);
}

// Composition
static struct bt_mesh_elem elements[] = {
    BT_MESH_ELEM(0, gen_onoff_srv, BT_MESH_MODEL_NONE),
};

static const struct bt_mesh_comp comp = {
    .cid = BL_COMP_ID,
    .pid = BL_PRODUCT_ID,
    .vid = 0x0001,
    .elem_count = ARRAY_SIZE(elements),
    .elem = elements,
};

// Initialize mesh
int ble_mesh_init(void)
{
    int err;
    
    // Initialize mesh stack
    err = bt_mesh_init(&prov, &comp);
    if (err < 0) {
        printf("Mesh init failed: %d\r\n", err);
        return err;
    }
    
    // Enable PB-ADV bearer for provisioning
    err = bt_mesh_prov_enable(BT_MESH_PROV_ADV);
    if (err < 0) {
        printf("Failed to enable provisioning bearer: %d\r\n", err);
        return err;
    }
    
    printf("BLE Mesh initialized\r\n");
    return 0;
}
```

### BLE Mesh Model Send Example

```c
#include "mesh.h"
#include "access.h"

// Send to a specific address
int send_onoff_set(uint16_t addr, uint16_t net_idx, uint16_t app_idx, uint8_t state)
{
    struct bt_mesh_msg_ctx ctx = {
        .net_idx = net_idx,
        .app_idx = app_idx,
        .addr = addr,
        .send_rel = true,
        .send_ttl = BT_MESH_TTL_DEFAULT,
    };
    
    BT_MESH_MODEL_BUF_DEFINE(buf, BT_MESH_MODEL_OP_2(0x82, 0x02), 1);
    bt_mesh_model_msg_init(&buf, BT_MESH_MODEL_OP_2(0x82, 0x02));
    net_buf_simple_add_u8(&buf, state);
    
    struct bt_mesh_send_cb cb = {
        .start = send_start_cb,
        .end = send_end_cb,
    };
    
    return bt_mesh_model_send(g_gen_onoff_cli, &ctx, &buf, &cb, NULL);
}

// Publish via model publication context
int publish_onoff_state(struct bt_mesh_model *model, uint8_t state)
{
    struct bt_mesh_model_pub *pub = model->pub;
    
    bt_mesh_model_msg_init(pub->msg, BT_MESH_MODEL_OP_2(0x82, 0x01));
    net_buf_simple_add_u8(pub->msg, state);
    
    return bt_mesh_model_publish(model);
}
```

### Coexistence Initialization Example

```c
#include "coex.h"

// Coex notify callback
static void coex_notify(void *env, struct coex_notify_args *args)
{
    switch (args->event) {
    case COEX_NTY_INITED:
        printf("Coex initialized\r\n");
        break;
    case COEX_NTY_RF_PRESENCE:
        printf("RF present, duration: %d ms\r\n", args->duration);
        break;
    case COEX_NTY_RF_ABSENCE:
        printf("RF absent\r\n");
        break;
    default:
        break;
    }
}

int coex_init_example(void)
{
    int ret;
    struct coex_evt_arg arg;
    
    // Initialize coex module
    ret = coex_init();
    if (ret != COEX_OK) {
        printf("Coex init failed: %d\r\n", ret);
        return ret;
    }
    
    // Send INIT event
    arg.role = COEX_ROLE_BT;
    arg.type = COEX_EVT_INIT;
    arg.arg.init.cb = coex_notify;
    arg.arg.init.env = NULL;
    
    ret = coex_event(&arg);
    if (ret != COEX_OK) {
        printf("Coex init event failed: %d\r\n", ret);
        return ret;
    }
    
    printf("Coex initialized successfully\r\n");
    return 0;
}
```

### Coex Activity Reporting Example

```c
#include "coex.h"

// Report BLE advertising activity
int report_ble_adv_activity(void)
{
    struct coex_evt_arg arg;
    
    arg.role = COEX_ROLE_BT;
    arg.type = COEX_EVT_SET_ACTIVITY;
    arg.arg.set_act.type = ACT_START_ADV;
    arg.arg.set_act.now = 1;  // Happening now
    
    return coex_event(&arg);
}

// Report WiFi scan activity
int report_wifi_scan_activity(void)
{
    struct coex_evt_arg arg;
    
    arg.role = COEX_ROLE_WIFI;
    arg.type = COEX_EVT_SET_ACTIVITY;
    arg.arg.set_act.type = ACT_STA_SCAN_START;
    arg.arg.set_act.now = 1;
    
    return coex_event(&arg);
}

// Report BT scan done
int report_bt_scan_done(void)
{
    struct coex_evt_arg arg;
    
    arg.role = COEX_ROLE_BT;
    arg.type = COEX_EVT_SET_ACTIVITY;
    arg.arg.set_act.type = ACT_BT_SCAN_DONE;
    arg.arg.set_act.now = 1;
    
    return coex_event(&arg);
}
```

### Complete Application Example

```c
#include "mesh.h"
#include "coex.h"
#include "FreeRTOS.h"
#include "task.h"

#define MESH_TASK_PRIORITY  5
#define MESH_TASK_STACK_SIZE 1024

static TaskHandle_t mesh_task_handle;

// Mesh task
static void mesh_task(void *param)
{
    int ret;
    
    // Initialize coexistence first
    ret = coex_init();
    if (ret != COEX_OK) {
        printf("[APP] Coex init failed\r\n");
        vTaskDelete(NULL);
        return;
    }
    
    // Report BT role to coex
    struct coex_evt_arg arg = {
        .role = COEX_ROLE_BT,
        .type = COEX_EVT_INIT,
        .arg.init.cb = NULL,
        .arg.init.env = NULL,
    };
    coex_event(&arg);
    
    // Initialize BLE Mesh
    ret = ble_mesh_init();
    if (ret < 0) {
        printf("[APP] BLE Mesh init failed\r\n");
        vTaskDelete(NULL);
        return;
    }
    
    // Report advertising start to coex
    report_ble_adv_activity();
    
    printf("[APP] BLE Mesh + Coex running\r\n");
    
    while (1) {
        // Mesh main loop processing
        vTaskDelay(pdMS_TO_TICKS(100));
    }
}

void app_main(void)
{
    BaseType_t ret;
    
    ret = xTaskCreate(mesh_task,
                      "mesh",
                      MESH_TASK_STACK_SIZE,
                      NULL,
                      MESH_TASK_PRIORITY,
                      &mesh_task_handle);
    
    if (ret != pdPASS) {
        printf("[APP] Failed to create mesh task\r\n");
    }
}
```

---

## Build Configuration

In your `proj.conf` or `CMakeLists.txt`:

```kconfig
# BLE Mesh configuration
CONFIG_BT=y
CONFIG_BT_MESH=y
CONFIG_BT_MESH_ADV_BUF_COUNT=60
CONFIG_BT_MESH_NODE_COUNT=128
CONFIG_BT_MESH_MODEL_KEY_COUNT=2
CONFIG_BT_MESH_APP_KEY_COUNT=2

# Coexistence configuration
CONFIG_COEX_WIFI_MODE=1  # TDMA mode
CONFIG_COEX_BT_MODE=1
CONFIG_COEX_THREAD_MODE=0
```

---

## Notes

1. **Mesh Priority**: Mesh ADV uses `CONFIG_BT_MESH_ADV_PRIO` (configMAX_PRIORITIES - 4) for task priority.

2. **Coex Priority**: The coex module handles RF time sharing between WiFi and BT/BLE. Activity events inform the coex scheduler about ongoing operations.

3. **Model Keys**: Models must be bound to AppKeys before they can send/receive messages.

4. **Provisioning**: Unprovisioned devices advertise on PB-ADV bearer until provisioned.

---

## References

- `bouffalo_sdk/components/wireless/bluetooth/blemesh/src/include/mesh.h`
- `bouffalo_sdk/components/wireless/bluetooth/blemesh/src/include/mesh_config.h`
- `bouffalo_sdk/components/wireless/bluetooth/blemesh/src/include/access.h`
- `bouffalo_sdk/components/wireless/bluetooth/blemesh/src/include/main.h`
- `bouffalo_sdk/components/wireless/bluetooth/blemesh/src/prov.h`
- `bouffalo_sdk/components/wireless/coex/coex.h`
