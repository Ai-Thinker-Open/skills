# TCP-IP / Socket指令

## 4.2.1 +EVENT:SocketDown — 通过Socket接收数据（URC）

| 项目 | 内容 |
|------|------|
| 描述 | URC主动数据，表示收到了Socket发送的数据 |
| 格式 | `+EVENT:SocketDown,<ConID>,<length>[,<data>]` |

| 参数 | 类型 | 必选 | 取值范围 | 说明 |
|------|------|:---:|----------|------|
| ConID | 整数 | 是 | — | 创建Socket连接后获取到的连接ID |
| length | 整数 | 是 | — | 收到的数据长度 |
| data | 字符串 | 否 | — | 主动读取模式时直接打印数据内容；被动模式不打印，需主动读取 |

| 备注 | TCPServer的连接无法收发数据，只能给客户端连接到TCPServer后创建的seed才能收发数据；UDPClient只能发送数据，不可以接收数据 |

## 4.2.2 +EVENT:SocketSeed — TCP Server新连接（URC）

| 项目 | 内容 |
|------|------|
| 描述 | 当TCP Server连接到新客户端时收到该消息 |
| 格式 | `+EVENT:SocketSeed,<seedConID>,<serverConID>` |

| 参数 | 类型 | 必选 | 取值范围 | 说明 |
|------|------|:---:|----------|------|
| seedConID | 整数 | 是 | — | 新连接的客户端的ConID |
| serverConID | 整数 | 是 | — | 该seed对应的server端的ConID |

## 4.2.3 AT+SOCKET — 创建Socket连接

### 查询: AT+SOCKET?

| 项目 | 内容 |
|------|------|
| 描述 | 查询已创建的Socket连接信息 |
| 响应 | `<ConID>,<type>,<status>,<remotehost>,<remoteport>,<localport>,<serverConID>` → OK |

**type类型：**

| 值 | 类型 | 说明 |
|----|------|------|
| 1 | UDPServer | UDP服务端 |
| 2 | UDPClient | UDP客户端 |
| 3 | TCPServer | TCP服务端 |
| 4 | TCPClient | TCP客户端 |
| 5 | TCPSeed | TCPServer的客户端连接后产生，不可主动创建 |
| 6 | SSLServer | SSL服务端 |
| 7 | SSLClient | SSL客户端 |
| 8 | SSLSeed | SSL Server的客户端连接后产生，不可主动创建 |

**status状态：**

| 值 | 说明 |
|----|------|
| 0 | 没有连接/已断开 |
| 1 | 正在连接 |
| 3 | 连接成功 |
| 4 | 连接失败 |
| 127 | 连接删除中 |

**其他字段：**

| 字段 | 说明 |
|------|------|
| remotehost | client模式连接的远程地址，server模式暂未设置 |
| remoteport | client模式连接的远程端口，server模式暂未设置，显示默认值-1 |
| localport | server模式显示的是本地监听端口，client模式暂未设置，显示默认值-1 |
| serverConID | type为TCPSeed时表示该连接是从哪个TCPServer创建的，其它type默认是-1 |

### 设置: AT+SOCKET=<type>[,<remotehost>],<port>[,<keepalive>,<conID>]

| 参数 | 类型 | 必选 | 取值范围 | 说明 |
|------|------|:---:|----------|------|
| type | 整数 | 是 | 1~8 | Socket类型（见上表；5为占位类型不可用，8为占位类型不可用） |
| remotehost | 字符串 | 条件 | — | 当type为客户端时必选，表示需要连接的服务器的域名或者IP；server模式不用设置（直接跳过，eg：AT+SOCKET=3,10086） |
| port | 整数 | 是 | — | 客户端时表示要连接的服务器的端口号；服务端时表示本地server需要监听的端口号 |
| keepalive | 整数 | 否 | 0, 1~7200 | TCP keep-alive间隔，0表示禁用，1~7200表示检测间隔，单位：秒（预留功能，暂时没有实现） |
| conID | 整数 | 否 | u32范围 | 指定新连接的ConID |

| 响应 | `connectsuccessConID=<ConID>` → OK |

**示例：**
```
// 连接wifi
AT+WJAP=specter,12345678909
+EVENT:WIFI_CONNECT
OK
+EVENT:WIFI_GOT_IP

// 创建UDPServer
AT+SOCKET=1,10086
connectsuccessConID=1
OK

// 创建UDPClient
AT+SOCKET=2,192.168.3.10,10086
connectsuccessConID=1
OK

// 使用域名创建tcpclient连接
// 使用IP创建tcpclient连接
```

## 4.2.4 AT+SOCKET2 — 创建Socket连接（简化版）

### 查询: AT+SOCKET2?

| 项目 | 内容 |
|------|------|
| 描述 | 同AT+SOCKET? |

