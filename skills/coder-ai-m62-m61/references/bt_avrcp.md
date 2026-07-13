# Bluetooth AVRCP Technical Documentation

## 1. Overview

AVRCP (Audio/Video Remote Control Profile) is a profile in the Bluetooth protocol stack used to control audio stream playback via A2DP (Advanced Audio Distribution Profile). Through AVRCP, users can remotely control music playback functions on another Bluetooth device, such as play, pause, stop, previous track, next track, and volume adjustment.

AVRCP uses AVCTP (Audio/Video Control Transport Protocol) for data transmission. AVCTP defines the transport format for control commands and response messages between devices, while AVRCP defines the semantics and interaction flow of these commands.

In the Bluetooth protocol stack, AVRCP typically works together with A2DP:
- **A2DP**: Responsible for audio data transmission, determining audio quality and encoding format
- **AVRCP**: Responsible for playback control, implementing user interaction operations

The two work in concert: AVRCP sends playback control commands, while A2DP transmits the actual audio stream data, thus enabling complete Bluetooth music playback functionality.

## 2. AVCTP Transport Layer

AVCTP is the underlying transport protocol for AVRCP, defining the encapsulation format for commands and responses.

### 2.1 AVCTP Key Parameters

| Parameter | Value | Description |
|------|-----|------|
| L2CAP PSM | 0x0017 | The L2CAP protocol service channel used by AVCTP |
| PID | 0x0e11 | Protocol identifier |
| CR Command | 0 | Command packet |
| CR Response | 1 | Response packet |

### 2.2 AVCTP Packet Types

AVCTP supports four packet types for handling data of different lengths:

| Type | Value | Description |
|------|-----|------|
| SINGLE | 0x0 | Single packet, complete data in one packet |
| START | 0x1 | First fragment packet |
| CONTINUE | 0x2 | Continuation fragment packet |
| END | 0x3 | Last fragment packet |

When AVRCP command or response data exceeds the L2CAP MTU size, AVCTP automatically splits the data into multiple packets for transmission, and the receiver reassembles the packets into complete data.

## 3. AVRCP Command Types (ctype)

AVRCP defines several command types to distinguish different operational intents:

| Command Type | Value | Description |
|----------|-----|------|
| CONTROL | 0x00 | Control command, used to perform playback control operations |
| STATUS | 0x01 | Status query, used to obtain the current playback status |
| SPECIFIC_INQUIRY | 0x02 | Specific inquiry |
| NOTIFY | 0x03 | Event notification registration, requesting the target to actively push specific events |
| GENERAL_INQUIRY | 0x04 | General inquiry |

### 3.1 CONTROL Command

The CONTROL command is used to perform specific playback control operations, such as play, pause, stop, etc. These commands typically require the target device to execute the corresponding action and return a response.

### 3.2 STATUS Command

The STATUS command is used to query the current state of the target device, such as playback status, current track information, playback position, etc. Upon receiving such a command, the target device should return a response containing the current state information.

### 3.3 NOTIFY Command

The NOTIFY command is used to register event notifications. When a device sends a NOTIFY command to subscribe to a certain event, the target device will actively push notifications to the subscriber whenever that event occurs. This is an event-driven model that avoids frequent polling by the client.

## 4. AVRCP Response Types

AVRCP command responses have the following types:

| Response Type | Value | Description |
|----------|-----|------|
| NOT_IMPLEMENTED | 0x08 | Command is not supported or cannot be processed |
| ACCEPTED | 0x09 | Command has been accepted and successfully executed |
| REJECTED | 0x0A | Command rejected, typically due to parameter error or incorrect state |
| IN_TRANSITION | 0x0B | State is in transition |
| IMPLEMENTED | 0x0C | Command has been implemented (for query responses) |
| CHANGED | 0x0D | State has changed |
| INTERIM | 0x0F | Interim response, indicating the command is being processed |

The INTERIM response is typically used for NOTIFY commands. When the target device receives a subscription request, it first returns an INTERIM response to acknowledge receipt, and the actual event notification is sent later.

## 5. AVRCP Opcodes

Opcodes define the specific operation types of AVRCP commands:

| Opcode | Value | Description |
|--------|-----|------|
| UNIT_INFO | 0x30 | Unit information query |
| SUBUNIT_INFO | 0x31 | Subunit information query |
| PASS_THROUGH | 0x7C | Pass-through command, used to transmit key/control operations |
| VENDOR_DEPENDENT | 0x00 | Vendor-defined command |

### 5.1 PASS_THROUGH Command

