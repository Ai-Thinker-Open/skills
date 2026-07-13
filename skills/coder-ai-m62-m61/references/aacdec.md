# PVMP4AudioDecoder AAC Software Decoder

## Overview

PVMP4AudioDecoder is an open-source AAC-LC/AAC+/eAAC+ software decoder developed by PacketVideo, integrated into the `multimedia/aacdec` component of Bouffalo SDK. The decoder is implemented entirely in ANSI C and is suitable for audio playback scenarios in embedded systems.

BL618 implements software decoding of AAC audio format through this decoder component, supporting the following audio types:

| Audio Type | Description | Sample Rate Range |
|---------|------|-----------|
| AAC-LC | Low Complexity AAC | 8-96 kHz |
| AACPlus | AAC+ (with SBR) | 24-48 kHz input, 2x upsampled output |
| enhanced AACPlus | Enhanced AAC+ (with SBR + PS) | Same as above |

## Header Files

```c
#include "pvmp4audiodecoder_api.h"
#include "pv_audio_type_defs.h"
```

## Key Data Types

### tPVMP4AudioDecoderExternal

Decoder external control structure, used for exchanging input/output data with the decoder library:

```c
typedef struct tPVMP4AudioDecoderExternal
{
    /* Input fields */
    UChar  *pInputBuffer;              // AAC bitstream input buffer
    Int     inputBufferCurrentLength; // Number of valid bytes in input buffer
    Int     inputBufferMaxLength;      // Total size of input buffer
    Int     desiredChannels;           // Desired output channels (1=mono, 2=stereo)

    /* Input/Output fields */
    Int     inputBufferUsedLength;     // Number of bytes consumed by decoding
    Int32   remainderBits;            // Cross-frame remaining bits

    /* Output fields */
    Int32   samplingRate;             // Sampling rate (samples/sec)
    Int32   bitRate;                  // Bit rate (bits/sec)
    Int     encodedChannels;          // Original channel count in bitstream
    Int     frameLength;              // Output PCM samples per channel (fixed 1024)
    Int     audioObjectType;          // Audio object type
    Int     extendedAudioObjectType;  // Extended audio object type

    /* AAC+ related */
    Int16  *pOutputBuffer;            // PCM main output buffer (2048 samples)
    Int16  *pOutputBuffer_plus;       // AAC+ output buffer
    Int32   aacPlusUpsamplingFactor; // Upsampling factor (usually 2)
    Bool    aacPlusEnabled;           // AAC+ enable flag

    /* Control flags */
    Bool    repositionFlag;           // Seek flag (set during fast-forward/rewind)
    tPVMP4AudioDecoderOutputFormat outputFormat; // Output format
} tPVMP4AudioDecoderExternal;
```

### AACDecStatus (Decode Status Codes)

```c
typedef enum ePVMP4AudioDecoderErrorCode
{
    AAC_SUCCESS           =  0,  // Decode successful
    AAC_INVALID_FRAME     = 10,  // Invalid frame
    AAC_INCOMPLETE_FRAME  = 20,  // Incomplete input data
    AAC_LOST_FRAME_SYNC   = 30   // Frame sync lost
} AACDecStatus;
```

### STREAMTYPE (Bitstream Type)

```c
typedef enum
{
    AAC       = 0,   // Regular AAC-LC
    AACPLUS   = 1,   // AAC+ (SBR)
    ENH_AACPLUS = 2  // Enhanced AAC+ (SBR + PS)
} STREAMTYPE;
```

### Output Format Enum

```c
typedef enum ePVMP4AudioDecoderOutputFormat
{
    OUTPUTFORMAT_16PCM_GROUPED     = 0,  // Grouped format: LLLL...RRRR
    OUTPUTFORMAT_16PCM_INTERLEAVED = 1   // Interleaved format: LRLRLR...
} tPVMP4AudioDecoderOutputFormat;
```

## Memory Requirements

### AACDecMemReq()

Gets the memory size required by the decoder. Must be called before initializing the decoder to allocate sufficient memory.

```c
UInt32 AACDecMemReq(void);
```

**Return value:** Number of bytes required by the decoder

**Example:**
```c
UInt32 memSize = AACDecMemReq();
void *pDecoderMem = malloc(memSize);
if (pDecoderMem == NULL) {
    // Memory allocation failed
}
```

## Core API

### AACInitDecoder() - Initialize Decoder

