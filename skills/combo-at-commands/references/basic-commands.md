# 基础指令

## 2.1 AT — 测试指令

| 项目 | 内容 |
|------|------|
| 描述 | 测试AT框架是否正常工作的指令 |
| 响应 | OK |
| 示例 | `AT` → `OK` |
| HELP中的描述信息 | Testcmd |

## 2.2 AT+HELP — 查看指令集

| 项目 | 内容 |
|------|------|
| 描述 | 查询AT指令集列表 |
| 响应 | `<指令名称>:<注释>` ... `<指令名称>:<注释>` OK |
| HELP中的描述信息 | Showcmdlist |

## 2.3 AT+RST — 模块重启

| 项目 | 内容 |
|------|------|
| 描述 | 重启模组 |
| 响应 | OK |

## 2.4 AT+RESTORE — 恢复出厂设置

| 项目 | 内容 |
|------|------|
| 描述 | 恢复出厂模式，擦除配置信息(三元组、IO映射除外) |
| 响应 | OK |
| 备注 | 成功后自动重启 |
| HELP中的描述信息 | Restoresetting |

## 2.5 ATE1 — 打开回显

| 项目 | 内容 |
|------|------|
| 描述 | 打开回显 |
| 响应 | OK |
| 示例 | `ATE1` → `OK` |
| HELP中的描述信息 | Enableecho |
| 注释 | PB系列默认回显打开，TB系列默认回显打开 |

## 2.6 ATE0 — 关闭回显

| 项目 | 内容 |
|------|------|
| 描述 | 关闭回显 |
| 响应 | OK |
| 示例 | `ATE0` → `OK` |
| HELP中的描述信息 | Disableecho |

## 2.7 AT+SYSMSG — 查询或设置系统提示信息

### 查询: AT+SYSMSG?

| 项目 | 内容 |
|------|------|
| 描述 | 查询URC数据打印掩码 |
| 响应 | `+SYSMSG: <mode1>,<mask1>` ... `<modeN>,<maskN>` OK |
| 示例 | `AT+SYSMSG?` → `+SYSMSG: 1,FFFFFFFF` → OK |

### 设置: AT+SYSMSG=<mode>,<mask>,<saveFlash>

| 参数 | 类型 | 必选 | 取值范围 | 说明 |
|------|------|:---:|----------|------|
| mode | 整数 | 是 | 1 | 指定需要设置掩码的模式：1=透传模式（包括socket透传和蓝牙透传） |
| mask | hex字符串 | 是 | 8位hex字符串(u32) | 打印掩码，32位16进制数据(字符串长度为8)，每个bit表示一种消息，0=禁止打印，1=允许打印 |
| saveFlash | 整数 | 是 | 0, 1 | 0=本次生效不保存到flash，1=本次生效并保存到flash |

**mask位定义：**

- Bit0: +EVENT:WIFI_DISCONNECT
- Bit1: +EVENT:WIFI_CONNECT
- Bit2: +EVENT:WIFI_APCLIENTDISCONNECT:<MAC>
- Bit3: +EVENT:WIFI_APCLIENTCONNECTED:<MAC>
- Bit4: +EVENT:SocketDown,<ConID>,<length>[,<data>]
- Bit5: +EVENT:SocketSeed,<seedConID>,<serverConID>
- Bit6: +EVENT:SocketDissconnect,<ConID>
- Bit7: +EVENT:SocketReconnect,<ConID>
- Bit8: +EVENT:SocketAutoDel,<ConID>
- Bit9: +EVENT:MQTT_CONNECT
- Bit10: +EVENT:MQTT_DISCONNECT
- Bit11: +EVENT:MQTT_SUB,<Topic>,<len>,<data>
- Bit12: +EVENT:BLE_DISCONNECT
- Bit13: +EVENT:BLE_CONNECTED
- Bit14: +DATA:<len>,<data>
- Bit15: +EVENT:WIFI_GOT_IP
- Bit16: +EVENT:WIFI_SCAN_DONE

