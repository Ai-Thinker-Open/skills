# wifi-hosal - WiFi Hardware Abstraction Service Layer

## Overview

wifi-hosal is a WiFi Hardware Abstraction Service Layer (HAL) that provides a unified interface for WiFi operations including eFuse access, RF control, ADC operations, and power management. It wraps platform-specific implementations behind a common API.

## Location

```
components/network/wifi_hosal/
```

## Key Files

- `include/wifi_hosal.h` - Main header with API definitions
- `wifi_hosal.c` - Main implementation
- `port/wifi_hosal_bl602.c` - BL602 platform port

## Architecture

The wifi-hosal module provides a function table `g_wifi_hosal_funcs` that contains platform-specific implementations:

```c
struct wifi_hosal_funcs {
    int (*efuse_read_mac)(uint8_t mac[6]);
    int (*rf_turn_on)(void *arg);
    int (*rf_turn_off)(void *arg);
    hosal_adc_dev_t* (*adc_device_get)(void);
    int (*adc_tsen_value_get)(hosal_adc_dev_t *adc);
    int (*pm_init)(void);
    int (*pm_event_register)(enum PM_EVEMT event, uint32_t code, 
                              uint32_t cap_bit, uint16_t pirority, 
                              bl_pm_cb_t ops, void *arg, 
                              enum PM_EVENT_ABLE enable);
    int (*pm_deinit)(void);
    int (*pm_state_run)(void);
    int (*pm_capacity_set)(enum PM_LEVEL level);
    int (*pm_post_event)(enum PM_EVEMT event, uint32_t code, uint32_t *retval);
    int (*pm_event_switch)(enum PM_EVEMT event, uint32_t code, 
                           enum PM_EVENT_ABLE enable);
};
```

## API Functions

### eFuse Operations

```c
int wifi_hosal_efuse_read_mac(uint8_t mac[6]);
```
Reads the MAC address from eFuse. The mac buffer must be at least 6 bytes.

**Returns:** 0 on success, negative errno on failure

### RF Operations

```c
int wifi_hosal_rf_turn_on(void *arg);
int wifi_hosal_rf_turn_off(void *arg);
```
Controls RF (Radio Frequency) module power state.

**Returns:** 0 on success, negative errno on failure

### ADC Operations

```c
hosal_adc_dev_t* wifi_hosal_adc_device_get(void);
int wifi_hosal_adc_tsen_value_get(hosal_adc_dev_t *adc);
```
Provides access to ADC device for temperature sensing and other analog measurements.

**Returns:** 
- `wifi_hosal_adc_device_get()` - Pointer to ADC device or NULL
- `wifi_hosal_adc_tsen_value_get()` - Temperature sensor value or negative errno

### Power Management Functions

```c
int wifi_hosal_pm_init(void);
int wifi_hosal_pm_deinit(void);
int wifi_hosal_pm_state_run(void);
```
Initialize/deinitialize power management and trigger state transitions.

**Returns:** 0 on success, negative errno on failure

```c
int wifi_hosal_pm_capacity_set(enum PM_LEVEL level);
```
Set power capacity level.

**Parameters:**
- `level` - PM_LEVEL_LIGHT, PM_LEVEL_MEDIUM, PM_LEVEL_HIGH, etc.

**Returns:** 0 on success, negative errno on failure

```c
int wifi_hosal_pm_event_register(enum PM_EVEMT event, uint32_t code, 
                                  uint32_t cap_bit, uint16_t priority,
                                  bl_pm_cb_t ops, void *arg, 
                                  enum PM_EVENT_ABLE enable);
```
Register a power management event callback.

**Returns:** 0 on success, negative errno on failure

```c
int wifi_hosal_pm_post_event(enum PM_EVEMT event, uint32_t code, uint32_t *retval);
```
Post a power management event.

**Returns:** 0 on success, negative errno on failure

```c
int wifi_hosal_pm_event_switch(enum PM_EVEMT event, uint32_t code, 
                                enum PM_EVENT_ABLE enable);
```
Enable or disable a power management event.

**Returns:** 0 on success, negative errno on failure

## Power Management Levels

```c
enum PM_LEVEL {
    PM_LEVEL_NONE,      // No power management
    PM_LEVEL_LIGHT,     // Light sleep
    PM_LEVEL_MEDIUM,    // Medium power mode
    PM_LEVEL_DEEP,      // Deep sleep
    // ... platform-specific levels
};
```

## Power Management Events

```c
enum PM_EVEMT {
    PM_EVENT_WAKEUP,    // Wake up event
    PM_EVENT_SLEEP,     // Sleep event
    PM_EVENT_SHUTDOWN,  // Shutdown event
    // ... platform-specific events
};
```

## Usage Example

```c
#include "wifi_hosal.h"

void example_wifi_init(void)
{
    uint8_t mac[6];
    
    // Read MAC address from eFuse
    if (wifi_hosal_efuse_read_mac(mac) == 0) {
        printf("MAC: %02x:%02x:%02x:%02x:%02x:%02x\n",
               mac[0], mac[1], mac[2], mac[3], mac[4], mac[5]);
    }
    
    // Turn on RF
    wifi_hosal_rf_turn_on(NULL);
    
    // Get ADC device for temperature sensing
    hosal_adc_dev_t *adc = wifi_hosal_adc_device_get();
    if (adc) {
        int temp = wifi_hosal_adc_tsen_value_get(adc);
        printf("Temperature: %d\n", temp);
    }
    
    // Initialize power management
    wifi_hosal_pm_init();
    
    // Set power level
    wifi_hosal_pm_capacity_set(PM_LEVEL_MEDIUM);
}
```

## Dependencies

- `hosal_adc.h` - ADC device definitions
- `bl_pm.h` - Power management definitions

## Related Components

- **hosal** - Hardware abstraction layer for other peripherals
- **wifi** - WiFi stack and manager
- **yloop** - Event loop for async notifications
