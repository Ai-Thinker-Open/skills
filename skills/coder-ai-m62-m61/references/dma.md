# DMA API Reference (BL616/BL618)

## Overview

The DMA (Direct Memory Access) controller on BL616/BL618 provides 8 independent channels (DMA0) for high-speed data transfers between memory and peripherals without CPU intervention.

## Source File

- **Header**: `bouffalo_sdk/drivers/lhal/include/bflb_dma.h`
- **Implementation**: `bouffalo_sdk/drivers/lhal/src/bflb_dma.c`

## Base Address

| Peripheral | Base Address |
|------------|--------------|
| DMA | `0x2000c000` |

## DMA Channels

BL616 has 8 DMA channels (CH0-CH7):

| Channel | Constant | IRQ |
|---------|----------|-----|
| 0 | `BL_AHB_DMA0_CH0` | DMA0_ALL_IRQn |
| 1 | `BL_AHB_DMA0_CH1` | DMA0_ALL_IRQn |
| 2 | `BL_AHB_DMA0_CH2` | DMA0_ALL_IRQn |
| 3 | `BL_AHB_DMA0_CH3` | DMA0_ALL_IRQn |
| 4 | `BL_AHB_DMA0_CH4` | DMA0_ALL_IRQn |
| 5 | `BL_AHB_DMA0_CH5` | DMA0_ALL_IRQn |
| 6 | `BL_AHB_DMA0_CH6` | DMA0_ALL_IRQn |
| 7 | `BL_AHB_DMA0_CH7` | DMA0_ALL_IRQn |

## Transfer Directions

| Constant | Value | Description |
|----------|-------|-------------|
| `DMA_MEMORY_TO_MEMORY` | 0 | Memory to memory transfer |
| `DMA_MEMORY_TO_PERIPH` | 1 | Memory to peripheral |
| `DMA_PERIPH_TO_MEMORY` | 2 | Peripheral to memory |
| `DMA_PERIPH_TO_PERIPH` | 3 | Peripheral to peripheral |

## Address Increment

| Constant | Value | Description |
|----------|-------|-------------|
| `DMA_ADDR_INCREMENT_DISABLE` | 0 | Address does not increment |
| `DMA_ADDR_INCREMENT_ENABLE` | 1 | Address increments |

## Data Width

| Constant | Value | Description |
|----------|-------|-------------|
| `DMA_DATA_WIDTH_8BIT` | 0 | 8-bit data width |
| `DMA_DATA_WIDTH_16BIT` | 1 | 16-bit data width |
| `DMA_DATA_WIDTH_32BIT` | 2 | 32-bit data width |

## Burst Count

| Constant | Value | Description |
|----------|-------|-------------|
| `DMA_BURST_INCR1` | 0 | Burst of 1 |
| `DMA_BURST_INCR4` | 1 | Burst of 4 |
| `DMA_BURST_INCR8` | 2 | Burst of 8 |
| `DMA_BURST_INCR16` | 3 | Burst of 16 |

## Peripheral Requests (BL616)

| Request | Value | Description |
|---------|-------|-------------|
| `DMA_REQUEST_NONE` | 0 | No request |
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

## Peripheral Register Addresses

| Peripheral | Address |
|------------|---------|
| `DMA_ADDR_UART0_TDR` | `0x2000A000 + 0x88` |
| `DMA_ADDR_UART0_RDR` | `0x2000A000 + 0x8C` |
| `DMA_ADDR_UART1_TDR` | `0x2000A100 + 0x88` |
| `DMA_ADDR_UART1_RDR` | `0x2000A100 + 0x8C` |
| `DMA_ADDR_SPI0_TDR` | `0x2000A200 + 0x88` |
| `DMA_ADDR_SPI0_RDR` | `0x2000A200 + 0x8C` |
| `DMA_ADDR_I2C0_TDR` | `0x2000A300 + 0x88` |
| `DMA_ADDR_I2C0_RDR` | `0x2000A300 + 0x8C` |
| `DMA_ADDR_ADC_RDR` | `0x20002000 + 0x04` |
| `DMA_ADDR_DAC_TDR` | `0x20002000 + 0x48` |

## Configuration Structures

### DMA Channel Configuration