| 示例 | `AT+SYSMSG=1,2468abcd,0` → OK |
|------|------|
| HELP中的描述信息 | Queryandsetsystemmessage |

## 2.8 AT+GMR — 查询版本信息

| 项目 | 内容 |
|------|------|
| 描述 | 查询版本信息 |
| 响应 | `<atversion:>` AT版本信息(combo版本) / `<sdkversion:>` SDK版本信息 / `<firmwareversion:>` 固件版本 OK |
| 示例 | `AT+GMR` → `atversion:release/v2.0.0` / `sdkversion:amebaD-6.2c` / `firmwareversion:release/v1.2.3` → OK |
| HELP中的描述信息 | Showversioninfo |

## 2.9 AT+FLASHID — 查询FLASH ID

| 项目 | 内容 |
|------|------|
| 描述 | 查询FLASHID |
| 响应 | `FlashManufacturerID:0xXX` / `FlashDeviceID:0xXX` / `FlashCapacityID:0xXX(XMB)` OK |
| HELP中的描述信息 | QueryFLASHID |
| 备注 | 已适配型号：BW16 |

## 2.10 AT+SLEEP — 睡眠模式

### 设置: AT+SLEEP=<mode>[,<wakeupsource>,<param1>,<param2>]

| 参数 | 类型 | 必选 | 取值范围 | 说明 |
|------|------|:---:|----------|------|
| mode | 整数 | 是 | 0, 1, 2, 3 | 0=进入浅睡眠（上电不自动进入），1=进入浅睡眠（上电自动进入），2=进入深度睡眠状态，3=普通模式 |
| wakeupsource | 整数 | 否 | 0, 2 | 设置唤醒源（仅mode=0/1/2时有效）：0=定时器唤醒，2=GPIO唤醒 |
| param1 | 整数 | 否 | 正整数 | 仅wakeupsource=0/2时有效。wakeupsource=0时表示定时时间，单位为ms；wakeupsource=2时表示唤醒脚的序号（从模组左上角逆时针排序，引脚序号从1开始） |
| param2 | 整数 | 否 | 0, 1, 2, 3, 4 | 仅wakeupsource=2时有效，表示GPIO唤醒时的唤醒电平：0=低电平唤醒，1=高电平唤醒，2=下降沿唤醒，3=上升沿唤醒，4=双边沿唤醒 |

| 项目 | 内容 |
|------|------|
| 响应 | OK |
| 备注 | 通过向串口发送任意数据唤醒模组 |
| HELP中的描述信息 | Setlowpowermode |

| 注释 | PB系列默认模式为3（普通模式），TB系列默认模式为3（普通模式），Ai-WB2系列支持mode2/3默认为3。注意：Ai-WB2系列的GPIO唤醒配置时param1指定的引脚是没有映射的，也就是芯片实际的引脚，且仅支持IO7引脚(IO7是RX引脚，所以串口唤醒我们一般设置IO7低电平环境即可，也就是 `AT+SLEEP=2,2,7,0`) |
|------|------|

## 2.11 AT+UARTCFG — 串口设置指令

### 查询: AT+UARTCFG?

| 项目 | 内容 |
|------|------|
| 描述 | 查询AT串口配置 |
| 响应 | `+UARTCFG:<baudrate>,<databits>,<stopbits>,<parity>` OK |

### 设置: AT+UARTCFG=<baudrate>,<databits>,<stopbits>,<parity>

| 参数 | 类型 | 必选 | 取值范围 | 说明 |
|------|------|:---:|----------|------|
| baudrate | 整数 | 是 | 正整数 | 串口波特率 |
| databits | 整数 | 是 | 5, 6, 7, 8 | 数据位：5=5bit，6=6bit，7=7bit，8=8bit |
| stopbits | 整数 | 是 | 1, 2, 3 | 停止位：1=1bit，2=1.5bit，3=2bit |
| parity | 整数 | 是 | 0, 1, 2 | 校验位：0=None，1=Odd，2=Even |

