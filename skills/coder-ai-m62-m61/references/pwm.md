# PWM API Reference (BL616/BL618)

## Overview

The PWM peripheral on BL616/BL618 provides up to 4 PWM channels with advanced features including dead-time insertion, brake input, and PWM-triggered ADC conversions. The BL616/BL618 uses the PWMv2 IP block.

## Source File

- **Header**: `bouffalo_sdk/drivers/lhal/include/bflb_pwm_v2.h`
- **Implementation**: `bouffalo_sdk/drivers/lhal/src/bflb_pwm_v2.c`

## Base Address

| Peripheral | Base Address |
|------------|--------------|
| PWM | `0x2000a400` |

## PWM Channels

| Constant | Value | Description |
|----------|-------|-------------|
| `PWM_CH0` | 0 | PWM Channel 0 |
| `PWM_CH1` | 1 | PWM Channel 1 |
| `PWM_CH2` | 2 | PWM Channel 2 |
| `PWM_CH3` | 3 | PWM Channel 3 |

**Note**: BL616/BL618 has 4 PWM channels (PWMv2 IP).

## Polarity

| Constant | Value | Description |
|----------|-------|-------------|
| `PWM_POLARITY_ACTIVE_LOW` | 0 | Active low polarity |
| `PWM_POLARITY_ACTIVE_HIGH` | 1 | Active high polarity |

## State Definitions

| Constant | Value | Description |
|----------|-------|-------------|
| `PWM_STATE_INACTIVE` | 0 | Inactive state |
| `PWM_STATE_ACTIVE` | 1 | Active state |

## PWMv2 Configuration Structure

```c
struct bflb_pwm_v2_config_s {
    uint8_t  clk_source;    /* PWM clock source, use @ref BFLB_SYSTEM_CLOCK */
    uint16_t clk_div;        /* PWM clock divider, 1-65535 */
    uint16_t period;         /* PWM period count, 2-65535 */
};
```

## PWM Channel Configuration Structure

```c
struct bflb_pwm_v2_channel_config_s {
    uint8_t positive_polarity;     /* Positive polarity, use @ref PWM_POLARITY */
    uint8_t negative_polarity;     /* Negative polarity, use @ref PWM_POLARITY */
    uint8_t positive_stop_state;   /* Positive state when stopped, use @ref PWM_STATE */
    uint8_t negative_stop_state;   /* Negative state when stopped, use @ref PWM_STATE */
    uint8_t positive_brake_state;   /* Positive state on brake, use @ref PWM_STATE */
    uint8_t negative_brake_state;   /* Negative state on brake, use @ref PWM_STATE */
    uint8_t dead_time;             /* Dead time value */
};
```

## API Functions

### bflb_pwm_v2_init

Initialize PWM with configuration.

```c
void bflb_pwm_v2_init(struct bflb_device_s *dev, const struct bflb_pwm_v2_config_s *config);
```

**Parameters:**
- `dev` - Device handle (e.g., `bflb_device_get_by_name("pwm")`)
- `config` - Pointer to PWM configuration structure

**Example:**
```c
struct bflb_pwm_v2_config_s config = {
    .clk_source = BFLB_SYSTEM_PBCLK,  /* or BFLB_SYSTEM_XCLK, BFLB_SYSTEM_32K_CLK */
    .clk_div = 255,                    /* Divide by 255 */
    .period = 1000,                     /* Period of 1000 counts */
};
bflb_pwm_v2_init(pwm, &config);
```

---

### bflb_pwm_v2_deinit

Deinitialize PWM.

```c
void bflb_pwm_v2_deinit(struct bflb_device_s *dev);
```

---

### bflb_pwm_v2_start

Start PWM output.

```c
void bflb_pwm_v2_start(struct bflb_device_s *dev);
```

**Parameters:**
- `dev` - Device handle

---

### bflb_pwm_v2_stop

Stop PWM output.

```c
void bflb_pwm_v2_stop(struct bflb_device_s *dev);
```

**Parameters:**
- `dev` - Device handle

---

### bflb_pwm_v2_channel_init

Initialize a specific PWM channel.

```c
void bflb_pwm_v2_channel_init(struct bflb_device_s *dev, uint8_t ch, 
                              struct bflb_pwm_v2_channel_config_s *config);
```

**Parameters:**
- `dev` - Device handle
- `ch` - Channel number (0-3)
- `config` - Channel configuration

---

### bflb_pwm_v2_channel_set_threshold

Set the PWM duty cycle by configuring threshold values.

```c
void bflb_pwm_v2_channel_set_threshold(struct bflb_device_s *dev, uint8_t ch,
                                       uint16_t low_threshold, uint16_t high_threshold);
```

**Parameters:**
- `dev` - Device handle
- `ch` - Channel number (0-3)
- `low_threshold` - Low threshold (rising edge position)
- `high_threshold` - High threshold (falling edge position)

**Duty Cycle Calculation:**
```
Duty Cycle (%) = (high_threshold - low_threshold) / period * 100%
```

---

