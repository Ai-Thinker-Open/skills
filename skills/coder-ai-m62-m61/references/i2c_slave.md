# I2C Slave Mode - BL616/BL618

## Overview

The BL616/BL618 I2C peripheral supports both master and slave modes. This document covers **I2C slave mode** operation, including initialization, address configuration, data transfer, and register-level details.

**Header:** `drivers/lhal/include/bflb_i2c.h`  
**Source:** `drivers/lhal/src/bflb_i2c.c`  
**Register Definitions:** `drivers/lhal/include/hardware/i2c_reg.h`

---

## 1. I2C Slave Initialization

### 1.1 Get Device Handle

```c
#include "bflb_device.h"
#include "bflb_i2c.h"

// Get I2C device handle
struct bflb_device_s *i2c;
i2c = bflb_device_get_by_name("i2c0");
if (i2c == NULL) {
    printf("Failed to get i2c0 device\r\n");
    return -1;
}
```

### 1.2 Initialize I2C Slave

```c
// Initialize I2C with frequency (305Hz ~ 400KHz)
uint32_t frequency = 100000;  // 100KHz typical for slave
bflb_i2c_init(i2c, frequency);
```

### 1.3 Configure GPIO Pins

```c
// board_i2c0_gpio_init() configures pins for I2C function
// Example for BL616:
// - SCL: GPIO14
// - SDA: GPIO15
board_i2c0_gpio_init();
```

### 1.4 Enable Interrupts (Optional - for callback-style handling)

```c
// Unmask interrupt types
bflb_i2c_int_mask(i2c, I2C_INTEN_ALL, false);

// Register interrupt handler (if using FreeRTOS/bthread)
#include "bflb_irq.h"
bflb_irq_register(i2c->irq_num, i2c_irq_handler);
```

---

## 2. Slave Address Configuration

### 2.1 7-bit Address Configuration

The slave address is set via the `I2C_CONFIG` register:

```c
// Address is configured in I2C_CR_I2C_SLV_ADDR bits [17:8] for BL616/BL618
// 7-bit address (shift left by 1)
uint16_t slave_addr = 0x50;  // Example: 7-bit address 0x50

// Configure via feature_control or direct register access
uint32_t reg_base = i2c->reg_base;
uint32_t regval = getreg32(reg_base + I2C_CONFIG_OFFSET);
regval &= ~I2C_CR_I2C_SLV_ADDR_MASK;
regval |= (slave_addr << I2C_CR_I2C_SLV_ADDR_SHIFT);
regval &= ~I2C_CR_I2C_10B_ADDR_EN;  // 7-bit mode
putreg32(regval, reg_base + I2C_CONFIG_OFFSET);
```

### 2.2 10-bit Address Configuration

```c
// 10-bit address
uint16_t slave_addr_10bit = 0x3A0;  // Example: 10-bit address

uint32_t regval = getreg32(reg_base + I2C_CONFIG_OFFSET);
regval &= ~I2C_CR_I2C_SLV_ADDR_MASK;
regval |= (slave_addr_10bit << I2C_CR_I2C_SLV_ADDR_SHIFT);
regval |= I2C_CR_I2C_10B_ADDR_EN;   // Enable 10-bit mode
putreg32(regval, reg_base + I2C_CONFIG_OFFSET);
```

### 2.3 Address Configuration via bflb_i2c_addr_config()

The SDK internal function used for address setup:

