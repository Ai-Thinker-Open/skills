# DAC API Reference (BL616/BL618)

## Overview

The DAC (Digital-to-Analog Converter) peripheral on BL616/BL618 provides two analog output channels (A and B) with programmable output voltage based on a digital input value. The DAC can operate in standalone mode or be triggered by DMA for continuous waveform generation.

## Source File

- **Header**: `bouffalo_sdk/drivers/lhal/include/bflb_dac.h`
- **Implementation**: `bouffalo_sdk/drivers/lhal/src/bflb_dac.c`

## Base Address

The DAC is part of the GPIP block at `0x20002000`. The DAC TDR (Transmit Data Register) is located at offset `0x48` from GPIP_BASE.

| Register | Address |
|----------|---------|
| `GPIP_BASE + 0x48` (DAC_TDR) | DAC Channel A/B Data Register |

## DAC Channels

| Channel | Constant | Description |
|---------|----------|-------------|
| Channel A | `DAC_CHANNEL_A` | DAC Channel A (bit 0) |
| Channel B | `DAC_CHANNEL_B` | DAC Channel B (bit 1) |

## Clock Division

| Constant | Value | Description |
|----------|-------|-------------|
| `DAC_CLK_DIV_1` | 4 | No division (source is 512 kHz) |
| `DAC_CLK_DIV_16` | 0 | Divide by 16 |
| `DAC_CLK_DIV_32` | 1 | Divide by 32 |
| `DAC_CLK_DIV_64` | 3 | Divide by 64 |

**Note**: DAC source clock must be 512 kHz. Effective DAC clock = 512 kHz / clk_div.

## Voltage Reference

| Constant | Value | Description |
|----------|-------|-------------|
| `DAC_VREF_INTERNAL` | 0 | Internal reference (0.2V to 1.8V output range) |
| `DAC_VREF_EXTERNAL` | 1 | External reference (GPIO28, 0.1*VREF to 0.9*VREF) |

**Output Voltage Calculation (Internal Reference):**
```
Output Voltage (V) = (1.8V - 0.2V) * digital_val / 4096 + 0.2V
                   = 1.6V * digital_val / 4096 + 0.2V
```

**Output Voltage Calculation (External Reference):**
```
Output Voltage (V) = (0.9*VREF - 0.1*VREF) * digital_val / 4096 + 0.1*VREF
                   = 0.8*VREF * digital_val / 4096 + 0.1*VREF
```

**Note**: BL616/BL618 has 12-bit resolution (x = 4096), unlike BL602/BL702 which have 10-bit (x = 1024).

## DMA Format

| Constant | Description |
|----------|-------------|
| `DAC_DMA_FORMAT_0` | Sequential format: {A0}, {A1}, {A2}, ... |
| `DAC_DMA_FORMAT_1` | Interleaved format: {B0,A0}, {B1,A1}, {B2,A2}, ... |

## API Functions

### bflb_dac_init

Initialize the DAC with clock division.

```c
void bflb_dac_init(struct bflb_device_s *dev, uint8_t clk_div);
```

**Parameters:**
- `dev` - Device handle (e.g., `bflb_device_get_by_name("dac")`)
- `clk_div` - Clock divider, use @ref DAC_CLK_DIV

**Example:**
```c
/* Initialize DAC with 512kHz / 1 = 512kHz DAC clock */
bflb_dac_init(dac, DAC_CLK_DIV_1);

/* Initialize DAC with 512kHz / 64 = 8kHz DAC clock */
bflb_dac_init(dac, DAC_CLK_DIV_64);
```

---

### bflb_dac_deinit

Deinitialize the DAC.

```c
void bflb_dac_deinit(struct bflb_device_s *dev);
```

---

### bflb_dac_channel_enable

Enable a DAC channel.

```c
void bflb_dac_channel_enable(struct bflb_device_s *dev, uint8_t ch);
```

**Parameters:**
- `dev` - Device handle
- `ch` - Channel (`DAC_CHANNEL_A` and/or `DAC_CHANNEL_B`)

**Example:**
```c
/* Enable channel A only */
bflb_dac_channel_enable(dac, DAC_CHANNEL_A);

/* Enable both channels */
bflb_dac_channel_enable(dac, DAC_CHANNEL_A | DAC_CHANNEL_B);
```

---

### bflb_dac_channel_disable

Disable a DAC channel.

```c
void bflb_dac_channel_disable(struct bflb_device_s *dev, uint8_t ch);
```

