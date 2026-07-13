# BL616/BL618 Touch/Capacitive Key Driver

## Overview

The BL616/BL618 provides a Touch V2 controller with up to **16 capacitive touch channels** supporting self-capacitance mode. The driver is available in two versions:

- **bflb_touch_v2** (recommended) - Newer driver with 16 channels, frequency hopping, active shielding
- **bflb_touch** (legacy) - Older driver with 12 channels

## Header Files

```c
#include "bflb_touch_v2.h"    // Recommended - Touch V2 driver
#include "bflb_touch.h"        // Legacy driver
#include "touch_v2_reg.h"     // Register definitions
```

## Base Address

The TOUCH peripheral base address is not explicitly defined as `TOUCH_BASE` in bl616.h. Instead, the touch device is accessed via the BFLB device framework:

```c
struct bflb_device_s *touch = bflb_device_get_by_name("touch");
uint32_t reg_base = touch->reg_base;  // Actual base address
```

Register offsets are relative to this base (e.g., `TOUCH_CTRL_0_OFFSET = 0x600`).

## Key Enumerations

### Clock Source (TOUCH_V2_CLK_SEL)
```c
#define TOUCH_V2_CLK_SEL_32K    (0)   // 32KHz clock
#define TOUCH_V2_CLK_SEL_32M    (1)   // 32MHz clock
```

### Clock Divider (TOUCH_V2_CLK_DIV)
```c
#define TOUCH_V2_CLK_DIV_8      (0)
#define TOUCH_V2_CLK_DIV_16     (1)
#define TOUCH_V2_CLK_DIV_32     (2)
#define TOUCH_V2_CLK_DIV_64     (3)
#define TOUCH_V2_CLK_DIV_128    (4)
#define TOUCH_V2_CLK_DIV_256    (5)
#define TOUCH_V2_CLK_DIV_512    (6)
#define TOUCH_V2_CLK_DIV_1024   (7)
```

### Channels (TOUCH_V2_CHANNEL)
```c
#define TOUCH_V2_CHANNEL_0      (0)
#define TOUCH_V2_CHANNEL_1      (1)
...
#define TOUCH_V2_CHANNEL_15     (15)
#define TOUCH_V2_CHANNEL_MAX    (16)
```

### Interrupt Status (TOUCH_V2_INT_STATUS)
```c
#define TOUCH_V2_INT_DET_MASK        (0xFFFF << 0)   // Touch detection interrupt
#define TOUCH_V2_INT_SCAN_LAST_MASK  (1 << 16)        // Last channel scan interrupt
#define TOUCH_V2_INT_HOP_FREQ_0_MASK (1 << 17)        // Frequency hopping interrupt 0
#define TOUCH_V2_INT_HOP_FREQ_1_MASK (1 << 18)        // Frequency hopping interrupt 1
```

## Configuration Structure

```c
struct bflb_touch_v2_config_s {
    uint8_t clk_sel;          // Clock source: TOUCH_V2_CLK_SEL_32K or TOUCH_V2_CLK_SEL_32M
    uint8_t clk_div;          // Clock divider: TOUCH_V2_CLK_DIV_8 ~ TOUCH_V2_CLK_DIV_1024
    uint8_t vref_sel;         // Reference voltage: TOUCH_V2_VREF_0P4V ~ TOUCH_V2_VREF_1P8V
    uint8_t vldo_sel;         // LDO voltage: TOUCH_V2_VLDO_0P6V ~ TOUCH_V2_VLDO_2P1V
    uint8_t hys_sel;          // Hysteresis: TOUCH_V2_HYS_22MV or TOUCH_V2_HYS_65MV
    uint8_t pcharge_low;      // Pcharge low time
    uint8_t pcharge_high;     // Pcharge high time
    uint8_t ldo_settle_cyc;   // LDO settle cycles
    uint8_t filter_order;     // Filter order
    uint8_t filter_sel;       // Filter type: TOUCH_V2_FILTER_IIR or TOUCH_V2_FILTER_FIR
    uint8_t lta_order;        // LTA order
    uint8_t lta_sel;          // LTA type
    uint8_t scn_lst_chl_cnt;  // Last channel scan count
    uint32_t sleep_cycle;     // Sleep cycles in continuous mode
    uint16_t tx_channel_en;   // TX channel enable bitmap
    uint16_t rx_channel_en;   // RX channel enable bitmap
    uint16_t as_channel_sel;  // Active shielding channel selection
    uint16_t det_int_mask;    // Detection interrupt mask
    uint8_t scan_int_mask;    // Scan last interrupt mask
    uint8_t hop_int_mask;     // Frequency hopping interrupt mask
    uint16_t det_dur;         // Touch detection duration
    bool touch_32m_clk_sel;   // true: xtal clock, false: rc clock
    bool cont_mode_en;        // Continuous mode enable
    bool wakeup_mode_en;      // Ultra low power wakeup mode 2
    bool as_chl_sel;          // Active shielding channel select
    bool det_on;              // Detection mode: true=on to off, false=off to on
    bool det_keep;            // Keep touch status when scanning again
    bool data_hys_en;         // Hysteresis time enable
    bool force_val_en;        // Force enable
    bool channel_cal_en;      // Channel calibration enable
    bool filter_en;           // Filter enable
    bool lta_en;              // LTA enable
    bool hop_freq_en;         // Frequency hopping enable
    uint8_t hop_freq_th;      // Frequency hopping threshold
    uint8_t hop_freq_div0;    // First scan clock div
    uint8_t hop_freq_div1;    // Second scan clock div
    uint8_t hop_freq_div2;    // Third scan clock div
};
```

