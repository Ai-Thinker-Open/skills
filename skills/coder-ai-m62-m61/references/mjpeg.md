# MJPEG API Reference (BL616/BL618)

> **Source:** `bouffalo_sdk/drivers/lhal/include/bflb_mjpeg.h`  
> **Implementation:** `bouffalo_sdk/drivers/lhal/src/bflb_mjpeg.c`  
> **Register Header:** `hardware/mjpeg_reg.h`  

## Overview

The MJPEG (Motion JPEG) hardware codec module provides YUV→JPEG compression functionality. The module supports multiple YUV input formats (interleaved/planar) and can perform JPEG encoding via hardware automatically, outputting standard JPEG bitstreams. It is suitable for camera video stream encoding, image compression, and similar scenarios.

The module supports two operating modes:
- **Camera Mode** (`bflb_mjpeg_start`/`bflb_mjpeg_stop`): Works together with the DVP camera interface to compress camera frames in real time
- **Software Mode** (`bflb_mjpeg_sw_run`): Reads YUV data from a specified memory buffer and encodes it
  - **Standard Mode**: Compresses a specified number of frames
  - **Kick Mode**: Manually controls block-by-block compression, suitable for real-time flow control

Each module caches a maximum of **4 frames** of compressed JPEG data (`MJPEG_MAX_FRAME_COUNT`).

---

## Macros

### Pixel Format (MJPEG_FORMAT)

| Macro | Value | Description |
|----|---|------|
| `MJPEG_FORMAT_YUV422_YUYV` | 0 | YUYV interleaved format |
| `MJPEG_FORMAT_YUV422_YVYU` | 1 | YVYU interleaved format |
| `MJPEG_FORMAT_YUV422_UYVY` | 2 | UYVY interleaved format |
| `MJPEG_FORMAT_YUV422_VYUY` | 3 | VYUY interleaved format |
| `MJPEG_FORMAT_YUV422SP_NV16` | 4 | YUV422 semi-planar NV16 (U first) |
| `MJPEG_FORMAT_YUV422SP_NV61` | 5 | YUV422 semi-planar NV61 (V first) |
| `MJPEG_FORMAT_YUV420SP_NV12` | 6 | YUV420 semi-planar NV12 (U first) |
| `MJPEG_FORMAT_YUV420SP_NV21` | 7 | YUV420 semi-planar NV21 (V first) |
| `MJPEG_FORMAT_GRAY` | 8 | Grayscale (Y component only) |

### Interrupt Status (MJPEG_INTSTS)

| Macro | Value | Description |
|----|---|------|
| `MJPEG_INTSTS_ONE_FRAME` | `(1 << 4)` | One frame encoding complete interrupt |
| `MJPEG_INTSTS_KICK_DONE` | `(1 << 23)` | Kick encoding complete interrupt (BL616CL only) |
| `MJPEG_INTSTS_SWAP` | `(1 << 30)` | Swap buffer interrupt |

### Interrupt Clear (MJPEG_INTCLR)

| Macro | Value | Description |
|----|---|------|
| `MJPEG_INTCLR_ONE_FRAME` | `(1 << 8)` | Clear one frame complete interrupt |
| `MJPEG_INTCLR_KICK_DONE` | `(1 << 5)` | Clear Kick complete interrupt (BL616CL only) |
| `MJPEG_INTCLR_SWAP` | `(1 << 13)` | Clear swap interrupt |

### Feature Control Commands (MJPEG_CMD)

| Macro | Value | Description |
|----|---|------|
| `MJPEG_CMD_SET_INPUTADDR0` | 0x00 | Set input buffer address 0 (YY frame address) |
| `MJPEG_CMD_SET_INPUTADDR1` | 0x01 | Set input buffer address 1 (UV frame address) |
| `MJPEG_CMD_SET_KICK_DONE_DELAY` | 0x02 | Set Kick done delay (BL616CL only) |
| `MJPEG_CMD_UPDATE_KICK_ADDR` | 0x03 | Update Kick address (BL616CL only) |
| `MJPEG_CMD_READ_HW_VERSION` | 0x04 | Read hardware version (BL616CL only) |
| `MJPEG_CMD_READ_SW_USAGE` | 0x05 | Read software usage flag (BL616CL only) |
| `MJPEG_CMD_WRITE_SW_USAGE` | 0x06 | Write software usage flag (BL616CL only) |
| `MJPEG_CMD_SWAP_ENABLE` | 0x07 | Enable/Disable swap exchange mode |

