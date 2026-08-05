---
name: coder-ra-01sc
description: Ai-Thinker Ra-01SC series LoRa module development guide (LLCC68 chip, covering Ra-01SC/Ra-01SC-P/Ra-01SCH/Ra-01SCH-P) - sub-GHz RF transceiver controlled via SPI, supporting LoRa modulation (SF5-SF11, 125/250/500kHz), (G)FSK 0.6-300kbps, CAD channel activity detection, RX duty cycle, covering SPI command protocol, initialization sequence, TX/RX programming, register-level control and driver porting.
---

# Ai-Thinker Ra-01SC Series Development Guide (LLCC68)

## Coding Standard

**All code development and review must follow the `ai-thinker-c-coding-standard` specification.**

Key requirements:
1. **Function Header Comments**: All functions (`.h` and `.c`) must have Doxygen-style function header comments, **Chinese comments are mandatory**
2. **Comment Format**:
   ```c
   /**
    * @brief 函数概述与作用
    *
    * @param[in]   param1     输入参数说明
    * @param[out]  *param2    输出参数说明
    * @return      返回值类型 返回值说明
    *              - 错误码1: 错误描述
    *              - 错误码2: 错误描述
    * @note        使用说明/前置条件
    */
   ```
3. **Naming**: Follow `axk` prefix convention for identifiers
4. **Format**: 4 spaces indentation, K&R brace style, 120 char line limit
5. **All code comments must be in Chinese**

## Programming Paradigm

> **Important**: Ra-01SC 系列模组内置 **LLCC68 sub-GHz 半双工射频收发芯片**(transceiver,芯片手册原文术语),**不含应用处理器、本身不运行应用代码**。它作为 **SPI 从设备**挂载在主机 MCU(如 STM32、BL602、ESP32 等)上,由主机通过 SPI 命令接口完成全部控制和数据收发。

**两种编程方式**:

1. **SPI 命令层编程(默认,推荐)**: 直接按 LLCC68 手册的 SPI 命令协议收发 opcode/参数。所有功能(初始化、发送、接收、CAD)都通过本技能中的命令封装函数完成。
   - 每次 SPI 事务前**必须等待 BUSY 引脚为低**才能发送新命令
   - 业务逻辑循环放在 FreeRTOS 任务中(`xTaskCreate`),延时用 `vTaskDelay`

2. **官方驱动移植**: 参考安信可 STM32 示例 Demo(基于 Semtech SX126x 驱动移植,API 为 `LLCC68SetXxx` / `LLCC68GetXxx` 系列)。驱动分三层:llcc68.c(高层 API)、radio.c(SPI 事务)、板级原语层——**移植只需重写板级原语**(SPI 收发/NSS/BUSY/复位/延时/DIO1 中断),详见示例 5。

---

## Product Overview

**Ra-01SC 系列**是安信可科技基于 **SEMTECH LLCC68 芯片**设计的 LoRa 系列模组,包含 **Ra-01SC / Ra-01SC-P / Ra-01SCH / Ra-01SCH-P** 四个型号,**四款芯片均为 LLCC68**(-P 变体为模组级大功率版本,芯片未变;官方产品文档页面以 Ra-01SCH 命名,仅作资料入口)。该系列用于超长距离扩频通信,借助 LoRa™ 专利调制技术,标准型号具有超过 -129dBm 的高灵敏度、+22dBm 发射功率,抗干扰性强,最大程度降低电流消耗。可广泛应用于自动抄表、家庭楼宇自动化、安防系统、远程灌溉系统等。

### 模组特性(芯片级参数四款一致,数值以高频段标准型号为准;各型号差异见下节系列型号表)

| 项目 | 参数(Ra-01SCH) | 其他型号差异 |
|------|------|------|
| 射频芯片 | SEMTECH LLCC68 | -P 变体芯片同为 LLCC68,模组另内置 PA(功率放大器)与 LNA(低噪声放大器)实现大功率 |
| 调制方式 | FSK、GFSK、LoRa® | - |
| 支持频段 | 803 MHz ~ 930 MHz | SC 系为 410 ~ 525 MHz |
| 工作电压 | 3.3 V | - |
| 最大输出功率 | +22 dBm | -P 变体可达 +29 dBm(SCH-P 可选 +31 dBm) |
| 最大工作电流 | 120 mA | SC 系 140 mA;-P 变体 700 mA 级 |
| 接收电流 | 最低 4.2 mA(接收状态下低功耗特性) | -P 变体 11 / 16 mA |
| 待机电流 | 0.6 mA | - |
| 灵敏度 | 低至 -129 dBm | -P 变体 -137 dBm@SF10 125kHz |
| 扩频因子 | SF5 / SF6 / SF7 / SF8 / SF9 / SF10 / SF11 | - |
| 通信接口 | SPI(半双工),带 CRC、高达 256 字节的数据包引擎 | - |
| 封装 | 小体积双列邮票孔贴片封装 | - |
| 天线 | 兼容邮票孔/圆孔和 IPEX 等多种接法 | - |

### 系列型号(均已核实官网产品页)

| 型号 | 射频芯片 | 支持频段 | 最大功率 | 说明 |
|------|---------|---------|---------|------|
| Ra-01SC | LLCC68 | 410 ~ 525 MHz | +22 dBm | 低频段标准型号 |
| Ra-01SC-P | LLCC68 | 410 ~ 525 MHz | +29 dBm | 低频段大功率变体(芯片同为 LLCC68,模组内置 PA/LNA) |
| Ra-01SCH | LLCC68 | 803 ~ 930 MHz | +22 dBm | 高频段标准型号 |
| Ra-01SCH-P | LLCC68 | 803 ~ 930 MHz | +29 dBm(可选 +31 dBm) | 高频段大功率变体(芯片同为 LLCC68,模组内置 PA/LNA) |

