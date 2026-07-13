# GMAC Ethernet Driver Documentation

## Overview

The GMAC (Gigabit Media Access Controller) is a 10/100/1000 Mbps Ethernet controller available on BL616/BL618 chips. This document covers the low-level driver interface (`bflb_gmac`) and register-level programming.

**Base Address:** `GMAC_BASE` (defined in chip-specific header, e.g., `0x400A0000`)

---

## GMAC Register Map

| Offset | Register | Description |
|--------|----------|-------------|
| `0x0000` | GMAC_CONFIG | MAC configuration (duplex, speed, loopback) |
| `0x0004` | GMAC_FRAME_FILTER | Frame filtering options |
| `0x0008` | GMAC_HASH_HIGH | Hash table high 32 bits |
| `0x000C` | GMAC_HASH_LOW | Hash table low 32 bits |
| `0x0010` | GMAC_GMII_ADDR | MII/SMI (MDIO) address register |
| `0x0014` | GMAC_GMII_DATA | MII/SMI (MDIO) data register |
| `0x0018` | GMAC_FLOW_CONTROL | Flow control settings |
| `0x001C` | GMAC_VLAN | VLAN tag register |
| `0x0020` | GMAC_VERSION | GMAC version |
| `0x0028` | GMAC_WAKEUP_ADDR | Wakeup frame address |
| `0x002C` | GMAC_PMT_CTRL_STATUS | PMT control/status |
| `0x0030` | GMAC_LPI_CTRL_STS | LPI control/status |
| `0x0034` | GMAC_LPI_TIMER_CTRL | LPI timer control |
| `0x0038` | GMAC_INTERRUPT_STATUS | Interrupt status |
| `0x003C` | GMAC_INTERRUPT_MASK | Interrupt mask |
| `0x0040` | GMAC_MAC_ADDR0_HIGH | MAC address 0 high |
| `0x0044` | GMAC_MAC_ADDR0_LOW | MAC address 0 low |
| `0x0048` | `0x004C` | MAC address 1-15 (high/low pairs) |
| `0x00B8` | `0x00BC` | MAC address 15 high/low |
| **DMA Registers** |||
| `0x1000` | GMAC_DMA_BUS_MODE | DMA bus mode |
| `0x1004` | GMAC_DMA_TX_POLL_DEMAND | TX poll demand |
| `0x1008` | GMAC_DMA_RX_POLL_DEMAND | RX poll demand |
| `0x100C` | GMAC_DMA_RX_BASE_ADDR | RX descriptor base address |
| `0x1010` | GMAC_DMA_TX_BASE_ADDR | TX descriptor base address |
| `0x1014` | GMAC_DMA_STATUS | DMA status |
| `0x1018` | GMAC_DMA_CONTROL | DMA operation mode |
| `0x101C` | GMAC_DMA_INTERRUPT_ENABLE | DMA interrupt enable |
| `0x1048` | GMAC_DMA_TX_CURR_DESC | Current TX descriptor |
| `0x104C` | GMAC_DMA_RX_CURR_DESC | Current RX descriptor |
| **Timestamp Registers** |||
| `0x0700` | GMAC_TS_CTRL | Timestamp control |
| `0x0704` | GMAC_TS_SUB_SEC_INCR | Sub-second increment |
| `0x0708` | GMAC_TS_HIGH | Timestamp high |
| `0x070C` | GMAC_TS_LOW | Timestamp low |

---

## Key Configuration Structures

### `bflb_gmac_config_s`

```c
struct bflb_gmac_config_s {
    uint8_t mac_addr[6];        // MAC address
    bool clk_internal_mode;      // Internal clock mode
    uint8_t mii_clk_div;        // MII clock divider
    uint8_t duplex_mode;        // Full/half duplex
    uint16_t speed;              // Speed: 10, 100, 1000
    uint16_t min_frame_len;     // Min frame length
    uint16_t max_frame_len;     // Max frame length
};
```

