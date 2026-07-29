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
