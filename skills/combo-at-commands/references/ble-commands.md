# BLE蓝牙专有指令

## 5.1 基础指令

### 5.1.1 AT+BLEMAC — 蓝牙MAC地址

#### 查询: AT+BLEMAC?

| 项目 | 内容 |
|------|------|
| 描述 | 查询蓝牙MAC地址 |
| 响应 | `+BLEMAC:<MAC>` → OK |

#### 设置: AT+BLEMAC=<MAC>

| 参数 | 说明 |
|------|------|
| MAC | 蓝牙MAC地址，格式小写无分隔（如ab5f8d9ebb01） |

| 响应 | OK |
| 备注 | 重启后生效 |

### 5.1.2 AT+BLEMODE — 蓝牙工作模式

#### 查询: AT+BLEMODE?

| 项目 | 内容 |
|------|------|
| 描述 | 查询蓝牙工作模式 |
| 响应 | `+BLEMODE:<mode>` → OK |

#### 设置: AT+BLEMODE=<mode>

| 参数 | 说明 |
|------|------|
| mode | 0=从机模式，1=主机模式，2=iBeacon模式，9=蓝牙关闭 |

| 响应 | OK |
|------|------|
| 注意 | 设置后立即执行，需先设好蓝牙参数后再启动蓝牙 |
| 瑞昱系列 | 如果开启多种无线类型需按指定顺序：先开AP，再开STA和蓝牙 |
| 注释 | PB系列默认模式0（从机），TB系列默认模式0（从机） |

### 5.1.3 AT+BLERFPWR — 蓝牙发射功率

#### 查询: AT+BLERFPWR?

| 项目 | 内容 |
|------|------|
| 描述 | 查询蓝牙发射功率 |
| 响应 | `+BLERFPWR:MAX:<max_power>MIN:<min_power>CURRENT:<cur_power>` → OK |
| 说明 | max_power=最大功率，min_power=最小功率，cur_power=当前功率 |

#### 设置: AT+BLERFPWR=<power>

| 参数 | 说明 |
|------|------|
| power | 蓝牙发射功率，取值为整数、MAX（最大）、MIN（最小） |

| 响应 | OK |
|------|------|
| 注意 | 需在蓝牙关闭状态下设置 |
| 注释 | PB/TB系列默认当前发射功率为最大发射功率10 |

### 5.1.4 AT+BLESTATE — 蓝牙连接状态

#### 查询: AT+BLESTATE?

| 项目 | 内容 |
|------|------|
| 描述 | 查询蓝牙连接状态 |
| 响应 | `+BLESTATE:<status>` → OK |
| status | 0=未连接，1=已连接 |

### 5.1.5 AT+BLEDISCON — 断开蓝牙连接

| 项目 | 内容 |
|------|------|
| 描述 | 断开蓝牙连接 |
| 响应 | OK |

### 5.1.6 AT+BLEMTU — 蓝牙MTU

#### 查询: AT+BLEMTU?

| 项目 | 内容 |
|------|------|
| 描述 | 查询蓝牙MTU |
| 响应 | `+BLEMTU:<MTU>` → OK |

#### 设置: AT+BLEMTU=<mtu>

| 参数 | 说明 |
|------|------|
| mtu | 蓝牙MTU，取值23~250 |

| 注释 | PB系列默认MTU为23，TB系列默认MTU为247 |

### 5.1.7 AT+BLESEND — 蓝牙透传发送数据

#### 发送: AT+BLESEND=<len>,<data>

| 参数 | 说明 |
|------|------|
| len | 数据长度（字节） |
| data | 数据内容，长度应与len一致 |

| 响应 | OK |

### 5.1.8 AT+BLESENDRAW — 蓝牙透传发送HEX数据

#### 发送: AT+BLESENDRAW=<len>

| 参数 | 说明 |
|------|------|
| len | 数据长度（字节） |

| 响应 | `>` → 输入数据 → OK |

### 5.1.9 AT+BLESERUUID — 透传服务UUID

#### 查询: AT+BLESERUUID?

