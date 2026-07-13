# Timer API Reference

> Source file: `components/platform/hosal/include/hosal_timer.h`

## Macros

```c
#define TIMER_RELOAD_PERIODIC 1  // Periodic reload (continuous)
#define TIMER_RELOAD_ONCE     2  // One-shot timer
```

## Type Definitions

### `hosal_timer_cb_t` — Timer Callback Function Type

```c
typedef void (*hosal_timer_cb_t)(void *arg);
```

### `hosal_timer_config_t` — Timer Configuration Structure

```c
typedef struct {
    uint32_t          period;      // Timer period (microseconds)
    uint8_t           reload_mode; // Reload mode: TIMER_RELOAD_PERIODIC / TIMER_RELOAD_ONCE
    hosal_timer_cb_t  cb;          // Timer callback function
    void              *arg;         // Callback argument
} hosal_timer_config_t;
```

### `hosal_timer_dev_t` — Timer Device Structure

```c
typedef struct {
    int8_t                port;   // Timer port number
    hosal_timer_config_t  config;
    void                  *priv;
} hosal_timer_dev_t;
```

## Function API

### `hosal_timer_init`

Initialize timer.

```c
int hosal_timer_init(hosal_timer_dev_t *tim);
```

---

### `hosal_timer_start`

Start timer.

```c
int hosal_timer_start(hosal_timer_dev_t *tim);
```

---

### `hosal_timer_stop`

Stop timer.

```c
void hosal_timer_stop(hosal_timer_dev_t *tim);
```

---

### `hosal_timer_finalize`

Finalize timer.

```c
int hosal_timer_finalize(hosal_timer_dev_t *tim);
```

## Usage Example

```c
#include "hal_timer.h"

static void timer_callback(void *arg)
{
    printf("Timer expired!\r\n");
    // Handle timer event
}

hosal_timer_dev_t tim0 = {
    .port = 0,
    .config = {
        .period = 1000000,          // 1 second (1000000 us)
        .reload_mode = TIMER_RELOAD_PERIODIC,  // Periodic reload
        .cb = timer_callback,
        .arg = NULL,
    }
};

hosal_timer_init(&tim0);
hosal_timer_start(&tim0);

// When you need to stop
hosal_timer_stop(&tim0);

// When you need to finalize
hosal_timer_finalize(&tim0);
```

---

## Register-Level Programming

> Register Header: `components/platform/soc/bl602/bl602_std/bl602_std/Device/Bouffalo/BL602/Peripherals/timer_reg.h`  
> Base Address: `0x4000A500` (WDT block); PWM channels 0-3 begin at offset `0x20` (channel 0) with 0x1C bytes per channel

### Register Overview

**WDT / Timer-0 (shared base 0x4000A500)**

| Offset | Name              | Description                          |
|--------|-------------------|--------------------------------------|
| 0x00   | TIMER_WDT_CURRENT | Current counter value (read-only)    |
| 0x04   | TIMER_WDT_RELOAD  | Reload value                         |
| 0x08   | TIMER_WDT_CMD     | Control: reload, stop, start         |
| 0x0C   | TIMER_WDT_INT_CFG | Interrupt enable                     |
| 0x10   | TIMER_WDT_RESET_MASK | Reset mask                        |
| 0x18   | TIMER_WDT_INT_STATUS | Interrupt status                  |

**PWM Channels 0-3** (base + 0x20 + ch * 0x1C)

| Offset (ch N) | Name   | Description                              |
|---------------|--------|------------------------------------------|
| 0x20 + N*0x1C | TCCR   | Timer counter control and enable         |
| 0x24 + N*0x1C | TMR2   | PWM output mode and enable               |
| 0x28 + N*0x1C | TMR3   | PWM threshold/thre2 (toggle point)       |
| 0x2C + N*0x1C | TIER   | Timer interrupt enable                   |
| 0x30 + N*0x1C | TISR   | Timer interrupt status                    |
| 0x34 + N*0x1C | WMR    | PWM period (match value for counter clear)|
| 0x38 + N*0x1C | WVR    | PWM threshold/thre1                       |
| 0x3C + N*0x1C | TCNT   | Timer counter value (read-only)          |

### Key Register Fields

**TIMER_WDT_CMD (0x08)**

| Bits | Name    | Description                    |
|------|---------|--------------------------------|
| 0    | reload  | Reload counter from RELOAD reg |
| 1    | stop    | Stop the counter               |
| 2    | start   | Start the counter              |

**TIMER_WDT_INT_CFG (0x0C)**

| Bits | Name        | Description              |
|------|-------------|--------------------------|
| 0    | wdt_int_enable | Watchdog interrupt enable |

**TIMER_WDT_INT_STATUS (0x18)**

| Bits | Name      | Description          |
|------|-----------|----------------------|
| 0    | int_sts   | Interrupt pending    |

**TCCR — Timer Counter Control Register (per channel)**

