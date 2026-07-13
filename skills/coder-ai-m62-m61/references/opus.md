# Opus Audio Codec

## Overview

Opus is an interactive voice and audio codec standardized by the IETF (Internet Engineering Task Force). It combines technology from Skype's SILK codec (optimized for speech) and Xiph.Org's CELT codec (optimized for music), capable of operating across a wide bitrate range from 6 kbps to 510 kbps.

Key features of Opus include:

- **Sample rate support**: 8 kHz to 48 kHz
- **Bitrate range**: 6 kbps ~ 510 kbps
- **Encoding modes**: Supports CBR (Constant Bitrate) and VBR (Variable Bitrate)
- **Audio bandwidth**: From narrowband (4 kHz) to fullband (20 kHz)
- **Channel support**: Mono, stereo, up to 255 channels
- **Frame sizes**: Adjustable from 2.5 ms to 60 ms
- **Packet loss concealment**: Built-in PLC (Packet Loss Concealment) functionality
- **Dual implementation**: Provides both floating-point and fixed-point implementations

On the BL618 platform, Opus is primarily used in VoIP (voice calling) and music streaming scenarios, maintaining good audio quality even under fluctuating network bandwidth conditions.

## Version Information

```c
const char *opus_get_version_string(void);
```

Gets the version string of the Opus library. Applications can check if the version string contains the "-fixed" substring to determine whether the current build is the fixed-point or floating-point version.

## Data Types

Opus uses the following basic data types defined in `opus_types.h`:

| Type | Description |
|------|------|
| `opus_int8` | Signed 8-bit integer |
| `opus_uint8` | Unsigned 8-bit integer |
| `opus_int16` | Signed 16-bit integer |
| `opus_uint16` | Unsigned 16-bit integer |
| `opus_int32` | Signed 32-bit integer |
| `opus_uint32` | Unsigned 32-bit integer |
| `opus_int64` | Signed 64-bit integer |

## Opaque Handles

The Opus library uses opaque pointers as state handles; applications do not need to know their internal structure:

| Handle Type | Description |
|---------|------|
| `OpusEncoder*` | Single-stream encoder state handle |
| `OpusDecoder*` | Single-stream decoder state handle |
| `OpusMSEncoder*` | Multi-stream encoder state handle |
| `OpusMSDecoder*` | Multi-stream decoder state handle |
| `OpusRepacketizer*` | Packet repacketizer handle |

## Error Codes

Error codes returned by all Opus functions are defined as follows:

| Error Code | Value | Description |
|--------|-----|------|
| `OPUS_OK` | 0 | Operation successful |
| `OPUS_BAD_ARG` | -1 | Invalid or out-of-range parameter |
| `OPUS_BUFFER_TOO_SMALL` | -2 | Insufficient output buffer space |
| `OPUS_INTERNAL_ERROR` | -3 | Internal error detected |
| `OPUS_INVALID_PACKET` | -4 | Compressed data corrupted or unsupported format |
| `OPUS_UNIMPLEMENTED` | -5 | Requested operation not supported |
| `OPUS_INVALID_STATE` | -6 | Encoder or decoder structure invalid or already freed |
| `OPUS_ALLOC_FAIL` | -7 | Memory allocation failed |

```c
const char *opus_strerror(int error);
```

Converts an error code to a human-readable error string.

## Encoding Modes

The application mode must be specified when creating an encoder:

```c
#define OPUS_APPLICATION_VOIP                2048
#define OPUS_APPLICATION_AUDIO                2049
#define OPUS_APPLICATION_RESTRICTED_LOWDELAY  2051
```

| Mode | Description |
|------|------|
| `OPUS_APPLICATION_VOIP` | Suitable for VoIP/video conferencing, enhances speech signals for improved intelligibility |
| `OPUS_APPLICATION_AUDIO` | Suitable for music and broadcast scenarios, pursues high fidelity of decoded audio to the original input |
| `OPUS_APPLICATION_RESTRICTED_LOWDELAY` | Lowest latency mode, disables speech optimization mode, suitable for scenarios with extremely strict latency requirements |

