# lmac154 Technical Documentation

## Overview

lmac154 is the IEEE 802.15.4 MAC layer protocol stack implemented in the Bouffalo chip series, providing physical layer and media access control layer abstraction for low-rate wireless personal area network (LR-WPAN) protocols such as Thread and Zigbee. This module operates in the 2.4GHz ISM band, supporting channels 11 through 26 (16 channels total), compliant with the 802.15.4-2015 standard.

lmac154 driver version is 1.7.4, providing complete core functionality including frame transmission and reception, RF state management, address configuration, CCA (Clear Channel Assessment), and AES-CCM encryption. This module is the physical layer and MAC layer abstraction foundation for the Thread protocol; upper-layer protocol stacks (such as OpenThread) perform wireless communication through the interfaces provided by lmac154.

---

## Core Data Types

### Channel Type `lmac154_channel_t`

Defines the 802.15.4 operating channel, ranging from channel 11 to channel 26:

```c
typedef enum {
    LMAC154_CHANNEL_NONE = -1,
    LMAC154_CHANNEL_11 = 0,
    LMAC154_CHANNEL_12,
    LMAC154_CHANNEL_13,
    LMAC154_CHANNEL_14,
    LMAC154_CHANNEL_15,
    LMAC154_CHANNEL_16,
    LMAC154_CHANNEL_17,
    LMAC154_CHANNEL_18,
    LMAC154_CHANNEL_19,
    LMAC154_CHANNEL_20,
    LMAC154_CHANNEL_21,
    LMAC154_CHANNEL_22,
    LMAC154_CHANNEL_23,
    LMAC154_CHANNEL_24,
    LMAC154_CHANNEL_25,
    LMAC154_CHANNEL_26,
} lmac154_channel_t;
```

### Transmit Power Type `lmac154_tx_power_t`

Defines 8 levels of transmit power, from 0 dBm to 7 dBm:

```c
typedef enum {
    LMAC154_TX_POWER_0dBm = 0,
    LMAC154_TX_POWER_1dBm = 1,
    LMAC154_TX_POWER_2dBm = 2,
    LMAC154_TX_POWER_3dBm = 3,
    LMAC154_TX_POWER_4dBm = 4,
    LMAC154_TX_POWER_5dBm = 5,
    LMAC154_TX_POWER_6dBm = 6,
    LMAC154_TX_POWER_7dBm = 7,
} lmac154_tx_power_t;
```

### Interrupt Callback Type `lmac154_isr_t`

Used to register hardware interrupt handler callback functions:

```c
typedef void (*lmac154_isr_t)(void);
```

### Data Rate Type `lmac154_data_rate_t`

Supports four data rate modes:

```c
typedef enum {
    LMAC154_DATA_RATE_250K = 0,  // 250 kbps (default)
    LMAC154_DATA_RATE_500K = 1,  // 500 kbps
    LMAC154_DATA_RATE_1M   = 2,  // 1 Mbps
    LMAC154_DATA_RATE_2M   = 3,  // 2 Mbps
} lmac154_data_rate_t;
```

### CCA Mode Type `lmac154_cca_mode_t`

Defines Clear Channel Assessment modes:

```c
typedef enum {
    LMAC154_CCA_MODE_ED        = 0,  // Energy Detection
    LMAC154_CCA_MODE_CS        = 1,  // Carrier Sense
    LMAC154_CCA_MODE_ED_AND_CS = 2,  // Energy Detection AND Carrier Sense (default)
    LMAC154_CCA_MODE_ED_OR_CS  = 3,  // Energy Detection OR Carrier Sense
} lmac154_cca_mode_t;
```

### Frame Type `lmac154_frame_type_t`

```c
typedef enum {
    LMAC154_FRAME_TYPE_BEACON = 0x01,  // Beacon frame
    LMAC154_FRAME_TYPE_DATA   = 0x02,  // Data frame
    LMAC154_FRAME_TYPE_ACK    = 0x04,  // Acknowledgment frame
    LMAC154_FRAME_TYPE_CMD    = 0x08,  // Command frame
    LMAC154_FRAME_TYPE_MPP    = 0x10,  // Multipurpose frame
} lmac154_frame_type_t;
```

### RF State Type `lmac154_rf_state_t`

```c
typedef enum {
    LMAC154_RF_STATE_RX_TRIG   = 1,  // RX trigger state
    LMAC154_RF_STATE_RX        = 2,  // RX running state
    LMAC154_RF_STATE_RX_DOING  = 3,  // RX in progress
    LMAC154_RF_STATE_ACK_DOING = 4,  // ACK sending
    LMAC154_RF_STATE_TX        = 5,  // TX running state
    LMAC154_RF_STATE_CSMA      = 6,  // CSMA/CA in progress
    LMAC154_RF_STATE_IDLE      = 7,  // Idle state
} lmac154_rf_state_t;
```