### `bflb_gmac_dma_desc_s` (DMA Descriptor)

```c
struct bflb_gmac_dma_desc_s {
    uint32_t status;        // Status word (OWN bit at bit 31)
    uint32_t length;        // Buffer lengths
    uint32_t buffer1;       // Buffer 1 DMA address
    uint32_t buffer2;       // Buffer 2 DMA address / next descriptor
    // Driver-internal fields:
    uint32_t extstatus;     // Extended status
    uint32_t reserved1;
    uint32_t timestamplow;
    uint32_t timestamphigh;
    uint32_t data1;         // Virtual buffer 1 address
    uint32_t data2;         // Virtual buffer 2 address
};
```

---

## DMA Descriptor Format

### RX Descriptor (RDES)

```
RDES0: [31] OWN | [30] AFM | [29:16] FL | [15] ES | [14] DE | ... | [8] LS | [7] FS | ...
RDES1: [31] DIS | [28:16] TBS2 | [14] TCH | [15] TER | [12:0] TBS1
RDES2: Buffer 1 Address
RDES3: Buffer 2 Address / Next Descriptor
```

### TX Descriptor (TDES)

```
TDES0: [31] OWN | [30] IC | [29] LS | [28] FS | [27] DC | [26] DP | [25] TTSEN | [23:22] CIS | [21] TER | [20] TCH | ...
TDES1: [28:16] TBS2 | [12:0] TBS1
TDES2: Buffer 1 Address
TDES3: Buffer 2 Address / Next Descriptor
```

### Key Descriptor Flags

**Status Flags:**
- `GMAC_DESC_OWN_BY_DMA` (bit 31) - Descriptor owned by DMA
- `GMAC_DESC_RX_FIRST` (bit 9) - First descriptor of frame
- `GMAC_DESC_RX_LAST` (bit 8) - Last descriptor of frame
- `GMAC_DESC_ERROR` (bit 15) - Error summary

**TX Control Flags:**
- `GMAC_DESC_TX_INT_ENABLE` - Interrupt on completion
- `GMAC_DESC_TX_LAST` - Last segment
- `GMAC_DESC_TX_FIRST` - First segment
- `GMAC_DESC_TX_END_OF_RING` - End of descriptor ring
- `GMAC_DESC_TX_DESC_CHAIN` - Chained descriptors

**RX Control Flags:**
- `GMAC_DESC_RX_DIS_INT_COMPL` - Disable RX interrupt
- `GMAC_DESC_RX_END_OF_RING` - End of ring
- `GMAC_DESC_RX_DESC_CHAIN` - Chained mode

---

## Initialization Sequence

```c
#include "bflb_gmac.h"

void gmac_init_example(struct bflb_device_s *dev)
{
    struct bflb_gmac_config_s config = {0};
    
    // Configure MAC address
    config.mac_addr[0] = 0xAA;
    config.mac_addr[1] = 0xBB;
    config.mac_addr[2] = 0xCC;
    config.mac_addr[3] = 0xDD;
    config.mac_addr[4] = 0xEE;
    config.mac_addr[5] = 0xFF;
    
    config.duplex_mode = GAMC_FULLDUPLEX;
    config.speed = GMAC_SPEED_1000;
    config.mii_clk_div = 4;
    config.min_frame_len = 64;
    config.max_frame_len = 1524;
    
    // Initialize GMAC
    bflb_gmac_init(dev, &config);
}
```

### Full Initialization with DMA

