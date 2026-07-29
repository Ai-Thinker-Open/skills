# MQTT指令

## 4.3.1 AT+MQTT — MQTT配置和连接

### 连接: AT+MQTT

| 项目 | 内容 |
|------|------|
| 描述 | 连接MQTT。注意：执行连接前需要先设置好MQTT参数，如果当前MQTT任务已经启动再次执行会重新连接（更改服务器的话建议先删除所有订阅后重连） |
| 响应 | OK。注意：这里是异步连接，显示OK只是表示MQTT任务启动，连接状态需要通过AT+MQTT?查询或等待收到URC数据"+EVENT:MQTT_CONNECT" |

### 查询: AT+MQTT?

| 项目 | 内容 |
|------|------|
| 描述 | 查询MQTT参数 |
| 响应 | `+MQTT:<MQTT_status>,<Host_name>,<Port>,<scheme>,<client_id>,<username>,<password>,<LWT_topic>,<LWT_qos>,<LWT_Retained>,<LWTpayload>` → OK |

**返回字段说明：**

| 字段 | 说明 |
|------|------|
| MQTT_status | MQTT连接状态：0=初始状态，1=正在连接，2=正在订阅消息，3=连接成功 |
| Host_name | 服务器域名 |
| Port | 服务器端口号 |
| scheme | 连接方式：1=TCP连接，2=SSL连接 |
| client_id | MQTT用户ID |
| username | MQTT用户名 |
| password | MQTT密码 |
| LWT_topic | 遗嘱主题 |
| LWT_qos | 遗嘱QOS |
| LWT_Retained | 遗嘱retained |
| LWTpayload | 遗嘱消息内容 |

**示例：**
```
AT+MQTT?
+MQTT:0,192.168.202.10,1883,1,client_id,admin,public,LWTTOPIC,0,1,123456
OK
```

### 设置: AT+MQTT=<key>,<data>

| 项目 | 内容 |
|------|------|
| 描述 | 设置MQTT参数。注意：不同的key设置的内容不同，所以需要执行多次设置才能将参数全部设置完毕 |
| 响应 | OK |

**key参数表：**

| key | 功能 | 参数说明 |
|-----|------|----------|
| 1 | 设置连接的域名或IP | data=服务器地址 |
| 2 | 设置服务器端口号 | data=端口号 |
| 3 | 设置连接方式 | data=1(TCP连接) 或 2(SSL连接) |
| 4 | 设置客户端ID | data=client_id |
| 5 | 设置用户名 | data=用户名（最大长度63字节） |
| 6 | 设置密码 | data=密码（最大长度63字节） |
| 7 | 设置遗嘱消息 | 格式为 `AT+MQTT=7,<LWT_topic>,<LWT_qos>,<LWT_Retained>,<LWTpayload>` |

**key=7 遗嘱参数：**

| 参数 | 类型 | 必选 | 取值范围 | 说明 |
|------|------|:---:|----------|------|
| LWT_topic | 字符串 | 是 | 任意字符串（不需要遗嘱设为""） | 遗嘱主题 |
| LWT_qos | 整数 | 是 | 0, 1, 2 | 遗嘱QOS |
| LWT_Retained | 整数 | 是 | 0, 1 | 遗嘱retained |
| LWTpayload | 字符串 | 是 | 任意字符串 | 遗嘱消息内容 |

**示例：**
```
AT+MQTT=1,192.168.202.10    // 设置域名
OK
AT+MQTT=2,1883              // 设置端口号
OK
AT+MQTT=3,1                 // 设置连接方式
OK
AT+MQTT=4,client_id         // 设置用户ID
OK
AT+MQTT=5,admin             // 设置MQTT用户名
OK
AT+MQTT=6,public            // 设置MQTT密码
OK
AT+MQTT=7,"LWTTOPIC",0,1,"123456"  // 设置遗嘱主题LWTTOPIC，qos0，开启retained，负载消息为123456
OK
AT+MQTT=7,"",0,0,""         // 不要遗嘱消息
OK
AT+MQTT?                    // 查询配置
+MQTT:0,192.168.202.10,1883,1,client_id,admin,public,LWTTOPIC,0,1,123456
OK
AT+MQTT                     // 连接MQTT
OK
+EVENT:MQTT_CONNECT         // MQTT连接成功
```

