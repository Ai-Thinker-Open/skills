# AUADC API Reference (BL616/BL618)

> **Source:** `bouffalo_sdk/drivers/lhal/include/bflb_auadc.h`  
> **Implementation:** `bouffalo_sdk/drivers/lhal/src/bflb_auadc.c`  
> **Register Header:** `bouffalo_sdk/drivers/lhal/include/hardware/auadc_reg.h`

## Overview

The AUADC (Audio ADC) peripheral provides audio analog-to-digital conversion with support for both analog microphone input and digital PDM microphone input. It features a configurable sampling rate, selectable data format, FIFO-based DMA transfer, and interrupt-driven operation. On chips with analog ADC support (BL616, BL618DG, BL702L), it also provides PGA gain control, measurement mode, and multiple analog input channels.

> **Note:** Analog ADC support is available on BL616, BL618DG, and BL702L. BL616CL only supports PDM digital input (`AUADC_ANALOG_ADC_SUPPORT = 0`).

## Base Address

| Chip | AUADC Base Address |
|------|-------------------|
| BL616 / BL616CL | `0x2000AC00` |
| BL618DG | `0x20017C00` |
| BL702L | `0x4000AD00` |

---

## Configuration Macros

### Sampling Rate (AUADC_SAMPLING_RATE)

Used in audio mode to set the ADC sampling rate:

| Macro | Value | Description |
|-------|-------|-------------|
| `AUADC_SAMPLING_RATE_8K` | 0 | 8 kHz (audio mode) |
| `AUADC_SAMPLING_RATE_16K` | 1 | 16 kHz (audio mode) |
| `AUADC_SAMPLING_RATE_24K` | 2 | 24 kHz / 22.05 kHz (audio mode, adjust AUPLL clock) |
| `AUADC_SAMPLING_RATE_32K` | 3 | 32 kHz (audio mode) |
| `AUADC_SAMPLING_RATE_48K` | 4 | 48 kHz / 44.1 kHz (audio mode, adjust AUPLL clock) |

Analog ADC measurement mode rates (only when `AUADC_ANALOG_ADC_SUPPORT = 1`):

| Macro | Value | Description |
|-------|-------|-------------|
| `AUADC_SAMPLING_RATE_MEASURE_128K` | 8 | 128 kHz (measurement mode only) |
| `AUADC_SAMPLING_RATE_MEASURE_256K` | 9 | 256 kHz (measurement mode only) |
| `AUADC_SAMPLING_RATE_MEASURE_512K` | 10 | 512 kHz (measurement mode only) |

### Input Mode (AUADC_INPUT_MODE)

| Macro | Value | Description |
|-------|-------|-------------|
| `AUADC_INPUT_MODE_ADC` | 0 | Analog ADC input *(requires analog ADC support)* |
| `AUADC_INPUT_MODE_PDM_L` | 1 | PDM left channel |
| `AUADC_INPUT_MODE_PDM_R` | 2 | PDM right channel |

### Data Format (AUADC_DATA_FORMAT)

| Macro | Value | Description |
|-------|-------|-------------|
| `AUADC_DATA_FORMAT_32BIT` | 0 | 32-bit samples |
| `AUADC_DATA_FORMAT_24BIT` | 1 | 24-bit samples |
| `AUADC_DATA_FORMAT_20BIT` | 2 | 20-bit samples |
| `AUADC_DATA_FORMAT_16BIT` | 3 | 16-bit samples |

### Analog ADC Channel (AUADC_ADC_ANALOG_CH)

Only when `AUADC_ANALOG_ADC_SUPPORT = 1`:

| Macro | Value | Description |
|-------|-------|-------------|
| `AUADC_ADC_ANALOG_CH_0` | 0 | Analog input channel 0 |
| `AUADC_ADC_ANALOG_CH_3` | 3 | Analog input channel 3 |
| `AUADC_ADC_ANALOG_CH_4` | 4 | Analog input channel 4 |
| `AUADC_ADC_ANALOG_CH_7` | 7 | Analog input channel 7 |