PASS_THROUGH is the most commonly used opcode for transmitting standard playback control commands. All play, pause, stop, previous/next track operations are sent via the PASS_THROUGH command.

### 5.2 VENDOR_DEPENDENT Command

VENDOR_DEPENDENT is used to transmit vendor-defined command extensions and can be used to implement non-standard control functions or transmit vendor-specific metadata.

## 6. Key States (Pass-through State)

In the PASS_THROUGH command, each key operation includes two states:

| State | Value | Description |
|------|-----|------|
| PRESSED | 0x00 | Key pressed |
| RELEASED | 0x01 | Key released |

A typical user interaction flow is: send the PRESSED state when the key is pressed, and send the RELEASED state when the key is released. This design allows the target device to distinguish between short press and long press operations.

## 7. Playback Status

AVRCP defines the following playback statuses:

| Playback Status | Value | Description |
|----------|-----|------|
| STOPPED | 0x00 | Playback stopped |
| PLAYING | 0x01 | Currently playing |
| PAUSED | 0x02 | Playback paused |
| FWD_SEEK | 0x03 | Fast-forwarding |
| REV_SEEK | 0x04 | Rewinding |
| ERROR | 0xFF | Playback error |

## 8. Key Operation IDs

The operation IDs in PASS_THROUGH commands define specific control functions:

| Operation ID | Value | Description |
|---------|-----|------|
| KEY_VOL_UP | 0x41 | Volume up |
| KEY_VOL_DOWN | 0x42 | Volume down |
| KEY_PLAY | 0x44 | Play |
| KEY_STOP | 0x45 | Stop |
| KEY_PAUSE | 0x46 | Pause |
| KEY_REWIND | 0x48 | Rewind / Previous track |
| KEY_FAST_FORWARD | 0x49 | Fast forward / Next track |
| KEY_FORWARD | 0x4B | Next track |
| KEY_BACKWARD | 0x4C | Previous track |

## 9. Event Notifications

AVRCP supports various event notification types. Devices can subscribe to these events via the NOTIFY command:

| Event ID | Value | Description |
|----------|-----|------|
| PLAYBACK_STATUS_CHANGED | 0x01 | Playback status changed |
| TRACK_CHANGED | 0x02 | Track changed |
| TRACK_REACHED_END | 0x03 | Track playback reached the end |
| TRACK_REACHED_START | 0x04 | Track playback reached the beginning |
| PLAYBACK_POS_CHANGED | 0x05 | Playback position changed |
| BATT_STATUS_CHANGED | 0x06 | Battery status changed |
| SYSTEM_STATUS_CHANGED | 0x07 | System status changed |
| PLAYER_APPLICATION_SETTING_CHANGED | 0x08 | Player application setting changed |
| NOW_PLAYING_CONTENT_CHANGED | 0x09 | Now playing content changed |
| AVAILABLE_PLAYERS_CHANGED | 0x0A | Available player list changed |
| ADDRESSED_PLAYER_CHANGED | 0x0B | Currently addressed player changed |
| UIDS_CHANGED | 0x0C | UIDs list changed |
| VOLUME_CHANGED | 0x0D | Volume changed |

### 9.1 Common Event Descriptions

**PLAYBACK_STATUS_CHANGED (0x01)**
Triggered when the playback status changes, such as from playing to paused, or from paused to playing. The event data contains the new playback status value.

**TRACK_CHANGED (0x02)**
Triggered when the currently playing track changes, such as switching to the next or previous track. The event data contains the identifier information of the new track.

**PLAYBACK_POS_CHANGED (0x05)**
Triggered when the playback position changes. This event is used to synchronize playback progress, and the event data contains the current playback position (in milliseconds).

**VOLUME_CHANGED (0x0D)**
Triggered when the volume changes. The event data contains the current volume value (0x00-0x7F). Note that the volume value only uses the lower 7 bits.

## 10. Vendor Command PDU IDs

In VENDOR_DEPENDENT commands, PDU IDs are used to identify different vendor-defined operations:

| PDU ID | Value | Command Type | Description |
|--------|-----|----------|------|
| GET_CAPABILITIES | 0x10 | STATUS | Get device capabilities |
| GET_ELEMENT_ATTRS | 0x20 | STATUS | Get media element attributes |
| GET_PLAY_STATUS | 0x30 | STATUS | Get playback status |
| REGISTER_NOTIFICATION | 0x31 | NOTIFY | Register event notification |
| REQUEST_CONTINUE_RSP | 0x40 | CONTROL | Request continued response |
| ABORT_CONTINUE_RSP | 0x41 | CONTROL | Abort continued response |
| SET_ABSOLUTE_VOLUME | 0x50 | CONTROL | Set absolute volume |