> **重要**:
> 1. **SC 与 SCH 频段不同**(410~525MHz vs 803~930MHz),开发前务必确认目标型号的频段范围,并配合对应的镜像校准频段(见寄存器文档)
> 2. **-P 变体(大功率版本)规格差异大**:官网原话"模组内置了功率放大器(PA)与低噪声放大器(LNA)",实现 +29dBm(需较大工作电流,SC-P 700mA / SCH-P 750mA~1A)、接收电流 11/16mA、灵敏度 -137dBm@SF10 125kHz;**芯片同为 LLCC68,命令层完全一致**;功率配置方式以官网设计指导为准(内部 PA 供电 3.3V→+29dBm / 5V→+31dBm)——本文档的 PA 配置与示例代码以标准型号(+22dBm)为准
> 3. 芯片命令层(SPI 命令/寄存器)四款完全通用,均为 LLCC68 命令集
> 4. 各变体均支持多种天线安装方式(半孔焊盘/通孔焊盘/IPEX 座子),具体差异以官网产品页为准:https://docs.ai-thinker.com/Ra-01SCH/
> 5. **注意区分**:官网 LoRa 目录下另有 **SX1278 芯片**的 Ra-01 / Ra-01S / Ra-01S-P 等产品(410~525MHz、+20dBm),与本系列**命令体系和驱动不通用**——本文档仅适用于本系列四款 LLCC68 模组

### LLCC68 芯片关键参数(DS_LLCC68 V1.0)

| 项目 | 参数 |
|------|------|
| 频率范围 | 150 ~ 960 MHz 连续覆盖 |
| 最大发射功率 | +22 dBm(868/915 MHz 下发射电流典型 118 mA) |
| 接收灵敏度 | LoRa 125kHz/SF9: -129 dBm;LoRa 125kHz/SF7: -124 dBm;2-FSK 4.8kbps: -118 dBm(均为 **Rx Boosted 增益**下;省电增益约低 4dB,见寄存器文档 Rx 增益) |
| LoRa 参数 | SF5~SF11,BW 125/250/500 kHz,CR 4/5~4/8 |
| GFSK 参数 | 0.6 ~ 300 kbps,频偏 0.6 ~ 200 kHz |
| 供电 | VBAT 1.8 ~ 3.7 V(绝对最大 3.9 V);VBAT≥VBAT_IO |
| 晶振 | 外部 32 MHz |
| 数据缓冲 | 256 字节 RAM(可自定义 TX/RX 基地址) |
| 封装 | QFN 4x4 mm,24 pin |
| 功耗 | SLEEP 600 nA(warm start);STDBY_RC 0.6 mA;RX 4.2~5.3 mA(DC-DC) |

---

## Hardware Interface

### LLCC68 引脚(QFN 4x4 24L)

| 引脚 | 名称 | 类型 | 说明 |
|------|------|------|------|
| 15 | NRESET | I | 复位信号,低有效,拉低典型 100 μs 触发完整复位 |
| 14 | BUSY | O | 忙指示,高=芯片忙不可收命令,低=可接受新命令(**必接**) |
| 19 | NSS | I | SPI 片选,低有效 |
| 18 | SCK | I | SPI 时钟(CPOL=0, CPHA=0,最高 16 MHz) |
| 17 | MOSI | I | SPI 主机输出/从机输入 |
| 16 | MISO | O | SPI 从机输出(未选中时高阻) |
| 13 | DIO1 | I/O | 通用 IRQ 输出线(推荐接主机外部中断) |
| 12 | DIO2 | I/O | IRQ 线 或 RF 开关控制(SetDio2AsRfSwitchCtrl) |
| 6 | DIO3 | I/O | IRQ 线 或 TCXO 供电控制(SetDio3AsTcxoCtrl) |
| 1/10 | VDD_IN/VBAT | I | 射频供电 |
| 11 | VBAT_IO | I | 数字 IO 供电(可独立 1.8V,需 ≤ VBAT) |
| 21/22 | RFI_P/RFI_N | I | 接收差分输入 |
| 23 | RFO | O | 发射输出 |

> **接线要点**: 至少 DIO1 必须接(用于 IRQ),BUSY 是必需的控制线(用于判断芯片是否就绪)。未接 DIO1 时只能轮询 `GetIrqStatus`(0x12)查询中断状态,不推荐。

### 主机 MCU 对接(以 BL602 的 HOSAL SPI 为例)

```c
#include "hal_spi.h"
#include "hal_gpio.h"

/* 引脚定义:按实际硬件连接调整 */
#define LLCC68_PIN_NSS    GPIO_PIN_10   /* SPI 片选 */
#define LLCC68_PIN_BUSY   GPIO_PIN_11   /* 忙检测 */
#define LLCC68_PIN_DIO1   GPIO_PIN_12   /* 中断 */
#define LLCC68_PIN_RST    GPIO_PIN_13   /* 复位 */

/* 使用 SPI0 外设 */
#define LLCC68_SPI_ID     SPI_ID_0
```

---

## SPI Command Protocol(核心必读)

LLCC68 通过 SPI 命令接口控制,命令结构为:**opcode(1 字节)+ 参数(n 字节)**,以 NSS 上升沿结束事务。读类命令返回时,主机需发送 NOP(0x00)作为空操作来读取数据。

### BUSY 处理规则

- 每次发送命令前,**必须等待 BUSY 引脚变为低电平**才可开始 SPI 事务
- 写命令会让内部状态机处理,BUSY 会拉高;读命令直接处理,BUSY 保持低
- Sleep 模式下 BUSY 通过 20 kΩ 上拉保持高,芯片苏醒后自动拉低

```c
/** 等待芯片就绪(BUSY 拉低) */
static void llcc68_wait_busy(void)
{
    /* BUSY 高电平期间芯片无法接受新命令,必须等待 */
    while (gpio_get_pin(GPIO_PORT_A, LLCC68_PIN_BUSY)) {
        /* 等待 BUSY 变低 */
    }
}
```

### 底层 SPI 读写封装

