# UART API Reference

> Source file: `components/platform/hosal/include/hosal_uart.h`

## Macros

```c
#define HOSAL_UART_AUTOBAUD_0X55     1   // Auto baud detection using 0x55
#define HOSAL_UART_AUTOBAUD_STARTBIT 2   // Auto detection using start bit

// Callback types
#define HOSAL_UART_TX_CALLBACK       1   // TX idle interrupt callback
#define HOSAL_UART_RX_CALLBACK       2   // RX complete callback
#define HOSAL_UART_TX_DMA_CALLBACK   3   // TX DMA complete callback
#define HOSAL_UART_RX_DMA_CALLBACK   4   // RX DMA complete callback

// ioctl control commands
#define HOSAL_UART_BAUD_SET          1
#define HOSAL_UART_BAUD_GET          2
#define HOSAL_UART_DATA_WIDTH_SET    3
#define HOSAL_UART_DATA_WIDTH_GET    4
#define HOSAL_UART_STOP_BITS_SET     5
#define HOSAL_UART_STOP_BITS_GET     6
#define HOSAL_UART_FLOWMODE_SET      7
#define HOSAL_UART_FLOWSTAT_GET      8
#define HOSAL_UART_PARITY_SET        9
#define HOSAL_UART_PARITY_GET       10
#define HOSAL_UART_MODE_SET         11
#define HOSAL_UART_MODE_GET         12
#define HOSAL_UART_FREE_TXFIFO_GET  13
#define HOSAL_UART_FREE_RXFIFO_GET  14
#define HOSAL_UART_FLUSH            15
#define HOSAL_UART_TX_TRIGGER_ON    16
#define HOSAL_UART_TX_TRIGGER_OFF   17
#define HOSAL_UART_DMA_TX_START     18
#define HOSAL_UART_DMA_RX_START     19
```

## Type Definitions

### `hosal_uart_data_width_t` — Data Width

```c
typedef enum {
    HOSAL_DATA_WIDTH_5BIT,
    HOSAL_DATA_WIDTH_6BIT,
    HOSAL_DATA_WIDTH_7BIT,
    HOSAL_DATA_WIDTH_8BIT,  // Common
    HOSAL_DATA_WIDTH_9BIT
} hosal_uart_data_width_t;
```

### `hosal_uart_stop_bits_t` — Stop Bits

```c
typedef enum {
    HOSAL_STOP_BITS_1,      // 1 stop bit (common)
    HOSAL_STOP_BITS_1_5,   // 1.5 stop bits
    HOSAL_STOP_BITS_2       // 2 stop bits
} hosal_uart_stop_bits_t;
```

### `hosal_uart_parity_t` — Parity

```c
typedef enum {
    HOSAL_NO_PARITY,        // No parity (common)
    HOSAL_ODD_PARITY,      // Odd parity
    HOSAL_EVEN_PARITY      // Even parity
} hosal_uart_parity_t;
```

### `hosal_uart_flow_control_t` — Flow Control

```c
typedef enum {
    HOSAL_FLOW_CONTROL_DISABLED, // No flow control (common)
    HOSAL_FLOW_CONTROL_CTS,
    HOSAL_FLOW_CONTROL_RTS,
    HOSAL_FLOW_CONTROL_CTS_RTS
} hosal_uart_flow_control_t;
```

### `hosal_uart_mode_t` — Mode

```c
typedef enum {
    HOSAL_UART_MODE_POLL,      // Polling mode (default)
    HOSAL_UART_MODE_INT_TX,    // TX interrupt mode
    HOSAL_UART_MODE_INT_RX,    // RX interrupt mode
    HOSAL_UART_MODE_INT,       // TX+RX interrupt mode
} hosal_uart_mode_t;
```

### `hosal_uart_callback_t` — Callback Function Type

```c
typedef int (*hosal_uart_callback_t)(void *p_arg);
```

### `hosal_uart_dma_cfg_t` — DMA Configuration

```c
typedef struct {
    uint8_t *dma_buf;         // DMA buffer
    uint32_t dma_buf_size;     // Buffer size
} hosal_uart_dma_cfg_t;
```

