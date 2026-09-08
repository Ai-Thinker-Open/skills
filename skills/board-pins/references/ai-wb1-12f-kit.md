# Ai-WB1-12F-Kit 开发板引脚配置

> 本文件是 `board-pins` skill 的**单板参考文档**。内容由官方规格书自动解析生成，**使用前请人工核对**。

## 板卡概要

| 项目 | 值 |
|------|----|
| 开发板型号 | Ai-WB1-12F-Kit |
| 分类 | WiFi |
| 规格书版本 | Ai-WB1-12F-Kit Specification V1.1.0 |
| 数据来源 | [官方规格书](https://aithinker-static.oss-cn-shenzhen.aliyuncs.com/docs/_media_old/ai-wb1-12f-kit_specification_v1.1.0.pdf) |

## 引脚定义表（26 脚）

| 脚序 | 名称 | 功能说明 |
|:---:|:---:|:---------|
| 1 | ADC | Reference voltage of ADC0 |
| 2 | PA1 | JTAG_CK/I2C_SCL/PWM3/I2S_LRCK/ADC0 |
| 3 | NC | Dangling |
| 4 | WAKE | WAKEUP wake up capabilities |
| 5 | PA4 | JTAG_SWO/I2C_SCL/PWM4/I2S_BCK/ADC1/JTAG_SWO |
| 6 | PB0 | PWM0/LSPI_MISO/UART3_TX/PSRAM_CK/Touch3/GPIO |
| 7 | PB1 | PWM1/LSPI_CLK/UART3_RX/PSRAM_CS/Touch4/GPIO |
| 8 | PB4 | LSPI_CS/UART2_RTS/UART4_TX/PSRAM_D2/Touch7/GPIO |
| 9 | PB8 | I2S_BCK/MMC_D0/PWM_BREAK/SDIO_D0/Touch11/GPIO |
| 10 | GND | Ground |
| 11 | 3V3 | 3.3V power supply |
| 12 | RST | as chip enable, high level enable |
| 13 | PA7 | PWM4/LSPI_MOSI/I2S_MCK/I2S_DI/Touch0/GPIO |
| 14 | GND | Ground |
| 15 | 5V | 5V power supply |
| 16 | 3V3 | 3.3V power supply |
| 17 | GND | Ground |
| 18 | TX | UART0_TX/PWM0/UART1_RTS/I2C_SCL |
| 19 | RX | UART0_RX/PWM1/UART1_CTS/I2C_SCL |
| 20 | PB5 | LSPI_MOSI/UART2_CTS/UART4_RX/PSARM_D3/Touch8/GPIO |
| 21 | PB11 | I2S_DO/MMC_D3/HSPI_DO/SDIO_D3/GPIO |
| 22 | PB10 | I2S_DI/MMC_D2/HSPI_DI/SDIO_D2/GPIO |
| 23 | PB9 | I2S_LRCK/MMC_D1/HSPI_CS/SDIO_D1/Touch12/GPIO |
| 24 | GND | Ground |
| 25 | 3V3 | 3.3V power supply |
| 26 | PB7 | UART1_RX/MMC_CMD/HSPI_INT/SDIO_CMD/Touch10/GPIO |

## 功能索引

| I2C_SCL | PA1、RX |
| I2C_SDA | PA4、TX |
| I2S_BCK | PA4、PB8 |
| I2S_DI | PA7、PB10 |
| I2S_DO | PB11 |
| I2S_LRCK | PA1、PB9 |
| I2S_MCK | PA7 |
| PWM | PB8 |
| PWM0 | PB0、TX |
| PWM1 | PB1、RX |
| PWM3 | PA1 |
| PWM4 | PA4、PA7 |
| SPI_CLK | PB1 |
| SPI_CS | PB4、PB9 |
| SPI_DI | PB10 |
| SPI_DO | PB11 |
| SPI_INT | PB7 |
| SPI_MISO | PB0 |
| SPI_MOSI | PA7、PB5 |

## 避坑提示

- 标 **NC / 默认不可用** 的引脚不能当普通 IO。
- 标 **与内部 Flash 共用** 的引脚勿用于外设，避免破坏固件。
- 引脚一针多功能，需**核对复用冲突**后再接线。
- 供电/电平、烧录流程以官方规格书为准。

## 数据来源与核对说明

> 本表由官方规格书自动解析生成（引脚页：12）。**以官方规格书/原理图为准**；解析可能存在断行/遗漏，请人工核对后再接入项目。
