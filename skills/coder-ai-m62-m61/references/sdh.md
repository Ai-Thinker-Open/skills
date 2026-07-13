# SDH API Reference (BL616/BL618)

> **Source:** `bouffalo_sdk/drivers/lhal/include/bflb_sdh.h`  
> **Register Header:** `bouffalo_sdk/drivers/soc/bl616/std/include/hardware/sdh_reg.h`

## Overview

The SDH (SD Host Controller) module provides a complete interface for SD/SDIO/eMMC card communication. It supports 1-bit, 4-bit, and 8-bit data bus widths, ADMA2 DMA, and various card command/response types. The controller is compliant with the SD Host Controller Standard Specification (v3).

### Supported Chips

| Chip | Variant |
|------|---------|
| BL616 / BL616CL | `SDH_STD_V3` |
| BL618DG | `SDH_STD_V3_SMIH` |

## Base Address

| Peripheral | Base Address |
|------------|-------------|
| SDH | `0x20060000` |

---

## Configuration Macros

### Data Transfer Direction

| Macro | Value | Description |
|-------|-------|-------------|
| `SDH_TRANSFER_DIR_WR` | 0 | Transfer direction: write (host → card) |
| `SDH_TRANSFER_DIR_RD` | 1 | Transfer direction: read (card → host) |

### Data Bus Width

| Macro | Value | Description |
|-------|-------|-------------|
| `SDH_DATA_BUS_WIDTH_1` | 0 | 1-bit mode |
| `SDH_DATA_BUS_WIDTH_4` | 1 | 4-bit mode |
| `SDH_DATA_BUS_WIDTH_8` | 2 | 8-bit mode |

### Endian Mode

| Macro | Value | Description |
|-------|-------|-------------|
| `SDH_ENDIAN_MODE_LITTLE` | 0 | Little endian mode |
| `SDH_ENDIAN_MODE_HALF_WORD_BIG` | 1 | Half word big endian mode |
| `SDH_ENDIAN_MODE_BIG` | 2 | Big endian mode |

### DMA FIFO Threshold

| Macro | Value | Description |
|-------|-------|-------------|
| `SDH_DMA_FIFO_THRESHOLD_64` | 0 | FIFO threshold 64 bytes |
| `SDH_DMA_FIFO_THRESHOLD_128` | 1 | FIFO threshold 128 bytes |
| `SDH_DMA_FIFO_THRESHOLD_192` | 2 | FIFO threshold 192 bytes |
| `SDH_DMA_FIFO_THRESHOLD_256` | 3 | FIFO threshold 256 bytes |

### DMA Burst Size

| Macro | Value | Description |
|-------|-------|-------------|
| `SDH_DMA_BURST_32` | 0 | Burst size 32 bytes |
| `SDH_DMA_BURST_64` | 1 | Burst size 64 bytes |
| `SDH_DMA_BURST_128` | 2 | Burst size 128 bytes |
| `SDH_DMA_BURST_256` | 3 | Burst size 256 bytes |

### DMA Type

| Macro | Value | Description |
|-------|-------|-------------|
| `SDH_DMA_TYPE_SDMA` | 0 | Simple DMA |
| `SDH_DMA_TYPE_ADMA1` | 1 | Advanced DMA 1 |
| `SDH_DMA_TYPE_ADMA2` | 2 | Advanced DMA 2 (default) |

### ADMA2 Descriptor Attributes

ADMA2 hardware descriptor table layout:

```
|----------------|---------------|-------------|--------------------------|
| Address field  |     Length    | Reserved    |         Attribute        |
|----------------|---------------|-------------|--------------------------|
|63            32|31           16|15         06|05  |04  |03|02 |01 |00   |
|----------------|---------------|-------------|----|----|--|---|---|-----|
| 32-bit address | 16-bit length | 0000000000  |Act2|Act1| 0|Int|End|Valid|
|----------------|---------------|-------------|----|----|--|---|---|-----|
```

