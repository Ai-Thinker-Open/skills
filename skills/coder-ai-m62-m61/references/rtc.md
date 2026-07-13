# RTC API Reference (BL616/BL618)

> Real-Time Clock peripheral in the AON (Always-On) domain

**Source:** `bouffalo_sdk/drivers/lhal/include/bflb_rtc.h`  
**Implementation:** `bouffalo_sdk/drivers/lhal/src/bflb_rtc.c`  
**Hardware Base:** `BFLB_RTC_BASE = 0x2000F000` (part of HBN/AON block at `HBN_BASE = 0x2000F000`)  
**Device Name:** `BFLB_NAME_RTC = "rtc"`

---

## Overview

The BL616/BL618 Real-Time Clock (RTC) is part of the **AON (Always-On) power domain**. The RTC runs from a dedicated 32.768 KHz oscillator and continues to keep time even when the main CPU is powered down in deep sleep or hibernate mode.

The RTC provides:
- **Wall-clock time:** 47-bit counter at 1/32768 second resolution
- **Alarm/timer:** Set an absolute time at which an interrupt fires
- **UTC time conversion:** Convert between raw counter values and `struct tm` calendar format
- **UTC timestamp:** Get Unix epoch seconds

The RTC is clocked from the 32 KHz RC oscillator (or external crystal) and the counter increments at **1/32768 second per tick** (approximately 30.5 µs per tick). The 47-bit counter provides a range of approximately **890 years** before rollover.

### RTC Time Conversion Macros

```c
#define BFLB_RTC_SEC2TIME(s)    (s * bflb_clk_get_peripheral_clock(BFLB_DEVICE_TYPE_RTC, 0))
#define BFLB_RTC_TIME2SEC(time) (time / bflb_clk_get_peripheral_clock(BFLB_DEVICE_TYPE_RTC, 0))
```

> These macros convert between real-time seconds and the raw RTC tick counter value. The peripheral clock for RTC on BL616 is 32768 Hz (1 Hz = 32768 ticks).

---

## Time Structure

```c
/* Compatible with standard struct tm */
struct bflb_tm {
    int tm_sec;    /* Seconds [0-59] */
    int tm_min;    /* Minutes [0-59] */
    int tm_hour;   /* Hours [0-23] */
    int tm_mday;   /* Day of month [1-31] */
    int tm_mon;    /* Month [0-11] (January=0) */
    int tm_year;   /* Years since 1900 */
    int tm_wday;   /* Day of week [1-7] (Sunday=1) */
    int tm_yday;   /* Day of year [0-365] */
};
```

---

## Function Reference

### `bflb_rtc_set_time()`

```c
void bflb_rtc_set_time(struct bflb_device_s *dev, uint64_t time);
```

Set the RTC alarm timer. The RTC continuously counts up; this sets an **absolute compare value** at which an alarm interrupt will fire. The `time` parameter is in raw RTC ticks (1 tick = 1/32768 second).

**Parameters:**
- `dev`  — Device handle from `bflb_device_get_by_name("rtc")`
- `time` — Alarm time in RTC ticks (absolute counter value)

**Example (alarm in ~10 seconds):**
```c
struct bflb_device_s *rtc = bflb_device_get_by_name("rtc");
uint64_t current = bflb_rtc_get_time(rtc);
bflb_rtc_set_time(rtc, current + 10 * 32768); /* 10 seconds = 10*32768 ticks */
```

---

### `bflb_rtc_get_time()`

```c
uint64_t bflb_rtc_get_time(struct bflb_device_s *dev);
```

Get the current RTC counter value (raw ticks since RTC epoch). This is the absolute counter value, not wall-clock time.

**Returns:** Current RTC counter value (47-bit, in ticks).

---

### `bflb_rtc_disable()`

```c
void bflb_rtc_disable(struct bflb_device_s *dev);
```

Disable the RTC counter and clear the alarm. The RTC does NOT continue counting when disabled.

---

### `bflb_rtc_set_utc_time()`

```c
void bflb_rtc_set_utc_time(const struct bflb_tm *time);
```

Set a wall-clock (UTC) reference time. This stores the calendar time and starts tracking delta time internally. Unlike `bflb_rtc_set_time()`, this sets a **human-readable UTC time** and maintains a reference point for subsequent UTC conversions.

**Parameters:**
- `time` — Pointer to `struct bflb_tm` with the current UTC time

**Example:**
```c
struct bflb_tm now;
now.tm_year = 2026 - 1900;  /* Year = 2026 */
now.tm_mon  = 3;              /* April (0-indexed) */
now.tm_mday = 28;
now.tm_hour = 12;
now.tm_min  = 0;
now.tm_sec  = 0;
bflb_rtc_set_utc_time(&now);
```

---

### `bflb_rtc_get_utc_time()`

```c
void bflb_rtc_get_utc_time(struct bflb_tm *time);
```

Get the current wall-clock (UTC) time as a calendar structure. This returns the UTC time computed from the stored reference time plus elapsed RTC ticks.

**Parameters:**
- `time` — Pointer to `struct bflb_tm` to receive the current UTC time

---

### `bflb_rtc_get_utc_timestamp()`

```c
uint64_t bflb_rtc_get_utc_timestamp(void);
```

Get the current UTC time as Unix epoch seconds (seconds since January 1, 1970).

**Returns:** Unix timestamp in seconds.

