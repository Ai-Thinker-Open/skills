# CAN-FD API Reference (BL616/BL618)

> **Source:** `bouffalo_sdk/drivers/lhal/include/bflb_canfd.h`  
> **Implementation:** `bouffalo_sdk/drivers/lhal/src/bflb_canfd.c`  
> **Register Header:** `bouffalo_sdk/drivers/lhal/include/hardware/canfd_reg.h`

## Overview

The BL616/BL618 CAN-FD controller is a full-featured CAN bus controller supporting both Classic CAN (CAN 2.0) and CAN FD (Flexible Data-rate) per ISO 11898-1. It provides:

- **ISO/Bosch dual mode** — selectable via `bosch_mode` config field
- **Two transmit buffers** — Primary Tx Buffer (PTB, single slot) and Secondary Tx Buffer (STB, 16-slot FIFO with priority mode)
- **Receive buffer** — 16-slot FIFO with configurable almost-full threshold
- **Acceptance filters** — up to 16 mask/code pairs with standard/extended/mixed ID matching
- **Time-Triggered CAN (TTCAN)** — per ISO 11898-4 with CiA 603 time stamping
- **Transmitter Delay Compensation (TDC)** — for reliable FD operation at high speeds
- **Four operation modes** — Normal, Listen-Only, Internal Loopback, External Loopback
- **Comprehensive error detection** — bit, form, stuff, ACK, CRC errors with error counters

## Base Address

| Peripheral | Base Address |
|------------|-------------|
| CANFD | `0x2000A000` |

> The CANFD peripheral is accessed through `bflb_device_get_by_name("canfd")` in LHAL.

---

## Configuration Macros

### Operation Mode (`CANFD_MODE`)

| Macro | Value | Description |
|-------|-------|-------------|
| `CANFD_MODE_NORMAL` | 0 | Normal operation (transmit + receive) |
| `CANFD_MODE_LISTEN_ONLY` | 1 | Listen only (no ACK, no error flags) |
| `CANFD_MODE_INTERNAL_LOOPBACK` | 2 | Internal loopback (TX → RX internally) |
| `CANFD_MODE_EXTERNAL_LOOPBACK` | 3 | External loopback (requires external wiring) |

### Identifier Type (`CANFD_ID`)

| Macro | Value | Description |
|-------|-------|-------------|
| `CANFD_ID_STANDARD` | 0 | Standard 11-bit identifier (0–0x7FF) |
| `CANFD_ID_EXTENDED` | 1 | Extended 29-bit identifier (0–0x1FFFFFFF) |

### Frame Type (`CANFD_FRAME`)

| Macro | Value | Description |
|-------|-------|-------------|
| `CANFD_FRAME_DATA` | 0 | Data frame |
| `CANFD_FRAME_REMOTE` | 1 | Remote frame (request) |

### Frame Format (`CANFD_FORMAT`)

| Macro | Value | Description |
|-------|-------|-------------|
| `CANFD_FORMAT_CLASSIC_CAN` | 0 | Classic CAN (max 8 bytes) |
| `CANFD_FORMAT_FD_CAN` | 1 | CAN FD (up to 64 bytes) |

### Bit Rate Switch (`CANFD_BRS`)

| Macro | Value | Description |
|-------|-------|-------------|
| `CANFD_BRS_OFF` | 0 | No bit rate switching |
| `CANFD_BRS_ON` | 1 | Switch to fast bit rate for data phase |

### Error State Indicator (`CANFD_ESI`)

| Macro | Value | Description |
|-------|-------|-------------|
| `CANFD_ESI_ACTIVE` | 0 | Error active state |
| `CANFD_ESI_PASSIVE` | 1 | Error passive state |

### TX Command (`CANFD_TX_CMD`)

| Macro | Value | Description |
|-------|-------|-------------|
| `CANFD_TX_CMD_STB_ABORT` | 0 | Abort secondary Tx buffer |
| `CANFD_TX_CMD_STB_ALL_START` | 1 | Start all secondary Tx buffer transmissions |
| `CANFD_TX_CMD_STB_ONE_START` | 2 | Start one secondary Tx buffer transmission |
| `CANFD_TX_CMD_PTB_ABORT` | 3 | Abort primary Tx buffer |
| `CANFD_TX_CMD_PTB_START` | 4 | Start primary Tx buffer transmission |

### STB State (`CANFD_STB_STATE`)

| Macro | Value | Description |
|-------|-------|-------------|
| `CANFD_STB_STATE_EMPTY` | 0 | Secondary Tx buffer empty |
| `CANFD_STB_STATE_LESS_EQUAL_HALF` | 1 | ≤ half full |
| `CANFD_STB_STATE_MORE_HALF` | 2 | > half full |
| `CANFD_STB_STATE_FULL` | 3 | Secondary Tx buffer full |

### RB State (`CANFD_RB_STATE`)

| Macro | Value | Description |
|-------|-------|-------------|
| `CANFD_RB_STATE_EMPTY` | 0 | Receive buffer empty |
| `CANFD_RB_STATE_LESS_THRESHOLD` | 1 | Below almost-full threshold |
| `CANFD_RB_STATE_EQUAL_MORE_THRESHOLD` | 2 | At or above almost-full threshold |
| `CANFD_RB_STATE_FULL` | 3 | Receive buffer full |

### Error Code (`CANFD_ERROR_CODE`)

