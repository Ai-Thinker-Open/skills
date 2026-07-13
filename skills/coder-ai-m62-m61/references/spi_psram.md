# SPI PSRAM API Reference (BL616/BL618)

> **Source:** `bouffalo_sdk/drivers/lhal/include/bflb_spi_psram.h`  
> **Source (implementation):** `bouffalo_sdk/drivers/lhal/src/bflb_spi_psram.c`  
> **Register Header:** `bouffalo_sdk/drivers/soc/bl616/std/include/hardware/sf_ctrl_reg.h`  
> **Dependencies:** `bflb_sf_ctrl.h`, `bflb_l1c.h`

## Overview

The SPI PSRAM module provides a software-level driver for interfacing with external SPI/QPI PSRAM (Pseudo-Static RAM) devices via the Serial Flash Controller (SF_CTRL) peripheral. It supports both standard SPI mode (1-bit) and QPI mode (4-bit), configurable drive strength, burst length/wrap size, and read/write operations.

The driver communicates with the PSRAM by constructing low-level commands and sending them through the SF_CTRL hardware. All API functions are marked `__WEAK` and placed in TCM (Tightly Coupled Memory) for performance.

## Base Addresses

| Peripheral | Base Address |
|------------|-------------|
| SF_CTRL | `0x2000B000` |
| SF_CTRL BUF | `0x2000B600` |
| BFLB_SF_CTRL (BL616/BL618) | `0x2000B000` |

---

## Configuration Macros

### Drive Strength

| Macro | Value | Description |
|-------|-------|-------------|
| `PSRAM_DRIVE_STRENGTH_50_OHMS` | 0 | Drive strength 50 ohms (default) |
| `PSRAM_DRIVE_STRENGTH_100_OHMS` | 1 | Drive strength 100 ohms |
| `PSRAM_DRIVE_STRENGTH_200_OHMS` | 2 | Drive strength 200 ohms |

### Burst Length (Wrap Size)

| Macro | Value | Description |
|-------|-------|-------------|
| `PSRAM_BURST_LENGTH_16_BYTES` | 0 | Burst length 16 bytes |
| `PSRAM_BURST_LENGTH_32_BYTES` | 1 | Burst length 32 bytes |
| `PSRAM_BURST_LENGTH_64_BYTES` | 2 | Burst length 64 bytes |
| `PSRAM_BURST_LENGTH_512_BYTES` | 3 | Burst length 512 bytes (default) |

### Control Mode (IO Mode)

| Macro | Value | Description |
|-------|-------|-------------|
| `PSRAM_SPI_CTRL_MODE` | 0 | Standard SPI mode (1-bit command/address/data) |
| `PSRAM_QPI_CTRL_MODE` | 1 | QPI mode (4-bit command/address/data) |

---

## Data Structure

### spi_psram_cfg_type — PSRAM Configuration

```c
struct spi_psram_cfg_type {
    uint8_t read_id_cmd;              // Read ID command opcode
    uint8_t read_id_dmy_clk;          // Read ID dummy clock cycles
    uint8_t burst_toggle_cmd;         // Burst toggle length command opcode
    uint8_t reset_enable_cmd;         // Reset enable command opcode
    uint8_t reset_cmd;                // Reset command opcode
    uint8_t enter_quad_mode_cmd;      // Enter quad mode command opcode
    uint8_t exit_quad_mode_cmd;       // Exit quad mode command opcode
    uint8_t read_reg_cmd;             // Read register command opcode
    uint8_t read_reg_dmy_clk;         // Read register dummy clock cycles
    uint8_t write_reg_cmd;            // Write register command opcode
    uint8_t read_cmd;                 // Standard read command opcode
    uint8_t read_dmy_clk;             // Standard read dummy clock cycles
    uint8_t f_read_cmd;               // Fast read command opcode
    uint8_t f_read_dmy_clk;           // Fast read dummy clock cycles
    uint8_t f_read_quad_cmd;          // Fast read quad command opcode
    uint8_t f_read_quad_dmy_clk;      // Fast read quad dummy clock cycles
    uint8_t write_cmd;                // Write command opcode
    uint8_t quad_write_cmd;           // Quad write command opcode
    uint16_t page_size;               // PSRAM page size
#if defined(BL702L)
    uint8_t burst_toggle_en;          // Burst toggle mode enable (BL702L only)
#endif
    uint8_t ctrl_mode;                // Control mode (PSRAM_SPI_CTRL_MODE / PSRAM_QPI_CTRL_MODE)
    uint8_t drive_strength;           // Drive strength (PSRAM_DRIVE_STRENGTH_*)
    uint8_t burst_length;             // Burst wrap length (PSRAM_BURST_LENGTH_*)
};
```

