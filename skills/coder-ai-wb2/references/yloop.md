# yloop - Event Loop Component

## Overview

yloop is an event loop component for AliOS Things (aos), providing a unified event-driven programming model for embedded systems. It manages system events, timers, and asynchronous operations.

## Location

```
components/stage/yloop/
```

## Key Files

- `include/aos/yloop.h` - Main header with API definitions
- `include/yloop_types.h` - Internal type definitions
- `src/yloop.c` - Core event loop implementation
- `src/local_event.c` - Local event handling
- `src/device.c` - Device event handling
- `src/select.c` - Select/poll implementation
- `src/aos_freertos.c` - FreeRTOS adapter

## Event Types

### System Events (EV_SYS = 0x0001)
| Code | Name | Description |
|------|------|-------------|
| 1 | CODE_SYS_ON_STARTING | System starting |
| 2 | CODE_SYS_ON_START_COMPLETED | System started |
| 3 | CODE_SYS_ON_IDLE | System idle |
| 4 | CODE_SYS_ON_START_FAILED | System start failed |
| 5 | CODE_SYS_ON_START_UOTA | OTA start |
| 6 | CODE_SYS_ON_ALINK_ONLINE | Cloud online |
| 7 | CODE_SYS_ON_ALINK_OFFLINE | Cloud offline |

### WiFi Events (EV_WIFI = 0x0002)
| Code | Name | Description |
|------|------|-------------|
| 1 | CODE_WIFI_ON_INIT_DONE | WiFi init completed |
| 2 | CODE_WIFI_ON_MGMR_DONE | WiFi manager ready |
| 3 | CODE_WIFI_CMD_RECONNECT | Reconnect command |
| 4 | CODE_WIFI_ON_CONNECTED | Connected to AP |
| 5 | CODE_WIFI_ON_DISCONNECT | Disconnected |
| 6 | CODE_WIFI_ON_PRE_GOT_IP | About to get IP |
| 7 | CODE_WIFI_ON_GOT_IP | Got IP address |
| 8 | CODE_WIFI_ON_CONNECTING | Connecting to AP |
| 9 | CODE_WIFI_ON_SCAN_DONE | Scan completed |
| 11 | CODE_WIFI_ON_AP_STARTED | AP mode started |
| 12 | CODE_WIFI_ON_AP_STOPPED | AP mode stopped |

### Other Events
- `EV_MESH (0x0003)` - Mesh network events
- `EV_UDATA (0x0004)` - uData service events
- `EV_CLI (0x0005)` - CLI events
- `EV_IR (0x0006)` - IR events
- `EV_ADCKEY (0x0010)` - ADC key events
- `EV_USER (0x1000)` - User-defined events start

## Core API

### Event Loop Management

```c
// Initialize event loop
aos_loop_t aos_loop_init(void);

// Get current event loop
aos_loop_t aos_current_loop(void);

// Start event loop (blocking)
void aos_loop_run(void);

// Exit event loop
void aos_loop_exit(void);

// Free event loop resources
void aos_loop_destroy(void);
```

### Event Registration

```c
// Register event filter callback
int aos_register_event_filter(uint16_t type, aos_event_cb cb, void *priv);

// Unregister event filter
int aos_unregister_event_filter(uint16_t type, aos_event_cb cb, void *priv);
```

### Event Posting

```c
// Post local event
int aos_post_event(uint16_t type, uint16_t code, unsigned long value);
```

### Delayed Actions

```c
// Post delayed action (ms milliseconds)
int aos_post_delayed_action(int ms, aos_call_t action, void *arg);

// Cancel delayed action
void aos_cancel_delayed_action(int ms, aos_call_t action, void *arg);
```

### Poll File Descriptors

```c
// Register poll read callback
int aos_poll_read_fd(int fd, aos_poll_call_t action, void *param);

// Cancel poll read
void aos_cancel_poll_read_fd(int fd, aos_poll_call_t action, void *param);
```

### Scheduled Calls

```c
// Schedule callback in next event loop (from any context)
int aos_schedule_call(aos_call_t action, void *arg);

// Schedule callback in specific event loop
int aos_loop_schedule_call(aos_loop_t *loop, aos_call_t action, void *arg);
```

### Work Queue

```c
// Schedule work in workqueue
void *aos_loop_schedule_work(int ms, aos_call_t action, void *arg1,
                             aos_call_t fini_cb, void *arg2);

// Cancel work
void aos_cancel_work(void *work, aos_call_t action, void *arg1);
```

## Event Structure

```c
typedef struct {
    uint32_t time;        // Timestamp (auto-filled)
    uint16_t type;         // Event type (< 0x1000 for system)
    uint16_t code;         // Event code (defined by type)
    unsigned long value;   // Event value
    unsigned long extra;   // Extra data
} input_event_t;
```

## Callback Types

```c
// Event callback
typedef void (*aos_event_cb)(input_event_t *event, void *private_data);

// Delayed execution callback
typedef void (*aos_call_t)(void *arg);

// Poll file descriptor callback
typedef void (*aos_poll_call_t)(int fd, void *arg);
```

## Usage Example

```c
#include <aos/yloop.h>

void wifi_event_handler(input_event_t *event, void *priv)
{
    if (event->type == EV_WIFI) {
        switch (event->code) {
            case CODE_WIFI_ON_CONNECTED:
                printf("WiFi connected\n");
                break;
            case CODE_WIFI_ON_GOT_IP:
                printf("Got IP: %lu\n", event->value);
                break;
            case CODE_WIFI_ON_DISCONNECT:
                printf("WiFi disconnected\n");
                break;
        }
    }
}

void app_main(void)
{
    // Register WiFi event handler
    aos_register_event_filter(EV_WIFI, wifi_event_handler, NULL);
    
    // Start event loop
    aos_loop_run();
}
```