| Macro | Value | Description |
|-------|-------|-------------|
| `CANFD_ERROR_CODE_NO` | 0 | No error |
| `CANFD_ERROR_CODE_BIT` | 1 | Bit error |
| `CANFD_ERROR_CODE_FORM` | 2 | Form error |
| `CANFD_ERROR_CODE_STUFF` | 3 | Stuff error |
| `CANFD_ERROR_CODE_ACKNOWLEDGEMENT` | 4 | ACK error |
| `CANFD_ERROR_CODE_CRC` | 5 | CRC error |
| `CANFD_ERROR_CODE_OTHER` | 6 | Other error |

### Acceptance Filter ID Type (`CANFD_ACF_ID_TYPE`)

| Macro | Value | Description |
|-------|-------|-------------|
| `CANFD_ACF_STANDARD_AND_EXTENDED` | 0 | Accept both standard and extended IDs |
| `CANFD_ACF_STANDARD_ONLY` | 1 | Accept standard IDs only |
| `CANFD_ACF_EXTENDED_ONLY` | 2 | Accept extended IDs only |

### Time Stamping (`CANFD_TIME_STAMPING`)

| Macro | Value | Description |
|-------|-------|-------------|
| `CANFD_TIME_STAMPING_NONE` | 0 | No time stamping |
| `CANFD_TIME_STAMPING_POS_SOF` | 1 | Time stamp at SOF position |
| `CANFD_TIME_STAMPING_POS_EOF` | 2 | Time stamp at EOF position |

### TTCAN Timer Prescaler (`CANFD_TT_PRESC`)

| Macro | Value | Description |
|-------|-------|-------------|
| `CANFD_TT_PRESC_1` | 0 | Prescaler ÷1 |
| `CANFD_TT_PRESC_2` | 1 | Prescaler ÷2 |
| `CANFD_TT_PRESC_4` | 2 | Prescaler ÷4 |
| `CANFD_TT_PRESC_8` | 3 | Prescaler ÷8 |

### Feature Control Commands (`CANFD_CMD`)

| Command | Value | Description |
|---------|-------|-------------|
| `CANFD_CMD_SET_RESET` | 0x01 | Enter or exit reset mode |
| `CANFD_CMD_SET_PTB_SHOT` | 0x02 | Enable/disable PTB single-shot mode |
| `CANFD_CMD_SET_STB_SHOT` | 0x03 | Enable/disable STB single-shot mode |
| `CANFD_CMD_SET_BUS_OFF` | 0x04 | Force bus-off state |
| `CANFD_CMD_SET_TRANSCEIVER_STANDBY_MODE` | 0x05 | Transceiver standby mode |
| `CANFD_CMD_SET_STB_PRIORITY_MODE` | 0x06 | STB priority-based transmission mode |
| `CANFD_CMD_SET_SELF_ACK_EXTERNAL_LOOPBACK` | 0x07 | Self-ACK in external loopback |
| `CANFD_CMD_SET_RX_OVERFLOW_DROP_NEW` | 0x08 | Drop new frames on RX overflow (vs. overwrite old) |
| `CANFD_CMD_SET_RX_STORE_CORRECT_AND_ERROR_FRAME` | 0x09 | Store both correct and error frames in RB |
| `CANFD_CMD_SET_RX_THRESHOLD` | 0x0A | Set RB almost-full warning threshold |
| `CANFD_CMD_GET_RX_THRESHOLD` | 0x0B | Get RB almost-full warning threshold |
| `CANFD_CMD_SET_ERROR_WARNING_LIMIT` | 0x0C | Set error warning limit |
| `CANFD_CMD_GET_ERROR_WARNING_LIMIT` | 0x0D | Get error warning limit |
| `CANFD_CMD_GET_VERSION` | 0x0E | Get CANFD IP version |
| `CANFD_CMD_SET_TIME_STAMPING` | 0x0F | Set CiA 603 time stamping type |

---

## Data Structures

### `bflb_canfd_message_header_s` — Message Header

```c
struct bflb_canfd_message_header_s {
    uint32_t identifier;               // CAN identifier (0~0x7FF or 0~0x1FFFFFFF)
    uint8_t id_type;                   // @ref CANFD_ID
    uint8_t frame_type;                // @ref CANFD_FRAME
    uint8_t data_length;               // Payload length in bytes (0–64)
    uint8_t error_state_indicator;     // @ref CANFD_ESI (RX only)
    uint8_t bit_rate_switch;           // @ref CANFD_BRS
    uint8_t fd_format;                 // @ref CANFD_FORMAT
    uint8_t time_stamping_enable;      // Enable time stamping for this message
    uint64_t time_stamping;            // Time stamp value (RX only)
};
```

### `bflb_canfd_timing_s` — Bit Timing

```c
struct bflb_canfd_timing_s {
    uint8_t prescaler;       // 0~255 (represents 1~256)
    uint8_t segment_1;       // 0~255 (slow) / 0~31 (fast), represents 1~256 / 1~32
    uint8_t segment_2;       // 0~127 (slow) / 0~15 (fast), represents 1~128 / 1~16
    uint8_t sync_jump_width; // 0~127 (slow) / 0~15 (fast), represents 1~128 / 1~16
};
```

**Bit rate formula:** `bitrate = clk / (prescaler + 1) / (1 + (segment_1 + 1) + (segment_2 + 1))`

Where `clk` is the CANFD peripheral clock (typically 80 MHz).

### `bflb_canfd_acf_s` — Acceptance Filter

```c
struct bflb_canfd_acf_s {
    uint8_t index;    // Filter index (0–15)
    uint8_t enable;   // 1 = enable, 0 = disable
    uint8_t id_type;  // @ref CANFD_ACF_ID_TYPE
    uint8_t resv;     // Reserved (unused)
    uint32_t mask;    // Acceptance mask
    uint32_t code;    // Acceptance code
};
```

