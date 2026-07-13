# EMAC Ethernet Driver Documentation

## Overview

The EMAC (Ethernet Media Access Controller) driver for BL616/BL618 provides Ethernet connectivity via RMII (Reduced Media Independent Interface). The driver is part of the Bouffalo Lab Hardware Abstraction Layer (LHAL).

## Hardware Architecture

### Buffer Descriptor Layout

```
Buffer Hardware Descriptor Table (8 bytes each):
|---------------------|-------------------|---------------------------|
|   Address field     |       Length      |         Attribute         |
|---------------------|-------------------|---------------------------|
|63                 32|31               16|15                       00|
|   32-bit address    |   16-bit length   | 16-bit control and status|
```

### Key Hardware Parameters

| Parameter | Value |
|-----------|-------|
| TX BD Max | 64 (must be power of 2) |
| RX BD Max | 64 (must be power of 2) |
| Max Ethernet Packet | 1524 bytes |
| TX Buffer Size | ETH_TX_BUFFER_SIZE (default 1524) |
| RX Buffer Size | ETH_RX_BUFFER_SIZE (default 1524) |

## Register Map (Base: EMAC_BASE)

| Offset | Register | Description |
|--------|----------|-------------|
| 0x0 | EMAC_MODE | Mode configuration |
| 0x4 | EMAC_INT_SOURCE | Interrupt source flags |
| 0x8 | EMAC_INT_MASK | Interrupt mask |
| 0xC | EMAC_IPGT | Inter-packet gap timing |
| 0x18 | EMAC_PACKETLEN | Min/Max frame length |
| 0x1C | EMAC_COLLCONFIG | Collision configuration |
| 0x20 | EMAC_TX_BD_NUM | TX BD number and pointers |
| 0x28 | EMAC_MIIMODE | MII clock divider |
| 0x2C | EMAC_MIICOMMAND | MII command |
| 0x30 | EMAC_MIIADDRESS | MII phy/reg address |
| 0x34 | EMAC_MIITX_DATA | MII TX data |
| 0x38 | EMAC_MIIRX_DATA | MII RX data |
| 0x3C | EMAC_MIISTATUS | MII status |
| 0x40 | EMAC_MAC_ADDR0 | MAC address B2-B5 |
| 0x44 | EMAC_MAC_ADDR1 | MAC address B0-B1 |
| 0x48 | EMAC_HASH0_ADDR | Hash table 0 |
| 0x4C | EMAC_HASH1_ADDR | Hash table 1 |
| 0x50 | EMAC_TXCTRL | TX pause frame control |
| 0x400 | EMAC_DMA_DESC | DMA BD descriptor base |

## EMAC_MODE Register Bits

| Bit | Name | Description |
|-----|------|-------------|
| 0 | EMAC_RX_EN | RX enable |
| 1 | EMAC_TX_EN | TX enable |
| 2 | EMAC_NOPRE | No preamble (0=preamble enabled) |
| 3 | EMAC_BRO | Broadcast reception |
| 5 | EMAC_PRO | Promiscuous mode |
| 6 | EMAC_IFG | Ignore IFG requirement |
| 10 | EMAC_FULLD | Full duplex |
| 13 | EMAC_CRCEN | CRC enable |
| 14 | EMAC_HUGEN | Huge frame enable |
| 15 | EMAC_PAD | Padding enable |
| 16 | EMAC_RECSMALL | Receive small frames |
| 17 | EMAC_RMII_EN | RMII mode enable |
| 18 | EMAC_100M | 100M mode (BL616CL/BL618DG only) |

## Interrupt Sources

| Bit | Name | Description |
|-----|------|-------------|
| 0 | EMAC_TXB | TX buffer interrupt |
| 1 | EMAC_TXE | TX error interrupt |
| 2 | EMAC_RXB | RX buffer interrupt |
| 3 | EMAC_RXE | RX error interrupt |
| 4 | EMAC_BUSY | RX busy (no buffer) |
| 5 | EMAC_TXC | TX complete |
| 6 | EMAC_RXC | RX complete |

