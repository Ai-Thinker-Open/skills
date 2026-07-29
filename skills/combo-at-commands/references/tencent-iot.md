---
name: tencent-iot
description: 腾讯云物联网平台(IoT Explorer)通过AT指令连接的完整流程，含密钥认证算法、主题体系、属性/事件上报、SSL配置
---

# 腾讯云 IoT 平台连接指南

## 概述

腾讯云物联网开发平台(IoT Explorer)基于 MQTT 协议通信，使用设备密钥(一机一密)或证书(一型一密)认证。Combo模组通过 AT 指令集完成 MQTT 连接和数据交互。

## 前置信息

从腾讯云 IoT 控制台获取以下设备三元组信息：

| 参数 | 示例 | 说明 |
|------|------|------|
| `product_id` | `ABCDE12345` | 产品 ID |
| `device_name` | `dev001` | 设备名称 |
| `device_secret` | `abc123def456...` | 设备密钥(Base64编码) |

**MQTT Broker 域名格式：**

| Region | 域名 |
|--------|------|
| 广州 | `{product_id}.iotcloud.tencentdevices.com` |
| 其他 | `{product_id}.ap-{region}.iotcloud.tencentdevices.com` |

如上海 region 域名为 `{product_id}.ap-shanghai.iotcloud.tencentdevices.com`。

## 认证算法

腾讯云 IoT MQTT 使用 **username + password** 方式认证，密码通过 HMAC-SHA1 动态生成，包含过期时间戳。

### Username 格式

```
{product_id}{device_name};12010126;{random};{expiry}
```

| 字段 | 说明 |
|------|------|
| `product_id` | 产品 ID |
| `device_name` | 设备名称 |
| `12010126` | 固定值(sdkappid) |
| `random` | 随机数(任意整数) |
| `expiry` | UTC 过期时间戳(秒)，如当前时间+86400 表示24小时后过期 |

### Password 格式

```
{token};hmacsha1
```

**token 计算：**
```
plaintext = "deviceName={device_name}&productId={product_id}&random={random}&timestamp={expiry}"
token = base64(hmac_sha1(device_secret, plaintext))
```

### Python 计算示例

```python
import hmac, hashlib, base64, time, random

product_id = "ABCDE12345"
device_name = "dev001"
device_secret = "your_base64_device_secret"

rand = random.randint(100000, 999999)
expiry = int(time.time()) + 86400  # 24小时后过期

username = f"{product_id}{device_name};12010126;{rand};{expiry}"

plaintext = f"deviceName={device_name}&productId={product_id}&random={rand}&timestamp={expiry}"
token = hmac.new(device_secret.encode(), plaintext.encode(), hashlib.sha1).digest()
password = base64.b64encode(token).decode() + ";hmacsha1"

print(f"Username: {username}")
print(f"Password: {password}")
```

> **重要**：密码内嵌过期时间戳，过期后需重新计算 username/password，然后重新执行 `AT+MQTT=5,...`、`AT+MQTT=6,...`、`AT+MQTT` 重连。

## 主题体系

腾讯云 IoT 使用 `$` 前缀的物模型主题，格式为 `$thing/{direction}/{category}/{product_id}/{device_name}`。

### 设备需订阅的主题(下行)

| 主题 | 用途 | 推荐Qos |
|------|------|---------|
| `$thing/down/property/{pid}/{dname}` | 接收云端属性下发/设置 | 1 |
| `$thing/down/action/{pid}/{dname}` | 接收云端行为调用 | 1 |

### 设备需发布的主题(上行)

| 主题 | 用途 | 推荐Qos |
|------|------|---------|
| `$thing/up/property/{pid}/{dname}` | 属性上报 | 1 |
| `$thing/up/event/{pid}/{dname}` | 事件上报 | 1 |
| `$thing/up/action/{pid}/{dname}` | 行为响应 | 1 |

> `{pid}` = product_id，`{dname}` = device_name

## 属性上报 JSON 格式

```json
{
  "method": "report",
  "clientToken": "唯一请求标识",
  "params": {
    "属性名1": 值,
    "属性名2": 值
  }
}
```

**示例 - 上报温度和湿度：**
```json
{"method":"report","clientToken":"t001","params":{"temperature":25.6,"humidity":60}}
```

## 事件上报 JSON 格式

```json
{
  "method": "event_post",
  "clientToken": "唯一请求标识",
  "eventId": "事件ID(控制台定义)",
  "params": {
    "参数名1": 值
  },
  "type": "info"
}
```

**示例 - 上电事件：**
```json
{"method":"event_post","clientToken":"e001","eventId":"power_on","params":{"voltage":3300},"type":"info"}
```

## 属性下发响应 JSON 格式

当设备收到 `$thing/down/property/...` 的属性设置消息后，需回复：

```json
{
  "method": "report_reply",
  "clientToken": "对应下发的clientToken",
  "code": 0,
  "status": "success"
}
```

## 行为响应 JSON 格式

收到行为调用后通过 `$thing/up/action/...` 回复：

```json
{
  "method": "action_reply",
  "clientToken": "对应下发的clientToken",
  "code": 0,
  "status": "success",
  "response": {
    "出参名": 值
  }
}
```

## SSL/TLS 加密连接

使用 8883 端口 + 证书认证时额外步骤：

```
AT+MQTT=2,8883
AT+MQTT=3,2
```

加载 CA 证书(长数据模式)：
```
AT+MQTTCRET=1,1758
>
-----BEGIN CERTIFICATE-----
...(证书内容)...
-----END CERTIFICATE-----
OK
```

> 腾讯云 IoT 的 CA 证书可从 [腾讯云官方文档](https://cloud.tencent.com/document/product/634/11914) 下载。

## 错误排查

| 现象 | 可能原因 | 排查方法 |
|------|----------|----------|
| `AT+MQTT` 后无 `+EVENT:MQTT_CONNECT` | 认证失败/网络不通 | 用 `AT+MQTT?` 查询状态，检查 username/password 是否正确计算、timestamp 是否过期 |
| 订阅主题后无下行数据 | 主题格式错误/product_id或device_name不匹配 | 用 `AT+MQTTSUB?` 确认已订阅主题格式 |
| 属性上报后云端无反应 | JSON 格式错误/method 字段缺失 | 检查 payload 是否严格符合物模型 JSON 规范 |
| 连接后快速断开 | 心跳间隔不匹配 | 尝试 `AT+MQTTKEEPALIVE=120,5` 对齐云端心跳配置 |
| 密码过期 | timestamp 已超过 expiry | 重新计算 username/password，重新连接 |