### Analog ADC Measurement Rate (AUADC_ADC_MEASURE_RATE)

Only when `AUADC_ANALOG_ADC_SUPPORT = 1`. Used when ADC mode is `AUADC_ADC_MODE_MEASURE` and sampling rate is `AUADC_SAMPLING_RATE_MEASURE_256K`:

| Macro | Value | Rate (SPS) |
|-------|-------|------------|
| `AUADC_ADC_MEASURE_RATE_SPS_2_5` | 0 | 2.5 |
| `AUADC_ADC_MEASURE_RATE_SPS_5` | 1 | 5 |
| `AUADC_ADC_MEASURE_RATE_SPS_10` | 2 | 10 |
| `AUADC_ADC_MEASURE_RATE_SPS_20` | 3 | 20 |
| `AUADC_ADC_MEASURE_RATE_SPS_25` | 4 | 25 |
| `AUADC_ADC_MEASURE_RATE_SPS_50` | 5 | 50 |
| `AUADC_ADC_MEASURE_RATE_SPS_100` | 6 | 100 |
| `AUADC_ADC_MEASURE_RATE_SPS_200` | 7 | 200 |
| `AUADC_ADC_MEASURE_RATE_SPS_400` | 8 | 400 |
| `AUADC_ADC_MEASURE_RATE_SPS_800` | 9 | 800 |
| `AUADC_ADC_MEASURE_RATE_SPS_1000` | 10 | 1000 |
| `AUADC_ADC_MEASURE_RATE_SPS_2000` | 11 | 2000 |
| `AUADC_ADC_MEASURE_RATE_SPS_4000` | 12 | 4000 |

### Analog ADC Mode (AUADC_ADC_MODE)

Only when `AUADC_ANALOG_ADC_SUPPORT = 1`:

| Macro | Value | Description |
|-------|-------|-------------|
| `AUADC_ADC_MODE_AUDIO` | 0 | Audio mode (standard audio capture) |
| `AUADC_ADC_MODE_MEASURE` | 1 | Measurement mode (DC/AC voltage measurement with configurable rate) |

### Analog ADC PGA Mode (AUADC_ADC_PGA_MODE)

Only when `AUADC_ANALOG_ADC_SUPPORT = 1`:

| Macro | Value | Description |
|-------|-------|-------------|
| `AUADC_ADC_PGA_MODE_AC_DIFFER` | 0 | AC-coupled differential input |
| `AUADC_ADC_PGA_MODE_AC_SINGLE` | 1 | AC-coupled single-ended input |
| `AUADC_ADC_PGA_MODE_DC_DIFFER` | 2 | DC-coupled differential input |
| `AUADC_ADC_PGA_MODE_DC_SINGLE` | 3 | DC-coupled single-ended input |

### Interrupt Masks (AUADC_INTMASK)

Used with `bflb_auadc_int_mask()` and `bflb_auadc_int_unmask()`:

| Macro | Value | Description |
|-------|-------|-------------|
| `AUADC_INTMASK_FIFO_OVER` | `(1 << 1)` | FIFO overflow interrupt |
| `AUADC_INTMASK_FIFO_UNDER` | `(1 << 2)` | FIFO underflow interrupt |
| `AUADC_INTMASK_FIFO_AVAILABLE` | `(1 << 3)` | FIFO data available interrupt |

### Interrupt Status (AUADC_INTSTS)

Returned by `bflb_auadc_get_intstatus()`:

| Macro | Value | Description |
|-------|-------|-------------|
| `AUADC_INTSTS_FIFO_OVER` | `(1 << 1)` | FIFO overflow occurred |
| `AUADC_INTSTS_FIFO_UNDER` | `(1 << 2)` | FIFO underflow occurred |
| `AUADC_INTSTS_FIFO_AVAILABLE` | `(1 << 4)` | FIFO data available |

### Feature Control Commands (AUADC_CMD)

Used with `bflb_auadc_feature_control()`:

| Command | Value | Description |
|---------|-------|-------------|
| `AUADC_CMD_RECORD_START` | `0x01` | Start audio recording |
| `AUADC_CMD_RECORD_STOP` | `0x02` | Stop audio recording |
| `AUADC_CMD_SET_VOLUME_VAL` | `0x03` | Set digital volume (arg: -191 to +36, 0.5 dB step, range ~ -95.5 to +18 dB) |
| `AUADC_CMD_SET_PGA_GAIN_VAL` | `0x04` | Set PGA gain (arg: 6-42 dB, step 3 dB) *(analog ADC only)* |
| `AUADC_CMD_CLEAR_RX_FIFO` | `0x05` | Flush the RX FIFO |
| `AUADC_CMD_GET_RX_FIFO_CNT` | `0x06` | Get current RX FIFO count |

---

## Configuration Structures

### bflb_auadc_init_config_s

AUADC initialization configuration structure:

```c
struct bflb_auadc_init_config_s {
    uint8_t sampling_rate;   /* AUADC_SAMPLING_RATE */
    uint8_t input_mode;      /* AUADC_INPUT_MODE */
    uint8_t data_format;     /* AUADC_DATA_FORMAT */
    uint8_t fifo_threshold;  /* RX FIFO threshold, 0 ~ 7 */
};
```

| Field | Type | Description |
|-------|------|-------------|
| `sampling_rate` | `uint8_t` | Sampling rate, use `AUADC_SAMPLING_RATE_*` macros |
| `input_mode` | `uint8_t` | Input mode, use `AUADC_INPUT_MODE_*` macros |
| `data_format` | `uint8_t` | FIFO data format, use `AUADC_DATA_FORMAT_*` macros |
| `fifo_threshold` | `uint8_t` | RX FIFO threshold level, valid range: 0 ~ 7 |

### bflb_auadc_adc_init_config_s

Analog ADC initialization structure. Only available when `AUADC_ANALOG_ADC_SUPPORT = 1`:

```c
struct bflb_auadc_adc_init_config_s {
    uint8_t auadc_analog_en;   /* true/false - enable analog circuit */
    uint8_t adc_mode;          /* AUADC_ADC_MODE */
    uint8_t adc_pga_mode;      /* AUADC_ADC_PGA_MODE */
    uint8_t adc_pga_posi_ch;   /* AUADC_ADC_ANALOG_CH - positive input channel */
    uint8_t adc_pga_nega_ch;   /* AUADC_ADC_ANALOG_CH - negative input channel (differential only) */
    uint8_t adc_pga_gain;      /* PGA gain: 6 ~ 42 dB, step 3 dB */
    uint8_t adc_measure_rate;  /* AUADC_ADC_MEASURE_RATE - measurement mode rate */
};
```

| Field | Type | Description |
|-------|------|-------------|
| `auadc_analog_en` | `uint8_t` | Enable analog ADC circuit (`true`/`false`) |
| `adc_mode` | `uint8_t` | ADC operating mode, use `AUADC_ADC_MODE_*` macros |
| `adc_pga_mode` | `uint8_t` | PGA coupling mode, use `AUADC_ADC_PGA_MODE_*` macros |
| `adc_pga_posi_ch` | `uint8_t` | Positive channel selection, use `AUADC_ADC_ANALOG_CH_*` macros |
| `adc_pga_nega_ch` | `uint8_t` | Negative channel selection (valid only in differential mode), use `AUADC_ADC_ANALOG_CH_*` macros |
| `adc_pga_gain` | `uint8_t` | PGA gain control, range 6 ~ 42 dB, step 3 dB |
| `adc_measure_rate` | `uint8_t` | Measurement mode sampling rate (valid when sampling rate is `AUADC_SAMPLING_RATE_MEASURE_256K`), use `AUADC_ADC_MEASURE_RATE_*` macros |

---

## LHAL API Functions

### bflb_auadc_init

Initialize the AUADC peripheral.

```c
int bflb_auadc_init(struct bflb_device_s *dev, const struct bflb_auadc_init_config_s *config);
```

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `dev` | `struct bflb_device_s *` | Device handle |
| `config` | `const struct bflb_auadc_init_config_s *` | Initialization configuration |