```c
/**
 * @brief 发送一条带参数的命令(写方向)
 *
 * @param[in]  opcode  命令码
 * @param[in]  *params 参数字节指针(可为 NULL)
 * @param[in]  len     参数个数
 * @note      发送前自动等待 BUSY 拉低
 */
static void llcc68_cmd_write(uint8_t opcode, const uint8_t *params, uint8_t len)
{
    uint8_t tx_buf[16];               /* 参数最多 9 字节(SetPacketParams GFSK) */
    uint8_t i;

    llcc68_wait_busy();
    tx_buf[0] = opcode;
    for (i = 0; i < len; i++) {
        tx_buf[i + 1] = params[i];
    }
    /* 单次 SPI 事务发送 opcode + 全部参数,以 NSS 上升沿结束 */
    spi_master_transfer(LLCC68_SPI_ID, tx_buf, NULL, len + 1);
}

/**
 * @brief 发送只读命令并接收返回数据(NOP 读取)
 *
 * @param[in]   opcode  命令码
 * @param[out]  *rx     返回数据缓冲
 * @param[in]   len     期望返回字节数(不含状态字节,≤6)
 * @note       数据在响应第 2 字节(状态字节)之后返回,须用 NOP 时钟驱动
 */
static void llcc68_cmd_read(uint8_t opcode, uint8_t *rx, uint8_t len)
{
    uint8_t tx_buf[8];
    uint8_t rx_buf[8];
    uint8_t i;

    llcc68_wait_busy();
    tx_buf[0] = opcode;
    for (i = 0; i < len + 1; i++) {   /* 首字节后每读 1 字节需发 1 个 NOP */
        tx_buf[i + 1] = 0x00;
    }
    spi_master_transfer(LLCC68_SPI_ID, tx_buf, rx_buf, len + 2);
    for (i = 0; i < len; i++) {
        rx[i] = rx_buf[i + 2];        /* 跳过状态字节 */
    }
}
```

### 寄存器/缓冲读写

```c
/** 写寄存器(地址自动递增,支持连续写) */
static void llcc68_write_reg(uint16_t addr, const uint8_t *data, uint8_t len)
{
    uint8_t buf[20];
    uint8_t i;

    buf[0] = (uint8_t)(addr >> 8);
    buf[1] = (uint8_t)(addr & 0xFF);
    for (i = 0; i < len; i++) {
        buf[i + 2] = data[i];
    }
    llcc68_cmd_write(0x0D, buf, len + 2);   /* WriteRegister: opcode + 地址 + 数据 */
}

/**
 * @brief 读寄存器(单次 SPI 事务:opcode + 地址 + NOP,数据在 NOP 期间返回)
 *
 * @note 手册 Table 13-25:地址后第 1 个 NOP 返回状态,第 2 个 NOP 起返回数据
 *       (数据从帧第 4 字节开始)
 */
static void llcc68_read_reg(uint16_t addr, uint8_t *data, uint8_t len)
{
    uint8_t buf[32];
    uint8_t i;

    llcc68_wait_busy();
    buf[0] = 0x1D;                    /* ReadRegister opcode */
    buf[1] = (uint8_t)(addr >> 8);
    buf[2] = (uint8_t)(addr & 0xFF);
    for (i = 0; i < len + 1; i++) {
        buf[i + 3] = 0x00;            /* NOP 时钟:首个 NOP 出状态,其后出数据 */
    }
    spi_master_transfer(LLCC68_SPI_ID, buf, buf, len + 4);
    for (i = 0; i < len; i++) {
        data[i] = buf[i + 4];
    }
}

/** 写 FIFO 数据缓冲(发送载荷,≤255 字节) */
static void llcc68_write_buffer(uint8_t offset, const uint8_t *data, uint8_t len)
{
    uint8_t buf[260];
    uint8_t i;

    buf[0] = offset;
    for (i = 0; i < len; i++) {
        buf[i + 1] = data[i];
    }
    llcc68_cmd_write(0x0E, buf, len + 1);   /* WriteBuffer: opcode + offset + data */
}

/**
 * @brief 读 FIFO 数据缓冲(单次 SPI 事务:opcode + offset + NOP)
 *
 * @note 手册 Table 13-27:offset 后第 1 个 NOP 返回状态,数据从帧第 3 字节开始
 */
static void llcc68_read_buffer(uint8_t offset, uint8_t *data, uint8_t len)
{
    uint8_t buf[260];
    uint8_t i;

    llcc68_wait_busy();
    buf[0] = 0x1E;                    /* ReadBuffer opcode */
    buf[1] = offset;
    for (i = 0; i < len + 1; i++) {
        buf[i + 2] = 0x00;            /* NOP 时钟:首个 NOP 出状态,其后出数据 */
    }
    spi_master_transfer(LLCC68_SPI_ID, buf, buf, len + 3);
    for (i = 0; i < len; i++) {
        data[i] = buf[i + 3];
    }
}
```

> 完整命令表(所有 opcode、参数布局)见 [references/llcc68-commands.md](./references/llcc68-commands.md)。

---

## LLCC68 核心概念

### 工作模式(6 种)

| 模式 | 说明 | 进入命令 |
|------|------|---------|
| SLEEP | 最低功耗,可选保留配置/RC64k RTC | SetSleep (0x84) |
| STDBY_RC | 待机,13MHz RC 时钟(默认上电状态) | SetStandby (0x80),param=0 |
| STDBY_XOSC | 待机,32MHz 晶振开启 | SetStandby (0x80),param=1 |
| FS | 频率合成,PLL 锁定到载频 | SetFs (0xC1) |
| TX | 发射 | SetTx (0x83) |
| RX | 接收 | SetRx (0x82) |

> 上电/复位后芯片自动完成校准进入 STDBY_RC(BUSY 拉低)。命令顺序约束:**必须先 SetPacketType 定义协议,再 SetModulationParams,最后 SetPacketParams**,顺序错误行为不可预期。

### 数据缓冲(256 字节 FIFO)

