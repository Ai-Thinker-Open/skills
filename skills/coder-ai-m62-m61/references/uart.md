# UART API Reference (BL616/BL618)

> **Source:** `bouffalo_sdk/drivers/lhal/include/bflb_uart.h`  
> **Register Header:** `bouffalo_sdk/drivers/soc/bl616/std/include/hardware/glb_reg.h`  
> **Base Address:** `UART0_BASE = 0x2000a000`, `UART1_BASE = 0x2000a100`

## Overview

The BL616/BL618 UART peripheral provides full-duplex asynchronous serial communication with:
- Programmable baud rate
- Data bits: 5-8
- Stop bits: 0.5, 1, 1.5, 2
- Parity: None, Odd, Even, Mark, Space
- Hardware flow control (RTS/CTS)
- FIFO: 32 bytes (both TX and RX)
- DMA support
- Auto-baud rate detection

## Base Addresses

| Instance | Base Address |
|----------|-------------|
| UART0 | `0x2000a000` |
| UART1 | `0x2000a100` |

---

## Configuration Constants

### UART Direction

| Constant | Value | Description |
|----------|-------|-------------|
| `UART_DIRECTION_TX` | `1 << 0` | Transmit only |
| `UART_DIRECTION_RX` | `1 << 1` | Receive only |
| `UART_DIRECTION_TXRX` | TX \| RX | Full duplex |

### Data Bits

| Constant | Value | Description |
|----------|-------|-------------|
| `UART_DATA_BITS_5` | 0 | 5 data bits |
| `UART_DATA_BITS_6` | 1 | 6 data bits |
| `UART_DATA_BITS_7` | 2 | 7 data bits |
| `UART_DATA_BITS_8` | 3 | 8 data bits |

### Stop Bits

| Constant | Value | Description |
|----------|-------|-------------|
| `UART_STOP_BITS_0_5` | 0 | 0.5 stop bits |
| `UART_STOP_BITS_1` | 1 | 1 stop bit |
| `UART_STOP_BITS_1_5` | 2 | 1.5 stop bits |
| `UART_STOP_BITS_2` | 3 | 2 stop bits |

### Parity

| Constant | Value | Description |
|----------|-------|-------------|
| `UART_PARITY_NONE` | 0 | No parity |
| `UART_PARITY_ODD` | 1 | Odd parity |
| `UART_PARITY_EVEN` | 2 | Even parity |
| `UART_PARITY_MARK` | 3 | Mark parity |
| `UART_PARITY_SPACE` | 4 | Space parity |

### Bit Order

| Constant | Value | Description |
|----------|-------|-------------|
| `UART_LSB_FIRST` | 0 | LSB transmitted first |
| `UART_MSB_FIRST` | 1 | MSB transmitted first |

### Flow Control

| Constant | Value | Description |
|----------|-------|-------------|
| `UART_FLOWCTRL_NONE` | 0 | No flow control |
| `UART_FLOWCTRL_RTS` | `1 << 0` | RTS only |
| `UART_FLOWCTRL_CTS` | `1 << 1` | CTS only |
| `UART_FLOWCTRL_RTS_CTS` | RTS \| CTS | Full RTS/CTS |

### Interrupt Status Flags

| Constant | Value | Description |
|----------|-------|-------------|
| `UART_INTSTS_TX_END` | `1 << 0` | TX transfer complete |
| `UART_INTSTS_RX_END` | `1 << 1` | RX transfer complete |
| `UART_INTSTS_TX_FIFO` | `1 << 2` | TX FIFO threshold reached |
| `UART_INTSTS_RX_FIFO` | `1 << 3` | RX FIFO threshold reached |
| `UART_INTSTS_RTO` | `1 << 4` | RX timeout |
| `UART_INTSTS_PCE` | `1 << 5` | Parity check error |
| `UART_INTSTS_TX_FER` | `1 << 6` | TX frame error |
| `UART_INTSTS_RX_FER` | `1 << 7` | RX frame error |
| `UART_INTSTS_RX_LSE` | `1 << 8` | RX LIN sync error |
| `UART_INTSTS_RX_BCR` | `1 << 9` | RX break character |
| `UART_INTSTS_RX_ADS` | `1 << 10` | Auto baud done |
| `UART_INTSTS_RX_AD5` | `1 << 11` | Auto baud 0x55 done |

