# RTC API Reference

> Source file: `components/platform/hosal/include/hosal_rtc.h`

## Macros

```c
#define HOSAL_RTC_FORMAT_DEC 1  // Decimal format
#define HOSAL_RTC_FORMAT_BCD 2  // BCD format
```

## Type Definitions

### `hosal_rtc_config_t` — RTC Configuration Structure

```c
typedef struct {
    uint8_t format;  // Time format: HOSAL_RTC_FORMAT_DEC or HOSAL_RTC_FORMAT_BCD
} hosal_rtc_config_t;
```

### `hosal_rtc_time_t` — RTC Time Structure

```c
typedef struct {
    uint8_t  sec;     // Seconds (DEC: 0~59 / BCD: 0x00~0x59)
    uint8_t  min;     // Minutes (DEC: 0~59 / BCD: 0x00~0x59)
    uint8_t  hr;      // Hours (DEC: 0~23 / BCD: 0x00~0x23)
    uint8_t  date;    // Day (DEC: 1~31 / BCD: 0x01~0x31)
    uint8_t  month;   // Month (DEC: 1~12 / BCD: 0x01~0x12)
    uint16_t year;    // Year (DEC: 0~9999 / BCD: 0x0000~0x9999)
} hosal_rtc_time_t;
```

### `hosal_rtc_dev_t` — RTC Device Structure

```c
typedef struct {
    uint8_t       port;
    hosal_rtc_config_t  config;
    void         *priv;
} hosal_rtc_dev_t;
```

## Function API

### `hosal_rtc_init`

Initialize RTC.

```c
int hosal_rtc_init(hosal_rtc_dev_t *rtc);
```

---

### `hosal_rtc_set_time`

Set time (struct mode).

```c
int hosal_rtc_set_time(hosal_rtc_dev_t *rtc, const hosal_rtc_time_t *time);
```

---

### `hosal_rtc_get_time`

Read time (struct mode).

```c
int hosal_rtc_get_time(hosal_rtc_dev_t *rtc, hosal_rtc_time_t *time);
```

---

### `hosal_rtc_set_count`

Set time (timestamp mode).

```c
int hosal_rtc_set_count(hosal_rtc_dev_t *rtc, uint64_t *time_stamp);
```

| Parameter | Description |
|-----------|-------------|
| `time_stamp` | 64-bit timestamp (seconds) |

---

### `hosal_rtc_get_count`

Read time (timestamp mode).

```c
int hosal_rtc_get_count(hosal_rtc_dev_t *rtc, uint64_t *time_stamp);
```

---

### `hosal_rtc_finalize`

Finalize RTC.

```c
int hosal_rtc_finalize(hosal_rtc_dev_t *rtc);
```

## Usage Example

```c
#include "hal_rtc.h"

hosal_rtc_dev_t rtc0 = {
    .port = 0,
    .config = {
        .format = HOSAL_RTC_FORMAT_DEC,  // Decimal format
    }
};

hosal_rtc_init(&rtc0);

// Set time
hosal_rtc_time_t set_time = {
    .year = 2025,
    .month = 6,
    .date = 18,
    .hr = 10,
    .min = 30,
    .sec = 0,
};
hosal_rtc_set_time(&rtc0, &set_time);

// Read time
hosal_rtc_time_t cur_time;
hosal_rtc_get_time(&rtc0, &cur_time);
printf("%04d-%02d-%02d %02d:%02d:%02d\r\n",
       cur_time.year, cur_time.month, cur_time.date,
       cur_time.hr, cur_time.min, cur_time.sec);

// Timestamp mode
uint64_t ts;
hosal_rtc_get_count(&rtc0, &ts);
printf("Timestamp: %llu\r\n", ts);

// Finalize
hosal_rtc_finalize(&rtc0);
```

---

## Register-Level Programming

> Register Header: `components/platform/soc/bl602/bl602_std/bl602_std/Device/Bouffalo/BL602/Peripherals/hbn_reg.h`  
> Base Address: `0x4000F000` (HBN - Hibernate domain)

### Register Overview

RTC is part of the HBN (Hibernate) subsystem.

| Offset | Name | Description |
|--------|------|-------------|
| 0x00 | HBN_TIME | RTC time register (sec, min, hr, mode) |
| 0x04 | HBN_DATE | RTC date register (day, month, year, century) |
| 0x08 | HBN_ALARM_TIME | Alarm trigger time |
| 0x0C | HBN_ALARM_DATE | Alarm trigger date |
| 0x10 | HBN_CTRL | RTC control (enable, alarm enable, LDO mode) |
| 0x14 | HBN_IRQ | RTC interrupt configuration and flags |
| 0x18 | HBN_COUNT | 40-bit hardware counter (lower 32 bits) |
| 0x1C | HBN_COUNT_H | 40-bit hardware counter (upper 8 bits) |

### Key Register Fields

**HBN_TIME (0x00)**

| Bits | Name | Description |
|------|------|-------------|
| [7:0] | sec | Seconds |
| [15:8] | min | Minutes |
| [23:16] | hr | Hours |
| 31 | hr_mode | Hour mode (0=24h, 1=12h) |

**HBN_DATE (0x04)**

