# 串口编程指南

## 串口硬件配置

| 参数 | 值 | 说明 |
|------|-----|------|
| 波特率 | 115200 | 默认值，可通过AT+UARTCFG修改 |
| 数据位 | 8 | |
| 停止位 | 1 | |
| 校验位 | None | |
| 流控 | 无 | 默认关闭，可通过AT+UARTFLOWCONTROL开启 |

## 指令发送规则

### 帧格式

每条AT指令必须以 `\r\n` 结尾（十六进制 `0x0D 0x0A`）。

```
发送帧: <指令内容>\r\n
```

### 字符编码

| 内容 | 编码 | 说明 |
|------|------|------|
| 指令名 | ASCII | 不区分大小写，`AT+WJAP` 和 `at+wjap` 等效 |
| 参数 | ASCII | 数字、字母、符号均为ASCII字符 |
| HEX数据 | ASCII HEX | 如发送0x31 0x32，应发送ASCII字符串"3132" |
| 中文参数 | UTF-8 | 如蓝牙名称支持中文，需UTF-8编码 |

### 参数转义规则

| 场景 | 处理方式 | 示例 |
|------|----------|------|
| 参数含逗号 | 用双引号括起来 | `AT+MQTT=7,"topic,1",0,0,""` |
| 参数含双引号 | 加转义字符`\"` | `AT+WJAP="my\"ap",password` |
| 首/末参数为空 | 用双引号占位 | `AT+MQTT=7,"",0,0,""` |
| 参数中不能有 | `\n` | 会导致指令截断 |

### 指令长度限制

| 限制 | 值 | 说明 |
|------|-----|------|
| 单条指令最大长度 | 1023字节 | 包含指令名、参数、`\r\n` |
| 单行发送模式数据量 | ≈997字节 | 1023 - 指令格式开销 |
| HEX单行发送数据量 | ≈498字节 | 997 / 2（HEX两字符一字节） |
| 长数据模式 | 无限制 | 使用`>`提示符分帧发送 |

## 指令间时序要求

### 普通指令

```
发送: AT+WMODE=1,1\r\n
等待: \r\nOK\r\n          ← 收到OK后才能发下一条
发送: AT+WJAP=test,12345678\r\n
等待: \r\nOK\r\n
```

**规则：必须等待上一条指令响应后才能发送下一条。**

### 异步指令

WiFi连接、MQTT连接等操作是异步的，`OK`仅表示任务启动。

```
发送: AT+WJAP=test,12345678\r\n
收到: \r\nOK\r\n                    ← 任务已启动，但连接未完成
      ... (等待数秒)
收到: +EVENT:WIFI_CONNECT\r\n       ← WiFi物理连接成功
收到: +EVENT:WIFI_GOT_IP\r\n        ← 已获取IP，现在可以发后续指令
```

### 数据输入模式

部分指令（SOCKETSEND、MQTTPUBRAW、SSLCRET等）使用`>`提示符进入数据输入模式。

```
发送: AT+SOCKETSEND=1,5\r\n
收到: >                              ← 提示符，开始输入数据
发送: hello                           ← 输入5字节数据（不需要\r\n）
收到: \r\nOK\r\n                     ← 数据发送完成
```

**注意：** 收到`>`后，直接发送原始数据，不需要加`\r\n`结尾。数据长度必须与指令中指定的length一致。

## 响应解析规则

### 响应帧结构

```
\r\n<响应内容>\r\n
```

每条响应都以`\r\n`开头和结尾。

### 响应类型判断

| 响应内容 | 类型 | 含义 |
|----------|------|------|
| `\r\nOK\r\n` | 成功 | 指令执行成功 |
| `\r\n+<CMD>:<code>\r\nERROR\r\n` | 错误 | 指令执行失败，code为错误码 |
| `\r\n+<CMD>:<data>\r\nOK\r\n` | 查询结果 | 查询指令返回数据 |
| `\r\n+EVENT:<event>\r\n` | URC事件 | 模组主动上报的事件 |
| `\r\nUnknowncmd:<cmd>\r\n` | 未知指令 | 指令不存在 |
| `>` | 数据提示 | 进入数据输入模式 |

### URC与响应的区分

URC事件可能在任何时候出现，甚至夹在指令响应中间：