---

## LHAL API Functions

### bflb_psram_init

Initialize the PSRAM controller interface. Configures SF_CTRL hardware, sets commands for the flash controller, and configures drive strength and burst wrap.

```c
void bflb_psram_init(struct spi_psram_cfg_type *psram_cfg,
                     struct sf_ctrl_cmds_cfg *cmds_cfg,
                     struct sf_ctrl_psram_cfg *sf_ctrl_psram_cfg);
```

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `psram_cfg` | `struct spi_psram_cfg_type *` | PSRAM parameter configuration |
| `cmds_cfg` | `struct sf_ctrl_cmds_cfg *` | SF_CTRL command set configuration |
| `sf_ctrl_psram_cfg` | `struct sf_ctrl_psram_cfg *` | SF_CTRL PSRAM hardware configuration |

**Internal flow:**
1. `bflb_sf_ctrl_psram_init(sf_ctrl_psram_cfg)` — Initialize hardware
2. `bflb_sf_ctrl_cmds_set(cmds_cfg, 0)` — Program command table
3. (BL702L only) `bflb_sf_ctrl_burst_toggle_set()`
4. `bflb_psram_setdrivestrength(psram_cfg)` — Configure drive strength
5. `bflb_psram_setburstwrap(psram_cfg)` — Configure burst wrap

---

### bflb_psram_readreg

Read the PSRAM configuration register. Sends the configured `read_reg_cmd` with 3-byte address and reads 1 byte of register data.

```c
void bflb_psram_readreg(struct spi_psram_cfg_type *psram_cfg, uint8_t *reg_value);
```

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `psram_cfg` | `struct spi_psram_cfg_type *` | PSRAM configuration |
| `reg_value` | `uint8_t *` | Pointer to store the read register value |

**Note:** In QPI mode (`PSRAM_QPI_CTRL_MODE`), the command, address, and data phases all use 4-line mode.

---

### bflb_psram_writereg

Write to the PSRAM configuration register. Copies the register value to the SF_CTRL buffer, then sends the configured `write_reg_cmd`.

```c
void bflb_psram_writereg(struct spi_psram_cfg_type *psram_cfg, uint8_t *reg_value);
```

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `psram_cfg` | `struct spi_psram_cfg_type *` | PSRAM configuration |
| `reg_value` | `uint8_t *` | Pointer to the register value to write |

---

### bflb_psram_setdrivestrength

Set PSRAM output drive strength. Reads the current register, modifies bits [1:0], writes back, and verifies.

```c
int bflb_psram_setdrivestrength(struct spi_psram_cfg_type *psram_cfg);
```

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `psram_cfg` | `struct spi_psram_cfg_type *` | PSRAM configuration (uses `.drive_strength`) |

**Returns:**
- `0` — Success (already set or verified)
- `-1` — Failed to verify after write

**Register bits:** Bits [1:0] of the PSRAM configuration register control drive strength.

---

### bflb_psram_setburstwrap

Set PSRAM burst wrap (wrap length). Reads the current register, modifies bits [6:5], writes back, and verifies.

```c
int bflb_psram_setburstwrap(struct spi_psram_cfg_type *psram_cfg);
```

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `psram_cfg` | `struct spi_psram_cfg_type *` | PSRAM configuration (uses `.burst_length`) |

**Returns:**
- `0` — Success
- `-1` — Failed to verify

**Register bits:** Bits [6:5] of the PSRAM configuration register control burst wrap length.

---

### bflb_psram_readid

Read the PSRAM device ID (8 bytes). Sends the configured `read_id_cmd` with `read_id_dmy_clk` dummy cycles.

```c
void bflb_psram_readid(struct spi_psram_cfg_type *psram_cfg, uint8_t *data);
```

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `psram_cfg` | `struct spi_psram_cfg_type *` | PSRAM configuration |
| `data` | `uint8_t *` | Buffer to store 8 bytes of ID data |

