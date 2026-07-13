# DPI API Reference (BL616/BL618)

> **Source:** `bouffalo_sdk/drivers/lhal/include/bflb_dpi.h`  
> **Implementation:** `bouffalo_sdk/drivers/lhal/src/bflb_dpi.c`  
> **Register Headers:** `hardware/mm_misc_reg.h`, `hardware/dvp_tsrc_reg.h`  

## Overview

The DPI (Display Parallel Interface) module is used to drive LCD displays with RGB/MIPI-DPI interfaces. It outputs pixel data from a framebuffer to the display panel via parallel data lines, supporting multiple color formats and timing configurations.

This module internally contains the DTSRC (Data Transport Source) subsystem, which reads framebuffer data over the AXI bus and outputs it according to DPI timing. It supports framebuffer switching (double buffering), test pattern output, and OSD (On-Screen Display) overlay.

> **Note:** The DPI module is only supported on the BL618DG chip.

## Base Address

| Subsystem | Base Address | Description |
|--------|-------------|------|
| MM_MISC (display config) | `dev->reg_base` | DPI timing, interface config, Y2R/R2Y color conversion |
| DTSRC (data transport) | `0x20045000` | Framebuffer read, pixel output, test patterns |

---

## Macro Definitions

### Input Selection (DPI_INPUT_SEL)

| Macro | Value | Description |
|----|---|------|
| `DPI_INPUT_SEL_TEST_PATTERN_WITHOUT_OSD` | 0 | Test pattern input (no OSD) |
| `DPI_INPUT_SEL_TEST_PATTERN_WITH_OSD` | 1 | Test pattern input (with OSD) |
| `DPI_INPUT_SEL_FRAMEBUFFER_WITHOUT_OSD` | 2 | Framebuffer input (no OSD), RGB format only |
| `DPI_INPUT_SEL_FRAMEBUFFER_WITH_OSD` | 3 | Framebuffer input (with OSD), supports RGB and YUV formats |

### Interface Color Coding (DPI_INTERFACE)

| Macro | Value | Description |
|----|---|------|
| `DPI_INTERFACE_24_PIN` | 0 | 24-pin interface (D0–D23) |
| `DPI_INTERFACE_18_PIN_MODE_1` | 1 | 18-pin interface Mode 1 (D0–D17) |
| `DPI_INTERFACE_18_PIN_MODE_2` | 2 | 18-pin interface Mode 2 (D0–D5, D8–D13, D16–D21) |
| `DPI_INTERFACE_16_PIN_MODE_1` | 3 | 16-pin interface Mode 1 (D0–D15) |
| `DPI_INTERFACE_16_PIN_MODE_2` | 4 | 16-pin interface Mode 2 (D0–D4, D8–D13, D16–D20) |
| `DPI_INTERFACE_16_PIN_MODE_3` | 5 | 16-pin interface Mode 3 (D1–D5, D8–D13, D17–D21) |

### Test Pattern Colors (DPI_TEST)

| Macro | Value | Description |
|----|---|------|
| `DPI_TEST_PATTERN_NULL` | 0 | No test pattern |
| `DPI_TEST_PATTERN_BLACK` | 1 | Black |
| `DPI_TEST_PATTERN_RED` | 2 | Red |
| `DPI_TEST_PATTERN_GREE` | 3 | Green |
| `DPI_TEST_PATTERN_YELLOW` | 4 | Yellow |

### Data Formats (DPI_DATA)

| Macro | Value | Description |
|----|---|------|
| `DPI_DATA_FORMAT_YUYV` | 0 | YUYV interleaved [31:24]=V, [23:16]=Y, [15:8]=U, [7:0]=Y |
| `DPI_DATA_FORMAT_RGB888` | 1 | 24-bit RGB [31:24]=B, [23:16]=R, [15:8]=G, [7:0]=B |
| `DPI_DATA_FORMAT_RGB565` | 2 | 16-bit RGB565 |
| `DPI_DATA_FORMAT_NRGB8888` | 3 | 32-bit NRGB8888 [31:24]=N, [23:16]=R, [15:8]=G, [7:0]=B |
| `DPI_DATA_FORMAT_Y_UV_PLANAR` | 4 | Y/UV planar separated format (Y and UV stored independently) |
| `DPI_DATA_FORMAT_UYVY` | 5 | UYVY interleaved [31:24]=Y, [23:16]=V, [15:8]=Y, [7:0]=U |
| `DPI_DATA_FORMAT_BGR888` | 6 | 24-bit BGR [31:24]=R, [23:16]=B, [15:8]=G, [7:0]=R |
| `DPI_DATA_FORMAT_BGR565` | 7 | 16-bit BGR565 |
| `DPI_DATA_FORMAT_NBGR8888` | 8 | 32-bit NBGR8888 |
| `DPI_DATA_FORMAT_TEST_PATTERN` | 10 | Test pattern format |

