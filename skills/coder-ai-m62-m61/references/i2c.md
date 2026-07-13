# I2C API Reference (BL616/BL618)

> **Source:** `bouffalo_sdk/drivers/lhal/include/bflb_i2c.h`  
> **Base Address:** `I2C0_BASE = 0x2000a300`, `I2C1_BASE = 0x2000a900`

## Overview

The BL616/BL618 I2C peripheral provides multi-master synchronous serial communication:
- Master and Slave modes
- Standard mode (100 KHz) and Fast mode (400 KHz)
- 7-bit and 10-bit addressing
- DMA support
- Clock stretching support
- Multi-master arbitration

## Base Addresses

| Instance | Base Address |
|----------|-------------|
| I2C0 | `0x2000a300` |
| I2C1 | `0x2000a900` |

---

## Message Flags

### Message Direction Flags

| Constant | Value | Description |
|----------|-------|-------------|
| `I2C_M_WRITE` | `0x0000` | Write data (master to slave) |
| `I2C_M_READ` | `0x0001` | Read data (slave to master) |
| `I2C_M_TEN` | `0x0002` | 10-bit address mode |
| `I2C_M_DMA` | `0x0004` | Enable DMA mode |
| `I2C_M_NOSTOP` | `0x0040` | Don't send STOP condition |
| `I2C_M_NOSTART` | `0x0080` | Don't send START condition |
| `I2C_M_RESTART` | `0x0010` | Repeated start (BL616CL only) |

### START/STOP Behavior

| msg[n] flags | msg[n+1] flags | Behavior |
|--------------|----------------|----------|
| 0 | 0 | Two separate messages with STOP then START |
| NOSTOP | NOSTART | Continuation of same transfer |
| NOSTOP | 0 | No STOP on msg[n]; repeated START on msg[n+1] |

---

## Interrupt Flags

### Interrupt Status Flags

| Constant | Value | Description |
|----------|-------|-------------|
| `I2C_INTSTS_END` | `1 << 0` | Transfer end interrupt |
| `I2C_INTSTS_TX_FIFO` | `1 << 1` | TX FIFO ready interrupt |
| `I2C_INTSTS_RX_FIFO` | `1 << 2` | RX FIFO ready interrupt |
| `I2C_INTSTS_NACK` | `1 << 3` | NACK received interrupt |
| `I2C_INTSTS_ARB` | `1 << 4` | Arbitration lost interrupt |
| `I2C_INTSTS_FER` | `1 << 5` | FIFO error interrupt |
| `I2C_INTSTS_TIMEOUT` | `1 << 6` | Master timeout (BL616CL only) |
| `I2C_INTSTS_RESTART` | `1 << 22` | Repeated start (BL616CL only) |

### Interrupt Enable Flags

| Constant | Value | Description |
|----------|-------|-------------|
| `I2C_INTEN_END` | `1 << 0` | Transfer end interrupt enable |
| `I2C_INTEN_TX_FIFO` | `1 << 1` | TX FIFO ready interrupt enable |
| `I2C_INTEN_RX_FIFO` | `1 << 2` | RX FIFO ready interrupt enable |
| `I2C_INTEN_NACK` | `1 << 3` | NACK interrupt enable |
| `I2C_INTEN_ARB` | `1 << 4` | Arbitration lost interrupt enable |
| `I2C_INTEN_FER` | `1 << 5` | FIFO error interrupt enable |

### Interrupt Clear Flags

| Constant | Value | Description |
|----------|-------|-------------|
| `I2C_INTCLR_END` | `1 << 0` | Clear transfer end interrupt |
| `I2C_INTCLR_NACK` | `1 << 3` | Clear NACK interrupt |
| `I2C_INTCLR_ARB` | `1 << 4` | Clear arbitration lost interrupt |
| `I2C_INTCLR_ALL` | `(1<<0)\|(1<<3)\|(1<<4)` | Clear all interrupts |

### Feature Control Commands

| Command | Description |
|---------|-------------|
| `I2C_CMD_SET_SCL_SYNC` | Enable multi-master/clock-stretching |
| `I2C_CMD_SET_DEGLITCH_CNT` | Set deglitch count (0 to disable) |
| `I2C_CMD_SET_TIMING` | Set I2C timing parameters |
| `I2C_CMD_GET_TIMING` | Get I2C timing parameters |
| `I2C_CMD_SET_TIMEOUT_VALUE` | Set timeout value (BL616CL) |
| `I2C_CMD_READ_HW_VERSION` | Read hardware version (BL616CL) |
| `I2C_CMD_READ_SW_USAGE` | Read software usage (BL616CL) |
| `I2C_CMD_WRITE_SW_USAGE` | Write software usage (BL616CL) |

---

## Data Structures

### I2C Message Structure