## TX Buffer Descriptor (BD) Format

| Bit | Name | Description |
|-----|------|-------------|
| 0 | CS | Carrier Sense Lost |
| 1 | DF | Defer Indication |
| 2 | LC | Late Collision |
| 3 | RL | Retransmission Limit |
| 4-7 | RTRY | Retry Count |
| 8 | UR | Underrun |
| 10 | EOF | End of Frame |
| 11 | CRC | CRC Enable |
| 12 | PAD | PAD Enable |
| 13 | WR | Wrap (last BD) |
| 14 | IRQ | Interrupt Request Enable |
| 15 | RD | Ready (buffer ready for TX) |
| 16-31 | LEN | TX data buffer length |

## RX Buffer Descriptor (BD) Format

| Bit | Name | Description |
|-----|------|-------------|
| 0 | LC | Late Collision |
| 1 | CRC | RX CRC Error |
| 2 | SF | Short Frame |
| 3 | TL | Too Long |
| 4 | DN | Dribble Nibble |
| 5 | RE | Receive Error |
| 6 | OR | Overrun |
| 7 | M | Miss |
| 8 | CF | Control Frame Received |
| 13 | WR | Wrap (last BD) |
| 14 | IRQ | Interrupt Request Enable |
| 15 | E | Empty (buffer ready for RX) |
| 16-31 | LEN | RX data buffer length |

## API Reference

### Configuration Structure

```c
struct bflb_emac_config_s {
    uint8_t mac_addr[6];      // MAC address
    bool clk_internal_mode;    // true=ref_clk out, false=ref_clk in
    uint8_t md_clk_div;        // MDIO clock divider
    uint8_t duplex_mode;       // 0=half, 1=full
    uint16_t speed;            // speed (unused in base BL616)
    uint16_t min_frame_len;    // minimum frame length
    uint16_t max_frame_len;    // maximum frame length
};
```

### Transaction Descriptor

```c
struct bflb_emac_trans_desc_s {
    void *buff_addr;           // buffer address
    uint16_t data_len;         // data length
    uint8_t attr_flag;         // attribute flags
    uint8_t err_status;        // error status
};
```

### TX Attribute Flags

```c
#define EMAC_TX_FLAG_FRAGMENT  (1 << 0)  // BD does not contain EOF
#define EMAC_TX_FLAG_NO_INT     (1 << 1)  // No interrupt after TX
#define EMAC_TX_FLAG_NO_CRC     (1 << 2)  // No CRC attached
#define EMAC_TX_FLAG_NO_PAD     (1 << 3)  // No padding appended
```

### TX Error Status

```c
#define EMAC_TX_STA_ERR_COLLISION     (1 << 0)  // Late Collision
#define EMAC_TX_STA_ERR_CS            (1 << 1)  // Carrier Sense Lost
#define EMAC_TX_STA_ERR_RETRY_LIMIT   (1 << 2)  // Retransmission Limit
#define EMAC_TX_STA_ERR_FIFO          (1 << 3)  // FIFO error
#define EMAC_TX_STA_ERR_UNKNOWN       (1 << 4)  // Unknown error
```

### RX Error Status

```c
#define EMAC_RX_STA_ERR_CRC           (1 << 0)  // CRC error
#define EMAC_RX_STA_ERR_COLLISION     (1 << 1)  // Collision error
#define EMAC_RX_STA_ERR_LONG_FRAME    (1 << 2)  // Frame too long
#define EMAC_RX_STA_ERR_FIFO          (1 << 3)  // FIFO error
```

### IRQ Events

