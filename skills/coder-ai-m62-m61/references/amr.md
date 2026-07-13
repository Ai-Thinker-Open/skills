# AMR Speech Codec

## Overview

AMR (Adaptive Multi-Rate) is a family of speech codecs defined by the 3GPP standard, widely used in voice call scenarios in mobile communications. The AMR family includes two main specifications:

| Type | Sample Rate | Bit Rate Range | Frame Duration | Application Scenario |
|------|--------|------------|--------|----------|
| AMR-NB (Narrowband) | 8 kHz | 4.75 ~ 12.2 kbps | 20 ms | Traditional mobile voice calls |
| AMR-WB (Wideband) | 16 kHz | 6.6 ~ 23.85 kbps | 20 ms | VoLTE, HD voice calls |

The BL618 chip features a built-in AMR hardware accelerator supporting both AMR-NB and AMR-WB decoding, suitable for product development such as VoIP phones and wireless intercoms.

---

## AMR-NB Decoder

AMR-NB (Adaptive Multi-Rate Narrowband) is a speech codec designed for 8 kHz sample rate, originally used in GSM networks and later adopted by the 3GPP standard.

### Frame Types

AMR-NB supports 8 encoding modes (bit rates):

| Mode | Bit Rate | Bits per Frame | Purpose |
|------|--------|------------|------|
| 0 | 4.75 kbps | 95 | Lowest bit rate |
| 1 | 5.15 kbps | 103 | - |
| 2 | 5.90 kbps | 118 | - |
| 3 | 6.70 kbps | 134 | Default recommended |
| 4 | 7.40 kbps | 148 | - |
| 5 | 7.95 kbps | 159 | - |
| 6 | 10.2 kbps | 204 | Highest bit rate (ETSI) |
| 7 | 12.2 kbps | 244 | Highest bit rate (AMR) |

Additionally includes SID (Silence Descriptor) frames for transmitting background noise information.

### Data Structures

The AMR-NB decoder uses a `void *` type internal state pointer. Developers must first query memory requirements, allocate a sufficient buffer, then initialize.

### API Functions

#### Memory_Associated_AMRNB_Decoder

Gets the memory size required by the AMR-NB decoder.

```c
Word32 Memory_Associated_AMRNB_Decoder(void);
```

**Return value:** Number of bytes required by the decoder

**Example:**
```c
Word32 mem_size = Memory_Associated_AMRNB_Decoder();
printf("AMR-NB decoder requires %lu bytes\r\n", mem_size);
```

#### Decoder_Index_AMRNB_Interface_init

Initializes an AMR-NB decoder instance.

```c
void Decoder_Index_AMRNB_Interface_init(void *state_data);
```

**Parameters:**
- `state_data` - Pointer to an allocated memory region for storing decoder internal state

**Example:**
```c
void *amrnb_state = malloc(mem_size);
if (amrnb_state == NULL) {
    // Memory allocation failed
    return -1;
}
Decoder_Index_AMRNB_Interface_init(amrnb_state);
```

#### Decoder_Index_AMRNB_Interface

Decodes one frame of AMR-NB speech data.

```c
Word16 Decoder_Index_AMRNB_Interface(
    void           *state_data,       // Decoder state pointer
    enum Frame_Type_3GPP frame_type, // Frame type (0-8)
    UWord8         *speech_bits_ptr,  // Input bitstream
    Word16         *raw_pcm_buffer,    // Output PCM buffer
    bitstream_format input_format     // Input format (WMF/IF2/ETS)
);
```

**Parameters:**
- `state_data` - Decoder state pointer (initialized by init)
- `frame_type` - AMR-NB frame type, enum values: `AMR_475, AMR_515, AMR_59, AMR_67, AMR_74, AMR_795, AMR_102, AMR_122, AMR_SID`
- `speech_bits_ptr` - Pointer to the compressed bitstream
- `raw_pcm_buffer` - Pointer to the output PCM buffer (needs at least 160 Word16 values)
- `input_format` - Input bitstream format: `WMF` (Wireless MSF), `IF2` (Interface Format 2), `ETS` (ETS 300 725)

