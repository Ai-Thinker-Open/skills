# PWM API Reference

> Source file: `components/platform/hosal/include/hosal_pwm.h`

## Type Definitions

### `hosal_pwm_config_t` — PWM Configuration Structure

```c
typedef struct {
    uint8_t    pin;        // PWM pin
    uint32_t   duty_cycle; // Duty cycle, range 0~10000 (corresponding to 0%~100%)
    uint32_t   freq;       // Frequency Hz, max 40MHz
} hosal_pwm_config_t;
```

> Note: `duty_cycle` uses ten-thousandths as unit, 5000 = 50% duty cycle.

### `hosal_pwm_dev_t` — PWM Device Structure

```c
typedef struct {
    uint8_t       port;         // PWM port
    hosal_pwm_config_t  config;
    void         *priv;
} hosal_pwm_dev_t;
```

## Function Interface

### `hosal_pwm_init`

Initialize PWM.

```c
int hosal_pwm_init(hosal_pwm_dev_t *pwm);
```

---

### `hosal_pwm_start`

Start PWM output.

```c
int hosal_pwm_start(hosal_pwm_dev_t *pwm);
```

---

### `hosal_pwm_stop`

Stop PWM output.

```c
int hosal_pwm_stop(hosal_pwm_dev_t *pwm);
```

---

### `hosal_pwm_para_chg`

Dynamically change PWM parameters (frequency + duty cycle updated simultaneously).

```c
int hosal_pwm_para_chg(hosal_pwm_dev_t *pwm, hosal_pwm_config_t para);
```

---

### `hosal_pwm_freq_set`

Set PWM frequency individually.

```c
int hosal_pwm_freq_set(hosal_pwm_dev_t *pwm, uint32_t freq);
```

| Parameter | Description |
|-----------|-------------|
| `pwm` | PWM device |
| `freq` | Frequency Hz (0~40M) |

---

### `hosal_pwm_freq_get`

Get current PWM frequency.

```c
int hosal_pwm_freq_get(hosal_pwm_dev_t *pwm, uint32_t *p_freq);
```

---

### `hosal_pwm_duty_set`

Set PWM duty cycle individually.

```c
int hosal_pwm_duty_set(hosal_pwm_dev_t *pwm, uint32_t duty);
```

| Parameter | Description |
|-----------|-------------|
| `duty` | Duty cycle, range 0~10000 (5000 = 50%) |

---

### `hosal_pwm_duty_get`

Get current PWM duty cycle.

```c
int hosal_pwm_duty_get(hosal_pwm_dev_t *pwm, uint32_t *p_duty);
```

---

### `hosal_pwm_finalize`

Release PWM.

```c
int hosal_pwm_finalize(hosal_pwm_dev_t *pwm);
```

## Usage Example

```c
#include "hal_pwm.h"

// Initialize: 10kHz, 50% duty cycle
hosal_pwm_dev_t pwm0 = {
    .port = 0,
    .config = {
        .pin = 10,
        .freq = 10000,        // 10kHz
        .duty_cycle = 5000,   // 50% (5000/10000)
    }
};

hosal_pwm_init(&pwm0);
hosal_pwm_start(&pwm0);

// Dynamic adjustment: change to 80% duty cycle
hosal_pwm_duty_set(&pwm0, 8000);

// Dynamic adjustment: change to 1kHz frequency
hosal_pwm_freq_set(&pwm0, 1000);

// Change both frequency and duty cycle simultaneously
hosal_pwm_config_t new_para = {
    .pin = 10,
    .freq = 5000,
    .duty_cycle = 2500,  // 25%
};
hosal_pwm_para_chg(&pwm0, new_para);

// Stop
hosal_pwm_stop(&pwm0);
```

---

## Register-Level Programming

> Register Header: `components/platform/soc/bl602/bl602_std/bl602_std/Device/Bouffalo/BL602/Peripherals/timer_reg.h`  
> Base Address: `0x4000A500` (shared with Timer; PWM channels 0-4 start at offset `0x20`, 0x1C bytes per channel)

### Register Overview

PWM channels 0-4 share the Timer peripheral registers. Each channel occupies a 0x1C-aligned block. Registers listed are for channel N starting at offset `0x20 + N*0x1C`.

| Offset (ch N) | Name   | Description                                 |
|---------------|--------|---------------------------------------------|
| 0x20+N*0x1C   | TCCR   | Timer counter control: enable, free-run     |
| 0x24+N*0x1C   | TMR2   | PWM mode: output enable, polarity/mode      |
| 0x28+N*0x1C   | TMR3   | PWM threshold thre2 (toggle/active point)   |
| 0x2C+N*0x1C   | TIER   | Timer interrupt enable                       |
| 0x30+N*0x1C   | TISR   | Timer interrupt status                       |
| 0x34+N*0x1C   | WMR    | PWM period match value (counter clears here)|
| 0x38+N*0x1C   | WVR    | PWM threshold thre1                         |
| 0x3C+N*0x1C   | TCNT   | Current timer counter value (read-only)      |

### Key Register Fields

**TCCR — Timer Counter Control Register (per channel)**

