# Netbus Framework Documentation (BL616/BL618)

## Overview

The **Netbus** framework is a comprehensive AT command-based networking framework for Bouffalo Lab BL616/BL618 chips. It provides:

- AT command interpretation and execution
- UART/WiFi transparent transmission bridge
- Network socket client/server support (TCP/UDP/SSL)
- Multiple transport layers (UART, USB, SPI, TTY)

---

## Architecture

```
┌─────────────────────────────────────────────────────┐
│                   Application                        │
├─────────────────────────────────────────────────────┤
│                   AT Module                          │
│  ┌─────────────┐  ┌──────────────┐  ┌────────────┐  │
│  │ at_main.c  │  │  at_core.c   │  │at_through.c│  │
│  │ - init     │  │ - cmd parse  │  │- bridge    │  │
│  │ - task     │  │ - dispatch  │  │- transfer  │  │
│  └─────────────┘  └──────────────┘  └────────────┘  │
├─────────────────────────────────────────────────────┤
│              AT Commands (at_net/)                   │
│  ┌──────────────┐ ┌─────────────┐ ┌──────────────┐  │
│  │ CIPSTART     │ │ CIPSEND    │ │ CIPCLOSE    │  │
│  │ (TCP/UDP)    │ │ (send data)│ │ (close)     │  │
│  └──────────────┘ └─────────────┘ └──────────────┘  │
├─────────────────────────────────────────────────────┤
│              Transport Layer                         │
│  ┌─────────────┐ ┌──────────────┐ ┌──────────────┐  │
│  │ UART        │ │ USB          │ │ SPI Sync    │  │
│  │ netbus_uart │ │ netbus_usbd  │ │ spisync     │  │
│  └─────────────┘ └──────────────┘ └──────────────┘  │
├─────────────────────────────────────────────────────┤
│              Network Stack (LwIP)                    │
└─────────────────────────────────────────────────────┘
```

---

## Core Data Structures

### at_main.h - Core AT Structure

```c
// Work modes
typedef enum {
    AT_WORK_MODE_CMD = 0x00,      // Normal AT command mode
    AT_WORK_MODE_THROUGHPUT,      // Transparent UART-WiFi mode
    AT_WORK_MODE_CMD_THROUGHPUT   // Mixed mode
} at_work_mode;

// Device operations (UART/USB transport)
typedef struct {
    int (*init_device)(void);
    int (*deinit_device)(void);
    int (*read_data) (uint8_t *data, int len);
    int (*write_data) (uint8_t *data, int len);
    int (*f_output_redirect) (void);
} at_device_ops;

// Main AT structure
struct at_struct {
    uint8_t initialized;
    uint8_t echo;
    uint8_t syslog;
    uint8_t store;
    uint8_t fakeoutput;
    uint8_t exit;
    at_work_mode incmd;           // Current work mode
    at_device_ops device_ops;      // Transport callbacks
    int function_num;
    at_function_ops function_ops[AT_CMD_MAX_FUNC];
    const at_cmd_struct *commands[AT_CMD_MAX_NUM];
    int num_commands;
    char *inbuf;                  // Input buffer
};

extern struct at_struct *at;      // Global AT instance
```

### AT Command Structure

```c
typedef struct {
    char *at_name;                         // Command name (e.g., "+CIPSTART")
    int (*at_query_cmd)(int argc, const char **argv);  // AT+XXX? query
    int (*at_setup_cmd)(int argc, const char **argv);  // AT+XXX=param setup
    int (*at_exe_cmd)(int argc, const char **argv);    // AT+XXX execute
    uint16_t para_num_min;                 // Min parameters
    uint16_t para_num_max;                 // Max parameters
} at_cmd_struct;
```

---

## 1. AT Module Initialization

### Header Files

```c
#include "at_main.h"
#include "at_core.h"
#include "at_port.h"
#include "at_pal.h"
```

### Initialization Code

