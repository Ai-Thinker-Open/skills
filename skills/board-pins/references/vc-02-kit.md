# VC-02-Kit 开发板引脚配置

> 本文件是 `board-pins` skill 的**单板参考文档**。内容由官方规格书自动解析生成，**使用前请人工核对**。

## 板卡概要

| 项目 | 值 |
|------|----|
| 开发板型号 | VC-02-Kit |
| 分类 | Voice |
| 规格书版本 | VC-02-Kit Specification |
| 数据来源 | [官方规格书](https://aithinker-static.oss-cn-shenzhen.aliyuncs.com/docs/Public%20Document%20Center/VoiceModule/vc/Specification/VC-02-Kit_V1.0.0%20Specification-20220317.pdf) |

## 引脚定义表（19 脚）

| 脚序 | 名称 | 功能说明 |
|:---:|:---:|:---------|
| 1 | VCC | 5V power input |
| 2 | NC | No connect |
| 3 | TCK | JTAG clock pin |
| 4 | TMS | JTAG data pin |
| 5 | GND | GND ground |
| 6 | DAC_L | Reserve the audio L channel output, which is not supported temporarily |
| 7 | DAC_R | Reserve the audio R channel output, which is not supported temporarily |
| 8 | 3V3OUT | 3.3V voltage output |
| 9 | GND | GND ground |
| 10 | VCC | 5V voltage input |
| 11 | GND | GND ground |
| 12 | TX1 | UART1 TXD |
| 13 | RX1 | UART1 RXD |
| 14 | IOB8 | UART0 output pin/Log information output |
| 15 | IOA27 | GPIO_A17 pin |
| 16 | SCL | 3.3V IIC clock pin / GPIO_B2 / TIM3_PWM (it cannot be used simultaneously with the 5V-level IIC communication port) |
| 17 | SDA | 3.3V IIC data pin / GPIO_B3 / TIM4_PWM (it cannot be used simultaneously with the 5V-level IIC communication port) |
| 18 | SCL_5V | 5V IIC clock pin (it cannot be used simultaneous with 3.3V level IIC communication port) |
| 19 | SDA_5V | 5V IIC data pin (it cannot be used simultaneous with 3.3V level IIC communication port) |

## 功能索引

| PWM | SCL、SDA |
| RXD | RX1 |
| TXD | TX1 |

## 避坑提示

- 标 **NC / 默认不可用** 的引脚不能当普通 IO。
- 标 **与内部 Flash 共用** 的引脚勿用于外设，避免破坏固件。
- 引脚一针多功能，需**核对复用冲突**后再接线。
- 供电/电平、烧录流程以官方规格书为准。

## 数据来源与核对说明

> 本表由官方规格书自动解析生成（引脚页：11）。**以官方规格书/原理图为准**；解析可能存在断行/遗漏，请人工核对后再接入项目。