| Bits | Name     | Description                                      |
|------|----------|--------------------------------------------------|
| 0    | enable   | Timer channel enable (1=enable, 0=disable)       |
| 1    | free_run | Free-run (1=free run, 0=clear on match)          |

**TMR2 — PWM Mode Register (per channel)**

| Bits  | Name       | Description                                           |
|-------|------------|-------------------------------------------------------|
| 8     | pwm_out_en | PWM output enable (1=enable output on PWM pin)       |
| [3:0] | pwm_mode   | 0=no PWM output, 1=always low, 2=always high, 3=PWM  |

**WMR — PWM Period Register (per channel, 16-bit)**

| Bits   | Name | Description                                                         |
|--------|------|---------------------------------------------------------------------|
| [15:0] | wmr  | Counter clears at this value. PWM period = (WMR+1) timer clocks.  |

**WVR — PWM Threshold 1 Register (per channel, 16-bit)**

| Bits   | Name | Description                                               |
|--------|------|-----------------------------------------------------------|
| [15:0] | wvr  | Active period ends when counter reaches this value.      |

**TMR3 — PWM Threshold 2 Register (per channel, 16-bit)**

| Bits   | Name  | Description                                         |
|--------|-------|-----------------------------------------------------|
| [15:0] | thre2 | Second threshold (toggle point for some PWM modes) |

### Register-Level Code Example

```c
#include <stdint.h>

#define TIMER_BASE  0x4000A500UL

/* Helper to compute register address for channel N */
#define PWM_TCCR(ch)   *(volatile uint32_t *)(TIMER_BASE + 0x20 + (ch) * 0x1C + 0x00)
#define PWM_TMR2(ch)   *(volatile uint32_t *)(TIMER_BASE + 0x20 + (ch) * 0x1C + 0x04)
#define PWM_TMR3(ch)   *(volatile uint32_t *)(TIMER_BASE + 0x20 + (ch) * 0x1C + 0x08)
#define PWM_TIER(ch)   *(volatile uint32_t *)(TIMER_BASE + 0x20 + (ch) * 0x1C + 0x0C)
#define PWM_TISR(ch)   *(volatile uint32_t *)(TIMER_BASE + 0x20 + (ch) * 0x1C + 0x10)
#define PWM_WMR(ch)    *(volatile uint32_t *)(TIMER_BASE + 0x20 + (ch) * 0x1C + 0x14)
#define PWM_WVR(ch)    *(volatile uint32_t *)(TIMER_BASE + 0x20 + (ch) * 0x1C + 0x18)
#define PWM_TCNT(ch)   *(volatile uint32_t *)(TIMER_BASE + 0x20 + (ch) * 0x1C + 0x1C)

/* Configure PWM on channel 0: freq Hz, duty percent (0-10000)
 * Timer clock is typically the bus clock (32MHz).
 * PWM period = (WMR + 1) timer clocks
 * Active duty = (WVR / (WMR + 1)) * 100%
 */
void pwm_channel_config(uint8_t ch, uint32_t freq_hz, uint16_t duty_percent)
{
    uint32_t timer_clk_hz = 32000000UL;  /* bus clock, adjust as needed */
    uint32_t wmr, wvr;

    /* Compute period and threshold for requested frequency and duty */
    wmr = (timer_clk_hz / freq_hz) - 1;
    wvr = (wmr + 1) * duty_percent / 10000;

    /* Disable channel while configuring */
    PWM_TCCR(ch) = 0x00;

    /* Set period and duty registers */
    PWM_WMR(ch)  = wmr & 0xFFFF;
    PWM_WVR(ch)  = wvr & 0xFFFF;
    PWM_TMR3(ch) = 0;  /* thre2 = 0 (use WVR as primary threshold) */

    /* Enable PWM output, mode = 3 (clear on match / PWM active high) */
    PWM_TMR2(ch) = (1 << 8)   /* pwm_out_en */
                 | (3 << 0);  /* pwm_mode = 3: clear on match */

    /* Enable counter in free-run mode */
    PWM_TCCR(ch) = (1 << 1)   /* free_run = 1 */
                 | (1 << 0);  /* enable   = 1 */
}

/* Stop a PWM channel */
void pwm_channel_stop(uint8_t ch)
{
    PWM_TCCR(ch) &= ~(1 << 0);  /* clear enable */
}

/* Read current duty cycle (approximation via WVR/WMR) */
uint16_t pwm_channel_get_duty(uint8_t ch)
{
    uint32_t wmr = PWM_WMR(ch) & 0xFFFF;
    uint32_t wvr = PWM_WVR(ch) & 0xFFFF;
    if (wmr == 0)
        return 0;
    return (uint16_t)((wvr * 10000) / (wmr + 1));
}

/* Example: Initialize channel 0 as 10kHz, 50% duty */
void pwm_reg_example(void)
{
    pwm_channel_config(0, 10000, 5000);  /* 10kHz, 50% */

    /* After some time, change to 20kHz, 25% duty */
    pwm_channel_config(0, 20000, 2500);

    /* Stop it */
    pwm_channel_stop(0);
}
```
