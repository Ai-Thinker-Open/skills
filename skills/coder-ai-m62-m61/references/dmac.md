# DMAC (DMA Controller) Reference - BL616/BL618

## Overview

The DMAC (DMA Controller) is the **upper-layer controller** that manages DMA channels and transfer operations. It is separate from the DMA peripheral (which handles hardware handshaking with specific peripherals like UART, SPI, I2C).

This document covers:
- **DMAC architecture** - How the controller manages channels
- **Channel configuration** - Setting up transfer parameters
- **Handshake mechanism** - Peripheral requests and acknowledgment
- **LLI (Linked List Item)** - Chained transfers for large/unbounded data
- **Working code examples** - Practical implementation patterns
- **Register-level details** - Hardware register definitions

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     DMAC (Controller)                       │
│  ┌─────────┐ ┌─────────┐ ┌─────────┐       ┌─────────┐     │
│  │ Channel │ │ Channel │ │ Channel │  ...  │ Channel │     │
│  │   CH0   │ │   CH1   │ │   CH2   │       │   CH7   │     │
│  └────┬────┘ └────┬────┘ └────┬────┘       └────┬────┘     │
│       │            │            │                 │          │
│  ┌────┴────────────┴────────────┴─────────────────┴────┐    │
│  │              DMA Crossbar / Request Router          │    │
│  └────┬────────────┬────────────┬─────────────────┬────┘    │
└───────┼────────────┼────────────┼─────────────────┼─────────┘
        │            │            │                 │
   ┌────┴────┐  ┌────┴────┐  ┌────┴────┐     ┌────┴────┐
   │  UART   │  │   SPI   │  │   I2C   │     │  ADC   │
   │Peripheral│  │Peripheral│  │Peripheral│     │Peripheral│
   └─────────┘  └─────────┘  └─────────┘     └─────────┘
