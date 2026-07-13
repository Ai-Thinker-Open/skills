# Timer API Reference (BL616/BL618)

## Overview

The Timer peripheral on BL616/BL618 provides general-purpose timer functionality with multiple clock sources, compare registers, and optional GPIO pulse capture support.

## Source File

- **Header**: `bouffalo_sdk/drivers/lhal/include/bflb_timer.h`
- **Implementation**: `bouffalo_sdk/drivers/lhal/src/bflb_timer.c`

## Base Address

| Peripheral | Base Address |
|------------|--------------|
| TIMER | `0x2000a500` |

## Clock Sources

| Constant | Value | Description |
|----------|-------|-------------|
| `TIMER_CLKSRC_32K` | 1 | 32 kHz internal RC oscillator |
| `TIMER_CLKSRC_1K` | 2 | 1 kHz clock (32K/32) |
| `TIMER_CLKSRC_XTAL` | 3 | External crystal oscillator |
| `TIMER_CLKSRC_GPIO` | 4 | External GPIO input (BL616/BL618DG only) |
| `TIMER_CLKSRC_NO` | 5 | No clock (timer disabled) |

## Counter Modes

| Constant | Value | Description |
|----------|-------|-------------|
| `TIMER_COUNTER_MODE_PROLOAD` | 0 | Counter reloads from preload value on trigger |
| `TIMER_COUNTER_MODE_UP` | 1 | Free-running up counter |

## Compare IDs

| Constant | Value | Description |
|----------|-------|-------------|
| `TIMER_COMP_ID_0` | 0 | Compare register 0 |
| `TIMER_COMP_ID_1` | 1 | Compare register 1 |
| `TIMER_COMP_ID_2` | 2 | Compare register 2 |
| `TIMER_COMP_NONE` | 3 | No compare trigger |

## Configuration Structure

```c
struct bflb_timer_config_s {
    uint8_t  counter_mode;      /* Timer counter mode, use @ref TIMER_COUNTER_MODE */
    uint8_t  clock_source;      /* Timer clock source, use @ref TIMER_CLK_SOURCE */
    uint8_t  clock_div;         /* Timer clock division value, 0-255 */
    uint8_t  trigger_comp_id;   /* Preload trigger source, use @ref TIMER_COMP_ID */
    uint32_t comp0_val;         /* Timer compare 0 value */
    uint32_t comp1_val;         /* Timer compare 1 value */
    uint32_t comp2_val;         /* Timer compare 2 value */
    uint32_t preload_val;       /* Timer preload value */
};
```

## API Functions

### bflb_timer_init

Initialize the timer with configuration.

```c
void bflb_timer_init(struct bflb_device_s *dev, const struct bflb_timer_config_s *config);
```

**Parameters:**
- `dev` - Device handle (e.g., `bflb_device_get_by_name("timer")`)
- `config` - Pointer to timer configuration structure

---

### bflb_timer_start

Start the timer.

```c
void bflb_timer_start(struct bflb_device_s *dev);
```

**Parameters:**
- `dev` - Device handle

---

### bflb_timer_stop

Stop the timer.

```c
void bflb_timer_stop(struct bflb_device_s *dev);
```

**Parameters:**
- `dev` - Device handle

---

### bflb_timer_set_preloadvalue

Set the timer preload value.

```c
void bflb_timer_set_preloadvalue(struct bflb_device_s *dev, uint32_t val);
```

**Parameters:**
- `dev` - Device handle
- `val` - Preload value

---

### bflb_timer_set_compvalue

Set the compare value for a specific compare ID.

```c
void bflb_timer_set_compvalue(struct bflb_device_s *dev, uint8_t cmp_no, uint32_t val);
```

**Parameters:**
- `dev` - Device handle
- `cmp_no` - Compare ID (`TIMER_COMP_ID_0`, `TIMER_COMP_ID_1`, `TIMER_COMP_ID_2`)
- `val` - Compare value

---

### bflb_timer_get_compvalue

Get the compare value for a specific compare ID.

```c
uint32_t bflb_timer_get_compvalue(struct bflb_device_s *dev, uint8_t cmp_no);
```

**Returns:** Current compare value

---

### bflb_timer_get_countervalue

Get the current timer counter value.

```c
uint32_t bflb_timer_get_countervalue(struct bflb_device_s *dev);
```

**Returns:** Current counter value

---

### bflb_timer_compint_mask

Enable or disable timer compare interrupt.

```c
void bflb_timer_compint_mask(struct bflb_device_s *dev, uint8_t cmp_no, bool mask);
```

