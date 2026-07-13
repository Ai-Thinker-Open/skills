# SPI API Reference (BL616/BL618)

> **Source:** `bouffalo_sdk/drivers/lhal/include/bflb_spi.h`  
> **Base Address:** `SPI_BASE = 0x2000a200`

## Overview

The BL616/BL618 SPI peripheral provides full-duplex synchronous serial communication:
- Master and Slave modes
- Configurable data width: 8, 16, 24, 32 bits
- SPI modes: 0, 1, 2, 3 (CPOL/CPHA combinations)
- Programmable bit order (MSB/LSB first)
- Programmable byte order
- FIFO: 32 bytes
- DMA support
- Configurable CS interval

## Base Address

| Instance | Base Address |
|----------|-------------|
| SPI | `0x2000a200` |

---

## Configuration Constants

### SPI Role

| Constant | Value | Description |
|----------|-------|-------------|
| `SPI_ROLE_MASTER` | 0 | Master mode |
| `SPI_ROLE_SLAVE` | 1 | Slave mode |

### SPI Mode (CPOL/CPHA)

| Constant | Value | CPOL | CPHA | Description |
|----------|-------|------|------|-------------|
| `SPI_MODE0` | 0 | 0 | 0 | Clock idle low, sample on first edge |
| `SPI_MODE1` | 1 | 0 | 1 | Clock idle low, sample on second edge |
| `SPI_MODE2` | 2 | 1 | 0 | Clock idle high, sample on first edge |
| `SPI_MODE3` | 3 | 1 | 1 | Clock idle high, sample on second edge |

### Data Width

| Constant | Value | Description |
|----------|-------|-------------|
| `SPI_DATA_WIDTH_8BIT` | 1 | 8-bit data |
| `SPI_DATA_WIDTH_16BIT` | 2 | 16-bit data |
| `SPI_DATA_WIDTH_24BIT` | 3 | 24-bit data |
| `SPI_DATA_WIDTH_32BIT` | 4 | 32-bit data |

### Bit Order

| Constant | Value | Description |
|----------|-------|-------------|
| `SPI_BIT_LSB` | 1 | LSB transmitted first |
| `SPI_BIT_MSB` | 0 | MSB transmitted first |

### Byte Order

| Constant | Value | Description |
|----------|-------|-------------|
| `SPI_BYTE_LSB` | 0 | Lowest byte first |
| `SPI_BYTE_MSB` | 1 | Highest byte first |

### Interrupt Status Flags

| Constant | Value | Description |
|----------|-------|-------------|
| `SPI_INTSTS_TC` | `1 << 0` | Transfer complete |
| `SPI_INTSTS_TX_FIFO` | `1 << 1` | TX FIFO ready |
| `SPI_INTSTS_RX_FIFO` | `1 << 2` | RX FIFO ready |
| `SPI_INTSTS_RTO` | `1 << 3` | RX timeout |
| `SPI_INTSTS_SLAVE_TX_UNDERRUN` | `1 << 4` | Slave TX underrun |
| `SPI_INTSTS_FIFO_ERR` | `1 << 5` | FIFO error |

### Interrupt Clear Flags

| Constant | Value | Description |
|----------|-------|-------------|
| `SPI_INTCLR_TC` | `1 << 16` | Clear TC interrupt |
| `SPI_INTCLR_SLAVE_TIMEOUT` | `1 << 19` | Clear slave timeout |
| `SPI_INTCLR_SLAVE_TX_UNDERRUN` | `1 << 20` | Clear TX underrun |

### FIFO Error Flags

| Constant | Value | Description |
|----------|-------|-------------|
| `SPI_FIFO_ERROR_FLAG_TX_OVERFLOW` | `1 << 0` | TX FIFO overflow |
| `SPI_FIFO_ERROR_FLAG_TX_UNDERFLOW` | `1 << 1` | TX FIFO underflow |
| `SPI_FIFO_ERROR_FLAG_RX_OVERFLOW` | `1 << 2` | RX FIFO overflow |
| `SPI_FIFO_ERROR_FLAG_RX_UNDERFLOW` | `1 << 3` | RX FIFO underflow |