## Encoder API

### Create and Destroy

```c
OpusEncoder *opus_encoder_create(
    opus_int32 Fs,      // Sample rate: 8000/12000/16000/24000/48000 Hz
    int channels,       // Number of channels: 1 (mono) or 2 (stereo)
    int application,    // Application mode
    int *error          // Output error code
);

void opus_encoder_destroy(OpusEncoder *st);
```

`opus_encoder_create()` allocates and initializes an encoder state. If creation fails, `error` will contain the error code and the return value is `NULL`.

### Encoding Operations

```c
opus_int32 opus_encode(
    OpusEncoder *st,
    const opus_int16 *pcm,      // Input PCM data (interleaved if stereo)
    int frame_size,              // Samples per channel
    unsigned char *data,         // Output compressed data buffer
    opus_int32 max_data_bytes    // Maximum bytes for output buffer
);

opus_int32 opus_encode_float(
    OpusEncoder *st,
    const float *pcm,            // Input float PCM data, range +/-1.0
    int frame_size,
    unsigned char *data,
    opus_int32 max_data_bytes
);
```

**frame_size parameter** (at 48 kHz):

| Frame Duration | frame_size (samples) |
|--------|---------------------|
| 2.5 ms | 120 |
| 5 ms | 240 |
| 10 ms | 480 |
| 20 ms | 960 |
| 40 ms | 1920 |
| 60 ms | 2880 |

The return value is the actual number of bytes in the compressed packet. A return value ≤ 2 indicates DTX (discontinuous transmission) can be enabled. Negative values indicate encoding errors.

### Encoder Control

```c
int opus_encoder_ctl(OpusEncoder *st, int request, ...);
```

Encoder parameters can be dynamically adjusted via the CTL interface. Common control macros:

```c
// Set bitrate (bps)
opus_encoder_ctl(enc, OPUS_SET_BITRATE(bitrate));
opus_encoder_ctl(enc, OPUS_GET_BITRATE(&bitrate));

// Set application mode
opus_encoder_ctl(enc, OPUS_SET_APPLICATION(OPUS_APPLICATION_VOIP));
opus_encoder_ctl(enc, OPUS_GET_APPLICATION(&app));

// Set sample rate
opus_encoder_ctl(enc, OPUS_SET_SAMPLE_RATE(sample_rate));

// Set complexity (0-10, default 10)
opus_encoder_ctl(enc, OPUS_SET_COMPLEXITY(10));

// Enable/disable VBR
opus_encoder_ctl(enc, OPUS_SET_VBR(1));  // 1=enable VBR, 0=disable

// Set signal type hint
opus_encoder_ctl(enc, OPUS_SET_SIGNAL(OPUS_SIGNAL_VOICE));
// OPUS_SIGNAL_MUSIC - bias towards music
// OPUS_SIGNAL_VOICE - bias towards voice
// OPUS_AUTO - auto select (default)
```

## Decoder API

### Create and Destroy

```c
OpusDecoder *opus_decoder_create(
    opus_int32 Fs,      // Sample rate: 8000/12000/16000/24000/48000 Hz
    int channels,       // Number of channels
    int *error          // Output error code
);

void opus_decoder_destroy(OpusDecoder *st);
```

### Decoding Operations

```c
int opus_decode(
    OpusDecoder *st,
    const unsigned char *data,   // Input compressed data packet
    opus_int32 len,              // Packet byte count, 0 indicates packet loss
    opus_int16 *pcm,             // Output PCM buffer
    int frame_size,              // Output samples per channel
    int decode_fec               // Whether to decode FEC data (0/1)
);

int opus_decode_float(
    OpusDecoder *st,
    const unsigned char *data,
    opus_int32 len,
    float *pcm,
    int frame_size,
    int decode_fec
);
```

**Packet loss handling**: When `data` is `NULL` and `len` is 0, PLC (Packet Loss Concealment) is performed, generating audio of the same length as the lost frame.

**FEC handling**: When `decode_fec` is 1, attempts to decode the forward error correction data embedded in the packet.

### Decoder Control