```c
Int AACInitDecoder(
    tPVMP4AudioDecoderExternal *pExt,  // Decoder external structure pointer
    void                       *pMem  // Decoder working memory
);
```

**Parameter description:**
- `pExt`: Pointer to `tPVMP4AudioDecoderExternal` structure
- `pMem`: Pointer to the memory block obtained via `AACDecMemReq()`

**Return value:** `AAC_SUCCESS` (0) indicates success

**Initialization steps:**
1. Call `AACDecMemReq()` to get required memory size
2. Allocate memory block
3. Initialize `tPVMP4AudioDecoderExternal` structure
4. Call `AACInitDecoder()` to complete initialization

---

### AACDecodeFrame() - Decode One Frame

```c
Int AACDecodeFrame(
    tPVMP4AudioDecoderExternal *pExt,  // Decoder external structure
    void                       *pMem  // Decoder working memory
);
```

**Input requirements:**
- `pInputBuffer`: Pointer to buffer containing one frame of AAC data
- `inputBufferCurrentLength`: Number of input data bytes
- `pOutputBuffer`: Pointer to output buffer of at least 2048 samples
- `desiredChannels`: Desired number of output channels

**Output results:**
- `inputBufferUsedLength`: Actual number of input bytes consumed
- `samplingRate`: Decoded sampling rate
- `frameLength`: Number of output PCM samples (usually 1024)
- `pOutputBuffer`: 16-bit PCM data

**Return values:**
- `AAC_SUCCESS`: Decode successful
- `AAC_INVALID_FRAME`: Invalid frame
- `AAC_INCOMPLETE_FRAME`: Insufficient input data

---

### AACDecodeAudioSpecificConfig() - Parse ASC

Parses Audio Specific Config (ASC) information to extract audio parameters from the bitstream.

```c
Int AACDecodeAudioSpecificConfig(
    tPVMP4AudioDecoderExternal *pExt,  // Decoder external structure
    void                       *pMem  // Decoder working memory
);
```

**Typical application scenarios:**
- Extract sampling rate and channel configuration from ADTS headers
- Validate configuration when manually setting audio parameters

---

### AACFreeDecoder() - Release Decoder

Since the decoder is implemented purely in software, there is no separate release function. Simply call `free()` on the previously allocated memory block:

```c
free(pDecoderMem);
pDecoderMem = NULL;
```

**Note:** Ensure there are no ongoing decoding operations before releasing.

## Output Format

The decoder outputs **PCM 16-bit interleaved** stereo data:

```
Sample sequence: L0 R0 L1 R1 L2 R2 ... L1023 R1023
Byte order:     Little Endian
Channel format: Interleaved
Sample range:   -32768 ~ 32767
```

For mono output, the buffer only contains left channel data.

**Output buffer size calculation:**
```c
// Stereo: 1024 samples/channel × 2 channels × 2 bytes = 4096 bytes
// Mono:   1024 samples/channel × 1 channel  × 2 bytes = 2048 bytes
```

## Code Examples

### Complete Decode Flow

```c
#include "pvmp4audiodecoder_api.h"
#include "pv_audio_type_defs.h"
#include <stdlib.h>
#include <stdio.h>

int aac_decode_example(const uint8_t *aac_data, uint32_t aac_len,
                       int16_t *pcm_out, uint32_t *pcm_samples)
{
    tPVMP4AudioDecoderExternal decExt = {0};
    UInt32 memSize;
    void *pDecoderMem;
    Int ret;

    /* Step 1: Get memory requirements */
    memSize = AACDecMemReq();

    /* Step 2: Allocate decoder memory */
    pDecoderMem = malloc(memSize);
    if (pDecoderMem == NULL) {
        printf("Decoder memory allocation failed\r\n");
        return -1;
    }

    /* Step 3: Initialize external structure */
    decExt.pInputBuffer          = (UChar *)aac_data;
    decExt.inputBufferCurrentLength = aac_len;
    decExt.inputBufferMaxLength  = aac_len;
    decExt.pOutputBuffer         = pcm_out;
    decExt.pOutputBuffer_plus    = NULL;
    decExt.desiredChannels       = 2;  // Output stereo
    decExt.outputFormat          = OUTPUTFORMAT_16PCM_INTERLEAVED;
    decExt.aacPlusEnabled        = TRUE;
    decExt.aacPlusUpsamplingFactor = 2;
    decExt.repositionFlag        = FALSE;
    decExt.inputBufferUsedLength = 0;
    decExt.remainderBits         = 0;

    /* Step 4: Initialize decoder */
    ret = AACInitDecoder(&decExt, pDecoderMem);
    if (ret != AAC_SUCCESS) {
        printf("Decoder init failed: %d\r\n", ret);
        free(pDecoderMem);
        return -1;
    }

    /* Step 5: Decode one frame */
    ret = AACDecodeFrame(&decExt, pDecoderMem);
    if (ret == AAC_SUCCESS) {
        printf("Decoded %d samples @ %d Hz\r\n",
               decExt.frameLength, decExt.samplingRate);
        *pcm_samples = decExt.frameLength * decExt.encodedChannels;
    } else {
        printf("Decode failed: %d\r\n", ret);
    }

    /* Step 6: Release resources */
    free(pDecoderMem);

    return ret;
}
```

