# NetHub Network Filtering Framework

## Overview

NetHub is the core network framework for the Bouffalo Lab BL616/BL618 chip series, providing complete streaming server capabilities with support for RTSP, HTTP-FLV, HLS, and other streaming media protocols. One of its core features is intelligent Wi-Fi packet filtering and distribution, using a configurable policy engine to classify and process received packets, deciding whether packets should be dropped, delivered to the local protocol stack, forwarded to the Host processor, or a combination of these.

NetHub's filtering system is located in the `components/net/nethub/core/` directory, where `nh_filter.h` defines the complete filtering data structures and API. The Wi-Fi backend implementation resides under `backend/wifi/`, containing the bridge layer and common backend interfaces. Host-side transport support is implemented via the SDIO transport layer under directories like `backend/host/sdio/`.

## Core Data Types

### Filter Match Type `nh_filter_match_t`

Packet match type enumeration, defining recognized protocols and port ranges:

```c
typedef enum {
    NH_FILTER_MATCH_8021X = 0,      // 802.1X authentication frame
    NH_FILTER_MATCH_ARP,            // ARP protocol
    NH_FILTER_MATCH_DHCP4,          // IPv4 DHCP Dynamic Host Configuration Protocol
    NH_FILTER_MATCH_ICMP4,          // IPv4 ICMP control message protocol
    NH_FILTER_MATCH_TCP4_DST_PORT_RANGE,  // TCP IPv4 destination port range
    NH_FILTER_MATCH_UDP4_DST_PORT_RANGE,  // UDP IPv4 destination port range
} nh_filter_match_t;
```

When the match type is `TCP4_DST_PORT_RANGE` or `UDP4_DST_PORT_RANGE`, the `port_min` and `port_max` fields must be specified in the rule structure to define the port range. The framework uses these fields to determine if an incoming packet's destination port falls within the specified range.

### Filter Action Type `nh_filter_action_t`

Filter actions determine how matched packets should be handled:

```c
#define NH_FILTER_ACTION_DROP  NETHUB_WIFI_RX_FILTER_DROP   // Drop packet
#define NH_FILTER_ACTION_LOCAL NETHUB_WIFI_RX_FILTER_LOCAL   // Deliver to local stack only
#define NH_FILTER_ACTION_HOST  NETHUB_WIFI_RX_FILTER_HOST    // Forward to Host only
#define NH_FILTER_ACTION_BOTH  NETHUB_WIFI_RX_FILTER_BOTH    // Deliver to both local and Host
```

`NH_FILTER_ACTION_BOTH` is a combined action, defined as `LOCAL | HOST` (bitwise OR), meaning the packet should be processed by the local protocol stack (e.g., lwIP) and also forwarded to the Host processor via channels like SDIO.

### Filter Rule Structure `nh_filter_rule_t`

Each filter rule consists of a match condition, an action, and optional parameters:

```c
typedef struct {
    nh_filter_match_t match;     // Match type
    nh_filter_action_t action;   // Action to perform on match
    uint16_t port_min;           // Lower bound of port range (valid only for port range matches)
    uint16_t port_max;           // Upper bound of port range (valid only for port range matches)
} nh_filter_rule_t;
```

For non-port-related match types (such as ARP, DHCP4), the `port_min` and `port_max` fields are ignored.

### Filter Policy Structure `nh_filter_policy_t`

A policy is a collection of rules and a default action:

```c
typedef struct {
    const nh_filter_rule_t *rules;      // Pointer to rule array
    size_t rule_count;                  // Number of rules
    nh_filter_action_t default_action;  // Default action when no rule matches
} nh_filter_policy_t;
```

When a packet does not match any rule, `default_action` specifies the default handling. Policies are created at system initialization and referenced during the packet processing flow.

## Channel Types

NetHub defines multiple data channels to distinguish different data sources and destinations:

```c
typedef enum {
    NETHUB_CHANNEL_WIFI_STA = 0,   // Wi-Fi Station mode receive channel
    NETHUB_CHANNEL_WIFI_AP,         // Wi-Fi AP mode receive channel
    NETHUB_CHANNEL_STACK_STA,       // Local stack Station channel
    NETHUB_CHANNEL_STACK_AP,        // Local stack AP channel
    NETHUB_CHANNEL_STACK_NAT,       // Local stack NAT channel
    NETHUB_CHANNEL_BRIDGE,          // Bridge channel
    NETHUB_CHANNEL_SDIO,            // SDIO transport channel
    NETHUB_CHANNEL_USB,             // USB transport channel
    NETHUB_CHANNEL_SPI,             // SPI transport channel
    NETHUB_CHANNEL_MAX
} nethub_channel_t;
```

Packets received on Wi-Fi channels (STA and AP) are first processed by the filter policy, then distributed to the local protocol stack or Host side based on the filter result.

## Core API

### `nh_filter_wifi_rx()`

Entry function for Wi-Fi receive packets, applying the currently registered filter policy to the packet:

```c
nh_filter_action_t nh_filter_wifi_rx(nethub_channel_t src_channel, const struct pbuf *pkt);
```

**Parameters:**
- `src_channel`: Source channel of the packet (`NETHUB_CHANNEL_WIFI_STA` or `NETHUB_CHANNEL_WIFI_AP`)
- `pkt`: Pointer to the lwIP `pbuf` structure containing the packet

**Returns:**
- Filter action of type `nh_filter_action_t`, indicating how the packet should be handled

This function is the core processing point on the Wi-Fi RX data path, responsible for parsing packet protocol layers and applying filter rules.

### `nh_filter_apply_policy()`

Explicitly apply a filter policy to a specified packet:

```c
nh_filter_action_t nh_filter_apply_policy(const struct pbuf *pkt, const nh_filter_policy_t *policy);
```

**Parameters:**
- `pkt`: Pointer to the `pbuf` of the packet to process
- `policy`: Pointer to the filter policy structure to apply

**Returns:**
- The action corresponding to the matched rule, or the policy's `default_action` (if no match)

This function allows the application layer to dynamically switch filter policies at runtime, suitable for scenarios requiring different network behavior adjustments.

### `nh_filter_should_deliver_local()`

Determine if the filter action includes local delivery:

```c
bool nh_filter_should_deliver_local(nh_filter_action_t action);
```

**Returns:**
- `true`: Action includes the `LOCAL` flag, needs local stack delivery
- `false`: Action does not include the `LOCAL` flag

### `nh_filter_should_deliver_host()`

Determine if the filter action includes Host forwarding:

```c
bool nh_filter_should_deliver_host(nh_filter_action_t action);
```

**Returns:**
- `true`: Action includes the `HOST` flag, needs forwarding to Host
- `false`: Action does not include the `HOST` flag

These two decision functions are typically used together in the packet processing flow to determine the final routing of packets. For example, the action `NH_FILTER_ACTION_BOTH` returns `true` for both functions.

### `nh_filter_custom_wifi_rx_is_active()`

Query whether a custom Wi-Fi filter callback is currently registered:

```c
bool nh_filter_custom_wifi_rx_is_active(void);
```

**Returns:**
- `true`: Custom filter callback registered via `nethub_set_wifi_rx_filter()`
- `false`: Using the built-in default filter policy

When a custom filter callback is active, the built-in filter policy is completely bypassed.

### `nethub_set_wifi_rx_filter()`

Register a custom Wi-Fi filter callback function:

```c
int nethub_set_wifi_rx_filter(nethub_wifi_rx_filter_cb_t filter_cb, void *user_ctx);
```

**Callback function type definition:**

```c
typedef nethub_wifi_rx_filter_action_t (*nethub_wifi_rx_filter_cb_t)(
    nethub_channel_t src_channel,
    const struct pbuf *pkt,
    void *user_ctx);
```