### YUV420 UV Valid Lines (DPI_YUV420)

| Macro | Value | Description |
|----|---|------|
| `DPI_YUV420_UV_VALID_LINE_EVEN` | 0 | UV valid on even lines (0/2/4/6/8...) |
| `DPI_YUV420_UV_VALID_LINE_ODD` | 1 | UV valid on odd lines (1/3/5/7/9...) |

### Burst Transfer Length (DPI_BURST)

| Macro | Value | Description |
|----|---|------|
| `DPI_BURST_INCR1` | 0 | Burst length 1 |
| `DPI_BURST_INCR4` | 1 | Burst length 4 |
| `DPI_BURST_INCR8` | 2 | Burst length 8 |
| `DPI_BURST_INCR16` | 3 | Burst length 16 |
| `DPI_BURST_INCR32` | 5 | Burst length 32 |
| `DPI_BURST_INCR64` | 6 | Burst length 64 |

### Feature Control Commands (DPI_CMD)

| Macro | Value | Description |
|----|---|------|
| `DPI_CMD_SET_YUV420_UV_VALID_LINE` | 0x01 | Set YUV420 UV valid line |
| `DPI_CMD_SET_BURST` | 0x02 | Set AXI burst transfer length |

---

## Data Structures

### bflb_dpi_config_s

DPI configuration structure.

```c
struct bflb_dpi_config_s {
    uint16_t width;               // Active pixel width
    uint16_t height;              // Active pixel height
    uint8_t hsw;                  // Horizontal sync width
    uint16_t hbp;                 // Horizontal back porch
    uint8_t hfp;                  // Horizontal front porch
    uint8_t vsw;                  // Vertical sync width
    uint16_t vbp;                 // Vertical back porch
    uint8_t vfp;                  // Vertical front porch
    uint8_t interface;            // Interface color coding, use DPI_INTERFACE macros
    uint8_t input_sel;            // Input selection, use DPI_INPUT_SEL macros
    uint8_t test_pattern;         // Test pattern color, use DPI_TEST macros
    uint8_t data_format;          // Data format, use DPI_DATA macros
    uint32_t framebuffer_addr;    // Framebuffer start address (Y framebuffer address in Y_UV_PLANAR mode)
    uint32_t uv_framebuffer_addr; // UV framebuffer start address (Y_UV_PLANAR mode only)
};
```

---

## LHAL API Functions

### bflb_dpi_init

Initialize the DPI interface, configure timing, data format, and input source.

```c
void bflb_dpi_init(struct bflb_device_s *dev, const struct bflb_dpi_config_s *config);
```

**Parameters:**

| Parameter | Type | Description |
|------|------|------|
| `dev` | `struct bflb_device_s *` | Device handle |
| `config` | `const struct bflb_dpi_config_s *` | Pointer to DPI configuration structure |

---

### bflb_dpi_enable

Enable DPI output.

```c
void bflb_dpi_enable(struct bflb_device_s *dev);
```

---

### bflb_dpi_disable

Disable DPI output.

```c
void bflb_dpi_disable(struct bflb_device_s *dev);
```

---

### bflb_dpi_framebuffer_switch

Switch framebuffer address (double buffering swap).

```c
void bflb_dpi_framebuffer_switch(struct bflb_device_s *dev, uint32_t addr);
```

**Parameters:**

| Parameter | Type | Description |
|------|------|------|
| `dev` | `struct bflb_device_s *` | Device handle |
| `addr` | `uint32_t` | New framebuffer start address |

---

### bflb_dpi_framebuffer_planar_switch

Switch Y and UV framebuffer addresses (`DPI_DATA_FORMAT_Y_UV_PLANAR` mode only).

```c
void bflb_dpi_framebuffer_planar_switch(struct bflb_device_s *dev, uint32_t y_addr, uint32_t uv_addr);
```

**Parameters:**

