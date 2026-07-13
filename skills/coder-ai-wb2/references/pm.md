# Power Management (PM) API Reference

> Source file: `components/network/wifi_hosal/include/wifi_hosal.h` (partial)  
> BL602 power management involves RF, Wi-Fi sleep, PDS (Power Down Sleep) and other low-power mechanisms.

---

## Overview

BL602 Power Management Architecture:

```
+--------------------------------------+
|           Application                |
+--------------------------------------+
|     Wi-Fi / BLE / System PM          |
+--------------------------------------+
|   RF (Radio Frequency)               |
|   PDS (Power Down Sleep)             |
|   Normal Run                         |
+--------------------------------------+
```

**Low Power Levels**:

| Level | Mode | Power Consumption | Description |
|-------|------|-------------------|-------------|
| `PM_LEVEL_NONE` | Full speed | Highest | Wi-Fi transmitting |
| `PM_LEVEL_1` | Light sleep | Low | RF stays connected |
| `PM_LEVEL_2` | Deep sleep | Ultra low | RAM retained, wake sources only |
| `PM_MODE_MAX` | Off | Lowest | Requires reinitialization |

---

## Wi-Fi HOSAL PM Functions

The following functions come from `wifi_hosal.h`:

### `wifi_hosal_pm_init`

Initialize power management.

```c
int wifi_hosal_pm_init(void);
```

---

### `wifi_hosal_pm_event_register`

Register PM event callback.

```c
int wifi_hosal_pm_event_register(enum PM_EVEMT event,
                                   uint32_t code,
                                   uint32_t cap_bit,
                                   uint16_t priority,
                                   bl_pm_cb_t ops,
                                   void *arg,
                                   enum PM_EVENT_ABLE enable);
```

---

### `wifi_hosal_pm_deinit`

Shutdown power management.

```c
int wifi_hosal_pm_deinit(void);
```

---

### `wifi_hosal_pm_state_run`

Enter running state (exit low power).

```c
int wifi_hosal_pm_state_run(void);
```

---

### `wifi_hosal_pm_capacity_set`

Set low power level.

```c
int wifi_hosal_pm_capacity_set(enum PM_LEVEL level);
```

| `level` | Description |
|---------|-------------|
| `PM_LEVEL_NONE` | Exit low power |
| `PM_LEVEL_1` | Light sleep |
| `PM_LEVEL_2` | Deep sleep |

---

### `wifi_hosal_pm_post_event`

Post a PM event.

```c
int wifi_hosal_pm_post_event(enum PM_EVEMT event, uint32_t code, uint32_t *retval);
```

---

### `wifi_hosal_pm_event_switch`

Enable/disable PM events.

```c
int wifi_hosal_pm_event_switch(enum PM_EVEMT event, uint32_t code,
                                 enum PM_EVENT_ABLE enable);
```

---

## RF Power Control

### `wifi_hosal_rf_turn_on`

Turn on RF radio.

```c
int wifi_hosal_rf_turn_on(void *arg);
```

---

### `wifi_hosal_rf_turn_off`

Turn off RF radio.

```c
int wifi_hosal_rf_turn_off(void *arg);
```

---

## Wi-Fi MGMR Power Interface

The following functions come from `wifi_mgmr_ext.h`:

### `wifi_mgmr_sta_ps_enter`

Wi-Fi STA enters low power.

```c
int wifi_mgmr_sta_ps_enter(uint32_t ps_level);
```

> Parameters: `PS_MODE_OFF` (off), `PS_MODE_ON` (normal), `PS_MODE_ON_DYN` (dynamic)

---

### `wifi_mgmr_sta_ps_exit`

Wi-Fi STA exits low power.

```c
int wifi_mgmr_sta_ps_exit(void);
```

---

### `wifi_mgmr_set_wifi_active_time`

Set Wi-Fi active time.

```c
int wifi_mgmr_set_wifi_active_time(uint32_t ms);
```

---

### `wifi_mgmr_set_listen_interval`

Set listen interval (number of beacons).

```c
int wifi_mgmr_set_listen_interval(uint16_t itv);
```

---

## Usage Example

```c
#include "wifi_hosal.h"

// Initialize PM
wifi_hosal_pm_init();

// Set low power level
wifi_hosal_pm_capacity_set(PM_LEVEL_1);

// Wi-Fi low power configuration
wifi_mgmr_set_wifi_active_time(100);    // Active 100ms
wifi_mgmr_set_listen_interval(10);      // Wake every 10 beacons
wifi_mgmr_sta_ps_enter(PS_MODE_ON_DYN); // Enter dynamic low power mode

// Exit low power
wifi_mgmr_sta_ps_exit();
wifi_hosal_pm_state_run();

// Turn off RF (extreme power saving, for specific scenarios only)
wifi_hosal_rf_turn_off(NULL);

// Turn RF back on
wifi_hosal_rf_turn_on(NULL);
```
