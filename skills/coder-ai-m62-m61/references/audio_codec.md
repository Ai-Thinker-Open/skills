# BL618 Audio Codec Driver

## Overview

The BL618 audio driver layer resides in the `multimedia` component of Bouffalo SDK and mainly consists of two major modules:

- **SndBl616 Sound Card Driver**: the `drv_snd_bl616` component, providing sound card abstraction for I2S/PCMDM/PDM audio interfaces
- **AudioFlowctrlBridge Audio Stream Bridge**: the `audio_flowctrl_bridge` component, implementing complete audio stream processing from SBC decoding to PCM

These two layers architecturally serve the upper-layer `smart_audio`, providing stable low-level support for scenarios such as voice playback and audio recording.

---

## SndBl616 Sound Card Driver

### Header File

```c
#include <devices/drv_snd_bl616.h>
```

### Configuration Structure

`snd_bl616_config_t` is used to initialize the gain parameters of the sound card driver:

```c
typedef struct {
    int audio_in_gain_list[3];   // Input gain list, supports 3-level gain configuration
    int audio_out_gain_list[2];  // Output gain list, supports 2-level gain configuration
} snd_bl616_config_t;
```

> `audio_in_gain_list` and `audio_out_gain_list` correspond to analog/digital input gain and output gain calibration values respectively. Actual values must be tuned according to hardware design.

### Registration and Deregistration

```c
void snd_card_bl616_register(void *config);
void snd_card_bl616_unregister(void *config);
```

- `snd_card_bl616_register()`: Registers the sound card driver based on the provided configuration parameters, completing I2S/PCMDM/PDM hardware resource initialization
- `snd_card_bl616_unregister()`: Deregisters the sound card, releasing related hardware resources

### I2S Input/Output Gain Configuration

The I2S interface input gain is configured via `audio_in_gain_list`, supporting 3-level gain adjustment suitable for microphones with different sensitivities. Output gain is configured via `audio_out_gain_list`, supporting 2-level output power adjustment for driving speakers or amplifiers with different impedances.

After the sound card is registered, the driver automatically sets the corresponding gain registers based on the configuration list, requiring no manual intervention from the user.

---

## AudioFlowctrlBridge Audio Stream Bridge

AudioFlowctrlBridge implements a complete decode and playback chain from SBC compressed audio data to PCM raw audio data, consisting of two parts: the `pcm_drv` driver abstraction layer and the `sbc2pcm` high-level interface.

### PCM Driver Layer

The PCM driver abstraction layer `pcm_drv` defines the standard PCM device operation interface:

```c
struct pcm_drv {
    pcm_handle_t *(*pcm_open)(int mode, int samplerate, int channels, int format);
    int (*pcm_write)(pcm_handle_t pcm, const void *buf, unsigned int size);
    int (*pcm_start)(pcm_handle_t pcm);
    int (*pcm_stop)(pcm_handle_t pcm);
    int (*pcm_ioctl)(pcm_handle_t pcm, int cmd, void *arg);
    void (*pcm_close)(pcm_handle_t pcm);
};

const struct pcm_drv *pcm_drv_register(void);
```

- `pcm_open`: Opens a PCM device with the specified mode, sample rate, channel count, and format, returning a handle
- `pcm_write`: Writes audio data to the PCM device (typically raw PCM samples)
- `pcm_start` / `pcm_stop`: Starts/stops the PCM data stream
- `pcm_ioctl`: Sends control commands, usable for setting volume, switching data sources, etc.
- `pcm_close`: Closes the PCM device, releasing the handle
- `pcm_drv_register`: Registers the PCM driver, returning the driver function table

> `pcm_handle_t` is a `void *` type handle used to uniquely identify an opened PCM device instance.

### PCM Data Format

The `format` parameter typically uses standard ALSA format definitions (such as `S16LE`, `S8`, etc.), `channels` supports mono (1) or stereo (2), and common `samplerate` values are 8000/16000/44100/48000 Hz.

### sbc2pcm Library

`sbc2pcm` is a high-level wrapper built on top of `pcm_drv`, specifically designed for handling SBC Bluetooth audio decoding scenarios. It internally integrates an SBC decoder and outputs decoded PCM data through the underlying PCM driver.

#### Handle Types

```c
typedef struct sbc2pcm_handle *sbc2pcm_player_handle_t;
```

#### Open and Close

```c
sbc2pcm_player_handle_t sbc2pcm_player_open(int mode, int samplerate, int channels, int format);
void sbc2pcm_player_close(sbc2pcm_player_handle_t handle);
```

The `mode` parameter specifies the playback mode, `samplerate` and `channels` set the target sample rate and channel count respectively, and `format` specifies the PCM sample format.

#### Writing Data

```c
int sbc2pcm_player_write(sbc2pcm_player_handle_t handle, const void *buf, unsigned int size);
```

Writes SBC compressed data into the decode queue. The library internally auto-completes SBC decoding and outputs PCM data. The return value is typically the number of bytes written or an error code.

#### Start and Stop

```c
int sbc2pcm_player_start(sbc2pcm_player_handle_t handle);
int sbc2pcm_player_stop(sbc2pcm_player_handle_t handle);
```

`start` starts the internal decode task, beginning to consume data from the queue and push it to the PCM driver. `stop` halts the decode task; the data stream freezes but the handle remains valid.

#### SBC Decode Initialization

```c
int sbc2pcm_decode_init();
```

This function must be called to initialize the decoder context before starting sbc2pcm playback, typically executed once during system initialization.

#### Event Mechanism

`sbc2pcm` internally maintains an event queue, notifying the upper layer via the `PLAYER_EVENT_*` series of event types:

| Event Type | Description |
|---|---|
| `PLAYER_EVENT_SBC_DATA` | Received SBC data to be decoded |
| `PLAYER_EVENT_OPEN` | PCM device has been opened |
| `PLAYER_EVENT_START` | Playback stream has started |
| `PLAYER_EVENT_STOP` | Playback stream has stopped |
| `PLAYER_EVENT_CLOSE` | PCM device has been closed |

The upper layer can listen for playback state changes through the event queue to implement synchronous control logic.

#### pcm_ioctl Control Commands

Specific control commands can be sent to the PCM driver via `pcm_ioctl`. Common commands include:

- Volume adjustment
- Mute toggle
- Data source switching
- Sample rate change

Specific command numbers and parameter formats are defined by the concrete implementation. Typically, `cmd` is a command enum and `arg` is a parameter structure pointer.

---

## Relationship with smart_audio

`smart_audio` is the upper-layer application framework of the BL618 audio solution, encapsulating business logic such as audio playback, recording, and codec operations. SndBl616 sound card driver and AudioFlowctrlBridge together form its low-level support:

```
smart_audio (upper-layer application)
    └── AudioFlowctrlBridge (sbc2pcm / pcm_drv)
            └── SndBl616 Sound Card Driver (drv_snd_bl616)
                    └── Hardware (I2S / PCMDM / PDM)
```

When smart_audio needs to play SBC audio streams, the data is decoded to PCM by `sbc2pcm`, then passed by `pcm_drv` to the `snd_bl616` sound card driver, and finally output through the I2S/PCMDM/PDM interface to the audio codec or amplifier.

The sound card driver's gain configuration (`audio_in_gain_list` / `audio_out_gain_list`) also directly affects the audio quality performance of smart_audio.

---

## Code Examples

### Register Sound Card

```c
#include <devices/drv_snd_bl616.h>

void audio_init(void)
{
    snd_bl616_config_t cfg = {
        .audio_in_gain_list  = {0, 10, 20},  // 3-level input gain
        .audio_out_gain_list = {0, 15},      // 2-level output gain
    };

    snd_card_bl616_register(&cfg);
}
```

### Play PCM Data (via sbc2pcm)

```c
#include "sbc2pcm.h"

void audio_playback_example(void)
{
    sbc2pcm_player_handle_t player;

    /* Initialize SBC decoder */
    sbc2pcm_decode_init();

    /* Open player: mode 0, 16kHz sample rate, mono, S16LE format */
    player = sbc2pcm_player_open(0, 16000, 1, 16);
    if (!player) {
        return;
    }

    /* Start playback */
    sbc2pcm_player_start(player);

    /* Write SBC data and auto-decode playback */
    uint8_t sbc_data[512];
    int len = read(sbc_fd, sbc_data, sizeof(sbc_data));
    if (len > 0) {
        sbc2pcm_player_write(player, sbc_data, len);
    }

    /* Stop and close */
    sbc2pcm_player_stop(player);
    sbc2pcm_player_close(player);
}
```

### Direct PCM Playback Using PCM Driver

```c
#include "pcm_drv.h"

void pcm_playback_example(void)
{
    const struct pcm_drv *drv = pcm_drv_register();
    if (!drv) {
        return;
    }

    /* Open PCM: mode 0, 48kHz sample rate, stereo, S16LE */
    pcm_handle_t pcm = drv->pcm_open(0, 48000, 2, 16);
    if (!pcm) {
        return;
    }

    drv->pcm_start(pcm);

    /* Write raw PCM data */
    int16_t pcm_samples[1024];
    int len = read(pcm_fd, pcm_samples, sizeof(pcm_samples));
    if (len > 0) {
        drv->pcm_write(pcm, pcm_samples, len);
    }

    /* Mute control */
    int mute = 0;
    drv->pcm_ioctl(pcm, 3, &mute);  /* Command 3 sets mute state */

    drv->pcm_stop(pcm);
    drv->pcm_close(pcm);
}
```

### Deregister Sound Card

```c
void audio_deinit(void)
{
    snd_bl616_config_t cfg = {0};
    snd_card_bl616_unregister(&cfg);
}
```

---

## Notes

1. **Initialization Order**: `sbc2pcm_decode_init()` must be called before using sbc2pcm to ensure the decoder context is ready.
2. **Gain Configuration**: Input/output gain list values should match the hardware design. Incorrect gain may cause sound distortion or excessive/insufficient volume.
3. **Sample Rate Matching**: The sample rate of SBC data written by the upper layer should match the sample rate specified when calling `sbc2pcm_player_open` to avoid abnormal output pitch.
4. **Thread Safety**: `sbc2pcm` internally uses independent tasks and message queues for decoding. Do not call `sbc2pcm_player_write` from interrupt context.
5. **Resource Release**: Ensure all PCM devices are closed before deregistering the sound card to avoid using released hardware resources.

---

## References

- [drv_snd_bl616.h - SndBl616 Sound Card Driver Header](../../../../workspase/BL618Claw/bouffalo_sdk/components/multimedia/drv_snd_bl616/include/devices/drv_snd_bl616.h)
- [pcm_drv.h - PCM Driver Abstraction Layer Header](../../../../workspase/BL618Claw/bouffalo_sdk/components/multimedia/audio_flowctrl_bridge/include/pcm_drv.h)
- [sbc2pcm.h - SBC to PCM Playback Library Header](../../../../workspase/BL618Claw/bouffalo_sdk/components/multimedia/audio_flowctrl_bridge/include/sbc2pcm.h)