### 10.1 Absolute Volume Control

AVRCP supports absolute volume control. The SET_ABSOLUTE_VOLUME command can directly set the volume value of the target device. The volume value range is 0x00-0x7F (only the lower 7 bits are valid).

## 11. Capability IDs

Use the GET_CAPABILITIES command to query the capabilities supported by the target device:

| Capability ID | Value | Description |
|---------|-----|------|
| COMPANY_ID | 0x02 | Company identifier list |
| EVENTS_SUPPORTED | 0x03 | Supported events list |

## 12. Relationship with A2DP

AVRCP and A2DP are two core profiles in Bluetooth audio applications, each serving different roles:

### 12.1 Functional Division

- **A2DP (Advanced Audio Distribution Profile)**
  - Responsible for audio data transmission
  - Defines audio encoding formats (such as SBC, AAC, aptX, etc.)
  - Manages the establishment and control of audio streams
  - Ensures high-quality transmission of audio data

- **AVRCP (Audio/Video Remote Control Profile)**
  - Responsible for transmitting playback control commands
  - Implements playback control functions such as play, pause, stop, track switching
  - Provides playback status and track information queries
  - Supports volume control and event notifications

### 12.2 Collaborative Workflow

When the user presses the play key, AVRCP transmits the play command to the target device. Upon receiving the command, the target device:
1. Parses the play command
2. Starts/resumes A2DP audio stream transmission
3. Updates the playback status
4. Sends a status change notification via AVRCP

The two profiles communicate over the shared Bluetooth connection but use different L2CAP channels:
- A2DP uses the audio transport channel
- AVRCP uses the control channel (PSM: 0x0017)

## 13. Code Examples

### 13.1 AVRCP Playback Control Request

The following example shows how to send a playback control request using the PASS_THROUGH command:

```c
#include "bluetooth/avrcp.h"

/* Send play command */
int send_play_command(struct bt_avctp *session)
{
    uint8_t released = PASTHR_STATE_PRESSED;  /* Key pressed */
    uint8_t opid = AVRCP_KEY_PLAY;            /* Play operation */

    /* Send PASS_THROUGH command */
    int ret = avrcp_pasthr_cmd(session, released, opid);
    if (ret < 0) {
        /* Handle send failure */
        return ret;
    }

    /* Send key released state */
    released = PASTHR_STATE_RELEASED;
    ret = avrcp_pasthr_cmd(session, released, opid);

    return ret;
}

/* Send pause command */
int send_pause_command(struct bt_avctp *session)
{
    uint8_t released = PASTHR_STATE_PRESSED;
    uint8_t opid = AVRCP_KEY_PAUSE;

    int ret = avrcp_pasthr_cmd(session, released, opid);
    if (ret < 0) {
        return ret;
    }

    released = PASTHR_STATE_RELEASED;
    ret = avrcp_pasthr_cmd(session, released, opid);

    return ret;
}

/* Send volume adjustment command */
int send_volume_command(struct bt_avctp *session, uint8_t is_up)
{
    uint8_t released = PASTHR_STATE_PRESSED;
    uint8_t opid = is_up ? AVRCP_KEY_VOL_UP : AVRCP_KEY_VOL_DOWN;

    int ret = avrcp_pasthr_cmd(session, released, opid);
    if (ret < 0) {
        return ret;
    }

    released = PASTHR_STATE_RELEASED;
    ret = avrcp_pasthr_cmd(session, released, opid);

    return ret;
}
```

### 13.2 Get Playback Status

The following example shows how to query the current playback status:

```c
#include "bluetooth/avrcp.h"

/* Get playback status */
int request_play_status(struct bt_avctp *session)
{
    return avrcp_get_play_status_cmd(session);
}

/* Playback status callback handler */
void handle_play_status(uint32_t song_len, uint32_t song_pos, uint8_t status)
{
    const char *status_str;

    switch (status) {
        case PLAY_STATUS_STOPPED:
            status_str = "Stopped";
            break;
        case PLAY_STATUS_PLAYING:
            status_str = "Playing";
            break;
        case PLAY_STATUS_PAUSED:
            status_str = "Paused";
            break;
        case PLAY_STATUS_FWD_SEEK:
            status_str = "Fast Forward";
            break;
        case PLAY_STATUS_REV_SEEK:
            status_str = "Fast Rewind";
            break;
        default:
            status_str = "Unknown";
            break;
    }

    printf("Play Status: %s\n", status_str);
    printf("Position: %u ms / %u ms\n", song_pos, song_len);
}
```