### Feature Control Commands

| Command | Description |
|---------|-------------|
| `SPI_CMD_SET_DATA_WIDTH` | Set data width |
| `SPI_CMD_GET_DATA_WIDTH` | Get data width |
| `SPI_CMD_CLEAR_TX_FIFO` | Clear TX FIFO |
| `SPI_CMD_CLEAR_RX_FIFO` | Clear RX FIFO |
| `SPI_CMD_SET_CS_INTERVAL` | Set CS interval |
| `SPI_CMD_RX_IGNORE_ENABLE` | Enable RX ignore |
| `SPI_CMD_SET_MODE` | Set SPI mode |
| `SPI_CMD_GET_MODE` | Get SPI mode |
| `SPI_CMD_SET_FREQ` | Set frequency |
| `SPI_CMD_GET_FREQ` | Get frequency |
| `SPI_CMD_SET_BIT_ORDER` | Set bit order |
| `SPI_CMD_GET_BIT_ORDER` | Get bit order |
| `SPI_CMD_SET_BYTE_ORDER` | Set byte order |
| `SPI_CMD_GET_BYTE_ORDER` | Get byte order |
| `SPI_CMD_SET_DEGLITCH_CNT` | Set deglitch count |
| `SPI_CMD_SET_CS_DISABLE` | Disable CS |
| `SPI_CMD_SET_ROLE` | Set master/slave |
| `SPI_CMD_GET_ROLE` | Get master/slave |
| `SPI_CMD_READ_FIFO_ERROR_FLAG` | Read FIFO errors |

### Default Idle Data

```c
#ifndef BFLB_SPI_IDEL_DATA
#define BFLB_SPI_IDEL_DATA 0xFFFFFFFF
#endif
```

### SPI Configuration Structure

```c
struct bflb_spi_config_s {
    uint32_t freq;                // Frequency in Hz (must be < spi_clk/2)
    uint8_t role;                 // Master or Slave
    uint8_t mode;                 // SPI mode (0-3)
    uint8_t data_width;           // Data width (SPI_DATA_WIDTH_*)
    uint8_t bit_order;            // Bit order (MSB/LSB first)
    uint8_t byte_order;           // Byte order
    uint8_t tx_fifo_threshold;    // TX FIFO threshold (0-3)
    uint8_t rx_fifo_threshold;     // RX FIFO threshold (0-3)
};
```

---

## LHAL API Functions

### bflb_spi_init

Initialize SPI with configuration.

```c
void bflb_spi_init(struct bflb_device_s *dev, const struct bflb_spi_config_s *config);
```

**Example:**
```c
struct bflb_spi_config_s config = {
    .freq = 1000000,          // 1 MHz
    .role = SPI_ROLE_MASTER,
    .mode = SPI_MODE0,
    .data_width = SPI_DATA_WIDTH_8BIT,
    .bit_order = SPI_BIT_MSB,
    .byte_order = SPI_BYTE_MSB,
    .tx_fifo_threshold = 0,
    .rx_fifo_threshold = 0,
};
bflb_spi_init(spi_dev, &config);
```

---

### bflb_spi_deinit

Deinitialize SPI.

```c
void bflb_spi_deinit(struct bflb_device_s *dev);
```

---

### bflb_spi_link_txdma / bflb_spi_link_rxdma

Enable SPI DMA for TX/RX.

```c
void bflb_spi_link_txdma(struct bflb_device_s *dev, bool enable);
void bflb_spi_link_rxdma(struct bflb_device_s *dev, bool enable);
```

---

### bflb_spi_poll_send

Send and receive one data word (blocking).

```c
uint32_t bflb_spi_poll_send(struct bflb_device_s *dev, uint32_t data);
```

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `dev` | `struct bflb_device_s *` | Device handle |
| `data` | `uint32_t` | Data to send |