### `hosal_uart_config_t` — UART Configuration Structure

```c
typedef struct {
    uint8_t                   uart_id;        // UART ID (0/1/2)
    uint8_t                   tx_pin;         // TX pin
    uint8_t                   rx_pin;         // RX pin
    uint8_t                   cts_pin;        // CTS pin (255=not used)
    uint8_t                   rts_pin;        // RTS pin (255=not used)
    uint32_t                  baud_rate;      // Baud rate
    hosal_uart_data_width_t   data_width;    // Data width
    hosal_uart_parity_t       parity;         // Parity
    hosal_uart_stop_bits_t    stop_bits;      // Stop bits
    hosal_uart_flow_control_t flow_control;   // Flow control
    hosal_uart_mode_t         mode;           // Mode
} hosal_uart_config_t;
```

### `hosal_uart_dev_t` — UART Device Structure

```c
typedef struct {
    uint8_t       port;
    hosal_uart_config_t config;
    hosal_uart_callback_t tx_cb;
    void *p_txarg;
    hosal_uart_callback_t rx_cb;
    void *p_rxarg;
    hosal_uart_callback_t txdma_cb;
    void *p_txdma_arg;
    hosal_uart_callback_t rxdma_cb;
    void *p_rxdma_arg;
    hosal_dma_chan_t dma_tx_chan;
    hosal_dma_chan_t dma_rx_chan;
    void         *priv;
} hosal_uart_dev_t;
```

## Macros

### Quick UART Configuration and Device Declaration

```c
// Declare configuration
HOSAL_UART_CFG_DECL(cfg, id, tx_pin, rx_pin, baud);
// Example: HOSAL_UART_CFG_DECL(my_cfg, 0, 16, 7, 115200);

// Declare device
HOSAL_UART_DEV_DECL(my_uart, 0, 16, 7, 115200);
```

## Function API

### `hosal_uart_init`

Initialize UART.

```c
int hosal_uart_init(hosal_uart_dev_t *uart);
```

### `hosal_uart_init_only_tx`

Initialize TX only (one-way communication).

```c
int hosal_uart_init_only_tx(hosal_uart_dev_t *uart);
```

### `hosal_uart_send`

Send data in polling mode.

```c
int hosal_uart_send(hosal_uart_dev_t *uart, const void *txbuf, uint32_t size);
```

| Parameter | Description |
|-----------|-------------|
| `uart` | UART device |
| `txbuf` | Transmit data buffer |
| `size` | Number of bytes to send |

**Return value**: bytes sent (>0) on success, `EIO` on failure

---

### `hosal_uart_receive`

Receive data in polling mode.

```c
int hosal_uart_receive(hosal_uart_dev_t *uart, void *data, uint32_t expect_size);
```

| Parameter | Description |
|-----------|-------------|
| `uart` | UART device |
| `data` | Receive data buffer |
| `expect_size` | Expected number of bytes to receive |

**Return value**: bytes received (>0) on success, `EIO` on failure

---

### `hosal_uart_ioctl`

UART IO control.

```c
int hosal_uart_ioctl(hosal_uart_dev_t *uart, int ctl, void *p_arg);
```

| ctl command | p_arg type | Description |
|-------------|------------|-------------|
| `HOSAL_UART_BAUD_SET` | `uint32_t *` | Set baud rate |
| `HOSAL_UART_DATA_WIDTH_SET` | `hosal_uart_data_width_t *` | Set data width |
| `HOSAL_UART_STOP_BITS_SET` | `hosal_uart_stop_bits_t *` | Set stop bits |
| `HOSAL_UART_PARITY_SET` | `hosal_uart_parity_t *` | Set parity |
| `HOSAL_UART_MODE_SET` | `hosal_uart_mode_t *` | Set mode |
| `HOSAL_UART_FLUSH` | `NULL` | Wait for TX complete |
| `HOSAL_UART_DMA_TX_START` | `hosal_uart_dma_cfg_t *` | Start DMA TX |
| `HOSAL_UART_DMA_RX_START` | `hosal_uart_dma_cfg_t *` | Start DMA RX |

