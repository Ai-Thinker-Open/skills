# Speex Speech Codec

## Overview

Speex is an open-source speech codec developed by the Xiph.Org Foundation, based on the CELP (Code Excited Linear Prediction) algorithm, designed specifically for VoIP (Voice over IP) applications. Unlike other commercial codecs, Speex uses the BSD license and is freely available for both commercial and non-commercial projects.

Speex supports three sampling rate modes:

| Mode | Sampling Rate | Typical Application Scenario |
|------|--------------|------------------------------|
| Narrowband | 8 kHz | Traditional telephony, voice calls |
| Wideband | 16 kHz | Video conferencing, IP voice |
| Ultra-Wideband | 32 kHz | High-quality voice transmission |

The BL618 chip integrates the Speex codec library, which can be used to develop multimedia applications such as VoIP phones, voice chat, and voice recording.

## Key Data Types

### SpeexBits

The `SpeexBits` structure is used to manage the packing and unpacking of bitstreams:

```c
typedef struct SpeexBits {
   char *chars;      // Raw data buffer
   int   nbBits;     // Total number of bits stored in the stream
   int   charPtr;    // Byte "cursor" position
   int   bitPtr;     // Bit "cursor" position within the current byte
   int   owner;      // Whether the structure "owns" the raw buffer
   int   overflow;   // Set to 1 when attempting to read beyond valid data
   int   buf_size;   // Allocated buffer size
} SpeexBits;
```

### SpeexMode

The `SpeexMode` structure defines a codec mode, including encoder/decoder initialization, encoding, decoding, and control function pointers:

```c
typedef struct SpeexMode {
   const void       *mode;          // Low-level mode data pointer
   mode_query_func   query;         // Mode query function
   const char       *modeName;      // Mode name
   int               modeID;        // Mode ID
   encoder_init_func enc_init;      // Encoder initialization function
   encoder_destroy_func enc_destroy; // Encoder destroy function
   encode_func       enc;           // Frame encoding function
   decoder_init_func dec_init;      // Decoder initialization function
   decoder_destroy_func dec_destroy; // Decoder destroy function
   decode_func       dec;           // Frame decoding function
   encoder_ctl_func  enc_ctl;       // Encoder control function
   decoder_ctl_func  dec_ctl;       // Decoder control function
} SpeexMode;
```

### SpeexEncoderState and SpeexDecoderState

The encoder state and decoder state are opaque pointer types maintained internally by the library. Users operate the codec through these pointers but should not directly access their internal structures:

```c
void *speex_encoder_init(const SpeexMode *mode);
void *speex_decoder_init(const SpeexMode *mode);
```

## Core API

### Codec Initialization and Destruction

```c
// Initialize narrowband encoder
void *speex_encoder_init(const SpeexMode *mode);

// Initialize decoder
void *speex_decoder_init(const SpeexMode *mode);

// Destroy encoder and release resources
void speex_encoder_destroy(void *state);

// Destroy decoder and release resources
void speex_decoder_destroy(void *state);
```

### Encoding and Decoding

```c
// Encode one frame of speech (float input)
// state: encoder state
// in: input PCM data, range ±2^15
// bits: bitstream output
// Return: 0 means frame does not need transmission (DTX mode only), 1 means normal
int speex_encode(void *state, float *in, SpeexBits *bits);

// Encode one frame of speech (integer input)
int speex_encode_int(void *state, spx_int16_t *in, SpeexBits *bits);

// Decode one frame of speech (float output)
// bits: bitstream input (NULL indicates packet loss)
// out: decoded output PCM data
// Return: 0 normal, -1 end of stream, -2 corrupted stream
int speex_decode(void *state, SpeexBits *bits, float *out);

// Decode one frame of speech (integer output)
int speex_decode_int(void *state, SpeexBits *bits, spx_int16_t *out);
```

### Bitstream Operations

```c
// Initialize SpeexBits structure
void speex_bits_init(SpeexBits *bits);

// Initialize using a pre-allocated buffer
void speex_bits_init_buffer(SpeexBits *bits, void *buff, int buf_size);

// Read data from a memory region to initialize the bitstream
void speex_bits_read_from(SpeexBits *bits, const char *bytes, int len);

// Write bitstream contents to memory
// Returns the number of bytes written
int speex_bits_write(SpeexBits *bits, char *bytes, int max_len);

// Destroy SpeexBits and release resources
void speex_bits_destroy(SpeexBits *bits);

// Reset the bitstream to initial state
void speex_bits_reset(SpeexBits *bits);
```