### 13.3 Event Notification Callback Registration

The following example shows how to register AVRCP callbacks to receive event notifications:

```c
#include "bluetooth/avrcp.h"

/* Define AVRCP callback structure */
static struct avrcp_callback g_avrcp_cbs = {
    .chain = avrcp_chain_cb,              /* Connection state callback */
    .abs_vol = avrcp_abs_vol_cb,         /* Absolute volume callback */
    .play_status = avrcp_play_status_cb, /* Playback status callback */
    .tg_reg_ntf_evt = avrcp_notify_evt_cb, /* Target event notification callback */
    .rp_passthrough = avrcp_passthrough_cb, /* Pass-through command callback */
};

/* Connection state callback */
void avrcp_chain_cb(struct bt_conn *conn, uint8_t state)
{
    if (state == BT_AVRCP_CHAIN_CONNECTED) {
        printf("AVRCP Connected\n");
    } else {
        printf("AVRCP Disconnected\n");
    }
}

/* Absolute volume callback */
void avrcp_abs_vol_cb(uint8_t vol)
{
    printf("Absolute Volume: %u (max 127)\n", vol);
}

/* Playback status callback */
void avrcp_play_status_cb(uint32_t song_len, uint32_t song_pos, uint8_t status)
{
    printf("Song Length: %u ms, Position: %u ms, Status: 0x%02x\n",
           song_len, song_pos, status);
}

/* Event notification callback */
void avrcp_notify_evt_cb(uint8_t evt, uint8_t *para, uint16_t para_len)
{
    printf("Event Notification: 0x%02x\n", evt);

    switch (evt) {
        case EVENT_PLAYBACK_STATUS_CHANGED:
            if (para_len >= 1) {
                printf("Playback Status Changed: 0x%02x\n", para[0]);
            }
            break;
        case EVENT_TRACK_CHANGED:
            printf("Track Changed\n");
            break;
        case EVENT_PLAYBACK_POS_CHANGED:
            if (para_len >= 4) {
                uint32_t pos = (para[0] << 24) | (para[1] << 16) |
                              (para[2] << 8) | para[3];
                printf("Playback Position: %u ms\n", pos);
            }
            break;
        case EVENT_VOLUME_CHANGED:
            if (para_len >= 1) {
                printf("Volume Changed: %u\n", para[0] & 0x7F);
            }
            break;
        default:
            printf("Unknown Event\n");
            break;
    }
}

/* Pass-through command callback */
void avrcp_passthrough_cb(uint8_t released, uint8_t option_id)
{
    const char *state_str = released ? "Released" : "Pressed";
    const char *cmd_str;

    switch (option_id) {
        case AVRCP_KEY_PLAY:
            cmd_str = "Play";
            break;
        case AVRCP_KEY_PAUSE:
            cmd_str = "Pause";
            break;
        case AVRCP_KEY_STOP:
            cmd_str = "Stop";
            break;
        case AVRCP_KEY_VOL_UP:
            cmd_str = "Volume Up";
            break;
        case AVRCP_KEY_VOL_DOWN:
            cmd_str = "Volume Down";
            break;
        default:
            cmd_str = "Unknown";
            break;
    }

    printf("Pass-through: %s - %s\n", cmd_str, state_str);
}

/* Initialize AVRCP callbacks */
void avrcp_init_callbacks(void)
{
    avrcp_cb_register(&g_avrcp_cbs);
}
```

### 13.4 Event Notification Registration

The following example shows how to register event notifications with the target device:

```c
#include "bluetooth/avrcp.h"

/* Register playback status change notification */
int register_playback_status_notification(struct bt_avctp *session)
{
    return avrcp_reg_not_cmd(session, EVENT_PLAYBACK_STATUS_CHANGED);
}

/* Register playback position change notification */
int register_position_notification(struct bt_avctp *session)
{
    return avrcp_reg_not_cmd(session, EVENT_PLAYBACK_POS_CHANGED);
}

/* Register volume change notification */
int register_volume_notification(struct bt_avctp *session)
{
    return avrcp_reg_not_cmd(session, EVENT_VOLUME_CHANGED);
}

/* Set player parameters (for simulating target device) */
void update_player_status(uint8_t status, uint32_t position, uint32_t duration)
{
    avrcp_set_player_parameter(status, position, duration);
}
```