**Returns:** `0` on success, negative on error.

**What it does:**
1. Enables the AUADC clock
2. Configures sampling rate
3. Enables DMA interface, disables channel 0
4. Selects PDM or analog ADC input source
5. Configures PDM path (enable/disable, left/right channel)
6. Configures audio OSR (64 for 32K/48K PDM, 128 otherwise)
7. Configures FIFO (data format, threshold, 24-bit sample resolution)
8. Disables record, DMA, and interrupts; flushes FIFO
9. Enables channel 0

---

### bflb_auadc_adc_init

Initialize the analog ADC sub-block. Only available when `AUADC_ANALOG_ADC_SUPPORT = 1`.

```c
int bflb_auadc_adc_init(struct bflb_device_s *dev, const struct bflb_auadc_adc_init_config_s *config);
```

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `dev` | `struct bflb_device_s *` | Device handle |
| `config` | `const struct bflb_auadc_adc_init_config_s *` | ADC analog configuration |

**Returns:** `0` on success, negative on error.

**What it does:**
1. If `auadc_analog_en` is `false`, powers down PGA and SDM, disables channels
2. Otherwise: powers up PGA and SDM, holds SDM in reset
3. Selects analog input channels (positive and negative)
4. Configures PGA mode (AC/DC, differential/single-ended)
5. Sets PGA gain (divides value by 3 for register)
6. Configures ADC mode (audio or measurement)
7. Sets measurement mode output data rate
8. Enables analog channels (both for differential, one for single-ended)
9. Starts SDM conversion
10. For DC modes, adjusts integrator op-number and bias current

---

### bflb_auadc_link_rxdma

Enable or disable the RX DMA link.

```c
int bflb_auadc_link_rxdma(struct bflb_device_s *dev, bool enable);
```

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `dev` | `struct bflb_device_s *` | Device handle |
| `enable` | `bool` | `true` to enable DMA, `false` to disable |

**Returns:** `0` on success, negative on error.

---

### bflb_auadc_int_mask

Mask (disable) specific AUADC interrupts.