### bflb_pwm_v2_channel_positive_start

Start positive PWM output on a channel.

```c
void bflb_pwm_v2_channel_positive_start(struct bflb_device_s *dev, uint8_t ch);
```

---

### bflb_pwm_v2_channel_negative_start

Start negative PWM output on a channel.

```c
void bflb_pwm_v2_channel_negative_start(struct bflb_device_s *dev, uint8_t ch);
```

---

### bflb_pwm_v2_channel_positive_stop

Stop positive PWM output on a channel.

```c
void bflb_pwm_v2_channel_positive_stop(struct bflb_device_s *dev, uint8_t ch);
```

---

### bflb_pwm_v2_channel_negative_stop

Stop negative PWM output on a channel.

```c
void bflb_pwm_v2_channel_negative_stop(struct bflb_device_s *dev, uint8_t ch);
```

---

### bflb_pwm_v2_set_period

Set the PWM period (affects frequency).

```c
void bflb_pwm_v2_set_period(struct bflb_device_s *dev, uint16_t period);
```

**Frequency Calculation:**
```
Frequency (Hz) = PWM_source_clock / clk_div / period
```

---

### bflb_pwm_v2_get_frequency

Get the current PWM frequency.

```c
uint32_t bflb_pwm_v2_get_frequency(struct bflb_device_s *dev);
```

**Returns:** Current frequency in Hz

---

### bflb_pwm_v2_get_duty

Get the current duty cycle.

```c
void bflb_pwm_v2_get_duty(struct bflb_device_s *dev, uint8_t ch, uint32_t *delta, uint32_t *period);
```

**Parameters:**
- `dev` - Device handle
- `ch` - Channel number
- `delta` - Pointer to store (high_threshold - low_threshold)
- `period` - Pointer to store period value

---

### bflb_pwm_v2_int_enable

Enable PWM interrupts.

```c
void bflb_pwm_v2_int_enable(struct bflb_device_s *dev, uint32_t int_en, bool enable);
```

**Interrupt Flags:**
- `PWM_INTEN_CH0_L` - Channel 0 low interrupt
- `PWM_INTEN_CH0_H` - Channel 0 high interrupt
- `PWM_INTEN_CH1_L`, `PWM_INTEN_CH1_H`
- `PWM_INTEN_CH2_L`, `PWM_INTEN_CH2_H`
- `PWM_INTEN_CH3_L`, `PWM_INTEN_CH3_H`
- `PWM_INTEN_PERIOD` - Period interrupt
- `PWM_INTEN_BRAKE` - Brake interrupt
- `PWM_INTEN_REPT` - Repeat count interrupt

---

### bflb_pwm_v2_get_intstatus

Get interrupt status.

```c
uint32_t bflb_pwm_v2_get_intstatus(struct bflb_device_s *dev);
```

**Returns:** Interrupt status flags

---

### bflb_pwm_v2_int_clear

Clear interrupt flags.

```c
void bflb_pwm_v2_int_clear(struct bflb_device_s *dev, uint32_t int_clear);
```

---

### bflb_pwm_v2_feature_control

Control advanced PWM features.

```c
int bflb_pwm_v2_feature_control(struct bflb_device_s *dev, int cmd, size_t arg);
```

**Commands:**
- `PWM_CMD_SET_TRIG_ADC_SRC` - Set ADC trigger source
- `PWM_CMD_SET_EXT_BRAKE_ENABLE` - Enable external brake
- `PWM_CMD_SET_EXT_BRAKE_POLARITY` - Set brake polarity
- `PWM_CMD_SET_SW_BRAKE_ENABLE` - Enable software brake
- `PWM_CMD_SET_STOP_ON_REPT` - Stop on repeat count
- `PWM_CMD_SET_REPT_COUNT` - Set repeat count
- `PWM_CMD_IO_SEL` - Configure I/O selection (BL616/BL616CL/BL618DG)

---

## Usage Examples

### Basic PWM Output (LED Dimming)

```c
#include "bflb_pwm_v2.h"

void pwm_led_example(void)
{
    struct bflb_device_s *pwm;
    struct bflb_pwm_v2_config_s pwm_cfg = {
        .clk_source = BFLB_SYSTEM_PBCLK,
        .clk_div = 255,        /* 80MHz / 255 = ~313kHz */
        .period = 1000,         /* 1000 counts per period */
    };
    struct bflb_pwm_v2_channel_config_s ch_cfg = {
        .positive_polarity = PWM_POLARITY_ACTIVE_HIGH,
        .negative_polarity = PWM_POLARITY_ACTIVE_LOW,
        .positive_stop_state = PWM_STATE_INACTIVE,
        .negative_stop_state = PWM_STATE_INACTIVE,
        .positive_brake_state = PWM_STATE_INACTIVE,
        .negative_brake_state = PWM_STATE_INACTIVE,
        .dead_time = 0,
    };

    pwm = bflb_device_get_by_name("pwm");
    
    /* Initialize PWM */
    bflb_pwm_v2_init(pwm, &pwm_cfg);
    
    /* Configure channel 0 */
    bflb_pwm_v2_channel_init(pwm, PWM_CH0, &ch_cfg);
    
    /* Set 50% duty cycle (low=250, high=750 in 1000 period) */
    bflb_pwm_v2_channel_set_threshold(pwm, PWM_CH0, 250, 750);
    
    /* Start PWM on positive side */
    bflb_pwm_v2_channel_positive_start(pwm, PWM_CH0);
    
    /* Start PWM */
    bflb_pwm_v2_start(pwm);
}
```

