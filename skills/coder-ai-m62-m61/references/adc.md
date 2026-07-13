# ADC API Reference (BL616/BL618)

## Overview

The ADC (Analog-to-Digital Converter) peripheral on BL616/BL618 provides multi-channel analog input sampling with programmable resolution, conversion modes, and reference voltage selection. The ADC is part of the GPIP (General Purpose Input/Peripheral) block.

## Source File

- **Header**: `bouffalo_sdk/drivers/lhal/include/bflb_adc.h`
- **Implementation**: `bouffalo_sdk/drivers/lhal/src/bflb_adc.c` or `bflb_adc_v2.c` or `bflb_adc_v3.c`

## Base Address

| Peripheral | Base Address |
|------------|--------------|
| GPIP (ADC) | `0x20002000` |

## ADC Channels

| Channel | Constant | Description |
|---------|----------|-------------|
| 0 | `ADC_CHANNEL_0` | ADC Channel 0 |
| 1 | `ADC_CHANNEL_1` | ADC Channel 1 |
| 2 | `ADC_CHANNEL_2` | ADC Channel 2 |
| 3 | `ADC_CHANNEL_3` | ADC Channel 3 |
| 4 | `ADC_CHANNEL_4` | ADC Channel 4 |
| 5 | `ADC_CHANNEL_5` | ADC Channel 5 |
| 6 | `ADC_CHANNEL_6` | ADC Channel 6 |
| 7 | `ADC_CHANNEL_7` | ADC Channel 7 |
| 8 | `ADC_CHANNEL_8` | ADC Channel 8 |
| 9 | `ADC_CHANNEL_9` | ADC Channel 9 |
| 10 | `ADC_CHANNEL_10` | ADC Channel 10 |
| DAC A | `ADC_CHANNEL_DACA` | DAC Channel A output |
| DAC B | `ADC_CHANNEL_DACB` | DAC Channel B output |
| TSEN P | `ADC_CHANNEL_TSEN_P` | Temperature sensor positive |
| TSEN N | `ADC_CHANNEL_TSEN_N` | Temperature sensor negative |
| VREF | `ADC_CHANNEL_VREF` | Internal voltage reference |
| VABT Half | `ADC_CHANNEL_VABT_HALF` | VBAT/2 (battery monitor) |
| GND | `ADC_CHANNEL_GND` | Ground (for calibration) |

## Clock Division

| Constant | Value | Description |
|----------|-------|-------------|
| `ADC_CLK_DIV_4` | 1 | ADC clock = source / 4 |
| `ADC_CLK_DIV_8` | 2 | ADC clock = source / 8 |
| `ADC_CLK_DIV_12` | 3 | ADC clock = source / 12 |
| `ADC_CLK_DIV_16` | 4 | ADC clock = source / 16 |
| `ADC_CLK_DIV_20` | 5 | ADC clock = source / 20 |
| `ADC_CLK_DIV_24` | 6 | ADC clock = source / 24 |
| `ADC_CLK_DIV_32` | 7 | ADC clock = source / 32 |

**Note**: ADC clock must be less than 500 kHz for accurate conversion.

## Resolution

| Constant | Value | Description |
|----------|-------|-------------|
| `ADC_RESOLUTION_12B` | 0 | 12-bit resolution |
| `ADC_RESOLUTION_14B` | 2 | 14-bit resolution |
| `ADC_RESOLUTION_16B` | 4 | 16-bit resolution |

## Voltage Reference

| Constant | Value | Description |
|----------|-------|-------------|
| `ADC_VREF_3P2V` | 0 | 3.2V reference |
| `ADC_VREF_2P0V` | 1 | 2.0V reference |

## Temperature Sensor Mode

| Constant | Value | Description |
|----------|-------|-------------|
| `ADC_TSEN_MOD_INTERNAL_DIODE` | 0 | Use internal temperature diode |
| `ADC_TSEN_MOD_EXTERNAL_DIODE` | 1 | Use external temperature diode |

## Configuration Structure

```c
struct bflb_adc_config_s {
    uint8_t clk_div;               /* ADC clock division, use @ref ADC_CLK_DIV */
    uint8_t scan_conv_mode;        /* Scan mode enable (1=scan multiple channels) */
    uint8_t continuous_conv_mode;  /* Continuous conversion enable */
    uint8_t differential_mode;     /* Differential mode enable */
    uint8_t resolution;            /* Resolution, use @ref ADC_RESOLUTION */
    uint8_t vref;                 /* Voltage reference, use @ref ADC_VREF */
};
```

## Channel Select Structure

```c
struct bflb_adc_channel_s {
    uint8_t pos_chan;    /* Positive input channel */
    uint8_t neg_chan;    /* Negative input channel (for differential) */
};
```

