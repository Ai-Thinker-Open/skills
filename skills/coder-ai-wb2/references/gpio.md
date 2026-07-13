# GPIO API Reference

> Source file: `components/platform/hosal/include/hosal_gpio.h`

## Type Definitions

### `hosal_gpio_config_t` — GPIO Mode

```c
typedef enum {
    ANALOG_MODE,               // Analog mode (used as function pin)
    INPUT_PULL_UP,             // Input with pull-up (button connects to ground)
    INPUT_PULL_DOWN,           // Input with pull-down (button connects to power)
    INPUT_HIGH_IMPEDANCE,      // High impedance input (must be driven)
    OUTPUT_PUSH_PULL,          // Push-pull output (LED, etc.)
    OUTPUT_OPEN_DRAIN_NO_PULL, // Open-drain output (no pull-up)
    OUTPUT_OPEN_DRAIN_PULL_UP, // Open-drain output (internal pull-up)
    OUTPUT_OPEN_DRAIN_AF,      // Open-drain alternate function
    OUTPUT_PUSH_PULL_AF,       // Push-pull alternate function
} hosal_gpio_config_t;
```

### `hosal_gpio_irq_trigger_t` — Interrupt Trigger Type

```c
typedef enum {
    HOSAL_IRQ_TRIG_NEG_PULSE,  // Falling edge pulse trigger
    HOSAL_IRQ_TRIG_POS_PULSE,  // Rising edge pulse trigger
    HOSAL_IRQ_TRIG_NEG_LEVEL,  // Falling edge level trigger (32k 3T)
    HOSAL_IRQ_TRIG_POS_LEVEL,   // Rising edge level trigger (32k 3T)
} hosal_gpio_irq_trigger_t;
```

### `hosal_gpio_irq_handler_t` — Interrupt Callback Function Type

```c
typedef void (*hosal_gpio_irq_handler_t)(void *arg);
```

### `hosal_gpio_dev_t` — GPIO Device Structure

```c
typedef struct {
    uint8_t        port;         // GPIO port
    hosal_gpio_config_t  config; // GPIO configuration mode
    void          *priv;         // Private data
} hosal_gpio_dev_t;
```

## Function Interface

### `hosal_gpio_init`

Initializes a GPIO pin.

```c
int hosal_gpio_init(hosal_gpio_dev_t *gpio);
```

| Parameter | Description |
|-----------|-------------|
| `gpio` | GPIO device structure pointer |

**Return value**: `0` success, `EIO` failure

---

### `hosal_gpio_output_set`

Sets GPIO output level.

```c
int hosal_gpio_output_set(hosal_gpio_dev_t *gpio, uint8_t value);
```

| Parameter | Description |
|-----------|-------------|
| `gpio` | GPIO device |
| `value` | `0` = output low, `>0` = output high |

**Return value**: `0` success, `EIO` failure

---

### `hosal_gpio_input_get`

Reads GPIO input level.

```c
int hosal_gpio_input_get(hosal_gpio_dev_t *gpio, uint8_t *value);
```

| Parameter | Description |
|-----------|-------------|
| `gpio` | GPIO device |
| `value` | Output parameter, stores the read level value |

**Return value**: `0` success, `EIO` failure

---

### `hosal_gpio_irq_set`

Configures GPIO interrupt.

```c
int hosal_gpio_irq_set(hosal_gpio_dev_t *gpio,
                        hosal_gpio_irq_trigger_t trigger,
                        hosal_gpio_irq_handler_t handler,
                        void *arg);
```

| Parameter | Description |
|-----------|-------------|
| `gpio` | GPIO device |
| `trigger` | Trigger type |
| `handler` | Interrupt callback function |
| `arg` | Argument passed to the callback |

**Return value**: `0` success, `EIO` failure

---

### `hosal_gpio_irq_mask`

Masks or enables GPIO interrupt.

```c
int hosal_gpio_irq_mask(hosal_gpio_dev_t *gpio, uint8_t mask);
```

| Parameter | Description |
|-----------|-------------|
| `gpio` | GPIO device |
| `mask` | `0` = enable interrupt, `1` = mask interrupt |

**Return value**: `0` success, `EIO` failure

---

### `hosal_gpio_finalize`

Releases GPIO.

```c
int hosal_gpio_finalize(hosal_gpio_dev_t *gpio);
```

