---
name: combo-at-commands
description: Ai-Thinker Combo模组AT指令开发助手。当用户需要使用AT指令开发IoT功能、查询AT指令用法、排查AT指令问题、规划AT指令执行流程时使用。支持WiFi、MQTT、Socket、BLE、HTTP、SNTP、GPIO、PWM等全功能AT指令指导。
---

# Combo模组AT指令开发助手

## 适用范围

本技能适用于安信可(Ai-Thinker)Combo框架AT指令集（版本V4.18P_3.8.0），支持以下模组系列：
- **Ai-WB2系列** (BL602芯片)：WiFi 4 + BLE 5.0
- **Ai-M61/M62系列** (BL616/BL618芯片)：WiFi 6 + BLE 5.0
- **BW16/BW20系列** (瑞昱RTL8720)：WiFi 5 + BLE 5.0
- **PB/TB系列**

## 核心原则

1. **指令格式严格性**：所有AT指令以`\r\n`结尾，指令名不区分大小写
2. **响应判断**：成功返回`OK`，失败返回`ERROR`（含错误码）
3. **异步操作**：WiFi连接、MQTT连接等为异步操作，OK仅表示任务启动，需通过URC事件或查询指令确认状态
4. **参数校验优先**：执行指令前先用`?`查询当前状态，确认参数正确后再设置

## 使用场景

### 场景1：用户需要完成某个功能开发

当用户描述一个功能需求时，按以下流程提供指导：

1. **拆解功能步骤**：将功能分解为按顺序执行的AT指令
2. **列出完整指令序列**：包括每条指令的参数说明
3. **说明预期响应**：每条指令执行后应收到的正确响应
4. **标注关键检查点**：哪些步骤需要等待URC事件或查询确认
5. **提供错误处理**：常见错误及解决方法

### 场景2：用户遇到AT指令问题

按以下排查流程：

1. **确认指令格式**：检查指令拼写、参数数量、参数类型
2. **查询当前状态**：使用`?`查询指令确认当前配置
3. **查阅错误码**：根据错误码定位具体问题（见参考文档）
4. **检查前置条件**：是否需要先连接WiFi、是否需要特定模式
5. **提供解决方案**：给出正确的指令序列

### 场景3：用户查询指令用法

1. **给出指令完整格式**：包括所有参数和可选参数
2. **说明每个参数的含义和取值范围**
3. **提供典型使用示例**
4. **列出注意事项和限制**
5. **推荐关联指令**：通常一起使用的其他指令

## 指令分类速查

### 基础指令
| 指令 | 功能 |
|------|------|
| `AT` | 测试AT框架是否正常 |
| `AT+HELP` | 查看所有可用指令列表 |
| `AT+RST` | 重启模组 |
| `AT+RESTORE` | 恢复出厂设置（三元组、IO映射除外） |
| `ATE0/ATE1` | 关闭/打开回显 |
| `AT+GMR` | 查询版本信息 |
| `AT+SYSMSG` | URC打印掩码控制（透传模式调试必备） |
| `AT+SLEEP` | 设置睡眠模式 |
| `AT+UARTCFG` | 串口配置（波特率等） |
| `AT+OTA` | 在线升级 |
| `AT+FLASHID` | 查询FLASH ID |
| `AT+TICKLESS` | 浅睡眠AP beacon监听间隔 |

> 详见 [basic-commands.md](./references/basic-commands.md)