### 13.5 Absolute Volume Control

The following example shows how to use the absolute volume control feature:

```c
#include "bluetooth/avrcp.h"

/* Send absolute volume set command */
int set_absolute_volume(struct bt_avctp *session, uint8_t volume)
{
    /* Ensure volume value is within valid range */
    uint8_t avrcp_vol = volume & ABS_VOL_MASK;

    return avrcp_set_absvol_cmd(session, avrcp_vol);
}

/* Send volume notification (target device side) */
int notify_volume_change(struct bt_avctp *session)
{
    return avrcp_send_volume_notification(session);
}
```

## 14. Error Codes

AVRCP defines the following error codes:

| Error Code | Value | Description |
|--------|-----|------|
| INVALID_CMD | 0x00 | Invalid command |
| INVALID_PARAM | 0x01 | Invalid parameter |
| PARAM_CONTENT_ERROR | 0x02 | Parameter content error |
| INTERNAL_ERROR | 0x03 | Internal error |
| OP_COMPLETE_WITHOUT_ERROR | 0x04 | Operation completed without error |
| UID_CHANGED | 0x05 | UIDs have changed |
| INVALID_DIRECTION | 0x07 | Invalid direction |
| NOT_A_DIRECTORY | 0x08 | Not a directory |
| DOES_NOT_EXIST | 0x09 | Does not exist |
| INVALID_SCOPE | 0x0A | Invalid scope |
| RANGE_OUT_OF_BOUNDS | 0x0B | Range out of bounds |
| FOLDER_ITEM_NOT_PLAYABLE | 0x0C | Folder item is not playable |
| MEDIA_IN_USE | 0x0D | Media is currently in use |
| NOW_PLAYING_LIST_FULL | 0x0E | Now playing list is full |
| SEARCH_NOT_SUPPORTED | 0x0F | Search not supported |
| SEARCH_IN_PROGRESS | 0x10 | Search in progress |
| INVALID_PLAYER_ID | 0x11 | Invalid player ID |
| PLAYER_NOT_BROWSABLE | 0x12 | Player is not browsable |
| PLAYER_NOT_ADDRESSED | 0x13 | Player is not addressed |
| NO_VALID_SEARCH_RESULTS | 0x14 | No valid search results |
| NO_AVAILABLE_PLAYERS | 0x15 | No available players |
| ADDRESSED_PLAYER_CHANGED | 0x16 | Addressed player has changed |

## 15. Unit Types

AVRCP defines the following unit types for device information queries:

| Unit Type | Value |
|----------|-----|
| MONITOR | 0x00 |
| AUDIO | 0x01 |
| PRINTER | 0x02 |
| DISC | 0x03 |
| TAPE_RECORDER_PLAYER | 0x04 |
| TUNER | 0x05 |
| CA | 0x06 |
| CAMERA | 0x07 |
| PANEL | 0x09 |
| BULLETIN_BOARD | 0x0A |
| CAMERA_STORAGE | 0x0B |
| VENDOR_UNIQUE | 0x1C |
| SUBUNIT_TYPE_EXTENDED | 0x1E |
| UNIT | 0x1F |

## 16. Initialization Flow

### 16.1 AVRCP Initialization

```c
#include "bluetooth/avrcp.h"

/* Initialize AVRCP */
int avrcp_profile_init(void)
{
    int ret;

    /* Initialize AVCTP transport layer */
    ret = bt_avctp_init();
    if (ret < 0) {
        printf("AVCTP init failed: %d\n", ret);
        return ret;
    }

    /* Initialize AVRCP */
    ret = bt_avrcp_init();
    if (ret < 0) {
        printf("AVRCP init failed: %d\n", ret);
        return ret;
    }

    /* Register callbacks */
    avrcp_init_callbacks();

    return 0;
}
```

### 16.2 Establish AVRCP Connection

```c
#include "bluetooth/avrcp.h"

/* Establish AVRCP connection */
struct bt_avrcp *connect_avrcp(struct bt_conn *conn)
{
    struct bt_avrcp *session;

    session = bt_avrcp_connect(conn);
    if (!session) {
        printf("AVRCP connection failed\n");
        return NULL;
    }

    printf("AVRCP connection initiated\n");
    return session;
}
```

## References

- [AVRCP Header File - bluetooth/avrcp.h](./bluetooth/avrcp.h)
- [AVCTP Header File - bluetooth/avctp.h](./bluetooth/avctp.h)
- Bluetooth SIG: AVRCP Specification
- Bluetooth SIG: AVCTP Specification