```c
struct bflb_dma_channel_config_s {
    uint8_t  direction;         /* Transfer direction, use @ref DMA_DIRECTION */
    uint32_t src_req;           /* Source request, use @ref DMA_PERIPHERAL_REQUEST */
    uint32_t dst_req;           /* Destination request, use @ref DMA_PERIPHERAL_REQUEST */
    uint8_t  src_addr_inc;       /* Source address increment, use @ref DMA_ADDR_INCREMENT */
    uint8_t  dst_addr_inc;       /* Destination address increment, use @ref DMA_ADDR_INCREMENT */
    uint8_t  src_burst_count;   /* Source burst count, use @ref DMA_BURST_COUNT */
    uint8_t  dst_burst_count;   /* Destination burst count, use @ref DMA_BURST_COUNT */
    uint8_t  src_width;         /* Source data width, use @ref DMA_DATA_WIDTH */
    uint8_t  dst_width;         /* Destination data width, use @ref DMA_DATA_WIDTH */
};
```

### DMA LLI Pool Structure

```c
struct bflb_dma_channel_lli_pool_s {
    uint32_t src_addr;                      /* Source address */
    uint32_t dst_addr;                      /* Destination address */
    uint32_t nextlli;                       /* Next LLI address (0 = last) */
    union bflb_dma_lli_control_s control;    /* Transfer control */
};
```

### DMA LLI Transfer Structure

```c
struct bflb_dma_channel_lli_transfer_s {
    uint32_t src_addr;    /* Source address */
    uint32_t dst_addr;    /* Destination address */
    uint32_t nbytes;      /* Number of bytes to transfer */
};
```

## API Functions

### bflb_dma_channel_init

Initialize a DMA channel.

```c
void bflb_dma_channel_init(struct bflb_device_s *dev, 
                           const struct bflb_dma_channel_config_s *config);
```

**Parameters:**
- `dev` - Device handle (e.g., `bflb_device_get_by_name("dma0_ch0")`)
- `config` - Pointer to channel configuration

---

### bflb_dma_channel_deinit

Deinitialize a DMA channel.

```c
void bflb_dma_channel_deinit(struct bflb_device_s *dev);
```

---

### bflb_dma_channel_start

Start DMA transfer on a channel.

```c
void bflb_dma_channel_start(struct bflb_device_s *dev);
```

---

### bflb_dma_channel_stop

Stop DMA transfer on a channel.

```c
void bflb_dma_channel_stop(struct bflb_device_s *dev);
```

---

### bflb_dma_channel_isbusy

Check if DMA channel is busy.

```c
bool bflb_dma_channel_isbusy(struct bflb_device_s *dev);
```

**Returns:** `true` if transfer in progress, `false` if complete

---

### bflb_dma_channel_irq_attach

Register DMA transfer completion callback.

```c
void bflb_dma_channel_irq_attach(struct bflb_device_s *dev, 
                                 void (*callback)(void *arg), void *arg);
```

---

### bflb_dma_channel_irq_detach

Unregister DMA callback.

```c
void bflb_dma_channel_irq_detach(struct bflb_device_s *dev);
```

---

### bflb_dma_channel_lli_reload

Configure DMA for LLI (Linked List Item) transfer.

```c
int bflb_dma_channel_lli_reload(struct bflb_device_s *dev,
                                struct bflb_dma_channel_lli_pool_s *lli_pool,
                                uint32_t max_lli_count,
                                struct bflb_dma_channel_lli_transfer_s *transfer,
                                uint32_t count);
```

**Parameters:**
- `dev` - Device handle
- `lli_pool` - Pointer to LLI pool (must be in SRAM)
- `max_lli_count` - Maximum number of LLIs in pool
- `transfer` - Pointer to transfer descriptors
- `count` - Number of transfers

**Returns:** Number of LLIs used, or negative error code

---

### bflb_dma_channel_lli_link_head

Enable continuous LLI mode (loop).

```c
void bflb_dma_channel_lli_link_head(struct bflb_device_s *dev,
                                    struct bflb_dma_channel_lli_pool_s *lli_pool,
                                    uint32_t used_lli_count);
```

---

### bflb_dma_channel_tcint_mask

Enable/disable transfer complete interrupt.

```c
void bflb_dma_channel_tcint_mask(struct bflb_device_s *dev, bool mask);
```

**Parameters:**
- `mask` - `true` to disable, `false` to enable

---

### bflb_dma_channel_get_tcint_status

Check transfer complete status.

```c
bool bflb_dma_channel_get_tcint_status(struct bflb_device_s *dev);
```

**Returns:** `true` if transfer complete

---

### bflb_dma_channel_tcint_clear

Clear transfer complete interrupt.

```c
void bflb_dma_channel_tcint_clear(struct bflb_device_s *dev);
```

---

### bflb_dma_feature_control

Control DMA features.

```c
int bflb_dma_feature_control(struct bflb_device_s *dev, int cmd, size_t arg);
```