| Parameter | Type | Description |
|------|------|------|
| `dev` | `struct bflb_device_s *` | Device handle |
| `y_addr` | `uint32_t` | New Y framebuffer start address |
| `uv_addr` | `uint32_t` | New UV framebuffer start address |

---

### bflb_dpi_get_framebuffer_using

Get the framebuffer address currently in use.

```c
uint32_t bflb_dpi_get_framebuffer_using(struct bflb_device_s *dev);
```

**Returns:** Current framebuffer start address.

---

### bflb_dpi_set_test_pattern_custom

Set custom test pattern color parameters for DPI.

```c
void bflb_dpi_set_test_pattern_custom(struct bflb_device_s *dev, uint16_t max, uint16_t value, uint8_t step);
```

**Parameters:**

| Parameter | Type | Description |
|------|------|------|
| `dev` | `struct bflb_device_s *` | Device handle |
| `max` | `uint16_t` | Maximum color value |
| `value` | `uint16_t` | Starting color value |
| `step` | `uint8_t` | Color step increment |

---

### bflb_dpi_feature_control

DPI feature control interface.

```c
int bflb_dpi_feature_control(struct bflb_device_s *dev, int cmd, size_t arg);
```

**Parameters:**

| Parameter | Type | Description |
|------|------|------|
| `dev` | `struct bflb_device_s *` | Device handle |
| `cmd` | `int` | Feature command, use DPI_CMD macros |
| `arg` | `size_t` | Command argument |

**Returns:** 0 on success, `-EPERM` on failure.

---

## Usage Examples

### Example 1: Basic RGB888 DPI Display

```c
#include "bflb_dpi.h"

#define LCD_WIDTH  480
#define LCD_HEIGHT 272

static uint32_t framebuffer[LCD_WIDTH * LCD_HEIGHT] __attribute__((aligned(16)));
static uint32_t framebuffer_back[LCD_WIDTH * LCD_HEIGHT] __attribute__((aligned(16)));

void dpi_lcd_example(void)
{
    struct bflb_device_s *dpi;

    dpi = bflb_device_get_by_name("dpi");

    struct bflb_dpi_config_s config = {
        .width = LCD_WIDTH,
        .height = LCD_HEIGHT,
        .hsw = 1,          // Horizontal sync width
        .hbp = 40,         // Horizontal back porch
        .hfp = 5,          // Horizontal front porch
        .vsw = 1,          // Vertical sync width
        .vbp = 8,          // Vertical back porch
        .vfp = 8,          // Vertical front porch
        .interface = DPI_INTERFACE_24_PIN,
        .input_sel = DPI_INPUT_SEL_FRAMEBUFFER_WITHOUT_OSD,
        .test_pattern = DPI_TEST_PATTERN_NULL,
        .data_format = DPI_DATA_FORMAT_NRGB8888,
        .framebuffer_addr = (uint32_t)framebuffer,
        .uv_framebuffer_addr = 0,
    };

    bflb_dpi_init(dpi, &config);
    bflb_dpi_enable(dpi);

    // Fill framebuffer with red
    for (int i = 0; i < LCD_WIDTH * LCD_HEIGHT; i++) {
        framebuffer[i] = 0x00FF0000;  // NRGB8888: N=0, R=0xFF, G=0, B=0
    }
}
```

### Example 2: Double Buffer Switching Display

```c
void dpi_double_buffer_example(void)
{
    struct bflb_device_s *dpi = bflb_device_get_by_name("dpi");

    // ... initialize DPI config ...

    // Fill back buffer first
    for (int i = 0; i < LCD_WIDTH * LCD_HEIGHT; i++) {
        framebuffer_back[i] = 0x0000FF00;  // Green
    }

    // Switch to back buffer (seamless switch)
    bflb_dpi_framebuffer_switch(dpi, (uint32_t)framebuffer_back);
}
```

### Example 3: Test Pattern Output

```c
void dpi_test_pattern_example(void)
{
    struct bflb_device_s *dpi = bflb_device_get_by_name("dpi");

    struct bflb_dpi_config_s config = {
        .width = 480,
        .height = 272,
        .hsw = 1,
        .hbp = 40,
        .hfp = 5,
        .vsw = 1,
        .vbp = 8,
        .vfp = 8,
        .interface = DPI_INTERFACE_24_PIN,
        .input_sel = DPI_INPUT_SEL_TEST_PATTERN_WITHOUT_OSD,
        .test_pattern = DPI_TEST_PATTERN_RED,
        .data_format = DPI_DATA_FORMAT_TEST_PATTERN,
        .framebuffer_addr = 0,
        .uv_framebuffer_addr = 0,
    };

    bflb_dpi_init(dpi, &config);
    bflb_dpi_enable(dpi);
}
```

