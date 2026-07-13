# MQTT API Reference

> Source file: `components/network/axk_protocol_stack/axk_mqtt/include/mqtt_client.h`  
> BL602 built-in full MQTT client, supports MQTT over TCP/SSL/WebSocket, QoS 0/1/2, LWT, auto-reconnect.

---

## Overview

The MQTT protocol stack is based on axk-mqtt, supporting the following transport methods:

| Transport Type | scheme | Description |
|----------------|--------|-------------|
| MQTT over TCP | `mqtt://` | Plain TCP connection |
| MQTT over SSL | `mqtts://` | TLS encrypted connection |
| MQTT over WS | `ws://` | WebSocket plain text |
| MQTT over WSS | `wss://` | WebSocket TLS |

---

## Header Files

```c
#include "mqtt_client.h"
```

---

## Event Types

### `axk_mqtt_event_id_t`

MQTT event enumeration, used to distinguish handling in event callbacks:

```c
typedef enum {
    MQTT_EVENT_ANY = -1,
    MQTT_EVENT_ERROR = 0,          // Error event
    MQTT_EVENT_CONNECTED,          // Connection successful
    MQTT_EVENT_DISCONNECTED,       // Connection disconnected
    MQTT_EVENT_SUBSCRIBED,         // Subscribe successful
    MQTT_EVENT_UNSUBSCRIBED,       // Unsubscribe successful
    MQTT_EVENT_PUBLISHED,          // Publish successful
    MQTT_EVENT_DATA,               // Received message data
    MQTT_EVENT_BEFORE_CONNECT,     // Pre-connection event
    MQTT_EVENT_DELETED,            // Message deleted (timeout error)
} axk_mqtt_event_id_t;
```

---

## Event Structures

### `axk_mqtt_event_t`

Context information carried in event callbacks:

```c
typedef struct {
    axk_mqtt_event_id_t event_id;       // Event type
    axk_mqtt_client_handle_t client;   // MQTT client handle
    void *user_context;                 // User context
    char *data;                         // Message data
    int data_len;                       // Data length
    int total_data_len;                 // Total length (for long message fragmentation)
    int current_data_offset;            // Current data offset
    char *topic;                        // Message topic
    int topic_len;                      // Topic length
    int msg_id;                         // Message ID
    int session_present;                // Session persistence flag
    axk_mqtt_error_codes_t *error_handle; // Error information
    bool retain;                        // Retain message flag
    int qos;                            // QoS level
    bool dup;                           // Duplicate flag
} axk_mqtt_event_t;
```

### Connection Error Codes

```c
typedef enum {
    MQTT_CONNECTION_ACCEPTED = 0,                   // Connection successful
    MQTT_CONNECTION_REFUSE_PROTOCOL,                // Protocol error
    MQTT_CONNECTION_REFUSE_ID_REJECTED,             // ID rejected
    MQTT_CONNECTION_REFUSE_SERVER_UNAVAILABLE,      // Server unavailable
    MQTT_CONNECTION_REFUSE_BAD_USERNAME,            // Bad username
    MQTT_CONNECTION_REFUSE_NOT_AUTHORIZED           // Bad password
} axk_mqtt_connect_return_code_t;
```

---

## Client Configuration

### `axk_mqtt_client_config_t`

