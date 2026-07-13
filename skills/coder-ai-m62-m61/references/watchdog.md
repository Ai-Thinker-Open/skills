# Watchdog API Reference (BL616/BL618)

> Timer-based Watchdog peripheral with reset and interrupt modes

**Source:** `bouffalo_sdk/drivers/lhal/include/bflb_wdg.h`  
**Header:** `bouffalo_sdk/drivers/lhal/include/bflb_timer.h` (shared Timer block)  
**Hardware Base:** `TIMER_BASE = 0x2000A500`  
**IRQ:** `TIMER0_WDT_IRQn = IRQ_NUM_BASE + 38` (BL616)  
**Device Name:** `BFLB_NAME_WDT = "watchdog0"`

---

## Overview

The BL616/BL618 contains an integrated **Watchdog Timer (WDT)** built on top of the Timer peripheral block. The watchdog is a safety mechanism that will reset the system if the CPU becomes unresponsive (fails to "feed" the watchdog within the configured timeout window).

The watchdog supports two modes:
- **Interrupt mode (`WDG_MODE_INTERRUPT`):** Generates an interrupt when the counter expires, but does NOT reset the system.
- **Reset mode (`WDG_MODE_RESET`):** Generates a system reset when the counter expires (default).

The watchdog shares the Timer block at `TIMER_BASE`, and is accessed through a register area protected by a "write-key" sequence (`0xBABA` → `0xEB10`) to prevent accidental modification.

### Clock Sources

```c
#define WDG_CLKSRC_BCLK  0   /* Bus clock (not on BL702L) */
#define WDG_CLKSRC_32K   1   /* 32 KHz RC / external crystal */
#define WDG_CLKSRC_1K    2   /* 1 KHz low-speed clock */
#define WDG_CLKSRC_XTAL  3   /* External crystal oscillator */
#define WDG_CLKSRC_GPIO  4   /* GPIO input (not on BL602/BL702) */
#define WDG_CLKSRC_NO    5   /* No clock (disabled) */
```

### Timeout Calculation

With the 32 KHz clock source and a clock divider of 1:
```
Timeout (ms) = (comp_val × clock_div) / clock_freq × 1000
```

Example: `clock_div=1`, `comp_val=1000`, `clock_source=WDG_CLKSRC_32K`:
```
Timeout ≈ (1000 × 1) / 32768 × 1000 ≈ 30.5 ms
```

---

## Configuration Structure

```c
struct bflb_wdg_config_s {
    uint8_t  clock_source;  /* Clock source, use WDG_CLKSRC_* */
    uint8_t  clock_div;      /* Clock divider (0-255), effective freq = source / (div+1) */
    uint16_t comp_val;       /* Compare value (timeout = comp_val × clock ticks) */
    uint8_t  mode;           /* WDG_MODE_INTERRUPT or WDG_MODE_RESET */
};
```

---

## Function Reference

### `bflb_wdg_init()`

```c
void bflb_wdg_init(struct bflb_device_s *dev, const struct bflb_wdg_config_s *config);
```

Initialize and configure the watchdog timer. This sets up the clock source, divider, compare value, and interrupt/reset mode. The watchdog does NOT start automatically — call `bflb_wdg_start()` after initialization.

**Parameters:**
- `dev`    — Device handle, obtained from `bflb_device_get_by_name("watchdog0")`
- `config` — Pointer to watchdog configuration structure

---

### `bflb_wdg_start()`

```c
void bflb_wdg_start(struct bflb_device_s *dev);
```

Start the watchdog counter. Once started, the counter decrements from `comp_val` toward zero. The application must periodically call `bflb_wdg_reset_countervalue()` to reload the counter before it reaches zero.

---

### `bflb_wdg_stop()`

```c
void bflb_wdg_stop(struct bflb_device_s *dev);
```

Stop the watchdog counter. The counter freezes at its current value.

---

### `bflb_wdg_reset_countervalue()`

```c
void bflb_wdg_reset_countervalue(struct bflb_device_s *dev);
```

**Feed the watchdog.** Reload the counter with the configured `comp_val`. Call this periodically in your main loop or from a timer interrupt to prevent a watchdog reset.

---

### `bflb_wdg_get_countervalue()`

```c
uint16_t bflb_wdg_get_countervalue(struct bflb_device_s *dev);
```

Read the current watchdog counter value. Useful for diagnostics.

**Returns:** Current counter value (decrements toward zero).

---

### `bflb_wdg_set_countervalue()`

```c
void bflb_wdg_set_countervalue(struct bflb_device_s *dev, uint16_t value);
```

Set the watchdog counter to a specific value. Normally not needed — use `bflb_wdg_reset_countervalue()` to reload with the configured compare value.

---

### `bflb_wdg_compint_clear()`

```c
void bflb_wdg_compint_clear(struct bflb_device_s *dev);
```

Clear the watchdog compare-match interrupt flag. In interrupt mode, the CPU must call this in the interrupt handler to acknowledge the watchdog event.

---

## Complete Usage Example

### Basic Watchdog Reset (Timeout = ~1 second)