```
发送: AT+MQTTSUB=topic,0\r\n
收到: \r\nOK\r\n                          ← 指令响应
收到: +EVENT:MQTT_SUB,topic,5,hello\r\n   ← URC事件（随时可能出现）
发送: AT+MQTTPUB=topic,0,0,test\r\n
收到: \r\nOK\r\n
```

**编程要点：** 解析响应时，需要区分指令响应和URC事件。URC以`+EVENT:`或`+DATA:`等前缀开头。

## 参考代码框架

### 伪代码：发送指令并等待响应

```
function sendATCommand(cmd, timeout_ms):
    // 1. 发送指令（加\r\n结尾）
    serial.write(cmd + "\r\n")

    // 2. 等待响应（带超时）
    response = serial.readUntil(timeout_ms)

    // 3. 解析响应
    if response contains "OK":
        return SUCCESS
    else if response contains "ERROR":
        errorCode = parseErrorCode(response)  // +CMD:<code>
        return ERROR(errorCode)
    else if response contains "Unknowncmd":
        return UNKNOWN_CMD
    else:
        return TIMEOUT
```

### 伪代码：发送长数据

```
function sendLongData(conId, data):
    length = len(data)

    // 1. 发送长度指令
    serial.write("AT+SOCKETSEND=" + conId + "," + length + "\r\n")

    // 2. 等待 '>' 提示符
    prompt = serial.readUntil(3000)
    if prompt != ">":
        return ERROR("未收到数据提示符")

    // 3. 发送原始数据（不加\r\n）
    serial.writeRaw(data)

    // 4. 等待 OK
    response = serial.readUntil(timeout_ms)
    if response contains "OK":
        return SUCCESS
```

### 伪代码：异步指令等待URC

```
function waitForURC(urcPrefix, timeout_ms):
    startTime = now()

    while (now() - startTime) < timeout_ms:
        line = serial.readLine()

        // 跳过空行
        if line is empty:
            continue

        // 检查是否为目标URC
        if line startsWith urcPrefix:
            return line

        // 其他URC存入队列（不影响等待）
        if line startsWith "+EVENT:" or line startsWith "+DATA:":
            urcQueue.push(line)

    return TIMEOUT
```

### 伪代码：WiFi连接完整流程

```
function connectWiFi(ssid, password):
    // 1. 测试AT
    if sendATCommand("AT") != SUCCESS:
        return ERROR("AT测试失败")

    // 2. 设置STA模式
    if sendATCommand("AT+WMODE=1,1") != SUCCESS:
        return ERROR("设置WiFi模式失败")

    // 3. 连接WiFi（异步）
    if sendATCommand("AT+WJAP=" + ssid + "," + password) != SUCCESS:
        return ERROR("WiFi连接指令失败")

    // 4. 等待连接成功URC（超时30秒）
    urc = waitForURC("+EVENT:WIFI_GOT_IP", 30000)
    if urc == TIMEOUT:
        return ERROR("WiFi连接超时")

    // 5. 确认连接状态
    result = sendATCommand("AT+STAINFO?")
    if "3" in result:  // status=3 表示已连接已获取IP
        return SUCCESS
    else:
        return ERROR("WiFi连接状态异常")
```

### 伪代码：MQTT连接完整流程

```
function connectMQTT(host, port, clientId, username, password):
    // 前置：WiFi已连接

    // 1. 设置MQTT参数
    sendATCommand("AT+MQTT=1," + host)       // 服务器
    sendATCommand("AT+MQTT=2," + port)       // 端口
    sendATCommand("AT+MQTT=3,1")             // TCP连接
    sendATCommand("AT+MQTT=4," + clientId)   // 客户端ID
    sendATCommand("AT+MQTT=5," + username)   // 用户名
    sendATCommand("AT+MQTT=6," + password)   // 密码

    // 2. 发起连接（异步）
    if sendATCommand("AT+MQTT") != SUCCESS:
        return ERROR("MQTT连接指令失败")

    // 3. 等待连接成功URC（超时15秒）
    urc = waitForURC("+EVENT:MQTT_CONNECT", 15000)
    if urc == TIMEOUT:
        return ERROR("MQTT连接超时")

    return SUCCESS
```

### 伪代码：BLE透传流程

