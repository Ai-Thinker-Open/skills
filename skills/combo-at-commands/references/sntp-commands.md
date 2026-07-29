# SNTP时间指令

## 4.5.1 AT+SNTPTIME — 查询SNTP时间

### 查询: AT+SNTPTIME?

| 项目 | 内容 |
|------|------|
| 描述 | 查询SNTP时间 |
| 响应 | `+SNTPTIME:<week><month><day><HH>:<mm>:<ss><yyyy>` → OK |
| 注意 | SNTP默认没有开启，需联网后使用AT+SNTPTIMECFG启动。未启用时查询的是本地RTC时间。 |

**响应字段说明：**
- week: 星期 [Mon,Tue,Wed,Thu,Fri,Sat,Sun]
- month: 月份 [Jan,Feb,Mar,Apr,May,Jun,Jul,Aug,Sep,Oct,Nov,Dec]
- day: 日
- HH: 小时
- mm: 分钟
- ss: 秒
- yyyy: 年

**示例：**
```
AT+SNTPTIMECFG=1,8    // 开启SNTP，时区+8
OK
AT+SNTPTIME?           // 同步成功后查询时间
+SNTPTIME:WedMay0310:49:412023
OK
```

| 支持型号 | Ai-WB2系列 |

## 4.5.2 AT+SNTPTIMECFG — SNTP时区和服务器配置

### 查询: AT+SNTPTIMECFG?

| 项目 | 内容 |
|------|------|
| 描述 | 查询SNTP服务状态 |
| 响应 | `+SNTPTIMECFG:<enable>,<timezone>[,<SNTPserver1>,<SNTPserver2>,<SNTPserver3>]` → OK |

**响应字段说明：**
- enable: SNTP刷新服务是否启动（0=未运行，1=运行中）
- timezone: 时区（-12~+14）
- SNTPserver1/2/3: SNTP服务器域名

**示例：**
```
AT+SNTPTIMECFG?
+SNTPTIMECFG:1,8,"cn.ntp.org.cn","ntp.sjtu.edu.cn","us.pool.ntp.org"
OK
```

### 设置: AT+SNTPTIMECFG=<enable>,<timezone>[,<SNTPserver1>,<SNTPserver2>,<SNTPserver3>]

| 参数 | 说明 |
|------|------|
| enable | 0=关闭，1=启动 |
| timezone | 时区（-12~+14） |
| SNTPserver1/2/3 | SNTP服务器域名（缺省默认"cn.ntp.org.cn"、"ntp.sjtu.edu.cn"、"us.pool.ntp.org"） |

| 响应 | OK |
| 示例 | `AT+SNTPTIMECFG=1,8,cn.ntp.org.cn` → OK |
| 支持型号 | Ai-WB2系列 |

## 4.5.3 AT+SNTPINTV — SNTP刷新时间间隔

### 查询: AT+SNTPINTV?

| 项目 | 内容 |
|------|------|
| 描述 | 查询SNTP服务刷新间隔 |
| 响应 | `+SNTPINTV:<intervalsecond>` → OK |
| 示例 | `AT+SNTPINTV?` → `+SNTPINTV:3600` → OK |

### 设置: AT+SNTPINTV=<intervalsecond>

| 参数 | 说明 |
|------|------|
| intervalsecond | 刷新间隔，单位秒，取值15~4294967 |

| 响应 | OK |
| 示例 | `AT+SNTPINTV=15` → OK |
