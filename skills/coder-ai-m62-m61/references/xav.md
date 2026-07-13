# XAV Multimedia Framework

## Overview

XAV is the multimedia processing framework for the BL618 chip, providing a complete solution for audio/video playback, encoding/decoding, muxing/demuxing, and audio filtering. The framework adopts a modular design, following a `player -> avformat(demux) -> avcodec(dec) -> avfilter -> ao` data flow pipeline architecture, capable of handling various media sources including local files and network streams.

The XAV framework supports mainstream audio codec formats such as AAC, MP3, OPUS, and AMR, as well as container formats including MP4, MKV, TS, FLV, and OGG. Developers can quickly implement multimedia playback functionality through a unified API interface, suitable for various application scenarios such as smart speakers, IoT devices, and audio players.

## Framework Structure

XAV framework components work together to form a complete multimedia processing pipeline:

```
┌─────────┐    ┌───────────┐    ┌──────────┐    ┌───────────┐    ┌─────┐
│ player  │───▶│  avformat │───▶│ avcodec  │───▶│ avfilter  │───▶│ ao  │
└─────────┘    │  (demux)  │    │  (dec)   │    │ (EQ/Vol)  │    └─────┘
               └───────────┘    └──────────┘    └───────────┘
                     │
               ┌─────┴─────┐
               │  stream   │
               │(file/socket/mem)
               └───────────┘
```

- **player**: High-level player encapsulation, providing playback control interface
- **stream**: Data stream abstraction layer, supporting file, network, memory, and other data sources
- **avformat**: Container format processing, responsible for demuxing and muxing
- **avcodec**: Audio/video codec abstraction layer
- **avfilter**: Audio filter, handling EQ, volume, speed change, and other effects
- **ao**: Audio output device abstraction

## Component Details

### 1. xplayer - Multimedia Player

xplayer is the high-level player interface of the XAV framework, providing complete playback control functionality. It supports local file playback (e.g., `file:///fatfs0/Music/1.mp3`) and network stream playback (e.g., `http://ip:port/1.mp3`).

#### Player Lifecycle Management

| Function | Description |
|----------|-------------|
| `xplayer_module_init()` | Initialize player module (global init, called only once) |
| `xplayer_module_config_init()` | Initialize player module configuration parameters |
| `xplayer_new()` | Create player instance; creates default player when name is NULL |
| `xplayer_free()` | Destroy player instance |

#### Playback Control Interface

| Function | Description |
|----------|-------------|
| `xplayer_set_url()` | Set media source URL |
| `xplayer_play()` | Start playback |
| `xplayer_pause()` | Pause playback |
| `xplayer_resume()` | Resume playback |
| `xplayer_stop()` | Stop playback |
| `xplayer_seek()` | Seek to specified time position (timestamp in milliseconds) |
| `xplayer_set_start_time()` | Set playback start time |

#### State and Information Retrieval

| Function | Description |
|----------|-------------|
| `xplayer_get_time()` | Get current playback time and total duration |
| `xplayer_get_media_info()` | Get media info (must call `media_info_uninit` to release) |
| `xplayer_get_vol()` | Get volume value (0~255) |
| `xplayer_set_vol()` | Set volume value (0~255) |
| `xplayer_get_speed()` | Get playback speed |
| `xplayer_set_speed()` | Set playback speed (recommended range 0.5 ~ 2.0) |
| `xplayer_get_url()` | Get current media URL |
| `xplayer_get_state()` | Get player state |

#### Event Callbacks

```c
int xplayer_set_callback(xplayer_t *xplayer, xplayer_eventcb_t event_cb, const void *user_data);
```

Sets player event callback, notifying the application layer on events such as playback start, pause, stop, and completion.

#### Configuration Management

```c
int xplayer_set_config(xplayer_t *xplayer, const xplayer_cnf_t *conf);
int xplayer_get_config(xplayer_t *xplayer, xplayer_cnf_t *conf);
```

Set player configuration parameters before playback, such as cache size and playback mode.

### 2. avcodec - Audio/Video Codec Abstraction Layer

The avcodec module provides a unified abstract interface for audio/video codecs, supporting multiple audio codecs.

#### Audio Decoder Management

| Function | Description |
|----------|-------------|
| `ad_ops_register()` | Register decoder operation interface |
| `ad_conf_init()` | Initialize decoder configuration parameters |
| `ad_open()` | Open/create audio decoder instance |
| `ad_close()` | Close/destroy decoder instance |
| `ad_reset()` | Reset decoder state |