```c
void gmac_full_init(struct bflb_device_s *dev,
                    struct bflb_gmac_dma_desc_s *tx_desc, uint8_t *tx_buf, uint32_t tx_cnt,
                    struct bflb_gmac_dma_desc_s *rx_desc, uint8_t *rx_buf, uint32_t rx_cnt)
{
    struct bflb_gmac_config_s config = {
        .mac_addr = {0xAA, 0xBB, 0xCC, 0xDD, 0xEE, 0xFF},
        .duplex_mode = GAMC_FULLDUPLEX,
        .speed = GMAC_SPEED_1000,
        .mii_clk_div = 4,
        .min_frame_len = 64,
        .max_frame_len = 1524,
    };
    
    // Initialize GMAC peripheral
    bflb_gmac_init(dev, &config);
    
    // Initialize DMA descriptors
    bflb_gmac_dma_desc_init(dev, tx_desc, tx_buf, tx_cnt, rx_desc, rx_buf, rx_cnt);
    
    // Configure DMA bus mode
    bflb_gmac_dma_bus_init(dev);
    
    // Configure DMA control
    bflb_gmac_dma_ctrl_init(dev);
    
    // Enable TX/RX
    bflb_gmac_tx_enable(dev);
    bflb_gmac_rx_enable(dev);
    
    // Enable DMA TX/RX
    bflb_gmac_enable_dma_tx(dev);
    bflb_gmac_enable_dma_rx(dev);
    
    // Start GMAC
    bflb_gmac_start(dev);
}
```

---

## TX/RX Descriptor Operations

### Transmit a Packet

```c
int gmac_send_packet(struct bflb_device_s *dev, const uint8_t *data, uint32_t len)
{
    // Set TX descriptor with data buffer
    return bflb_gmac_set_tx_qptr(dev,
                                  (uint32_t)data,      // buffer1 (DMA address)
                                  len,                  // length1
                                  (uint32_t)data,      // data1 (virtual address)
                                  0, 0, 0,             // buffer2 not used
                                  0);                   // no checksum offload
}

int gmac_send_with_checksum(struct bflb_device_s *dev, const uint8_t *data, uint32_t len)
{
    // Use TCP checksum offload
    return bflb_gmac_set_tx_qptr(dev,
                                  (uint32_t)data, len, (uint32_t)data,
                                  0, 0, 0,
                                  1);  // checksum offload enabled
}
```

### Receive a Packet

```c
int gmac_receive_packet(struct bflb_device_s *dev, uint8_t *data, uint32_t *len)
{
    uint32_t status, buffer1, length1, data1;
    uint32_t buffer2, length2, data2;
    uint32_t ext_status, ts_high, ts_low;
    
    int idx = bflb_gmac_get_rx_qptr(dev, &status, &buffer1, &length1, &data1,
                                     &buffer2, &length2, &data2,
                                     &ext_status, &ts_high, &ts_low);
    
    if (idx >= 0) {
        // Check if frame is valid
        if (bflb_gmac_is_rx_desc_valid(status)) {
            *len = bflb_gmac_get_rx_desc_frame_length(status);
            // Copy data from buffer
            // data1 contains virtual address of buffer
            *len = (length1 < *len) ? length1 : *len;
        }
    }
    return idx;
}
```

### Polling TX Completion

```c
void gmac_handle_tx_done(struct bflb_device_s *dev)
{
    bflb_gmac_handle_transmit_over(dev);
    
    uint32_t status, buffer1, length1, data1;
    uint32_t buffer2, length2, data2;
    uint32_t ext_status, ts_high, ts_low;
    
    while (bflb_gmac_get_tx_qptr(dev, &status, &buffer1, &length1, &data1,
                                  &buffer2, &length2, &data2,
                                  &ext_status, &ts_high, &ts_low) >= 0) {
        // Process completed TX descriptor
        // Reuse or recycle buffer if needed
    }
}
```

---

## MDIO (MII Management Interface)

MDIO is used to communicate with external PHYs (e.g., PHY address 0-31).

### MDIO Register Access

```c
int gmac_phy_read(struct bflb_device_s *dev, uint16_t phy_addr, uint16_t reg, uint16_t *value)
{
    // Set MDIO clock divider (CSR clock)
    bflb_gmac_mdc_clk_div_set(dev, 0x0F);  // Adjust divider as needed
    
    return bflb_gmac_phy_reg_read(dev, phy_addr, value);
}

int gmac_phy_write(struct bflb_device_s *dev, uint16_t phy_addr, uint16_t reg, uint16_t value)
{
    bflb_gmac_mdc_clk_div_set(dev, 0x0F);
    return bflb_gmac_phy_reg_write(dev, reg, value);
}
```

