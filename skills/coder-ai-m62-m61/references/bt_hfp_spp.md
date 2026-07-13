# Bluetooth Classic HFP and SPP Profiles - BL616/BL618

This document describes the Hands-Free Profile (HFP) and Serial Port Profile (SPP) implementations for Bouffalo BL616/BL618 chips using the Bouffalo SDK.

## Table of Contents
- [HFP Hands-Free Role](#hfp-hands-free-role)
  - [Overview](#overview)
  - [AT Commands](#at-commands)
  - [Call Control (Answer/Reject/Hangup)](#call-control-answerrejecthangup)
  - [Audio Path](#audio-path)
  - [Callback API](#callback-api)
  - [Working Code Examples](#working-code-examples)
- [SPP Serial Port Profile](#spp-serial-port-profile)
  - [Overview](#overview-1)
  - [API Reference](#api-reference)
  - [Working Code Examples](#working-code-examples-1)
- [SDP Service Discovery](#sdp-service-discovery)
  - [Overview](#overview-2)
  - [Key Definitions](#key-definitions)
  - [SDP Server/Client API](#sdp-serverclient-api)
- [RFCOMM](#rfcomm)
  - [Overview](#overview-3)
  - [RFCOMM Channels](#rfcomm-channels)
  - [DLC Operations](#dlc-operations)
  - [Server Registration](#server-registration)

---

## HFP Hands-Free Role

### Overview

The Hands-Free Profile (HFP) implements the Hands-Free unit role, communicating with an Audio Gateway (AG) such as a smartphone. The HF role operates over RFCOMM and uses AT commands for control.

**Key Header File:** `btprofile/include/bluetooth/hfp_hf.h`

### AT Commands

The following AT commands are supported via `enum bt_hfp_hf_at_cmd`:

| AT Command | Description |
|------------|-------------|
| `BT_HFP_HF_ATA` | Answer incoming call |
| `BT_HFP_HF_AT_CHUP` | Reject/Terminate call |
| `BT_HFP_HF_AT_VGM` | Set microphone volume |
| `BT_HFP_HF_AT_VGS` | Set speaker volume |
| `BT_HFP_HF_AT_DDD` | Dial phone number |
| `BT_HFP_HF_AT_NREC` | Disable echo cancellation |
| `BT_HFP_HF_AT_BVRA` | Voice recognition activation |
| `BT_HFP_HF_AT_BINP` | Voice recognition button press |
| `BT_HFP_ACCEPT_INCOMING_CALLER_ID` | Accept incoming caller ID |
| `BT_HFP_SET_MIC_VOL` | Set microphone volume |
| `BT_HFP_QUERY_LIST_CALLS` | Query current calls list |
| `BT_HFP_RESPONSE_CALLS` | Respond to call (accept/reject) |
| `BT_HFP_SUBSCRIBE_NUM_INFO` | Subscribe to caller number info |
| `BT_HFP_SEND_INDICATOR` | Send indicator update |
| `BT_HFP_UPDATE_INDICATOR` | Update indicator state |

**Command Completion Status:**
```c
#define HFP_HF_CMD_OK             0
#define HFP_HF_CMD_ERROR          1
#define HFP_HF_CMD_CME_ERROR      2
#define HFP_HF_CMD_UNKNOWN_ERROR  4
```

### Call Control (Answer/Reject/Hangup)

**Answer Incoming Call:**
```c
int bt_hfp_hf_send_cmd(struct bt_conn *conn, BT_HFP_HF_ATA, NULL);
```

**Reject/Hangup Call:**
```c
int bt_hfp_hf_send_cmd(struct bt_conn *conn, BT_HFP_HF_AT_CHUP, NULL);
```

**Dial Number:**
```c
// Dial specific number
bt_hfp_hf_send_cmd(conn, BT_HFP_HF_AT_DDD, "ATD1234567;");

// Last number redial
bt_hfp_hf_send_cmd(conn, BT_HFP_HF_AT_DDD, "AT+BLDN");
```

**Volume Control:**
```c
// Speaker volume (0-15)
bt_hfp_hf_send_cmd_arg(conn, BT_HFP_HF_AT_VGS, volume);

// Microphone volume (0-15)
bt_hfp_hf_send_cmd_arg(conn, BT_HFP_HF_AT_VGM, volume);
```

### Audio Path

Audio is carried over SCO (Synchronous Connection-Oriented) link, separate from RFCOMM control channel. The SCO connection is established after service level connection (SLC) is formed.

**Audio Connection Callback Structure:**
```c
struct bt_hfp_hf_cb {
    void (*connected)(struct bt_conn *conn);
    void (*disconnected)(struct bt_conn *conn);
    void (*service)(struct bt_conn *conn, uint32_t value);      // Service indicator
    void (*call)(struct bt_conn *conn, uint32_t value);           // Call indicator
    void (*call_setup)(struct bt_conn *conn, uint32_t value);     // Call setup indicator
    void (*call_held)(struct bt_conn *conn, uint32_t value);      // Call held indicator
    void (*signal)(struct bt_conn *conn, uint32_t value);         // Signal strength
    void (*roam)(struct bt_conn *conn, uint32_t value);          // Roaming indicator
    void (*battery)(struct bt_conn *conn, uint32_t value);       // Battery indicator
    void (*vgs_indication)(struct bt_conn *conn, uint32_t value); // Speaker volume
    void (*vgm_indication)(struct bt_conn *conn, uint32_t value); // Mic volume
    void (*ring_indication)(struct bt_conn *conn);                // Incoming call ring
    void (*cmd_complete_cb)(struct bt_conn *conn, struct bt_hfp_hf_cmd_complete *cmd);
};
```

### Callback API

**Register HFP callbacks:**
```c
int bt_hfp_hf_register(struct bt_hfp_hf_cb *cb);
```

**Initialize HFP module:**
```c
int bt_hfp_hf_init(void);
```

**Connect to Audio Gateway:**
```c
int bt_hfp_hf_initiate_connect(struct bt_conn *conn);
```

**Send AT command:**
```c
int bt_hfp_hf_send_cmd(struct bt_conn *conn, enum bt_hfp_hf_at_cmd cmd, const char *format);
int bt_hfp_hf_send_cmd_arg(struct bt_conn *conn, enum bt_hfp_hf_at_cmd cmd, int arg1);
```

**Disconnect:**
```c
int bt_hfp_hf_send_disconnect(struct bt_conn *conn);
```

### Working Code Examples

**HFP Initialization and Callbacks:**
```c
#include <bluetooth/hfp_hf.h>

static struct bt_conn *default_conn;

// Connection callback
static void bredr_connected(struct bt_conn *conn, uint8_t err)
{
    char addr[BT_ADDR_STR_LEN];
    bt_addr_to_str(&conn->br.dst, addr, sizeof(addr));
    
    if (err) {
        printf("BR/EDR connect failed: %s (err %u)\r\n", addr, err);
        return;
    }
    
    printf("BR/EDR connected: %s\r\n", addr);
    default_conn = bt_conn_ref(conn);
}

// Disconnection callback
static void bredr_disconnected(struct bt_conn *conn, uint8_t reason)
{
    printf("BR/EDR disconnected (reason %u)\r\n", reason);
    if (default_conn == conn) {
        default_conn = NULL;
    }
}

// HFP callbacks
static void hf_connected(struct bt_conn *conn)
{
    printf("HFP HF connected\r\n");
}

static void hf_disconnected(struct bt_conn *conn)
{
    printf("HFP HF disconnected\r\n");
}

static void hf_ring_indication(struct bt_conn *conn)
{
    printf("Incoming call - RING!\r\n");
}

static void hf_call_setup(struct bt_conn *conn, uint32_t value)
{
    printf("Call setup indicator: %u\r\n", value);
}

static void hf_vgs_indication(struct bt_conn *conn, uint32_t value)
{
    printf("Speaker volume: %u\r\n", value);
}

static struct bt_hfp_hf_cb hfp_hf_callbacks = {
    .connected = hf_connected,
    .disconnected = hf_disconnected,
    .ring_indication = hf_ring_indication,
    .call_setup = hf_call_setup,
    .vgs_indication = hf_vgs_indication,
};

void hfp_example_init(void)
{
    // Register connection callbacks
    bt_conn_cb_register(&(struct bt_conn_cb){
        .connected = bredr_connected,
        .disconnected = bredr_disconnected,
    });
    
    // Register HFP callbacks
    bt_hfp_hf_register(&hfp_hf_callbacks);
    
    // Initialize HFP
    bt_hfp_hf_init();
}

void hfp_answer_call(void)
{
    if (!default_conn) {
        printf("Not connected\r\n");
        return;
    }
    
    int err = bt_hfp_hf_send_cmd(default_conn, BT_HFP_HF_ATA, NULL);
    if (err) {
        printf("Failed to answer call: %d\r\n", err);
    } else {
        printf("Answering call...\r\n");
    }
}

void hfp_hangup_call(void)
{
    if (!default_conn) {
        printf("Not connected\r\n");
        return;
    }
    
    int err = bt_hfp_hf_send_cmd(default_conn, BT_HFP_HF_AT_CHUP, NULL);
    if (err) {
        printf("Failed to hangup: %d\r\n", err);
    } else {
        printf("Hanging up...\r\n");
    }
}

void hfp_dial_number(const char *number)
{
    if (!default_conn) {
        printf("Not connected\r\n");
        return;
    }
    
    char cmd[32];
    snprintf(cmd, sizeof(cmd), "ATD%s;", number);
    
    int err = bt_hfp_hf_send_cmd(default_conn, BT_HFP_HF_AT_DDD, cmd);
    if (err) {
        printf("Failed to dial: %d\r\n", err);
    } else {
        printf("Dialing %s...\r\n", number);
    }
}

void hfp_set_speaker_volume(uint8_t volume)
{
    if (!default_conn) {
        printf("Not connected\r\n");
        return;
    }
    
    volume = (volume > 15) ? 15 : volume;  // Clamp to 0-15
    
    int err = bt_hfp_hf_send_cmd_arg(default_conn, BT_HFP_HF_AT_VGS, volume);
    if (err) {
        printf("Failed to set volume: %d\r\n", err);
    }
}

void hfp_set_mic_volume(uint8_t volume)
{
    if (!default_conn) {
        printf("Not connected\r\n");
        return;
    }
    
    volume = (volume > 15) ? 15 : volume;  // Clamp to 0-15
    
    int err = bt_hfp_hf_send_cmd_arg(default_conn, BT_HFP_HF_AT_VGM, volume);
    if (err) {
        printf("Failed to set mic volume: %d\r\n", err);
    }
}
```

---

## SPP Serial Port Profile

### Overview

The Serial Port Profile (SPP) provides emulated serial port functionality over Bluetooth BR/EDR. It is the basis for many classic Bluetooth serial communication use cases.

**Key Header File:** `btprofile/include/bluetooth/spp.h`

### API Reference

**Callback Structure:**
```c
struct spp_callback_t {
    void (*connected)(void);                      // SPP connected callback
    void (*disconnected)(void);                   // SPP disconnected callback
    void (*bt_spp_recv)(uint8_t *data, uint16_t length);  // Data receive callback
};
```

**Initialize SPP:**
```c
int bt_spp_init(void);
```

**Connect to remote SPP server:**
```c
int bt_spp_connect(struct bt_conn *conn);
```

**Disconnect SPP:**
```c
int bt_spp_disconnect(struct bt_conn *conn);
```

**Send data:**
```c
int bt_spp_send(uint8_t *buf_data, uint16_t length);
```

**Register SPP callbacks:**
```c
void spp_cb_register(struct spp_callback_t *cb);
```

### Working Code Examples

**SPP Initialization and Callbacks:**
```c
#include <bluetooth/spp.h>

static uint8_t spp_test_buffer[256];

// SPP connected callback
static void spp_connected(void)
{
    printf("SPP connected\r\n");
}

// SPP disconnected callback
static void spp_disconnected(void)
{
    printf("SPP disconnected\r\n");
}

// SPP data received callback
static void spp_recv_callback(uint8_t *data, uint16_t length)
{
    printf("SPP received %u bytes: %s\r\n", length, bt_hex(data, length));
    
    // Echo back the data
    bt_spp_send(data, length);
}

// SPP callback structure
static struct spp_callback_t spp_callbacks = {
    .connected = spp_connected,
    .disconnected = spp_disconnected,
    .bt_spp_recv = spp_recv_callback,
};

void spp_example_init(void)
{
    // Register SPP callbacks
    spp_cb_register(&spp_callbacks);
    
    // Initialize SPP
    bt_spp_init();
}

void spp_connect_to_remote(struct bt_conn *conn)
{
    int err = bt_spp_connect(conn);
    if (err) {
        printf("SPP connect failed: %d\r\n", err);
    } else {
        printf("SPP connecting...\r\n");
    }
}

void spp_disconnect_from_remote(void)
{
    int err = bt_spp_disconnect(default_conn);
    if (err) {
        printf("SPP disconnect failed: %d\r\n", err);
    }
}

void spp_send_data(uint8_t *data, uint16_t len)
{
    if (len > sizeof(spp_test_buffer)) {
        len = sizeof(spp_test_buffer);
    }
    
    int err = bt_spp_send(data, len);
    if (err) {
        printf("SPP send failed: %d\r\n", err);
    } else {
        printf("SPP sent %u bytes\r\n", len);
    }
}

void spp_send_test_pattern(uint16_t len)
{
    if (len > sizeof(spp_test_buffer)) {
        len = sizeof(spp_test_buffer);
    }
    
    // Fill buffer with test pattern
    for (uint16_t i = 0; i < len; i++) {
        spp_test_buffer[i] = (i + 1) & 0xFF;
    }
    
    int err = bt_spp_send(spp_test_buffer, len);
    if (err) {
        printf("SPP send failed: %d\r\n", err);
    } else {
        printf("SPP sent test pattern: %u bytes\r\n", len);
    }
}
```

---

## SDP Service Discovery

### Overview

The Service Discovery Protocol (SDP) allows devices to discover services offered by other Bluetooth devices and their associated attributes.

**Key Header File:** `btprofile/include/bluetooth/sdp.h`

### Key Definitions

**Service Class IDs:**
```c
#define BT_SDP_SERIAL_PORT_SVCLASS       0x1101  // SPP
#define BT_SDP_HEADSET_SVCLASS          0x1108
#define BT_SDP_HANDSFREE_SVCLASS        0x111e  // HFP
#define BT_SDP_HANDSFREE_AGW_SVCLASS    0x111f  // HFP AG
```

**Attribute IDs:**
```c
#define BT_SDP_ATTR_RECORD_HANDLE        0x0000
#define BT_SDP_ATTR_SVCLASS_ID_LIST      0x0001
#define BT_SDP_ATTR_PROTO_DESC_LIST      0x0004
#define BT_SDP_ATTR_PROFILE_DESC_LIST    0x0009
#define BT_SDP_ATTR_SUPPORTED_FEATURES   0x0311
#define BT_SDP_ATTR_SVCNAME_PRIMARY      0x0100
```

**Data Element Types:**
```c
#define BT_SDP_UINT8            0x08
#define BT_SDP_UINT16           0x09
#define BT_SDP_UINT32           0x0a
#define BT_SDP_UUID16           0x19
#define BT_SDP_TEXT_STR8        0x25
#define BT_SDP_SEQ8             0x35
#define BT_SDP_SEQ16            0x36
```

### SDP Server/Client API

**Register SDP Service Record:**
```c
int bt_sdp_register_service(struct bt_sdp_record *service);
```

**SDP Record Structure:**
```c
struct bt_sdp_record {
    uint32_t                    handle;       // Service record handle
    struct bt_sdp_attribute    *attrs;       // Attribute array
    size_t                      attr_count;  // Number of attributes
    uint8_t                     index;
    struct bt_sdp_record       *next;
};
```

**SDP Attribute Structure:**
```c
struct bt_sdp_attribute {
    uint16_t                id;   // Attribute ID
    struct bt_sdp_data_elem val;  // Attribute data
};
```

**SDP Data Element:**
```c
struct bt_sdp_data_elem {
    uint8_t        type;       // Data type
    uint32_t       data_size;  // Size of data
    uint32_t       total_size; // Total size including header
    const void    *data;       // Pointer to data
};
```

**Helper Macros:**
```c
// Declare a new service record
#define BT_SDP_NEW_SERVICE

// Service name attribute
#define BT_SDP_SERVICE_NAME(_name)

// Supported features
#define BT_SDP_SUPPORTED_FEATURES(_features)

// List attribute
#define BT_SDP_LIST(_att_id, _type_size, _data_elem_seq)

// Service ID
#define BT_SDP_SERVICE_ID(_uuid)
```

### Working Code Examples

**SPP SDP Service Record Declaration:**
```c
#include <bluetooth/sdp.h>

// SPP Service Record with attributes
static struct bt_sdp_attribute spp_attrs[] = {
    BT_SDP_NEW_SERVICE,  // Record handle, record state, language base, browse group
    
    // Service class ID list - Serial Port
    {
        BT_SDP_ATTR_SVCLASS_ID_LIST,
        {
            BT_SDP_TYPE_SIZE_VAR(BT_SDP_SEQ8, 3),
            BT_SDP_DATA_ELEM_LIST(
                {
                    BT_SDP_TYPE_SIZE(BT_SDP_UUID16),
                    BT_SDP_ARRAY_16(BT_SDP_SERIAL_PORT_SVCLASS)
                }
            )
        }
    },
    
    // Protocol descriptor list (L2CAP + RFCOMM)
    {
        BT_SDP_ATTR_PROTO_DESC_LIST,
        {
            BT_SDP_TYPE_SIZE_VAR(BT_SDP_SEQ8, 13),
            BT_SDP_DATA_ELEM_LIST(
                {
                    BT_SDP_TYPE_SIZE_VAR(BT_SDP_SEQ8, 3),
                    BT_SDP_DATA_ELEM_LIST(
                        {
                            BT_SDP_TYPE_SIZE(BT_SDP_UUID16),
                            BT_SDP_ARRAY_16(0x0100)  // L2CAP UUID
                        }
                    )
                },
                {
                    BT_SDP_TYPE_SIZE_VAR(BT_SDP_SEQ8, 3),
                    BT_SDP_DATA_ELEM_LIST(
                        {
                            BT_SDP_TYPE_SIZE(BT_SDP_UUID16),
                            BT_SDP_ARRAY_16(0x0003)  // RFCOMM UUID
                        },
                        {
                            BT_SDP_TYPE_SIZE(BT_SDP_UINT8),
                            BT_SDP_ARRAY_8(0x01)     // RFCOMM channel 1
                        }
                    )
                }
            )
        }
    },
    
    // Profile descriptor list
    {
        BT_SDP_ATTR_PROFILE_DESC_LIST,
        {
            BT_SDP_TYPE_SIZE_VAR(BT_SDP_SEQ8, 6),
            BT_SDP_DATA_ELEM_LIST(
                {
                    BT_SDP_TYPE_SIZE_VAR(BT_SDP_SEQ8, 3),
                    BT_SDP_DATA_ELEM_LIST(
                        {
                            BT_SDP_TYPE_SIZE(BT_SDP_UUID16),
                            BT_SDP_ARRAY_16(BT_SDP_SERIAL_PORT_SVCLASS)
                        },
                        {
                            BT_SDP_TYPE_SIZE(BT_SDP_UINT16),
                            BT_SDP_ARRAY_16(0x0102)  // SPP version 1.02
                        }
                    )
                }
            )
        }
    },
    
    // Service name
    BT_SDP_SERVICE_NAME("Serial Port"),
    
    // Supported features (SPP has none required)
    BT_SDP_SUPPORTED_FEATURES(0x0000),
};

static struct bt_sdp_record spp_service_record = BT_SDP_RECORD(spp_attrs);

void sdp_register_spp_service(void)
{
    int err = bt_sdp_register_service(&spp_service_record);
    if (err) {
        printf("SDP SPP service registration failed: %d\r\n", err);
    } else {
        printf("SDP SPP service registered successfully\r\n");
    }
}
```

**HFP Hands-Free SDP Service Record:**
```c
#include <bluetooth/sdp.h>

static struct bt_sdp_attribute hfp_hf_attrs[] = {
    BT_SDP_NEW_SERVICE,
    
    // Service class ID list - Hands-Free
    {
        BT_SDP_ATTR_SVCLASS_ID_LIST,
        {
            BT_SDP_TYPE_SIZE_VAR(BT_SDP_SEQ8, 3),
            BT_SDP_DATA_ELEM_LIST(
                {
                    BT_SDP_TYPE_SIZE(BT_SDP_UUID16),
                    BT_SDP_ARRAY_16(BT_SDP_HANDSFREE_SVCLASS)
                }
            )
        }
    },
    
    // Protocol descriptor list (L2CAP + RFCOMM)
    {
        BT_SDP_ATTR_PROTO_DESC_LIST,
        {
            BT_SDP_TYPE_SIZE_VAR(BT_SDP_SEQ8, 13),
            BT_SDP_DATA_ELEM_LIST(
                {
                    BT_SDP_TYPE_SIZE_VAR(BT_SDP_SEQ8, 3),
                    BT_SDP_DATA_ELEM_LIST(
                        {
                            BT_SDP_TYPE_SIZE(BT_SDP_UUID16),
                            BT_SDP_ARRAY_16(0x0100)  // L2CAP UUID
                        }
                    )
                },
                {
                    BT_SDP_TYPE_SIZE_VAR(BT_SDP_SEQ8, 3),
                    BT_SDP_DATA_ELEM_LIST(
                        {
                            BT_SDP_TYPE_SIZE(BT_SDP_UUID16),
                            BT_SDP_ARRAY_16(0x0003)  // RFCOMM UUID
                        },
                        {
                            BT_SDP_TYPE_SIZE(BT_SDP_UINT8),
                            BT_SDP_ARRAY_8(0x02)     // RFCOMM channel 2
                        }
                    )
                }
            )
        }
    },
    
    // Profile descriptor list - Hands-Free
    {
        BT_SDP_ATTR_PROFILE_DESC_LIST,
        {
            BT_SDP_TYPE_SIZE_VAR(BT_SDP_SEQ8, 6),
            BT_SDP_DATA_ELEM_LIST(
                {
                    BT_SDP_TYPE_SIZE_VAR(BT_SDP_SEQ8, 3),
                    BT_SDP_DATA_ELEM_LIST(
                        {
                            BT_SDP_TYPE_SIZE(BT_SDP_UUID16),
                            BT_SDP_ARRAY_16(BT_SDP_HANDSFREE_SVCLASS)
                        },
                        {
                            BT_SDP_TYPE_SIZE(BT_SDP_UINT16),
                            BT_SDP_ARRAY_16(0x0107)  // HFP version 1.07
                        }
                    )
                }
            )
        }
    },
    
    // Supported features (HF features)
    {
        BT_SDP_ATTR_SUPPORTED_FEATURES,
        {
            BT_SDP_TYPE_SIZE(BT_SDP_UINT16),
            BT_SDP_ARRAY_16(0x002F)  // Feature mask: WBS, ESCO, etc.
        }
    },
    
    BT_SDP_SERVICE_NAME("Hands-Free"),
};

static struct bt_sdp_record hfp_hf_service_record = BT_SDP_RECORD(hfp_hf_attrs);

void sdp_register_hfp_service(void)
{
    int err = bt_sdp_register_service(&hfp_hf_service_record);
    if (err) {
        printf("SDP HFP service registration failed: %d\r\n", err);
    } else {
        printf("SDP HFP service registered successfully\r\n");
    }
}
```

---

## RFCOMM

### Overview

RFCOMM (Radio Frequency Communication) is a simple transport protocol providing emulated serial ports over L2CAP. It is used by both HFP and SPP profiles.

**Key Header File:** `btprofile/include/bluetooth/rfcomm.h`

### RFCOMM Channels

```c
enum {
    BT_RFCOMM_CHAN_HFP_HF = 1,   // HFP Hands-Free unit
    BT_RFCOMM_CHAN_HFP_AG,       // HFP Audio Gateway
    BT_RFCOMM_CHAN_HSP_AG,       // Headset Profile AG
    BT_RFCOMM_CHAN_HSP_HS,       // Headset Profile HS
    BT_RFCOMM_CHAN_SPP,          // Serial Port Profile
};
```

### DLC Operations

**DLC Callbacks:**
```c
struct bt_rfcomm_dlc_ops {
    void (*connected)(struct bt_rfcomm_dlc *dlc);
    void (*disconnected)(struct bt_rfcomm_dlc *dlc, struct bt_conn *conn);
    void (*recv)(struct bt_rfcomm_dlc *dlc, struct net_buf *buf);
};
```

**DLC Structure:**
```c
struct bt_rfcomm_dlc {
    struct k_delayed_work      rtx_work;       // Response timeout
    struct k_fifo              tx_queue;       // TX queue
    struct k_sem               tx_credits;     // TX credits
    struct bt_rfcomm_session  *session;
    struct bt_rfcomm_dlc_ops  *ops;            // Operations callback
    struct bt_rfcomm_dlc      *_next;
    
    bt_security_t              required_sec_level;
    bt_rfcomm_role_t           role;           // Initiator/Acceptor
    
    uint16_t                   mtu;             // Max transmission unit
    uint8_t                    dlci;            // Data link connection identifier
    uint8_t                    state;
    uint8_t                    rx_credit;
};
```

### Server Registration

**RFCOMM Server Structure:**
```c
struct bt_rfcomm_server {
    uint8_t channel;              // Server channel (1-30)
    
    // Accept callback for new connections
    int (*accept)(struct bt_conn *conn, struct bt_rfcomm_dlc **dlc);
    
    struct bt_rfcomm_server *next;
};
```

**Register RFCOMM Server:**
```c
int bt_rfcomm_server_register(struct bt_rfcomm_server *server);
```

**Connect RFCOMM DLC:**
```c
int bt_rfcomm_dlc_connect(struct bt_conn *conn, struct bt_rfcomm_dlc *dlc, uint8_t channel);
```

**Send Data:**
```c
int bt_rfcomm_dlc_send(struct bt_rfcomm_dlc *dlc, struct net_buf *buf);
```

**Disconnect:**
```c
int bt_rfcomm_dlc_disconnect(struct bt_rfcomm_dlc *dlc);
```

**Create PDU buffer:**
```c
struct net_buf *bt_rfcomm_create_pdu(struct net_buf_pool *pool);
```

**Initialize RFCOMM:**
```c
void bt_rfcomm_init(void);
```

### Working Code Examples

**RFCOMM Server for Custom Service:**
```c
#include <bluetooth/rfcomm.h>

static struct bt_rfcomm_dlc *current_dlc;

static void rfcomm_connected(struct bt_rfcomm_dlc *dlc)
{
    printf("RFCOMM DLC connected\r\n");
    current_dlc = dlc;
}

static void rfcomm_disconnected(struct bt_rfcomm_dlc *dlc, struct bt_conn *conn)
{
    printf("RFCOMM DLC disconnected\r\n");
    current_dlc = NULL;
}

static void rfcomm_recv(struct bt_rfcomm_dlc *dlc, struct net_buf *buf)
{
    printf("RFCOMM received %u bytes\r\n", buf->len);
    
    // Process received data
    // ... handle data ...
    
    // Free the buffer
    net_buf_unref(buf);
}

static struct bt_rfcomm_dlc_ops rfcomm_ops = {
    .connected = rfcomm_connected,
    .disconnected = rfcomm_disconnected,
    .recv = rfcomm_recv,
};

static struct bt_rfcomm_dlc rfcomm_dlc = {
    .ops = &rfcomm_ops,
    .mtu = 127,  // Typical RFCOMM MTU
};

static int rfcomm_server_accept(struct bt_conn *conn, struct bt_rfcomm_dlc **dlc)
{
    printf("RFCOMM incoming connection\r\n");
    
    // Initialize DLC
    rfcomm_dlc.role = BT_RFCOMM_ROLE_ACCEPTOR;
    
    *dlc = &rfcomm_dlc;
    return 0;
}

static struct bt_rfcomm_server rfcomm_server = {
    .channel = 10,  // Custom channel
    .accept = rfcomm_server_accept,
};

void rfcomm_server_init(void)
{
    // Initialize RFCOMM
    bt_rfcomm_init();
    
    // Register server
    int err = bt_rfcomm_server_register(&rfcomm_server);
    if (err) {
        printf("RFCOMM server register failed: %d\r\n", err);
    } else {
        printf("RFCOMM server registered on channel %d\r\n", rfcomm_server.channel);
    }
}

void rfcomm_send_data(uint8_t *data, uint16_t len)
{
    if (!current_dlc) {
        printf("No RFCOMM connection\r\n");
        return;
    }
    
    // Create buffer with RFCOMM/L2CAP/ACL headers
    struct net_buf *buf = bt_rfcomm_create_pdu(NULL);
    if (!buf) {
        printf("Failed to allocate buffer\r\n");
        return;
    }
    
    // Add data
    net_buf_add_mem(buf, data, len);
    
    // Send
    int err = bt_rfcomm_dlc_send(current_dlc, buf);
    if (err) {
        printf("RFCOMM send failed: %d\r\n", err);
        net_buf_unref(buf);
    } else {
        printf("RFCOMM sent %u bytes\r\n", len);
    }
}

void rfcomm_disconnect(void)
{
    if (!current_dlc) {
        printf("No RFCOMM connection to disconnect\r\n");
        return;
    }
    
    int err = bt_rfcomm_dlc_disconnect(current_dlc);
    if (err) {
        printf("RFCOMM disconnect failed: %d\r\n", err);
    }
}
```

**RFCOMM Client Connection:**
```c
void rfcomm_client_connect(struct bt_conn *conn, uint8_t channel)
{
    int err;
    
    // Initialize DLC
    rfcomm_dlc.role = BT_RFCOMM_ROLE_INITIATOR;
    
    // Connect to server
    err = bt_rfcomm_dlc_connect(conn, &rfcomm_dlc, channel);
    if (err) {
        printf("RFCOMM connect failed: %d\r\n", err);
    } else {
        printf("RFCOMM connecting to channel %d...\r\n", channel);
    }
}
```

---

## Architecture Summary

```
┌─────────────────────────────────────────────────────────────┐
│                    Application Layer                         │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐ │
│  │    HFP      │  │    SPP      │  │   Application       │ │
│  │ Hands-Free  │  │ Serial Port │  │   Custom Service    │ │
│  └──────┬──────┘  └──────┬──────┘  └──────────┬──────────┘ │
├─────────┼────────────────┼────────────────────┼─────────────┤
│         │                │                    │             │
│  ┌──────▼──────┐  ┌──────▼──────┐  ┌──────────▼──────────┐ │
│  │   bt_hfp_hf │  │    spp      │  │    rfcomm_server    │ │
│  │  (AT cmds)  │  │  (send/recv)│  │   (custom server)   │ │
│  └──────┬──────┘  └──────┬──────┘  └──────────┬──────────┘ │
├─────────┼────────────────┼────────────────────┼─────────────┤
│         │                │                    │             │
│  ┌──────▼────────────────▼────────────────────▼──────────┐ │
│  │                     RFCOMM Layer                       │ │
│  │           (bt_rfcomm_dlc, channels, DLC ops)           │ │
│  └──────────────────────────┬────────────────────────────┘ │
├─────────────────────────────┼───────────────────────────────┤
│                             │                                │
│  ┌──────────────────────────▼────────────────────────────┐ │
│  │                     SDP Layer                           │ │
│  │        (Service records, discovery, attributes)        │ │
│  └────────────────────────────────────────────────────────┘ │
├─────────────────────────────────────────────────────────────┤
│                    L2CAP / ACL                              │
├─────────────────────────────────────────────────────────────┤
│                    HCI (Host Controller Interface)          │
├─────────────────────────────────────────────────────────────┤
│                    Bluetooth BR/EDR Controller              │
└─────────────────────────────────────────────────────────────┘
```

---

## File Locations

| Component | Header Path |
|-----------|-------------|
| HFP HF | `components/wireless/bluetooth/btprofile/include/bluetooth/hfp_hf.h` |
| SPP | `components/wireless/bluetooth/btprofile/include/bluetooth/spp.h` |
| RFCOMM | `components/wireless/bluetooth/btprofile/include/bluetooth/rfcomm.h` |
| SDP | `components/wireless/bluetooth/btprofile/include/bluetooth/sdp.h` |

## Build Configuration

Enable these profiles in your `proj.conf`:

```makefile
# Enable BR/EDR (Classic Bluetooth)
CONFIG_BT=y
CONFIG_BT_BREDR=y

# Enable HFP
CONFIG_BT_HFP_HF=y

# Enable SPP
CONFIG_BT_SPP=y

# Enable RFCOMM
CONFIG_BT_RFCOMM=y

# Enable SDP
CONFIG_BT_SDP=y
```
