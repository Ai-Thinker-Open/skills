# Smart Audio Framework

## Overview

Smart Audio is the unified audio playback framework for the BL618 chip, integrating four audio sources: local music, notification sounds, Bluetooth A2DP, and Bluetooth HFP. The framework provides volume management and playback state machine, and supports notifying the application layer of playback state changes via a callback mechanism.

## Playback Source Types

| Type | Enum Value | Description |
|------|--------|------|
| SMTAUDIO_ONLINE_MUSIC | MEDIA_MUSIC | Online music playback |
| SMTAUDIO_LOCAL_PLAY | MEDIA_SYSTEM | Local notification sound playback |
| SMTAUDIO_BT_A2DP | 102 | Bluetooth A2DP music |
| SMTAUDIO_BT_HFP | 103 | Bluetooth HFP call |

```c
typedef enum {
    SMTAUDIO_ONLINE_MUSIC = MEDIA_MUSIC,
    SMTAUDIO_LOCAL_PLAY   = MEDIA_SYSTEM,
    SMTAUDIO_BT_A2DP     = 102,
    SMTAUDIO_BT_HFP      = 103,
    SMTAUDIO_PLAY_TYPE_NUM = 4,
    SMTAUDIO_TYPE_ALL     = 255,
} smtaudio_player_type_t;
```

## Playback States

```c
typedef enum {
    SMTAUDIO_STATE_PLAYING,  // Currently playing
    SMTAUDIO_STATE_PAUSE,    // Paused
    SMTAUDIO_STATE_STOP,     // Stopped
    SMTAUDIO_STATE_MUTE,     // Muted
    SMTAUDIO_STATE_NOINIT,   // Not initialized
} smtaudio_state_t;
```

## Sub-State Machine

Each playback source has an independent sub-state:

```c
typedef enum {
    // Online music sub-states
    SMTAUDIO_SUBSTATE_ONLINE_PLAYING,
    SMTAUDIO_SUBSTATE_ONLINE_PAUSE,
    SMTAUDIO_SUBSTATE_ONLINE_STOP,

    // Local notification sound sub-states
    SMTAUDIO_SUBSTATE_LOCAL_PLAYING,
    SMTAUDIO_SUBSTATE_LOCAL_PAUSE,
    SMTAUDIO_SUBSTATE_LOCAL_STOP,

    // Bluetooth A2DP sub-states
    SMTAUDIO_SUBSTATE_BT_A2DP_PLAYING,
    SMTAUDIO_SUBSTATE_BT_A2DP_PAUSE,
    SMTAUDIO_SUBSTATE_BT_A2DP_STOP,

    // Bluetooth HFP sub-states
    SMTAUDIO_SUBSTATE_BT_HFP_PLAYING,
    SMTAUDIO_SUBSTATE_BT_HFP_PAUSE,
    SMTAUDIO_SUBSTATE_BT_HFP_STOP,

    SMTAUDIO_SUBSTATE_MUTE,
} smtaudio_sub_state_t;
```

## Core Constants

| Constant | Value | Description |
|------|-----|------|
| VOLUME_SAVE_KV_NAME | "volume" | Volume persistence key name |
| SMART_AUDIO_DEFAULT_VOLUME | 60 | Default volume value |
| INTERRUPT_REASON_BY_USER | 255 | User interrupt reason code |

## Core API

### Initialization

```c
int8_t smtaudio_init(audio_evt_t audio_evt_cb);
```

### Register Playback Sources

```c
int8_t smtaudio_register_local_play(uint8_t min_vol, uint8_t *aef_conf, 
                                     size_t aef_conf_size, float speed, int resample);
int8_t smtaudio_register_bt_a2dp(uint8_t min_vol, uint8_t *aef_conf,
                                  size_t aef_conf_size, float speed, int resample);
int8_t smtaudio_register_bt_hfp(uint8_t min_vol, uint8_t *aef_conf,
                                 size_t aef_conf_size, float speed, int resample);
int8_t smtaudio_register_online_music(uint8_t min_vol, uint8_t *aef_conf,
                                       size_t aef_conf_size, float speed, int resample);
```

### Playback Control

```c
int8_t smtaudio_start(int type, char *url, uint64_t seek_time, uint8_t resume);
int8_t smtaudio_pause(void);
int8_t smtaudio_resume(void);
int8_t smtaudio_stop(int type);
int8_t smtaudio_mute(void);
```

### Volume Control

```c
int8_t smtaudio_vol_set(int16_t vol);    // Set volume (0-100)
int8_t smtaudio_vol_get(void);           // Get current volume
int8_t smtaudio_vol_up(int16_t vol);     // Increase volume
int8_t smtaudio_vol_down(int16_t vol);   // Decrease volume
int8_t smtaudio_vol_config(audio_vol_config_t *vol_config); // Configure volume mapping
```

### Status Query

```c
smtaudio_state_t smtaudio_get_state(void);
smtaudio_player_type_t smtaudio_get_play_type(void);
int8_t smtaudio_info(int type, smtaudio_play_time_t *t);
```