**Important constraints:**
- This function must be called before `nethub_bootstrap()`
- The callback runs on the Wi-Fi RX critical path and must meet the following requirements:
  - Must not block or sleep
  - Must not free, retain, or modify `pkt`
  - Must not assume the entire frame is contiguous memory (pbuf may be a chain)
- Passing `NULL` restores the built-in policy

## Wi-Fi Backend Interfaces

### `nh_wifi_backend_init()`

Initialize the Wi-Fi backend module:

```c
int nh_wifi_backend_init(void);
```

**Returns:**
- `0` or `NETHUB_OK`: Initialization successful
- Negative: Initialization failed

### `nh_wifi_backend_tx()`

Send a packet via the Wi-Fi backend:

```c
nh_wifi_backend_tx_result_t nh_wifi_backend_tx(struct pbuf *p, bool is_sta);
```

**Parameters:**
- `p`: Packet to send
- `is_sta`: `true` to send via Station interface, `false` to send via AP interface

**Returns:**
- `NH_WIFI_BACKEND_TX_OK`: Send successful
- `NH_WIFI_BACKEND_TX_ERR_SEND`: Send failed
- `NH_WIFI_BACKEND_TX_ERR_NETIF_DOWN`: Network interface not ready

### `nh_wifi_bridge_handle_rx()`

Common bridge RX processing path for all Wi-Fi backend implementations:

```c
struct pbuf *nh_wifi_bridge_handle_rx(bool is_sta, struct pbuf *p);
```

This function encapsulates the complete processing flow from Wi-Fi driver to protocol stack or Host, including filter policy application and distribution decisions.

### Wi-Fi Endpoint Operation Interfaces

Wi-Fi endpoints define operation interfaces related to specific hardware:

```c
const struct nhif_ops *nh_wifi_endpoint_get_ops(size_t index);
size_t nh_wifi_endpoint_get_count(void);
```

Obtain the corresponding operation function set by endpoint index, supporting multiple Wi-Fi hardware configurations.

## SDIO Transport Layer

The SDIO channel is one of the primary communication paths between BL616/BL618 and the Host processor:

```c
extern const struct nhif_ops nhsdio_ops;
extern const nh_ctrlpath_ops_t nhsdio_ctrlpath_ops;
```

These operation interfaces are exported by `transport_sdio.h`, providing data transport and control plane capabilities for the SDIO channel.

## Runtime Status

NetHub provides runtime status query interfaces:

```c
typedef struct {
    bool initialized;                      // Whether the framework is initialized
    bool started;                           // Whether the framework is started
    bool custom_wifi_rx_filter_active;     // Whether custom filter callback is active
    const char *profile_name;               // Current configuration file name
    nethub_channel_t host_channel;          // Host channel
    nethub_channel_t active_wifi_channel;   // Currently active Wi-Fi channel
    nethub_statistics_t statistics;         // Traffic statistics
} nethub_runtime_status_t;
```

Statistics include packet counts, drop counts, and successful transmission counts for both download (dnld) and upload (upld) directions.

## Code Examples

### Filter Policy Initialization

The following example shows how to initialize a basic filter policy that allows DHCP, ARP, and ICMP through, forwards common media port traffic to the Host, and drops other traffic by default:

```c
#include "nh_filter.h"

// Define filter rules
static const nh_filter_rule_t my_rules[] = {
    // Allow DHCP traffic delivered locally (for IP address acquisition)
    {
        .match = NH_FILTER_MATCH_DHCP4,
        .action = NH_FILTER_ACTION_LOCAL,
    },
    // Allow ARP traffic delivered locally (for ARP resolution)
    {
        .match = NH_FILTER_MATCH_ARP,
        .action = NH_FILTER_ACTION_LOCAL,
    },
    // Allow ICMP traffic delivered locally (for ping testing)
    {
        .match = NH_FILTER_MATCH_ICMP4,
        .action = NH_FILTER_ACTION_LOCAL,
    },
    // Forward HTTP/RTSP and other media port traffic to Host
    {
        .match = NH_FILTER_MATCH_TCP4_DST_PORT_RANGE,
        .action = NH_FILTER_ACTION_HOST,
        .port_min = 80,
        .port_max = 554,  // HTTP to RTSP port range
    },
    // Forward RTMP streaming port to Host
    {
        .match = NH_FILTER_MATCH_TCP4_DST_PORT_RANGE,
        .action = NH_FILTER_ACTION_HOST,
        .port_min = 1935,
        .port_max = 1935,  // RTMP default port
    },
    // Forward HTTP-FLV port to Host
    {
        .match = NH_FILTER_MATCH_TCP4_DST_PORT_RANGE,
        .action = NH_FILTER_ACTION_HOST,
        .port_min = 8080,
        .port_max = 8080,
    },
};

// Create filter policy
static const nh_filter_policy_t my_policy = {
    .rules = my_rules,
    .rule_count = sizeof(my_rules) / sizeof(my_rules[0]),
    .default_action = NH_FILTER_ACTION_DROP,  // Default drop unmatched traffic
};

// Function to apply the policy
void apply_my_policy(void) {
    nh_filter_action_t action;
    struct pbuf *pkt = NULL;  // Assume this is a received packet

    // Apply filter policy to the packet
    action = nh_filter_apply_policy(pkt, &my_policy);

    // Decide routing based on action
    if (nh_filter_should_deliver_local(action)) {
        // Deliver to local lwIP protocol stack
    }
    if (nh_filter_should_deliver_host(action)) {
        // Forward to Host via SDIO or other channels
    }
}
```

### Custom Wi-Fi Filter Callback Registration

When the built-in policy cannot meet requirements, a custom filter callback can be registered. The following example shows a simple custom filter that determines handling based on the packet's protocol type and source channel:

```c
#include "nethub_filter.h"
#include "lwip/pbuf.h"

// Custom user context
typedef struct {
    bool debug_enabled;
    uint32_t dropped_count;
} my_filter_ctx_t;

static my_filter_ctx_t g_my_ctx = {
    .debug_enabled = true,
    .dropped_count = 0,
};

// Custom filter callback implementation
static nethub_wifi_rx_filter_action_t my_wifi_filter(
    nethub_channel_t src_channel,
    const struct pbuf *pkt,
    void *user_ctx) {

    my_filter_ctx_t *ctx = (my_filter_ctx_t *)user_ctx;

    if (ctx == NULL || pkt == NULL) {
        return NH_FILTER_ACTION_DROP;
    }

    // Simplified logic: assume all DHCP traffic needs local handling
    // Actual implementation needs to parse protocol headers in pbuf
    nethub_wifi_rx_filter_action_t result = NH_FILTER_ACTION_DROP;

    // Determine behavior based on source channel
    switch (src_channel) {
        case NETHUB_CHANNEL_WIFI_STA:
            // In STA mode, forward all traffic to Host
            result = NH_FILTER_ACTION_HOST;
            break;
        case NETHUB_CHANNEL_WIFI_AP:
            // In AP mode, only forward media port traffic to Host
            result = NH_FILTER_ACTION_LOCAL;
            break;
        default:
            result = NH_FILTER_ACTION_DROP;
            break;
    }

    return result;
}

// Initialize custom filtering
int init_custom_filter(void) {
    int ret;

    // Register custom filter callback (must be called before nethub_bootstrap)
    ret = nethub_set_wifi_rx_filter(my_wifi_filter, &g_my_ctx);
    if (ret != 0) {
        return ret;
    }

    // Check if registration was successful
    if (nh_filter_custom_wifi_rx_is_active()) {
        // Custom filter is active
    }

    return 0;
}
```

### Wi-Fi Packet Receive and Filter Processing

