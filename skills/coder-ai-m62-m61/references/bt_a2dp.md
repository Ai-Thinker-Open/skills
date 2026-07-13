# BL616/BL618 BT Classic A2DP Audio Profile Guide

## Overview

This document describes the A2DP (Advanced Audio Distribution Profile) implementation for Bouffalo Lab BL616/BL618 chips using the Bouffalo SDK. A2DP enables wireless streaming of high-quality audio over Bluetooth Classic.

### Key Components

| Component | Header | Purpose |
|-----------|--------|---------|
| A2DP | `a2dp.h` | Main audio distribution profile |
| SBC Codec | `a2dp-codec.h` | SBC audio codec configuration |
| AVRCP | `avrcp.h` | Audio/video remote control |
| AVCTP | `avctp.h` | AV transport protocol |
| AVDTP | `avdtp.h` | Audio/video distribution transport |

---

## 1. A2DP Initialization

### 1.1 Profile Initialization

```c
#include "bluetooth/a2dp.h"
#include "bluetooth/avrcp.h"

// A2DP callback structure
static struct a2dp_callback a2dp_cb = {
    .chain = a2dp_chain_cb,          // Connection state callback
    .stream = a2dp_stream_cb,        // Stream state callback
    .start_cfm = a2dp_start_cfm_cb,  // Stream start confirmation
    .suspend_cfm = a2dp_suspend_cfm_cb, // Stream suspend confirmation
};

// Connection state callback
static void a2dp_chain_cb(struct bt_conn *conn, uint8_t state)
{
    if (state == BT_A2DP_CHAIN_CONNECTED) {
        printf("A2DP Connected\n");
    } else if (state == BT_A2DP_CHAIN_DISCONNECTED) {
        printf("A2DP Disconnected\n");
    }
}

// Stream state callback
static void a2dp_stream_cb(uint8_t state)
{
    if (state == BT_A2DP_STREAM_START) {
        printf("Stream Started\n");
    } else if (state == BT_A2DP_STREAM_SUSPEND) {
        printf("Stream Suspended\n");
    }
}

// Initialize A2DP profile
int a2dp_init(void)
{
    int ret;

    // Initialize A2DP
    ret = bt_a2dp_init();
    if (ret != 0) {
        printf("A2DP init failed: %d\n", ret);
        return ret;
    }

    // Register A2DP callbacks
    a2dp_cb_register(&a2dp_cb);

    // Initialize SBC decoder (for sink role)
    ret = a2dp_sbc_decode_init();
    if (ret != 0) {
        printf("SBC decode init failed: %d\n", ret);
        return ret;
    }

    return 0;
}
```

### 1.2 Endpoint Registration

A2DP requires registering Stream End Points (SEPs) for Source or Sink roles.