- 地址由 `SetBufferBaseAddress(TX基地址, RX基地址)`(0x8F)设置,默认 0x00
- TX: `WriteBuffer(offset, data)` 写入待发数据,`SetPacketParams` 的 PayloadLength 决定发送字节数
- RX: 接收后 `GetRxBufferStatus`(0x13)取回**载荷长度**和**起始指针**,再用 `ReadBuffer` 读出
- Sleep 模式会清空数据缓冲

### IRQ 中断(10 个源,可映射到 DIO1/2/3)

| Bit | IRQ | 说明 | 适用调制 |
|-----|-----|------|---------|
| 0 | TxDone | 数据包发送完成 | 全部 |
| 1 | RxDone | 数据包接收完成 | 全部 |
| 2 | PreambleDetected | 检测到前导码 | 全部 |
| 3 | SyncWordValid | 同步字有效 | FSK |
| 4 | HeaderValid | LoRa 头有效 | LoRa |
| 5 | HeaderErr | LoRa 头 CRC 错误 | LoRa |
| 6 | CrcErr | 收到错误 CRC | 全部 |
| 7 | CadDone | CAD 检测完成 | LoRa |
| 8 | CadDetected | CAD 检测到信号 | LoRa |
| 9 | Timeout | RX/TX 超时 | 全部 |

> **RxDone 不等于 CRC 正确**,收到包后必须用 `GetIrqStatus`(0x12)检查 CrcErr 位再决定是否采用数据。

---

## 开发流程(初始化顺序)

### TX 发送流程(手册 14.2)

1. `SetStandby(0)` 进入 STDBY_RC(若不在)
2. `SetPacketType(0x01)` 选择 LoRa 协议(0x00=GFSK)
3. `SetRfFrequency(rfFreq)` 设置载频(见频率计算)
4. `SetPaConfig(paDutyCycle, hpMax, 0x00, 0x01)` 配置功放
5. `SetTxParams(power, rampTime)` 设置输出功率与斜坡时间
6. `SetBufferBaseAddress(0x00, 0x00)` 设置 FIFO 基地址
7. `WriteBuffer(0x00, payload, len)` 写入待发数据
8. `SetModulationParams(SF, BW, CR, LDRO)` 调制参数
9. `SetPacketParams(preamble, headerType, payloadLen, crcType, invertIQ)` 包参数
10. `SetDioIrqParams(TxDone, TxDone, 0, 0)` 使能并映射 TxDone 中断
11. `SetTx(timeout=0x000000)` 进入发射(0=单次模式无超时)
12. 等待 TxDone IRQ → 芯片自动回 STDBY_RC → `ClearIrqStatus(TxDone)`

### RX 接收流程(手册 14.3)

1. `SetStandby(0)`
2. `SetPacketType(0x01)`
3. `SetRfFrequency(rfFreq)`
4. `SetBufferBaseAddress(0x00, 0x00)`
5. `SetModulationParams(SF, BW, CR, LDRO)` — 收发双方必须一致
6. `SetPacketParams(preamble, headerType, maxPayloadLen, crcType, invertIQ)` — 接收侧 PayloadLength 表示可接收最大长度
7. `SetDioIrqParams(RxDone|Timeout, RxDone|Timeout, 0, 0)`
8. `SetRx(timeout)` — 0x000000=单次模式;0xFFFFFF=连续模式;其他值=超时模式(≤262s)
9. 收到 RxDone 后:`GetIrqStatus` 检查 CrcErr → `GetRxBufferStatus` 取长度/指针 → `ReadBuffer` 读载荷 → `ClearIrqStatus(RxDone)`

> **注意(隐式头超时缺陷)**: 使用超时模式接收 LoRa 隐式头包后,建议补写寄存器 0x0902=0x00 停止 RTC 计数、0x0944=0x00 清除超时事件(详见 Known Limitations)。

---

## Programming Examples

### 示例 1:LoRa 发送