| Macro | Description |
|-------|-------------|
| `SDH_ADMA2_ATTR_VALID` | Descriptor valid (bit 0) |
| `SDH_ADMA2_ATTR_END` | Descriptor end / complete (bit 1) |
| `SDH_ADMA2_ATTR_INT` | DMA interrupt (bit 2) |
| `SDH_ADMA2_ATTR_ACT_NOP` | No operation (Act2=0, Act1=0) |
| `SDH_ADMA2_ATTR_ACT_RSV` | Reserved (Act2=0, Act1=1) |
| `SDH_ADMA2_ATTR_ACT_TRAN` | Transfer data (Act2=1, Act1=0) |
| `SDH_ADMA2_ATTR_ACT_LINK` | Link descriptor (Act2=1, Act1=1) |

### Command Type

| Macro | Value | Description |
|-------|-------|-------------|
| `SDH_CMD_TPYE_NORMAL` | 0 | Normal command |
| `SDH_CMD_TPYE_SUPEND` | 1 | Suspend command |
| `SDH_CMD_TPYE_RESUME` | 2 | Resume command |
| `SDH_CMD_TPYE_ABORT` | 3 | Abort command |
| `SDH_CMD_TPYE_EMPTY` | 4 | Empty command |

### Response Type

| Macro | Value | Description |
|-------|-------|-------------|
| `SDH_RESP_TPYE_NONE` | 0 | No Response |
| `SDH_RESP_TPYE_R1` | 1 | Response R1 (48-bit, CRC) |
| `SDH_RESP_TPYE_R1b` | 2 | Response R1b (48-bit, busy) |
| `SDH_RESP_TPYE_R2` | 3 | Response R2 (136-bit, CID/CSD) |
| `SDH_RESP_TPYE_R3` | 4 | Response R3 (48-bit, OCR) |
| `SDH_RESP_TPYE_R4` | 5 | Response R4 (48-bit, OCR) |
| `SDH_RESP_TPYE_R5` | 6 | Response R5 (48-bit, SDIO) |
| `SDH_RESP_TPYE_R5b` | 7 | Response R5b (48-bit, busy) |
| `SDH_RESP_TPYE_R6` | 8 | Response R6 (48-bit) |
| `SDH_RESP_TPYE_R7` | 9 | Response R7 (48-bit) |

### Data Type

| Macro | Value | Description |
|-------|-------|-------------|
| `SDH_DATA_TPYE_NORMAL` | 0 | Normal read/write data |
| `SDH_DATA_TPYE_TUNING` | 1 | Tuning data |
| `SDH_DATA_TPYE_BOOT` | 2 | Boot data |
| `SDH_DATA_TPYE_BOOT_CONTINU` | 3 | Boot data continuous |

### Auto CMD Mode

| Macro | Value | Description |
|-------|-------|-------------|
| `SDH_AUTO_CMD_DISABLE` | 0 | Auto CMD disabled |
| `SDH_AUTO_CMD_CMD12` | 1 | Auto CMD12 enabled |
| `SDH_AUTO_CMD_CMD23` | 2 | Auto CMD23 enabled |

---

## Normal Interrupt Status Flags

| Macro | Bit | Description |
|-------|-----|-------------|
| `SDH_NORMAL_STA_CMD_COMP` | 0 | Command complete |
| `SDH_NORMAL_STA_TRAN_COMP` | 1 | Transfer complete |
| `SDH_NORMAL_STA_BLK_GAP_EVENT` | 2 | Block gap event |
| `SDH_NORMAL_STA_DMA_INT` | 3 | DMA interrupt |
| `SDH_NORMAL_STA_BUFF_WR_RDY` | 4 | Buffer write ready (non-DMA) |
| `SDH_NORMAL_STA_BUFF_RD_RDY` | 5 | Buffer read ready (non-DMA) |
| `SDH_NORMAL_STA_CARD_INSERT` | 6 | Card insertion detected |
| `SDH_NORMAL_STA_CARD_REMOVE` | 7 | Card removal detected |
| `SDH_NORMAL_STA_CARD_INT` | 8 | Card interrupt (SDIO DAT[1]) |
| `SDH_NORMAL_STA_INT_A` | 9 | Card interrupt INT_A |
| `SDH_NORMAL_STA_INT_B` | 10 | Card interrupt INT_B |
| `SDH_NORMAL_STA_INT_C` | 11 | Card interrupt INT_C |
| `SDH_NORMAL_STA_RETUNING_EVENT` | 12 | Re-tuning event |
| `SDH_NORMAL_STA_ERROR` | 15 | Error interrupt summary |