```c
#include "bluetooth/a2dp.h"
#include "bluetooth/a2dp-codec.h"

// SBC codec configuration preset
static uint8_t sbc_preset_data[4] = {
    // Byte 0: Sample frequency (44100) | Channel mode (Stereo)
    (A2DP_SBC_SAMP_FREQ_44100 | A2DP_SBC_CH_MODE_STREO),
    // Byte 1: Block length (16) | Subbands (8) | Allocation (Loudness)
    (A2DP_SBC_BLK_LEN_16 | A2DP_SBC_SUBBAND_8 | A2DP_SBC_ALLOC_MTHD_LOUDNESS),
    // Byte 2: Min bitpool
    2,
    // Byte 3: Max bitpool
    53
};

// Create preset structure
static struct bt_a2dp_preset sbc_preset = {
    .len = 4,
    .preset = sbc_preset_data
};

// A2DP Source endpoint (streaming device)
static struct bt_a2dp_endpoint a2dp_source_endpoint = {
    .codec_id = BT_A2DP_SBC,
    .preset = &sbc_preset,
    .caps = &sbc_preset,
};

// A2DP Sink endpoint (receiving device)
static struct bt_a2dp_endpoint a2dp_sink_endpoint = {
    .codec_id = BT_A2DP_SBC,
    .preset = &sbc_preset,
    .caps = &sbc_preset,
};

// Register A2DP Source endpoint
int register_a2dp_source(void)
{
    int ret;

    // Register as Source role (BT_A2DP_SOURCE = 0)
    ret = bt_a2dp_register_endpoint(&a2dp_source_endpoint,
                                    BT_A2DP_AUDIO,  // Media type
                                    BT_A2DP_SOURCE); // Role
    if (ret != 0) {
        printf("Register A2DP Source endpoint failed: %d\n", ret);
        return ret;
    }

    printf("A2DP Source endpoint registered\n");
    return 0;
}

// Register A2DP Sink endpoint
int register_a2dp_sink(void)
{
    int ret;

    // Register as Sink role (BT_A2DP_SINK = 1)
    ret = bt_a2dp_register_endpoint(&a2dp_sink_endpoint,
                                    BT_A2DP_AUDIO,  // Media type
                                    BT_A2DP_SINK);  // Role
    if (ret != 0) {
        printf("Register A2DP Sink endpoint failed: %d\n", ret);
        return ret;
    }

    printf("A2DP Sink endpoint registered\n");
    return 0;
}
```

---

## 2. SBC Codec Configuration

### 2.1 SBC Parameters

The SBC (Sub-band Coding) codec is the mandatory codec for A2DP.

```c
#include "bluetooth/a2dp-codec.h"

// SBC codec configuration structure
struct bt_a2dp_codec_sbc_params {
    uint8_t config[2];       // Codec configuration bytes
    uint8_t min_bitpool;     // Minimum bitpool (2-130)
    uint8_t max_bitpool;     // Maximum bitpool (2-130)
} __packed;

// SBC capability flags
// Sampling Frequency
#define A2DP_SBC_SAMP_FREQ_16000 BIT(7)  // 16 kHz
#define A2DP_SBC_SAMP_FREQ_32000 BIT(6)  // 32 kHz
#define A2DP_SBC_SAMP_FREQ_44100 BIT(5)  // 44.1 kHz
#define A2DP_SBC_SAMP_FREQ_48000 BIT(4)  // 48 kHz

// Channel Mode
#define A2DP_SBC_CH_MODE_MONO   BIT(3)   // Mono
#define A2DP_SBC_CH_MODE_DUAL   BIT(2)   // Dual channel
#define A2DP_SBC_CH_MODE_STREO  BIT(1)   // Stereo
#define A2DP_SBC_CH_MODE_JOINT  BIT(0)   // Joint stereo

// Block Length
#define A2DP_SBC_BLK_LEN_4  BIT(7)  // 4 blocks
#define A2DP_SBC_BLK_LEN_8  BIT(6)  // 8 blocks
#define A2DP_SBC_BLK_LEN_12 BIT(5)  // 12 blocks
#define A2DP_SBC_BLK_LEN_16 BIT(4)  // 16 blocks

// Subbands
#define A2DP_SBC_SUBBAND_4 BIT(3)   // 4 subbands
#define A2DP_SBC_SUBBAND_8 BIT(2)   // 8 subbands

// Allocation Method
#define A2DP_SBC_ALLOC_MTHD_SNR      BIT(1)  // SNR method
#define A2DP_SBC_ALLOC_MTHD_LOUDNESS BIT(0)  // Loudness method

// Helper macros to extract SBC parameters from preset
#define BT_A2DP_SBC_SAMP_FREQ(preset)    ((preset->config[0] >> 4) & 0x0f)
#define BT_A2DP_SBC_CHAN_MODE(preset)    ((preset->config[0]) & 0x0f)
#define BT_A2DP_SBC_BLK_LEN(preset)      ((preset->config[1] >> 4) & 0x0f)
#define BT_A2DP_SBC_SUB_BAND(preset)     ((preset->config[1] >> 2) & 0x03)
#define BT_A2DP_SBC_ALLOC_MTHD(preset)   ((preset->config[1]) & 0x03)
```