| 项目 | 内容 |
|------|------|
| 描述 | 查询蓝牙透传服务的UUID |
| 响应 | `+BLESERUUID:<UUID>` → OK |

#### 设置: AT+BLESERUUID=<UUID>

| 参数 | 说明 |
|------|------|
| UUID | 支持16位和128位模式。128位：字符串长度32位（如00112233445566778899aabbccddeeff）。16位：当128位UUID为0000XXXX00001000800000805F9B34FB时，第17~32位设置为16位UUID。 |

| 响应 | OK |
|------|------|
| 注意 | 仅允许在蓝牙关闭状态下设置 |
| 默认 | 主服务UUID: 55535343fe7d4ae58fa99fafd205e455 |
| 模式支持 | BW16: 128位；WB2系列: 16/128位 |

### 5.1.10 AT+BLETXUUID — TX特征UUID

#### 查询: AT+BLETXUUID?

| 项目 | 内容 |
|------|------|
| 响应 | `+BLETXUUID:<UUID>` → OK |

#### 设置: AT+BLETXUUID=<UUID>

| 参数 | 说明 |
|------|------|
| UUID | 同BLESERUUID格式 |

| 注意 | 仅允许在蓝牙关闭状态下设置 |
| 默认 | TX UUID: 49535343884143f4a8d4ecbe34729bb3 |
| 属性 | TX对应的蓝牙服务属性为NOTIFY |

### 5.1.11 AT+BLERXUUID — RX特征UUID

#### 查询: AT+BLERXUUID?

| 项目 | 内容 |
|------|------|
| 响应 | `+BLERXUUID:<UUID>` → OK |

#### 设置: AT+BLERXUUID=<UUID>

| 参数 | 说明 |
|------|------|
| UUID | 同BLESERUUID格式 |

| 注意 | 仅允许在蓝牙关闭状态下设置 |
| 默认 | RX UUID: 495353431e4d4bd9ba6123c647249616 |
| 属性 | RX对应的蓝牙属性为WRITE |

### 5.1.12 AT+TRANSENTER — 进入蓝牙透传模式

#### 进入: AT+TRANSENTER

| 项目 | 内容 |
|------|------|
| 描述 | 进入蓝牙透传模式 |
| 响应 | OK |
| 退出 | 输入`+++`后退出透传，进入AT指令模式 |

#### 配置自动进入: AT+TRANSENTER=<autoEntry>,<saveFlash>

| 参数 | 说明 |
|------|------|
| autoEntry | 0=蓝牙连接后不自动进入透传，1=蓝牙连接后自动进入透传 |
| saveFlash | 0=不保存到flash，1=保存到flash |

## 5.2 从机指令

### 5.2.1 +DATA — 主机模式收到透传数据（URC）

| 项目 | 内容 |
|------|------|
| 描述 | 主机模式下收到蓝牙透传UUID通道发送过来的数据 |
| 格式 | `+DATA:<len>,<data>` |
| len | 数据长度（字节） |
| data | 数据内容 |
| 备注 | 仅AT模式下有效，透传模式下直接收到原始data数据 |

### 5.2.2 AT+BLENAME — 蓝牙设备名称

#### 查询: AT+BLENAME?

| 项目 | 内容 |
|------|------|
| 描述 | 查询蓝牙名称 |
| 响应 | `+BLENAME:<blename>` → OK |

#### 设置: AT+BLENAME=<blename>

| 参数 | 说明 |
|------|------|
| blename | 蓝牙名称（UTF-8格式，支持中文） |

| 注意 | 仅允许在蓝牙关闭状态下设置 |
| 默认 | ai-thinker |

### 5.2.3 AT+BLECONINTV — 蓝牙连接间隔

#### 查询: AT+BLECONINTV?

| 项目 | 内容 |
|------|------|
| 响应 | `+BLECONINTV:<min_interval>,<max_interval>,<latency>,<timeout>` → OK |

#### 设置: AT+BLECONINTV=<min_interval>,<max_interval>,<latency>,<timeout>

