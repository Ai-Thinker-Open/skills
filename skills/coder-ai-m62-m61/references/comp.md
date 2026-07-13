# BL616/BL618 Analog Comparator (ACOMP) Documentation

## Overview

The BL616/BL618 chips include two analog comparators (ACOMP0 and ACOMP1) that can compare an input voltage against a reference threshold and output a digital result.

## Header Files

- **Driver API**: `bouffalo_sdk/drivers/lhal/include/bflb_acomp.h`
- **Register Definitions**: `bouffalo_sdk/drivers/lhal/include/hardware/acomp_reg.h`

## Base Address

```
ACOMP_BASE = 0x2000F000 (BL616/BL616CL)
```

## Register Map

| Offset   | Register         | Description              |
|----------|------------------|--------------------------|
| 0x900    | acomp0_ctrl      | ACOMP0 control           |
| 0x904    | acomp1_ctrl      | ACOMP1 control           |
| 0x908    | acomp_ctrl       | ACOMP shared control    |

---

## Initialization

### Configuration Structure

```c
struct bflb_acomp_config_s {
    uint8_t mux_en;              // MUX enable
    uint8_t pos_chan_sel;        // Positive channel select
    uint8_t neg_chan_sel;        // Negative channel select
    uint8_t vio_sel;             // VIO voltage select
    uint8_t scaling_factor;      // Scaling factor
    uint8_t bias_prog;           // Bias current control
    uint8_t hysteresis_pos_volt; // Hysteresis for positive input
    uint8_t hysteresis_neg_volt; // Hysteresis for negative input
};
```

### Initialize ACOMP

```c
void bflb_acomp_init(uint8_t acomp_id, const struct bflb_acomp_config_s *config);
```

**Parameters**:
- `acomp_id`: `AON_ACOMP0_ID` (0) or `AON_ACOMP1_ID` (1)
- `config`: Pointer to configuration structure

**Example**:
```c
struct bflb_acomp_config_s acomp_cfg = {
    .mux_en = 0,
    .pos_chan_sel = AON_ACOMP_CHAN_ADC0,    // Positive: ADC0
    .neg_chan_sel = AON_ACOMP_CHAN_VREF_1P25V, // Negative: 1.25V ref
    .vio_sel = 0,
    .scaling_factor = AON_ACOMP_SCALING_FACTOR_1,
    .bias_prog = AON_ACOMP_BIAS_POWER_MODE2,
    .hysteresis_pos_volt = AON_ACOMP_HYSTERESIS_VOLT_NONE,
    .hysteresis_neg_volt = AON_ACOMP_HYSTERESIS_VOLT_NONE,
};

bflb_acomp_init(AON_ACOMP0_ID, &acomp_cfg);
```

### Enable/Disable

```c
void bflb_acomp_enable(uint8_t acomp_id);
void bflb_acomp_disable(uint8_t acomp_id);
```

---

## Channel Selection

### Available Channels

| Channel ID          | Description                    |
|---------------------|--------------------------------|
| 0-7                 | ADC channels 0-7               |
| 8                   | DAC channel A                  |
| 9                   | DAC channel B                  |
| 10                  | 1.25V reference voltage        |
| 11-14               | VIO × scaling factor (1-4)     |
| 15                  | VSS (ground)                   |

### Channel Definitions

```c
#define AON_ACOMP_CHAN_ADC0           0
#define AON_ACOMP_CHAN_ADC1           1
#define AON_ACOMP_CHAN_ADC2           2
#define AON_ACOMP_CHAN_ADC3           3
#define AON_ACOMP_CHAN_ADC4           4
#define AON_ACOMP_CHAN_ADC5           5
#define AON_ACOMP_CHAN_ADC6           6
#define AON_ACOMP_CHAN_ADC7           7
#define AON_ACOMP_CHAN_DACA           8
#define AON_ACOMP_CHAN_DACB           9
#define AON_ACOMP_CHAN_VREF_1P25V    10
#define AON_ACOMP_CHAN_VIO_X_SCALING_FACTOR_1  11
#define AON_ACOMP_CHAN_VIO_X_SCALING_FACTOR_2  12
#define AON_ACOMP_CHAN_VIO_X_SCALING_FACTOR_3  13
#define AON_ACOMP_CHAN_VIO_X_SCALING_FACTOR_4  14
#define AON_ACOMP_CHAN_VSS           15
```

