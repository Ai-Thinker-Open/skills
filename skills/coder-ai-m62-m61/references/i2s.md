# BL616/BL618 I2S Audio Interface Documentation

## Overview

The BL616/BL618 I2S (Inter-IC Sound) interface is a hardware audio peripheral for stereo audio transmission. It supports master/slave modes, multiple data formats (I2S, left-justified, right-justified, DSP), and DMA operation.

**Base Address:** `0x2000AB00`

---

## Header Files

```c
#include "bflb_i2s.h"          // LHAL API header
#include "hardware/i2s_reg.h"  // Register definitions
```

---

## Register Map (I2S_BASE = 0x2000AB00)

| Offset | Register | Description |
|--------|----------|-------------|
| 0x00   | I2S_CONFIG    | I2S control configuration |
| 0x04   | I2S_INT_STS   | Interrupt status |
| 0x10   | I2S_BCLK_CONFIG | BCLK divider configuration |
| 0x80   | I2S_FIFO_CONFIG_0 | FIFO control, DMA enable |
| 0x84   | I2S_FIFO_CONFIG_1 | FIFO threshold and count |
| 0x88   | I2S_FIFO_WDATA | TX FIFO write data |
| 0x8C   | I2S_FIFO_RDATA | RX FIFO read data |
| 0xFC   | I2S_IO_CONFIG  | Signal inversion, deglitch |

---

## Register Details

### I2S_CONFIG (Offset 0x00)

| Bit | Name | Description |
|-----|------|-------------|
| 0   | I2S_CR_I2S_M_EN | Master mode enable |
| 1   | I2S_CR_I2S_S_EN | Slave mode enable |
| 2   | I2S_CR_I2S_TXD_EN | TX data output enable |
| 3   | I2S_CR_I2S_RXD_EN | RX data input enable |
| 4   | I2S_CR_MONO_MODE | Mono mode (1 channel) |
| 5   | I2S_CR_MUTE_MODE | Mute enable |
| 6   | I2S_CR_FS_1T_MODE | FS 1T mode (DSP short frame) |
| 7-8 | FS_CH_CNT | Frame channel count (0=1ch, 1=2ch, 2=3ch, 3=4ch, 4=6ch) |
| 12-13 | FRAME_SIZE | Frame/slot width (0=8bit, 1=16bit, 2=24bit, 3=32bit) |
| 14-15 | DATA_SIZE | Data width |
| 16-17 | I2S_MODE | Format mode (0=I2S/LJ, 1=RJ, 2=DSP) |
| 18  | ENDIAN | Bit endianness (0=MSB first) |
| 19  | MONO_RX_CH | Mono RX channel select (0=L, 1=R) |
| 20-24 | OFS_CNT | FS offset cycle count |
| 25  | OFS_EN | FS offset enable |

### I2S_INT_STS (Offset 0x04)

| Bit | Name | Description |
|-----|------|-------------|
| 0   | TXF_INT | TX FIFO threshold interrupt |
| 1   | RXF_INT | RX FIFO threshold interrupt |
| 2   | FER_INT | FIFO error interrupt |
| 8   | I2S_CR_I2S_TXF_MASK | TX interrupt mask |
| 9   | I2S_CR_I2S_RXF_MASK | RX interrupt mask |
| 10  | I2S_CR_I2S_FER_MASK | Error interrupt mask |
| 24  | I2S_CR_I2S_TXF_EN | TX interrupt enable |
| 25  | I2S_CR_I2S_RXF_EN | RX interrupt enable |
| 26  | I2S_CR_I2S_FER_EN | Error interrupt enable |

### I2S_BCLK_CONFIG (Offset 0x10)

| Bit | Name | Description |
|-----|------|-------------|
| 0-11 | BCLK_DIV_L | BCLK low period divider |
| 16-27 | BCLK_DIV_H | BCLK high period divider |

### I2S_FIFO_CONFIG_0 (Offset 0x80)

| Bit | Name | Description |
|-----|------|-------------|
| 0   | DMA_TX_EN | TX DMA enable |
| 1   | DMA_RX_EN | RX DMA enable |
| 2   | TX_FIFO_CLR | Clear TX FIFO |
| 3   | RX_FIFO_CLR | Clear RX FIFO |
| 4   | TX_FIFO_OVERFLOW | TX FIFO overflow flag |
| 5   | TX_FIFO_UNDERFLOW | TX FIFO underflow flag |
| 6   | RX_FIFO_OVERFLOW | RX FIFO overflow flag |
| 7   | RX_FIFO_UNDERFLOW | RX FIFO underflow flag |
| 8   | FIFO_LR_MERGE | L/R channel merge (one FIFO entry = both channels) |
| 9   | FIFO_LR_EXCHG | L/R channel exchange |
| 10  | FIFO_24B_LJ | 24-bit data in left-justified mode |