## Error Interrupt Status Flags

| Macro | Bit | Description |
|-------|-----|-------------|
| `SDH_ERROR_STA_CMD_TIMEOUT` | 16 | CMD timeout |
| `SDH_ERROR_STA_CMD_CRC_ERR` | 17 | CMD CRC error |
| `SDH_ERROR_STA_CMD_END_BIT` | 18 | CMD end bit error |
| `SDH_ERROR_STA_CMD_IDX_ERR` | 19 | CMD index error |
| `SDH_ERROR_STA_DATA_TIMEOUT` | 20 | Data timeout |
| `SDH_ERROR_STA_DATA_CRC_ERR` | 21 | Data CRC error |
| `SDH_ERROR_STA_DATA_END_BIT` | 22 | Data end bit error |
| `SDH_ERROR_STA_CURR_LIMIT` | 23 | Current limit exceeded |
| `SDH_ERROR_STA_AUTO_CMD_ERR` | 24 | Auto CMD12/CMD23 error |
| `SDH_ERROR_STA_ADMA_ERR` | 25 | ADMA error |
| `SDH_ERROR_STA_TUNING_ERROR` | 26 | Tuning error |
| `SDH_ERROR_STA_SPI_MODE_ERR` | 28 | SPI token error (V3 only) |
| `SDH_ERROR_STA_AXI_BUS_ERR` | 29 | AXI bus response error (V3 only) |
| `SDH_ERROR_STA_CMD_COMP_TIMEOUT` | 30 | Command completion signal timeout (V3 only) |
| `SDH_ERROR_STA_CRC_STA_ERR` | 31 | CRC status / MMC_BOOT_ACK error (V3 only) |

---

## Feature Control Commands

These are passed to `bflb_sdh_feature_control()` as the `cmd` parameter:

| Command | Description |
|---------|-------------|
| `SDH_CMD_GET_PRESENT_STA_RD_BUFF_RDY` | Check read buffer ready |
| `SDH_CMD_GET_PRESENT_STA_WD_BUFF_RDY` | Check write buffer ready |
| `SDH_CMD_GET_PRESENT_STA_RX_ACTIVE` | Check RX active |
| `SDH_CMD_GET_PRESENT_STA_TX_ACTIVE` | Check TX active |
| `SDH_CMD_GET_PRESENT_STA_RE_TUNING` | Check re-tuning request |
| `SDH_CMD_GET_PRESENT_STA_DATA_LINE_ACTIVE` | Check data line active |
| `SDH_CMD_GET_PRESENT_STA_DATA_INHIBIT` | Check data inhibit |
| `SDH_CMD_GET_PRESENT_STA_CMD_INHIBIT` | Check CMD inhibit |
| `SDH_CMD_GET_PRESENT_STA_CMD_SIG` | Get CMD signal level |
| `SDH_CMD_GET_PRESENT_STA_DATA_SIG` | Get DATA signal levels |
| `SDH_CMD_GET_PRESENT_STA_WR_PROTECT` | Check write protect |
| `SDH_CMD_GET_PRESENT_STA_CARD_DETECT` | Check card detect pin |
| `SDH_CMD_GET_PRESENT_STA_CARD_STABLE` | Check card stable |
| `SDH_CMD_GET_PRESENT_STA_CARD_INSERTED` | Check card inserted |
| `SDH_CMD_SET_BUS_WIDTH` | Set data bus width (1/4/8) |
| `SDH_CMD_SET_HS_MODE_EN` | Enable high-speed mode |
| `SDH_CMD_SET_SD_BUS_POWER` | Control SD bus power |
| `SDH_CMD_SET_INT_AT_BLK_GAP_EN` | Enable interrupt at block gap |
| `SDH_CMD_SET_RD_WAIT_EN` | Enable read wait control |
| `SDH_CMD_SET_CONTINUE_REQ` | Continue request after block gap |
| `SDH_CMD_SET_STOP_AT_BLK_GAP_REQ` | Stop at block gap request |
| `SDH_CMD_SET_BUS_CLK_DIV` | Set SD clock divider |
| `SDH_CMD_SET_BUS_CLK_EN` | Enable/disable SD bus clock |
| `SDH_CMD_GET_INTERNAL_CLK_STABLE` | Check internal clock stable |
| `SDH_CMD_SET_INTERNAL_CLK_EN` | Enable/disable internal clock |
| `SDH_CMD_SET_DATA_TIMEOUT_CNT_VAL` | Set data timeout value |
| `SDH_CMD_SOFT_RESET_ALL` | Software reset all |
| `SDH_CMD_SOFT_RESET_CMD_LINE` | Software reset CMD line |
| `SDH_CMD_SOFT_RESET_DATA_LINE` | Software reset DATA line |
| `SDH_CMD_SET_DRIVER_TYPE` | Set driver type |
| `SDH_CMD_SET_SIG_VOL_1V8_EN` | Enable 1.8V signaling |
| `SDH_CMD_SET_UHS_MODE` | Set UHS mode |
| `SDH_CMD_SET_ASYNC_INT_EN` | Enable async interrupt |
| `SDH_CMD_ACTIVE_CLK_OUT` | Active clock output (V3 only) |
| `SDH_CMD_FORCE_CLK_OUTPUT` | Force clock output (V3 only) |