```c
#define EMAC_IRQ_EVENT_RX_BUSY        (1)   // RX busy, no buffer
#define EMAC_IRQ_EVENT_RX_FRAME       (2)   // RX frame received
#define EMAC_IRQ_EVENT_RX_CTRL_FRAME  (3)   // RX control frame
#define EMAC_IRQ_EVENT_RX_ERR_FRAME   (4)   // RX frame error
#define EMAC_IRQ_EVENT_TX_FRAME       (5)   // TX frame complete
#define EMAC_IRQ_EVENT_TX_ERR_FRAME   (6)   // TX frame error
```

### Feature Control Commands

```c
#define EMAC_CMD_SET_TX_EN            (0)
#define EMAC_CMD_SET_TX_AUTO_PADDING   (1)
#define EMAC_CMD_SET_TX_CRC_FIELD_EN  (2)
#define EMAC_CMD_SET_TX_PREAMBLE      (3)
#define EMAC_CMD_SET_TX_GAP_CLK       (4)
#define EMAC_CMD_SET_TX_COLLISION     (5)
#define EMAC_CMD_SET_TX_MAXRET        (6)
#define EMAC_CMD_SET_RX_EN            (7)
#define EMAC_CMD_SET_RX_SMALL_FRAME   (8)
#define EMAC_CMD_SET_RX_HUGE_FRAME    (9)
#define EMAC_CMD_SET_RX_GAP_CHECK     (10)
#define EMAC_CMD_SET_RX_PROMISCUOUS   (11)
#define EMAC_CMD_SET_RX_BROADCASE     (12)
#define EMAC_CMD_SET_FULL_DUPLEX      (13)
#define EMAC_CMD_SET_SPEED_100M       (14)
#define EMAC_CMD_SET_SPEED_10M        (15)  // BL616CL/BL618DG only
#define EMAC_CMD_SET_MAC_RX_CLK_INVERT (16)
#define EMAC_CMD_GET_TX_DB_AVAILABLE  (20)
#define EMAC_CMD_GET_RX_DB_AVAILABLE  (21)
#define EMAC_CMD_GET_TX_BD_PTR        (22)
#define EMAC_CMD_GET_RX_BD_PTR        (23)
#define EMAC_CMD_SET_PHY_ADDRESS      (24)
#define EMAC_CMD_SET_SPEED_1000M      (25)
```

## Initialization Sequence

```c
#include "bflb_emac.h"
#include "bflb_clock.h"

// EMAC device handle
struct bflb_device_s *emac0;

// Configuration
static struct bflb_emac_config_s emac_cfg = {
    .mac_addr = {0xAA, 0xBB, 0xCC, 0xDD, 0xEE, 0xFF},
    .clk_internal_mode = false,  // ref_clk input mode
#if defined(BL616CL) || defined(BL618DG)
    .md_clk_div = 79,
#else
    .md_clk_div = 39,
#endif
    .min_frame_len = 64,
    .max_frame_len = 1518,
};

// Get EMAC device
emac0 = bflb_device_get_by_name("emac0");
if (emac0 == NULL) {
    return -1;
}

// Initialize EMAC
bflb_emac_init(emac0, &emac_cfg);

// Attach IRQ callback
bflb_emac_irq_attach(emac0, eth_emac_irq_cb, NULL);

// Enable TX/RX (via feature control)
bflb_emac_feature_control(emac0, EMAC_CMD_SET_TX_EN, true);
bflb_emac_feature_control(emac0, EMAC_CMD_SET_RX_EN, true);
```

## IRQ Callback Example

