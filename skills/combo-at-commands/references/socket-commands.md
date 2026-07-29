# TCP-IP / Socket指令

## 4.2.1 +EVENT:SocketDown — 通过Socket接收数据（URC）

| 项目 | 内容 |
|------|------|
| 描述 | URC主动数据，表示收到了Socket发送的数据 |
| 格式 | `+EVENT:SocketDown,<ConID>,<length>[,<data>]` |
| ConID | 创建Socket连接后获取到的连接ID |
| length | 收到的数据长度 |
| data | 主动读取模式时直接打印数据内容；被动模式不打印，需主动读取 |

| 备注 | TCPServer的连接无法收发数据，只能给客户端连接到TCPServer后创建的seed才能收发数据；UDPClient只能发送数据，不可以接收数据 |

## 4.2.2 +EVENT:SocketSeed — TCP Server新连接（URC）

| 项目 | 内容 |
|------|------|
| 描述 | 当TCP Server连接到新客户端时收到该消息 |
| 格式 | `+EVENT:SocketSeed,<seedConID>,<serverConID>` |
| seedConID | 新连接的客户端的ConID |
| serverConID | 该seed对应的server端的ConID |

## 4.2.3 AT+SOCKET — 创建Socket连接

### 查询: AT+SOCKET?

| 项目 | 内容 |
|------|------|
| 描述 | 查询已创建的Socket连接信息 |
| 响应 | `<ConID>,<type>,<status>,<remotehost>,<remoteport>,<localport>,<serverConID>` → OK |

**type类型：**
- 1: UDPServer
- 2: UDPClient
- 3: TCPServer
- 4: TCPClient
- 5: TCPSeed（TCPServer的客户端连接后产生，不可主动创建）
- 6: SSLServer
- 7: SSLClient
- 8: SSLSeed（SSL Server的客户端连接后产生，不可主动创建）

**status状态：**
- 0: 没有连接/已断开
- 1: 正在连接
- 3: 连接成功
- 4: 连接失败
- 127: 连接删除中

### 创建: AT+SOCKET=<type>[,<remotehost>],<port>[,<keepalive>,<conID>]

| 参数 | 说明 |
|------|------|
| type | Socket类型（见上表） |
| remotehost | client模式必填，服务器域名或IP；server模式跳过 |
| port | client=远程端口，server=本地监听端口 |
| keepalive | TCP keep-alive间隔，0=禁用，1~7200秒（预留功能，暂未实现） |
| conID | 指定新连接的ConID（u32类型） |

| 响应 | `connectsuccessConID=<ConID>` → OK |

**示例：**
```
// 创建UDPServer
AT+SOCKET=1,10086
connectsuccessConID=1
OK

// 创建UDPClient
AT+SOCKET=2,192.168.3.10,10086
connectsuccessConID=1
OK

// 创建TCPClient（IP）
AT+SOCKET=4,192.168.3.10,80
connectsuccessConID=1
OK

// 创建TCPServer
AT+SOCKET=3,10086
connectsuccessConID=1
OK
```

## 4.2.4 AT+SOCKET2 — 创建Socket连接（简化版）

### 创建: AT+SOCKET2=<type>,<remotehost>,<remotePort>[,<localPort>,<keepalive>,<conID>]

| 参数 | 说明 |
|------|------|
| type | 2=UDPClient，4=TCPClient（其他为占位符） |
| remotehost | 服务器域名或IP |
| remotePort | 远端服务器端口 |
| localPort | 绑定的本地端口（-1=随机绑定） |
| keepalive | TCP keep-alive间隔（UDP无效） |
| conID | 指定ConID |

| 响应 | `connectsuccessConID=<ConID>` → OK |

## 4.2.5 AT+SOCKETSEND — 通过Socket发送数据（长数据模式）

### 发送: AT+SOCKETSEND=<ConID>,<length>

| 参数 | 说明 |
|------|------|
| ConID | 连接ID |
| length | 要发送的数据长度 |

| 响应 | `>` → 输入数据 → OK |
|------|------|
| 特点 | 可发送任意长度数据（超长自动分包，默认超过1024字节分包），可接收任意字符 |

| 示例 | `AT+SOCKETSEND=1,3` → `>` → `123` → OK |

## 4.2.6 AT+SOCKETSENDLINE — 通过Socket发送数据（单行模式）

### 发送: AT+SOCKETSENDLINE=<ConID>,<length>,<data>

| 参数 | 说明 |
|------|------|
| ConID | 连接ID |
| length | 数据长度 |
| data | 要发送的数据（特殊字符需双引号括起来，双引号需转义） |

| 响应 | OK |
|------|------|
| 特点 | 使用简单，但长度受限（单条指令最大1023字节） |
| 示例 | `AT+SOCKETSENDLINE=1,5,12345` → OK |

## 4.2.7 AT+SOCKETSENDHEX — 通过Socket发送HEX数据（单行模式）

### 发送: AT+SOCKETSENDHEX=<ConID>,<length>,<data>

| 参数 | 说明 |
|------|------|
| ConID | 连接ID |
| length | 数据长度 |
| data | 字符串形式的hex数据 |

| 响应 | OK |
|------|------|
| 示例 | `AT+SOCKETSENDHEX=1,2,3132` → 发送0x31 0x32 → OK |
| 备注 | hex字符串两个字节表示一个hex数据，最大可发送997/2=498字节 |