```c
int opus_decoder_ctl(OpusDecoder *st, int request, ...);
```

Common decoder CTL:

```c
// Get sample rate
opus_int32 sample_rate;
opus_decoder_ctl(dec, OPUS_GET_SAMPLE_RATE(&sample_rate));

// Get duration of previous packet
opus_decoder_ctl(dec, OPUS_GET_LAST_PACKET_DURATION(&duration));
```

## Packet Analysis API

```c
int opus_packet_get_bandwidth(const unsigned char *data);
```

Gets the audio bandwidth of an Opus packet:

| Return Value | Bandwidth |
|--------|------|
| `OPUS_BANDWIDTH_NARROWBAND` | 4 kHz (narrowband) |
| `OPUS_BANDWIDTH_MEDIUMBAND` | 6 kHz (medium band) |
| `OPUS_BANDWIDTH_WIDEBAND` | 8 kHz (wideband) |
| `OPUS_BANDWIDTH_SUPERWIDEBAND` | 12 kHz (super wideband) |
| `OPUS_BANDWIDTH_FULLBAND` | 20 kHz (fullband) |

```c
int opus_packet_get_nb_channels(const unsigned char *data);
```

Gets the number of channels in an Opus packet.

## Multi-Stream Encoder/Decoder

For applications requiring more than 2 channels, the multi-stream API can be used:

```c
OpusMSEncoder *opus_multistream_encoder_create(
    opus_int32 Fs,
    int channels,           // Total number of channels
    int streams,           // Number of encoded streams
    int coupled_streams,   // Number of stereo streams
    const unsigned char *mapping,
    int application,
    int *error
);

OpusMSDecoder *opus_multistream_decoder_create(
    opus_int32 Fs,
    int channels,
    int streams,
    int coupled_streams,
    const unsigned char *mapping,
    int *error
);
```

## Code Examples

The following examples demonstrate the basic flow of using Opus for PCM data encoding and decoding on BL618:

### Initialization

```c
#include "opus.h"
#include "opus_defines.h"
#include <stdio.h>
#include <stdlib.h>

// Error checking helper macro
#define CHECK_ERROR(ret, ctx) do { \
    if ((ret) != OPUS_OK) { \
        fprintf(stderr, "Opus error: %s\n", opus_strerror(ret)); \
        goto ctx; \
    } \
} while(0)

// Sample rate
#define SAMPLE_RATE     48000
// Number of channels
#define CHANNELS        1
// Frame duration (20 ms)
#define FRAME_SIZE      (SAMPLE_RATE * 20 / 1000)  // 960 samples
// Maximum packet size
#define MAX_PACKET_SIZE 4000
```

### Encoder Example

```c
int opus_encode_example(const opus_int16 *pcm_data, int frame_size,
                        unsigned char *opus_packet, opus_int32 *packet_size)
{
    OpusEncoder *encoder = NULL;
    int error;
    opus_int32 len;

    // Create encoder (VoIP mode)
    encoder = opus_encoder_create(SAMPLE_RATE, CHANNELS,
                                   OPUS_APPLICATION_VOIP, &error);
    CHECK_ERROR(error, cleanup);

    // Optional: set encoding parameters
    opus_encoder_ctl(encoder, OPUS_SET_BITRATE(64000));  // 64 kbps
    opus_encoder_ctl(encoder, OPUS_SET_COMPLEXITY(10));  // Highest complexity
    opus_encoder_ctl(encoder, OPUS_SET_VBR(1));           // Enable VBR

    // Perform encoding
    len = opus_encode(encoder, pcm_data, frame_size,
                      opus_packet, MAX_PACKET_SIZE);
    if (len < 0) {
        fprintf(stderr, "Encode failed: %s\n", opus_strerror(len));
        error = len;
        goto cleanup;
    }

    *packet_size = len;
    error = OPUS_OK;

cleanup:
    if (encoder) {
        opus_encoder_destroy(encoder);
    }
    return error;
}
```

### Decoder Example