**Filter logic:** A message is accepted when `(received_id & mask) == (code & mask)`.

### `bflb_canfd_config_s` — Initialization Configuration

```c
struct bflb_canfd_config_s {
    struct bflb_canfd_timing_s timing_slow;  // Nominal bit timing
    struct bflb_canfd_timing_s timing_fast;  // Data phase bit timing (for FD+BRS)
    struct bflb_canfd_acf_s *acf;            // Acceptance filter array (NULL to skip)
    uint8_t acf_count;                       // Number of filters (0–16)
    uint8_t mode;                            // @ref CANFD_MODE
    uint8_t bosch_mode;                      // 0 = ISO 11898-1, 1 = Bosch mode
};
```

### `bflb_canfd_error_s` — Error Status

```c
struct bflb_canfd_error_s {
    uint8_t error_code;                 // @ref CANFD_ERROR_CODE
    uint8_t arbitration_lost_position;  // Bit position where arbitration was lost
    uint8_t receive_error_count;        // RX error counter (0–255)
    uint8_t transmit_error_count;       // TX error counter (0–255)
};
```

### `bflb_canfd_tt_config_s` — TTCAN Configuration

```c
struct bflb_canfd_tt_config_s {
    uint8_t time_stamping;       // @ref CANFD_TIME_STAMPING
    uint8_t prescaler;           // @ref CANFD_TT_PRESC
    uint16_t watch_trigger_time; // Watch trigger timeout (0 = disabled, max 65535)
};
```

### `bflb_canfd_tt_message_config_s` — TTCAN Message Trigger Config

```c
struct bflb_canfd_tt_message_config_s {
    uint8_t slot;         // TB slot pointer (0–63)
    uint8_t type;         // Trigger type (0–7)
    uint8_t tew;          // Time error window (0–15)
    uint16_t trig_time;   // Trigger time
};
```

---

## Interrupt Macros

### Interrupt Enable (`CANFD_INTEN`)

| Macro | Bit | Description |
|-------|-----|-------------|
| `CANFD_INTEN_ERROR` | 1 | Error interrupt |
| `CANFD_INTEN_STB_TC` | 2 | Secondary Tx buffer transmission complete |
| `CANFD_INTEN_PTB_TC` | 3 | Primary Tx buffer transmission complete |
| `CANFD_INTEN_RB_THRESHOLD` | 4 | RX buffer almost-full threshold reached |
| `CANFD_INTEN_RB_FULL` | 5 | RX buffer full |
| `CANFD_INTEN_RB_OVERRUN` | 6 | RX buffer overrun |
| `CANFD_INTEN_RB_AVAILABLE` | 7 | RX buffer has data available |
| `CANFD_INTEN_BUS_ERROR` | 17 | Bus error |
| `CANFD_INTEN_ARBITRATION_LOST` | 19 | Arbitration lost |
| `CANFD_INTEN_ERROR_PASSIVE` | 21 | Error passive state change |
| `CANFD_INTEN_TT_TIME_TRIGGER` | 28 | TTCAN time trigger |
| `CANFD_INTEN_TT_WATCH_TRIGGER` | 31 | TTCAN watch trigger |
| `CANFD_INTEN_ALL` | — | All interrupts (0x902A00FE) |

### Interrupt Status (`CANFD_INTSTS`)

| Macro | Bit | Description |
|-------|-----|-------------|
| `CANFD_INTSTS_STB_FULL` | 0 | Secondary Tx buffer full |
| `CANFD_INTSTS_ABORT` | 8 | Transmission aborted |
| `CANFD_INTSTS_ERROR` | 9 | Error detected |
| `CANFD_INTSTS_STB_TC` | 10 | Secondary Tx buffer TX complete |
| `CANFD_INTSTS_PTB_TC` | 11 | Primary Tx buffer TX complete |
| `CANFD_INTSTS_RB_THRESHOLD` | 12 | RX threshold reached |
| `CANFD_INTSTS_RB_FULL` | 13 | RX buffer full |
| `CANFD_INTSTS_RB_OVERRUN` | 14 | RX buffer overrun |
| `CANFD_INTSTS_RB_AVAILABLE` | 15 | RX buffer data available |
| `CANFD_INTSTS_BUS_ERROR` | 16 | Bus error |
| `CANFD_INTSTS_ARBITRATION_LOST` | 18 | Arbitration lost |
| `CANFD_INTSTS_ERROR_PASSIVE` | 20 | Error passive state |
| `CANFD_INTSTS_ERROR_PASSIVE_MODE` | 22 | In error passive mode |
| `CANFD_INTSTS_EWL_REACHED` | 23 | Error warning limit reached |
| `CANFD_INTSTS_TT_TIME_TRIGGER` | 27 | TTCAN time trigger fired |
| `CANFD_INTSTS_TT_TRIGGER_ERROR` | 29 | TTCAN trigger error |
| `CANFD_INTSTS_TT_WATCH_TRIGGER` | 30 | TTCAN watch trigger fired |
| `CANFD_INTSTS_ALL` | — | All status bits (0x68D5FF01) |

### Interrupt Clear (`CANFD_INTCLR`)

Use the same bit definitions as `CANFD_INTSTS`. Write `1` to clear the corresponding flag.

| Additional defines | Value | Description |
|-------------------|-------|-------------|
| `CANFD_INTCLR_ALL` | `0x6815FF00` | Clear all interrupts |
| `CANFD_INT_EVENT_MASK` | `0xFFFFFF` | Event interrupt mask (bits 0-23) |
| `CANFD_INT_TT_MASK` | `0xFF << 24` | Time-trigger interrupt mask (bits 24-31) |

