# BL616/BL618 AI Hardware Acceleration Technical Documentation

## Overview

BL616 and BL618 are high-performance Wi-Fi 6 + Bluetooth LE 5.x combo chips launched by Bouffalo Lab, integrating a DNN (Deep Neural Network) hardware accelerator specifically optimized for edge AI inference scenarios. This chip series supports a variety of AI applications including image classification, object detection, keyword spotting (KWS), and gesture recognition.

As a multimedia-enhanced version of BL616, BL618 offers stronger AI inference capabilities with larger memory bandwidth and richer peripheral interfaces, making it especially suitable for AIoT application scenarios requiring image and voice processing.

## 1. Hardware Architecture

### 1.1 DNN/CNN Hardware Accelerator

BL616/BL618 integrates a dedicated CNN (Convolutional Neural Network) hardware accelerator module, controlled and managed through the multimedia clock management system (MM GLB) in the SDK. The following key features can be observed from the register definitions:

- **CNN Clock Enable**: `MM_GLB_REG_CNN_CLK_DIV_EN` is used to enable the CNN clock
- **CNN Clock Select**: `MM_GLB_REG_CNN_CLK_SEL` supports 2-bit clock source selection
- **CNN Clock Division**: `MM_GLB_REG_CNN_CLK_DIV` provides 3-bit division factor
- **CNN Software Reset**: `MM_GLB_SWRST_CNN` is used for module reset control

The CNN accelerator uses an independent clock domain design that can run independently of the CPU main frequency. This design allows AI inference tasks to execute efficiently without affecting system responsiveness.

### 1.2 Processor Configuration

BL616/BL618 feature a built-in RISC-V E907 processor core with the following computing capabilities:

- **FPU (Floating Point Unit)**: Supports single-precision and double-precision floating-point operations, accelerating activation function computations in AI models
- **DSP (Digital Signal Processor)**: Supports SIMD (Single Instruction Multiple Data) operations, accelerating convolution and matrix computations
- **Tightly Coupled Memory**: Used for fast data access in critical algorithms

### 1.3 Memory System

#### BL618 Multimedia Enhancement Features

BL618 has significantly enhanced memory configuration, which is key to supporting AI inference:

| Memory Type | Capacity | Purpose |
|---------|------|------|
| PSRAM | 4MB | Model weights, intermediate result caching, large image frame buffers |
| SRAM | 532KB | Runtime data, stacks, real-time processing data |

**PSRAM Address Mapping:**

- BL618DG X8 PSRAM: 0x88000000
- BL616 X8 PSRAM: 0xA8000000
- BL616CL X8 PSRAM: 0x88000000
- UHS PSRAM: 0x50000000

The 4MB large-capacity PSRAM design allows simultaneous storage of large AI model weights and intermediate results from multiple image frames, which is crucial for real-time image processing. In contrast, the 532KB SRAM is used for real-time data and system runtime states that require fast access.

## 2. Multimedia Interfaces

### 2.1 Camera/DVP Interface

BL616/BL618 supports the DVP (Digital Video Port) camera interface, which is the key interface for connecting image sensors to obtain real-time video streams. The image sensors supported in the SDK include:

| Model | Interface Type | Supported Chips |
|------|----------|----------|
| gc2053 | DVP/CSI | BL702/BL616/BL808 |
| gc0308 | DVP | BL702/BL616/BL808 |
| gc0328 | DVP | BL702/BL616/BL808 |
| ov2640 | DVP | BL702/BL616/BL808 |
| bf2013 | DVP | BL702/BL616/BL808 |
| bf20a6 | DVP/SPI | Multiple configurations |

The DVP interface supports various data formats and resolution configurations, with source selection via `CAM_INPUT_SOURCE_DVP` defined in `bflb_cam.h`. The camera interface works in conjunction with the CNN accelerator to form a complete visual AI processing pipeline.

### 2.2 Display Output Interface

BL618 supports the DPI (Display Parallel Interface) for outputting processed image results. DVP-to-display data transfer is implemented through the `bflb_dpi.c` driver, supporting multiple pixel format configurations.

## 3. AI Application Scenarios

### 3.1 Image Recognition (CNN)

The Convolutional Neural Network (CNN) hardware accelerator is the core of BL616/BL618 AI capabilities. This accelerator is specifically optimized for convolution operations, which are the most computationally intensive part of CNNs. Typical application scenarios include:

- **Image Classification**: Classifying input images into predefined categories such as animals, plants, products, etc.
- **Object Detection**: Locating multiple target objects in images and marking bounding boxes and categories
- **Face Detection**: Detecting face positions in images, usable for attendance systems, smart locks, etc.

The CNN accelerator supports multiple convolution optimization strategies, including sliding window optimization and Winograd algorithm acceleration, which can significantly improve inference speed while maintaining accuracy.

### 3.2 Keyword Spotting (KWS)

Keyword Spotting is a fundamental application of voice AI. BL616/BL618 implements low-power keyword spotting functionality through audio capture interfaces combined with software algorithms. A typical wake word detection flow includes:

1. **Audio Capture**: Collect microphone data via I2S or PDM interface
2. **Feature Extraction**: Convert time-domain audio signals to frequency-domain features (such as MFCC)
3. **Model Inference**: Use a small neural network to determine whether the wake word is present
4. **Result Output**: Trigger corresponding action upon wake word detection

The KWS system design emphasizes low power consumption and real-time performance. BL618's DSP extension instruction set can accelerate MFCC computation, while the dedicated CNN accelerator can run lightweight classification networks.

### 3.3 Gesture Recognition

Gesture recognition combines visual perception and temporal analysis, typically using the following technical approaches:

- **Spatial Feature Extraction**: Use CNN to extract spatial features of gestures from single frames
- **Temporal Modeling**: Use RNN/LSTM or 1D CNN to process temporal dependencies across multi-frame sequences
- **Classification Output**: Finally determine the gesture category

BL618's 4MB PSRAM provides ample buffering for gesture recognition, enabling caching of multiple image frames for temporal analysis, while 532KB SRAM ensures the low-latency data access required for real-time processing.

## 4. API Reference

### 4.1 DNN Initialization and Model Loading

The DNN (Deep Neural Network) module is the software abstraction layer for the CNN accelerator, responsible for model loading and inference scheduling. The following is a typical DNN usage flow:

```c
#include "bflb_dnn.h"

// DNN context handle
bflb_dnn_context_t dnn_ctx;

// DNN configuration parameters
bflb_dnn_config_t dnn_config = {
    .priority = 5,              // Task priority
    .timeout_ms = 1000,         // Inference timeout
    .psram_buffer = 1,          // Use PSRAM as data buffer
};

// Initialize DNN module
int ret = bflb_dnn_init(&dnn_ctx, &dnn_config);
if (ret < 0) {
    printf("DNN init failed: %d\r\n", ret);
    return ret;
}

// Load model data (model data typically stored in Flash or filesystem)
// Model format may be a vendor-specific binary format
ret = bflb_dnn_load_model(&dnn_ctx, model_data, model_size);
if (ret < 0) {
    printf("Model load failed: %d\r\n", ret);
    bflb_dnn_deinit(&dnn_ctx);
    return ret;
}

printf("DNN model loaded successfully\r\n");
```

### 4.2 Inference Execution

After model loading is complete, inference can be performed on input data. Input data typically comes from a camera or other sensors:

```c
// Prepare input data (assuming RGB image from camera)
// Image data is typically placed in PSRAM to save SRAM space
uint8_t *image_input = (uint8_t *)psram_malloc(224 * 224 * 3);
if (image_input == NULL) {
    printf("Failed to allocate PSRAM for input\r\n");
    return -1;
}

// Fill input buffer with image data from camera
// fill_image_data_from_camera(image_input, 224, 224);

// Prepare output buffer
float output_buffer[NUM_CLASSES];

// Create input and output tensor descriptors
bflb_dnn_tensor_t input_tensor = {
    .data = image_input,
    .shape = {1, 224, 224, 3},  // NCHW format
    .dtype = BFLB_DNN_DTYPE_UINT8,
};

bflb_dnn_tensor_t output_tensor = {
    .data = output_buffer,
    .shape = {1, NUM_CLASSES},
    .dtype = BFLB_DNN_DTYPE_FLOAT32,
};

// Execute inference
bflb_dnn_inference_t inference = {
    .input = &input_tensor,
    .output = &output_tensor,
};

ret = bflb_dnn_run_inference(&dnn_ctx, &inference);
if (ret < 0) {
    printf("Inference failed: %d\r\n", ret);
} else {
    // Parse output results
    int predicted_class = argmax(output_buffer, NUM_CLASSES);
    printf("Predicted class: %d\r\n", predicted_class);
}

// Clean up resources
psram_free(image_input);
```