```

**Key distinction:**
- **DMAC (this document)**: Configures channels, manages LLI chains, handles transfer logic
- **DMA Peripheral**: Hardware handshaking signals (request/ack), FIFO interfaces

## Source Files

| File | Description |
|------|-------------|
| `drivers/lhal/include/bflb_dma.h` | DMAC API header (upper layer) |
| `drivers/lhal/include/hardware/dma_reg.h` | Register definitions |
| `drivers/lhal/src/bflb_dma.c` | DMAC implementation |

## Base Address

| Peripheral | Base Address |
|------------|--------------|
| DMA | `0x2000C000` |

## Channel Register Map

Each channel has registers at offset `0x100 + (channel × 0x30)`:

| Register | Offset | Name | Description |
|----------|--------|------|-------------|
| `CxSRCADDR` | `0x00` | Source Address | Starting source address |
| `CxDSTADDR` | `0x04` | Destination Address | Starting destination address |
| `CxLLI` | `0x08` | Linked List Pointer | Next LLI address (0 = end) |
| `CxCONTROL` | `0x0C` | Control | Transfer size, widths, burst, increment |
| `CxCONFIG` | `0x10` | Configuration | Enable, peripheral selection, flow control |

**Global registers at `dma_base + offset`:**

| Register | Offset | Description |
|----------|--------|-------------|
| `DMA_INTSTATUS` | `0x0` | Raw interrupt status |
| `DMA_INTTCSTATUS` | `0x4` | Transfer complete status |
| `DMA_INTTCCLEAR` | `0x8` | Clear TC interrupt |
| `DMA_INTERRORSTATUS` | `0xC` | Error status |
| `DMA_INTERRCLR` | `0x10` | Clear error interrupt |
| `DMA_ENBLDCHNS` | `0x1C` | Enabled channels mask |
| `DMA_TOP_CONFIG` | `0x30` | Global enable (DMA_E) |
| `DMA_SYNC` | `0x34` | Peripheral sync control |

---

## Channel Configuration

### Configuration Structure

```c
struct bflb_dma_channel_config_s {
    uint8_t  direction;         /* Transfer direction */
    uint32_t src_req;           /* Source peripheral request */
    uint32_t dst_req;           /* Destination peripheral request */
    uint8_t  src_addr_inc;      /* Source increment: DMA_ADDR_INCREMENT_ENABLE/DISABLE */
    uint8_t  dst_addr_inc;      /* Destination increment */
    uint8_t  src_burst_count;   /* Burst size: DMA_BURST_INCR1/4/8/16 */
    uint8_t  dst_burst_count;   /* Destination burst size */
    uint8_t  src_width;         /* Source width: DMA_DATA_WIDTH_8/16/32BIT */
    uint8_t  dst_width;         /* Destination width */
};
```

### Transfer Directions

| Constant | Value | Description |
|----------|-------|-------------|
| `DMA_MEMORY_TO_MEMORY` | 0 | Memcpy-style transfer |
| `DMA_MEMORY_TO_PERIPH` | 1 | Memory → Peripheral (TX) |
| `DMA_PERIPH_TO_MEMORY` | 2 | Peripheral → Memory (RX) |
| `DMA_PERIPH_TO_PERIPH` | 3 | Peripheral ↔ Peripheral |

### Data Width

| Constant | Value | Description |
|----------|-------|-------------|
| `DMA_DATA_WIDTH_8BIT` | 0 | 8-bit transfer |
| `DMA_DATA_WIDTH_16BIT` | 1 | 16-bit transfer |
| `DMA_DATA_WIDTH_32BIT` | 2 | 32-bit transfer |

### Burst Count

| Constant | Value | Description |
|----------|-------|-------------|
| `DMA_BURST_INCR1` | 0 | Burst of 1 |
| `DMA_BURST_INCR4` | 1 | Burst of 4 |
| `DMA_BURST_INCR8` | 2 | Burst of 8 |
| `DMA_BURST_INCR16` | 3 | Burst of 16 |

### Initialization Example

```c
void dma_channel_init_example(void)
{
    struct bflb_device_s *dma_ch;
    struct bflb_dma_channel_config_s config;

    /* Get channel 0 */
    dma_ch = bflb_device_get_by_name("dma0_ch0");

    config.direction = DMA_MEMORY_TO_PERIPH;
    config.src_req = DMA_REQUEST_NONE;          /* Memory source */
    config.dst_req = DMA_REQUEST_UART0_TX;      /* UART0 TX peripheral */
    config.src_addr_inc = DMA_ADDR_INCREMENT_ENABLE;
    config.dst_addr_inc = DMA_ADDR_INCREMENT_DISABLE;
    config.src_burst_count = DMA_BURST_INCR1;
    config.dst_burst_count = DMA_BURST_INCR1;
    config.src_width = DMA_DATA_WIDTH_8BIT;
    config.dst_width = DMA_DATA_WIDTH_8BIT;

    bflb_dma_channel_init(dma_ch, &config);
}
```

---

## Handshake Mechanism

### Peripheral Requests (BL616)

| Request | Value | Description |
|---------|-------|-------------|
| `DMA_REQUEST_NONE` | 0 | No request (memory-only) |
| `DMA_REQUEST_UART0_RX` | 0 | UART0 receive |
| `DMA_REQUEST_UART0_TX` | 1 | UART0 transmit |
| `DMA_REQUEST_UART1_RX` | 2 | UART1 receive |
| `DMA_REQUEST_UART1_TX` | 3 | UART1 transmit |
| `DMA_REQUEST_I2C0_RX` | 6 | I2C0 receive |
| `DMA_REQUEST_I2C0_TX` | 7 | I2C0 transmit |
| `DMA_REQUEST_WO` | 9 | Waveform output |
| `DMA_REQUEST_SPI0_RX` | 10 | SPI0 receive |
| `DMA_REQUEST_SPI0_TX` | 11 | SPI0 transmit |
| `DMA_REQUEST_DBI_TX` | 20 | DBI transmit |
| `DMA_REQUEST_AUADC_RX` | 21 | AUADC receive |
| `DMA_REQUEST_AUDAC_TX` | 13 | AUDAC transmit |
| `DMA_REQUEST_I2S_RX` | 16 | I2S receive |
| `DMA_REQUEST_I2S_TX` | 17 | I2S transmit |
| `DMA_REQUEST_ADC` | 22 | ADC |
| `DMA_REQUEST_DAC` | 23 | DAC |

### Peripheral Data Register Addresses

| Peripheral | TDR (TX) | RDR (RX) |
|------------|----------|----------|
| UART0 | `0x2000A000 + 0x88` | `0x2000A000 + 0x8C` |
| UART1 | `0x2000A100 + 0x88` | `0x2000A100 + 0x8C` |
| SPI0 | `0x2000A200 + 0x88` | `0x2000A200 + 0x8C` |
| I2C0 | `0x2000A300 + 0x88` | `0x2000A300 + 0x8C` |
| ADC | - | `0x20002000 + 0x04` |
| DAC | `0x20002000 + 0x48` | - |

### Hardware Handshake Flow

```
CPU                    DMAC                   Peripheral
 │                       │                         │
 │  Configure channel    │                         │
 ├──────────────────────>│                         │
 │                       │                         │
 │  Enable DMA on        │                         │
 │  peripheral           │                         │
 │───────────────────────│                         │
 │                       │                         │
 │                       │  DMAC_REQ ────────────>│
 │                       │                         │
 │                       │<────────── DMAC_ACK ────│
 │                       │                         │
 │                       │  Transfer data         │
 │                       │<══════════════════════>│
 │                       │                         │
 │  (Repeat until done)  │                         │
 │                       │                         │
 │                       │  TC interrupt          │
 │<──────────────────────│                         │
