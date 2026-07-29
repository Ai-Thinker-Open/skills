# WiFi指令

## 4.1 基础指令

### 4.1.1 AT+WMODE — WiFi工作模式

#### 查询: AT+WMODE?

| 项目 | 内容 |
|------|------|
| 描述 | 查询WiFi工作模式 |
| 响应 | `+WMODE:<MODE>` → OK |

#### 设置: AT+WMODE=<MODE>,<save_flash>

| 参数 | 说明 |
|------|------|
| MODE | 0=未初始化或关闭WiFi，1=STA，2=AP，3=AP+STA |
| save_flash | 0=不保存到flash，1=保存到flash |

| 注意 | 瑞昱系列(BW16/BW20)如果开启多种无线类型需要按照指定顺序开启。如果开启AP+STA+蓝牙三模或AP+STA混杂模式，需要先开AP，然后连接STA和蓝牙（蓝牙和STA顺序先后没有要求，但必须先开AP）。 |
|------|------|
| 注释 | BW16 save_flash==1时保存flash时MODE不支持0（关闭WiFi） |

### 4.1.2 AT+WDISCONNECT — 断开WiFi连接

| 项目 | 内容 |
|------|------|
| 描述 | 断开WiFi连接，该指令会先关闭WiFi然后再次启动 |
| 等效 | 先执行`AT+WMODE=0,0`然后执行`AT+WMODE=x,0`（x为断开前的WiFi状态） |
| 响应 | OK |

### 4.1.3 AT+WSCAN — 扫描WiFi列表

#### 扫描全部: AT+WSCAN?

| 项目 | 内容 |
|------|------|
| 描述 | 扫描WiFi列表 |
| 响应 | `+WSCAN:index,SSID,CH,SECURITY,RSSI,BSSID` ... OK |

**响应字段说明：**
- index: 序号
- SSID: WiFi名称
- CH: 信道
- SECURITY: 加密方式
- RSSI: 信号强度(dBm)
- BSSID: AP的MAC地址

#### 带过滤扫描: AT+WSCAN=[<ssid>,<mac>,<channel>,<rssi>]

| 参数 | 说明 |
|------|------|
| ssid | 扫描指定SSID（为空代表跳过） |
| mac | 扫描指定MAC地址 |
| channel | 扫描指定通道号 |
| rssi | 过滤低于此信号强度的AP，单位dBm，默认-100，范围[-100,40] |

| 示例 | `AT+WSCAN=AXK` → 扫描SSID为AXK的AP |

### 4.1.4 AT+WSCANACTIVE — 主动模式扫描指定SSID

| 项目 | 内容 |
|------|------|
| 描述 | 主动模式扫描指定SSID |
| 参数 | ssid: 需要扫描的SSID |
| 响应 | `+WSCANACTIVE:SSID,CH,SECURITY,RSSI,BSSID` ... OK |
| 示例 | `AT+WSCANACTIVE=test` → `+WSCANACTIVE:test,44,WPA/WPA2TKIP,-31,11:22:33:44:55:66` → OK |
| 备注 | 已适配型号：BW16 |

### 4.1.5 AT+WSDHCP — STA模式DHCP参数

#### 查询: AT+WSDHCP?

| 项目 | 内容 |
|------|------|
| 描述 | 查询STA模式的DHCP设置（信息保存到flash） |
| 响应 | `+WSDHCP:<MODE>[,<IP>,<MASK>,<GATEWAY>]` → OK |
| 示例 | `AT+WSDHCP?` → `+WSDHCP:0,192.168.31.199,255.255.255.0,192.168.31.1` → OK |

#### 设置: AT+WSDHCP=<MODE>[,<IP>,<MASK>,<GATEWAY>]

| 参数 | 说明 |
|------|------|
| MODE | 0=禁用DHCP使用静态IP，1=使用DHCP获取IP |
| IP | 模块IP地址（静态IP时需设置） |
| MASK | 子网掩码（静态IP时需设置） |
| GATEWAY | 网关（静态IP时需设置） |

| 示例 | `AT+WSDHCP=0,192.168.31.199,255.255.255.0,192.168.31.1` → OK |

### 4.1.6 AT+WJAP — 连接AP

#### 查询: AT+WJAP?

| 项目 | 内容 |
|------|------|
| 描述 | 查询WiFi联网信息（从硬件获取的当前状态） |
| 响应 | `+WJAP:<status>,<ssid>,<pwd>,<bssid>,<Security>,<MAC>,<ch>,<IP>,<gateway>` → OK |
| 推荐 | 推荐使用`AT+STAINFO?`查询，该指令查询如果SSID或密码中有逗号会导致解析错误 |

**status状态码：**
- 0: 没有连接WiFi（初始状态或STA模式未开启）
- 1: 正在连接WiFi或WiFi重连中
- 2: 已连接WiFi，还未获取到IP
- 3: 已连接WiFi，已获取到IP
- 4: WiFi连接失败（超过重连次数）

**Security加密方式：** Open, WEP, WPATKIP, WPAAES, WPAMixed, WPA2AES, WPA2TKIP, WPA2Mixed, WPA/WPA2TKIP, WPA/WPA2AES, WPA/WPA2Mixed, WPA2Enterprise, WPA/WPA2Enterprise, WPA3-ASEAES, UnknownType