### 2.2 SBC Configuration Example

```c
// High quality SBC configuration for A2DP Source
int configure_sbc_high_quality(void)
{
    struct bt_a2dp_codec_sbc_params sbc_params;
    
    // Config byte 0: 44.1 kHz + Joint Stereo
    sbc_params.config[0] = (A2DP_SBC_SAMP_FREQ_44100 >> 4) | A2DP_SBC_CH_MODE_JOINT;
    
    // Config byte 1: 16 blocks + 8 subbands + Loudness
    sbc_params.config[1] = (A2DP_SBC_BLK_LEN_16 >> 4) | A2DP_SBC_SUBBAND_8 | A2DP_SBC_ALLOC_MTHD_LOUDNESS;
    
    // Bitpool range for high quality
    sbc_params.min_bitpool = 2;
    sbc_params.max_bitpool = 53;

    printf("SBC Config: freq=%d, mode=%d, blocks=%d, subbands=%d, alloc=%d\n",
           BT_A2DP_SBC_SAMP_FREQ(&sbc_params),
           BT_A2DP_SBC_CHAN_MODE(&sbc_params),
           BT_A2DP_SBC_BLK_LEN(&sbc_params),
           BT_A2DP_SBC_SUB_BAND(&sbc_params),
           BT_A2DP_SBC_ALLOC_MTHD(&sbc_params));

    return 0;
}
```

---

## 3. A2DP Connection Management

### 3.1 Connect A2DP

```c
#include "bluetooth/a2dp.h"

// Global A2DP connection pointer
static struct bt_a2dp *a2dp_conn = NULL;

// Connect to peer A2DP device
int a2dp_connect(struct bt_conn *conn)
{
    int ret;

    if (a2dp_conn != NULL) {
        printf("A2DP already connected\n");
        return -EALREADY;
    }

    ret = bt_a2dp_connect(conn);
    if (ret != 0) {
        printf("A2DP connect failed: %d\n", ret);
        return ret;
    }

    printf("A2DP connection initiated\n");
    return 0;
}

// Disconnect A2DP
int a2dp_disconnect(void)
{
    int ret;
    struct bt_conn *conn;

    if (a2dp_conn == NULL) {
        printf("A2DP not connected\n");
        return -ENOTCONN;
    }

    // Get connection from A2DP handle
    // Note: Implementation-specific method to obtain bt_conn
    conn = get_conn_from_a2dp(a2dp_conn);
    if (conn == NULL) {
        return -ENOTCONN;
    }

    ret = bt_a2dp_disconnect(conn);
    if (ret != 0) {
        printf("A2DP disconnect failed: %d\n", ret);
        return ret;
    }

    a2dp_conn = NULL;
    printf("A2DP disconnected\n");
    return 0;
}
```

### 3.2 Stream Control (Discovery/Configuration)