---

### bflb_psram_enterquadmode

Put the PSRAM into Quad I/O (QPI) mode. Sends the configured `enter_quad_mode_cmd`.

```c
int bflb_psram_enterquadmode(struct spi_psram_cfg_type *psram_cfg);
```

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `psram_cfg` | `struct spi_psram_cfg_type *` | PSRAM configuration |

**Returns:**
- `0` — Success
- `-2` — Timeout (SF_CTRL busy)

---

### bflb_psram_exitquadmode

Exit Quad I/O (QPI) mode and return to standard SPI mode. Sends the configured `exit_quad_mode_cmd` in 4-line mode.

```c
int bflb_psram_exitquadmode(struct spi_psram_cfg_type *psram_cfg);
```

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `psram_cfg` | `struct spi_psram_cfg_type *` | PSRAM configuration |

**Returns:**
- `0` — Success
- `-2` — Timeout

---

### bflb_psram_toggleburstlength

Toggle the burst length setting of the PSRAM. Sends the configured `burst_toggle_cmd`.

```c
int bflb_psram_toggleburstlength(struct spi_psram_cfg_type *psram_cfg, uint8_t ctrl_mode);
```

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `psram_cfg` | `struct spi_psram_cfg_type *` | PSRAM configuration |
| `ctrl_mode` | `uint8_t` | Control mode for this operation (PSRAM_SPI_CTRL_MODE / PSRAM_QPI_CTRL_MODE) |

**Returns:**
- `0` — Success
- `-2` — Timeout

---

### bflb_psram_softwarereset

Perform a software reset of the PSRAM device. Sends `reset_enable_cmd` followed by `reset_cmd`. Waits 50 µs after reset.

```c
int bflb_psram_softwarereset(struct spi_psram_cfg_type *psram_cfg, uint8_t ctrl_mode);
```

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `psram_cfg` | `struct spi_psram_cfg_type *` | PSRAM configuration |
| `ctrl_mode` | `uint8_t` | Control mode for reset commands |

**Returns:**
- `0` — Success
- `-2` — Timeout

**Sequence:**
1. Send `reset_enable_cmd` (e.g., 0x66)
2. Wait for busy clear
3. Send `reset_cmd` (e.g., 0x99)
4. Wait for busy clear
5. Delay 50 µs

---

### bflb_psram_set_idbus_cfg

Configure the SF_CTRL IDBus read/write command parameters for cache access. Sets up read and write command descriptors for the specified IO mode.

```c
int bflb_psram_set_idbus_cfg(struct spi_psram_cfg_type *psram_cfg,
                              uint8_t io_mode, uint32_t addr, uint32_t len);
```

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `psram_cfg` | `struct spi_psram_cfg_type *` | PSRAM configuration |
| `io_mode` | `uint8_t` | IO mode: `SF_CTRL_NIO_MODE` (SPI) or `SF_CTRL_QIO_MODE` (QPI) |
| `addr` | `uint32_t` | Base address for read/write commands |
| `len` | `uint32_t` | Data length for read/write commands |

**Returns:**
- `0` — Success
- `-1` — Invalid IO mode

**Internal behavior:**
- Takes ownership of SF_CTRL via `bflb_sf_ctrl_set_owner(SF_CTRL_OWNER_IAHB)`
- Configures read command: `f_read_cmd` (NIO) or `f_read_quad_cmd` (QIO) with appropriate dummy cycles
- Configures write command: `write_cmd` (NIO) or `quad_write_cmd` (QIO)
- Calls `bflb_sf_ctrl_psram_read_set()` and `bflb_sf_ctrl_psram_write_set()`

---

### bflb_psram_cache_write_set

Configure PSRAM cache write behavior. Sets up IDBus configuration for 32-byte cache line reads and configures L1 cache write policy.

```c
int bflb_psram_cache_write_set(struct spi_psram_cfg_type *psram_cfg,
                                uint8_t io_mode, uint8_t wt_en,
                                uint8_t wb_en, uint8_t wa_en);
```

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `psram_cfg` | `struct spi_psram_cfg_type *` | PSRAM configuration |
| `io_mode` | `uint8_t` | IO mode (SF_CTRL_NIO_MODE / SF_CTRL_QIO_MODE) |
| `wt_en` | `uint8_t` | Write-through cache enable |
| `wb_en` | `uint8_t` | Write-back cache enable |
| `wa_en` | `uint8_t` | Write-allocate cache enable |