| Parameter | Description |
|-----------|-------------|
| `gpio` | GPIO device |

**Return value**: `0` success, `EIO` failure

## Usage Example

```c
#include "hal_gpio.h"

hosal_gpio_dev_t led = {
    .port = 0,
    .config = OUTPUT_PUSH_PULL,
};

// Initialize as push-pull output
hosal_gpio_init(&led);

// Output high level (turn on LED)
hosal_gpio_output_set(&led, 1);

// Input mode + interrupt
hosal_gpio_dev_t btn = {
    .port = 1,
    .config = INPUT_PULL_UP,
};
hosal_gpio_init(&btn);
hosal_gpio_irq_set(&btn, HOSAL_IRQ_TRIG_NEG_PULSE, my_handler, NULL);
```

---

## Register-Level Programming

> Register Header: `components/platform/soc/bl602/bl602_std/bl602_std/Device/Bouffalo/BL602/Peripherals/glb_reg.h`  
> Base Address: GLB_BASE = 0x40000000 (GPIO peripheral is part of GLB)

### Register Overview

| Offset | Name | Description |
|--------|------|-------------|
| 0x000 | GLB_CFG_BASE_ADDR | Global configuration base address |
| 0x004 | GLB_SWRST_CFG0 | Software reset configuration 0 |
| 0x008 | GLB_SWRST_CFG1 | Software reset configuration 1 |
| 0x00C | GLB_SWRST_CFG2 | Software reset configuration 2 |
| 0x040 | GLB_MISC_CFG0 | Miscellaneous configuration 0 |
| 0x044 | GLB_MISC_CFG1 | Miscellaneous configuration 1 |
| 0x100 | GPIO_OUTPUT_0 | GPIO output data for pins 0-31 |
| 0x104 | GPIO_OUTPUT_1 | GPIO output data for pins 32-63 |
| 0x108 | GPIO_OUTPUT_2 | GPIO output data for pins 64-95 |
| 0x10C | GPIO_OUTPUT_3 | GPIO output data for pins 96-127 |
| 0x110 | GPIO_OUTPUT_DRV0 | GPIO drive strength for pins 0-31 |
| 0x114 | GPIO_OUTPUT_DRV1 | GPIO drive strength for pins 32-63 |
| 0x118 | GPIO_OUTPUT_DRV2 | GPIO drive strength for pins 64-95 |
| 0x11C | GPIO_OUTPUT_DRV3 | GPIO drive strength for pins 96-127 |
| 0x120 | GPIO_PTMODE_0 | GPIO pin mode for pins 0-31 |
| 0x124 | GPIO_PTMODE_1 | GPIO pin mode for pins 32-63 |
| 0x128 | GPIO_PTMODE_2 | GPIO pin mode for pins 64-95 |
| 0x12C | GPIO_PTMODE_3 | GPIO pin mode for pins 96-127 |
| 0x130 | GPIO_INPUT_0 | GPIO input data for pins 0-31 |
| 0x134 | GPIO_INPUT_1 | GPIO input data for pins 32-63 |
| 0x138 | GPIO_INPUT_2 | GPIO input data for pins 64-95 |
| 0x13C | GPIO_INPUT_3 | GPIO input data for pins 96-127 |
| 0x160 | GPIO_INT_MODE_0 | GPIO interrupt mode for pins 0-31 |
| 0x164 | GPIO_INT_MODE_1 | GPIO interrupt mode for pins 32-63 |
| 0x168 | GPIO_INT_MODE_2 | GPIO interrupt mode for pins 64-95 |
| 0x16C | GPIO_INT_MODE_3 | GPIO interrupt mode for pins 96-127 |
| 0x170 | GPIO_INT_MASK_0 | GPIO interrupt mask for pins 0-31 |
| 0x174 | GPIO_INT_MASK_1 | GPIO interrupt mask for pins 32-63 |
| 0x178 | GPIO_INT_MASK_2 | GPIO interrupt mask for pins 64-95 |
| 0x17C | GPIO_INT_MASK_3 | GPIO interrupt mask for pins 96-127 |
| 0x180 | GPIO_INT_STAT_0 | GPIO interrupt status for pins 0-31 |
| 0x184 | GPIO_INT_STAT_1 | GPIO interrupt status for pins 32-63 |
| 0x188 | GPIO_INT_STAT_2 | GPIO interrupt status for pins 64-95 |
| 0x18C | GPIO_INT_STAT_3 | GPIO interrupt status for pins 96-127 |
| 0x190 | GPIO_INT_CLR_0 | GPIO interrupt clear for pins 0-31 |
| 0x194 | GPIO_INT_CLR_1 | GPIO interrupt clear for pins 32-63 |
| 0x198 | GPIO_INT_CLR_2 | GPIO interrupt clear for pins 64-95 |
| 0x19C | GPIO_INT_CLR_3 | GPIO interrupt clear for pins 96-127 |
| 0x1A0 | GPIO_INT_ENABLE_0 | GPIO interrupt enable for pins 0-31 |
| 0x1A4 | GPIO_INT_ENABLE_1 | GPIO interrupt enable for pins 32-63 |
| 0x1A8 | GPIO_INT_ENABLE_2 | GPIO interrupt enable for pins 64-95 |
| 0x1AC | GPIO_INT_ENABLE_3 | GPIO interrupt enable for pins 96-127 |
| 0x1B0 | GPIO_INT_STATUS | GPIO interrupt common status |
| 0x200+N*4 | GPIO_PIN0-31_CFG | Pin N configuration (FUNC_SEL, DRV, PU, PD, IE, SMT) |