### Mode Retrieval

```c
// Get the SpeexMode pointer for the specified mode
// mode: SPEEX_MODEID_NB (0), SPEEX_MODEID_WB (1), SPEEX_MODEID_UWB (2)
const SpeexMode *speex_lib_get_mode(int mode);
```

Predefined mode constants:

```c
extern const SpeexMode speex_nb_mode;   // Narrowband mode
extern const SpeexMode speex_wb_mode;   // Wideband mode
extern const SpeexMode speex_uwb_mode;  // Ultra-Wideband mode
```

### Parameter Control

`speex_encoder_ctl` and `speex_decoder_ctl` are used to set/get codec parameters, with usage similar to ioctl:

```c
int speex_encoder_ctl(void *state, int request, void *ptr);
int speex_decoder_ctl(void *state, int request, void *ptr);
```

Common control commands:

| Control Command | Description | Value Range |
|----------------|-------------|-------------|
| `SPEEX_SET_QUALITY` | Set encoding quality | 0~10 |
| `SPEEX_GET_FRAME_SIZE` | Get frame size | - |
| `SPEEX_SET_COMPLEXITY` | Set encoding complexity | 0~10 |
| `SPEEX_SET_VBR` | Set variable bitrate | 0 or 1 |
| `SPEEX_SET_VBR_QUALITY` | Set VBR quality | 0~10 |
| `SPEEX_SET_ABR` | Set average bitrate | bps |
| `SPEEX_SET_DTX` | Set discontinuous transmission | 0 or 1 |
| `SPEEX_SET_SAMPLING_RATE` | Set sampling rate | Hz |
| `SPEEX_GET_BITRATE` | Get current bitrate | - |
| `SPEEX_SET_ENH` | Set enhancement (decoder) | 0 or 1 |
| `SPEEX_SET_HIGHPASS` | Set high-pass filter | 0 or 1 |

## Quality Levels

Speex supports 11 quality levels from 0 to 10. Higher values produce better encoding quality but also higher bitrates:

| Quality Level | Narrowband Bitrate | Wideband Bitrate | Typical Use |
|--------------|-------------------|------------------|-------------|
| 0 | ~2.15 kbps | ~3.95 kbps | Very low bandwidth |
| 1 | ~5.9 kbps | ~7.75 kbps | Very low bandwidth |
| 2-3 | 8~11 kbps | 9~12 kbps | Low bandwidth |
| 4-6 | 11~18 kbps | 12~22 kbps | Balanced quality/bandwidth |
| 7-8 | 18~24 kbps | 22~28 kbps | Higher quality |
| 9-10 | 24~44 kbps | 28~44 kbps | Highest quality |

In wideband mode, the same quality level typically consumes more bitrate than in narrowband mode.

## Usage Flow

Typical Speex encoding/decoding flow:

```
1. speex_bits_init()        - Initialize bitstream structure
2. speex_lib_get_mode()     - Get codec mode
3. speex_encoder_init()     - Initialize encoder
4. speex_decoder_init()     - Initialize decoder
5. [Optional] speex_encoder_ctl() - Set quality and other parameters
6. Loop:
   a. speex_encode()         - Encode one frame
   b. speex_bits_write()     - Write to network buffer
   c. speex_bits_read_from() - Read from network
   d. speex_decode()         - Decode
7. speex_encoder_destroy()   - Destroy encoder
8. speex_decoder_destroy()   - Destroy decoder
9. speex_bits_destroy()      - Destroy bitstream
```

## Code Examples

The following example demonstrates the basic flow of using Speex for speech encoding/decoding on BL618:

```c
#include "speex/speex.h"
#include "speex/speex_bits.h"

#define FRAME_SIZE 160  // Narrowband 8kHz/16bit = 20ms frame

void speex_voip_example(void)
{
    // Bitstream structures
    SpeexBits enc_bits;
    SpeexBits dec_bits;
    SpeexBits *bits = &enc_bits;

    // PCM data buffers
    spx_int16_t pcm_in[FRAME_SIZE];
    spx_int16_t pcm_out[FRAME_SIZE];
    char encoded[256];

    // Encoder and decoder states
    void *enc_state;
    void *dec_state;

    const SpeexMode *mode;

    // Step 1: Initialize bitstreams
    speex_bits_init(&enc_bits);
    speex_bits_init(&dec_bits);

    // Step 2: Get narrowband mode
    mode = speex_lib_get_mode(SPEEX_MODEID_NB);

    // Step 3: Initialize encoder and decoder
    enc_state = speex_encoder_init(mode);
    dec_state = speex_decoder_init(mode);

    // Step 4: Set encoding quality (0-10)
    int quality = 4;
    speex_encoder_ctl(enc_state, SPEEX_SET_QUALITY, &quality);

    // Step 5: Set variable bitrate (optional)
    int vbr = 1;
    speex_encoder_ctl(enc_state, SPEEX_SET_VBR, &vbr);

    // Get frame size
    int frame_size;
    speex_encoder_ctl(enc_state, SPEEX_GET_FRAME_SIZE, &frame_size);

    // Encoding example
    // Assume pcm_in has been filled with raw PCM data
    speex_bits_reset(bits);                    // Reset bitstream
    speex_encode_int(enc_state, pcm_in, bits);  // Encode
    int nb_bytes = speex_bits_write(bits, encoded, sizeof(encoded));

    // Decoding example
    speex_bits_read_from(&dec_bits, encoded, nb_bytes);
    int ret = speex_decode_int(dec_state, &dec_bits, pcm_out);

    // Step 6: Destroy resources
    speex_encoder_destroy(enc_state);
    speex_decoder_destroy(dec_state);
    speex_bits_destroy(&enc_bits);
    speex_bits_destroy(&dec_bits);
}
```

### Wideband Mode Example

```c
void speex_wideband_example(void)
{
    SpeexBits bits;
    void *enc_state, *dec_state;
    spx_int16_t pcm_in[320];  // Wideband frame is larger (16kHz * 20ms)
    spx_int16_t pcm_out[320];

    speex_bits_init(&bits);

    // Use wideband mode
    const SpeexMode *mode = speex_lib_get_mode(SPEEX_MODEID_WB);
    enc_state = speex_encoder_init(mode);
    dec_state = speex_decoder_init(mode);

    int quality = 6;
    speex_encoder_ctl(enc_state, SPEEX_SET_QUALITY, &quality);

    // Encode
    speex_bits_reset(&bits);
    speex_encode_int(enc_state, pcm_in, &bits);
    char encoded[256];
    int nb_bytes = speex_bits_write(&bits, encoded, sizeof(encoded));

    // Decode
    speex_bits_read_from(&bits, encoded, nb_bytes);
    speex_decode_int(dec_state, &bits, pcm_out);

    // Destroy
    speex_encoder_destroy(enc_state);
    speex_decoder_destroy(dec_state);
    speex_bits_destroy(&bits);
}
```

## Packet Loss Concealment (PLC)

Speex has built-in Packet Loss Concealment (PLC) functionality. When a network packet is lost, the decoder can call `speex_decode()` with the `bits` parameter set to `NULL`, which uses the previous frame's data to extrapolate and generate compensation audio:

```c
// Decode when packet is lost
speex_decode_int(dec_state, NULL, pcm_out);  // bits is NULL
```

Packet loss compensation uses silence or some variation of the previous frame to replace lost speech. While the quality is not as good as normal decoding, it prevents the decoder from producing harsh noise.

## Notes

1. **Frame Size Matching**: The encoder and decoder must use the same frame size. Call `SPEEX_GET_FRAME_SIZE` to get the frame size of the current mode.

2. **Endianness**: Speex-encoded data is endianness-dependent; care must be taken when transmitting across different platforms.

3. **Memory Management**: The `chars` buffer in the `SpeexBits` structure is allocated by `speex_bits_init()` and freed by `speex_bits_destroy()`. If initialized with `speex_bits_init_buffer()`, the buffer lifecycle is managed externally.

4. **VBR Quality Setting**: When Variable Bitrate (VBR) is enabled, set `SPEEX_SET_VBR_QUALITY` to control the target quality. The encoder will automatically balance between guaranteed quality and bitrate limits.

5. **DTX Discontinuous Transmission**: When DTX is enabled, the encoder stops sending data when silence is detected, saving approximately 50% bandwidth.

## References

- Xiph.Org Foundation: https://www.xiph.org/
- Speex Official Documentation: https://www.speex.org/docs/
- Bouffalo SDK Speex component source: `components/multimedia/speex/include/speex/`