**Returns:** Received data

---

### bflb_spi_poll_exchange

Exchange a block of data (blocking).

```c
int bflb_spi_poll_exchange(struct bflb_device_s *dev, const void *txbuffer, void *rxbuffer, size_t nbytes);
```

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `dev` | `struct bflb_device_s *` | Device handle |
| `txbuffer` | `const void *` | TX data buffer |
| `rxbuffer` | `void *` | RX data buffer |
| `nbytes` | `size_t` | Number of bytes |

**Returns:** 0 on success, negative errno on failure

---

### bflb_spi_isbusy

Check if SPI is busy.

```c
bool bflb_spi_isbusy(struct bflb_device_s *dev);
```

**Returns:** `true` if busy, `false` if idle

---

### bflb_spi_txint_mask / bflb_spi_rxint_mask / bflb_spi_tcint_mask / bflb_spi_errint_mask / bflb_spi_rtoint_mask

Enable/disable SPI interrupts.

```c
void bflb_spi_txint_mask(struct bflb_device_s *dev, bool mask);
void bflb_spi_rxint_mask(struct bflb_device_s *dev, bool mask);
void bflb_spi_tcint_mask(struct bflb_device_s *dev, bool mask);
void bflb_spi_errint_mask(struct bflb_device_s *dev, bool mask);
void bflb_spi_rtoint_mask(struct bflb_device_s *dev, bool mask);
```

**Parameters:** `mask = true` disables interrupt, `false` enables

---

### bflb_spi_get_intstatus

Get interrupt status.

```c
uint32_t bflb_spi_get_intstatus(struct bflb_device_s *dev);
```

**Returns:** Bitmask of active interrupt flags

---

### bflb_spi_int_clear

Clear interrupt flags.

```c
void bflb_spi_int_clear(struct bflb_device_s *dev, uint32_t int_clear);
```

---

### bflb_spi_feature_control

Control SPI special features.

```c
int bflb_spi_feature_control(struct bflb_device_s *dev, int cmd, size_t arg);
```

---

## Usage Examples

### Example 1: Master Mode - Read/Write Flash

```c
#include "bflb_spi.h"

#define FLASH_READ_CMD    0x03
#define FLASH_WRITE_CMD   0x02
#define FLASH_STATUS_CMD  0x05

void spi_flash_example(void)
{
    struct bflb_device_s *spi;
    
    spi = bflb_device_get_by_name("spi");
    
    // Configure SPI master
    struct bflb_spi_config_s config = {
        .freq = 40000000,          // 40 MHz (max for most flash)
        .role = SPI_ROLE_MASTER,
        .mode = SPI_MODE0,
        .data_width = SPI_DATA_WIDTH_8BIT,
        .bit_order = SPI_BIT_MSB,
        .byte_order = SPI_BYTE_MSB,
        .tx_fifo_threshold = 0,
        .rx_fifo_threshold = 0,
    };
    bflb_spi_init(spi, &config);
    
    // Read flash ID
    uint8_t tx_buf[4] = {0x9F, 0, 0, 0};
    uint8_t rx_buf[4] = {0};
    
    bflb_spi_poll_exchange(spi, tx_buf, rx_buf, 4);
    
    printf("Flash JEDEC ID: %02X %02X %02X\r\n", rx_buf[1], rx_buf[2], rx_buf[3]);
    
    // Read status register
    tx_buf[0] = FLASH_STATUS_CMD;
    tx_buf[1] = 0;
    bflb_spi_poll_exchange(spi, tx_buf, rx_buf, 2);
    
    printf("Status: 0x%02X\r\n", rx_buf[1]);
    
    // Read 256 bytes from address 0x0000
    uint32_t addr = 0x0000;
    uint8_t read_cmd[4] = {FLASH_READ_CMD, (addr >> 16) & 0xFF, (addr >> 8) & 0xFF, addr & 0xFF};
    uint8_t data[256];
    
    // Assert CS (handled by driver)
    bflb_spi_poll_exchange(spi, read_cmd, NULL, 4);  // Send command
    bflb_spi_poll_exchange(spi, NULL, data, 256);      // Receive data
}
```

