# RTSP Streaming Server - BL616/BL618

RTSP (Real Time Streaming Protocol) implementation for Bouffalo Lab BL616/BL618 using the `librtspsrv` library.

## Overview

The RTSP server provides video streaming capabilities supporting:
- **MJPEG** video streaming
- **H264** video streaming
- **Audio** support (AAC, PCMA, PCMU, OPUS)
- **RTP over UDP** transport
- **RTP over RTSP/TCP** (interleaved mode)

## API Reference

### Main Header: `librtspsrv.h`

Located at: `bouffalo_sdk/components/net/lib/rtsp/inc/librtspsrv.h`

### Core Functions

#### `int rtsp_init_lib(void)`
Initialize and start the RTSP server. Must be called after setting all callbacks and configurations.

**Returns:** 0 on success, -1 on error

```c
// Example initialization sequence
void strm_rtsp_start(void)
{
    bl_cam_frame_init();
    rtsp_set_video_en(1);
    rtsp_set_audio_en(0);
    set_strm_cb(get_frm_cb);
    rtsp_set_videoFmt(RTSP_VIDEOFMT_MJPEG);
    rtsp_set_strm_report_cb(rtsp_client_event_handler);
    rtsp_set_video_fps(25);
    rtsp_init_lib();
}
```

#### `int rtsp_deinit_lib(void)`
Stop and deinitialize the RTSP server.

#### `void set_strm_cb(get_frm_t get)`
Set the frame callback function for streaming.

```c
typedef int (*get_frm_t)(struct strm_info *strm_info, struct frm_info *frm_info);

int get_frm_cb(struct strm_info *strm_info, struct frm_info *frm_info)
{
    if (rtsp_get_video_en()) {
        int ret = frame_queue_output_pop(g_mjpeg_out_frame_ctrl, 
            (frame_elem_t *)&jpeg_frame_info, jpeg_out_queue_rtc_id, 1000);
        
        if (ret < 0) {
            return -1;
        }
        
        memcpy(frm_info->frm_buf, (uint8_t *)jpeg_frame_info.elem_base.frame_addr, 
               jpeg_frame_info.data_size);
        frm_info->frm_sz = jpeg_frame_info.data_size;
        frm_info->frm_type = FRM_TYPE_M;  // M-JPEG frame
        frm_info->timestamp = xTaskGetTickCount();  // 100ns units
        
        frame_queue_output_free(g_mjpeg_out_frame_ctrl, (frame_elem_t *)&jpeg_frame_info);
        return 1;
    }
    return -1;
}
```

### Configuration Functions

| Function | Description |
|----------|-------------|
| `rtsp_set_video_en(int en)` | Enable/disable video streaming |
| `rtsp_set_audio_en(int en)` | Enable/disable audio streaming |
| `rtsp_set_videoFmt(int vdofmt)` | Set video format (`RTSP_VIDEOFMT_MJPEG` or `RTSP_VIDEOFMT_H264`) |
| `rtsp_set_audioFmt(int audfmt)` | Set audio format (`RTSP_AUDIOFMT_AAC`, `RTSP_AUDIOFMT_PCMA`, etc.) |
| `rtsp_set_video_fps(int fps)` | Set video frame rate (default: 25) |
| `rtsp_set_strm_report_cb(rtsp_report_fn_t fn)` | Set client event callback |

### Query Functions

| Function | Returns |
|----------|---------|
| `rtsp_get_video_en()` | Video enabled status |
| `rtsp_get_audio_en()` | Audio enabled status |
| `rtsp_get_videoFmt()` | Current video format |
| `rtsp_get_audioFmt()` | Current audio format |
| `rtsp_get_video_fps()` | Current frame rate |

## RTSP Methods

The server implements the following RTSP methods:

### OPTIONS
Returns the list of supported RTSP methods.

**Request:**
```
OPTIONS rtsp://server/stream RTSP/1.0
CSeq: 1
```

**Response:**
```
RTSP/1.0 200 OK
CSeq: 1
Public: OPTIONS, DESCRIBE, SETUP, TEARDOWN, PLAY, PAUSE, GET_PARAMETER, SET_PARAMETER
```

### DESCRIBE
Retrieves the SDP (Session Description Protocol) information for the stream.

**Request:**
```
DESCRIBE rtsp://server/stream RTSP/1.0
CSeq: 2
Accept: application/sdp
```

**Response (MJPEG):**
```
RTSP/1.0 200 OK
CSeq: 2
Content-Type: application/sdp
Content-Length: 215

v=0
o=- 1234567890 1 IN IP4 192.168.1.100
s=streamed by the BL MM RTSP server
t=0 0
a=control:*
a=type:broadcast
m=video 0 RTP/AVP 26
c=IN IP4 0.0.0.0
a=rtpmap:26 JPEG/90000
a=framerate:25
a=control:track0
```