### Example 4: Custom Test Pattern

```c
void dpi_custom_test_pattern_example(void)
{
    struct bflb_device_s *dpi = bflb_device_get_by_name("dpi");

    struct bflb_dpi_config_s config = {
        .width = 480,
        .height = 272,
        .hsw = 1,
        .hbp = 40,
        .hfp = 5,
        .vsw = 1,
        .vbp = 8,
        .vfp = 8,
        .interface = DPI_INTERFACE_24_PIN,
        .input_sel = DPI_INPUT_SEL_TEST_PATTERN_WITHOUT_OSD,
        .test_pattern = DPI_TEST_PATTERN_NULL,
        .data_format = DPI_DATA_FORMAT_TEST_PATTERN,
        .framebuffer_addr = 0,
        .uv_framebuffer_addr = 0,
    };

    bflb_dpi_init(dpi, &config);

    // Set custom gradient color: max 0xFFFF, start value 0, step 4
    bflb_dpi_set_test_pattern_custom(dpi, 0xFFFF, 0, 4);

    bflb_dpi_enable(dpi);
}
```

### Example 5: Y_UV_PLANAR Format + AXI Burst Config

```c
void dpi_yuv_planar_example(void)
{
    struct bflb_device_s *dpi = bflb_device_get_by_name("dpi");

    struct bflb_dpi_config_s config = {
        .width = 480,
        .height = 272,
        .hsw = 1,
        .hbp = 40,
        .hfp = 5,
        .vsw = 1,
        .vbp = 8,
        .vfp = 8,
        .interface = DPI_INTERFACE_24_PIN,
        .input_sel = DPI_INPUT_SEL_FRAMEBUFFER_WITHOUT_OSD,
        .data_format = DPI_DATA_FORMAT_Y_UV_PLANAR,
        .framebuffer_addr = (uint32_t)y_buffer,
        .uv_framebuffer_addr = (uint32_t)uv_buffer,
    };

    bflb_dpi_init(dpi, &config);

    // Set AXI burst length to 16
    bflb_dpi_feature_control(dpi, DPI_CMD_SET_BURST, DPI_BURST_INCR16);

    // Set YUV420 UV valid on odd lines
    bflb_dpi_feature_control(dpi, DPI_CMD_SET_YUV420_UV_VALID_LINE,
                             DPI_YUV420_UV_VALID_LINE_ODD);

    bflb_dpi_enable(dpi);

    // Switch Y/UV buffers
    bflb_dpi_framebuffer_planar_switch(dpi,
                                       (uint32_t)y_buffer_back,
                                       (uint32_t)uv_buffer_back);
}
```

---

## Register Information

The DPI module involves two register groups.

### MM_MISC Registers (Display Configuration)

| Register | Offset | Description |
|--------|------|------|
| `MM_MISC_DISP_CONFIG` | `0x300` | Display config (includes DPI enable and interface selection) |
| `MM_MISC_DISP_DPI_CONFIG` | `0x304` | DPI timing configuration |
| `MM_MISC_DVP_MUX_SEL_REG2` | `0x14` | DVP mux selection (includes MUXO and OSD selection) |
| `MM_MISC_DISP_Y2R_CONFIG_0–7` | `0x200–0x21C` | YUV→RGB color space conversion matrix |
| `MM_MISC_DISP_R2Y_CONFIG_0–7` | `0x240–0x25C` | RGB→YUV color space conversion matrix |

#### DISP_CONFIG Register (Offset 0x300)

| Bit | Field | Description |
|----|------|------|
| 1 | `RG_DISP_DPI_EN` | DPI enable (1=enable) |
| 4–6 | `RG_DISP_DPI_ICC` | DPI interface color coding selection |

#### DISP_DPI_CONFIG Register (Offset 0x304)

| Bit | Field | Description |
|----|------|------|
| 0–7 | `RG_DISP_DPI_HS_W` | Horizontal sync width (pixel clock) |
| 8–15 | `RG_DISP_DPI_HFP_W` | Horizontal front porch width (pixel clock) |
| 16–23 | `RG_DISP_DPI_VS_W` | Vertical sync width (line count) |
| 24–31 | `RG_DISP_DPI_VFP_W` | Vertical front porch width (line count) |

