# MQTT指令

## 4.3.1 AT+MQTT — MQTT配置和连接

### 查询: AT+MQTT?

| 项目 | 内容 |
|------|------|
| 描述 | 查询MQTT参数 |
| 响应 | `+MQTT:<MQTT_status>,<Host_name>,<Port>,<scheme>,<client_id>,<username>,<password>,<LWT_topic>,<LWT_qos>,<LWT_Retained>,<LWTpayload>` → OK |

**MQTT_status状态：**
- 0: 初始状态
- 1: 正在连接
- 2: 正在订阅消息
- 3: 连接成功

**scheme连接方式：**
- 1: TCP连接
- 2: SSL连接

**示例：**
```
AT+MQTT?
+MQTT:0,192.168.202.10,1883,1,client_id,admin,public,LWTTOPIC,0,1,123456
OK
```

### 设置: AT+MQTT=<key>,<data>

| key | 功能 | 参数说明 |
|-----|------|----------|
| 1 | 设置域名或IP | data=服务器地址 |
| 2 | 设置端口号 | data=端口号 |
| 3 | 设置连接方式 | data=1(TCP) 或 2(SSL) |
| 4 | 设置客户端ID | data=client_id |
| 5 | 设置用户名 | data=用户名（最大63字节） |
| 6 | 设置密码 | data=密码（最大63字节） |
| 7 | 设置遗嘱消息 | `AT+MQTT=7,<LWT_topic>,<LWT_qos>,<LWT_Retained>,<LWTpayload>` |

| 响应 | OK |
|------|------|
| 注释 | 默认MQTT版本为MQTT3.1 |

**遗嘱参数说明：**
- LWT_topic: 遗嘱主题（不需要设为""）
- LWT_qos: 遗嘱QOS（0/1/2）
- LWT_Retained: 遗嘱retained（0/1）
- LWTpayload: 遗嘱消息内容

### 连接: AT+MQTT

| 项目 | 内容 |
|------|------|
| 描述 | 连接MQTT |
| 响应 | OK（异步连接，OK只表示MQTT任务启动） |
| 确认 | 通过`AT+MQTT?`查询状态或等待`+EVENT:MQTT_CONNECT` |
| 注意 | 更改服务器建议先删除所有订阅后重连 |

**完整示例：**
```
AT+MQTT=1,192.168.202.10    // 设置域名
OK
AT+MQTT=2,1883              // 设置端口号
OK
AT+MQTT=3,1                 // 设置连接方式(TCP)
OK
AT+MQTT=4,client_id         // 设置用户ID
OK
AT+MQTT=5,admin             // 设置用户名
OK
AT+MQTT=6,public            // 设置密码
OK
AT+MQTT=7,"LWTTOPIC",0,1,"123456"  // 设置遗嘱
OK
AT+MQTT?                    // 查询配置
+MQTT:0,192.168.202.10,1883,1,client_id,admin,public,LWTTOPIC,0,1,123456
OK
AT+MQTT                     // 连接
OK
+EVENT:MQTT_CONNECT         // 连接成功URC
```

## 4.3.2 AT+MQTTVER — MQTT版本

### 查询: AT+MQTTVER?

| 项目 | 内容 |
|------|------|
| 描述 | 查询当前MQTT使用的版本 |
| 响应 | `+MQTTVER:<version>` → OK |
| 示例 | `AT+MQTTVER?` → `+MQTTVER:3` → OK |

### 设置: AT+MQTTVER=<version>

| 参数 | 说明 |
|------|------|
| version | 3=MQTT3.1，4=MQTT3.1.1 |

| 响应 | OK |
| 示例 | `AT+MQTTVER=4` → OK |

## 4.3.3 AT+MQTTBUF — MQTT收发buf大小

### 查询: AT+MQTTBUF?

| 项目 | 内容 |
|------|------|
| 描述 | 查询MQTT buf大小（修改后需要重启MQTT才会生效） |
| 响应 | `+MQTTBUF:<sendBufSize>,<reciveBufSize>` → OK |
| 示例 | `AT+MQTTBUF?` → `+MQTTBUF:2048,2048` → OK |

### 设置: AT+MQTTBUF=<sendBufSize>,<reciveBufSize>

| 参数 | 说明 |
|------|------|
| sendBufSize | MQTT发送buf大小，单位字节 |
| reciveBufSize | MQTT接收buf大小，单位字节 |

| 响应 | OK |
|------|------|
| 注意 | 1. 该参数在下一次连接时生效（已连接需先断开再重连） 2. 只是设置buf大小，没有立即分配，MQTT连接时才分配，应根据内存合理设置 |

