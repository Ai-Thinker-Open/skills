# MQTT Client Documentation (BL616/BL618)

MQTT-C implementation for Bouffalo SDK. Based on Liam Bindle's MQTT-C library.

## Overview

- **Header**: `bouffalo_sdk/components/net/lib/mqtt/inc/mqtt.h`
- **Thread-safe**: Yes
- **Protocol**: MQTT v3.1.1

## Quality of Service (QoS)

| Level | Flag | Description |
|-------|------|-------------|
| 0 | `MQTT_PUBLISH_QOS_0` | At most once delivery (fire and forget) |
| 1 | `MQTT_PUBLISH_QOS_1` | At least once delivery (acknowledged) |
| 2 | `MQTT_PUBLISH_QOS_2` | Exactly once delivery (handshake) |

## Core Functions

### mqtt_init - Initialize MQTT Client

```c
enum MQTTErrors mqtt_init(struct mqtt_client *client,
                          mqtt_pal_socket_handle sockfd,
                          uint8_t *sendbuf, size_t sendbufsz,
                          uint8_t *recvbuf, size_t recvbufsz,
                          void (*publish_response_callback)(void** state, struct mqtt_response_publish *publish));
```

**Parameters**:
- `client` - Pointer to MQTT client structure
- `sockfd` - Connected TCP socket handle
- `sendbuf` - Transmit buffer
- `sendbufsz` - Transmit buffer size
- `recvbuf` - Receive buffer
- `recvbufsz` - Receive buffer size
- `publish_response_callback` - Callback for incoming messages

**Example**:
```c
static uint8_t mqtt_tx_buffer[1024];
static uint8_t mqtt_rx_buffer[1024];

void message_callback(void** state, struct mqtt_response_publish *publish) {
    printf("Received: %.*s\n", 
           (int)publish->application_message_size,
           (char*)publish->application_message);
}

mqtt_init(&client, socketfd, 
          mqtt_tx_buffer, sizeof(mqtt_tx_buffer),
          mqtt_rx_buffer, sizeof(mqtt_rx_buffer),
          message_callback);
```

---

### mqtt_connect - Connect to Broker

```c
enum MQTTErrors mqtt_connect(struct mqtt_client *client,
                             const char* client_id,
                             const char* will_topic,
                             const void* will_message,
                             size_t will_message_size,
                             const char* user_name,
                             const char* password,
                             uint8_t connect_flags,
                             uint16_t keep_alive);
```

**Parameters**:
- `client_id` - Unique client identifier (NULL for anonymous)
- `will_topic` - LWT topic (set NULL if unused)
- `will_message` - LWT message payload
- `will_message_size` - LWT message size in bytes
- `user_name` - Authentication username (NULL if none)
- `password` - Authentication password (NULL if none)
- `connect_flags` - Connection flags (see below)
- `keep_alive` - Keep-alive interval in seconds

**Connection Flags**:
```c
MQTT_CONNECT_CLEAN_SESSION    // Start fresh session
MQTT_CONNECT_WILL_QOS_0       // Will QoS level 0
MQTT_CONNECT_WILL_QOS_1        // Will QoS level 1
MQTT_CONNECT_WILL_QOS_2        // Will QoS level 2
MQTT_CONNECT_WILL_RETAIN       // Retain will message
MQTT_CONNECT_PASSWORD          // Password flag
MQTT_CONNECT_USER_NAME         // Username flag
```

**Example - Basic Connection**:
```c
mqtt_connect(&client,
             "my_device",    // client_id
             NULL,           // will_topic
             NULL,           // will_message
             0,              // will_message_size
             NULL,           // user_name
             NULL,           // password
             MQTT_CONNECT_CLEAN_SESSION,
             400);          // keep_alive 400 seconds
```

**Example - Connection with LWT and Authentication**:
```c
mqtt_connect(&client,
             "sensor_01",
             "devices/sensor_01/status",     // Will topic
             "offline",                       // Will message
             7,                               // message size
             "user",                          // username
             "pass",                          // password
             MQTT_CONNECT_CLEAN_SESSION | MQTT_CONNECT_WILL_QOS_1 | MQTT_CONNECT_WILL_RETAIN,
             400);
```

---

### mqtt_subscribe - Subscribe to Topic

```c
enum MQTTErrors mqtt_subscribe(struct mqtt_client *client,
                               const char* topic_name,
                               int max_qos_level);
```

**Parameters**:
- `topic_name` - Topic to subscribe to
- `max_qos_level` - Maximum QoS level (0, 1, or 2)

**Example**:
```c
mqtt_subscribe(&client, "home/sensors/temperature", 1);
mqtt_subscribe(&client, "home/sensors/humidity", 0);
mqtt_subscribe(&client, "commands/#", 2);  // Wildcard subscription
```

---

### mqtt_publish - Publish Message

```c
enum MQTTErrors mqtt_publish(struct mqtt_client *client,
                             const char* topic_name,
                             const void* application_message,
                             size_t application_message_size,
                             uint8_t publish_flags);
```