---

### bflb_dac_set_value

Set the DAC output value for a channel.

```c
void bflb_dac_set_value(struct bflb_device_s *dev, uint8_t ch, uint16_t value);
```

**Parameters:**
- `dev` - Device handle
- `ch` - Channel (`DAC_CHANNEL_A` or `DAC_CHANNEL_B`)
- `value` - DAC value (0-4095 for 12-bit resolution)

**Example:**
```c
/* Set channel A to mid-scale (approximately 1.0V) */
bflb_dac_set_value(dac, DAC_CHANNEL_A, 2048);

/* Set channel B to quarter-scale (approximately 0.6V) */
bflb_dac_set_value(dac, DAC_CHANNEL_B, 1024);
```

---

### bflb_dac_link_txdma

Enable/disable DMA linking for DAC transmit.

```c
void bflb_dac_link_txdma(struct bflb_device_s *dev, bool enable);
```

**Parameters:**
- `dev` - Device handle
- `enable` - `true` to enable DMA, `false` to disable

---

### bflb_dac_set_dma_format

Set the DAC DMA format for interleaved transfers.

```c
void bflb_dac_set_dma_format(struct bflb_device_s *dev, uint8_t format);
```

**Parameters:**
- `dev` - Device handle
- `format` - `DAC_DMA_FORMAT_0` or `DAC_DMA_FORMAT_1`

---

## Usage Examples

### Basic DAC Output

```c
#include "bflb_dac.h"

void dac_basic_example(void)
{
    struct bflb_device_s *dac;

    /* Get DAC device handle */
    dac = bflb_device_get_by_name("dac");
    
    /* Initialize DAC with 512kHz source clock, divide by 1 */
    bflb_dac_init(dac, DAC_CLK_DIV_1);
    
    /* Enable channel A */
    bflb_dac_channel_enable(dac, DAC_CHANNEL_A);
    
    /* Set output to mid-scale (1.0V with internal reference) */
    bflb_dac_set_value(dac, DAC_CHANNEL_A, 2048);
    
    /* Channel A now outputs ~1.0V */
}
```

### Dual Channel DAC Output

```c
void dac_dual_channel_example(void)
{
    struct bflb_device_s *dac;

    dac = bflb_device_get_by_name("dac");
    bflb_dac_init(dac, DAC_CLK_DIV_1);
    
    /* Enable both channels */
    bflb_dac_channel_enable(dac, DAC_CHANNEL_A | DAC_CHANNEL_B);
    
    /* Channel A: 0.2V (minimum) */
    bflb_dac_set_value(dac, DAC_CHANNEL_A, 0);
    
    /* Channel B: 1.8V (maximum) */
    bflb_dac_set_value(dac, DAC_CHANNEL_B, 4095);
    
    /*
     * With internal reference:
     * - Channel A outputs 0.2V
     * - Channel B outputs 1.8V
     */
}
```

### DAC with DMA for Waveform Generation

```c
#include "bflb_dac.h"
#include "bflb_dma.h"

#define DAC_WAVEFORM_SAMPLES 256

static uint16_t sine_wave[DAC_WAVEFORM_SAMPLES];
static struct bflb_device_s *dac;
static struct bflb_device_s *dma_ch;

void dac_dma_waveform_example(void)
{
    /* Generate sine wave lookup table */
    for (int i = 0; i < DAC_WAVEFORM_SAMPLES; i++) {
        float angle = (2.0f * 3.14159f * i) / DAC_WAVEFORM_SAMPLES;
        /* Map sine [-1, 1] to DAC range [0, 4095] centered at 2048 */
        sine_wave[i] = (uint16_t)(2048 + 2047 * sinf(angle));
    }
    
    /* Initialize DAC */
    dac = bflb_device_get_by_name("dac");
    bflb_dac_init(dac, DAC_CLK_DIV_1);
    bflb_dac_channel_enable(dac, DAC_CHANNEL_A);
    
    /* Configure DMA for memory to DAC */
    struct bflb_dma_channel_config_s dma_config = {
        .direction = DMA_MEMORY_TO_PERIPH,
        .src_req = DMA_REQUEST_NONE,          /* Memory */
        .dst_req = DMA_REQUEST_DAC,            /* DAC peripheral */
        .src_addr_inc = DMA_ADDR_INCREMENT_ENABLE,
        .dst_addr_inc = DMA_ADDR_INCREMENT_DISABLE,
        .src_burst_count = DMA_BURST_INCR1,
        .dst_burst_count = DMA_BURST_INCR1,
        .src_width = DMA_DATA_WIDTH_16BIT,
        .dst_width = DMA_DATA_WIDTH_16BIT,
    };
    
    dma_ch = bflb_device_get_by_name("dma0_ch0");
    bflb_dma_channel_init(dma_ch, &dma_config);
    
    /* Set DMA format for sequential transfer */
    bflb_dac_set_dma_format(dac, DAC_DMA_FORMAT_0);
    
    /* Link DAC to DMA */
    bflb_dac_link_txdma(dac, true);
    
    /* Configure DMA transfer */
    struct bflb_dma_channel_lli_pool_s lli;
    struct bflb_dma_channel_lli_transfer_s transfer = {
        .src_addr = (uint32_t)sine_wave,
        .dst_addr = 0x20002048,  /* DAC_TDR address */
        .nbytes = sizeof(sine_wave),
    };
    
    bflb_dma_channel_lli_reload(dma_ch, &lli, 1, &transfer, 1);
    bflb_dma_channel_tcint_mask(dma_ch, false);
    
    /* Start DMA - DAC will output sine wave continuously */
    bflb_dma_channel_start(dma_ch);
}
```