---

## LHAL API Functions

### bflb_canfd_init

Initialize the CAN-FD controller with specified configuration.

```c
int bflb_canfd_init(struct bflb_device_s *dev, const struct bflb_canfd_config_s *config);
```

| Parameter | Type | Description |
|-----------|------|-------------|
| `dev` | `struct bflb_device_s *` | Device handle (from `bflb_device_get_by_name("canfd")`) |
| `config` | `const struct bflb_canfd_config_s *` | Pointer to configuration structure |

**Returns:** `0` on success, `-ETIMEDOUT` if reset release timeout.

---

### bflb_canfd_deinit

Deinitialize the CAN-FD controller (put in reset state).

```c
void bflb_canfd_deinit(struct bflb_device_s *dev);
```

---

### bflb_canfd_write_ptb

Fill the Primary Transmit Buffer with a message.

```c
void bflb_canfd_write_ptb(struct bflb_device_s *dev, struct bflb_canfd_message_header_s *head, uint8_t *data);
```

| Parameter | Type | Description |
|-----------|------|-------------|
| `dev` | `struct bflb_device_s *` | Device handle |
| `head` | `struct bflb_canfd_message_header_s *` | Message header (ID, type, length, format) |
| `data` | `uint8_t *` | Pointer to payload data |

> Use `bflb_canfd_exe_tx_cmd(dev, CANFD_TX_CMD_PTB_START)` to trigger transmission.

---

### bflb_canfd_write_stb

Fill the Secondary Transmit Buffer with a message.

```c
void bflb_canfd_write_stb(struct bflb_device_s *dev, struct bflb_canfd_message_header_s *head, uint8_t *data);
```

| Parameter | Type | Description |
|-----------|------|-------------|
| `dev` | `struct bflb_device_s *` | Device handle |
| `head` | `struct bflb_canfd_message_header_s *` | Message header |
| `data` | `uint8_t *` | Pointer to payload data |

> Each call auto-increments the STB slot. Use `bflb_canfd_exe_tx_cmd()` with `STB_ALL_START` or `STB_ONE_START` to transmit.

---

### bflb_canfd_read_rx_buffer

Read a message from the receive buffer and release the slot.

```c
void bflb_canfd_read_rx_buffer(struct bflb_device_s *dev, struct bflb_canfd_message_header_s *head, uint8_t *data);
```

| Parameter | Type | Description |
|-----------|------|-------------|
| `dev` | `struct bflb_device_s *` | Device handle |
| `head` | `struct bflb_canfd_message_header_s *` | Output: received message header |
| `data` | `uint8_t *` | Output: received payload data (must be ≥64 bytes) |

> After reading, the slot is automatically marked as empty (RREL bit set).

---

### bflb_canfd_exe_tx_cmd

Execute a transmit command.

```c
void bflb_canfd_exe_tx_cmd(struct bflb_device_s *dev, uint8_t cmd);
```

| Parameter | Type | Description |
|-----------|------|-------------|
| `dev` | `struct bflb_device_s *` | Device handle |
| `cmd` | `uint8_t` | Command, use `CANFD_TX_CMD_*` |

---

### bflb_canfd_ptb_is_busy

Check whether the primary transmit buffer is busy.

```c
uint8_t bflb_canfd_ptb_is_busy(struct bflb_device_s *dev);
```

**Returns:** `1` if busy, `0` if idle.

---

### bflb_canfd_get_tx_buffer_state

Get the secondary transmit buffer fill state.

```c
uint8_t bflb_canfd_get_tx_buffer_state(struct bflb_device_s *dev);
```

**Returns:** `CANFD_STB_STATE_*` (empty, ≤half, >half, full).

---

### bflb_canfd_get_rx_buffer_state

Get the receive buffer fill state.

```c
uint8_t bflb_canfd_get_rx_buffer_state(struct bflb_device_s *dev);
```

**Returns:** `CANFD_RB_STATE_*` (empty, below threshold, ≥threshold, full).

---

### bflb_canfd_set_tdc

Configure Transmitter Delay Compensation for FD operation.

```c
void bflb_canfd_set_tdc(struct bflb_device_s *dev, uint8_t enable, uint8_t offset);
```

| Parameter | Type | Description |
|-----------|------|-------------|
| `dev` | `struct bflb_device_s *` | Device handle |
| `enable` | `uint8_t` | 1 = enable TDC, 0 = disable |
| `offset` | `uint8_t` | Secondary sample point offset (0–127) |

---

### bflb_canfd_get_error_state

Read the current error status and counters.

```c
void bflb_canfd_get_error_state(struct bflb_device_s *dev, struct bflb_canfd_error_s *error);
```

| Parameter | Type | Description |
|-----------|------|-------------|
| `dev` | `struct bflb_device_s *` | Device handle |
| `error` | `struct bflb_canfd_error_s *` | Output: error structure |

---

### bflb_canfd_int_enable

Enable CAN-FD interrupts.

```c
void bflb_canfd_int_enable(struct bflb_device_s *dev, uint32_t inten);
```

| Parameter | Type | Description |
|-----------|------|-------------|
| `dev` | `struct bflb_device_s *` | Device handle |
| `inten` | `uint32_t` | Interrupt mask, OR'd `CANFD_INTEN_*` flags |

---

### bflb_canfd_int_disable

Disable CAN-FD interrupts.

```c
void bflb_canfd_int_disable(struct bflb_device_s *dev, uint32_t inten);
```