### 设置: AT+SOCKET2=<type>,<remotehost>,<remotePort>[,<localPort>,<keepalive>,<conID>]

| 参数 | 类型 | 必选 | 取值范围 | 说明 |
|------|------|:---:|----------|------|
| type | 整数 | 是 | 1~8 | Socket类型：1=占位符，2=UDPClient，3=占位符，4=TCPClient，5=占位符，6=占位符，7=占位符，8=占位符 |
| remotehost | 字符串 | 是 | — | 需要连接的服务器的域名或者IP |
| remotePort | 整数 | 是 | — | 要连接的远端服务器的端口号 |
| localPort | 整数 | 否 | -1, 正整数 | 需要绑定的本地端口号，不需要绑定时设置为-1（随机绑定本地端口号） |
| keepalive | 整数 | 否 | 0, 1~7200 | TCP keep-alive间隔，0表示禁用，1~7200表示检测间隔，单位：秒（UDP模式时该参数无效） |
| conID | 整数 | 否 | u32范围 | 指定新连接的ConID |

| 响应 | `connectsuccessConID=<ConID>` → OK |

## 4.2.5 AT+SOCKETSEND — 通过Socket发送数据（长数据模式）

### 发送: AT+SOCKETSEND=<ConID>,<length>

| 参数 | 类型 | 必选 | 取值范围 | 说明 |
|------|------|:---:|----------|------|
| ConID | 整数 | 是 | — | 创建Socket连接后获取到的连接ID（TCPServer的连接无法发送，只能给客户端连接到TCPServer后创建的seed才能发送数据；UDPserver必须先收到客户端数据才可以发送，发送对象为第一次收到数据的对象） |
| length | 整数 | 是 | — | 要发送的数据长度 |

| 项目 | 内容 |
|------|------|
| 描述 | 向指定连接发送数据，当指令执行完毕后会在第二行出现一个`>`符号，出现这个符号后就可以开始输入数据了（可以输入任意数据，不限定数据内容），当接收到length个字节的数据后就会停止接收，开始发送（如果长度超过单包最大长度数据就会分包，默认超过1024字节后会对数据进行分包） |
| 特点 | 该模式可以发送任意长度数据（超长会被分包），并且可以接收任意字符 |
| 响应 | OK |

| 示例 | `AT+SOCKETSEND=1,3` → `>` → `123` → OK |

## 4.2.6 AT+SOCKETSENDLINE — 通过Socket发送数据（单行模式）

### 发送: AT+SOCKETSENDLINE=<ConID>,<length>,<data>

| 参数 | 类型 | 必选 | 取值范围 | 说明 |
|------|------|:---:|----------|------|
| ConID | 整数 | 是 | — | 创建Socket连接后获取到的连接ID（TCPServer的连接无法发送，只能给客户端连接到TCPServer后创建的seed才能发送数据；UDPserver必须先收到客户端数据才可以发送，发送对象为第一次收到数据的对象） |
| length | 整数 | 是 | — | 要发送的数据长度 |
| data | 字符串 | 是 | — | 要发送的数据 |

| 项目 | 内容 |
|------|------|
| 描述 | 向指定连接发送数据。特点：该模式使用较为简单，但是长度受限（一条AT指令的最大长度有限），如果有特殊字符需要将整个参数用双引号括起来，如果参数中有双引号需要加转义字符 |
| 响应 | OK |

**示例：**
```
// 连接wifi
AT+WJAP=specter,12345678909
+EVENT:WIFI_CONNECT
OK
+EVENT:WIFI_GOT_IP

// 创建UDPClient
AT+SOCKET=2,192.168.3.10,10086
connectsuccessConID=1
OK

// 向ConID1发送数据
AT+SOCKETSENDLINE=1,5,12345
OK
```

| 注释 | 单行模式发送的数据长度有限制，指令的总长度不能超过一条指令的总长度限制。一条指令的总长度默认为1023，ConID为一位数字的时候数据可以发送的总长度为1023-26指令格式数据=997字节 |

## 4.2.7 AT+SOCKETSENDHEX — 通过Socket发送HEX数据（单行模式）

### 发送: AT+SOCKETSENDHEX=<ConID>,<length>,<data>

| 参数 | 类型 | 必选 | 取值范围 | 说明 |
|------|------|:---:|----------|------|
| ConID | 整数 | 是 | — | 创建Socket连接后获取到的连接ID（TCPServer的连接无法发送，只能给客户端连接到TCPServer后创建的seed才能发送数据；UDPserver必须先收到客户端数据才可以发送，发送对象为第一次收到数据的对象） |
| length | 整数 | 是 | — | 要发送的数据长度 |
| data | hex字符串 | 是 | — | 要发送的数据（该数据是字符串形式的hex数据） |

| 响应 | OK |

