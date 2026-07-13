# BL616/BL618 Camera Interface Documentation

## Overview

The BL616/BL618 series supports camera interfaces via DVP (Digital Video Port) with MJPEG encoding/decoding capabilities. This document covers the camera initialization, capture, MJPEG decode, and DVP raster interface.

## Header Files

- `bflb_cam.h` - Camera (CAM) driver
- `bflb_mjpeg.h` - MJPEG encoder driver  
- `bflb_mjdec.h` - MJPEG decoder driver
- `bflb_dvp_raster.h` - DVP raster processing driver

---

## 1. Camera (CAM) Interface

### 1.1 Input Formats

```c
CAM_INPUT_FORMAT_YUV422_YUYV   0  /* YUYV interleaved */
CAM_INPUT_FORMAT_YUV422_YVYU   1  /* YVYU interleaved */
CAM_INPUT_FORMAT_YUV422_UYVY   2  /* UYVY interleaved */
CAM_INPUT_FORMAT_YUV422_VYUY   3  /* VYUY interleaved */
CAM_INPUT_FORMAT_GRAY          4  /* 8-bit grayscale */
CAM_INPUT_FORMAT_RGB565        5  /* 16-bit RGB */
CAM_INPUT_FORMAT_BGR565        6  /* 16-bit BGR */
CAM_INPUT_FORMAT_RGB888        7  /* 24-bit RGB */
CAM_INPUT_FORMAT_BGR888        8  /* 24-bit BGR */
```

### 1.2 Output Formats

```c
CAM_OUTPUT_FORMAT_AUTO              0  /* Auto select */
CAM_OUTPUT_FORMAT_YUV422            1  /* YUV422 output */
CAM_OUTPUT_FORMAT_GRAY              2  /* 8-bit grayscale */
CAM_OUTPUT_FORMAT_YUV422_UV         3  /* YUV422 UV interleaved */
CAM_OUTPUT_FORMAT_YUV420_UV         4  /* YUV420 UV interleaved */
CAM_OUTPUT_FORMAT_RGB565_OR_BGR565  5  /* RGB565 or BGR565 */
CAM_OUTPUT_FORMAT_RGB888_OR_BGR888  6  /* RGB888 or BGR888 */
CAM_OUTPUT_FORMAT_RGB888_TO_RGB565  7  /* Convert RGB888 to RGB565 */
CAM_OUTPUT_FORMAT_RGB888_TO_BGR565  8  /* Convert RGB888 to BGR565 */
CAM_OUTPUT_FORMAT_RGB888_TO_RGBA8888 9 /* Convert RGB888 to RGBA8888 */
```

### 1.3 Configuration Structure

```c
struct bflb_cam_config_s {
    uint8_t  input_format;      /* CAM_INPUT_FORMAT_* */
    uint16_t resolution_x;       /* Width in pixels */
    uint16_t resolution_y;       /* Height in lines */
    uint16_t h_blank;            /* Hsync blank time */
    uint32_t pixel_clock;         /* Pixel clock in Hz */
    bool     with_mjpeg;         /* Enable MJPEG mode */
    uint8_t  input_source;      /* CAM_INPUT_SOURCE_DVP */
    uint8_t  output_format;      /* CAM_OUTPUT_FORMAT_* */
    uint32_t output_bufaddr;     /* Output buffer address (align 16) */
    uint32_t output_bufsize;     /* Output buffer size */
};
```

### 1.4 Camera API Functions