| Parameter | Type | Description |
|-----------|------|-------------|
| `dev` | `struct bflb_device_s *` | Device handle |
| `inten` | `uint32_t` | Interrupt mask, OR'd `CANFD_INTEN_*` flags |

---

### bflb_canfd_get_intstatus

Read interrupt status flags.

```c
uint32_t bflb_canfd_get_intstatus(struct bflb_device_s *dev);
```

**Returns:** OR'd `CANFD_INTSTS_*` flags.

---

### bflb_canfd_int_clear

Clear interrupt status flags.

```c
void bflb_canfd_int_clear(struct bflb_device_s *dev, uint32_t intclr);
```

| Parameter | Type | Description |
|-----------|------|-------------|
| `dev` | `struct bflb_device_s *` | Device handle |
| `intclr` | `uint32_t` | Clear mask, OR'd `CANFD_INTCLR_*` flags |

---

### bflb_canfd_get_tts

Get the transmit time stamp value.

```c
uint64_t bflb_canfd_get_tts(struct bflb_device_s *dev);
```

**Returns:** 64-bit time stamp of the last transmitted frame.

---

### bflb_canfd_tt_init

Initialize Time-Triggered CAN (TTCAN) operation.

```c
void bflb_canfd_tt_init(struct bflb_device_s *dev, const struct bflb_canfd_tt_config_s *config);
```

| Parameter | Type | Description |
|-----------|------|-------------|
| `dev` | `struct bflb_device_s *` | Device handle |
| `config` | `const struct bflb_canfd_tt_config_s *` | TTCAN configuration |

---

### bflb_canfd_tt_set_reference_id

Set the TTCAN reference message ID.

```c
void bflb_canfd_tt_set_reference_id(struct bflb_device_s *dev, uint32_t id, uint8_t ide_enable);
```

| Parameter | Type | Description |
|-----------|------|-------------|
| `dev` | `struct bflb_device_s *` | Device handle |
| `id` | `uint32_t` | Reference message identifier |
| `ide_enable` | `uint8_t` | `1` = extended ID, `0` = standard ID |

---

### bflb_canfd_tt_write_tb

Write a TTCAN-triggered transmit buffer message.

```c
void bflb_canfd_tt_write_tb(struct bflb_device_s *dev, struct bflb_canfd_message_header_s *head, uint8_t *data, struct bflb_canfd_tt_message_config_s *tt);
```

| Parameter | Type | Description |
|-----------|------|-------------|
| `dev` | `struct bflb_device_s *` | Device handle |
| `head` | `struct bflb_canfd_message_header_s *` | Message header |
| `data` | `uint8_t *` | Payload data |
| `tt` | `struct bflb_canfd_tt_message_config_s *` | TTCAN trigger configuration (slot, type, time) |

---

### bflb_canfd_feature_control

Control advanced CAN-FD features via command interface.

```c
int bflb_canfd_feature_control(struct bflb_device_s *dev, int cmd, size_t arg);
```

| Parameter | Type | Description |
|-----------|------|-------------|
| `dev` | `struct bflb_device_s *` | Device handle |
| `cmd` | `int` | Feature command, use `CANFD_CMD_*` |
| `arg` | `size_t` | Command argument (0/1 for toggles, value for settings) |

**Returns:** `0` on success, negative errno on failure.

---

## Usage Examples

### Example 1: Classic CAN Initialization and TX/RX

```c
#include "bflb_canfd.h"
#include "bflb_mtimer.h"

#define CANFD_CLK 80000000  // 80 MHz CANFD peripheral clock

static struct bflb_device_s *canfd_dev;

void canfd_example_init(void)
{
    // Get CANFD device handle
    canfd_dev = bflb_device_get_by_name("canfd");

    // Configure bit timing for 500 kbps nominal
    // bitrate = 80MHz / (15+1) / (1 + (7+1) + (3+1)) = 80M / 16 / 13 ≈ 384.6 kbps
    struct bflb_canfd_config_s config = {
        .mode = CANFD_MODE_NORMAL,
        .bosch_mode = 0,  // ISO 11898-1 mode
        .acf = NULL,
        .acf_count = 0,
    };

    // Nominal timing: 500 kbps @ 80 MHz
    // prescaler=9 → tq=80MHz/10=8MHz → Tq=125ns
    // seg1=14, seg2=4, sjw=3 → bit = (1+15+5)*125ns = 2.625µs → ~381kbps
    config.timing_slow.prescaler = 9;
    config.timing_slow.segment_1 = 14;
    config.timing_slow.segment_2 = 4;
    config.timing_slow.sync_jump_width = 3;

    // Data phase timing: 2 Mbps
    config.timing_fast.prescaler = 1;
    config.timing_fast.segment_1 = 14;
    config.timing_fast.segment_2 = 4;
    config.timing_fast.sync_jump_width = 3;

    int ret = bflb_canfd_init(canfd_dev, &config);
    if (ret < 0) {
        printf("CANFD init failed: %d\r\n", ret);
        return;
    }

    // Enable receive interrupt
    bflb_canfd_int_enable(canfd_dev, CANFD_INTEN_RB_AVAILABLE);
}

// Send a Classic CAN message
void canfd_send_message(uint32_t id, uint8_t *data, uint8_t len)
{
    struct bflb_canfd_message_header_s header = {
        .identifier = id,
        .id_type = CANFD_ID_STANDARD,
        .frame_type = CANFD_FRAME_DATA,
        .data_length = len,
        .bit_rate_switch = CANFD_BRS_OFF,
        .fd_format = CANFD_FORMAT_CLASSIC_CAN,
        .time_stamping_enable = 0,
    };

    // Wait until PTB is free
    while (bflb_canfd_ptb_is_busy(canfd_dev));

    bflb_canfd_write_ptb(canfd_dev, &header, data);
    bflb_canfd_exe_tx_cmd(canfd_dev, CANFD_TX_CMD_PTB_START);
}

// Receive a message (call from ISR or polling)
void canfd_receive_message(void)
{
    uint32_t status = bflb_canfd_get_intstatus(canfd_dev);

    if (status & CANFD_INTSTS_RB_AVAILABLE) {
        struct bflb_canfd_message_header_s header;
        uint8_t data[64];

        bflb_canfd_read_rx_buffer(canfd_dev, &header, data);

        printf("RX: ID=0x%X DLC=%d FDF=%d BRS=%d\r\n",
               header.identifier, header.data_length,
               header.fd_format, header.bit_rate_switch);

        // Process data...
    }
}
```