### I2S_FIFO_CONFIG_1 (Offset 0x84)

| Bit | Name | Description |
|-----|------|-------------|
| 0-4  | TX_FIFO_CNT | TX FIFO count |
| 8-12 | RX_FIFO_CNT | RX FIFO count |
| 16-19 | TX_FIFO_TH | TX FIFO threshold |
| 24-27 | RX_FIFO_TH | RX FIFO threshold |

### I2S_FIFO_WDATA (Offset 0x88)
Write-only. 32-bit TX FIFO data register.

### I2S_FIFO_RDATA (Offset 0x8C)
Read-only. 32-bit RX FIFO data register.

### I2S_IO_CONFIG (Offset 0xFC)

| Bit | Name | Description |
|-----|------|-------------|
| 0   | I2S_TXD_INV | TX data inversion |
| 1   | I2S_RXD_INV | RX data inversion |
| 2   | I2S_FS_INV | FS (word select) inversion |
| 3   | I2S_BCLK_INV | BCLK inversion |
| 4-6 | DEG_CNT | Deglitch cycle count |
| 7   | DEG_EN | Deglitch enable |

---

## Configuration Structure

```c
struct bflb_i2s_config_s {
    uint32_t bclk_freq_hz;      // BCLK frequency (Hz)
    uint8_t  role;              // I2S_ROLE_MASTER or I2S_ROLE_SLAVE
    uint8_t  format_mode;       // I2S_MODE_*
    uint8_t  channel_mode;      // I2S_CHANNEL_MODE_NUM_*
    uint8_t  frame_width;       // I2S_SLOT_WIDTH_*
    uint8_t  data_width;       // I2S_SLOT_WIDTH_*
    uint8_t  fs_offset_cycle;  // First bit offset
    uint8_t  tx_fifo_threshold;
    uint8_t  rx_fifo_threshold;
};
```

---

## Constants/Enums

### I2S Role
```c
#define I2S_ROLE_MASTER  0
#define I2S_ROLE_SLAVE   1
```

### Format Mode
```c
#define I2S_MODE_LEFT_JUSTIFIED       0  // Phillips I2S standard
#define I2S_MODE_RIGHT_JUSTIFIED      1  // Right-justified (Sony)
#define I2S_MODE_DSP_SHORT_FRAME_SYNC 2  // DSP Mode A/B short frame
#define I2S_MODE_DSP_LONG_FRAME_SYNC  3  // DSP Mode A/B long frame
```

### Channel Mode
```c
#define I2S_CHANNEL_MODE_NUM_1  0  // Mono mode
#define I2S_CHANNEL_MODE_NUM_2  1  // Stereo (2 channels)
#define I2S_CHANNEL_MODE_NUM_3  2  // 3 channels (DSP only)
#define I2S_CHANNEL_MODE_NUM_4  3  // 4 channels (DSP only)
#define I2S_CHANNEL_MODE_NUM_6  4  // 6 channels (DSP only)
```

### Slot/Data Width
```c
#define I2S_SLOT_WIDTH_8  0
#define I2S_SLOT_WIDTH_16 1
#define I2S_SLOT_WIDTH_24 2
#define I2S_SLOT_WIDTH_32 3
```

### Interrupt Status
```c
#define I2S_INTSTS_TX_FIFO   (1 << 0)
#define I2S_INTSTS_RX_FIFO   (1 << 1)
#define I2S_INTSTS_FIFO_ERR  (1 << 2)
```

### Feature Commands (I2S_CMD_*)
```c
#define I2S_CMD_CLEAR_TX_FIFO        0x01
#define I2S_CMD_CLEAR_RX_FIFO        0x02
#define I2S_CMD_GET_TX_FIFO_CNT      0x03
#define I2S_CMD_GET_RX_FIFO_CNT      0x04
#define I2S_CMD_SET_DEGLITCH_CNT     0x05
#define I2S_CMD_DATA_ENABLE          0x06
#define I2S_CMD_CHANNEL_LR_MERGE     0x07
#define I2S_CMD_CHANNEL_LR_EXCHG     0x08
#define I2S_CMD_MUTE                 0x09
#define I2S_CMD_BIT_REVERSE          0x0A
#define I2S_CMD_MONO_CHANEL_SEL      0x0B
```

### Data Enable Types
```c
#define I2S_CMD_DATA_ENABLE_TX  (1 << 1)
#define I2S_CMD_DATA_ENABLE_RX  (1 << 2)
```