| Function | Description |
|----------|-------------|
| `bflb_cam_init(dev, config)` | Initialize camera with configuration |
| `bflb_cam_start(dev)` | Start camera capture |
| `bflb_cam_stop(dev)` | Stop camera capture |
| `bflb_cam_int_mask(dev, type, mask)` | Enable/disable interrupts |
| `bflb_cam_int_clear(dev, type)` | Clear interrupt flags |
| `bflb_cam_get_intstatus(dev)` | Get interrupt status |
| `bflb_cam_get_frame_info(dev, &pic)` | Get frame address and size |
| `bflb_cam_get_frame_count(dev)` | Get pending frame count |
| `bflb_cam_pop_one_frame(dev)` | Discard one frame |
| `bflb_cam_crop_vsync(dev, start, end)` | Crop vertical sync |
| `bflb_cam_crop_hsync(dev, start, end)` | Crop horizontal sync |
| `bflb_cam_feature_control(dev, cmd, arg)` | Feature control |

### 1.5 Feature Control Commands

```c
CAM_CMD_SET_VSYNC_POLARITY      1   /* Set VSYNC polarity */
CAM_CMD_SET_HSYNC_POLARITY      2   /* Set HSYNC polarity */
CAM_CMD_SET_BURST               3   /* Set burst length */
CAM_CMD_SET_RGBA8888_ALPHA      4   /* Set RGBA alpha value */
CAM_CMD_GET_FRAME_ID            5   /* Get frame ID */
CAM_CMD_WRAP_MODE               6   /* Set wrap mode */
CAM_CMD_COUNT_TRIGGER_NORMAL_INT 7 /* Count trigger normal interrupts */
CAM_CMD_FRAME_ID_RESET          8   /* Reset frame ID */
CAM_CMD_INVERSE_VSYNC_POLARITY  9   /* Invert VSYNC polarity */
CAM_CMD_INVERSE_HSYNC_POLARITY 10   /* Invert HSYNC polarity */
CAM_CMD_INVERSE_YUYV2UYVY     11   /* Invert YUYV to UYVY */
CAM_CMD_FRAME_FILTER           12   /* Frame filter config */
CAM_CMD_SET_OUTPUT_ADDR        13   /* Set output buffer address */
CAM_CMD_SET_PIXEL_SIZE         14   /* Set pixel size (BL618DG) */
```

### 1.6 Interrupt Status

```c
CAM_INTSTS_NORMAL              (1 << 12)  /* Normal interrupt */
CAM_INTSTS_MEMORY_OVERWRITE    (1 << 13)  /* Memory overwrite */
CAM_INTSTS_FRAME_OVERWRITE     (1 << 14)  /* Frame overwrite */
CAM_INTSTS_FIFO_OVERWRITE      (1 << 15)  /* FIFO overwrite */
CAM_INTSTS_HSYNC_MISMATCH      (1 << 21)  /* HSync mismatch */
CAM_INTSTS_VSYNC_MISMATCH      (1 << 22)  /* VSync mismatch */
```

---

## 2. DVP (Digital Video Port) Raster Interface

### 2.1 Geometric Transformation Modes

```c
DVP_RASTER_TRANSLATE           (0 << 6)   /* No transformation */
DVP_RASTER_FLIP_HORIZONTAL     (1 << 4)   /* Horizontal flip */
DVP_RASTER_FLIP_VERTICAL       (1 << 5)   /* Vertical flip */
DVP_RASTER_ROTATE_DEGREE_90   (1 << 6)   /* Rotate 90° */
DVP_RASTER_ROTATE_DEGREE_180  (2 << 6)   /* Rotate 180° */
DVP_RASTER_ROTATE_DEGREE_270  (3 << 6)   /* Rotate 270° */
```

### 2.2 Configuration Structure

```c
struct bflb_dvp_raster_config_s {
    uint32_t mode;             /* Transformation mode */
    uint16_t resolution_x;      /* Width in pixels */
    uint16_t resolution_y;      /* Height in lines */
    uint32_t y_frame_addr;      /* Y data buffer address */
    uint8_t  y_frame_cnt;       /* Y buffer frame count */
    uint32_t uv_frame_addr;     /* UV data buffer address */
    uint8_t  uv_frame_cnt;      /* UV buffer frame count */
};
```

### 2.3 DVP Raster API Functions