**Commands:**
- `DMA_CMD_SET_SRCADDR_INCREMENT` - Set source increment mode
- `DMA_CMD_SET_DSTADDR_INCREMENT` - Set destination increment mode
- `DMA_CMD_SET_LLI_CONFIG` - Configure LLI transfer
- `DMA_CMD_GET_LLI_SRCADDR` - Get LLI source address
- `DMA_CMD_GET_LLI_DSTADDR` - Get LLI destination address
- `DMA_CMD_GET_LLI_CONTROL` - Get LLI control value
- `DMA_CMD_GET_LLI_COUNT` - Get LLI transfer count
- `DMA_CMD_SET_SUSPEND` - Suspend DMA transfer
- `DMA_CMD_SET_RESUME` - Resume DMA transfer
- `DMA_CMD_GET_TRANSFER_PENDING` - Check if transfer pending

---

## Usage Examples

### Memory to Memory Copy

```c
#include "bflb_dma.h"

static uint8_t src_buffer[1024];
static uint8_t dst_buffer[1024];
static struct bflb_device_s *dma_ch;

void dma_memcpy_callback(void *arg)
{
    printf("DMA transfer complete!\r\n");
}

void dma_memcpy_example(void)
{
    struct bflb_dma_channel_config_s config = {
        .direction = DMA_MEMORY_TO_MEMORY,
        .src_req = DMA_REQUEST_NONE,
        .dst_req = DMA_REQUEST_NONE,
        .src_addr_inc = DMA_ADDR_INCREMENT_ENABLE,
        .dst_addr_inc = DMA_ADDR_INCREMENT_ENABLE,
        .src_burst_count = DMA_BURST_INCR1,
        .dst_burst_count = DMA_BURST_INCR1,
        .src_width = DMA_DATA_WIDTH_32BIT,
        .dst_width = DMA_DATA_WIDTH_32BIT,
    };

    /* Get DMA channel 0 */
    dma_ch = bflb_device_get_by_name("dma0_ch0");
    
    /* Initialize channel */
    bflb_dma_channel_init(dma_ch, &config);
    
    /* Register callback */
    bflb_dma_channel_irq_attach(dma_ch, dma_memcpy_callback, NULL);
    
    /* Enable transfer complete interrupt */
    bflb_dma_channel_tcint_mask(dma_ch, false);
    
    /* Configure LLI for 1024 byte transfer */
    struct bflb_dma_channel_lli_pool_s lli;
    struct bflb_dma_channel_lli_transfer_s transfer = {
        .src_addr = (uint32_t)src_buffer,
        .dst_addr = (uint32_t)dst_buffer,
        .nbytes = 1024,
    };
    
    bflb_dma_channel_lli_reload(dma_ch, &lli, 1, &transfer, 1);
    
    /* Start transfer */
    bflb_dma_channel_start(dma_ch);
}
```

### UART TX with DMA

```c
#include "bflb_dma.h"
#include "bflb_uart.h"

static struct bflb_device_s *dma_ch;
static const uint8_t uart_tx_data[] = "Hello DMA UART!\r\n";

void dma_uart_tx_example(void)
{
    struct bflb_dma_channel_config_s config = {
        .direction = DMA_MEMORY_TO_PERIPH,
        .src_req = DMA_REQUEST_NONE,           /* Memory, no request needed */
        .dst_req = DMA_REQUEST_UART0_TX,        /* UART0 TX peripheral */
        .src_addr_inc = DMA_ADDR_INCREMENT_ENABLE,
        .dst_addr_inc = DMA_ADDR_INCREMENT_DISABLE,
        .src_burst_count = DMA_BURST_INCR1,
        .dst_burst_count = DMA_BURST_INCR1,
        .src_width = DMA_DATA_WIDTH_8BIT,
        .dst_width = DMA_DATA_WIDTH_8BIT,
    };

    dma_ch = bflb_device_get_by_name("dma0_ch1");
    bflb_dma_channel_init(dma_ch, &config);
    
    /* Configure transfer */
    struct bflb_dma_channel_lli_pool_s lli;
    struct bflb_dma_channel_lli_transfer_s transfer = {
        .src_addr = (uint32_t)uart_tx_data,
        .dst_addr = DMA_ADDR_UART0_TDR,
        .nbytes = sizeof(uart_tx_data),
    };
    
    bflb_dma_channel_lli_reload(dma_ch, &lli, 1, &transfer, 1);
    bflb_dma_channel_tcint_mask(dma_ch, false);
    bflb_dma_channel_start(dma_ch);
}
```

### ADC DMA Capture