### MDIO Register Bit Definitions

```
GMAC_GMII_ADDR:
  [0]     - GMII_BUSY (read-only, set when operation in progress)
  [1]     - GMII_WRITE (1=write, 0=read)
  [5:2]   - CSR Clock divider
  [10:6]  - REG (PHY register address)
  [15:11] - ADDR (PHY address)

GMAC_GMII_DATA:
  [15:0]  - DATA (register value)
```

---

## Interrupts

### Interrupt Types

| Flag | Description |
|------|-------------|
| `GMAC_DMA_INT_API_RX_NORMAL` | Normal RX interrupt |
| `GMAC_DMA_INT_API_RX_ABNORMAL` | Abnormal RX interrupt |
| `GMAC_DMA_INT_API_RX_STOPPED` | RX process stopped |
| `GMAC_DMA_INT_API_TX_NORMAL` | Normal TX interrupt |
| `GMAC_DMA_INT_API_TX_ABNORMAL` | Abnormal TX interrupt |
| `GMAC_DMA_INT_API_TX_STOPPED` | TX process stopped |
| `GMAC_DMA_INT_API_ERROR` | DMA engine error |

### Interrupt Configuration

```c
void gmac_enable_interrupts(struct bflb_device_s *dev)
{
    // Enable standard interrupts
    uint32_t interrupts = GMAC_DMA_INT_API_RX_NORMAL |
                          GMAC_DMA_INT_API_TX_NORMAL |
                          GMAC_DMA_INT_API_RX_ABNORMAL |
                          GMAC_DMA_INT_API_TX_ABNORMAL |
                          GMAC_DMA_INT_API_ERROR;
    
    bflb_gmac_enable_interrupt(dev, interrupts);
}

void gmac_interrupt_handler(struct bflb_device_s *dev)
{
    // Get interrupt status
    uint32_t status = bflb_gmac_get_interrupt_status(dev);
    uint32_t type = bflb_gmac_get_interrupt_type(dev);
    
    // Check for normal RX interrupt
    if (type & GMAC_DMA_INT_API_RX_NORMAL) {
        // Process received packets
    }
    
    // Check for normal TX interrupt
    if (type & GMAC_DMA_INT_API_TX_NORMAL) {
        // Handle TX completion
    }
    
    // Clear interrupts
    bflb_gmac_clear_interrupt(dev, status);
}

void gmac_disable_all_interrupts(struct bflb_device_s *dev)
{
    bflb_gmac_disable_interrupt_all(dev);
}
```

### DMA Status Register Bits

```
[28]  - PMT interrupt
[25]  - DMA error bit 2
[24]  - DMA error bit 1
[23]  - DMA error bit 0
[22:20] - TX state
[19:17] - RX state
[16]  - Normal interrupt summary
[15]  - Abnormal interrupt summary
[8]   - RX stopped
[5]   - RX buffer unavailable
[4]   - RX completed
[1]   - TX stopped
[0]   - TX completed
```

---

## Register-Level Programming

### Direct Register Access Pattern