### Triangle Wave Generator

```c
void dac_triangle_example(void)
{
    #define TRIANGLE_SAMPLES 128
    static uint16_t triangle[TRIANGLE_SAMPLES];
    
    /* Generate triangle wave */
    for (int i = 0; i < TRIANGLE_SAMPLES; i++) {
        if (i < TRIANGLE_SAMPLES / 2) {
            /* Rising edge: 0 to 4095 */
            triangle[i] = (i * 2 * 4095) / TRIANGLE_SAMPLES;
        } else {
            /* Falling edge: 4095 to 0 */
            int j = i - TRIANGLE_SAMPLES / 2;
            triangle[i] = 4095 - (j * 2 * 4095) / TRIANGLE_SAMPLES;
        }
    }
    
    struct bflb_device_s *dac = bflb_device_get_by_name("dac");
    bflb_dac_init(dac, DAC_CLK_DIV_1);
    bflb_dac_channel_enable(dac, DAC_CHANNEL_A);
    
    /* Setup DMA similar to sine wave example */
    /* ... DMA configuration code ... */
    
    bflb_dma_channel_start(dma_ch);
}
```

### Variable Voltage Control

```c
#include "bflb_dac.h"

void dac_voltage_control_example(void)
{
    struct bflb_device_s *dac;
    float target_voltage = 1.0f;  /* Target voltage in volts */
    uint16_t dac_value;
    
    dac = bflb_device_get_by_name("dac");
    bflb_dac_init(dac, DAC_CLK_DIV_1);
    bflb_dac_channel_enable(dac, DAC_CHANNEL_A);
    
    /* Convert voltage to DAC value
     * V_out = 1.6V * dac_value / 4096 + 0.2V
     * dac_value = (V_out - 0.2V) * 4096 / 1.6V
     */
    dac_value = (uint16_t)((target_voltage - 0.2f) * 4096.0f / 1.6f);
    
    /* Clamp to valid range */
    if (dac_value > 4095) dac_value = 4095;
    
    bflb_dac_set_value(dac, DAC_CHANNEL_A, dac_value);
    printf("Setting DAC to %u (%.2fV)\r\n", dac_value, target_voltage);
}
```

## Register-Level Overview

| Register | Offset | Description |
|----------|--------|-------------|
| `GPADC_CONFIG` | `0x00` | ADC/DAC configuration |
| `DAC_TDR` | `0x48` | DAC transmit data register |
| `DAC_FIFO` | `0x4C` | DAC FIFO control |

**DAC Output Formula:**
```
Channel A: Output voltage determined by DAC_TDR[11:0]
Channel B: Output voltage determined by DAC_TDR[27:16]
```

## Key Points

1. **12-bit Resolution**: BL616/BL618 DAC has 12-bit resolution (0-4095)
2. **Source Clock**: DAC requires 512 kHz source clock
3. **Output Range**: 0.2V to 1.8V (internal reference) or 0.1*VREF to 0.9*VREF (external)
4. **DMA Support**: DAC supports DMA for continuous waveform generation
5. **Dual Channels**: Two independent DAC channels (A and B)
6. **GPIO Pin**: On BL616/BL618, external reference uses GPIO28
