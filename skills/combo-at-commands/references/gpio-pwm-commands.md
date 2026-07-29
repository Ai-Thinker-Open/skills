# 控制指令 — GPIO与PWM

## 3.1 AT+SYSIOMAP — IO映射表

### 查询: AT+SYSIOMAP?

| 项目 | 内容 |
|------|------|
| 描述 | 查询IO管脚映射关系表 |
| 响应 | `+SYSIOMAP:PinNumber:<PinNumber>,PinMap:<pin1>,<pin2>,...,<pinN>` |
| 说明 | PinNumber表示当前映射表一共有几组数据 |
| 示例 | `AT+SYSIOMAP?` → `+SYSIOMAP:PinNumber:6,PinMap:NC,5,20,NC,15,NC` → OK |

### 设置: AT+SYSIOMAP=<PinNumber>,<pin1>,<pin2>,...,<pinN>

| 参数 | 说明 |
|------|------|
| PinNumber | 要设置的IO总数 |
| pinxx | 模组IO引脚（从模组左上角逆时针排序，引脚序号从1开始）对应的芯片引脚编号（1~254）。如果模组没有对应芯片引脚则设置为NC |

| 示例 | `AT+SYSIOMAP=4,3,5,NC,1` → OK |
|------|------|
| 含义 | 共设置4个IO映射：模组1号引脚→芯片3号引脚；模组2号引脚→芯片5号引脚；模组3号引脚→NC（不可用）；模组4号引脚→芯片1号引脚 |

> 各型号的IOMap映射表参考 io-map-table.md

## 3.2 AT+SYSGPIOWRITE — GPIO输出电平

### 设置: AT+SYSGPIOWRITE=<pin>,<level>

| 参数 | 说明 |
|------|------|
| pin | 模组IO引脚号（从模组左上角逆时针排序，引脚序号从1开始） |
| level | 0=低电平（默认下拉），1=高电平（默认上拉） |

| 响应 | OK |

## 3.3 AT+SYSGPIOREAD — GPIO读取电平

### 读取: AT+SYSGPIOREAD=<pin>

| 参数 | 说明 |
|------|------|
| pin | 模组IO引脚号（从模组左上角逆时针排序，引脚序号从1开始） |

| 响应 | `+SYSGPIOREAD:<pin>,<level>` → OK |
|------|------|
| level | 0=低电平，1=高电平 |

### 查询帮助: AT+SYSGPIOREAD=?

| 响应 | GetGPIOlevel |

## 3.4 AT+PWMCFG — PWM配置（寄存器单位）

### 设置: AT+PWMCFG=<pin>,<cycle>,<duty>

| 参数 | 说明 |
|------|------|
| pin | 模块上的引脚（从模组左上角开始逆时针排序，从1开始） |
| cycle | PWM周期（寄存器单位） |
| duty | 占空比时间（寄存器单位） |

| 响应 | OK |
|------|------|
| 注意 | Ai-WB2系列模组一共有5路PWM，同时开启时必须注意芯片引脚的IO序号对5取余不能重复，否则只会有一个生效。例如设置了IO1/2/6实际只有IO2/6生效，IO1被IO6覆盖了。 |
| 备注 | 该指令设置的单位是芯片的周期寄存器，相同参数在不同模组上的效果可能不同。如果精度可以满足要求，推荐使用AT+PWMCFGS设置。 |

## 3.5 AT+PWMCFGS — PWM配置（us/百分比单位，推荐）

### 设置: AT+PWMCFGS=<pin>,<cycle>,<duty>

| 参数 | 说明 |
|------|------|
| pin | 模块上的引脚（从模组左上角开始逆时针排序，从1开始） |
| cycle | PWM周期，单位us |
| duty | 整数0~100，表示占空比的百分比 |

| 响应 | OK |
|------|------|
| 注意 | 同AT+PWMCFG注意事项 |
| 优势 | 相同参数在不同模组上的效果基本保持一致（不同芯片可能存在几us差异） |

## 3.6 AT+PWMSTOP — 关闭PWM

### 设置: AT+PWMSTOP=<pin>

| 参数 | 说明 |
|------|------|
| pin | 模块上的引脚（从模组左上角开始逆时针排序，从1开始） |

| 响应 | OK |

## 3.7 AT+PWMDUTYSET — 更新PWM占空比（寄存器单位）

### 设置: AT+PWMDUTYSET=<pin>,<duty>

| 参数 | 说明 |
|------|------|
| pin | 模块上的引脚（从模组左上角开始逆时针排序，从1开始） |
| duty | 占空比时间，单位寄存器单位 |

| 响应 | OK |

## 3.8 AT+PWMDUTYSETS — 更新PWM占空比（百分比，推荐）

### 设置: AT+PWMDUTYSETS=<pin>,<duty>

| 参数 | 说明 |
|------|------|
| pin | 模块上的引脚（从模组左上角开始逆时针排序，从1开始） |
| duty | 整数0~100，表示占空比的百分比 |

| 响应 | OK |