```c
static void bflb_i2c_addr_config(struct bflb_device_s *dev, uint16_t slaveaddr, 
                                  uint8_t *subaddr, uint8_t subaddr_size, 
                                  bool is_addr_10bit)
{
    uint32_t reg_base = dev->reg_base;
    uint32_t regval;
    
    // Configure sub-address (if needed)
    if (subaddr_size > 0) {
        regval = getreg32(reg_base + I2C_CONFIG_OFFSET);
        regval |= I2C_CR_I2C_SUB_ADDR_EN;
        regval &= ~I2C_CR_I2C_SUB_ADDR_BC_MASK;
        regval |= ((subaddr_size - 1) << I2C_CR_I2C_SUB_ADDR_BC_SHIFT);
        putreg32(regval, reg_base + I2C_CONFIG_OFFSET);
        // Write sub-address bytes to I2C_SUB_ADDR_OFFSET
    }
    
    // Configure slave address
    regval = getreg32(reg_base + I2C_CONFIG_OFFSET);
    regval &= ~I2C_CR_I2C_SLV_ADDR_MASK;
    regval |= (slaveaddr << I2C_CR_I2C_SLV_ADDR_SHIFT);
    
    if (is_addr_10bit) {
        regval |= I2C_CR_I2C_10B_ADDR_EN;
    } else {
        regval &= ~I2C_CR_I2C_10B_ADDR_EN;
    }
    putreg32(regval, reg_base + I2C_CONFIG_OFFSET);
}
```

---

## 3. TX/RX Callbacks (Interrupt-Based)

The SDK uses interrupt status flags rather than explicit callbacks. Handle TX/RX in an ISR:

### 3.1 Interrupt Status Flags

```c
// Interrupt status bits (I2C_INT_STS register)
#define I2C_INTSTS_END     (1 << 0)  // Transfer end
#define I2C_INTSTS_TX_FIFO (1 << 1)  // TX FIFO ready
#define I2C_INTSTS_RX_FIFO (1 << 2)  // RX FIFO ready
#define I2C_INTSTS_NACK    (1 << 3)  // NACK received
#define I2C_INTSTS_ARB     (1 << 4)  // Arbitration lost
#define I2C_INTSTS_FER     (1 << 5)  // FIFO error
```

### 3.2 Example: Interrupt Handler for Slave TX/RX

```c
static volatile uint8_t tx_data[256];
static volatile uint8_t rx_data[256];
static volatile uint16_t tx_len;
static volatile uint16_t rx_len;
static volatile bool rx_done = false;
static volatile bool tx_done = false;

void i2c_slave_irq_handler(struct bflb_device_s *dev, void *arg)
{
    uint32_t int_sts = bflb_i2c_get_intstatus(dev);
    
    if (int_sts & I2C_INTSTS_RX_FIFO) {
        // Data received from master
        while (1) {
            uint32_t fifo_stat = getreg32(dev->reg_base + I2C_FIFO_CONFIG_1_OFFSET);
            uint32_t rx_cnt = (fifo_stat >> 8) & 0x3;  // RX_FIFO_CNT
            if (rx_cnt == 0) break;
            
            uint32_t data = getreg32(dev->reg_base + I2C_FIFO_RDATA_OFFSET);
            if (rx_len < sizeof(rx_data)) {
                rx_data[rx_len++] = data & 0xFF;
            }
        }
        bflb_i2c_int_clear(dev, I2C_INTCLR_END);
    }
    
    if (int_sts & I2C_INTSTS_END) {
        // Transfer complete
        rx_done = true;
        tx_done = true;
        bflb_i2c_int_clear(dev, I2C_INTCLR_END);
    }
    
    if (int_sts & I2C_INTSTS_NACK) {
        // NACK received - master ended transfer
        bflb_i2c_int_clear(dev, I2C_INTCLR_NACK);
    }
    
    // Clear all interrupt flags
    bflb_i2c_int_clear(dev, I2C_INTCLR_ALL);
}
```

### 3.3 Register ISR and Enable Interrupts

```c
// In initialization code:
bflb_irq_register(i2c->irq_num, i2c_slave_irq_handler, NULL);
bflb_i2c_int_mask(i2c, I2C_INTEN_ALL, false);  // Enable all interrupts
```

---

## 4. Complete Working Code Example

### 4.1 Slave Transmitter (Master reads from slave)