### 4.3 Image Frame Input Processing

For real-time video stream processing, continuous multi-frame processing is required. The following is a typical frame processing flow:

```c
#include "bflb_cam.h"
#include "bflb_dnn.h"

// Assuming camera and DNN are already initialized
bflb_cam_device_t cam;
bflb_dnn_context_t dnn_ctx;

// Allocate frame buffers (use PSRAM for large images)
#define FRAME_WIDTH 320
#define FRAME_HEIGHT 240
#define FRAME_BUFFER_COUNT 2

uint8_t *frame_buffers[FRAME_BUFFER_COUNT];

for (int i = 0; i < FRAME_BUFFER_COUNT; i++) {
    frame_buffers[i] = psram_malloc(FRAME_WIDTH * FRAME_HEIGHT * 2);  // RGB565
}

// Allocate preprocessing buffer
uint8_t *preprocess_buffer = psram_malloc(224 * 224 * 3);

// Image preprocessing function
void preprocess_image(uint8_t *src, uint8_t *dst, int src_w, int src_h, int dst_size) {
    // 1. Scale image to model input size
    // 2. Color space conversion (if needed)
    // 3. Normalization
    // Using simple nearest-neighbor scaling as example
    scale_image_nearest_neighbor(src, dst, src_w, src_h, dst_size, dst_size);
    normalize_image(dst, dst_size * dst_size * 3);
}

// Main loop processing video frames
while (1) {
    // Wait for camera frame interrupt (simplified representation)
    bflb_cam_frame_t *frame = bflb_cam_get_frame(&cam, 1000);
    if (frame == NULL) {
        continue;
    }
    
    // Image preprocessing (scaling, normalization)
    preprocess_image(frame->data, preprocess_buffer, 
                     FRAME_WIDTH, FRAME_HEIGHT, 224);
    
    // Execute AI inference
    bflb_dnn_tensor_t input_tensor = {
        .data = preprocess_buffer,
        .shape = {1, 224, 224, 3},
        .dtype = BFLB_DNN_DTYPE_UINT8,
    };
    
    float output[NUM_CLASSES];
    bflb_dnn_tensor_t output_tensor = {
        .data = output,
        .shape = {1, NUM_CLASSES},
        .dtype = BFLB_DNN_DTYPE_FLOAT32,
    };
    
    bflb_dnn_inference_t inference = {
        .input = &input_tensor,
        .output = &output_tensor,
    };
    
    int ret = bflb_dnn_run_inference(&dnn_ctx, &inference);
    if (ret == 0) {
        // Process inference results
        handle_inference_result(output);
    }
    
    // Release frame buffer
    bflb_cam_release_frame(&cam, frame);
}

// Cleanup
for (int i = 0; i < FRAME_BUFFER_COUNT; i++) {
    psram_free(frame_buffers[i]);
}
psram_free(preprocess_buffer);
```

### 4.4 KWS Keyword Spotting

Keyword spotting is typically implemented using independent software algorithms working with audio capture peripherals:

```c
#include "bflb_kws.h"
#include "bflb_i2s.h"

// KWS configuration
bflb_kws_config_t kws_config = {
    .sample_rate = 16000,
    .frame_size = 512,
    .hop_size = 160,
    .num_mfcc = 13,
    .detection_threshold = 0.75,
    .model_type = KWS_MODEL_MLP,
};

// Initialize KWS
bflb_kws_context_t kws_ctx;
int ret = bflb_kws_init(&kws_ctx, &kws_config);
if (ret < 0) {
    printf("KWS init failed: %d\r\n", ret);
    return ret;
}

// Load keyword detection model
ret = bflb_kws_load_model(&kws_ctx, kws_model_data, kws_model_size);
if (ret < 0) {
    printf("KWS model load failed: %d\r\n", ret);
    return ret;
}

// Audio buffer
int16_t audio_buffer[512];

// KWS detection loop
while (1) {
    // Get audio data from I2S
    ret = bflb_i2s_read(&i2s_device, audio_buffer, 512);
    if (ret < 0) {
        continue;
    }
    
    // Run KWS detection
    float score = 0.0f;
    int detected = bflb_kws_detect(&kws_ctx, audio_buffer, 512, &score);
    
    if (detected) {
        printf("Keyword detected! score=%.2f\r\n", score);
        // Trigger subsequent processing, such as starting voice recognition or command processing
    }
}

// Cleanup
bflb_kws_deinit(&kws_ctx);
```