```c
// Start A2DP discovery to find peer endpoints
int a2dp_start_discovery(struct bt_conn *conn)
{
    int ret;

    ret = bt_a2dp_start_discovery(conn);
    if (ret != 0) {
        printf("A2DP discovery failed: %d\n", ret);
        return ret;
    }

    printf("A2DP discovery started\n");
    return 0;
}

// Get peer capabilities
int a2dp_get_capabilities(struct bt_conn *conn)
{
    int ret;

    ret = bt_a2dp_get_cap(conn);
    if (ret != 0) {
        printf("Get capabilities failed: %d\n", ret);
        return ret;
    }

    printf("Capabilities retrieved\n");
    return 0;
}

// Configure stream with peer endpoint
int a2dp_configure_stream(struct bt_conn *conn, uint8_t acp_seid)
{
    int ret;

    ret = bt_a2dp_set_conf(conn, acp_seid);
    if (ret != 0) {
        printf("Configure stream failed: %d\n", ret);
        return ret;
    }

    printf("Stream configured with SEID: %d\n", acp_seid);
    return 0;
}

// Open stream
int a2dp_open_stream(struct bt_conn *conn)
{
    int ret;

    ret = bt_a2dp_open_stream(conn);
    if (ret != 0) {
        printf("Open stream failed: %d\n", ret);
        return ret;
    }

    printf("Stream opened\n");
    return 0;
}

// Start streaming
int a2dp_start_stream(struct bt_conn *conn)
{
    int ret;

    ret = bt_a2dp_start_stream(conn);
    if (ret != 0) {
        printf("Start stream failed: %d\n", ret);
        return ret;
    }

    printf("Stream started\n");
    return 0;
}

// Suspend streaming
int a2dp_suspend_stream(struct bt_conn *conn)
{
    int ret;

    ret = bt_a2dp_suspend_stream(conn);
    if (ret != 0) {
        printf("Suspend stream failed: %d\n", ret);
        return ret;
    }

    printf("Stream suspended\n");
    return 0;
}

// Close stream
int a2dp_close_stream(struct bt_conn *conn)
{
    int ret;

    ret = bt_a2dp_close_stream(conn);
    if (ret != 0) {
        printf("Close stream failed: %d\n", ret);
        return ret;
    }

    printf("Stream closed\n");
    return 0;
}
```

---

## 4. Stream Management

### 4.1 Send Media Data (Source Role)

```c
// Send audio data to peer
int a2dp_send_media_data(const uint8_t *audio_data, uint32_t size)
{
    int ret;

    ret = bt_a2dp_send_media(audio_data, size);
    if (ret != 0) {
        printf("Send media failed: %d\n", ret);
        return ret;
    }

    return 0;
}

// Example: PCM to SBC encoding and sending
int send_pcm_audio(const uint8_t *pcm_data, uint32_t pcm_size)
{
    // SBC encoder would process PCM data here
    // For details, see sbc_encoder.h in the SDK
    
    uint8_t sbc_encoded[1030];  // Max SBC packet size
    uint32_t encoded_size;
    
    // Encode PCM to SBC (pseudo-code - actual implementation varies)
    // encoded_size = sbc_encode(pcm_data, pcm_size, sbc_encoded);
    
    // Send to peer
    return bt_a2dp_send_media(sbc_encoded, encoded_size);
}
```

### 4.2 Receive Media Data (Sink Role)

```c
// PCM interface callback structure
static A2DP_PCM_PRCOESS pcm_cb = {
    .open = pcm_open,
    .close = pcm_close,
    .write = pcm_write,
    .read = pcm_read,
    .start = pcm_start,
    .stop = pcm_stop,
    .ioctl = pcm_ioctl,
};

// Register PCM callback for decoded audio output
void register_pcm_interface(void)
{
    register_pcm(&pcm_cb);
}

// SBC decode process (for sink to decode received SBC data)
int process_received_sbc(uint8_t *media_data, uint16_t data_len)
{
    int ret;

    ret = a2dp_sbc_decode_process(media_data, data_len);
    if (ret != 0) {
        printf("SBC decode failed: %d\n", ret);
        return ret;
    }

    return 0;
}

// Audio run loop - call periodically to process audio
void audio_process_loop(void)
{
    audio_run();
}
```

### 4.3 Stream Resume/Suspend API

```c
// Resume stream (convenience API)
int bt_stream_resume(struct bt_conn *conn)
{
    int ret;

    ret = bt_stream_resume(conn);
    if (ret != 0) {
        printf("Stream resume failed: %d\n", ret);
        return ret;
    }

    printf("Stream resumed\n");
    return 0;
}

// Suspend stream (convenience API)
int bt_stream_suspend(struct bt_conn *conn)
{
    int ret;

    ret = bt_stream_suspend(conn);
    if (ret != 0) {
        printf("Stream suspend failed: %d\n", ret);
        return ret;
    }

    printf("Stream suspended\n");
    return 0;
}
```

---

## 5. AVRCP Control (Play/Pause/Volume)

### 5.1 AVRCP Initialization