## 4.3.4 AT+MQTTKEEPALIVE — MQTT心跳间隔

### 查询: AT+MQTTKEEPALIVE?

| 项目 | 内容 |
|------|------|
| 描述 | 查询当前MQTT心跳间隔（修改后需要重启MQTT才会生效） |
| 响应 | `+MQTTKEEPALIVE:<mqttKeepAliveInterval>,<mqttTcpKeepAliveInterval>` → OK |
| 示例 | `AT+MQTTKEEPALIVE?` → `+MQTTKEEPALIVE:60,10` → OK |

### 设置: AT+MQTTKEEPALIVE=<mqttKeepAliveInterval>,<mqttTcpKeepAliveInterval>

| 参数 | 说明 |
|------|------|
| mqttKeepAliveInterval | MQTT心跳间隔，单位秒 |
| mqttTcpKeepAliveInterval | MQTT Socket心跳间隔，单位秒 |

| 响应 | OK |
| 示例 | `AT+MQTTKEEPALIVE=120,5` → OK |

## 4.3.5 AT+MQTTCRET — MQTT SSL证书

### 查询: AT+MQTTCRET=<type>

| 项目 | 内容 |
|------|------|
| 响应 | `+MQTTCRET:<type>,<length>,<证书内容>` → OK |

### 设置: AT+MQTTCRET=<type>,<length>

| 参数 | 说明 |
|------|------|
| type | 1=CA根证书，2=客户端公钥，3=客户端私钥 |
| length | 证书长度（0=清空当前证书） |

| 响应 | `>` → 输入证书 → OK |
|------|------|
| 注意 | 1. 修改只保存在RAM，重启后失效 2. 修改后需重启MQTT才生效 |
| 备注 | 证书为空时length设为0，客户端不加载证书自动获取 |

**示例：**
```
// 查询证书
AT+MQTTCRET=1
+MQTTCRET:1,1758,-----BEGIN CERTIFICATE-----
.....(证书内容).....
-----END CERTIFICATE-----
OK

// 设置证书
AT+MQTTCRET=1,1758
>
-----BEGIN CERTIFICATE-----
.....(证书内容).....
-----END CERTIFICATE-----
OK
```

## 4.3.6 AT+MQTTDISCONN — 断开MQTT连接

### 执行: AT+MQTTDISCONN

| 项目 | 内容 |
|------|------|
| 描述 | 断开MQTT |
| 响应 | OK |

## 4.3.7 AT+MQTTPUB — 发布MQTT消息

### 发布: AT+MQTTPUB=<topic>,<qos>,<Retained>,<payload>

| 参数 | 说明 |
|------|------|
| topic | 要发布的主题 |
| qos | QOS等级（0/1/2） |
| Retained | 0=普通消息，1=Retained消息 |
| payload | 负载消息 |

| 响应 | OK |
| 示例 | `AT+MQTTPUB=testtopic,1,0,456` → OK |

## 4.3.8 AT+MQTTPUBRAW — 发布指定长度MQTT消息

### 发布: AT+MQTTPUBRAW=<topic>,<qos>,<Retained>,<length>

| 参数 | 说明 |
|------|------|
| topic | 要发布的主题 |
| qos | QOS等级（0/1/2） |
| Retained | 0=普通消息，1=Retained消息 |
| length | 要发送的数据长度 |

| 响应 | `>` → 输入数据 → OK |
| 示例 | `AT+MQTTPUBRAW=testtopic,1,0,10` → `>` → 输入10字节数据 → OK |

## 4.3.9 AT+MQTTSUB — 订阅MQTT消息

### 查询: AT+MQTTSUB?

| 项目 | 内容 |
|------|------|
| 描述 | 查询已订阅的主题和状态 |
| 响应 | `<status>,<Topic>` ... OK |

**status状态：**
- 0: 初始化状态
- 1: 订阅中（首次）
- 2: 订阅中（断线重连后重新订阅）
- 3: 订阅成功

### 订阅: AT+MQTTSUB=<topic>,<qos>

| 参数 | 说明 |
|------|------|
| topic | 要订阅的主题 |
| qos | QOS等级（0/1/2） |

| 响应 | OK |
|------|------|
| 备注 | 可以订阅的主题条数默认最多5条，每条订阅大约消耗100字节内存 |
| 示例 | `AT+MQTTSUB=testtopic0,0` → OK |

## 4.3.10 AT+MQTTUNSUB — 取消订阅MQTT消息

### 取消: AT+MQTTUNSUB=<topic>

| 参数 | 说明 |
|------|------|
| topic | 要取消的主题 |

| 响应 | OK |
| 示例 | `AT+MQTTUNSUB=testtopic0` → OK |