**Returns:**
- `0` — Success
- Other — Error from `bflb_psram_set_idbus_cfg()`

**Note:** Cache is configured for 32-byte read operations.

---

### bflb_psram_write

Write data to PSRAM. Breaks large writes into burst-aligned chunks respecting the configured burst length, sends each chunk via SF_CTRL.

```c
int bflb_psram_write(struct spi_psram_cfg_type *psram_cfg, uint8_t io_mode,
                      uint32_t addr, uint8_t *data, uint32_t len);
```

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `psram_cfg` | `struct spi_psram_cfg_type *` | PSRAM configuration |
| `io_mode` | `uint8_t` | IO mode (SF_CTRL_NIO_MODE / SF_CTRL_QIO_MODE) |
| `addr` | `uint32_t` | Starting address in PSRAM |
| `data` | `uint8_t *` | Source data buffer |
| `len` | `uint32_t` | Number of bytes to write |

**Returns:**
- `0` — Success
- `-1` — Invalid IO mode

**Behavior:**
- Data is copied to the SF_CTRL buffer before each command
- Writes are broken into chunks aligned to the configured burst length (16/32/64/512 bytes)
- Each chunk triggers a separate SF_CTRL command

---

### bflb_psram_read

Read data from PSRAM. Breaks large reads into burst-aligned chunks, sends read commands via SF_CTRL, waits for completion, then copies data from SF_CTRL buffer.

```c
int bflb_psram_read(struct spi_psram_cfg_type *psram_cfg, uint8_t io_mode,
                     uint32_t addr, uint8_t *data, uint32_t len);
```

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `psram_cfg` | `struct spi_psram_cfg_type *` | PSRAM configuration |
| `io_mode` | `uint8_t` | IO mode (SF_CTRL_NIO_MODE / SF_CTRL_QIO_MODE) |
| `addr` | `uint32_t` | Starting address in PSRAM |
| `data` | `uint8_t *` | Destination data buffer |
| `len` | `uint32_t` | Number of bytes to read |

**Returns:**
- `0` — Success
- `-1` — Invalid IO mode
- `-2` — Timeout (SF_CTRL busy too long)

**Behavior:**
- Large reads are chunked to `NOR_FLASH_CTRL_BUF_SIZE` maximum per command
- Small reads are padded to word-aligned (4-byte) boundaries for SF_CTRL
- Data is copied from SF_CTRL buffer after each chunk completes

---

## Usage Examples

### Example 1: Basic PSRAM Initialization and Read/Write

```c
#include "bflb_spi_psram.h"
#include "bflb_sf_ctrl.h"

// Typical APS6404L PSRAM configuration
static struct spi_psram_cfg_type psram_cfg = {
    .read_id_cmd = 0x9F,
    .read_id_dmy_clk = 0,
    .burst_toggle_cmd = 0xC0,
    .reset_enable_cmd = 0x66,
    .reset_cmd = 0x99,
    .enter_quad_mode_cmd = 0x35,
    .exit_quad_mode_cmd = 0xF5,
    .read_reg_cmd = 0x05,
    .read_reg_dmy_clk = 1,
    .write_reg_cmd = 0x01,
    .read_cmd = 0x03,
    .read_dmy_clk = 0,
    .f_read_cmd = 0x0B,
    .f_read_dmy_clk = 1,
    .f_read_quad_cmd = 0xEB,
    .f_read_quad_dmy_clk = 3,
    .write_cmd = 0x02,
    .quad_write_cmd = 0x38,
    .page_size = 1024,
    .ctrl_mode = PSRAM_SPI_CTRL_MODE,
    .drive_strength = PSRAM_DRIVE_STRENGTH_50_OHMS,
    .burst_length = PSRAM_BURST_LENGTH_512_BYTES,
};

void psram_example(void)
{
    uint8_t tx_data[256];
    uint8_t rx_data[256] = {0};
    uint8_t psram_id[8];

    // Fill test pattern
    for (int i = 0; i < 256; i++) {
        tx_data[i] = i;
    }

    // Initialize PSRAM with SF_CTRL
    struct sf_ctrl_psram_cfg sf_psram_cfg = { /* ... */ };
    struct sf_ctrl_cmds_cfg cmds_cfg = { /* ... */ };
    bflb_psram_init(&psram_cfg, &cmds_cfg, &sf_psram_cfg);

    // Read PSRAM ID
    bflb_psram_readid(&psram_cfg, psram_id);

    // Write data in SPI mode
    bflb_psram_write(&psram_cfg, SF_CTRL_NIO_MODE, 0x000000, tx_data, 256);

    // Read it back
    bflb_psram_read(&psram_cfg, SF_CTRL_NIO_MODE, 0x000000, rx_data, 256);

    // Verify
    for (int i = 0; i < 256; i++) {
        if (rx_data[i] != tx_data[i]) {
            // Error at index i
        }
    }
}
```

