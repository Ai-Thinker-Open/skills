# SPI API Reference

> Source file: `components/platform/hosal/include/hosal_spi.h`

## Macros

```c
#define HOSAL_SPI_MODE_MASTER 0  // Master mode
#define HOSAL_SPI_MODE_SLAVE  1  // Slave mode
#define HOSAL_WAIT_FOREVER  0xFFFFFFFFU  // Wait forever (no timeout)
```

## Type Definitions

### `hosal_spi_irq_t` — Interrupt Callback Type

```c
typedef void (*hosal_spi_irq_t)(void *parg);
```

### `hosal_spi_config_t` — SPI Configuration Structure

```c
typedef struct {
    uint8_t mode;           // Master/slave mode
    uint8_t dma_enable;     // DMA enable (0=disabled)
    uint8_t polar_phase;    // Polarity and phase (CPOL=0/1, CPHA=0/1)
    uint32_t freq;          // Communication frequency in Hz (e.g. 1000000 = 1MHz)
    uint8_t pin_clk;        // CLK pin
    uint8_t pin_mosi;       // MOSI pin
    uint8_t pin_miso;       // MISO pin
} hosal_spi_config_t;
```

### `hosal_spi_dev_t` — SPI Device Structure

```c
typedef struct {
    uint8_t port;
    hosal_spi_config_t  config;
    hosal_spi_irq_t cb;     // Interrupt callback
    void *p_arg;
    void *priv;
} hosal_spi_dev_t;
```

## Function API

### `hosal_spi_init`

Initialize SPI.

```c
int hosal_spi_init(hosal_spi_dev_t *spi);
```

---

### `hosal_spi_send`

Send data only (full-duplex transmit side).

```c
int hosal_spi_send(hosal_spi_dev_t *spi,
                   const uint8_t *data,
                   uint16_t size,
                   uint32_t timeout);
```

---

### `hosal_spi_recv`

Receive data only.

```c
int hosal_spi_recv(hosal_spi_dev_t *spi,
                   uint8_t *data,
                   uint16_t size,
                   uint32_t timeout);
```

---

### `hosal_spi_send_recv`

Send and receive (common full-duplex operation).

```c
int hosal_spi_send_recv(hosal_spi_dev_t *spi,
                        uint8_t *tx_data,
                        uint8_t *rx_data,
                        uint16_t size,
                        uint32_t timeout);
```

| Parameter | Description |
|-----------|-------------|
| `spi` | SPI device |
| `tx_data` | Transmit data buffer |
| `rx_data` | Receive data buffer (can be same as tx_data) |
| `size` | Number of bytes to send/receive |
| `timeout` | Timeout (milliseconds) |

---

### `hosal_spi_irq_callback_set`

Set interrupt callback.

```c
int hosal_spi_irq_callback_set(hosal_spi_dev_t *spi,
                               hosal_spi_irq_t pfn,
                               void *p_arg);
```

---

### `hosal_spi_set_cs`

Software control of CS chip select pin (master only).

```c
int hosal_spi_set_cs(uint8_t pin, uint8_t value);
```

| Parameter | Description |
|-----------|-------------|
| `pin` | CS pin number |
| `value` | `0` = low, `1` = high |

---

### `hosal_spi_finalize`

Finalize SPI.

```c
int hosal_spi_finalize(hosal_spi_dev_t *spi);
```

## Usage Example

```c
#include "hal_spi.h"

hosal_spi_dev_t spi0 = {
    .port = 0,
    .config = {
        .mode = HOSAL_SPI_MODE_MASTER,
        .dma_enable = 0,
        .polar_phase = 0,      // CPOL=0, CPHA=0
        .freq = 1000000,       // 1MHz
        .pin_clk = 14,
        .pin_mosi = 15,
        .pin_miso = 16,
    }
};

hosal_spi_init(&spi0);

// Send and receive (full-duplex)
uint8_t tx_buf[4] = {0x9F, 0, 0, 0};
uint8_t rx_buf[4];
hosal_spi_send_recv(&spi0, tx_buf, rx_buf, 4, HOSAL_WAIT_FOREVER);

// Send only
hosal_spi_send(&spi0, tx_buf, 4, HOSAL_WAIT_FOREVER);

// Software CS control (chip select slave)
hosal_spi_set_cs(17, 0);  // CS low, select slave
// ... operations ...
hosal_spi_set_cs(17, 1);  // CS high, release slave
```

---

## Register-Level Programming

> Register Header: `components/platform/soc/bl602/bl602_std/bl602_std/Device/Bouffalo/BL602/Peripherals/spi_reg.h`  
> Base Address: `0x4000A400`

### Register Overview

| Offset | Name          | Description                        |
|--------|---------------|------------------------------------|
| 0x00   | SPI_CONFIG    | SPI enable, mode, clock polarity/phase, frame length |
| 0x04   | SPI_SPI       | Clock divider and byte order       |
| 0x08   | SPI_DEV_ID    | Device identification (read-only)  |
| 0x0C   | SPI_TX_FIFO   | Transmit FIFO (write)              |
| 0x10   | SPI_RX_FIFO   | Receive FIFO (read)                 |
| 0x14   | SPI_STAS      | TX/RX FIFO status and SPI busy flag|
| 0x18   | SPI_INT_STS   | Interrupt status flags             |
| 0x1C   | SPI_INT_MASK  | Interrupt mask                     |
| 0x20   | SPI_INT_CLR   | Interrupt clear                    |
| 0x24   | SPI_DLY       | Delay configuration                |

