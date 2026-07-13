# GPIO API Reference (BL616/BL618)

> **Source:** `bouffalo_sdk/drivers/lhal/include/bflb_gpio.h`  
> **Register Header:** `bouffalo_sdk/drivers/soc/bl616/std/include/hardware/glb_reg.h`  
> **Chip-Specific Header:** `bouffalo_sdk/drivers/soc/bl616/std/include/bl616_glb_gpio.h`

## Overview

The BL616/BL618 GPIO controller provides general-purpose input/output functionality with per-pin configuration registers. Each GPIO pin has its own dedicated 32-bit configuration register, unlike the shared per-2-pin layout used in BL602.

## Base Address

| Peripheral | Base Address |
|------------|-------------|
| GLB (GPIO Controller) | `0x20000000` |

GPIO pin `N` config register address: `GLB_BASE + 0x8C4 + (N × 4)`

---

## Pin Definitions

### BL616 Available Pins

| Pin Group | Pins Available |
|-----------|---------------|
| Low pins | GPIO0, GPIO1, GPIO2, GPIO3 |
| High pins | GPIO10–GPIO17, GPIO20–GPIO22, GPIO27–GPIO30 |

### BL618 Available Pins

All GPIO0 through GPIO34 are available.

### Pin Number Macros

```c
#define GPIO_PIN_0      0
#define GPIO_PIN_1      1
#define GPIO_PIN_2      2
#define GPIO_PIN_3      3
// ... through GPIO_PIN_34 (BL616/BL618)
```

---

## GPIO Configuration Masks

These masks are used with `bflb_gpio_init()` to configure pin behavior:

### Pin Mode (Bits 5-8)

| Mask | Description |
|------|-------------|
| `GPIO_INPUT` | Input Enable |
| `GPIO_OUTPUT` | Output Enable |
| `GPIO_ANALOG` | Analog Enable |
| `GPIO_ALTERNATE` | Alternate Function Enable |

### Pull-Up/Down (Bits 9-10)

| Mask | Description |
|------|-------------|
| `GPIO_FLOAT` | No pull-up, no pull-down |
| `GPIO_PULLUP` | Pull-up enabled |
| `GPIO_PULLDOWN` | Pull-down enabled |

### Drive Strength (Bits 12-13)

| Mask | Description |
|------|-------------|
| `GPIO_DRV_0` | Driver strength level 0 |
| `GPIO_DRV_1` | Driver strength level 1 |
| `GPIO_DRV_2` | Driver strength level 2 |
| `GPIO_DRV_3` | Driver strength level 3 |

### SMT (Bits 11)

| Mask | Description |
|------|-------------|
| `GPIO_SMT_DIS` | SMT (Schmitt Trigger) disabled |
| `GPIO_SMT_EN` | SMT enabled |

### Function Select (Bits 0-4)

For BL616/BL618, the following GPIO functions are available:

| Macro | Value | Description |
|-------|-------|-------------|
| `GPIO_FUNC_SDH` | 0 | SDH peripheral |
| `GPIO_FUNC_SPI0` | 1 | SPI0 peripheral |
| `GPIO_FUNC_I2S` | 3 | I2S peripheral |
| `GPIO_FUNC_PDM` | 4 | PDM peripheral |
| `GPIO_FUNC_I2C0` | 5 | I2C0 peripheral |
| `GPIO_FUNC_I2C1` | 6 | I2C1 peripheral |
| `GPIO_FUNC_EMAC` | 8 | Ethernet MAC |
| `GPIO_FUNC_CAM` | 9 | Camera interface |
| `GPIO_FUNC_GPIO` | 11 | General GPIO |
| `GPIO_FUNC_SDU` | 12 | SDU peripheral |
| `GPIO_FUNC_PWM0` | 16 | PWM0 peripheral |
| `GPIO_FUNC_DBI_B` | 22 | DBI type B |
| `GPIO_FUNC_DBI_C` | 23 | DBI type C |
| `GPIO_FUNC_DBI_QSPI` | 24 | DBI QSPI |
| `GPIO_FUNC_AUDAC_PWM` | 25 | Audio DAC PWM |
| `GPIO_FUNC_JTAG` | 26 | JTAG interface |
| `GPIO_FUNC_CLKOUT` | 31 | Clock output |

### Interrupt Trigger Modes