### Example 2: CAN FD with Bit Rate Switching

```c
void canfd_send_fd_message(void)
{
    struct bflb_canfd_message_header_s header = {
        .identifier = 0x123,
        .id_type = CANFD_ID_STANDARD,
        .frame_type = CANFD_FRAME_DATA,
        .data_length = 64,    // 64-byte FD payload
        .bit_rate_switch = CANFD_BRS_ON,    // Switch to fast bit rate
        .fd_format = CANFD_FORMAT_FD_CAN,   // FD format
        .time_stamping_enable = 0,
    };

    uint8_t data[64];
    for (int i = 0; i < 64; i++) {
        data[i] = i;
    }

    while (bflb_canfd_ptb_is_busy(canfd_dev));

    // Enable TDC for reliable FD operation
    bflb_canfd_set_tdc(canfd_dev, 1, 31);  // Enable TDC, offset=31

    bflb_canfd_write_ptb(canfd_dev, &header, data);
    bflb_canfd_exe_tx_cmd(canfd_dev, CANFD_TX_CMD_PTB_START);
}
```

### Example 3: Acceptance Filter Configuration

```c
void canfd_setup_filters(void)
{
    // Filter 0: Accept only ID 0x100–0x10F (standard)
    struct bflb_canfd_acf_s filter0 = {
        .index = 0,
        .enable = 1,
        .id_type = CANFD_ACF_STANDARD_ONLY,
        .mask = 0x7F0,   // Match upper 7 bits
        .code = 0x100,   // Code = 0x100
    };

    // Filter 1: Accept all extended IDs
    struct bflb_canfd_acf_s filter1 = {
        .index = 1,
        .enable = 1,
        .id_type = CANFD_ACF_EXTENDED_ONLY,
        .mask = 0x00000000,   // Match all
        .code = 0x00000000,
    };

    struct bflb_canfd_acf_s filters[] = { filter0, filter1 };

    struct bflb_canfd_config_s config = {
        .mode = CANFD_MODE_NORMAL,
        .bosch_mode = 0,
        .acf = filters,
        .acf_count = 2,
        // ... timing configuration ...
    };

    bflb_canfd_init(canfd_dev, &config);
}
```

### Example 4: Error Monitoring

```c
void canfd_check_errors(void)
{
    struct bflb_canfd_error_s error;
    bflb_canfd_get_error_state(canfd_dev, &error);

    printf("CAN Errors: code=%d alc_pos=%d rx_cnt=%d tx_cnt=%d\r\n",
           error.error_code,
           error.arbitration_lost_position,
           error.receive_error_count,
           error.transmit_error_count);

    // Check if in bus-off state
    if (error.transmit_error_count >= 256) {
        printf("BUS-OFF detected!\r\n");
        // Recover: set reset mode then exit
        bflb_canfd_feature_control(canfd_dev, CANFD_CMD_SET_RESET, 1);
        bflb_mtimer_delay_ms(1);
        bflb_canfd_feature_control(canfd_dev, CANFD_CMD_SET_RESET, 0);
    }
}
```

### Example 5: Interrupt-Driven Reception

```c
#include "bflb_canfd.h"
#include "bflb_irq.h"

static struct bflb_device_s *canfd_dev;

void canfd_irq_handler(int irq, void *arg)
{
    uint32_t status = bflb_canfd_get_intstatus(canfd_dev);

    // Handle receive buffer available
    if (status & CANFD_INTSTS_RB_AVAILABLE) {
        struct bflb_canfd_message_header_s header;
        uint8_t data[64];

        while (bflb_canfd_get_rx_buffer_state(canfd_dev) != CANFD_RB_STATE_EMPTY) {
            bflb_canfd_read_rx_buffer(canfd_dev, &header, data);
            // Process received message...
        }
    }

    // Handle errors
    if (status & CANFD_INTSTS_ERROR) {
        struct bflb_canfd_error_s error;
        bflb_canfd_get_error_state(canfd_dev, &error);
        printf("CAN Error: code=%d\r\n", error.error_code);
    }

    // Clear handled interrupts
    bflb_canfd_int_clear(canfd_dev, status);
}

void canfd_interrupt_setup(void)
{
    canfd_dev = bflb_device_get_by_name("canfd");

    // ... init config ...

    // Enable multiple interrupts
    uint32_t int_en = CANFD_INTEN_RB_AVAILABLE
                    | CANFD_INTEN_RB_FULL
                    | CANFD_INTEN_ERROR
                    | CANFD_INTEN_BUS_ERROR
                    | CANFD_INTEN_ARBITRATION_LOST;
    bflb_canfd_int_enable(canfd_dev, int_en);

    // Register IRQ handler (platform-specific)
    // bflb_irq_attach(CANFD_IRQn, canfd_irq_handler, NULL);
    // bflb_irq_enable(CANFD_IRQn);
}
```

