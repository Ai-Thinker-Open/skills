# Watchdog API Reference

> Source file: `components/platform/hosal/include/hosal_wdg.h`

## Type Definitions

### `hosal_wdg_config_t` — Watchdog Configuration Structure

```c
typedef struct {
    uint32_t timeout;  // Watchdog timeout (milliseconds)
} hosal_wdg_config_t;
```

### `hosal_wdg_dev_t` — Watchdog Device Structure

```c
typedef struct {
    uint8_t       port;
    hosal_wdg_config_t  config;
    void         *priv;
} hosal_wdg_dev_t;
```

## Function Interface

### `hosal_wdg_init`

Initializes the watchdog.

```c
int hosal_wdg_init(hosal_wdg_dev_t *wdg);
```

---

### `hosal_wdg_reload`

Feeds the watchdog (reloads the counter to prevent reset).

```c
void hosal_wdg_reload(hosal_wdg_dev_t *wdg);
```

---

### `hosal_wdg_finalize`

Releases the watchdog.

```c
int hosal_wdg_finalize(hosal_wdg_dev_t *wdg);
```

## Usage Example

```c
#include "hal_wdg.h"

hosal_wdg_dev_t wdg = {
    .port = 0,
    .config = {
        .timeout = 3000,  // 3 second timeout
    }
};

hosal_wdg_init(&wdg);

// In the main loop, periodically feed the watchdog
while (1) {
    hosal_wdg_reload(&wdg);  // Feed the watchdog
    // Business logic
    vTaskDelay(pdMS_TO_TICKS(500));
}
```

---

## Register-Level Programming

> Register Header: `components/platform/soc/bl602/bl602_std/bl602_std/Device/Bouffalo/BL602/Peripherals/timer_reg.h`  
> Base Address: `0x4000A500` (TIMER/WDT block)

### Register Overview

Watchdog registers are located at offsets `0x100-0x140` within the TIMER base address.

| Offset | Name | Description |
|--------|------|-------------|
| 0x100 | TIMER_WDT_CURRENT | Current watchdog counter value |
| 0x104 | TIMER_WDT_RELOAD | Watchdog timeout reload value |
| 0x108 | TIMER_WDT_CMD | Watchdog command (reload, stop, start) |
| 0x10C | TIMER_WDT_INT_CFG | Watchdog interrupt configuration |
| 0x110 | TIMER_WDT_RESET_MASK | Reset mask control |
| 0x114 | TIMER_WDT_LOCK | Watchdog lock register |
| 0x118 | TIMER_WDT_INT_STATUS | Watchdog interrupt status |

### Key Register Fields

**TIMER_WDT_CMD (0x108)**

| Bits | Name | Description |
|------|------|-------------|
| 0 | reload | Reload watchdog counter (write 1) |
| 1 | stop | Stop watchdog (write 1) |
| 2 | start | Start watchdog (write 1) |

**TIMER_WDT_INT_CFG (0x10C)**

| Bits | Name | Description |
|------|------|-------------|
| 0 | wdt_int_enable | Watchdog interrupt enable |

**TIMER_WDT_RESET_MASK (0x110)**

| Bits | Name | Description |
|------|------|-------------|
| 0 | reset_mask | Reset mask (0=reset enabled, 1=reset masked) |

**TIMER_WDT_LOCK (0x114)**

| Value | Description |
|-------|-------------|
| 0xBFFF | Unlock watchdog registers |
| 0x0000 | Lock watchdog registers |

### Register-Level Code Example

```c
#include <stdint.h>

#define TIMER_BASE   0x4000A500

/* Watchdog register offsets (within timer block) */
#define TIMER_WDT_CURRENT   0x100
#define TIMER_WDT_RELOAD    0x104
#define TIMER_WDT_CMD       0x108
#define TIMER_WDT_INT_CFG   0x10C
#define TIMER_WDT_RESET_MASK  0x110
#define TIMER_WDT_LOCK      0x114
#define TIMER_WDT_INT_STATUS  0x118

/* Bit masks */
#define WDT_CMD_RELOAD   (1 << 0)
#define WDT_CMD_STOP     (1 << 1)
#define WDT_CMD_START    (1 << 2)
#define WDT_INT_EN       (1 << 0)
#define WDT_RESET_EN     (0 << 0)  /* 0 = reset enabled */

/* Lock/Unlock values */
#define WDT_UNLOCK_VAL   0xBFFF
#define WDT_LOCK_VAL     0x0000

static volatile uint32_t * const WDT = (volatile uint32_t *)(TIMER_BASE + 0x100);

/* Unlock watchdog registers to allow writes */
static void wdt_unlock(void) {
    WDT[TIMER_WDT_LOCK / 4] = WDT_UNLOCK_VAL;
}

/* Lock watchdog registers after configuration */
static void wdt_lock(void) {
    WDT[TIMER_WDT_LOCK / 4] = WDT_LOCK_VAL;
}

/* Initialize watchdog with timeout in ms */
void wdt_init(uint32_t timeout_ms) {
    /* Unlock to access watchdog */
    wdt_unlock();

    /* Stop watchdog first */
    WDT[TIMER_WDT_CMD / 4] = WDT_CMD_STOP;

    /* Set reload value (timeout in watchdog ticks, typically 1 tick = 1ms) */
    WDT[TIMER_WDT_RELOAD / 4] = timeout_ms;

    /* Enable reset (not masked), enable interrupt */
    WDT[TIMER_WDT_RESET_MASK / 4] = 0;  /* reset enabled */
    WDT[TIMER_WDT_INT_CFG / 4] = WDT_INT_EN;

    /* Start watchdog */
    WDT[TIMER_WDT_CMD / 4] = WDT_CMD_START;

    /* Lock to prevent accidental modification */
    wdt_lock();
}

/* Feed the watchdog (reload counter) */
void wdt_feed(void) {
    wdt_unlock();
    WDT[TIMER_WDT_CMD / 4] = WDT_CMD_RELOAD;
    wdt_lock();
}

/* Stop the watchdog */
void wdt_stop(void) {
    wdt_unlock();
    WDT[TIMER_WDT_CMD / 4] = WDT_CMD_STOP;
    wdt_lock();
}

/* Check if watchdog interrupt pending */
int wdt_irq_pending(void) {
    return (WDT[TIMER_WDT_INT_STATUS / 4] & 1) != 0;
}

/* Example usage */
void wdt_example(void) {
    /* Initialize 2-second watchdog */
    wdt_init(2000);

    while (1) {
        /* Feed watchdog every 500ms */
        wdt_feed();
        /* Do work... */
    }
}
```