```c
int bflb_auadc_int_mask(struct bflb_device_s *dev, uint32_t int_sts);
```

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `dev` | `struct bflb_device_s *` | Device handle |
| `int_sts` | `uint32_t` | Interrupt mask bits (OR'd `AUADC_INTMASK_*` values) |

**Returns:** `0` on success, negative on error.

---

### bflb_auadc_int_unmask

Unmask (enable) specific AUADC interrupts.

```c
int bflb_auadc_int_unmask(struct bflb_device_s *dev, uint32_t int_sts);
```

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `dev` | `struct bflb_device_s *` | Device handle |
| `int_sts` | `uint32_t` | Interrupt unmask bits (OR'd `AUADC_INTMASK_*` values) |

**Returns:** `0` on success, negative on error.

---

### bflb_auadc_get_intstatus

Get the current interrupt status.

```c
int bflb_auadc_get_intstatus(struct bflb_device_s *dev);
```

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `dev` | `struct bflb_device_s *` | Device handle |

**Returns:** Interrupt status bits (OR'd `AUADC_INTSTS_*` values), or negative on error.

---

### bflb_auadc_feature_control

Control AUADC features via command interface.

```c
int bflb_auadc_feature_control(struct bflb_device_s *dev, int cmd, size_t arg);
```

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `dev` | `struct bflb_device_s *` | Device handle |
| `cmd` | `int` | Command, use `AUADC_CMD_*` macros |
| `arg` | `size_t` | Command argument (meaning depends on `cmd`) |

**Returns:** Depends on command. `AUADC_CMD_GET_RX_FIFO_CNT` returns the FIFO count; others return 0 on success or negative on error.

**Command Argument Details:**

| Command | `arg` Meaning |
|---------|--------------|
| `AUADC_CMD_RECORD_START` | Not used |
| `AUADC_CMD_RECORD_STOP` | Not used |
| `AUADC_CMD_SET_VOLUME_VAL` | Volume in 0.5 dB steps: -191 to +36 (range ~ -95.5 dB to +18 dB) |
| `AUADC_CMD_SET_PGA_GAIN_VAL` | PGA gain: 6 ~ 42 dB, step 3 dB *(analog ADC only)* |
| `AUADC_CMD_CLEAR_RX_FIFO` | Not used |
| `AUADC_CMD_GET_RX_FIFO_CNT` | Not used; returns current FIFO data count |

---

## Usage Examples

### Example 1: PDM Microphone Recording with DMA

```c
#include "bflb_auadc.h"
#include "bflb_dma.h"

#define AUDIO_BUFFER_SIZE  4096

static uint32_t audio_buffer[AUDIO_BUFFER_SIZE / 4];

void pdm_record_example(void)
{
    struct bflb_device_s *auadc;

    // Get AUADC device handle
    auadc = bflb_device_get_by_name("auadc");

    // Configure AUADC for PDM left channel, 16 kHz, 16-bit
    struct bflb_auadc_init_config_s cfg = {
        .sampling_rate = AUADC_SAMPLING_RATE_16K,
        .input_mode    = AUADC_INPUT_MODE_PDM_L,
        .data_format   = AUADC_DATA_FORMAT_16BIT,
        .fifo_threshold = 4,
    };

    bflb_auadc_init(auadc, &cfg);

    // Enable DMA
    bflb_auadc_link_rxdma(auadc, true);

    // Start recording
    bflb_auadc_feature_control(auadc, AUADC_CMD_RECORD_START, 0);
}
```

### Example 2: Analog ADC Audio Recording

```c
#include "bflb_auadc.h"

void analog_adc_audio_example(void)
{
    struct bflb_device_s *auadc;

    auadc = bflb_device_get_by_name("auadc");

    // Step 1: Configure AUADC for analog ADC, 48 kHz, 24-bit
    struct bflb_auadc_init_config_s auadc_cfg = {
        .sampling_rate  = AUADC_SAMPLING_RATE_48K,
        .input_mode     = AUADC_INPUT_MODE_ADC,
        .data_format    = AUADC_DATA_FORMAT_24BIT,
        .fifo_threshold = 4,
    };
    bflb_auadc_init(auadc, &auadc_cfg);

    // Step 2: Configure analog ADC sub-block
    struct bflb_auadc_adc_init_config_s adc_cfg = {
        .auadc_analog_en   = true,
        .adc_mode          = AUADC_ADC_MODE_AUDIO,
        .adc_pga_mode      = AUADC_ADC_PGA_MODE_AC_SINGLE,
        .adc_pga_posi_ch   = AUADC_ADC_ANALOG_CH_0,
        .adc_pga_nega_ch   = 0,              // not used in single-ended mode
        .adc_pga_gain      = 18,             // 18 dB gain
        .adc_measure_rate  = 0,              // not used in audio mode
    };
    bflb_auadc_adc_init(auadc, &adc_cfg);

    // Step 3: Set volume
    bflb_auadc_feature_control(auadc, AUADC_CMD_SET_VOLUME_VAL, 0); // 0 dB

    // Step 4: Enable DMA and start recording
    bflb_auadc_link_rxdma(auadc, true);
    bflb_auadc_feature_control(auadc, AUADC_CMD_RECORD_START, 0);
}
```

### Example 3: Analog ADC Measurement Mode (DC Voltage)

```c
#include "bflb_auadc.h"

void analog_adc_measure_example(void)
{
    struct bflb_device_s *auadc;

    auadc = bflb_device_get_by_name("auadc");

    // Step 1: Initialize AUADC with measurement sampling rate
    struct bflb_auadc_init_config_s auadc_cfg = {
        .sampling_rate  = AUADC_SAMPLING_RATE_MEASURE_256K,
        .input_mode     = AUADC_INPUT_MODE_ADC,
        .data_format    = AUADC_DATA_FORMAT_24BIT,
        .fifo_threshold = 4,
    };
    bflb_auadc_init(auadc, &auadc_cfg);

    // Step 2: Configure analog ADC for DC single-ended measurement at 100 SPS
    struct bflb_auadc_adc_init_config_s adc_cfg = {
        .auadc_analog_en   = true,
        .adc_mode          = AUADC_ADC_MODE_MEASURE,
        .adc_pga_mode      = AUADC_ADC_PGA_MODE_DC_SINGLE,
        .adc_pga_posi_ch   = AUADC_ADC_ANALOG_CH_0,
        .adc_pga_nega_ch   = 0,
        .adc_pga_gain      = 6,    // 6 dB (minimum)
        .adc_measure_rate  = AUADC_ADC_MEASURE_RATE_SPS_100,
    };
    bflb_auadc_adc_init(auadc, &adc_cfg);

    // Step 3: Enable interrupts for FIFO available
    bflb_auadc_int_unmask(auadc, AUADC_INTMASK_FIFO_AVAILABLE);

    // Step 4: Start recording
    bflb_auadc_feature_control(auadc, AUADC_CMD_RECORD_START, 0);

    // Step 5: Read measurement data in interrupt handler
    while (1) {
        int status = bflb_auadc_get_intstatus(auadc);
        if (status & AUADC_INTSTS_FIFO_AVAILABLE) {
            int fifo_cnt = bflb_auadc_feature_control(auadc, AUADC_CMD_GET_RX_FIFO_CNT, 0);
            // Read data from FIFO...
        }
    }
}
```

### Example 4: Interrupt-Driven PDM Recording

```c
#include "bflb_auadc.h"
#include "bflb_irq.h"

void auadc_interrupt_example(void)
{
    struct bflb_device_s *auadc;

    auadc = bflb_device_get_by_name("auadc");

    // Initialize AUADC for PDM right channel, 48 kHz, 32-bit
    struct bflb_auadc_init_config_s cfg = {
        .sampling_rate = AUADC_SAMPLING_RATE_48K,
        .input_mode    = AUADC_INPUT_MODE_PDM_R,
        .data_format   = AUADC_DATA_FORMAT_32BIT,
        .fifo_threshold = 2,
    };
    bflb_auadc_init(auadc, &cfg);

    // Enable FIFO available and overflow interrupts
    bflb_auadc_int_unmask(auadc,
        AUADC_INTMASK_FIFO_AVAILABLE | AUADC_INTMASK_FIFO_OVER);

    // Start recording
    bflb_auadc_feature_control(auadc, AUADC_CMD_RECORD_START, 0);
}

// AUADC interrupt handler
void auadc_irq_handler(void)
{
    struct bflb_device_s *auadc = bflb_device_get_by_name("auadc");
    int status = bflb_auadc_get_intstatus(auadc);

    if (status & AUADC_INTSTS_FIFO_OVER) {
        // Handle overflow - clear FIFO and restart
        bflb_auadc_feature_control(auadc, AUADC_CMD_CLEAR_RX_FIFO, 0);
    }

    if (status & AUADC_INTSTS_FIFO_AVAILABLE) {
        int fifo_cnt = bflb_auadc_feature_control(auadc, AUADC_CMD_GET_RX_FIFO_CNT, 0);
        // Process available data...
    }
}
```

### Example 5: Dynamic Volume Control

```c
void set_auadc_volume(struct bflb_device_s *auadc, float gain_db)
{
    // Volume range: -95.5 dB to +18 dB, 0.5 dB step
    // arg = gain_db * 2 (e.g., 3 dB → arg=6, -6 dB → arg=-12)

    int16_t volume_val = (int16_t)(gain_db * 2.0f);

    // Clamp to valid range
    if (volume_val > 36)  volume_val = 36;   // +18 dB max
    if (volume_val < -191) volume_val = -191; // -95.5 dB min

    bflb_auadc_feature_control(auadc, AUADC_CMD_SET_VOLUME_VAL, (size_t)volume_val);
}
```

---

## Register-Level Reference

The AUADC register block consists of several sub-blocks:

### Register Map

| Offset | Name | Description |
|--------|------|-------------|
| `0x00` | `AUDPDM_TOP` | Clock enable, ADC rate, interface invert |
| `0x04` | `AUDPDM_ITF` | ADC channel enable, DMA interface enable |
| `0x08` | `PDM_ADC_0` | PDM ADC channel 0 FIR mode |
| `0x0C` | `PDM_ADC_1` | PDM ADC channel 0 K1/K2 filter coefficients |
| `0x10` | `PDM_DAC_0` | PDM H/L filter, ADC source select |
| `0x1C` | `PDM_PDM_0` | PDM enable, PDM channel select |
| `0x38` | `PDM_ADC_S0` | Digital volume control |
| `0x60` | `AUDADC_ANA_CFG1` | Analog ADC config 1: PGA chop, noise, bias current |
| `0x64` | `AUDADC_ANA_CFG2` | Analog ADC config 2: dither, quantization, integrator |
| `0x68` | `AUDADC_CMD` | ADC command: measurement rate, PGA gain/mode, channels, conversion |
| `0x6C` | `AUDADC_DATA` | Raw data, data ready, soft reset |
| `0x80` | `AUDADC_RX_FIFO_CTRL` | RX FIFO control: flush, interrupts, DMA, threshold, data format |
| `0x84` | `AUDADC_RX_FIFO_STATUS` | RX FIFO status: interrupts, data count |
| `0x88` | `AUDADC_RX_FIFO_DATA` | RX FIFO data read port |

### Key Register Details

#### AUDPDM_TOP (Offset `0x00`)

| Bits | Field | Description |
|------|-------|-------------|
| 0 | `AUDIO_CKG_EN` | Audio clock enable |
| 2 | `ADC_ITF_INV_SEL` | ADC interface invert select |
| 3 | `PDM_ITF_INV_SEL` | PDM interface invert select |
| 28-31 | `ADC_RATE` | ADC sampling rate select |

#### AUDPDM_ITF (Offset `0x04`)

| Bits | Field | Description |
|------|-------|-------------|
| 0 | `ADC_0_EN` | ADC channel 0 enable |
| 30 | `ADC_ITF_EN` | ADC DMA interface enable |

#### PDM_DAC_0 (Offset `0x10`)

| Bits | Field | Description |
|------|-------|-------------|
| 0-3 | `ADC_PDM_H` | PDM H value |
| 6-9 | `ADC_PDM_L` | PDM L value |
| 12 | `ADC_0_SRC` | ADC channel 0 source select (0=analog ADC, 1=PDM) |

#### PDM_PDM_0 (Offset `0x1C`)

| Bits | Field | Description |
|------|-------|-------------|
| 0 | `PDM_0_EN` | PDM channel 0 enable |
| 3-5 | `ADC_0_PDM_SEL` | PDM channel select (0=L, 1=R) |

#### PDM_ADC_S0 (Offset `0x38`)

| Bits | Field | Description |
|------|-------|-------------|
| 0-8 | `ADC_S0_VOLUME` | Digital volume (0.5 dB steps, -191 to +36) |

#### AUDADC_CMD (Offset `0x68`)

| Bits | Field | Description |
|------|-------|-------------|
| 0-3 | `MEAS_ODR_SEL` | Measurement mode output data rate |
| 4 | `MEAS_FILTER_TYPE` | Measurement filter type |
| 5 | `MEAS_FILTER_EN` | Measurement filter enable |
| 6 | `AUDIO_OSR_SEL` | Audio OSR select (0=128, 1=64) |
| 8-11 | `PGA_GAIN` | PGA gain (value = gain_dB / 3) |
| 12-13 | `PGA_MODE` | PGA mode (0=AC diff, 1=AC single, 2=DC diff, 3=DC single) |
| 16-18 | `CHANNEL_SELN` | Negative channel select |
| 20-22 | `CHANNEL_SELP` | Positive channel select |
| 24-25 | `CHANNEL_EN` | Channel enable (2=single, 3=differential) |
| 28 | `CONV` | SDM conversion start |
| 29 | `SDM_PU` | SDM power up |
| 30 | `PGA_PU` | PGA power up |

#### AUDADC_RX_FIFO_CTRL (Offset `0x80`)

| Bits | Field | Description |
|------|-------|-------------|
| 0 | `RX_FIFO_FLUSH` | Write 1 to flush RX FIFO |
| 1 | `RXO_INT_EN` | RX overflow interrupt enable |
| 2 | `RXU_INT_EN` | RX underflow interrupt enable |
| 3 | `RXA_INT_EN` | RX available interrupt enable |
| 4 | `RX_DRQ_EN` | RX DMA request enable |
| 5-6 | `RX_DATA_RES` | RX data resolution (2=24-bit) |
| 8 | `RX_CH_EN` | RX channel enable (record start/stop) |
| 14-15 | `RX_DRQ_CNT` | RX DMA request count |
| 16-19 | `RX_TRG_LEVEL` | RX FIFO trigger level |
| 24-25 | `RX_DATA_MODE` | RX data format (0=32-bit, 1=24-bit, 2=20-bit, 3=16-bit) |

#### AUDADC_RX_FIFO_STATUS (Offset `0x84`)

| Bits | Field | Description |
|------|-------|-------------|
| 1 | `RXO_INT` | RX overflow interrupt flag |
| 2 | `RXU_INT` | RX underflow interrupt flag |
| 4 | `RXA_INT` | RX available interrupt flag |
| 16-19 | `RXA_CNT` | RX FIFO available data count |
| 24 | `RXA` | RX FIFO data available |

### Direct Register Access Example

```c
#include "hardware/auadc_reg.h"

// Assuming AUADC_BASE is defined for your chip
void auadc_direct_start_record(uint32_t auadc_base)
{
    uint32_t regval;

    // Enable channel recording
    regval = getreg32(auadc_base + AUADC_AUDADC_RX_FIFO_CTRL_OFFSET);
    regval |= AUADC_RX_CH_EN;
    putreg32(regval, auadc_base + AUADC_AUDADC_RX_FIFO_CTRL_OFFSET);
}

void auadc_direct_read_volume(uint32_t auadc_base)
{
    uint32_t regval;

    regval = getreg32(auadc_base + AUADC_PDM_ADC_S0_OFFSET);
    uint32_t raw_volume = (regval & AUADC_ADC_S0_VOLUME_MASK) >> AUADC_ADC_S0_VOLUME_SHIFT;

    // Convert to dB: value / 2 (0.5 dB steps)
    // For signed interpretation: raw_volume is treated as signed 10-bit in the register
    float gain_db = (float)((int16_t)(raw_volume << 6) >> 6) / 2.0f;
}
```

---

## Initialization Sequence Summary

The typical AUADC initialization sequence for audio recording:

1. **`bflb_auadc_init()`** — Configure clock, sampling rate, input mode, data format, FIFO
2. **`bflb_auadc_adc_init()`** — *(Analog ADC only)* Configure PGA, channels, gain, mode
3. **`bflb_auadc_feature_control()`** with `AUADC_CMD_SET_VOLUME_VAL` — Set digital volume
4. **`bflb_auadc_link_rxdma()`** — Enable DMA transfer
5. **`bflb_auadc_int_unmask()`** — *(Optional)* Enable interrupts
6. **`bflb_auadc_feature_control()`** with `AUADC_CMD_RECORD_START` — Start capturing

To stop: **`bflb_auadc_feature_control()`** with `AUADC_CMD_RECORD_STOP`.

---

## Chip Differences

| Feature | BL616 | BL618DG | BL616CL | BL702L |
|---------|-------|---------|---------|--------|
| AUADC Base Address | `0x2000AC00` | `0x20017C00` | `0x2000AC00` | `0x4000AD00` |
| Analog ADC Support | ✅ Yes | ✅ Yes | ❌ No (PDM only) | ✅ Yes |
| `bflb_auadc_adc_init()` | ✅ Available | ✅ Available | ❌ Not available | ✅ Available |
| `AUADC_CMD_SET_PGA_GAIN_VAL` | ✅ Available | ✅ Available | ❌ Not available | ✅ Available |