| 项目 | 内容 |
|------|------|
| 注释 | 默认MQTT版本为MQTT3.1 |

## 4.3.2 AT+MQTTVER — MQTT版本

### 查询: AT+MQTTVER?

| 项目 | 内容 |
|------|------|
| 描述 | 查询当前MQTT使用的版本 |
| 响应 | `+MQTTVER:<version>` → OK |
| 示例 | `AT+MQTTVER?` → `+MQTTVER:3` → OK |

### 设置: AT+MQTTVER=<version>

| 参数 | 类型 | 必选 | 取值范围 | 说明 |
|------|------|:---:|----------|------|
| version | 整数 | 是 | 3, 4 | 3=MQTT3.1，4=MQTT3.1.1 |

| 项目 | 内容 |
|------|------|
| 响应 | OK |
| 示例 | `AT+MQTTVER=4` → OK |

## 4.3.3 AT+MQTTBUF — MQTT收发buf大小

### 查询: AT+MQTTBUF?

| 项目 | 内容 |
|------|------|
| 描述 | 查询MQTTbuf大小（修改后需要重启MQTT才会生效） |
| 响应 | `+MQTTBUF:<sendBufSize>,<reciveBufSize>` → OK |
| 示例 | `AT+MQTTBUF?` → `+MQTTBUF:2048,2048` → OK |

### 设置: AT+MQTTBUF=<sendBufSize>,<reciveBufSize>

| 参数 | 类型 | 必选 | 取值范围 | 说明 |
|------|------|:---:|----------|------|
| sendBufSize | 整数 | 是 | 正整数 | MQTT发送buf大小，单位字节 |
| reciveBufSize | 整数 | 是 | 正整数 | MQTT接收buf大小，单位字节 |

| 项目 | 内容 |
|------|------|
| 响应 | OK |
| 示例 | `AT+MQTTBUF=1024,4096` → OK |

**注意：**
1. 该参数在下一次连接时生效（如果当前已经连接需要先断开再重新连接后才生效）
2. 该命令只是设置buf的大小，并没有立即生效，之后执行MQTT连接时才会分配，所以应该根据内存合理设置，否则设置成功后也会因为内存不足而无法启动MQTT任务

## 4.3.4 AT+MQTTKEEPALIVE — MQTT心跳间隔

### 查询: AT+MQTTKEEPALIVE?

| 项目 | 内容 |
|------|------|
| 描述 | 查询当前MQTT心跳间隔（修改后需要重启MQTT才会生效） |
| 响应 | `+MQTTKEEPALIVE:<mqttKeepAliveInterval>,<mqttTcpKeepAliveInterval>` → OK |
| 示例 | `AT+MQTTKEEPALIVE?` → `+MQTTKEEPALIVE:60,10` → OK |

### 设置: AT+MQTTKEEPALIVE=<mqttKeepAliveInterval>,<mqttTcpKeepAliveInterval>

| 参数 | 类型 | 必选 | 取值范围 | 说明 |
|------|------|:---:|----------|------|
| mqttKeepAliveInterval | 整数 | 是 | 正整数 | MQTT心跳间隔，单位s |
| mqttTcpKeepAliveInterval | 整数 | 是 | 正整数 | MQTTsocket心跳间隔，单位s |

| 项目 | 内容 |
|------|------|
| 响应 | OK |
| 示例 | `AT+MQTTKEEPALIVE=120,5` → OK |

## 4.3.5 AT+MQTTCRET — MQTT SSL证书

### 查询: AT+MQTTCRET=<type>

| 项目 | 内容 |
|------|------|
| 描述 | 查询和设置MQTT SSL证书 |
| 响应 | `+MQTTCRET:<type>,<length>,<证书内容>` → OK |

### 设置: AT+MQTTCRET=<type>,<length>

| 参数 | 类型 | 必选 | 取值范围 | 说明 |
|------|------|:---:|----------|------|
| type | 整数 | 是 | 1, 2, 3 | 操作的证书类型：1=CA根证书，2=客户端公钥，3=客户端私钥 |
| length | 整数 | 否 | 非负整数 | 证书长度。省略时表示查询对应的证书；为0时表示清空当前证书 |