| 参数 | 说明 |
|------|------|
| min_interval | 最小连接间隔，6~3200（实际时间=值×1.25ms，范围7.5ms~4s） |
| max_interval | 最大连接间隔，6~3200（实际时间=值×1.25ms，范围7.5ms~4s） |
| latency | 延时（可跳过几次连接），0~499 |
| timeout | 超时时间，10~3200（实际时间=值×10ms，即100ms~32s），要求timeout×10 > (1+latency)×max_interval×1.25 |

| 注意 | 仅允许在蓝牙关闭状态下设置 |
| 注释 | PB系列默认: +BLECONINTV:6,12,0,200 |

### 5.2.4 AT+BLEAUTH — 蓝牙配对码

#### 查询: AT+BLEAUTH?

| 项目 | 内容 |
|------|------|
| 响应 | `+BLEAUTH:<pind>` → OK |

#### 设置: AT+BLEAUTH=<pind>

| 参数 | 说明 |
|------|------|
| pind | 6位数字配对码（如123456），或DISENABLE禁用 |

| 注意 | 仅允许在蓝牙关闭状态下设置 |
| 默认 | 不开启 |

### 5.2.5 AT+BLEADVINTV — 蓝牙广播间隔

#### 查询: AT+BLEADVINTV?

| 项目 | 内容 |
|------|------|
| 响应 | `+BLEADVINTV:<intv>` → OK |

#### 设置: AT+BLEADVINTV=<intv>

| 参数 | 说明 |
|------|------|
| intv | 广播间隔，取值160~16384，广播间隔=intv×0.625ms |

| 注意 | 仅允许在蓝牙关闭状态下设置 |
| 注释 | PB默认参数320，TB默认参数800 |

### 5.2.6 AT+BLEADVDATA — 蓝牙广播数据

#### 查询: AT+BLEADVDATA?

| 项目 | 内容 |
|------|------|
| 描述 | 查询当前设置的蓝牙广播数据 |
| 响应 | `+BLEADVDATA:<data>` → OK |
| 备注 | 默认广播数据8字节，前6字节为蓝牙MAC地址+透传服务UUID前两个字节 |

#### 设置: AT+BLEADVDATA=<data>

| 参数 | 说明 |
|------|------|
| data | 蓝牙数据（hex字符串，最大32字节，如00112233445566778899aabbccddeeff） |

| 注意 | 仅允许在蓝牙关闭状态下设置 |
| 默认 | MAC+55e4（主服务uuid前四个），如40154641871855e4 |

### 5.2.7 AT+BLEADVEN — 蓝牙广播使能

#### 查询: AT+BLEADVEN?

| 项目 | 内容 |
|------|------|
| 响应 | `+BLEADVEN:<status>` → OK |

#### 设置: AT+BLEADVEN=<status>

| 参数 | 说明 |
|------|------|
| status | 0=关闭，1=开启 |

| 注意 | 仅允许在蓝牙从机状态下设置 |
| 默认 | 开启 |

## 5.3 主机指令

### 5.3.1 AT+BLESCAN — 蓝牙扫描

#### 执行: AT+BLESCAN

| 项目 | 内容 |
|------|------|
| 描述 | 蓝牙主机模式下发起扫描 |
| 响应 | OK（表示指令发送成功，扫描实际未结束） |
| 扫描结果 | `DevicesFound:id/total` / `name:<name>` / `MAC:<MAC>` / `rssi:<rssi>` |

**响应字段说明：**
- id/total: 当前扫描到的设备序号/总共扫描到的数量
- name: 蓝牙名称（无则显示N/A）
- MAC: 小写不加冒号
- rssi: 信号强度

| 注释 | PB系列默认扫描时间5秒，扫描间隔230×0.625ms，扫描窗口160×0.625ms。TB系列默认扫描时间2秒，扫描间隔160×0.625ms，扫描窗口160×0.625ms |

### 5.3.2 AT+BLECONNECT — 连接指定蓝牙

#### 连接: AT+BLECONNECT=<MAC>

| 参数 | 说明 |
|------|------|
| MAC | 连接目标MAC地址（如A4C13812505C） |