| 项目 | 内容 |
|------|------|
| 描述 | 设置AT串口配置指令，6212,6252,8258只支持baudrate |
| 响应 | OK |

| 注释 | PB系列只支持baudrate，TB系列只支持baudrate。流控默认为关闭状态，使用 `AT+UARTFLOWCONTROL` 设置。 |
|------|------|

## 2.12 AT+UARTFLOWCONTROL — 串口设置流控

### 查询: AT+UARTFLOWCONTROL?

| 项目 | 内容 |
|------|------|
| 描述 | 查询AT串口流控配置 |
| 响应 | `+UARTFLOWCONTROL:<flowcontrol>` OK |
| 示例 | `AT+UARTFLOWCONTROL?` → `+UARTFLOWCONTROL:0` → OK |

### 设置: AT+UARTFLOWCONTROL=<flowcontrol>

| 参数 | 类型 | 必选 | 取值范围 | 说明 |
|------|------|:---:|----------|------|
| flowcontrol | 整数 | 是 | 0, 1, 2, 3 | 流控：0=无流控，1=使能RTS，2=使能CTS，3=同时使能RTS和CTS |

| 项目 | 内容 |
|------|------|
| 响应 | OK（注意该OK是设置成功后才回复，如果开启了流控，接收端也需要配置流控后才可以收到数据） |
| 示例 | `AT+UARTFLOWCONTROL=3` → OK |
| 注释 | 已适配型号：BW16系列(RTS:PA_14/CTS:PA_15) |

## 2.13 AT+SETDOWNLOADMODE — 进入下载模式

### 设置: AT+SETDOWNLOADMODE=<mode>

| 参数 | 类型 | 必选 | 取值范围 | 说明 |
|------|------|:---:|----------|------|
| mode | 整数 | 是 | 1 | 1=进入串口下载模式 |

| 项目 | 内容 |
|------|------|
| 描述 | 进入下载模式 |
| 响应 | OK |
| HELP中的描述信息 | Setdownloadmode |

## 2.14 AT+OTA — 在线升级指令

### 执行: AT+OTA

| 项目 | 内容 |
|------|------|
| 描述 | 开始一次OTA升级（注意：升级是异步的，显示OK只是表示启动任务成功，并不表示升级成功，升级成功后会重启模组，并切换到新的固件） |
| 响应 | OK |

### 查询: AT+OTA?

| 项目 | 内容 |
|------|------|
| 描述 | 查询OTA参数 |
| 响应 | `+OTA:<Mode>,<Host_name>,<Port>,<Route>` OK |

### 设置: AT+OTA=<Mode>,<Host_name>,<Port>,<Route>

| 参数 | 类型 | 必选 | 取值范围 | 说明 |
|------|------|:---:|----------|------|
| Mode | 整数 | 是 | 1, 2 | 下载方式：1=HTTP，2=HTTPS |
| Host_name | 字符串 | 是 | — | 服务器域名 |
| Port | 整数 | 是 | 正整数 | 服务器端口号 |
| Route | 字符串 | 是 | — | 要下载的资源地址 |

| 项目 | 内容 |
|------|------|
| 响应 | OK |
| HELP中的描述信息 | FirmwareOTA |

## 2.15 AT+TICKLESS — 查询或设置进入浅睡眠模式监听AP beacon的间隔

### 查询: AT+TICKLESS?

| 项目 | 内容 |
|------|------|
| 响应 | OK |

### 设置: AT+TICKLESS=<tickless>

| 参数 | 类型 | 必选 | 取值范围 | 说明 |
|------|------|:---:|----------|------|
| tickless | 整数 | 是 | 1~100 | 进入浅睡眠模式监听AP beacon的间隔，默认值10 |

| 项目 | 内容 |
|------|------|
| 响应 | OK |
| 示例 | `AT+TICKLESS=10` → OK / `AT+SLEEP=0,2,22,2` → OK |
| 注释 | 1. 已适配型号：BL616/618系列模组 2. 需配合AT+SLEEP指令使用 |