### Example 2: Master Mode - 16-bit Data Width

```c
#include "bflb_spi.h"

void spi_16bit_example(void)
{
    struct bflb_device_s *spi;
    
    spi = bflb_device_get_by_name("spi");
    
    // Configure SPI with 16-bit data width
    struct bflb_spi_config_s config = {
        .freq = 10000000,
        .role = SPI_ROLE_MASTER,
        .mode = SPI_MODE3,
        .data_width = SPI_DATA_WIDTH_16BIT,
        .bit_order = SPI_BIT_MSB,
        .byte_order = SPI_BYTE_MSB,
        .tx_fifo_threshold = 0,
        .rx_fifo_threshold = 0,
    };
    bflb_spi_init(spi, &config);
    
    // Send 16-bit values
    uint16_t tx_data = 0xABCD;
    uint16_t rx_data = bflb_spi_poll_send(spi, tx_data);
    
    printf("Sent: 0x%04X, Received: 0x%04X\r\n", tx_data, rx_data);
}
```

### Example 3: Interrupt-Driven SPI

```c
#include "bflb_spi.h"
#include "bflb_irq.h"

static volatile bool spi_transfer_done = false;
static uint8_t rx_buf[256];

void spi_isr(struct bflb_device_s *dev, uint32_t int_status)
{
    if (int_status & SPI_INTSTS_TC) {
        spi_transfer_done = true;
    }
    
    if (int_status & SPI_INTSTS_FIFO_ERR) {
        // Read and clear FIFO errors
        uint32_t errors = bflb_spi_feature_control(dev, SPI_CMD_READ_FIFO_ERROR_FLAG, 0);
        printf("SPI FIFO errors: 0x%08X\r\n", errors);
    }
    
    bflb_spi_int_clear(dev, int_status);
}

void spi_interrupt_example(void)
{
    struct bflb_device_s *spi;
    
    spi = bflb_device_get_by_name("spi");
    
    struct bflb_spi_config_s config = {
        .freq = 8000000,
        .role = SPI_ROLE_MASTER,
        .mode = SPI_MODE0,
        .data_width = SPI_DATA_WIDTH_8BIT,
        .bit_order = SPI_BIT_MSB,
        .byte_order = SPI_BYTE_MSB,
        .tx_fifo_threshold = 0,
        .rx_fifo_threshold = 0,
    };
    bflb_spi_init(spi, &config);
    
    // Register interrupt handler
    bflb_irq_register(SPI0_IRQn, spi_isr);
    
    // Enable transfer complete interrupt
    bflb_spi_tcint_mask(spi, false);
    
    // Enable error interrupt
    bflb_spi_errint_mask(spi, false);
    
    // Perform exchange
    uint8_t tx_buf[256];
    for (int i = 0; i < 256; i++) {
        tx_buf[i] = i;
    }
    
    spi_transfer_done = false;
    bflb_spi_poll_exchange(spi, tx_buf, rx_buf, 256);
    
    // Wait for completion
    while (!spi_transfer_done) {
        // Could use proper RTOS delay here
    }
    
    printf("Transfer complete\r\n");
}
```

### Example 4: DMA SPI Transfer