---

## Complete Usage Example

### RTC Alarm (Timer) Example

```c
#include "bflb_rtc.h"
#include "bflb_device.h"
#include "bflb_irq.h"

static struct bflb_device_s *rtc_dev;

void rtc_alarm_handler(void)
{
    printf("RTC Alarm triggered!\n");
    /* Clear and re-arm if needed */
    bflb_rtc_disable(rtc_dev);
}

void rtc_alarm_demo(void)
{
    uint64_t now;

    rtc_dev = bflb_device_get_by_name("rtc");
    if (!rtc_dev) {
        printf("RTC device not found\n");
        return;
    }

    /* Register ISR */
    bflb_irq_register(rtc_dev->irq_num, rtc_alarm_handler);

    /* Get current RTC counter */
    now = bflb_rtc_get_time(rtc_dev);
    printf("Current RTC count: %llu\n", now);

    /* Set alarm for 5 seconds from now */
    /* 5 seconds = 5 * 32768 ticks */
    bflb_rtc_set_time(rtc_dev, now + (5 * 32768));

    printf("Alarm set for 5 seconds...\n");
}
```

### RTC Wall-Clock Time Example

```c
#include "bflb_rtc.h"
#include "bflb_device.h"
#include <stdio.h>

void rtc_wallclock_demo(void)
{
    struct bflb_device_s *rtc = bflb_device_get_by_name("rtc");
    struct bflb_tm time_val;
    uint64_t timestamp;

    /* Initialize RTC with a known UTC time */
    struct bflb_tm init_time = {
        .tm_year = 2026 - 1900,  /* 2026 */
        .tm_mon  = 3,             /* April (0-indexed) */
        .tm_mday = 28,
        .tm_hour = 14,
        .tm_min  = 30,
        .tm_sec  = 0,
    };
    bflb_rtc_set_utc_time(&init_time);

    /* Later, read back the current UTC time */
    bflb_rtc_get_utc_time(&time_val);
    printf("Current UTC: %04d-%02d-%02d %02d:%02d:%02d\n",
           time_val.tm_year + 1900,
           time_val.tm_mon + 1,
           time_val.tm_mday,
           time_val.tm_hour,
           time_val.tm_min,
           time_val.tm_sec);

    /* Or get Unix timestamp */
    timestamp = bflb_rtc_get_utc_timestamp();
    printf("Unix timestamp: %llu\n", timestamp);
}
```

### Deep Sleep with RTC Wake-Up

```c
#include "bflb_rtc.h"
#include "bflb_pds.h"
#include "bflb_device.h"

void rtc_wake_from_deep_sleep(void)
{
    struct bflb_device_s *rtc = bflb_device_get_by_name("rtc");
    uint64_t wake_time;

    /* Set wake-up alarm for 10 seconds in the future */
    wake_time = bflb_rtc_get_time(rtc);
    bflb_rtc_set_time(rtc, wake_time + (10 * 32768));

    printf("Going to deep sleep for ~10 seconds...\n");

    /* Enter deep sleep. RTC stays powered. */
    /* bflb_pds_enter(PDS_LEVEL_4); */  /* Pseudocode */

    printf("Woke up from deep sleep!\n");
}
```

---

## Register-Level Reference

RTC registers are part of the HBN/AON block at `BFLB_RTC_BASE = 0x2000F000` (same as `HBN_BASE`):

| Offset | Register | Description |
|--------|----------|-------------|
| `HBN_CTL_OFFSET` (0x0) | HBN_CTL | RTC control: `HBN_RTC_ENABLE` starts counter, `HBN_RTC_CTL` selects mode |
| `HBN_RTC_TIME_L_OFFSET` (0x1C) | HBN_TIME_L | RTC current time low 32 bits (read via latch) |
| `HBN_RTC_TIME_H_OFFSET` (0x20) | HBN_TIME_H | RTC current time high bits + latch trigger |
| `HBN_TIME_L_OFFSET` (0x24) | HBN_TIME_L | RTC alarm compare low 32 bits |
| `HBN_TIME_H_OFFSET` (0x28) | HBN_TIME_H | RTC alarm compare high bits |

### Key HBN Register Bitfields

From `hbn_reg.h` and `rtc_reg.h`:

```c
/* HBN_CTL (offset 0x0) */
#define HBN_RTC_ENABLE          /* Bit to enable RTC counter */
#define HBN_RTC_CTL_MASK        /* RTC mode control mask */
#define HBN_RTC_DLY_OPTION      /* Delay option for precise timing */
#define HBN_RTC_BIT39_0_COMPARE /* Enable 39-bit compare */

/* HBN_RTC_TIME_H (offset 0x20) - Latch trigger + read */
#define HBN_RTC_TIME_LATCH      /* Write 1 to latch RTC value for reading */

/* Time is a 47-bit counter: upper bits in HBN_RTC_TIME_H[7:0], 
 * lower 32 bits in HBN_RTC_TIME_L
 */
```

> **Important:** The RTC counter must be read through a **latch sequence**: write `HBN_RTC_TIME_LATCH` to `HBN_RTC_TIME_H`, then read `HBN_RTC_TIME_L` then `HBN_RTC_TIME_H`. The `bflb_rtc_get_time()` function handles this sequence automatically. The raw counter resolution is 1/32768 second (approximately 30.5 µs per tick).