---

## API Reference

### `bflb_i2s_init`

```c
void bflb_i2s_init(struct bflb_device_s *dev, const struct bflb_i2s_config_s *config);
```

Initialize I2S peripheral with configuration. Sets up:
- Master/slave mode
- Format mode (I2S/LJ/RJ/DSP)
- Channel count
- Frame and data width
- BCLK divider
- FIFO thresholds
- Signal polarities

**Example:**
```c
struct bflb_i2s_config_s i2s_cfg = {
    .bclk_freq_hz = 16000 * 16 * 2,  // 512 kHz for 16kHz stereo 16-bit
    .role = I2S_ROLE_MASTER,
    .format_mode = I2S_MODE_LEFT_JUSTIFIED,
    .channel_mode = I2S_CHANNEL_MODE_NUM_2,
    .frame_width = I2S_SLOT_WIDTH_16,
    .data_width = I2S_SLOT_WIDTH_16,
    .fs_offset_cycle = 0,
    .tx_fifo_threshold = 7,
    .rx_fifo_threshold = 7,
};

struct bflb_device_s *i2s = bflb_device_get_by_name("i2s0");
bflb_i2s_init(i2s, &i2s_cfg);
```

---

### `bflb_i2s_deinit`

```c
void bflb_i2s_deinit(struct bflb_device_s *dev);
```

Disable I2S and release resources.

---

### `bflb_i2s_link_txdma`

```c
void bflb_i2s_link_txdma(struct bflb_device_s *dev, bool enable);
```

Enable/disable TX DMA. When enabled, DMA handles data transfer from memory to I2S TX FIFO.

---

### `bflb_i2s_link_rxdma`

```c
void bflb_i2s_link_rxdma(struct bflb_device_s *dev, bool enable);
```

Enable/disable RX DMA. When enabled, DMA handles data transfer from I2S RX FIFO to memory.

---

### `bflb_i2s_txint_mask`

```c
void bflb_i2s_txint_mask(struct bflb_device_s *dev, bool mask);
```

Mask/unmask TX FIFO threshold interrupt. `mask=true` disables interrupt.

---

### `bflb_i2s_rxint_mask`

```c
void bflb_i2s_rxint_mask(struct bflb_device_s *dev, bool mask);
```

Mask/unmask RX FIFO threshold interrupt. `mask=true` disables interrupt.

---

### `bflb_i2s_errint_mask`

```c
void bflb_i2s_errint_mask(struct bflb_device_s *dev, bool mask);
```

Mask/unmask FIFO error interrupt. `mask=true` disables interrupt.

---

### `bflb_i2s_get_intstatus`

```c
uint32_t bflb_i2s_get_intstatus(struct bflb_device_s *dev);
```

Get current interrupt status. Returns OR'd flags:
- `I2S_INTSTS_TX_FIFO`
- `I2S_INTSTS_RX_FIFO`
- `I2S_INTSTS_FIFO_ERR`

---

### `bflb_i2s_feature_control`

```c
int bflb_i2s_feature_control(struct bflb_device_s *dev, int cmd, size_t arg);
```

Execute various feature commands.

**Commands:**

| Command | Arg | Description |
|---------|-----|-------------|
| `I2S_CMD_CLEAR_TX_FIFO` | 0 | Clear TX FIFO |
| `I2S_CMD_CLEAR_RX_FIFO` | 0 | Clear RX FIFO |
| `I2S_CMD_GET_TX_FIFO_CNT` | 0 | Returns TX FIFO count |
| `I2S_CMD_GET_RX_FIFO_CNT` | 0 | Returns RX FIFO count |
| `I2S_CMD_SET_DEGLITCH_CNT` | cycle_count | Set deglitch cycles (1-7) |
| `I2S_CMD_DATA_ENABLE` | `I2S_CMD_DATA_ENABLE_TX\|RX` | Enable TX/RX data lines |
| `I2S_CMD_CHANNEL_LR_MERGE` | true/false | Merge L/R in one FIFO entry |
| `I2S_CMD_CHANNEL_LR_EXCHG` | true/false | Exchange L/R channels |
| `I2S_CMD_MUTE` | true/false | Enable/disable mute |
| `I2S_CMD_BIT_REVERSE` | true/false | MSB/LSB first |
| `I2S_CMD_MONO_CHANEL_SEL` | false=L-ch, true=R-ch | Mono channel select |

---

## DMA Operation

### DMA Requests
- **TX:** `DMA_REQUEST_I2S_TX` → memory to I2S (write to TDR)
- **RX:** `DMA_REQUEST_I2S_RX` → I2S to memory (read from RDR)