### Transmit Status Type `lmac154_tx_status_t`

```c
typedef enum {
    LMAC154_TX_STATUS_TX_FINISHED = 0,  // Transmission finished
    LMAC154_TX_STATUS_CSMA_FAILED = 1,  // CSMA failed
    LMAC154_TX_STATUS_TX_ABORTED  = 2,  // Transmission aborted
    LMAC154_TX_STATUS_HW_ERROR    = 3,  // Hardware error
    LMAC154_TX_STATUS_DELAY_ERROR = 4,  // Delay error
    LMAC154_TX_STATUS_NO_ACK      = 5,  // No ACK received
    LMAC154_TX_STATUS_ACKED       = 6,  // Acknowledged
    LMAC154_TX_STATUS_CCA_FAILED  = 7,  // CCA failed
    LMAC154_TX_STATUS_MAX         = 8,
} lmac154_tx_status_t;
```

### Receive Status Type `lmac154_rx_status_t`

```c
typedef enum {
    LMAC154_RX_STATUS_NONE     = 0,  // No event
    LMAC154_RX_STATUS_RX_DONE  = 1,  // Reception complete
    LMAC154_RX_STATUS_ACK_SENT = 2,  // ACK sent
    LMAC154_RX_STATUS_ACK_ERR  = 3,  // ACK error
} lmac154_rx_status_t;
```

### Callback Function Types

Transmit done callback:

```c
typedef void (*lmac154_txDoneCallback_t)(lmac154_tx_status_t status, 
                                          uint32_t *extra, uint32_t extra_len);
```

Receive done callback:

```c
typedef void (*lmac154_rxDoneCallback_t)(lmac154_rx_status_t status, 
                                         lmac154_receiveInfo_t *info, uint32_t *);
```

---

## Register Operation Macros

lmac154 provides a set of register access macros for direct hardware register read/write:

### Basic Read/Write Macros

```c
#define M154_RD_WORD(addr)      (*((volatile uint32_t *)(uintptr_t)(addr)))
#define M154_WR_WORD(addr, val) ((*(volatile uint32_t *)(uintptr_t)(addr)) = (val))
```

- `M154_RD_WORD(addr)`: Read 32-bit data from the specified address
- `M154_WR_WORD(addr, val)`: Write 32-bit data to the specified address

### Register Field Operation Macros

```c
#define M154_SET_REG_BIT(val, bitname)    ((val) | (1U << bitname##_POS))
#define M154_CLR_REG_BIT(val, bitname)    ((val) & bitname##_UMSK)
#define M154_GET_REG_BITS_VAL(val, bitname) (((val) & bitname##_MSK) >> bitname##_POS)
#define M154_SET_REG_BITS_VAL(val, bitname, bitval) (((val) & bitname##_UMSK) | \
                                    ((uint32_t)(bitval) << bitname##_POS))
#define M154_IS_REG_BIT_SET(val, bitname) (((val) & (1U << (bitname##_POS))) != 0)
```

- `M154_SET_REG_BIT`: Set a specific bit
- `M154_CLR_REG_BIT`: Clear a specific bit
- `M154_GET_REG_BITS_VAL`: Get register field value
- `M154_SET_REG_BITS_VAL`: Set register field value
- `M154_IS_REG_BIT_SET`: Check if a specific bit is set

---

## 802.15.4 Frame Structure

### Frame Control Field

The Frame Control Field occupies 2 bytes and contains key information such as frame type, security enable, and address mode. Rich frame parsing macros are defined in lmac154_frame.h:

```c
// Frame type
#define LMAC154_FRAME_CONTROL_FRAME_TYPE_MASK    (7)
#define LMAC154_FRAME_CONTROL_FRAME_TYPE_BEACON (0)
#define LMAC154_FRAME_CONTROL_FRAME_TYPE_DATA   (1)
#define LMAC154_FRAME_CONTROL_FRAME_TYPE_ACK    (2)
#define LMAC154_FRAME_CONTROL_FRAME_TYPE_CMD   (3)
#define LMAC154_FRAME_CONTROL_FRAME_TYPE_MPP    (5)

// Security and pending bits
#define LMAC154_FRAME_SECURITY_MASK            (1 << 3)
#define LMAC154_FRAME_FRAME_PENDING_MASK       (1 << 4)
#define LMAC154_FRAME_ACK_REQUEST_MASK         (1 << 5)
#define LMAC154_FRAME_PANID_COMPRESSION       (1 << 6)

// Address mode
#define LMAC154_FRAME_ADDR_DEST_NONE   (0 << 10)   // No destination address
#define LMAC154_FRAME_ADDR_DEST_SHORT  (2 << 10)   // Short address
#define LMAC154_FRAME_ADDR_DEST_EXT    (3 << 10)    // Extended address

#define LMAC154_FRAME_ADDR_SRC_NONE    (0 << 14)
#define LMAC154_FRAME_ADDR_SRC_SHORT   (2 << 14)
#define LMAC154_FRAME_ADDR_SRC_EXT     (3 << 14)

// Frame version
#define LMAC154_FRAME_VERSION_MASK     (3 << 12)
#define LMAC154_FRAME_VERSION_2006     (0 << 12)
#define LMAC154_FRAME_VERSION_2011     (1 << 12)
#define LMAC154_FRAME_VERSION_2015     (2 << 12)
```

### Frame Structure Constants

```c
#define LMAC154_LIFS                    40   // Long inter-frame spacing (in symbols)
#define LMAC154_SIFS                    12   // Short inter-frame spacing (in symbols)
#define LMAC154_PKT_MAX_LEN             127  // Maximum MPDU length
#define LMAC154_PREAMBLE_LEN             8    // Preamble length
#define LMAC154_US_PER_SYMBOL            16   // Microseconds per symbol
```

### MHR Parsing Function

`lmac154_parse_mhr()` is an optimized 32-bit MAC header parsing function for quickly extracting address information from frames:

```c
static inline uint32_t lmac154_parse_mhr(uint8_t *pr, uint8_t **a_dest_panid,
                                 uint8_t **a_dest_sa, uint8_t **a_dest_xa,
                                 uint8_t **a_src_sa, uint8_t **a_src_xa);
```

This function reads 32-bit data at once, parsing the frame control field, sequence number, destination PAN ID, destination address, source PAN ID, and source address, and returns the MAC header length.

---

## Core API Functions

### Initialization and Reset

#### `lmac154_init()`

Initializes the lmac154 hardware module. This function must be called before using any other APIs.

```c
void lmac154_init(void);
```

#### `lmac154_reset()`

Resets the lmac154 module, restoring all registers to their default state.

```c
void lmac154_reset(void);
```

#### `lmac154_resetTx()`

Resets the transmit state machine, used to abort an ongoing transmission.

```c
void lmac154_resetTx(void);
```

#### `lmac154_resetRx()`

Resets the receive state machine.

```c
void lmac154_resetRx(void);
```

---

### Channel and Power Configuration

#### `lmac154_set_channel()`

Sets the operating channel. Default value is `LMAC154_CHANNEL_11`.

```c
void lmac154_setChannel(lmac154_channel_t ch_ind);
```

**Parameters:**
- `ch_ind`: Channel index, values from `LMAC154_CHANNEL_11` to `LMAC154_CHANNEL_26`

**Example:**

```c
lmac154_setChannel(LMAC154_CHANNEL_15);
```

#### `lmac154_get_channel()`

Gets the current operating channel.

```c
lmac154_channel_t lmac154_getChannel(void);
```

**Return Value:**
- Current channel index

#### `lmac154_set_tx_power()`

Sets the transmit power. Has no default; must be set before use.

```c
void lmac154_setTxPower(lmac154_tx_power_t power_dbm);
```

**Parameters:**
- `power_dbm`: Transmit power level, values from `LMAC154_TX_POWER_0dBm` to `LMAC154_TX_POWER_7dBm`

**Example:**

```c
lmac154_setTxPower(LMAC154_TX_POWER_5dBm);
```

#### `lmac154_get_tx_power()`

Gets the current transmit power setting.

```c
lmac154_tx_power_t lmac154_getTxPower(void);
```

---

### Frame Transmission and Reception

#### `lmac154_send()`

Sends an 802.15.4 data frame. This is the most basic transmit interface.

```c
void lmac154_send(uint8_t *data, uint16_t length);
```

**Parameters:**
- `data`: Pointer to data buffer
- `length`: Data length (in bytes)

**Note:**
This function internally adds the MHR (MAC Header). The actual transmitted MPDU length must not exceed 127 bytes.

#### `lmac154_trigger_tx()`

Triggers transmission, optionally using CSMA/CA.

```c
void lmac154_triggerTx(uint8_t *DataPtr, uint8_t length, uint8_t csma);
```