**Parameters:**
- `dev` - Device handle
- `cmp_no` - Compare ID
- `mask` - `true` to disable, `false` to enable

---

### bflb_timer_compint_clear

Clear the compare interrupt flag.

```c
void bflb_timer_compint_clear(struct bflb_device_s *dev, uint8_t cmp_no);
```

**Parameters:**
- `dev` - Device handle
- `cmp_no` - Compare ID

---

### bflb_timer_feature_control

Control advanced timer features.

```c
int bflb_timer_feature_control(struct bflb_device_s *dev, int cmd, size_t arg);
```

**Commands (BL616CL):**
- `TIMER_CMD_DMA_REQUEST_SET_COMPARE_ID` - Set DMA request compare ID
- `TIMER_CMD_GPIO_PULSE_SET_ENABLE` - Enable GPIO pulse capture
- `TIMER_CMD_GPIO_PULSE_SET_POLARITY` - Set GPIO pulse polarity
- `TIMER_CMD_GPIO_PULSE_GET_BUSY` - Get GPIO pulse busy status
- `TIMER_CMD_GPIO_PULSE_GET_VALUE` - Get GPIO pulse value

---

## Usage Example

### Basic Timer with Interrupt

```c
#include "bflb_timer.h"
#include "bflb_irq.h"

static struct bflb_device_s *timer;

void timer_isr(void *arg)
{
    /* Check and clear compare 0 interrupt */
    if (bflb_timer_get_compint_status(timer, TIMER_COMP_ID_0)) {
        bflb_timer_compint_clear(timer, TIMER_COMP_ID_0);
        printf("Timer compare 0 interrupt!\r\n");
    }
}

void timer_example(void)
{
    struct bflb_timer_config_s config = {
        .counter_mode = TIMER_COUNTER_MODE_UP,
        .clock_source = TIMER_CLKSRC_32K,
        .clock_div = 0,
        .trigger_comp_id = TIMER_COMP_NONE,
        .comp0_val = 32000,      /* 1 second at 32kHz clock */
        .comp1_val = 0,
        .comp2_val = 0,
        .preload_val = 0,
    };

    /* Get device handle */
    timer = bflb_device_get_by_name("timer");
    
    /* Initialize timer */
    bflb_timer_init(timer, &config);
    
    /* Register interrupt callback */
    bflb_irq_register(timer->irq_num, timer_isr, NULL);
    
    /* Enable compare 0 interrupt */
    bflb_timer_compint_mask(timer, TIMER_COMP_ID_0, false);
    
    /* Start timer */
    bflb_timer_start(timer);
}
```

### Periodic Interrupt Using Compare Value

```c
void periodic_timer_example(void)
{
    struct bflb_timer_config_s config = {
        .counter_mode = TIMER_COUNTER_MODE_UP,
        .clock_source = TIMER_CLKSRC_XTAL,
        .clock_div = 255,        /* XTAL / 256 */
        .trigger_comp_id = TIMER_COMP_NONE,
        .comp0_val = 62500,      /* ~1 second at 16MHz after divider */
        .comp1_val = 0,
        .comp2_val = 0,
        .preload_val = 0,
    };

    timer = bflb_device_get_by_name("timer");
    bflb_timer_init(timer, &config);
    
    /* Enable interrupt */
    bflb_timer_compint_mask(timer, TIMER_COMP_ID_0, false);
    bflb_irq_enable(timer->irq_num);
    
    bflb_timer_start(timer);
    
    while (1) {
        /* Application code */
    }
}
```

## Register-Level Overview

| Register | Offset | Description |
|----------|--------|-------------|
| `TIMER_CR` | `0x00` | Timer control register |
| `TIMER_SR` | `0x04` | Timer status register |
| `TIMER_CV` | `0x08` | Timer current value |
| `TIMER_PRELOAD` | `0x0C` | Preload value register |
| `TIMER_COMP0` | `0x10` | Compare 0 value |
| `TIMER_COMP1` | `0x14` | Compare 1 value |
| `TIMER_COMP2` | `0x18` | Compare 2 value |
| `TIMER_COMP_INT` | `0x1C` | Compare interrupt enable/mask |
| `TIMER_INT` | `0x20` | Interrupt status/clear |

## Interrupt Numbers

| Timer Channel | IRQ Number |
|--------------|------------|
| Timer CH0 | `TIMER0_CH0_IRQn` (36) |
| Timer CH1 | `TIMER0_CH1_IRQn` (37) |
| Watchdog | `TIMER0_WDT_IRQn` (38) |