---

## Data Structures

### bflb_sdh_config_s — Controller Configuration

```c
struct bflb_sdh_config_s {
    uint8_t dma_fifo_th;   // FIFO threshold (SDH_DMA_FIFO_THRESHOLD_*)
    uint8_t dma_burst;     // DMA burst size (SDH_DMA_BURST_*)
    uint8_t power_vol;     // SD bus power voltage
};
```

### bflb_sdh_data_tranfer_s — Data Transfer Descriptor

```c
struct bflb_sdh_data_tranfer_s {
    void *address;      // Data buffer address
    uint32_t length;    // Transfer length in bytes
    bool int_en;        // Enable DMA interrupt for this segment
};
```

### bflb_sdh_adma2_hw_desc_s — ADMA2 Hardware Descriptor

```c
struct bflb_sdh_adma2_hw_desc_s {
    uint16_t attribute; // ADMA2 attributes (SDH_ADMA2_ATTR_*)
    uint16_t length;    // Data length for this descriptor
    uint32_t address;   // Data buffer address
};
```

### bflb_sdh_cmd_cfg_s — Command Configuration

```c
struct bflb_sdh_cmd_cfg_s {
    uint8_t index;       // Command index (e.g., 0, 1, 8, 17, ...)
    uint8_t cmd_type;    // Command type (SDH_CMD_TPYE_*)
    uint8_t resp_type;   // Response type (SDH_RESP_TPYE_*)
    uint32_t argument;   // Command argument
    uint32_t resp[4];    // Response data (4 × 32 bits)
};
```

### bflb_sdh_data_cfg_s — Data Transfer Configuration

```c
struct bflb_sdh_data_cfg_s {
    uint8_t data_dir;       // Transfer direction (SDH_TRANSFER_DIR_*)
    uint8_t data_type;      // Data type (SDH_DATA_TPYE_*)
    uint8_t auto_cmd_mode;  // Auto CMD mode (SDH_AUTO_CMD_*)
    uint16_t block_size;    // Block size in bytes
    uint16_t block_count;   // Number of blocks

    // ADMA2 config
    bool adma2_hw_desc_raw_mode;                          // Use raw hardware descriptors
    struct bflb_sdh_data_tranfer_s *adma_tranfer;          // Transfer descriptors
    uint32_t adma_tranfer_cnt;                             // Transfer descriptor count
    struct bflb_sdh_adma2_hw_desc_s *adma2_hw_desc;        // Hardware descriptors (non-cacheable)
    uint32_t adma2_hw_desc_cnt;                            // Hardware descriptor count
};
```

### bflb_sdh_capability_s — Controller Capability