```

### Handshake Configuration

When `direction = DMA_MEMORY_TO_PERIPH`:
- `src_req = DMA_REQUEST_NONE` (memory has no handshake)
- `dst_req = peripheral_TX_request` (peripheral drives ACK)

When `direction = DMA_PERIPH_TO_MEMORY`:
- `src_req = peripheral_RX_request` (peripheral drives REQ)
- `dst_req = DMA_REQUEST_NONE` (memory has no handshake)

---

## LLI (Linked List Item) - Deep Dive

### What is LLI?

LLI enables **chained transfers** where multiple discontinuous memory blocks are transferred sequentially without CPU intervention. Each LLI node points to the next, forming a chain.

### LLI Pool Structure

```c
struct bflb_dma_channel_lli_pool_s {
    uint32_t src_addr;                      /* Source address */
    uint32_t dst_addr;                      /* Destination address */
    uint32_t nextlli;                       /* Next LLI address (0 = last) */
    union bflb_dma_lli_control_s control;    /* Transfer control */
};
```

### LLI Control Union

```c
union bflb_dma_lli_control_s {
    struct {
        uint32_t TransferSize : 12;  /* [11:0] Transfer count */
        uint32_t SBSize       : 2;  /* [13:12] Source burst size */
        uint32_t dst_min_mode : 1;  /* [14] Destination address wrap */
        uint32_t DBSize       : 2;  /* [16:15] Dest burst size */
        uint32_t dst_add_mode : 1;  /* [17] Destination add mode */
        uint32_t SWidth       : 2;  /* [19:18] Source width */
        uint32_t reserved_20  : 1;  /* [20] Reserved */
        uint32_t DWidth       : 2;  /* [22:21] Destination width */
        uint32_t fix_cnt      : 2;  /* [24:23] Fix count (for wrap) */
        uint32_t SLargerD     : 1;  /* [25] Source > Dest mode */
        uint32_t SI           : 1;  /* [26] Source increment enable */
        uint32_t DI           : 1;  /* [27] Destination increment enable */
        uint32_t Prot         : 3;  /* [30:28] Protection bits */
        uint32_t I            : 1;  /* [31] Interrupt on completion */
    } bits;
    uint32_t WORD;
};
```

### LLI Transfer Structure

```c
struct bflb_dma_channel_lli_transfer_s {
    uint32_t src_addr;    /* Source address */
    uint32_t dst_addr;    /* Destination address */
    uint32_t nbytes;      /* Number of bytes to transfer */
};
```

### Key LLI Rules

1. **Maximum transfer per LLI**: 4095 units (not bytes - depends on width)
2. **LLI chain alignment**: Addresses auto-adjusted to 32-byte alignment for cache coherence
3. **Last LLI sets I bit**: Triggers interrupt on overall completion
4. **nextlli = 0**: Indicates this is the last node in chain

### How LLI Reload Works

The `bflb_dma_channel_lli_reload()` function:

1. Calculates how many LLIs needed based on `nbytes` and data width
2. Splits large transfers into 4064-unit chunks (leaving margin for alignment)
3. Chains LLIs together via `nextlli` pointers
4. Sets `I` bit only on final LLI (enables completion interrupt)
5. Writes first LLI addresses to channel registers

```c
// Inside bflb_dma_channel_lli_reload()
actual_transfer_offset = 4064;  // For 8-bit width
// actual_transfer_offset = 4064 << 1 = 8128  For 16-bit
// actual_transfer_offset = 4064 << 2 = 16256 For 32-bit