---

### `hosal_uart_callback_set`

Set interrupt callback.

```c
int hosal_uart_callback_set(hosal_uart_dev_t *uart,
                            int callback_type,
                            hosal_uart_callback_t pfn_callback,
                            void *arg);
```

| callback_type | Description |
|---------------|-------------|
| `HOSAL_UART_TX_CALLBACK` | TX idle callback |
| `HOSAL_UART_RX_CALLBACK` | RX complete callback |
| `HOSAL_UART_TX_DMA_CALLBACK` | TX DMA complete callback |
| `HOSAL_UART_RX_DMA_CALLBACK` | RX DMA complete callback |

---

### `hosal_uart_finalize`

Finalize UART.

```c
int hosal_uart_finalize(hosal_uart_dev_t *uart);
```

## Usage Example

```c
#include "hal_uart.h"

hosal_uart_dev_t uart0 = {
    .port = 0,
    .config = {
        .uart_id = 0,
        .tx_pin = 16,
        .rx_pin = 7,
        .baud_rate = 115200,
        .data_width = HOSAL_DATA_WIDTH_8BIT,
        .parity = HOSAL_NO_PARITY,
        .stop_bits = HOSAL_STOP_BITS_1,
        .mode = HOSAL_UART_MODE_POLL,
    }
};

hosal_uart_init(&uart0);

// Send
uint8_t tx_data[] = "Hello\r\n";
hosal_uart_send(&uart0, tx_data, sizeof(tx_data) - 1);

// Receive (blocking, wait for 10 bytes)
uint8_t rx_buf[10];
int len = hosal_uart_receive(&uart0, rx_buf, sizeof(rx_buf));

// Dynamically change baud rate
uint32_t new_baud = 9600;
hosal_uart_ioctl(&uart0, HOSAL_UART_BAUD_SET, &new_baud);
```

---

## Register-Level Programming

> Register Header: `components/platform/soc/bl602/bl602_std/bl602_std/Device/Bouffalo/BL602/Peripherals/uart_reg.h`  
> Base Address: UART0_BASE = 0x4000A000, UART1_BASE = 0x4000A100

### Register Overview

| Offset | Name | Description |
|--------|------|-------------|
| 0x00 | UTX_CONFIG | UART TX configuration |
| 0x04 | URX_CONFIG | UART RX configuration |
| 0x08 | UART_BIT_PRD | Bit period and sample cycle configuration |
| 0x0C | DATA_CONFIG | Data format configuration (parity, stop bits, bit width) |
| 0x10 | UTX_IR_POSITION | UART TX IR position |
| 0x14 | URX_IR_POSITION | UART RX IR position |
| 0x18 | UART_STATUS | UART status flags |
| 0x1C | UART_INT_STATUS | UART interrupt status |
| 0x20 | UART_INT_CLEAR | UART interrupt clear |
| 0x24 | UART_INT_ENABLE | UART interrupt enable |
| 0x28 | UART_FIFO_CONFIG_0 | FIFO configuration 0 (thresholds) |
| 0x2C | UART_FIFO_CONFIG_1 | FIFO configuration 1 (overflow/underflow) |
| 0x30 | UART_FIFO_STATUS | FIFO status (TX/RX count) |
| 0x34 | UART_FIFO_WDATA | FIFO write data |
| 0x38 | UART_FIFO_RDATA | FIFO read data |
| 0x40 | UART_UTX_DUMMY | TX dummy register |
| 0x44 | UART_CLKDIV | Clock divider |
| 0x80 | AUTO_BAUD_CONFIG | Auto baud configuration |

### Key Register Fields

**UTX_CONFIG (offset 0x00) — TX Configuration**

| Bits | Field | Description |
|------|-------|-------------|
| 0 | tx_enable | TX enable (1=enable) |
| 1 | tx_irq_enable | TX interrupt enable (1=enable) |
| 4 | tx_dma_enable | TX DMA enable (1=enable) |
| 8 | tx_cts_enable | TX CTS flow control enable |
| 16 | tx_fifo_overflow_int_enable | TX FIFO overflow interrupt enable |