### WiFi指令
| 指令 | 功能 |
|------|------|
| `AT+WMODE` | 设置WiFi工作模式(STA/AP/AP+STA) |
| `AT+WJAP` | 连接指定AP |
| `AT+WAP` | 设置AP热点参数 |
| `AT+WAPINFO` | 查询AP信息（含客户端列表） |
| `AT+WSCAN` | 扫描WiFi列表 |
| `AT+WSCANACTIVE` | 主动模式扫描指定SSID |
| `AT+WSDHCP` | 设置STA模式DHCP/静态IP |
| `AT+WAPDHCP` | 设置AP模式DHCP参数 |
| `AT+WAUTOCONN` | 设置上电自动重连 |
| `AT+WDISCONNECT` | 断开WiFi连接 |
| `AT+WRSSI` | 查询WiFi信号强度 |
| `AT+PING` | Ping测试 |
| `AT+WCONFIG` | 手机配网(SmartConfig/AirKiss/BLE配网) |
| `AT+STAINFO` | 查询WiFi连接信息 |
| `AT+WJEAP` | 连接企业认证热点 |
| `AT+WCOUNTRY` | WiFi国家码 |
| `AT+WSCANOPT` | 筛选扫描显示信息 |
| `AT+CIPSTAMAC_DEF` | 查询/设置WiFi Station MAC地址 |
| `AT+BLUFISEND` | 发送蓝牙配网自定义数据 |

> 详见 [wifi-commands.md](./references/wifi-commands.md)

### Socket/TCP-IP指令
| 指令 | 功能 |
|------|------|
| `AT+SOCKET` | 创建socket连接(TCP/UDP/SSL) |
| `AT+SOCKETSEND` | 长数据模式发送 |
| `AT+SOCKETSENDLINE` | 单行模式发送 |
| `AT+SOCKETSENDHEX` | HEX模式发送 |
| `AT+SOCKETREAD` | 读取socket数据 |
| `AT+SOCKETDEL` | 删除socket连接 |
| `AT+SOCKETTT` | 进入透传模式 |
| `AT+SOCKETAUTOTT` | 配置上电自动透传 |
| `AT+SOCKETRECVCFG` | 设置接收模式(主动/被动) |
| `AT+SSLCRET` | SSL证书配置 |
| `AT+WDOMAIN` | DNS域名解析 |
| `AT+WDNS` | DNS服务器设置 |

> 详见 [socket-commands.md](./references/socket-commands.md)

### MQTT指令
| 指令 | 功能 |
|------|------|
| `AT+MQTT` | 配置MQTT参数并连接 |
| `AT+MQTT?` | 查询MQTT连接状态和参数 |
| `AT+MQTTPUB` | 发布MQTT消息 |
| `AT+MQTTPUBRAW` | 发布指定长度MQTT消息 |
| `AT+MQTTSUB` | 订阅主题 |
| `AT+MQTTUNSUB` | 取消订阅 |
| `AT+MQTTDISCONN` | 断开MQTT连接 |
| `AT+MQTTVER` | 设置MQTT版本(3.1/3.1.1) |
| `AT+MQTTBUF` | 设置收发buf大小 |
| `AT+MQTTKEEPALIVE` | 设置心跳间隔 |
| `AT+MQTTCRET` | MQTT SSL证书配置 |

> 详见 [mqtt-commands.md](./references/mqtt-commands.md)

### HTTP指令
| 指令 | 功能 |
|------|------|
| `AT+HTTPCLIENTLINE` | 单行模式HTTP/HTTPS请求 |
| `AT+HTTPRAW` | 长数据模式HTTP/HTTPS请求 |

> 详见 [http-commands.md](./references/http-commands.md)