```
function setupBLETransparent(deviceName):
    // 1. 关闭蓝牙
    sendATCommand("AT+BLEMODE=9")

    // 2. 确认关闭
    result = sendATCommand("AT+BLESTATE?")
    if "0" not in result:
        return ERROR("蓝牙未关闭")

    // 3. 设置从机模式
    sendATCommand("AT+BLEMODE=0")

    // 4. 设置名称
    sendATCommand("AT+BLENAME=" + deviceName)

    // 5. 开启广播
    sendATCommand("AT+BLEADVEN=1")

    // 6. 等待手机连接
    urc = waitForURC("+EVENT:BLE_CONNECTED", 60000)
    if urc == TIMEOUT:
        return ERROR("等待蓝牙连接超时")

    // 7. 进入透传模式
    sendATCommand("AT+TRANSENTER")

    return SUCCESS  // 现在可以透传收发数据
```

## 常见编程错误

| 错误 | 现象 | 正确做法 |
|------|------|----------|
| 未等响应就发下一条 | 模组丢指令或乱序 | 每条指令等待OK/ERROR后再发下一条 |
| 长数据模式未等`>` | 数据丢失 | 收到`>`提示符后再输入数据 |
| `\r\n`遗漏 | 模组不响应 | 每条指令必须以`\r\n`结尾 |
| 数据长度不匹配 | 发送失败或截断 | BLESEND/SOCKETSEND的len参数必须与实际数据字节数一致 |
| 异步指令当同步处理 | 误判连接状态 | WiFi/MQTT/BLE连接需等待URC确认 |
| URC和响应混在一起解析 | 解析混乱 | 用前缀区分：`OK`/`ERROR`为响应，`+EVENT:`/`+DATA:`为URC |
| 指令名大小写写死 | 无影响但不规范 | 指令名不区分大小写，但建议统一大写 |
| 未处理超时 | 程序卡死 | 所有等待操作加超时机制 |

## C语言参考实现

### 串口发送基础

```c
#include <string.h>
#include <stdio.h>

// 串口发送AT指令（自动追加\r\n）
void at_send(const char *cmd)
{
    char buf[512];
    snprintf(buf, sizeof(buf), "%s\r\n", cmd);
    uart_write(buf, strlen(buf));  // 平台相关：串口发送
}

// 串口发送原始数据（不追加\r\n，用于长数据模式）
void at_send_raw(const uint8_t *data, uint16_t len)
{
    uart_write(data, len);
}
```

### 响应读取与解析

```c
typedef enum {
    AT_RESP_OK = 0,       // 收到OK
    AT_RESP_ERROR,        // 收到ERROR
    AT_RESP_TIMEOUT,      // 超时
    AT_RESP_DATA,         // 收到查询数据
} at_resp_t;

// 读取一行响应（以\r\n为分隔），超时返回NULL
// buf: 接收缓冲区  buf_size: 缓冲区大小  timeout_ms: 超时毫秒
const char *at_readline(char *buf, uint16_t buf_size, uint32_t timeout_ms)
{
    uint16_t idx = 0;
    uint32_t start = get_tick_ms();  // 平台相关：获取系统tick

    while ((get_tick_ms() - start) < timeout_ms) {
        uint8_t ch;
        if (uart_read(&ch, 1, 10) == 1) {  // 平台相关：串口接收，10ms超时
            if (ch == '\n' && idx > 0 && buf[idx - 1] == '\r') {
                buf[idx - 1] = '\0';  // 去掉\r\n
                return buf;
            }
            if (idx < buf_size - 1) {
                buf[idx++] = ch;
            }
        }
    }
    return NULL;  // 超时
}

// 解析响应类型
at_resp_t at_parse_response(const char *line)
{
    if (line == NULL)               return AT_RESP_TIMEOUT;
    if (strstr(line, "OK"))         return AT_RESP_OK;
    if (strstr(line, "ERROR"))      return AT_RESP_ERROR;
    if (line[0] == '+')             return AT_RESP_DATA;
    return AT_RESP_DATA;
}
```

### 发送指令并等待OK