**示例：**
```
AT+WJAP=test,12345678
+EVENT:WIFI_CONNECT
+EVENT:WIFI_GOT_IP
OK
AT+SOCKET=4,192.168.3.10,10086
connectsuccessConID=1
OK
// 向conid1发送2字节hex数据0x31 0x32
AT+SOCKETSENDHEX=1,2,3132
OK
```

| 注释 | 单行模式发送的数据长度有限制，指令的总长度不能超过一条指令的总长度限制。一条指令的总长度默认为1023，ConID为一位数字的时候数据可以发送的总长度为1023-26指令格式数据=997字节，hex字符串两个字节表示一个hex数据，所以最多发送997/2=498 |

## 4.2.8 AT+SOCKETREAD — 从Socket读取数据

### 读取: AT+SOCKETREAD=<ConID>

| 参数 | 类型 | 必选 | 取值范围 | 说明 |
|------|------|:---:|----------|------|
| ConID | 整数 | 是 | — | 创建Socket连接后获取到的连接ID（TCPServer的连接无法收发数据，只能给客户端连接到TCPServer后创建的seed才能收发送数据；UDPClient需要先发送一次数据之后server端获取到本地的端口才可以向该UDPclient发送数据） |

| 项目 | 内容 |
|------|------|
| 描述 | 从指定连接读取数据。注意：读取的时候是按包读取的，一次读取一包数据 |
| 响应 | `+SOCKETREAD:<ConID>,<len>,<data>` → OK |

## 4.2.9 AT+SOCKETDEL — 删除Socket连接

### 删除: AT+SOCKETDEL=<ConID>

| 参数 | 类型 | 必选 | 取值范围 | 说明 |
|------|------|:---:|----------|------|
| ConID | 整数 | 是 | — | 要删除的连接ID |

| 项目 | 内容 |
|------|------|
| 描述 | 删除指定socket连接。注意：seed因为是客户端发起的，server无法重连，所以seed断开后需要手动删除连接（删除连接后接收到的数据也会被清空） |
| 响应 | OK |

| 示例 | `AT+SOCKETDEL=9` → OK |

## 4.2.10 AT+SOCKETRECVCFG — Socket接收模式

### 设置: AT+SOCKETRECVCFG=<mode>

| 参数 | 类型 | 必选 | 取值范围 | 说明 |
|------|------|:---:|----------|------|
| mode | 整数 | 是 | 0, 1 | 0：被动模式（默认），该模式下收到数据后打印只提示`+EVENT:SocketDown,<ConID>,<length>`不打印数据内容；1：主动模式，该模式下收到socket数据直接将收到的数据以如下格式打印`+EVENT:SocketDown,<ConID>,<length>,<data>` |

| 响应 | OK |

| 注释 | 被动模式可以缓存的数据是以链表形式保存在RAM中，如果没有读取则会一直占用内存，当内存不足时将无法继续缓存数据，新收到的数据将会被丢弃 |

## 4.2.11 AT+SOCKETTT — 进入Socket透传模式

### 进入: AT+SOCKETTT

| 项目 | 内容 |
|------|------|
| 描述 | 进入Socket透传模式。备注：UDPserver默认的透传对象是第一次通信的client客户端 |
| 响应 | `>` → 收到这个表示透传开启了，可以收发数据了。OK → 连续输入三个加号会退出透传，透传退出时打印`\r\nOK\r\n` |

**进入条件（满足任意一个）：**
- 当前仅有一个client连接（通过client透传）
- 仅有一个server和一个seed连接（可以通过客户端连接模组server后产生的seed透传，该模式必须手动进入，无法自动进入）
- 仅有一个UDPClient
- 仅有一个UDPServer（注意，透传模式不建议使用UDPserver，默认透传对象是第一个连接的client端，如果有其他连接向模组发起了通信可能导致后续透传对象出错）
- 输入`+++`后可以退出透传模式，进入AT指令模式

### UDP Server透传模式: AT+SOCKETTT=UDPServerTTMode

| 参数 | 类型 | 必选 | 取值范围 | 说明 |
|------|------|:---:|----------|------|
| UDPServerTTMode | 整数 | 是 | 0, 2 | 0：透传对象固定为第一次通讯的客户端，后续有其他客户端通信也不会改变通信对象；2：透传对象会动态修改为最后一次通信的客户端 |

| 响应 | `>` → 收到这个表示透传开启了，可以收发数据了。OK → 连续输入三个加号会退出透传，透传退出时打印`\r\nOK\r\n` |

**示例：**
```
AT+WJAP=test,123456789    // 连接wifi
OK
AT+SOCKET=4,192.168.31.98,18    // 创建tcpclient
connectsuccessConID=1
OK
AT+SOCKETTT    // 进入透传模式
>sendtomodule  // 此时发送的数据会透传到目标，目标发送的数据会透传到本地
OK             // 当输入连续的三个加号后退出透传模式
#
```