### Interrupt Clear Flags

| Constant | Value | Description |
|----------|-------|-------------|
| `UART_INTCLR_TX_END` | `1 << 0` | Clear TX end interrupt |
| `UART_INTCLR_RX_END` | `1 << 1` | Clear RX end interrupt |
| `UART_INTCLR_RTO` | `1 << 4` | Clear RX timeout interrupt |
| `UART_INTCLR_PCE` | `1 << 5` | Clear parity error interrupt |

### Feature Control Commands

| Command | Description |
|---------|-------------|
| `UART_CMD_SET_BAUD_RATE` | Set baud rate |
| `UART_CMD_SET_DATA_BITS` | Set data bits |
| `UART_CMD_SET_STOP_BITS` | Set stop bits |
| `UART_CMD_SET_PARITY_BITS` | Set parity |
| `UART_CMD_CLR_TX_FIFO` | Clear TX FIFO |
| `UART_CMD_CLR_RX_FIFO` | Clear RX FIFO |
| `UART_CMD_SET_RTO_VALUE` | Set RX timeout value |
| `UART_CMD_SET_RTS_VALUE` | Set RTS pin value |
| `UART_CMD_GET_TX_FIFO_CNT` | Get TX FIFO count |
| `UART_CMD_GET_RX_FIFO_CNT` | Get RX FIFO count |
| `UART_CMD_SET_AUTO_BAUD` | Configure auto baud |
| `UART_CMD_SET_BREAK_VALUE` | Set break character |
| `UART_CMD_SET_TX_LIN_VALUE` | Set LIN TX value |
| `UART_CMD_SET_RX_LIN_VALUE` | Set LIN RX value |
| `UART_CMD_SET_DEGLITCH_CNT` | Set deglitch count |
| `UART_CMD_SET_TX_RS485_EN` | Enable RS485 TX |
| `UART_CMD_SET_TX_FIFO_THREHOLD` | Set TX FIFO threshold |
| `UART_CMD_SET_RX_FIFO_THREHOLD` | Set RX FIFO threshold |

### UART Configuration Structure

```c
struct bflb_uart_config_s {
    uint32_t baudrate;          // Baud rate in bps
    uint8_t direction;          // Direction (TX/RX/TXRX)
    uint8_t data_bits;          // Data bits
    uint8_t stop_bits;          // Stop bits
    uint8_t parity;             // Parity
    uint8_t bit_order;          // Bit order
    uint8_t flow_ctrl;           // Flow control
    uint8_t tx_fifo_threshold;   // TX FIFO threshold
    uint8_t rx_fifo_threshold;   // RX FIFO threshold
};
```

### IR Configuration Structure

```c
struct bflb_uart_ir_config_s {
    bool tx_en;            // TX enable
    bool rx_en;            // RX enable
    bool tx_inverse;       // TX invert
    bool rx_inverse;       // RX invert
    uint16_t tx_pluse_start;  // TX pulse start
    uint16_t tx_pluse_stop;   // TX pulse stop
    uint16_t rx_pluse_start;  // RX pulse start
};
```

---

## LHAL API Functions

### bflb_uart_init

Initialize UART with configuration.

```c
void bflb_uart_init(struct bflb_device_s *dev, const struct bflb_uart_config_s *config);
```

**Example:**
```c
struct bflb_uart_config_s config = {
    .baudrate = 115200,
    .direction = UART_DIRECTION_TXRX,
    .data_bits = UART_DATA_BITS_8,
    .stop_bits = UART_STOP_BITS_1,
    .parity = UART_PARITY_NONE,
    .bit_order = UART_LSB_FIRST,
    .flow_ctrl = UART_FLOWCTRL_NONE,
    .tx_fifo_threshold = 0,
    .rx_fifo_threshold = 0,
};
bflb_uart_init(uart_dev, &config);
```