### Key Register Fields

**SPI_CONFIG (0x00)**

| Bits | Name      | Description                              |
|------|-----------|------------------------------------------|
| 0    | spi_en    | SPI enable (1=enable, 0=disable)         |
| 1    | ms_mode   | Master/slave mode (0=master, 1=slave)    |
| 2    | cpha      | Clock phase (0=first edge, 1=second edge)|
| 3    | cpol      | Clock polarity (0=normal, 1=inverted)    |
| [7:6]| frame_len | Frame length (0=8-bit, others vary)       |

**SPI_SPI (0x04)**

| Bits  | Name      | Description                          |
|-------|-----------|--------------------------------------|
| [15:0]| clk_div   | Clock divider. Effective divisor = clk_div + 1 |
| 16    | byte_seq  | Byte sequence (0=MSB first, 1=LSB first) |

**SPI_STAS (0x14)**

| Bits | Name         | Description                        |
|------|--------------|------------------------------------|
| 0    | tx_fifo_qi   | TX FIFO queue empty (1=empty)      |
| 1    | rx_fifo_qi   | RX FIFO queue empty (1=empty)      |
| 4    | spi_busy     | SPI busy flag                       |

**SPI_INT_STS (0x18)**

| Bits | Name            | Description           |
|------|-----------------|-----------------------|
| 0    | tx_end_int      | TX transfer end        |
| 1    | rx_end_int      | RX transfer end        |
| 2    | rx_timeout_int  | RX timeout             |

### Register-Level Code Example

```c
#include <stdint.h>

/* BL602 bus clock is typically 32MHz */
#define BUS_CLK_HZ    32000000UL
#define SPI_TARGET_HZ 1000000UL

/* SPI base address */
#define SPI_BASE      0x4000A400UL
#define SPI_CONFIG    *(volatile uint32_t *)(SPI_BASE + 0x00)
#define SPI_SPI       *(volatile uint32_t *)(SPI_BASE + 0x04)
#define SPI_TX_FIFO   *(volatile uint32_t *)(SPI_BASE + 0x0C)
#define SPI_RX_FIFO   *(volatile uint32_t *)(SPI_BASE + 0x10)
#define SPI_STAS      *(volatile uint32_t *)(SPI_BASE + 0x14)
#define SPI_INT_STS   *(volatile uint32_t *)(SPI_BASE + 0x18)
#define SPI_INT_CLR   *(volatile uint32_t *)(SPI_BASE + 0x20)

/* Polls TX end interrupt flag in SPI_INT_STS */
static void spi_poll_tx_end(void)
{
    while ((SPI_INT_STS & 0x01) == 0) {
        /* spin */
    }
}

/* Reads 4 bytes from SPI RX FIFO */
static void spi_read_fifo(uint8_t *buf, int len)
{
    int i;
    for (i = 0; i < len; i++) {
        /* Wait for RX FIFO not empty */
        while ((SPI_STAS & 0x02) != 0) {
            /* spin */
        }
        buf[i] = (uint8_t)SPI_RX_FIFO;
    }
}

/* Writes len bytes to SPI TX FIFO */
static void spi_write_fifo(const uint8_t *buf, int len)
{
    int i;
    for (i = 0; i < len; i++) {
        /* Wait for TX FIFO not full */
        while ((SPI_STAS & 0x01) != 0) {
            /* spin */
        }
        SPI_TX_FIFO = buf[i];
    }
}

void spi_reg_example(void)
{
    uint32_t clk_div;

    /* Calculate clock divider: divisor = clk_div + 1
     * clk_div = (BUS_CLK_HZ / SPI_TARGET_HZ) - 1
     * For 1MHz from 32MHz: clk_div = 32 - 1 = 31
     */
    clk_div = (BUS_CLK_HZ / SPI_TARGET_HZ) - 1;

    /* Disable SPI before configuring */
    SPI_CONFIG = 0;

    /* Configure: master (ms_mode=0), CPOL=0, CPHA=0, 8-bit frames */
    SPI_CONFIG = (1 << 0)   /* spi_en */
                | (0 << 1)   /* ms_mode: 0=master */
                | (0 << 2)   /* cpha */
                | (0 << 3);  /* cpol */

    /* Set clock divider and MSB-first byte order */
    SPI_SPI = clk_div & 0xFFFF;

    /* Enable SPI */
    SPI_CONFIG |= (1 << 0);

    /* Flush RX FIFO by reading any residual bytes */
    while ((SPI_STAS & 0x02) == 0) {
        (void)SPI_RX_FIFO;
    }

    /* Perform a 4-byte exchange (e.g., read JEDEC ID: 0x9F, 0, 0, 0) */
    uint8_t tx[4] = {0x9F, 0x00, 0x00, 0x00};
    uint8_t rx[4];

    spi_write_fifo(tx, 4);
    spi_poll_tx_end();
    SPI_INT_CLR = 0x01;          /* clear TX end interrupt */
    spi_read_fifo(rx, 4);
    SPI_INT_CLR = 0x02;          /* clear RX end interrupt */
}
```