### GPIO to Channel Mapping (BL616)

| GPIO Pin | Channel    |
|----------|------------|
| GPIO_20  | ADC0       |
| GPIO_19  | ADC1       |
| GPIO_2   | ADC2       |
| GPIO_3   | ADC3       |
| GPIO_14  | ADC4       |
| GPIO_13  | ADC5       |
| GPIO_12  | ADC6       |
| GPIO_10  | ADC7       |

### Helper Functions

```c
// Convert GPIO pin to ACOMP channel
int bflb_acomp_gpio_2_chanid(uint32_t pin, uint32_t *channel);

// Convert ACOMP channel to GPIO pin
int bflb_acomp_chanid_2_gpio(uint32_t channel, uint32_t *pin);

// Get positive input channel
uint32_t bflb_acomp_get_postive_input(uint8_t acomp_id);
```

---

## Threshold/Reference

The threshold is set by selecting the negative channel input. Common reference options:

| Reference Source    | Channel ID         | Description                      |
|--------------------|--------------------|----------------------------------|
| 1.25V internal ref  | `AON_ACOMP_CHAN_VREF_1P25V` | Bandgap reference |
| DAC output         | `AON_ACOMP_CHAN_DACA` / `AON_ACOMP_CHAN_DACB` | Programmable voltage |
| VIO scaled         | `AON_ACOMP_CHAN_VIO_X_SCALING_FACTOR_1-4` | VIO × factor |

### Scaling Factors

```c
#define AON_ACOMP_SCALING_FACTOR_0P25  0x00  // VIO × 0.25
#define AON_ACOMP_SCALING_FACTOR_0P5   0x10  // VIO × 0.5
#define AON_ACOMP_SCALING_FACTOR_0P75  0x20  // VIO × 0.75
#define AON_ACOMP_SCALING_FACTOR_1     0x30  // VIO × 1.0
```

### VIO Select (Threshold Voltage)

The `vio_sel` field sets the threshold voltage as: `(vioSel / 66) * avdd33`

---

## Polarity

Polarity is controlled by swapping the positive and negative channel selections:

- **Normal**: `pos_chan_sel` = input, `neg_chan_sel` = threshold
- **Inverted**: `pos_chan_sel` = threshold, `neg_chan_sel` = input

---

## Interrupt

The comparator output result can be read directly:

```c
uint32_t bflb_acomp_get_result(uint8_t acomp_id);
```

**Return value**: 0 or 1 (comparator output state)

**Note**: For interrupt-driven operation, configure the result in your application by:
1. Setting up an external interrupt on a GPIO tied to the comparator output
2. Or polling `bflb_acomp_get_result()` in a timer/isr

---

## Working Code Example

```c
#include "bflb_acomp.h"
#include "bflb_gpio.h"

void acomp_example(void)
{
    struct bflb_acomp_config_s acomp_cfg;
    
    // Configure: Compare ADC0 against 1.25V reference
    acomp_cfg.mux_en = 0;
    acomp_cfg.pos_chan_sel = AON_ACOMP_CHAN_ADC0;       // Input from ADC0/GPIO20
    acomp_cfg.neg_chan_sel = AON_ACOMP_CHAN_VREF_1P25V; // 1.25V threshold
    acomp_cfg.vio_sel = 0;
    acomp_cfg.scaling_factor = AON_ACOMP_SCALING_FACTOR_1;
    acomp_cfg.bias_prog = AON_ACOMP_BIAS_POWER_MODE2;   // Medium response
    acomp_cfg.hysteresis_pos_volt = AON_ACOMP_HYSTERESIS_VOLT_10MV;
    acomp_cfg.hysteresis_neg_volt = AON_ACOMP_HYSTERESIS_VOLT_NONE;
    
    // Initialize ACOMP0
    bflb_acomp_init(AON_ACOMP0_ID, &acomp_cfg);
    
    // Enable ACOMP
    bflb_acomp_enable(AON_ACOMP0_ID);
    
    // Read comparator result
    uint32_t result = bflb_acomp_get_result(AON_ACOMP0_ID);
    // result = 1: Input > 1.25V
    // result = 0: Input < 1.25V
}
```

---

## Register-Level Details

### ACOMP0/ACOMP1 Control Register (0x900 / 0x904)

