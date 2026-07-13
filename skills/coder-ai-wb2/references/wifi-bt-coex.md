# wifi-bt-coex - WiFi/Bluetooth Coexistence Component

## Overview

wifi-bt-coex manages the coexistence between WiFi and Bluetooth wireless signals on Bouffalo chips. Since WiFi (2.4GHz) and Bluetooth share the same frequency band, this component handles priority negotiation and time-division multiplexing to minimize interference when both radios operate simultaneously.

## Location

```
components/network/wifi_bt_coex/
```

## Key Files

- `include/wifi_bt_coex.h` - Main header with API definitions
- `src/wifi_bt_coex.c` - Core implementation
- `src/wifi_bt_coex_ctx.c` - Context management
- `src/wifi_bt_coex_cli.c` - CLI interface
- `src/wifi_bt_coex_impl_bl602.c` - BL602 platform implementation

## Architecture

The module uses a platform-specific implementation pattern with a common API:

```
wifi_bt_coex.c (common API)
       |
       v
wifi_bt_coex_impl_*.c (platform-specific)
```

### Force Modes

| Mode | Description |
|------|-------------|
| `WIFI_BT_COEX_FORCE_MODE_PTA_FORCE` | PTA (Packet Traffic Arbitration) forced mode |
| `WIFI_BT_COEX_FORCE_MODE_PTI_DEFAULT_FORCE` | PTI default priority forced |
| `WIFI_BT_COEX_FORCE_MODE_PTI_PRIORITY_FORCE` | PTI priority forced |
| `WIFI_BT_COEX_FORCE_MODE_PTI_PRIORITY_FORCE2` | PTI priority forced (variant 2) |

### Events

| Event | Description |
|-------|-------------|
| `WIFI_BT_COEX_EVENT_BT_A2DP_UNDERRUN` | BT A2DP underrun event |

## Core API

### Coexistence Control

```c
int wifi_bt_coex_dump_all(void);
```

Dumps all coexistence configuration and status information.

**Returns:** 0 on success

---

```c
int wifi_bt_coex_force_wlan(void);
```

Forces priority to WiFi, giving WLAN maximum bandwidth.

**Returns:** 0 on success

---

```c
int wifi_bt_coex_force_bt(void);
```

Forces priority to Bluetooth, ensuring BT/BLE performance.

**Returns:** 0 on success

---

```c
int wifi_bt_coex_force_mode(enum WIFI_BT_COEX_FORCE_MODE mode);
```

Sets the coexistence force mode.

**Parameters:**
- `mode` - One of the `WIFI_BT_COEX_FORCE_MODE` enum values

**Returns:** 0 on success, -1 on invalid mode

---

### Event Notification

```c
int wifi_bt_coex_event_notify(enum WIFI_BT_COEX_EVENT event, void *event_arg);
```

Notifies the coexistence module of BT/WiFi events that may require priority adjustment.

**Parameters:**
- `event` - Event type
- `event_arg` - Event-specific argument (may be NULL)

**Returns:** Implementation-specific result

## Context Structure

```c
struct wifi_bt_coex_ctx {
    TimerHandle_t coexTimer;        // Coexistence timer
    uint32_t timer_now;              // Current time
    uint32_t timer_max;              // Maximum time window
    uint32_t timer_toggle_start;     // Toggle start time
    uint32_t timer_toggle_end;       // Toggle end time
    uint32_t timeus_last_called;     // Last function call time
    uint32_t time_step_inc;          // Time step increment
    uint32_t time_step_dec;          // Time step decrement
};
```

## Usage Notes

1. Initialize the CLI for debugging: `wifi_bt_coex_cli_init()`
2. Use `wifi_bt_coex_dump_all()` to debug coexistence issues
3. For A2DP streaming with WiFi, notify via `wifi_bt_coex_event_notify()` when underruns occur
4. Platform implementations handle the actual hardware registers (PTA/PTI)

## Platform Differences

- **BL602**: PTA-based arbitration with configurable priority control