```c
static void eth_emac_irq_cb(void *arg, uint32_t irq_event, 
                           struct bflb_emac_trans_desc_s *trans_desc)
{
    switch (irq_event) {
        case EMAC_IRQ_EVENT_RX_FRAME:
            // Process received data
            // trans_desc->buff_addr contains data
            // trans_desc->data_len contains length
            process_rx_packet(trans_desc->buff_addr, trans_desc->data_len);
            // Re-queue the buffer
            bflb_emac_queue_rx_push(emac0, trans_desc);
            break;
            
        case EMAC_IRQ_EVENT_TX_FRAME:
            // TX complete - return buffer to pool
            return_tx_buffer(trans_desc);
            break;
            
        case EMAC_IRQ_EVENT_RX_ERR_FRAME:
            // Handle RX error
            handle_rx_error(trans_desc->err_status);
            bflb_emac_queue_rx_push(emac0, trans_desc);
            break;
            
        case EMAC_IRQ_EVENT_TX_ERR_FRAME:
            // Handle TX error
            handle_tx_error(trans_desc->err_status);
            return_tx_buffer(trans_desc);
            break;
            
        case EMAC_IRQ_EVENT_RX_BUSY:
            // No RX buffer available - critical
            break;
    }
}
```

## Transmit Operation

```c
// Get TX buffer from pool
struct bflb_emac_trans_desc_s tx_desc;
if (eth_emac_tx_buff_get(&tx_desc, portMAX_DELAY) != 0) {
    return -1;
}

// Fill buffer with data
memcpy(tx_desc.buff_addr, tx_data, tx_len);
tx_desc.data_len = tx_len;
tx_desc.attr_flag = 0;  // Use default flags (CRC, PAD, IRQ enabled)

// Push to TX queue
int ret = bflb_emac_queue_tx_push(emac0, &tx_desc);
if (ret < 0) {
    // Queue full - handle error
    return -1;
}
```

## Receive Operation

```c
// Get received data from queue (from IRQ callback or polling)
struct bflb_emac_trans_desc_s rx_desc;
if (eth_emac_rx_data_get(&rx_desc, timeout) == 0) {
    // Process received packet
    uint8_t *data = (uint8_t *)rx_desc.buff_addr;
    uint16_t len = rx_desc.data_len;
    
    // ... process data ...
    
    // Return buffer to RX queue
    eth_emac_rx_data_free(&rx_desc);
}
```

## MII/MDIO Operations

### MDIO Read

```c
uint16_t phy_data;
int ret = bflb_emac_md_read(emac0, phy_addr, reg_addr, &phy_data);
if (ret == 0) {
    // phy_data contains register value
}
```

### MDIO Write

```c
int ret = bflb_emac_md_write(emac0, phy_addr, reg_addr, value);
```

### MII Clock Divider Calculation

```c
// MDCLK = bus_clock / (2 * (md_clk_div + 1))
// For 2.5MHz MDCLK with 120MHz bus:
// md_clk_div = 120 / (2 * 2.5) - 1 = 23
config.md_clk_div = 23;
```

## Clock Configuration (BL616/BL618)

### Internal Reference Clock Mode (PHY provides clock)

```c
config.clk_internal_mode = false;

// GLB clock configuration
regval = getreg32(GLB_EMAC_CLK_OUT_ADDRESS);
regval &= ~(1 << 5);  // ref_clk in mode
regval &= ~(1 << 6);
regval &= ~(1 << 7);
regval &= ~(1 << 10);
putreg32(regval, GLB_EMAC_CLK_OUT_ADDRESS);
```

### External Reference Clock Mode (MAC provides clock)

```c
config.clk_internal_mode = true;

// GLB clock configuration
regval = getreg32(GLB_EMAC_CLK_OUT_ADDRESS);
regval |= (1 << 5);   // ref_clk out mode
regval |= (1 << 6);   // ref_clk out invert
regval &= ~(1 << 7);  // mac_tx_clk not invert
regval |= (1 << 10);  // mac_rx_clk invert
putreg32(regval, GLB_EMAC_CLK_OUT_ADDRESS);
```

## DMA Descriptor Location

DMA descriptors are located at `EMAC_BASE + 0x400`:
- TX BD: indices 0-63 (64 BDs max)
- RX BD: indices 64-127 (64 BDs max)

Each BD is 8 bytes (2 x 32-bit words):
- Word 0: attributes/control
- Word 1: buffer address