lli_count = actual_transfer_len / 4064 + 1;
last_transfer_len = actual_transfer_len % 4064;
```

### Circular (Continuous) LLI Mode

To create a continuous/circular transfer:

```c
void dma_circular_setup(struct bflb_device_s *dma_ch)
{
    static uint8_t buffer[512];
    struct bflb_dma_channel_lli_pool_s lli_pool[2];

    /* First half */
    lli_pool[0].src_addr = peripheral_addr;
    lli_pool[0].dst_addr = (uint32_t)buffer;
    lli_pool[0].nextlli = (uint32_t)&lli_pool[1];
    lli_pool[0].control.bits.TransferSize = 256;
    lli_pool[0].control.bits.I = 0;  /* No interrupt yet */

    /* Second half - loops back */
    lli_pool[1].src_addr = peripheral_addr;
    lli_pool[1].dst_addr = (uint32_t)(buffer + 256);
    lli_pool[1].nextlli = (uint32_t)&lli_pool[0];  /* CIRCULAR! */
    lli_pool[1].control.bits.TransferSize = 256;
    lli_pool[1].control.bits.I = 1;  /* Interrupt on completion */

    /* Initialize with 2 LLIs */
    bflb_dma_channel_lli_reload(dma_ch, lli_pool, 2, NULL, 0);
    
    /* Make circular */
    bflb_dma_channel_lli_link_head(dma_ch, lli_pool, 2);
    
    bflb_dma_channel_start(dma_ch);
}
```

### LLI Link Head Function

`bflb_dma_channel_lli_link_head()` connects the last LLI back to the first:

```c
void bflb_dma_channel_lli_link_head(struct bflb_device_s *dev,
                                    struct bflb_dma_channel_lli_pool_s *lli_pool,
                                    uint32_t used_lli_count)
{
    /* Point last LLI back to first for circular mode */
    lli_pool[used_lli_count - 1].nextlli = (uint32_t)&lli_pool[0];
    
    /* Update DMA LLI register */
    putreg32(lli_pool[0].nextlli, channel_base + DMA_CxLLI_OFFSET);
    
    /* Clean cache for DMA coherence */
    bflb_l1c_dcache_clean_range(...);
}
```

---

## Register-Level Details

### Channel Configuration Register (CxCONFIG)

| Bit | Name | Description |
|-----|------|-------------|
| 0 | `DMA_E` | Channel enable |
| 1-5 | `SRCPERIPHERAL` | Source peripheral select |
| 6-10 | `DSTPERIPHERAL` | Destination peripheral select |
| 11-13 | `FLOWCNTRL` | Flow control: 0=mem-to-mem, 1=mem-to-periph, 2=periph-to-mem, 3=periph-to-periph |
| 14 | `IE` | Error interrupt enable |
| 15 | `ITC` | Transfer complete interrupt enable |
| 16 | `L` | Last LLI (internal use) |
| 17 | `A` | Active flag (read-only) |
| 18 | `H` | Halt flag (set to pause) |
| 20-29 | `LLICOUNTER` | LLI count remaining |

### Channel Control Register (CxCONTROL)

| Bit | Name | Description |
|-----|------|-------------|
| 0-11 | `TRANSFERSIZE` | Transfer count (in units, not bytes) |
| 12-13 | `SBSIZE` | Source burst size (0=1, 1=4, 2=8, 3=16) |
| 14 | `DST_MIN_MODE` | Destination address wrap mode |
| 15-16 | `DBSIZE` | Destination burst size |
| 17 | `DST_ADD_MODE` | Destination address add mode |
| 18-19 | `SWIDTH` | Source data width (0=8, 1=16, 2=32-bit) |
| 21-22 | `DWIDTH` | Destination data width |
| 23-25 | `FIX_CNT` | Fix count for wrap mode |
| 26 | `SI` | Source increment enable |
| 27 | `DI` | Destination increment enable |
| 28-30 | `PROT` | Protection bits |
| 31 | `I` | Interrupt on completion |

### Global Registers

**DMA_TOP_CONFIG (offset 0x30):**
- Bit 0: `DMA_E` - Global DMA enable

**DMA_ENBLDCHNS (offset 0x1C):**
- Bits 0-7: Channel enable status

---

## Complete Working Examples

### Example 1: UART DMA Transfer

```c
#include "bflb_dma.h"
#include "bflb_uart.h"