| Function | Description |
|----------|-------------|
| `bflb_dvp_raster_init(dev, config)` | Initialize DVP raster |
| `bflb_dvp_raster_deinit(dev)` | Deinitialize DVP raster |
| `bflb_dvp_raster_enable(dev)` | Enable DVP raster |
| `bflb_dvp_raster_disable(dev)` | Disable DVP raster |
| `bflb_dvp_raster_sw_mode(dev, enable)` | Enable software mode |
| `bflb_dvp_raster_sw_mode_kick(dev)` | Trigger software mode |
| `bflb_dvp_raster_sw_mode_output_rgb(dev, enable)` | Output RGB in sw mode |
| `bflb_dvp_raster_int_mask(dev, type, mask)` | Enable/disable interrupts |
| `bflb_dvp_raster_get_intstatus(dev, type)` | Get interrupt status |
| `bflb_dvp_raster_int_clear(dev, type)` | Clear interrupt flags |
| `bflb_dvp_raster_crop_vsync(dev, start, end)` | Crop vertical sync |
| `bflb_dvp_raster_crop_hsync(dev, start, end)` | Crop horizontal sync |
| `bflb_dvp_raster_feature_control(dev, cmd, arg)` | Feature control |

---

## 3. MJPEG Encoder Interface

### 3.1 MJPEG Formats

```c
MJPEG_FORMAT_YUV422_YUYV   0  /* YUYV interleaved */
MJPEG_FORMAT_YUV422_YVYU   1  /* YVYU interleaved */
MJPEG_FORMAT_YUV422_UYVY   2  /* UYVY interleaved */
MJPEG_FORMAT_YUV422_VYUY   3  /* VYUY interleaved */
MJPEG_FORMAT_YUV422SP_NV16 4 /* YUV422 semi-planar NV16 */
MJPEG_FORMAT_YUV422SP_NV61 5 /* YUV422 semi-planar NV61 */
MJPEG_FORMAT_YUV420SP_NV12 6 /* YUV420 semi-planar NV12 */
MJPEG_FORMAT_YUV420SP_NV21 7 /* YUV420 semi-planar NV21 */
MJPEG_FORMAT_GRAY          8 /* 8-bit grayscale */
```

### 3.2 Configuration Structure

```c
struct bflb_mjpeg_config_s {
    uint8_t  format;            /* MJPEG_FORMAT_* */
    uint8_t  quality;           /* 0-100 quality */
    uint16_t rows;              /* Rows/height */
    uint16_t resolution_x;      /* Width */
    uint16_t resolution_y;      /* Height (must be multiple of 8) */
    uint32_t input_bufaddr0;    /* Input buffer 0 for YY (align 16) */
    uint32_t input_bufaddr1;    /* Input buffer 1 for UV (align 16) */
    uint32_t output_bufaddr;    /* Output buffer address (align 16) */
    uint32_t output_bufsize;    /* Output buffer size */
    uint16_t *input_yy_table;   /* YY quantization table */
    uint16_t *input_uv_table;   /* UV quantization table */
};
```

### 3.3 MJPEG Encoder API Functions