**Parameters:**
- `DataPtr`: Data buffer pointer
- `length`: Data length
- `csma`: 0 to not use CSMA/CA, 1 to use CSMA/CA

#### `lmac154_register_cb()`

Registers a receive interrupt callback function. This callback is invoked whenever a complete frame is received.

```c
void lmac154_register_cb(lmac154_rxDoneCallback_t callback);
```

**Parameters:**
- `callback`: Receive done callback function pointer

#### `lmac154_register_event_callback()`

Registers a receive event callback for a specified protocol stack, supporting dual stack mode.

```c
bool lmac154_registerEventCallback(lmac154_stack_idx_t stack_idx,
                                    lmac154_rxDoneCallback_t stack_rxDoneCallback);
```

**Parameters:**
- `stack_idx`: Protocol stack index (`LMAC154_STACK_1` or `LMAC154_STACK_2`)
- `stack_rxDoneCallback`: Receive done callback

---

### Address Configuration

#### PAN ID Configuration

```c
void lmac154_setPanId(uint16_t pid);   // Set PAN ID
uint16_t lmac154_getPanId(void);       // Get PAN ID
```

#### Short Address Configuration

```c
void lmac154_setShortAddr(uint16_t sadr);  // Set 16-bit short address
uint16_t lmac154_getShortAddr(void);       // Get short address
```

#### Extended Address Configuration

```c
void lmac154_setLongAddr(uint8_t *ladr);   // Set 64-bit extended address
void lmac154_getLongAddr(uint8_t *ladr);   // Get extended address
```

---

### Receive Control

#### Enable/Disable Receive

```c
void lmac154_enableRx(void);    // Enable receive (disabled by default)
void lmac154_disableRx(void);   // Disable receive
bool lmac154_isRxStateWhenIdle(void);
void lmac154_setRxStateWhenIdle(bool isRxOnWhenIdle);
```

#### Promiscuous Mode

```c
void lmac154_enableRxPromiscuousMode(uint8_t enhanced_mode, uint8_t ignore_mpdu);
void lmac154_disableRxPromiscuousMode(void);
```

**Parameter Description:**
- `enhanced_mode`: 0 standard mode, 1 enhanced mode
- `ignore_mpdu`: 0 read MPDU from register, 1 do not read

#### Frame Type Filtering

```c
void lmac154_enableFrameTypeFiltering(uint8_t frame_types);
void lmac154_disableFrameTypeFiltering(void);
```

---

### CCA and RF State

#### Set CCA Mode

```c
void lmac154_setCCAMode(lmac154_cca_mode_t mode);
lmac154_cca_mode_t mode = LMAC154_CCA_MODE_ED_AND_CS;  // Default
lmac154_setCCAMode(mode);
```

#### Set ED Threshold

```c
void lmac154_setEDThreshold(int threshold);  // Default -71 dBm
int threshold = -70;
lmac154_setEDThreshold(threshold);
```

#### Run CCA Detection

```c
uint8_t lmac154_runCCA(int *rssi);
```

**Return Value:**
- 0: Channel idle
- 1: Channel busy

#### Get RF State

```c
lmac154_rf_state_t lmac154_getRFState(void);
```

#### Get RSSI and LQI

```c
int lmac154_getRSSI(void);  // Get RSSI (dBm)
int lmac154_getLQI(void);   // Get LQI
```

---

### Other Configuration APIs

#### Data Rate

```c
void lmac154_setTxDataRate(lmac154_data_rate_t rate);  // Default 250K
void lmac154_enableAutoRxDataRate(void);
void lmac154_disableAutoRxDataRate(void);
```

#### Retry Count

```c
void lmac154_setTxRetry(uint32_t num);  // Default 0 retries
```

#### Interrupt Handling

```c
lmac154_isr_t lmac154_getInterruptHandler(void);
lmac154_isr_t lmac154_getInterruptCallback(void);
```

#### Version Information

```c
uint32_t lmac154_getVersionNumber(void);
char *lmac154_getVersionString(void);
```

#### Country Code and Power Limits

```c
bool lmac154_setCountryCode(const char *country_code);
void lmac154_setTxPowerWithPowerLimit(lmac154_tx_power_t power_dbm, 
                                       lmac154_channel_t ch_ind, 
                                       const char *country_code);
```

---

## Relationship with Thread Protocol

lmac154 is the physical layer and MAC layer abstraction for the Thread protocol. In the Thread protocol stack, lmac154 is responsible for:

- **Physical Layer Operations**: RF channel switching, transmit power control, TX/RX switching
- **MAC Layer Functions**: Frame transmission/reception, CSMA/CA, ACK handling, address matching
- **Security Support**: AES-CCM encryption/decryption support, providing the foundation for Thread's MAC layer security