| 响应 | `Connecting......` → OK |
|------|------|
| 注意 | 单次连接，连接失败后不自动重连，连接成功后断开也不自动重连 |

### 5.3.3 AT+BLEAUTOCON — 主机自动连接从机

#### 设置: AT+BLEAUTOCON=<MAC>,<UUID>,<save_flash>

| 参数 | 说明 |
|------|------|
| MAC | 连接目标MAC地址（如A4C13812505C），不需要设为FALSE |
| UUID | 连接指定UUID的末两位（如E455），不需要设为FALSE |
| save_flash | 0=仅本次连接，1=保存到flash并开机自动连接 |

| 响应 | `+EVENT:BLE_CONNECTED`（连接成功）或 `+BLEAUTOCON:Waitconnect`（未扫描到，后台继续扫描） |
|------|------|
| 备注 | MAC和UUID任意一个设置即可实现连接，都设为FALSE则关闭自动连接。首次连接成功后才会不停主动连接。 |

### 5.3.4 AT+BLEDISAUTOCON — 取消自动扫描连接

| 项目 | 内容 |
|------|------|
| 描述 | 取消启动自动扫描连接蓝牙 |
| 响应 | OK |

## 5.4 BLE iBeacon指令

### 5.4.1 AT+BLEIBCNUUID — iBeacon UUID

#### 查询: AT+BLEIBCNUUID?

| 项目 | 内容 |
|------|------|
| 响应 | `+BLEIBCNIIUD:<iBeacon>` → OK |

#### 设置: AT+BLEIBCNUUID=<iBeacon>

| 参数 | 说明 |
|------|------|
| iBeacon | UUID（长度16字节，字符串32位，如00112233445566778899aabbccddeeff） |

| 注意 | 仅允许在蓝牙关闭状态下设置 |

### 5.4.2 AT+BLEIBCNDATA — iBeacon数据

#### 查询: AT+BLEIBCNDATA?

| 项目 | 内容 |
|------|------|
| 响应 | `+BLEIBCNDATA:<companyID>,<major>,<minor>,<power>` → OK |
| 示例 | `AT+BLEIBCNDATA?` → `+BLEIBCNDATA:4c00,2774,6b74,c5` → OK |

#### 设置: AT+BLEIBCNDATA=<companyID>,<MAJOR>,<MINOR>,<POWER>

| 参数 | 说明 |
|------|------|
| companyID | 2字节16进制数据（如11aa） |
| MAJOR | 2字节16进制数据（如11aa） |
| MINOR | 2字节16进制数据（如11aa） |
| POWER | 1字节16进制数据（如aa） |

| 注意 | 仅允许在蓝牙关闭状态下设置 |

## 5.5 BLE MESH指令

### 5.5.1 SIG-MESH

#### AT+PROVISION — 蓝牙配网使能

| 项目 | 内容 |
|------|------|
| 描述 | 蓝牙设置启动配网功能 |
| 备注 | 当节点处于unProvisioning状态（未配网），不发送广播，网关无法扫描到此设备。需使用此指令使能节点。已配网的设备自动接入mesh网络。 |
| 响应 | OK |

#### AT+MESHSEND — SIG-MESH发送数据

#### 发送: AT+MESHSEND=<addr>,<opcode>,<data>

| 参数 | 说明 |
|------|------|
| addr | 目标地址 |
| opcode | 操作码：1=set(D18888)，2=get(D08888)，3=ACK(D38888)，4=删除节点(D28888) |
| data | JSON格式数据 |

**data示例：**
```json
{"mesh_datavendor":{"daddr":3,"saddr":2,"opcode":d38888,"data_len":2,"data":"0101","ret":1}}
```

#### AT+MESHADDR — 查询节点地址

| 项目 | 内容 |
|------|------|
| 响应 | `+MESHADDR:<addr>` → OK |

#### AT+MESHSTATE — 查询配网状态

| 项目 | 内容 |
|------|------|
| 响应 | `+MESHSTATE:<status>` → OK（0=失败，1=成功） |

### 5.5.2 ALI-MESH