## ADC Result Structure

```c
struct bflb_adc_result_s {
    int8_t pos_chan;      /* Positive channel number */
    int8_t neg_chan;      /* Negative channel number */
    int32_t value;        /* Raw ADC value */
    int32_t millivolt;    /* Converted voltage in millivolts */
};
```

## API Functions

### bflb_adc_init

Initialize the ADC.

```c
void bflb_adc_init(struct bflb_device_s *dev, const struct bflb_adc_config_s *config);
```

**Parameters:**
- `dev` - Device handle (e.g., `bflb_device_get_by_name("adc")`)
- `config` - Pointer to ADC configuration

---

### bflb_adc_deinit

Deinitialize the ADC.

```c
void bflb_adc_deinit(struct bflb_device_s *dev);
```

---

### bflb_adc_link_rxdma

Enable/disable DMA linking for ADC receive.

```c
void bflb_adc_link_rxdma(struct bflb_device_s *dev, bool enable);
```

---

### bflb_adc_channel_config

Configure ADC channels for sampling.

```c
int bflb_adc_channel_config(struct bflb_device_s *dev, 
                            struct bflb_adc_channel_s *chan, 
                            uint8_t channels);
```

**Parameters:**
- `dev` - Device handle
- `chan` - Pointer to channel configuration array
- `channels` - Number of channel pairs to configure

**Returns:** 0 on success, negative error code on failure

---

### bflb_adc_start_conversion

Start ADC conversion.

```c
void bflb_adc_start_conversion(struct bflb_device_s *dev);
```

---

### bflb_adc_stop_conversion

Stop ADC conversion.

```c
void bflb_adc_stop_conversion(struct bflb_device_s *dev);
```

---

### bflb_adc_read_raw

Read raw ADC conversion value.

```c
uint32_t bflb_adc_read_raw(struct bflb_device_s *dev);
```

**Returns:** Raw ADC value (12/14/16 bit depending on resolution)

---

### bflb_adc_get_count

Get number of completed conversions in FIFO.

```c
uint8_t bflb_adc_get_count(struct bflb_device_s *dev);
```

**Returns:** Number of conversion results available

---

### bflb_adc_parse_result

Parse raw ADC values to voltage values.

```c
void bflb_adc_parse_result(struct bflb_device_s *dev, uint32_t *buffer,
                           struct bflb_adc_result_s *result, uint16_t count);
```

**Parameters:**
- `dev` - Device handle
- `buffer` - Pointer to raw ADC values
- `result` - Pointer to parsed results
- `count` - Number of values to parse

---

### bflb_adc_rxint_mask

Enable/disable conversion complete interrupt.

```c
void bflb_adc_rxint_mask(struct bflb_device_s *dev, bool mask);
```

**Parameters:**
- `mask` - `true` to disable, `false` to enable

---

### bflb_adc_errint_mask

Enable/disable error interrupt.

```c
void bflb_adc_errint_mask(struct bflb_device_s *dev, bool mask);
```

---

### bflb_adc_get_intstatus

Get interrupt status.

```c
uint32_t bflb_adc_get_intstatus(struct bflb_device_s *dev);
```

**Returns:** Interrupt status flags

---

### bflb_adc_int_clear

Clear interrupt flags.

```c
void bflb_adc_int_clear(struct bflb_device_s *dev, uint32_t int_clear);
```

---

### bflb_adc_set_reference_channel

Set reference channel for calibration.

```c
void bflb_adc_set_reference_channel(int channel, int32_t millivolt);
```

---

### bflb_adc_tsen_init

Initialize temperature sensor.

```c
void bflb_adc_tsen_init(struct bflb_device_s *dev, uint8_t tsen_mod);
```

**Parameters:**
- `tsen_mod` - Temperature sensor mode (`ADC_TSEN_MOD_INTERNAL_DIODE` or `ADC_TSEN_MOD_EXTERNAL_DIODE`)

---

### bflb_adc_tsen_get_temp

Get temperature from sensor.

```c
float bflb_adc_tsen_get_temp(struct bflb_device_s *dev);
```

**Returns:** Temperature in degrees Celsius

---

### bflb_adc_vbat_enable

Enable VBAT (battery voltage) measurement.

```c
void bflb_adc_vbat_enable(struct bflb_device_s *dev);
```

---

### bflb_adc_vbat_disable

Disable VBAT measurement.

```c
void bflb_adc_vbat_disable(struct bflb_device_s *dev);
```

---

### bflb_update_adc_trim

Update ADC calibration trim values.

```c
void bflb_update_adc_trim(struct bflb_device_s *dev, const struct bflb_adc_config_s *config);
```