### Parameter Validation Macros

| Macro | Description |
|----|------|
| `IS_MJPEG_FORMAT(type)` | Validates that the format is legal (`<= MJPEG_FORMAT_GRAY`) |
| `IS_MJPEG_RESOLUTION(type)` | Validates that the resolution is a multiple of 8 |
| `IS_MJPEG_QUALITY(type)` | Validates that quality is ≤ 100 |
| `IS_MJPEG_ADDR(type)` | Validates that the address is 16-byte aligned |

### Frame Buffer Constants

| Macro | Value | Description |
|----|---|------|
| `MJPEG_MAX_FRAME_COUNT` | 4 | Maximum cached frame count |

---

## Data Structures

### bflb_mjpeg_config_s

MJPEG configuration structure.

```c
struct bflb_mjpeg_config_s {
    uint8_t   format;           // Pixel format, use MJPEG_FORMAT macros
    uint8_t   quality;          // JPEG compression quality (0–100)
    uint16_t  rows;             // Total input data rows (used to calculate mem_hblk row block count)
    uint16_t  resolution_x;     // Image width (must be a multiple of 8 or 16)
    uint16_t  resolution_y;     // Image height (must be a multiple of 8 or 16)
    uint32_t  input_bufaddr0;   // Input buffer 0 address (YY), must be 16-byte aligned
    uint32_t  input_bufaddr1;   // Input buffer 1 address (UV), must be 16-byte aligned
    uint32_t  output_bufaddr;   // Output JPEG buffer address, must be 16-byte aligned
    uint32_t  output_bufsize;   // Output buffer size (should be > resolution_x * resolution_y * 2 * MJPEG_MAX_FRAME_COUNT)
    uint16_t *input_yy_table;   // Custom Y quantization table pointer (NULL uses default)
    uint16_t *input_uv_table;   // Custom UV quantization table pointer (NULL uses default)
};
```

---

## LHAL API Functions

### bflb_mjpeg_init

Initialize the MJPEG codec.

```c
void bflb_mjpeg_init(struct bflb_device_s *dev, const struct bflb_mjpeg_config_s *config);
```

**Parameters:**

| Parameter | Type | Description |
|------|------|------|
| `dev` | `struct bflb_device_s *` | Device handle |
| `config` | `const struct bflb_mjpeg_config_s *` | Pointer to MJPEG configuration structure |

---

### bflb_mjpeg_start

Start MJPEG camera compression (linked with the DVP camera interface).

```c
void bflb_mjpeg_start(struct bflb_device_s *dev);
```

---

### bflb_mjpeg_stop

Stop MJPEG camera compression.

```c
void bflb_mjpeg_stop(struct bflb_device_s *dev);
```

---

### bflb_mjpeg_sw_run

Software-triggered mode: reads YUV data from a memory buffer and compresses a specified number of frames.

```c
void bflb_mjpeg_sw_run(struct bflb_device_s *dev, uint8_t frame_count);
```

**Parameters:**

| Parameter | Type | Description |
|------|------|------|
| `dev` | `struct bflb_device_s *` | Device handle |
| `frame_count` | `uint8_t` | Number of frames to compress |

---

### bflb_mjpeg_kick_run

Start Kick mode compression (block-by-block compression, no camera).

```c
void bflb_mjpeg_kick_run(struct bflb_device_s *dev, uint16_t kick_count);
```

**Parameters:**

| Parameter | Type | Description |
|------|------|------|
| `dev` | `struct bflb_device_s *` | Device handle |
| `kick_count` | `uint16_t` | Horizontal block count (number of blocks to compress) |

---

### bflb_mjpeg_kick_stop

Stop Kick mode compression.

```c
void bflb_mjpeg_kick_stop(struct bflb_device_s *dev);
```

---

### bflb_mjpeg_kick

Trigger one compression block in Kick mode.

```c
void bflb_mjpeg_kick(struct bflb_device_s *dev);
```

---

### bflb_mjpeg_tcint_mask

Enable or disable the one-frame compression complete interrupt.

```c
void bflb_mjpeg_tcint_mask(struct bflb_device_s *dev, bool mask);
```

**Parameters:**

| Parameter | Type | Description |
|------|------|------|
| `dev` | `struct bflb_device_s *` | Device handle |
| `mask` | `bool` | `true` = disable interrupt, `false` = enable |

