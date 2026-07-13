# WO Waveform Output API Reference (BL616/BL618)

## Overview

**WO (Waveform Output)** is the waveform output peripheral of the BL616/BL618 chip, generating precise dual-level waveform signals via GPIO. It is widely used for driving single-wire protocol LEDs such as WS2812, UART bit-banging, signal modulation, and other scenarios.

WO is actually embedded inside the **GLB (Global Controller)** peripheral and operates by configuring GPIO special function modes. Core principle: configure the time ratio of two levels (code0/code1), push 16-bit data via FIFO, where each bit determines whether a code0 or code1 waveform is output.

**Typical Applications**:
- WS2812 / NeoPixel RGB LED driver
- Single-wire protocol device communication
- UART passthrough (WO UART mode)
- Arbitrary dual-level signal output

**Base Address**: WO registers are located in the GLB address space. Obtain the device handle via `bflb_device_get_by_name("wo")`.

---

## Header Files

```c
#include "bflb_wo.h"           // LHAL API
#include "hardware/wo_reg.h"    // Register definitions
```

---

## Mode Definitions

### WO_MODE — Operating Mode

```c
#define WO_MODE_WRITE   0  // WO direct write
#define WO_MODE_SET_CLR 1  // WO set/clr
```

### WO_INT — Interrupt Types

```c
#define WO_INT_END  (1 << 0)  // WO transfer end interrupt (TX FIFO empty)
#define WO_INT_FIFO (1 << 1)  // WO FIFO ready interrupt (data can be written)
#define WO_INT_FER  (1 << 2)  // WO FIFO error interrupt (overflow/underflow)
```

---

## Configuration Structure

### bflb_wo_cfg_s

```c
struct bflb_wo_cfg_s {
    uint16_t code_total_cnt;     // Total count per cycle, should be < 512
    uint8_t  code0_first_cnt;   // code0 high-level count, should be < 256
    uint8_t  code1_first_cnt;   // code1 high-level count, should be < 256
    uint8_t  code0_first_level; // code0 starting level (0=low, 1=high)
    uint8_t  code1_first_level; // code1 starting level (0=low, 1=high)
    uint8_t  idle_level;        // Idle GPIO level (0=low, 1=high)
    uint8_t  fifo_threshold;    // FIFO threshold, should be < 128
    uint8_t  mode;              // Operating mode, use WO_MODE
};
```

---

## Register Map (GLB GPIO Configuration Area)

WO is actually implemented via GPIO configuration registers within the GLB peripheral:

| Register | Address Offset | Description |
|----------|---------------|-------------|
| `GLB_GPIO_CFG0 + pin×4` | `0x8C4 + pin×4` | Per-GPIO pin configuration (including WO function selection) |
| `GLB_GPIO_CFG142` | `0xAFC` | WO core control: waveform timing, FIFO, DMA |
| `GLB_GPIO_CFG143` | `0xB00` | WO DMA enable, FIFO status, interrupts |
| `GLB_GPIO_CFG144` | `0xB04` | WO transmit data port |

### GLB_GPIO_CFG142 Key Bit Fields

```c
// 0xAFC : GLB_GPIO_CFG142
#define GLB_CR_INVERT_CODE0_HIGH   (1 << 1)   // code0 level invert
#define GLB_CR_INVERT_CODE1_HIGH   (1 << 2)   // code1 level invert
#define GLB_CR_CODE_TOTAL_TIME_SHIFT (7)       // Cycle total count (9 bits)
#define GLB_CR_CODE_TOTAL_TIME_MASK  (0x1FF << 7)
#define GLB_CR_CODE0_HIGH_TIME_SHIFT (16)      // code0 high-level count (8 bits)
#define GLB_CR_CODE0_HIGH_TIME_MASK (0xFF << 16)
#define GLB_CR_CODE1_HIGH_TIME_SHIFT (24)      // code1 high-level count (8 bits)
#define GLB_CR_CODE1_HIGH_TIME_MASK (0xFF << 24)
#define GLB_CR_GPIO_TX_EN           (1 << 0)   // WO output enable
```

### GLB_GPIO_CFG143 Key Bit Fields