| Function | Description |
|----------|-------------|
| `bflb_mjpeg_init(dev, config)` | Initialize MJPEG encoder |
| `bflb_mjpeg_start(dev)` | Start MJPEG encoding |
| `bflb_mjpeg_stop(dev)` | Stop MJPEG encoding |
| `bflb_mjpeg_sw_run(dev, frame_count)` | Software encoding run |
| `bflb_mjpeg_kick_run(dev, kick_count)` | Kick mode encoding |
| `bflb_mjpeg_kick_stop(dev)` | Stop kick mode |
| `bflb_mjpeg_kick(dev)` | Trigger single kick |
| `bflb_mjpeg_tcint_mask(dev, mask)` | Mask transfer complete int |
| `bflb_mjpeg_swapint_mask(dev, mask)` | Mask swap interrupt |
| `bflb_mjpeg_errint_mask(dev, mask)` | Mask error interrupt |
| `bflb_mjpeg_get_intstatus(dev)` | Get interrupt status |
| `bflb_mjpeg_int_clear(dev, val)` | Clear interrupts |
| `bflb_mjpeg_get_frame_count(dev)` | Get encoded frame count |
| `bflb_mjpeg_get_frame_info(dev, &pic)` | Get frame info |
| `bflb_mjpeg_pop_one_frame(dev)` | Discard one frame |
| `bflb_mjpeg_calculate_quantize_table(quality, in, out)` | Calculate Q table |
| `bflb_mjpeg_fill_quantize_table(dev, yy, uv)` | Fill Q table to HW |
| `bflb_mjpeg_fill_jpeg_header_tail(dev, header, len)` | Fill JPEG header |
| `bflb_mjpeg_set_yuv420sp_cam_input(dev, yy, uv)` | Set camera input |
| `bflb_mjpeg_update_input_output_buff(dev, in0, in1, out, size)` | Update buffers |
| `bflb_mjpeg_feature_control(dev, cmd, arg)` | Feature control |

### 3.4 Interrupt Status

```c
MJPEG_INTSTS_ONE_FRAME     (1 << 4)  /* One frame done */
MJPEG_INTSTS_KICK_DONE     (1 << 23) /* Kick done (BL616CL) */
MJPEG_INTSTS_SWAP          (1 << 30) /* Swap interrupt */
```

---

## 4. MJPEG Decoder Interface

### 4.1 MJDEC Formats

```c
MJDEC_FORMAT_YUV422SP_NV16 (4) /* YUV422 semi-planar */
MJDEC_FORMAT_YUV422SP_NV61 (5) /* YUV422 semi-planar */
MJDEC_FORMAT_YUV420SP_NV12 (6) /* YUV420 semi-planar */
MJDEC_FORMAT_YUV420SP_NV21 (7) /* YUV420 semi-planar */
MJDEC_FORMAT_GRAY          (8) /* 8-bit grayscale */
```

### 4.2 Configuration Structure

```c
struct bflb_mjdec_config_s {
    uint8_t  format;            /* MJDEC_FORMAT_* */
    uint8_t  swap_enable;        /* Ping-pong buffer mode */
    uint16_t resolution_x;      /* Width (must be multiple of 8) */
    uint16_t resolution_y;      /* Height (must be multiple of 8) */
    uint16_t head_size;         /* JPEG header size */
    uint32_t output_bufaddr0;    /* Output buffer 0 for YY (align 8) */
    uint32_t output_bufaddr1;    /* Output buffer 1 for UV (align 8) */
};
```

### 4.3 MJPEG Decoder API Functions

| Function | Description |
|----------|-------------|
| `bflb_mjdec_init(dev, config)` | Initialize MJPEG decoder |
| `bflb_mjdec_start(dev)` | Start decoding |
| `bflb_mjdec_stop(dev)` | Stop decoding |
| `bflb_mjdec_push_jpeg(dev, frame)` | Push JPEG frame to decode |
| `bflb_mjdec_tcint_mask(dev, mask)` | Mask transfer complete int |
| `bflb_mjdec_get_intstatus(dev)` | Get interrupt status |
| `bflb_mjdec_int_clear(dev, val)` | Clear interrupts |
| `bflb_mjdec_get_frame_count(dev)` | Get decoded frame count |
| `bflb_mjdec_pop_one_frame(dev)` | Discard one frame |
| `bflb_mjdec_set_dqt_from_quality(dev, quality)` | Set Q table from quality |
| `bflb_mjdec_feature_control(dev, cmd, arg)` | Feature control |

### 4.4 Error Codes