### Example 2: QPI Mode Read/Write

```c
void psram_qpi_example(void)
{
    // First enter QPI mode (must be in SPI mode beforehand)
    int ret = bflb_psram_enterquadmode(&psram_cfg);
    if (ret != 0) {
        // Failed to enter quad mode
        return;
    }

    // Update control mode
    psram_cfg.ctrl_mode = PSRAM_QPI_CTRL_MODE;

    // Now read/write in QPI mode (4-line)
    uint8_t data[512];
    bflb_psram_read(&psram_cfg, SF_CTRL_QIO_MODE, 0x100000, data, 512);

    uint8_t write_data[512];
    for (int i = 0; i < 512; i++) write_data[i] = i;
    bflb_psram_write(&psram_cfg, SF_CTRL_QIO_MODE, 0x100000, write_data, 512);

    // Exit QPI mode when done
    bflb_psram_exitquadmode(&psram_cfg);
    psram_cfg.ctrl_mode = PSRAM_SPI_CTRL_MODE;
}
```

### Example 3: Configure Drive Strength and Burst Length

```c
void psram_config_example(void)
{
    // Set drive strength to 100 ohms
    psram_cfg.drive_strength = PSRAM_DRIVE_STRENGTH_100_OHMS;
    bflb_psram_setdrivestrength(&psram_cfg);

    // Set burst wrap to 32 bytes
    psram_cfg.burst_length = PSRAM_BURST_LENGTH_32_BYTES;
    bflb_psram_setburstwrap(&psram_cfg);

    // Read register to verify
    uint8_t reg_val;
    bflb_psram_readreg(&psram_cfg, &reg_val);
    // Bits [1:0] = drive strength, [6:5] = burst length
}
```

### Example 4: Software Reset

```c
void psram_reset_example(void)
{
    // Perform software reset in current mode
    int ret = bflb_psram_softwarereset(&psram_cfg, psram_cfg.ctrl_mode);
    if (ret == 0) {
        // PSRAM reset successfully
    }

    // After reset, PSRAM is in SPI mode
    psram_cfg.ctrl_mode = PSRAM_SPI_CTRL_MODE;
}
```

---

## PSRAM Configuration Register Bits

The PSRAM configuration register is 8 bits wide, accessed via `bflb_psram_readreg()` / `bflb_psram_writereg()`.

| Bits | Field | Description |
|------|-------|-------------|
| 1:0 | **Drive Strength** | `00` = 50Ω, `01` = 100Ω, `10` = 200Ω |
| 6:5 | **Burst Length** | `00` = 16 bytes, `01` = 32 bytes, `10` = 64 bytes, `11` = 512 bytes |

---

## SF_CTRL Register Reference

The PSRAM driver uses the SF_CTRL peripheral for low-level SPI/QPI command execution.

### Key SF_CTRL Registers