> **Note:** Horizontal back porch HBP and vertical back porch VBP are implicitly calculated from DTSRC's `FRAME_SIZE_H`/`FRAME_SIZE_V`:  
> `BLANK_H = HSW + HBP + HFP`  
> `BLANK_V = VSW + VBP + VFP`

#### DVP_MUX_SEL_REG2 Register (Offset 0x14)

| Bit | Field | Description |
|----|------|------|
| 0–1 | `RG_DISP_OSD_SEL` | OSD source selection |
| 4–5 | `RG_DISP_MUXO_SEL` | Display MUXO source selection (2=test pattern/dtsrc, 1=OSD) |

### DTSRC Registers (Base: 0x20045000)

| Register | Offset | Description |
|--------|------|------|
| `DVP_TSRC_CONFIG` | `0x00` | DTSRC main configuration register |
| `DVP_TSRC_FRAME_SIZE_H` | `0x04` | Horizontal frame size (total width + blank width) |
| `DVP_TSRC_FRAME_SIZE_V` | `0x08` | Vertical frame size (total height + blank height) |
| `DVP_TSRC_AXI2DVP_SETTING` | `0x0C` | AXI→DVP conversion settings |
| `DVP_TSRC_PIX_DATA_RANGE` | `0x10` | Test pattern pixel data range |
| `DVP_TSRC_PIX_DATA_STEP` | `0x14` | Test pattern pixel step |
| `DVP_TSRC_AXI2DVP_START_ADDR_BY` | `0x2C` | AXI start address BY |
| `DVP_TSRC_AXI2DVP_SWAP_ADDR_BY` | `0x30` | AXI swap address BY |
| `DVP_TSRC_AXI2DVP_PREFETCH` | `0x34` | Prefetch line count setting |
| `DVP_TSRC_AXI2DVP_START_ADDR_UV` | `0x40` | AXI start address UV |
| `DVP_TSRC_AXI2DVP_SWAP_ADDR_UV` | `0x44` | AXI swap address UV |
| `DVP_TSRC_AXI_PUSH_MODE` | `0x60` | Push mode control |

#### DVP_TSRC_CONFIG Register (Offset 0x00)

| Bit | Field | Description |
|----|------|------|
| 0 | `CR_ENABLE` | DTSRC enable |
| 1 | `CR_AXI_EN` | AXI read enable |
| 3 | `CR_AXI_PUSH_MODE` | Push mode |
| 7 | `CR_AXI_SWAP_MODE` | Swap mode enable |
| 8–11 | `CR_AXI_SWAP_IDX_SEL` | Swap index selection |
| 12 | `CR_AXI_SWAP_IDX_SWM` | Swap index write mode |
| 13 | `CR_AXI_SWAP_IDX_SWV` | Swap index read/write status |
| 16–18 | `CR_AXI_DVP_DATA_MODE` | AXI→DVP data mode |
| 20–21 | `CR_AXI_B0_SEL` | Byte 0 (B0) selection |
| 22–23 | `CR_AXI_B1_SEL` | Byte 1 (B1) selection |
| 24–25 | `CR_AXI_B2_SEL` | Byte 2 (B2) selection |

#### DVP_TSRC_FRAME_SIZE_H Register (Offset 0x04)

| Bit | Field | Description |
|----|------|------|
| 0–15 | Total width | `HSW + HBP + HFP + Width` (lower 16 bits) |
| 16–31 | `CR_BLANK_H` | Total horizontal blank width `HSW + HBP + HFP` |

#### DVP_TSRC_FRAME_SIZE_V Register (Offset 0x08)

| Bit | Field | Description |
|----|------|------|
| 0–15 | Total height | `VSW + VBP + VFP + Height` (lower 16 bits) |
| 16–31 | `CR_BLANK_V` | Total vertical blank width `VSW + VBP + VFP` |

#### DVP_TSRC_AXI2DVP_SETTING Register (Offset 0x0C)

| Bit | Field | Description |
|----|------|------|
| 0–2 | `CR_AXI_XLEN` | AXI burst length (0=1, 1=4, 2=8, 3=16, 5=32, 6=64) |
| 7 | `CR_AXI_422_SP_MODE` | YUV422 semi-planar mode |
| 8 | `CR_AXI_420_SP_MODE` | YUV420 semi-planar mode |
| 9 | `CR_AXI_420_UD_SEL` | YUV420 UV line selection (0=even lines, 1=odd lines) |