```c
int opus_decode_example(const unsigned char *opus_packet, opus_int32 packet_size,
                        opus_int16 *pcm_data, int frame_size)
{
    OpusDecoder *decoder = NULL;
    int error;
    int samples;

    // Create decoder
    decoder = opus_decoder_create(SAMPLE_RATE, CHANNELS, &error);
    CHECK_ERROR(error, cleanup);

    // Perform decoding
    // decode_fec = 0 means do not decode FEC data
    samples = opus_decode(decoder, opus_packet, packet_size,
                           pcm_data, frame_size, 0);
    if (samples < 0) {
        fprintf(stderr, "Decode failed: %s\n", opus_strerror(samples));
        error = samples;
        goto cleanup;
    }

    error = OPUS_OK;

cleanup:
    if (decoder) {
        opus_decoder_destroy(decoder);
    }
    return error;
}
```

### Packet Loss Concealment Example

```c
int opus_plc_example(OpusDecoder *decoder, opus_int16 *pcm_data, int frame_size)
{
    int samples;

    // Passing NULL and 0 indicates packet loss, triggers PLC
    samples = opus_decode(decoder, NULL, 0, pcm_data, frame_size, 0);
    if (samples < 0) {
        fprintf(stderr, "PLC failed: %s\n", opus_strerror(samples));
        return samples;
    }

    return samples;
}
```

### Complete Encoding/Decoding Flow

```c
int opus_full_example(const opus_int16 *input_pcm, int frame_size,
                      opus_int16 *output_pcm, int *output_size)
{
    OpusEncoder *encoder = NULL;
    OpusDecoder *decoder = NULL;
    unsigned char packet[MAX_PACKET_SIZE];
    opus_int32 packet_size;
    int error = OPUS_OK;
    int decoded_samples;

    // Create encoder
    encoder = opus_encoder_create(SAMPLE_RATE, CHANNELS,
                                  OPUS_APPLICATION_VOIP, &error);
    if (error != OPUS_OK) goto cleanup;

    // Create decoder
    decoder = opus_decoder_create(SAMPLE_RATE, CHANNELS, &error);
    if (error != OPUS_OK) goto cleanup;

    // Encode: PCM -> Opus packet
    packet_size = opus_encode(encoder, input_pcm, frame_size,
                               packet, MAX_PACKET_SIZE);
    if (packet_size < 0) {
        error = packet_size;
        goto cleanup;
    }

    // Decode: Opus packet -> PCM
    decoded_samples = opus_decode(decoder, packet, packet_size,
                                   output_pcm, frame_size, 0);
    if (decoded_samples < 0) {
        error = decoded_samples;
        goto cleanup;
    }

    *output_size = decoded_samples;

cleanup:
    if (encoder) opus_encoder_destroy(encoder);
    if (decoder) opus_decoder_destroy(decoder);
    return error;
}
```

## Performance Notes

1. **Frame size selection**: Longer frames (e.g., 20 ms, 40 ms, 60 ms) provide better compression efficiency but increase latency. For VoIP applications, 20 ms frames are recommended.

2. **Complexity setting**: Higher `OPUS_SET_COMPLEXITY` values yield better encoding quality but increase CPU consumption. On embedded platforms like BL618, choose an appropriate complexity (recommended 1-8) based on performance requirements.

3. **VBR vs CBR**: VBR (Variable Bitrate) saves average bandwidth while maintaining quality, but output data sizes are not fixed. CBR is suitable for scenarios with strict bandwidth requirements.

4. **Packet loss protection**: Enabling in-band FEC (`OPUS_SET_INBAND_FEC(1)`) adds a small amount of extra bandwidth but improves audio quality under high packet loss network conditions.

5. **Memory footprint**: Encoder and decoder states require persistent memory; they are freed immediately upon destruction.

## References

- [RFC 6716](https://tools.ietf.org/html/rfc6716) - Opus Audio Codec
- [RFC 7845](https://tools.ietf.org/html/rfc7845) - Ogg Encapsulation for Opus Audio
- Xiph.Org Foundation: <https://opus-codec.org/>
- BL618 Bouffalo SDK Opus component source: `components/multimedia/opus/include/opus/`
