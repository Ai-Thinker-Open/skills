# BL616/BL618 Power Management & Clock Gating Guide

Power management (PM) for BL616/BL618 is handled through multiple layers:
- **PM Manager** (`pm_manager.c/h`) - Sleep check callbacks and tickless idle
- **Low Power (LP) API** (`bl616cl_lp.h`) - Sleep/hibernate, wake sources
- **Tickless Mode** (`tickless.c`) - FreeRTOS tickless idle integration
- **Clock Gating** - Peripheral clock control

---

## 1. PM Init

### `bl_pm_init()` - WiFi Power Manager Init

From `bflb_pm.h` (wifi_hosal):

```c
int bl_pm_init(void);
```

Initializes the WiFi power management subsystem. This must be called before using any PM features.

### `pm_sys_init()` - System PM Init

From `pm_manager.h`:

```c
int pm_sys_init(void);
```

Initializes the OS power management system (creates internal tasks, sets up memory pools).

---

## 2. Sleep / Hibernate

### `bl_lp_fw_enter()` - Enter Low Power Sleep

From `bl616cl_lp.h`:

```c
int bl_lp_fw_enter(bl_lp_fw_cfg_t *bl_lp_fw_cfg);
```

Enters the firmware-controlled low power mode. Configuration structure:

```c
typedef struct {
    uint8_t tim_wakeup_en;       /* TIM bit wakeup enable */
    uint8_t rtc_wakeup_en;       /* RTC timer wakeup enable */
    uint32_t rtc_wakeup_cmp_cnt;  /* RTC compare count */
    uint32_t rtc_timeout_us;     /* RTC timeout in microseconds */
    uint8_t dtim_num;            /* DTIM number */
    uint8_t dtim_origin;         /* Original DTIM value */
    uint8_t bcmc_dtim_mode;      /* Broadcast DTIM mode */
    uint8_t *buf_addr;           /* Buffer address for multicast */
    uint32_t mtimer_timeout_mini_us; /* Mini timer min timeout */
    uint32_t mtimer_timeout_max_us; /* Mini timer max timeout */
    uint8_t lpfw_copy;           /* Copy LP firmware to RAM */
    uint8_t lpfw_verify;         /* Verify LP firmware */
} bl_lp_fw_cfg_t;
```

### `bl_lp_pds_enter_with_restore()` - PDS Sleep with Restore

```c
int bl_lp_pds_enter_with_restore(uint32_t pds_level, uint32_t sleep_time);
```

Enter Power Down Sleep (PDS) with automatic register restoration.

### Tickless Mode (FreeRTOS Idle)

The tickless mode integrates with FreeRTOS to skip idle ticks when sleeping.

```c
#include "pm_manager.h"
#include "tickless.c"  // Or use pm_enable_tickless/pm_disable_tickless

// Enable tickless idle
pm_enable_tickless();

// Disable tickless idle
pm_disable_tickless();
```

From `pm_manager.h`:

```c
int pm_enable_tickless(void);
int pm_disable_tickless(void);
```

**Internal flow of `pm_enable_tickless()`:**
1. Calls `pm_enter_lp_perparation()` - prepares WiFi for sleep, enters WiFi PS mode
2. Calls `tickless_enter()` - enables tickless flag

**Internal flow of `pm_disable_tickless()`:**
1. Calls `pm_exit_lp_perparation()` - exits WiFi PS mode
2. Calls `tickless_exit()` - disables tickless flag

### `pm_enter_lp_perparation()` / `pm_exit_lp_perparation()`

```c
int pm_enter_lp_perparation(void);
int pm_exit_lp_perparation(void);
```

Prepare system for low power (allocate memory pool, configure DTIM, enter/exit WiFi PS).

---

## 3. Sleep Check Callbacks

Register callbacks to prevent sleep when certain conditions are met (e.g., ongoing UART traffic, active timers).

From `pm_manager.h`:

```c
typedef int (*pm_sleep_check_cb_t)(void);

int pm_sleep_check_register(const char *name, pm_sleep_check_cb_t cb, uint8_t priority);
int pm_sleep_check_unregister(const char *name);
int pm_sleep_check_dispatch(void);
```

**Parameters:**
- `name` - Unique identifier string
- `cb` - Callback function, returns 0 to allow sleep, non-zero to prevent
- `priority` - Lower value = higher priority (executed first)

**Example:**
```c
int my_peripheral_busy_check(void)
{
    // Return non-zero if busy (prevents sleep)
    if (uart_is_transmitting()) {
        return 1;
    }
    return 0;  // OK to sleep
}

// Register at init
pm_sleep_check_register("uart_busy", my_peripheral_busy_check, 5);

// Unregister when done
pm_sleep_check_unregister("uart_busy");
```

---

## 4. Clock Gating

Control peripheral clocks to save power when peripherals are not in use.

### Disable Unused Clocks

```c
#include "bl616_clock.h"

// Disable UART1 clock when not in use
system_clock_disable(CLK_UART1);

// Re-enable when needed
system_clock_enable(CLK_UART1);
```

Available clock definitions (from `bl616_clock.h`):
- `CLK_UART0`, `CLK_UART1`, `CLK_UART2`
- `CLK_SPI0`, `CLK_SPI1`
- `CLK_I2C0`, `CLK_I2C1`
- `CLK_PWM`
- `CLK_TIMER`
- `CLK_GPIO`
- etc.

### 32k Clock Management

For low power modes, the 32k clock must be ready:

```c
int bl_lp_get_32k_clock_ready(void);
int bl_lp_get_32k_trim_ready(void);
```