## 5. The Role of PSRAM in AI Inference

PSRAM (Pseudo Static RAM) is an external storage chip supported by BL618 that plays a crucial role in AI inference.

### 5.1 Model Weight Storage

Modern deep learning models have parameter counts ranging from millions to hundreds of millions. Taking the common MobileNetV2 as an example, its model size is approximately 14MB, far exceeding the chip's built-in SRAM capacity. Although 4MB PSRAM cannot store a complete large model, it can:

- **Hierarchical Storage Strategy**: Layer the model, keeping frequently used layer weights in PSRAM and loading infrequently used layers from Flash on demand
- **Model Sharding**: Split large models into multiple small segments, loading them into PSRAM in execution order
- **Hybrid Inference**: Some layers in PSRAM, some in Flash, with efficient DMA transfers

### 5.2 Intermediate Result Caching

During CNN inference, each layer's output feature maps need temporary storage:

- **Feature Map Caching**: Convolutional layer outputs need to be saved as inputs for the next layer; PSRAM's large capacity can cache multiple layers of feature maps
- **Multi-Task Sharing**: When running multiple AI tasks (such as simultaneous face detection and gesture recognition), PSRAM can separately store intermediate results for each task
- **Video Frame Buffering**: For temporal applications like gesture recognition, multiple image frames need to be cached; PSRAM space can hold dozens of QVGA frames

### 5.3 Image Frame Buffering

In image processing applications, PSRAM is used to store raw images from the camera:

```c
// JPEG decoding example - using PSRAM as decode buffer
ATTR_NOINIT_PSRAM_SECTION __ALIGNED(64) uint8_t jpeg_buff[32 * 1024];

// Display buffer
ATTR_NOINIT_PSRAM_SECTION __ALIGNED(64) uint8_t bpp_buff[1][320 * 240 * N_BPP];
```

PSRAM's 64-byte alignment feature is beneficial for DMA transfers, enabling zero-copy image processing with camera and display peripherals.

## 6. Camera and Display Coordination

BL618's multimedia processing pipeline supports a complete chain of Camera input, AI inference, and Display output.

### 6.1 Data Flow Architecture

```
┌─────────┐    DVP     ┌──────────┐   DMA/PSRAM   ┌─────────┐   AXI     ┌──────────┐
│ Camera  │ ────────▶  │  Camera  │ ───────────▶ │  PSRAM  │ ────────▶ │   CNN    │
│ Sensor  │            │ Interface│              │ Buffer  │           │Accelerator│
└─────────┘            └──────────┘              └─────────┘           └──────────┘
                                                                           │
                                                                           ▼
┌─────────┐    DVP     ┌──────────┐   DMA/PSRAM   ┌─────────┐           ┌──────────┐
│ Display │ ◀────────  │   DPI    │ ◀─────────── │  OSD    │ ◀──────── │ Results  │
│  Panel  │            │ Interface│              │ Buffer  │           │ Process  │
└─────────┘            └──────────┘              └─────────┘           └──────────┘
```

### 6.2 Complete Application Example

The following code demonstrates a complete face detection application flow:

```c
#include "bflb_cam.h"
#include "bflb_dnn.h"
#include "bflb_dpi.h"
#include "bl616_psram.h"

// System initialization
void ai_vision_system_init(void) {
    // 1. Initialize PSRAM
    bl_psram_init();
    
    // 2. Initialize camera interface
    bflb_cam_config_t cam_config = {
        .input_source = CAM_INPUT_SOURCE_DVP,
        .width = 320,
        .height = 240,
        .format = CAM_FORMAT_YUV422_YUYV,
    };
    bflb_cam_init(&cam, &cam_config);
    
    // 3. Initialize display interface
    bflb_dpi_config_t dpi_config = {
        .width = 320,
        .height = 240,
        .format = DPI_FORMAT_RGB565,
    };
    bflb_dpi_init(&dpi, &dpi_config);
    
    // 4. Initialize DNN accelerator
    bflb_dnn_config_t dnn_config = {
        .priority = 5,
        .timeout_ms = 2000,
        .psram_buffer = 1,
    };
    bflb_dnn_init(&dnn_ctx, &dnn_config);
    bflb_dnn_load_model(&dnn_ctx, face_detection_model, model_size);
}

// Main loop
void ai_vision_task(void *params) {
    uint8_t *camera_frame = psram_malloc(320 * 240 * 2);
    uint8_t *preprocessed = psram_malloc(224 * 224 * 3);
    uint8_t *osd_overlay = psram_malloc(320 * 240 * 2);
    
    while (1) {
        // Get camera frame
        bflb_cam_frame_t *frame = bflb_cam_get_frame(&cam, 1000);
        if (!frame) continue;
        
        // Copy to PSRAM buffer
        memcpy(camera_frame, frame->data, frame->size);
        bflb_cam_release_frame(&cam, frame);
        
        // Image preprocessing
        convert_yuv_to_rgb(camera_frame, preprocessed, 320, 240);
        resize_and_normalize(preprocessed, 224, 224);
        
        // AI Inference - face detection
        float boxes[10][4];  // Maximum 10 faces
        int face_count = run_face_detection(&dnn_ctx, preprocessed, boxes);
        
        // Generate OSD overlay (draw detection boxes)
        memset(osd_overlay, 0, 320 * 240 * 2);
        for (int i = 0; i < face_count; i++) {
            draw_rectangle(osd_overlay, boxes[i], 320, 240);
        }
        
        // Overlay OSD and display
        bflb_dpi_send_frame(&dpi, osd_overlay, 320 * 240 * 2);
    }
    
    psram_free(camera_frame);
    psram_free(preprocessed);
    psram_free(osd_overlay);
}
```

## 7. Performance Optimization Suggestions

### 7.1 Memory Access Optimization

- **PSRAM vs SRAM Selection**: Use SRAM for frequently accessed data, PSRAM for large buffers
- **Aligned Access**: Ensure data structures are 64-byte aligned for optimal DMA performance
- **Cache Optimization**: Make good use of processor cache to reduce PSRAM access latency

### 7.2 Inference Optimization

- **Model Quantization**: Quantize float32 models to int8, reducing memory usage by 75% and improving inference speed
- **Layer Fusion**: Fuse adjacent convolution, BatchNorm, and ReLU layers into a single operation
- **Input Size Optimization**: Choose input sizes closest to those used during model training to avoid extra scaling computations

### 7.3 Power Consumption Optimization

- **Dynamic Frequency Scaling**: Adjust CNN clock frequency dynamically based on inference complexity
- **Interrupt-Driven**: Use interrupts instead of polling for camera frames and inference completion events
- **Sleep Strategy**: Put the CPU into low-power mode when idle, keeping only the CNN accelerator listening

## 8. Notes

### 8.1 Development Limitations

- **Model Size**: Limited by PSRAM capacity, a single model typically should not exceed 2MB (after quantization)
- **Real-Time Performance**: Complex models may cause inference time exceeding 100ms; trade-offs must be made based on application scenarios
- **Memory Layout**: PSRAM address mapping varies by chip model; always refer to the corresponding chip datasheet

### 8.2 Debugging Suggestions

- **Verify Hardware First**: Ensure Camera, DVP, PSRAM, and other peripherals are working correctly before AI development
- **Incremental Testing**: Test data acquisition first, then preprocessing, and finally integrate AI inference
- **Resource Monitoring**: Regularly check memory usage to avoid memory leaks causing system crashes

### 8.3 Common Problem Troubleshooting

| Problem | Possible Cause | Solution |
|------|----------|----------|
| Inference returns error | Model format mismatch | Verify model is compatible with DNN accelerator version |
| Abnormal image display | Frame buffer format error | Check Camera and DPI pixel format configuration |
| Memory allocation failure | PSRAM not initialized | Call bl_psram_init() to initialize PSRAM |
| Incorrect inference results | Inconsistent input preprocessing | Ensure preprocessing matches the data processing used during model training |

## References

- [Bouffalo SDK Official Documentation](https://github.com/bouffalo-lab/bouffalo_sdk)
- [BL618 Reference Manual](./bl618.md)
- [PSRAM Driver Usage Guide](./psram.md)
- [Camera Interface Development Guide](./camera.md)
- [DNN Model Conversion Tool Documentation](./model_converter.md)
- Bouffalo Lab Official SDK Repository: https://github.com/bouffalo-lab/bouffalo_sdk
- BL616/BL618 Chip Series Datasheet