```c
#include "bflb_device.h"
#include "bflb_i2c.h"
#include "bflb_irq.h"

#define I2C_SLAVE_ADDR 0x50
static uint8_t tx_buffer[64];
static volatile bool transfer_complete = false;

void i2c_slave_isr(struct bflb_device_s *dev, void *arg)
{
    uint32_t int_sts = bflb_i2c_get_intstatus(dev);
    
    if (int_sts & I2C_INTSTS_END) {
        transfer_complete = true;
        bflb_i2c_int_clear(dev, I2C_INTCLR_END);
    }
    
    if (int_sts & I2C_INTSTS_TX_FIFO) {
        // Fill TX FIFO when requested by master
        // HW handles TX automatically in slave mode
    }
    
    bflb_i2c_int_clear(dev, I2C_INTCLR_ALL);
}

int i2c_slave_init(void)
{
    struct bflb_device_s *i2c;
    
    // Get I2C device
    i2c = bflb_device_get_by_name("i2c0");
    if (i2c == NULL) {
        return -1;
    }
    
    // Initialize I2C at 100KHz
    bflb_i2c_init(i2c, 100000);
    
    // Configure slave address (7-bit)
    uint32_t reg_base = i2c->reg_base;
    uint32_t regval = getreg32(reg_base + I2C_CONFIG_OFFSET);
    regval &= ~I2C_CR_I2C_SLV_ADDR_MASK;
    regval |= (I2C_SLAVE_ADDR << I2C_CR_I2C_SLV_ADDR_SHIFT);
    regval &= ~I2C_CR_I2C_10B_ADDR_EN;  // 7-bit mode
    putreg32(regval, reg_base + I2C_CONFIG_OFFSET);
    
    // Prepare TX data
    for (int i = 0; i < sizeof(tx_buffer); i++) {
        tx_buffer[i] = i;
    }
    
    // Enable interrupts
    bflb_i2c_int_mask(i2c, I2C_INTEN_END, false);
    bflb_irq_register(i2c->irq_num, i2c_slave_isr, NULL);
    
    printf("I2C Slave initialized with address 0x%02X\r\n", I2C_SLAVE_ADDR);
    return 0;
}

// Call this to prepare data for master to read
void i2c_slave_set_tx_data(uint8_t *data, uint16_t len)
{
    if (len > sizeof(tx_buffer)) len = sizeof(tx_buffer);
    memcpy(tx_buffer, data, len);
}
```

### 4.2 Slave Receiver (Master writes to slave)

```c
#include "bflb_device.h"
#include "bflb_i2c.h"
#include "bflb_irq.h"

#define I2C_SLAVE_ADDR 0x50
static uint8_t rx_buffer[256];
static volatile uint16_t rx_count = 0;
static volatile bool data_received = false;

void i2c_slave_rx_isr(struct bflb_device_s *dev, void *arg)
{
    uint32_t int_sts = bflb_i2c_get_intstatus(dev);
    
    if (int_sts & I2C_INTSTS_END) {
        data_received = true;
        bflb_i2c_int_clear(dev, I2C_INTCLR_END);
    }
    
    if (int_sts & I2C_INTSTS_RX_FIFO) {
        // Read all available bytes from RX FIFO
        while (1) {
            uint32_t fifo_stat = getreg32(dev->reg_base + I2C_FIFO_CONFIG_1_OFFSET);
            uint32_t rx_cnt = (fifo_stat >> 8) & 0x3;
            if (rx_cnt == 0) break;
            
            uint32_t data = getreg32(dev->reg_base + I2C_FIFO_RDATA_OFFSET);
            if (rx_count < sizeof(rx_buffer)) {
                rx_buffer[rx_count++] = data & 0xFF;
            }
        }
    }
    
    bflb_i2c_int_clear(dev, I2C_INTCLR_ALL);
}

// Call this to get received data
int i2c_slave_get_rx_data(uint8_t *data, uint16_t max_len)
{
    if (!data_received) return 0;
    
    int copy_len = (rx_count < max_len) ? rx_count : max_len;
    memcpy(data, rx_buffer, copy_len);
    
    // Reset for next transfer
    rx_count = 0;
    data_received = false;
    
    return copy_len;
}
```

---

## 5. Register-Level Reference

### 5.1 Key Registers