## Channel Data Structure

```c
struct bflb_touch_v2_channel_data_s {
    uint16_t raw_data;    // Raw touch data
    uint16_t flt_data;    // Filtered touch data
    uint16_t lta_data;    // Long time average data
    uint16_t force_data;  // Force data
    uint8_t vth_data;     // Threshold data
    uint8_t hys_data;     // Hysteresis data
};
```

## API Functions

### Initialization

```c
int bflb_touch_v2_init(struct bflb_device_s *dev, const struct bflb_touch_v2_config_s *config);
```
Initialize touch V2 with configuration. Returns 0 on success.

```c
void bflb_touch_v2_deinit(struct bflb_device_s *dev);
```
Deinitialize touch V2, performs reset and disables module.

### Enable/Disable

```c
void bflb_touch_v2_enable(struct bflb_device_s *dev);
void bflb_touch_v2_disable(struct bflb_device_s *dev);
```

### Scanning

```c
void bflb_touch_v2_scan_start(struct bflb_device_s *dev);
void bflb_touch_v2_scan_stop(struct bflb_device_s *dev);
```

### Data Access

```c
uint16_t bflb_touch_v2_get_raw_data(struct bflb_device_s *dev, uint8_t channel);
uint16_t bflb_touch_v2_get_flt_data(struct bflb_device_s *dev, uint8_t channel);
uint16_t bflb_touch_v2_get_lta_data(struct bflb_device_s *dev, uint8_t channel);
void bflb_touch_v2_get_channel_data(struct bflb_device_s *dev, uint8_t channel, 
                                     struct bflb_touch_v2_channel_data_s *data);
```

### Channel Configuration

```c
void bflb_touch_v2_set_channel_threshold(struct bflb_device_s *dev, uint8_t channel, 
                                          uint8_t threshold);
void bflb_touch_v2_set_channel_hysteresis(struct bflb_device_s *dev, uint8_t channel, 
                                           uint8_t hys);
void bflb_touch_v2_set_channel_force_data(struct bflb_device_s *dev, uint8_t channel, 
                                           uint16_t force_data);
void bflb_touch_v2_latch_force_data(struct bflb_device_s *dev);
```

### Interrupt Handling

```c
uint32_t bflb_touch_v2_get_int_status(struct bflb_device_s *dev);
void bflb_touch_v2_clear_int(struct bflb_device_s *dev, uint32_t int_mask);
void bflb_touch_v2_set_int_mask(struct bflb_device_s *dev, uint32_t int_mask);
```

### Frequency Hopping

```c
void bflb_touch_v2_config_freq_hopping(struct bflb_device_s *dev, bool enable,
                                        uint8_t threshold, uint8_t div0, 
                                        uint8_t div1, uint8_t div2);
```

### Detection Settings

```c
void bflb_touch_v2_set_detection_duration(struct bflb_device_s *dev, uint16_t duration);
void bflb_touch_v2_set_sleep_cycle(struct bflb_device_s *dev, uint32_t sleep_cycle);
```

### Channel Enable

```c
void bflb_touch_v2_set_tx_channel(struct bflb_device_s *dev, uint16_t channels);
void bflb_touch_v2_set_rx_channel(struct bflb_device_s *dev, uint16_t channels);
```