```c
#include "at_main.h"
#include "at_core.h"
#include "at_port.h"
#include "at_pal.h"

// AT module must be initialized before use
int at_module_init(void)
{
    int ret = -1;

    if (at) {
        printf("ERROR: atcmd has been initialized\r\n");
        return -1;
    }

    // Allocate AT structure
    at = (struct at_struct *)at_malloc(sizeof(struct at_struct));
    if (at == NULL) {
        return -1;
    }

    memset((void *)at, 0, sizeof(struct at_struct));
    at->initialized = 0;
    at->echo = 0;
    at->syslog = 0;
    at->store = 1;
    at->exit = 0;
    at->incmd = AT_WORK_MODE_CMD;

    // Setup device operations (UART transport)
    at->device_ops.init_device = at_port_init;
    at->device_ops.deinit_device = at_port_deinit;
    at->device_ops.read_data = at_port_read_data;
    at->device_ops.write_data = at_port_write_data;

    // Initialize UART hardware
    ret = at->device_ops.init_device();
    if (ret < 0) {
        printf("ERROR: init at cmd device failed, ret = %d\r\n", ret);
        goto INIT_ERROR;
    }

    // Register command sets
#ifdef CONFIG_ATMODULE_NETWORK
    at_net_cmd_regist();       // Network commands (CIPSTART, CIPSEND, etc.)
#endif
#ifdef CONFIG_ATMODULE_FS
    at_fs_register();          // File system commands
#endif

    at_base_cmd_regist();      // Base commands (AT, AT+GMR, etc.)
    at_user_cmd_regist();      // User-defined commands
    at_wifi_cmd_regist();      // WiFi commands
#ifdef CONFIG_ATMODULE_MQTT
    at_mqtt_cmd_regist();
#endif
#ifdef CONFIG_ATMODULE_HTTP
    at_http_cmd_regist();
#endif
#ifdef CONFIG_ATMODULE_BLUETOOTH
    at_ble_cmd_regist();
#endif

    // Create AT command task (FreeRTOS)
    ret = xTaskCreate(at_main_task, (char*)"at_main_task",
                      ATCMD_TASK_STACK_SIZE, NULL,
                      ATCMD_TASK_PRIORITY, NULL);
    if (ret != pdPASS) {
        printf("ERROR: create at_main_task failed\r\n");
        goto INIT_ERROR;
    }

    at->initialized = 1;
    return 0;

INIT_ERROR:
    if (at) {
        at_free(at);
        at = NULL;
    }
    return -1;
}
```

### UART Port Implementation (at_port_uart.c)

```c
#include "netbus_uart.h"

static const netbus_uart_config_t uart_config = {
    .name = "uart1",
    .speed = 2000000,      // 2Mbps baud rate
    .databits = 8,
    .stopbits = 1,
    .parity = 0,
    .flow_control = 0,
};

static netbus_uart_ctx_t at_uart;

int at_port_init(void)
{
    // Initialize UART with 1KB tx/rx stream buffers
    netbus_uart_init(&at_uart, &uart_config, 1024, 1024);
    return 1;
}

int at_port_read_data(uint8_t *data, int len)
{
    // Blocking read from UART stream buffer
    return netbus_uart_receive(&at_uart, data, len, portMAX_DELAY);
}

int at_port_write_data(uint8_t *data, int len)
{
    return netbus_uart_send(&at_uart, data, len, 10000); // 10s timeout
}
```

### Deinitialization

```c
int at_module_deinit(void)
{
    if (!at) {
        return -1;
    }

    at->exit = 1;
    vTaskDelay(1000);  // Wait for task to exit

    at->device_ops.deinit_device();
    at_free(at);
    at = NULL;
    return 0;
}
```

---

## 2. AT Command Bridge Mode

The **AT Command Bridge Mode** allows the device to act as a transparent bridge between UART and WiFi socket connections.

### Network Commands

| Command | Description |
|---------|-------------|
| `AT+CIPSTART` | Establish TCP/UDP connection |
| `AT+CIPSEND` | Send data in command mode |
| `AT+CIPSENDL` | Send fixed-length data with progress reporting |
| `AT+CIPCLOSE` | Close connection |
| `AT+CIFSR` | Get IP address |

### Establishing a Connection (CIPSTART)