### Key Register Fields

**Pin Configuration Register (offset 0x200 + N*4, for pins 0-31; extended pins use different base offsets)**

| Bits | Field | Description |
|------|-------|-------------|
| [5:0] | FUNC_SEL | Pin function select (0=GPIO, 1-15=alternate functions) |
| [7:6] | Reserved | Reserved |
| [10:8] | DRV | Drive strength (0=5mA, 1=10mA, 2=15mA, 3=20mA, 4=25mA, 5=30mA, 6=35mA, 7=40mA) |
| 11 | Reserved | Reserved |
| 12 | PU | Pull-up enable |
| 13 | PD | Pull-down enable |
| 14 | IE | Input enable |
| 15 | SMT | Schmitt trigger enable |

**GPIO Output Data Register (offset 0x100 + (pin/32)*4)**

| Bits | Field | Description |
|------|-------|-------------|
| [31:0] | GPIO_OUT | Output data for pins in this 32-bit group |

**GPIO Input Data Register (offset 0x104 + (pin/32)*4)**

| Bits | Field | Description |
|------|-------|-------------|
| [31:0] | GPIO_IN | Input data for pins in this 32-bit group |

**GPIO Interrupt Mode Register (offset 0x160 + (pin/32)*4)**

| Bits | Field | Description |
|------|-------|-------------|
| [1:0] | INT_MODE | Interrupt mode per pin (0=none, 1=pos edge, 2=neg edge, 3=both edges) |

**GPIO Interrupt Enable Register (offset 0x1A0 + (pin/32)*4)**

| Bits | Field | Description |
|------|-------|-------------|
| [31:0] | INT_EN | Interrupt enable per pin (1=enable) |

**GPIO Interrupt Clear Register (offset 0x190 + (pin/32)*4)**

| Bits | Field | Description |
|------|-------|-------------|
| [31:0] | INT_CLR | Write 1 to clear interrupt flag |

### Register-Level Code Example

