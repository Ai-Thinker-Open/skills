# BL616/618 Thread Technical Documentation

## Overview

Thread is a low-power wireless mesh networking protocol based on IEEE 802.15.4, designed specifically for smart home and IoT devices. BL616/618 provides full Thread network functionality support through the integrated OpenThread protocol stack, enabling IPv6-addressable low-power mesh networking.

The Thread protocol stack operates in the 2.4 GHz band, supports mesh networks of up to 32 devices, with a theoretical transmission rate of up to 250 kbps. Unlike traditional point-to-point protocols, Thread supports self-organizing networks, self-healing, and large-scale device interconnection.

## Thread Technical Features

### 6LoWPAN Compression

Thread is based on the 6LoWPAN (IPv6 over Low-Power Wireless Personal Area Networks) protocol stack. Through header compression and fragmentation/reassembly techniques, it efficiently transmits IPv6 packets within the limited 802.15.4 frame size (127 bytes). This design allows Thread devices to communicate directly with the Internet without requiring additional gateway protocol translation.

### Native IPv6 Support

Thread devices obtain full IPv6 addresses and support native TCP/UDP transport layer protocols. This means developers can use standard socket APIs to develop IoT applications without worrying about low-level wireless communication details. The Thread network supports Thread 1.1/1.2/1.3 versions and is compatible with the Matter protocol stack.

### Mesh Network Topology

Thread uses a mesh network topology where all router devices can forward data to each other, allowing network coverage to scale linearly with the number of devices. Data packets are automatically routed through the optimal path by routing algorithms, with traffic automatically switching to backup paths in case of single point failures.

### Self-Healing Capability

When a router device leaves or fails in the network, the remaining routers automatically re-elect a leader, and new routers are promoted from EndDevices. The entire process requires no external intervention, and the network automatically restores connectivity. This self-healing mechanism gives Thread networks extremely high reliability.

## Thread vs BLE Mesh Comparison

| Feature | Thread | BLE Mesh |
|---------|--------|----------|
| Physical Layer | IEEE 802.15.4 | Bluetooth LE 4.x/5.x |
| Frequency Band | 2.4GHz | 2.4GHz |
| Transmission Rate | 250kbps | 1-2Mbps |
| Max Devices | 32 routers | 4096 nodes |
| IPv6 Support | Native | Requires conversion |
| Power Consumption | Low | Very low |
| Typical Application | Backbone network, controller | Low-power sensors |

Thread is suitable as a smart home backbone network, connecting controllers, gateways, and smart appliances that require continuous communication. BLE Mesh is better suited for low-power sensor nodes such as door/window sensors, temperature/humidity meters, etc.

## Core Concepts and Device Roles

### Leader

The Leader is the core router in a Thread network, responsible for managing the entire network domain. It maintains network configuration information, coordinates device onboarding, and assigns network addresses. The Leader can be automatically elected from any router, and when the original Leader fails, the network automatically re-elects.

### Router

Routers are responsible for forwarding network traffic, maintaining routing tables, and supporting child device onboarding. Routers have stable power supply and serve as backbone nodes of the network. Routers can be promoted to Leader or demoted to REED.

### EndDevice

EndDevices are leaf nodes that do not participate in routing and can only communicate with their parent device. EndDevices can enter deep sleep to save power, making them suitable for battery-powered devices. EndDevices cannot become Routers.

### REED (Router Eligible End Device)

A REED is an EndDevice with router eligibility. When the network needs more routers, REEDs can be promoted to Routers. BL616/618 joins the network as a REED by default and dynamically adjusts its role based on network topology requirements.

## OpenThread Platform Interface

BL616/618's Thread functionality is implemented through the OpenThread protocol stack, with the platform layer interface defined as follows:

### Initialization Functions

```c
// Initialize OpenThread protocol stack
void otrStackInit(void);

// Start OpenThread task
void otrStart(void);

// Get OpenThread instance
otInstance *otrGetInstance(void);

// User initialization callback (called in OpenThread task)
void otrInitUser(otInstance *instance);
```

### Radio Interface

```c
// Initialize 802.15.4 radio
void ot_radioInit(void);

// Radio event processing
void ot_radioTask(ot_system_event_t trxEvent);
```

### UART CLI Interface

```c
// Initialize OpenThread CLI (for debugging)
void otAppCliInit(otInstance *aInstance);

// Initialize NCP mode
void otAppNcpInit(otInstance *aInstance);
```

### System Events

```c
typedef enum _ot_system_event {
    OT_SYSTEM_EVENT_NONE                = 0,
    OT_SYSTEM_EVENT_OT_TASKLET          = 0x00000001,  // Tasklet event
    OT_SYSTEM_EVENT_ALARM_MS_EXPIRED    = 0x00000002,  // Millisecond timer
    OT_SYSTEM_EVENT_ALARM_US_EXPIRED    = 0x00000004,  // Microsecond timer
    OT_SYSTEM_EVENT_RADIO_TX_DONE       = 0x00000100,  // TX complete
    OT_SYSTEM_EVENT_RADIO_RX_DONE       = 0x00002000,  // RX complete
    OT_SYSTEM_EVENT_POLL                = 0x00010000,  // Data polling
    // ... more events
} ot_system_event_t;
```