| Mode | Value | Description |
|------|-------|-------------|
| `GPIO_INT_TRIG_MODE_SYNC_FALLING_EDGE` | 0 | Synchronous falling edge |
| `GPIO_INT_TRIG_MODE_SYNC_RISING_EDGE` | 1 | Synchronous rising edge |
| `GPIO_INT_TRIG_MODE_SYNC_LOW_LEVEL` | 2 | Synchronous low level |
| `GPIO_INT_TRIG_MODE_SYNC_HIGH_LEVEL` | 3 | Synchronous high level |
| `GPIO_INT_TRIG_MODE_SYNC_FALLING_RISING_EDGE` | 4 | Synchronous both edges |
| `GPIO_INT_TRIG_MODE_ASYNC_FALLING_EDGE` | 8 | Asynchronous falling edge |
| `GPIO_INT_TRIG_MODE_ASYNC_RISING_EDGE` | 9 | Asynchronous rising edge |
| `GPIO_INT_TRIG_MODE_ASYNC_LOW_LEVEL` | 10 | Asynchronous low level |
| `GPIO_INT_TRIG_MODE_ASYNC_HIGH_LEVEL` | 11 | Asynchronous high level |

---

## LHAL API Functions

### bflb_gpio_init

Initialize a GPIO pin with the specified configuration.

