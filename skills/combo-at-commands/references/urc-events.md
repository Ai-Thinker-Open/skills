# URC主动上报事件

URC（Unsolicited Result Code）是模组主动上报的事件数据，无需用户查询。

## WiFi事件

| URC | 说明 |
|-----|------|
| `+EVENT:WIFI_DISCONNECT` | WiFi断开连接 |
| `+EVENT:WIFI_CONNECT` | WiFi连接成功 |
| `+EVENT:WIFI_GOT_IP` | 获取到IP地址 |
| `+EVENT:WIFI_SCAN_DONE` | WiFi扫描结束 |
| `+EVENT:WIFI_APCLIENTCONNECTED:<MAC>` | AP模式有新客户端连接（MAC小写无冒号） |
| `+EVENT:WIFI_APCLIENTDISCONNECT:<MAC>` | AP模式客户端断开连接（MAC小写无冒号） |
| `+BLUFIDATA:<length>,<data>` | 收到蓝牙配网自定义数据 |

## Socket事件

| URC | 说明 |
|-----|------|
| `+EVENT:SocketDown,<ConID>,<length>[,<data>]` | 收到socket数据（主动模式时带data） |
| `+EVENT:SocketSeed,<seedConID>,<serverConID>` | TCP Server收到新客户端连接 |
| `+EVENT:SocketDissconnect,<ConID>` | Socket断开连接 |
| `+EVENT:SocketReconnect,<ConID>` | Socket自动重连成功 |
| `+EVENT:SocketAutoDel,<ConID>` | Socket自动删除 |

## MQTT事件

| URC | 说明 |
|-----|------|
| `+EVENT:MQTT_MALLOC_ERROR` | MQTT malloc错误（内存不足） |
| `+EVENT:MQTT_CONNECT` | MQTT连接成功 |
| `+EVENT:MQTT_DISCONNECT` | MQTT连接断开 |
| `+EVENT:MQTT_SUB,<Topic>,<len>,<data>` | 收到MQTT订阅消息 |

## BLE蓝牙事件

| URC | 说明 |
|-----|------|
| `+EVENT:BLE_DISCONNECT` | 蓝牙断开 |
| `+EVENT:BLE_CONNECTED` | 蓝牙连接成功 |
| `+DATA:<len>,<data>` | 主机模式收到蓝牙透传数据 |

## 云端事件

| URC | 说明 |
|-----|------|
| `aliGenie_data` | 天猫精灵下发数据 |
| `+EVENT:CloudDown,<type>,<data>` | 云端下发数据 |

## 产测事件

| URC | 说明 |
|-----|------|
| `##boot` | 开发板按键触发信号 |

## URC打印掩码设置

使用`AT+SYSMSG`可以控制哪些URC在透传模式下打印：

```
AT+SYSMSG=<mode>,<mask>,<saveFlash>
```

**mask位定义（32位hex）：**

| Bit | 对应URC |
|-----|---------|
| 0 | +EVENT:WIFI_DISCONNECT |
| 1 | +EVENT:WIFI_CONNECT |
| 2 | +EVENT:WIFI_APCLIENTDISCONNECT |
| 3 | +EVENT:WIFI_APCLIENTCONNECTED |
| 4 | +EVENT:SocketDown |
| 5 | +EVENT:SocketSeed |
| 6 | +EVENT:SocketDissconnect |
| 7 | +EVENT:SocketReconnect |
| 8 | +EVENT:SocketAutoDel |
| 9 | +EVENT:MQTT_CONNECT |
| 10 | +EVENT:MQTT_DISCONNECT |
| 11 | +EVENT:MQTT_SUB |
| 12 | +EVENT:BLE_DISCONNECT |
| 13 | +EVENT:BLE_CONNECTED |
| 14 | +DATA（蓝牙透传） |
| 15 | +EVENT:WIFI_GOT_IP |
| 16 | +EVENT:WIFI_SCAN_DONE |

**示例：**
```
AT+SYSMSG=1,2468abcd,0   // 设置透传模式URC掩码，本次生效
```