#### Decoding Operations

| Function | Description |
|----------|-------------|
| `ad_decode()` | Decode one frame of audio data |
| `ad_control()` | Control decoder (e.g., set parameters, get status) |

```c
// Decoding interface description
int ad_decode(ad_cls_t *o, avframe_t *frame, int *got_frame, const avpacket_t *pkt);
```

- `o`: Decoder instance
- `frame`: Output PCM data frame
- `got_frame`: Output parameter, indicates whether a frame was successfully decoded
- `pkt`: Input encoded data packet
- Return value: Number of input bytes consumed on success, -1 on failure

#### Supported Audio Codec Formats

- **AAC**: Advanced Audio Coding, supports multiple sample rates and channel configurations
- **MP3**: MPEG-1 Audio Layer III, widely used audio format
- **OPUS**: High-efficiency audio codec, suitable for network transmission
- **AMR**: Adaptive Multi-Rate codec, commonly used for voice scenarios

#### Decoder Configuration Parameters

```c
typedef struct ad_conf {
    sf_t          sf;             // Sample format
    uint8_t       *extradata;     // Extra data (e.g., ADTS header)
    int32_t       extradata_size;
    uint32_t      block_align;    // Frame data size
    uint32_t      bps;            // Bitrate
} ad_conf_t;
```

### 3. avformat - Container Format Processing

The avformat module handles various media container formats, implementing demux and mux functionality.

#### Core Interface

| Function | Description |
|----------|-------------|
| `demux_ops_register()` | Register demuxer operation interface |
| `demux_open()` | Open demuxer, parameter is stream handle |
| `demux_read_packet()` | Read one media data packet (audio/video frame) |
| `demux_seek()` | Seek to specified time position (milliseconds) |
| `demux_close()` | Close demuxer |
| `demux_control()` | Control demuxer |

#### Packet Reading

```c
int demux_read_packet(demux_cls_t *o, avpacket_t *pkt);
```

Reads one compressed audio/video data packet from the media file; after return, it must be fed to the corresponding decoder for decoding.

#### Supported Container Formats

| Container Format | Description |
|-----------------|-------------|
| MP4 | Based on ISO Base Media File Format, commonly used for H.264/AAC encoding |
| MKV | Matroska multimedia container, supports multiple audio tracks and subtitles |
| TS | MPEG-2 Transport Stream, used for live streaming |
| FLV | Flash Video, used for RTMP streaming |
| OGG | Open-source multimedia container, commonly used for Vorbis/Opus audio |

### 4. avfilter - Audio Filter

The avfilter module provides audio signal processing capabilities, including equalizer (EQ), volume control, playback speed adjustment, and more.

#### Filter Interface

| Function | Description |
|----------|-------------|
| `avf_init()` | Initialize filter instance |
| `avf_control()` | Control filter (set parameters) |
| `avf_set_bypass()` | Set whether to bypass filter |
| `avf_link()` | Link two filters to form a filter chain |
| `avf_link_tail()` | Link tail filter to chain head |
| `avf_filter_frame()` | Filter an audio frame |
| `avf_uninit()` | Release filter internal resources |
| `avf_close()` | Close and release filter |
| `avf_chain_close()` | Close entire filter chain |

#### Audio Frame Processing

```c
int avf_filter_frame(avfilter_t *avf, const avframe_t *in, avframe_t *out);
```

Filters the input audio frame `in` and outputs to `out`. Returns the number of output samples per channel, -1 on error.

#### Filter Chain Example

```
Input Frame → [EQ Filter] → [Volume Filter] → [atempo Filter] → Output Frame
```

Multiple filters can be chained in series via `avf_link()` to implement complex audio processing pipelines.

#### Supported Filter Types

- **EQ (Equalizer)**: Adjust gain across different frequency bands
- **Volume**: Volume gain/attenuation control
- **atempo (Speed Change)**: Adjust playback speed without changing pitch
- **swr (Resampler)**: Audio format conversion

### 5. stream - Data Stream Abstraction

The stream module provides a unified data stream abstraction interface, supporting various data sources including file, network, and memory.

#### Stream Operation Interface

