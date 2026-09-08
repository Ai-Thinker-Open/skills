# Ai-WB1-32S-Kit 开发板引脚配置

> 本文件是 `board-pins` skill 的**单板参考文档**。内容由官方规格书自动解析生成，**使用前请人工核对**。

## 板卡概要

| 项目 | 值 |
|------|----|
| 开发板型号 | Ai-WB1-32S-Kit |
| 分类 | WiFi |
| 规格书版本 | Ai-WB1-32S-Kit Specification V1.1.0 |
| 数据来源 | [官方规格书](https://aithinker-static.oss-cn-shenzhen.aliyuncs.com/docs/_media_old/ai-wb1-32s-kit_specification_v1.1.0.pdf) |

## 引脚定义表（30 脚）

| 脚序 | 名称 | 功能说明 |
|:---:|:---:|:---------|
| 1 | 3V3 | 3.3V power suppl |
| 2 | RST | as chip enable, high level enable |
| 3 | PA7 | PWM4/LSPI_MOSI/I2S_MCK/I2S_DI/Touch0/GPIO |
| 4 | PA1 | JTAG_CK/I2C_SCL/PWM3/I2S_LRCK/ADC0 |
| 5 | NC | Empty feet |
| 6 | NC | Empty feet |
| 7 | PA4 | JTAG_SWO/I2C_SCL/PWM4/I2S_BCK/ADC1 |
| 8 | PB0 | PWM0/LSPI_MISO/UART3_TX/PSRAM_CK/Touch3/GPIO |
| 9 | PB1 | PWM1/LSPI_CLK/UART3_RX/PSRAM_CS/Touch4/GPIO |
| 10 | PB8 | I2S_BCK/MMC_D0/PWM_BREAK/SDIO_D0/Touch11/GPIO |
| 11 | PB9 | I2S_LRCK/MMC_D1/HSPI_CS/SDIO_D1/Touch12/GPIO |
| 12 | PB5 | LSPI_MOSI/UART2_CTS/UART4_RX/PSARM_D3/Touch8/GPIO |
| 13 | PB4 | LSPI_CS/UART2_RTS/UART4_TX/PSRAM_D2/Touch7/GPIO |
| 14 | GND | Ground 15、16、 17、18 NC Empty feet |
| 19 | 5V | 5V power supply 20、21、 22、23、 |
| 24 | NC | Empty feet |
| 25 | PA0 | I2S_MCLK/LSPI_CS/PWM2/I2S_DO/BOOTMODE |
| 26 | NC | Empty feet |
| 27 | PB7 | UART1_RX/MMC_CMD/HSPI_INT/SDIO_CMD/Touch10/GPIO |
| 28 | PB6 | UART1_TX/MMC_CLK/HSPI_CK/SDIO_CK/Touch9/GPIO |
| 29 | NC | Empty feet |
| 30 | PB3 | PWM3/LSPI_MISO/UART2_RX/PSRAM_D1/Touch6/GPIO |
| 31 | PB2 | PWM2/LSPI_CK/UART2_TX/PSRAM_D0/Touch5/GPIO |
| 32 | NC | Empty feet |
| 33 | PB10 | I2S_DI/MMC_D2/HSPI_DI/SDIO_D2/GPIO |
| 34 | RX | UART0_RX/PWM1/UART1_CTS/I2C_SCL |
| 35 | TX | UART0_TX/PWM0/UART1_RTS/I2C_SCL |
| 36 | WAKE | WAKEUP Wake function |
| 37 | PB11 | I2S_DO/MMC_D3/HSPI_DO/SDIO_D3/GPIO |
| 38 | GND | Ground 6. Precautions Ai-WB1-32S-Kit is used for serial communication, the Type-C interface cannot be connected to the TX and RX interfaces of pin row at the same time; otherwise, the Type-C interface cannot send data. Front Back Figure 8 Interface diagram Both can’t be accessed at the same time |

## 功能索引

| I2C_SCL | PA1、RX |
| I2C_SDA | PA4、TX |
| I2S_BCK | PA4、PB8 |
| I2S_DI | PA7、PB10 |
| I2S_DO | PA0、PB11 |
| I2S_LRCK | PA1、PB9 |
| I2S_MCK | PA7 |
| I2S_MCLK | PA0 |
| PWM | PB8 |
| PWM0 | PB0、TX |
| PWM1 | PB1、RX |
| PWM2 | PA0、PB2 |
| PWM3 | PA1、PB3 |
| PWM4 | PA7、PA4 |
| SPI_CK | PB6、PB2 |
| SPI_CLK | PB1 |
| SPI_CS | PB9、PB4、PA0 |
| SPI_DI | PB10 |
| SPI_DO | PB11 |
| SPI_INT | PB7 |
| SPI_MISO | PB0、PB3 |
| SPI_MOSI | PA7、PB5 |

## 避坑提示

- 标 **NC / 默认不可用** 的引脚不能当普通 IO。
- 标 **与内部 Flash 共用** 的引脚勿用于外设，避免破坏固件。
- 引脚一针多功能，需**核对复用冲突**后再接线。
- 供电/电平、烧录流程以官方规格书为准。

## 数据来源与核对说明

> 本表由官方规格书自动解析生成（引脚页：12, 13）。**以官方规格书/原理图为准**；解析可能存在断行/遗漏，请人工核对后再接入项目。