```c
#include "FreeRTOS.h"
#include "task.h"

/* 默认参数:915MHz(SCH 系频段;SC 系请改用 470MHz),SF7,BW125kHz,CR4/5,+22dBm */
#define LORA_FREQ_HZ       915000000UL
#define LORA_SF            7
#define LORA_BW            0x04   /* 0x04=125kHz, 0x05=250kHz, 0x06=500kHz */
#define LORA_CR            0x01   /* 0x01=4/5, 0x02=4/6, 0x03=4/7, 0x04=4/8 */
#define LORA_PREAMBLE_LEN  8      /* 前导码符号数 */
#define LORA_TX_POWER      22     /* dBm,-9 ~ +22 */

/** 计算频率寄存器值:RfFreq = FRF × 2^25 / 32MHz */
static uint32_t llcc68_freq_to_reg(uint32_t freq_hz)
{
    return (uint32_t)(((uint64_t)freq_hz << 25) / 32000000UL);
}

/**
 * @brief LoRa 初始化(发送与接收共用)
 *
 * @note 必须在 SetTx/SetRx 之前完成全部配置
 */
static void llcc68_lora_init(void)
{
    uint8_t standby = 0x00;                    /* STDBY_RC */
    uint8_t packet_type = 0x01;                /* LoRa */
    uint8_t pa_cfg[4] = {0x04, 0x07, 0x00, 0x01};  /* paDutyCycle=0x04, hpMax=0x07 → +22dBm */
    uint8_t tx_params[2] = {LORA_TX_POWER, 0x00};  /* 功率, ramp=10us */
    uint8_t base_addr[2] = {0x00, 0x00};       /* TX/RX 基地址 */
    uint8_t mod_params[4] = {LORA_SF, LORA_BW, LORA_CR, 0x00}; /* SF,BW,CR,LDRO */
    uint8_t pkt_params[6] = {0x00, LORA_PREAMBLE_LEN, 0x00, 32, 0x01, 0x00};
    /* pktParams: preamble[15:8],[7:0], headerType(0=显式), payloadLen, crc(1=开), invertIQ(0=标准) */
    uint32_t freq = llcc68_freq_to_reg(LORA_FREQ_HZ);
    uint8_t freq_buf[4];

    freq_buf[0] = (uint8_t)(freq >> 24);
    freq_buf[1] = (uint8_t)(freq >> 16);
    freq_buf[2] = (uint8_t)(freq >> 8);
    freq_buf[3] = (uint8_t)(freq & 0xFF);

    llcc68_cmd_write(0x80, &standby, 1);                 /* SetStandby(STDBY_RC) */
    llcc68_cmd_write(0x8A, &packet_type, 1);             /* SetPacketType(LoRa) */
    llcc68_cmd_write(0x86, freq_buf, 4);                 /* SetRfFrequency */
    llcc68_cmd_write(0x95, pa_cfg, 4);                   /* SetPaConfig(+22dBm) */
    llcc68_cmd_write(0x8E, tx_params, 2);                /* SetTxParams(22dBm, 10us) */
    llcc68_cmd_write(0x8F, base_addr, 2);                /* SetBufferBaseAddress */
    llcc68_cmd_write(0x8B, mod_params, 4);               /* SetModulationParams */
    llcc68_cmd_write(0x8C, pkt_params, 6);               /* SetPacketParams */
}

/**
 * @brief 发送一帧 LoRa 数据(阻塞式,等待 TxDone)
 *
 * @param[in]  *payload  待发送数据
 * @param[in]  len       数据长度(≤255 字节)
 * @return     0=成功, -1=失败
 */
static int8_t llcc68_lora_send(const uint8_t *payload, uint8_t len)
{
    uint8_t irq_mask[8] = {0x00, 0x01, 0x00, 0x01, 0x00, 0x00, 0x00, 0x00};
    uint8_t tx_timeout[3] = {0x00, 0x00, 0x00};          /* 无超时,单次模式 */
    uint8_t irq_status[2];

    /* 更新包长度(显式头模式) */
    llcc68_cmd_write(0x8C, (uint8_t[]){0x00, LORA_PREAMBLE_LEN, 0x00, len, 0x01, 0x00}, 6);

    /* 写载荷到 FIFO */
    llcc68_write_buffer(0x00, payload, len);

    /* 使能并映射 TxDone(bit0)→ DIO1。注意参数大端:数组首元素为高字节,
       {0x00,0x01} = 0x0001 = bit0 */
    llcc68_cmd_write(0x08, irq_mask, 8);                 /* SetDioIrqParams */

    /* 进入发射 */
    llcc68_cmd_write(0x83, tx_timeout, 3);               /* SetTx(timeout=0) */

    /* 等待 DIO1 触发 TxDone 中断 */
    while (!gpio_get_pin(GPIO_PORT_A, LLCC68_PIN_DIO1)) {
        vTaskDelay(pdMS_TO_TICKS(1));
    }

    /* 读 IRQ 状态并清除(TxDone=bit0,位于低字节 bit0) */
    llcc68_cmd_read(0x12, irq_status, 2);                /* GetIrqStatus */
    llcc68_cmd_write(0x02, (uint8_t[]){0x00, 0x01}, 2);  /* ClearIrqStatus(TxDone) */
    return 0;
}
```

### 示例 2:LoRa 接收(中断 + FreeRTOS 任务)

```c
#include "FreeRTOS.h"
#include "task.h"

static volatile uint8_t g_rx_done = 0;   /* 接收完成标志 */
static uint8_t g_rx_buf[255];
static uint8_t g_rx_len = 0;

/** DIO1 外部中断回调:仅置标志,处理放在任务中 */
static void llcc68_dio1_irq_handler(void)
{
    g_rx_done = 1;
}

/**
 * @brief LoRa 接收初始化
 *
 * @note 接收侧 SetPacketParams 的 PayloadLength 是最大可接收长度
 */
static void llcc68_lora_rx_init(void)
{
    uint8_t standby = 0x00;
    uint8_t packet_type = 0x01;
    uint32_t freq = llcc68_freq_to_reg(LORA_FREQ_HZ);
    uint8_t freq_buf[4];
    uint8_t base_addr[2] = {0x00, 0x00};
    uint8_t mod_params[4] = {LORA_SF, LORA_BW, LORA_CR, 0x00};
    uint8_t pkt_params[6] = {0x00, LORA_PREAMBLE_LEN, 0x00, 255, 0x01, 0x00};
    /* IRQ: RxDone(bit1) + Timeout(bit9) 映射到 DIO1。
       大端:高字节[0]=bit15..8,低字节[1]=bit7..0 → 0x0202 */
    uint8_t irq_mask[8] = {0x02, 0x02, 0x02, 0x02, 0x00, 0x00, 0x00, 0x00};
    uint8_t rx_timeout[3] = {0xFF, 0xFF, 0xFF};          /* 连续接收模式 */

    freq_buf[0] = (uint8_t)(freq >> 24);
    freq_buf[1] = (uint8_t)(freq >> 16);
    freq_buf[2] = (uint8_t)(freq >> 8);
    freq_buf[3] = (uint8_t)(freq & 0xFF);

    llcc68_cmd_write(0x80, &standby, 1);
    llcc68_cmd_write(0x8A, &packet_type, 1);
    llcc68_cmd_write(0x86, freq_buf, 4);
    llcc68_cmd_write(0x8F, base_addr, 2);
    llcc68_cmd_write(0x8B, mod_params, 4);
    llcc68_cmd_write(0x8C, pkt_params, 6);
    llcc68_cmd_write(0x08, irq_mask, 8);                 /* SetDioIrqParams */
    llcc68_cmd_write(0x82, rx_timeout, 3);               /* SetRx(continuous) */
}

/** 接收处理任务 */
static void llcc68_rx_task(void *param)
{
    uint8_t rx_status[2];
    uint8_t irq_status[2];
    uint8_t clear[2];

    (void)param;
    llcc68_lora_rx_init();

    while (1) {
        if (g_rx_done) {
            g_rx_done = 0;

            llcc68_cmd_read(0x12, irq_status, 2);        /* GetIrqStatus */
            /* irq_status[0]=IRQ[15:8], irq_status[1]=IRQ[7:0] */
            if ((irq_status[0] & 0x02) == 0x02) {        /* Timeout = bit9 */
                /* 隐式头超时缺陷 workaround:停止 RTC、清事件 */
                llcc68_cmd_write(0x0D, (uint8_t[]){0x09, 0x02, 0x00}, 3);
                llcc68_cmd_write(0x0D, (uint8_t[]){0x09, 0x44, 0x00}, 3);
            } else {
                /* RxDone(bit1):检查 CRC(bit6),无错才采用数据 */
                if ((irq_status[1] & 0x40) == 0x00) {    /* 无 CrcErr */
                    llcc68_cmd_read(0x13, rx_status, 2); /* GetRxBufferStatus */
                    g_rx_len = rx_status[0];             /* PayloadLengthRx */
                    llcc68_read_buffer(rx_status[1], g_rx_buf, g_rx_len);
                    printf("RX %d bytes: %s\r\n", g_rx_len, g_rx_buf);
                } else {
                    printf("RX CRC error\r\n");
                }
            }
            /* 清除 RxDone + Timeout 后继续接收 */
            clear[0] = 0x02;
            clear[1] = 0x02;
            llcc68_cmd_write(0x02, clear, 2);            /* ClearIrqStatus */
            llcc68_cmd_write(0x82, (uint8_t[]){0xFF, 0xFF, 0xFF}, 3);  /* 重新 SetRx */
        }
        vTaskDelay(pdMS_TO_TICKS(5));
    }
}
```

