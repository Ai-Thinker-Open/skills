# AUDAC (Audio DAC) Driver Documentation

## Overview

The AUDAC (Audio DAC) is a digital-to-analog converter peripheral in the BL616/BL618 chip. It supports multiple output modes including PWM and GPDAC, with DMA support for audio playback.

**Base Address:** `AUDAC_BASE` = `0x20055000`

---

## Header Files

```c
#include "bflb_audac.h"              // Main driver API
#include "hardware/audac_reg.h"      // Register definitions
```

---

## Register Map

| Offset | Register | Description |
|--------|----------|-------------|
| `0x000` | `AUDAC_0` | Control register 0 (enable, clock, mode) |
| `0x004` | `AUDAC_STATUS` | Status register (busy, mute done, interrupts) |
| `0x008` | `AUDAC_S0` | Volume and mute control |
| `0x00C` | `AUDAC_S0_MISC` | Zero-crossing timeout |
| `0x010` | `AUDAC_ZD_0` | Zero deletion configuration |
| `0x014` | `AUDAC_1` | Mixer and DSM configuration |
| `0x018` | `AUDAC_RSVD` | Reserved |
| `0x01C` | `AUDAC_TEST_0` | Test data input |
| `0x020` | `AUDAC_TEST_1` | FIR coefficient |
| `0x024` | `AUDAC_TEST_2` | Sinc coefficient |
| `0x028` | `AUDAC_TEST_3` | PWM test read |
| `0x08C` | `AUDAC_FIFO_CTRL` | FIFO control (DMA, threshold, int) |
| `0x090` | `AUDAC_FIFO_STATUS` | FIFO status |
| `0x094` | `AUDAC_FIFO_DATA` | TX FIFO data port |

---

## Key Register Bitfields

### AUDAC_0 (0x000)
- `AUDAC_DAC_0_EN` (bit 0): DAC channel 0 enable
- `AUDAC_DAC_ITF_EN` (bit 1): DAC interface enable
- `AUDAC_CKG_ENA` (bit 27): Clock gate enable
- `AUDAC_AU_PWM_MODE_SHIFT` (bits 28-31): Output mode and sampling rate

### AUDAC_S0 (0x008)
- `AUDAC_DAC_S0_CTRL_RMP_RATE_SHIFT` (bits 2-5): Volume ramp rate
- `AUDAC_DAC_S0_CTRL_ZCD_RATE_SHIFT` (bits 6-9): Zero-crossing detect rate
- `AUDAC_DAC_S0_CTRL_MODE_SHIFT` (bits 10-11): Volume update mode
- `AUDAC_DAC_S0_VOLUME_UPDATE` (bit 12): Volume update trigger
- `AUDAC_DAC_S0_VOLUME_SHIFT` (bits 13-21): Volume value (9 bits, 0.5dB step)
- `AUDAC_DAC_S0_MUTE` (bit 31): Mute control

### AUDAC_FIFO_CTRL (0x08C)
- `AUDAC_TX_FIFO_FLUSH` (bit 0): FIFO flush
- `AUDAC_TXO_INT_EN` (bit 1): FIFO overflow interrupt enable
- `AUDAC_TXU_INT_EN` (bit 2): FIFO underflow interrupt enable
- `AUDAC_TXA_INT_EN` (bit 3): FIFO available interrupt enable
- `AUDAC_TX_DRQ_EN` (bit 4): DMA request enable
- `AUDAC_TX_CH_EN_SHIFT` (bits 8-9): TX channel enable
- `AUDAC_TX_TRG_LEVEL_SHIFT` (bits 16-20): FIFO threshold trigger level

---

## Configuration Constants

### Sampling Rates
```c
AUDAC_SAMPLING_RATE_8K      0
AUDAC_SAMPLING_RATE_16K     1
AUDAC_SAMPLING_RATE_22P05K  5
AUDAC_SAMPLING_RATE_24K     3
AUDAC_SAMPLING_RATE_32K     2
AUDAC_SAMPLING_RATE_44P1K   6
AUDAC_SAMPLING_RATE_48K     4
```

### Output Modes
```c
AUDAC_OUTPUT_MODE_PWM          0   // PWM output only
AUDAC_OUTPUT_MODE_GPDAC_CH_A   1   // GPDAC Channel A
AUDAC_OUTPUT_MODE_GPDAC_CH_B   2   // GPDAC Channel B
AUDAC_OUTPUT_MODE_GPDAC_CH_A_B 3   // GPDAC Channels A + B
```