```c
// 0xB00 : GLB_GPIO_CFG143
#define GLB_CR_GPIO_DMA_TX_EN       (1 << 0)   // WO DMA transmit enable
#define GLB_GPIO_TX_FIFO_CLR       (1 << 2)   // FIFO clear
#define GLB_GPIO_TX_END_CLR        (1 << 3)   // Transfer end flag clear
#define GLB_GPIO_TX_FIFO_OVERFLOW   (1 << 4)   // FIFO overflow flag (read-only)
#define GLB_GPIO_TX_FIFO_UNDERFLOW  (1 << 5)   // FIFO underflow flag (read-only)
#define GLB_CR_GPIO_TX_FIFO_TH_SHIFT (16)      // FIFO threshold (7 bits)
#define GLB_CR_GPIO_TX_END_MASK    (1 << 23)   // End interrupt mask
#define GLB_CR_GPIO_TX_FIFO_MASK   (1 << 24)   // FIFO interrupt mask
#define GLB_CR_GPIO_TX_FER_MASK    (1 << 25)   // FIFO error interrupt mask
#define GLB_R_GPIO_TX_END_INT      (1 << 26)   // End interrupt flag (read-only)
#define GLB_R_GPIO_TX_FIFO_INT     (1 << 27)   // FIFO interrupt flag (read-only)
#define GLB_R_GPIO_TX_FER_INT      (1 << 28)   // FIFO error interrupt flag (read-only)
#define GLB_CR_GPIO_TX_END_EN      (1 << 29)   // End interrupt enable
#define GLB_CR_GPIO_TX_FIFO_EN     (1 << 30)   // FIFO interrupt enable
#define GLB_CR_GPIO_TX_FER_EN      (1 << 31)   // FIFO error interrupt enable
```

---

## API Functions

### bflb_wo_pin_init — Initialize WO Pin

```c
void bflb_wo_pin_init(struct bflb_device_s *dev, uint8_t pin, uint8_t mode);
```

Configure a specified GPIO pin in WO mode and assign it to the WO peripheral.

**Parameters**:
- `pin` — GPIO pin number (e.g., `10`)
- `mode` — `WO_MODE_WRITE` or `WO_MODE_SET_CLR`

**Implementation details**: Sets the GPIO `FUNC_SEL` to `0xB`, `MODE` to `2` (WRITE) or `3` (SET_CLR).

---

### bflb_wo_init — Initialize WO Peripheral

```c
void bflb_wo_init(struct bflb_device_s *dev, struct bflb_wo_cfg_s *cfg);
```

Initialize WO core functionality (waveform timing, FIFO, polarity).

> ⚠️ For **BL616CL**, this API resets the clock divider to 1. To use a custom divider, call `bflb_wo_set_clk_div()`.

---

### bflb_wo_set_clk_div — Set Clock Divider (BL616CL only)

```c
void bflb_wo_set_clk_div(struct bflb_device_s *dev, uint16_t clk_div);
```

**Note**:
- Default divider value is 1
- `bflb_wo_init()` resets the divider to 1, **must be called after `bflb_wo_init()`**
- When the divider is not 1, the duty cycle of the first WO-generated waveform may be inaccurate

---

### bflb_wo_enable / bflb_wo_disable — Enable/Disable WO

```c
void bflb_wo_enable(struct bflb_device_s *dev);
void bflb_wo_disable(struct bflb_device_s *dev);
```

After enabling, the GPIO starts outputting WO waveforms. After disabling, the GPIO reverts to normal GPIO function.

---

### bflb_wo_get_fifo_available_cnt — Query FIFO Available Space

```c
uint32_t bflb_wo_get_fifo_available_cnt(struct bflb_device_s *dev);
```

**Returns**: The current number of 16-bit data words that can be written to the FIFO.

---

### bflb_wo_push_fifo — Push Data to FIFO

```c
uint32_t bflb_wo_push_fifo(struct bflb_device_s *dev, uint16_t *data, uint32_t len);
```

**Returns**: The number of data words successfully written (may be less than `len`, depending on FIFO remaining space).

---

### bflb_wo_push_fifo_force — Force Push Data

```c
void bflb_wo_push_fifo_force(struct bflb_device_s *dev, uint16_t *data, uint32_t len);
```

Force pushes data, **stops only when FIFO is full** (blocking).

---

### bflb_wo_clear_fifo — Clear FIFO

```c
void bflb_wo_clear_fifo(struct bflb_device_s *dev);
```

---

### bflb_wo_enable_dma / bflb_wo_disable_dma — DMA Enable

```c
void bflb_wo_enable_dma(struct bflb_device_s *dev);
void bflb_wo_disable_dma(struct bflb_device_s *dev);
```