| Function | Description |
|----------|-------------|
| `stream_ops_register()` | Register stream operation interface |
| `stream_conf_init()` | Initialize stream configuration parameters |
| `stream_open()` | Open data stream |
| `stream_read()` | Read data from stream |
| `stream_write()` | Write data to stream |
| `stream_seek()` | Stream seek (SEEK_SET/SEEK_CUR/SEEK_END) |
| `stream_skip()` | Skip specified number of bytes |
| `stream_tell()` | Get current stream position |
| `stream_get_size()` | Get stream size |
| `stream_get_url()` | Get stream URL |
| `stream_close()` | Close stream |
| `stream_control()` | Control stream |
| `stream_is_seekable()` | Check if stream is seekable |
| `stream_is_eof()` | Check if stream ended |
| `stream_is_live()` | Check if it's a live stream |
| `stream_is_interrupt()` | Check if stream was interrupted |

#### Stream Configuration Parameters

```c
typedef struct stream_conf {
    enum stream_mode    mode;               // Stream mode
    irq_av_t            irq;                // Interrupt handling
    uint8_t             need_parse;         // Whether URL parsing is needed
    uint32_t            rcv_timeout;         // Receive timeout (milliseconds)
    uint32_t            cache_size;          // Cache size
    uint32_t            cache_start_threshold; // Cache start threshold (0~100)
    get_decrypt_cb_t    get_dec_cb;         // Decryption callback
    void                *opaque;            // User data
    stream_event_t      stream_event_cb;     // Stream event callback
} stm_conf_t;
```

#### Supported URL Prefixes

| Prefix | Description |
|--------|-------------|
| `file://` | Local file, e.g. `file:///fatfs0/Music/1.mp3` |
| `http://` | HTTP network stream |
| `https://` | HTTPS encrypted network stream |
| `mem://` | Memory data source, e.g. `mem://addr=%u&size=%u` |
| `fifo://` | FIFO pipe, e.g. `fifo://tts/1` |

#### Binary Read Interface

The stream module provides convenient binary data read interfaces:

```c
int stream_r8(stream_cls_t *o);
uint16_t stream_r16be(stream_cls_t *o);
uint16_t stream_r16le(stream_cls_t *o);
uint32_t stream_r24be(stream_cls_t *o);
uint32_t stream_r24le(stream_cls_t *o);
uint32_t stream_r32be(stream_cls_t *o);
uint32_t stream_r32le(stream_cls_t *o);
uint64_t stream_r64be(stream_cls_t *o);
uint64_t stream_r64le(stream_cls_t *o);
```

Supports big-endian (be) and little-endian (le) integer reading.

### 6. ao - Audio Output Device Abstraction

The ao module provides a unified abstraction for audio output devices, supporting audio parameter configuration, buffer management, and volume control.

#### Audio Output Interface

| Function | Description |
|----------|-------------|
| `ao_ops_register()` | Register audio output operation interface |
| `ao_conf_init()` | Initialize audio output configuration parameters |
| `ao_open()` | Open audio output device |
| `ao_start()` | Start audio output |
| `ao_stop()` | Stop audio output |
| `ao_write()` | Write audio data |
| `ao_drain()` | Drain tail PCM data |
| `ao_close()` | Close audio output device |
| `ao_control()` | Control audio output |

#### Audio Output Configuration

```c
typedef struct ao_conf {
    char        *name;           // Audio output name
    uint32_t    period_ms;       // Period buffer size (milliseconds)
    uint32_t    period_num;      // Number of periods
    uint8_t     eq_segments;     // Equalizer segment count
    uint8_t     *aef_conf;       // AEF configuration data
    size_t      aef_conf_size;   // AEF configuration data size
    uint32_t    resample_rate;   // Target resampling rate (non-zero means resampling needed)
    uint8_t     vol_en;          // Software volume enable
    uint8_t     vol_index;       // Software volume value (0~255)
    uint8_t     atempo_play_en;  // Speed-change playback enable
    float       speed;           // Playback speed (recommended 0.5 ~ 2.0)
    int32_t     db_min;          // Digital volume curve minimum
    int32_t     db_max;          // Digital volume curve maximum
} ao_conf_t;
```

### 7. swresample - Resampling and Format Conversion

The swresample module provides audio resampling and format conversion functionality.

#### Sample Rate Conversion

| Function | Description |
|----------|-------------|
| `resx_ops_register()` | Register resampling operation interface |
| `resx_new()` | Create resampler instance |
| `resx_get_osamples_max()` | Get maximum output sample count |
| `resx_convert()` | Execute resampling conversion |
| `resx_free()` | Release resampler |

```c
resx_t *resx_new(uint32_t irate, uint32_t orate, uint8_t channels, uint8_t bits);
```

Create resampler: input sample rate `irate`, output sample rate `orate`, channel count `channels`, bit depth `bits` (only 16-bit supported).

#### Sample Format Conversion