**Return value:** 0 indicates success

**Output PCM:** Each frame outputs 160 samples (20ms @ 8kHz)

#### Decoder_Index_AMRNB_Interface_exit

Releases AMR-NB decoder resources.

```c
void Decoder_Index_AMRNB_Interface_exit(void *state_data);
```

**Parameters:**
- `state_data` - Decoder state pointer

**Example:**
```c
Decoder_Index_AMRNB_Interface_exit(amrnb_state);
free(amrnb_state);
amrnb_state = NULL;
```

---

## AMR-WB Decoder

AMR-WB (Adaptive Multi-Rate Wideband) is a wideband speech codec designed for 16 kHz sample rate, providing more natural voice quality and better intelligibility.

### Frame Types

AMR-WB supports 9 encoding modes:

| Mode | Bit Rate | Bits per Frame | Purpose |
|------|--------|------------|------|
| 0 | 6.60 kbps | 132 | Lowest bit rate |
| 1 | 8.85 kbps | 177 | - |
| 2 | 12.65 kbps | 253 | - |
| 3 | 14.25 kbps | 285 | - |
| 4 | 15.85 kbps | 317 | - |
| 5 | 18.25 kbps | 365 | - |
| 6 | 19.85 kbps | 397 | - |
| 7 | 23.05 kbps | 461 | - |
| 8 | 23.85 kbps | 477 | Highest bit rate |

Also includes SID frames for transmitting comfort noise parameters.

### API Functions

#### AMR_WB_get_memreq

Gets the memory size required by the AMR-WB decoder.

```c
Word32 AMR_WB_get_memreq(void);
```

**Return value:** Number of bytes required by the decoder

#### AMR_WB_dec_init

Initializes an AMR-WB decoder instance.

```c
int AMR_WB_dec_init(void **spd_state, void *st, int16 **scratch_mem);
```

**Parameters:**
- `spd_state` - Output parameter, returns the decoder state pointer
- `st` - Allocated memory buffer
- `scratch_mem` - Output parameter, returns temporary working memory pointer

**Return value:** 0 indicates success

#### AMR_WB_decode

Decodes one frame of AMR-WB speech data.

```c
int AMR_WB_decode(
    int16  mode,           // Encoding mode (0-8)
    int16  prms[],         // Input parameter vector
    int16  synth16k[],     // Output synthesized speech
    int16 *frame_length,   // Output frame length
    void  *spd_state,      // Decoder state pointer
    int16  frame_type,     // Frame type
    int16  scratch_mem[]   // Temporary working memory
);
```

**Parameters:**
- `mode` - AMR-WB encoding mode (0-8)
- `prms` - Pointer to compressed bitstream parameters
- `synth16k` - Output buffer, stores 16kHz sampled PCM speech (needs at least 320 int16 values)
- `frame_length` - Output parameter, actual number of output samples
- `spd_state` - Decoder state pointer
- `frame_type` - AMR-WB frame type
- `scratch_mem` - Temporary working memory

**Return value:** 0 indicates success

**Output PCM:** Each frame outputs 320 samples (20ms @ 16kHz)

#### AMR_WB_dec_deinit

Releases AMR-WB decoder resources.

```c
void AMR_WB_dec_deinit(void *spd_state);
```

**Parameters:**
- `spd_state` - Decoder state pointer

---

## Usage Flows

### AMR-NB Complete Decode Flow