| Register | Offset | Name | Description |
|----------|--------|------|-------------|
| `I2C_CONFIG` | 0x00 | I2C Configuration | Slave address, direction, packet length |
| `I2C_INT_STS` | 0x04 | Interrupt Status | TX/RX/NACK/END interrupt flags |
| `I2C_SUB_ADDR` | 0x08 | Sub-address | Optional sub-address for indexed access |
| `I2C_BUS_BUSY` | 0x0C | Bus Status | Bus busy flag |
| `I2C_PRD_START` | 0x10 | Start Timing | START condition timing phases |
| `I2C_PRD_STOP` | 0x14 | Stop Timing | STOP condition timing phases |
| `I2C_PRD_DATA` | 0x18 | Data Timing | Data phase timing |
| `I2C_FIFO_CONFIG_0` | 0x80 | FIFO Config 0 | DMA enable, FIFO clear |
| `I2C_FIFO_CONFIG_1` | 0x84 | FIFO Config 1 | FIFO count, threshold |
| `I2C_FIFO_WDATA` | 0x88 | FIFO Write Data | TX FIFO write register |
| `I2C_FIFO_RDATA` | 0x8C | FIFO Read Data | RX FIFO read register |

### 5.2 I2C_CONFIG Register (0x00) - Key Fields

```
Bits:
[0]     I2C_CR_I2C_M_EN       - Master enable (0=slave mode active when M_EN=0)
[1]     I2C_CR_I2C_PKT_DIR    - Packet direction (0=slave rx, 1=slave tx)
[3]     I2C_CR_I2C_SCL_SYNC_EN- Clock stretching enable
[7]     I2C_CR_I2C_10B_ADDR_EN- 10-bit address enable
[17:8]  I2C_CR_I2C_SLV_ADDR   - Slave address (7 or 10 bits)
[19:18] I2C_CR_I2C_PKT_LEN    - Packet length - 1
```

### 5.3 I2C_INT_STS Register (0x04) - Interrupt Flags

```
Status Bits (read):
[0]     I2C_END_INT    - Transfer end
[1]     I2C_TXF_INT    - TX FIFO ready
[2]     I2C_RXF_INT    - RX FIFO ready  
[3]     I2C_NAK_INT    - NACK received
[4]     I2C_ARB_INT    - Arbitration lost
[5]     I2C_FER_INT    - FIFO error

Mask Bits (upper 16 bits):
[24]    I2C_CR_I2C_END_EN   - END interrupt enable
[25]    I2C_CR_I2C_TXF_EN   - TX FIFO interrupt enable
[26]    I2C_CR_I2C_RXF_EN   - RX FIFO interrupt enable
```

### 5.4 FIFO Registers

```c
// FIFO Configuration 0 (0x80)
#define I2C_DMA_TX_EN     (1 << 0)   // TX DMA enable
#define I2C_DMA_RX_EN     (1 << 1)   // RX DMA enable
#define I2C_TX_FIFO_CLR  (1 << 2)   // Clear TX FIFO
#define I2C_RX_FIFO_CLR  (1 << 3)   // Clear RX FIFO

// FIFO Configuration 1 (0x84) - BL616/BL618
#define I2C_TX_FIFO_CNT_SHIFT  (0)   // TX FIFO count (bits [1:0])
#define I2C_RX_FIFO_CNT_SHIFT  (8)   // RX FIFO count (bits [9:8])
#define I2C_TX_FIFO_TH         (1 << 16)  // TX threshold
#define I2C_RX_FIFO_TH         (1 << 24)  // RX threshold

// FIFO Data (0x88 / 0x8C)
// Write to I2C_FIFO_WDATA_OFFSET to send
// Read from I2C_FIFO_RDATA_OFFSET to receive
```

### 5.5 Direct Register Access Example