The Thread protocol runs on top of lmac154, performing MAC frame interactions by calling the transmit and receive interfaces provided by lmac154. lmac154 supports 802.15.4-2015 standard features, including Enhanced ACK and Information Elements (IE), both of which are required by the Thread protocol.

---

## Code Examples

### Basic Initialization and Send Flow

```c
#include "lmac154.h"
#include "lmac154_frame.h"

// Receive callback function
void my_rx_callback(lmac154_rx_status_t status, 
                    lmac154_receiveInfo_t *info, 
                    uint32_t *mpdu)
{
    if (status == LMAC154_RX_STATUS_RX_DONE) {
        uint8_t *data = (uint8_t *)mpdu;
        uint16_t len = info->rx_length;
        
        // Process received data
        // ...
    }
}

void app_main(void)
{
    // 1. Initialize lmac154
    lmac154_init();
    
    // 2. Set PAN ID and short address
    lmac154_setPanId(0x1234);
    lmac154_setShortAddr(0x0001);
    
    // 3. Set operating channel
    lmac154_setChannel(LMAC154_CHANNEL_15);
    
    // 4. Set transmit power
    lmac154_setTxPower(LMAC154_TX_POWER_5dBm);
    
    // 5. Register receive callback
    lmac154_registerEventCallback(LMAC154_STACK_1, my_rx_callback);
    
    // 6. Enable receive
    lmac154_enableRx();
    
    // 7. Send data frame
    uint8_t tx_data[] = {
        0x12, 0x34,  // Destination PAN ID
        0x00, 0x00,  // Destination address (broadcast)
        0xFE, 0xCA,  // Source PAN ID
        0x00, 0x01,  // Source address
        0x01,        // Sequence number
        0x02,        // Frame type=Data, Protocol version=2006
        0x00,        // Security disabled
        // ... application data
    };
    
    lmac154_send(tx_data, sizeof(tx_data));
    
    while (1) {
        // Main loop
    }
}
```

### Advanced Send (with Parameters)

```c
void advanced_send_example(void)
{
    // Configure send parameters
    lmac154_txParam_t tx_param = {0};
    
    uint8_t packet[] = { /* frame data */ };
    
    tx_param.pkt = (uint32_t *)packet;
    tx_param.pkt_length = sizeof(packet);
    tx_param.tx_channel = LMAC154_CHANNEL_20 - LMAC154_CHANNEL_11;
    tx_param.is_cca = 1;                    // Enable CCA
    tx_param.is_ack_required = 1;           // Request ACK
    tx_param.csma_ca_max_backoff = 4;       // Max backoff count
    
    // Trigger transmission
    int ret = lmac154_triggerParamTx(&tx_param);
    if (ret != 0) {
        // Handle transmission failure
    }
}
```

### CCA Channel Detection

```c
void cca_check_example(void)
{
    int rssi;
    uint8_t result = lmac154_runCCA(&rssi);
    
    if (result == 0) {
        // Channel idle, can send
        lmac154_send(data, len);
    } else {
        // Channel busy, wait and retry
    }
}
```

---

## Frame Structure Diagram

### 802.15.4 MAC Frame Format

```
+--------+--------+------+----------+--------+--------+--------+------+
|        |        |      |          |        |        |        |      |
|  FCF   |  Seq   | Dst  |  Dst     |  Src   |  Src   |  Aux   |  Payload |
| (2B)   |  Num   | PAN  |  Addr    |  PAN   |  Addr  |  Sec   |  (nB) |
|        |  (1B)  | (2B) | (0/2/8B) |  (0/2B)|(0/2/8B)| Header |        |
|        |        |      |          |        |        | (5-14B)|        |
+--------+--------+------+----------+--------+--------+--------+------+
 |<---------- MAC Header (MHR) -------------------->|<---- MDS ---->|
```

- **FCF**: Frame Control Field, 2 bytes
- **Seq Num**: Sequence Number, 1 byte
- **Dst PAN/Addr**: Destination PAN ID and address
- **Src PAN/Addr**: Source PAN ID and address
- **Aux Sec Header**: Auxiliary Security Header (when security is enabled)
- **Payload**: MAC Service Data Unit

---

## References

- IEEE 802.15.4-2015 Standard
- Bouffalo SDK lmac154 Component v1.7.4
- Source files:
  - `lmac154.h` - Main header file
  - `lmac154_frame.h` - Frame structure definitions
  - `lmac154_fpt.h` - Frame pending table related definitions