```c
#include "bluetooth/avrcp.h"

// AVRCP callback structure
static struct avrcp_callback avrcp_cb = {
    .chain = avrcp_chain_cb,                 // Connection state
    .abs_vol = avrcp_abs_vol_cb,             // Absolute volume changed
    .play_status = avrcp_play_status_cb,     // Playback status
    .tg_reg_ntf_evt = avrcp_reg_evt_cb,      // Registered event
    .rp_passthrough = avrcp_rp_passthrough_cb,
    .passthrough_handler = avrcp_passthrough_cb,
};

// AVRCP connection callback
static void avrcp_chain_cb(struct bt_conn *conn, uint8_t state)
{
    if (state == BT_AVRCP_CHAIN_CONNECTED) {
        printf("AVRCP Connected\n");
    } else if (state == BT_AVRCP_CHAIN_DISCONNECTED) {
        printf("AVRCP Disconnected\n");
    }
}

// Absolute volume callback (0-127)
static void avrcp_abs_vol_cb(uint8_t vol)
{
    printf("Volume changed: %d/127\n", vol);
    
    // Update local volume control
    set_audio_volume(vol * 100 / 127);  // Convert to percentage
}

// Play status callback
static void avrcp_play_status_cb(uint32_t song_len, uint32_t song_pos, uint8_t status)
{
    printf("Play status: %s, position: %u/%u\n",
           status == PLAY_STATUS_PLAYING ? "Playing" :
           status == PLAY_STATUS_PAUSED ? "Paused" : "Stopped",
           song_pos, song_len);
}

// Initialize AVRCP
int avrcp_init(void)
{
    int ret;

    ret = bt_avrcp_init();
    if (ret != 0) {
        printf("AVRCP init failed: %d\n", ret);
        return ret;
    }

    avrcp_cb_register(&avrcp_cb);
    printf("AVRCP initialized\n");

    return 0;
}
```

### 5.2 AVRCP Connection

```c
static struct bt_avrcp *avrcp_conn = NULL;

// Connect AVRCP
int avrcp_connect(struct bt_conn *conn)
{
    int ret;

    if (avrcp_conn != NULL) {
        printf("AVRCP already connected\n");
        return -EALREADY;
    }

    avrcp_conn = bt_avrcp_connect(conn);
    if (avrcp_conn == NULL) {
        printf("AVRCP connect failed\n");
        return -EIO;
    }

    printf("AVRCP connection initiated\n");
    return 0;
}
```

### 5.3 AVRCP Pass-Through Commands (Play/Pause/Stop)

```c
// AVRCP key operation IDs
#define AVRCP_KEY_PLAY         0x44
#define AVRCP_KEY_STOP         0x45
#define AVRCP_KEY_PAUSE        0x46
#define AVRCP_KEY_VOL_UP       0x41
#define AVRCP_KEY_VOL_DOWN     0x42
#define AVRCP_KEY_REWIND       0x48
#define AVRCP_KEY_FAST_FORWARD 0x49

// Send AVRCP pass-through command
int avrcp_send_passthrough(uint8_t opid)
{
    int ret;

    if (avrcp_conn == NULL) {
        printf("AVRCP not connected\n");
        return -ENOTCONN;
    }

    // Press and release (two commands)
    ret = avrcp_pasthr_cmd(&avrcp_conn->session, PASTHR_STATE_PRESSED, opid);
    if (ret != 0) {
        return ret;
    }

    k_msleep(50);  // Small delay between press and release

    ret = avrcp_pasthr_cmd(&avrcp_conn->session, PASTHR_STATE_RELEASED, opid);
    if (ret != 0) {
        return ret;
    }

    return 0;
}

// Control functions
int avrcp_play(void)
{
    return avrcp_send_passthrough(AVRCP_KEY_PLAY);
}

int avrcp_pause(void)
{
    return avrcp_send_passthrough(AVRCP_KEY_PAUSE);
}

int avrcp_stop(void)
{
    return avrcp_send_passthrough(AVRCP_KEY_STOP);
}

int avrcp_volume_up(void)
{
    return avrcp_send_passthrough(AVRCP_KEY_VOL_UP);
}

int avrcp_volume_down(void)
{
    return avrcp_send_passthrough(AVRCP_KEY_VOL_DOWN);
}

int avrcp_rewind(void)
{
    return avrcp_send_passthrough(AVRCP_KEY_REWIND);
}

int avrcp_fast_forward(void)
{
    return avrcp_send_passthrough(AVRCP_KEY_FAST_FORWARD);
}
```