```c
struct bflb_sdh_capability_s {
    uint32_t sd_version;       // Supported SD version
    uint32_t mmc_version;      // Supported eMMC version
    uint32_t block_size_max;   // Max block size (bytes)
    uint32_t block_count_max;  // Max block count per transfer
    uint64_t capability;       // Capability flag bitmap
};
```

---

## LHAL API Functions

### bflb_sdh_init

Initialize the SD host controller. Enables internal clock, configures ADMA2 DMA mode, sets bus power voltage, and enables interrupt status reporting.

```c
int bflb_sdh_init(struct bflb_device_s *dev, struct bflb_sdh_config_s *cfg);
```

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `dev` | `struct bflb_device_s *` | SDH device handle |
| `cfg` | `struct bflb_sdh_config_s *` | Controller configuration |

**Returns:** `0` on success, negative on error.

---

### bflb_sdh_adma2_desc_init

Initialize/convert ADMA2 descriptors from transfer descriptors. Converts the high-level `adma_tranfer` array into hardware-compatible `adma2_hw_desc` descriptors.

```c
int bflb_sdh_adma2_desc_init(struct bflb_device_s *dev, struct bflb_sdh_data_cfg_s *data_cfg);
```

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `dev` | `struct bflb_device_s *` | SDH device handle |
| `data_cfg` | `struct bflb_sdh_data_cfg_s *` | Data configuration with transfer descriptors |

**Returns:**
- `0` — Success
- `-1` — NULL data_cfg
- `-2` — Unaligned address
- `-3` — Unaligned data size
- `-4` — Insufficient hardware descriptors

---

### bflb_sdh_cmd_cfg

Configure a card command. Sets up argument, command type, response type, CRC and index checking. Does NOT trigger the command.

```c
int bflb_sdh_cmd_cfg(struct bflb_device_s *dev, struct bflb_sdh_cmd_cfg_s *cmd_cfg);
```

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `dev` | `struct bflb_device_s *` | SDH device handle |
| `cmd_cfg` | `struct bflb_sdh_cmd_cfg_s *` | Command configuration |

**Returns:**
- `0` — Success
- `-1` — CMD line inhibited
- `-2` — DAT line inhibited (for R1b/R5b)

---

### bflb_sdh_data_cfg

Configure data transfer. Sets direction, block size/count, auto CMD mode, ADMA2 descriptor address, and enables DMA.

```c
int bflb_sdh_data_cfg(struct bflb_device_s *dev, struct bflb_sdh_data_cfg_s *data_cfg);
```

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `dev` | `struct bflb_device_s *` | SDH device handle |
| `data_cfg` | `struct bflb_sdh_data_cfg_s *` | Data configuration (NULL = cmd-only) |

**Returns:**
- `0` — Success
- `-2` — DAT line inhibited

---

### bflb_sdh_tranfer_start

Start a combined command + data transfer transaction. Calls `bflb_sdh_cmd_cfg()` → `bflb_sdh_adma2_desc_init()` → `bflb_sdh_data_cfg()` internally, then triggers the command.

```c
int bflb_sdh_tranfer_start(struct bflb_device_s *dev,
                            struct bflb_sdh_cmd_cfg_s *cmd_cfg,
                            struct bflb_sdh_data_cfg_s *data_cfg);
```

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `dev` | `struct bflb_device_s *` | SDH device handle |
| `cmd_cfg` | `struct bflb_sdh_cmd_cfg_s *` | Command configuration |
| `data_cfg` | `struct bflb_sdh_data_cfg_s *` | Data configuration (NULL for CMD-only) |

**Returns:** `0` on success, transfer error code on failure.

---

### bflb_sdh_get_resp

Read the response registers after command completion. Fills the `resp[4]` array in the command config structure.

```c
int bflb_sdh_get_resp(struct bflb_device_s *dev, struct bflb_sdh_cmd_cfg_s *cmd_cfg);
```

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `dev` | `struct bflb_device_s *` | SDH device handle |
| `cmd_cfg` | `struct bflb_sdh_cmd_cfg_s *` | Command config (receives response) |

**Returns:** `0` on success.

---

### bflb_sdh_sta_en