### SETUP
Establishes the RTP session for video/audio transport.

**Request (UDP):**
```
SETUP rtsp://server/stream/track0 RTSP/1.0
CSeq: 3
Transport: RTP/AVP/UDP;unicast;client_port=5000-5001
```

**Response:**
```
RTSP/1.0 200 OK
CSeq: 3
Transport: RTP/AVP/UDP;unicast;client_port=5000-5001;server_port=5002-5003
Session: 12345678
```

### PLAY
Starts streaming media.

**Request:**
```
PLAY rtsp://server/stream RTSP/1.0
CSeq: 4
Session: 12345678
Range: npt=0.000-
```

**Response:**
```
RTSP/1.0 200 OK
CSeq: 4
Range: npt=0.000-
Session: 12345678
```

### TEARDOWN
Stops the stream and terminates the session.

**Request:**
```
TEARDOWN rtsp://server/stream RTSP/1.0
CSeq: 5
Session: 12345678
```

**Response:**
```
RTSP/1.0 200 OK
CSeq: 5
```

## RTP over UDP

The server uses UDP sockets for RTP/RTCP transport:

### Port Configuration
- **RTP Video**: Default ports 5002 (server), client ports from SETUP request
- **RTCP Video**: Default ports 5003 (server), client ports from SETUP request  
- **RTP Audio**: Additional ports if audio enabled

### RTP Header Structure

```c
struct rtp_hdr {
    unsigned char cc:4;    /* CSRC count */
    unsigned char x:1;     /* Header extension flag */
    unsigned char p:1;    /* Padding flag */
    unsigned char v:2;     /* Protocol version */
    unsigned char pt:7;   /* Payload type */
    unsigned char m:1;    /* Marker bit */
    unsigned short seq;   /* Sequence number */
    unsigned int ts;      /* Timestamp */
    unsigned int ssrc;    /* Synchronization source */
};
```

### Payload Types

| Type | Value | Description |
|------|-------|-------------|
| `RTP_PT_JPEG` | 26 | JPEG video |
| `RTP_PT_H264` | 96 | H264 video |
| `RTP_PT_PCMU` | 0 | G.711 mu-law audio |
| `RTP_PT_PCMA` | 8 | G.711 A-law audio |
| `RTP_PT_AAC` | 97 | AAC audio |
| `RTP_PT_OPUS` | 101 | Opus audio |

### UDP Socket Setup

The server creates separate UDP sockets for each media stream:

```c
// From rtsp_sess.c - create_rtp_sess()
struct rtp_rtcp {
    struct rtp_hdr rtp_hdr;
    union {
        struct tcp {        /* Interleaved mode */
            char rtp_chn;
            char rtcp_chn;
        } tcp;
        struct udp {
            int rtp_sd;              /* Server RTP socket descriptor */
            int rtcp_sd;             /* Server RTCP socket descriptor */
            struct sockaddr rtp_sa;   /* Client RTP socket address */
            struct sockaddr rtcp_sa;  /* Client RTCP socket address */
        } udp;
    };
};
```

## Streaming Session Management

### Session States

```
INIT -> READY -> PLAYING
  |        |        |
  +--------+--------+--------> TEARDOWN
```

| State | Description |
|-------|-------------|
| `RTSP_STATE_INIT` | Initial state, no session established |
| `RTSP_STATE_READY` | SETUP completed, ready to play |
| `RTSP_STATE_PLAYING` | PLAY command received, streaming active |

### Session Structure

```c
struct rtsp_sess {
    struct list_head entry;
    unsigned long long sess_id;      /* Unique session ID */
    unsigned int cseq;               /* RTSP sequence number */
    enum rtsp_state rtsp_state;      /* Current state */
    enum handling_state handling_state;
    int rtsp_sd;                     /* RTSP TCP socket */
    int intlvd_mode;                 /* 0=UDP, 1=TCP interleaved */
    struct list_head send_queue;      /* Pending send buffers */
    char *recv_buf;                  /* Receive buffer */
    struct rtsp_req *req;            /* Current request */
    struct rtsp_resp *resp;          /* Current response */
    struct strm strm;                /* Stream resource */
    struct rtp_rtcp rtp_rtcp[2];     /* Video[0] & Audio[1] */
};
```

### Session Lifecycle

1. **Creation**: `create_rtsp_sess()` - Called when client connects
2. **SETUP Phase**: `create_rtp_sess()` - Allocates RTP/RTCP ports
3. **PLAY Phase**: `prefetch_frm()` - Starts frame delivery via delay task
4. **TEARDOWN Phase**: `destroy_rtsp_sess()` - Schedules cleanup (10ms delay)

### Send Buffer Queue

Each session has a send queue for outgoing data:

```c
struct send_buf {
    struct list_head entry;
    enum data_type type;      /* DATA_TYPE_RTSP_RESP, RTP_V_PKT, etc. */
    unsigned int sz;
    char *buf;
};
```

### Event Handler Callback

```c
static void rtsp_client_event_handler(int action)
{
    switch (action) {
        case RTSP_STRM_REPORT_CLIENT_EXIT:
            printf("RTSP disconnect\r\n");
            break;
        default:
            break;
    }
}
```

## Frame Types

```c
enum frm_type {
    FRM_TYPE_I = 1,   /* I-frame (keyframe) */
    FRM_TYPE_B,       /* B-frame */
    FRM_TYPE_P,       /* P-frame */
    FRM_TYPE_A,       /* Audio frame */
    FRM_TYPE_M,       /* MJPEG frame */
};
```

## Complete Working Example

```c
#include <FreeRTOS.h>
#include <task.h>
#include <stdio.h>
#include <string.h>
#include "librtspsrv.h"
#include "frame_queue_ctrl.h"
#include "frame_queue.h"

static jpeg_frame_t jpeg_frame_info;
static uint16_t jpeg_out_queue_rtc_id = FRAME_QUEUE_DEFAULT_ID;

void bl_cam_frame_init(void)
{
    if (jpeg_out_queue_rtc_id != MJPEG_OUT_FRAME_STREAM_WIFI_RTC_ID) {
        jpeg_out_queue_rtc_id = MJPEG_OUT_FRAME_STREAM_WIFI_RTC_ID;
        frame_queue_output_create(g_mjpeg_out_frame_ctrl, 
            &jpeg_out_queue_rtc_id, 
            MJPEG_OUT_FRAME_STREAM_WIFI_RTC_DEPTH);
    }
}

static void rtsp_client_event_handler(int action)
{
    if (action == RTSP_STRM_REPORT_CLIENT_EXIT) {
        printf("RTSP client disconnected\r\n");
    }
}

static int get_frm_cb(struct strm_info *strm_info, struct frm_info *frm_info)
{
    int ret = frame_queue_output_pop(g_mjpeg_out_frame_ctrl,
        (frame_elem_t *)&jpeg_frame_info,
        jpeg_out_queue_rtc_id, 1000);

    if (ret < 0) {
        return -1;
    }

    memcpy(frm_info->frm_buf,
           (uint8_t *)jpeg_frame_info.elem_base.frame_addr,
           jpeg_frame_info.data_size);
    frm_info->frm_sz = jpeg_frame_info.data_size;
    frm_info->frm_type = FRM_TYPE_M;
    frm_info->timestamp = xTaskGetTickCount();

    frame_queue_output_free(g_mjpeg_out_frame_ctrl,
                           (frame_elem_t *)&jpeg_frame_info);
    return 1;
}

void strm_rtsp_start(void)
{
    bl_cam_frame_init();
    rtsp_set_video_en(1);
    rtsp_set_audio_en(0);
    set_strm_cb(get_frm_cb);
    rtsp_set_videoFmt(RTSP_VIDEOFMT_MJPEG);
    rtsp_set_strm_report_cb(rtsp_client_event_handler);
    rtsp_set_video_fps(25);
    rtsp_init_lib();
}
```

## Architecture Overview

```
+-------------------+
|   Application     |
| strm_rtsp_start() |
+--------+----------+
         |
         v
+--------+----------+
|  librtspsrv.c    |  <-- Public API
|  - rtsp_init_lib |
|  - set_strm_cb   |
+--------+----------+
         |
         v
+--------+----------+
|   rtsp_srv.c     |  <-- Server main loop
|   FreeRTOS Task   |      (poll-based)
+--------+----------+
         |
         +---> rtsp_sess.c  (Session management)
         +---> rtsp_method.c (DESCRIBE/OPTIONS/SETUP/PLAY/TEARDOWN)
         +---> rtp.c (RTP packetization)
         +---> sd_handler.c (Socket event handling)
         +---> delay_task.c (Delayed task scheduling)
```

## Default Configuration

| Parameter | Value |
|-----------|-------|
| RTSP Port | 8554 |
| Max Frame Size | 100 KB |
| Max Channels | 3 |
| Video FPS | 25 |
| Max Poll FDs | 32 |
| RTSP Task Stack | 4096 bytes |
| RTSP Task Priority | 0 (lowest) |

## Client Connection Example (VLC)

```
rtsp://<device_ip>:8554/stream
```

## Notes

- The RTSP server runs as a FreeRTOS task with configurable stack size
- Uses `poll()` for I/O multiplexing (not epoll, for broader compatibility)
- Supports both UDP and TCP (interleaved) transport
- Session IDs are 64-bit integers
- Frame timestamps are in 100ns units (from `xTaskGetTickCount()`)