```c
// 发送AT指令并等待OK/ERROR响应
// 返回: AT_RESP_OK / AT_RESP_ERROR / AT_RESP_TIMEOUT
at_resp_t at_cmd(const char *cmd, uint32_t timeout_ms)
{
    char buf[512];
    at_send(cmd);

    while (1) {
        if (at_readline(buf, sizeof(buf), timeout_ms) == NULL) {
            return AT_RESP_TIMEOUT;
        }

        // 跳过URC事件（+EVENT: / +DATA:）
        if (strncmp(buf, "+EVENT:", 7) == 0 || strncmp(buf, "+DATA:", 6) == 0) {
            urc_handler(buf);  // 处理URC（见下方）
            continue;
        }

        return at_parse_response(buf);
    }
}
```

### 查询指令（提取响应数据）

```c
// 发送查询指令，提取OK之前的响应行
// 返回: AT_RESP_OK 并将响应内容存入 resp_buf
at_resp_t at_query(const char *cmd, char *resp_buf, uint16_t resp_size, uint32_t timeout_ms)
{
    char buf[512];
    resp_buf[0] = '\0';
    at_send(cmd);

    while (1) {
        if (at_readline(buf, sizeof(buf), timeout_ms) == NULL) {
            return AT_RESP_TIMEOUT;
        }

        if (strncmp(buf, "+EVENT:", 7) == 0 || strncmp(buf, "+DATA:", 6) == 0) {
            urc_handler(buf);
            continue;
        }

        if (strstr(buf, "OK")) {
            return AT_RESP_OK;
        }
        if (strstr(buf, "ERROR")) {
            return AT_RESP_ERROR;
        }

        // 保存响应数据（去掉前导\r\n）
        const char *data = buf;
        while (*data == '\r' || *data == '\n') data++;
        snprintf(resp_buf, resp_size, "%s", data);
    }
}
```

### URC事件处理

```c
// URC事件回调注册
typedef void (*urc_callback_t)(const char *urc_line);

static urc_callback_t g_urc_cb = NULL;

void at_set_urc_callback(urc_callback_t cb)
{
    g_urc_cb = cb;
}

// URC处理（在指令等待循环中调用）
static void urc_handler(const char *urc_line)
{
    if (g_urc_cb) {
        g_urc_cb(urc_line);
    }

    // 也可以在这里直接处理关键URC
    if (strstr(urc_line, "+EVENT:WIFI_GOT_IP")) {
        // WiFi已获取IP
        wifi_connected = 1;
    } else if (strstr(urc_line, "+EVENT:MQTT_CONNECT")) {
        // MQTT连接成功
        mqtt_connected = 1;
    } else if (strstr(urc_line, "+EVENT:BLE_CONNECTED")) {
        // 蓝牙已连接
        ble_connected = 1;
    }
}
```

### 等待指定URC事件

```c
// 等待包含指定前缀的URC事件
// 返回: 0=成功  -1=超时
int at_wait_urc(const char *urc_prefix, uint32_t timeout_ms)
{
    char buf[512];
    uint32_t start = get_tick_ms();

    while ((get_tick_ms() - start) < timeout_ms) {
        if (at_readline(buf, sizeof(buf), 500) == NULL) {
            continue;  // 单次读取超时，继续等
        }

        // 处理所有URC
        if (strncmp(buf, "+EVENT:", 7) == 0 || strncmp(buf, "+DATA:", 6) == 0) {
            urc_handler(buf);
            if (strstr(buf, urc_prefix)) {
                return 0;  // 找到目标URC
            }
        }
    }
    return -1;  // 超时
}
```

### 长数据发送（等待`>`提示符）

```c
// 发送需要>提示符的长数据指令
// 例: at_send_with_data("AT+SOCKETSEND=1,5", (uint8_t*)"hello", 5, 5000)
int at_send_with_data(const char *cmd, const uint8_t *data, uint16_t len, uint32_t timeout_ms)
{
    char buf[16];
    at_send(cmd);

    // 等待 '>' 提示符
    uint32_t start = get_tick_ms();
    int got_prompt = 0;
    while ((get_tick_ms() - start) < timeout_ms) {
        uint8_t ch;
        if (uart_read(&ch, 1, 10) == 1) {
            if (ch == '>') {
                got_prompt = 1;
                break;
            }
        }
    }
    if (!got_prompt) return -1;

    // 发送原始数据（不加\r\n）
    at_send_raw(data, len);

    // 等待 OK
    return (at_cmd("", timeout_ms) == AT_RESP_OK) ? 0 : -1;
}
```

