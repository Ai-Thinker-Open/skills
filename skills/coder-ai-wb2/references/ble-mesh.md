# BLE Mesh API Reference

> Source files: `components/network/ble/blemesh/src/mesh.h` etc.  
> BLE Mesh is a low-power mesh network protocol based on BLE 5.0, suitable for large-scale IoT device networking.

## Overview

BLE Mesh network architecture:

```
┌─────────┐     ┌─────────┐     ┌─────────┐
│ Node A  │────▶│ Node B  │────▶│ Node C  │
│(Relay)  │     │(Relay)  │     │(Leaf)   │
└─────────┘     └─────────┘     └─────────┘
```

**Role types**: Provisioner, Node, Relay, Proxy, Friend, Low Power Node

---

## Initialization

### `ble_mesh_init`

Initialize the BLE Mesh protocol stack.

```c
int ble_mesh_init(void);
```

---

## Configuration

### `ble_mesh_prov_enable`

Enable BLE Mesh Provisioning.

```c
int ble_mesh_prov_enable(void);
```

---

### `ble_mesh_config_enable`

Enable BLE Mesh Configuration model.

```c
int ble_mesh_config_enable(void);
```

---

### `ble_mesh_app_key_add`

Add an application key.

```c
int ble_mesh_app_key_add(uint16_t net_idx, uint16_t app_idx, const uint8_t key[16]);
```

| Parameter | Description |
|-----------|-------------|
| `net_idx` | Network key index |
| `app_idx` | Application key index |
| `key` | 128-bit key |

---

## Sending and Receiving

### `ble_mesh_model_publish`

Publish a message (model initiated sending).

```c
int ble_mesh_model_publish(uint16_t elem_idx, uint16_t mod_id,
                            uint16_t opcode, size_t len, uint8_t *data);
```

---

### `ble_mesh_model_send`

Send a model message.

```c
int ble_mesh_model_send(uint16_t dst, uint16_t app_idx,
                        uint16_t elem_idx, uint16_t mod_id,
                        uint16_t opcode, size_t len, const uint8_t *data);
```

| Parameter | Description |
|-----------|-------------|
| `dst` | Destination unicast/group address |
| `app_idx` | Application key index |
| `elem_idx` | Element index |
| `mod_id` | Model ID |
| `opcode` | Opcode |
| `data` | Message payload |

---

## Subscription

### `ble_mesh_model_sub_add`

Add a subscription address.

```c
int ble_mesh_model_sub_add(uint16_t elem_idx, uint16_t sub_addr,
                            uint16_t mod_id, uint16_t cid);
```

---

## Generic Attributes

### `ble_mesh_gen_onoff_get`

Get generic on/off state (OnOff Server).

```c
int ble_mesh_gen_onoff_get(uint16_t addr, uint8_t *onoff);
```

---

### `ble_mesh_gen_onoff_set`

Set generic on/off state.

```c
int ble_mesh_gen_onoff_set(uint16_t addr, uint8_t onoff, uint8_t ack);
```

| Parameter | Description |
|-----------|-------------|
| `addr` | Target node address |
| `onoff` | `0` = OFF, `1` = ON |
| `ack` | `1` = request acknowledgment |

---

### `ble_mesh_gen_level_get` / `ble_mesh_gen_level_set`

Get/Set generic level (0~65535).

```c
int ble_mesh_gen_level_get(uint16_t addr, int16_t *level);
int ble_mesh_gen_level_set(uint16_t addr, int16_t level, uint8_t ack);
```

---

## Configuration Client Operations

### `ble_mesh_cfg_client_get`

Get node configuration.

```c
int ble_mesh_cfg_client_get(uint16_t dst, uint16_t elem_idx, uint8_t opcode);
```

---

### `ble_mesh_cfg_client_set`

Set node configuration.

```c
int ble_mesh_cfg_client_set(uint16_t dst, uint16_t elem_idx,
                             uint8_t opcode, size_t len, const uint8_t *data);
```

---

## Gateway/Proxy

### `ble_mesh_proxy_filter_set`

Set Proxy filter type.

```c
int ble_mesh_proxy_filter_set(uint16_t net_idx, uint8_t filter_type);
```

> `filter_type`: `PROXY_FILTER_WHITELIST` / `PROXY_FILTER_BLACKLIST`

---

## Health Related

### `ble_mesh_health_fault_get`

Get health fault status.

```c
int ble_mesh_health_fault_get(uint16_t addr, uint8_t test_id, uint8_t *faults);
```

---

### `ble_mesh_health_attention_set`

Set node attention timer.

```c
int ble_mesh_health_attention_set(uint16_t addr, uint8_t attention);
```

---

## Usage Example

```c
#include "mesh.h"

// Initialize BLE Mesh
ble_mesh_init();

// As a Provisioner
ble_mesh_prov_enable();
ble_mesh_config_enable();

// Add keys
uint8_t net_key[16] = {0x00, 0x11, 0x22, /*...*/};
uint8_t app_key[16] = {0xAA, 0xBB, 0xCC, /*...*/};
ble_mesh_app_key_add(0, 0, app_key);

// Control light node (unicast address 0x0002) on/off
ble_mesh_gen_onoff_set(0x0002, 1, 1); // Turn on and request acknowledgment

// Get light state
uint8_t state;
ble_mesh_gen_onoff_get(0x0002, &state);
printf("Light state: %s\r\n", state ? "ON" : "OFF");
```

## Common Model IDs

| Model | ID | Description |
|-------|----|-------------|
| Generic OnOff Server | `0x1000` | On/Off control |
| Generic Level Server | `0x1002` | Level control |
| Light Lightness Server | `0x1300` | Brightness control |
| Light CTL Server | `0x1303` | Color temperature control |
| Sensor Server | `0x1100` | Sensor data |
| Time Server | `0x1200` | Time service |
| Configuration Server | `0x0000` | Configuration model (required) |
| Health Server | `0x0002` | Health model (required) |
