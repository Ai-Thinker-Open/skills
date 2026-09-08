# Rd-60-Kit 开发板引脚配置

> 本文件是 `board-pins` skill 的**单板参考文档**。内容由官方规格书自动解析生成，**使用前请人工核对**。

## 板卡概要

| 项目 | 值 |
|------|----|
| 开发板型号 | Rd-60-Kit |
| 分类 | Radar |
| 规格书版本 | Rd-60-Kit Specification V2.0.0 |
| 数据来源 | [官方规格书](https://aithinker-static.oss-cn-shenzhen.aliyuncs.com/docs/Public%20Document%20Center/Radar/rd-6x/Specification/Rd-60-Kit_V2.0.0%20Specification-20250208.pdf) |

## 引脚定义表（17 脚）

| 脚序 | 名称 | 功能说明 |
|:---:|:---:|:---------|
| 8 | PA0 | (IO),PA0,WIO0,SPI0-CS,UART1-TX,PWM0,MCO-CLK |
| 9 | V13 | (PI), Analog power input voltage 1.2V~2.5V, default 1.5V, NC |
| 10 | VDDIO | (PI), module IO power supply 1.7~3.6V, default input 3.3V |
| 11 | VCC | (PI), module power supply 1.7V~5.5V, default input 3.3V |
| 12 | GND | (G), Ground |
| 13 | GND | (G), Ground |
| 14 | PB1 | (IO/WUP),PB1,WIO17,UART0-RX,S-SWD-TCK,PWM1 |
| 15 | PB0 | (IO/WUP),PB0,WIO16,UART0-TX,S-SWD-TMS,PWM0 |
| 16 | PA7 | (IO/WUP),PA7,WIO7,UART1-CTS,UART2-RX,I2C1-SCL,PWM7,GPADC7 |
| 17 | PA6 | (IO/WUP),PA6,WIO6,UART1-RTS,UART2-TX,I2C1-SDA,PWM6,GPADC6 |
| 18 | PA4 | (IO),PA4,WIO4,SPI0-HOLD,I2C0-SDA,PWM4 |
| 19 | PA5 | (IO),PA5,WIO5,SPI0-WP,I2C-SCL,PWM5 |
| 20 | PA11 | (IO/WUP),PA11,WIO11,I2C1-SCL,S-SWD-TCK,PWM3,GPADC3 |
| 21 | PA10 | (IO/WUP),PA10,WIO10,I2C1-SDA,S-SWD-TMS,PWM2,GPADC2 |
| 22 | PA9 | (IO/WUP),PA9,WIO9,UART1-RX,I2C1-SDA,PWM1,GPADC1 |
| 23 | PA8 | (IO/WUP),PA8,WIO8,UART1-TX,I2C1-SCL,PWM0,GPADC0 |
| 24 | GND | (G), Ground |

## 功能索引

| PWM0 | PA0、PB0、PA8 |
| PWM1 | PB1、PA9 |
| PWM2 | PA10 |
| PWM3 | PA11 |
| PWM4 | PA4 |
| PWM5 | PA5 |
| PWM6 | PA6 |
| PWM7 | PA7 |

## 避坑提示

- 标 **NC / 默认不可用** 的引脚不能当普通 IO。
- 标 **与内部 Flash 共用** 的引脚勿用于外设，避免破坏固件。
- 引脚一针多功能，需**核对复用冲突**后再接线。
- 供电/电平、烧录流程以官方规格书为准。

## 数据来源与核对说明

> 本表由官方规格书自动解析生成（引脚页：16）。**以官方规格书/原理图为准**；解析可能存在断行/遗漏，请人工核对后再接入项目。