## 4.2.12 AT+SOCKETAUTOTT — 自动透传配置

### 查询: AT+SOCKETAUTOTT?

| 项目 | 内容 |
|------|------|
| 描述 | 查询当前自动透传配置信息 |
| 响应 | `+SOCKETAUTOTT:<type>,<remotehost>,<remoteport>` → OK |

**type类型：**

| 值 | 说明 |
|----|------|
| 0 | 禁用自动进入透传模式 |
| 1 | 自动进入UDPServer透传模式 |
| 2 | 自动进入UDPClient透传模式 |
| 3 | 占位类型，不可用 |
| 4 | 自动进入TCPClient透传模式 |
| 5 | 占位类型，不可用 |
| 6 | 占位类型，不可用 |
| 7 | 占位类型，不可用 |
| 8 | 占位类型，不可用 |

**其他字段：**

| 字段 | 说明 |
|------|------|
| remotehost | client模式连接的远程地址，server模式暂未设置 |
| remoteport | client模式连接的远程端口，server模式暂未设置，显示默认值-1 |
| localport | server模式显示的是本地监听端口，client模式暂未设置，显示默认值-1 |
| serverConID | type为TCPSeed时表示该连接是从哪个TCPServer创建的，其它type默认是-1 |

### 设置: AT+SOCKETAUTOTT=<type>[,<remotehost>],<port>

| 参数 | 类型 | 必选 | 取值范围 | 说明 |
|------|------|:---:|----------|------|
| type | 整数 | 是 | 0~8 | Socket类型（见上表；0=禁用，3/5/6/7/8为占位类型不可用） |
| remotehost | 字符串 | 条件 | — | 当type为客户端时必选，表示需要连接的服务器的域名或者IP；server时不用设置（跳过该参数，eg:AT+SOCKETAUTOTT=1,10086） |
| port | 整数 | 是 | — | 客户端时表示要连接的服务器的端口号；服务端时表示本地server需要监听的端口号 |

| 项目 | 内容 |
|------|------|
| 描述 | 创建对应socket连接后自动进入透传模式。该指令设置完成后需要配合AT+WAUTOCONN使用，配置完成后复位生效。上电后自动连接wifi（AT+WAUTOCONN配置），Wifi连接成功后自动创建socket连接，socket创建成功后自动进入透传模式（本指令设置） |
| 响应 | OK |
| 示例 | `AT+SOCKETAUTOTT=4,www.baidu.com,80` |

## 4.2.13 AT+SSLCRET — SSL证书

### 查询: AT+SSLCRET=<type>

| 参数 | 类型 | 必选 | 取值范围 | 说明 |
|------|------|:---:|----------|------|
| type | 整数 | 是 | 1, 2, 3 | 操作的证书类型：1=CA根证书，2=客户端公钥，3=客户端私钥 |

| 项目 | 内容 |
|------|------|
| 描述 | 查询当前设置的证书内容（只有一个参数时为查询模式） |
| 响应 | `+SSLCRET:<type>,<length>,<证书内容>` → OK |

### 设置: AT+SSLCRET=<type>,<length>

| 参数 | 类型 | 必选 | 取值范围 | 说明 |
|------|------|:---:|----------|------|
| type | 整数 | 是 | 1, 2, 3 | 操作的证书类型：1=CA根证书，2=客户端公钥，3=客户端私钥 |
| length | 整数 | 是 | — | 证书长度（有此参数时表示要设置证书） |

| 项目 | 内容 |
|------|------|
| 描述 | 设置SSL证书。证书为空时客户端不加载证书，自动获取 |
| 响应 | `>` → 收到这个符号表示可以开始写证书了 → OK |

**示例：**
```
// 设置证书
AT+SSLCRET=1,10
>1234567890
OK

// 查询证书
AT+SSLCRET=1
+SSLCRET:1,10,1234567890
OK
```

## 4.2.14 AT+WDOMAIN — DNS域名解析

### 解析: AT+WDOMAIN=<servername>

| 参数 | 类型 | 必选 | 取值范围 | 说明 |
|------|------|:---:|----------|------|
| servername | 字符串 | 是 | — | 需要解析的域名 |

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

| 参数 | 类型 | 必选 | 取值范围 | 说明 |
|------|------|:---:|----------|------|
| DNSIP1 | 字符串 | 是 | — | 域名解析服务器 |
| DNSIP2 | 字符串 | 否 | — | 域名解析服务器 |

| 项目 | 内容 |
|------|------|
| 描述 | 设置DNS域名解析服务器 |
| 响应 | `+WDNS:<DNSIP1>[,DNSIP2]` → OK |
| 示例 | `AT+WDNS=114.114.114.114` → `+WDNS:114.114.114.114` → OK |