---

### bflb_mjpeg_kickint_mask

Enable or disable the Kick encoding complete interrupt. (BL616CL only)

```c
void bflb_mjpeg_kickint_mask(struct bflb_device_s *dev, bool mask);
```

---

### bflb_mjpeg_swapint_mask

Enable or disable the Swap exchange interrupt.

```c
void bflb_mjpeg_swapint_mask(struct bflb_device_s *dev, bool mask);
```

---

### bflb_mjpeg_errint_mask

Enable or disable error interrupts (including all error types: cam, mem, frame, idle, swap).

```c
void bflb_mjpeg_errint_mask(struct bflb_device_s *dev, bool mask);
```

---

### bflb_mjpeg_get_intstatus

Get the MJPEG interrupt status register value.

```c
uint32_t bflb_mjpeg_get_intstatus(struct bflb_device_s *dev);
```

**Returns:** Interrupt status value; use `MJPEG_INTSTS_*` macros for bit testing.

---

### bflb_mjpeg_int_clear

Clear MJPEG interrupt status.

```c
void bflb_mjpeg_int_clear(struct bflb_device_s *dev, uint32_t int_clear);
```

**Parameters:**

| Parameter | Type | Description |
|------|------|------|
| `dev` | `struct bflb_device_s *` | Device handle |
| `int_clear` | `uint32_t` | Clear value, use `MJPEG_INTCLR_*` macros |

---

### bflb_mjpeg_get_frame_count

Get the number of frames that have been compressed.

```c
uint8_t bflb_mjpeg_get_frame_count(struct bflb_device_s *dev);
```

**Returns:** Current valid frame count (0–4).

---

### bflb_mjpeg_pop_one_frame

Discard one compressed frame's data and free the frame buffer space.

```c
void bflb_mjpeg_pop_one_frame(struct bflb_device_s *dev);
```

---

### bflb_mjpeg_pop_swap_block

Discard the current block in Swap mode.

```c
void bflb_mjpeg_pop_swap_block(struct bflb_device_s *dev);
```

---

### bflb_mjpeg_get_swap_bit_count

Get the remaining encoded bit count in Swap mode.

```c
uint32_t bflb_mjpeg_get_swap_bit_count(struct bflb_device_s *dev);
```

**Returns:** Remaining bit count.

---

### bflb_mjpeg_get_frame_info

Get the JPEG frame information after one frame has been encoded.

```c
uint32_t bflb_mjpeg_get_frame_info(struct bflb_device_s *dev, uint8_t **pic);
```

**Parameters:**

| Parameter | Type | Description |
|------|------|------|
| `dev` | `struct bflb_device_s *` | Device handle |
| `pic` | `uint8_t **` | Output parameter, points to the starting address of JPEG frame data |

**Returns:** JPEG frame data length (in bytes).

---

### bflb_mjpeg_get_swap_block_info

Get the current swap block information in Swap mode.

```c
uint8_t bflb_mjpeg_get_swap_block_info(struct bflb_device_s *dev, uint8_t *idx);
```

**Parameters:**

| Parameter | Type | Description |
|------|------|------|
| `dev` | `struct bflb_device_s *` | Device handle |
| `idx` | `uint8_t *` | Output parameter, current swap block index (0 or 1) |

**Returns:** `1` = frame end, `0` = not ended.

---

### bflb_mjpeg_swap_is_block_full

Check whether the swap block at the specified index is full in Swap mode.

```c
uint8_t bflb_mjpeg_swap_is_block_full(struct bflb_device_s *dev, uint8_t idx);
```

**Parameters:**

| Parameter | Type | Description |
|------|------|------|
| `dev` | `struct bflb_device_s *` | Device handle |
| `idx` | `uint8_t` | Block index (0 or 1) |

**Returns:** `1` = block full, `0` = block not full.

---

### bflb_mjpeg_calculate_quantize_table

Calculate JPEG quantization tables based on quality parameters.

```c
void bflb_mjpeg_calculate_quantize_table(uint8_t quality, uint16_t *input_table, uint16_t *output_table);
```

**Parameters:**

| Parameter | Type | Description |
|------|------|------|
| `quality` | `uint8_t` | Image quality (1–100) |
| `input_table` | `uint16_t *` | Input quantization table (64 uint16_t values) |
| `output_table` | `uint16_t *` | Output quantization table (64 uint16_t values) |

