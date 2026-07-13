# IR (Infrared) Remote Driver Documentation

**Chip:** BL616/BL618  
**IR Base Address:** `0x2000A800`  
**Header:** `bflb_ir.h`  
**Source:** `bflb_ir.c`  

---

## Table of Contents
1. [Overview](#overview)
2. [IR Modes](#ir-modes)
3. [NEC Protocol](#nec-protocol)
4. [API Reference](#api-reference)
5. [Register Map](#register-map)
6. [Working Code Examples](#working-code-examples)

---

## Overview

The IR peripheral supports:
- **TX (Transmit):** NEC, RC5, SWM (Software Mode), Custom protocols
- **RX (Receive):** NEC, RC5, SWM (Software Mode)
- **Features:** Modulation, DMA support, FIFO, deglitch filtering

---

## IR Modes

### TX Modes (`IR_TX_MODE`)
| Mode | Value | Description |
|------|-------|-------------|
| `IR_TX_NEC` | 0 | NEC protocol |
| `IR_TX_RC5` | 1 | RC5 protocol |
| `IR_TX_SWM` | 2 | Software Mode |
| `IR_TX_CUSTOMIZE` | 3 | Custom protocol |

### RX Modes (`IR_RX_MODE`)
| Mode | Value | Description |
|------|-------|-------------|
| `IR_RX_NEC` | 0 | NEC protocol |
| `IR_RX_RC5` | 1 | RC5 protocol |
| `IR_RX_SWM` | 2 | Software Mode |

---

## NEC Protocol

### NEC Frame Format
```
| Leader | Address | ~Address | Command | ~Command |
| 9ms    | 8 bits  | 8 bits   | 8 bits  | 8 bits   |
```

- **Leader:** 9ms pulse + 4.5ms space
- **Logic 0:** 560µs pulse + 560µs space
- **Logic 1:** 560µs pulse + 1680µs space
- **Total:** 32 bits (address + inverse + command + inverse)
- **End:** 560µs pulse + 40ms space (repeat code)

### Auto-Configuration (bflb_ir_tx_init with IR_TX_NEC)
The driver automatically sets:
```c
tx_config->data_bits = 32;
tx_config->tail_inverse = 0;
tx_config->tail_enable = 1;       // Tail pulse enabled
tx_config->head_inverse = 0;
tx_config->head_enable = 1;       // Head pulse enabled
tx_config->logic1_inverse = 0;
tx_config->logic0_inverse = 0;
tx_config->data_enable = 1;
tx_config->swm_enable = 0;
tx_config->output_modulation = 1;  // 38kHz modulation
tx_config->output_inverse = 0;
tx_config->freerun_enable = 0;
tx_config->continue_enable = 0;
tx_config->fifo_width = IR_TX_FIFO_WIDTH_32BIT;
// Pulse widths calculated for NEC timing
```

---

## API Reference

### TX APIs

#### `bflb_ir_tx_init(dev, config)`
Initialize IR TX with configuration.

```c
void bflb_ir_tx_init(struct bflb_device_s *dev, 
                      const struct bflb_ir_tx_config_s *config);
```

**Example:**
```c
struct bflb_device_s *ir;
struct bflb_ir_tx_config_s tx_config = {
    .tx_mode = IR_TX_NEC,
    .output_modulation = 1,
    .output_inverse = 0,
};

ir = bflb_device_get_by_name("ir");
bflb_ir_tx_init(ir, &tx_config);
```

#### `bflb_ir_send(dev, data, length)`
Send data in NEC/RC5/Custom mode.

```c
void bflb_ir_send(struct bflb_device_s *dev, uint32_t *data, uint32_t length);
```

**NEC Send Example:**
```c
// NEC frame: Address=0x00, Command=0x45
uint32_t nec_data = 0x00FF45BA;  // MSB=addr, then ~addr, then cmd, then ~cmd
bflb_ir_send(ir, &nec_data, 1);
```

#### `bflb_ir_swm_send(dev, data, length)`
Send data in Software Mode (raw pulse widths).

```c
void bflb_ir_swm_send(struct bflb_device_s *dev, uint16_t *data, uint32_t length);
```

#### `bflb_ir_tx_enable(dev, enable)`
Enable/disable TX.

```c
void bflb_ir_tx_enable(struct bflb_device_s *dev, bool enable);
```

#### `bflb_ir_txint_mask(dev, int_type, mask)`
Mask/unmask TX interrupts.

```c
void bflb_ir_txint_mask(struct bflb_device_s *dev, uint8_t int_type, bool mask);
// int_type: IR_TX_INTEN_END, IR_TX_INTEN_FIFO, IR_TX_INTEN_FER
```

#### `bflb_ir_get_txint_status(dev)`
Get TX interrupt status.

```c
uint32_t bflb_ir_get_txint_status(struct bflb_device_s *dev);
// Returns: IR_TX_INTSTS_END, IR_TX_INTSTS_FIFO, IR_TX_INTSTS_FER
```

#### `bflb_ir_txint_clear(dev)`
Clear TX interrupt.

```c
void bflb_ir_txint_clear(struct bflb_device_s *dev);
```

#### `bflb_ir_txfifo_clear(dev)`
Clear TX FIFO.

```c
void bflb_ir_txfifo_clear(struct bflb_device_s *dev);
```

#### `bflb_ir_get_txfifo_cnt(dev)`
Get TX FIFO available count.

```c
uint8_t bflb_ir_get_txfifo_cnt(struct bflb_device_s *dev);
```

---

### RX APIs

#### `bflb_ir_rx_init(dev, config)`
Initialize IR RX with configuration.

```c
void bflb_ir_rx_init(struct bflb_device_s *dev, 
                     const struct bflb_ir_rx_config_s *config);
```

**Example:**
```c
struct bflb_ir_rx_config_s rx_config = {
    .rx_mode = IR_RX_NEC,
    .input_inverse = 0,
    .deglitch_enable = 1,
    .deglitch_cnt = 0,
    .fifo_threshold = 0,
};

bflb_ir_rx_init(ir, &rx_config);
```

#### `bflb_ir_receive(dev, data)`
Receive data in NEC/RC5 mode (blocking).

```c
uint16_t bflb_ir_receive(struct bflb_device_s *dev, uint64_t *data);
// Returns: bit count of data received
```

**NEC Receive Example:**
```c
uint64_t nec_data;
uint16_t bits = bflb_ir_receive(ir, &nec_data);
// Extract: address = (nec_data >> 0) & 0xFF
//          command = (nec_data >> 16) & 0xFF
```

#### `bflb_ir_swm_receive(dev, data, length)`
Receive data in Software Mode.

```c
uint16_t bflb_ir_swm_receive(struct bflb_device_s *dev, uint16_t *data, uint16_t length);
```

#### `bflb_ir_rx_enable(dev, enable)`
Enable/disable RX.

```c
void bflb_ir_rx_enable(struct bflb_device_s *dev, bool enable);
```

#### `bflb_ir_rxint_mask(dev, int_type, mask)`
Mask/unmask RX interrupts.

```c
void bflb_ir_rxint_mask(struct bflb_device_s *dev, uint8_t int_type, bool mask);
// int_type: IR_RX_INTEN_END, IR_RX_INTEN_FIFO, IR_RX_INTEN_FER
```

#### `bflb_ir_get_rxint_status(dev)`
Get RX interrupt status.

```c
uint32_t bflb_ir_get_rxint_status(struct bflb_device_s *dev);
```

#### `bflb_ir_rxint_clear(dev)`
Clear RX interrupt.

```c
void bflb_ir_rxint_clear(struct bflb_device_s *dev);
```

#### `bflb_ir_rxfifo_clear(dev)`
Clear RX FIFO.

```c
void bflb_ir_rxfifo_clear(struct bflb_device_s *dev);
```

#### `bflb_ir_get_rxfifo_cnt(dev)`
Get RX FIFO available count.

```c
uint8_t bflb_ir_get_rxfifo_cnt(struct bflb_device_s *dev);
```

---

### Feature Control

#### `bflb_ir_feature_control(dev, cmd, arg)`
Special feature control.

```c
int bflb_ir_feature_control(struct bflb_device_s *dev, int cmd, size_t arg);
// cmds:
//   IR_CMD_SWM_SET_DATA_LEN    - Set SWM data length
//   IR_CMD_SWM_WRITE_TX_FIFO   - Write TX FIFO (SWM)
//   IR_CMD_SWM_READ_RX_FIFO     - Read RX FIFO (SWM)
//   IR_CMD_SWM_SET_UNIT_DATA    - Set pulse width unit
```

---

## Register Map

**IR_BASE = 0x2000A800**

### TX Registers (BL616/BL618, non-BL602/BL702)

| Offset | Name | Description |
|--------|------|-------------|
| `0x00` | IRTX_CONFIG | TX configuration |
| `0x04` | IRTX_INT_STS | TX interrupt status |
| `0x10` | IRTX_PULSE_WIDTH | Pulse width unit & modulation |
| `0x14` | IRTX_PW_0 | Logic 0/1 pulse widths |
| `0x18` | IRTX_PW_1 | Head/Tail pulse widths |
| `0x80` | IR_FIFO_CONFIG_0 | FIFO control 0 |
| `0x84` | IR_FIFO_CONFIG_1 | FIFO threshold/count |
| `0x88` | IR_FIFO_WDATA | TX FIFO write data |

### RX Registers (BL616/BL618, non-BL602/BL702)

| Offset | Name | Description |
|--------|------|-------------|
| `0x40` | IRRX_CONFIG | RX configuration |
| `0x44` | IRRX_INT_STS | RX interrupt status |
| `0x48` | IRRX_PW_CONFIG | Data/End thresholds |
| `0x50` | IRRX_DATA_COUNT | Received bit count |
| `0x54` | IRRX_DATA_WORD0 | Received data low 32bits |
| `0x58` | IRRX_DATA_WORD1 | Received data high bits |
| `0x8C` | IR_FIFO_RDATA | RX FIFO read data |

### TX Config Register (`IRTX_CONFIG`)

| Bit | Name | Description |
|-----|------|-------------|
| 0 | IRTX_EN | TX enable |
| 1 | IRTX_OUT_INV | Output inverse |
| 2 | IRTX_MOD_EN | Modulation enable |
| 3 | IRTX_SWM_EN | Software mode enable |
| 4 | IRTX_DATA_EN | Data pulse enable |
| 5 | IRTX_LOGIC0_HL_INV | Logic 0 inverse |
| 6 | IRTX_LOGIC1_HL_INV | Logic 1 inverse |
| 8 | IRTX_HEAD_EN | Head pulse enable |
| 9 | IRTX_HEAD_HL_INV | Head pulse inverse |
| 10 | IRTX_TAIL_EN | Tail pulse enable |
| 11 | IRTX_TAIL_HL_INV | Tail pulse inverse |
| 12 | IRTX_FRM_EN | Frame mode (freerun) |
| 13 | IRTX_FRM_CONT_EN | Frame continue mode |
| 14-15 | IRTX_FRM_FRAME_SIZE | Frame size |
| 16+ | IRTX_DATA_NUM | Data bit count |

### RX Config Register (`IRRX_CONFIG`)

| Bit | Name | Description |
|-----|------|-------------|
| 0 | IRRX_EN | RX enable |
| 1 | IRRX_IN_INV | Input inverse |
| 2-3 | IRRX_MODE | RX mode (0=NEC, 1=RC5, 2=SWM) |
| 4 | IRRX_DEG_EN | Deglitch enable |
| 8-11 | IRRX_DEG_CNT | Deglitch cycle count |

### RX Pulse Width Config (`IRRX_PW_CONFIG`)

| Bit | Name | Description |
|-----|------|-------------|
| 0-15 | IRRX_DATA_TH | Data threshold |
| 16-31 | IRRX_END_TH | End threshold |

---

## Working Code Examples

### Example 1: NEC TX (Send TV Power On)

```c
#include "bflb_ir.h"
#include "bflb_device.h"

#define IR_DEV_NAME "ir"

void ir_nec_send_example(void)
{
    struct bflb_device_s *ir;
    struct bflb_ir_tx_config_s tx_cfg;
    
    // Get IR device
    ir = bflb_device_get_by_name(IR_DEV_NAME);
    if (!ir) {
        printf("IR device not found\r\n");
        return;
    }
    
    // Configure for NEC
    tx_cfg.tx_mode = IR_TX_NEC;
    tx_cfg.output_modulation = 1;   // 38kHz modulation
    tx_cfg.output_inverse = 0;       // Idle low
    
    bflb_ir_tx_init(ir, &tx_cfg);
    
    // NEC frame: Address=0x00, Command=0xEF (Power key)
    // Format: MSB first, address, ~address, command, ~command
    uint32_t nec_frame = 0x00EF10EF;
    
    // Enable and send
    bflb_ir_tx_enable(ir, true);
    bflb_ir_send(ir, &nec_frame, 1);
    bflb_ir_tx_enable(ir, false);
    
    printf("NEC frame sent: 0x%08X\r\n", nec_frame);
}
```

### Example 2: NEC RX (Receive NEC signal)

```c
#include "bflb_ir.h"
#include "bflb_device.h"

#define IR_DEV_NAME "ir"

void ir_nec_receive_example(void)
{
    struct bflb_device_s *ir;
    struct bflb_ir_rx_config_s rx_cfg;
    uint64_t nec_data;
    uint16_t bits;
    uint8_t address, command;
    
    ir = bflb_device_get_by_name(IR_DEV_NAME);
    if (!ir) {
        printf("IR device not found\r\n");
        return;
    }
    
    // Configure for NEC
    rx_cfg.rx_mode = IR_RX_NEC;
    rx_cfg.input_inverse = 0;
    rx_cfg.deglitch_enable = 1;
    rx_cfg.deglitch_cnt = 0;
    rx_cfg.fifo_threshold = 0;
    
    bflb_ir_rx_init(ir, &rx_cfg);
    bflb_ir_rx_enable(ir, true);
    
    // Wait for reception (blocking)
    bits = bflb_ir_receive(ir, &nec_data);
    
    bflb_ir_rx_enable(ir, false);
    
    if (bits == 32) {
        // Extract address and command
        address = (nec_data >> 0) & 0xFF;
        command = (nec_data >> 16) & 0xFF;
        printf("NEC received: addr=0x%02X, cmd=0x%02X\r\n", address, command);
    } else {
        printf("Invalid NEC data, bits=%d\r\n", bits);
    }
}
```

### Example 3: Software Mode TX (Custom Protocol)

```c
#include "bflb_ir.h"
#include "bflb_device.h"

#define IR_DEV_NAME "ir"

void ir_swm_send_example(void)
{
    struct bflb_device_s *ir;
    struct bflb_ir_tx_config_s tx_cfg;
    
    ir = bflb_device_get_by_name(IR_DEV_NAME);
    if (!ir) return;
    
    // Configure SWM
    tx_cfg.tx_mode = IR_TX_SWM;
    tx_cfg.output_modulation = 1;
    tx_cfg.output_inverse = 0;
    tx_cfg.fifo_width = IR_TX_FIFO_WIDTH_32BIT;
    tx_cfg.fifo_threshold = 0;
    
    bflb_ir_tx_init(ir, &tx_cfg);
    
    // Custom pulse widths array (each value = pulse width in units)
    uint16_t pulse_data[] = {
        100, 50,  // Pulse 1: 100 units, space: 50 units
        80, 30,
        60, 60,
        40, 120
    };
    
    bflb_ir_tx_enable(ir, true);
    bflb_ir_swm_send(ir, pulse_data, sizeof(pulse_data)/sizeof(pulse_data[0]));
    bflb_ir_tx_enable(ir, false);
}
```

### Example 4: Software Mode RX (Raw Pulse Widths)

```c
#include "bflb_ir.h"
#include "bflb_device.h"

#define IR_DEV_NAME "ir"

void ir_swm_receive_example(void)
{
    struct bflb_device_s *ir;
    struct bflb_ir_rx_config_s rx_cfg;
    uint16_t pulse_data[128];
    uint16_t count;
    
    ir = bflb_device_get_by_name(IR_DEV_NAME);
    if (!ir) return;
    
    // Configure SWM RX
    rx_cfg.rx_mode = IR_RX_SWM;
    rx_cfg.input_inverse = 0;
    rx_cfg.deglitch_enable = 1;
    rx_cfg.deglitch_cnt = 0;
    rx_cfg.fifo_threshold = 0;
    
    bflb_ir_rx_init(ir, &rx_cfg);
    bflb_ir_rx_enable(ir, true);
    
    count = bflb_ir_swm_receive(ir, pulse_data, 128);
    
    bflb_ir_rx_enable(ir, false);
    
    printf("Received %d pulse widths:\r\n", count);
    for (int i = 0; i < count && i < 16; i++) {
        printf("  [%d] = %d\r\n", i, pulse_data[i]);
    }
}
```

### Example 5: Register-Level TX (Direct Hardware Access)

```c
#include "bflb_ir.h"
#include "bflb_clock.h"
#include "hardware/ir_reg.h"

#define IR_BASE 0x2000A800

void ir_reg_write_example(void)
{
    uint32_t ir_clock;
    uint32_t reg_base = IR_BASE;
    
    // Get IR clock
    ir_clock = bflb_clk_get_peripheral_clock(BFLB_DEVICE_TYPE_IR, 0);
    if (ir_clock == 0) ir_clock = 2000000;
    
    // Configure pulse width unit
    uint32_t pulse_width_unit = (ir_clock * 10 / 17777 - 1) & 0xFFF;
    uint32_t modu_width_1 = ((ir_clock / 11310 + 5) / 10 - 1) & 0xFF;
    uint32_t modu_width_0 = ((ir_clock / 5655 + 5) / 10 - 1) & 0xFF;
    
    // IRTX_PULSE_WIDTH (0x10)
    uint32_t regval = pulse_width_unit | (modu_width_1 << 16) | (modu_width_0 << 24);
    putreg32(regval, reg_base + 0x10);
    
    // IRTX_PW_0 (0x14) - Logic 0/1 pulse widths
    regval = 0 | (0 << 8) | (2 << 16) | (0 << 24);  // L0=0, L1=2
    putreg32(regval, reg_base + 0x14);
    
    // IRTX_PW_1 (0x18) - Head/Tail pulse widths
    regval = 15 | (7 << 8) | (0 << 16) | (0 << 24);  // H0=15, H1=7, T=0
    putreg32(regval, reg_base + 0x18);
    
    // IRTX_CONFIG (0x00) - Enable TX, NEC mode
    regval = getreg32(reg_base + 0x00);
    regval &= ~0xFFFF;
    regval |= (32 - 1) << 16;    // 32 bits
    regval |= (1 << 10);         // Tail enable
    regval |= (1 << 8);          // Head enable
    regval |= (1 << 4);          // Data enable
    regval |= (1 << 2);          // Modulation enable
    regval |= (1 << 0);          // TX enable
    putreg32(regval, reg_base + 0x00);
    
    // Write data to TX FIFO (0x88)
    uint32_t nec_data = 0x00EF10EF;
    putreg32(nec_data, reg_base + 0x88);
    
    // Wait for send complete
    while ((getreg32(reg_base + 0x04) & 0x01) == 0);
    
    // Clear interrupt
    putreg32(1 << 16, reg_base + 0x04);
}
```

---

## Interrupt Definitions

### TX Interrupts (`IR_TX_INTEN` / `IR_TX_INTSTS`)
| Name | Bit | Description |
|------|-----|-------------|
| `IR_TX_INTEN_END` | 0 | Transfer end interrupt |
| `IR_TX_INTEN_FIFO` | 1 | TX FIFO threshold interrupt |
| `IR_TX_INTEN_FER` | 2 | TX FIFO error interrupt |

### RX Interrupts (`IR_RX_INTEN` / `IR_RX_INTSTS`)
| Name | Bit | Description |
|------|-----|-------------|
| `IR_RX_INTEN_END` | 0 | Reception end interrupt |
| `IR_RX_INTEN_FIFO` | 1 | RX FIFO threshold interrupt |
| `IR_RX_INTEN_FER` | 2 | RX FIFO error interrupt |

---

## Notes

1. **Clock:** IR uses peripheral clock. If `bflb_clk_get_peripheral_clock()` returns 0, default to 2MHz.

2. **FIFO:** TX has 4-entry FIFO, RX has 8-entry FIFO.

3. **Modulation:** NEC/RC5 typically use 38kHz modulation.

4. **DMA:** TX supports DMA mode via `bflb_ir_link_txdma()`.

5. **BL602/BL702:** Different register layout - see `ir_reg.h` for details.

---

## References

- Header: `drivers/lhal/include/bflb_ir.h`
- Source: `drivers/lhal/src/bflb_ir.c`
- Registers: `drivers/lhal/include/hardware/ir_reg.h`
