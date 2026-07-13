# DMA API Reference

> Source file: `components/platform/hosal/include/hosal_dma.h`

## Macro Definitions

```c
#define HOSAL_DMA_INT_TRANS_COMPLETE 0  // Transfer complete interrupt
#define HOSAL_DMA_INT_TRANS_ERROR    1  // Transfer error interrupt
```

## Type Definitions

### `hosal_dma_irq_t` — DMA Interrupt Callback Type

```c
typedef void (*hosal_dma_irq_t)(void *p_arg, uint32_t flag);
```

- `flag` = `0` (`HOSAL_DMA_INT_TRANS_COMPLETE`): Transfer complete
- `flag` = `1` (`HOSAL_DMA_INT_TRANS_ERROR`): Transfer error

### `hosal_dma_chan_t` — DMA Channel Number

```c
typedef int hosal_dma_chan_t;
```

Channel numbers are integers (e.g., 0, 1, 2, etc.).

### `hosal_dma_dev_t` — DMA Device Structure

```c
typedef struct hosal_dma_dev {
    int max_chans;                    // Maximum number of channels
    struct hosal_dma_chan *used_chan; // Array of used channels
    void *priv;
} hosal_dma_dev_t;
```

## Function API

### `hosal_dma_init`

Initialize the DMA global controller.

```c
int hosal_dma_init(void);
```

**Return value**: `0` success, `EIO` failure

---

### `hosal_dma_chan_request`

Request a DMA channel.

```c
hosal_dma_chan_t hosal_dma_chan_request(int flag);
```

| Parameter | Description |
|------|------|
| `flag` | Request flag (usually set to 0) |

**Return value**: Returns channel number (>=0) on success, negative number on failure

---

### `hosal_dma_chan_release`

Release a DMA channel.

```c
int hosal_dma_chan_release(hosal_dma_chan_t chan);
```

| Parameter | Description |
|------|------|
| `chan` | DMA channel number |

**Return value**: `0` success, `EIO` failure

---

### `hosal_dma_chan_start`

Start DMA transfer.

```c
int hosal_dma_chan_start(hosal_dma_chan_t chan);
```

---

### `hosal_dma_chan_stop`

Stop DMA transfer.

```c
int hosal_dma_chan_stop(hosal_dma_chan_t chan);
```

---

### `hosal_dma_irq_callback_set`

Set DMA transfer completion/error interrupt callback.

```c
int hosal_dma_irq_callback_set(hosal_dma_chan_t chan,
                               hosal_dma_irq_t pfn,
                               void *p_arg);
```

---

### `hosal_dma_finalize`

Release the DMA global controller.

```c
int hosal_dma_finalize(void);
```

## Usage Example

```c
#include "hal_dma.h"

// Global DMA initialization (usually called once during system initialization)
hosal_dma_init();

// Request a channel
hosal_dma_chan_t chan = hosal_dma_chan_request(0);
if (chan < 0) {
    // Request failed
}

// Set interrupt callback
hosal_dma_irq_callback_set(chan, my_dma_callback, NULL);

// Start transfer (actual transfer is triggered by peripheral driver)
hosal_dma_chan_start(chan);

// Stop after transfer completes
hosal_dma_chan_stop(chan);

// Release the channel
hosal_dma_chan_release(chan);
```

---

## Register-Level Programming

> Register Header: `components/platform/soc/bl602/bl602_std/bl602_std/Device/Bouffalo/BL602/Peripherals/dma_reg.h`  
> Base Address: `DMA_BASE = 0x4000C000`

### Register Overview

The DMA controller has 8 channels. Each channel occupies 0x1C bytes. Channel N registers start at `DMA_BASE + N * 0x1C`.

| Offset (ch N) | Name    | Description                              |
|---------------|---------|------------------------------------------|
| 0x00          | SAR     | Source address                           |
| 0x04          | DAR     | Destination address                      |
| 0x08          | CHAR    | Chain address (linked list pointer)       |
| 0x0C          | CTRLH   | Control high: widths, burst, block size  |
| 0x10          | CTRLG   | Control: enable, handshake, mode         |
| 0x14          | SR      | Status: done, block done, error          |
| 0x18          | PER     | Peripheral handshake number              |

### Key Register Fields

**SAR / DAR — Source/Destination Address (32-bit)**
Holds the physical source or destination address for the transfer.

**CHAR — Chain Address Register (32-bit)**
Pointer to next DMA descriptor (linked-list mode). Set to 0 for single-block transfers.

**CTRLH — Control High (32-bit)**

| Bits    | Name           | Description                                      |
|---------|----------------|--------------------------------------------------|
| [27:26] | src_width      | Source data width: 0=byte, 1=halfword, 2=word   |
| [25:24] | dst_width      | Destination data width: 0=byte, 1=halfword, 2=word |
| [23:20] | src_burst_size | Source burst transaction length (0=1, 1=4, etc.)|
| [19:14] | block_size     | Number of transfers per block minus 1            |
| [13:8]  | dst_burst_size | Destination burst transaction length             |

**CTRLG — Control (32-bit)**

| Bits | Name          | Description                                    |
|------|---------------|------------------------------------------------|
| 0    | channel_enable| Channel enable (1=enable, 0=disable)          |
| 1    | handshake_mode| Handshake mode (1=hardware handshake, 0=software) |
| 4    | dma_mode      | DMA mode (1=linked list, 0=basic)             |

