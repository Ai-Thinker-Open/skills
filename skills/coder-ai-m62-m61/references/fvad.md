# FVAD Voice Activity Detection

## Overview

FVAD (FreeVAD) is a WebRTC-based Voice Activity Detection (VAD) module specifically designed to detect speech intervals in audio streams. This module originates from the WebRTC VAD algorithm, later extracted by Daniel Pirch as an independent open-source library (libfvad), featuring small size, low power consumption, and high detection accuracy.

On the BL618 platform, FVAD typically serves as a front-end processing module for speech recognition systems, responsible for marking speech-containing segments from continuous audio streams for subsequent processing by speech recognition, wake word detection, and other algorithms. Accurate voice interval detection effectively reduces useless data processing, lowering system power consumption and computational burden.

## Key Types

### Fvad Handle

```c
typedef struct Fvad Fvad;
```

`Fvad` is an opaque handle type representing a VAD instance. Developers do not need to understand its internal structure and only need to operate the handle through the API. All VAD-related operations require an instance pointer created by `fvad_new()`.

## Core API

### fvad_new — Create VAD Instance

```c
Fvad *fvad_new(void);
```

Create and initialize a new VAD instance. This function allocates necessary memory and sets default parameters (8000 Hz sample rate, mode 0).

**Return value:** Returns a pointer to the new instance on success, `NULL` on failure (usually memory allocation failure). After successful creation, call `fvad_free()` to release.

---

### fvad_free — Release VAD Instance

```c
void fvad_free(Fvad *inst);
```

Release the dynamic memory occupied by the specified VAD instance. Instances created with `fvad_new()` should ultimately call this function to release, preventing memory leaks.

**Parameters:**
- `inst` — Instance pointer returned by `fvad_new()`

---

### fvad_reset — Reset VAD State

```c
void fvad_reset(Fvad *inst);
```

Reinitialize the VAD instance, clear all internal state, and restore mode and sample rate to default values (mode 0, 8000 Hz sample rate). Compared to `fvad_free()` + `fvad_new()`, `fvad_reset()` avoids the overhead of reallocating memory, suitable for scenarios where the same instance needs to be reused.

**Parameters:**
- `inst` — VAD instance pointer

---

### fvad_process — Detect Voice Activity

```c
int fvad_process(Fvad *inst, const int16_t *frame, size_t length);
```

Perform voice activity detection on a frame of audio data — the core VAD functionality.

**Parameters:**
- `inst` — VAD instance pointer
- `frame` — Pointer to an array of PCM 16-bit signed samples
- `length` — Number of samples, must correspond to 10ms, 20ms, or 30ms frame length

**Sample Rate to Frame Length Correspondence:**

| Sample Rate (Hz) | 10ms Frame | 20ms Frame | 30ms Frame |
|-------------|-----------|-----------|-----------|
| 8000        | 80        | 160       | 240       |
| 16000       | 160       | 320       | 480       |
| 32000       | 320       | 640       | 960       |
| 48000       | 480       | 960       | 1440      |

**Return values:**
- `1` — Speech detected (Active Voice)
- `0` — No speech detected (Non-active Voice)
- `-1` — Invalid frame length (length does not meet requirements)

---

### fvad_set_mode — Set Detection Mode

```c
int fvad_set_mode(Fvad *inst, int mode);
```

Set the VAD aggressiveness mode. Higher modes enforce stricter speech determination, meaning the condition to return 1 is more stringent, increasing the miss probability but lowering the false positive probability.

**Parameters:**
- `inst` — VAD instance pointer
- `mode` — Aggressiveness mode, values 0~3

**Mode Descriptions:**

| Mode | Name           | Description                                           |
|------|----------------|------------------------------------------------|
| 0    | Quality        | Highest quality, lowest miss rate, default mode                  |
| 1    | Low Bitrate    | Low bitrate scenarios, reduce false positives                            |
| 2    | Aggressive     | Aggressive mode, stricter filtering                            |
| 3    | Very Aggressive | Highest aggressiveness, highest speech confirmation threshold                       |

**Return value:** 0 on success, -1 on failure (invalid mode).

**Scenario selection suggestions:**
- General scenarios (speech recognition front-end): Recommended mode 0 or 1
- Noisy environments: Recommended mode 2 or 3
- Quiet environments requiring high recall rate: Recommended mode 0

---

### fvad_set_sample_rate — Set Sample Rate

```c
int fvad_set_sample_rate(Fvad *inst, int sample_rate);
```

Set the input audio sample rate. Internal processing is uniformly performed at 8000 Hz; input data above 8000 Hz is automatically downsampled.

**Parameters:**
- `inst` — VAD instance pointer
- `sample_rate` — Sample rate in Hz, valid values: 8000, 16000, 32000, 48000

**Return value:** 0 on success, -1 on failure (invalid sample rate).

**Note:** The default sample rate is 8000 Hz. It is recommended to explicitly set the correct sample rate based on the input audio format before actual use for accurate detection results.

## Input Requirements

FVAD has explicit format requirements for input audio:

- **Data type**: PCM 16-bit signed integer (`int16_t`)
- **Frame length**: Only 10ms, 20ms, and 30ms frame lengths are supported
- **Sample rate**: 8000, 16000, 32000, 48000 Hz
- **Channel**: Mono

Input data must conform to the above specifications, otherwise `fvad_process()` will return -1.

## Usage Flow

The typical FVAD usage flow is as follows:

```
1. fvad_new()           Create VAD instance
2. fvad_set_sample_rate()  Set sample rate
3. fvad_set_mode()      (Optional) Set detection mode
4. fvad_process()       Process each audio frame in a loop
5. fvad_free()          Release instance
```

## Code Examples

The following example demonstrates how to use FVAD on the BL618 for voice activity detection:

```c
#include "fvad.h"
#include <stdio.h>
#include <stddef.h>

/* Assume audio parameters: 16kHz sample rate, 20ms frame length */
#define SAMPLE_RATE     16000
#define FRAME_DURATION  20  /* ms */
#define FRAME_SIZE      (SAMPLE_RATE * FRAME_DURATION / 1000)  /* 320 samples */

int vad_example(const int16_t *audio_buffer, size_t num_frames)
{
    /* 1. Create VAD instance */
    Fvad *vad = fvad_new();
    if (vad == NULL) {
        printf("Failed to create VAD instance\r\n");
        return -1;
    }

    /* 2. Set sample rate to 16kHz */
    if (fvad_set_sample_rate(vad, SAMPLE_RATE) != 0) {
        printf("Invalid sample rate: %d\r\n", SAMPLE_RATE);
        fvad_free(vad);
        return -1;
    }

    /* 3. Set detection mode (0: quality priority) */
    if (fvad_set_mode(vad, 0) != 0) {
        printf("Invalid mode\r\n");
        fvad_free(vad);
        return -1;
    }

    /* 4. Process each audio frame in a loop */
    int speech_frames = 0;
    for (size_t i = 0; i < num_frames; i++) {
        const int16_t *frame = audio_buffer + i * FRAME_SIZE;
        int result = fvad_process(vad, frame, FRAME_SIZE);

        if (result < 0) {
            printf("Frame %zu: invalid length\r\n", i);
            continue;
        }

        if (result == 1) {
            printf("Frame %zu: speech detected\r\n", i);
            speech_frames++;
        } else {
            printf("Frame %zu: silence\r\n", i);
        }
    }

    /* 5. Release VAD instance */
    fvad_free(vad);

    printf("Total speech frames: %d / %zu\r\n", speech_frames, num_frames);
    return 0;
}
```

### Real-Time Audio Stream Processing Example

In practical applications, audio data typically comes from a microphone or audio input interface (such as I2S). Below is a simplified real-time processing framework:

```c
#include "fvad.h"

/* Audio buffer size calculation: 16kHz * 20ms = 320 samples */
#define FRAME_SIZE  320

void audio_vad_task(void *param)
{
    Fvad *vad = fvad_new();
    fvad_set_sample_rate(vad, 16000);
    fvad_set_mode(vad, 1);  /* Low bitrate mode, reduce false positives */

    int16_t pcm_frame[FRAME_SIZE];

    while (1) {
        /* Read a frame of data from audio interface (pseudo-code) */
        // audio_read_frame(pcm_frame, FRAME_SIZE);

        int is_speech = fvad_process(vad, pcm_frame, FRAME_SIZE);

        if (is_speech == 1) {
            /* Speech detected, can trigger subsequent processing such as:
             * - Wake word detection
             * - Speech recognition
             * - Recording storage
             */
        }
    }

    fvad_free(vad);
}
```

## Application Scenarios

### Speech Recognition Front-End

In offline speech recognition or keyword wake-up systems, FVAD is used to detect speech segments, segmenting continuous audio streams into independent speech fragments. Only activating recognition algorithms when speech is detected significantly reduces power consumption and false trigger rates — this is the standard front-end processing for embedded voice interaction.

### Call Silence Detection

In VoIP telephony or video conferencing applications, FVAD can be used to detect whether the user is speaking. When silence is detected, the system can choose not to transmit or to compress audio data, saving network bandwidth. In call quality monitoring, silence detection also helps generate call quality reports.

### Recording Trigger

In scenarios such as voice recorders, voice memos, and environmental monitoring, VAD is used to detect sound activity to trigger recording start and end. Compared to continuous recording, triggered recording can significantly save storage space and battery power while reducing the amount of useless audio data to process later.

## Performance Characteristics

- **Low computational overhead**: Simple decision algorithm based on short-time energy and frequency domain features, suitable for embedded MCUs
- **Low memory footprint**: Extremely small single-instance memory usage, suitable for resource-constrained systems
- **Low latency**: Frame-by-frame processing, detection latency is approximately the duration of a single frame (10~30ms)
- **Strong independence**: Pure C implementation, no external dependencies, easy to port

## Notes

1. **Frame alignment**: Input frame length must precisely match the specification; variable-length frames are not supported.
2. **Sample rate matching**: Must set using the actual audio sample rate; otherwise detection results will be inaccurate.
3. **Mode selection**: Choose an appropriate detection mode based on actual noise environment; higher modes are recommended for noisier environments.
4. **Thread safety**: `fvad_process()` is not thread-safe; when used in multi-threaded scenarios, synchronize access yourself.
5. **Reset timing**: When switching audio streams or detection scenarios, consider calling `fvad_reset()` to clear internal state.

## References

- [libfvad Official Repository](https://github.com/dpirch/libfvad)
- [WebRTC VAD Algorithm Documentation](https://webrtc.github.io/webrtc-org/audio/)
- `/home/seahi/workspase/BL618Claw/bouffalo_sdk/components/multimedia/libfvad/include/fvad.h`