Enable or disable individual status signals. Use `SDH_NORMAL_STA_*` and `SDH_ERROR_STA_*` macros for `sta_bit`.

```c
void bflb_sdh_sta_en(struct bflb_device_s *dev, uint32_t sta_bit, bool en);
```

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `dev` | `struct bflb_device_s *` | SDH device handle |
| `sta_bit` | `uint32_t` | Status bit mask to configure |
| `en` | `bool` | `true` = enable, `false` = disable |

---

### bflb_sdh_sta_en_get

Get the currently enabled status register value.

```c
uint32_t bflb_sdh_sta_en_get(struct bflb_device_s *dev);
```

**Returns:** 32-bit enabled status mask.

---

### bflb_sdh_sta_int_en

Enable or disable status-based interrupts. Use `SDH_NORMAL_STA_*` and `SDH_ERROR_STA_*` macros for `sta_bit`.

```c
void bflb_sdh_sta_int_en(struct bflb_device_s *dev, uint32_t sta_bit, bool en);
```

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `dev` | `struct bflb_device_s *` | SDH device handle |
| `sta_bit` | `uint32_t` | Interrupt bit mask to configure |
| `en` | `bool` | `true` = enable, `false` = disable |

---

### bflb_sdh_sta_int_en_get

Get the currently enabled interrupt status register value.

```c
uint32_t bflb_sdh_sta_int_en_get(struct bflb_device_s *dev);
```

**Returns:** 32-bit interrupt enable mask.

---

### bflb_sdh_sta_get

Read current interrupt status register.

```c
uint32_t bflb_sdh_sta_get(struct bflb_device_s *dev);
```

**Returns:** 32-bit status value (OR of `SDH_NORMAL_STA_*` and `SDH_ERROR_STA_*`).

---

### bflb_sdh_sta_clr

Clear specific interrupt status bits.

```c
void bflb_sdh_sta_clr(struct bflb_device_s *dev, uint32_t sta_bit);
```

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `dev` | `struct bflb_device_s *` | SDH device handle |
| `sta_bit` | `uint32_t` | Status bit mask to clear |

---

### bflb_sdh_feature_control

Extended feature control interface. Provides clock, bus width, power, and reset control.

```c
int bflb_sdh_feature_control(struct bflb_device_s *dev, int cmd, uintptr_t arg);
```

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `dev` | `struct bflb_device_s *` | SDH device handle |
| `cmd` | `int` | Feature command (`SDH_CMD_*`) |
| `arg` | `uintptr_t` | Command argument (value depends on cmd) |

**Returns:**
- `0` — Success (or value for get commands)
- `-1` — Invalid argument (e.g., bad bus width)
- `-EPERM` — Unsupported command

---

## Usage Example

```c
#include "bflb_sdh.h"
#include "bflb_clock.h"
#include "bflb_gpio.h"

// SDH card initialization example
void sdh_card_init_example(void)
{
    struct bflb_device_s *sdh;

    sdh = bflb_device_get_by_name("sdh");

    // Initialize SDH controller with ADMA2
    struct bflb_sdh_config_s sdh_cfg = {
        .dma_fifo_th = SDH_DMA_FIFO_THRESHOLD_128,
        .dma_burst = SDH_DMA_BURST_128,
        .power_vol = 7, // 3.3V
    };
    bflb_sdh_init(sdh, &sdh_cfg);

    // Set clock to 400 kHz for card identification
    // SD clock = root_clk / (2 * divider)
    uint32_t root_clk = bflb_clk_get_peripheral_clock(BFLB_DEVICE_TYPE_SDH, SDH_CLK);
    uint32_t divider = root_clk / 400000;
    bflb_sdh_feature_control(sdh, SDH_CMD_SET_BUS_CLK_DIV, divider);
    bflb_sdh_feature_control(sdh, SDH_CMD_SET_BUS_CLK_EN, 1);

    // Power on SD bus
    bflb_sdh_feature_control(sdh, SDH_CMD_SET_SD_BUS_POWER, 1);

    // Send CMD0 (GO_IDLE_STATE)
    struct bflb_sdh_cmd_cfg_s cmd = {
        .index = 0,
        .cmd_type = SDH_CMD_TPYE_NORMAL,
        .resp_type = SDH_RESP_TPYE_NONE,
        .argument = 0,
    };
    bflb_sdh_cmd_cfg(sdh, &cmd);
    // trigger command send by writing index byte
    bflb_sdh_tranfer_start(sdh, &cmd, NULL);

    // Wait for command complete
    while (!(bflb_sdh_sta_get(sdh) & SDH_NORMAL_STA_CMD_COMP));
    bflb_sdh_sta_clr(sdh, SDH_NORMAL_STA_CMD_COMP);

    // Send CMD8 with response
    cmd.index = 8;
    cmd.resp_type = SDH_RESP_TPYE_R7;
    cmd.argument = 0x000001AA; // 2.7-3.6V, check pattern
    bflb_sdh_tranfer_start(sdh, &cmd, NULL);

    while (!(bflb_sdh_sta_get(sdh) & SDH_NORMAL_STA_CMD_COMP));
    bflb_sdh_sta_clr(sdh, SDH_NORMAL_STA_CMD_COMP);

    // Read response
    bflb_sdh_get_resp(sdh, &cmd);
    // cmd.resp[0] contains the R7 response
}
```

