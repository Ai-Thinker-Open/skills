# BW21-CBV-Kit 开发板引脚配置

> 本文件是 `board-pins` skill 的**单板参考文档**。内容由官方规格书自动解析生成，**使用前请人工核对**。

## 板卡概要

| 项目 | 值 |
|------|----|
| 开发板型号 | BW21-CBV-Kit |
| 分类 | WiFi |
| 规格书版本 | BW21-CBV-Kit Specification V1.0.0 |
| 数据来源 | [官方规格书](https://aithinker-static.oss-cn-shenzhen.aliyuncs.com/docs/Public%20Document%20Center/WiFi/rtl87xx/bw21/Specification/BW21-CBV-Kit_V1.0.0%20Specification-20241225.pdf) |

## 引脚定义表（11 脚）

| 脚序 | 名称 | 功能说明 |
|:---:|:---:|:---------|
| 1 | LOG_RX | GPIOF_3/ADC3/RFE_CTRL_2/UART1_IN/ArduinoPin_26 |
| 2 | LOG_TX | GPIOF_4/UART1_OUT/ArduinoPin_25 |
| 3 | IOF5 | GPIOF_5/SPI_1_MISO/SPI_3_MISO/ArduinoPin_0 |
| 4 | IOF6 | GPIOF_6/PWM0/SPI_1_SCL/SPI_3_SC/ArduinoPin_1 |
| 5 | IOF7 | GPIOF_7/PWM1/SPI_1_MOSI/SPI_3_MOSI//ArduinoPin_2 |
| 6 | IOF8 | GPIOF_8/PWM2/SPI_1_CS0/SPI_3_CS/ArduinoPin_3 |
| 7 | IOF11 | GPIOF_11/PWM5/I2S0_MCK/ArduinoPin_4 |
| 8 | IOF12 | GPIOF_12/PWM6/I2S0_SD_RX/UART1_IN/ArduinoPin_5 |
| 9 | IOF13 | GPIOF_13/PWM7/I2S0_CLK/UART1_OUT/ArduinoPin_6 |
| 10 | IOF14 | GPIOF_14/SGPIO_RX/PWM8/I2S0_SD_TX0/ArduinoPin_7 |
| 11 | IOF15 | GPIOF_15/SGPIO_TX/PWM9/I2S_WS/ArduinoPin_8 |

## 功能索引

| I2S_WS | IOF15 |
| PWM0 | IOF6 |
| PWM1 | IOF7 |
| PWM2 | IOF8 |
| PWM5 | IOF11 |
| PWM6 | IOF12 |
| PWM7 | IOF13 |
| PWM8 | IOF14 |
| PWM9 | IOF15 |

## 避坑提示

- 标 **NC / 默认不可用** 的引脚不能当普通 IO。
- 标 **与内部 Flash 共用** 的引脚勿用于外设，避免破坏固件。
- 引脚一针多功能，需**核对复用冲突**后再接线。
- 供电/电平、烧录流程以官方规格书为准。

## 数据来源与核对说明

> 本表由官方规格书自动解析生成（引脚页：3, 11）。**以官方规格书/原理图为准**；解析可能存在断行/遗漏，请人工核对后再接入项目。