| Offset | Register | Description |
|--------|----------|-------------|
| `0x00` | `SF_CTRL_0` | Main control: clock inversion, read delay, AES settings |
| `0x04` | `SF_CTRL_1` | Status read, bus control, function select, enable |
| `0x08` | `SF_IF_SAHB_0` | SAHB interface: busy, trigger, byte counts, SPI mode, QPI enable |
| `0x0C` | `SF_IF_SAHB_1` | SAHB command buffer 0 |
| `0x10` | `SF_IF_SAHB_2` | SAHB command buffer 1 |
| `0x14` | `SF_IF_IAHB_0` | IAHB interface: byte counts, SPI mode, QPI enable |
| `0x18` | `SF_IF_IAHB_1` | IAHB command buffer 0 |
| `0x1C` | `SF_IF_IAHB_2` | IAHB command buffer 1 |
| `0x20` | `SF_IF_STATUS_0` | Interface status 0 |
| `0x24` | `SF_IF_STATUS_1` | Interface status 1 |
| `0x30` | `SF_IF_IO_DLY_0` | IO delay config: CS, CLK, DQS |
| `0x34` | `SF_IF_IO_DLY_1` | IO delay for IO0 |
| `0x38` | `SF_IF_IO_DLY_2` | IO delay for IO1 |
| `0x3C` | `SF_IF_IO_DLY_3` | IO delay for IO2 |
| `0x40` | `SF_IF_IO_DLY_4` | IO delay for IO3 |

### SF_CTRL_1 Key Bits

| Bit | Field | Description |
|-----|-------|-------------|
| 29 | `SF_CTRL_SF_IF_EN` | SF interface enable |
| 30 | `SF_CTRL_SF_AHB2SIF_EN` | AHB to SIF bridge enable |
| 31 | `SF_CTRL_SF_AHB2SRAM_EN` | AHB to SRAM enable (PSRAM access) |

### SF_IF_SAHB_0 Key Bits

| Bit | Field | Description |
|-----|-------|-------------|
| 0 | `SF_CTRL_SF_IF_BUSY` | Interface busy (RO) |
| 1 | `SF_CTRL_SF_IF_0_TRIG` | Trigger command execution |
| 11:2 | `SF_CTRL_SF_IF_0_DAT_BYTE` | Data byte count |
| 16:12 | `SF_CTRL_SF_IF_0_DMY_BYTE` | Dummy byte count |
| 19:17 | `SF_CTRL_SF_IF_0_ADR_BYTE` | Address byte count |
| 22:20 | `SF_CTRL_SF_IF_0_CMD_BYTE` | Command byte count |
| 23 | `SF_CTRL_SF_IF_0_DAT_RW` | Data direction (0=write, 1=read) |
| 27 | `SF_CTRL_SF_IF_0_CMD_EN` | Command phase enable |
| 28:30 | `SF_CTRL_SF_IF_0_SPI_MODE` | SPI mode select |
| 31 | `SF_CTRL_SF_IF_0_QPI_MODE_EN` | QPI mode enable |

---

## Data Flow

### Write Operation Flow

```
bflb_psram_write()
  ├── For each burst-aligned chunk:
  │   ├── arch_memcpy_fast() → SF_CTRL BUF
  │   ├── Build sf_ctrl_cmd_cfg_type (cmd, addr, len, mode)
  │   └── bflb_sf_ctrl_sendcmd()
  │       └── SF_CTRL hardware executes SPI/QPI command
  └── Return 0
```

### Read Operation Flow

```
bflb_psram_read()
  ├── For each burst-aligned chunk:
  │   ├── Build sf_ctrl_cmd_cfg_type (cmd, addr, len, dummy, mode)
  │   ├── bflb_sf_ctrl_sendcmd()
  │   ├── Poll SF_CTRL busy state (timeout check)
  │   └── arch_memcpy_fast() ← SF_CTRL BUF
  └── Return 0
```

---

## Important Notes

1. **TCM Placement:** All PSRAM functions are placed in TCM (`ATTR_TCM_SECTION`) for fast execution.
2. **WEAK Functions:** All functions are `__WEAK`, allowing platform-specific overrides.
3. **Burst Alignment:** Read/write operations are automatically broken into burst-aligned chunks based on the configured `burst_length`.
4. **QPI Mode:** When in QPI mode, register read/write, reset, and burst toggle commands all use 4-line command/address/data phases.
5. **Cache Integration:** `bflb_psram_cache_write_set()` configures the L1C cache for 32-byte cache line reads from PSRAM via the IDBus.
6. **SF_CTRL Buffer:** The SF_CTRL buffer (`BFLB_SF_CTRL_BASE`) at `0x2000B000` is used as a data buffer — write operations must copy data into it before sending commands, and read data must be copied out after commands complete.
7. **BL702L:** The BL702L has an additional `burst_toggle_en` field and `bflb_sf_ctrl_burst_toggle_set()` support not present on BL616/BL618.
