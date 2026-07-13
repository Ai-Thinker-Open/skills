# OpenThread API Reference (BL616/BL618)

OpenThread is a Thread networking protocol implementation. This document covers the essential OpenThread APIs for BL616/BL618 devices using the Bouffalo SDK.

## Table of Contents

1. [Instance Creation](#1-instance-creation)
2. [Thread Stack Initialization](#2-thread-stack-initialization)
3. [Device Role (Leader/Router/Child)](#3-device-role-leaderrouterchild)
4. [IPv6 Interface](#4-ipv6-interface)
5. [UDP Sockets](#5-udp-sockets)
6. [CoAP](#6-coap)
7. [Complete Working Example](#7-complete-working-example)

---

## 1. Instance Creation

### 1.1 Initialize Single Instance

For most use cases with a single OpenThread instance:

```c
#include <openthread/instance.h>

// Single instance initialization (no dynamic allocation)
otInstance *instance = otInstanceInitSingle();

if (instance == NULL) {
    // Handle error
}
```

### 1.2 Initialize with Buffer

When multiple instances or custom allocation is needed:

```c
uint8_t instanceBuffer[4096];
size_t bufferSize = sizeof(instanceBuffer);

otInstance *instance = otInstanceInit(instanceBuffer, &bufferSize);
if (instance == NULL) {
    // Handle error
}
```

### 1.3 Get Instance (Bouffalo SDK)

In the Bouffalo SDK, after `otrStart()` is called, get the instance:

```c
#include <openthread_port.h>

otInstance *instance = otrGetInstance();
```

### 1.4 Instance Cleanup

```c
void otInstanceFinalize(otInstance *aInstance);
```

---

## 2. Thread Stack Initialization

### 2.1 Platform-Level Init (Bouffalo SDK)

```c
#include <openthread_port.h>

// Initialize radio, alarm, UART, and thread task
otrStart();

// Get the instance after start
otInstance *instance = otrGetInstance();
```

### 2.2 User Initialization Callback

Implement `otrInitUser()` to add your own initialization:

```c
// This is called by OpenThread task after instance creation
void otrInitUser(otInstance *instance) {
    // Your initialization code here
    // This runs in OpenThread task context - thread-safe
}
```

### 2.3 Enable Thread Protocol

```c
#include <openthread/thread.h>

// Enable Thread operation (interface must be up first)
otError error = otThreadSetEnabled(instance, true);
if (error != OT_ERROR_NONE) {
    // Handle error
}
```

### 2.4 Configure Network Parameters

```c
#include <openthread/dataset.h>

// Create operational dataset
otOperationalDataset dataset = {0};

// Set network key (16 bytes)
uint8_t networkKey[16] = {0x00, 0x11, 0x22, 0x33, 0x44, 0x55, 0x66, 0x77,
                          0x88, 0x99, 0xAA, 0xBB, 0xCC, 0xDD, 0xEE, 0xFF};
memcpy(dataset.mNetworkKey.m8, networkKey, 16);
dataset.mComponents.mIsNetworkKeyPresent = true;

// Set network name
strcpy((char *)dataset.mNetworkName.m8, "MyThreadNet");
dataset.mComponents.mIsNetworkNamePresent = true;

// Set channel (channel 11 = 0x0B)
dataset.mChannel = 11;
dataset.mComponents.mIsChannelPresent = true;

// Set PAN ID
dataset.mPanId = 0x1234;
dataset.mComponents.mIsPanIdPresent = true;

// Set active dataset
otError error = otDatasetSetActive(instance, &dataset);
```

---

## 3. Device Role (Leader/Router/Child)

### 3.1 Device Role Enum

```c
typedef enum {
    OT_DEVICE_ROLE_DISABLED = 0,  // Thread stack is disabled
    OT_DEVICE_ROLE_DETACHED  = 1,  // Not in a Thread network
    OT_DEVICE_ROLE_CHILD     = 2,  // Child role
    OT_DEVICE_ROLE_ROUTER    = 3,  // Router role
    OT_DEVICE_ROLE_LEADER   = 4,  // Leader role
} otDeviceRole;
```

### 3.2 Get Current Device Role

```c
#include <openthread/thread.h>

otDeviceRole role = otThreadGetDeviceRole(instance);

switch (role) {
    case OT_DEVICE_ROLE_DISABLED:
        printf("Role: Disabled\n");
        break;
    case OT_DEVICE_ROLE_DETACHED:
        printf("Role: Detached\n");
        break;
    case OT_DEVICE_ROLE_CHILD:
        printf("Role: Child\n");
        break;
    case OT_DEVICE_ROLE_ROUTER:
        printf("Role: Router\n");
        break;
    case OT_DEVICE_ROLE_LEADER:
        printf("Role: Leader\n");
        break;
}
```

### 3.3 Role Change Callback

```c
#include <openthread/instance.h>

static void stateChangedCallback(otChangedFlags flags, void *context) {
    if (flags & OT_CHANGED_THREAD_ROLE) {
        otInstance *instance = (otInstance *)context;
        otDeviceRole role = otThreadGetDeviceRole(instance);
        printf("Device role changed to: %d\n", role);
    }
}

// Register callback
otSetStateChangedCallback(instance, stateChangedCallback, instance);
```

### 3.4 Get Leader Info

```c
otLeaderData leaderData;
otError error = otThreadGetLeaderData(instance, &leaderData);
if (error == OT_ERROR_NONE) {
    printf("Leader Router ID: %u\n", leaderData.mLeaderRouterId);
    printf("Partition ID: %u\n", leaderData.mPartitionId);
}
```

### 3.5 Get Leader RLOC Address

```c
otIp6Address leaderRloc;
otError error = otThreadGetLeaderRloc(instance, &leaderRloc);
if (error == OT_ERROR_NONE) {
    // Print leader address
    char addrStr[64];
    printf("Leader RLOC: %s\n", 
           otIp6AddressToString(&leaderRloc, addrStr, sizeof(addrStr)));
}
```

---

## 4. IPv6 Interface

### 4.1 Enable/Disable IPv6

```c
#include <openthread/ip6.h>

// Enable IPv6 interface
otError error = otIp6SetEnabled(instance, true);

// Check if IPv6 is enabled
bool enabled = otIp6IsEnabled(instance);
```

### 4.2 Get IPv6 Addresses

```c
// Get all unicast addresses
const otNetifAddress *addr = otIp6GetUnicastAddresses(instance);
while (addr != NULL) {
    char addrStr[64];
    printf("Address: %s/%u\n", 
           otIp6AddressToString(&addr->mAddress, addrStr, sizeof(addrStr)),
           addr->mPrefixLength);
    addr = addr->mNext;
}
```

### 4.3 Get Mesh Local EID

```c
const otIp6Address *meshLocalEid = otThreadGetMeshLocalEid(instance);
char addrStr[64];
printf("Mesh Local EID: %s\n", 
       otIp6AddressToString(meshLocalEid, addrStr, sizeof(addrStr)));
```

### 4.4 Get RLOC Address

```c
const otIp6Address *rloc = otThreadGetRloc(instance);
char addrStr[64];
printf("RLOC: %s\n", 
       otIp6AddressToString(rloc, addrStr, sizeof(addrStr)));
```

### 4.5 Subscribe to Multicast

```c
// Subscribe to link-local all nodes multicast
otIp6Address linkLocalAllNodes;
otIp6AddressFromString("ff02::1", &linkLocalAllNodes);
otIp6SubscribeMulticastAddress(instance, &linkLocalAllNodes);

// Subscribe to realm-local all nodes
otIp6Address realmLocalAllNodes;
otIp6AddressFromString("ff03::1", &realmLocalAllNodes);
otIp6SubscribeMulticastAddress(instance, &realmLocalAllNodes);
```

---

## 5. UDP Sockets

### 5.1 UDP Socket Structure

```c
#include <openthread/udp.h>

typedef struct otUdpSocket {
    otSockAddr          mSockName;      // Local address:port
    otSockAddr          mPeerName;      // Peer address:port
    otUdpReceive        mHandler;       // Receive callback
    void               *mContext;       // User context
    void               *mHandle;        // Platform handle (internal)
    struct otUdpSocket *mNext;          // Next socket (internal)
    otNetifIdentifier   mNetifId;       // Network interface
} otUdpSocket;
```

### 5.2 UDP Receive Callback

```c
static void udpReceiveCallback(void *context, otMessage *message, 
                                const otMessageInfo *messageInfo) {
    (void)context;
    
    // Read data from message
    uint16_t length = otMessageGetLength(message);
    uint8_t buffer[256];
    
    if (length > sizeof(buffer)) {
        length = sizeof(buffer);
    }
    
    otMessageRead(message, 0, buffer, length);
    
    printf("UDP received %u bytes from [%s]:%u\n",
           length,
           otIp6AddressToString(&messageInfo->mPeerAddr, 
                                (char[64]){0}, 64),
           messageInfo->mPeerPort);
}
```

### 5.3 Open and Bind UDP Socket

```c
otUdpSocket socket;
otSockAddr bindAddr;

// Initialize socket
memset(&socket, 0, sizeof(socket));

// Configure local address (unspecified = auto-select)
memset(&bindAddr, 0, sizeof(bindAddr));
bindAddr.mPort = 12345;  // Local port

// Open UDP socket
otError error = otUdpOpen(instance, &socket, udpReceiveCallback, instance);
if (error != OT_ERROR_NONE) {
    printf("Failed to open UDP socket: %d\n", error);
    return;
}

// Bind to port
error = otUdpBind(instance, &socket, &bindAddr, OT_NETIF_THREAD_INTERNAL);
if (error != OT_ERROR_NONE) {
    printf("Failed to bind UDP socket: %d\n", error);
    return;
}

printf("UDP socket bound to port %u\n", bindAddr.mPort);
```

### 5.4 Connect UDP Socket (Set Default Peer)

```c
otSockAddr peerAddr;

// Set peer address
otIp6AddressFromString("ff02::1", &peerAddr.mAddress);  // Multicast
peerAddr.mPort = 54321;

// Connect (optional - sets default peer)
error = otUdpConnect(instance, &socket, &peerAddr);
```

### 5.5 Send UDP Message

```c
// Create message
otMessage *message = otUdpNewMessage(instance, NULL);
if (message == NULL) {
    printf("Failed to create message\n");
    return;
}

// Write data
const char *data = "Hello, Thread!";
otMessageWrite(message, 0, (const uint8_t *)data, strlen(data));

// Configure message info
otMessageInfo msgInfo;
memset(&msgInfo, 0, sizeof(msgInfo));
msgInfo.mPeerAddr = peerAddr.mAddress;  // Use connected peer or specify
msgInfo.mPeerPort = peerAddr.mPort;
msgInfo.mSockPort = bindAddr.mPort;

// Send
error = otUdpSend(instance, &socket, message, &msgInfo);
if (error != OT_ERROR_NONE) {
    printf("Failed to send UDP: %d\n", error);
    otMessageFree(message);
}
```

### 5.6 Close UDP Socket

```c
otUdpClose(instance, &socket);
```

---

## 6. CoAP

### 6.1 CoAP Type and Code Enums

```c
#include <openthread/coap.h>

// CoAP Message Types
typedef enum {
    OT_COAP_TYPE_CONFIRMABLE     = 0,    // CON
    OT_COAP_TYPE_NON_CONFIRMABLE = 1,    // NON
    OT_COAP_TYPE_ACKNOWLEDGMENT  = 2,    // ACK
    OT_COAP_TYPE_RESET           = 3,    // RST
} otCoapType;

// CoAP Request Codes
typedef enum {
    OT_COAP_CODE_GET    = OT_COAP_CODE(0, 1),
    OT_COAP_CODE_POST   = OT_COAP_CODE(0, 2),
    OT_COAP_CODE_PUT    = OT_COAP_CODE(0, 3),
    OT_COAP_CODE_DELETE = OT_COAP_CODE(0, 4),
} otCoapCode;

// CoAP Response Codes
typedef enum {
    OT_COAP_CODE_CREATED   = OT_COAP_CODE(2, 1),
    OT_COAP_CODE_CHANGED   = OT_COAP_CODE(2, 4),
    OT_COAP_CODE_CONTENT   = OT_COAP_CODE(2, 5),
    // ... and many more
} otCoapCode;
```

### 6.2 CoAP Resource Structure

```c
typedef struct otCoapResource {
    const char            *mUriPath;    // URI path (e.g., "sensor/temp")
    otCoapRequestHandler  mHandler;    // Request handler callback
    void                  *mContext;   // User context
    struct otCoapResource *mNext;      // Next resource (internal)
} otCoapResource;
```

### 6.3 CoAP Request Handler

```c
static void coapRequestHandler(void *context, otMessage *message,
                               const otMessageInfo *messageInfo) {
    (void)context;
    
    // Check request method from code
    otCoapCode code = otMessageGetCode(message);
    
    if (code == OT_COAP_CODE_GET) {
        // Handle GET request
        printf("CoAP GET request received\n");
        
        // Create response
        otMessage *response = otCoapNewMessage(instance, NULL);
        otCoapMessageInitResponse(response, message, 
                                  OT_COAP_TYPE_ACKNOWLEDGMENT,
                                  OT_COAP_CODE_CONTENT);
        
        // Add payload
        const char *payload = "Temperature: 25C";
        otMessageSetPayloadMarker(response);
        otMessageWrite(response, 0, (const uint8_t *)payload, strlen(payload));
        
        // Send response
        otUdpSend(instance, &coapSocket, response, messageInfo);
        
    } else if (code == OT_COAP_CODE_POST) {
        // Handle POST request
        printf("CoAP POST request received\n");
        
        // Read payload
        uint16_t length = otMessageGetLength(message);
        uint8_t buffer[256];
        if (length > sizeof(buffer)) length = sizeof(buffer);
        otMessageRead(message, 0, buffer, length);
        
        // Process data...
        
        // Send response
        otMessage *response = otCoapNewMessage(instance, NULL);
        otCoapMessageInitResponse(response, message,
                                  OT_COAP_TYPE_ACKNOWLEDGMENT,
                                  OT_COAP_CODE_CHANGED);
        otUdpSend(instance, &coapSocket, response, messageInfo);
    }
}
```

### 6.4 Initialize CoAP Server

```c
#include <openthread/coap.h>

#define COAP_PORT 5683

// Start CoAP service
otError error = otCoapStart(instance, COAP_PORT);
if (error != OT_ERROR_NONE) {
    printf("Failed to start CoAP: %d\n", error);
    return;
}

// Define resources
static otCoapResource sensorResource = {
    .mUriPath = "sensor/temp",
    .mHandler = coapRequestHandler,
    .mContext = instance,
};

// Add resource
otCoapAddResource(instance, &sensorResource);

// Add another resource
static otCoapResource ledResource = {
    .mUriPath = "led",
    .mHandler = ledRequestHandler,
    .mContext = instance,
};
otCoapAddResource(instance, &ledResource);
```

### 6.5 Send CoAP Request

```c
otMessage *request = otCoapNewMessage(instance, NULL);
if (request == NULL) {
    return;
}

otCoapMessageInit(request, OT_COAP_TYPE_CONFIRMABLE, OT_COAP_CODE_GET);

// Add URI path option
otCoapMessageAppendUriPathOptions(request, "sensor/temp");

// Set destination
otMessageInfo msgInfo;
memset(&msgInfo, 0, sizeof(msgInfo));
otIp6AddressFromString("ff02::1", &msgInfo.mPeerAddr);  // Multicast
msgInfo.mPeerPort = COAP_PORT;

// Send
otError error = otCoapSendRequest(instance, request, &msgInfo,
                                  responseCallback, context);
```

### 6.6 CoAP Response Callback

```c
static void coapResponseHandler(void *context, otMessage *message,
                                 const otMessageInfo *messageInfo,
                                 otError aResult) {
    (void)context;
    (void)messageInfo;
    
    if (aResult == OT_ERROR_NONE && message != NULL) {
        uint16_t length = otMessageGetLength(message);
        uint8_t buffer[256];
        if (length > sizeof(buffer)) length = sizeof(buffer);
        otMessageRead(message, 0, buffer, length);
        printf("CoAP Response: %.*s\n", length, buffer);
    } else if (aResult == OT_ERROR_RESPONSE_TIMEOUT) {
        printf("CoAP Response timeout\n");
    }
}
```

### 6.7 Remove CoAP Resource

```c
otCoapRemoveResource(instance, &sensorResource);

// Stop CoAP server
otCoapStop(instance);
```

---

## 7. Complete Working Example

```c
#include <openthread/instance.h>
#include <openthread/thread.h>
#include <openthread/ip6.h>
#include <openthread/udp.h>
#include <openthread/coap.h>
#include <openthread/dataset.h>
#include <openthread_port.h>

static otInstance *sInstance = NULL;
static otUdpSocket sUdpSocket;
static otUdpSocket sCoapSocket;
static otCoapResource sSensorResource;

/*******************************************************************************
 * UDP Receive Callback
 ******************************************************************************/
static void udpReceiveCallback(void *context, otMessage *message,
                                const otMessageInfo *messageInfo) {
    (void)context;
    uint16_t length = otMessageGetLength(message);
    uint8_t buffer[256];
    
    if (length > sizeof(buffer)) length = sizeof(buffer);
    otMessageRead(message, 0, buffer, length);
    
    printf("UDP [%s]:%u -> %u bytes: %.*s\n",
           otIp6AddressToString(&messageInfo->mPeerAddr, (char[64]){0}, 64),
           messageInfo->mPeerPort,
           length, length, buffer);
}

/*******************************************************************************
 * State Change Callback
 ******************************************************************************/
static void stateChangedCallback(otChangedFlags flags, void *context) {
    if (flags & OT_CHANGED_THREAD_ROLE) {
        otDeviceRole role = otThreadGetDeviceRole(sInstance);
        const char *roleStr = otThreadDeviceRoleToString(role);
        printf("Thread role changed to: %s\n", roleStr);
    }
    
    if (flags & OT_CHANGED_THREAD_NETIF_STATE) {
        if (otIp6IsEnabled(sInstance)) {
            printf("IPv6 interface is up\n");
        }
    }
}

/*******************************************************************************
 * CoAP Request Handler
 ******************************************************************************/
static void sensorRequestHandler(void *context, otMessage *message,
                                  const otMessageInfo *messageInfo) {
    (void)context;
    otCoapCode code = otMessageGetCode(message);
    
    if (code == OT_COAP_CODE_GET) {
        printf("CoAP GET /sensor/temp\n");
        
        otMessage *response = otCoapNewMessage(sInstance, NULL);
        otCoapMessageInitResponse(response, message,
                                  OT_COAP_TYPE_ACKNOWLEDGMENT,
                                  OT_COAP_CODE_CONTENT);
        
        const char *payload = "{\"temp\":25}";
        otMessageSetPayloadMarker(response);
        otMessageWrite(response, 0, (const uint8_t *)payload, strlen(payload));
        
        otUdpSend(sInstance, &sCoapSocket, response, messageInfo);
    }
}

/*******************************************************************************
 * Thread Network Setup
 ******************************************************************************/
static otError setupThreadNetwork(void) {
    otOperationalDataset dataset = {0};
    
    // Network key
    uint8_t networkKey[16] = {0x00, 0x11, 0x22, 0x33, 0x44, 0x55, 0x66, 0x77,
                              0x88, 0x99, 0xAA, 0xBB, 0xCC, 0xDD, 0xEE, 0xFF};
    memcpy(dataset.mNetworkKey.m8, networkKey, 16);
    dataset.mComponents.mIsNetworkKeyPresent = true;
    
    // Network name
    strcpy((char *)dataset.mNetworkName.m8, "BL616-Thread");
    dataset.mComponents.mIsNetworkNamePresent = true;
    
    // Channel
    dataset.mChannel = 11;
    dataset.mComponents.mIsChannelPresent = true;
    
    // PAN ID
    dataset.mPanId = 0x1234;
    dataset.mComponents.mIsPanIdPresent = true;
    
    // Active timestamp
    dataset.mActiveTimestamp.mSeconds = 1;
    dataset.mComponents.mIsActiveTimestampPresent = true;
    
    return otDatasetSetActive(sInstance, &dataset);
}

/*******************************************************************************
 * User Initialization (called from OpenThread task)
 ******************************************************************************/
void otrInitUser(otInstance *instance) {
    sInstance = instance;
    
    printf("OpenThread initialized\n");
    printf("Version: %s\n", otGetVersionString());
    
    // Setup network
    otError error = setupThreadNetwork();
    if (error != OT_ERROR_NONE) {
        printf("Failed to setup network: %d\n", error);
    }
    
    // Enable IPv6
    otIp6SetEnabled(instance, true);
    
    // Enable Thread
    otThreadSetEnabled(instance, true);
    
    // Register state change callback
    otSetStateChangedCallback(instance, stateChangedCallback, instance);
    
    // Setup UDP socket
    otSockAddr bindAddr = {0};
    bindAddr.mPort = 12345;
    
    error = otUdpOpen(instance, &sUdpSocket, udpReceiveCallback, instance);
    if (error == OT_ERROR_NONE) {
        otUdpBind(instance, &sUdpSocket, &bindAddr, OT_NETIF_THREAD_INTERNAL);
    }
    
    // Setup CoAP
    otCoapStart(instance, 5683);
    
    sSensorResource.mUriPath = "sensor/temp";
    sSensorResource.mHandler = sensorRequestHandler;
    sSensorResource.mContext = instance;
    otCoapAddResource(instance, &sSensorResource);
    
    // Subscribe to multicast
    otIp6Address multicastAddr;
    otIp6AddressFromString("ff03::1", &multicastAddr);
    otIp6SubscribeMulticastAddress(instance, &multicastAddr);
}

/*******************************************************************************
 * Main Application
 ******************************************************************************/
void app_main(void) {
    // Start OpenThread (creates task, calls otrInitUser)
    otrStart();
    
    // Main loop
    while (1) {
        // Your application code
        vTaskDelay(pdMS_TO_TICKS(1000));
    }
}
```

---

## Error Handling

All OpenThread functions return `otError`:

```c
typedef enum {
    OT_ERROR_NONE = 0,
    OT_ERROR_FAILED = 1,
    OT_ERROR_NO_BUFS = 3,
    OT_ERROR_INVALID_ARGS = 7,
    OT_ERROR_BUSY = 5,
    OT_ERROR_NOT_FOUND = 23,
    OT_ERROR_ALREADY = 24,
    // ... more errors
} otError;
```

Convert error to string:
```c
const char *errorStr = otThreadErrorToString(error);
printf("Error: %s\n", errorStr);
```

## Thread Safety

Use these macros when calling OpenThread APIs from other tasks:

```c
// Thread-safe call (no return value)
OT_THREAD_SAFE(
    otThreadSetEnabled(instance, true);
);

// Thread-safe call with return value
otError error;
OT_THREAD_SAFE_RET(error, otThreadGetDeviceRole(instance));
```

## Key Header Files

| Header | Description |
|--------|-------------|
| `openthread/instance.h` | Instance creation and management |
| `openthread/thread.h` | Thread protocol, device roles |
| `openthread/ip6.h` | IPv6 interface |
| `openthread/udp.h` | UDP sockets |
| `openthread/coap.h` | CoAP server/client |
| `openthread/dataset.h` | Network configuration |
| `openthread/error.h` | Error codes |
| `openthread/message.h` | Message buffers |
| `openthread_port.h` | Bouffalo SDK specific |

## References

- OpenThread API Version: 512
- Thread Version: 1.3/1.4
- Based on Bouffalo SDK OpenThread implementation