### Source Channels
```c
AUDAC_SOURCE_CHANNEL_SINGLE  0x01  // Single channel (mono)
AUDAC_SOURCE_CHANNEL_DUAL    0x03  // Dual channel (stereo)
```

### Mixer Modes (Dual channel only)
```c
AUDAC_MIXER_MODE_ONLY_L    0   // Left channel only
AUDAC_MIXER_MODE_ONLY_R    1   // Right channel only
AUDAC_MIXER_MODE_SUM       2   // Sum L+R
AUDAC_MIXER_MODE_AVERAGE   3   // Average (L+R)/2
```

### Data Formats
```c
AUDAC_DATA_FORMAT_16BIT    3
AUDAC_DATA_FORMAT_20BIT    2
AUDAC_DATA_FORMAT_24BIT    1
AUDAC_DATA_FORMAT_32BIT    0
```

### Volume Ramp Rates
```c
AUDAC_RAMP_RATE_FS_2      0
AUDAC_RAMP_RATE_FS_4      1
AUDAC_RAMP_RATE_FS_8      2
AUDAC_RAMP_RATE_FS_16     3
AUDAC_RAMP_RATE_FS_32     4
AUDAC_RAMP_RATE_FS_64     5
AUDAC_RAMP_RATE_FS_128    6
AUDAC_RAMP_RATE_FS_256    7
AUDAC_RAMP_RATE_FS_512    8
AUDAC_RAMP_RATE_FS_1024   9
AUDAC_RAMP_RATE_FS_2048   10
```

### Volume Update Modes
```c
AUDAC_VOLUME_UPDATE_MODE_FORCE             0  // Immediate update
AUDAC_VOLUME_UPDATE_MODE_RAMP               1  // Ramp to new value
AUDAC_VOLUME_UPDATE_MODE_RAMP_ZERO_CROSSING 2  // Ramp with zero-crossing detection
```

### Interrupt Status Flags
```c
AUDAC_INTSTS_VOLUME_RAMP      (1 << 0)  // Volume ramp done
AUDAC_INTSTS_FIFO_OVER        (1 << 1)  // FIFO overflow
AUDAC_INTSTS_FIFO_UNDER       (1 << 2)  // FIFO underflow
AUDAC_INTSTS_FIFO_AVAILABLE   (1 << 3)  // FIFO data available
```

### Feature Control Commands
```c
AUDAC_CMD_PLAY_START       0x01  // Start playback
AUDAC_CMD_PLAY_STOP        0x02  // Stop playback
AUDAC_CMD_SET_MUTE         0x03  // Set mute (arg: true/false)
AUDAC_CMD_SET_VOLUME_VAL   0x04  // Set volume (arg: -191 to +36, 0.5dB steps)
AUDAC_CMD_CLEAR_TX_FIFO    0x05  // Clear TX FIFO
AUDAC_CMD_GET_TX_FIFO_CNT  0x06  // Get FIFO count
```

---

## Data Structures

### Initialization Configuration
```c
struct bflb_audac_init_config_s {
    uint8_t sampling_rate;        // @ref AUDAC_SAMPLING_RATE
    uint8_t output_mode;          // @ref AUDAC_OUTPUT_MODE
    uint8_t source_channels_num;  // @ref AUDAC_SOURCE_CHANNEL
    uint8_t mixer_mode;           // @ref AUDAC_MIXER_MODE
    uint8_t data_format;          // @ref AUDAC_DATA_FORMAT
    uint8_t fifo_threshold;       // 0 ~ 7
};
```

### Volume Configuration
```c
struct bflb_audac_volume_config_s {
    bool mute_ramp_en;                 // Enable mute ramp
    uint8_t mute_up_ramp_rate;        // @ref AUDAC_RAMP_RATE
    uint8_t mute_down_ramp_rate;      // @ref AUDAC_RAMP_RATE
    uint8_t volume_update_mode;       // @ref AUDAC_VOLUME_UPDATE_MODE
    uint8_t volume_ramp_rate;         // @ref AUDAC_RAMP_RATE
    uint8_t volume_zero_cross_timeout;// Zero-cross timeout period
};
```

---

## API Functions

### `bflb_audac_init`
```c
int bflb_audac_init(struct bflb_device_s *dev, const struct bflb_audac_init_config_s *config);
```
Initialize the AUDAC peripheral with sampling rate, output mode, channel configuration, and data format.

### `bflb_audac_volume_init`
```c
int bflb_audac_volume_init(struct bflb_device_s *dev, const struct bflb_audac_volume_config_s *vol_cfg);
```
Configure volume control including mute ramp, update mode, and ramp rates.