```c
struct bflb_i2c_msg_s {
    uint16_t addr;      // Slave address (7-bit or 10-bit)
    uint16_t flags;     // Message flags (I2C_M_*)
    uint8_t *buffer;    // Data buffer
    uint16_t length;    // Buffer length in bytes (must be < 256)
};
```

### I2C Timing Structure

```c
struct bflb_i2c_timing_s {
    uint8_t data_phase0;    // Data phase 0 length
    uint8_t data_phase1;    // Data phase 1 length
    uint8_t data_phase2;    // Data phase 2 length
    uint8_t data_phase3;    // Data phase 3 length
    uint8_t start_phase0;   // Start condition phase 0
    uint8_t start_phase1;   // Start condition phase 1
    uint8_t start_phase2;   // Start condition phase 2
    uint8_t start_phase3;   // Start condition phase 3
    uint8_t stop_phase0;    // Stop condition phase 0
    uint8_t stop_phase1;    // Stop condition phase 1
    uint8_t stop_phase2;    // Stop condition phase 2
    uint8_t stop_phase3;    // Stop condition phase 3
};
```

---

## LHAL API Functions

### bflb_i2c_init

Initialize I2C with frequency.

```c
void bflb_i2c_init(struct bflb_device_s *dev, uint32_t frequency);
```

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `dev` | `struct bflb_device_s *` | Device handle |
| `frequency` | `uint32_t` | I2C frequency in Hz (305Hz - 400KHz) |

**Example:**
```c
// Initialize I2C0 at 400 KHz (Fast mode)
bflb_i2c_init(i2c0_dev, 400000);
```

---

### bflb_i2c_deinit

Deinitialize I2C.

```c
void bflb_i2c_deinit(struct bflb_device_s *dev);
```

---

### bflb_i2c_link_txdma / bflb_i2c_link_rxdma

Enable I2C DMA for TX/RX.

```c
void bflb_i2c_link_txdma(struct bflb_device_s *dev, bool enable);
void bflb_i2c_link_rxdma(struct bflb_device_s *dev, bool enable);
```

---

### bflb_i2c_transfer

Perform I2C message transfer.

```c
int bflb_i2c_transfer(struct bflb_device_s *dev, struct bflb_i2c_msg_s *msgs, int count);
```

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `dev` | `struct bflb_device_s *` | Device handle |
| `msgs` | `struct bflb_i2c_msg_s *` | Array of I2C messages |
| `count` | `int` | Number of messages |

**Returns:** 0 on success, negative errno on failure

**Example:**
```c
// Single byte write to slave 0x50
uint8_t data = 0xAA;
struct bflb_i2c_msg_s msgs[] = {
    {
        .addr = 0x50,
        .flags = I2C_M_WRITE,
        .buffer = &data,
        .length = 1
    }
};
bflb_i2c_transfer(i2c_dev, msgs, 1);

// Read 4 bytes from slave 0x50 register 0x00
uint8_t reg_addr = 0x00;
uint8_t read_buf[4];
struct bflb_i2c_msg_s msgs[] = {
    {
        .addr = 0x50,
        .flags = I2C_M_WRITE | I2C_M_NOSTOP,
        .buffer = &reg_addr,
        .length = 1
    },
    {
        .addr = 0x50,
        .flags = I2C_M_READ,
        .buffer = read_buf,
        .length = 4
    }
};
bflb_i2c_transfer(i2c_dev, msgs, 2);
```

---

### bflb_i2c_int_mask

Enable or disable I2C interrupt.

```c
void bflb_i2c_int_mask(struct bflb_device_s *dev, uint32_t int_type, bool mask);
```

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `dev` | `struct bflb_device_s *` | Device handle |
| `int_type` | `uint32_t` | Interrupt type (I2C_INTEN_*) |
| `mask` | `bool` | `true` = disable, `false` = enable |

---

### bflb_i2c_int_clear

Clear I2C interrupt status.

```c
void bflb_i2c_int_clear(struct bflb_device_s *dev, uint32_t int_clear);
```

---

### bflb_i2c_get_intstatus

Get I2C interrupt status.

```c
uint32_t bflb_i2c_get_intstatus(struct bflb_device_s *dev);
```

**Returns:** Bitmask of active interrupt flags

---

### bflb_i2c_feature_control

Control I2C special features.

```c
int bflb_i2c_feature_control(struct bflb_device_s *dev, int cmd, size_t arg);
```

---

## Usage Examples

### Example 1: Write Single Register

```c
#include "bflb_i2c.h"

int i2c_write_register(uint8_t slave_addr, uint8_t reg, uint8_t value)
{
    struct bflb_device_s *i2c;
    uint8_t buf[2] = {reg, value};
    
    i2c = bflb_device_get_by_name("i2c0");
    
    struct bflb_i2c_msg_s msg = {
        .addr = slave_addr,
        .flags = I2C_M_WRITE,
        .buffer = buf,
        .length = 2
    };
    
    return bflb_i2c_transfer(i2c, &msg, 1);
}

// Usage
i2c_write_register(0x50, 0x10, 0xAA);
```