### BLE蓝牙指令
| 指令 | 功能 |
|------|------|
| `AT+BLEMODE` | 设置蓝牙模式(从机/主机/iBeacon/关闭) |
| `AT+BLENAME` | 设置蓝牙名称 |
| `AT+BLEMAC` | 查询/设置蓝牙MAC |
| `AT+BLESTATE` | 查询蓝牙连接状态 |
| `AT+BLERFPWR` | 蓝牙发射功率 |
| `AT+BLEMTU` | 设置蓝牙MTU |
| `AT+BLEAUTH` | 设置配对码 |
| `AT+BLECONINTV` | 蓝牙连接间隔 |
| `AT+BLESEND` | 蓝牙透传发送数据 |
| `AT+BLESENDRAW` | 蓝牙透传发送HEX数据 |
| `AT+BLESERUUID` | 设置透传服务UUID |
| `AT+BLETXUUID` | 设置TX特征UUID |
| `AT+BLERXUUID` | 设置RX特征UUID |
| `AT+TRANSENTER` | 进入蓝牙透传模式 |
| `AT+BLEADVEN` | 启停蓝牙广播 |
| `AT+BLEADVINTV` | 蓝牙广播间隔 |
| `AT+BLEADVDATA` | 蓝牙广播数据 |
| `AT+BLESCAN` | 主机模式扫描 |
| `AT+BLECONNECT` | 主机连接指定蓝牙 |
| `AT+BLEAUTOCON` | 设置自动连接 |
| `AT+BLEDISCON` | 断开蓝牙连接 |
| `AT+BLEDISAUTOCON` | 取消自动扫描连接 |
| `AT+BLEIBCNUUID` | iBeacon UUID |
| `AT+BLEIBCNDATA` | iBeacon数据 |
| `AT+PROVISION` | MESH配网使能 |
| `AT+MESHSEND` | MESH发送数据 |
| `AT+MESHADDR` | 查询MESH节点地址 |
| `AT+MESHSTATE` | 查询MESH配网状态 |
| `AT+AliGenie` | 天猫精灵三元组 |
| `AT+SEND2ALI` | 天猫精灵上报数据 |

> 详见 [ble-commands.md](./references/ble-commands.md)

### GPIO/PWM控制指令
| 指令 | 功能 |
|------|------|
| `AT+SYSIOMAP` | 设置IO引脚映射表 |
| `AT+SYSGPIOWRITE` | 设置GPIO输出电平 |
| `AT+SYSGPIOREAD` | 读取GPIO电平 |
| `AT+PWMCFG` | 配置PWM(寄存器单位) |
| `AT+PWMCFGS` | 配置PWM(us/百分比单位，推荐) |
| `AT+PWMDUTYSET` | 更新PWM占空比(寄存器单位) |
| `AT+PWMDUTYSETS` | 更新PWM占空比(百分比，推荐) |
| `AT+PWMSTOP` | 关闭PWM |

> 详见 [gpio-pwm-commands.md](./references/gpio-pwm-commands.md)

### SNTP时间指令
| 指令 | 功能 |
|------|------|
| `AT+SNTPTIMECFG` | 启停SNTP服务、设置时区和服务器 |
| `AT+SNTPTIME` | 查询SNTP时间 |
| `AT+SNTPINTV` | 设置SNTP刷新间隔 |

> 详见 [sntp-commands.md](./references/sntp-commands.md)

### 产测指令
| 指令 | 功能 |
|------|------|
| `AT+NodeMCUTEST` | 开发板测试使能 |
| `AT+LEDTEST` | LED测试 |

> 详见 [test-commands.md](./references/test-commands.md)

## 常用功能开发流程

> **格式说明**：每条指令给出「发送 → 预期响应」，`⚠` 标注关键检查点，`💡` 标注提示信息。

### 流程1：WiFi连接 + MQTT通信

| 步骤 | 指令 | 预期响应 | 说明 |
|:----:|------|----------|------|
| 1 | `AT` | `OK` | 测试AT框架是否正常 |
| 2 | `AT+WMODE=1,1` | `OK` | 设置STA模式，参数`=模式,保存flash` |
| 3 | `AT+WJAP=SSID,密码` | `OK` | 连接WiFi热点 |
| ⚠ | *等待URC* | `+EVENT:WIFI_CONNECT` | WiFi物理连接成功 |
| ⚠ | *等待URC* | `+EVENT:WIFI_GOT_IP` | 已获取IP地址 |
| 4 | `AT+STAINFO?` | `+STAINFO:3` | 确认status=3（已连接+已获取IP） |
| 5 | `AT+MQTT=1,服务器地址` | `OK` | 设置MQTT服务器IP或域名 |
| | `AT+MQTT=2,端口号` | `OK` | 设置端口（如1883） |
| | `AT+MQTT=3,1` | `OK` | 连接方式：1=TCP，2=SSL |
| | `AT+MQTT=4,client_id` | `OK` | 设置客户端ID |
| | `AT+MQTT=5,用户名` | `OK` | 设置用户名（最大63字节） |
| | `AT+MQTT=6,密码` | `OK` | 设置密码（最大63字节） |
| 6 | `AT+MQTT` | `OK` | 发起连接（异步，OK仅表示任务启动） |
| ⚠ | *等待URC* | `+EVENT:MQTT_CONNECT` | MQTT连接成功 |
| 7 | `AT+MQTTSUB=topic,0` | `OK` | 订阅主题，QOS=0 |
| 8 | `AT+MQTTPUB=topic,0,0,data` | `OK` | 发布消息（topic,qos,retain,payload） |
| 9 | *接收URC* | `+EVENT:MQTT_SUB,topic,len,data` | 消息自动推送到串口 |