```c
void bflb_gpio_init(struct bflb_device_s *dev, uint8_t pin, uint32_t cfgset);
```

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `dev` | `struct bflb_device_s *` | Device handle |
| `pin` | `uint8_t` | GPIO pin number (use `GPIO_PIN_N`) |
| `cfgset` | `uint32_t` | Configuration mask (OR'd GPIO_* masks) |

**Example:**
```c
// Configure GPIO0 as output with pull-up
bflb_gpio_init(gpio_dev, GPIO_PIN_0, GPIO_FUNC_GPIO | GPIO_OUTPUT | GPIO_PULLUP);
```

---

### bflb_gpio_deinit

Deinitialize a GPIO pin (sets to input floating).

```c
void bflb_gpio_deinit(struct bflb_device_s *dev, uint8_t pin);
```

---

### bflb_gpio_set

Set a GPIO pin to high level.

```c
void bflb_gpio_set(struct bflb_device_s *dev, uint8_t pin);
```

---

### bflb_gpio_reset

Reset a GPIO pin to low level.

```c
void bflb_gpio_reset(struct bflb_device_s *dev, uint8_t pin);
```

---

### bflb_gpio_read

Read the current logic level of a GPIO pin.

```c
bool bflb_gpio_read(struct bflb_device_s *dev, uint8_t pin);
```

**Returns:** `true` = high level, `false` = low level

---

### bflb_gpio_pin0_31_output

Write output value for GPIO pins 0-31 simultaneously.

```c
void bflb_gpio_pin0_31_output(struct bflb_device_s *dev, uint32_t value);
```

---

### bflb_gpio_pin0_31_set

Set multiple GPIO pins 0-31 using a bitmap.

```c
void bflb_gpio_pin0_31_set(struct bflb_device_s *dev, uint32_t value);
```

---

### bflb_gpio_pin0_31_reset

Reset multiple GPIO pins 0-31 using a bitmap.

```c
void bflb_gpio_pin0_31_reset(struct bflb_device_s *dev, uint32_t value);
```

---

### bflb_gpio_pin0_31_read

Read all GPIO pins 0-31 at once.

```c
uint32_t bflb_gpio_pin0_31_read(struct bflb_device_s *dev);
```

---

### bflb_gpio_int_init

Configure GPIO pin interrupt.

```c
void bflb_gpio_int_init(struct bflb_device_s *dev, uint8_t pin, uint8_t trig_mode);
```

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `dev` | `struct bflb_device_s *` | Device handle |
| `pin` | `uint8_t` | GPIO pin number |
| `trig_mode` | `uint8_t` | Interrupt trigger mode |

---

### bflb_gpio_int_mask

Enable or disable interrupt for a specific pin.

```c
void bflb_gpio_int_mask(struct bflb_device_s *dev, uint8_t pin, bool mask);
```

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `dev` | `struct bflb_device_s *` | Device handle |
| `pin` | `uint8_t` | GPIO pin number |
| `mask` | `bool` | `true` = disable interrupt, `false` = enable |

---

### bflb_gpio_get_intstatus

Get interrupt status for a specific pin.

```c
bool bflb_gpio_get_intstatus(struct bflb_device_s *dev, uint8_t pin);
```

**Returns:** `true` if interrupt is pending

---

### bflb_gpio_int_clear

Clear interrupt status for a specific pin.

```c
void bflb_gpio_int_clear(struct bflb_device_s *dev, uint8_t pin);
```

---

### bflb_gpio_uart_init

Configure a GPIO pin for UART functionality.

```c
void bflb_gpio_uart_init(struct bflb_device_s *dev, uint8_t pin, uint8_t uart_func);
```

**UART Function Values:**

| Value | Function |
|-------|----------|
| `GPIO_UART_FUNC_UART0_RTS` | 0 |
| `GPIO_UART_FUNC_UART0_CTS` | 1 |
| `GPIO_UART_FUNC_UART0_TX` | 2 |
| `GPIO_UART_FUNC_UART0_RX` | 3 |
| `GPIO_UART_FUNC_UART1_RTS` | 4 |
| `GPIO_UART_FUNC_UART1_CTS` | 5 |
| `GPIO_UART_FUNC_UART1_TX` | 6 |
| `GPIO_UART_FUNC_UART1_RX` | 7 |

---

### bflb_gpio_feature_control

Control GPIO special features.

```c
int bflb_gpio_feature_control(struct bflb_device_s *dev, int cmd, size_t arg);
```

**Commands:**

| Command | Description |
|---------|-------------|
| `GPIO_CMD_GET_GPIO_FUN` | Get current pin function |

---

### bflb_gpio_irq_attach / bflb_gpio_irq_detach

Attach/detach interrupt callback for a GPIO pin.

```c
void bflb_gpio_irq_attach(uint8_t pin, void (*callback)(uint8_t pin));
void bflb_gpio_irq_detach(uint8_t pin);
```

---

## Usage Examples

### Example 1: Basic Output (LED Blink)

```c
#include "bflb_gpio.h"

void led_blink_example(void)
{
    struct bflb_device_s *gpio;

    // Get GPIO device handle
    gpio = bflb_device_get_by_name("gpio");
    
    // Configure GPIO10 as output
    uint32_t cfg = GPIO_FUNC_GPIO | GPIO_OUTPUT | GPIO_PULLUP | GPIO_SMT_EN | GPIO_DRV_1;
    bflb_gpio_init(gpio, GPIO_PIN_10, cfg);
    
    // Blink LED
    while (1) {
        bflb_gpio_set(gpio, GPIO_PIN_10);  // LED on
        bflb_mtimer_delay_ms(500);
        bflb_gpio_reset(gpio, GPIO_PIN_10); // LED off
        bflb_mtimer_delay_ms(500);
    }
}
```

### Example 2: Input with Interrupt

```c
#include "bflb_gpio.h"

void gpio_interrupt_example(void)
{
    struct bflb_device_s *gpio;
    
    gpio = bflb_device_get_by_name("gpio");
    
    // Configure GPIO20 as input with interrupt
    uint32_t cfg = GPIO_FUNC_GPIO | GPIO_INPUT | GPIO_PULLUP;
    bflb_gpio_init(gpio, GPIO_PIN_20, cfg);
    
    // Setup interrupt on falling edge
    bflb_gpio_int_init(gpio, GPIO_PIN_20, GPIO_INT_TRIG_MODE_SYNC_FALLING_EDGE);
    
    // Attach callback
    bflb_gpio_irq_attach(GPIO_PIN_20, my_button_callback);
}

void my_button_callback(uint8_t pin)
{
    if (pin == GPIO_PIN_20) {
        // Handle button press
    }
}
```

### Example 3: Bitwise GPIO Operations

```c
void gpio_bitwise_example(void)
{
    struct bflb_device_s *gpio;
    gpio = bflb_device_get_by_name("gpio");
    
    // Configure multiple pins as output
    bflb_gpio_init(gpio, GPIO_PIN_0, GPIO_FUNC_GPIO | GPIO_OUTPUT);
    bflb_gpio_init(gpio, GPIO_PIN_1, GPIO_FUNC_GPIO | GPIO_OUTPUT);
    bflb_gpio_init(gpio, GPIO_PIN_2, GPIO_FUNC_GPIO | GPIO_OUTPUT);
    bflb_gpio_init(gpio, GPIO_PIN_3, GPIO_FUNC_GPIO | GPIO_OUTPUT);
    
    // Set all pins high at once (binary 1111 = 0x0F)
    bflb_gpio_pin0_31_set(gpio, 0x0F);
    
    bflb_mtimer_delay_ms(100);
    
    // Clear all pins at once
    bflb_gpio_pin0_31_reset(gpio, 0x0F);
    
    // Read all pins
    uint32_t state = bflb_gpio_pin0_31_read(gpio);
}
```

---

## Register-Level Reference

> **Important:** BL616/BL618 use **per-pin** GPIO configuration registers, NOT the shared per-2-pin layout of BL602.

### GPIO Configuration Registers

Each GPIO pin has its own 32-bit configuration register at:

```
GLB_BASE + 0x8C4 + (pin_number × 4)
```

**Register Layout (same for all pins, example shows GPIO_0):**

| Bits | Field | Description |
|------|-------|-------------|
| 0 | `REG_GPIO_N_IE` | Input enable |
| 1 | `REG_GPIO_N_SMT` | Schmitt trigger enable |
| 2-3 | `REG_GPIO_N_DRV` | Drive strength (0-3) |
| 4 | `REG_GPIO_N_PU` | Pull-up enable |
| 5 | `REG_GPIO_N_PD` | Pull-down enable |
| 6 | `REG_GPIO_N_OE` | Output enable |
| 8-12 | `REG_GPIO_N_FUNC_SEL` | Function select (5 bits) |
| 16-19 | `REG_GPIO_N_INT_MODE_SET` | Interrupt mode |
| 20 | `REG_GPIO_N_INT_CLR` | Interrupt clear |
| 21 | `GPIO_N_INT_STAT` | Interrupt status |
| 22 | `REG_GPIO_N_INT_MASK` | Interrupt mask |
| 24 | `REG_GPIO_N_O` | Output value |
| 25 | `REG_GPIO_N_SET` | Set output (write 1 to set) |
| 26 | `REG_GPIO_N_CLR` | Clear output (write 1 to clear) |
| 28 | `REG_GPIO_N_I` | Input value (read) |
| 30-31 | `REG_GPIO_N_MODE` | Pin mode |

### GPIO Register Offsets (BL616/BL618)

| Pin(s) | Register Offset | Address |
|--------|----------------|---------|
| GPIO_0 | `0x8C4` | `0x200008C4` |
| GPIO_1 | `0x8C8` | `0x200008C8` |
| GPIO_2 | `0x8CC` | `0x200008CC` |
| GPIO_3 | `0x8D0` | `0x200008D0` |
| GPIO_10 | `0x8F0` | `0x200008F0` |
| GPIO_11 | `0x8F4` | `0x200008F4` |
| ... | ... | ... |
| GPIO_30 | `0x9E4` | `0x200009E4` |
| GPIO_31 | `0x9E8` | `0x200009E8` |

### Direct Register Access Example

```c
#include "bflb_gpio.h"
#include "hardware/glb_reg.h"

void set_gpio_direct(uint8_t pin, uint8_t value)
{
    uint32_t reg_addr = GLB_BASE + 0x8C4 + (pin * 4);
    
    if (value) {
        // Set high - write to O bit
        *(uint32_t *)reg_addr |= (1 << 24);
    } else {
        // Set low - use CLR bit
        *(uint32_t *)(reg_addr + 0x100) |= (1 << 26);  // CLR is at offset +4 from SET
    }
}

void read_gpio_direct(uint8_t pin)
{
    uint32_t reg_addr = GLB_BASE + 0x8C4 + (pin * 4);
    uint32_t input_value = (*(uint32_t *)reg_addr >> 28) & 0x01;
    // Read input level from bit 28
}
```

### Key Differences from BL602

| Feature | BL602 | BL616/BL618 |
|---------|-------|-------------|
| Config register spacing | Per 2 pins shared | Per pin dedicated |
| Config register offset | `0x3C + (pin/2)*4` | `0x8C4 + pin*4` |
| Available pins | GPIO0-5, 7, 8, 11, 12, 14, 16, 17, 20, 21, 22 | GPIO0-3, 10-17, 20-22, 27-30 (BL616), GPIO0-34 (BL618) |
| Interrupt modes | 8 modes | 9 modes including `SYNC_FALLING_RISING_EDGE` |

---

## GLB GPIO Driver (Low-Level)

For chip-specific GPIO operations, use the GLB GPIO driver from `bl616_glb_gpio.h`:

### Key Functions

```c
BL_Err_Type GLB_GPIO_Init(GLB_GPIO_Cfg_Type *cfg);
BL_Err_Type GLB_GPIO_Func_Init(uint8_t gpioFun, uint8_t *pinList, uint8_t cnt);
BL_Err_Type GLB_GPIO_Input_Enable(uint8_t gpioPin);
BL_Err_Type GLB_GPIO_Output_Enable(uint8_t gpioPin);
BL_Err_Type GLB_GPIO_Set_HZ(uint8_t gpioPin);
uint32_t GLB_GPIO_Read(uint8_t gpioPin);
BL_Err_Type GLB_GPIO_Write(uint8_t gpioPin, uint32_t val);
BL_Err_Type GLB_GPIO_Set(uint8_t gpioPin);
BL_Err_Type GLB_GPIO_Clr(uint8_t gpioPin);
BL_Err_Type GLB_GPIO_Int_Init(GLB_GPIO_INT_Cfg_Type *intCfg);
```

### Configuration Structure

```c
typedef struct {
    uint8_t gpioPin;    // Pin number
    uint8_t gpioFun;    // Function (GPIO_FUN_*)
    uint8_t gpioMode;   // Mode (GPIO_MODE_*)
    uint8_t pullType;   // Pull type
    uint8_t drive;      // Drive strength
    uint8_t smtCtrl;    // Schmitt trigger
    uint8_t outputMode; // Output mode
} GLB_GPIO_Cfg_Type;
```