**URX_CONFIG (offset 0x04) — RX Configuration**

| Bits | Field | Description |
|------|-------|-------------|
| 0 | rx_enable | RX enable (1=enable) |
| 1 | rx_irq_enable | RX interrupt enable (1=enable) |
| 4 | rx_dma_enable | RX DMA enable (1=enable) |
| 8 | rts_enable | RTS flow control enable |
| 16 | rx_fifo_overflow_int_enable | RX FIFO overflow interrupt enable |

**UART_BIT_PRD (offset 0x08) — Bit Timing**

| Bits | Field | Description |
|------|-------|-------------|
| [15:0] | bit_period | Bit period value (baud rate divisor - 1) |
| [31:16] | sample_cycle | Sample cycle count for oversampling |

**DATA_CONFIG (offset 0x0C) — Data Format**

| Bits | Field | Description |
|------|-------|-------------|
| [2:0] | data_width | Data width (0=5bit, 1=6bit, 2=7bit, 3=8bit, 4=9bit) |
| [5:3] | stop_bits | Stop bits (0=1stop, 1=1.5stop, 2=2stop) |
| 8 | parity_enable | Parity enable (1=enable) |
| 9 | paritysel | Parity select (0=even, 1=odd) |
| 12 | bit_inverse | Bit inverse (1=invert TX/RX) |
| 13 | byte_inverse | Byte inverse (1=invert byte order) |

**UART_STATUS (offset 0x18) — Status Flags**

| Bits | Field | Description |
|------|-------|-------------|
| 0 | tx_done | TX done flag |
| 1 | rx_done | RX done flag |
| 2 | rx_break | RX break detected |
| 8 | tx_fifo_full | TX FIFO full |
| 9 | tx_fifo_empty | TX FIFO empty |
| 10 | rx_fifo_full | RX FIFO full |
| 11 | rx_fifo_empty | RX FIFO empty |

**UART_INT_STATUS (offset 0x1C) — Interrupt Status**

| Bits | Field | Description |
|------|-------|-------------|
| 0 | tx_end_int | TX end interrupt |
| 1 | rx_end_int | RX end interrupt |
| 2 | rx_break_int | RX break interrupt |
| 3 | rto_int | RX timeout interrupt |
| 4 | rx_fifo_overflow_int | RX FIFO overflow interrupt |
| 5 | tx_fifo_underflow_int | TX FIFO underflow interrupt |

**UART_FIFO_CONFIG_0 (offset 0x28) — FIFO Thresholds**

| Bits | Field | Description |
|------|-------|-------------|
| [7:0] | tx_fifo_threshold | TX FIFO threshold for interrupt |
| [15:8] | rx_fifo_threshold | RX FIFO threshold for interrupt |

**UART_FIFO_STATUS (offset 0x30) — FIFO Counts**

| Bits | Field | Description |
|------|-------|-------------|
| [7:0] | tx_fifo_cnt | TX FIFO count |
| [15:8] | rx_fifo_cnt | RX FIFO count |

**UART_FIFO_WDATA (offset 0x34) — FIFO Write**

| Bits | Field | Description |
|------|-------|-------------|
| [8:0] | fifo_wdata | Write data to TX FIFO |

**UART_FIFO_RDATA (offset 0x38) — FIFO Read**

| Bits | Field | Description |
|------|-------|-------------|
| [8:0] | fifo_rdata | Read data from RX FIFO |
| 16 | rx_fifo_push | Push RX data to FIFO |

**UART_CLKDIV (offset 0x44) — Clock Divider**

| Bits | Field | Description |
|------|-------|-------------|
| [11:0] | div | Clock divider value |

**AUTO_BAUD_CONFIG (offset 0x80) — Auto Baud**