---

### bflb_adc_feature_control

Control ADC features.

```c
int bflb_adc_feature_control(struct bflb_device_s *dev, int cmd, size_t arg);
```

**Commands:**
- `ADC_CMD_CLR_FIFO` - Clear ADC FIFO
- `ADC_CMD_VBAT_EN` - Enable VBAT measurement
- `ADC_CMD_TRIG_BY_PWM` - Trigger ADC by PWM (BL616/BL702L)

---

## Usage Examples

### Basic Single-Channel ADC Reading

```c
#include "bflb_adc.h"

void adc_single_channel_example(void)
{
    struct bflb_device_s *adc;
    struct bflb_adc_config_s config = {
        .clk_div = ADC_CLK_DIV_16,       /* ADC clock = 500kHz */
        .scan_conv_mode = false,           /* Single channel mode */
        .continuous_conv_mode = false,     /* One-shot conversion */
        .differential_mode = false,         /* Single-ended mode */
        .resolution = ADC_RESOLUTION_12B,   /* 12-bit resolution */
        .vref = ADC_VREF_3P2V,             /* 3.2V reference */
    };
    struct bflb_adc_channel_s chan = {
        .pos_chan = ADC_CHANNEL_0,
        .neg_chan = ADC_CHANNEL_GND,
    };

    adc = bflb_device_get_by_name("adc");
    
    /* Initialize ADC */
    bflb_adc_init(adc, &config);
    
    /* Configure channel */
    bflb_adc_channel_config(adc, &chan, 1);
    
    /* Start conversion */
    bflb_adc_start_conversion(adc);
    
    /* Wait for completion and read */
    while (bflb_adc_get_count(adc) == 0) {
        /* Wait */
    }
    
    uint32_t raw_value = bflb_adc_read_raw(adc);
    printf("Raw ADC value: %lu\r\n", raw_value);
    
    /* Parse result to get voltage */
    struct bflb_adc_result_s result;
    bflb_adc_parse_result(adc, &raw_value, &result, 1);
    printf("Channel: %d, Value: %ld, Voltage: %ld mV\r\n",
           result.pos_chan, result.value, result.millivolt);
}
```

### Continuous ADC with Interrupt

```c
#include "bflb_adc.h"

static struct bflb_device_s *adc;
static uint32_t adc_buffer[16];
static uint8_t buffer_index = 0;

void adc_isr(void *arg)
{
    /* Clear interrupt */
    bflb_adc_int_clear(adc, ADC_INTCLR_FIFO_UNDERRUN | ADC_INTCLR_FIFO_OVERRUN);
    
    /* Read all available values */
    while (bflb_adc_get_count(adc) > 0) {
        adc_buffer[buffer_index++] = bflb_adc_read_raw(adc);
        if (buffer_index >= 16) {
            buffer_index = 0;
            /* Process buffer... */
        }
    }
}

void adc_continuous_example(void)
{
    struct bflb_adc_config_s config = {
        .clk_div = ADC_CLK_DIV_32,
        .scan_conv_mode = false,
        .continuous_conv_mode = true,      /* Continuous mode */
        .differential_mode = false,
        .resolution = ADC_RESOLUTION_12B,
        .vref = ADC_VREF_3P2V,
    };
    struct bflb_adc_channel_s chan = {
        .pos_chan = ADC_CHANNEL_1,
        .neg_chan = ADC_CHANNEL_GND,
    };

    adc = bflb_device_get_by_name("adc");
    bflb_adc_init(adc, &config);
    bflb_adc_channel_config(adc, &chan, 1);
    
    /* Enable interrupt */
    bflb_adc_rxint_mask(adc, false);
    
    /* Register and enable IRQ */
    bflb_irq_register(adc->irq_num, adc_isr, NULL);
    bflb_irq_enable(adc->irq_num);
    
    /* Start continuous conversion */
    bflb_adc_start_conversion(adc);
}
```

### Temperature Sensor Reading

```c
#include "bflb_adc.h"

void adc_temperature_example(void)
{
    struct bflb_device_s *adc;
    struct bflb_adc_config_s config = {
        .clk_div = ADC_CLK_DIV_16,
        .scan_conv_mode = false,
        .continuous_conv_mode = false,
        .differential_mode = false,
        .resolution = ADC_RESOLUTION_12B,
        .vref = ADC_VREF_3P2V,
    };

    adc = bflb_device_get_by_name("adc");
    bflb_adc_init(adc, &config);
    
    /* Initialize temperature sensor */
    bflb_adc_tsen_init(adc, ADC_TSEN_MOD_INTERNAL_DIODE);
    
    /* Start conversion - the temperature sensor is channel 14/15 */
    bflb_adc_start_conversion(adc);
    
    while (bflb_adc_get_count(adc) == 0) {
        /* Wait */
    }
    
    /* Get temperature */
    float temperature = bflb_adc_tsen_get_temp(adc);
    printf("Temperature: %.1f C\r\n", temperature);
}
```