### 完整示例：WiFi连接

```c
// 返回: 0=成功  负值=失败
int wifi_connect(const char *ssid, const char *password)
{
    char cmd[128];
    char resp[256];

    // 1. 测试AT
    if (at_cmd("AT", 1000) != AT_RESP_OK) {
        printf("AT测试失败\n");
        return -1;
    }

    // 2. 设置STA模式
    if (at_cmd("AT+WMODE=1,1", 2000) != AT_RESP_OK) {
        printf("设置WiFi模式失败\n");
        return -2;
    }

    // 3. 连接WiFi
    snprintf(cmd, sizeof(cmd), "AT+WJAP=%s,%s", ssid, password);
    if (at_cmd(cmd, 5000) != AT_RESP_OK) {
        printf("WiFi连接指令失败\n");
        return -3;
    }

    // 4. 等待获取IP（异步，超时30秒）
    if (at_wait_urc("+EVENT:WIFI_GOT_IP", 30000) != 0) {
        printf("WiFi连接超时\n");
        return -4;
    }

    // 5. 确认连接状态
    at_query("AT+STAINFO?", resp, sizeof(resp), 2000);
    if (strstr(resp, "+STAINFO:3") == NULL) {
        printf("WiFi状态异常: %s\n", resp);
        return -5;
    }

    printf("WiFi连接成功\n");
    return 0;
}
```

### 完整示例：MQTT连接

```c
// 前置：WiFi已连接
// 返回: 0=成功  负值=失败
int mqtt_connect(const char *host, int port, const char *client_id,
                 const char *username, const char *password)
{
    char cmd[256];

    // 1. 设置MQTT参数
    snprintf(cmd, sizeof(cmd), "AT+MQTT=1,%s", host);
    at_cmd(cmd, 2000);

    snprintf(cmd, sizeof(cmd), "AT+MQTT=2,%d", port);
    at_cmd(cmd, 2000);

    at_cmd("AT+MQTT=3,1", 2000);  // TCP连接

    snprintf(cmd, sizeof(cmd), "AT+MQTT=4,%s", client_id);
    at_cmd(cmd, 2000);

    snprintf(cmd, sizeof(cmd), "AT+MQTT=5,%s", username);
    at_cmd(cmd, 2000);

    snprintf(cmd, sizeof(cmd), "AT+MQTT=6,%s", password);
    at_cmd(cmd, 2000);

    // 2. 发起连接
    if (at_cmd("AT+MQTT", 2000) != AT_RESP_OK) {
        printf("MQTT连接指令失败\n");
        return -1;
    }

    // 3. 等待连接成功URC
    if (at_wait_urc("+EVENT:MQTT_CONNECT", 15000) != 0) {
        printf("MQTT连接超时\n");
        return -2;
    }

    printf("MQTT连接成功\n");
    return 0;
}

// MQTT订阅主题
int mqtt_subscribe(const char *topic, int qos)
{
    char cmd[256];
    snprintf(cmd, sizeof(cmd), "AT+MQTTSUB=%s,%d", topic, qos);
    return (at_cmd(cmd, 3000) == AT_RESP_OK) ? 0 : -1;
}

// MQTT发布消息
int mqtt_publish(const char *topic, int qos, int retain, const char *payload)
{
    char cmd[512];
    snprintf(cmd, sizeof(cmd), "AT+MQTTPUB=%s,%d,%d,%s", topic, qos, retain, payload);
    return (at_cmd(cmd, 3000) == AT_RESP_OK) ? 0 : -1;
}
```

### 完整示例：BLE透传