swresample provides `swr_convert` and `swr_convert_frame` interfaces for sample format conversion:

```c
swr_t *swr_new(sf_t isf, sf_t osf);
int swr_convert(swr_t *s, void **out, size_t nb_osamples, const void **in, size_t nb_isamples);
int swr_convert_frame(swr_t *s, const avframe_t *iframe, avframe_t *oframe);
void swr_free(swr_t *s);
```

#### PCM Format Conversion Macros

The pcm_convert module provides conversion functions between various PCM formats:

| Function | Description |
|----------|-------------|
| `s8_ch1_to_s16_ch2()` | Mono S8 to Stereo S16 |
| `s8_ch1_to_s16_ch1()` | Mono S8 to Mono S16 |
| `u8_ch1_to_s16_ch2()` | Mono U8 to Stereo S16 |
| `s8_ch2_to_s16_ch2()` | Stereo S8 to Stereo S16 |
| `s8_ch2_to_s16_ch1()` | Stereo S8 to Mono S16 |
| `s16_ch1_to_s16_ch2()` | Mono S16 to Stereo S16 |
| `s16_ch2_to_s16_ch1()` | Stereo S16 to Mono S16 |
| `u16_le_to_s16_le()` | U16 LE to S16 LE |
| `u16_be_to_s16_le()` | U16 BE to S16 LE |

## Camera/Display Collaboration

The XAV framework supports collaboration with camera and display modules for synchronized audio/video playback.

### Video Display Control

The player provides the following video display control interfaces:

| Function | Description |
|----------|-------------|
| `xplayer_set_video_visible()` | Show/hide video |
| `xplayer_set_display_window()` | Set display window |
| `xplayer_set_fullscreen()` | Set fullscreen/window mode |
| `xplayer_set_display_format()` | Set display format |
| `xplayer_set_video_rotate()` | Rotate video |
| `xplayer_set_video_crop()` | Crop video |

### Audio/Video Synchronization

When playing video, the framework internally handles audio/video synchronization automatically. Audio streams are output via ao, while video frames are rendered via the display module; both are scheduled uniformly by the player to maintain synchronization.

### Multimedia Track Switching

| Function | Description |
|----------|-------------|
| `xplayer_switch_audio_track()` | Switch audio track |
| `xplayer_switch_subtitle_track()` | Switch subtitle track |
| `xplayer_set_subtitle_url()` | Set external subtitle URL |
| `xplayer_set_subtitle_visible()` | Show/hide subtitles |

## Code Examples

### Playing a Local MP3 File

The following example demonstrates how to use xplayer to play a local MP3 file:

```c
#include "xplayer/xplayer.h"
#include "avutil/av_config.h"

// Player event callback
static void player_event_cb(xplayer_event_t event, void *user_data)
{
    switch (event) {
        case XPLAYER_EVENT_START:
            printf("Playback started\n");
            break;
        case XPLAYER_EVENT_PAUSE:
            printf("Playback paused\n");
            break;
        case XPLAYER_EVENT_STOP:
            printf("Playback stopped\n");
            break;
        case XPLAYER_EVENT_FINISH:
            printf("Playback finished\n");
            break;
        case XPLAYER_EVENT_ERROR:
            printf("Playback error\n");
            break;
        default:
            break;
    }
}

int main(void)
{
    xplayer_t *player;
    xplayer_mdl_cnf_t mdl_cnf;
    
    // 1. Initialize player module
    xplayer_module_config_init(&mdl_cnf);
    if (xplayer_module_init(&mdl_cnf) < 0) {
        printf("Failed to init player module\n");
        return -1;
    }
    
    // 2. Create player instance
    player = xplayer_new(NULL);
    if (player == NULL) {
        printf("Failed to create player\n");
        return -1;
    }
    
    // 3. Set event callback
    xplayer_set_callback(player, player_event_cb, NULL);
    
    // 4. Set media source
    if (xplayer_set_url(player, "file:///fatfs0/Music/test.mp3") < 0) {
        printf("Failed to set URL\n");
        xplayer_free(player);
        return -1;
    }
    
    // 5. Set volume (0~255)
    xplayer_set_vol(player, 200);
    
    // 6. Start playback
    if (xplayer_play(player) < 0) {
        printf("Failed to start playback\n");
        xplayer_free(player);
        return -1;
    }
    
    // 7. Get playback info
    xplay_time_t time;
    xplayer_get_time(player, &time);
    printf("Duration: %llu ms, Current: %llu ms\n", time.duration, time.current_time);
    
    // 8. Playback control example
    sleep(5);  // Play for 5 seconds
    
    // Pause
    xplayer_pause(player);
    sleep(2);  // Pause for 2 seconds
    
    // Resume
    xplayer_resume(player);
    
    // Seek to 30-second position
    xplayer_seek(player, 30000);
    
    // 9. Stop playback and release resources
    xplayer_stop(player);
    xplayer_free(player);
    
    return 0;
}
```