### 5.4 AVRCP Volume Control (Absolute)

```c
// Set absolute volume (0-127)
int avrcp_set_absolute_volume(uint8_t volume)
{
    int ret;
    uint8_t avrcp_vol;

    if (avrcp_conn == NULL) {
        return -ENOTCONN;
    }

    // Clamp volume to valid range
    avrcp_vol = (volume > 127) ? 127 : volume;

    ret = avrcp_set_absvol_cmd(&avrcp_conn->session, avrcp_vol);
    if (ret != 0) {
        printf("Set absolute volume failed: %d\n", ret);
        return ret;
    }

    printf("Absolute volume set to: %d/127\n", avrcp_vol);
    return 0;
}

// Send volume notification (for Target role)
int avrcp_notify_volume_change(uint8_t volume)
{
    int ret;

    if (avrcp_conn == NULL) {
        return -ENOTCONN;
    }

    ret = avrcp_send_volume_notification(&avrcp_conn->session);
    if (ret != 0) {
        printf("Volume notification failed: %d\n", ret);
        return ret;
    }

    return 0;
}

// Handle set absolute volume from Controller
int avrcp_handle_set_abs_vol(struct bt_avctp *session, uint8_t trans_lab, uint8_t *params)
{
    uint8_t volume;

    volume = params[0] & ABS_VOL_MASK;
    printf("Received absolute volume: %d/127\n", volume);

    // Apply volume to audio output
    set_audio_volume(volume * 100 / 127);

    return avrcp_hdl_set_abs_vol(session, trans_lab, params);
}
```

### 5.5 AVRCP Play Status

```c
// Get play status
int avrcp_get_play_status(void)
{
    int ret;

    if (avrcp_conn == NULL) {
        return -ENOTCONN;
    }

    ret = avrcp_get_play_status_cmd(&avrcp_conn->session);
    if (ret != 0) {
        printf("Get play status failed: %d\n", ret);
        return ret;
    }

    return 0;
}

// Register for play status notifications
int avrcp_register_play_status_notification(void)
{
    int ret;

    if (avrcp_conn == NULL) {
        return -ENOTCONN;
    }

    ret = avrcp_reg_not_cmd(&avrcp_conn->session, EVENT_PLAYBACK_STATUS_CHANGED);
    if (ret != 0) {
        printf("Register notification failed: %d\n", ret);
        return ret;
    }

    return 0;
}

// Set player parameters (for Target role)
void avrcp_update_player_status(uint8_t status, uint32_t position, uint32_t duration)
{
    avrcp_set_player_parameter(status, position, duration);
}

// Example: Update player status
void update_now_playing(void)
{
    // Set as playing, position 30 seconds into a 4 minute song
    avrcp_update_player_status(PLAY_STATUS_PLAYING, 30000, 240000);
}
```

---

## 6. Complete Usage Example

### 6.1 A2DP Source (Speaker) Implementation