## Code Examples

### Basic Initialization Flow

```c
#include "openthread_port.h"
#include <openthread/thread.h>
#include <openthread/instance.h>

// User initialization callback implementation
void otrInitUser(otInstance *instance) {
    // Set network name
    otThreadSetNetworkName(instance, "MyThreadNet");

    // Set PAN ID
    otLinkSetPanId(instance, 0x1234);

    // Set Extended PAN ID
    uint8_t extPanId[] = {0xdead, 0xbeef, 0xca, 0xfe, 0xba, 0xbe, 0xfa, 0xce};
    otThreadSetExtendedPanId(instance, extPanId);

    // Start Thread protocol stack
    otIp6SetEnabled(instance, true);
    otThreadSetEnabled(instance, true);

    printf("Thread network started\r\n");
}

void app_main(void) {
    // Initialize radio
    ot_radioInit();

    // Initialize OpenThread stack
    otrStackInit();

    // Start OpenThread task
    otrStart();
}
```

### Device Role Query

```c
void printDeviceRole(otInstance *instance) {
    otDeviceRole role = otThreadGetDeviceRole(instance);

    switch (role) {
        case OT_DEVICE_ROLE_DISABLED:
            printf("Role: Disabled\r\n");
            break;
        case OT_DEVICE_ROLE_DETACHED:
            printf("Role: Detached\r\n");
            break;
        case OT_DEVICE_ROLE_CHILD:
            printf("Role: EndDevice/REED\r\n");
            break;
        case OT_DEVICE_ROLE_ROUTER:
            printf("Role: Router\r\n");
            break;
        case OT_DEVICE_ROLE_LEADER:
            printf("Role: Leader\r\n");
            break;
    }
}
```

### Network Information Query

```c
void printNetworkInfo(otInstance *instance) {
    if (!otThreadGetDeviceRole(instance)) {
        return;
    }

    // Get RLOC16 (Routing Locator)
    uint16_t rloc16 = otThreadGetRloc16(instance);
    printf("RLOC16: 0x%04x\r\n", rloc16);

    // Get router count
    uint8_t routerCount = 0;
    otThreadGetRouterCount(instance, &routerCount);
    printf("Router Count: %d\r\n", routerCount);

    // Get Leader Router ID
    uint8_t leaderRouterId = otThreadGetLeaderRouterId(instance);
    printf("Leader Router ID: %d\r\n", leaderRouterId);

    // Get network name
    char name[32];
    otThreadGetNetworkName(instance, name, sizeof(name));
    printf("Network Name: %s\r\n", name);
}
```

## Configuration Parameters

### Task Configuration

```c
// OpenThread task stack size (default 1024)
#ifndef OT_TASK_SIZE
#define OT_TASK_SIZE 1024
#endif

// OpenThread task priority (default 20)
#ifndef OT_TASK_PRORITY
#define OT_TASK_PRORITY 20
#endif
```

### Radio Configuration

```c
// Number of receive frame buffers (default 8)
#ifndef OTRADIO_RX_FRAME_BUFFER_NUM
#define OTRADIO_RX_FRAME_BUFFER_NUM 8
#endif
```

### UART Configuration

```c
// UART receive buffer size (default 256)
#ifndef OT_UART_RX_BUFFSIZE
#define OT_UART_RX_BUFFSIZE 256
#endif
```

## Event-Driven Programming

OpenThread uses an event-driven model with the following main event types:

```c
// Process events in the main loop
void processThreadEvents(void) {
    ot_system_event_t event = otrGetEvents();

    if (event & OT_SYSTEM_EVENT_OT_TASKLET) {
        // Process OpenThread tasklet events
        otTaskletsProcess(otrGetInstance());
    }

    if (event & OT_SYSTEM_EVENT_RADIO_RX_DONE) {
        // Process receive complete event
    }

    if (event & OT_SYSTEM_EVENT_RADIO_TX_DONE) {
        // Process transmit complete event
    }
}
```

## Thread Network Security

Thread uses 802.15.4 secure frame encryption, supporting AES-128 encryption algorithm. Network security keys are distributed through the network provisioning process, and devices must pass pre-shared key or certificate authentication before joining the network.

Key security features:
- Frame-level encryption (AES-CCM-128)
- Device identity verification (KEK/MLEK keys)
- Periodic key rotation
- Security counters for replay attack prevention

## References

- [OpenThread Official Documentation](https://openthread.io/)
- [Thread Group Specification](https://www.threadgroup.org/)
- [BL618 OpenThread Source](../bouffalo_sdk/components/wireless/thread/openthread_port/)
- [Matter Protocol Integration](matter.md)