WO supports DMA transfer. DMA source is `DMA_REQUEST_WO`.

---

### Interrupt Related

```c
uint32_t bflb_wo_get_int_status(struct bflb_device_s *dev);  // Get interrupt status
void bflb_wo_int_mask(struct bflb_device_s *dev, uint32_t int_type);      // Mask interrupt
void bflb_wo_int_unmask(struct bflb_device_s *dev, uint32_t int_type);   // Unmask interrupt
void bflb_wo_int_clear(struct bflb_device_s *dev, uint32_t int_type);    // Clear interrupt flag
```

---

### WO UART Mode

WO has a built-in UART bit-banging mode, allowing UART transmission to be simulated on any GPIO:

```c
// Initialize WO UART
void bflb_wo_uart_init(struct bflb_device_s *dev, uint32_t baudrate, uint8_t pin);

// Send a single character
void bflb_wo_uart_putchar(struct bflb_device_s *dev, uint8_t ch);

// Send a data block (polling)
void bflb_wo_uart_put(struct bflb_device_s *dev, uint8_t *data, uint32_t len);
```

---

## Complete WS2812 Driver Example

WS2812 is a single-wire RGB LED where each bit is represented by one cycle:
- `0` = High 0.4μs + Low 0.85μs
- `1` = High 0.85μs + Low 0.4μs
- Each RGB pixel requires 24 bits (GRB order)

```c
#include "bflb_wo.h"
#include "bflb_dma.h"
#include "bflb_mtimer.h"

#define WS2812_PIN    10
#define WS2812_NUM    60
#define WS2812_BUFFER (WS2812_NUM * 24)

struct bflb_device_s *wo;
struct bflb_device_s *dma0_ch0;
static ATTR_NOCACHE_RAM_SECTION struct bflb_dma_channel_lli_pool_s llipool[1];
static ATTR_NOCACHE_RAM_SECTION struct bflb_dma_channel_lli_transfer_s transfers[1];
uint16_t buffer_data[WS2812_BUFFER] __attribute__((aligned(32)));

/* WS2812 timing config (XCLK=40MHz, cycle=1.25μs) */
struct bflb_wo_cfg_s wo_cfg = {
    .code_total_cnt = 50,   /* 40MHz / 50 = 800kHz */
    .code0_first_cnt = 16,  /* High 0.4μs = 1.25μs * 16/50 */
    .code1_first_cnt = 34,  /* High 0.85μs = 1.25μs * 34/50 */
    .code0_first_level = 1,
    .code1_first_level = 1,
    .idle_level = 0,
    .fifo_threshold = 64,
    .mode = WO_MODE_WRITE,
};

struct bflb_dma_channel_config_s dma_cfg = {
    .direction = DMA_MEMORY_TO_PERIPH,
    .src_req = DMA_REQUEST_NONE,
    .dst_req = DMA_REQUEST_WO,
    .src_addr_inc = DMA_ADDR_INCREMENT_ENABLE,
    .dst_addr_inc = DMA_ADDR_INCREMENT_DISABLE,
    .src_burst_count = DMA_BURST_INCR8,
    .dst_burst_count = DMA_BURST_INCR8,
    .src_width = DMA_DATA_WIDTH_16BIT,
    .dst_width = DMA_DATA_WIDTH_16BIT,
};

/* Convert RGB color to WS2812 data (GRB order) */
static void set_rgb_color(uint16_t index, uint8_t r, uint8_t g, uint8_t b)
{
    for (int i = 0; i < 8; i++) {
        buffer_data[index * 24 + i]     = (g & (0x80 >> i)) ? 34 : 16;  /* G */
        buffer_data[index * 24 + 8 + i] = (r & (0x80 >> i)) ? 34 : 16;  /* R */
        buffer_data[index * 24 + 16 + i]= (b & (0x80 >> i)) ? 34 : 16;  /* B */
    }
}

void app_main(void)
{
    /* Get device handles */
    wo = bflb_device_get_by_name("wo");
    dma0_ch0 = bflb_device_get_by_name("dma0_ch0");

    /* Initialize WO pin */
    bflb_wo_pin_init(wo, WS2812_PIN, WO_MODE_WRITE);

    /* Initialize WO */
    bflb_wo_init(wo, &wo_cfg);

    /* Configure DMA */
    bflb_dma_channel_init(dma0_ch0, DMA_CH0, &dma_cfg);
    bflb_dma_channel_lli_reinit(dma0_ch0, DMA_CH0, llipool, 1);

    /* Fill color data */
    for (int i = 0; i < WS2812_NUM; i++) {
        set_rgb_color(i, 255, 0, 0);  /* All red */
    }

    /* Prepare DMA transfer */
    transfers[0].src_addr = (uint32_t)buffer_data;
    transfers[0].dst_addr = (uint32_t)(dev->reg_base + 0xB04);  /* GLB_GPIO_CFG144 */
    transfers[0].next = (uint32_t)0;
    transfers[0].nbytes = sizeof(buffer_data);
    bflb_dma_channel_lli_add_node(dma0_ch0, DMA_CH0, transfers);

    /* Start DMA + WO */
    bflb_wo_enable_dma(wo);
    bflb_wo_enable(wo);
    bflb_dma_channel_start(dma0_ch0, DMA_CH0);

    /* Wait for transfer to complete */
    bflb_mtimer_delay_ms(2);  /* WS2812 requires >50μs low-level reset */
}
```