```c
#include "bluetooth/bluetooth.h"
#include "bluetooth/hci.h"
#include "bluetooth/a2dp.h"
#include "bluetooth/a2dp-codec.h"
#include "bluetooth/avrcp.h"

static struct bt_conn *a2dp_peer_conn = NULL;

// GAP connection callback
static void connected(struct bt_conn *conn, uint8_t err)
{
    if (err) {
        printf("Connection failed (err 0x%02x)\n", err);
        return;
    }

    printf("Connected\n");
    a2dp_peer_conn = bt_conn_ref(conn);
}

// GAP disconnection callback
static void disconnected(struct bt_conn *conn, uint8_t reason)
{
    printf("Disconnected (reason 0x%02x)\n", reason);
    
    if (a2dp_peer_conn) {
        bt_conn_unref(a2dp_peer_conn);
        a2dp_peer_conn = NULL;
    }
}

static struct bt_conn_cb conn_callbacks = {
    .connected = connected,
    .disconnected = disconnected,
};

// A2DP callbacks
static struct a2dp_callback a2dp_cbs = {
    .chain = chain_cb,
    .stream = stream_cb,
    .start_cfm = start_cfm_cb,
    .suspend_cfm = suspend_cfm_cb,
};

static void chain_cb(struct bt_conn *conn, uint8_t state)
{
    printf("A2DP chain state: %s\n", 
           state == BT_A2DP_CHAIN_CONNECTED ? "Connected" : "Disconnected");
}

static void stream_cb(uint8_t state)
{
    printf("A2DP stream state: %s\n",
           state == BT_A2DP_STREAM_START ? "Started" : "Suspended");
}

static void start_cfm_cb(void)
{
    printf("Stream start confirmed - begin sending audio\n");
}

static void suspend_cfm_cb(void)
{
    printf("Stream suspend confirmed\n");
}

// SBC preset for CD quality audio
static uint8_t sbc_preset[] = {
    (A2DP_SBC_SAMP_FREQ_44100 | A2DP_SBC_CH_MODE_JOINT) & 0xFF,
    (A2DP_SBC_BLK_LEN_16 | A2DP_SBC_SUBBAND_8 | A2DP_SBC_ALLOC_MTHD_LOUDNESS),
    2,   // min bitpool
    53   // max bitpool
};

static struct bt_a2dp_preset sbc_preset_cfg = {
    .len = 4,
    .preset = sbc_preset
};

static struct bt_a2dp_endpoint a2dp_src_ep = {
    .codec_id = BT_A2DP_SBC,
    .preset = &sbc_preset_cfg,
    .caps = &sbc_preset_cfg,
};

int a2dp_speaker_init(void)
{
    int ret;

    // Initialize Bluetooth
    ret = bt_enable(NULL);
    if (ret) {
        printf("Bluetooth init failed: %d\n", ret);
        return ret;
    }

    bt_conn_cb_register(&conn_callbacks);

    // Initialize A2DP
    ret = bt_a2dp_init();
    if (ret) {
        printf("A2DP init failed: %d\n", ret);
        return ret;
    }
    a2dp_cb_register(&a2dp_cbs);

    // Register Source endpoint
    ret = bt_a2dp_register_endpoint(&a2dp_src_ep, BT_A2DP_AUDIO, BT_A2DP_SOURCE);
    if (ret) {
        printf("Register endpoint failed: %d\n", ret);
        return ret;
    }

    printf("A2DP Speaker initialized\n");
    return 0;
}

// Send audio data periodically
void send_audio_stream(const uint8_t *pcm_buffer, uint32_t size)
{
    if (a2dp_peer_conn == NULL) {
        return;
    }

    bt_a2dp_send_media(pcm_buffer, size);
}
```

### 6.2 A2DP Sink (Headphone) Implementation