```c
MJDEC_OK                   0   /* Success */
MJDEC_ERR_POINTER_NULL     1   /* Null pointer */
MJDEC_ERR_HEADER_SOI       2   /* Missing SOI marker */
MJDEC_ERR_HEADER_MARKER    3   /* Invalid marker */
MJDEC_ERR_DQT_TYPE         4   /* Invalid DQT type */
MJDEC_ERR_DQT_LENGTH       5   /* Invalid DQT length */
MJDEC_ERR_HEADER_TIMEOUT   6   /* Header parse timeout */
MJDEC_ERR_DHT_TRIG        20   /* DHT trigger error */
MJDEC_ERR_DHT_TYPE        21   /* Invalid DHT type */
MJDEC_ERR_DHT_COUNT       22   /* Invalid DHT count */
MJDEC_ERR_DHT_YY_DC_CNT   23   /* YY DC count error */
MJDEC_ERR_DHT_YY_DC_VAL   24   /* YY DC value error */
MJDEC_ERR_DHT_YY_DC_BYTES 25   /* YY DC bytes error */
MJDEC_ERR_DHT_YY_AC_BYTES 26   /* YY AC bytes error */
MJDEC_ERR_DHT_UV_DC_CNT   27   /* UV DC count error */
MJDEC_ERR_DHT_UV_DC_VAL   28   /* UV DC value error */
MJDEC_ERR_DHT_UV_DC_BYTES 29   /* UV DC bytes error */
MJDEC_ERR_DHT_UV_AC_BYTES 30   /* UV AC bytes error */
```

---

## 5. Working Code Examples

### 5.1 Camera Initialization and Capture (Blocking Mode)

```c
#include "bflb_cam.h"
#include "bflb_mjpeg.h"
#include "bflb_dvp_raster.h"
#include "bflb_gpio.h"
#include "bflb_irq.h"

#define CAM_DEVICE_NAME "cam"
#define MJPEG_DEVICE_NAME "mjpeg"
#define MJDEC_DEVICE_NAME "mjdec"

static struct bflb_device_s *cam_dev;
static struct bflb_device_s *mjpeg_dev;
static struct bflb_device_s *mjdec_dev;

/* Frame buffers - must be 16-byte aligned */
static uint8_t cam_output_buf[320 * 240 * 2] __attribute__((aligned(16)));
static uint8_t jpeg_output_buf[64 * 1024] __attribute__((aligned(16)));
static uint8_t y_frame_buf[320 * 240] __attribute__((aligned(8)));
static uint8_t uv_frame_buf[320 * 120] __attribute__((aligned(8)));

void camera_isr(int irq, void *arg)
{
    uint32_t int_status = bflb_cam_get_intstatus(cam_dev);
    
    if (int_status & CAM_INTSTS_NORMAL) {
        bflb_cam_int_clear(cam_dev, CAM_INTCLR_NORMAL);
        /* Frame captured - process it */
        uint8_t *frame_addr;
        uint32_t frame_size = bflb_cam_get_frame_info(cam_dev, &frame_addr);
        printf("Frame captured: addr=%p, size=%u\r\n", frame_addr, frame_size);
    }
    
    if (int_status & CAM_INTSTS_FIFO_OVERWRITE) {
        bflb_cam_int_clear(cam_dev, CAM_INTCLR_FIFO_OVERWRITE);
        printf("FIFO overwrite error\r\n");
    }
}

int camera_capture_example(void)
{
    /* Get device handles */
    cam_dev = bflb_device_get_by_name(CAM_DEVICE_NAME);
    if (cam_dev == NULL) {
        printf("Failed to get cam device\r\n");
        return -1;
    }
    
    /* Configure camera */
    struct bflb_cam_config_s cam_config = {
        .input_format = CAM_INPUT_FORMAT_YUV422_YUYV,
        .resolution_x = 320,
        .resolution_y = 240,
        .h_blank = 0,
        .pixel_clock = 12000000,  /* 12MHz */
        .with_mjpeg = false,
        .input_source = CAM_INPUT_SOURCE_DVP,
        .output_format = CAM_OUTPUT_FORMAT_YUV422,
        .output_bufaddr = (uint32_t)cam_output_buf,
        .output_bufsize = sizeof(cam_output_buf),
    };
    
    bflb_cam_init(cam_dev, &cam_config);
    
    /* Setup interrupt */
    bflb_irq_request(cam_dev->irq_num, camera_isr, NULL);
    bflb_cam_int_mask(cam_dev, CAM_INTMASK_NORMAL, false);
    
    /* Start capture */
    bflb_cam_start(cam_dev);
    
    /* Capture frames - call bflb_cam_pop_one_frame() to discard or
       bflb_cam_get_frame_info() to retrieve */
    
    return 0;
}
```