---

### bflb_mjpeg_fill_quantize_table

Fill the quantization tables into the MJPEG hardware registers.

```c
void bflb_mjpeg_fill_quantize_table(struct bflb_device_s *dev, uint16_t *input_yy, uint16_t *input_uv);
```

---

### bflb_mjpeg_fill_jpeg_header_tail

Fill the JPEG file header into the MJPEG hardware registers and enable the hardware to automatically append the JPEG file tail (0xFFD9).

```c
void bflb_mjpeg_fill_jpeg_header_tail(struct bflb_device_s *dev, uint8_t *header, uint32_t header_len);
```

**Parameters:**

| Parameter | Type | Description |
|------|------|------|
| `dev` | `struct bflb_device_s *` | Device handle |
| `header` | `uint8_t *` | Pointer to JPEG file header data |
| `header_len` | `uint32_t` | Header data length |

---

### bflb_mjpeg_set_yuv420sp_cam_input

Set the YUV420SP camera input source (specify DVP channel IDs for YY and UV).

```c
void bflb_mjpeg_set_yuv420sp_cam_input(struct bflb_device_s *dev, uint8_t yy, uint8_t uv);
```

---

### bflb_mjpeg_update_input_output_buff

Update MJPEG input/output buffer addresses at runtime.

```c
void bflb_mjpeg_update_input_output_buff(struct bflb_device_s *dev, void *input_buf0, void *input_buf1, void *output_buff, size_t output_buff_size);
```

**Parameters:**

| Parameter | Type | Description |
|------|------|------|
| `dev` | `struct bflb_device_s *` | Device handle |
| `input_buf0` | `void *` | New input buffer 0 address (NULL = no update) |
| `input_buf1` | `void *` | New input buffer 1 address (NULL = no update) |
| `output_buff` | `void *` | New output buffer address (NULL = no update) |
| `output_buff_size` | `size_t` | Output buffer size |

---

### bflb_mjpeg_feature_control

MJPEG feature control interface.

```c
int bflb_mjpeg_feature_control(struct bflb_device_s *dev, int cmd, size_t arg);
```

**Parameters:**

| Parameter | Type | Description |
|------|------|------|
| `dev` | `struct bflb_device_s *` | Device handle |
| `cmd` | `int` | Feature command, use MJPEG_CMD macros |
| `arg` | `size_t` | Command argument |

**Returns:** 0 on success, `-EPERM` on failure. `MJPEG_CMD_READ_HW_VERSION` and `MJPEG_CMD_READ_SW_USAGE` return the read value.

---

## Usage Examples

### Example 1: Software Mode Single-Frame JPEG Compression

```c
#include "bflb_mjpeg.h"

// JPEG file header (JFIF standard)
static const uint8_t jpeg_header[] = {
    0xFF, 0xD8, 0xFF, 0xE0, 0x00, 0x10, 0x4A, 0x46,
    0x49, 0x46, 0x00, 0x01, 0x01, 0x00, 0x00, 0x01,
    0x00, 0x01, 0x00, 0x00, 0xFF, 0xDB, 0x00, 0x43,
    // ... more JPEG header data
};

static uint8_t yuv_frame[320 * 240 * 2] __attribute__((aligned(16)));
static uint8_t jpeg_output[320 * 240 * 2 * 4] __attribute__((aligned(16)));

void mjpeg_encode_example(void)
{
    struct bflb_device_s *mjpeg;

    mjpeg = bflb_device_get_by_name("mjpeg");

    // Fill JPEG file header
    bflb_mjpeg_fill_jpeg_header_tail(mjpeg, (uint8_t *)jpeg_header, sizeof(jpeg_header));

    struct bflb_mjpeg_config_s config = {
        .format = MJPEG_FORMAT_YUV422_YUYV,
        .quality = 75,
        .rows = 240,
        .resolution_x = 320,
        .resolution_y = 240,
        .input_bufaddr0 = (uint32_t)yuv_frame,
        .input_bufaddr1 = 0,
        .output_bufaddr = (uint32_t)jpeg_output,
        .output_bufsize = sizeof(jpeg_output),
        .input_yy_table = NULL,  // Use default quantization table
        .input_uv_table = NULL,
    };

    bflb_mjpeg_init(mjpeg, &config);

    // Enable one frame complete interrupt
    bflb_mjpeg_tcint_mask(mjpeg, false);

    // Software trigger to compress 1 frame
    bflb_mjpeg_sw_run(mjpeg, 1);

    // Wait for interrupt or poll frame count
    while (bflb_mjpeg_get_frame_count(mjpeg) == 0) {
        // Wait for compression to complete (use interrupt callback in real applications)
    }

    // Get JPEG data
    uint8_t *pic = NULL;
    uint32_t len = bflb_mjpeg_get_frame_info(mjpeg, &pic);

    // pic points to valid JPEG data, len is byte count
    // Can send or save pic[0..len-1]

    // Discard the processed frame
    bflb_mjpeg_pop_one_frame(mjpeg);
}
```