---

## WO UART Mode Example (GPIO-Simulated UART)

```c
#include "bflb_wo.h"

struct bflb_device_s *wo;

void app_main(void)
{
    wo = bflb_device_get_by_name("wo");

    /* Configure GPIO10 as WO UART, baud rate 115200 */
    bflb_wo_uart_init(wo, 115200, 10);

    /* Send string */
    bflb_wo_uart_put(wo, (uint8_t *)"Hello WO UART\r\n", 15);
}
```

---

## Register-Level Programming

Directly operating GLB registers to configure WO:

```c
#include "hardware/wo_reg.h"

#define GLB_BASE  0x20000000
#define GLB_GPIO_CFG142_OFFSET  0xAFC

/* Assume the pin has been configured for WO function via bflb_gpio_init */
uint32_t reg_base = GLB_BASE;

/* Configure waveform timing */
uint32_t regval = getreg32(reg_base + GLB_GPIO_CFG142_OFFSET);
regval &= ~GLB_CR_CODE_TOTAL_TIME_MASK;
regval &= ~GLB_CR_CODE0_HIGH_TIME_MASK;
regval &= ~GLB_CR_CODE1_HIGH_TIME_MASK;
regval |= (50 << GLB_CR_CODE_TOTAL_TIME_SHIFT);
regval |= (16 << GLB_CR_CODE0_HIGH_TIME_SHIFT);   /* code0 = 16/50 high */
regval |= (34 << GLB_CR_CODE1_HIGH_TIME_SHIFT);   /* code1 = 34/50 high */
putreg32(regval, reg_base + GLB_GPIO_CFG142_OFFSET);

/* Enable WO */
regval = getreg32(reg_base + GLB_GPIO_CFG142_OFFSET);
regval |= GLB_CR_GPIO_TX_EN;
putreg32(regval, reg_base + GLB_GPIO_CFG142_OFFSET);

/* Write data to FIFO (via GLB_GPIO_CFG144 = 0xB04) */
for (int i = 0; i < len; i++) {
    putreg32(data[i] & 0xFFFF, reg_base + 0xB04);
}
```

---

## SDK Example Paths

| Example | Description |
|---------|-------------|
| `examples/peripherals/wo/wo_ws2812/` | WS2812 RGB LED driver + DMA |
| `examples/peripherals/wo/wo_console/` | WO UART Console |
| `examples/peripherals/wo/wo_int/` | WO interrupt example |
| `examples/peripherals/wo/wo_uart/` | WO UART mode |
| `examples/peripherals/wo/wo_dma/` | WO DMA transfer |

---

## Notes

1. **XCLK clock**: WO depends on the `XCLK` clock source. Ensure the clock is enabled before initialization.
2. **WS2812 timing**: Must strictly adhere to WS2812 specifications (800kHz ±15%). When XCLK=40MHz, `code_total_cnt=50` equals exactly 800kHz.
3. **DMA transfer**: DMA destination address is fixed at `GLB_BASE + 0xB04` (GLB_GPIO_CFG144).
4. **FIFO threshold**: `fifo_threshold` should be set to 64 or below; otherwise, FIFO error interrupts may be triggered.
5. **Multi-byte color**: WS2812 uses **GRB** order, not the common RGB.
6. **Reset time**: After sending data, at least **50μs of low level** is required to latch and move to the next LED.