### 5.2 MJPEG Encoding with Camera

```c
#include "bflb_mjpeg.h"

static uint16_t yy_quant_table[64];
static uint16_t uv_quant_table[64];

int mjpeg_encoding_example(void)
{
    /* Get MJPEG device */
    mjpeg_dev = bflb_device_get_by_name(MJPEG_DEVICE_NAME);
    if (mjpeg_dev == NULL) {
        return -1;
    }
    
    /* Calculate quantization tables */
    bflb_mjpeg_calculate_quantize_table(80, yy_quant_table, uv_quant_table);
    
    /* Configure MJPEG */
    struct bflb_mjpeg_config_s mjpeg_config = {
        .format = MJPEG_FORMAT_YUV422_YUYV,
        .quality = 80,
        .rows = 240,
        .resolution_x = 320,
        .resolution_y = 240,
        .input_bufaddr0 = (uint32_t)cam_output_buf,
        .input_bufaddr1 = 0,
        .output_bufaddr = (uint32_t)jpeg_output_buf,
        .output_bufsize = sizeof(jpeg_output_buf),
        .input_yy_table = yy_quant_table,
        .input_uv_table = uv_quant_table,
    };
    
    bflb_mjpeg_init(mjpeg_dev, &mjpeg_config);
    
    /* Start MJPEG encoding */
    bflb_mjpeg_start(mjpeg_dev);
    
    /* Or run in software mode for specific frame count */
    /* bflb_mjpeg_sw_run(mjpeg_dev, 1); */
    
    return 0;
}
```

### 5.3 MJPEG Decoding

```c
int mjpeg_decoding_example(void)
{
    /* Get MJPEG decoder device */
    mjdec_dev = bflb_device_get_by_name(MJDEC_DEVICE_NAME);
    if (mjdec_dev == NULL) {
        return -1;
    }
    
    /* Configure MJPEG decoder */
    struct bflb_mjdec_config_s mjdec_config = {
        .format = MJDEC_FORMAT_YUV420SP_NV21,
        .swap_enable = 1,  /* Enable ping-pong buffers */
        .resolution_x = 320,
        .resolution_y = 240,
        .head_size = 0,   /* Auto-detect from JPEG */
        .output_bufaddr0 = (uint32_t)y_frame_buf,
        .output_bufaddr1 = (uint32_t)uv_frame_buf,
    };
    
    bflb_mjdec_init(mjdec_dev, &mjdec_config);
    
    /* Set quantization table from quality (0-100) */
    bflb_mjdec_set_dqt_from_quality(mjdec_dev, 80);
    
    /* Start decoder */
    bflb_mjdec_start(mjdec_dev);
    
    return 0;
}

/* Decode a JPEG frame (call after frame is captured) */
void decode_jpeg_frame(uint8_t *jpeg_data, uint32_t jpeg_size)
{
    /* Push JPEG frame to decoder */
    bflb_mjdec_push_jpeg(mjdec_dev, jpeg_data);
    
    /* Wait for decode complete (polling or interrupt) */
    uint32_t timeout = 1000;
    while (timeout-- > 0) {
        uint32_t int_status = bflb_mjdec_get_intstatus(mjdec_dev);
        if (int_status & MJDEC_INTSTS_ONE_FRAME) {
            bflb_mjdec_int_clear(mjdec_dev, MJDEC_INTCLR_ONE_FRAME);
            printf("Decode complete\r\n");
            /* Y/UV data now available in y_frame_buf/uv_frame_buf */
            break;
        }
        bflb_m delay(1);
    }
}
```