```c
#include "bflb_spi.h"

#define SPI_BUFFER_SIZE 1024

void spi_dma_example(void)
{
    struct bflb_device_s *spi;
    struct bflb_device_s *dma;
    
    spi = bflb_device_get_by_name("spi");
    dma = bflb_device_get_by_name("dma");
    
    struct bflb_spi_config_s config = {
        .freq = 20000000,
        .role = SPI_ROLE_MASTER,
        .mode = SPI_MODE0,
        .data_width = SPI_DATA_WIDTH_8BIT,
        .bit_order = SPI_BIT_MSB,
        .byte_order = SPI_BYTE_MSB,
        .tx_fifo_threshold = 0,
        .rx_fifo_threshold = 0,
    };
    bflb_spi_init(spi, &config);
    
    // Enable DMA
    bflb_spi_link_txdma(spi, true);
    bflb_spi_link_rxdma(spi, true);
    
    // Note: DMA channel configuration and initiation would be done
    // through the DMA driver, not the SPI driver directly.
    // This is a simplified example showing DMA linkage.
}
```

### Example 5: Slave Mode

```c
#include "bflb_spi.h"

void spi_slave_example(void)
{
    struct bflb_device_s *spi;
    
    spi = bflb_device_get_by_name("spi");
    
    // Configure as slave
    struct bflb_spi_config_s config = {
        .freq = 0,  // Ignored for slave
        .role = SPI_ROLE_SLAVE,
        .mode = SPI_MODE1,  // Match master's mode
        .data_width = SPI_DATA_WIDTH_8BIT,
        .bit_order = SPI_BIT_MSB,
        .byte_order = SPI_BYTE_MSB,
        .tx_fifo_threshold = 0,
        .rx_fifo_threshold = 0,
    };
    bflb_spi_init(spi, &config);
    
    // Prepare TX data
    uint8_t tx_data = 0xAA;
    uint8_t rx_data;
    
    // Exchange data (blocking)
    rx_data = bflb_spi_poll_send(spi, tx_data);
    
    printf("Slave received: 0x%02X\r\n", rx_data);
}
```

---

## Register-Level Reference

### SPI Register Map

| Offset | Register | Description |
|--------|----------|-------------|
| 0x00 | `SPI_GLB` | Global control |
| 0x04 | `SPI_RXD` | RX data |
| 0x08 | `SPI_TXD` | TX data |
| 0x0C | `SPI_FIFO_RDATA` | FIFO read data |
| 0x10 | `SPI_FIFO_WDATA` | FIFO write data |
| 0x14 | `SPI_INT_STS` | Interrupt status |
| 0x18 | `SPI_INT_MASK` | Interrupt mask |
| 0x1C | `SPI_INT_CLR` | Interrupt clear |
| 0x20 | `SPI_FIFO_CFG` | FIFO configuration |
| 0x24 | `SPI_FIFO_STS` | FIFO status |
| 0x28 | `SPI_FIFO_INT_STS` | FIFO interrupt status |
| 0x2C | `SPI_FIFO_INT_MASK` | FIFO interrupt mask |
| 0x30 | `SPI_FIFO_INT_CLR` | FIFO interrupt clear |
| 0x34 | `SPI_BUS_BUSY` | Bus busy status |
| 0x38 | `SPI_MODE` | SPI mode config |
| 0x3C | `SPI_CS_CTRL` | Chip select control |
| 0x40 | `SPI_CMD` | Command register |
| 0x44 | `SPI_SLAVE_CMD` | Slave command |
| 0x48 | `SPI_TRIG` | Trigger control |
| 0x4C | `SPI_TIMEOUT` | Timeout config |

### Clock Configuration

The SPI frequency is derived from the APB clock. The divisor is set through the feature control:

```c
// Set 10 MHz SPI clock
bflb_spi_feature_control(spi_dev, SPI_CMD_SET_FREQ, 10000000);
```

### CS Timing Control

```c
// Set CS interval (in SPI clock cycles)
bflb_spi_feature_control(spi_dev, SPI_CMD_SET_CS_INTERVAL, 16);
```

### FIFO Threshold Configuration

```c
// Configure FIFO thresholds
struct bflb_spi_config_s config = {
    // ... other settings
    .tx_fifo_threshold = 3,  // Trigger when 3+ bytes in TX FIFO
    .rx_fifo_threshold = 3,  // Trigger when 3+ bytes in RX FIFO
};
```