```c
typedef struct {
    mqtt_event_callback_t event_handle;      // Event callback function
    const char *host;                        // MQTT server domain/IP
    const char *uri;                         // Full URI (overrides host/port)
    uint32_t port;                           // Server port
    const char *client_id;                   // Client ID (default BL602_XXXXXX)
    const char *username;                    // Username
    const char *password;                    // Password
    const char *lwt_topic;                  // Last Will topic
    const char *lwt_msg;                    // Last Will message
    int lwt_qos;                            // Last Will QoS
    int lwt_retain;                         // Last Will retain
    int disable_clean_session;              // Disable clean session (1=keep session)
    int keepalive;                          // Keepalive interval (seconds, default 120)
    bool disable_auto_reconnect;            // Disable auto-reconnect
    void *user_context;                     // User context
    int task_prio;                          // MQTT task priority (default 5)
    int task_stack;                         // Task stack size (default 6144)
    int buffer_size;                        // Buffer size (default 1024)
    const char *cert_pem;                   // Server CA certificate (PEM)
    size_t cert_len;                        // Certificate length
    const char *client_cert_pem;            // Client certificate (two-way auth)
    size_t client_cert_len;
    const char *client_key_pem;            // Client private key
    size_t client_key_len;
    axk_mqtt_transport_t transport;         // Transport type (TCP/SSL/WS/WSS)
    int reconnect_timeout_ms;               // Reconnect timeout (default 10s)
    const char **alpn_protos;              // ALPN protocol list
    axk_mqtt_protocol_ver_t protocol_ver;  // MQTT version (3.1/3.1.1)
    bool skip_cert_common_name_check;        // Skip CN verification
    bool disable_keepalive;                 // Disable keepalive
    const char *path;                      // WebSocket path
} axk_mqtt_client_config_t;
```

---

## Function Interface

### `axk_mqtt_client_init`

Create and initialize an MQTT client.

```c
axk_mqtt_client_handle_t axk_mqtt_client_init(const axk_mqtt_client_config_t *config);
```

| Parameter | Description |
|-----------|-------------|
| `config` | Pointer to MQTT configuration structure |

**Return value**: Returns client handle on success, NULL on failure

---

### `axk_mqtt_client_start`

Start the MQTT client (initiate connection).

```c
axk_err_t axk_mqtt_client_start(axk_mqtt_client_handle_t client);
```

---

### `axk_mqtt_client_reconnect`

Force reconnect.

```c
axk_err_t axk_mqtt_client_reconnect(axk_mqtt_client_handle_t client);
```

---

### `axk_mqtt_client_disconnect`

Actively disconnect.

```c
axk_err_t axk_mqtt_client_disconnect(axk_mqtt_client_handle_t client);
```

---

### `axk_mqtt_client_stop`

Stop the MQTT task.

```c
axk_err_t axk_mqtt_client_stop(axk_mqtt_client_handle_t client);
```

---

### `axk_mqtt_client_subscribe`

Subscribe to a topic.

```c
int axk_mqtt_client_subscribe(axk_mqtt_client_handle_t client,
                              const char *topic, int qos);
```

| Parameter | Description |
|-----------|-------------|
| `topic` | Topic to subscribe to (supports wildcards `+` `#`) |
| `qos` | QoS level (0/1/2) |

**Return value**: Returns message ID on success, -1 on failure

---

### `axk_mqtt_client_unsubscribe`

Unsubscribe.

```c
int axk_mqtt_client_unsubscribe(axk_mqtt_client_handle_t client,
                                const char *topic);
```

---

### `axk_mqtt_client_publish`

Publish a message.

```c
int axk_mqtt_client_publish(axk_mqtt_client_handle_t client,
                             const char *topic,
                             const char *data, int len,
                             int qos, int retain);
```

| Parameter | Description |
|-----------|-------------|
| `topic` | Topic to publish to |
| `data` | Message payload |
| `len` | Payload length (0=auto calculate) |
| `qos` | QoS level (0/1/2) |
| `retain` | Retain flag |

**Return value**: Returns message ID on success, -1 on failure

---

### `axk_mqtt_client_enqueue`

Non-blocking publish (put into queue).

```c
int axk_mqtt_client_enqueue(axk_mqtt_client_handle_t client,
                             const char *topic,
                             const char *data, int len,
                             int qos, int retain,
                             bool store);
```

---

### `axk_mqtt_client_destroy`

Destroy the client and release resources.

```c
axk_err_t axk_mqtt_client_destroy(axk_mqtt_client_handle_t client);
```

---

### `axk_mqtt_set_config`

Update client configuration.

```c
axk_err_t axk_mqtt_set_config(axk_mqtt_client_handle_t client,
                                const axk_mqtt_client_config_t *config);
```