### 5.4 DVP Raster Processing

```c
#include "bflb_dvp_raster.h"

static struct bflb_device_s *dvp_raster_dev;

int dvp_raster_example(void)
{
    dvp_raster_dev = bflb_device_get_by_name("dvp_raster");
    if (dvp_raster_dev == NULL) {
        return -1;
    }
    
    /* Configure DVP raster with rotation */
    struct bflb_dvp_raster_config_s raster_config = {
        .mode = DVP_RASTER_ROTATE_DEGREE_90,  /* Rotate 90 degrees */
        .resolution_x = 320,
        .resolution_y = 240,
        .y_frame_addr = (uint32_t)y_frame_buf,
        .y_frame_cnt = 2,    /* Double buffer */
        .uv_frame_addr = (uint32_t)uv_frame_buf,
        .uv_frame_cnt = 2,
    };
    
    bflb_dvp_raster_init(dvp_raster_dev, &raster_config);
    
    /* Enable DVP raster */
    bflb_dvp_raster_enable(dvp_raster_dev);
    
    /* Or use software mode */
    bflb_dvp_raster_sw_mode(dvp_raster_dev, true);
    bflb_dvp_raster_sw_mode_kick(dvp_raster_dev);
    
    return 0;
}
```

### 5.5 Complete Camera + MJPEG Capture/Decode Loop