### 示例 3:CAD 信道活动检测(LoRa 先听后发)

```c
/**
 * @brief 启动一次 CAD 检测(检测信道是否有 LoRa 前导码)
 *
 * @param[in]  symbols  检测符号数(0=1, 1=2, 2=4, 3=8, 4=16)
 * @note      检测结果通过 CadDone/CadDetected IRQ 通知
 */
static void llcc68_lora_cad(uint8_t symbols)
{
    uint8_t cad_params[7] = {symbols, 0x16, 0x0B, 0x00, 0x00, 0x00, 0x00};
    /* cadSymbolNum, cadDetPeak, cadDetMin, cadExitMode, cadTimeout[23:0]
       (cadDetPeak/cadDetMin 常用 0x16/0x0B,微调参考应用笔记 AN1200.48;
       cadExitMode=0x00 表示 CAD_ONLY,cadTimeout 仅 CAD_RX 模式生效) */
    uint8_t irq_mask[8] = {0x80, 0x01, 0x80, 0x01, 0x00, 0x00, 0x00, 0x00};
    /* CadDone(bit7) + CadDetected(bit8) 映射到 DIO1 */

    llcc68_cmd_write(0x88, cad_params, 7);               /* SetCadParams(7 字节) */
    llcc68_cmd_write(0x08, irq_mask, 8);                 /* SetDioIrqParams */
    llcc68_cmd_write(0xC5, NULL, 0);                     /* SetCAD */
    /* 收到 CadDone IRQ 后读 GetIrqStatus:bit8=CadDetected 表示信道忙 */
}
```

### 示例 4:GFSK 模式(短距离高速传输)

```c
/**
 * @brief GFSK 初始化(50kbps,频偏 25kHz,带宽 117.3kHz)
 *
 * @note GFSK 参数:br = 32×Fxtal/bitrate;Fdev = FreqDev×2^25/Fxtal
 */
static void llcc68_gfsk_init(void)
{
    uint8_t standby = 0x00;
    uint8_t packet_type = 0x00;                          /* GFSK */
    uint32_t freq = llcc68_freq_to_reg(915000000UL);
    uint8_t freq_buf[4];
    uint8_t mod_params[8];
    uint8_t pkt_params[9];
    uint8_t syncword[8] = {0x12, 0x34, 0x56, 0x78, 0x00, 0x00, 0x00, 0x00};

    /* 比特率 50kbps:br = 32×32e6/50000 = 20480 = 0x005000 */
    /* 频偏 25kHz:Fdev = 25000×2^25/32e6 = 26214 = 0x006666 */
    mod_params[0] = 0x00; mod_params[1] = 0x50; mod_params[2] = 0x00;  /* br[23:0] */
    mod_params[3] = 0x08;                               /* PulseShape: Gaussian BT 0.3 */
    mod_params[4] = 0x0B;                               /* BW: 117.3kHz (需 ≥ BR+2×Fdev) */
    mod_params[5] = 0x00; mod_params[6] = 0x66; mod_params[7] = 0x66;  /* Fdev[23:0] */

    /* preamble 16bit, 前导检测 16bit, syncword 8bit(1字节), 无地址过滤,
       变长包, 载荷 255, CRC 2字节, 白化关 */
    pkt_params[0] = 0x00; pkt_params[1] = 0x10;          /* PreambleLength=16 */
    pkt_params[2] = 0x05;                               /* PreambleDetectorLength=16bit */
    pkt_params[3] = 0x08;                               /* SyncWordLength=8bit */
    pkt_params[4] = 0x00;                               /* AddrComp: 关 */
    pkt_params[5] = 0x01;                               /* 变长包 */
    pkt_params[6] = 255;                                /* PayloadLength */
    pkt_params[7] = 0x02;                               /* CRC_2_BYTE */
    pkt_params[8] = 0x00;                               /* Whitening 关 */

    freq_buf[0] = (uint8_t)(freq >> 24);
    freq_buf[1] = (uint8_t)(freq >> 16);
    freq_buf[2] = (uint8_t)(freq >> 8);
    freq_buf[3] = (uint8_t)(freq & 0xFF);

    llcc68_cmd_write(0x80, &standby, 1);
    llcc68_cmd_write(0x8A, &packet_type, 1);
    llcc68_cmd_write(0x86, freq_buf, 4);
    llcc68_cmd_write(0x8B, mod_params, 8);
    llcc68_cmd_write(0x8C, pkt_params, 9);
    /* 写 SyncWord 到寄存器 0x06C0(最多 8 字节):地址 2 字节 + 数据 8 字节 */
    llcc68_cmd_write(0x0D, (uint8_t[]){0x06, 0xC0, syncword[0], syncword[1],
                       syncword[2], syncword[3], syncword[4], syncword[5],
                       syncword[6], syncword[7]}, 10);
    /* 其余 TX 流程与 LoRa 相同:SetPaConfig → SetTxParams → WriteBuffer → SetTx */
}
```