static struct bflb_device_s *dma_ch0;
static struct bflb_device_s *dma_ch1;
static uint8_t tx_buffer[] = "Hello DMA!\r\n";
static uint8_t rx_buffer[64];

void dma_uart_isr(void *arg)
{
    bflb_dma_channel_tcint_clear(dma_ch1);
    printf("RX Complete: %s\r\n", rx_buffer);
}

void uart_dma_example(void)
{
    /* Initialize UART first */
    struct bflb_device_s *uart = bflb_device_get_by_name("uart1");
    struct bflb_uart_config_s uart_cfg = {
        .baudrate = 115200,
        .data_bits = UART_DATA_BITS_8,
        .stop_bits = UART_STOP_BITS_1,
        .parity = UART_PARITY_NONE,
    };
    bflb_uart_init(uart, &uart_cfg);

    /* Link UART to DMA */
    bflb_uart_link_txdma(uart, true);
    bflb_uart_link_rxdma(uart, true);

    /* TX Channel: Memory -> UART */
    struct bflb_dma_channel_config_s tx_cfg = {
        .direction = DMA_MEMORY_TO_PERIPH,
        .src_req = DMA_REQUEST_NONE,
        .dst_req = DMA_REQUEST_UART1_TX,
        .src_addr_inc = DMA_ADDR_INCREMENT_ENABLE,
        .dst_addr_inc = DMA_ADDR_INCREMENT_DISABLE,
        .src_burst_count = DMA_BURST_INCR1,
        .dst_burst_count = DMA_BURST_INCR1,
        .src_width = DMA_DATA_WIDTH_8BIT,
        .dst_width = DMA_DATA_WIDTH_8BIT,
    };

    /* RX Channel: UART -> Memory */
    struct bflb_dma_channel_config_s rx_cfg = {
        .direction = DMA_PERIPH_TO_MEMORY,
        .src_req = DMA_REQUEST_UART1_RX,
        .dst_req = DMA_REQUEST_NONE,
        .src_addr_inc = DMA_ADDR_INCREMENT_DISABLE,
        .dst_addr_inc = DMA_ADDR_INCREMENT_ENABLE,
        .src_burst_count = DMA_BURST_INCR1,
        .dst_burst_count = DMA_BURST_INCR1,
        .src_width = DMA_DATA_WIDTH_8BIT,
        .dst_width = DMA_DATA_WIDTH_8BIT,
    };

    dma_ch0 = bflb_device_get_by_name("dma0_ch0");
    dma_ch1 = bflb_device_get_by_name("dma0_ch1");

    bflb_dma_channel_init(dma_ch0, &tx_cfg);
    bflb_dma_channel_init(dma_ch1, &rx_cfg);

    /* Register RX interrupt */
    bflb_dma_channel_irq_attach(dma_ch1, dma_uart_isr, NULL);

    /* Configure TX transfer */
    struct bflb_dma_channel_lli_pool_s tx_llipool[1];
    struct bflb_dma_channel_lli_transfer_s tx_transfer = {
        .src_addr = (uint32_t)tx_buffer,
        .dst_addr = 0x2000A100 + 0x88,  /* UART1_TDR */
        .nbytes = sizeof(tx_buffer),
    };
    bflb_dma_channel_lli_reload(dma_ch0, tx_llipool, 1, &tx_transfer, 1);

    /* Configure RX transfer */
    struct bflb_dma_channel_lli_pool_s rx_llipool[1];
    struct bflb_dma_channel_lli_transfer_s rx_transfer = {
        .src_addr = 0x2000A100 + 0x8C,  /* UART1_RDR */
        .dst_addr = (uint32_t)rx_buffer,
        .nbytes = sizeof(rx_buffer) - 1,
    };
    bflb_dma_channel_lli_reload(dma_ch1, rx_llipool, 1, &rx_transfer, 1);

    /* Start both channels */
    bflb_dma_channel_start(dma_ch0);
    bflb_dma_channel_start(dma_ch1);
}
```

### Example 2: Multi-Block Memory Transfer with LLI

```c
void dma_multi_block_example(void)
{
    static uint8_t block1[1000];
    static uint8_t block2[2000];
    static uint8_t block3[500];
    static uint8_t dest[4000];

    struct bflb_device_s *dma_ch = bflb_device_get_by_name("dma0_ch0");
    
    struct bflb_dma_channel_config_s config = {
        .direction = DMA_MEMORY_TO_MEMORY,
        .src_req = DMA_REQUEST_NONE,
        .dst_req = DMA_REQUEST_NONE,
        .src_addr_inc = DMA_ADDR_INCREMENT_ENABLE,
        .dst_addr_inc = DMA_ADDR_INCREMENT_ENABLE,
        .src_burst_count = DMA_BURST_INCR4,
        .dst_burst_count = DMA_BURST_INCR4,
        .src_width = DMA_DATA_WIDTH_32BIT,
        .dst_width = DMA_DATA_WIDTH_32BIT,
    };

    bflb_dma_channel_init(dma_ch, &config);

    /* LLI pool for 3 blocks */
    struct bflb_dma_channel_lli_pool_s lli_pool[10];
    struct bflb_dma_channel_lli_transfer_s transfers[] = {
        { .src_addr = (uint32_t)block1, .dst_addr = (uint32_t)dest, .nbytes = 1000 },
        { .src_addr = (uint32_t)block2, .dst_addr = (uint32_t)(dest + 1000), .nbytes = 2000 },
        { .src_addr = (uint32_t)block3, .dst_addr = (uint32_t)(dest + 3000), .nbytes = 500 },
    };

    int used = bflb_dma_channel_lli_reload(dma_ch, lli_pool, 10, transfers, 3);
    
    printf("Used %d LLIs for 3 blocks\r\n", used);
    
    bflb_dma_channel_start(dma_ch);
    
    /* Wait for completion */
    while (bflb_dma_channel_isbusy(dma_ch)) {
        /* Could yield to RTOS here */
    }
    
    printf("Multi-block transfer complete!\r\n");
}
```

### Example 3: SPI DMA Transfer

```c
#include "bflb_dma.h"
#include "bflb_spi.h"