### Example 2: Camera Mode Real-Time MJPEG Encoding

```c
void mjpeg_camera_example(void)
{
    struct bflb_device_s *mjpeg;

    mjpeg = bflb_device_get_by_name("mjpeg");

    // Fill JPEG file header
    bflb_mjpeg_fill_jpeg_header_tail(mjpeg, (uint8_t *)jpeg_header, sizeof(jpeg_header));

    struct bflb_mjpeg_config_s config = {
        .format = MJPEG_FORMAT_YUV420SP_NV12,
        .quality = 80,
        .rows = 480,
        .resolution_x = 640,
        .resolution_y = 480,
        .input_bufaddr0 = (uint32_t)yy_buffer,
        .input_bufaddr1 = (uint32_t)uv_buffer,
        .output_bufaddr = (uint32_t)jpeg_output,
        .output_bufsize = 640 * 480 * 2 * 4,
        .input_yy_table = NULL,
        .input_uv_table = NULL,
    };

    bflb_mjpeg_init(mjpeg, &config);

    // Set camera YUV420SP input source
    bflb_mjpeg_set_yuv420sp_cam_input(mjpeg, 0, 0);

    // Enable interrupts
    bflb_mjpeg_tcint_mask(mjpeg, false);

    // Start camera mode compression
    bflb_mjpeg_start(mjpeg);

    // Process frames in main loop
    while (1) {
        if (bflb_mjpeg_get_frame_count(mjpeg) > 0) {
            uint8_t *pic = NULL;
            uint32_t len = bflb_mjpeg_get_frame_info(mjpeg, &pic);

            // Send or save JPEG frame
            // send_jpeg_frame(pic, len);

            bflb_mjpeg_pop_one_frame(mjpeg);
        }
    }
}
```

### Example 3: Custom Quantization Tables + Swap Mode

```c
static uint16_t my_quant_y[64] = {
    16, 11, 10, 16, 24, 40, 51, 61,
    12, 12, 14, 19, 26, 58, 60, 55,
    14, 13, 16, 24, 40, 57, 69, 56,
    14, 17, 22, 29, 51, 87, 80, 62,
    18, 22, 37, 56, 68, 109, 103, 77,
    24, 35, 55, 64, 81, 104, 113, 92,
    49, 64, 78, 87, 103, 121, 120, 101,
    72, 92, 95, 98, 112, 100, 103, 99
};

static uint16_t my_quant_uv[64] = {
    17, 18, 24, 47, 99, 99, 99, 99,
    // ... UV quantization table 64 entries
};

void mjpeg_custom_quality_example(void)
{
    struct bflb_device_s *mjpeg;

    mjpeg = bflb_device_get_by_name("mjpeg");

    // Calculate quantization tables
    uint16_t quant_y[64], quant_uv[64];
    bflb_mjpeg_calculate_quantize_table(60, my_quant_y, quant_y);
    bflb_mjpeg_calculate_quantize_table(60, my_quant_uv, quant_uv);

    struct bflb_mjpeg_config_s config = {
        .format = MJPEG_FORMAT_YUV422_YUYV,
        .quality = 60,
        .rows = 480,
        .resolution_x = 640,
        .resolution_y = 480,
        .input_bufaddr0 = (uint32_t)yuv_frame,
        .input_bufaddr1 = 0,
        .output_bufaddr = (uint32_t)jpeg_output,
        .output_bufsize = sizeof(jpeg_output),
        .input_yy_table = my_quant_y,  // Use custom quantization table
        .input_uv_table = my_quant_uv,
    };

    bflb_mjpeg_init(mjpeg, &config);

    // Enable Swap mode (dual-block exchange output)
    bflb_mjpeg_feature_control(mjpeg, MJPEG_CMD_SWAP_ENABLE, 1);

    // Enable Swap interrupt
    bflb_mjpeg_swapint_mask(mjpeg, false);

    // Start compression
    bflb_mjpeg_sw_run(mjpeg, 1);

    // Poll Swap block status
    uint8_t idx;
    while (!bflb_mjpeg_get_swap_block_info(mjpeg, &idx)) {
        if (bflb_mjpeg_swap_is_block_full(mjpeg, idx)) {
            uint32_t bits = bflb_mjpeg_get_swap_bit_count(mjpeg);
            // Process the full swap block
            bflb_mjpeg_pop_swap_block(mjpeg);
        }
    }
}
```