### 示例 5:官方驱动移植(安信可 STM32 Demo)

安信可提供 STM32F103C8T6 示例 Demo(官网下载:`LLCC68_Ra-01SC_Ra-01SCH_Driver_V0.0.4.zip`,下载链接见资源表),为 **Semtech SX126x 驱动框架移植版**。

> **为什么是 SX126x 驱动?** LLCC68 与 SX1261/SX1262 同属 Semtech SX126x 家族,**SPI 命令集(opcode)与寄存器完全兼容**,因此安信可基于 Semtech SX126x 驱动框架(保留 Semtech 2013-2017 版权头)改写,API 全部重命名为 `LLCC68SetXxx` / `LLCC68GetXxx`;驱动内部仍保留 SX1261/SX1262 器件 ID 常量(llcc68.h),部分 workaround 注释直接引用 SX1261-2 手册(如天线失配钳制,与 LLCC68 手册 15.2 章内容一致)。**该驱动就是为 LLCC68 芯片编写的,直接适用于本系列模组。**

驱动分三层:

| 层 | 文件 | 内容 |
|----|------|------|
| 高层 API | `peripherals/radio/llcc68/llcc68.c` + `llcc68.h` | `LLCC68SetXxx` / `LLCC68GetXxx` 系列,业务调用入口 |
| SPI 事务层 | `peripherals/radio/llcc68/radio.c` | `LLCC68WriteRegisters`/`LLCC68ReadRegisters`/`LLCC68WriteBuffer`/`LLCC68ReadBuffer` 及 RadioXxx 封装(**读事务为单次 NSS 事务,与本文档示例一致**) |
| 板级原语 | `HAL/LLCC68STM32F103-board.c` + `peripherals/radio/llcc68-board.h` | `LLCC68SpiInOut`(字节级 SPI)、`LLCC68SetNss`、`LLCC68WaitOnBusy`、`LLCC68ResetInit`、`LLCC68DelayMs`、`LLCC68IoIrqInit`(DIO1 外部中断) |

**移植到新平台**:`llcc68.c` + `radio.c` **无需改动**,只需按 `llcc68-board.h` 的声明重写板级原语(SPI 收发、NSS/BUSY/复位 GPIO、延时、DIO1 中断)。
示例主程序:`USER/main.c`;使用说明:`doc/LLCC68驱动demo使用说明.pdf`。

驱动核心 API(与本章示例的 SPI 命令一一对应):

| 官方驱动 API | 对应 SPI 命令 | 说明 |
|--------------|--------------|------|
| `LLCC68Init` | - | 硬件初始化(复位+等待就绪) |
| `LLCC68SetStandby` | SetStandby (0x80) | 进入待机 |
| `LLCC68SetPacketType` | SetPacketType (0x8A) | 选择 LoRa/GFSK |
| `LLCC68SetRfFrequency` | SetRfFrequency (0x86) | 设置频率 |
| `LLCC68SetPaConfig` | SetPaConfig (0x95) | 功放配置 |
| `LLCC68SetTxParams` | SetTxParams (0x8E) | 功率/斜坡 |
| `LLCC68SetBufferBaseAddress` | SetBufferBaseAddress (0x8F) | FIFO 基地址 |
| `LLCC68WriteBuffer` / `LLCC68ReadBuffer` | WriteBuffer/ReadBuffer (0x0E/0x1E) | 读写载荷 |
| `LLCC68SetModulationParams` | SetModulationParams (0x8B) | 调制参数 |
| `LLCC68SetPacketParams` | SetPacketParams (0x8C) | 包参数 |
| `LLCC68SetDioIrqParams` | SetDioIrqParams (0x08) | IRQ 映射 |
| `LLCC68SetTx` / `LLCC68SetRx` | SetTx/SetRx (0x83/0x82) | 收发模式 |
| `LLCC68GetIrqStatus` / `LLCC68ClearIrqStatus` | GetIrqStatus/ClearIrqStatus (0x12/0x02) | IRQ 查询/清除 |
| `LLCC68SetSyncWord` | 寄存器 0x0740/0x0741 | LoRa 同步字(0x1424 私有网/0x3444 公共网) |
| `LLCC68GetPayload` / `LLCC68SetPayload` | ReadBuffer/WriteBuffer (0x1E/0x0E) | 读取/写入载荷数据 |
| `LLCC68SetRxBoosted` | 寄存器 0x08AC=0x96 | Rx Boosted 增益 |
| `LLCC68GetRssiInst` | GetRssiInst (0x15) | 瞬时 RSSI |
| `LLCC68SetCad` | SetCad (0xC5) | CAD 检测 |
| `LLCC68GetRandom` | 寄存器 0x0819~0x081C | 随机数 |

---

## 频率计算与空中时间

### 频率寄存器值(RfFreq)

```c
/* 频率寄存器 = 目标频率 × 2^25 / 晶振频率(32MHz) */
rf_freq = (uint32_t)(((uint64_t)freq_hz << 25) / 32000000UL);
```

常用频点参考值(32MHz 晶振,已用整数运算验证):

| 目标频率 | RfFreq 值 |
|---------|-----------|
| 470 MHz | 0x1D600000 |
| 868 MHz | 0x36400000 |
| 915 MHz | 0x39300000 |
| 923 MHz | 0x39B00000 |