### DMA Address Constants
```c
DMA_ADDR_I2S_TDR  // TX data register address
DMA_ADDR_I2S_RDR  // RX data register address
```

### DMA Configuration Example (TX)

```c
struct bflb_dma_channel_config_s dma_cfg = {
    .direction = DMA_MEMORY_TO_PERIPH,
    .src_req = DMA_REQUEST_NONE,
    .dst_req = DMA_REQUEST_I2S_TX,
    .src_addr_inc = DMA_ADDR_INCREMENT_ENABLE,
    .dst_addr_inc = DMA_ADDR_INCREMENT_DISABLE,
    .src_burst_count = DMA_BURST_INCR8,
    .dst_burst_count = DMA_BURST_INCR8,
    .src_width = DMA_DATA_WIDTH_16BIT,
    .dst_width = DMA_DATA_WIDTH_16BIT,
};

struct bflb_device_s *dma_ch = bflb_device_get_by_name("dma0");
bflb_dma_channel_init(dma_ch, &dma_cfg);
bflb_dma_channel_irq_attach(dma_ch, tx_dma_isr, NULL);
bflb_i2s_link_txdma(i2s, true);  // Enable I2S TX DMA
```

### DMA LLI Transfer Setup

```c
// Configure LLI entry
lli_pool[0].src_addr = (uint32_t)src_buffer;
lli_pool[0].dst_addr = DMA_ADDR_I2S_TDR;
lli_pool[0].control.bits.TransferSize = transfer_size;
lli_pool[0].control.bits.I = 1;  // Last LLI
lli_pool[0].nextlli = 0;

// Start transfer
bflb_dma_feature_control(dma_ch, DMA_CMD_SET_LLI_CONFIG, (uint32_t)&lli_pool[0]);
bflb_dma_channel_start(dma_ch);
```

---

## Working Code Example

### Full I2S Master TX with DMA

```c
#include "bflb_i2s.h"
#include "bflb_dma.h"
#include "bflb_clock.h"

static struct bflb_device_s *i2s;
static struct bflb_device_s *dma_ch;
static ATTR_NOCACHE_RAM_SECTION __ALIGNED(32) uint16_t tx_buffer[1024];

static void dma_isr(void *arg)
{
    // Reuse buffer, restart DMA, etc.
}

void i2s_audio_init(void)
{
    struct bflb_i2s_config_s i2s_cfg = {
        .bclk_freq_hz = 16000 * 16 * 2,  // 512 kHz
        .role = I2S_ROLE_MASTER,
        .format_mode = I2S_MODE_LEFT_JUSTIFIED,
        .channel_mode = I2S_CHANNEL_MODE_NUM_2,
        .frame_width = I2S_SLOT_WIDTH_16,
        .data_width = I2S_SLOT_WIDTH_16,
        .fs_offset_cycle = 0,
        .tx_fifo_threshold = 7,
        .rx_fifo_threshold = 7,
    };
    
    struct bflb_dma_channel_config_s dma_cfg = {
        .direction = DMA_MEMORY_TO_PERIPH,
        .src_req = DMA_REQUEST_NONE,
        .dst_req = DMA_REQUEST_I2S_TX,
        .src_addr_inc = DMA_ADDR_INCREMENT_ENABLE,
        .dst_addr_inc = DMA_ADDR_INCREMENT_DISABLE,
        .src_burst_count = DMA_BURST_INCR8,
        .dst_burst_count = DMA_BURST_INCR8,
        .src_width = DMA_DATA_WIDTH_16BIT,
        .dst_width = DMA_DATA_WIDTH_16BIT,
    };
    
    // Get devices
    i2s = bflb_device_get_by_name("i2s0");
    dma_ch = bflb_device_get_by_name("dma0");
    
    // Init I2S
    bflb_i2s_init(i2s, &i2s_cfg);
    
    // Init DMA
    bflb_dma_channel_init(dma_ch, &dma_cfg);
    bflb_dma_channel_irq_attach(dma_ch, dma_isr, NULL);
    
    // Link DMA to I2S
    bflb_i2s_link_txdma(i2s, true);
    
    // Enable TX
    bflb_i2s_feature_control(i2s, I2S_CMD_DATA_ENABLE, I2S_CMD_DATA_ENABLE_TX);
}

void i2s_send_audio_frame(uint16_t *data, uint32_t size)
{
    struct bflb_dma_channel_lli_pool_s lli;
    
    lli.src_addr = (uint32_t)data;
    lli.dst_addr = DMA_ADDR_I2S_TDR;
    lli.control.bits.TransferSize = size / 2;  // 16-bit samples
    lli.control.bits.I = 1;
    lli.nextlli = 0;
    
    bflb_dma_feature_control(dma_ch, DMA_CMD_SET_LLI_CONFIG, (uint32_t)&lli);
    bflb_dma_channel_start(dma_ch);
}
```