static struct bflb_device_s *spi_dma_ch;
static uint8_t spi_tx_data[256];
static uint8_t spi_rx_data[256];

void spi_dma_isr(void *arg)
{
    bflb_dma_channel_tcint_clear(spi_dma_ch);
    printf("SPI DMA transfer done\r\n");
}

void spi_dma_example(void)
{
    /* Initialize SPI first */
    struct bflb_device_s *spi = bflb_device_get_by_name("spi0");
    bflb_spi_init(spi, ...);
    
    /* Link SPI to DMA */
    bflb_spi_link_txdma(spi, true);
    bflb_spi_link_rxdma(spi, true);

    /* TX Configuration: Memory -> SPI */
    struct bflb_dma_channel_config_s tx_cfg = {
        .direction = DMA_MEMORY_TO_PERIPH,
        .src_req = DMA_REQUEST_NONE,
        .dst_req = DMA_REQUEST_SPI0_TX,
        .src_addr_inc = DMA_ADDR_INCREMENT_ENABLE,
        .dst_addr_inc = DMA_ADDR_INCREMENT_DISABLE,
        .src_burst_count = DMA_BURST_INCR1,
        .dst_burst_count = DMA_BURST_INCR1,
        .src_width = DMA_DATA_WIDTH_8BIT,
        .dst_width = DMA_DATA_WIDTH_8BIT,
    };

    spi_dma_ch = bflb_device_get_by_name("dma0_ch0");
    bflb_dma_channel_init(spi_dma_ch, &tx_cfg);
    bflb_dma_channel_irq_attach(spi_dma_ch, spi_dma_isr, NULL);

    /* Configure transfer */
    struct bflb_dma_channel_lli_pool_s lli_pool[1];
    struct bflb_dma_channel_lli_transfer_s transfer = {
        .src_addr = (uint32_t)spi_tx_data,
        .dst_addr = 0x2000A200 + 0x88,  /* SPI0_TDR */
        .nbytes = sizeof(spi_tx_data),
    };
    
    bflb_dma_channel_lli_reload(spi_dma_ch, lli_pool, 1, &transfer, 1);
    bflb_dma_channel_start(spi_dma_ch);
}
```

### Example 4: Continuous RX with Ping-Pong Buffer

```c
#define RX_BUFFER_SIZE 1024