```c
#include "bflb_cam.h"
#include "bflb_mjpeg.h"
#include "bflb_mjdec.h"

#define FRAME_WIDTH  320
#define FRAME_HEIGHT 240

static uint8_t cam_buf[FRAME_WIDTH * FRAME_HEIGHT * 2] __attribute__((aligned(16)));
static uint8_t jpeg_buf[64 * 1024] __attribute__((aligned(16)));
static uint8_t y_buf[FRAME_WIDTH * FRAME_HEIGHT] __attribute__((aligned(8)));
static uint8_t uv_buf[FRAME_WIDTH * FRAME_HEIGHT / 2] __attribute__((aligned(8)));

static volatile uint8_t frame_ready = 0;

void cam_irq_handler(int irq, void *arg)
{
    uint32_t status = bflb_cam_get_intstatus(cam_dev);
    
    if (status & CAM_INTSTS_NORMAL) {
        bflb_cam_int_clear(cam_dev, CAM_INTCLR_NORMAL);
        frame_ready = 1;
    }
}

int camera_mjpeg_capture_decode_loop(void)
{
    /* Initialize camera */
    cam_dev = bflb_device_get_by_name("cam");
    struct bflb_cam_config_s cam_cfg = {
        .input_format = CAM_INPUT_FORMAT_YUV422_YUYV,
        .resolution_x = FRAME_WIDTH,
        .resolution_y = FRAME_HEIGHT,
        .h_blank = 0,
        .pixel_clock = 12000000,
        .with_mjpeg = true,
        .input_source = CAM_INPUT_SOURCE_DVP,
        .output_format = CAM_OUTPUT_FORMAT_YUV422,
        .output_bufaddr = (uint32_t)cam_buf,
        .output_bufsize = sizeof(cam_buf),
    };
    bflb_cam_init(cam_dev, &cam_cfg);
    bflb_irq_request(cam_dev->irq_num, cam_irq_handler, NULL);
    bflb_cam_int_mask(cam_dev, CAM_INTMASK_NORMAL, false);
    
    /* Initialize MJPEG encoder */
    mjpeg_dev = bflb_device_get_by_name("mjpeg");
    struct bflb_mjpeg_config_s mjpeg_cfg = {
        .format = MJPEG_FORMAT_YUV422_YUYV,
        .quality = 80,
        .rows = FRAME_HEIGHT,
        .resolution_x = FRAME_WIDTH,
        .resolution_y = FRAME_HEIGHT,
        .input_bufaddr0 = (uint32_t)cam_buf,
        .input_bufaddr1 = 0,
        .output_bufaddr = (uint32_t)jpeg_buf,
        .output_bufsize = sizeof(jpeg_buf),
        .input_yy_table = NULL,
        .input_uv_table = NULL,
    };
    bflb_mjpeg_init(mjpeg_dev, &mjpeg_cfg);
    
    /* Initialize MJPEG decoder */
    mjdec_dev = bflb_device_get_by_name("mjdec");
    struct bflb_mjdec_config_s mjdec_cfg = {
        .format = MJDEC_FORMAT_YUV420SP_NV21,
        .swap_enable = 1,
        .resolution_x = FRAME_WIDTH,
        .resolution_y = FRAME_HEIGHT,
        .head_size = 0,
        .output_bufaddr0 = (uint32_t)y_buf,
        .output_bufaddr1 = (uint32_t)uv_buf,
    };
    bflb_mjdec_init(mjdec_dev, &mjdec_cfg);
    bflb_mjdec_set_dqt_from_quality(mjdec_dev, 80);
    
    /* Start all */
    bflb_cam_start(cam_dev);
    bflb_mjpeg_start(mjpeg_dev);
    bflb_mjdec_start(mjdec_dev);
    
    while (1) {
        if (frame_ready) {
            frame_ready = 0;
            
            /* Get encoded JPEG */
            uint8_t *jpeg_addr;
            uint32_t jpeg_size = bflb_mjpeg_get_frame_info(mjpeg_dev, &jpeg_addr);
            
            if (jpeg_size > 0) {
                printf("JPEG encoded: %u bytes\r\n", jpeg_size);
                
                /* Decode JPEG */
                bflb_mjdec_push_jpeg(mjdec_dev, jpeg_addr);
                
                /* Wait for decode */
                uint32_t timeout = 1000;
                while (timeout-- > 0) {
                    if (bflb_mjdec_get_intstatus(mjdec_dev) & MJDEC_INTSTS_ONE_FRAME) {
                        bflb_mjdec_int_clear(mjdec_dev, MJDEC_INTCLR_ONE_FRAME);
                        printf("YUV420 decoded: Y=%p, UV=%p\r\n", y_buf, uv_buf);
                        break;
                    }
                }
            }
            
            /* Pop processed frames */
            bflb_cam_pop_one_frame(cam_dev);
            bflb_mjpeg_pop_one_frame(mjpeg_dev);
            bflb_mjdec_pop_one_frame(mjdec_dev);
        }
        
        bflb_m delay(10);
    }
    
    return 0;
}
```

---

## 6. Pin Configuration Notes

DVP interface typically requires:
- **DVP_D0-D7** (or D0-D7): Data lines
- **DVP_PCLK**: Pixel clock
- **DVP_VSYNC**: Vertical sync
- **DVP_HSYNC**: Horizontal sync

Configure GPIO pins to DVP function using `bflb_gpio_iomux_func_sel()`.

---

## 7. Memory Requirements

| Format | Bytes per Pixel | 320x240 Frame Size |
|--------|----------------|-------------------|
| YUV422 YUYV | 2 | 153,600 |
| YUV420 NV12 | 1.5 | 115,200 |
| RGB565 | 2 | 153,600 |
| RGB888 | 3 | 230,400 |
| JPEG | Variable | Typically 10-30KB |

**Buffer Alignment Requirements:**
- Camera output: 16-byte alignment
- MJPEG input/output: 16-byte alignment  
- MJDEC output: 8-byte alignment
- DVP raster: 8-byte alignment