### Decoding Audio Using avcodec

The following example demonstrates how to manually decode audio data:

```c
#include "avcodec/ad.h"
#include "avformat/demux.h"
#include "stream/stream.h"
#include "output/ao.h"

// Decode and play flow example
int decode_and_play(const char *url)
{
    stream_cls_t *stream;
    demux_cls_t *demux;
    ad_cls_t *decoder;
    ao_cls_t *ao;
    ad_conf_t ad_cnf = {0};
    ao_conf_t ao_cnf = {0};
    avpacket_t pkt;
    avframe_t frame;
    int got_frame;
    
    // 1. Open stream
    stream = stream_open(url, NULL);
    if (stream == NULL) {
        return -1;
    }
    
    // 2. Open demuxer
    demux = demux_open(stream);
    if (demux == NULL) {
        stream_close(stream);
        return -1;
    }
    
    // 3. Open audio decoder (assume AAC)
    ad_cnf.sf = SF_S16_STEREO;
    decoder = ad_open(AVCODEC_ID_AAC, &ad_cnf);
    if (decoder == NULL) {
        demux_close(demux);
        stream_close(stream);
        return -1;
    }
    
    // 4. Open audio output
    ao_cnf.period_ms = 50;
    ao_cnf.vol_en = 1;
    ao_cnf.vol_index = 200;
    ao = ao_open(SF_S16_STEREO, &ao_cnf);
    if (ao == NULL) {
        ad_close(decoder);
        demux_close(demux);
        stream_close(stream);
        return -1;
    }
    
    ao_start(ao);
    
    // 5. Decode loop
    while (1) {
        // Read compressed data packet
        if (demux_read_packet(demux, &pkt) < 0) {
            break;
        }
        
        // Decode
        int ret = ad_decode(decoder, &frame, &got_frame, &pkt);
        if (ret < 0 || !got_frame) {
            continue;
        }
        
        // Output audio
        ao_write(ao, frame.data, frame.size);
    }
    
    // 6. Clean up resources
    ao_drain(ao);
    ao_close(ao);
    ad_close(decoder);
    demux_close(demux);
    stream_close(stream);
    
    return 0;
}
```

## Data Structures

### Key Data Types

| Type | Description |
|------|-------------|
| `xplayer_t` | Player handle |
| `stream_cls_t` | Stream handle |
| `demux_cls_t` | Demuxer handle |
| `ad_cls_t` | Audio decoder handle |
| `avfilter_t` | Audio filter handle |
| `ao_cls_t` | Audio output handle |
| `swr_t` | Software resampler handle |
| `resx_t` | Resampler handle |
| `avframe_t` | Audio frame data structure |
| `avpacket_t` | Audio/video data packet structure |

### Player States

```
xplayer state enum:
- XPLAYER_STATE_IDLE      // Idle state
- XPLAYER_STATE_PREPARE   // Preparing state
- XPLAYER_STATE_PLAYING   // Playing
- XPLAYER_STATE_PAUSED    // Paused
- XPLAYER_STATE_STOPPED   // Stopped
```

## Error Handling

All XAV framework interfaces follow a unified error handling convention:

- Return value `0` indicates success
- Return value `-1` or negative indicates failure
- When specific error codes are used, positive values indicate success-related meanings (e.g., `ad_decode` returns the number of bytes consumed)

Recommended error handling pattern:

```c
int ret = xplayer_play(player);
if (ret < 0) {
    printf("Player start failed: %d\n", ret);
    // Error handling
    return ret;
}
```

## References

- [Bouffalo SDK Official Documentation](../CLAUDE.md)
- Multimedia component source: `components/multimedia/xav/`
- xplayer interface definition: `include/xplayer/xplayer.h`
- avcodec interface definition: `include/avcodec/avcodec.h`
- avformat interface definition: `include/avformat/avformat.h`
- stream interface definition: `include/stream/stream.h`
- avfilter interface definition: `include/avfilter/avfilter.h`
- ao interface definition: `include/output/ao.h`
- swresample interface definition: `include/swresample/swresample.h`