```c
// Assuming base address and register definitions
#define GMAC_BASE_ADDR  0x400A0000

static inline uint32_t gmac_read32(uint32_t offset)
{
    return *(volatile uint32_t *)(GMAC_BASE + offset);
}

static inline void gmac_write32(uint32_t offset, uint32_t value)
{
    *(volatile uint32_t *)(GMAC_BASE + offset) = value;
}

// Example: Configure full duplex, 1000Mbps
void gmac_config_mac(void)
{
    uint32_t reg;
    
    // Read current config
    reg = gmac_read32(GMAC_CONFIG_OFFSET);
    
    // Modify: Enable full duplex, 1000Mbps, TX/RX enable
    reg |= (1 << GMAC_DUPLEX_SHIFT) |     // Full duplex
           (0 << GMAC_FE_100M_SHIFT) |   // 1000Mbps
           (1 << GMAC_TX_ENABLE_SHIFT) | // TX enable
           (1 << GMAC_RX_ENABLE_SHIFT);  // RX enable
    
    gmac_write32(GMAC_CONFIG_OFFSET, reg);
}

// Example: Set MAC address
void gmac_set_mac_addr(const uint8_t mac[6])
{
    // MAC_ADDR0_HIGH: [15:0] = MAC[47:32]
    uint32_t high = (mac[5] << 8) | mac[4];
    gmac_write32(GMAC_MAC_ADDR0_HIGH_OFFSET, high);
    
    // MAC_ADDR0_LOW: [31:0] = MAC[31:0]
    uint32_t low = (mac[3] << 24) | (mac[2] << 16) | (mac[1] << 8) | mac[0];
    gmac_write32(GMAC_MAC_ADDR0_LOW_OFFSET, low);
}

// Example: Configure DMA descriptor base
void gmac_config_dma_descriptors(uint32_t rx_desc_addr, uint32_t tx_desc_addr)
{
    gmac_write32(GMAC_DMA_RX_BASE_ADDR_OFFSET, rx_desc_addr);
    gmac_write32(GMAC_DMA_TX_BASE_ADDR_OFFSET, tx_desc_addr);
}

// Example: Start DMA
void gmac_dma_start(void)
{
    uint32_t reg;
    
    // Set bus mode: fixed burst, burst length 32
    gmac_write32(GMAC_DMA_BUS_MODE_OFFSET, 
                 GMAC_DMA_FIXED_BURST_ENABLE | GMAC_DMA_BURST_LEN_32);
    
    // Start TX/RX in control register
    reg = gmac_read32(GMAC_DMA_CONTROL_OFFSET);
    reg |= GMAC_DMA_TX_START | GMAC_DMA_RX_START;
    gmac_write32(GMAC_DMA_CONTROL_OFFSET, reg);
}
```

### DMA Bus Mode Register (Offset 0x1000)

```
[24]   - BURST_LEN_X8 (multiply PBL by 8)
[16]   - FIXED_BURST_ENABLE
[15:14] - PR (priority ratio TX:RX)
[13:8]  - PBL (programmable burst length)
[7]    - DESCRIPTOR_8_WORDS (1=8-word, 0=4-word)
[6:2]  - DSL (descriptor skip length)
[1]    - DA (0=RR, 1=strict priority)
[0]    - SWR (software reset)
```

### DMA Control Register (Offset 0x1018)

```
[26]   - DT (drop TCP checksum error frames)
[21]   - SF (store and forward)
[20]   - FTF (flush TX FIFO)
[16:14] - TTC (TX threshold)
[13]   - ST (start TX)
[8]    - EFC (enable HW flow control)
[4]    - OSF (operate on second frame)
[1]    - SR (start RX)
```

---

## Feature Control Commands

```c
// Promiscuous mode
bflb_gmac_feature_control(dev, GMAC_CMD_EN_PROMISCUOUS, 1);

// Set MAC address
bflb_gmac_feature_control(dev, GMAC_CMD_SET_MAC_ADDRESS, (size_t)mac_addr);

// Set PHY address
bflb_gmac_feature_control(dev, GMAC_CMD_SET_PHY_ADDRESS, phy_addr);

// Set speed mode
bflb_gmac_feature_control(dev, GMAC_CMD_SET_SPEED_MODE, GMAC_SPEED_1000);

// Full duplex
bflb_gmac_feature_control(dev, GMAC_CMD_FULL_DUPLEX, 1);
```

---

## Flow Control