#### 连接: AT+WJAP=<ssid>,<pwd>[,<bssid>]

| 参数 | 说明 |
|------|------|
| ssid | AP的SSID |
| pwd | 连接密码 |
| bssid | AP的MAC地址（可选，用于区分同名SSID，格式小写冒号分隔如94:c9:60:12:34:56） |

| 响应 | OK |
| 示例 | `AT+WJAP=super_2G,123456798` → OK |

### 4.1.7 AT+STAINFO — 查询WiFi连接信息

#### 查询: AT+STAINFO?

| 项目 | 内容 |
|------|------|
| 描述 | 查询WiFi联网信息（从硬件获取的当前状态） |
| 响应 | `+STAINFO:<status>` / `SSID:<ssid>` / `Password:<pwd>` / `<bssid>,<Security>,<MAC>,<ch>,<IP>,<gateway>` → OK |
| 示例 | `AT+STAINFO?` → `+STAINFO:3` / `SSID:test` / `Password:123456789` / `e1:f9:8a:aa:fc:4f,WPA/WPA2TKIP,b2:e3:41:c2:b3:42,5,192.168.3.125,192.168.3.1` → OK |

### 4.1.8 AT+WJEAP — 连接企业认证热点

#### 连接: AT+WJEAP=<type>,<ssid>,<identity>,<pwd>

| 参数 | 说明 |
|------|------|
| type | EAP加密方式：1=PEAP，2=TLS，3=TTLS，4=FAST |
| ssid | AP的SSID |
| identity | 登录用户名 |
| pwd | 用户密码 |

| 响应 | OK |
| 示例 | `AT+WJEAP=1,EAPTEST,test,test` → `+EVENT:WIFI_CONNECT` / `+EVENT:WIFI_GOT_IP` / OK |
| 已适配 | BW16（1:PEAP/2:TLS/3:TTLS/4:FAST），BW20（1:PEAP/2:TLS/3:TTLS/4:FAST） |

### 4.1.9 AT+WAUTOCONN — 上电自动重连

#### 查询: AT+WAUTOCONN?

| 项目 | 内容 |
|------|------|
| 描述 | 查询是否启用上电自动连接功能 |
| 响应 | `+WAUTOCONN:<status>` → OK（0=不自动连接，1=自动连接） |

#### 设置: AT+WAUTOCONN=<status>[,<ssid>,<pwd>,<bssid>]

| 参数 | 说明 |
|------|------|
| status | 0=禁用，1=使能 |
| ssid | AP的SSID（可选） |
| pwd | 连接密码（可选） |
| bssid | AP的MAC地址（可选） |

| 响应 | OK |
|------|------|
| 注 | 该指令指定的WiFi没有对连接进行检查，即使信息错误也会自动保存。建议先用AT+WJAP连接成功验证后再用AT+WAUTOCONN=1设置。 |

| 示例 |
|------|
| `AT+WAUTOCONN=1` — 将上次连接成功的WiFi信息配置为上电自动连接 |
| `AT+WAUTOCONN=1,test01,12345678` — 保存SSID和密码 |
| `AT+WAUTOCONN=1,test01,12345678,94:c9:60:12:34:56` — 保存SSID、密码和BSSID |

### 4.1.10 AT+WAPDHCP — AP模式DHCP参数

#### 查询: AT+WAPDHCP?

| 项目 | 内容 |
|------|------|
| 描述 | 查询AP模式的DHCP设置（信息保存到flash） |
| 响应 | `+WAPDHCP:<MODE>[,<start_ip>,<end_ip>,<GATEWAY>]` → OK |

#### 设置: AT+WAPDHCP=<MODE>,<start_ip>,<end_ip>,<GATEWAY>

| 参数 | 说明 |
|------|------|
| MODE | 0=禁用DHCP，1=使能DHCP |
| start_ip | DHCP起始地址（如192.168.43.100） |
| end_ip | DHCP结束地址（如192.168.43.200） |
| GATEWAY | 网关IP（使能DHCP时需设置，模组IP就是网关IP，如192.168.43.1） |

### 4.1.11 AT+WAP — AP模式WiFi参数

#### 查询: AT+WAP?

| 项目 | 内容 |
|------|------|
| 描述 | 查询AP参数信息（从硬件获取的当前状态） |
| 响应 | `+WAP:<ssid>,<pwd>,<security>,<channel>,<maxconn>,<ssidhidden>,<mac>,<IP>,<Gateway>` / `ClientNum:<clientnumber>` / `Client<id>MAC:<xx:xx:xx:xx:xx:xx>` → OK |

#### 设置: AT+WAP=<ssid>,<pwd>,<channel>,<maxconn>,<ssidhidden>

| 参数 | 说明 |
|------|------|
| ssid | WiFi名称 |
| pwd | WiFi密码（空字符串表示无密码） |
| channel | 信道 |
| maxconn | 最大连接数量（不写默认3） |
| ssidhidden | 0=不隐藏SSID，1=隐藏 |