### Low Power Management

```c
int8_t smtaudio_lpm(uint8_t state);      // Set low power mode
int smtaudio_enter_lpm_check(void);      // Check if can enter low power
```

## Event Callbacks

```c
typedef void (*audio_evt_t)(int type, smtaudio_player_evtid_t evt_id);

typedef enum {
    SMTAUDIO_PLAYER_EVENT_ERROR,
    SMTAUDIO_PLAYER_EVENT_START,
    SMTAUDIO_PLAYER_EVENT_STOP,
    SMTAUDIO_PLAYER_EVENT_RESUME,
    SMTAUDIO_PLAYER_EVENT_UNDER_RUN,
    SMTAUDIO_PLAYER_EVENT_OVER_RUN,
    SMTAUDIO_PLAYER_EVENT_PAUSE,
} smtaudio_player_evtid_t;
```

## Playback Time Info

```c
typedef struct {
    uint64_t duration;  // Total duration (milliseconds)
    uint64_t curtime;   // Current playback position (milliseconds)
} smtaudio_play_time_t;
```

## Volume Config Structure

```c
typedef struct _audio_vol_config {
    int32_t db_min;    // Minimum dB value
    int32_t db_max;    // Maximum dB value
    uint8_t *map;      // Volume mapping table (size 101)
} audio_vol_config_t;
```

## Relationship with Bluetooth Module

### Bluetooth A2DP Interface

```c
int msp_app_bt_a2dp_connect(uint8_t remote_addr[BT_BD_ADDR_LEN]);
int msp_app_bt_a2dp_disconnect(void);
int msp_app_bt_a2dp_get_connect_status(void);
int msp_app_bt_avrcp_send_passthrouth_cmd(msp_app_avrcp_cmd_type_t cmd_type);
int msp_app_bt_avrcp_change_vol(uint8_t vol);
int msp_app_bt_a2dp_register_cb(msp_app_bt_callback_t callback);
```

AVRCP Command Types:

```c
typedef enum {
    MSP_APP_BT_AVRCP_CMD_PLAY = 0,
    MSP_APP_BT_AVRCP_CMD_PAUSE,
    MSP_APP_BT_AVRCP_CMD_FORWARD,
    MSP_APP_BT_AVRCP_CMD_BACKWARD,
    MSP_APP_BT_AVRCP_CMD_FAST_FORWARD,
    MSP_APP_BT_AVRCP_CMD_REWIND,
    MSP_APP_BT_AVRCP_CMD_STOP,
    MSP_APP_BT_AVRCP_CMD_VOL_UP,
    MSP_APP_BT_AVRCP_CMD_VOL_DOWN,
} msp_app_avrcp_cmd_type_t;
```

### Bluetooth HFP Interface

```c
int32_t msp_app_bt_hfp_reg_callback(MSP_APP_BT_HFP_IMPL_CB_FUNC_T *callback);
int32_t msp_app_bt_hfp_connect(const char *mac);
int32_t msp_app_bt_hfp_disconnect(const char *mac);
int32_t msp_app_bt_hfp_connect_audio(const char *mac);
int32_t msp_app_bt_hfp_disconnect_audio(const char *mac);
int32_t msp_app_bt_hfp_send_command(MSP_APP_BT_HFP_COMMAND_T command);
int32_t msp_app_bt_hfp_dial(char *number);
int32_t msp_app_bt_hfp_get_call_status(void);
int32_t msp_app_bt_hfp_volume_update(int type, int volume);
```

HFP State Enums:

```c
typedef enum hfp_call_status {
    CALL_NONE = 0,
    CALL_NO_PROGRESS,
    CALL_IN_PROGRESS,
    CALL_INCOMING,
    CALL_OUTGOING_DIALING,
} msp_app_bt_hfp_call_status_t;

typedef enum {
    MSP_APP_BT_HFP_CONNECTION_STATE_DISCONNECTED = 0,
    MSP_APP_BT_HFP_CONNECTION_STATE_CONNECTING,
    MSP_APP_BT_HFP_CONNECTION_STATE_CONNECTED,
    MSP_APP_BT_HFP_CONNECTION_STATE_SLC_CONNECTED,
    MSP_APP_BT_HFP_CONNECTION_STATE_DISCONNECTING,
} MSP_APP_BT_HFP_STATE_T;

typedef enum {
    MSP_APP_BT_HFP_AUDIO_STATE_DISCONNECTED = 0,
    MSP_APP_BT_HFP_AUDIO_STATE_CONNECTING,
    MSP_APP_BT_HFP_AUDIO_STATE_CONNECTED,
    MSP_APP_BT_HFP_AUDIO_STATE_CONNECTED_MSBC,
} MSP_APP_BT_HFP_AUDIO_STATE_T;
```

## Code Examples

### Example 1: Initialization