### 流程2：WiFi连接 + TCP通信

> 前置：WiFi已连接（参考流程1步骤1-4）

| 步骤 | 指令 | 预期响应 | 说明 |
|:----:|------|----------|------|
| 1 | `AT+SOCKET=4,服务器IP,端口` | `connectsuccessConID=1` | 创建TCP Client，返回ConID |
| 2a | `AT+SOCKETSEND=1,5` | `>` | 长数据模式：ConID=1，发送5字节 |
| | *输入数据* `hello` | `OK` | 收到`>`后输入数据，满5字节自动发送 |
| 2b | `AT+SOCKETSENDLINE=1,5,hello` | `OK` | 单行模式（替代，适合小数据，最大1023字节） |
| 3 | `AT+SOCKETRECVCFG=1` | `OK` | 切换到主动接收模式（收到数据直接打印） |
| 4 | *接收URC* | `+EVENT:SocketDown,1,len,data` | 主动模式自动打印；被动模式用`AT+SOCKETREAD=1`读取 |
| 5 | `AT+SOCKETTT` | `>` | 进入透传模式（仅限单连接） |
| | `+++` | `OK` | 退出透传 |

### 流程3：BLE蓝牙透传

> ⚠ **关键前置条件**：名称、UUID、广播、功率、连接间隔、配对码等参数**必须在蓝牙关闭状态下设置**

| 步骤 | 指令 | 预期响应 | 说明 |
|:----:|------|----------|------|
| 1 | `AT+BLEMODE=9` | `OK` | 先关闭蓝牙（9=关闭） |
| | `AT+BLESTATE?` | `+BLESTATE:0` | 确认未连接状态 |
| 2 | `AT+BLEMODE=0` | `OK` | 设置为从机模式（0=从机） |
| 3 | `AT+BLENAME=设备名` | `OK` | 设置蓝牙名称（UTF-8，支持中文） |
| 4 | `AT+BLESERUUID=UUID` | `OK` | 主服务UUID（可选，默认已有） |
| | `AT+BLETXUUID=UUID` | `OK` | TX特征UUID（属性=NOTIFY） |
| | `AT+BLERXUUID=UUID` | `OK` | RX特征UUID（属性=WRITE） |
| 5 | `AT+BLEADVEN=1` | `OK` | 开启广播 |
| ⚠ | *等待URC* | `+EVENT:BLE_CONNECTED` | 手机已连接 |
| | `AT+BLESTATE?` | `+BLESTATE:1` | 确认已连接 |
| 6 | `AT+TRANSENTER` | `OK` | 进入透传模式 |
| 7 | `AT+BLESEND=5,hello` | `OK` | 发送数据（长度必须与实际字节数一致） |
| 8 | *接收URC* | `+DATA:len,data` | 收到蓝牙透传数据 |
| | `+++` | `OK` | 退出透传 |

### 流程4：GPIO控制

| 步骤 | 指令 | 预期响应 | 说明 |
|:----:|------|----------|------|
| 1 | `AT+SYSIOMAP?` | `+SYSIOMAP:PinNumber:N,PinMap:...` | 查询当前IO映射表 |
| 2 | `AT+SYSIOMAP=引脚数,pin1,pin2,...` | `OK` | 设置IO映射，NC=不可用引脚 |
| 3 | `AT+SYSGPIOWRITE=引脚号,1` | `OK` | 输出高电平 |
| 4 | `AT+SYSGPIOWRITE=引脚号,0` | `OK` | 输出低电平 |
| 5 | `AT+SYSGPIOREAD=引脚号` | `+SYSGPIOREAD:引脚号,电平` | 读取电平（0=低/1=高） |