### Multi-Block DMA Read Example

```c
void sdh_dma_read_example(struct bflb_device_s *sdh, uint32_t sector, uint8_t *buffer, uint32_t count)
{
    // Setup ADMA2 hardware descriptors (must be non-cacheable)
    static struct bflb_sdh_adma2_hw_desc_s adma2_desc[1]
        __attribute__((aligned(4)));

    // Setup transfer descriptor
    struct bflb_sdh_data_tranfer_s tranfer = {
        .address = buffer,
        .length = count * 512,   // 512 bytes per sector
        .int_en = true,
    };

    // Setup data configuration
    struct bflb_sdh_data_cfg_s data_cfg = {
        .data_dir = SDH_TRANSFER_DIR_RD,
        .data_type = SDH_DATA_TPYE_NORMAL,
        .auto_cmd_mode = SDH_AUTO_CMD_CMD12,
        .block_size = 512,
        .block_count = count,
        .adma2_hw_desc_raw_mode = false,
        .adma_tranfer = &tranfer,
        .adma_tranfer_cnt = 1,
        .adma2_hw_desc = adma2_desc,
        .adma2_hw_desc_cnt = 1,
    };

    // Setup command
    struct bflb_sdh_cmd_cfg_s cmd = {
        .index = (count > 1) ? 18 : 17,  // READ_MULTIPLE or READ_SINGLE
        .cmd_type = SDH_CMD_TPYE_NORMAL,
        .resp_type = SDH_RESP_TPYE_R1,
        .argument = sector,               // For SDSC: sector * 512
    };

    // Start transfer
    bflb_sdh_tranfer_start(sdh, &cmd, &data_cfg);

    // Wait for transfer complete
    while (!(bflb_sdh_sta_get(sdh) & SDH_NORMAL_STA_TRAN_COMP));

    // Check for errors
    uint32_t status = bflb_sdh_sta_get(sdh);
    if (status & SDH_NORMAL_STA_ERROR) {
        // Handle error
    }

    bflb_sdh_sta_clr(sdh, SDH_NORMAL_STA_CMD_COMP | SDH_NORMAL_STA_TRAN_COMP);

    bflb_sdh_get_resp(sdh, &cmd);
}
```

---

## Register-Level Reference

### SDH Register Map