**SR — Status Register (32-bit)**

| Bits | Name         | Description                          |
|------|--------------|--------------------------------------|
| 0    | channel_done | Transfer complete for this channel  |
| 1    | block_done   | Block transfer done                  |
| 2    | error        | DMA error occurred                   |

**PER — Peripheral Handshake Number (32-bit)**

| Bits   | Name          | Description                            |
|--------|---------------|----------------------------------------|
| [7:4]  | handshake_num | Peripheral handshake select (for hardware handshake mode) |
| [9:8]  | priority      | Channel priority (0-3)                |

### Register-Level Code Example

```c
#include <stdint.h>

#define DMA_BASE   0x4000C000UL
#define DMA_CHAN_SIZE 0x1C  /* bytes per channel */

/* Per-channel register offsets */
#define DMA_SAR(ch)   *(volatile uint32_t *)(DMA_BASE + (ch) * DMA_CHAN_SIZE + 0x00)
#define DMA_DAR(ch)   *(volatile uint32_t *)(DMA_BASE + (ch) * DMA_CHAN_SIZE + 0x04)
#define DMA_CHAR(ch)  *(volatile uint32_t *)(DMA_BASE + (ch) * DMA_CHAN_SIZE + 0x08)
#define DMA_CTRLH(ch) *(volatile uint32_t *)(DMA_BASE + (ch) * DMA_CHAN_SIZE + 0x0C)
#define DMA_CTRLG(ch) *(volatile uint32_t *)(DMA_BASE + (ch) * DMA_CHAN_SIZE + 0x10)
#define DMA_SR(ch)    *(volatile uint32_t *)(DMA_BASE + (ch) * DMA_CHAN_SIZE + 0x14)
#define DMA_PER(ch)   *(volatile uint32_t *)(DMA_BASE + (ch) * DMA_CHAN_SIZE + 0x18)

/* Build CTRLH value for a memory-to-memory transfer
 * width=2 (word = 4 bytes), burst=1 (4 beats), block_size = count-1
 * For block_size: if count=256 transfers, block_size = 255 (bits[19:14])
 */
static uint32_t build_ctrlh(uint32_t count)
{
    return (2 << 26)   /* src_width = 2 (word)  */
         | (2 << 24)   /* dst_width = 2 (word)  */
         | (1 << 20)   /* src_burst_size = 1 (burst of 4 beats) */
         | ((count - 1) & 0x3F) << 14;  /* block_size [19:14] */
}

/* Polls channel_done bit in SR */
static void dma_wait_done(uint8_t ch)
{
    while ((DMA_SR(ch) & 0x01) == 0) {
        /* spin */
    }
}

/* Start a memory-to-memory DMA copy on channel 0.
 * Copy count words from src to dst.
 * NOTE: Ensure src and dst are DMA-capable memory regions.
 */
void dma_memcpy(uint32_t *dst, const uint32_t *src, uint32_t count)
{
    uint8_t ch = 0;

    /* Disable channel before configuring */
    DMA_CTRLG(ch) = 0x00;

    /* Source and destination addresses */
    DMA_SAR(ch) = (uint32_t)src;
    DMA_DAR(ch) = (uint32_t)dst;

    /* No linked list */
    DMA_CHAR(ch) = 0;

    /* Control: word transfers, burst of 4, block_size = count-1 */
    DMA_CTRLH(ch) = build_ctrlh(count);

    /* Configuration: enable channel, software trigger (handshake_num=0) */
    DMA_PER(ch)   = 0 << 4;     /* handshake_num = 0 (software) */
    DMA_CTRLG(ch) = 0 << 4      /* dma_mode = 0 (basic) */
                 | 0 << 1        /* handshake_mode = 0 (software trigger) */
                 | (1 << 0);     /* channel_enable = 1 */

    /* Poll for completion */
    dma_wait_done(ch);

    /* Disable channel */
    DMA_CTRLG(ch) = 0x00;
}

/* Example: Copy 256 words (1 KiB) using channel 1 */
void dma_reg_example(void)
{
    uint32_t src_buf[256];
    uint32_t dst_buf[256];
    int i;

    for (i = 0; i < 256; i++) {
        src_buf[i] = i * 2;
    }

    /* Configure channel 1 for memory-to-memory copy of 256 words */
    DMA_CTRLG(1) = 0x00;

    DMA_SAR(1) = (uint32_t)src_buf;
    DMA_DAR(1) = (uint32_t)dst_buf;
    DMA_CHAR(1) = 0;

    DMA_CTRLH(1) = (2 << 26)   /* src_width = word */
                 | (2 << 24)   /* dst_width = word */
                 | (1 << 20)   /* src_burst_size = 4 beats */
                 | ((256 - 1) & 0x3F) << 14;  /* block_size = 255 */

    DMA_PER(1)   = 0 << 4;     /* handshake_num = 0 (software) */
    DMA_CTRLG(1) = (1 << 0);   /* channel_enable */

    dma_wait_done(1);

    DMA_CTRLG(1) = 0x00;

    /* dst_buf now contains identical data to src_buf */
}
```