> 💡 不同模组IO映射不同，使用前查阅 [io-map-table.md](./references/io-map-table.md)

### 流程5：PWM控制

| 步骤 | 指令 | 预期响应 | 说明 |
|:----:|------|----------|------|
| 1 | `AT+PWMCFGS=引脚号,周期us,占空比%` | `OK` | 配置PWM（推荐CFGS，单位统一） |
| | *示例* `AT+PWMCFGS=5,1000,50` | `OK` | 1kHz，50%占空比 |
| 2 | `AT+PWMDUTYSETS=引脚号,新占空比%` | `OK` | 动态更新占空比 |
| 3 | `AT+PWMSTOP=引脚号` | `OK` | 关闭PWM输出 |

> 💡 Ai-WB2系列5路PWM的芯片引脚IO序号对5取余不能重复

### 流程6：低功耗模式

| 模式 | 指令 | 预期响应 | 说明 |
|:----:|------|----------|------|
| 浅睡眠+定时唤醒 | `AT+SLEEP=0,0,唤醒时间ms` | `OK` | 上电不自动进入浅睡眠 |
| 浅睡眠+GPIO唤醒 | `AT+SLEEP=0,2,引脚号,电平` | `OK` | 电平：0=低/1=高/2=下降沿/3=上升沿/4=双边沿 |
| | *示例* `AT+SLEEP=0,2,7,0` | `OK` | IO7低电平唤醒 |
| 深度睡眠+定时唤醒 | `AT+SLEEP=2,0,唤醒时间ms` | `OK` | 唤醒后等同重启 |
| 唤醒方式 | *串口发送任意数据* | — | 浅睡眠可通过串口数据唤醒 |

### 流程7：HTTP请求

> 前置：WiFi已连接并获取IP

| 步骤 | 指令 | 预期响应 | 说明 |
|:----:|------|----------|------|
| 1 | `AT+HTTPCLIENTLINE=1,2,,www.baidu.com,,` | `Responselength:xxx` + 响应体 + `OK` | HTTP GET（端口缺省80，路径缺省/） |
| 2 | `AT+HTTPCLIENTLINE=2,2,,www.baidu.com,,` | 同上 | HTTPS GET（端口缺省443） |
| 3 | `AT+HTTPCLIENTLINE=1,3,,192.168.1.100,8080,/api,"{\"k\":\"v\"}"` | 响应体 + `OK` | HTTP POST JSON |
| 4 | `AT+HTTPRAW=1,3,application/json,IP,端口,/path,长度` | `>` | 长数据POST（超过单行限制时） |
| | *输入数据* | 响应体 + `OK` | 收到`>`后输入指定长度数据 |

### 流程8：自动透传模式（上电即用）

> 配置完成后，模组上电自动执行：连WiFi → 建Socket → 进透传

| 步骤 | 指令 | 预期响应 | 说明 |
|:----:|------|----------|------|
| 1 | `AT+WJAP=SSID,密码` | `OK` | 连接WiFi |
| ⚠ | *等待连接成功* | `+EVENT:WIFI_GOT_IP` | 确认WiFi连接 |
| 2 | `AT+WAUTOCONN=1` | `OK` | 保存WiFi自动重连 |
| 3 | `AT+SOCKETAUTOTT=4,服务器IP,端口` | `OK` | 4=TCPClient自动透传 |
| 4 | `AT+RST` | `OK` | 重启后自动进入透传 |

## URC事件速查