```c
// Enable RX flow control (decode pause frames)
bflb_gmac_rx_flow_control_enable(dev);

// Enable TX flow control (send pause frames in full duplex)
bflb_gmac_tx_flow_control_enable(dev);

// Send pause frame immediately
bflb_gmac_tx_flow_control_activate(dev);

// Back pressure (half duplex)
bflb_gmac_tx_flow_control_deactivate(dev);
```

---

## Frame Filtering

```c
// Enable broadcast frames
bflb_gmac_broadcast_enable(dev);

// Enable multicast frames
bflb_gmac_multicast_enable(dev);

// Set hash table
bflb_gmac_hash_table_high_set(dev, 0x0000FFFF);
bflb_gmac_hash_table_low_set(dev, 0xFFFFFFFF);

// Hash filtering
bflb_gmac_multicast_hash_filter_enable(dev);

// Promiscuous mode
bflb_gmac_promisc_enable(dev);
```

---

## Checksum Offload

```c
// Enable RX checksum offload
bflb_gmac_rx_chksum_offload_enable(dev);

// Enable TCP/IP checksum drop on error
bflb_gmac_rx_tcpip_chksum_drop_enable(dev);

// TX checksum modes
// - GMAC_DESC_TX_CIS_BYPASS (no checksum)
// - GMAC_DESC_TX_CIS_IPV4_HDR_CS (IPv4 header only)
// - GMAC_DESC_TX_CIS_TCP_ONLY_CS (TCP/UDP with pseudo header)
// - GMAC_DESC_TX_CIS_TCP_PSEUDO_CS (full TCP/UDP checksum)
```

---

## Timestamp (PTP) Support

```c
// Enable timestamping
bflb_gmac_ts_enable(dev);

// Configure timestamp
bflb_gmac_ts_ipv4_enable(dev);
bflb_gmac_ts_ipv6_enable(dev);
bflb_gmac_ts_ptp_over_ethernet_enable(dev);
bflb_gmac_ts_master_enable(dev);
bflb_gmac_ts_event_enable(dev);

// Set clock type (0=ordinary, 1=boundary, 2=E2E transparent, 3=P2P transparent)
bflb_gmac_ts_set_clk_type(dev, 0);

// Initialize timestamp
bflb_gmac_ts_timestamp_init(dev, high_sec, low_sec);
bflb_gmac_ts_subsecond_init(dev, subsec_inc);
```

---

## Common Issues and Debug

### PHY Not Responding
1. Check MDIO clock divider (try lower values)
2. Verify PHY address matches hardware strapping
3. Ensure clocks are enabled

### TX Hang
1. Check DMA is running (poll status register)
2. Verify descriptors have OWN bit set correctly
3. Check for TX underflow (buffer not ready)

### RX No Packets
1. Verify RX descriptors are initialized with OWN bit set
2. Check frame filter is not blocking
3. Ensure DMA RX is started

### DMA Bus Errors
1. Verify descriptor addresses are DMA-able
2. Check memory attributes (non-cacheable for DMA)
3. Ensure buffer sizes match descriptor lengths

---

## Constants Reference

### Speed/Duplex
```c
#define GAMC_HALFDUPLEX    0
#define GAMC_FULLDUPLEX    1
#define GMAC_SPEED_10       10
#define GMAC_SPEED_100      100
#define GMAC_SPEED_1000     1000
```

### Ethernet Frame Sizes
```c
#define ETH_MAX_PACKET_SIZE       1524
#define ETH_HEADER_SIZE           14
#define ETH_CRC_SIZE              4
#define ETH_EXTRA_SIZE            2
#define ETH_VLAN_TAG_SIZE         4
#define ETH_MIN_PAYLOAD_SIZE      46
#define ETH_MAX_PAYLOAD_SIZE      1500
#define ETH_JUMBO_FRAME_PAYLOAD  9000
```

### Default Buffer Sizes
```c
#define ETH_TX_BUFFER_SIZE  ETH_MAX_PACKET_SIZE
#define ETH_RX_BUFFER_SIZE  ETH_MAX_PACKET_SIZE
```