**Publish Flags**:
```c
MQTT_PUBLISH_QOS_0    // QoS 0
MQTT_PUBLISH_QOS_1    // QoS 1
MQTT_PUBLISH_QOS_2    // QoS 2
MQTT_PUBLISH_RETAIN   // Retain message
```

**Example - QoS 0 Publish**:
```c
const char *msg = "Hello MQTT";
mqtt_publish(&client,
             "home/sensors/temperature",
             msg, strlen(msg),
             MQTT_PUBLISH_QOS_0);
```

**Example - QoS 2 Publish with Retain**:
```c
const char *msg = "Sensor data";
mqtt_publish(&client,
             "home/sensors/data",
             msg, strlen(msg),
             MQTT_PUBLISH_QOS_2 | MQTT_PUBLISH_RETAIN);
```

---

### mqtt_disconnect - Disconnect from Broker

```c
enum MQTTErrors mqtt_disconnect(struct mqtt_client *client);
```

**Example**:
```c
mqtt_disconnect(&client);
```

---

### mqtt_sync - Process Network Traffic

```c
enum MQTTErrors mqtt_sync(struct mqtt_client *client);
```

**Description**: Must be called periodically to send/receive MQTT traffic and invoke callbacks.

**Note**: Call this every ~200ms in your main loop.

---

## Complete Working Example

```c
#include <mqtt.h>
#include <sys/socket.h>
#include <netdb.h>

static struct mqtt_client client;
static uint8_t sendbuf[1024];
static uint8_t recvbuf[512];

void publish_callback(void** state, struct mqtt_response_publish *publish) {
    printf("Topic: %.*s\n", (int)publish->topic_name_size, (char*)publish->topic_name);
    printf("Message: %.*s\n", 
           (int)publish->application_message_size,
           (char*)publish->application_message);
}

int mqtt_task(void) {
    int sockfd;
    struct sockaddr_in broker_addr;
    struct hostent *broker;

    // Create socket
    sockfd = socket(AF_INET, SOCK_STREAM, 0);
    if (sockfd < 0) return -1;

    // Resolve broker
    broker = gethostbyname("test.mosquitto.org");
    if (!broker) return -1;

    // Connect to broker
    memset(&broker_addr, 0, sizeof(broker_addr));
    broker_addr.sin_family = AF_INET;
    memcpy(&broker_addr.sin_addr, broker->h_addr, broker->h_length);
    broker_addr.sin_port = htons(1883);

    if (connect(sockfd, (struct sockaddr*)&broker_addr, sizeof(broker_addr)) < 0)
        return -1;

    // Initialize MQTT client
    mqtt_init(&client, (mqtt_pal_socket_handle)sockfd,
              sendbuf, sizeof(sendbuf),
              recvbuf, sizeof(recvbuf),
              publish_callback);

    // Connect to MQTT broker
    enum MQTTErrors ret = mqtt_connect(&client,
                                       "bl616_client",
                                       "devices/bl616/status",
                                       "offline", 7,
                                       NULL, NULL,
                                       MQTT_CONNECT_CLEAN_SESSION,
                                       400);
    if (ret != MQTT_OK) {
        printf("MQTT connect failed: %s\n", mqtt_error_str(ret));
        return -1;
    }

    // Subscribe to topics
    mqtt_subscribe(&client, "home/commands", 1);

    // Main loop
    while (1) {
        mqtt_sync(&client);
        
        // Publish sensor data every 5 seconds
        static uint32_t last_publish = 0;
        if (g_msec_since_boot() - last_publish > 5000) {
            char msg[64];
            snprintf(msg, sizeof(msg), "temp=%.1f", 25.5);
            mqtt_publish(&client, "home/sensors/temp",
                         msg, strlen(msg),
                         MQTT_PUBLISH_QOS_1);
            last_publish = g_msec_since_boot();
        }
        
        usleep(10000);  // 10ms delay
    }

    mqtt_disconnect(&client);
    close(sockfd);
    return 0;
}
```

## Error Handling

```c
const char* mqtt_error_str(enum MQTTErrors error);
```

**Common Errors**:
- `MQTT_ERROR_NULLPTR` - Null pointer provided
- `MQTT_ERROR_SOCKET_ERROR` - Socket communication error
- `MQTT_ERROR_CONNECTION_CLOSED` - Connection lost
- `MQTT_ERROR_CONNECT_NOT_CALLED` - mqtt_connect not called
- `MQTT_ERROR_SEND_BUFFER_IS_FULL` - TX buffer overflow

---

## Will Topic (LWT - Last Will and Testament)

The will topic allows you to specify a message that the broker will publish if the client disconnects unexpectedly.

**Configuration during mqtt_connect**:
- `will_topic` - Topic name for the will message
- `will_message` - Payload to be published
- `connect_flags` - QoS and retain flags for will message

**Use Cases**:
- Device online/offline status tracking
- Failure notifications
- State cleanup commands

---

## Keep-Alive

- **Purpose**: Detect if broker or client is still reachable
- **Value**: Seconds between keep-alive pings
- **Behavior**: Client sends PINGREQ if no traffic for keep_alive seconds
- **Recommended**: 400 seconds for most applications
- **Minimum**: 60 seconds recommended

**Note**: `mqtt_sync()` handles keep-alive automatically.