## Register Map (Touch V2)

Base offset `0x600` from device reg_base:

| Offset | Register | Description |
|--------|----------|-------------|
| 0x600 | TOUCH_CTRL_0 | Control 0: enable, clock, scan |
| 0x604 | TOUCH_CTRL_1 | Control 1: interrupts, filter, LTA |
| 0x608 | TOUCH_INT_STS | Interrupt status |
| 0x60C | TOUCH_CHL_CFG | Channel configuration |
| 0x610 | TOUCH_CTRL_2 | Control 2: sleep, pcharge |
| 0x614-0x630 | TOUCH_FORCE_DAT_XX | Force data (pairs) |
| 0x634-0x638 | TOUCH_HYS_DAT_XX | Hysteresis data |
| 0x63C-0x648 | TOUCH_VTH_DAT_XX | Threshold data |
| 0x64C-0x668 | TOUCH_RAW_DAT_XX | Raw data (read-only) |
| 0x66C-0x688 | TOUCH_FLT_DAT_XX | Filtered data (read-only) |
| 0x68C-0x6A8 | TOUCH_LTA_DAT_XX | LTA data (read-only) |
| 0x6A8 | TOUCH_INT_CLR | Interrupt clear |
| 0x6B0 | TOUCH_HOP_FREQ_CFG | Frequency hopping config |
| 0x6B4 | TOUCH_DET_DUR | Detection duration |

## Working Code Example

```c
#include "bflb_touch_v2.h"
#include "bflb_device.h"
#include "bflb_clock.h"
#include "bflb_irq.h"

static struct bflb_device_s *touch;

void touch_isr(int irq, void *arg)
{
    uint32_t int_status = bflb_touch_v2_get_int_status(touch);
    printf("Touch int status=%08x\r\n", int_status);
    
    if (int_status & TOUCH_V2_INT_DET_MASK) {
        // Check which channels detected
        uint16_t ch_detected = int_status & 0xFFFF;
        for (int i = 0; i < 16; i++) {
            if (ch_detected & (1 << i)) {
                printf("Channel %d touched\r\n", i);
            }
        }
    }
    
    bflb_touch_v2_clear_int(touch, int_status);
}

void touch_init_example(void)
{
    struct bflb_touch_v2_config_s config = {
        .clk_sel = TOUCH_V2_CLK_SEL_32M,
        .clk_div = TOUCH_V2_CLK_DIV_16,
        .vref_sel = TOUCH_V2_VREF_1P4V,
        .vldo_sel = TOUCH_V2_VLDO_1P8V,
        .hys_sel = TOUCH_V2_HYS_22MV,
        .pcharge_low = TOUCH_V2_PCHARGE_LOW_127,
        .pcharge_high = TOUCH_V2_PCHARGE_HIGH_4095,
        .ldo_settle_cyc = TOUCH_V2_LDO_SETTLE_80,
        .filter_order = TOUCH_V2_FILTER_ORDER_2,
        .filter_sel = TOUCH_V2_FILTER_IIR,
        .lta_order = TOUCH_V2_LTA_ORDER_4,
        .lta_sel = TOUCH_V2_FILTER_IIR,
        .scn_lst_chl_cnt = 0,
        .sleep_cycle = 0,
        .tx_channel_en = 0x0003,    // Channels 0-1 TX enabled
        .rx_channel_en = 0x0003,    // Channels 0-1 RX enabled
        .as_channel_sel = 0,
        .det_int_mask = 0x0003,     // Interrupt enabled for channels 0-1
        .scan_int_mask = 0,
        .hop_int_mask = 0,
        .det_dur = 10,
        .touch_32m_clk_sel = false,
        .cont_mode_en = true,
        .wakeup_mode_en = false,
        .as_chl_sel = false,
        .det_on = true,             // On to off detection
        .det_keep = false,
        .data_hys_en = true,
        .force_val_en = false,
        .channel_cal_en = true,
        .filter_en = true,
        .lta_en = true,
        .hop_freq_en = false,
        .hop_freq_th = 0,
        .hop_freq_div0 = 0,
        .hop_freq_div1 = 0,
        .hop_freq_div2 = 0,
    };
    
    // Get touch device handle
    touch = bflb_device_get_by_name("touch");
    if (touch == NULL) {
        printf("Touch device not found\r\n");
        return;
    }
    
    // Initialize touch
    bflb_touch_v2_init(touch, &config);
    
    // Set thresholds for channels
    bflb_touch_v2_set_channel_threshold(touch, 0, 50);
    bflb_touch_v2_set_channel_threshold(touch, 1, 50);
    
    // Set hysteresis
    bflb_touch_v2_set_channel_hysteresis(touch, 0, 5);
    bflb_touch_v2_set_channel_hysteresis(touch, 1, 5);
    
    // Register interrupt
    bflb_irq_attach(touch->irq_num, touch_isr, NULL);
    bflb_irq_enable(touch->irq_num);
    
    // Enable touch
    bflb_touch_v2_enable(touch);
}

void touch_polling_example(void)
{
    touch_init_example();
    
    while (1) {
        // Poll raw data
        for (int ch = 0; ch < 2; ch++) {
            uint16_t raw = bflb_touch_v2_get_raw_data(touch, ch);
            uint16_t flt = bflb_touch_v2_get_flt_data(touch, ch);
            uint16_t lta = bflb_touch_v2_get_lta_data(touch, ch);
            printf("CH%d: raw=%d flt=%d lta=%d\r\n", ch, raw, flt, lta);
        }
        bflb_mtimer_delay_ms(100);
    }
}
```