```c
// Example: TCP connection
// AT+CIPSTART=0,"TCP","192.168.1.100",8080

static int at_setup_cmd_cipstart(int argc, const char **argv)
{
    int linkid = 0;
    char type[8];  // "TCP", "UDP", "SSL"
    char ip[64];
    int port;
    int ret;

    // Parse: linkid, type, remote_ip, port
    AT_CMD_PARSE_NUMBER(0, &linkid);
    AT_CMD_PARSE_STRING(1, type, sizeof(type));
    AT_CMD_PARSE_STRING(2, ip, sizeof(ip));
    AT_CMD_PARSE_NUMBER(3, &port);

    // Create socket based on type
    if (strcmp(type, "TCP") == 0) {
        ret = tcp_client_connect(ipaddr, port, timeout);
    } else if (strcmp(type, "UDP") == 0) {
        ret = udp_client_create(ipaddr, port);
    }

    if (ret >= 0) {
        at_response_string("CONNECT\r\n");
        return AT_RESULT_CODE_OK;
    }
    return AT_RESULT_CODE_FAIL;
}
```

### Sending Data (CIPSEND)

```c
// Example: Send 100 bytes
// AT+CIPSEND=0,100

static int at_setup_cmd_cipsend(int argc, const char **argv)
{
    int linkid = 0;
    int length = 0;

    AT_CMD_PARSE_NUMBER(0, &linkid);
    AT_CMD_PARSE_NUMBER(1, &length);

    if (length > AT_THROUGH_MAX_LEN) {
        return AT_RESULT_CODE_ERROR;
    }

    // Switch to throughput mode for transparent transmission
    at_set_work_mode(AT_WORK_MODE_THROUGHPUT);
    at_through_set_length(linkid, length, 0, length);

    at_response_string("OK\r\n");
    at_response_string(">");  // Prompt for data

    return AT_RESULT_CODE_IGNORE;  // Don't send final result code
}
```

### Closing Connection

```c
// AT+CIPCLOSE=0

static int at_setup_cmd_cipclose(int argc, const char **argv)
{
    int linkid = 0;
    AT_CMD_PARSE_NUMBER(0, &linkid);

    if (g_at_client_handle[linkid].valid) {
        close(g_at_client_handle[linkid].fd);
        g_at_client_handle[linkid].valid = 0;
    }

    return AT_RESULT_CODE_OK;
}
```

---

## 3. Transparent UART-WiFi Transmission

The **Transparent Transmission Mode** (`AT_WORK_MODE_THROUGHPUT`) provides a direct bridge between UART and the network socket, with no AT command processing overhead.

### Throughput Mode State Machine

```
                           ┌─────────────────┐
                           │   AT_WORK_MODE_CMD    │
                           │   (Command Mode)      │
                           └─────────┬───────────┘
                                     │ AT+CIPSEND=len
                                     ▼
                           ┌─────────────────┐
                           │ AT_WORK_MODE_THROUGHPUT │
                           │ ">" prompt shown       │
                           │ Wait for UART data     │
                           └─────────┬───────────────┘
                                     │ Data arrives
                                     │ Send to socket
                                     ▼
                           ┌─────────────────┐
                           │ Transparent     │
                           │ UART ↔ WiFi     │
                           │ Bridge Active   │
                           └─────────┬────────┘
                                     │ "+++" received
                                     │ or length reached
                                     ▼
                           ┌─────────────────┐
                           │   AT_WORK_MODE_CMD    │
                           │   SEND OK/SEND FAIL  │
                           └───────────────────────┘
```

### Throughput Mode Implementation (at_through.c)

