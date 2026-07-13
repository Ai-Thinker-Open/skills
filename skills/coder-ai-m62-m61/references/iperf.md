# BL616/BL618 iperf Network Throughput Test Component

## Overview

iperf is a widely used network performance testing tool, primarily used to measure throughput of TCP and UDP protocols. The BL616/BL618 SDK integrates the iperf component so that developers can verify Wi-Fi communication performance in embedded environments. Through iperf testing, you can obtain key network metrics such as maximum upstream/downstream bandwidth, latency, and jitter, providing a performance reference basis for Wi-Fi application development.

On the BL616/BL618 platform, the iPerf component is implemented based on the lightweight TCP/IP protocol stack lwIP, supporting independent task running mode. The component provides a concise API interface; developers only need to configure necessary parameters to quickly start testing. Test results can be obtained through serial logs or callback functions, facilitating integration into automated testing systems.

## Header File

```c
#include "iperf.h"
```

## Key Constants

### IP Address Type

```c
#define IPERF_IP_TYPE_IPV4          0
#define IPERF_IP_TYPE_IPV6          1
```

iPerf supports both IPv4 and IPv6 address protocol families. IPv4 uses 32-bit addresses, IPv6 uses 128-bit addresses. IPv4 is the default; IPv6 is mainly used for next-generation network environment testing.

### Transport Protocol Type

```c
#define IPERF_TRANS_TYPE_TCP        0
#define IPERF_TRANS_TYPE_UDP        1
```

The transport layer protocol selection determines the data transmission method for the test. TCP provides reliable connections, suitable for testing actual throughput; UDP provides connectionless service, suitable for testing maximum packet loss rate and jitter performance.

### Run Mode Flags

```c
#define IPERF_FLAG_CLIENT           (1)
#define IPERF_FLAG_SERVER           (1 << 1)
#define IPERF_FLAG_TCP              (1 << 2)
#define IPERF_FLAG_UDP              (1 << 3)
#define IPERF_FLAG_DUAL             (1 << 4)
```

Flags are used to configure the iPerf run mode, and multiple modes can be combined via bitwise operations:

| Flag | Value | Description |
|------|-----|------|
| IPERF_FLAG_CLIENT | 0x01 | Client mode, initiates the test |
| IPERF_FLAG_SERVER | 0x02 | Server mode, receives test data |
| IPERF_FLAG_TCP | 0x04 | Uses TCP protocol for transport |
| IPERF_FLAG_UDP | 0x08 | Uses UDP protocol for transport |
| IPERF_FLAG_DUAL | 0x10 | Duplex mode, performs simultaneous send/receive testing |

### Default Configuration Parameters

```c
#define IPERF_DEFAULT_PORT          5001
#define IPERF_DEFAULT_INTERVAL      1
#define IPERF_DEFAULT_TIME          10
#define IPERF_DEFAULT_NO_BW_LIMIT   -1
```

| Parameter | Value | Description |
|------|-----|------|
| IPERF_DEFAULT_PORT | 5001 | Default listening/connection port |
| IPERF_DEFAULT_INTERVAL | 1 | Report interval, in seconds |
| IPERF_DEFAULT_TIME | 10 | Test duration, in seconds |
| IPERF_DEFAULT_NO_BW_LIMIT | -1 | No bandwidth limit |

### Task Configuration Parameters

```c
#define IPERF_TRAFFIC_TASK_NAME     "iperf_traffic"
#define IPERF_TRAFFIC_TASK_PRIORITY 10
#define IPERF_TRAFFIC_TASK_STACK    2048
```

iPerf uses an independent task to handle traffic transmission and reception. The task name is `iperf_traffic`, priority is 10 (relative value), and stack size is 2048 bytes.

### Buffer Length Configuration

```c
#define IPERF_UDP_TX_LEN            (1470)
#define IPERF_UDP_RX_LEN            (1470)
#define IPERF_TCP_TX_LEN            (4 << 10)
#define IPERF_TCP_RX_LEN            (4 << 10)
```

| Parameter | Value | Description |
|------|-----|------|
| IPERF_UDP_TX_LEN | 1470 | UDP transmit buffer, 1470 bytes conforms to MTU |
| IPERF_UDP_RX_LEN | 1470 | UDP receive buffer |
| IPERF_TCP_TX_LEN | 4096 | TCP transmit buffer, 4KB |
| IPERF_TCP_RX_LEN | 4096 | TCP receive buffer, 4KB |