---

### bflb_uart_deinit

Deinitialize UART.

```c
void bflb_uart_deinit(struct bflb_device_s *dev);
```

---

### bflb_uart_enable / bflb_uart_disable

Enable or disable UART.

```c
void bflb_uart_enable(struct bflb_device_s *dev);
void bflb_uart_disable(struct bflb_device_s *dev);
```

---

### bflb_uart_link_txdma / bflb_uart_link_rxdma

Enable UART DMA for TX/RX.

```c
void bflb_uart_link_txdma(struct bflb_device_s *dev, bool enable);
void bflb_uart_link_rxdma(struct bflb_device_s *dev, bool enable);
```

---

### bflb_uart_putchar

Send a single character (blocking).

```c
int bflb_uart_putchar(struct bflb_device_s *dev, int ch);
```

**Returns:** 0 on success, negative errno on failure

---

### bflb_uart_getchar

Receive a single character (blocking).

```c
int bflb_uart_getchar(struct bflb_device_s *dev);
```

**Returns:** Received character, or negative errno on failure

---

### bflb_uart_put

Send a block of data (polling).

```c
int bflb_uart_put(struct bflb_device_s *dev, uint8_t *data, uint32_t len);
```

**Returns:** 0 on success, negative errno on failure

---

### bflb_uart_put_block

Send a block of data and wait until complete.

```c
int bflb_uart_put_block(struct bflb_device_s *dev, uint8_t *data, uint32_t len);
```

**Returns:** 0 on success, negative errno on failure

---

### bflb_uart_get

Receive data asynchronously.

```c
int bflb_uart_get(struct bflb_device_s *dev, uint8_t *data, uint32_t len);
```

**Returns:** Actual number of bytes received

---

### bflb_uart_wait_tx_done

Wait for TX transfer to complete.

```c
int bflb_uart_wait_tx_done(struct bflb_device_s *dev);
```

**Returns:** 0 on success, negative errno on failure

---

### bflb_uart_txready

Check if TX hardware is ready for another byte.

```c
bool bflb_uart_txready(struct bflb_device_s *dev);
```

**Returns:** `true` if ready, `false` otherwise

---

### bflb_uart_txempty

Check if TX FIFO is empty.

```c
bool bflb_uart_txempty(struct bflb_device_s *dev);
```

**Returns:** `true` if all data sent, `false` otherwise

---

### bflb_uart_rxavailable

Check if RX data is available.

```c
bool bflb_uart_rxavailable(struct bflb_device_s *dev);
```

**Returns:** `true` if data in RX FIFO

---

### bflb_uart_txint_mask / bflb_uart_rxint_mask / bflb_uart_errint_mask

Enable/disable UART interrupts.

```c
void bflb_uart_txint_mask(struct bflb_device_s *dev, bool mask);
void bflb_uart_rxint_mask(struct bflb_device_s *dev, bool mask);
void bflb_uart_errint_mask(struct bflb_device_s *dev, bool mask);
```

**Parameters:** `mask = true` disables interrupt, `false` enables

---

### bflb_uart_get_intstatus

Get interrupt status.

```c
uint32_t bflb_uart_get_intstatus(struct bflb_device_s *dev);
```

**Returns:** Bitmask of active interrupt flags

---

### bflb_uart_int_clear

Clear interrupt flags.

```c
void bflb_uart_int_clear(struct bflb_device_s *dev, uint32_t int_clear);
```

---

### bflb_uart_feature_control

Control UART special features.

```c
int bflb_uart_feature_control(struct bflb_device_s *dev, int cmd, size_t arg);
```

---

## Usage Examples

### Example 1: Basic TX/RX