```c
#include "at_through.h"

#define AT_THROUGH_EXIT_CMD "+++"  // Exit sequence
#define AT_THROUGH_MAX_LEN   256   // Default max transfer size

static int g_through_linkid = -1;
static int g_through_max_size = 0;
static int g_through_transmit_size = 0;
static int g_through_send_size = 0;
static int g_through_recv_size = 0;

// Input handler: UART → WiFi direction
int at_through_input(uint8_t *data, int32_t len)
{
    if (!data || len <= 0) {
        return -1;
    }

    // Check for exit command
    if (len == strlen(AT_THROUGH_EXIT_CMD) &&
        memcmp(data, AT_THROUGH_EXIT_CMD, strlen(AT_THROUGH_EXIT_CMD)) == 0) {
        if (g_through_max_size > 0) {
            // Exit throughput mode
            g_through_linkid = -1;
            g_through_max_size = 0;
            return -2;  // Signal exit
        }
    }

    if (g_through_max_size > 0) {
        // Bounded transfer: send up to remaining length
        int unit_size;
        int send_size = 0;

        while (len - send_size > 0) {
            if (len - send_size >= g_through_transmit_size)
                unit_size = g_through_transmit_size;
            else
                unit_size = len - send_size;

            // Send to network socket
            if (at_net_client_send(g_through_linkid,
                                    data + send_size,
                                    unit_size) < unit_size) {
                break;  // Send failed
            }
            send_size += unit_size;
        }

        g_through_send_size += send_size;
        g_through_recv_size += len;

        // Progress reporting
        if (send_size < len) {
            at_response_string("+CIPSENDL:%d,%d\r\n",
                             g_through_send_size, g_through_recv_size);
        } else {
            if (g_through_send_size - g_through_report_tag >= g_through_report_size) {
                g_through_report_tag = (g_through_send_size / g_through_report_size) * g_through_report_size;
                at_response_string("+CIPSENDL:%d,%d\r\n",
                                 g_through_report_tag, g_through_recv_size);
            }
        }
        return send_size;
    } else {
        // Unbounded transfer: send all to default link
        return at_net_client_send(0, data, len);
    }
}

// Maximum data length for next UART read
int at_through_max_length(void)
{
    if (g_through_max_size > 0) {
        int unit_size = g_through_max_size - g_through_recv_size;
        if (unit_size > AT_THROUGH_MAX_LEN)
            unit_size = AT_THROUGH_MAX_LEN;
        if (unit_size <= 0) {
            return -1;  // Transfer complete
        }
        return unit_size;
    } else {
        return AT_THROUGH_MAX_LEN;
    }
}

// Configure throughput mode
int at_through_set_length(int linkid, int max_size, int report_size, int transmit_size)
{
    g_through_linkid = linkid;
    g_through_max_size = max_size;
    g_through_report_size = report_size;
    g_through_transmit_size = transmit_size;
    g_through_send_size = 0;
    g_through_recv_size = 0;
    g_through_report_tag = 0;
    return 0;
}
```

### Main Task Loop (at_main.c)

```c
static void at_main_task(void *pvParameters)
{
    int ret;
    int len = 0;
    at_work_mode cmd_mode = at->incmd;
    int recv_size = 0;

    // Send welcome message
    at->device_ops.write_data((uint8_t *)AT_CMD_MSG_WEL,
                              strlen(AT_CMD_MSG_WEL));

    while(!at->exit) {
        // Check mode change
        if (cmd_mode != at->incmd) {
            if (at->incmd == AT_WORK_MODE_CMD) {
                // Entering command mode
            } else {
                // Entering throughput mode
                at->device_ops.write_data((uint8_t *)AT_CMD_MSG_WAIT_DATA,
                                         strlen(AT_CMD_MSG_WAIT_DATA));
            }
            cmd_mode = at->incmd;
        }

        if (cmd_mode == AT_WORK_MODE_CMD) {
            // Command mode: parse AT commands
            ret = at->device_ops.read_data((uint8_t *)(at->inbuf + len),
                                          AT_CMD_MAX_LEN - len);
            if (ret > 0) {
                len += ret;
                len = at_cmd_input((uint8_t *)at->inbuf, len);
            }
        } else {
            // Throughput mode: transparent bridge
            recv_size = at_through_max_length();
            if (recv_size == 0) {
                // Transfer complete - success
                at->device_ops.write_data((uint8_t *)AT_CMD_MSG_SEND_OK,
                                         strlen(AT_CMD_MSG_SEND_OK));
                at_set_work_mode(AT_WORK_MODE_CMD);
            } else if (recv_size < 0) {
                // Transfer complete - failure
                at->device_ops.write_data((uint8_t *)AT_CMD_MSG_SEND_FAIL,
                                         strlen(AT_CMD_MSG_SEND_FAIL));
                at_set_work_mode(AT_WORK_MODE_CMD);
            } else {
                // Read UART data and forward to network
                ret = at->device_ops.read_data((uint8_t *)(at->inbuf), recv_size);
                if (ret > 0) {
                    ret = at_through_input((uint8_t *)at->inbuf, ret);
                    len = 0;

                    if (ret == -1) {
                        printf("at_through_input fail\r\n");
                        at_set_work_mode(AT_WORK_MODE_CMD);
                    } else if (ret == -2) {
                        // "+++" exit
                        at->device_ops.write_data((uint8_t *)AT_CMD_MSG_SEND_CANCELLED,
                                                 strlen(AT_CMD_MSG_SEND_CANCELLED));
                        at_set_work_mode(AT_WORK_MODE_CMD);
                    }
                }
            }
        }
    }

    vTaskDelete(NULL);
}
```