```c
#include "smart_audio.h"

void audio_event_callback(int type, smtaudio_player_evtid_t evt_id)
{
    switch (evt_id) {
        case SMTAUDIO_PLAYER_EVENT_START:
            printf("[Audio] Play started\r\n");
            break;
        case SMTAUDIO_PLAYER_EVENT_STOP:
            printf("[Audio] Play stopped\r\n");
            break;
    }
}

void smart_audio_init(void)
{
    // Initialize
    smtaudio_init(audio_event_callback);

    // Register playback sources
    smtaudio_register_local_play(5, NULL, 0, 1.0f, 48000);
    smtaudio_register_bt_a2dp(5, NULL, 0, 1.0f, 48000);
    smtaudio_register_bt_hfp(5, NULL, 0, 1.0f, 16000);
    smtaudio_register_online_music(5, NULL, 0, 1.0f, 48000);

    // Set default volume
    smtaudio_vol_set(SMART_AUDIO_DEFAULT_VOLUME);
}
```

### Example 2: Play Local Notification Sound

```c
void play_notification(void)
{
    // Play local notification sound
    smtaudio_start(SMTAUDIO_LOCAL_PLAY, "/system/notification.wav", 0, 0);

    // Get playback info
    smtaudio_play_time_t time_info;
    smtaudio_info(SMTAUDIO_LOCAL_PLAY, &time_info);
    printf("Duration: %llu ms\r\n", time_info.duration);

    // Stop playback
    smtaudio_stop(SMTAUDIO_LOCAL_PLAY);
}
```

### Example 3: Bluetooth A2DP Playback

```c
#include "bt/msp_app_bt.h"

void bt_a2dp_play(uint8_t *remote_addr)
{
    // Connect Bluetooth device
    msp_app_bt_a2dp_connect(remote_addr);

    // Play Bluetooth music
    smtaudio_start(SMTAUDIO_BT_A2DP, NULL, 0, 1);

    // Set volume
    smtaudio_vol_set(70);

    // Send AVRCP command
    msp_app_bt_avrcp_send_passthrouth_cmd(MSP_APP_BT_AVRCP_CMD_PAUSE);

    // Resume playback
    smtaudio_resume();

    // Get current state
    smtaudio_state_t state = smtaudio_get_state();
    smtaudio_player_type_t type = smtaudio_get_play_type();

    // Disconnect
    msp_app_bt_a2dp_disconnect();
}
```

### Example 4: Bluetooth HFP Call

```c
void hfp_call_callbacks(MSP_APP_BT_HFP_STATE_T state, const char *mac)
{
    printf("[HFP] State: %d, MAC: %s\r\n", state, mac);
}

void bt_hfp_call(const char *mac)
{
    MSP_APP_BT_HFP_IMPL_CB_FUNC_T callbacks = {
        .hfpStateChangedCB = hfp_call_callbacks,
        .hfpAudioStateCB = NULL,
        .hfpVolumeChangedCB = NULL,
        .hfpRingIndCB = NULL,
    };

    // Register callback and connect
    msp_app_bt_hfp_reg_callback(&callbacks);
    msp_app_bt_hfp_connect(mac);
    msp_app_bt_hfp_connect_audio(mac);

    // Set volume
    msp_app_bt_hfp_volume_update(0, 10);

    // Make a call
    msp_app_bt_hfp_dial("10086");

    // Hang up after call ends
    msp_app_bt_hfp_send_command(MSP_APP_BT_HFP_COMMAND_TYPE_TERMINATE);
    msp_app_bt_hfp_disconnect(mac);
}
```

### Example 5: Volume Control

```c
void volume_control(void)
{
    // Set volume
    smtaudio_vol_set(80);

    // Get current volume
    int8_t vol = smtaudio_vol_get();
    printf("Current volume: %d\r\n", vol);

    // Volume adjustment
    smtaudio_vol_up(10);
    smtaudio_vol_down(5);

    // Mute
    smtaudio_mute();
    smtaudio_resume();

    // Get playback state
    smtaudio_state_t state = smtaudio_get_state();
}
```

### Example 6: Custom Volume Mapping

```c
void volume_config_example(void)
{
    static uint8_t volume_db_map[101];

    // Build custom mapping table
    for (int i = 0; i <= 100; i++) {
        volume_db_map[i] = i;  // Linear mapping
    }

    audio_vol_config_t vol_config = {
        .db_min = -60,
        .db_max = 0,
        .map = volume_db_map,
    };

    smtaudio_vol_config(&vol_config);
}
```

## References

- [smart_audio.h header source](../workspase/BL618Claw/bouffalo_sdk/components/multimedia/smart_audio_bl616/include/smart_audio.h)
- [msp_app_bt.h Bluetooth interface header](../workspase/BL618Claw/bouffalo_sdk/components/multimedia/smart_audio_bl616/include/bt/msp_app_bt.h)
- [Bouffalo SDK Multimedia Components](../workspase/BL618Claw/bouffalo_sdk/components/multimedia)
- [BL618 Chip Technical Manual](https://www.bouffalolab.com)
