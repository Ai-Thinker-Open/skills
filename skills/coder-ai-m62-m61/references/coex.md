# Wi-Fi / BLE Coexistence (Coex)

## Overview

BL616/BL618 supports simultaneous Wi-Fi and BLE/Thread operation. The `coex` module implements time-sliced scheduling of radio resources to avoid mutual interference. This module is located in `components/wireless/coex/`.

## Header File

```c
#include "coex.h"
```

## Coexistence Modes

```c
#define COEX_MODE_TDMA    1  // Time Division Multiple Access mode (default)
#define COEX_MODE_PTI     2  // Priority Time Interval mode
```

### TDMA Mode

Time Division Multiple Access mode divides time into fixed slots. Wi-Fi, BLE, and Thread are allocated Tx/Rx time according to configured ratios.

### PTI Mode

Priority Time Interval mode, implemented via `coex_pti.c`, supports priority arbitration.

## Coexistence Roles

```c
enum coex_role {
    COEX_ROLE_BT = 0,      // Bluetooth
    COEX_ROLE_WIFI,        // Wi-Fi
    COEX_ROLE_THREAD,      // Thread
    COEX_ROLE_DUMMY,
    COEX_ROLE_MAX,
};
```

## Event Types

```c
enum coex_event {
    COEX_EVT_INIT = 0,           // Initialize wireless module
    COEX_EVT_DEINIT,             // Deinitialize wireless module
    COEX_EVT_SET_ACTIVITY,       // Set wireless module activity
    COEX_EVT_GET_ACTIVITY,       // Get coexistence module activity
    COEX_EVT_TMR_ISR_HANDLE,     // Timer interrupt handler
    COEX_EVT_FUNC_CALL,          // Call function in coexistence module
    COEX_EVT_MAX,
};
```

## Activity Types

Activity events for Wi-Fi, BLE, and Thread, used to notify the coexistence scheduler:

```c
enum coex_event_activity {
    /* BLE */
    ACT_START_ADV,           // BLE advertising started

    /* BT Classic */
    ACT_BT_SCAN_START,       // BT scan started
    ACT_BT_SCAN_DONE,        // BT scan completed
    ACT_BT_CONNECT_START,    // BT connection started
    ACT_BT_CONNECT_DONE_OK,  // BT connection succeeded
    ACT_BT_CONNECT_DONE_FAIL,// BT connection failed
    ACT_BT_DISCONNECT_START, // BT disconnection started
    ACT_BT_DISCONNECT_DONE,  // BT disconnection completed
    ACT_BT_A2DP_START,      // A2DP audio started
    ACT_BT_A2DP_STOP,       // A2DP audio stopped

    /* Wi-Fi STA */
    ACT_STA_SCAN_START,       // Wi-Fi scan started
    ACT_STA_SCAN_DONE,       // Wi-Fi scan completed
    ACT_STA_CONNECT_START,   // Wi-Fi connection started
    ACT_STA_CONNECT_DONE_OK, // Wi-Fi connection succeeded
    ACT_STA_CONNECT_DONE_FAIL,// Wi-Fi connection failed
    ACT_STA_DISCONNECT_START,// Wi-Fi disconnection started
    ACT_STA_DISCONNECT_DONE, // Wi-Fi disconnection completed
    ACT_STA_DPSM_START,      // Power save state machine started
    ACT_STA_DPSM_YIELD,     // Power save state machine yield
    ACT_STA_DPSM_STOP,      // Power save state machine stopped
    ACT_STA_ROC_REQ,        // Remain-on-Channel request
    ACT_STA_TBTT_UPDATE,    // TBTT update (Beacon sync)

    /* Wi-Fi AP */
    ACT_SOFTAP_START,        // SoftAP started
    ACT_SOFTAP_STOP,         // SoftAP stopped
    ACT_SOFTAP_TBTT_UPDATE,  // AP TBTT update

    /* Thread */
    ACT_START_PAN,           // PAN started
    ACT_STOP_PAN,            // PAN stopped

    /* Dummy */
    ACT_DUMMY_ADD_ACT,       // Dummy activity added
    ACT_DUMMY_DEL_ACT,       // Dummy activity deleted
};
```

## Callback Notifications

The coexistence module notifies upper layers of events via callbacks:

```c
struct coex_notify_args {
    int event;      // @COEX_NTY_* event code
    int duration;   // Duration (ms)
};

typedef void (*coex_notify_cb)(void *env, struct coex_notify_args *args);
```

## Notification Events

```c
enum coex_notify {
    COEX_NTY_INITED = 0,      // Coexistence initialized
    COEX_NTY_DEINITED,        // Coexistence deinitialized
    COEX_NTY_RF_PRESENCE,     // RF in use
    COEX_NTY_RF_ABSENCE,      // RF idle
    COEX_NTY_MAX,
};
```

## Event Argument Union

```c
union evt_arg {
    struct {              // INIT event
        coex_notify_cb cb;
        void *env;
    } init;
    struct {              // SET_ACTIVITY event
        int type;         // Activity type @ coex_event_activity
        int now;          // Occurrence time
    } set_act;
    struct {              // TMR_ISR event
        uint64_t time;
        void *env;
    } tmr_isr;
    struct {              // FUNC_CALL event
        coex_func_call func;
        int arg[4];
    } func_call;
};

struct coex_evt_arg {
    int role;      // @ coex_role
    int type;      // @ coex_event
    union evt_arg arg;
};
```