---

## 4. Network Client/Server API

### TCP Client Connection

```c
#include "at_net_main.h"

static int tcp_client_connect(const ip_addr_t *ipaddr, uint16_t port, uint32_t timeout)
{
    int fd;
    struct sockaddr_in addr;

    // Create TCP socket
    fd = socket(AF_INET, SOCK_STREAM, 0);
    if (fd < 0) {
        return -1;
    }

    // Set address
    memset(&addr, 0, sizeof(addr));
    addr.sin_family = AF_INET;
    addr.sin_port = htons(port);
    addr.sin_addr.s_addr = ip_addr_get_ip4_u32(ipaddr);

    // Connect with timeout
    if (timeout) {
        // Set non-blocking
        int flag = fcntl(fd, F_GETFL, 0);
        fcntl(fd, F_SETFL, flag | O_NONBLOCK);

        int res = connect(fd, (struct sockaddr *)&addr, sizeof(addr));
        if (res < 0 && errno != EINPROGRESS) {
            close(fd);
            return -1;
        }

        // Wait for connection
        fd_set writefds;
        FD_ZERO(&writefds);
        FD_SET(fd, &writefds);
        struct timeval tv = { .tv_sec = timeout / 1000,
                             .tv_usec = (timeout % 1000) * 1000 };

        res = select(fd + 1, NULL, &writefds, NULL, &tv);
        if (res <= 0) {
            close(fd);
            return -1;
        }

        // Check socket error
        int so_error;
        socklen_t len = sizeof(so_error);
        getsockopt(fd, SOL_SOCKET, SO_ERROR, &so_error, &len);
        if (so_error != 0) {
            close(fd);
            return -1;
        }

        fcntl(fd, F_SETFL, flag);  // Restore flags
    } else {
        // Blocking connect
        if (connect(fd, (struct sockaddr *)&addr, sizeof(addr)) < 0) {
            close(fd);
            return -1;
        }
    }

    return fd;
}
```

### UDP Client

```c
static int udp_client_create(const ip_addr_t *ipaddr, uint16_t port)
{
    int fd;
    struct sockaddr_in addr;

    fd = socket(AF_INET, SOCK_DGRAM, 0);
    if (fd < 0) {
        return -1;
    }

    memset(&addr, 0, sizeof(addr));
    addr.sin_family = AF_INET;
    addr.sin_port = htons(port);
    addr.sin_addr.s_addr = ip_addr_get_ip4_u32(ipaddr);

    if (connect(fd, (struct sockaddr *)&addr, sizeof(addr)) < 0) {
        close(fd);
        return -1;
    }

    return fd;
}
```

---

## 5. Complete Usage Example

### Initializing and Running

```c
void at_task_example(void *param)
{
    // Initialize AT module
    if (at_module_init() != 0) {
        printf("AT module init failed\r\n");
        vTaskDelete(NULL);
        return;
    }

    printf("AT module initialized\r\n");

    // AT module runs autonomously in its own task
    // Commands are processed automatically

    while(1) {
        vTaskDelay(pdMS_TO_TICKS(1000));
    }
}

void app_main(void)
{
    xTaskCreate(at_task_example, "at_demo", 4096, NULL, 5, NULL);
}
```