```c
#include "bflb_uart.h"

void uart_basic_example(void)
{
    struct bflb_device_s *uart;
    
    // Get UART0 device
    uart = bflb_device_get_by_name("uart0");
    
    // Configure UART
    struct bflb_uart_config_s config = {
        .baudrate = 115200,
        .direction = UART_DIRECTION_TXRX,
        .data_bits = UART_DATA_BITS_8,
        .stop_bits = UART_STOP_BITS_1,
        .parity = UART_PARITY_NONE,
        .bit_order = UART_LSB_FIRST,
        .flow_ctrl = UART_FLOWCTRL_NONE,
        .tx_fifo_threshold = 0,
        .rx_fifo_threshold = 0,
    };
    bflb_uart_init(uart, &config);
    bflb_uart_enable(uart);
    
    // Send string
    uint8_t msg[] = "Hello UART!\r\n";
    bflb_uart_put(uart, msg, sizeof(msg) - 1);
    
    // Receive character
    int ch = bflb_uart_getchar(uart);
    if (ch >= 0) {
        // Echo character
        bflb_uart_putchar(uart, ch);
    }
}
```

### Example 2: Interrupt-Driven RX

```c
#include "bflb_uart.h"
#include "bflb_irq.h"

static uint8_t rx_buffer[256];
static volatile uint32_t rx_count;

void uart_rx_isr(struct bflb_device_s *dev, uint32_t int_status)
{
    if (int_status & UART_INTSTS_RX_FIFO) {
        // Read available bytes
        while (bflb_uart_rxavailable(dev)) {
            int ch = bflb_uart_getchar(dev);
            if (ch >= 0 && rx_count < sizeof(rx_buffer)) {
                rx_buffer[rx_count++] = ch;
            }
        }
    }
    
    // Clear interrupts
    bflb_uart_int_clear(dev, int_status);
}

void uart_interrupt_example(void)
{
    struct bflb_device_s *uart;
    
    uart = bflb_device_get_by_name("uart0");
    
    struct bflb_uart_config_s config = {
        .baudrate = 115200,
        .direction = UART_DIRECTION_TXRX,
        .data_bits = UART_DATA_BITS_8,
        .stop_bits = UART_STOP_BITS_1,
        .parity = UART_PARITY_NONE,
        .bit_order = UART_LSB_FIRST,
        .flow_ctrl = UART_FLOWCTRL_NONE,
        .tx_fifo_threshold = 0,
        .rx_fifo_threshold = 0,
    };
    bflb_uart_init(uart, &config);
    
    // Setup interrupt
    bflb_irq_register(UART0_IRQn, uart_rx_isr);
    bflb_uart_rxint_mask(uart, false);  // Enable RX interrupt
    
    bflb_uart_enable(uart);
}
```

### Example 3: DMA Transfer

```c
#include "bflb_uart.h"

#define TX_BUFFER_SIZE 1024
static uint8_t tx_buffer[TX_BUFFER_SIZE];

void uart_dma_example(void)
{
    struct bflb_device_s *uart;
    struct bflb_device_s *dma;
    
    uart = bflb_device_get_by_name("uart0");
    dma = bflb_device_get_by_name("dma");
    
    struct bflb_uart_config_s config = {
        .baudrate = 115200,
        .direction = UART_DIRECTION_TXRX,
        .data_bits = UART_DATA_BITS_8,
        .stop_bits = UART_STOP_BITS_1,
        .parity = UART_PARITY_NONE,
        .bit_order = UART_LSB_FIRST,
        .flow_ctrl = UART_FLOWCTRL_NONE,
        .tx_fifo_threshold = 0,
        .rx_fifo_threshold = 0,
    };
    bflb_uart_init(uart, &config);
    
    // Enable DMA
    bflb_uart_link_txdma(uart, true);
    bflb_uart_link_rxdma(uart, true);
    
    bflb_uart_enable(uart);
    
    // Fill buffer with data
    for (int i = 0; i < TX_BUFFER_SIZE; i++) {
        tx_buffer[i] = i & 0xFF;
    }
    
    // DMA transfer would be initiated via DMA driver
    // ...
}
```

### Example 4: Modbus RTU (8N1 at 9600)