### Multi-Channel Scan Mode

```c
#include "bflb_adc.h"

#define NUM_CHANNELS 4

void adc_scan_example(void)
{
    struct bflb_device_s *adc;
    struct bflb_adc_config_s config = {
        .clk_div = ADC_CLK_DIV_16,
        .scan_conv_mode = true,            /* Scan multiple channels */
        .continuous_conv_mode = false,
        .differential_mode = false,
        .resolution = ADC_RESOLUTION_12B,
        .vref = ADC_VREF_3P2V,
    };
    struct bflb_adc_channel_s chan[NUM_CHANNELS] = {
        { .pos_chan = ADC_CHANNEL_0, .neg_chan = ADC_CHANNEL_GND },
        { .pos_chan = ADC_CHANNEL_1, .neg_chan = ADC_CHANNEL_GND },
        { .pos_chan = ADC_CHANNEL_2, .neg_chan = ADC_CHANNEL_GND },
        { .pos_chan = ADC_CHANNEL_3, .neg_chan = ADC_CHANNEL_GND },
    };
    uint32_t raw_values[NUM_CHANNELS];
    struct bflb_adc_result_s results[NUM_CHANNELS];

    adc = bflb_device_get_by_name("adc");
    bflb_adc_init(adc, &config);
    bflb_adc_channel_config(adc, chan, NUM_CHANNELS);
    
    /* Start scan conversion */
    bflb_adc_start_conversion(adc);
    
    /* Wait for all channels */
    while (bflb_adc_get_count(adc) < NUM_CHANNELS) {
        /* Wait */
    }
    
    /* Read all values */
    for (int i = 0; i < NUM_CHANNELS; i++) {
        raw_values[i] = bflb_adc_read_raw(adc);
    }
    
    /* Parse results */
    bflb_adc_parse_result(adc, raw_values, results, NUM_CHANNELS);
    
    /* Print results */
    for (int i = 0; i < NUM_CHANNELS; i++) {
        printf("CH%d: %ld mV\r\n", results[i].pos_chan, results[i].millivolt);
    }
}
```

### Battery Voltage Monitoring

```c
#include "bflb_adc.h"

void adc_vbat_example(void)
{
    struct bflb_device_s *adc;
    struct bflb_adc_config_s config = {
        .clk_div = ADC_CLK_DIV_16,
        .scan_conv_mode = false,
        .continuous_conv_mode = false,
        .differential_mode = false,
        .resolution = ADC_RESOLUTION_12B,
        .vref = ADC_VREF_3P2V,
    };
    struct bflb_adc_channel_s chan = {
        .pos_chan = ADC_CHANNEL_VABT_HALF,
        .neg_chan = ADC_CHANNEL_GND,
    };

    adc = bflb_device_get_by_name("adc");
    bflb_adc_init(adc, &config);
    
    /* Enable VBAT measurement */
    bflb_adc_vbat_enable(adc);
    
    bflb_adc_channel_config(adc, &chan, 1);
    bflb_adc_start_conversion(adc);
    
    while (bflb_adc_get_count(adc) == 0) {
        /* Wait */
    }
    
    uint32_t raw = bflb_adc_read_raw(adc);
    struct bflb_adc_result_s result;
    bflb_adc_parse_result(adc, &raw, &result, 1);
    
    /* VBAT_HALF returns VBAT/2, so multiply by 2 */
    printf("Battery Voltage: %ld mV\r\n", result.millivolt * 2);
    
    bflb_adc_vbat_disable(adc);
}
```

## Register-Level Overview

| Register | Offset | Description |
|----------|--------|-------------|
| `GPADC_CONFIG` | `0x00` | ADC configuration |
| `GPADC_GLOBAL` | `0x04` | ADC global control |
| `GPADC_FIFO_CONFIG` | `0x08` | FIFO configuration |
| `GPADC_FIFO_DATA` | `0x0C` | FIFO data |
| `GPADC_DINLY` | `0x10` | Data input delay |
| `GPADC2_CONFIG` | `0x14` | ADC2 configuration (16-bit mode) |
| `GPADC2_FIFO_CONFIG` | `0x18` | ADC2 FIFO configuration |
| `GPADC2_FIFO_DATA` | `0x1C` | ADC2 FIFO data |

## Interrupt Number

| Peripheral | IRQ Number |
|------------|------------|
| GPADC (ADC) | `GPADC_DMA_IRQn` (41) |