---

### `axk_mqtt_client_register_event`

Register event handler (alternative to callback method).

```c
axk_err_t axk_mqtt_client_register_event(axk_mqtt_client_handle_t client,
                                           axk_mqtt_event_id_t event,
                                           axk_event_handler_t event_handler,
                                           void *event_handler_arg);
```

---

## Usage Examples

### Basic MQTT Connection (QoS 0)

```c
#include "mqtt_client.h"

static const char *mqtt_uri = "mqtt://mqtt.eclipse.org:1883";
static const char *sub_topic = "bl602/test";
static const char *pub_topic = "bl602/status";

static void mqtt_event_handler(void *handler_args,
                                esp_event_base_t base,
                                int32_t event_id,
                                void *event_data)
{
    axk_mqtt_event_t *event = (axk_mqtt_event_t *)event_data;

    switch (event->event_id) {
    case MQTT_EVENT_CONNECTED:
        printf("MQTT connected\r\n");
        // Subscribe to topic
        axk_mqtt_client_subscribe(event->client, sub_topic, 0);
        // Publish online message
        axk_mqtt_client_publish(event->client, pub_topic,
                                "online", 6, 0, 1);
        break;

    case MQTT_EVENT_DISCONNECTED:
        printf("MQTT disconnected\r\n");
        break;

    case MQTT_EVENT_SUBSCRIBED:
        printf("Subscribed to: %s\r\n", sub_topic);
        break;

    case MQTT_EVENT_DATA:
        printf("Message on %.*s: %.*s\r\n",
               event->topic_len, event->topic,
               event->data_len, event->data);
        break;

    case MQTT_EVENT_ERROR:
        printf("MQTT error\r\n");
        break;
    }
}

void mqtt_app_start(void)
{
    // Configure MQTT client
    axk_mqtt_client_config_t config = {
        .uri = mqtt_uri,
        .event_handle = mqtt_event_handler,
        .keepalive = 120,
        .disable_auto_reconnect = false,
    };

    // Initialize and start
    axk_mqtt_client_handle_t client = axk_mqtt_client_init(&config);
    if (client) {
        axk_mqtt_client_start(client);
    }
}
```

### MQTT over SSL (Two-Way Authentication)

```c
axk_mqtt_client_config_t ssl_config = {
    .uri = "mqtts://your-mqtt-server.com:8883",
    .event_handle = mqtt_event_handler,
    .cert_pem = ca_cert_pem,          // Server CA certificate
    .client_cert_pem = client_cert,   // Client certificate
    .client_key_pem = client_key,     // Client private key
    .skip_cert_common_name_check = false,
};

axk_mqtt_client_handle_t ssl_client = axk_mqtt_client_init(&ssl_config);
axk_mqtt_client_start(ssl_client);
```

### MQTT over WebSocket

```c
axk_mqtt_client_config_t ws_config = {
    .uri = "wss://your-mqtt-server.com:443/mqtt",
    .event_handle = mqtt_event_handler,
    .transport = MQTT_TRANSPORT_OVER_WSS,
};

axk_mqtt_client_handle_t ws_client = axk_mqtt_client_init(&ws_config);
axk_mqtt_client_start(ws_client);
```

---

## Transport Types

```c
typedef enum {
    MQTT_TRANSPORT_UNKNOWN = 0x0,
    MQTT_TRANSPORT_OVER_TCP,      // mqtt://
    MQTT_TRANSPORT_OVER_SSL,      // mqtts://
    MQTT_TRANSPORT_OVER_WS,       // ws://
    MQTT_TRANSPORT_OVER_WSS       // wss://
} axk_mqtt_transport_t;
```

## MQTT Versions

```c
typedef enum {
    MQTT_PROTOCOL_UNDEFINED = 0,
    MQTT_PROTOCOL_V_3_1,      // MQTT 3.1
    MQTT_PROTOCOL_V_3_1_1     // MQTT 3.1.1 (default)
} axk_mqtt_protocol_ver_t;
```