---

### Example 2: Read Multiple Bytes

```c
#include "bflb_i2c.h"

int i2c_read_bytes(uint8_t slave_addr, uint8_t reg, uint8_t *buf, uint32_t len)
{
    struct bflb_device_s *i2c;
    
    i2c = bflb_device_get_by_name("i2c0");
    
    // Write register address (no stop)
    struct bflb_i2c_msg_s msgs[] = {
        {
            .addr = slave_addr,
            .flags = I2C_M_WRITE | I2C_M_NOSTOP,
            .buffer = &reg,
            .length = 1
        },
        {
            .addr = slave_addr,
            .flags = I2C_M_READ,
            .buffer = buf,
            .length = len
        }
    };
    
    return bflb_i2c_transfer(i2c, msgs, 2);
}

// Usage
uint8_t data[16];
i2c_read_bytes(0x50, 0x00, data, 16);
```

---

### Example 3: Scan I2C Bus

```c
#include "bflb_i2c.h"

void i2c_scan(void)
{
    struct bflb_device_s *i2c;
    int ret;
    
    i2c = bflb_device_get_by_name("i2c0");
    
    printf("I2C Scan:\r\n");
    
    for (uint8_t addr = 1; addr < 127; addr++) {
        uint8_t dummy;
        struct bflb_i2c_msg_s msg = {
            .addr = addr,
            .flags = I2C_M_WRITE,
            .buffer = &dummy,
            .length = 1
        };
        
        ret = bflb_i2c_transfer(i2c, &msg, 1);
        
        if (ret == 0) {
            printf("  0x%02X found\r\n", addr << 1);
        }
    }
}
```

---

### Example 4: EEPROM Read/Write

```c
#include "bflb_i2c.h"

#define EEPROM_ADDR  0x50
#define EEPROM_SIZE  32768
#define PAGE_SIZE    64

int eeprom_write_page(uint8_t page_addr, const uint8_t *data, uint16_t len)
{
    struct bflb_device_s *i2c;
    uint8_t buf[66];  // 2 byte address + 64 bytes data
    
    if (len > PAGE_SIZE) {
        return -1;
    }
    
    i2c = bflb_device_get_by_name("i2c0");
    
    buf[0] = (page_addr >> 8) & 0xFF;  // High byte of address
    buf[1] = page_addr & 0xFF;          // Low byte of address
    memcpy(&buf[2], data, len);
    
    struct bflb_i2c_msg_s msg = {
        .addr = EEPROM_ADDR,
        .flags = I2C_M_WRITE,
        .buffer = buf,
        .length = len + 2
    };
    
    return bflb_i2c_transfer(i2c, &msg, 1);
}

int eeprom_read(uint16_t eeprom_addr, uint8_t *data, uint16_t len)
{
    struct bflb_device_s *i2c;
    
    i2c = bflb_device_get_by_name("i2c0");
    
    uint8_t addr_buf[2] = {
        (eeprom_addr >> 8) & 0xFF,
        eeprom_addr & 0xFF
    };
    
    struct bflb_i2c_msg_s msgs[] = {
        {
            .addr = EEPROM_ADDR,
            .flags = I2C_M_WRITE | I2C_M_NOSTOP,
            .buffer = addr_buf,
            .length = 2
        },
        {
            .addr = EEPROM_ADDR,
            .flags = I2C_M_READ,
            .buffer = data,
            .length = len
        }
    };
    
    return bflb_i2c_transfer(i2c, msgs, 2);
}
```

---

### Example 5: I2C with DMA

```c
#include "bflb_i2c.h"

#define I2C_BUFFER_SIZE 256

void i2c_dma_example(void)
{
    struct bflb_device_s *i2c;
    struct bflb_device_s *dma;
    static uint8_t tx_buf[I2C_BUFFER_SIZE];
    static uint8_t rx_buf[I2C_BUFFER_SIZE];
    
    i2c = bflb_device_get_by_name("i2c0");
    dma = bflb_device_get_by_name("dma");
    
    // Initialize I2C
    bflb_i2c_init(i2c, 400000);
    
    // Enable DMA
    bflb_i2c_link_txdma(i2c, true);
    bflb_i2c_link_rxdma(i2c, true);
    
    // Fill TX buffer
    for (int i = 0; i < I2C_BUFFER_SIZE; i++) {
        tx_buf[i] = i & 0xFF;
    }
    
    // Note: DMA transfer setup would require additional DMA driver calls
    // to configure the DMA channel and trigger the transfer
}
```