#### aliGenie_data — 天猫精灵下发数据（URC）

| 项目 | 内容 |
|------|------|
| 格式 | JSON字符串，包含daddr/saddr/opcode/data_len/data字段 |

#### AT+AliGenie — 设置天猫精灵三元组

#### 设置: AT+AliGenie=<pid>,<mac>,<secret>

| 参数 | 说明 |
|------|------|
| pid | 三元组产品ID（8位） |
| mac | 三元组物理地址（12位） |
| secret | 三元组密钥（32位） |

| 注意 | 全部为16进制字符串 |

#### AT+SEND2ALI — 向天猫精灵上报数据

#### 发送: AT+SEND2ALI=<opcode>,<param>

| 参数 | 说明 |
|------|------|
| opcode | 操作码（长度6位/4位） |
| param | 上报参数（长度最多20位） |

| 示例 | `AT+SEND2ALI=8204,01` — 上报状态为开 |

---

## 5.6 BLE 通信实用指南

### 5.6.1 透传数据收发详解

Combo模组的BLE通信以**透传模式**为核心，数据流路径如下：

```
手机APP  ←→  BLE透传UUID通道  ←→  模组串口AT指令
         TX特征(NOTIFY)    →  模组→手机
         RX特征(WRITE)     ←  手机→模组
```

**默认UUID配置：**

| 项目 | 128位UUID | 说明 |
|------|-----------|------|
| 主服务 | `55535343fe7d4ae58fa99fafd205e455` | BLE透传服务 |
| TX特征 | `49535343884143f4a8d4ecbe34729bb3` | NOTIFY属性，模组→手机 |
| RX特征 | `495353431e4d4bd9ba6123c647249616` | WRITE属性，手机→模组 |

**AT模式下的数据收发：**

| 方向 | 指令/URC | 说明 |
|------|----------|------|
| 模组→手机 | `AT+BLESEND=<len>,<data>` | 文本数据 |
| 模组→手机 | `AT+BLESENDRAW=<len>` → `>` → 输入数据 | HEX数据 |
| 手机→模组 | `+DATA:<len>,<data>` | URC自动上报（仅AT模式） |

**透传模式下的数据收发：**

| 方向 | 操作 | 说明 |
|------|------|------|
| 进入 | `AT+TRANSENTER` → `>` | 进入透传模式 |
| 模组→手机 | 串口直接输入数据 | 数据直接转发到BLE通道 |
| 手机→模组 | 手机APP发送数据 | 数据直接输出到串口 |
| 退出 | `+++` → `OK` | 回到AT指令模式 |

### 5.6.2 MTU 与数据分包

MTU（Maximum Transmission Unit）决定了单次BLE传输的最大数据长度。

| 参数 | 说明 |
|------|------|
| 默认值 | PB系列=23字节，TB系列=247字节 |
| 取值范围 | 23~250字节 |
| 设置指令 | `AT+BLEMTU=<mtu>`（需蓝牙关闭状态） |
| 查询指令 | `AT+BLEMTU?` |

**分包规则：**

| 场景 | 行为 |
|------|------|
| `AT+BLESEND` 数据长度 ≤ MTU | 单包发送 |
| `AT+BLESEND` 数据长度 > MTU | 自动分包发送（协议栈处理） |
| 手机→模组 数据长度 > MTU | 多包发送，模组自动重组后通过`+DATA`上报 |

**MTU优化建议：**

| 目标 | 建议MTU | 说明 |
|------|---------|------|
| 兼容性优先 | 23 | BLE 4.0默认值，兼容所有设备 |
| 速度优先 | 247 | TB系列默认，减少分包次数 |
| 最大吞吐 | 250 | 需两端协商支持 |

### 5.6.3 连接参数优化

`AT+BLECONINTV` 控制BLE连接的通信参数，直接影响**功耗**和**实时性**。

**参数关系：**

```
连接间隔 = interval × 1.25ms
实际通信间隔 = interval × 1.25ms × (1 + latency)
超时要求 = timeout × 10ms > (1 + latency) × max_interval × 1.25ms
```

**场景化配置推荐：**