> 速记:2^25 / 32MHz = 1.048576,即寄存器值 ≈ 频率(MHz)× 2^20。

### LoRa 空中时间(Time-on-Air)

```
T_sym     = 2^SF / BW                       符号周期(秒)
T_preamble = (N_preamble + 4.25) × T_sym   前导码时长
N_payload = 8 + max(ceil((8×PL - 4×SF + 28 + 16×CRC - 20×IH) / (4×(SF - 2×LDRO))), 0) × (CR+4)
T_packet  = T_preamble + N_payload × T_sym
```

其中:PL=载荷字节数,SF=扩频因子,BW=带宽(Hz),CRC=1(开)/0(关),IH=0(显式头)/1(隐式头),LDRO=0/1,CR=1~4(对应 4/5~4/8);ceil 内结果小于 0 时取 0(短载荷场景)。

> 官网提供 LoRa 速率计算工具:https://docs.ai-thinker.com/Ra-01SCH/ 开发指南 → LoRa 速率计算

---

## Known Limitations(芯片已知缺陷与规避,手册第 15 章)

| # | 缺陷 | 规避方法 |
|---|------|---------|
| 1 | **500kHz LoRa 带宽调制质量下降**:接收灵敏度可能降低 | 每次发射前设置寄存器 **0x0889 bit2**:BW=500kHz 时写 0;其他 BW 和所有 GFSK 配置写 1(默认值即 1) |
| 2 | **天线失配时 PA 过度钳制**,实测输出功率低 5~6 dB | 芯片初始化时(冷启动后)将寄存器 **0x08D8**(TxClampConfig)的 bits[4:1] 设为 1111(即写 0xDE) |
| 3 | **隐式头模式超时缺陷**:带超时接收隐式头包后,RTC 超时计时器未停,可能引发意外超时 | 任何带超时的 RX 之后执行:写 **0x0902=0x00**(停 RTC 计数)、写 **0x0944=0x00**(清超时事件) |
| 4 | **反向 IQ 长包丢包**:反向 IQ 极性下长包偶发丢包 | 寄存器 **0x0736 bit2**:反向 IQ 时写 0,标准 IQ 时写 1(默认 0x0D,bit2=1 标准) |

---

## 常见问题排查

**Q: 芯片无响应/命令无返回**
- 检查 NRESET 是否完成复位(拉低 ≥100μs 后释放),复位后必须等 BUSY 拉低
- 检查 SPI 模式:CPOL=0、CPHA=0,SCK 不超过 16MHz
- 检查供电:VBAT 1.8~3.7V,VBAT≥VBAT_IO

**Q: 发送无信号/功率低**
- 检查 SetPaConfig:+22dBm 需 paDutyCycle=0x04、hpMax=0x07;+20dBm→0x03/0x05;+17dBm→0x02/0x03;+14dBm→0x02/0x02(配套匹配网络)
- 检查 SetTxParams 功率值(-9~+22dBm)
- 天线未接或失配会触发 PA 钳制(见 Known Limitations #2)

**Q: 收不到数据**
- 收发双方 SF/BW/CR/同步字/频率必须完全一致
- 接收侧 PacketParams 的 PayloadLength 需 ≥ 发送长度(显式头模式)
- 检查 RxDone 后是否读取了 CrcErr 位(CRC 错误也会触发 RxDone)

**Q: 灵敏度差(实测低于手册)**
- 检查 Rx 增益:寄存器 0x08AC 默认 0x94(省电增益),写 0x96 切换 Rx Boosted 增益可提升灵敏度
- 检查天线匹配与阻抗

**Q: 掉电/复位后配置丢失**
- 默认冷启动(SetSleep 不保留配置)会丢失全部配置;需要保留时 SetSleep 参数 bit2=1(warm start,保留当前协议配置)
- 注意 warm start 仅保留激活中的 modem 配置

---

## Common Resource Links

| 资源 | 链接 |
|------|------|
| 产品页(规格书/开发指南/FAQ/示例) | https://docs.ai-thinker.com/Ra-01SCH/ |
| LLCC68 芯片手册(英文) | https://aithinker-static.oss-cn-shenzhen.aliyuncs.com/docs/chip_datasheet/DS_LLCC68_V1.0.pdf |
| STM32F103C8T6 示例 Demo(已核实可下载) | https://aithinker-static.oss-cn-shenzhen.aliyuncs.com/docs/media/LoRa_LoRaWAN/Firmware/LoRa_Driver_Demo/LLCC68_Ra-01SC_Ra-01SCH_Driver_V0.0.4.zip |
| 原理图/PCB 封装 | https://aithinker-static.oss-cn-shenzhen.aliyuncs.com/docs/packaging/SCHEMATIC_PCB_Ra-01S_SC-P.zip |
| SX126x/LLCC68 认证操作说明 | https://aithinker-static.oss-cn-shenzhen.aliyuncs.com/docs/media/LoRa_LoRaWAN/CertificationTestManual/CertificationTestOperationalGuideline_FOR_SX126x_LLCC68.pdf |
| LoRa 速率计算 | 产品页开发指南 → LoRa 速率计算 |
| LoRa 常见问题 | 产品页 FAQ → LoRa常见问题 |
| Semtech 官方 LLCC68 资料 | https://www.semtech.com/products/wireless-rf/lora-connect/llcc68 |

---

## API Reference

详细命令与寄存器文档独立存放在 `references/` 目录:

| 文档 | 内容 |
|------|------|
| [命令参考](./references/llcc68-commands.md) | 全部 SPI 命令:opcode、参数布局、返回值、注意事项(模式命令/寄存器访问/IRQ 控制/RF 调制包命令/状态命令) |
| [寄存器参考](./references/llcc68-registers.md) | 关键寄存器地址表、PA 最优配置、校准频段、Rx 增益、已知缺陷 workaround 寄存器 |