UDP buffer is set to 1470 bytes, which is the optimal payload size considering the Ethernet MTU (1500 bytes) minus the IP header (20 bytes) and UDP header (8 bytes).

### Other Configuration Parameters

```c
#define IPERF_MAX_DELAY             64
#define IPERF_SOCKET_RX_TIMEOUT     10
#define IPERF_SOCKET_ACCEPT_TIMEOUT 5
```

| Parameter | Description |
|------|------|
| IPERF_MAX_DELAY | Maximum delay tolerance in UDP mode |
| IPERF_SOCKET_RX_TIMEOUT | Socket receive timeout |
| IPERF_SOCKET_ACCEPT_TIMEOUT | Server accept connection timeout |

## Flag Manipulation Macros

```c
#define IPERF_FLAG_SET(cfg, flag)   ((cfg) |= (flag))
#define IPERF_FLAG_CLR(cfg, flag)   ((cfg) &= (~(flag)))
```

These two macros are used to manipulate the flag field in the configuration structure:

- `IPERF_FLAG_SET(cfg, flag)`: Sets the flag bit in cfg to 1
- `IPERF_FLAG_CLR(cfg, flag)`: Clears the flag bit in cfg to 0

Usage example:

```c
iperf_cfg_t cfg;
cfg.flag = 0;

// Set to client mode, using TCP
IPERF_FLAG_SET(cfg.flag, IPERF_FLAG_CLIENT);
IPERF_FLAG_SET(cfg.flag, IPERF_FLAG_TCP);

// Clear UDP flag (if present)
IPERF_FLAG_CLR(cfg.flag, IPERF_FLAG_UDP);
```

## Configuration Structure

```c
typedef struct {
    uint32_t flag;
    union {
        uint32_t destination_ip4;
        char *destination_ip6;
    };
    union {
        uint32_t source_ip4;
        char *source_ip6;
    };
    uint8_t type;
    uint16_t dport;
    uint16_t sport;
    uint32_t interval;
    uint32_t time;
    uint16_t len_buf;
    int32_t bw_lim;
    uint8_t tos;
    uint8_t traffic_task_priority;
    uint32_t num_bytes;
} iperf_cfg_t;
```

| Field | Type | Description |
|------|------|------|
| flag | uint32_t | Run mode flag combination |
| destination_ip4 | uint32_t | Destination IPv4 address (network byte order) |
| destination_ip6 | char* | Destination IPv6 address string |
| source_ip4 | uint32_t | Source IPv4 address (network byte order) |
| source_ip6 | char* | Source IPv6 address string |
| type | uint8_t | IP address type, IPv4 or IPv6 |
| dport | uint16_t | Destination port number |
| sport | uint16_t | Source port number |
| interval | uint32_t | Report interval (seconds) |
| time | uint32_t | Test duration (seconds) |
| len_buf | uint16_t | Buffer length |
| bw_lim | int32_t | Bandwidth limit (-1 means no limit) |
| tos | uint8_t | Type of Service field |
| traffic_task_priority | uint8_t | Traffic task priority |
| num_bytes | uint32_t | Total number of bytes transferred |

## API Interface

### Start iperf Test

```c
int iperf_start(iperf_cfg_t *cfg);
```

**Parameter Description:**

- `cfg`: Pointer to the iperf_cfg_t configuration structure

**Return Value:**

- 0: Successfully started
- Negative: Start failed

**Function Description:**

Starts an iPerf test according to the configuration parameters. The test can run in client or server mode, TCP or UDP protocol. This function creates an independent traffic task to handle data transmission.

### Stop iperf Test

```c
int iperf_stop(void);
```

**Return Value:**

- 0: Successfully stopped
- Negative: Stop failed

**Function Description:**

Stops the running iPerf test and releases related resources.

## Client Mode

Client mode is used to actively initiate test requests to the iPerf server, measuring the network throughput from the local device to the server.

### Client Configuration Key Points

1. **Set client flag**: Configure `IPERF_FLAG_CLIENT` flag
2. **Specify destination address**: Set the server's IP address and port
3. **Select transport protocol**: TCP or UDP, based on testing needs
4. **Set test parameters**: Test duration, report interval, bandwidth limit, etc.

### TCP Client Example