| Bits | Name | Description |
|------|------|-------------|
| [7:0] | day | Day (1-31) |
| [15:8] | month | Month (1-12) |
| [23:16] | year | Year (0-9999 in DEC mode) |
| [31:24] | century | Century |

**HBN_CTRL (0x10)**

| Bits | Name | Description |
|------|------|-------------|
| 0 | rtc_enable | RTC enable |
| 1 | alarm_enable | Alarm enable |
| 2 | ldo_mode | LDO mode |

**HBN_IRQ (0x14)**

| Bits | Name | Description |
|------|------|-------------|
| 0 | rtc_irq_enable | RTC interrupt enable |
| 1 | alarm_irq_enable | Alarm interrupt enable |
| 2 | rtc_irq_flag | RTC interrupt flag (status) |

### Register-Level Code Example

```c
#include <stdint.h>

#define HBN_BASE  0x4000F000

/* Register offsets */
#define HBN_TIME       0x00
#define HBN_DATE       0x04
#define HBN_ALARM_TIME 0x08
#define HBN_ALARM_DATE 0x0C
#define HBN_CTRL       0x10
#define HBN_IRQ        0x14
#define HBN_COUNT      0x18
#define HBN_COUNT_H    0x1C

/* Bit masks */
#define HBN_CTRL_EN          (1 << 0)
#define HBN_CTRL_ALARM_EN    (1 << 1)
#define HBN_TIME_HR_MSK      (0xFF << 16)
#define HBN_TIME_HR_24H      (0 << 31)
#define HBN_IRQ_EN           (1 << 0)
#define HBN_IRQ_ALARM_EN     (1 << 1)
#define HBN_IRQ_FLAG         (1 << 2)

static volatile uint32_t * const HBN = (volatile uint32_t *)HBN_BASE;

/* Helper: pack BCD digit */
static uint8_t to_bcd(uint8_t val) {
    return ((val / 10) << 4) | (val % 10);
}

/* Helper: unpack BCD digit */
static uint8_t from_bcd(uint8_t bcd) {
    return ((bcd >> 4) * 10) + (bcd & 0x0F);
}

/* Set RTC time in DECIMAL format */
void rtc_set_time_dec(uint8_t hr, uint8_t min, uint8_t sec) {
    /* Configure 24-hour mode, write time value */
    HBN[HBN_TIME / 4] = ((uint32_t)hr << 16) | ((uint32_t)min << 8) | sec;
}

/* Set RTC date in DECIMAL format */
void rtc_set_date_dec(uint16_t year, uint8_t month, uint8_t day) {
    uint8_t century = (year / 100) % 100;
    uint16_t yr = year % 100;
    HBN[HBN_DATE / 4] = ((uint32_t)century << 24) | ((uint32_t)yr << 16) |
                         ((uint32_t)month << 8) | day;
}

/* Enable RTC */
void rtc_enable(void) {
    HBN[HBN_CTRL / 4] |= HBN_CTRL_EN;
}

/* Get current RTC time (decimal) */
void rtc_get_time_dec(uint8_t *hr, uint8_t *min, uint8_t *sec) {
    uint32_t t = HBN[HBN_TIME / 4];
    *hr = (t >> 16) & 0xFF;
    *min = (t >> 8) & 0xFF;
    *sec = t & 0xFF;
}

/* Get current RTC date (decimal) */
void rtc_get_date_dec(uint16_t *year, uint8_t *month, uint8_t *day) {
    uint32_t d = HBN[HBN_DATE / 4];
    uint8_t century = (d >> 24) & 0xFF;
    uint8_t yr = (d >> 16) & 0xFF;
    *month = (d >> 8) & 0xFF;
    *day = d & 0xFF;
    *year = (uint16_t)(century * 100 + yr);
}

/* Read 64-bit hardware counter (timestamp) */
uint64_t rtc_get_count(void) {
    uint32_t low = HBN[HBN_COUNT / 4];
    uint32_t high = HBN[HBN_COUNT_H / 4] & 0xFF;
    return ((uint64_t)high << 32) | low;
}

/* Set alarm time (decimal) */
void rtc_set_alarm(uint8_t hr, uint8_t min, uint8_t sec) {
    HBN[HBN_ALARM_TIME / 4] = ((uint32_t)hr << 16) | ((uint32_t)min << 8) | sec;
    /* Enable alarm interrupt */
    HBN[HBN_IRQ / 4] |= HBN_IRQ_ALARM_EN;
}

/* Example: set RTC to 2025-06-18 10:30:00 and read it back */
void rtc_example(void) {
    /* Set time: 10:30:00 */
    rtc_set_time_dec(10, 30, 0);

    /* Set date: 2025-06-18 */
    rtc_set_date_dec(2025, 6, 18);

    /* Enable RTC */
    rtc_enable();

    /* Read back time */
    uint8_t hr, min, sec;
    rtc_get_time_dec(&hr, &min, &sec);
    printf("Time: %02u:%02u:%02u\r\n", hr, min, sec);

    /* Read back date */
    uint16_t year;
    uint8_t month, day;
    rtc_get_date_dec(&year, &month, &day);
    printf("Date: %04u-%02u-%02u\r\n", year, month, day);

    /* Read timestamp counter */
    uint64_t ts = rtc_get_count();
    printf("Counter: %llu\r\n", ts);
}
```