```c
#include "amrdecode.h"
#include "frame_type_3gpp.h"

// 1. Get memory requirements
Word32 mem_size = Memory_Associated_AMRNB_Decoder();

// 2. Allocate memory
void *amrnb_state = malloc(mem_size);
if (amrnb_state == NULL) {
    return -1;
}

// 3. Initialize decoder
Decoder_Index_AMRNB_Interface_init(amrnb_state);

// 4. Allocate input and output buffers
UWord8 speech_bits[32];        // Input bitstream
Word16 pcm_buffer[160];       // Output PCM (160 samples @ 8kHz)

// 5. Loop decode each frame
enum Frame_Type_3GPP frame_type = AMR_67;  // Assume using 6.7kbps mode
for (int i = 0; i < frame_count; i++) {
    // Fill compressed bitstream into speech_bits
    // ...

    // Decode one frame
    Decoder_Index_AMRNB_Interface(
        amrnb_state,
        frame_type,
        speech_bits,
        pcm_buffer,
        IF2  // Interface Format 2
    );

    // Process PCM data (pcm_buffer contains 160 16-bit samples)
    // ...
}

// 6. Destroy decoder
Decoder_Index_AMRNB_Interface_exit(amrnb_state);
free(amrnb_state);
```

### AMR-WB Complete Decode Flow

```c
#include "pvamrwbdecoder.h"

// 1. Get memory requirements
Word32 mem_size = AMR_WB_get_memreq();

// 2. Allocate memory
void *amrwb_buf = malloc(mem_size);
void *amrwb_state = NULL;
int16 *scratch_mem = NULL;

// 3. Initialize decoder
AMR_WB_dec_init(&amrwb_state, amrwb_buf, &scratch_mem);

// 4. Allocate input and output buffers
int16 prms[64];                // Input parameters
int16 synth16k[320];           // Output PCM (320 samples @ 16kHz)
int16 frame_length = 0;

// 5. Loop decode each frame
for (int i = 0; i < frame_count; i++) {
    // Fill compressed parameters into prms
    // ...

    // Decode one frame
    AMR_WB_decode(
        2,                      // mode 2 (12.65 kbps)
        prms,
        synth16k,
        &frame_length,
        amrwb_state,
        0,                      // frame_type
        scratch_mem
    );

    // Process PCM data (synth16k contains frame_length 16-bit samples)
    // ...
}

// 6. Destroy decoder
AMR_WB_dec_deinit(amrwb_state);
free(amrwb_buf);
```

---

## Sample Rates and Frame Lengths

| Codec | Sample Rate | Samples per Frame | Frame Duration |
|----------|--------|------------|--------|
| AMR-NB | 8 kHz | 160 | 20 ms |
| AMR-WB | 16 kHz | 320 | 20 ms |

**Calculation Example:**
- AMR-NB: 8000 Hz × 0.02 s = 160 samples
- AMR-WB: 16000 Hz × 0.02 s = 320 samples

---

## Input Format Description

AMR bitstream supports multiple encapsulation formats:

| Format | Description | Applicable Scenario |
|------|------|----------|
| WMF | Wireless MSF format | Early GSM implementations |
| IF2 | Interface Format 2 | 3GPP standard recommendation |
| ETS | ETS 300 725 format | European Telecommunications Standard |

BL618 SDK recommends using the IF2 format, which is consistent with the 3GPP TS 26.101 specification.

---

## Notes

1. **Memory Alignment**: The allocated decoder state buffer should be 4-byte aligned to ensure access efficiency on ARM architecture.

2. **Frame Type Synchronization**: The input frame type (bit rate mode) must be correctly identified before decoding. An incorrect frame type will cause decoding failure or output noise.

3. **PCM Output Range**: The decoded PCM data is 16-bit signed integer, range [-32768, 32767], requiring appropriate volume adjustment before feeding to the DAC.

4. **Edge Cases**: For damaged or lost frames, it is recommended to use the previous frame's decode result for comfort noise filling to improve the listening experience.

5. **Thread Safety**: Decoder instances cannot be shared across threads. Each concurrent decode channel requires an independently allocated decoder state.

---

## References

- 3GPP TS 26.073: ANSI-C code for the Adaptive Multi-Rate (AMR) speech codec
- 3GPP TS 26.173: ANSI-C code for the Adaptive Multi-Rate - Wideband (AMR-WB) speech codec
- 3GPP TS 26.101: Frame structure for Adaptive Multi-Rate - Wideband (AMR-WB) speech codec