```c
// 返回: 0=成功  负值=失败
int ble_transparent_setup(const char *device_name)
{
    char cmd[128];

    // 1. 关闭蓝牙
    at_cmd("AT+BLEMODE=9", 2000);

    // 2. 确认关闭
    char resp[64];
    at_query("AT+BLESTATE?", resp, sizeof(resp), 2000);
    if (strstr(resp, "+BLESTATE:0") == NULL) {
        printf("蓝牙未关闭\n");
        return -1;
    }

    // 3. 设置从机模式
    at_cmd("AT+BLEMODE=0", 2000);

    // 4. 设置名称
    snprintf(cmd, sizeof(cmd), "AT+BLENAME=%s", device_name);
    at_cmd(cmd, 2000);

    // 5. 开启广播
    at_cmd("AT+BLEADVEN=1", 2000);

    // 6. 等待手机连接（超时60秒）
    if (at_wait_urc("+EVENT:BLE_CONNECTED", 60000) != 0) {
        printf("等待蓝牙连接超时\n");
        return -2;
    }

    // 7. 进入透传模式
    at_cmd("AT+TRANSENTER", 2000);

    printf("蓝牙透传已建立\n");
    return 0;
}
```

### 完整示例：Socket TCP通信

```c
static int g_con_id = -1;  // Socket连接ID

// 创建TCP Client
int tcp_connect(const char *host, int port)
{
    char cmd[256];
    char resp[128];

    snprintf(cmd, sizeof(cmd), "AT+SOCKET=4,%s,%d", host, port);
    at_send(cmd);

    // 等待 connectsuccessConID=x
    uint32_t start = get_tick_ms();
    while ((get_tick_ms() - start) < 10000) {
        if (at_readline(resp, sizeof(resp), 1000) == NULL) continue;

        if (strstr(resp, "connectsuccessConID=")) {
            g_con_id = atoi(strstr(resp, "=") + 1);
            printf("TCP连接成功, ConID=%d\n", g_con_id);
            return 0;
        }
        if (strstr(resp, "ERROR")) {
            printf("TCP连接失败\n");
            return -1;
        }
    }
    return -2;  // 超时
}

// 发送数据
int tcp_send(const uint8_t *data, uint16_t len)
{
    char cmd[64];
    snprintf(cmd, sizeof(cmd), "AT+SOCKETSEND=%d,%d", g_con_id, len);
    return at_send_with_data(cmd, data, len, 5000);
}

// 读取数据（被动模式）
int tcp_recv(char *buf, uint16_t buf_size, uint32_t timeout_ms)
{
    char cmd[32];
    char resp[1500];

    snprintf(cmd, sizeof(cmd), "AT+SOCKETREAD=%d", g_con_id);
    at_send(cmd);

    // 等待 +SOCKETREAD:ConID,len,data
    uint32_t start = get_tick_ms();
    while ((get_tick_ms() - start) < timeout_ms) {
        if (at_readline(resp, sizeof(resp), 1000) == NULL) continue;

        if (strncmp(resp, "+SOCKETREAD:", 12) == 0) {
            // 解析: +SOCKETREAD:1,5,hello
            char *p = strchr(resp, ',');  // 跳过ConID
            if (p) {
                p++;  // 跳过逗号
                // p 指向 "len,data"
                char *comma = strchr(p, ',');
                if (comma) {
                    uint16_t data_len = atoi(p);
                    snprintf(buf, buf_size, "%s", comma + 1);
                    return data_len;
                }
            }
        }
    }
    return -1;  // 超时无数据
}
```

### 主循环示例

```c
int main(void)
{
    uart_init(115200);  // 初始化串口

    // 等待模组启动（检测ready）
    char buf[256];
    while (1) {
        if (at_readline(buf, sizeof(buf), 10000)) {
            if (strstr(buf, "ready")) break;
        }
    }
    printf("模组已启动\n");

    // 连接WiFi
    if (wifi_connect("MySSID", "MyPassword") != 0) {
        printf("WiFi连接失败\n");
        return -1;
    }

    // 连接MQTT
    if (mqtt_connect("192.168.1.100", 1883, "device001", "user", "pass") != 0) {
        printf("MQTT连接失败\n");
        return -2;
    }

    // 订阅主题
    mqtt_subscribe("device/cmd", 0);

    // 主循环：上报数据 + 处理下发
    while (1) {
        // 上报属性
        mqtt_publish("device/property", 0, 0, "{\"temp\":25.6}");

        // 检查是否有下发数据（URC已在at_cmd内部处理）
        delay_ms(5000);
    }
}
```

> 💡 以上代码基于Combo模组AT指令协议实现，可直接移植到STM32/ESP32/BL602等嵌入式平台。需根据实际平台替换 `uart_write()`、`uart_read()`、`get_tick_ms()` 等硬件相关函数。