| 类别 | URC | 说明 |
|------|-----|------|
| WiFi | `+EVENT:WIFI_DISCONNECT` | WiFi断开 |
| WiFi | `+EVENT:WIFI_CONNECT` | WiFi连接成功 |
| WiFi | `+EVENT:WIFI_GOT_IP` | 获取到IP |
| Socket | `+EVENT:SocketDown,<ConID>,<length>[,<data>]` | 收到数据 |
| Socket | `+EVENT:SocketSeed,<seed>,<server>` | TCP新连接 |
| Socket | `+EVENT:SocketDissconnect,<ConID>` | Socket断开 |
| MQTT | `+EVENT:MQTT_CONNECT` | MQTT连接成功 |
| MQTT | `+EVENT:MQTT_DISCONNECT` | MQTT断开 |
| MQTT | `+EVENT:MQTT_SUB,<Topic>,<len>,<data>` | 收到订阅消息 |
| BLE | `+EVENT:BLE_CONNECTED` | 蓝牙连接 |
| BLE | `+EVENT:BLE_DISCONNECT` | 蓝牙断开 |
| BLE | `+DATA:<len>,<data>` | 蓝牙透传数据 |

> 详见 [urc-events.md](./references/urc-events.md)

## 重要注意事项

1. **瑞昱系列(BW16/BW20)多模开启顺序**：必须先开AP，再开STA和蓝牙
2. **MQTT连接是异步的**：OK只表示任务启动，需等待`+EVENT:MQTT_CONNECT`确认
3. **Socket透传条件**：仅当只有一个client连接时才能进入透传
4. **蓝牙参数设置前置条件**：`AT+BLENAME`、`AT+BLESERUUID`、`AT+BLETXUUID`、`AT+BLERXUUID`、`AT+BLEADVDATA`、`AT+BLEADVINTV`、`AT+BLEAUTH`、`AT+BLECONINTV`、`AT+BLERFPWR` 等指令**必须在蓝牙关闭状态下执行**，否则会返回错误码228
5. **IO映射表**：不同模组型号的IO映射不同，必须查阅对应型号的映射表
6. **PWM注意事项**：Ai-WB2系列5路PWM的芯片引脚IO序号对5取余不能重复
7. **被动接收模式**：socket被动模式下数据缓存在RAM中，不读取会占满内存导致丢包
8. **指令最大长度**：单条AT指令最大长度默认1023字节
9. **AT+STAINFO 优于 AT+WJAP?**：查询WiFi连接信息推荐使用`AT+STAINFO?`，因为`AT+WJAP?`在SSID或密码含逗号时会解析错误

## 参考文档

按需加载以下参考文档获取详细信息：

| 文档 | 内容 |
|------|------|
| [command-format.md](./references/command-format.md) | 指令格式、默认配置、启动信息、响应格式 |
| [urc-events.md](./references/urc-events.md) | URC主动上报事件完整列表及掩码设置 |
| [basic-commands.md](./references/basic-commands.md) | 基础指令详细参数（AT/RST/RESTORE/SLEEP/UARTCFG/OTA等） |
| [wifi-commands.md](./references/wifi-commands.md) | WiFi指令详细参数（WMODE/WJAP/WAP/WSCAN/DHCP等） |
| [socket-commands.md](./references/socket-commands.md) | Socket指令详细参数（SOCKET/SEND/READ/TT/SSL等） |
| [mqtt-commands.md](./references/mqtt-commands.md) | MQTT指令详细参数（MQTT/PUB/SUB/VER/BUF/CERT等） |
| [http-commands.md](./references/http-commands.md) | HTTP指令详细参数（HTTPCLIENTLINE/HTTPRAW） |
| [sntp-commands.md](./references/sntp-commands.md) | SNTP指令详细参数（SNTPTIMECFG/SNTPTIME/SNTPINTV） |
| [ble-commands.md](./references/ble-commands.md) | BLE蓝牙指令详细参数（BLEMODE/NAME/SCAN/CONNECT/MESH等） |
| [gpio-pwm-commands.md](./references/gpio-pwm-commands.md) | GPIO/PWM指令详细参数（SYSIOMAP/GPIOWRITE/PWMCFG等） |
| [test-commands.md](./references/test-commands.md) | 产测指令详细参数（NodeMCUTEST/LEDTEST） |
| [error-codes.md](./references/error-codes.md) | 完整错误码列表及排查方法 |
| [io-map-table.md](./references/io-map-table.md) | 各型号模组IO映射配置表 |