### `bflb_audac_link_rxdma`
```c
int bflb_audac_link_rxdma(struct bflb_device_s *dev, bool enable);
```
Enable or disable DMA mode for audio data transfer.

### `bflb_audac_feature_control`
```c
int bflb_audac_feature_control(struct bflb_device_s *dev, int cmd, size_t arg);
```
Send commands to control playback, mute, volume, and FIFO operations.

### Interrupt Functions
```c
int bflb_audac_int_mask(struct bflb_device_s *dev, uint32_t mask);
int bflb_audac_int_unmask(struct bflb_device_s *dev, uint32_t int_sts);
int bflb_audac_get_intstatus(struct bflb_device_s *dev);
int bflb_audac_int_clear(struct bflb_device_s *dev, uint32_t int_clear);
```

---

## Usage Example

### Basic Initialization and Playback

```c
#include "bflb_audac.h"
#include "bflb_dma.h"
#include "bl616_glb.h"

// Device handles
static struct bflb_device_s *audac;
static struct bflb_device_s *dma;

void audac_example_init(void)
{
    uint32_t val;
    
    // 1. Configure audio PLL and enable clock
    GLB_Config_AUDIO_PLL_To_491P52M();
    GLB_PER_Clock_UnGate(GLB_AHB_CLOCK_AUDIO);
    
    // 2. Initialize AUDAC with PWM output at 16kHz
    struct bflb_audac_init_config_s audac_init_cfg = {
        .sampling_rate = AUDAC_SAMPLING_RATE_16K,
        .output_mode = AUDAC_OUTPUT_MODE_PWM,
        .source_channels_num = AUDAC_SOURCE_CHANNEL_SINGLE,
        .mixer_mode = AUDAC_MIXER_MODE_ONLY_L,
        .data_format = AUDAC_DATA_FORMAT_16BIT,
        .fifo_threshold = 7,
    };
    
    audac = bflb_device_get_by_name("audac");
    bflb_audac_init(audac, &audac_init_cfg);
    
    // 3. Configure volume (-15dB)
    bflb_audac_feature_control(audac, AUDAC_CMD_SET_VOLUME_VAL, (size_t)(-15 * 2));
    
    // 4. Configure volume control
    struct bflb_audac_volume_config_s audac_vol_cfg = {
        .mute_ramp_en = false,
        .mute_up_ramp_rate = AUDAC_RAMP_RATE_FS_32,
        .mute_down_ramp_rate = AUDAC_RAMP_RATE_FS_8,
        .volume_update_mode = AUDAC_VOLUME_UPDATE_MODE_FORCE,
        .volume_ramp_rate = AUDAC_RAMP_RATE_FS_128,
        .volume_zero_cross_timeout = AUDAC_RAMP_RATE_FS_128,
    };
    bflb_audac_volume_init(audac, &audac_vol_cfg);
    
    // 5. Enable DMA mode
    bflb_audac_link_rxdma(audac, true);
    
    // 6. Start playback
    bflb_audac_feature_control(audac, AUDAC_CMD_PLAY_START, 0);
}
```

### DMA Configuration for Audio Playback

```c
#include "bflb_dma.h"

static struct bflb_device_s *dma;
static struct bflb_dma_channel_lli_pool_s dma_lli_pool[FRAME_COUNT];

void audac_dma_init(void)
{
    struct bflb_dma_channel_config_s dma_cfg = {
        .direction = DMA_MEMORY_TO_PERIPH,
        .src_req = DMA_REQUEST_NONE,
        .dst_req = DMA_REQUEST_AUDAC_TX,
        .src_addr_inc = DMA_ADDR_INCREMENT_ENABLE,
        .dst_addr_inc = DMA_ADDR_INCREMENT_DISABLE,
        .src_burst_count = DMA_BURST_INCR8,
        .dst_burst_count = DMA_BURST_INCR8,
        .src_width = DMA_DATA_WIDTH_16BIT,
        .dst_width = DMA_DATA_WIDTH_16BIT,
    };
    
    dma = bflb_device_get_by_name("dma0_ch1");
    bflb_dma_channel_init(dma, &dma_cfg);
    bflb_dma_channel_irq_attach(dma, dma_isr, NULL);
}

void dma_isr(void *arg)
{
    // Handle DMA completion
    // Process next audio buffer
}

// Setup DMA LLI transfer
void audac_dma_start(uint32_t *audio_buffer, uint32_t buffer_size)
{
    dma_lli_pool[0].src_addr = (uint32_t)audio_buffer;
    dma_lli_pool[0].dst_addr = DMA_ADDR_AUDAC_TDR;  // AUDAC TX Data Register
    dma_lli_pool[0].control.bits.TransferSize = buffer_size / 2;
    dma_lli_pool[0].nextlli = 0;
    dma_lli_pool[0].control.bits.I = 1;  // Interrupt on completion
    
    bflb_dma_feature_control(dma, DMA_CMD_SET_LLI_CONFIG, (uint32_t)&dma_lli_pool[0]);
    bflb_dma_channel_start(dma);
}
```