| 场景 | min_interval | max_interval | latency | timeout | 特点 |
|------|:---:|:---:|:---:|:---:|------|
| 低功耗传感器 | 800 | 1600 | 4 | 600 | 间隔长+跳过连接，最省电 |
| 实时控制 | 6 | 12 | 0 | 200 | 最短间隔，响应最快 |
| 均衡模式 | 100 | 200 | 2 | 300 | 功耗和响应兼顾 |
| 大数据传输 | 6 | 6 | 0 | 200 | 最短间隔+无跳过，吞吐最大 |

**默认配置：** `AT+BLECONINTV=6,12,0,200`（PB系列，实时性优先）

### 5.6.4 安全配对

Combo模组支持**配对码（Passkey）** 配对方式。

**配对流程：**

```
步骤1: 设置配对码（蓝牙关闭状态下）
  AT+BLEAUTH=123456 → OK

步骤2: 启动蓝牙并广播
  AT+BLEMODE=0 → OK
  AT+BLEADVEN=1 → OK

步骤3: 手机连接时弹出配对码输入框
  手机端输入 123456 完成配对

步骤4: 禁用配对码（如需）
  AT+BLEAUTH=DISENABLE → OK
```

**安全等级说明：**

| 模式 | 指令 | 安全性 | 说明 |
|------|------|:---:|------|
| 无配对 | 不设置AT+BLEAUTH | 低 | 默认模式，任何设备可连接 |
| 配对码 | `AT+BLEAUTH=6位数字` | 中 | 连接时需输入6位数字配对码 |

> 💡 Combo模组当前仅支持Passkey配对方式。Just Works和OOB等高级配对方式暂不支持。

### 5.6.5 广播参数调优

**广播间隔影响：**

| 广播间隔 | 计算公式 | 扫描发现速度 | 功耗 |
|:---:|------|:---:|:---:|
| 160 | 160×0.625=100ms | 最快 | 最高 |
| 320 | 320×0.625=200ms | 快 | 中（PB默认） |
| 800 | 800×0.625=500ms | 中等 | 低（TB默认） |
| 16384 | 16384×0.625=10.24s | 最慢 | 最低 |

**自定义广播数据：**

```
AT+BLEADVDATA=<hex数据>  // 最大32字节
```

默认广播数据 = 6字节MAC + 2字节服务UUID前缀（55e4），共8字节。
自定义广播数据会覆盖默认值。

### 5.6.6 主机模式通信

**从机模式 vs 主机模式：**

| 模式 | 设置 | 角色 | 典型场景 |
|------|------|------|----------|
| 从机 | `AT+BLEMODE=0` | 被连接方 | 模组作为外设，手机连接模组 |
| 主机 | `AT+BLEMODE=1` | 发起连接方 | 模组连接其他BLE设备（传感器/手环等） |

**主机模式通信流程：**

```
步骤1: 设置为主机模式
  AT+BLEMODE=1 → OK

步骤2: 扫描周围设备
  AT+BLESCAN → OK
  DevicesFound:1/5
  name:Sensor_01 MAC:a4c13812505c rssi:-45
  ...

步骤3: 连接指定设备
  AT+BLECONNECT=a4c13812505c → Connecting...... → OK
  URC: +EVENT:BLE_CONNECTED

步骤4: 收发数据（透传UUID通道）
  发送: AT+BLESEND=5,hello → OK
  接收: +DATA:5,hello  （URC自动上报）

步骤5: 断开连接
  AT+BLEDISCON → OK
```

**自动重连配置：**

```
// 按MAC自动连接，保存到flash，开机自动连接
AT+BLEAUTOCON=a4c13812505c,FALSE,1 → OK

// 按UUID末两位自动连接
AT+BLEAUTOCON=FALSE,E455,1 → OK

// 取消自动连接
AT+BLEDISAUTOCON → OK
```

> 💡 `AT+BLEAUTOCON` 首次连接成功后才会持续自动重连。如未扫描到目标设备，会返回 `+BLEAUTOCON:Waitconnect` 并在后台持续扫描。