## Register-Level Programming

### Direct Register Access Pattern

```c
uint32_t reg_base = touch->reg_base;

// Write to control register
putreg32(regval, reg_base + TOUCH_CTRL_0_OFFSET);

// Read from status register
regval = getreg32(reg_base + TOUCH_INT_STS_OFFSET);

// Example: Enable touch and start scanning
uint32_t regval = getreg32(reg_base + TOUCH_CTRL_0_OFFSET);
regval |= TOUCH_EN;      // Enable touch
regval |= TOUCH_SCN_EN;  // Start scanning
putreg32(regval, reg_base + TOUCH_CTRL_0_OFFSET);
```

### Key Register Bit Definitions

```c
// TOUCH_CTRL_0 (0x600)
#define TOUCH_EN              (1 << 4)
#define TOUCH_SCN_EN          (1 << 5)
#define TOUCH_CLK_SEL         (1 << 0)    // 0=32K, 1=32M
#define TOUCH_CLK_DIV_RATIO_SHIFT (1)
#define TOUCH_HYS_SEL         (1 << 19)

// TOUCH_CTRL_1 (0x604)
#define TOUCH_DET_INT_MASK_SHIFT (0)
#define TOUCH_FLT_EN          (1 << 29)
#define TOUCH_LTA_EN          (1 << 25)
#define TOUCH_SWRST           (1 << 31)

// TOUCH_INT_STS (0x608)
#define TOUCH_DET_INT_SHIFT   (0)
#define TOUCH_DET_INT_MASK    (0xFFFF << 0)

// TOUCH_CHL_CFG (0x60C)
#define TOUCH_CH_RX_EN_SHIFT  (16)
#define TOUCH_CH_TX_EN_SHIFT  (24)
```

## Legacy Touch API (bflb_touch.h)

For BL616/BL618 with 12 channels:

```c
// Initialization
int bflb_touch_init(struct bflb_device_s *dev, const struct bflb_touch_config_s *config);
int bflb_touch_channel_init(struct bflb_device_s *dev, 
                            const struct bflb_touch_chan_config_s *config, 
                            uint8_t lp_chan_sel);

// Enable/Disable
void bflb_touch_enable(struct bflb_device_s *dev);
void bflb_touch_disable(struct bflb_device_s *dev);

// Data access
uint32_t bflb_touch_get_raw_data(struct bflb_device_s *dev, uint8_t channel);
uint32_t bflb_touch_get_lta_data(struct bflb_device_s *dev, uint8_t channel);
uint32_t bflb_touch_get_flt_data(struct bflb_device_s *dev, uint8_t channel);

// Threshold
void bflb_touch_set_vth_data(struct bflb_device_s *dev, uint8_t channel, uint32_t vth);
uint32_t bflb_touch_get_vth_data(struct bflb_device_s *dev, uint8_t channel);

// Status
bool bflb_touch_get_end_status(struct bflb_device_s *dev);
```

## Notes

- Touch V2 supports up to **16 channels** (0-15)
- Touch legacy supports **12 channels** (0-11)
- Channel scan order: TX channels first, then RX channels
- Detection works by comparing filtered data against LTA with threshold/hysteresis
- For best results, run calibration first with `cal_en=1` to establish baseline LTA values
- Frequency hopping can improve noise immunity in hostile RF environments