```c
#include "bluetooth/bluetooth.h"
#include "bluetooth/a2dp.h"
#include "bluetooth/a2dp-codec.h"
#include "bluetooth/avrcp.h"

static struct bt_conn *avrcp_peer_conn = NULL;

// PCM output callbacks
static int pcm_open_cb(int sample_rate, int channels)
{
    printf("PCM opened: %d Hz, %d channels\n", sample_rate, channels);
    return 0;
}

static int pcm_close_cb(void)
{
    printf("PCM closed\n");
    return 0;
}

static int pcm_write_cb(uint8_t *data, uint32_t size)
{
    // Write to I2S/DAC - actual implementation
    // i2s_write(data, size);
    return 0;
}

static A2DP_PCM_PRCOESS pcm_ops = {
    .open = pcm_open_cb,
    .close = pcm_close_cb,
    .write = pcm_write_cb,
    .read = NULL,
    .start = NULL,
    .stop = NULL,
    .ioctl = NULL,
};

int a2dp_headphone_init(void)
{
    int ret;

    ret = bt_enable(NULL);
    if (ret) {
        return ret;
    }

    // Initialize A2DP
    ret = bt_a2dp_init();
    if (ret) {
        return ret;
    }
    a2dp_cb_register(&a2dp_cbs);

    // Initialize SBC decoder
    ret = a2dp_sbc_decode_init();
    if (ret) {
        return ret;
    }

    // Register PCM interface for decoded audio
    register_pcm(&pcm_ops);

    // Initialize AVRCP
    ret = bt_avrcp_init();
    if (ret) {
        return ret;
    }
    avrcp_cb_register(&avrcp_cbs);

    // Register Sink endpoint
    ret = bt_a2dp_register_endpoint(&a2dp_sink_ep, BT_A2DP_AUDIO, BT_A2DP_SINK);
    if (ret) {
        return ret;
    }

    printf("A2DP Headphone initialized\n");
    return 0;
}
```

---

## 7. AVDTP Stream States

The AVDTP (Audio/Video Distribution Transport Protocol) manages stream states:

```
IDLE ──────────────► CONFIGURED ──────────────► OPEN
                                              │
                                              ▼
                                          STREAMING ◄──► CLOSING
                                              │
                                              ▼
                                         ABORTING
```

| State | Description |
|-------|-------------|
| `AVDTP_IDLE` | Stream endpoint initialized |
| `AVDTP_CONFIGURED` | Stream configured by INT |
| `AVDTP_OPEN` | Stream opened between endpoints |
| `AVDTP_STREAMING` | Active streaming |
| `AVDTP_CLOSING` | Stream being closed |
| `AVDTP_ABORTING` | Stream aborted |

---

## 8. Data Structures Summary

### A2DP Core

| Structure | Purpose |
|-----------|---------|
| `struct bt_a2dp` | A2DP connection handle |
| `struct bt_a2dp_stream` | Stream instance |
| `struct bt_a2dp_endpoint` | Stream end point |
| `struct bt_a2dp_config` | Stream configuration |

### Codec

| Structure | Purpose |
|-----------|---------|
| `struct bt_a2dp_codec_sbc_params` | SBC codec parameters |
| `a2dp_sbc_t` | Compact SBC configuration |

### AVRCP

| Structure | Purpose |
|-----------|---------|
| `struct bt_avrcp` | AVRCP connection handle |
| `struct avrcp_callback` | Event callbacks |
| `struct avrcp_media_player` | Player status |

---

## 9. Build Configuration

Ensure these Kconfig options are enabled:

```
CONFIG_BT=y
CONFIG_BT_CLASSIC=y
CONFIG_BT_A2DP=y
CONFIG_BT_A2DP_SINK=y
CONFIG_BT_A2DP_SOURCE=y
CONFIG_BT_AVRCP=y
CONFIG_BT_AVDTP=y
CONFIG_BT_AVCTP=y
```

---

## 10. Header Files Reference

| Header | Path |
|--------|------|
| `a2dp.h` | `bouffalo_sdk/components/wireless/bluetooth/btprofile/include/bluetooth/a2dp.h` |
| `a2dp-codec.h` | `bouffalo_sdk/components/wireless/bluetooth/btprofile/include/bluetooth/a2dp-codec.h` |
| `avrcp.h` | `bouffalo_sdk/components/wireless/bluetooth/btprofile/include/bluetooth/avrcp.h` |
| `avctp.h` | `bouffalo_sdk/components/wireless/bluetooth/btprofile/include/bluetooth/avctp.h` |
| `avdtp.h` | `bouffalo_sdk/components/wireless/bluetooth/btprofile/include/bluetooth/avdtp.h` |