Check these before entering deep sleep modes.

---

## 5. PM Events

The WiFi PM system uses event flags to coordinate sleep:

From `bflb_pm.h`:

```c
void bl_pm_event_bit_set(enum PSM_EVENT event_bit);
void bl_pm_event_bit_clear(enum PSM_EVENT event_bit);
uint32_t bl_pm_event_get(void);
void bl_pm_enter_ps(void);
void bl_pm_exit_ps(void);
```

**Wake Reasons** (from `bl_lp_get_wake_reason()`):
- `LPFW_WAKEUP_TIME_OUT` - RTC timer wakeup
- `LPFW_WAKEUP_WIFI` - WiFi activity wakeup
- `LPFW_WAKEUP_WIFI_BROADCAST` - Broadcast/multicast wakeup
- `LPFW_WAKEUP_AP_LOSS` - AP connection loss
- `LPFW_WAKEUP_IO` - GPIO wakeup

---

## 6. Working Example - Tickless Idle with WiFi

```c
#include "FreeRTOS.h"
#include "task.h"
#include "pm_manager.h"
#include "bl_lp.h"
#include "wifi_mgmr_ext.h"

// Sleep check callback - prevent sleep if WiFi busy
int wifi_sleep_check(void)
{
    // Return non-zero to prevent sleep
    if (wifi_mgmr_sta_state_get()) {
        // WiFi connected - let tickless handle it
        return 0;
    }
    return 0;
}

void app_main(void)
{
    // Initialize power management
    pm_sys_init();
    
    // Initialize WiFi PM
    bl_pm_init();
    
    // Register sleep check (priority 3)
    pm_sleep_check_register("wifi_check", wifi_sleep_check, 3);
    
    // Configure DTIM for sleep (listen interval)
    set_dtim_config(3);  // Wake every 3 DTIMs
    
    // Enable tickless mode
    pm_enable_tickless();
    
    // Now FreeRTOS idle task will enter low power
    // when no tasks are running
    
    while (1) {
        vTaskDelay(pdMS_TO_TICKS(1000));
        printf("Running...\r\n");
    }
}
```

---

## 7. Working Example - Deep Sleep with RTC Wake

```c
#include "bl_lp.h"
#include "bflb_rtc.h"

void enter_deep_sleep(uint32_t sleep_time_us)
{
    bl_lp_fw_cfg_t cfg = {0};
    
    cfg.rtc_wakeup_en = 1;
    cfg.rtc_timeout_us = sleep_time_us;
    cfg.dtim_num = 1;
    cfg.dtim_origin = 1;
    cfg.mtimer_timeout_mini_us = 4500;
    cfg.mtimer_timeout_max_us = 12000;
    
    // Enter low power mode
    bl_lp_fw_enter(&cfg);
}

void app_main(void)
{
    // Sleep for 5 seconds, then wake
    printf("Entering deep sleep for 5 seconds...\r\n");
    enter_deep_sleep(5 * 1000 * 1000);
    
    // Execution resumes here after wake
    printf("Woke up!\r\n");
    
    // Check wake reason
    uint32_t reason = bl_lp_get_wake_reason();
    if (reason & LPFW_WAKEUP_TIME_OUT) {
        printf("Woke up from RTC timeout\r\n");
    }
}
```

---

## 8. PM API Quick Reference

| Function | File | Description |
|----------|------|-------------|
| `bl_pm_init()` | bflb_pm.h | Initialize WiFi PM |
| `pm_sys_init()` | pm_manager.h | Initialize system PM |
| `pm_sleep_check_register()` | pm_manager.h | Register sleep prevention callback |
| `pm_sleep_check_unregister()` | pm_manager.h | Unregister callback |
| `pm_enable_tickless()` | pm_manager.h | Enable FreeRTOS tickless idle |
| `pm_disable_tickless()` | pm_manager.h | Disable tickless idle |
| `bl_lp_fw_enter()` | bl616cl_lp.h | Enter low power sleep |
| `bl_lp_pds_enter_with_restore()` | bl616cl_lp.h | Enter PDS sleep |
| `bl_lp_get_wake_reason()` | bl616cl_lp.h | Get wake-up source |
| `bl_pm_event_bit_set()` | bl616cl_lp.h | Set PM event flag |
| `bl_pm_event_bit_clear()` | bl616cl_lp.h | Clear PM event flag |
| `system_clock_disable()` | bl616_clock.h | Disable peripheral clock |
| `system_clock_enable()` | bl616_clock.h | Enable peripheral clock |
| `set_dtim_config()` | pm_manager.h | Configure DTIM listen interval |

---

## 9. Low Power Hooks

Custom callbacks can be registered to run before/after sleep:

```c
#include "bl_lp.h"

// Called before system enters low power
void lp_hook_pre_sys(void *env)
{
    // Save peripheral states, disable non-wake sources
}

// Called after system wakes from low power
void lp_hook_post_sys(iot2lp_para_t *param)
{
    // Restore peripheral states
}

// Register hooks (already weak-defined in SDK, just implement them)
void lp_hook_pre_sys(void *env) __attribute__((weak));
void lp_hook_post_sys(iot2lp_para_t *) __attribute__((weak));
```

---

## 10. Notes

- WiFi must be in PS (Power Save) mode for effective tickless operation
- DTIM interval affects wake frequency - higher values = more power savings but higher latency
- Always check `bl_lp_get_32k_clock_ready()` before deep sleep if using RTC wake
- Clock gating only affects peripherals - CPU and critical clocks cannot be disabled
- The `pm_sleep_check_dispatch()` is called automatically before entering sleep to verify it's safe