### Example 6: Feature Control — RX Buffer Management

```c
void canfd_configure_rx_buffer(void)
{
    // Set almost-full threshold to 8 (interrupt when ≥8 messages in buffer)
    bflb_canfd_feature_control(canfd_dev, CANFD_CMD_SET_RX_THRESHOLD, 8);

    // Enable overflow mode: drop new frames instead of overwriting old ones
    bflb_canfd_feature_control(canfd_dev, CANFD_CMD_SET_RX_OVERFLOW_DROP_NEW, 1);

    // Get current threshold value
    int threshold = bflb_canfd_feature_control(canfd_dev, CANFD_CMD_GET_RX_THRESHOLD, 0);
    printf("RX threshold: %d\r\n", threshold);

    // Get IP version
    int version = bflb_canfd_feature_control(canfd_dev, CANFD_CMD_GET_VERSION, 0);
    printf("CANFD IP version: %d\r\n", version);

    // Set error warning limit to 96 (register value 11: (11+1)*8=96)
    bflb_canfd_feature_control(canfd_dev, CANFD_CMD_SET_ERROR_WARNING_LIMIT, 11);
}
```

### Example 7: CAN-FD Loopback Self-Test

```c
void canfd_loopback_test(void)
{
    struct bflb_device_s *dev;
    int ret;

    dev = bflb_device_get_by_name("canfd");

    // Initialize in internal loopback mode
    struct bflb_canfd_config_s config = {
        .mode = CANFD_MODE_INTERNAL_LOOPBACK,
        .bosch_mode = 0,
        .acf = NULL,
        .acf_count = 0,
    };

    config.timing_slow.prescaler = 9;
    config.timing_slow.segment_1 = 14;
    config.timing_slow.segment_2 = 4;
    config.timing_slow.sync_jump_width = 3;

    config.timing_fast.prescaler = 1;
    config.timing_fast.segment_1 = 14;
    config.timing_fast.segment_2 = 4;
    config.timing_fast.sync_jump_width = 3;

    ret = bflb_canfd_init(dev, &config);
    if (ret < 0) {
        printf("Init failed!\r\n");
        return;
    }

    // Send a test message
    uint8_t tx_data[8] = { 0xAA, 0xBB, 0xCC, 0xDD, 0xEE, 0xFF, 0x00, 0x11 };
    struct bflb_canfd_message_header_s tx_header = {
        .identifier = 0x456,
        .id_type = CANFD_ID_STANDARD,
        .frame_type = CANFD_FRAME_DATA,
        .data_length = 8,
        .bit_rate_switch = CANFD_BRS_OFF,
        .fd_format = CANFD_FORMAT_CLASSIC_CAN,
        .time_stamping_enable = 0,
    };

    bflb_canfd_write_ptb(dev, &tx_header, tx_data);
    bflb_canfd_exe_tx_cmd(dev, CANFD_TX_CMD_PTB_START);

    // Wait for loopback receive
    bflb_mtimer_delay_ms(10);

    // Read back the looped message
    if (bflb_canfd_get_rx_buffer_state(dev) != CANFD_RB_STATE_EMPTY) {
        struct bflb_canfd_message_header_s rx_header;
        uint8_t rx_data[64];

        bflb_canfd_read_rx_buffer(dev, &rx_header, rx_data);

        // Verify
        if (rx_header.identifier == 0x456 && rx_header.data_length == 8) {
            printf("Loopback test: PASS\r\n");
        } else {
            printf("Loopback test: FAIL\r\n");
        }
    }
}
```

---

## Register-Level Reference

The CANFD register map starts at `CANFD_BASE + 0x2000A000`. All registers are 32-bit.

### Register Overview

| Offset | Name | Description |
|--------|------|-------------|
| `0x00` | `RBUF_ID` | Receive buffer — ID and ESI |
| `0x04` | `RBUF_CTRL` | Receive buffer — control (DLC, BRS, FDF, RTR, IDE) |
| `0x08` | `RBUF_DATA` | Receive buffer — data (64 bytes) |
| `0x48` | `RBUF_RTS` | Receive buffer — time stamp (64-bit) |
| `0x50` | `TBUF_ID` | Transmit buffer — ID and TTSEN |
| `0x54` | `TBUF_CTRL` | Transmit buffer — control |
| `0x58` | `TBUF_DATA` | Transmit buffer — data (64 bytes) |
| `0x98` | `TTS` | Transmit time stamp (64-bit, read-only) |
| `0xA0` | `CTRL` | Configuration & status / command / control |
| `0xA4` | `INT` | Interrupt enable, flag, error, limits |
| `0xA8` | `S_TIMING` | Nominal bit timing (slow speed) |
| `0xAC` | `F_TIMING` | Data phase bit timing (fast speed) |
| `0xB0` | `ERROR` | Error/arbitration lost capture + TDC + error counters |
| `0xB4` | `ACFCTRL` | Acceptance filter control + CiA 603 time stamping |
| `0xB8` | `ACF_X` | Acceptance filter code/mask |
| `0xBC` | `VERSION` / `TTCFG` | IP version (no TTCAN) or TTCAN config (with TTCAN) |
| `0xC0` | `REF_MSG` | TTCAN reference message |
| `0xC4` | `TRIG_CFG` | TTCAN trigger configuration |
| `0xC8` | `TT_WTRIG` | TTCAN watch trigger time |
| `0xCC` | `MEM_ES` | Memory error stimulation |
| `0xD0` | `SCFG` | Safety configuration |