### GPDAC Output Mode Configuration

```c
void audac_gpdac_output_init(void)
{
    struct bflb_audac_init_config_s audac_init_cfg = {
        .sampling_rate = AUDAC_SAMPLING_RATE_48K,
        .output_mode = AUDAC_OUTPUT_MODE_GPDAC_CH_A_B,  // Use both GPDAC channels
        .source_channels_num = AUDAC_SOURCE_CHANNEL_DUAL,
        .mixer_mode = AUDAC_MIXER_MODE_SUM,
        .data_format = AUDAC_DATA_FORMAT_16BIT,
        .fifo_threshold = 3,
    };
    
    audac = bflb_device_get_by_name("audac");
    bflb_audac_init(audac, &audac_init_cfg);
    
    // GPDAC configuration is handled automatically in bflb_audac_init
    // when output_mode != AUDAC_OUTPUT_MODE_PWM
}
```

### Volume Control with Mute

```c
void audac_volume_example(void)
{
    // Set volume to -10dB (value * 2 = -20 for -10dB)
    bflb_audac_feature_control(audac, AUDAC_CMD_SET_VOLUME_VAL, (size_t)(-10 * 2));
    
    // Mute with ramp down
    bflb_audac_feature_control(audac, AUDAC_CMD_SET_MUTE, true);
    
    // Wait for mute ramp to complete
    
    // Unmute with ramp up
    bflb_audac_feature_control(audac, AUDAC_CMD_SET_MUTE, false);
}
```

---

## GPIO Configuration

For PWM output mode, configure GPIO pins:

```c
#include "bflb_gpio.h"

void audac_gpio_init(void)
{
    struct bflb_device_s *gpio;
    gpio = bflb_device_get_by_name("gpio");
    
    // AUDAC PWM output pins
    bflb_gpio_init(gpio, GPIO_PIN_27, GPIO_FUNC_AUDAC_PWM | GPIO_ALTERNATE | GPIO_PULLUP | GPIO_SMT_EN | GPIO_DRV_2);
    bflb_gpio_init(gpio, GPIO_PIN_28, GPIO_FUNC_AUDAC_PWM | GPIO_ALTERNATE | GPIO_PULLUP | GPIO_SMT_EN | GPIO_DRV_2);
    
    // PA enable pins (if used)
    bflb_gpio_init(gpio, GPIO_PIN_25, GPIO_OUTPUT | GPIO_PULLUP | GPIO_SMT_EN | GPIO_DRV_0);
    bflb_gpio_init(gpio, GPIO_PIN_26, GPIO_OUTPUT | GPIO_PULLUP | GPIO_SMT_EN | GPIO_DRV_0);
    bflb_gpio_set(gpio, GPIO_PIN_25);
    bflb_gpio_set(gpio, GPIO_PIN_26);
}
```

---

## DMA Address

The AUDAC TX FIFO data register address for DMA destination:
- `DMA_ADDR_AUDAC_TDR` - TX Data Register address

---

## Volume Calculation

Volume value is encoded as 9 bits (bits 13-21 of `AUDAC_S0`) with 0.5dB steps:
- Range: -191 to +36 (0.5dB steps)
- Effective range: -95.5dB to +18dB
- Formula: `register_value = volume_dB * 2`

Examples:
- 0dB: `0`
- -10dB: `-20`
- -20dB: `-40`
- +6dB: `12`

---

## Notes

1. **Clock Configuration**: Audio PLL must be configured before initializing AUDAC using `GLB_Config_AUDIO_PLL_To_491P52M()`.

2. **DMA Mode**: When DMA is enabled via `bflb_audac_link_rxdma()`, the AUDAC will request data from memory automatically.

3. **GPDAC Mode**: When using GPDAC output modes, the driver automatically configures the GLB registers for GPDAC operation.

4. **FIFO Threshold**: The `fifo_threshold` parameter (0-7) sets when the DMA request or interrupt is triggered based on FIFO fill level.

5. **Zero Deletion**: Enabled by default with time value 512 for handling sample rate conversion artifacts.