### 4.1.12 AT+WAPINFO — 查询AP信息

#### 查询: AT+WAPINFO?

| 项目 | 内容 |
|------|------|
| 描述 | 查询AP参数信息（从硬件获取的当前状态） |
| 响应 | `+WAP:<ssid>,<pwd>,<security>,<channel>,<maxconn>,<ssidhidden>,<mac>,<IP>,<Gateway>` / `ClientNum:<clientnumber>` / `Client<id>MAC:<xx:xx:xx:xx:xx:xx>,IP:<xxx.xxx.xxx.xxx>` → OK |

### 4.1.13 AT+PING — Ping测试

#### 执行: AT+PING=<addr>[,<count>]

| 参数 | 说明 |
|------|------|
| addr | IP或域名 |
| count | ping次数（默认3次，loop表示一直ping不返回，此时只能重启模组） |

| 响应 | 成功: `+PING:<time>` → OK（time为平均延时） / 失败: `+PING:TIMEOUT` → ERROR |

### 4.1.14 AT+CIPSTAMAC_DEF — WiFi Station MAC地址

#### 查询: AT+CIPSTAMAC_DEF?

| 项目 | 内容 |
|------|------|
| 描述 | 查询WiFi Station的MAC地址 |
| 响应 | `+CIPSTAMAC_DEF:<MAC>` → OK（MAC格式84f3ebdd9e63，小写无分隔） |

#### 设置: AT+CIPSTAMAC_DEF=<MAC>

| 项目 | 内容 |
|------|------|
| 描述 | 设置WiFi Station的MAC地址（暂时不支持） |
| 参数 | MAC：小写无分隔16进制 |

### 4.1.15 AT+WCOUNTRY — WiFi国家码

#### 查询: AT+WCOUNTRY?

| 项目 | 内容 |
|------|------|
| 描述 | 查询配置的国家码 |
| 响应 | `+WCOUNTRY:<country_code>` → OK |

#### 设置: AT+WCOUNTRY=<country_code>

| 参数 | 说明 |
|------|------|
| 0 | 不指定（使用SDK默认） |
| 1 | JP日本 |
| 2 | AS美属萨摩亚 |
| 3 | CA加拿大 |
| 4 | US美国 |
| 5 | CN中国 |
| 6 | HK中国香港 |
| 7 | TW中国台湾 |
| 8 | MO中国澳门 |
| 9 | IL以色列 |
| 10 | SG新加坡 |
| 11 | KR韩国 |
| 12 | TR土耳其 |
| 13 | AU澳大利亚 |
| 14 | ZA南非 |
| 15 | BR巴西 |

| 备注 | 重启后生效 |

### 4.1.16 AT+WCONFIG — 手机配网

#### 查询: AT+WCONFIG?

| 项目 | 内容 |
|------|------|
| 描述 | 查询配网状态 |
| 响应 | `+WCONFIG:<status>` → OK |

#### 设置: AT+WCONFIG=<status>[,<name>]

| 参数 | 说明 |
|------|------|
| status | 0=关闭配网任务，1=开启WiFi配网，2=开启蓝牙配网，3=开启AirKiss配网，9=开启blufi配网，10=WPS配网 |
| name | 自定义配网广播名称（仅espBluFi协议支持） |

**配网协议（中间件）：** 1=smartconfig，2=blufi，3=AirKiss，4=web配网

**非中间件：**
- BW16: 1=瑞昱SimpleConfig，2=瑞昱WiFiConfig，3=微信AirKiss，9=blufi，10=WPS
- Ai-WB2: 1=WiFi配网(esptouch)，2=蓝牙配网(espBluFi)，3=微信AirKiss，9=blufi

| 备注 | 配网成功/超时会自动返回关闭状态 |

### 4.1.17 AT+WSCANOPT — 筛选WiFi扫描显示信息

#### 查询: AT+WSCANOPT?

| 项目 | 内容 |
|------|------|
| 描述 | 查询设置的WiFi扫描显示信息 |
| 响应 | `+WSCANOPT:<option>` → OK |

#### 设置: AT+WSCANOPT=<option>

| 参数 | 说明 |
|------|------|
| option | 32位掩码，默认0xFF。bit0=SSID，bit1=channel，bit2=security，bit3=rssi，bit4=MAC。支持16进制(0xXY)和10进制输入。 |

| 示例 | `AT+WSCANOPT=15` → `+WSCANOPT:0x0f` → OK |

### 4.1.18 AT+WRSSI — 查询WiFi信号强度

#### 查询: AT+WRSSI? 或 AT+WRSSI

| 项目 | 内容 |
|------|------|
| 描述 | 查询WiFi连接信号强度 |
| 响应 | `+WRSSI:<rssi>` → OK |

### 4.1.19 AT+BLUFISEND — 发送蓝牙配网自定义数据

#### 发送: AT+BLUFISEND=<length>

| 项目 | 内容 |
|------|------|
| 描述 | 发送蓝牙配网自定义数据 |
| 响应 | `>` → 输入数据 → OK |
| 示例 | `AT+BLUFISEND=5` → `>` → `hello` → OK |