Complete Wi-Fi RX processing flow example:

```c
#include "nh_wifi_backend.h"
#include "nh_filter.h"

// Wi-Fi receive handler
void handle_wifi_rx(bool is_sta, struct pbuf *p) {
    nh_filter_action_t action;

    if (p == NULL) {
        return;
    }

    // Get source channel
    nethub_channel_t src_channel = is_sta ?
        NETHUB_CHANNEL_WIFI_STA : NETHUB_CHANNEL_WIFI_AP;

    // Apply filter policy
    action = nh_filter_wifi_rx(src_channel, p);

    // Handle packet based on filter result
    if (nh_filter_should_deliver_local(action)) {
        // Deliver to local network protocol stack
        // Pass to lwIP via bridge function
        struct pbuf *local_pkt = p;
        // nh_wifi_bridge_handle_rx handles local delivery
    }

    if (nh_filter_should_deliver_host(action)) {
        // Forward to Host processor
        // Send via SDIO or other channels
        nh_wifi_backend_tx_result_t tx_result;
        tx_result = nh_wifi_backend_tx(p, is_sta);

        if (tx_result != NH_WIFI_BACKEND_TX_OK) {
            // Handle send failure
        }
    }

    // If action is DROP, packet is naturally not processed here, pbuf will be freed
}
```

## Filter Policy Design Recommendations

### Policy Order

The order of rules in the array matters — the framework traverses rules sequentially and returns the first matching result. Therefore, place the most frequently used rules at the beginning of the array to improve processing efficiency.

### Port Range Matching

For TCP/UDP port range matching, plan `port_min` and `port_max` values appropriately:

- Single port: set `port_min == port_max`
- Contiguous port segment: set range boundaries
- Non-contiguous ports: require multiple rules

### Default Action Selection

The choice of default action depends on the specific application scenario:

- `NH_FILTER_ACTION_DROP`: High-security scenarios, only allow explicitly specified traffic through
- `NH_FILTER_ACTION_LOCAL`: All traffic needs local processing, Host only for monitoring
- `NH_FILTER_ACTION_HOST`: Local only for forwarding, most processing done on Host
- `NH_FILTER_ACTION_BOTH`: Scenarios requiring simultaneous local and Host processing

### Performance Considerations

Filter callbacks run on the Wi-Fi RX critical path and should avoid:

- Dynamic memory allocation
- Complex protocol parsing (use fast field extraction)
- Lock contention and blocking calls

## Error Codes

NetHub defines the following error codes:

```c
typedef enum {
    NETHUB_OK = 0,
    NETHUB_ERR_INVALID_PARAM = -1,      // Invalid parameter
    NETHUB_ERR_NOT_FOUND = -2,          // Requested resource not found
    NETHUB_ERR_ALREADY_EXISTS = -3,    // Resource already exists
    NETHUB_ERR_NO_MEMORY = -4,         // Out of memory
    NETHUB_ERR_NOT_INITIALIZED = -5,   // Not initialized
    NETHUB_ERR_INVALID_STATE = -6,     // Invalid state
    NETHUB_ERR_INTERNAL = -7,          // Internal error
    NETHUB_ERR_NOT_SUPPORTED = -8,     // Operation not supported
} nethub_status_t;
```

## References

- [BL618Claw Bouffalo SDK](https://github.com/bouffalolab/bl_mcu_sdk)
- `components/net/nethub/core/nh_filter.h` — Filter core API definitions
- `components/net/nethub/backend/wifi/nh_wifi_bridge.h` — Wi-Fi bridge interface
- `components/net/nethub/backend/wifi/nh_wifi_backend.h` — Wi-Fi backend interface
- `components/net/nethub/backend/host/sdio/transport_sdio.h` — SDIO transport layer definitions
- `components/net/nethub/include/nethub_filter.h` — Filter callback and action types
- `components/net/nethub/include/nethub_defs.h` — Channel and status type definitions