### Example 4: Interrupt Handling Mode

```c
void mjpeg_interrupt_example(void)
{
    struct bflb_device_s *mjpeg;

    mjpeg = bflb_device_get_by_name("mjpeg");

    // ... Initialize MJPEG configuration ...

    // Enable one-frame complete interrupt and error interrupt
    bflb_mjpeg_tcint_mask(mjpeg, false);
    bflb_mjpeg_errint_mask(mjpeg, false);

    // Start camera mode
    bflb_mjpeg_start(mjpeg);
}

// Interrupt service routine
void mjpeg_isr_handler(void)
{
    struct bflb_device_s *mjpeg = bflb_device_get_by_name("mjpeg");
    uint32_t status = bflb_mjpeg_get_intstatus(mjpeg);

    if (status & MJPEG_INTSTS_ONE_FRAME) {
        // One frame complete
        uint8_t *pic = NULL;
        uint32_t len = bflb_mjpeg_get_frame_info(mjpeg, &pic);

        // Process JPEG frame...

        bflb_mjpeg_pop_one_frame(mjpeg);

        // Clear interrupt
        bflb_mjpeg_int_clear(mjpeg, MJPEG_INTCLR_ONE_FRAME);
    }

    if (status & MJPEG_INTSTS_SWAP) {
        // Swap interrupt handling
        bflb_mjpeg_int_clear(mjpeg, MJPEG_INTCLR_SWAP);
    }
}
```

---

## Register Information

The MJPEG module register base address is obtained via `dev->reg_base`.

### Core Control Registers

#### MJPEG_CONTROL_1 (Offset 0x00)

| Bit | Field | Description |
|----|------|------|
| 0 | `MJPEG_ENABLE` | MJPEG enable (1=enable) |
| 1 | `MJPEG_BIT_ORDER` | JPEG bit order |
| 2 | `ORDER_U_EVEN` | U component ordering (1=UV, 0=VU) |
| 3 | `HW_MODE_SWEN` | Hardware mode software enable |
| 4 | `LAST_HF_WBLK_DMY` | Last half-width block padding |
| 5 | `LAST_HF_HBLK_DMY` | Last half-height block padding |
| 7 | `READ_FWRAP` | Frame read wrap enable |
| 8–10 | `W_XLEN` | AXI write burst length |
| 12–13 | `YUV_MODE` | YUV mode (0=420, 1=Gray, 2=422SP, 3=422) |
| 14 | `KICK_DONE_STS_EN` | Kick done status enable (BL616CL only) |
| 24–29 | `MJPEG_HW_FRAME` | Hardware frame count |
| 30 | `KICK_UPDATE_ADDR` | Kick update address (BL616CL only) |

#### MJPEG_CONTROL_2 (Offset 0x04)

| Bit | Field | Description |
|----|------|------|
| 0–4 | `SW_FRAME` | Software-triggered frame count (0–31) |
| 5 | `INT_KICK_CLR` | Kick interrupt clear (BL616CL only) |
| 6 | `SW_KICK` | Software Kick trigger |
| 7 | `SW_KICK_MODE` | Kick mode enable |
| 8 | `MJPEG_SW_MODE` | Software mode enable |
| 9 | `MJPEG_SW_RUN` | Software run |
| 10–12 | `YY_DVP2AXI_SEL` | YY component DVP→AXI channel select |
| 13–15 | `UV_DVP2AXI_SEL` | UV component DVP→AXI channel select |
| 16–31 | `MJPEG_WAIT_CYCLE` | Wait cycles (default 0x100) |

#### MJPEG_CONTROL_3 (Offset 0x1C)