```c
#include "bflb_dma.h"
#include "bflb_adc.h"

#define ADC_DMA_SAMPLE_COUNT 256

static uint32_t adc_buffer[ADC_DMA_SAMPLE_COUNT];
static struct bflb_device_s *dma_ch;

void adc_dma_example(void)
{
    struct bflb_dma_channel_config_s config = {
        .direction = DMA_PERIPH_TO_MEMORY,
        .src_req = DMA_REQUEST_ADC,              /* ADC peripheral */
        .dst_req = DMA_REQUEST_NONE,             /* Memory, no request needed */
        .src_addr_inc = DMA_ADDR_INCREMENT_DISABLE,
        .dst_addr_inc = DMA_ADDR_INCREMENT_ENABLE,
        .src_burst_count = DMA_BURST_INCR1,
        .dst_burst_count = DMA_BURST_INCR1,
        .src_width = DMA_DATA_WIDTH_16BIT,
        .dst_width = DMA_DATA_WIDTH_32BIT,
    };

    dma_ch = bflb_device_get_by_name("dma0_ch2");
    bflb_dma_channel_init(dma_ch, &config);
    
    /* Configure LLI */
    struct bflb_dma_channel_lli_pool_s lli;
    struct bflb_dma_channel_lli_transfer_s transfer = {
        .src_addr = DMA_ADDR_ADC_RDR,
        .dst_addr = (uint32_t)adc_buffer,
        .nbytes = sizeof(adc_buffer),
    };
    
    bflb_dma_channel_lli_reload(dma_ch, &lli, 1, &transfer, 1);
    bflb_dma_channel_tcint_mask(dma_ch, false);
    bflb_dma_channel_start(dma_ch);
    
    /* ADC is triggered separately and DMA captures results */
}
```

### Circular DMA (Continuous Transfer)

```c
void dma_circular_example(void)
{
    static uint8_t rx_buffer[512];
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

    struct bflb_device_s *dma_ch = bflb_device_get_by_name("dma0_ch3");
    bflb_dma_channel_init(dma_ch, &config);
    
    /* Create circular LLI chain */
    struct bflb_dma_channel_lli_pool_s lli_pool[2];
    
    /* First LLI: transfer first half */
    lli_pool[0].src_addr = DMA_ADDR_UART0_RDR;
    lli_pool[0].dst_addr = (uint32_t)rx_buffer;
    lli_pool[0].nextlli = (uint32_t)&lli_pool[1];
    lli_pool[0].control.bits.TransferSize = 256;
    lli_pool[0].control.bits.SWidth = 0;   /* 8-bit source */
    lli_pool[0].control.bits.DWidth = 0;   /* 8-bit dest */
    lli_pool[0].control.bits.SI = 0;       /* No source increment */
    lli_pool[0].control.bits.DI = 1;       /* Dest increment */
    
    /* Second LLI: transfer second half, loops back */
    lli_pool[1].src_addr = DMA_ADDR_UART0_RDR;
    lli_pool[1].dst_addr = (uint32_t)(rx_buffer + 256);
    lli_pool[1].nextlli = (uint32_t)&lli_pool[0];  /* Circular */
    lli_pool[1].control = lli_pool[0].control;
    
    bflb_dma_channel_lli_reload(dma_ch, lli_pool, 2, NULL, 0);
    bflb_dma_channel_start(dma_ch);
}
```

## Register-Level Overview

| Register | Offset | Description |
|----------|--------|-------------|
| `DMA_CH0_SAR` | `0x00` | Channel 0 Source Address |
| `DMA_CH0_DAR` | `0x04` | Channel 0 Destination Address |
| `DMA_CH0_LLP` | `0x08` | Channel 0 Linked List Pointer |
| `DMA_CH0_CTL` | `0x0C` | Channel 0 Control |
| `DMA_CH0_SSTAT` | `0x10` | Channel 0 Source Status |
| `DMA_CH0_DSTAT` | `0x14` | Channel 0 Destination Status |
| `DMA_CH0_SSTATAR` | `0x18` | Channel 0 Source Status Address |
| `DMA_CH0_DSTATAR` | `0x1C` | Channel 0 Destination Status Address |
| `DMA_CH0_CFG` | `0x20` | Channel 0 Configuration |
| `DMA_CH0_SGR` | `0x24` | Channel 0 Source Gather |
| `DMA_CH0_DSR` | `0x28` | Channel 0 Destination Scatter |

**Channel registers are at offsets 0x00 + (CH * 0x30)**

| Register | Offset | Description |
|----------|--------|-------------|
| `DMA_STATUS` | `0x100` | Status register |
| `DMA_CFG` | `0x104` | Configuration register |
| `DMA_CH_EN` | `0x108` | Channel enable |

## Interrupt Number

| Peripheral | IRQ Number |
|------------|------------|
| DMA0 | `DMA0_ALL_IRQn` (31) |