---

### Example 6: I2C with Custom Timing

```c
#include "bflb_i2c.h"

void i2c_custom_timing_example(void)
{
    struct bflb_device_s *i2c;
    struct bflb_i2c_timing_s timing;
    
    i2c = bflb_device_get_by_name("i2c0");
    
    // Configure custom timing for 1 MHz operation
    timing.data_phase0 = 5;
    timing.data_phase1 = 5;
    timing.data_phase2 = 5;
    timing.data_phase3 = 5;
    timing.start_phase0 = 10;
    timing.start_phase1 = 10;
    timing.start_phase2 = 10;
    timing.start_phase3 = 10;
    timing.stop_phase0 = 10;
    timing.stop_phase1 = 10;
    timing.stop_phase2 = 10;
    timing.stop_phase3 = 10;
    
    bflb_i2c_feature_control(i2c, I2C_CMD_SET_TIMING, (size_t)&timing);
}
```

---

### Example 7: Multi-Message Transfer (Repeated Start)

```c
#include "bflb_i2c.h"

int i2c_read_register_with_restart(uint8_t slave_addr, uint8_t reg)
{
    struct bflb_device_s *i2c;
    uint8_t value;
    
    i2c = bflb_device_get_by_name("i2c0");
    
    // Write register address, then read value with repeated start
    struct bflb_i2c_msg_s msgs[] = {
        {
            .addr = slave_addr,
            .flags = I2C_M_WRITE | I2C_M_NOSTOP,
            .buffer = &reg,
            .length = 1
        },
        {
            .addr = slave_addr,
            .flags = I2C_M_READ,
            .buffer = &value,
            .length = 1
        }
    };
    
    int ret = bflb_i2c_transfer(i2c, msgs, 2);
    
    if (ret < 0) {
        return ret;
    }
    
    return value;
}
```

---

## Register-Level Reference

### I2C Register Map

| Offset | Register | Description |
|--------|----------|-------------|
| 0x00 | `I2C_CFG` | Configuration register |
| 0x04 | `I2C_TAR` | Target address |
| 0x08 | `I2C_SAR` | Slave address |
| 0x0C | `I2C_HS_MADDR` | High-speed master code |
| 0x10 | `I2C_DATA_CMD` | Data/command register |
| 0x14 | `I2C_SS_SCL_HCNT` | Standard speed SCL high count |
| 0x18 | `I2C_SS_SCL_LCNT` | Standard speed SCL low count |
| 0x1C | `I2C_FS_SCL_HCNT` | Fast speed SCL high count |
| 0x20 | `I2C_FS_SCL_LCNT` | Fast speed SCL low count |
| 0x24 | `I2C_INTR_MASK` | Interrupt mask |
| 0x28 | `I2C_RAW_INTR_STAT` | Raw interrupt status |
| 0x2C | `I2C_RX_TL` | RX FIFO threshold |
| 0x30 | `I2C_TX_TL` | TX FIFO threshold |
| 0x34 | `I2C_CLR_INTR` | Clear interrupt |
| 0x38 | `I2C_CLR_TX_UNDER` | Clear TX underrun |
| 0x3C | `I2C_CLR_TX_OVER` | Clear TX overrun |
| 0x40 | `I2C_CLR_RX_OVER` | Clear RX overrun |
| 0x44 | `I2C_CLR_TX_REQUEST` | Clear TX request |
| 0x48 | `I2C_ENABLE` | I2C enable |
| 0x4C | `I2C_STATUS` | Status register |
| 0x50 | `I2C_TXFLR` | TX FIFO level |
| 0x54 | `I2C_RXFLR` | RX FIFO level |
| 0x58 | `I2C_TX_ABRT_SOURCE` | TX abort source |
| 0x60 | `I2C_SDA_HOLD` | SDA hold time |
| 0x64 | `I2C_TX_TL` | TX threshold |
| 0x68 | `I2C_RX_TL` | RX threshold |

### Timing Calculation

The I2C timing is based on the I2C input clock (typically 40 MHz or 48 MHz APB clock):

```
SCL period = 2 × (SCL_HCNT + SCL_LCNT) × clock_period
```

For 400 KHz Fast mode with 40 MHz clock:
```
SCL_HCNT = 60
SCL_LCNT = 64
```

### SCL Frequency Formula

```
target_freq = clk_freq / (2 × (high_count + low_count + 7))
```

### Clock Stretching

```c
// Enable clock stretching (allow slave to stretch SCL)
bflb_i2c_feature_control(i2c_dev, I2C_CMD_SET_SCL_SYNC, true);
```

### Deglitch Configuration

```c
// Set deglitch count (helps with noisy I2C lines)
bflb_i2c_feature_control(i2c_dev, I2C_CMD_SET_DEGLITCH_CNT, 16);
```