```
Bits    Name            Description
31-27   Reserved
26      MUX_EN          MUX enable
25-23   Reserved
22-19   POS_SEL         Positive channel select (0-15)
18-15   NEG_SEL         Negative channel select (0-15)
14-13   Reserved
12-7    LEVEL_SEL       Scaling factor
6-5     Reserved
4-2     HYST_SELN       Hysteresis for negative
1       Reserved
0       EN              ACOMP enable
```

**Bitfield Definitions**:
```c
#define AON_ACOMP_MUX_EN           (1 << 26)
#define AON_ACOMP_POS_SEL_SHIFT    22
#define AON_ACOMP_POS_SEL_MASK     (0xf << 22)
#define AON_ACOMP_NEG_SEL_SHIFT    18
#define AON_ACOMP_NEG_SEL_MASK     (0xf << 18)
#define AON_ACOMP_LEVEL_SEL_SHIFT  12
#define AON_ACOMP_LEVEL_SEL_MASK   (0x3f << 12)
#define AON_ACOMP_BIAS_PROG_SHIFT  10
#define AON_ACOMP_BIAS_PROG_MASK   (0x3 << 10)
#define AON_ACOMP_HYST_SELP_SHIFT  7
#define AON_ACOMP_HYST_SELP_MASK   (0x7 << 7)
#define AON_ACOMP_HYST_SELN_SHIFT  4
#define AON_ACOMP_HYST_SELN_MASK   (0x7 << 4)
#define AON_ACOMP_EN               (1 << 0)
```

### ACOMP Shared Control Register (0x908)

```
Bits    Name                Description
31-26   VREF_SEL            VIO reference select (0-63)
25-20   Reserved
19      ACOMP0_OUT_RAW      ACOMP0 raw output
18-17   Reserved
16      ACOMP1_OUT_RAW      ACOMP1 raw output
15-13   Reserved
12-11   ACOMP0_TEST_SEL    Test select
10-9    ACOMP1_TEST_SEL    Test select
8       ACOMP0_TEST_EN     Test enable
7       ACOMP1_TEST_EN     Test enable
6-2     Reserved
1       ACOMP0_RSTN_ANA    ACOMP0 analog reset
0       ACOMP1_RSTN_ANA    ACOMP1 analog reset
```

**Bitfield Definitions**:
```c
#define AON_ACOMP_VREF_SEL_SHIFT        24
#define AON_ACOMP_VREF_SEL_MASK         (0x3f << 24)
#define AON_ACOMP0_OUT_RAW_DATA_SHIFT   19
#define AON_ACOMP0_OUT_RAW_DATA_MASK    (0x1 << 19)
#define AON_ACOMP1_OUT_RAW_DATA_SHIFT   17
#define AON_ACOMP1_OUT_RAW_DATA_MASK    (0x1 << 17)
#define AON_ACOMP0_TEST_SEL_SHIFT       12
#define AON_ACOMP0_TEST_SEL_MASK        (0x3 << 12)
#define AON_ACOMP1_TEST_SEL_SHIFT       10
#define AON_ACOMP1_TEST_SEL_MASK        (0x3 << 10)
#define AON_ACOMP0_TEST_EN              (1 << 9)
#define AON_ACOMP1_TEST_EN              (1 << 8)
#define AON_ACOMP0_RSTN_ANA             (1 << 1)
#define AON_ACOMP1_RSTN_ANA             (1 << 0)
```

---

## Bias/Hysteresis Options

### Bias Current (Response Speed)

```c
#define AON_ACOMP_BIAS_POWER_MODE1  0  // Slow response
#define AON_ACOMP_BIAS_POWER_MODE2  1  // Medium response
#define AON_ACOMP_BIAS_POWER_MODE3  2  // Fast response
#define AON_ACOMP_BIAS_POWER_NONE   3  // Power down
```

### Hysteresis Voltage

```c
#define AON_ACOMP_HYSTERESIS_VOLT_NONE   0   // No hysteresis
#define AON_ACOMP_HYSTERESIS_VOLT_10MV   1
#define AON_ACOMP_HYSTERESIS_VOLT_20MV   2
#define AON_ACOMP_HYSTERESIS_VOLT_30MV   3
#define AON_ACOMP_HYSTERESIS_VOLT_40MV   4
#define AON_ACOMP_HYSTERESIS_VOLT_50MV   5
#define AON_ACOMP_HYSTERESIS_VOLT_60MV   6
#define AON_ACOMP_HYSTERESIS_VOLT_70MV   7
```