```c
#include <stdint.h>

/* Register definitions */
#define GLB_BASE         0x40000000UL
#define GLB_GPIO_OUT0    (GLB_BASE + 0x100)
#define GLB_GPIO_IN0     (GLB_BASE + 0x130)
#define GLB_PIN0_CFG     (GLB_BASE + 0x200)  /* Pin 0 config register */
#define GLB_PIN1_CFG     (GLB_BASE + 0x204)  /* Pin 1 config register */

#define GLB_GPIO_INT_MODE0 (GLB_BASE + 0x160)
#define GLB_GPIO_INT_EN0   (GLB_BASE + 0x1A0)
#define GLB_GPIO_INT_CLR0  (GLB_BASE + 0x190)
#define GLB_GPIO_INT_STAT0 (GLB_BASE + 0x180)

/* Helper macros */
#define PIN_CFG_REG(pin)  (GLB_BASE + 0x200 + (pin) * 4)
#define GPIO_OUT_REG(pin) (GLB_BASE + 0x100 + (((pin) / 32) * 4))
#define GPIO_IN_REG(pin)  (GLB_BASE + 0x130 + (((pin) / 32) * 4))

/* Set pin function and mode directly via registers */
static void gpio_config_pin(uint8_t pin, uint8_t func, uint8_t drv,
                            uint8_t pull_up, uint8_t pull_down,
                            uint8_t input_en, uint8_t smt_en)
{
    volatile uint32_t *cfg = (volatile uint32_t *)PIN_CFG_REG(pin);
    uint32_t val = 0;
    val |= (func & 0x3F);        /* FUNC_SEL: bits[5:0] */
    val |= ((drv & 0x7) << 8);   /* DRV: bits[10:8] */
    val |= ((pull_up & 0x1) << 12);   /* PU: bit 12 */
    val |= ((pull_down & 0x1) << 13);  /* PD: bit 13 */
    val |= ((input_en & 0x1) << 14);   /* IE: bit 14 */
    val |= ((smt_en & 0x1) << 15);     /* SMT: bit 15 */
    *cfg = val;
}

/* Set GPIO output high or low */
static void gpio_output_set(uint8_t pin, uint8_t value)
{
    volatile uint32_t *out_reg = (volatile uint32_t *)GPIO_OUT_REG(pin);
    uint8_t bit = pin % 32;
    if (value) {
        *out_reg |= (1UL << bit);
    } else {
        *out_reg &= ~(1UL << bit);
    }
}

/* Read GPIO input level */
static uint8_t gpio_input_get(uint8_t pin)
{
    volatile uint32_t *in_reg = (volatile uint32_t *)GPIO_IN_REG(pin);
    uint8_t bit = pin % 32;
    return (*in_reg >> bit) & 0x1;
}

/* Configure GPIO interrupt for a pin */
static void gpio_irq_config(uint8_t pin, uint8_t mode, uint8_t enable)
{
    volatile uint32_t *mode_reg = (volatile uint32_t *)(GLB_BASE + 0x160 + ((pin / 32) * 4));
    volatile uint32_t *en_reg   = (volatile uint32_t *)(GLB_BASE + 0x1A0 + ((pin / 32) * 4));
    uint8_t bit = pin % 32;

    /* Set interrupt mode (2 bits per pin) */
    uint32_t mask = 0x3UL << (bit * 2);
    uint32_t shift = bit * 2;
    *mode_reg = (*mode_reg & ~mask) | ((mode & 0x3) << shift);

    /* Enable/disable interrupt */
    if (enable) {
        *en_reg |= (1UL << bit);
    } else {
        *en_reg &= ~(1UL << bit);
    }
}

/* Clear GPIO interrupt flag */
static void gpio_irq_clear(uint8_t pin)
{
    volatile uint32_t *clr_reg = (volatile uint32_t *)(GLB_BASE + 0x190 + ((pin / 32) * 4));
    uint8_t bit = pin % 32;
    *clr_reg = (1UL << bit);
}

/* Get GPIO interrupt status */
static uint32_t gpio_irq_status(void)
{
    volatile uint32_t *stat_reg = (volatile uint32_t *)(GLB_BASE + 0x180);
    return *stat_reg;
}

/* Example: Initialize GPIO 0 as push-pull output */
static void example_gpio_init_output(void)
{
    /* Configure pin 0: GPIO function (0), medium drive (2), no pull, output enabled */
    gpio_config_pin(0, 0, 2, 0, 0, 0, 0);

    /* Set output high */
    gpio_output_set(0, 1);
}

/* Example: Initialize GPIO 1 as input with pull-up and interrupt */
static void example_gpio_init_input(void)
{
    /* Configure pin 1: GPIO function (0), no drive, pull-up, input enabled */
    gpio_config_pin(1, 0, 0, 1, 0, 1, 1);

    /* Configure falling edge interrupt (mode=2) and enable it */
    gpio_irq_config(1, 2, 1);
}

/* Example: ISR handler for GPIO interrupts */
static void example_gpio_isr(void)
{
    uint32_t status = gpio_irq_status();
    uint8_t pin;

    for (pin = 0; pin < 32; pin++) {
        if (status & (1UL << pin)) {
            /* Handle interrupt for pin */
            /* ... */

            /* Clear interrupt flag */
            gpio_irq_clear(pin);
        }
    }
}
```