### CTRL Register (0xA0) Detailed Breakdown

The CTRL register spans 4 bytes (0xA0–0xA3) with multiple sub-registers:

**Byte 0xA0 — CFG_STAT (Configuration and Status)**

| Bit | Name | Description |
|-----|------|-------------|
| 0 | `BUSOFF` | Bus-off state (read-only) |
| 1 | `TACTIVE` | Transmitter active |
| 2 | `RACTIVE` | Receiver active |
| 3 | `TSSS` | STB single-shot mode |
| 4 | `TPSS` | PTB single-shot mode |
| 5 | `LBMI` | Internal loopback mode |
| 6 | `LBME` | External loopback mode |
| 7 | `RESET` | Reset mode (1 = in reset) |

**Byte 0xA1 — TCMD (Transmit Command)**

| Bit | Name | Description |
|-----|------|-------------|
| 8 | `TSA` | STB abort |
| 9 | `TSALL` | STB start all |
| 10 | `TSONE` | STB start one |
| 11 | `TPA` | PTB abort |
| 12 | `TPE` | PTB enable / busy |
| 13 | `STBY` | Transceiver standby |
| 14 | `LOM` | Listen-only mode |
| 15 | `TBSEL` | Buffer select (0=PTB, 1=STB) |

**Byte 0xA2 — TCTRL (Transmit Control)**

| Bits | Name | Description |
|------|------|-------------|
| 16-17 | `TSSTAT` | STB status (0=empty, 1≤½, 2>½, 3=full) |
| 20 | `TTTBM` | TTCAN time base mode |
| 21 | `TSMODE` | STB priority decision mode |
| 22 | `TSNEXT` | STB mark next slot as filled |
| 23 | `FD_ISO` | FD ISO mode (0=Bosch, 1=ISO 11898-1) |

**Byte 0xA3 — RCTRL (Receive Control)**

| Bits | Name | Description |
|------|------|-------------|
| 24-25 | `RSTAT` | RB status (0=empty, 1<threshold, 2≥threshold, 3=full) |
| 27 | `RBALL` | Store both correct and error frames |
| 28 | `RREL` | Release current RB slot |
| 29 | `ROV` | RB overrun flag |
| 30 | `ROM` | RB overflow mode (0=overwrite old, 1=drop new) |
| 31 | `SACK` | Self-ACK in external loopback |

### S_TIMING Register (0xA8)

Nominal (slow speed) bit timing — single 32-bit register:

| Bits | Name | Description |
|------|------|-------------|
| 0-7 | `S_SEG_1` | Time segment 1 (0–255, actual = value+1) |
| 8-14 | `S_SEG_2` | Time segment 2 (0–127, actual = value+1) |
| 16-22 | `S_SJW` | Sync jump width (0–127, actual = value+1) |
| 24-31 | `S_PRESC` | Prescaler (0–255, actual = value+1) |

### F_TIMING Register (0xAC)

Data phase (fast speed) bit timing — single 32-bit register:

| Bits | Name | Description |
|------|------|-------------|
| 0-4 | `F_SEG_1` | Time segment 1 (0–31, actual = value+1) |
| 8-11 | `F_SEG_2` | Time segment 2 (0–15, actual = value+1) |
| 16-19 | `F_SJW` | Sync jump width (0–15, actual = value+1) |
| 24-31 | `F_PRESC` | Prescaler (0–255, actual = value+1) |

### ERROR Register (0xB0)

| Bits | Name | Description |
|------|------|-------------|
| 0-4 | `ALC` | Arbitration lost capture position |
| 5-7 | `KOER` | Error code (0=no error, 1=bit, 2=form, 3=stuff, 4=ACK, 5=CRC, 6=other) |
| 8-14 | `SSPOFF` | TDC secondary sample point offset |
| 15 | `TDCEN` | TDC enable |
| 16-23 | `RECNT` | Receive error counter |
| 24-31 | `TECNT` | Transmit error counter |

### DLC Code Table

CAN FD uses a 4-bit DLC code to represent payload lengths:

| DLC Code | Payload Length (bytes) |
|----------|----------------------|
| 0 | 0 |
| 1 | 1 |
| 2 | 2 |
| 3 | 3 |
| 4 | 4 |
| 5 | 5 |
| 6 | 6 |
| 7 | 7 |
| 8 | 8 |
| 9 | 12 |
| 10 | 16 |
| 11 | 20 |
| 12 | 24 |
| 13 | 32 |
| 14 | 48 |
| 15 | 64 |

---

## Bit Timing Calculation

The CAN bit rate is determined by the system clock and timing parameters:

```
tq = (prescaler + 1) / f_clk
Nominal Bit Time = tq × (1 + (segment_1 + 1) + (segment_2 + 1))
bitrate = 1 / Nominal_Bit_Time
```

**Example for 500 kbps nominal @ 80 MHz:**

```
prescaler = 9   → tq = 10/80MHz = 125 ns
segment_1 = 14  → 15 tq
segment_2 = 4   → 5 tq
sjw = 3         → 4 tq

Bit Time = (1 + 15 + 5) × 125ns = 2.625 µs
bitrate = 1 / 2.625µs ≈ 381 kbps
```

For precise 500 kbps: `prescaler=7` (tq=8/80MHz=100ns), `segment_1=12` (13tq), `segment_2=5` (6tq) → 20tq × 100ns = 2µs → 500 kbps.

> The sample point is at `(1 + segment_1 + 1) / (1 + segment_1 + 1 + segment_2 + 1)`. For the above example: 16/21 ≈ 76%.