```c
#include "iperf.h"
#include <stdint.h>

void iperf_tcp_client_example(void)
{
    iperf_cfg_t cfg;
    
    // Zero-initialize configuration structure
    memset(&cfg, 0, sizeof(cfg));
    
    // Set to client mode, using TCP
    cfg.flag = IPERF_FLAG_CLIENT | IPERF_FLAG_TCP;
    
    // Set destination IPv4 address (assuming 192.168.1.100)
    cfg.type = IPERF_IP_TYPE_IPV4;
    cfg.destination_ip4 = 0x6401A8C0;  // 192.168.1.100 in network byte order
    
    // Set port
    cfg.dport = IPERF_DEFAULT_PORT;  // 5001
    
    // Set test parameters
    cfg.interval = IPERF_DEFAULT_INTERVAL;  // 1 second
    cfg.time = IPERF_DEFAULT_TIME;          // 10 seconds
    
    // Set buffer
    cfg.len_buf = IPERF_TCP_TX_LEN;  // 4096 bytes
    
    // Set bandwidth limit (-1 means no limit)
    cfg.bw_lim = IPERF_DEFAULT_NO_BW_LIMIT;
    
    // Set task priority
    cfg.traffic_task_priority = IPERF_TRAFFIC_TASK_PRIORITY;
    
    // Start TCP client test
    int ret = iperf_start(&cfg);
    if (ret == 0) {
        printf("iPerf TCP client started\r\n");
    } else {
        printf("iPerf TCP client failed: %d\r\n", ret);
    }
}
```

### UDP Client Example

```c
void iperf_udp_client_example(void)
{
    iperf_cfg_t cfg;
    
    memset(&cfg, 0, sizeof(cfg));
    
    // Set to client mode, using UDP
    cfg.flag = IPERF_FLAG_CLIENT | IPERF_FLAG_UDP;
    
    // Set destination address
    cfg.type = IPERF_IP_TYPE_IPV4;
    cfg.destination_ip4 = 0x6401A8C0;  // 192.168.1.100
    
    // Set port
    cfg.dport = IPERF_DEFAULT_PORT;
    
    // Set test parameters
    cfg.interval = IPERF_DEFAULT_INTERVAL;
    cfg.time = IPERF_DEFAULT_TIME;
    
    // UDP buffer settings
    cfg.len_buf = IPERF_UDP_TX_LEN;  // 1470 bytes
    
    // Limit bandwidth to 10 Mbps
    cfg.bw_lim = 10000;
    
    // Set TOS
    cfg.tos = 0;
    
    // Start UDP client test
    int ret = iperf_start(&cfg);
    if (ret == 0) {
        printf("iPerf UDP client started\r\n");
    } else {
        printf("iPerf UDP client failed: %d\r\n", ret);
    }
}
```

## Server Mode

Server mode is used to receive test data from iPerf clients, passively waiting for connections and reporting receive performance.

### Server Configuration Key Points

1. **Set server flag**: Configure `IPERF_FLAG_SERVER` flag
2. **Bind port**: Set the local listening port
3. **Select protocol**: TCP requires accept connections, UDP directly receives data
4. **Configure reports**: Set report interval and duration

### TCP Server Example

```c
void iperf_tcp_server_example(void)
{
    iperf_cfg_t cfg;
    
    memset(&cfg, 0, sizeof(cfg));
    
    // Set to server mode, using TCP
    cfg.flag = IPERF_FLAG_SERVER | IPERF_FLAG_TCP;
    
    // Set local listening port
    cfg.dport = IPERF_DEFAULT_PORT;
    
    // Set report interval
    cfg.interval = IPERF_DEFAULT_INTERVAL;
    
    // Set buffer size
    cfg.len_buf = IPERF_TCP_RX_LEN;  // 4096 bytes
    
    // Start TCP server
    int ret = iperf_start(&cfg);
    if (ret == 0) {
        printf("iPerf TCP server started on port %d\r\n", IPERF_DEFAULT_PORT);
    } else {
        printf("iPerf TCP server failed: %d\r\n", ret);
    }
}
```

### UDP Server Example

```c
void iperf_udp_server_example(void)
{
    iperf_cfg_t cfg;
    
    memset(&cfg, 0, sizeof(cfg));
    
    // Set to server mode, using UDP
    cfg.flag = IPERF_FLAG_SERVER | IPERF_FLAG_UDP;
    
    // Set listening port
    cfg.dport = IPERF_DEFAULT_PORT;
    
    // Set report interval
    cfg.interval = IPERF_DEFAULT_INTERVAL;
    
    // UDP receive buffer
    cfg.len_buf = IPERF_UDP_RX_LEN;  // 1470 bytes
    
    // Start UDP server
    int ret = iperf_start(&cfg);
    if (ret == 0) {
        printf("iPerf UDP server started on port %d\r\n", IPERF_DEFAULT_PORT);
    } else {
        printf("iPerf UDP server failed: %d\r\n", ret);
    }
}
```