## PHY Example (LAN8720)

```c
#include "eth_phy.h"
#include "ephy_lan8720.h"

// PHY configuration
static eth_phy_init_cfg_t phy_cfg = {
    .speed_mode = EPHY_SPEED_MODE_AUTO_NEGOTIATION,
    .local_auto_negotiation_ability = EPHY_ABILITY_100M_TX | 
                                      EPHY_ABILITY_100M_FULL_DUPLEX,
};

// Initialize PHY
eth_phy_ctrl_t phy_ctrl;
int ret = eth_phy_scan(&phy_ctrl, EPHY_ADDR_MIN, EPHY_ADDR_MAX);
if (ret < 0) {
    return -1;
}

ret = eth_phy_init(&phy_ctrl, &phy_cfg);
if (ret < 0) {
    return -1;
}

// LAN8720 requires rx_clk inversion in ref_clk input mode
if (config.clk_internal_mode == false && 
    phy_ctrl.phy_drv->phy_id == EPHY_LAN8720_ID) {
    bflb_emac_feature_control(emac0, EMAC_CMD_SET_MAC_RX_CLK_INVERT, true);
}

// Check link status
int link_sta = eth_phy_ctrl(&phy_ctrl, EPHY_CMD_GET_LINK_STA, 0);
int speed = eth_phy_ctrl(&phy_ctrl, EPHY_CMD_GET_SPEED_MODE, 0);
```

## Memory Requirements

### Buffer Alignment
- TX/RX buffers must be 32-byte aligned
- Use `ATTR_NOCACHE_NOINIT_RAM_SECTION` for DMA buffers

### Example Buffer Definition

```c
#define EMAC_TX_BUFF_CNT  16
#define EMAC_RX_BUFF_CNT  16
#define ETH_TX_BUFF_SIZE  1524
#define ETH_RX_BUFF_SIZE  1524
#define EAMC_BUF_HEAD_SIZE 64

// TX buffers (32-byte aligned)
static uint8_t ATTR_NOCACHE_NOINIT_RAM_SECTION __ALIGNED(32) 
    emac_tx_buff[EMAC_TX_BUFF_CNT][ETH_TX_BUFF_SIZE + EAMC_BUF_HEAD_SIZE];

// RX buffers (32-byte aligned)
static uint8_t ATTR_NOCACHE_NOINIT_RAM_SECTION __ALIGNED(32) 
    emac_rx_buff[EMAC_RX_BUFF_CNT][ETH_RX_BUFF_SIZE + EAMC_BUF_HEAD_SIZE];
```

## Troubleshooting

### No TX/RX Interrupts
1. Check interrupt mask: `EMAC_INT_MASK_OFFSET` should have relevant bits cleared
2. Verify IRQ is enabled: `bflb_irq_enable(dev->irq_num)`
3. Check NVIC configuration

### TX Queue Full
- Return used buffers promptly in TX callback
- Increase `EMAC_TX_BD_NUM_MAX` if needed
- Check for TX errors causing buffer retention

### RX Busy Condition
- Occurs when hardware has data but no empty RX buffers
- Increase RX buffer count
- Process RX frames faster in callback

### PHY Not Detected
1. Verify MDIO communication
2. Check MDCLK divider setting
3. Verify RMII connections
4. Check PHY power supply

### CRC Errors
1. Check cable quality
2. Verify RMII timing
3. Check for electrical noise
4. May indicate hardware issue

## File References

- Header: `bouffalo_sdk/drivers/lhal/include/bflb_emac.h`
- Common: `bouffalo_sdk/drivers/lhal/include/bflb_emac_common.h`
- Register: `bouffalo_sdk/drivers/lhal/include/hardware/emac_reg.h`
- Implementation: `bouffalo_sdk/drivers/lhal/src/bflb_emac.c`
- Example: `bouffalo_sdk/examples/cherryusb/.../eth_emac.c`