| Bits | Field | Description |
|------|-------|-------------|
| 0 | auto_baud_enable | Auto baud enable |
| 1 | auto_baud_start | Auto baud start (write 1 to begin) |
| 8 | overflow_indication | Overflow indication flag |

### Register-Level Code Example

```c
#include <stdint.h>

/* Register definitions for BL602 UART0 */
#define UART0_BASE           0x4000A000UL
#define UART1_BASE           0x4000A100UL

#define UART_UTX_CONFIG      0x00
#define UART_URX_CONFIG      0x04
#define UART_BIT_PRD         0x08
#define UART_DATA_CONFIG     0x0C
#define UART_STATUS          0x18
#define UART_INT_STATUS      0x1C
#define UART_INT_CLEAR       0x20
#define UART_INT_ENABLE      0x24
#define UART_FIFO_CONFIG_0   0x28
#define UART_FIFO_STATUS     0x30
#define UART_FIFO_WDATA      0x34
#define UART_FIFO_RDATA      0x38
#define UART_CLKDIV          0x44

/* Helper macros for register access */
#define UART_REG(base, offset)  (*(volatile uint32_t *)((base) + (offset)))
#define UTX_CONFIG(base)   UART_REG(base, UART_UTX_CONFIG)
#define URX_CONFIG(base)   UART_REG(base, UART_URX_CONFIG)
#define UBIT_PRD(base)     UART_REG(base, UART_BIT_PRD)
#define UDATA_CONFIG(base) UART_REG(base, UART_DATA_CONFIG)
#define USTATUS(base)      UART_REG(base, UART_STATUS)
#define UINT_STATUS(base)  UART_REG(base, UART_INT_STATUS)
#define UINT_CLEAR(base)   UART_REG(base, UART_INT_CLEAR)
#define UINT_ENABLE(base)  UART_REG(base, UART_INT_ENABLE)
#define UFIFO_CONFIG0(base) UART_REG(base, UART_FIFO_CONFIG_0)
#define UFIFO_STATUS(base) UART_REG(base, UART_FIFO_STATUS)
#define UFIFO_WDATA(base)  UART_REG(base, UART_FIFO_WDATA)
#define UFIFO_RDATA(base)  UART_REG(base, UART_FIFO_RDATA)
#define UCLKDIV(base)      UART_REG(base, UART_CLKDIV)

/* System clock is 80MHz */
#define SYS_CLK_HZ  80000000UL

/* Calculate bit period for desired baud rate */
/* Formula: bit_period = (sys_clk / baud) - 1 */
static uint32_t calc_bit_period(uint32_t baud)
{
    return (SYS_CLK_HZ / baud) - 1;
}

/* Initialize UART0 at 115200 baud, 8N1 using registers only */
static void uart_reg_init(uint32_t base, uint32_t baud)
{
    uint32_t bit_period;
    uint32_t clkdiv_val;

    /* Disable TX and RX during configuration */
    UTX_CONFIG(base) = 0;
    URX_CONFIG(base) = 0;

    /* Configure clock divider: div = (sys_clk / (baud * 16)) - 1 */
    clkdiv_val = (SYS_CLK_HZ / (baud * 16)) - 1;
    UCLKDIV(base) = clkdiv_val & 0xFFF;

    /* Configure bit timing: sample_cycle = 15 (16x oversampling) */
    bit_period = calc_bit_period(baud);
    UBIT_PRD(base) = (bit_period & 0xFFFF) | (15UL << 16);

    /* Configure data format: 8-bit, no parity, 1 stop bit */
    UDATA_CONFIG(base) = 0;  /* data_width=0 (8bit), stop_bits=0 (1stop), no parity */

    /* Configure FIFO thresholds: 1/2 full trigger */
    UFIFO_CONFIG0(base) = (31UL << 8) | (31UL << 0);  /* tx threshold=31, rx threshold=31 */

    /* Clear any pending interrupts */
    UINT_CLEAR(base) = 0xFFFFFFFF;

    /* Enable TX and RX */
    UTX_CONFIG(base) = 1;   /* tx_enable = 1 */
    URX_CONFIG(base) = 1;   /* rx_enable = 1 */
}

/* Send a single byte via register-level access */
static void uart_reg_putc(uint32_t base, uint8_t ch)
{
    /* Wait until TX FIFO has space */
    while (UFIFO_STATUS(base) & (1UL << 8)) { /* tx_fifo_full flag */ }

    /* Write byte to TX FIFO */
    UFIFO_WDATA(base) = ch & 0xFF;
}

/* Receive a single byte via register-level access (blocking) */
static uint8_t uart_reg_getc(uint32_t base)
{
    uint32_t status;

    /* Wait for RX data available */
    do {
        status = UINT_STATUS(base);
    } while ((status & (1UL << 1)) == 0);  /* rx_end_int not set */

    /* Read from RX FIFO */
    uint32_t rdata = UFIFO_RDATA(base);
    UINT_CLEAR(base) = (1UL << 1);  /* clear rx_end_int */

    return rdata & 0xFF;
}

/* Send a buffer via register-level access */
static void uart_reg_send(uint32_t base, const uint8_t *data, uint32_t len)
{
    uint32_t i;
    for (i = 0; i < len; i++) {
        uart_reg_putc(base, data[i]);
    }
}

/* Receive multiple bytes (blocking) */
static void uart_reg_receive(uint32_t base, uint8_t *data, uint32_t len)
{
    uint32_t i;
    for (i = 0; i < len; i++) {
        data[i] = uart_reg_getc(base);
    }
}

/* Configure UART interrupt */
static void uart_reg_irq_config(uint32_t base, uint8_t enable)
{
    if (enable) {
        /* Enable RX interrupt */
        UINT_ENABLE(base) = (1UL << 1);  /* rx_end_int enable */
        /* Also enable TX end interrupt */
        UINT_ENABLE(base) |= (1UL << 0); /* tx_end_int enable */
    } else {
        UINT_ENABLE(base) = 0;
    }
}

/* Clear UART interrupt flags */
static void uart_reg_irq_clear(uint32_t base)
{
    UINT_CLEAR(base) = 0xFFFFFFFF;
}

/* Example: Initialize UART0 at 115200 and send/receive data */
static void example_uart_reg(void)
{
    /* Initialize UART0 at 115200 baud, 8N1 */
    uart_reg_init(UART0_BASE, 115200);

    /* Send a string */
    uint8_t tx_buf[] = "Hello from register-level UART!\r\n";
    uart_reg_send(UART0_BASE, tx_buf, sizeof(tx_buf) - 1);

    /* Receive 5 bytes (blocking) */
    uint8_t rx_buf[5];
    uart_reg_receive(UART0_BASE, rx_buf, 5);

    /* Echo received bytes back */
    uart_reg_send(UART0_BASE, rx_buf, 5);
}

/* Example: Initialize UART0 with interrupt-based RX */
static void example_uart_reg_irq(uint32_t uart_base)
{
    /* Disable interrupts during setup */
    UINT_ENABLE(uart_base) = 0;

    /* Initialize UART */
    uart_reg_init(uart_base, 115200);

    /* Configure FIFO thresholds for interrupt */
    UFIFO_CONFIG0(uart_base) = (1UL << 8) | (1UL << 0);  /* trigger when 1+ bytes */

    /* Clear any pending interrupts */
    UINT_CLEAR(uart_base) = 0xFFFFFFFF;

    /* Enable interrupts for RX */
    UINT_ENABLE(uart_base) = (1UL << 1) | (1UL << 2) | (1UL << 3); /* rx_end + rx_break + rto */

    /* Note: In real usage, enable global interrupts and configure the GIPO-related
     * interrupt controller (like GLB_REG) to route UART interrupts to CPU */
}

/* Calculate proper bit_period value for given baud and sample rate */
static uint32_t calc_bit_prd(uint32_t baud, uint32_t sample_cycle)
{
    /* Formula: bit_period = (sys_clk / (baud * (sample_cycle + 1))) - 1 */
    return (SYS_CLK_HZ / (baud * (sample_cycle + 1))) - 1;
}
```