## Core API

### Initialization / Deinitialization

```c
int coex_init(void);    // Returns COEX_OK (0) or COEX_FAIL (-1)
int coex_deinit(void);
```

### Event Notification

```c
int coex_event(struct coex_evt_arg *arg);
```

Report wireless module events (Wi-Fi scan/BT connection, etc.) to the coexistence module. The coexistence scheduler adjusts time-slice allocation accordingly.

## Working Code Examples

### Basic Initialization

```c
#include "coex.h"

static void coex_notify(void *env, struct coex_notify_args *args)
{
    switch (args->event) {
    case COEX_NTY_INITED:
        printf("Coex initialized\r\n");
        break;
    case COEX_NTY_RF_PRESENCE:
        printf("RF active, duration=%dms\r\n", args->duration);
        break;
    case COEX_NTY_RF_ABSENCE:
        printf("RF idle\r\n");
        break;
    }
}

void coex_example(void)
{
    struct coex_evt_arg evt;
    int ret;

    /* Initialize coexistence module */
    ret = coex_init();
    if (ret != COEX_OK) {
        printf("coex init failed\r\n");
        return;
    }

    /* Register notification callback */
    evt.role = COEX_ROLE_WIFI;
    evt.type = COEX_EVT_INIT;
    evt.arg.init.cb = coex_notify;
    evt.arg.init.env = NULL;
    coex_event(&evt);

    /* ... Wi-Fi and BLE business logic ... */

    coex_deinit();
}
```

### Notifying Coex During Wi-Fi Scan

```c
void wifi_scan_with_coex(void)
{
    struct coex_evt_arg evt;

    /* Notify BLE: Wi-Fi is about to scan */
    evt.role = COEX_ROLE_WIFI;
    evt.type = COEX_EVT_SET_ACTIVITY;
    evt.arg.set_act.type = ACT_STA_SCAN_START;
    evt.arg.set_act.now = 1;
    coex_event(&evt);

    /* Execute Wi-Fi scan */
    wifi_mgmr_sta_scan(NULL);

    /* Notify BLE: Wi-Fi scan complete */
    evt.arg.set_act.type = ACT_STA_SCAN_DONE;
    coex_event(&evt);
}
```

### Notifying Coex During BLE Connection

```c
void ble_connect_with_coex(void)
{
    struct coex_evt_arg evt;

    /* Notify Wi-Fi: BLE is about to connect */
    evt.role = COEX_ROLE_BT;
    evt.type = COEX_EVT_SET_ACTIVITY;
    evt.arg.set_act.type = ACT_BT_CONNECT_START;
    evt.arg.set_act.now = 1;
    coex_event(&evt);

    /* Execute BLE connection */
    ble_gap_connect(...);

    /* Notify on successful connection */
    evt.arg.set_act.type = ACT_BT_CONNECT_DONE_OK;
    coex_event(&evt);
}
```

### Priority Handling During A2DP Audio Playback

```c
void a2dp_playback_with_coex(void)
{
    struct coex_evt_arg evt;

    /* A2DP start — assign higher priority */
    evt.role = COEX_ROLE_BT;
    evt.type = COEX_EVT_SET_ACTIVITY;
    evt.arg.set_act.type = ACT_BT_A2DP_START;
    evt.arg.set_act.now = 1;
    coex_event(&evt);

    /* During A2DP streaming, Wi-Fi scan will have lower priority */

    /* A2DP stop */
    evt.arg.set_act.type = ACT_BT_A2DP_STOP;
    coex_event(&evt);
}
```

## Configuration Macros

Coexistence mode configured via Kconfig:

| Macro | Default | Description |
|----|--------|------|
| `CONFIG_COEX_WIFI_MODE` | `0` | Wi-Fi coexistence mode (0=off, 1=TDMA, 2=PTI) |
| `CONFIG_COEX_THREAD_MODE` | `0` | Thread coexistence mode |
| `CONFIG_COEX_BT_MODE` | `0` | BT/BLE coexistence mode |
| `CONFIG_COEX_TDMA_NONE` | `COEX_NONE_NULL` | Behavior when idle |

## Coexistence Scheduling Policy

1. **Time Slicing**: In TDMA mode, the scheduler divides time into fixed slots; ratios can be specified in configuration files
2. **Priority Arbitration**: In PTI mode, high-priority activities (such as A2DP) can preempt time slices from low-priority activities (such as Wi-Fi scan)
3. **Activity Reporting**: Wi-Fi/BLE/Thread drivers report current activities via `coex_event()`, and the scheduler adjusts dynamically
4. **RF Status**: Upper layers are notified via `COEX_NTY_RF_PRESENCE/_ABSENCE`, allowing applications to decide whether to initiate new activities

## Related Documents

- [wifi_mgmr](./wifi_mgmr.md) — Wi-Fi Manager (internally calls coex)
- [BLE](./ble.md) — BLE Controller
- [bt_a2dp](./bt_a2dp.md) — A2DP Audio Configuration