### PWM with Dead-Time (Complementary Outputs)

```c
void pwm_deadtime_example(void)
{
    struct bflb_device_s *pwm;
    struct bflb_pwm_v2_config_s pwm_cfg = {
        .clk_source = BFLB_SYSTEM_PBCLK,
        .clk_div = 63,          /* 80MHz / 64 = 1.25MHz */
        .period = 1250,        /* 1kHz PWM */
    };
    struct bflb_pwm_v2_channel_config_s ch_cfg = {
        .positive_polarity = PWM_POLARITY_ACTIVE_HIGH,
        .negative_polarity = PWM_POLARITY_ACTIVE_HIGH,
        .positive_stop_state = PWM_STATE_INACTIVE,
        .negative_stop_state = PWM_STATE_INACTIVE,
        .positive_brake_state = PWM_STATE_INACTIVE,
        .negative_brake_state = PWM_STATE_INACTIVE,
        .dead_time = 50,        /* 50 clock cycles dead-time */
    };

    pwm = bflb_device_get_by_name("pwm");
    bflb_pwm_v2_init(pwm, &pwm_cfg);
    
    /* Configure channel for complementary outputs with dead-time */
    bflb_pwm_v2_channel_init(pwm, PWM_CH0, &ch_cfg);
    
    /* 30% duty cycle */
    bflb_pwm_v2_channel_set_threshold(pwm, PWM_CH0, 0, 375);
    
    /* Start both positive and negative outputs */
    bflb_pwm_v2_channel_positive_start(pwm, PWM_CH0);
    bflb_pwm_v2_channel_negative_start(pwm, PWM_CH0);
    
    bflb_pwm_v2_start(pwm);
}
```

### Multiple PWM Channels

```c
void pwm_multi_channel_example(void)
{
    struct bflb_device_s *pwm;
    struct bflb_pwm_v2_config_s pwm_cfg = {
        .clk_source = BFLB_SYSTEM_PBCLK,
        .clk_div = 255,
        .period = 1000,
    };
    struct bflb_pwm_v2_channel_config_s ch_cfg = {
        .positive_polarity = PWM_POLARITY_ACTIVE_HIGH,
        .negative_polarity = PWM_POLARITY_ACTIVE_LOW,
        .positive_stop_state = PWM_STATE_INACTIVE,
        .negative_stop_state = PWM_STATE_INACTIVE,
        .positive_brake_state = PWM_STATE_INACTIVE,
        .negative_brake_state = PWM_STATE_INACTIVE,
        .dead_time = 0,
    };

    pwm = bflb_device_get_by_name("pwm");
    bflb_pwm_v2_init(pwm, &pwm_cfg);
    
    /* Configure all 4 channels */
    for (int ch = PWM_CH0; ch <= PWM_CH3; ch++) {
        bflb_pwm_v2_channel_init(pwm, ch, &ch_cfg);
        /* Each channel gets different duty cycle */
        bflb_pwm_v2_channel_set_threshold(pwm, ch, (ch * 100), ((ch + 1) * 100));
        bflb_pwm_v2_channel_positive_start(pwm, ch);
    }
    
    bflb_pwm_v2_start(pwm);
}
```

## Register-Level Overview

| Register | Offset | Description |
|----------|--------|-------------|
| `PWM_CR` | `0x00` | PWM control register |
| `PWM_PRESCALE` | `0x04` | Clock prescaler |
| `PWM_PERIOD` | `0x08` | PWM period value |
| `PWM_CNT` | `0x0C` | PWM counter value |
| `PWM_THRE0` | `0x10` | Channel 0 threshold |
| `PWM_THRE1` | `0x14` | Channel 1 threshold |
| `PWM_THRE2` | `0x18` | Channel 2 threshold |
| `PWM_THRE3` | `0x1C` | Channel 3 threshold |
| `PWM_DT` | `0x20` | Dead-time configuration |
| `PWM_INT` | `0x24` | Interrupt enable/status |
| `PWM_BR` | `0x28` | Brake configuration |

## Interrupt Number

| Peripheral | IRQ Number |
|------------|------------|
| PWM | `PWM_IRQn` (33) |

## Clock Source Options

| Constant | Description |
|----------|-------------|
| `BFLB_SYSTEM_PBCLK` | Peripheral clock (typically 80MHz) |
| `BFLB_SYSTEM_XCLK` | External crystal clock |
| `BFLB_SYSTEM_32K_CLK` | 32kHz internal clock |
