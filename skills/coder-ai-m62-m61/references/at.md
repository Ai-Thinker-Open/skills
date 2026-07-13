# BL616/BL618 AT Command Module Documentation

AT Command Framework for Bouffalo BL616/BL618 chips. This document covers the AT command architecture, initialization, parsing, command registration, and all available AT command categories.

**Source Location:** `/workspase/BL618Claw/bouffalo_sdk/components/net/netbus/atmodule/`

---

## Table of Contents

1. [Architecture Overview](#1-architecture-overview)
2. [AT Core API](#2-at-core-api)
3. [AT Initialization](#3-at-initialization)
4. [Command Parsing](#4-command-parsing)
5. [Command Registration](#5-command-registration)
6. [Base AT Commands](#6-base-at-commands)
7. [Wi-Fi AT Commands](#7-wi-fi-at-commands)
8. [BLE AT Commands](#8-ble-at-commands)
9. [MQTT AT Commands](#9-mqtt-at-commands)
10. [HTTP AT Commands](#10-http-at-commands)
11. [Network AT Commands](#11-network-at-commands)
12. [Working Code Examples](#12-working-code-examples)

---

## 1. Architecture Overview

### Core Components

```
at_core.c          - Core AT engine (parsing, registration, dispatch)
at_main.h          - Main AT structures and types
at_port.h          - Platform port (UART read/write)
at_base/           - Base system commands (AT+RST, AT+GMR)
at_wifi/           - Wi-Fi commands (AT+CWJAP, AT+CWMODE)
at_ble/            - BLE commands (AT+BLEINIT, AT+BLESCAN)
at_mqtt/           - MQTT commands (AT+MQTTCONN, AT+MQTTSUB)
at_http/           - HTTP commands (AT+HTTPCGET, AT+HTTPCPOST)
at_net/            - Network commands (AT+CIFSR, AT+PING)
```

### Key Structures

```c
// From at_main.h
typedef struct {
    char *at_name;
    int (*at_query_cmd)(int argc, const char **argv);
    int (*at_setup_cmd)(int argc, const char **argv);
    int (*at_exe_cmd)(int argc, const char **argv);
    uint16_t para_num_min;
    uint16_t para_num_max;
} at_cmd_struct;

typedef struct {
    int (*init_device)(void);
    int (*deinit_device)(void);
    int (*read_data) (uint8_t *data, int len);
    int (*write_data) (uint8_t *data, int len);
    int (*f_output_redirect) (void);
} at_device_ops;

typedef enum {
    AT_RESULT_CODE_OK           = 0x00,
    AT_RESULT_CODE_ERROR        = 0x01,
    AT_RESULT_CODE_FAIL         = 0x02,
    AT_RESULT_CODE_SEND_OK      = 0x03,
    AT_RESULT_CODE_SEND_FAIL    = 0x04,
    AT_RESULT_CODE_IGNORE       = 0x05,
    AT_RESULT_CODE_PROCESS_DONE = 0x06,
} at_result_code_string_index;

typedef enum {
    AT_WORK_MODE_CMD = 0x00,
    AT_WORK_MODE_THROUGHPUT,
    AT_WORK_MODE_CMD_THROUGHPUT
} at_work_mode;
```

### AT Command Response Messages

```c
// From at_core.h
#define AT_CMD_MSG_WEL              "\r\nready\r\n"
#define AT_CMD_MSG_BUSY             "\r\nbusy p...\r\n"
#define AT_CMD_MSG_OK               "\r\nOK\r\n"
#define AT_CMD_MSG_ERROR            "\r\nERROR\r\n"
#define AT_CMD_MSG_FAIL             "\r\nERROR\r\n"
#define AT_CMD_MSG_SEND_OK          "\r\nSEND OK\r\n"
#define AT_CMD_MSG_SEND_FAIL        "\r\nSEND FAIL\r\n"
#define AT_CMD_MSG_SEND_CANCELLED   "\r\nSEND CANCELLED\r\n"
#define AT_CMD_MSG_WAIT_DATA        "\r\n>"
```

---

## 2. AT Core API

### Core Functions (from at_core.h)

```c
// Version and compile info
uint32_t at_cmd_get_version(void);
int at_cmd_get_compile_time(char *time, size_t buf_len);

// Command registration
int at_cmd_register(const at_cmd_struct *cmds, int num_cmds);
int at_cmd_unregister(const at_cmd_struct *cmds, int num_cmds);

// Input processing
int at_cmd_input(uint8_t *data, int32_t len);

// Output functions
int at_write_data(uint8_t *data, int32_t len);
void at_write_string(const char *format, va_list args);

// Error handling
int at_cmd_set_error(uint32_t error);
void at_cmd_syslog(uint32_t error);

// Argument parsing helpers
int at_arg_is_null(const char *arg);
int at_arg_get_number(const char *arg, int *value);
int at_arg_get_string(const char *arg, char *string, int max);
```

### Error Codes

```c
// From at_core.h
typedef enum {
    AT_SUB_OK                       = 0x00,
    AT_SUB_COMMON_ERROR             = 0x01,
    AT_SUB_NO_TERMINATOR            = 0x02,  // "\r\n" not found
    AT_SUB_NO_AT                    = 0x03,   // "AT" not found
    AT_SUB_PARA_LENGTH_MISMATCH     = 0x04,
    AT_SUB_PARA_TYPE_MISMATCH       = 0x05,
    AT_SUB_PARA_NUM_MISMATCH        = 0x06,
    AT_SUB_PARA_VALUE_INVALID       = 0x07,
    AT_SUB_PARA_PARSE_FAIL          = 0x08,
    AT_SUB_UNSUPPORT_CMD            = 0x09,
    AT_SUB_CMD_EXEC_FAIL            = 0x0A,
    AT_SUB_CMD_PROCESSING           = 0x0B,
    AT_SUB_NO_MEMORY                = 0x0D,
    AT_SUB_NO_RESOURCE              = 0x0E,
    AT_SUB_TIMEOUT                  = 0x0F,
    AT_SUB_NOT_ALLOWED              = 0x10,
    AT_SUB_NOT_INIT                 = 0x11,
} at_error_code;

// Error code macro
#define AT_ERROR_NO(subcategory,extension)  \
    ((AT_MODULE_NUM << 24) | ((subcategory) << 16) | (extension))

#define AT_CMD_ERROR_OK                   AT_ERROR_NO(AT_SUB_OK,0x00)
#define AT_CMD_ERROR_NOT_FOUND_AT         AT_ERROR_NO(AT_SUB_NO_AT,0x00)
#define AT_CMD_ERROR_PARA_NUM(need,given)  AT_ERROR_NO(AT_SUB_PARA_NUM_MISMATCH,(((need) << 8) | (given)))
```

---

## 3. AT Initialization

### Module Initialization

```c
// From at_main.h
extern struct at_struct *at;

int at_module_init(void);
int at_module_deinit(void);

// Register function callbacks (restore factory defaults, stop services)
int at_register_function(at_func restore, at_func stop);

// Response handling
void at_response_result(uint32_t result_code);
void at_response_string(const char *format, ... );
void at_write(const char *format , ...);

// Work mode
int at_set_work_mode(at_work_mode mode);
at_work_mode at_get_work_mode(void);
```

### Port Functions (from at_port.h)

```c
int at_port_init(void);
int at_port_deinit(void);
int at_port_read_data(uint8_t* data, int len);
int at_port_write_data(uint8_t *data, int len);
int at_port_para_set(int baudrate, uint8_t databits, uint8_t stopbits, uint8_t parity, uint8_t flow_control);
int at_port_para_get(int *baudrate, uint8_t *databits, uint8_t *stopbits, uint8_t *parity, uint8_t *flow_control);
int at_port_netmode_set(int mode);
int at_port_netmode_get(void);
```

### Example Initialization Code

```c
// Complete AT module initialization sequence
#include "at_main.h"
#include "at_core.h"
#include "at_port.h"
#include "at_base_cmd.h"
#include "at_wifi_cmd.h"
#include "at_ble_cmd.h"
#include "at_mqtt_cmd.h"
#include "at_http_cmd.h"
#include "at_net_cmd.h"

int at_module_init(void)
{
    // Initialize AT structure
    at = (struct at_struct *)malloc(sizeof(struct at_struct));
    if (!at) {
        return -1;
    }
    memset(at, 0, sizeof(struct at_struct));
    
    // Initialize port (UART)
    at_port_init();
    
    // Register device operations
    at->device_ops.init_device = your_uart_init;
    at->device_ops.deinit_device = your_uart_deinit;
    at->device_ops.read_data = your_uart_read;
    at->device_ops.write_data = your_uart_write;
    
    // Set default work mode
    at->incmd = AT_WORK_MODE_CMD;
    at->echo = 1;
    at->syslog = 0;
    at->store = 1;
    
    // Register base commands
    at_base_cmd_regist();
    
    // Register Wi-Fi commands
    at_wifi_cmd_regist();
    
    // Register BLE commands
    at_ble_cmd_regist();
    
    // Register MQTT commands
    at_mqtt_cmd_regist();
    
    // Register HTTP commands
    at_http_cmd_regist();
    
    // Register Network commands
    at_net_cmd_regist();
    
    return 0;
}
```

---

## 4. Command Parsing

### Command Types

```c
typedef enum {
    AT_CMD_TYPE_TEST,   // AT+NAME=?  - Test command
    AT_CMD_TYPE_QUERY,  // AT+NAME?   - Query current value
    AT_CMD_TYPE_SETUP,  // AT+NAME=x,y - Set parameters
    AT_CMD_TYPE_EXE,    // AT+NAME    - Execute command
    AT_CMD_TYPE_ERROR
} at_cmd_type;
```

### Parsing State Machine (from at_core.c)

```c
static int at_cmd_parse(char *inbuf)
{
    // State machine for parsing AT commands
    // Handles: =, ?, ", ", comma separation, escape characters
    
    struct {
        unsigned inArg : 1;
        unsigned inQuote : 1;
        unsigned done : 1;
        unsigned error : 1;
        unsigned haveEqual : 1;
        unsigned haveQuest : 1;
    } stat;
    
    // Parsing logic:
    // - "=" sets parameters
    // - "?" queries values
    // - Quoted strings ("value") are treated as single arguments
    // - Commas separate multiple arguments
    // - Backslash (\) escapes characters
}
```

### Command Input Processing

```c
// From at_core.c - Main input handler
int at_cmd_input(uint8_t *data, int32_t len)
{
    // Waits for \r\n terminator
    // Validates "AT" prefix (case-insensitive)
    // Echoes command if enabled
    // Routes to at_cmd_parse() for processing
    // Returns result code
}
```

### Argument Parsing Macros

```c
// From at_core.h - Convenient parsing macros

// Parse required string parameter
#define AT_CMD_PARSE_STRING(i, string, max) do { \
    if (!at_arg_get_string(argv[i], string, max)) { \
        at_cmd_set_error(AT_CMD_ERROR_PARA_PARSE_FAIL(i)); \
        return AT_RESULT_CODE_ERROR; \
    } \
} while(0);

// Parse required number parameter
#define AT_CMD_PARSE_NUMBER(i, num) do {\
    if (!at_arg_get_number(argv[i], num)) { \
        at_cmd_set_error(AT_CMD_ERROR_PARA_PARSE_FAIL(i)); \
        return AT_RESULT_CODE_ERROR; \
    } \
} while(0);

// Parse optional string parameter
#define AT_CMD_PARSE_OPT_STRING(i, string, max, valid) do { \
    if(argc > i && !at_arg_is_null(argv[i])) { \
        if (!at_arg_get_string(argv[i], string, max)) { \
            at_cmd_set_error(AT_CMD_ERROR_PARA_PARSE_FAIL(i)); \
            return AT_RESULT_CODE_ERROR; \
        } \
        valid = 1; \
    } \
} while(0);

// Parse optional number parameter
#define AT_CMD_PARSE_OPT_NUMBER(i, num, valid) do {\
    if(argc > i && !at_arg_is_null(argv[i])) { \
        if (!at_arg_get_number(argv[i], num)) { \
            at_cmd_set_error(AT_CMD_ERROR_PARA_PARSE_FAIL(i)); \
            return AT_RESULT_CODE_ERROR; \
        } \
        valid = 1; \
    } \
} while(0);
```

---

## 5. Command Registration

### Registering Commands

```c
// Each command group (base, wifi, ble, etc.) provides a registration function
// These return bool indicating success

bool at_base_cmd_regist(void);   // Register base AT commands
bool at_wifi_cmd_regist(void);   // Register Wi-Fi commands
bool at_ble_cmd_regist(void);    // Register BLE commands
bool at_mqtt_cmd_regist(void);   // Register MQTT commands
bool at_http_cmd_regist(void);   // Register HTTP commands
bool at_net_cmd_regist(void);    // Register Network commands
```

### Command Structure Example

```c
// Define a command table
static const at_cmd_struct at_example_cmds[] = {
    {
        .at_name = "+EXAMPLE",           // Command name (AT+EXAMPLE)
        .at_query_cmd = at_query_cmd_example,  // AT+EXAMPLE?
        .at_setup_cmd = at_setup_cmd_example,  // AT+EXAMPLE=value
        .at_exe_cmd = at_exe_cmd_example,     // AT+EXAMPLE
        .para_num_min = 0,
        .para_num_max = 3,
    },
    // More commands...
    { NULL }  // Terminator
};

// Register function
bool at_example_cmd_regist(void)
{
    return at_cmd_register(at_example_cmds, 1) == 0;
}
```

### Internal Registration Flow

```c
// From at_core.c
static int at_register_command(const at_cmd_struct *cmd)
{
    if (!at) return -1;
    
    if (at->num_commands < AT_CMD_MAX_NUM) {
        // Check if already registered
        for (i = 0; i < at->num_commands; i++) {
            if (at->commands[i] == cmd) {
                return 0;  // Already registered
            }
        }
        at->commands[at->num_commands++] = cmd;
        return 0;
    }
    return -1;
}

// Command lookup during execution
static const at_cmd_struct *at_cmd_lookup(char *name)
{
    // Iterates through registered command tables
    // Case-insensitive strcasecmp comparison
}
```

---

## 6. Base AT Commands

**Header:** `at_base/at_base_cmd.h`  
**Source:** `at_base/at_base_cmd.c`

### Command Table

| Command | Type | Description |
|---------|------|-------------|
| `AT` | EXE | Basic AT test |
| `AT+RST` | EXE | Reset system |
| `AT+GMR` | EXE | Get firmware version |
| `AT+CMD` | QUERY | List all registered commands |
| `AT+SYSRAM` | QUERY | Get system RAM info |
| `AT+SYSMSG` | QUERY/SET | System message configuration |
| `AT+SYSLOG` | QUERY/SET | System logging enable/disable |
| `AT+SYSSTORE` | QUERY/SET | Flash storage enable/disable |
| `AT+ECHO` | EXE | Enable/disable echo |
| `AT+RESTORE` | EXE | Restore factory defaults |

### Key Base Commands

```c
// AT+RST - Reset system
static int at_exe_cmd_rst(int argc, const char **argv)
{
    int i;
    // Stop all registered services
    for (i = 0; i < AT_CMD_MAX_FUNC; i++) {
        if (at->function_ops[i].stop_func)
            at->function_ops[i].stop_func();
    }
    vTaskDelay(pdMS_TO_TICKS(100));
    bl_sys_reset_por();  // Reset chip
    return AT_RESULT_CODE_OK;
}

// AT+GMR - Get version info
static int at_exe_cmd_gmr(int argc, const char **argv)
{
    char *outbuf = malloc(1024);
    uint32_t core_version = at_cmd_get_version();
    char core_compile_time[32];
    at_cmd_get_compile_time(core_compile_time, sizeof(core_compile_time));
    
    snprintf(outbuf, 1024, "AT version:%d.%d.%d.%d(%s)\r\n",
             AT_CMD_GET_VERSION(core_version), core_compile_time);
    // Add more version info...
    AT_CMD_RESPONSE(outbuf);
    free(outbuf);
    return AT_RESULT_CODE_OK;
}

// AT+CMD - List all commands
static int at_query_cmd_cmd(int argc, const char **argv)
{
    // Lists all registered AT commands with their types
}

// AT+SYSRAM - System RAM query
static int at_query_cmd_sysram(int argc, const char **argv)
{
    at_response_string("+SYSRAM:%d,%d", kfree_size(0), lwip_heap);
    return AT_RESULT_CODE_OK;
}
```

---

## 7. Wi-Fi AT Commands

**Header:** `at_wifi/at_wifi_cmd.h`, `at_wifi/at_wifi_mgmr.h`  
**Source:** `at_wifi/at_wifi_cmd.c`

### Wi-Fi Adapter Layer

```c
// Key types from at_wifi_mgmr.h

typedef struct at_wifi_mgmr_scan_item {
    uint32_t mode;
    uint32_t timestamp_lastseen;
    int ssid_len;
    uint8_t channel;
    int8_t rssi;
    char ssid[32];
    uint8_t bssid[6];
    uint8_t auth;
    uint8_t cipher;
    // ... more fields
} at_wifi_mgmr_scan_item_t;

typedef struct at_wifi_mgmr_connect_ind_stat_info {
    char ssid[33];
    uint8_t bssid[6];
    uint8_t channel;
    uint8_t security;
} at_wifi_mgmr_connect_ind_stat_info_t;

typedef struct at_wifi_mgmr_ap_params {
    char *ssid;
    char *key;
    uint8_t hidden_ssid;
    uint8_t channel;
    uint8_t use_dhcpd;
    uint8_t start;
    // ... more fields
} at_wifi_mgmr_ap_params_t;
```

### Key Wi-Fi Functions

```c
// Connection management
int at_wifi_mgmr_sta_connect(const char *ssid, const char *key, const char *bssid, 
                              const char *akm_str, uint8_t pmf_cfg, 
                              uint16_t freq1, uint16_t freq2, uint8_t use_dhcp);
int at_wifi_mgmr_sta_disconnect(void);
int at_wifi_mgmr_sta_rssi_get(int *rssi);
int at_wifi_mgmr_sta_ip_set(uint32_t ip, uint32_t mask, uint32_t gw, uint32_t dns);

// Scan functions
int at_wifi_mgmr_sta_scan(at_wifi_mgmr_scan_params_t *scan_cfg);
int at_wifi_mgmr_sta_scanlist(void);
int at_wifi_mgmr_sta_scanlist_free(void);

// AP functions
int at_wifi_mgmr_ap_start(at_wifi_mgmr_ap_params_t *config);
int at_wifi_mgmr_ap_stop(void);

// State queries
int at_wifi_mgmr_state_get(void);
int at_wifi_mgmr_sta_state_get(void);
int at_wifi_mgmr_ap_state_get(void);
```

### Wi-Fi AT Commands

| Command | Type | Description |
|---------|------|-------------|
| `AT+CWMODE` | QUERY/SET | Wi-Fi mode (STA/AP/STA+AP) |
| `AT+CWJAP` | QUERY/SET/EXE | Join access point |
| `AT+CWLAP` | SET | List available APs |
| `AT+CWQAP` | EXE | Disconnect from AP |
| `AT+CWSAP` | QUERY/SET | Set AP configuration |
| `AT+CWLIF` | EXE | Get connected STA list |
| `AT+CIPSTA` | QUERY/SET | Set STA IP address |
| `AT+CIPAP` | QUERY/SET | Set AP IP address |
| `AT+CIFSR` | EXE | Get IP address |
| `AT+CWNETMODE` | QUERY | Get network mode (NCP/RCP) |
| `AT+WIFISP` | QUERY/SET | Wi-Fi power save mode |

### Wi-Fi Command Examples

```c
// AT+CWMODE - Set Wi-Fi mode
static int at_setup_cmd_cwmode(int argc, const char **argv)
{
    int mode = 0;
    int auto_connect_valid = 0, auto_connect = 0;
    
    AT_CMD_PARSE_NUMBER(0, &mode);
    AT_CMD_PARSE_OPT_NUMBER(1, &auto_connect, auto_connect_valid);
    
    if (mode < WIFI_DISABLE || mode > WIFI_AP_STA_MODE) {
        return AT_RESULT_WITH_SUB_CODE(AT_SUB_PARA_VALUE_INVALID);
    }
    
    if (at_wifi_config->wifi_mode != mode) {
        at_wifi_config->wifi_mode = mode;
        at_wifi_set_mode();
    }
    
    if (at->store) {
        at_wifi_config_save(AT_CONFIG_KEY_WIFI_MODE);
    }
    return AT_RESULT_CODE_OK;
}

// AT+CWJAP - Connect to AP
static int at_setup_cmd_cwjap(int argc, const char **argv)
{
    char ssid[33];
    char password[65];
    char bssidString[20];
    int bssid_valid = 0;
    uint8_t bssid[6] = {0};
    int pmf_valid = 0, pmf = 0;
    
    AT_CMD_PARSE_STRING(0, ssid, sizeof(ssid));
    AT_CMD_PARSE_STRING(1, password, sizeof(password));
    AT_CMD_PARSE_OPT_STRING(2, bssidString, sizeof(bssidString), bssid_valid);
    AT_CMD_PARSE_OPT_NUMBER(7, &pmf, pmf_valid);
    
    if (bssid_valid) {
        get_mac_from_string(bssidString, bssid);
    }
    
    strlcpy(at_wifi_config->sta_info.ssid, ssid, sizeof(ssid));
    strlcpy(at_wifi_config->sta_info.psk, password, sizeof(password));
    
    at_wifi_sta_connect(at_wifi_config->sta_info.jap_timeout * 1000);
    
    return AT_RESULT_CODE_OK;
}

// AT+CIPSTA - Set STA IP
static int at_setup_cmd_cipsta(int argc, const char **argv)
{
    char ip[16], gateway[16], netmask[16];
    int gateway_valid = 0, netmask_valid = 0;
    uint32_t ipaddr, gwaddr, maskaddr = IP_SET_ADDR(255, 255, 255, 0);
    
    AT_CMD_PARSE_STRING(0, ip, sizeof(ip));
    AT_CMD_PARSE_OPT_STRING(1, gateway, sizeof(gateway), gateway_valid);
    AT_CMD_PARSE_OPT_STRING(2, netmask, sizeof(netmask), netmask_valid);
    
    ipaddr = ipaddr_addr(ip);
    if (gateway_valid) {
        gwaddr = ipaddr_addr(gateway);
    } else {
        gwaddr = (ipaddr & maskaddr) | (0x01 << 24);
    }
    
    at_wifi_mgmr_sta_ip_set(ipaddr, maskaddr, gwaddr, 0);
    
    return AT_RESULT_CODE_OK;
}
```

---

## 8. BLE AT Commands

**Header:** `at_ble/at_ble_cmd.h`  
**Source:** `at_ble/at_ble_cmd.c`

### BLE Configuration

```c
// From at_ble/at_ble_cmd.c
#define BLE_AT_FORMAT_MAX_LEN          64
#define BLE_AT_HEX_STRING_MAX_LEN      62

#define BLE_SERVER    0
#define BLE_CLIENT    1
#define BLE_DUALMODE  2
#define BLE_DISABLE   3

// BLE roles
typedef enum {
    BLE_ROLE_DISABLE = 0,
    BLE_ROLE_SERVER,
    BLE_ROLE_CLIENT,
    BLE_ROLE_DUAL
} ble_work_role_t;
```

### Key BLE Functions

```c
// From at_ble/at_ble_main.h
int at_ble_init(uint8_t role);
int at_ble_get_public_addr(uint8_t addr[6]);
int at_ble_set_public_addr(uint8_t addr[6]);
const char *at_ble_get_name(void);
int at_ble_set_name(const char *name);
```

### BLE AT Commands

| Command | Type | Description |
|---------|------|-------------|
| `AT+BLEINIT` | QUERY/SET | Initialize BLE (role selection) |
| `AT+BLEADDR` | QUERY/SET | Get/Set BLE MAC address |
| `AT+BLENAME` | QUERY/SET | Get/Set BLE device name |
| `AT+BLESCANPARAM` | QUERY/SET | Set scan parameters |
| `AT+BLESCAN` | SET/EXE | Start/stop BLE scan |
| `AT+BLESCANJSON` | EXE | Get scan results as JSON |
| `AT+BLECONN` | SET | Connect to BLE device |
| `AT+BLEDISCONN` | SET | Disconnect BLE connection |
| `AT+BLEGATTSSRVCRE` | SET | Create GATT service |
| `AT+BLEGATTSSRVSTART` | SET | Start GATT service |
| `AT+BLEGATTCCFG` | SET | Configure GATT characteristic |
| `AT+BLEGATTSNTFY` | SET | Send notification |
| `AT+BLESPPCFG` | SET | Configure SPP mode |
| `AT+BLESPPDATA` | SET | Send SPP data |

### BLE Command Examples

```c
// AT+BLEINIT - Initialize BLE
static int at_setup_cmd_ble_init(int argc, const char **argv)
{
    int role = 0;
    
    AT_CMD_PARSE_NUMBER(0, &role);
    
    if (role != BLE_SERVER && role != BLE_CLIENT && 
        role != BLE_DUALMODE && role != BLE_DISABLE) {
        return AT_RESULT_WITH_SUB_CODE(AT_SUB_PARA_VALUE_INVALID);
    }
    
    if (at_ble_init(role) != 0) {
        return AT_RESULT_WITH_SUB_CODE(AT_SUB_CMD_EXEC_FAIL);
    }
    at_ble_config->work_role = role;
    
    return AT_RESULT_CODE_OK;
}

// AT+BLEADDR - Get/Set BLE address
static int at_setup_cmd_ble_addr(int argc, const char **argv)
{
    char addr_string[18];
    uint8_t addr[6];
    
    AT_CMD_PARSE_STRING(0, addr_string, sizeof(addr_string));
    
    if (get_mac_from_string(addr_string, addr) != 0) {
        return AT_RESULT_WITH_SUB_CODE(AT_SUB_PARA_VALUE_INVALID);
    }
    
    if (at_ble_set_public_addr(addr) != 0) {
        return AT_RESULT_WITH_SUB_CODE(AT_SUB_CMD_EXEC_FAIL);
    }
    
    return AT_RESULT_CODE_OK;
}

// Helper function for MAC parsing
static int get_mac_from_string(const char *string, uint8_t mac[6])
{
    // Format: "XX:XX:XX:XX:XX:XX"
    if (strlen(string) != 17) return -1;
    // Parse hex pairs separated by ':'
    // ...
}
```

---

## 9. MQTT AT Commands

**Header:** `at_mqtt/at_mqtt_cmd.h`  
**Source:** `at_mqtt/at_mqtt_cmd.c`

### MQTT Configuration

```c
// From at_mqtt/at_mqtt_cmd.c
#define AT_MQTT_LINK_MAX      (1)
#define AT_MQTT_ALPN_MAX      (6)
#define AT_MQTT_SUB_TOPIC_MAX (32)

#define AT_MQTT_STATE_NOT_INIT           0
#define AT_MQTT_STATE_USERCFG            1
#define AT_MQTT_STATE_CONNCFG            2
#define AT_MQTT_STATE_DISCONNECT         3
#define AT_MQTT_STATE_CONNECTED          4
#define AT_MQTT_STATE_CONNECTED_NO_TOPIC 5
#define AT_MQTT_STATE_CONNECTED_TOPIC    6

#define AT_MQTT_OVER_TCP                 0
#define AT_MQTT_OVER_TLS_NOT_AUTH        1
#define AT_MQTT_OVER_TLS_SERVER_AUTH     2
#define AT_MQTT_OVER_TLS_CLIENT_AUTH     3
#define AT_MQTT_OVER_TLS_BOTH_AUTH       4

typedef struct at_mqtt {
    struct custom_socket_handle sockfd;
    ssl_param_t *ctx;
    uint8_t scheme;
    uint8_t reconnect;
    uint8_t state;
    uint8_t refresher_run;
    struct mqtt_client client;
    TaskHandle_t client_task;
    char *client_id;
    char *user_name;
    char *password;
    uint16_t keepalive;
    char will_topic[128];
    char will_message[128];
    char topic[128];
    char remote_host[128];
    char remote_port[8];
    // ... subscription topics
} at_mqtt_t;
```

### MQTT AT Commands

| Command | Type | Description |
|---------|------|-------------|
| `AT+MQTTCONN` | SET | Connect to MQTT broker |
| `AT+MQTTDISCONN` | EXE | Disconnect from broker |
| `AT+MQTTSUB` | SET | Subscribe to topic |
| `AT+MQTTUNSUB` | SET | Unsubscribe from topic |
| `AT+MQTTPUB` | SET | Publish message |
| `AT+MQTTPUBDATA` | SET | Publish data (with body) |
| `AT+MQTTUSERNAME` | SET | Set MQTT username |
| `AT+MQTTPASSWORD` | SET | Set MQTT password |
| `AT+MQTTCLIENTID` | SET | Set client ID |
| `AT+MQTTCAENABLE` | SET | Enable/disable CA |
| `AT+MQTTSSLCFG` | SET | Configure SSL |

### MQTT Command Examples

```c
// AT+MQTTCONN - Connect to broker
// Command: AT+MQTTCONN=<linkid>,"host",port,keepalive[,scheme]
// Example: AT+MQTTCONN=0,"mqtt.example.com",1883,60,0

static int at_setup_cmd_mqttconn(int argc, const char **argv)
{
    int linkid = 0;
    char host[128];
    int port = 1883;
    int keepalive = 60;
    int scheme = AT_MQTT_OVER_TCP;
    
    AT_CMD_PARSE_NUMBER(0, &linkid);
    AT_CMD_PARSE_STRING(1, host, sizeof(host));
    AT_CMD_PARSE_NUMBER(2, &port);
    AT_CMD_PARSE_NUMBER(3, &keepalive);
    AT_CMD_PARSE_OPT_NUMBER(4, &scheme, scheme_valid);
    
    // Establish TCP/TLS connection
    // Configure MQTT client
    // Start MQTT task
    
    return AT_RESULT_CODE_OK;
}

// AT+MQTTSUB - Subscribe to topic
// Command: AT+MQTTSUB=<linkid>,<topic>,<qos>
static int at_setup_cmd_mqttsub(int argc, const char **argv)
{
    int linkid, qos;
    char topic[128];
    
    AT_CMD_PARSE_NUMBER(0, &linkid);
    AT_CMD_PARSE_STRING(1, topic, sizeof(topic));
    AT_CMD_PARSE_NUMBER(2, &qos);
    
    // Add to subscription list
    // Send MQTT SUBSCRIBE packet
    
    return AT_RESULT_CODE_OK;
}

// AT+MQTTPUB - Publish message
// Command: AT+MQTTPUB=<linkid>,<topic>,<data>,<qos>[,<retain>]
static int at_setup_cmd_mqttpub(int argc, const char **argv)
{
    int linkid, qos, retain = 0;
    char topic[128];
    char data[1024];
    
    AT_CMD_PARSE_NUMBER(0, &linkid);
    AT_CMD_PARSE_STRING(1, topic, sizeof(topic));
    AT_CMD_PARSE_STRING(2, data, sizeof(data));
    AT_CMD_PARSE_NUMBER(3, &qos);
    AT_CMD_PARSE_OPT_NUMBER(4, &retain, retain_valid);
    
    // Send MQTT PUBLISH packet
    
    return AT_RESULT_CODE_OK;
}
```

---

## 10. HTTP AT Commands

**Header:** `at_http/at_http_cmd.h`  
**Source:** `at_http/at_http_cmd.c`

### HTTP Configuration

```c
// From at_http/at_http_cmd.c
#define AT_HTTPC_HANDLE_MAX (3)
#define AT_HTTPC_DEFAULT_TIMEOUT (5000)
#define AT_HTTPC_RECVBUF_SIZE_DEFAULT (15*1024)

#define AT_HTTPC_RECV_MODE_ACTIVE  0
#define AT_HTTPC_RECV_MODE_PASSIVE 1

#define AT_HTTPS_NOT_AUTH        0
#define AT_HTTPS_SERVER_AUTH     1
#define AT_HTTPS_CLIENT_AUTH     2
#define AT_HTTPS_BOTH_AUTH       3

struct at_http_ctx {
    httpc_connection_t settings;
    uint8_t *data;
    struct altcp_pcb *altcp_conn;
    QueueHandle_t recv_mbox;
    SemaphoreHandle_t mutex;
    uint8_t used;
    uint8_t https_auth_type;
    uint8_t recv_mode;
    uint8_t linkid;
    char ca_file[32];
    char cert_file[32];
    char key_file[32];
    char *url;
    uint32_t url_size;
    uint32_t recv_avail;
};
```

### HTTP AT Commands

| Command | Type | Description |
|---------|------|-------------|
| `AT+HTTPCLIENT` | SET | HTTP client request |
| `AT+HTTPCGET` | SET | HTTP GET request |
| `AT+HTTPCPOST` | SET | HTTP POST request |
| `AT+HTTPCPUT` | SET | HTTP PUT request |
| `AT+HTTPCDELETE` | SET | HTTP DELETE request |
| `AT+HTTPCHEAD` | SET | Set custom HTTP header |
| `AT+HTTPCRECV` | EXE | Receive HTTP response data |
| `AT+HTTPCFG` | SET | Configure HTTP parameters |

### HTTP Command Examples

```c
// AT+HTTPCLIENT - HTTP client request
// Command: AT+HTTPCLIENT=<mode>,<timeout>,<url>[,<content_type>]

static int at_setup_cmd_httpcclient(int argc, const char **argv)
{
    int mode, timeout;
    char url[256];
    char content_type[64] = "text/plain";
    int content_type_valid = 0;
    
    AT_CMD_PARSE_NUMBER(0, &mode);
    AT_CMD_PARSE_NUMBER(1, &timeout);
    AT_CMD_PARSE_STRING(2, url, sizeof(url));
    AT_CMD_PARSE_OPT_STRING(3, content_type, sizeof(content_type), content_type_valid);
    
    // Parse URL to extract host, path, scheme
    // Establish TCP/TLS connection
    // Send HTTP request
    // Handle response
    
    return AT_RESULT_CODE_OK;
}

// AT+HTTPCGET - HTTP GET
// Command: AT+HTTPCGET=<linkid>,<url>,<timeout>

static int at_setup_cmd_httpcget(int argc, const char **argv)
{
    int linkid, timeout;
    char url[256];
    
    AT_CMD_PARSE_NUMBER(0, &linkid);
    AT_CMD_PARSE_STRING(1, url, sizeof(url));
    AT_CMD_PARSE_NUMBER(2, &timeout);
    
    // GET request implementation
    
    return AT_RESULT_CODE_OK;
}

// AT+HTTPCRECV - Receive response data
// Command: AT+HTTPCRECV=<linkid>,<length>

static int at_exe_cmd_httpcrecv(int argc, const char **argv)
{
    int linkid, len;
    uint8_t *buf;
    
    AT_CMD_PARSE_NUMBER(0, &linkid);
    AT_CMD_PARSE_NUMBER(1, &len);
    
    buf = malloc(len);
    // Read from receive buffer
    // Send data to host
    
    return AT_RESULT_CODE_OK;
}
```

---

## 11. Network AT Commands

**Header:** `at_net/at_net_cmd.h`  
**Source:** `at_net/at_net_cmd.c`

### Network AT Commands

| Command | Type | Description |
|---------|------|-------------|
| `AT+CIFSR` | EXE | Get IP addresses (STA/AP) |
| `AT+CIPV6` | QUERY/SET | Enable/disable IPv6 |
| `AT+CIPDNS` | QUERY/SET | Configure DNS servers |
| `AT+PING` | SET | Ping remote host |
| `AT+CIPSTART` | SET | Establish TCP/UDP connection |
| `AT+CIPSEND` | SET | Send TCP/UDP data |
| `AT+CIPCLOSE` | SET | Close TCP/UDP connection |
| `AT+CIPSSLCCONF` | SET | Configure SSL |
| `AT+CIPSSLCFG` | SET | Configure SSL parameters |
| `AT+SNTP` | QUERY/SET | Configure SNTP |

### Network Command Examples

```c
// AT+CIFSR - Get IP addresses
static int at_exe_cmd_cifsr(int argc, const char **argv)
{
    ip4_addr_t sta_addr, sta_gw, sta_mask, dns, ap_addr;
    
    // Get STA IP
    if (at_wifi_config->wifi_mode == WIFI_STATION_MODE || 
        at_wifi_config->wifi_mode == WIFI_AP_STA_MODE) {
        at_response_string("+CIFSR:STAIP,\"%s\"\r\n", ip4addr_ntoa(&sta_addr));
        at_response_string("+CIFSR:STAMAC,\"%02x:%02x:%02x:%02x:%02x:%02x\"\r\n", ...);
    }
    
    // Get AP IP
    if (at_wifi_config->wifi_mode == WIFI_SOFTAP_MODE || 
        at_wifi_config->wifi_mode == WIFI_AP_STA_MODE) {
        at_response_string("+CIFSR:APIP,\"%s\"\r\n", ip4addr_ntoa(&ap_addr));
        at_response_string("+CIFSR:APMAC,\"%02x:%02x:%02x:%02x:%02x:%02x\"\r\n", ...);
    }
    
    return AT_RESULT_CODE_OK;
}

// AT+PING - Ping host
// Command: AT+PING=<host>[,<timeout>]

static int at_setup_cmd_ping(int argc, const char **argv)
{
    char host[128];
    int timeout = 1000;
    int timeout_valid = 0;
    
    AT_CMD_PARSE_STRING(0, host, sizeof(host));
    AT_CMD_PARSE_OPT_NUMBER(1, &timeout, timeout_valid);
    
    // Resolve host name or use IP directly
    // Send ICMP echo request
    // Wait for reply
    // Report RTT
    
    return AT_RESULT_CODE_OK;
}

// AT+CIPDNS - Set DNS servers
// Command: AT+CIPDNS=<enable>[,<dns1>[,<dns2>[,<dns3>]]]

static int at_setup_cmd_cipdns(int argc, const char **argv)
{
    int enable;
    char dns_str1[16], dns_str2[16], dns_str3[16];
    int dns1_valid = 0, dns2_valid = 0, dns3_valid = 0;
    ip_addr_t dns1, dns2, dns3;
    
    AT_CMD_PARSE_NUMBER(0, &enable);
    AT_CMD_PARSE_OPT_STRING(1, dns_str1, sizeof(dns_str1), dns1_valid);
    AT_CMD_PARSE_OPT_STRING(2, dns_str2, sizeof(dns_str2), dns2_valid);
    AT_CMD_PARSE_OPT_STRING(3, dns_str3, sizeof(dns_str3), dns3_valid);
    
    if (dns1_valid) dns_setserver(0, ipaddr_aton(dns_str1));
    if (dns2_valid) dns_setserver(1, ipaddr_aton(dns_str2));
    if (dns3_valid) dns_setserver(2, ipaddr_aton(dns_str3));
    
    return AT_RESULT_CODE_OK;
}
```

---

## 12. Working Code Examples

### Complete AT Module Setup Example

```c
// main.c - Complete AT module initialization for BL618

#include "at_main.h"
#include "at_core.h"
#include "at_port.h"
#include "at_base_cmd.h"
#include "at_wifi_cmd.h"
#include "at_ble_cmd.h"
#include "at_mqtt_cmd.h"
#include "at_http_cmd.h"
#include "at_net_cmd.h"

// Device operations - UART implementation
static int uart_init(void)
{
    // Initialize UART with configured baudrate
    // Set 115200 8N1 by default
    return 0;
}

static int uart_deinit(void)
{
    return 0;
}

static int uart_read(uint8_t *data, int len)
{
    // Blocking read from UART
    // Return actual bytes read
    return uart_read_bytes(data, len, portMAX_DELAY);
}

static int uart_write(uint8_t *data, int len)
{
    // Write to UART
    return uart_write_bytes(data, len);
}

static const at_device_ops device_ops = {
    .init_device = uart_init,
    .deinit_device = uart_deinit,
    .read_data = uart_read,
    .write_data = uart_write,
};

// Restore factory defaults function
static void at_restore_func(void)
{
    // Clear all configurations
    // Reset Wi-Fi settings
    // Reset BLE settings
    // Reset network settings
}

// Stop all services function
static void at_stop_func(void)
{
    // Disconnect Wi-Fi
    // Stop BLE
    // Close MQTT connections
    // Close network sockets
}

void at_task(void *param)
{
    uint8_t buf[512];
    int len;
    
    // Initialize AT module
    at_module_init();
    
    // Register device operations
    at->device_ops = device_ops;
    
    // Register restore/stop functions
    at_register_function(at_restore_func, at_stop_func);
    
    // Register all command groups
    at_base_cmd_regist();
    at_wifi_cmd_regist();
    at_ble_cmd_regist();
    at_mqtt_cmd_regist();
    at_http_cmd_regist();
    at_net_cmd_regist();
    
    // Main loop
    while (1) {
        len = uart_read(buf, sizeof(buf));
        if (len > 0) {
            at_cmd_input(buf, len);
        }
        vTaskDelay(pdMS_TO_TICKS(10));
    }
}
```

### Adding a Custom AT Command

```c
// Example: Adding a custom "HELLO" command
// File: at_custom_cmd.c

#include "at_main.h"
#include "at_core.h"

// Custom command: AT+HELLO="name"
// Returns: +HELLO:<greeting>

static int at_setup_cmd_hello(int argc, const char **argv)
{
    char name[32];
    
    AT_CMD_PARSE_STRING(0, name, sizeof(name));
    
    at_response_string("+HELLO:Hello, %s!\r\n", name);
    return AT_RESULT_CODE_OK;
}

static int at_query_cmd_hello(int argc, const char **argv)
{
    at_response_string("+HELLO:Usage: AT+HELLO=\"name\"\r\n");
    return AT_RESULT_CODE_OK;
}

static const at_cmd_struct at_custom_cmds[] = {
    {
        .at_name = "+HELLO",
        .at_query_cmd = at_query_cmd_hello,
        .at_setup_cmd = at_setup_cmd_hello,
        .at_exe_cmd = NULL,
        .para_num_min = 1,
        .para_num_max = 1,
    },
    { NULL }  // Terminator
};

bool at_custom_cmd_regist(void)
{
    return at_cmd_register(at_custom_cmds, 1) == 0;
}
```

### Parsing Arguments Example

```c
// Example: Complex command with multiple parameters
// AT+DEVICE=<type>,<id>,<name>,<enabled>[,<timeout>,<options>]

static int at_setup_cmd_device(int argc, const char **argv)
{
    int type, id, enabled;
    char name[64];
    int timeout = 1000;         // Default
    int options = 0;            // Default
    int timeout_valid = 0;
    int options_valid = 0;
    
    // Required parameters
    AT_CMD_PARSE_NUMBER(0, &type);
    AT_CMD_PARSE_NUMBER(1, &id);
    AT_CMD_PARSE_STRING(2, name, sizeof(name));
    AT_CMD_PARSE_NUMBER(3, &enabled);
    
    // Optional parameters
    AT_CMD_PARSE_OPT_NUMBER(4, &timeout, timeout_valid);
    AT_CMD_PARSE_OPT_NUMBER(5, &options, options_valid);
    
    // Validation
    if (type < 0 || type > 3) {
        return AT_RESULT_WITH_SUB_CODE(AT_SUB_PARA_VALUE_INVALID);
    }
    
    if (enabled != 0 && enabled != 1) {
        return AT_RESULT_WITH_SUB_CODE(AT_SUB_PARA_VALUE_INVALID);
    }
    
    // Execute command
    device_config_t config = {
        .type = type,
        .id = id,
        .name = name,
        .enabled = enabled,
        .timeout = timeout,
        .options = options,
    };
    
    if (device_set_config(&config) != 0) {
        return AT_RESULT_WITH_SUB_CODE(AT_SUB_CMD_EXEC_FAIL);
    }
    
    return AT_RESULT_CODE_OK;
}
```

### Response Examples

```c
// Standard responses
at_response_string(AT_CMD_MSG_OK);           // "\r\nOK\r\n"
at_response_string(AT_CMD_MSG_ERROR);      // "\r\nERROR\r\n"
at_response_string(AT_CMD_MSG_FAIL);         // "\r\nERROR\r\n"

// With data
at_response_string("+DEVICE:type=%d,id=%d\r\n", type, id);

// Error with sub-code
return AT_RESULT_WITH_SUB_CODE(AT_SUB_PARA_VALUE_INVALID);
// Returns: +CME ERROR:<code>

// With hex data
uint8_t mac[6] = {0xAA, 0xBB, 0xCC, 0xDD, 0xEE, 0xFF};
at_response_string("+MAC:\"%02X:%02X:%02X:%02X:%02X:%02X\"\r\n",
                   mac[0], mac[1], mac[2], mac[3], mac[4], mac[5]);
```

---

## File Locations Reference

| Header | Location |
|--------|----------|
| at_core.h | `/components/net/netbus/atmodule/include/at_core.h` |
| at_main.h | `/components/net/netbus/atmodule/include/at_main.h` |
| at_port.h | `/components/net/netbus/atmodule/include/at_port.h` |
| at_base_cmd.h | `/components/net/netbus/atmodule/include/at_base/at_base_cmd.h` |
| at_wifi_cmd.h | `/components/net/netbus/atmodule/include/at_wifi/at_wifi_cmd.h` |
| at_wifi_mgmr.h | `/components/net/netbus/atmodule/include/at_wifi/at_wifi_mgmr.h` |
| at_ble_cmd.h | `/components/net/netbus/atmodule/include/at_ble/at_ble_cmd.h` |
| at_mqtt_cmd.h | `/components/net/netbus/atmodule/include/at_mqtt/at_mqtt_cmd.h` |
| at_http_cmd.h | `/components/net/netbus/atmodule/include/at_http/at_http_cmd.h` |
| at_net_cmd.h | `/components/net/netbus/atmodule/include/at_net/at_net_cmd.h` |

| Source | Location |
|--------|----------|
| at_core.c | `/components/net/netbus/atmodule/src/at_core.c` |
| at_base_cmd.c | `/components/net/netbus/atmodule/src/at_base/at_base_cmd.c` |
| at_wifi_cmd.c | `/components/net/netbus/atmodule/src/at_wifi/at_wifi_cmd.c` |
| at_ble_cmd.c | `/components/net/netbus/atmodule/src/at_ble/at_ble_cmd.c` |
| at_mqtt_cmd.c | `/components/net/netbus/atmodule/src/at_mqtt/at_mqtt_cmd.c` |
| at_http_cmd.c | `/components/net/netbus/atmodule/src/at_http/at_http_cmd.c` |
| at_net_cmd.c | `/components/net/netbus/atmodule/src/at_net/at_net_cmd.c` |

---

## Appendix: AT Command Format Summary

```
Basic AT Command:     AT<command>
Test Command:         AT+<command>=?
Query Command:        AT+<command>?
Set Command:          AT+<command>=<param1>,<param2>,...
Execute Command:      AT+<command>

Examples:
  AT                          - Basic AT test
  AT+GMR                      - Get version (execute)
  AT+CWMODE?                  - Query Wi-Fi mode
  AT+CWMODE=1                 - Set Wi-Fi mode to STA
  AT+CWJAP="ssid","password"  - Connect to AP
```