### Continuous Multi-Frame Decoding

```c
int aac_decode_stream(const uint8_t *aac_stream, uint32_t stream_len,
                      int16_t *pcm_buf, uint32_t max_pcm_samples)
{
    tPVMP4AudioDecoderExternal decExt = {0};
    void *pDecoderMem;
    UInt32 memSize;
    Int ret;
    uint32_t total_samples = 0;
    uint32_t offset = 0;

    memSize = AACDecMemReq();
    pDecoderMem = malloc(memSize);
    if (!pDecoderMem) return -1;

    /* Initialize (error checking omitted) */
    decExt.pOutputBuffer    = pcm_buf;
    decExt.desiredChannels  = 2;
    decExt.outputFormat     = OUTPUTFORMAT_16PCM_INTERLEAVED;
    decExt.aacPlusEnabled   = TRUE;
    decExt.aacPlusUpsamplingFactor = 2;

    AACInitDecoder(&decExt, pDecoderMem);

    /* Loop decode until data exhausted */
    while (offset < stream_len) {
        decExt.pInputBuffer           = (UChar *)&aac_stream[offset];
        decExt.inputBufferCurrentLength = stream_len - offset;
        decExt.inputBufferUsedLength  = 0;

        ret = AACDecodeFrame(&decExt, pDecoderMem);
        if (ret != AAC_SUCCESS) {
            break;
        }

        offset += decExt.inputBufferUsedLength;
        total_samples += decExt.frameLength * decExt.encodedChannels;

        /* Check output buffer capacity */
        if (total_samples > max_pcm_samples) {
            break;
        }

        /* Update output buffer pointer */
        decExt.pOutputBuffer = &pcm_buf[total_samples];
    }

    free(pDecoderMem);
    return total_samples;
}
```

## Audio Object Types

MPEG-4 audio object types supported by the decoder (defined in `e_tMP4AudioObjectType.h`):

| Type Value | Name | Description |
|-------|------|------|
| 1 | AAC_MAIN | AAC Main profile |
| 2 | AAC_LC | Low Complexity (most commonly used) |
| 3 | AAC_SSR | Scalable Sampling Rate |
| 4 | LTP | Long Term Prediction |
| 5 | SBR | Spectral Band Replication |
| 17 | ER_AAC_LC | Error Resilient AAC-LC |
| 23 | ER_AAC_LD | Error Resilient AAC-LD |
| 29 | PS | Parametric Stereo |

## Notes

1. **Memory Alignment**: Allocated decoder memory should be 4-byte aligned

2. **Input Buffer**: The decoder processes data frame by frame; `inputBufferUsedLength` indicates the actual number of bytes consumed

3. **AAC+ Output**: When AAC+ decoding is enabled, an additional `pOutputBuffer_plus` buffer (2048 samples) is required

4. **Thread Safety**: The decoder itself does not guarantee thread safety; manual synchronization is needed for multi-threaded use

5. **Frame Length**: Output frame length is fixed at 1024 samples/channel, independent of sampling rate

## References

- [PVMP4AudioDecoder API Header](../../workspase/BL618Claw/bouffalo_sdk/components/multimedia/aacdec/include/pvmp4audiodecoder_api.h)
- [PV Audio Type Definitions](../../workspase/BL618Claw/bouffalo_sdk/components/multimedia/aacdec/include/pv_audio_type_defs.h)
- [MPEG-4 Audio Object Types](../../workspase/BL618Claw/bouffalo_sdk/components/multimedia/aacdec/include/e_tmp4audioobjecttype.h)
- ISO/IEC 14496-3:2001 - MPEG-4 Audio Coding Standard
