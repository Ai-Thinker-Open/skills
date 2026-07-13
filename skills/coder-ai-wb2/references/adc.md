# ADC API Reference

> Source file: `components/platform/hosal/include/hosal_adc.h`

## Macro Definitions

```c
#define HOSAL_WAIT_FOREVER 0xFFFFFFFFU  // Wait indefinitely
```

## Type Definitions

### `hosal_adc_sample_mode_t` — Sampling Mode

```c
typedef enum {
    HOSAL_ADC_ONE_SHOT,   // Single sampling
    HOSAL_ADC_CONTINUE    // Continuous sampling
} hosal_adc_sample_mode_t;
```

### `hosal_adc_event_t` — ADC Interrupt Events

```c
typedef enum {
    HOSAL_ADC_INT_OV,      // Overflow error
    HOSAL_ADC_INT_EOS,     // End of Sample
    HOSAL_ADC_INT_DMA_TRH, // DMA transfer half-full
    HOSAL_ADC_INT_DMA_TRC, // DMA transfer complete
    HOSAL_ADC_INT_DMA_TRE, // DMA transfer error
} hosal_adc_event_t;
```

### `hosal_adc_config_t` — ADC Configuration Structure

```c
typedef struct {
    uint32_t sampling_freq;       // Sampling frequency in Hz
    uint32_t pin;                 // ADC pin
    hosal_adc_sample_mode_t mode; // Sampling mode
    uint8_t  sample_resolution;   // Sampling resolution (bits)
} hosal_adc_config_t;
```

### `hosal_adc_irq_t` — ADC Interrupt Callback Type

```c
typedef void (*hosal_adc_irq_t)(void *parg);
```

### `hosal_adc_cb_t` — ADC Sampling Callback Type

```c
typedef void (*hosal_adc_cb_t)(hosal_adc_event_t event, void *data, uint32_t size);
```

### `hosal_adc_dev_t` — ADC Device Structure

```c
typedef struct {
    uint8_t port;
    hosal_adc_config_t config;
    hosal_dma_chan_t dma_chan;   // DMA channel
    hosal_adc_irq_t cb;          // Interrupt callback
    void *p_arg;
    void *priv;
} hosal_adc_dev_t;
```

## Function API

### `hosal_adc_init`

Initialize the ADC.

```c
int hosal_adc_init(hosal_adc_dev_t *adc);
```

---

### `hosal_adc_add_channel`

Add an ADC sampling channel.

```c
int hosal_adc_add_channel(hosal_adc_dev_t *adc, uint32_t channel);
```

---

### `hosal_adc_remove_channel`

Remove an ADC sampling channel.

```c
int hosal_adc_remove_channel(hosal_adc_dev_t *adc, uint32_t channel);
```

---

### `hosal_adc_add_reference_channel`

Add a reference channel.

```c
int hosal_adc_add_reference_channel(hosal_adc_dev_t *adc,
                                     uint32_t refer_channel,
                                     float refer_voltage);
```

---

### `hosal_adc_remove_reference_channel`

Remove the reference channel.

```c
int hosal_adc_remove_reference_channel(hosal_adc_dev_t *adc);
```

---

### `hosal_adc_value_get`

Read a single ADC sample value (blocking).

```c
int hosal_adc_value_get(hosal_adc_dev_t *adc,
                        uint32_t channel,
                        uint32_t timeout);
```

| Parameter | Description |
|-----------|-------------|
| `adc` | ADC device |
| `channel` | ADC channel number |
| `timeout` | Timeout in milliseconds |

**Return value**: Sample value (>=0), failure `-1`

---

### `hosal_adc_tsen_value_get`

Read the internal temperature sensor.

```c
int hosal_adc_tsen_value_get(hosal_adc_dev_t *adc);
```

---

### `hosal_adc_sample_cb_reg`

Register an ADC sampling callback (used in continuous sampling mode).

```c
int hosal_adc_sample_cb_reg(hosal_adc_dev_t *adc, hosal_adc_cb_t cb);
```

---

### `hosal_adc_start`

Start continuous sampling.

```c
int hosal_adc_start(hosal_adc_dev_t *adc, void *data, uint32_t size);
```

| Parameter | Description |
|-----------|-------------|
| `data` | Sampling data buffer |
| `size` | Buffer size (aligned by resolution) |

---

### `hosal_adc_stop`

Stop ADC sampling.

```c
int hosal_adc_stop(hosal_adc_dev_t *adc);
```

---

### `hosal_adc_finalize`

Release the ADC.

```c
int hosal_adc_finalize(hosal_adc_dev_t *adc);
```

## Usage Example