| Bits | Name     | Description                                      |
|------|----------|--------------------------------------------------|
| 0    | enable   | Timer channel enable (1=enable)                  |
| 1    | free_run | Free-run mode (1=free run, 0=clear on match)    |

**TMR2 — PWM Mode Register (per channel)**

| Bits  | Name      | Description                                        |
|-------|-----------|----------------------------------------------------|
| 8     | pwm_out_en| PWM output enable (1=enable)                      |
| [3:0] | pwm_mode  | 0=no PWM, 1=always low, 2=always high, 3=clear on match |

**WMR — PWM Period Register (per channel)**

| Bits  | Name    | Description                                          |
|-------|---------|------------------------------------------------------|
| [15:0]| wmr     | Match value: counter clears at this value (sets PWM period) |

**WVR — PWM Threshold Register (per channel)**

| Bits  | Name  | Description                                    |
|-------|-------|------------------------------------------------|
| [15:0]| wvr   | Threshold 1: active level ends at this count |

### Register-Level Code Example

**WDT Timer**

```c
#include <stdint.h>

#define TIMER_BASE            0x4000A500UL
#define TIMER_WDT_CURRENT     *(volatile uint32_t *)(TIMER_BASE + 0x00)
#define TIMER_WDT_RELOAD      *(volatile uint32_t *)(TIMER_BASE + 0x04)
#define TIMER_WDT_CMD         *(volatile uint32_t *)(TIMER_BASE + 0x08)
#define TIMER_WDT_INT_CFG     *(volatile uint32_t *)(TIMER_BASE + 0x0C)
#define TIMER_WDT_RESET_MASK  *(volatile uint32_t *)(TIMER_BASE + 0x10)
#define TIMER_WDT_INT_STATUS  *(volatile uint32_t *)(TIMER_BASE + 0x18)

/* Start a one-shot watchdog-style timer with ~1s period */
void wdt_timer_example(void)
{
    uint32_t reload_val = 0x100000;  /* approximate for 1s at 32kHz LP clock */

    /* Set reload value */
    TIMER_WDT_RELOAD = reload_val;

    /* Enable watchdog interrupt */
    TIMER_WDT_INT_CFG = 0x01;

    /* Mask reset on timeout (only interrupt, no chip reset) */
    TIMER_WDT_RESET_MASK = 0x00;

    /* Reload counter from TIMER_WDT_RELOAD */
    TIMER_WDT_CMD = 0x01;

    /* Start the counter */
    TIMER_WDT_CMD = 0x04;
}

/* Check if timer expired (polling) */
int wdt_timer_expired(void)
{
    return (TIMER_WDT_INT_STATUS & 0x01) != 0;
}

/* Stop timer */
void wdt_timer_stop(void)
{
    TIMER_WDT_CMD = 0x02;  /* stop */
}
```

**PWM Timer Channel 0**

```c
/* PWM channel register offsets from timer base */
#define TCCR_CH0      *(volatile uint32_t *)(TIMER_BASE + 0x20)
#define TMR2_CH0      *(volatile uint32_t *)(TIMER_BASE + 0x24)
#define TMR3_CH0      *(volatile uint32_t *)(TIMER_BASE + 0x28)
#define TIER_CH0      *(volatile uint32_t *)(TIMER_BASE + 0x2C)
#define TISR_CH0      *(volatile uint32_t *)(TIMER_BASE + 0x30)
#define WMR_CH0       *(volatile uint32_t *)(TIMER_BASE + 0x34)
#define WVR_CH0       *(volatile uint32_t *)(TIMER_BASE + 0x38)
#define TCNT_CH0      *(volatile uint32_t *)(TIMER_BASE + 0x3C)

/* Configure PWM on channel 0: ~10kHz, 50% duty cycle
 * Assumes bus clock or relevant timer clock is 32MHz.
 * Effective PWM freq = timer_clk / (WMR + 1)
 * For 10kHz from 32MHz: WMR = 3200 - 1 = 3199
 * Duty cycle = WVR / (WMR + 1), so WVR = WMR/2 for 50%
 */
void pwm_timer_example(void)
{
    uint32_t wmr = 3199;   /* period register: 3200 counts */
    uint32_t wvr = 1600;   /* threshold: ~50% duty cycle */

    /* Disable channel during configuration */
    TCCR_CH0 = 0x00;

    /* Set period (WMR) and duty cycle (WVR) */
    WMR_CH0 = wmr;
    WVR_CH0 = wvr;

    /* Configure PWM mode: enable output, clear-on-match mode (pwm_mode=3) */
    TMR2_CH0 = (1 << 8)   /* pwm_out_en: PWM output enabled */
             | (3 << 0);  /* pwm_mode=3: clear on match (active high) */

    /* Configure timer: free-run mode, enable counter */
    TCCR_CH0 = (1 << 1)   /* free_run=1: counter free-runs */
             | (1 << 0);  /* enable=1: start counting */
}
```