| 项目 | 内容 |
|------|------|
| 响应 | 设置模式：`>`（收到此符号后开始写证书）→ OK（输入长度足够后返回） |
| 注意 | 1. 该修改只是保存在RAM，没有保存到flash，重启模组后会失效 2. 修改后需要重启MQTT才会生效 |
| 备注 | 证书为空时length需要设置为0，客户端不加载证书，自动获取 |

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

**示例：**
```
AT+MQTT=1,192.168.202.10    // 设置域名
OK
AT+MQTT=2,1883              // 设置端口号
OK
AT+MQTT=3,1                 // 设置连接方式
OK
AT+MQTT=4,client_id         // 设置用户ID
OK
AT+MQTT=5,admin             // 设置MQTT用户名
OK
AT+MQTT=6,public            // 设置MQTT密码
OK
AT+MQTT
OK
AT+MQTTDISCONN
OK
```

## 4.3.7 AT+MQTTPUB — 发布MQTT消息

### 发布: AT+MQTTPUB=<topic>,<qos>,<Retained>,<payload>

| 参数 | 类型 | 必选 | 取值范围 | 说明 |
|------|------|:---:|----------|------|
| topic | 字符串 | 是 | 任意字符串 | 要发布的主题 |
| qos | 整数 | 是 | 0, 1, 2 | QOS等级 |
| Retained | 整数 | 是 | 0, 1 | 0=普通消息，1=Retained消息 |
| payload | 字符串 | 是 | 任意字符串 | 负载消息 |

| 项目 | 内容 |
|------|------|
| 响应 | OK |
| 示例 | `AT+MQTTPUB=testtopic,1,0,456` → OK |

## 4.3.8 AT+MQTTPUBRAW — 发布指定长度MQTT消息

### 发布: AT+MQTTPUBRAW=<topic>,<qos>,<Retained>,<length>

| 参数 | 类型 | 必选 | 取值范围 | 说明 |
|------|------|:---:|----------|------|
| topic | 字符串 | 是 | 任意字符串 | 要发布的主题 |
| qos | 整数 | 是 | 0, 1, 2 | QOS等级 |
| Retained | 整数 | 是 | 0, 1 | 0=普通消息，1=Retained消息 |
| length | 整数 | 是 | 正整数 | 要发送的数据长度 |

| 项目 | 内容 |
|------|------|
| 响应 | `>`（收到此符号后开始输入数据）→ OK（收到足够长度数据后发送，发送完成显示OK） |
| 示例 | `AT+MQTTPUBRAW=testtopic,1,0,10` → `>` → 输入10字节任意数据 → OK |

## 4.3.9 AT+MQTTSUB — 订阅MQTT消息

### 查询: AT+MQTTSUB?

| 项目 | 内容 |
|------|------|
| 描述 | 查询已经订阅的主题和主题状态 |
| 响应 | `<status>,<Topic>` ... → OK |

**status状态：**
- 0: 初始化状态
- 1: 订阅中（首次订阅）
- 2: 订阅中（断线重连后重新订阅）
- 3: 订阅成功

**示例：**
```
AT+MQTTSUB=testtopic0,0
OK
AT+MQTTSUB=testtopic1,1
OK
AT+MQTTSUB?
3,testtopic0
3,testtopic1
OK
```

### 订阅: AT+MQTTSUB=<topic>,<qos>

| 参数 | 类型 | 必选 | 取值范围 | 说明 |
|------|------|:---:|----------|------|
| topic | 字符串 | 是 | 任意字符串 | 要订阅的主题 |
| qos | 整数 | 是 | 0, 1, 2 | QOS等级 |

| 项目 | 内容 |
|------|------|
| 响应 | OK |
| 示例 | `AT+MQTTSUB=testtopic0,0` → OK |
| 注释 | 可以订阅的主题条数默认最多为5条，每条订阅大概消耗100字节内存 |

## 4.3.10 AT+MQTTUNSUB — 取消订阅MQTT消息

### 取消: AT+MQTTUNSUB=<topic>

| 参数 | 类型 | 必选 | 取值范围 | 说明 |
|------|------|:---:|----------|------|
| topic | 字符串 | 是 | 任意字符串 | 要取消的主题 |

| 项目 | 内容 |
|------|------|
| 响应 | OK |
| 示例 | `AT+MQTTSUB=testtopic0` → OK |