```c
void i2c_slave_set_address(struct bflb_device_s *dev, uint8_t addr, bool ten_bit)
{
    uint32_t reg_base = dev->reg_base;
    uint32_t regval;
    
    regval = getreg32(reg_base + I2C_CONFIG_OFFSET);
    regval &= ~I2C_CR_I2C_SLV_ADDR_MASK;
    regval |= (addr << I2C_CR_I2C_SLV_ADDR_SHIFT);
    
    if (ten_bit) {
        regval |= I2C_CR_I2C_10B_ADDR_EN;
    } else {
        regval &= ~I2C_CR_I2C_10B_ADDR_EN;
    }
    
    putreg32(regval, reg_base + I2C_CONFIG_OFFSET);
}

void i2c_slave_enable_tx(struct bflb_device_s *dev)
{
    uint32_t reg_base = dev->reg_base;
    uint32_t regval;
    
    regval = getreg32(reg_base + I2C_CONFIG_OFFSET);
    regval |= I2C_CR_I2C_PKT_DIR;  // Set direction to TX
    putreg32(regval, reg_base + I2C_CONFIG_OFFSET);
}

void i2c_slave_enable_rx(struct bflb_device_s *dev)
{
    uint32_t reg_base = dev->reg_base;
    uint32_t regval;
    
    regval = getreg32(reg_base + I2C_CONFIG_OFFSET);
    regval &= ~I2C_CR_I2C_PKT_DIR;  // Set direction to RX
    putreg32(regval, reg_base + I2C_CONFIG_OFFSET);
}
```

---

## 6. Timing Configuration

### 6.1 Auto-calculated Timing

`bflb_i2c_init()` automatically calculates timing based on the frequency parameter:

```c
// Frequency <= 100KHz: 50% duty cycle
// Frequency > 100KHz:  33% duty cycle

// Internal calculation (from bflb_i2c.c):
phase = (peripheral_clock + frequency/2) / frequency;

if (freq <= 100000) {
    phase0 = (phase + 2) / 4;
    phase1 = phase0;
    phase2 = phase / 2 - phase0;
    phase3 = phase - phase0 - phase1 - phase2;
} else {
    phase0 = (phase + 2) / 3;
    phase1 = (phase + 3) / 6;
    phase2 = (phase + 1) / 3 - phase1;
    phase3 = phase - phase0 - phase1 - phase2;
}
```

### 6.2 Manual Timing Configuration

```c
#include "bflb_i2c.h"

struct bflb_i2c_timing_s timing = {
    .data_phase0 = 50,
    .data_phase1 = 25,
    .data_phase2 = 25,
    .data_phase3 = 25,
    .start_phase0 = 50,
    .start_phase1 = 50,
    .start_phase2 = 50,
    .start_phase3 = 25,
    .stop_phase0 = 50,
    .stop_phase1 = 50,
    .stop_phase2 = 50,
    .stop_phase3 = 25,
};

bflb_i2c_feature_control(i2c, I2C_CMD_SET_TIMING, (size_t)&timing);
```

---

## 7. Advanced Features

### 7.1 Clock Stretching

```c
// Enable SCL clock stretching (allows slave to pause bus)
bflb_i2c_feature_control(i2c, I2C_CMD_SET_SCL_SYNC, 1);

// Disable
bflb_i2c_feature_control(i2c, I2C_CMD_SET_SCL_SYNC, 0);
```

### 7.2 Deglitch Filter

```c
// Enable deglitch with count (0=disable, 1-15=filter count)
bflb_i2c_feature_control(i2c, I2C_CMD_SET_DEGLITCH_CNT, 4);
```

### 7.3 DMA Mode

```c
// Enable TX DMA
bflb_i2c_link_txdma(i2c, true);

// Enable RX DMA  
bflb_i2c_link_rxdma(i2c, true);
```

---

## 8. Notes

1. **No dedicated `bflb_i2c_slave.h`**: The BL616/BL618 SDK integrates slave functionality into the main `bflb_i2c.h` driver. Use `bflb_i2c_init()` and configure the `I2C_CR_I2C_SLV_ADDR` bits to set the slave address.

2. **Master/Slave sharing**: The same peripheral operates as master or slave depending on context. When not actively driving as master, it responds as a slave to addressed traffic.

3. **Bus busy check**: 
```c
uint32_t busy = getreg32(reg_base + I2C_BUS_BUSY_OFFSET);
if (busy & I2C_STS_I2C_BUS_BUSY) {
    // Bus is busy
}
```

4. **7-bit vs 10-bit**: 7-bit addresses use `I2C_CR_I2C_10B_ADDR_EN=0`, 10-bit uses `=1`. The address mask differs: 7-bit uses bits [14:8], 10-bit uses bits [17:8].