## 4.2.8 AT+SOCKETREAD — 从Socket读取数据

### 读取: AT+SOCKETREAD=<ConID>

| 参数 | 说明 |
|------|------|
| ConID | 连接ID |

| 响应 | `+SOCKETREAD:<ConID>,<len>,<data>` → OK |
|------|------|
| 备注 | 按包读取，一次读取一包数据 |

## 4.2.9 AT+SOCKETDEL — 删除Socket连接

### 删除: AT+SOCKETDEL=<ConID>

| 参数 | 说明 |
|------|------|
| ConID | 要删除的连接ID |

| 响应 | OK |
|------|------|
| 备注 | Seed因为是客户端发起的，Server无法重连，所以Seed断开后需手动删除（删除后接收到的数据也会被清空） |

## 4.2.10 AT+SOCKETRECVCFG — Socket接收模式

### 设置: AT+SOCKETRECVCFG=<mode>

| 参数 | 说明 |
|------|------|
| mode | 0=被动模式（默认），收到数据只提示`+EVENT:SocketDown,<ConID>,<length>`不打印内容；1=主动模式，收到数据直接打印`+EVENT:SocketDown,<ConID>,<length>,<data>` |

| 备注 | 被动模式下数据以链表形式保存在RAM中，如果不读取会一直占用内存，内存不足时新数据将被丢弃 |

## 4.2.11 AT+SOCKETTT — 进入Socket透传模式

### 进入: AT+SOCKETTT

| 项目 | 内容 |
|------|------|
| 描述 | 进入Socket透传模式 |
| 响应 | `>` → 可收发数据 |
| 退出 | 输入连续三个加号`+++`退出透传，返回`\r\nOK\r\n` |
| 备注 | UDP Server默认透传对象是第一次通信的client客户端 |

**进入条件（满足任意一个）：**
- 当前仅有一个client连接
- 仅有一个server和一个seed连接（必须手动进入）
- 仅有一个UDPClient
- 仅有一个UDPServer

### UDP Server透传模式: AT+SOCKETTT=UDPServerTTMode

| 参数 | 说明 |
|------|------|
| UDPServerTTMode | 0=透传对象固定为第一次通讯的客户端（后续不改变）；2=透传对象动态修改为最后一次通信的客户端 |

**示例：**
```
AT+WJAP=test,123456789
OK
AT+SOCKET=4,192.168.31.98,18
connectsuccessConID=1
OK
AT+SOCKETTT
>
sendtomodule    // 数据透传到目标
OK              // +++退出透传
```

## 4.2.12 AT+SOCKETAUTOTT — 自动透传配置

### 查询: AT+SOCKETAUTOTT?

| 项目 | 内容 |
|------|------|
| 描述 | 查询当前自动透传配置信息 |
| 响应 | `+SOCKETAUTOTT:<type>,<remotehost>,<remoteport>` → OK |

**type类型：**
- 0: 禁用自动进入透传模式
- 1: 自动进入UDPServer透传模式
- 2: 自动进入UDPClient透传模式
- 4: 自动进入TCPClient透传模式

### 设置: AT+SOCKETAUTOTT=<type>[,<remotehost>],<port>

| 参数 | 说明 |
|------|------|
| type | Socket类型（见上表） |
| remotehost | client模式必填，server模式跳过 |
| port | client=远程端口，server=本地监听端口 |

| 响应 | OK |
|------|------|
| 使用方法 | 配合`AT+WAUTOCONN`使用，设置完成后复位生效。上电后自动连接WiFi → 自动创建Socket → 自动进入透传。 |
| 示例 | `AT+SOCKETAUTOTT=4,www.baidu.com,80` |

## 4.2.13 AT+SSLCRET — SSL证书

### 查询: AT+SSLCRET=<type>

| 项目 | 内容 |
|------|------|
| 响应 | `+SSLCRET:<type>,<length>,<证书内容>` → OK |

### 设置: AT+SSLCRET=<type>,<length>

| 参数 | 说明 |
|------|------|
| type | 1=CA根证书，2=客户端公钥，3=客户端私钥 |
| length | 证书长度（省略=查询，有此参数=设置） |

| 响应 | `>` → 输入证书 → OK |
|------|------|
| 备注 | 证书为空时客户端不加载证书，自动获取 |

## 4.2.14 AT+WDOMAIN — DNS域名解析

### 解析: AT+WDOMAIN=<servername>

| 项目 | 内容 |
|------|------|
| 描述 | DNS解析域名 |
| 响应 | `+WDOMAIN:<IP>` → OK |
| 示例 | `AT+WDOMAIN=www.baidu.com` → `+WDOMAIN:14.119.104.189` → OK |

## 4.2.15 AT+WDNS — DNS服务器

### 查询: AT+WDNS?

| 项目 | 内容 |
|------|------|
| 描述 | 查询DNS解析服务器 |
| 响应 | `+WDNS:<DNSIP1>,<DNSIP2>` → OK |
| 示例 | `AT+WDNS?` → `+WDNS:192.168.3.1,0.0.0.0` → OK |

### 设置: AT+WDNS=<"DNSIP1">[,<"DNSIP2">]

| 参数 | 说明 |
|------|------|
| DNSIP1/DNSIP2 | 域名解析服务器 |

| 示例 | `AT+WDNS=114.114.114.114` → `+WDNS:114.114.114.114` → OK |