| Bit | Field | Description |
|----|------|------|
| 0 | `INT_NORMAL_EN` | Normal interrupt enable |
| 1 | `INT_CAM_EN` | Camera error interrupt enable |
| 2 | `INT_MEM_EN` | Memory error interrupt enable |
| 3 | `INT_FRAME_EN` | Frame error interrupt enable |
| 4 | `STS_NORMAL_INT` | Normal interrupt status |
| 5 | `STS_CAM_INT` | Camera error interrupt status |
| 6 | `STS_MEM_INT` | Memory error interrupt status |
| 7 | `STS_FRAME_INT` | Frame error interrupt status |
| 8–15 | Status flags | IDLE/FUNC/WAIT etc. status |
| 16–20 | `FRAME_CNT_TRGR_INT` | Frame trigger interrupt threshold |
| 21 | `INT_IDLE_EN` | Idle interrupt enable |
| 22 | `STS_IDLE_INT` | Idle interrupt status |
| 23 | `STS_KICK_INT` | Kick interrupt status (BL616CL only) |
| 24–28 | `FRAME_VALID_CNT` | Valid frame count (0–4) |
| 29 | `INT_SWAP_EN` | Swap interrupt enable |
| 30 | `STS_SWAP_INT` | Swap interrupt status |
| 31 | `INT_KICK_EN` | Kick interrupt enable (BL616CL only) |

### Buffer Address Registers

| Register | Offset | Description |
|--------|------|------|
| `MJPEG_YY_FRAME_ADDR` | `0x08` | YY frame buffer address |
| `MJPEG_UV_FRAME_ADDR` | `0x0C` | UV frame buffer address |
| `MJPEG_JPEG_FRAME_ADDR` | `0x14` | JPEG output buffer address |
| `MJPEG_JPEG_STORE_MEMORY` | `0x18` | JPEG storage space size (burst count = size/128) |

### Frame Information Registers

| Register | Offset | Description |
|--------|------|------|
| `MJPEG_START_ADDR0–3` | `0x80/88/90/98` | Frame 0–3 start address |
| `MJPEG_BIT_CNT0–3` | `0x84/8C/94/9C` | Frame 0–3 bit count |

### Frame Size and Header

| Register | Offset | Description |
|--------|------|------|
| `MJPEG_FRAME_SIZE` | `0x24` | Frame width block count (bits 0–11) + frame height block count (bits 16–27) |
| `MJPEG_HEADER_BYTE` | `0x28` | JPEG header length + YUV component ordering + tail enable |

### YUV Memory Configuration

| Register | Offset | Description |
|--------|------|------|
| `MJPEG_YUV_MEM` | `0x10` | YY hblk count (bits 0–12) + UV hblk count (bits 16–28) |
| `MJPEG_YUV_MEM_SW` | `0x38` | Software mode Kick hblk count |

### Swap Mode Registers

| Register | Offset | Description |
|--------|------|------|
| `MJPEG_SWAP_MODE` | `0x30` | Swap mode configuration and status |
| `MJPEG_SWAP_BIT_CNT` | `0x34` | Swap frame end bit count |

### Quantization/Encoding Registers

| Register | Offset | Description |
|--------|------|------|
| `MJPEG_Q_ENC` | `0x100` | Quantization encoding control (bit 24=Q_SRAM_SW) |
| `MJPEG_Q_PARAM_00` | `0x400–0x47C` | Y quantization table (8×4 32-bit registers) |
| `MJPEG_Q_PARAM_40` | `0x480–0x4FC` | UV quantization table (8×4 32-bit registers) |

### Other Registers

| Register | Offset | Description |
|--------|------|------|
| `MJPEG_FRAME_FIFO_POP` | `0x20` | Frame/interrupt pop and clear register |
| `MJPEG_KICK_DONE_DELAY` | `0x104` | Kick done delay (BL616CL only) |
| `MJPEG_FRAME_ID_10` | `0x110` | Frame 0 and frame 1 IDs |
| `MJPEG_FRAME_ID_32` | `0x114` | Frame 2 and frame 3 IDs |
| `MJPEG_DEBUG` | `0x1F0` | Debug control |
| `MJPEG_SW_USAGE` | `0x1F8` | Software usage flag (BL616CL only) |
| `MJPEG_HW_VERSION` | `0x1F8` | Hardware version (BL616CL only) |
| `MJPEG_DUMMY_REG` | `0x1FC` | Dummy register |

> **Note:** The quantization table register layout is 8 columns × 4 rows, with each register containing two uint16_t values (lower 16 bits + upper 16 bits).