---

## Register-Level Programming

### Manual TX/RX (Polling Mode)

```c
// TX a sample (32-bit register)
putreg32(sample_data, I2S_BASE + I2S_FIFO_WDATA_OFFSET);

// RX a sample
uint32_t data = getreg32(I2S_BASE + I2S_FIFO_RDATA_OFFSET);

// Check FIFO status
uint32_t fifo_sts = getreg32(I2S_BASE + I2S_FIFO_CONFIG_1_OFFSET);
uint32_t tx_cnt = (fifo_sts & I2S_TX_FIFO_CNT_MASK) >> I2S_TX_FIFO_CNT_SHIFT;
uint32_t rx_cnt = (fifo_sts & I2S_RX_FIFO_CNT_MASK) >> I2S_RX_FIFO_CNT_SHIFT;
```

### Manual I2S Init (Register-Level)

```c
// Disable I2S
uint32_t reg = getreg32(I2S_BASE + I2S_CONFIG_OFFSET);
reg &= ~(I2S_CR_I2S_M_EN | I2S_CR_I2S_S_EN | I2S_CR_I2S_TXD_EN | I2S_CR_I2S_RXD_EN);
putreg32(reg, I2S_BASE + I2S_CONFIG_OFFSET);

// Configure: Master, I2S format, stereo, 16-bit
reg = I2S_CR_I2S_M_EN;  // Master enable
reg |= (1 << I2S_CR_FRAME_SIZE_SHIFT);   // 16-bit frame
reg |= (1 << I2S_CR_DATA_SIZE_SHIFT);    // 16-bit data
putreg32(reg, I2S_BASE + I2S_CONFIG_OFFSET);

// Configure BCLK divider (bclk = periph_clk / (div+2) * 2)
reg = getreg32(I2S_BASE + I2S_BCLK_CONFIG_OFFSET);
reg &= ~(I2S_CR_BCLK_DIV_L_MASK | I2S_CR_BCLK_DIV_H_MASK);
reg |= (div / 2) << I2S_CR_BCLK_DIV_L_SHIFT;
reg |= (div - (div / 2)) << I2S_CR_BCLK_DIV_H_SHIFT;
putreg32(reg, I2S_BASE + I2S_BCLK_CONFIG_OFFSET);

// Configure FIFO thresholds
reg = getreg32(I2S_BASE + I2S_FIFO_CONFIG_1_OFFSET);
reg &= ~(I2S_TX_FIFO_TH_MASK | I2S_RX_FIFO_TH_MASK);
reg |= (7 << I2S_TX_FIFO_TH_SHIFT) | (7 << I2S_RX_FIFO_TH_SHIFT);
putreg32(reg, I2S_BASE + I2S_FIFO_CONFIG_1_OFFSET);

// Clear FIFOs, disable DMA
reg = getreg32(I2S_BASE + I2S_FIFO_CONFIG_0_OFFSET);
reg |= I2S_TX_FIFO_CLR | I2S_RX_FIFO_CLR;
reg &= ~(I2S_DMA_TX_EN | I2S_DMA_RX_EN);
putreg32(reg, I2S_BASE + I2S_FIFO_CONFIG_0_OFFSET);

// Enable TX data output
reg = getreg32(I2S_BASE + I2S_CONFIG_OFFSET);
reg |= I2S_CR_I2S_TXD_EN;
putreg32(reg, I2S_BASE + I2S_CONFIG_OFFSET);
```

---

## Timing Relationships

**Sampling Rate Calculation:**
```
bclk_freq = sampling_rate × frame_width × channel_count
```

**Example (16kHz stereo 16-bit):**
```
bclk_freq = 16000 × 16 × 2 = 512000 Hz (512 kHz)
```

**Example (48kHz stereo 32-bit):**
```
bclk_freq = 48000 × 32 × 2 = 3072000 Hz (3.072 MHz)
```

---

## Notes

1. **FIFO Depth:** 16 entries × 32 bits each
2. **DMA Burst:** Recommend `DMA_BURST_INCR8` for optimal throughput
3. **Mono Mode:** Use `I2S_CHANNEL_MODE_NUM_1` with `I2S_CMD_MONO_CHANEL_SEL` to select L or R channel
4. **DSP Mode:** Supports 1/2/3/4/6 channels with frame_sync as a pulse (short) or width (long)
5. **Deglitch:** Useful for filtering noisy input signals; set cycle count 1-7