| Offset | Register | Description |
|--------|----------|-------------|
| `0x00` | `SDH_SYS_ADDR_LOW` | System Address Low (DMA addr [15:0]) |
| `0x02` | `SDH_SYS_ADDR_HIGH` | System Address High (DMA addr [31:16]) |
| `0x04` | `SDH_BLOCK_SIZE` | Block Size [11:0] + DMA Boundary [14:12] |
| `0x06` | `SDH_BLOCK_COUNT` | Block Count |
| `0x08` | `SDH_ARG_LOW` | Argument Low [15:0] |
| `0x0A` | `SDH_ARG_HIGH` | Argument High [31:16] |
| `0x0C` | `SDH_TRANSFER_MODE` | Transfer Mode: DMA_EN[0], BLK_CNT_EN[1], AUTO_CMD[3:2], DIR[4], MULTI_BLK[5] |
| `0x0E` | `SDH_CMD` | Command: RESP_TYPE[1:0], CRC_CHK[3], IDX_CHK[4], DATA_PRESENT[5], CMD_TYPE[7:6], CMD_INDEX[13:8] |
| `0x10–0x1E` | `SDH_RESP_0` – `SDH_RESP_7` | Response registers (8 × 16-bit) |
| `0x20` | `SDH_BUFFER_DATA_PORT_0` | Buffer Data Port 0 (non-DMA) |
| `0x22` | `SDH_BUFFER_DATA_PORT_1` | Buffer Data Port 1 (non-DMA) |
| `0x24` | `SDH_PRESENT_STATE_1` | Present State: CMD/DAT inhibit, DAT active, TX/RX active, buffer ready |
| `0x26` | `SDH_PRESENT_STATE_2` | Present State: card inserted/stable, write protect, DAT/CMD levels |
| `0x28` | `SDH_HOST_CTRL` | Host Control: data width, high speed, DMA select, bus power/voltage |
| `0x2A` | `SDH_BLOCK_GAP_CTRL` | Block Gap Control |
| `0x2C` | `SDH_CLOCK_CTRL` | Clock Control: internal clk, SD clk, frequency divider [15:6] |
| `0x2E` | `SDH_TIMEOUT_CTRL` | Timeout Control + Software Reset |
| `0x30` | `SDH_NORMAL_INT_STATUS` | Normal Interrupt Status |
| `0x34` | `SDH_NORMAL_INT_STATUS_EN` | Normal Interrupt Status Enable |
| `0x38` | `SDH_NORMAL_INT_STATUS_INT_EN` | Normal Interrupt Signal Enable |

### Key Register Bit Fields

#### Clock Control (0x2C)

| Bit | Field | Description |
|-----|-------|-------------|
| 0 | `SDH_INT_CLK_EN` | Internal clock enable |
| 1 | `SDH_INT_CLK_STABLE` | Internal clock stable (RO) |
| 2 | `SDH_SD_CLK_EN` | SD bus clock enable |
| 5 | `SDH_CLK_GEN_SEL` | Clock generator select |
| 7:6 | `SDH_SD_FREQ_SEL_HI` | SD frequency select [9:8] |
| 15:8 | `SDH_SD_FREQ_SEL_LO` | SD frequency select [7:0] |

**Clock formula:** `SD_CLK = root_clk / (2 × (divider + 1))`

#### Host Control (0x28)

| Bit | Field | Description |
|-----|-------|-------------|
| 0 | `SDH_LED_CTRL` | LED control |
| 1 | `SDH_DATA_WIDTH` | Data width (0=1-bit, 1=4-bit) |
| 2 | `SDH_HI_SPEED_EN` | High speed enable |
| 4:3 | `SDH_DMA_SEL` | DMA select (2=ADMA2) |
| 5 | `SDH_EX_DATA_WIDTH` | Extended data width (for 8-bit) |
| 8 | `SDH_SD_BUS_POWER` | SD bus power |
| 11:9 | `SDH_SD_BUS_VLT` | SD bus voltage select |

### Data Timeout Formula

```
Data_timeout_s = 2^(timeout_val + 13) / root_clk_freq
```

Where `timeout_val` is the 4-bit value written to `SDH_TIMEOUT_VALUE` in register `0x2E`.

### CLKOUT Feature (SDH_STD_V3 Only)

When using `SDH_CMD_ACTIVE_CLK_OUT`:
- Enables MISC interrupt and waits for MISC completion
- Uses `SDH_GEN_PAD_CLK_CNT` and `SDH_GEN_PAD_CLK_ON` in the `SDH_CFG_FIFO_PARAM` register

When using `SDH_CMD_FORCE_CLK_OUTPUT`:
- Sets `SDH_OVRRD_CLK_OEN` and optionally `SDH_FORCE_CLK_ON` in `SDH_FIFO_PARAM` register