static uint8_t rx_buffer[RX_BUFFER_SIZE * 2];  /* Double buffer */
static struct bflb_device_s *ping_pong_ch;

void rx_dma_isr(void *arg)
{
    static uint32_t toggle = 0;
    
    bflb_dma_channel_tcint_clear(ping_pong_ch);
    
    /* Determine which half was just filled */
    if (toggle == 0) {
        /* First half complete - process it */
        process_buffer(rx_buffer, RX_BUFFER_SIZE);
    } else {
        /* Second half complete - process it */
        process_buffer(rx_buffer + RX_BUFFER_SIZE, RX_BUFFER_SIZE);
    }
    
    toggle = !toggle;
}

void ping_pong_dma_example(void)
{
    struct bflb_dma_channel_config_s config = {
        .direction = DMA_PERIPH_TO_MEMORY,
        .src_req = DMA_REQUEST_UART0_RX,
        .dst_req = DMA_REQUEST_NONE,
        .src_addr_inc = DMA_ADDR_INCREMENT_DISABLE,
        .dst_addr_inc = DMA_ADDR_INCREMENT_ENABLE,
        .src_burst_count = DMA_BURST_INCR1,
        .dst_burst_count = DMA_BURST_INCR1,
        .src_width = DMA_DATA_WIDTH_8BIT,
        .dst_width = DMA_DATA_WIDTH_8BIT,
    };

    ping_pong_ch = bflb_device_get_by_name("dma0_ch0");
    bflb_dma_channel_init(ping_pong_ch, &config);
    bflb_dma_channel_irq_attach(ping_pong_ch, rx_dma_isr, NULL);

    /* Setup two LLIs for ping-pong */
    struct bflb_dma_channel_lli_pool_s lli_pool[2];
    
    /* First LLI: UART RX -> first half */
    lli_pool[0].src_addr = 0x2000A000 + 0x8C;  /* UART0_RDR */
    lli_pool[0].dst_addr = (uint32_t)rx_buffer;
    lli_pool[0].nextlli = (uint32_t)&lli_pool[1];
    lli_pool[0].control.bits.TransferSize = RX_BUFFER_SIZE;
    lli_pool[0].control.bits.SWidth = 0;  /* 8-bit */
    lli_pool[0].control.bits.DWidth = 0;
    lli_pool[0].control.bits.SI = 0;
    lli_pool[0].control.bits.DI = 1;
    lli_pool[0].control.bits.I = 0;  /* No interrupt */

    /* Second LLI: UART RX -> second half */
    lli_pool[1].src_addr = 0x2000A000 + 0x8C;
    lli_pool[1].dst_addr = (uint32_t)(rx_buffer + RX_BUFFER_SIZE);
    lli_pool[1].nextlli = (uint32_t)&lli_pool[0];  /* Loop back */
    lli_pool[1].control = lli_pool[0].control;
    lli_pool[1].control.bits.I = 1;  /* Interrupt on completion */

    bflb_dma_channel_lli_reload(ping_pong_ch, lli_pool, 2, NULL, 0);
    bflb_dma_channel_start(ping_pong_ch);
}
```

---

## API Summary

| Function | Description |
|----------|-------------|
| `bflb_dma_channel_init()` | Initialize DMA channel with configuration |
| `bflb_dma_channel_deinit()` | Deinitialize channel |
| `bflb_dma_channel_start()` | Start DMA transfer |
| `bflb_dma_channel_stop()` | Stop DMA transfer |
| `bflb_dma_channel_isbusy()` | Check if transfer in progress |
| `bflb_dma_channel_irq_attach()` | Register completion callback |
| `bflb_dma_channel_irq_detach()` | Unregister callback |
| `bflb_dma_channel_lli_reload()` | Configure LLI chain |
| `bflb_dma_channel_lli_link_head()` | Enable circular LLI mode |
| `bflb_dma_channel_lli_insert()` | Insert LLI nodes (BL616CL) |
| `bflb_dma_channel_tcint_mask()` | Enable/disable TC interrupt |
| `bflb_dma_channel_get_tcint_status()` | Check TC status |
| `bflb_dma_channel_tcint_clear()` | Clear TC interrupt flag |
| `bflb_dma_feature_control()` | Various control commands |

---

## Feature Control Commands

| Command | Description |
|---------|-------------|
| `DMA_CMD_SET_SRCADDR_INCREMENT` | Enable/disable source increment |
| `DMA_CMD_SET_DSTADDR_INCREMENT` | Enable/disable dest increment |
| `DMA_CMD_SET_ADD_MODE` | Set destination address add mode |
| `DMA_CMD_SET_REDUCE_MODE` | Set destination address reduce mode |
| `DMA_CMD_SET_LLI_CONFIG` | Configure LLI |
| `DMA_CMD_GET_LLI_SRCADDR` | Get current LLI source address |
| `DMA_CMD_GET_LLI_DSTADDR` | Get current LLI destination address |
| `DMA_CMD_GET_LLI_CONTROL` | Get current LLI control value |
| `DMA_CMD_GET_LLI_COUNT` | Get remaining LLI count |
| `DMA_CMD_SET_SUSPEND` | Suspend DMA channel |
| `DMA_CMD_SET_RESUME` | Resume suspended channel |
| `DMA_CMD_GET_TRANSFER_PENDING` | Check transfer pending |
