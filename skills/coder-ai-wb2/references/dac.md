# DAC API Reference

> Source file: `components/platform/hosal/include/hosal_dac.h`

## Type Definitions

### `hosal_dac_cb_t` — DAC Callback Function Type

```c
typedef void (*hosal_dac_cb_t)(void *arg);
```

### `hosal_dac_config_t` — DAC Configuration Structure

```c
typedef struct {
    uint8_t  dma_enable;  // 1: use DMA, 0: do not use DMA
    uint32_t pin;         // DAC pin
    uint32_t freq;        // DAC frequency
} hosal_dac_config_t;
```

### `hosal_dac_dev_t` — DAC Device Structure

```c
typedef struct {
    uint8_t            port;       // DAC port number
    hosal_dac_config_t config;    // DAC configuration
    hosal_dac_cb_t     cb;        // DMA callback
    hosal_dma_chan_t   dma_chan;  // DMA channel
    void              *arg;        // Callback argument
    void              *priv;
} hosal_dac_dev_t;
```

## Function API

### `hosal_dac_init`

Initialize DAC.

```c
int hosal_dac_init(hosal_dac_dev_t *dac);
```

| Parameter | Description |
|------|------|
| `dac` | DAC device structure pointer |

**Return value**: `0` success, `EIO` failure

---

### `hosal_dac_finalize`

Release DAC.

```c
int hosal_dac_finalize(hosal_dac_dev_t *dac);
```

| Parameter | Description |
|------|------|
| `dac` | DAC device |

**Return value**: `0` success, `EIO` failure

---

### `hosal_dac_start`

Start DAC output (non-DMA mode).

```c
int hosal_dac_start(hosal_dac_dev_t *dac);
```

---

### `hosal_dac_stop`

Stop DAC output.

```c
int hosal_dac_stop(hosal_dac_dev_t *dac);
```

---

### `hosal_dac_set_value`

Set DAC output value (in μV).

```c
int hosal_dac_set_value(hosal_dac_dev_t *dac, uint32_t data);
```

| Parameter | Description |
|------|------|
| `dac` | DAC device |
| `data` | Output value in μV |

**Return value**: `0` success, `EIO` failure

---

### `hosal_dac_get_value`

Get the most recent DAC output value.

```c
int hosal_dac_get_value(hosal_dac_dev_t *dac);
```

**Return value**: DAC output value (μV)

---

### `hosal_dac_dma_cb_reg`

Register DMA mode completion callback.

```c
int hosal_dac_dma_cb_reg(hosal_dac_dev_t *dac, hosal_dac_cb_t callback, void *arg);
```

---

### `hosal_dac_dma_start`

Start DMA mode DAC output.

```c
int hosal_dac_dma_start(hosal_dac_dev_t *dac, uint32_t *data, uint32_t size);
```

| Parameter | Description |
|------|------|
| `dac` | DAC device |
| `data` | DAC data buffer |
| `size` | Buffer size |

---

### `hosal_dac_dma_stop`

Stop DMA mode DAC output.

```c
int hosal_dac_dma_stop(hosal_dac_dev_t *dac);
```

## Usage Example

```c
#include "hal_dac.h"

hosal_dac_dev_t dac0 = {
    .port = 0,
    .config = {
        .dma_enable = 0,   // Non-DMA mode
        .pin = 0,
        .freq = 0,
    }
};

hosal_dac_init(&dac0);
hosal_dac_start(&dac0);

// Set output voltage value (in μV), e.g., 3300000 = 3.3V
hosal_dac_set_value(&dac0, 3300000);

// Get current output value
int val = hosal_dac_get_value(&dac0);

// DMA mode
hosal_dac_dma_cb_reg(&dac0, my_dac_callback, NULL);
hosal_dac_dma_start(&dac0, dac_buf, sizeof(dac_buf));
```

---

## Register-Level Programming

> Register Header: `components/platform/soc/bl602/bl602_std/bl602_std/Device/Bouffalo/BL602/Peripherals/dac_reg.h`  
> Base Address: `0x40003000` (Audio subsystem)

### Register Overview

| Offset | Name | Description |
|--------|------|-------------|
| 0x00 | DAC_CONFIG | DAC configuration (enable, channel, DMA) |
| 0x04 | DAC_FIFO | DAC FIFO data (write audio samples) |
| 0x08 | DAC_VOL | DAC volume control |
| 0x0C | DAC_CTRL | DAC control (start/stop) |

### Key Register Fields

**DAC_CONFIG (0x00)**

| Bits | Name | Description |
|------|------|-------------|
| 0 | dac_en | DAC enable (1=enable) |
| 1 | dma_en | DMA enable (1=enable) |
| [7:4] | channel | DAC channel (0 or 1) |

**DAC_FIFO (0x04)**

| Bits | Name | Description |
|------|------|-------------|
| [7:0] | fifo_data | FIFO data (write 8-bit audio sample) |

**DAC_CTRL (0x0C)**

| Bits | Name | Description |
|------|------|-------------|
| 0 | dac_start | DAC start (write 1 to start) |
| 1 | dac_stop | DAC stop (write 1 to stop) |

### Register-Level Code Example

```c
#include <stdint.h>

/* Audio/DAC base - typically 0x40003000 on BL602 */
#define AUDIO_BASE   0x40003000

/* DAC register offsets */
#define DAC_CONFIG  0x00
#define DAC_FIFO   0x04
#define DAC_VOL    0x08
#define DAC_CTRL   0x0C

/* Bit masks */
#define DAC_CONFIG_EN      (1 << 0)
#define DAC_CONFIG_DMA_EN  (1 << 1)
#define DAC_CONFIG_CHAN_MSK (0xF << 4)
#define DAC_CTRL_START     (1 << 0)
#define DAC_CTRL_STOP      (1 << 1)

static volatile uint8_t * const DAC = (volatile uint8_t *)AUDIO_BASE;

/* DAC output voltage (8-bit, 0-255 -> 0-VREF) */
void dac_set_value(uint8_t channel, uint8_t value) {
    /* Disable DAC during config */
    DAC[DAC_CONFIG] = 0;

    /* Configure: enable, channel select */
    DAC[DAC_CONFIG] = DAC_CONFIG_EN | ((channel & 1) << 4);

    /* Write sample to FIFO */
    DAC[DAC_FIFO] = value;

    /* Start DAC */
    DAC[DAC_CTRL] = DAC_CTRL_START;
}

/* Generate sine wave samples (8-bit, unsigned) */
uint8_t sine_8bit(uint16_t phase) {
    /* phase: 0-255 maps to 0-2pi */
    int32_t s = 127 + (int32_t)(127.0 * sinf((float)phase * 6.2832f / 256.0f));
    if (s > 255) s = 255;
    if (s < 0) s = 0;
    return (uint8_t)s;
}

/* Example: output sawtooth on channel 0 */
void dac_example(void) {
    uint8_t i;
    for (i = 0; i < 255; i++) {
        dac_set_value(0, i);
    }
    /* Stop after output */
    DAC[DAC_CTRL] = DAC_CTRL_STOP;
}

/* Example: output sine wave using DMA-like polling */
void dac_sine_example(void) {
    uint16_t phase = 0;
    uint8_t sample;

    /* Enable DAC channel 0 with FIFO */
    DAC[DAC_CONFIG] = DAC_CONFIG_EN;

    /* Stream samples (in real use, this would be in an interrupt or DMA) */
    while (phase < 256) {
        sample = sine_8bit(phase++);
        DAC[DAC_FIFO] = sample;
        /* Wait for FIFO not full (simplified) */
    }
}
```