```c
#include "hal_adc.h"

hosal_adc_dev_t adc0 = {
    .port = 0,
    .config = {
        .sampling_freq = 100000,   // 100kHz
        .pin = 0,                  // ADC channel 0
        .mode = HOSAL_ADC_ONE_SHOT, // One-shot mode
        .sample_resolution = 12,    // 12 bits
    }
};

hosal_adc_init(&adc0);
hosal_adc_add_channel(&adc0, 0);

// Single read
int val = hosal_adc_value_get(&adc0, 0, HOSAL_WAIT_FOREVER);
if (val >= 0) {
    float voltage = val * 3.3f / 4096.0f;
    printf("ADC: %d, Voltage: %.3fV\r\n", val, voltage);
}

// Read internal temperature sensor
int temp = hosal_adc_tsen_value_get(&adc0);

hosal_adc_finalize(&adc0);
```

---

## Register-Level Programming

> Register Header: `components/platform/soc/bl602/bl602_std/bl602_std/Device/Bouffalo/BL602/Peripherals/gpip_reg.h`  
> Base Address: `0x40002000`

### Register Overview

| Offset | Name | Description |
|--------|------|-------------|
| 0x00 | GPADC_CONFIG | ADC configuration (enable, channel select, mode) |
| 0x04 | GPADC_GLOBAL | Global ADC control (enable, clock divider) |
| 0x08 | GPADC_STATUS | ADC status (conversion done, IRQ flags) |
| 0x0C | GPADC_RDATA | ADC result data (12-bit) |
| 0x10 | GPADC_DMA_RDATA | DMA read data address |

### Key Register Fields

**GPADC_CONFIG (0x00)**

| Bits | Name | Description |
|------|------|-------------|
| 0 | gpadc_en | ADC enable (1=enable) |
| [7:4] | channel_sel | Channel select (0-7) |
| 8 | conti_conv | Continuous conversion mode (1=continuous) |
| 9 | dma_en | DMA enable (1=enable) |
| 10 | interrupt_en | Interrupt enable (1=enable) |

**GPADC_GLOBAL (0x04)**

| Bits | Name | Description |
|------|------|-------------|
| 0 | global_en | Global ADC enable (1=enable) |
| [5:2] | clock_div | Clock divider (divider = value + 1) |

**GPADC_STATUS (0x08)**

| Bits | Name | Description |
|------|------|-------------|
| 0 | conv_done | Conversion done flag (1=done) |
| 1 | conv_done_irq | Conversion done interrupt flag |

**GPADC_RDATA (0x0C)**

| Bits | Name | Description |
|------|------|-------------|
| [11:0] | adc_data | 12-bit ADC result |

### Register-Level Code Example

```c
#include <stdint.h>

/* Register base */
#define GPADC_BASE  0x40002000

/* Register offsets */
#define GPADC_CONFIG   0x00
#define GPADC_GLOBAL   0x04
#define GPADC_STATUS   0x08
#define GPADC_RDATA    0x0C

/* Bit masks */
#define GPADC_CONFIG_EN       (1 << 0)
#define GPADC_CONFIG_CHAN_MSK (0xF << 4)
#define GPADC_CONFIG_CONTI    (1 << 8)
#define GPADC_GLOBAL_EN       (1 << 0)
#define GPADC_STATUS_DONE     (1 << 0)

static volatile uint32_t * const GPADC = (volatile uint32_t *)GPADC_BASE;

/* Simple delay for polling */
static void delay(void) {
    volatile uint32_t i;
    for (i = 0; i < 1000; i++);
}

/* Read ADC channel (blocking, one-shot) */
uint32_t adc_read_reg(uint8_t channel) {
    uint32_t cfg;

    /* Disable ADC during configuration */
    GPADC[GPADC_CONFIG / 4] = 0;

    /* Set clock divider: PCLK / (div+1) = 1MHz, assuming PCLK=2MHz */
    GPADC[GPADC_GLOBAL / 4] = GPADC_GLOBAL_EN | (1 << 2);  /* div=1 -> 1MHz */

    /* Configure: channel select, enable */
    cfg = GPADC_CONFIG_EN | ((channel & 0x7) << 4);
    GPADC[GPADC_CONFIG / 4] = cfg;

    /* Wait for conversion done */
    delay();
    while ((GPADC[GPADC_STATUS / 4] & GPADC_STATUS_DONE) == 0);

    /* Read result */
    uint32_t rdata = GPADC[GPADC_RDATA / 4] & 0xFFF;

    /* Disable ADC */
    GPADC[GPADC_CONFIG / 4] = 0;

    return rdata;
}

/* Example: read channel 3 */
void adc_example(void) {
    uint32_t raw = adc_read_reg(3);
    float voltage = (float)raw * 3.3f / 4096.0f;
    printf("ADC ch3: raw=%u, voltage=%.3fV\r\n", raw, voltage);
}
```