```c
#include "bflb_wdg.h"
#include "bflb_device.h"
#include "bflb_irq.h"

static struct bflb_device_s *wdg;

void wdg_irq_handler(void)
{
    /* Clear interrupt flag */
    bflb_wdg_compint_clear(wdg);
    printf("Watchdog interrupt! CPU is still alive.\n");
}

int main(void)
{
    struct bflb_wdg_config_s wdg_cfg;

    /* Get watchdog device handle */
    wdg = bflb_device_get_by_name("watchdog0");
    if (!wdg) {
        printf("Watchdog device not found\n");
        return -1;
    }

    /* Configure watchdog:
     * Clock source: 32 KHz
     * Clock divider: 1 (so tick = 1/32K ≈ 30.5 µs)
     * Compare value: 32768 (approx 1 second timeout)
     * Mode: Reset (system reset on timeout)
     */
    wdg_cfg.clock_source = WDG_CLKSRC_32K;
    wdg_cfg.clock_div = 1;
    wdg_cfg.comp_val = 32768;
    wdg_cfg.mode = WDG_MODE_RESET;

    bflb_wdg_init(wdg, &wdg_cfg);

    /* Register interrupt handler (for interrupt mode) */
    bflb_irq_register(wdg->irq_num, wdg_irq_handler);

    /* Start watchdog */
    bflb_wdg_start(wdg);

    /* Main loop - feed the watchdog */
    while (1) {
        /* Simulate work */
        bflb_mtimer_delay_ms(100);

        /* Feed the watchdog (reload counter) */
        bflb_wdg_reset_countervalue(wdg);

        printf("Watchdog fed. Counter=%u\n",
               bflb_wdg_get_countervalue(wdg));
    }

    return 0;
}
```

### Watchdog in Interrupt Mode (No Reset)

```c
#include "bflb_wdg.h"
#include "bflb_device.h"
#include "bflb_irq.h"

static struct bflb_device_s *wdg;

void wdg_timeout_handler(void)
{
    /* Clear the interrupt */
    bflb_wdg_compint_clear(wdg);

    /* Log the event — system stays running */
    printf("Watchdog timeout! Taking corrective action...\n");

    /* Re-feed the watchdog */
    bflb_wdg_reset_countervalue(wdg);
}

void wdg_demo(void)
{
    struct bflb_wdg_config_s cfg = {
        .clock_source = WDG_CLKSRC_32K,
        .clock_div = 1,
        .comp_val = 16384,     /* ~0.5 second timeout */
        .mode = WDG_MODE_INTERRUPT, /* Interrupt only, no reset */
    };

    wdg = bflb_device_get_by_name("watchdog0");
    if (!wdg) {
        return;
    }

    /* Install ISR before init (init enables the interrupt) */
    bflb_irq_register(wdg->irq_num, wdg_timeout_handler);

    bflb_wdg_init(wdg, &cfg);
    bflb_wdg_start(wdg);

    /* Now the watchdog will interrupt every ~0.5 seconds
     * instead of resetting the system */
}
```

---

## Register-Level Reference

Watchdog registers are at `TIMER_BASE = 0x2000A500`. **All WDT registers require the write-key sequence** (`0xBABA` to `WFAR`, then `0xEB10` to `WSAR`) before each write access.

| Offset | Register | Description |
|--------|----------|-------------|
| `0x64` | TIMER_WMER | Watchdog Mode Enable Register. `WE` (bit 0) enables WDT, `WRIE` (bit 1) selects reset vs. interrupt |
| `0x68` | TIMER_WMR | Watchdog Match Register. 16-bit compare value |
| `0x6C` | TIMER_WVR | Watchdog Counter Value (read-only current count) |
| `0x70` | TIMER_WSR | Watchdog Reset Status. `WTS` bit set if reset was triggered |
| `0x80` | TIMER_WICR | Watchdog Interrupt Clear. Write `WICLR` (bit 0) to clear |
| `0x98` | TIMER_WCR | Watchdog Counter Reset. Write 1 to reload counter from WMR |
| `0x9C` | TIMER_WFAR | Watchdog Write Key 1 (write `0xBABA` before each WDT register write) |
| `0xA0` | TIMER_WSAR | Watchdog Write Key 2 (write `0xEB10` after WFAR) |
| `0xBC` | TIMER_TCDR | Timer Clock Division. `WCDR` field (bits 24-31) = WDT clock divider |

### Key Register Bitfields

```c
/* TIMER_WMER (offset 0x64) */
#define TIMER_WE   (1 << 0)   /* Watchdog enable */
#define TIMER_WRIE (1 << 1)   /* 0=reset mode, 1=interrupt mode on timeout */

/* TIMER_WMR (offset 0x68) */
#define TIMER_WMR_MASK      (0xFFFF << 0)  /* 16-bit compare value */

/* TIMER_WCR (offset 0x98) */
#define TIMER_WCR (1 << 0)   /* Write 1 to reset counter to WMR value */

/* TIMER_WICR (offset 0x80) */
#define TIMER_WICLR (1 << 0) /* Write 1 to clear watchdog interrupt */

/* TIMER_TCCR (offset 0x00) */
#define TIMER_CS_WDT_SHIFT  (8)           /* WDT clock source shift */
#define TIMER_CS_WDT_MASK    (0xF << 8)    /* WDT clock source mask */
```

> **Important:** On BL616, the WDT device is registered in the device table with `reg_base = TIMER_BASE` and `irq_num = TIMER0_WDT_IRQn (IRQ 38)`. The WDT hardware sits inside the Timer IP block at the TIMER_BASE address.