```c
void uart_modbus_example(void)
{
    struct bflb_device_s *uart;
    
    uart = bflb_device_get_by_name("uart0");
    
    struct bflb_uart_config_s config = {
        .baudrate = 9600,
        .direction = UART_DIRECTION_TXRX,
        .data_bits = UART_DATA_BITS_8,
        .stop_bits = UART_STOP_BITS_1,
        .parity = UART_PARITY_NONE,
        .bit_order = UART_LSB_FIRST,
        .flow_ctrl = UART_FLOWCTRL_NONE,
        .tx_fifo_threshold = 0,
        .rx_fifo_threshold = 0,
    };
    bflb_uart_init(uart, &config);
    bflb_uart_enable(uart);
    
    // Send Modbus query
    uint8_t query[] = {0x01, 0x03, 0x00, 0x00, 0x00, 0x0A, 0xC5, 0xCD};
    bflb_uart_put(uart, query, sizeof(query));
    
    // Wait and receive response
    bflb_mtimer_delay_ms(50);
    
    uint8_t response[64];
    int len = bflb_uart_get(uart, response, sizeof(response));
    
    if (len > 0) {
        // Process Modbus response
    }
}
```

---

## Auto-Baud Rate Detection

```c
void uart_autobaud_example(void)
{
    struct bflb_device_s *uart;
    
    uart = bflb_device_get_by_name("uart0");
    
    struct bflb_uart_config_s config = {
        .baudrate = 115200,  // Initial baud rate for autobaud
        .direction = UART_DIRECTION_TXRX,
        .data_bits = UART_DATA_BITS_8,
        .stop_bits = UART_STOP_BITS_1,
        .parity = UART_PARITY_NONE,
        .bit_order = UART_LSB_FIRST,
        .flow_ctrl = UART_FLOWCTRL_NONE,
        .tx_fifo_threshold = 0,
        .rx_fifo_threshold = 0,
    };
    bflb_uart_init(uart, &config);
    
    // Enable auto-baud with 0x55 pattern
    bflb_uart_feature_control(uart, UART_CMD_SET_AUTO_BAUD, UART_AUTO_BAUD_0X55);
    
    // Wait for auto-baud to complete
    while (!(bflb_uart_get_intstatus(uart) & UART_INTSTS_RX_ADS)) {
        bflb_mtimer_delay_ms(1);
    }
    
    // Read detected baud rate
    uint32_t baudrate;
    bflb_uart_feature_control(uart, UART_CMD_GET_AUTO_BAUD, (size_t)&baudrate);
    
    printf("Detected baud rate: %u\r\n", baudrate);
}
```

---

## Register-Level Reference

### UART Register Map

| Offset | Register | Description |
|--------|----------|-------------|
| 0x00 | `UART_RXD` | RX data register (read) |
| 0x04 | `UART_TXD` | TX data register (write) |
| 0x08 | `UART_TXCFG` | TX configuration |
| 0x0C | `UART_RXCFG` | RX configuration |
| 0x10 | `UART_CTRL` | Control register |
| 0x14 | `UART_INTSTS` | Interrupt status |
| 0x18 | `UART_INTCLR` | Interrupt clear |
| 0x1C | `UART_INTMASK` | Interrupt mask |
| 0x20 | `UART_BAUD` | Baud rate divisor |
| 0x24 | `UART_AUTOBAUD` | Auto-baud control |
| 0x28 | `UART_FIFO_CONFIG_0` | FIFO configuration 0 |
| 0x2C | `UART_FIFO_CONFIG_1` | FIFO configuration 1 |
| 0x30 | `UART_FIFO_DATA` | FIFO data |
| 0x34 | `UART_TIMEOUT` | RX timeout config |
| 0x38 | `UART_GLITCH` | De-glitch config |
| 0x3C | `UART_RS485` | RS485 control |

### Baud Rate Calculation

```
baud_rate = uart_clk / ( baud_div + 1 )
```

For example, with 40MHz uart_clk and 115200 baud:
```
baud_div = 40000000 / 115200 - 1 = 346
```

### Setting Baud Rate via Feature Control

```c
void uart_set_baudrate(struct bflb_device_s *uart, uint32_t baudrate)
{
    bflb_uart_feature_control(uart, UART_CMD_SET_BAUD_RATE, baudrate);
}
```
