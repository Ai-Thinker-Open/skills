# BL616/BL618 Display Interface Documentation

This document covers the four display interfaces available on BL616/BL618: **DPI**, **DSI**, **DBI**, and **OSD**.

---

## Table of Contents

1. [DPI (Display Pixel Interface)](#1-dpi-display-pixel-interface)
2. [DSI (Display Serial Interface)](#2-dsi-display-serial-interface)
3. [DBI (Display Bus Interface)](#3-dbi-display-bus-interface)
4. [OSD (On-Screen Display)](#4-osd-on-screen-display)

---

## 1. DPI (Display Pixel Interface)

DPI is a parallel display interface that outputs pixel data to external display panels (e.g., LCD panels with RGB interface).

### Header File
```c
#include "bflb_dpi.h"
```

### Key Definitions

#### Input Selection
| Macro | Description |
|-------|-------------|
| `DPI_INPUT_SEL_TEST_PATTERN_WITHOUT_OSD` | Test pattern, no OSD |
| `DPI_INPUT_SEL_TEST_PATTERN_WITH_OSD` | Test pattern with OSD overlay |
| `DPI_INPUT_SEL_FRAMEBUFFER_WITHOUT_OSD` | Framebuffer RGB data only |
| `DPI_INPUT_SEL_FRAMEBUFFER_WITH_OSD` | Framebuffer with OSD overlay (RGB + YUV supported) |

#### Interface Types
| Macro | Description |
|-------|-------------|
| `DPI_INTERFACE_24_PIN` | D0~D23 (full 24-bit) |
| `DPI_INTERFACE_18_PIN_MODE_1` | D0~D17 |
| `DPI_INTERFACE_18_PIN_MODE_2` | D0~D5, D8~D13, D16~D21 |
| `DPI_INTERFACE_16_PIN_MODE_1` | D0~D15 |
| `DPI_INTERFACE_16_PIN_MODE_2` | D0~D4, D8~D13, D16~D20 |
| `DPI_INTERFACE_16_PIN_MODE_3` | D1~D5, D8~D13, D17~D21 |

#### Data Formats
| Macro | Description |
|-------|-------------|
| `DPI_DATA_FORMAT_YUYV` | YUV422 packed |
| `DPI_DATA_FORMAT_RGB888` | RGB888 (B[31:24], R[23:16], G[15:8], B[7:0]) |
| `DPI_DATA_FORMAT_RGB565` | RGB565 |
| `DPI_DATA_FORMAT_NRGB8888` | NRGB8888 with alpha |
| `DPI_DATA_FORMAT_Y_UV_PLANAR` | Y and UV separate planes (for MJDEC output) |
| `DPI_DATA_FORMAT_UYVY` | UYVY packed |
| `DPI_DATA_FORMAT_BGR888` | BGR888 |
| `DPI_DATA_FORMAT_BGR565` | BGR565 |
| `DPI_DATA_FORMAT_TEST_PATTERN` | Test pattern mode |

### Configuration Structure
```c
struct bflb_dpi_config_s {
    uint16_t width;              // Active width
    uint16_t height;             // Active height
    uint8_t  hsw;                // Horizontal sync width
    uint16_t hbp;                // Horizontal back porch
    uint8_t  hfp;                // Horizontal front porch
    uint8_t  vsw;                // Vertical sync width
    uint16_t vbp;               // Vertical back porch
    uint8_t  vfp;               // Vertical front porch
    uint8_t  interface;          // Interface type (DPI_INTERFACE_*)
    uint8_t  input_sel;          // Input selection (DPI_INPUT_SEL_*)
    uint8_t  test_pattern;       // Test pattern color (DPI_TEST_*)
    uint8_t  data_format;        // Data format (DPI_DATA_FORMAT_*)
    uint32_t framebuffer_addr;   // Framebuffer start address
    uint32_t uv_framebuffer_addr;// UV plane address (Y_UV_PLANAR only)
};
```

### API Functions

| Function | Description |
|----------|-------------|
| `bflb_dpi_init(dev, config)` | Initialize DPI with configuration |
| `bflb_dpi_enable(dev)` | Enable DPI output |
| `bflb_dpi_disable(dev)` | Disable DPI output |
| `bflb_dpi_framebuffer_switch(dev, addr)` | Switch to different framebuffer |
| `bflb_dpi_framebuffer_planar_switch(dev, y_addr, uv_addr)` | Switch Y/UV planes (Y_UV_PLANAR mode) |
| `bflb_dpi_get_framebuffer_using(dev)` | Get currently used framebuffer address |
| `bflb_dpi_set_test_pattern_custom(dev, max, value, step)` | Set custom test pattern |
| `bflb_dpi_feature_control(dev, cmd, arg)` | Feature control (YUV420 UV line, burst length) |

### Working Code Example

```c
#include "bflb_dpi.h"
#include "bflb_gpio.h"
#include "board.h"

#define LCD_WIDTH  800
#define LCD_HEIGHT 480

/* Framebuffers (placed in PSRAM for large buffer) */
ATTR_NOINIT_PSRAM_SECTION uint16_t framebuffer_1[LCD_WIDTH * LCD_HEIGHT];
ATTR_NOINIT_PSRAM_SECTION uint16_t framebuffer_2[LCD_WIDTH * LCD_HEIGHT];

static struct bflb_device_s *dpi;

int dpi_example(void)
{
    struct bflb_dpi_config_s dpi_config = {
        .width  = LCD_WIDTH,
        .height = LCD_HEIGHT,
        .hsw    = 45,
        .hbp    = 45,
        .hfp    = 89,
        .vsw    = 7,
        .vbp    = 7,
        .vfp    = 5,
        .interface      = DPI_INTERFACE_24_PIN,
        .input_sel       = DPI_INPUT_SEL_FRAMEBUFFER_WITH_OSD,
        .test_pattern    = DPI_TEST_PATTERN_NULL,
        .data_format     = DPI_DATA_FORMAT_RGB565,
        .framebuffer_addr = (uint32_t)framebuffer_1,
    };

    /* Initialize board GPIOs for DPI */
    board_init();
    board_dpi_gpio_init();

    /* Get DPI device */
    dpi = bflb_device_get_by_name("dpi");
    if (dpi == NULL) {
        return -1;
    }

    /* Initialize and enable DPI */
    bflb_dpi_init(dpi, &dpi_config);
    bflb_dpi_enable(dpi);

    /* Framebuffer switching example */
    /* Clean cache before switching */
    bflb_l1c_dcache_clean_range(framebuffer_2, sizeof(framebuffer_2));
    bflb_dpi_framebuffer_switch(dpi, (uint32_t)framebuffer_2);

    return 0;
}
```

---

## 2. DSI (Display Serial Interface)

DSI is a MIPI-compliant serial interface for communicating with display panels using D-PHY physical layer.

### Header File
```c
#include "bflb_dsi.h"
```

### Key Definitions

#### Data Types
| Macro | Description |
|-------|-------------|
| `BFLB_DSI_DATA_YUV422` | YUV422 8-bit |
| `BFLB_DSI_DATA_RGB565` | RGB565 |
| `BFLB_DSI_DATA_RGB666` | RGB666 (loosely packed) |
| `BFLB_DSI_DATA_RGB888` | RGB888 |

#### Lane Configuration
| Macro | Description |
|-------|-------------|
| `BFLB_DSI_LANES_1` | 1 data lane |
| `BFLB_DSI_LANES_2` | 2 data lanes |
| `BFLB_DSI_LANES_4` | 4 data lanes |

#### Lane Order
| Macro | Description |
|-------|-------------|
| `BFLB_DSI_LANE_ORDER_3210` | Lane 3, 2, 1, 0 |
| `BFLB_DSI_LANE_ORDER_2130` | Lane 2, 1, 3, 0 |
| `BFLB_DSI_LANE_ORDER_1320` | Lane 1, 3, 2, 0 |
| `BFLB_DSI_LANE_ORDER_3120` | Lane 3, 1, 2, 0 |

#### Lane States
| Macro | Description |
|-------|-------------|
| `BFLB_DSI_LANE_STATE_NORMAL` | Normal operation |
| `BFLB_DSI_LANE_STATE_STOP` | Stop state |
| `BFLB_DSI_LANE_STATE_BRIDGE` | Bridge changing |
| `BFLB_DSI_LANE_STATE_ULP` | Ultra-low power |
| `BFLB_DSI_LANE_STATE_HS` | High speed |

### Configuration Structures

```c
typedef struct bflb_dsi_config_s {
    uint8_t data_type;    // MIPI-DSI data type (BFLB_DSI_DATA_*)
    uint8_t lane_num;     // Lane number (BFLB_DSI_LANES_*)
    uint8_t lane_order;   // Lane order (BFLB_DSI_LANE_ORDER_*)
    uint8_t sync_type;    // HS sync type (event or pulse mode)
    uint8_t virtual_chan; // Virtual channel ID (0-3)
    uint8_t vfp;          // Vertical front porch
    uint8_t vsa;         // Vertical sync active
} bflb_dsi_config_t;

typedef struct bflb_dsi_dphy_config_s {
    uint8_t time_clk_zero;      // Clock lane HS-ZERO
    uint8_t time_clk_trail;    // Clock lane HS-TRAIL
    uint8_t time_clk_exit;      // Clock lane HS-EXIT
    uint8_t time_data_zero;     // Data lane HS-ZERO
    uint8_t time_data_trail;   // Data lane HS-TRAIL
    uint8_t time_data_exit;     // Data lane HS-EXIT
    uint8_t time_data_prepare;  // Data lane HS-PREPARE
    uint8_t time_ta_go;         // Turnaround GO
    uint8_t time_ta_get;        // Turnaround GET
    uint8_t time_req_ready;    // Request to ready
    uint8_t time_lpx;           // Low-power transmission
    uint32_t time_wakeup;      // Wakeup timing (clock cycles)
} bflb_dsi_dphy_config_t;

typedef struct bflb_dsi_lpdt_msg_s {
    uint8_t data_type;      // DCS or generic packet data type
    uint8_t virtual_chan;   // Virtual channel ID (0-3)
    const uint8_t *tx_buf; // Transmit buffer
    uint16_t tx_len;        // TX length (payload bytes for long packets)
    uint8_t *rx_buf;        // Receive buffer
    uint16_t rx_len;        // RX buffer size / actual received length
} bflb_dsi_lpdt_msg_t;
```

### API Functions

#### Initialization/Deinitialization
| Function | Description |
|----------|-------------|
| `bflb_dsi_init(dev, cfg)` | Initialize DSI controller |
| `bflb_dsi_deinit(dev)` | Deinitialize DSI controller |

#### PHY Control
| Function | Description |
|----------|-------------|
| `bflb_dsi_phy_reset(dev)` | Reset DSI PHY |
| `bflb_dsi_phy_enable(dev)` | Enable DSI PHY |
| `bflb_dsi_phy_config(dev, phy)` | Configure PHY timing |
| `bflb_dsi_phy_enable_lanes(dev, mask)` | Enable DSI lanes |
| `bflb_dsi_phy_disable_lanes(dev, mask)` | Disable DSI lanes |
| `bflb_dsi_phy_set_clock_lane(dev, ops)` | Control clock lane (ULP enter/exit, HS request) |
| `bflb_dsi_phy_get_lanes_state(dev, lane, state)` | Get lane state |
| `bflb_dsi_phy_hs_mode_start(dev)` | Start high-speed mode |
| `bflb_dsi_phy_hs_mode_stop(dev)` | Stop high-speed mode |

#### LPDT (Low-Power Data Transmission) Packets
| Function | Description |
|----------|-------------|
| `bflb_dsi_lpdt_send_short_packet(dev, msg)` | Send short packet (0-2 bytes) |
| `bflb_dsi_lpdt_send_long_packet(dev, msg)` | Send long packet (variable length) |
| `bflb_dsi_lpdt_recv(dev, msg)` | Receive LPDT packet |

#### FIFO Operations
| Function | Description |
|----------|-------------|
| `bflb_dsi_read_fifo(dev, data, maxlen)` | Read from RX FIFO |
| `bflb_dsi_full_fill_fifo(dev, data, len)` | Fill TX FIFO completely |
| `bflb_dsi_feed_fifo(dev, data, len)` | Feed data to TX FIFO (partial fill) |
| `bflb_dsi_get_tx_fifo_count(dev)` | Get TX FIFO count |
| `bflb_dsi_get_rx_fifo_count(dev)` | Get RX FIFO count |

#### Interrupts
| Function | Description |
|----------|-------------|
| `bflb_dsi_int_mask(dev, mask, enable)` | Mask/unmask interrupts |
| `bflb_dsi_int_clear(dev, flag)` | Clear interrupt flags |
| `bflb_dsi_int_enable(dev, type)` | Enable interrupts |
| `bflb_dsi_int_get(dev)` | Get interrupt status |

### Working Code Example

```c
#include "bflb_dsi.h"

static struct bflb_device_s *dsi;

int dsi_example(void)
{
    bflb_dsi_config_t dsi_config = {
        .data_type   = BFLB_DSI_DATA_RGB888,
        .lane_num    = BFLB_DSI_LANES_4,
        .lane_order  = BFLB_DSI_LANE_ORDER_3210,
        .sync_type   = BFLB_DSI_HS_SYNC_EVENT_MODE,
        .virtual_chan = 0,
        .vfp         = 10,
        .vsa         = 10,
    };

    bflb_dsi_dphy_config_t phy_config = {
        .time_clk_zero     = 0x3C,
        .time_clk_trail    = 0x04,
        .time_clk_exit     = 0x07,
        .time_data_zero    = 0x2A,
        .time_data_trail   = 0x04,
        .time_data_exit    = 0x07,
        .time_data_prepare = 0x06,
        .time_ta_go        = 0x04,
        .time_ta_get       = 0x05,
        .time_req_ready    = 0x01,
        .time_lpx          = 0x06,
        .time_wakeup       = 0xFF,
    };

    /* Get DSI device */
    dsi = bflb_device_get_by_name("dsi");
    if (dsi == NULL) {
        return -1;
    }

    /* Initialize DSI */
    bflb_dsi_init(dsi, &dsi_config);

    /* Configure PHY and enable lanes */
    bflb_dsi_phy_config(dsi, &phy_config);
    bflb_dsi_phy_reset(dsi);
    bflb_dsi_phy_enable(dsi);
    bflb_dsi_phy_enable_lanes(dsi, BFLB_DSI_LANE_DATA0 | BFLB_DSI_LANE_DATA1 |
                                     BFLB_DSI_LANE_DATA2 | BFLB_DSI_LANE_DATA3 |
                                     BFLB_DSI_LANE_CLOCK);

    /* Start high-speed transmission */
    bflb_dsi_phy_hs_mode_start(dsi);

    /* Send DCS command to display */
    bflb_dsi_lpdt_msg_t msg = {
        .data_type   = 0x05,  // DCS command: Exit sleep mode
        .virtual_chan = 0,
        .tx_buf      = NULL,
        .tx_len      = 0,
        .rx_buf      = NULL,
        .rx_len      = 0,
    };
    bflb_dsi_lpdt_send_short_packet(dsi, &msg);

    /* Send frame data via DSI */

    /* Stop high-speed and cleanup */
    bflb_dsi_phy_hs_mode_stop(dsi);
    bflb_dsi_deinit(dsi);

    return 0;
}
```

---

## 3. DBI (Display Bus Interface)

DBI is a parallel display interface that supports MIPI-DBI Type B and Type C protocols. It's used for LCD panels with parallel RGB interface.

### Header File
```c
#include "bflb_dbi.h"
```

### Key Definitions

#### Working Modes
| Macro | Description |
|-------|-------------|
| `DBI_MODE_TYPE_B` | MIPI-DBI Type B (8-wire data mode) |
| `DBI_MODE_TYPE_C_4_WIRE` | MIPI-DBI Type C 4-wire mode |
| `DBI_MODE_TYPE_C_3_WIRE` | MIPI-DBI Type C 3-wire mode |
| `DBI_MODE_EX_QSPI` | Extended QSPI mode (BL616/BL618 only) |

#### Pixel Input Formats (FIFO input)
| Macro | Description |
|-------|-------------|
| `DBI_PIXEL_INPUT_FORMAT_NBGR_8888` | 32bpp, memory: [R][G][B][invalid] |
| `DBI_PIXEL_INPUT_FORMAT_NRGB_8888` | 32bpp, memory: [B][G][R][invalid] |
| `DBI_PIXEL_INPUT_FORMAT_BGRN_8888` | 32bpp, memory: [invalid][R][G][B] |
| `DBI_PIXEL_INPUT_FORMAT_RGBN_8888` | 32bpp, memory: [invalid][B][G][R] |
| `DBI_PIXEL_INPUT_FORMAT_BGR_888` | 24bpp, packed BGR |
| `DBI_PIXEL_INPUT_FORMAT_RGB_888` | 24bpp, packed RGB |
| `DBI_PIXEL_INPUT_FORMAT_BGR_565` | 16bpp BGR565 |
| `DBI_PIXEL_INPUT_FORMAT_RGB_565` | 16bpp RGB565 |
| `DBI_PIXEL_INPUT_FORMAT_YUYV` | 16bpp YUYV (YUV422 packed) |
| `DBI_PIXEL_INPUT_FORMAT_UYVY` | 16bpp UYVY |
| `DBI_PIXEL_INPUT_FORMAT_VYUY` | 16bpp VYUY |
| `DBI_PIXEL_INPUT_FORMAT_YVYU` | 16bpp YVYU |

#### Pixel Output Formats
| Macro | Description |
|-------|-------------|
| `DBI_PIXEL_OUTPUT_FORMAT_RGB_565` | 16bpp output |
| `DBI_PIXEL_OUTPUT_FORMAT_RGB_888` | 24bpp output (RGB666 compatible) |

#### Clock Modes
| Macro | Description |
|-------|-------------|
| `DBI_CLOCK_MODE_0` | CPOL=0, CPHA=0 |
| `DBI_CLOCK_MODE_1` | CPOL=0, CPHA=1 |
| `DBI_CLOCK_MODE_2` | CPOL=1, CPHA=0 |
| `DBI_CLOCK_MODE_3` | CPOL=1, CPHA=1 |

#### Interrupt Status
| Macro | Description |
|-------|-------------|
| `DBI_INTSTS_TC` | Transfer complete |
| `DBI_INTSTS_TX_FIFO` | TX FIFO threshold reached |
| `DBI_INTSTS_FIFO_ERR` | FIFO error |

### Configuration Structure
```c
struct bflb_dbi_config_s {
    uint8_t dbi_mode;           // Working mode (DBI_MODE_*)
    uint8_t pixel_input_format; // Input format (DBI_PIXEL_INPUT_FORMAT_*)
    uint8_t pixel_output_format;// Output format (DBI_PIXEL_OUTPUT_FORMAT_*)
    uint8_t clk_mode;           // Clock mode (DBI_CLOCK_MODE_*)
    uint32_t clk_freq_hz;       // Clock frequency in Hz
    uint8_t tx_fifo_threshold;  // TX FIFO threshold (< 16)
#if DBI_QSPI_SUPPORT
    uint8_t cmd_wire_mode;      // QSPI command phase wires
    uint8_t addr_wire_mode;     // QSPI address phase wires
    uint8_t data_wire_mode;     // QSPI data phase wires
#endif
};
```

### API Functions

| Function | Description |
|----------|-------------|
| `bflb_dbi_init(dev, config)` | Initialize DBI |
| `bflb_dbi_deinit(dev)` | Deinitialize DBI |
| `bflb_dbi_qspi_set_addr(dev, size, val)` | Set QSPI address (QSPI mode only) |
| `bflb_dbi_send_cmd_data(dev, cmd, len, buf)` | Send command with parameter data |
| `bflb_dbi_send_cmd_read_data(dev, cmd, len, buf)` | Send command and read response |
| `bflb_dbi_send_cmd_pixel(dev, cmd, cnt, buf)` | Send command with pixel data |
| `bflb_dbi_link_txdma(dev, enable)` | Enable/disable TX DMA |
| `bflb_dbi_txint_mask(dev, mask)` | Mask/unmask TX interrupt |
| `bflb_dbi_tcint_mask(dev, mask)` | Mask/unmask transfer complete interrupt |
| `bflb_dbi_errint_mask(dev, mask)` | Mask/unmask error interrupt |
| `bflb_dbi_get_intstatus(dev)` | Get interrupt status |
| `bflb_dbi_int_clear(dev, clear)` | Clear interrupts |
| `bflb_dbi_feature_control(dev, cmd, arg)` | Feature control |

### Working Code Example

```c
#include "bflb_dbi.h"
#include "lcd.h"

static struct bflb_device_s *dbi;

int dbi_example(void)
{
    struct bflb_dbi_config_s dbi_config = {
        .dbi_mode           = DBI_MODE_TYPE_C_4_WIRE,
        .pixel_input_format = DBI_PIXEL_INPUT_FORMAT_RGB565,
        .pixel_output_format = DBI_PIXEL_OUTPUT_FORMAT_RGB565,
        .clk_mode          = DBI_CLOCK_MODE_0,
        .clk_freq_hz       = 10000000,  // 10 MHz
        .tx_fifo_threshold = 8,
    };

    /* Get DBI device */
    dbi = bflb_device_get_by_name("dbi0");
    if (dbi == NULL) {
        return -1;
    }

    /* Initialize DBI */
    bflb_dbi_init(dbi, &dbi_config);

    /* Send LCD initialization commands */
    uint8_t display_on_cmd = 0x29;  // DCS command: Display ON
    bflb_dbi_send_cmd_data(dbi, display_on_cmd, 0, NULL);

    uint8_t pixel_format_cmd = 0x3A;  // DCS command: Pixel Format
    uint8_t pixel_format_data = 0x55; // 16bpp
    bflb_dbi_send_cmd_data(dbi, pixel_format_cmd, 1, &pixel_format_data);

    /* Send pixel data to LCD */
    uint16_t width = 480;
    uint16_t height = 320;
    uint16_t *pixel_data;  // Your pixel buffer

    /* Clean cache for DMA */
    bflb_l1c_dcache_clean_range(pixel_data, width * height * 2);

    /* Enable TX DMA for pixel transfer */
    bflb_dbi_link_txdma(dbi, true);

    /* Send pixel data via command */
    bflb_dbi_send_cmd_pixel(dbi, 0x2C, width * height, pixel_data);  // DCS Memory Write

    /* Or without DMA - direct pixel send */
    bflb_dbi_link_txdma(dbi, false);
    bflb_dbi_send_cmd_pixel(dbi, 0x2C, width * height, pixel_data);

    /* Cleanup */
    bflb_dbi_deinit(dbi);

    return 0;
}
```

---

## 4. OSD (On-Screen Display)

OSD provides hardware-accelerated layer blending and rectangle drawing for overlay graphics on top of the display output.

### Header File
```c
#include "bflb_osd.h"
```

### Key Definitions

#### Blend Color Formats
| Macro | Description |
|-------|-------------|
| `OSD_BLEND_FORMAT_ARGB8888` | ARGB 32-bit |
| `OSD_BLEND_FORMAT_AYUV8888` | AYUV 32-bit |
| `OSD_BLEND_FORMAT_ARGB4444` | ARGB 16-bit |
| `OSD_BLEND_FORMAT_AYUV4444` | AYUV 16-bit |
| `OSD_BLEND_FORMAT_ARGB1555` | ARGB 16-bit (1-bit alpha) |
| `OSD_BLEND_FORMAT_AYUV1555` | AYUV 16-bit (1-bit alpha) |
| `OSD_BLEND_FORMAT_RGB565` | RGB 16-bit |
| `OSD_BLEND_FORMAT_YUV655` | YUV 16-bit |
| `OSD_BLEND_FORMAT_A8_GLOBAL_RGB` | Alpha 8-bit + global RGB |
| `OSD_BLEND_FORMAT_A8_GLOBAL_YUV` | Alpha 8-bit + global YUV |
| `OSD_BLEND_FORMAT_ARGB_PALETTE_8BIT` | ARGB palette, 8-bit index |
| `OSD_BLEND_FORMAT_AYUV_PALETTE_8BIT` | AYUV palette, 8-bit index |
| `OSD_BLEND_FORMAT_ARGB_PALETTE_4BIT` | ARGB palette, 4-bit index |
| `OSD_BLEND_FORMAT_ARGB_PALETTE_2BIT` | ARGB palette, 2-bit index |
| `OSD_BLEND_FORMAT_ARGB_PALETTE_1BIT` | ARGB palette, 1-bit index |

#### Draw Layers (0-15)
Layers can be used for drawing rectangles:
- `OSD_DRAW_LAYER_0` through `OSD_DRAW_LAYER_15`

### Configuration Structures

```c
/* OSD Coordinate */
struct bflb_osd_coordinate_s {
    uint16_t start_x;  // Start X position
    uint16_t start_y;  // Start Y position
    uint16_t end_x;    // End X position (not included)
    uint16_t end_y;    // End Y position (not included)
};

/* OSD Blend Configuration */
struct bflb_osd_blend_config_s {
    uint8_t blend_format;       // Color format (OSD_BLEND_FORMAT_*)
    uint8_t order_a;            // Alpha channel order (0=LSB, 3=MSB)
    uint8_t order_rv;           // Red/V channel order
    uint8_t order_gy;           // Green/Y channel order
    uint8_t order_bu;           // Blue/U channel order
    struct bflb_osd_coordinate_s coor;  // Layer coordinates
    uint32_t layer_buffer_addr; // Layer buffer address
};

/* Blend Replace Configuration */
struct bflb_osd_blend_replace_s {
    bool replace_between;   // true: min <= value <= max, false: outside range
    uint8_t target_value;    // Replacement value
    uint8_t min_value;       // Minimum value
    uint8_t max_value;       // Maximum value
};

/* OSD Draw Rectangle Configuration */
struct bflb_osd_draw_config_s {
    bool is_solid;           // true: solid rectangle, false: hollow
    uint8_t border_thickness; // Border thickness (must be even)
    uint8_t color_y;         // Color Y component
    uint8_t color_u;         // Color U component
    uint8_t color_v;         // Color V component
    struct bflb_osd_coordinate_s coor;  // Rectangle coordinates
};
```

### API Functions

#### Blend Functions
| Function | Description |
|----------|-------------|
| `bflb_osd_blend_init(dev, config)` | Initialize OSD blend layer |
| `bflb_osd_blend_enable(dev)` | Enable blend layer |
| `bflb_osd_blend_disable(dev)` | Disable blend layer |
| `bflb_osd_blend_set_coordinate(dev, coor)` | Set layer position |
| `bflb_osd_blend_set_layer_buffer(dev, addr)` | Set layer buffer address |
| `bflb_osd_blend_get_layer_buffer(dev)` | Get current layer buffer address |
| `bflb_osd_blend_set_global_a(dev, enable, value)` | Set global alpha |
| `bflb_osd_blend_set_global_rgb_yuv(dev, en, r, g, b)` | Set global RGB/YUV color |
| `bflb_osd_blend_set_palette_color(dev, idx, val)` | Set palette entry |
| `bflb_osd_blend_replace_palette_index(dev, en, rep)` | Replace palette index |
| `bflb_osd_blend_replace_color_value(dev, en, rep_a, rep_rv, rep_gy, rep_bu)` | Replace color values |

#### Draw Functions
| Function | Description |
|----------|-------------|
| `bflb_osd_draw_init(dev, layer, config)` | Initialize draw layer |
| `bflb_osd_draw_enable(dev, layer)` | Enable draw layer |
| `bflb_osd_draw_disable(dev, layer)` | Disable draw layer |
| `bflb_osd_draw_set_coordinate(dev, layer, coor)` | Set rectangle coordinates |

#### Interrupt Functions
| Function | Description |
|----------|-------------|
| `bflb_osd_int_mask(dev, mask)` | Mask/unmask interrupt |
| `bflb_osd_get_intstatus(dev)` | Get interrupt status |
| `bflb_osd_int_clear(dev)` | Clear interrupt |
| `bflb_osd_feature_control(dev, cmd, arg)` | Feature control |

### Working Code Example

```c
#include "bflb_osd.h"
#include "bflb_dpi.h"

#define LCD_WIDTH  800
#define LCD_HEIGHT 480

static struct bflb_device_s *osd0;
static struct bflb_device_s *osd1;

/* OSD layer buffers */
ATTR_NOINIT_PSRAM_SECTION uint16_t osd0_layer_buffer[80 * 96];  // RGB565
ATTR_NOINIT_PSRAM_SECTION uint8_t  osd1_layer_buffer[96 * 96];   // Palette index

int osd_example(void)
{
    /* OSD0 blend configuration - RGB565 image */
    static struct bflb_osd_blend_config_s osd0_blend_config = {
        .blend_format = OSD_BLEND_FORMAT_RGB565,
        .order_a = 3,    // Alpha at MSB
        .order_rv = 2,
        .order_gy = 1,
        .order_bu = 0,
        .coor = {
            .start_x = 0,
            .start_y = 0,
            .end_x = 80,
            .end_y = 96,
        },
        .layer_buffer_addr = (uint32_t)osd0_layer_buffer,
    };

    /* OSD1 blend configuration - Palette indexed image */
    static struct bflb_osd_blend_config_s osd1_blend_config = {
        .blend_format = OSD_BLEND_FORMAT_ARGB_PALETTE_8BIT,
        .order_a = 0,
        .order_rv = 1,
        .order_gy = 2,
        .order_bu = 3,
        .coor = {
            .start_x = 100,
            .start_y = 100,
            .end_x = 196,
            .end_y = 196,
        },
        .layer_buffer_addr = (uint32_t)osd1_layer_buffer,
    };

    /* Draw rectangle configuration */
    static struct bflb_osd_draw_config_s draw_config = {
        .is_solid = false,
        .border_thickness = 2,
        .color_y = (OSD_DRAW_YUV_COLOR_BLUE >> 16) & 0xff,
        .color_u = (OSD_DRAW_YUV_COLOR_BLUE >> 8) & 0xff,
        .color_v = OSD_DRAW_YUV_COLOR_BLUE & 0xff,
        .coor = {
            .start_x = 200,
            .start_y = 100,
            .end_x = 499,
            .end_y = 299,
        },
    };

    /* Get OSD devices */
    osd0 = bflb_device_get_by_name("osd0");
    osd1 = bflb_device_get_by_name("osd1");
    if (osd0 == NULL || osd1 == NULL) {
        return -1;
    }

    /* Setup OSD0 - RGB565 blend layer */
    bflb_osd_blend_init(osd0, &osd0_blend_config);
    bflb_osd_blend_set_global_a(osd0, true, 0x7F);  // 50% alpha
    bflb_osd_blend_enable(osd0);

    /* Setup OSD1 - Palette indexed layer */
    bflb_osd_blend_init(osd1, &osd1_blend_config);

    /* Set palette colors (256 entries) */
    extern const uint32_t balloon_palette_256[];
    for (int i = 0; i < 256; i++) {
        bflb_osd_blend_set_palette_color(osd1, i, balloon_palette_256[i] | 0xBF);
    }
    /* Set transparent index (alpha = 0) */
    bflb_osd_blend_set_palette_color(osd1, 0xFF, balloon_palette_256[0xFF] | 0);
    bflb_osd_blend_enable(osd1);

    /* Setup draw layer - rectangle border */
    bflb_osd_draw_init(osd0, OSD_DRAW_LAYER_0, &draw_config);
    bflb_osd_draw_enable(osd0, OSD_DRAW_LAYER_0);

    /* Another draw layer */
    draw_config.border_thickness = 4;
    draw_config.color_y = (OSD_DRAW_YUV_COLOR_GOLD >> 16) & 0xff;
    draw_config.color_u = (OSD_DRAW_YUV_COLOR_GOLD >> 8) & 0xff;
    draw_config.color_v = OSD_DRAW_YUV_COLOR_GOLD & 0xff;
    draw_config.coor.start_x = 300;
    draw_config.coor.start_y = 60;
    draw_config.coor.end_x = 599;
    draw_config.coor.end_y = 399;
    bflb_osd_draw_init(osd0, OSD_DRAW_LAYER_1, &draw_config);
    bflb_osd_draw_enable(osd0, OSD_DRAW_LAYER_1);

    /* Dynamic palette index replacement (for animation) */
    static struct bflb_osd_blend_replace_s replace = {
        .replace_between = true,
        .target_value = 128,
        .min_value = 0xB1,
        .max_value = 0xF6,
    };
    bflb_osd_blend_replace_palette_index(osd1, true, &replace);

    /* Clean cache for layer buffers */
    bflb_l1c_dcache_clean_range(osd0_layer_buffer, sizeof(osd0_layer_buffer));
    bflb_l1c_dcache_clean_range(osd1_layer_buffer, sizeof(osd1_layer_buffer));

    return 0;
}

/* OSD layer position update ISR example */
void osd_layer_isr(int irq, void *arg)
{
    static int32_t x_step = 2;
    static int32_t y_step = 2;

    bflb_osd_int_clear(osd0);
    bflb_osd_blend_disable(osd0);

    /* Update position */
    osd0_blend_config.coor.start_x += x_step;
    osd0_blend_config.coor.start_y += y_step;

    /* Bounce at boundaries */
    if (osd0_blend_config.coor.start_x + 80 > LCD_WIDTH) {
        x_step = -2;
    } else if (osd0_blend_config.coor.start_x == 0) {
        x_step = 2;
    }
    if (osd0_blend_config.coor.start_y + 96 > LCD_HEIGHT) {
        y_step = -2;
    } else if (osd0_blend_config.coor.start_y == 0) {
        y_step = 2;
    }

    osd0_blend_config.coor.end_x = osd0_blend_config.coor.start_x + 80;
    osd0_blend_config.coor.end_y = osd0_blend_config.coor.start_y + 96;

    bflb_osd_blend_set_coordinate(osd0, &osd0_blend_config.coor);
    bflb_osd_blend_enable(osd0);
}
```

---

## Combined DPI + OSD Example

This example shows a complete setup combining DPI for display output and OSD for overlay layers:

```c
#include "bflb_dpi.h"
#include "bflb_osd.h"
#include "bflb_mtimer.h"
#include "board.h"

#define LCD_WIDTH  800
#define LCD_HEIGHT 480

/* Triple framebuffer for smooth animation */
ATTR_NOINIT_PSRAM_SECTION uint16_t framebuffer_1[LCD_WIDTH * LCD_HEIGHT];
ATTR_NOINIT_PSRAM_SECTION uint16_t framebuffer_2[LCD_WIDTH * LCD_HEIGHT];
ATTR_NOINIT_PSRAM_SECTION uint16_t framebuffer_3[LCD_WIDTH * LCD_HEIGHT];

/* OSD layers */
ATTR_NOINIT_PSRAM_SECTION uint16_t osd_layer_buffer[100 * 100];

static struct bflb_device_s *dpi;
static struct bflb_device_s *osd0;

int display_init(void)
{
    /* DPI Configuration */
    struct bflb_dpi_config_s dpi_config = {
        .width   = LCD_WIDTH,
        .height  = LCD_HEIGHT,
        .hsw     = 45,
        .hbp     = 45,
        .hfp     = 89,
        .vsw     = 7,
        .vbp     = 7,
        .vfp     = 5,
        .interface       = DPI_INTERFACE_24_PIN,
        .input_sel       = DPI_INPUT_SEL_FRAMEBUFFER_WITH_OSD,
        .test_pattern    = DPI_TEST_PATTERN_NULL,
        .data_format     = DPI_DATA_FORMAT_RGB565,
        .framebuffer_addr = (uint32_t)framebuffer_1,
    };

    /* OSD Configuration */
    struct bflb_osd_blend_config_s osd_blend_config = {
        .blend_format = OSD_BLEND_FORMAT_ARGB8888,
        .order_a = 3,  // ARGB order
        .order_rv = 2,
        .order_gy = 1,
        .order_bu = 0,
        .coor = {
            .start_x = 0,
            .start_y = 0,
            .end_x = 100,
            .end_y = 100,
        },
        .layer_buffer_addr = (uint32_t)osd_layer_buffer,
    };

    /* Initialize board and GPIOs */
    board_init();
    board_dpi_gpio_init();

    /* Get devices */
    dpi = bflb_device_get_by_name("dpi");
    osd0 = bflb_device_get_by_name("osd0");

    if (dpi == NULL || osd0 == NULL) {
        return -1;
    }

    /* Initialize DPI */
    bflb_dpi_init(dpi, &dpi_config);
    bflb_dpi_enable(dpi);

    /* Initialize OSD */
    bflb_osd_blend_init(osd0, &osd_blend_config);
    bflb_osd_blend_enable(osd0);

    return 0;
}

int main(void)
{
    display_init();

    /* Fill framebuffers with colors for visual effect */
    /* ... fill framebuffers ... */

    /* Framebuffer switch loop */
    while (1) {
        bflb_mtimer_delay_ms(16);  // ~60 FPS

        /* Round-robin framebuffer switching */
        static int fb_index = 0;
        uint32_t new_fb;
        if (fb_index == 0) {
            new_fb = (uint32_t)framebuffer_2;
        } else if (fb_index == 1) {
            new_fb = (uint32_t)framebuffer_3;
        } else {
            new_fb = (uint32_t)framebuffer_1;
        }

        bflb_l1c_dcache_clean_range((void *)new_fb, sizeof(framebuffer_1));
        bflb_dpi_framebuffer_switch(dpi, new_fb);

        fb_index = (fb_index + 1) % 3;
    }
}
```

---

## Summary Comparison

| Interface | Type | Use Case | Key Features |
|-----------|------|----------|--------------|
| **DPI** | Parallel RGB | LCD panels with RGB interface | Multiple data widths (16/18/24-bit), YUV/RGB formats, OSD support |
| **DSI** | MIPI Serial | MIPI DSI display panels | D-PHY, 1/2/4 lanes, LPDT commands, DCS support |
| **DBI** | Parallel/MIPI | LCDs with parallel interface | Type B/C modes, QSPI support, multiple pixel formats |
| **OSD** | Overlay | GUI overlays, icons, text | Up to 16 layers, palette support, hardware blending |

---

## Notes

1. **Framebuffer Placement**: For large displays, framebuffers should be placed in PSRAM (`ATTR_NOINIT_PSRAM_SECTION`) rather than SRAM.

2. **Cache Management**: Always call `bflb_l1c_dcache_clean_range()` after writing to framebuffers that will be accessed by DMA.

3. **Device Names**: Use `bflb_device_get_by_name()` with names like `"dpi"`, `"dbi0"`, `"dsi"`, `"osd0"`, `"osd1"`.

4. **Interrupt Safety**: OSD layer updates should be done in the OSD ISR or with proper synchronization to avoid visual artifacts.

5. **MIP-DSI Compliance**: The DSI controller implements D-PHY and follows MIPI DSI specification for communication with display panels.