## Duplex Mode

Duplex (Dual) Mode allows simultaneous bidirectional testing, i.e., testing upstream bandwidth while testing downstream bandwidth.

```c
void iperf_dual_mode_example(void)
{
    iperf_cfg_t cfg;
    
    memset(&cfg, 0, sizeof(cfg));
    
    // Set duplex mode flags
    cfg.flag = IPERF_FLAG_CLIENT | IPERF_FLAG_TCP | IPERF_FLAG_DUAL;
    
    // Set destination address
    cfg.type = IPERF_IP_TYPE_IPV4;
    cfg.destination_ip4 = 0x6401A8C0;  // 192.168.1.100
    
    // Set port
    cfg.dport = IPERF_DEFAULT_PORT;
    
    // Test duration
    cfg.interval = IPERF_DEFAULT_INTERVAL;
    cfg.time = IPERF_DEFAULT_TIME;
    
    // Buffer
    cfg.len_buf = IPERF_TCP_TX_LEN;
    
    // No bandwidth limit
    cfg.bw_lim = IPERF_DEFAULT_NO_BW_LIMIT;
    
    // Start duplex test
    int ret = iperf_start(&cfg);
    if (ret == 0) {
        printf("iPerf dual mode started\r\n");
    }
}
```

## Relationship with Wi-Fi Throughput

iperf test results are closely related to Wi-Fi throughput performance. The following explains the main relationships:

### Theoretical Bandwidth vs Actual Throughput

Wi-Fi theoretical bandwidth depends on the protocol standard used:

| Wi-Fi Standard | Band | Max Theoretical Bandwidth | Typical Actual Throughput |
|------------|------|-------------|----------------|
| 802.11n | 2.4GHz | 600 Mbps | 200-400 Mbps |
| 802.11ac | 5GHz | 6.9 Gbps | 500-1000 Mbps |
| 802.11ax (Wi-Fi 6) | 2.4/5GHz | 9.6 Gbps | 600-1200 Mbps |

Actual throughput is typically 30%-70% of theoretical values, affected by many factors.

### Factors Affecting Throughput

1. **Signal Strength**: Lower RSSI values result in lower PHY rates and smaller throughput
2. **Interference Level**: Co-channel interference increases retransmissions, reducing effective throughput
3. **MCS Rate**: Different modulation and coding schemes affect PHY rate
4. **Frame Overhead**: 802.11 frame structure contains significant control overhead
5. **Window Size**: TCP/UDP window size affects transmission efficiency
6. **Fragmentation and Aggregation**: MSDU aggregation and MPDU aggregation affect efficiency

### Testing Recommendations

- **Test Environment**: Choose channels with less interference for baseline testing
- **Test Duration**: Each test should run at least 10 seconds to obtain stable averages
- **Protocol Selection**: TCP testing is suitable for evaluating actual available bandwidth, UDP testing is suitable for evaluating peak capability
- **Direction Selection**: Test upstream (device sending) and downstream (device receiving) performance separately
- **Packet Size**: Default 1470 bytes (UDP) or 4096 bytes (TCP) yields optimal performance

### Performance Evaluation Metrics

| Metric | Description | Evaluation Point |
|------|------|----------|
| Throughput | Amount of data transferred per unit time | Higher is better |
| Jitter | Variation range of UDP packet latency | Lower is more stable |
| Packet Loss Rate | Proportion of lost packets in UDP transmission | Lower is more reliable |
| Latency | Time from data send to receive | Lower means faster response |

## Typical Application Scenarios

### Scenario 1: Wi-Fi Connection Performance Verification

After the device successfully connects to a Wi-Fi network, use iperf for throughput verification:

```c
void wifi_performance_test(void)
{
    // Assume Wi-Fi is already connected
    printf("Starting Wi-Fi performance test...\r\n");
    
    // Start server to receive test first
    iperf_cfg_t server_cfg;
    memset(&server_cfg, 0, sizeof(server_cfg));
    server_cfg.flag = IPERF_FLAG_SERVER | IPERF_FLAG_TCP;
    server_cfg.dport = IPERF_DEFAULT_PORT;
    server_cfg.interval = IPERF_DEFAULT_INTERVAL;
    server_cfg.len_buf = IPERF_TCP_RX_LEN;
    iperf_start(&server_cfg);
    
    // Wait for server to start
    vTaskDelay(pdMS_TO_TICKS(500));
    
    // Start client to initiate test
    iperf_cfg_t client_cfg;
    memset(&client_cfg, 0, sizeof(client_cfg));
    client_cfg.flag = IPERF_FLAG_CLIENT | IPERF_FLAG_TCP;
    client_cfg.type = IPERF_IP_TYPE_IPV4;
    client_cfg.destination_ip4 = 0x0100007F;  // 127.0.0.1 or server IP
    client_cfg.dport = IPERF_DEFAULT_PORT;
    client_cfg.interval = IPERF_DEFAULT_INTERVAL;
    client_cfg.time = IPERF_DEFAULT_TIME;
    client_cfg.len_buf = IPERF_TCP_TX_LEN;
    client_cfg.bw_lim = IPERF_DEFAULT_NO_BW_LIMIT;
    iperf_start(&client_cfg);
    
    // Wait for test to complete
    vTaskDelay(pdMS_TO_TICKS(client_cfg.time * 1000 + 2000));
    
    printf("Performance test completed\r\n");
}
```

### Scenario 2: Performance Comparison at Different Distances

In the same network environment, evaluate the impact of coverage range on throughput by varying the distance between device and AP:

```c
void range_performance_test(const char *server_ip)
{
    iperf_cfg_t cfg;
    memset(&cfg, 0, sizeof(cfg));
    
    cfg.flag = IPERF_FLAG_CLIENT | IPERF_FLAG_UDP;
    cfg.type = IPERF_IP_TYPE_IPV4;
    cfg.destination_ip4 = ipaddr_aton(server_ip);
    cfg.dport = IPERF_DEFAULT_PORT;
    cfg.interval = IPERF_DEFAULT_INTERVAL;
    cfg.time = 5;  // Short test
    cfg.len_buf = IPERF_UDP_TX_LEN;
    
    // Simulate different distance performance with different bandwidth limits
    int bandwidths[] = {50000, 20000, 10000, 5000};  // 50/20/10/5 Mbps
    
    for (int i = 0; i < 4; i++) {
        cfg.bw_lim = bandwidths[i];
        printf("Testing with bandwidth limit: %d Kbps\r\n", bandwidths[i]);
        iperf_start(&cfg);
        vTaskDelay(pdMS_TO_TICKS(6000));
    }
}
```

### Scenario 3: Continuous Stress Testing

Observe throughput stability by running iperf tests for extended periods:

```c
void stress_test_example(const char *server_ip)
{
    iperf_cfg_t cfg;
    memset(&cfg, 0, sizeof(cfg));
    
    cfg.flag = IPERF_FLAG_CLIENT | IPERF_FLAG_TCP;
    cfg.type = IPERF_IP_TYPE_IPV4;
    cfg.destination_ip4 = ipaddr_aton(server_ip);
    cfg.dport = IPERF_DEFAULT_PORT;
    cfg.interval = IPERF_DEFAULT_INTERVAL;
    cfg.time = 60;  // 1 minute test
    cfg.len_buf = IPERF_TCP_TX_LEN;
    cfg.bw_lim = IPERF_DEFAULT_NO_BW_LIMIT;
    
    printf("Starting 60-second stress test...\r\n");
    iperf_start(&cfg);
}
```

## Notes

### Firewall Configuration

Before running iPerf tests, ensure the test device's firewall allows inbound and outbound traffic on port 5001. For Linux systems, you can use the following command:

```bash
# Open port 5001
sudo ufw allow 5001
```

### Network Compatibility

- Ensure both ends of the test (device and PC) are connected to the same network or mutually reachable networks
- IPv6 testing requires network environment support for the IPv6 protocol stack
- Cross-NAT testing requires port mapping configuration

### Resource Usage

The iPerf traffic task occupies certain CPU and memory resources:

- Task stack: 2048 bytes
- Buffers: TCP mode 4KB × 2, UDP mode 1470 bytes × 2
- CPU overhead: Mainly consumed in data copying and protocol processing

### Error Handling

```c
int ret = iperf_start(&cfg);
if (ret < 0) {
    switch (ret) {
        case -1:
            printf("Invalid configuration\r\n");
            break;
        case -2:
            printf("Socket creation failed\r\n");
            break;
        case -3:
            printf("Task creation failed\r\n");
            break;
        default:
            printf("Unknown error: %d\r\n", ret);
            break;
    }
}
```

## References

- Bouffalo SDK iperf component source: `components/iperf/iperf.h`
- lwIP TCP/IP protocol stack documentation
- IETF RFC 9000 (QUIC protocol definition)
- Wi-Fi Alliance 802.11 standard documentation