### AT Command Sequences

```bash
# 1. Check version
AT+GMR
# Response: OK

# 2. Connect to WiFi
AT+WIFI=ssid,password
# Response: OK

# 3. Get IP address
AT+CIFSR
# Response: +CIFSR:STAIP,"192.168.1.50"
# Response: OK

# 4. Establish TCP connection
AT+CIPSTART=0,"TCP","192.168.1.100",8080
# Response: CONNECT
# Response: OK

# 5. Send 100 bytes transparently
AT+CIPSEND=0,100
# Response: OK
# Response: >
# [Now send 100 bytes of raw binary data]
# Response: SEND OK

# 6. Or use unbounded send (exit with +++)
AT+CIPSEND=0
> [send data...]
+++  # Exit sequence
# Response: SEND CANCELLED

# 7. Close connection
AT+CIPCLOSE=0
# Response: CLOSED
# Response: OK
```

---

## Configuration Constants

| Constant | Default | Description |
|----------|---------|-------------|
| `AT_CMD_MAX_NUM` | 12 | Maximum registered commands |
| `AT_CMD_MAX_LEN` | 256 | Maximum command line length |
| `AT_CMD_MAX_PARA` | 16 | Maximum parameters per command |
| `AT_THROUGH_MAX_LEN` | 256 | Default throughput buffer size |
| `AT_THROUGH_EXIT_CMD` | "+++" | Exit throughput mode sequence |
| `AT_NET_TX_MAX_LEN` | 1024 | Network TX buffer size |
| `AT_NET_RECV_BUF_SIZE` | 4608 | Network RX buffer (3×1536) |

---

## Error Codes

```c
enum {
    AT_RESULT_CODE_OK = 0x00,          // Success
    AT_RESULT_CODE_ERROR = 0x01,       // Generic error
    AT_RESULT_CODE_FAIL = 0x02,        // Operation failed
    AT_RESULT_CODE_SEND_OK = 0x03,     // Send completed
    AT_RESULT_CODE_SEND_FAIL = 0x04,   // Send failed
    AT_RESULT_CODE_IGNORE = 0x05,      // No response
    AT_RESULT_CODE_PROCESS_DONE = 0x06 // Processing complete
};

// With sub-code: AT_RESULT_WITH_SUB_CODE(sub_code << 8 | AT_RESULT_CODE_ERROR)
```

---

## File Structure

```
bouffalo_sdk/components/net/netbus/
├── atmodule/
│   ├── include/
│   │   ├── at_main.h          # Core AT definitions
│   │   ├── at_config.h         # Configuration API
│   │   ├── at_port.h          # Port interface
│   │   ├── at_through.h       # Throughput mode
│   │   ├── at_core.h          # Command parser
│   │   └── at_*/              # Subsystem headers
│   └── src/
│       ├── at_main.c          # Init, main task
│       ├── at_core.c          # Command parsing
│       ├── at_through.c       # Transparent bridge
│       ├── at_port/
│       │   └── at_port_uart.c # UART transport
│       └── at_net/            # Network commands
└── transport/
    ├── uart/                  # UART driver
    ├── usb/                   # USB CDC-ACM
    ├── spisync/               # SPI sync
    └── tty/                   # TTY transport
```

---

## Notes

1. **Thread Safety**: The AT module uses FreeRTOS tasks; UART operations are protected by mutex semaphores.

2. **Exit Sequence**: The "+++" sequence must be sent with >1 second gap before and after to exit throughput mode.

3. **Memory**: AT commands use `at_malloc/at_free` wrappers defined in `at_pal.h` for memory allocation tracking.

4. **WiFi Events**: During throughput mode, WiFi events (connect/disconnect) are suppressed unless `link_state_msg` is enabled.

5. **Baud Rate**: Default UART speed is 2Mbps for high throughput; can be changed via `at_port_para_set()`.
