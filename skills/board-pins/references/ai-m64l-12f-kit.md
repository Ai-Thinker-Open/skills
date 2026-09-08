# Ai-M64L-12F-Kit 开发板引脚配置

> 本文件是 `board-pins` skill 的**单板参考文档**。内容由官方规格书自动解析生成，**使用前请人工核对**。

## 板卡概要

| 项目 | 值 |
|------|----|
| 开发板型号 | Ai-M64L-12F-Kit |
| 分类 | WiFi |
| 规格书版本 | Ai-M64L-12F-Kit Specification V1.0.1 |
| 数据来源 | [官方规格书](https://aithinker-static.oss-cn-shenzhen.aliyuncs.com/docs/Public%20Document%20Center/WiFi/ai_m64/Specification/Ai-M64L-12F-Kit_V1.0.1%20Specification-20260716A.pdf) |

## 引脚定义表（30 脚）

| 脚序 | 名称 | 功能说明 |
|:---:|:---:|:---------|
| 1 | ADC | ADC pin, voltage-divided with IO12 pin |
| 2 | 5/NC | GPIO5/SPI0_SCLK/SPI1_SCLK/I2S_FS/I2C_SCL/UART_SIG5/ADC_C H5/PWM0_CH1P/PWM0_CH2N/DBI_TypeC_DCn/JTAG_TCK (Default available; shared with module internal 32.768kHz crystal output pin. NC if custom module with internal SMD 32.768kHz crystal.) |
| 3 | 4/NC | GPIO4/SPI0_SS/SPI1_SS/I2S_BCLK/I2C_SCL/UART_SIG4/ADC_CH4/ PWM0_CH0P/PWM0_CH2P/DBI_TypeC_SDA/JTAG_TMS (Default available; shared with module internal 32.768kHz crystal input pin. NC if custom module with internal SMD 32.768kHz crystal.) |
| 4 | IO12 | GPIO12/SPI0_SS/SPI1_SS/I2S_BCLK/I2C_SCL/UART_SIG0/RMII_MD IO/CAM_DAT0/ADC_CH8/PWM0_CH0P/PWM0_CH2P/DBI_TypeB_D B0/DBI_TypeC_SDA/DISP_QSPI_SCL/AUPWM_P/JTAG_TMS |
| 5 | IO19 | GPIO19/SPI0_MOSI/SPI1_MOSI/I2S_DO/I2S_RCLK_O/I2C_SCL/UAR T_SIG7/RMII_RXD[0]/CAM_DAT7/PWM0_CH3P/PWM0_CH1N/DBI_ TypeB_DB7/DBI_TypeC_CSn/DISP_QSPI_CSn/AUPWM_N/JTAG_TDI |
| 6 | IO22 | GPIO22/SPI0_MISO/SPI1_MISO/I2S_DI/I2S_RCLK_O/I2C_SCL/UART _SIG10/CAM_HSYNC/PWM0_CH2P/PWM0_CH3P/DBI_TypeC_SCL/ DISP_QSPI_SDA2/JTAG_TDO |
| 7 | IO18 | GPIO18/SPI0_MISO/SPI1_MISO/I2S_DI/I2S_RCLK_O/I2C_SCL/UART _SIG6/RMII_RXD[1]/CAM_DAT6/PWM0_CH2P/PWM0_CH1P/DBI_Ty peB_DB6/DBI_TypeC_SCL/DISP_QSPI_SCL/AUPWM_P/JTAG_TDO |
| 8 | IO8/NC | GPIO8/SPI0_SS/SPI1_SS/I2S_BCLK/I2C_SCL/UART_SIG8/SF2_D2/SD IO_CMD/PWM0_CH0P/DBI_TypeC_SDA/DISP_QSPI_SDA0/JTAG_T MS (Default available; shared with module internal Flash pin. NC if custom module with internal SMD Flash.) |
| 9 | IO11/NC | GPIO11/SPI0_MOSI/SPI1_MOSI/I2S_DO/I2S_RCLK_O/I2C_SCL/UAR T_SIG11/SF2_D3/SDIO_DAT1/PWM0_CH3P/PWM0_CH1N/DBI_Type C_CSn/DISP_QSPI_SDA3/JTAG_TDI (Default available; shared with module internal Flash pin. NC if custom module with internal SMD Flash.) |
| 10 | GND | Ground |
| 11 | 3V3 | 3.3V power supply, recommended current ≥500mA |
| 12 | EN | Default as chip enable, active high |
| 13 | GND | Ground |
| 14 | GND | Ground |
| 15 | 5V | 5V power supply, recommended current ≥500mA |
| 16 | IO23 | GPIO23/SPI0_MOSI/SPI1_MOSI/I2S_DO/I2S_RCLK_O/I2C_SCL/UAR T_SIG11/RMII_MDIO/CAM_VSYNC/SWGPIO[23]/PWM0_CH3P/PWM0_CH3N/DBI_TypeC_CSn/DISP_QSPI_SDA3/JTAG_TDI Form Number: B&T-QR-RF-064-2 Version: A0 |
| 17 | IO13 | GPIO13/SPI0_SCLK/SPI1_SCLK/I2S_FS/I2C_SCL/UART_SIG1/RMII_ MDC/CAM_DAT1/ADC_CH9/PWM0_CH1P/PWM0_CH2N/DBI_TypeB _DB1/DBI_TypeC_DCn/DISP_QSPI_CSn/AUPWM_N/JTAG_TCK |
| 18 | IO21 | GPIO21/SPI0_SCLK/SPI1_SCLK/I2S_FS/I2C_SCL/UART_SIG9/PDM_ IN/CAM_CLK/PWM0_CH1P/PWM0_CH2N/DBI_TypeC_DCn/DISP_Q SPI_SDA1/JTAG_TCK |
| 19 | 36/NC | BOOT/GPIO36/SPI0_SS/SPI1_SS/I2S_BCLK/I2C_SCL/UART_SIG0/P WM0_CH0P/PWM0_CH2P/DBI_TypeB_DCn/JTAG_TMS (Only available on module versions with suffix “A” on the shield can marking, exposed to the module edge castellated pad) |
| 20 | IO20 | GPIO20/SPI0_SS/SPI1_SS/I2S_BCLK/I2C_SCL/UART_SIG8/PDM_CL K/RMII_RX_DV/CAM_VSYNC/PWM0_CH0P/PWM0_CH2P/DBI_Type C_SDA/DISP_QSPI_SDA0/JTAG_TMS |
| 21 | 3V3 | 3.3V power supply, recommended current ≥500mA |
| 22 | GND | Ground |
| 23 | USB_DM | USB_DM/GPIO33/SPI0_SCLK/SPI1_SCLK/I2S_FS/I2C_SCL/UART_SI G9/PDM_IN/ADC_CH11/PWM0_CH1P/PWM0_CH0N/DBI_TypeC_DC n/JTAG_TCK |
| 24 | USB_DP | USB_DP/GPIO32/SPI0_SS/SPI1_SS/I2S_BCLK/I2C_SCL/UART_SIG8/ PDM_CLK/ADC_CH10/PWM0_CH0P/DBI_TypeC_SDA/JTAG_TMS |
| 25 | IO9/NC | GPIO9/SPI0_SCLK/SPI1_SCLK/I2S_FS/I2C_SCL/UART_SIG9/SF2_D0 /SDIO_CLK/PWM0_CH1P/PWM0_CH0N/DBI_TypeC_DCn/DISP_QSPI _SDA1/JTAG_TCK (Default available; shared with module internal Flash pin. NC if custom module with internal SMD Flash.) |
| 26 | IO10/NC | GPIO10/SPI0_MISO/SPI1_MISO/I2S_DI/I2S_RCLK_O/I2C_SCL/UART _SIG10/SF2_CLK/SDIO_DAT0/PWM0_CH2P/PWM0_CH1P/DBI_Type C_SCL/DISP_QSPI_SDA2/JTAG_TDO (Default available; shared with module internal Flash pin. NC if custom module with internal SMD Flash.) |
| 27 | RX | GPIO35/SPI0_MOSI/SPI1_MOSI/I2S_DO/I2S_RCLK_O/I2C_SCL/UAR T_SIG11/PWM0_CH3P/PWM0_CH1N/DBI_TypeC_CSn/JTAG_TDI |
| 28 | TX | GPIO34/SPI0_MISO/SPI1_MISO/I2S_DI/I2S_RCLK_O/I2C_SCL/UART _SIG10/PWM0_CH2P/PWM0_CH1P/DBI_TypeC_SCL/JTAG_TDO |
| 29 | GND | Ground |
| 30 | 3V3 | 3.3V power supply, recommended current ≥500mA Note: Both BOOT and the test point on the back of the module can be used as Bootstrap. When the voltage is high at power-up, the module enters flashing mode; when the voltage is low at power-up, the module boots normally. The module internal default is low level. |

## 功能索引

| ADC_CH10 | USB_DP |
| ADC_CH11 | USB_DM |
| ADC_CH4 | 4/NC |
| ADC_CH8 | IO12 |
| ADC_CH9 | IO13 |
| GPIO10 | IO10/NC |
| GPIO11 | IO11/NC |
| GPIO12 | IO12 |
| GPIO13 | IO13 |
| GPIO18 | IO18 |
| GPIO19 | IO19 |
| GPIO20 | IO20 |
| GPIO21 | IO21 |
| GPIO22 | IO22 |
| GPIO23 | IO23 |
| GPIO32 | USB_DP |
| GPIO33 | USB_DM |
| GPIO34 | TX |
| GPIO35 | RX |
| GPIO36 | 36/NC |
| GPIO4 | 4/NC |
| GPIO5 | 5/NC |
| GPIO8 | IO8/NC |
| GPIO9 | IO9/NC |
| I2C_SCL | 4/NC、IO12、IO22、IO18、IO8/NC、36/NC、IO20、USB_DP、IO10/NC、TX |
| I2C_SDA | 5/NC、IO19、IO11/NC、IO23、IO13、IO21、USB_DM、IO9/NC、RX |
| I2S_BCLK | 4/NC、IO12、IO8/NC、36/NC、IO20、USB_DP |
| I2S_DI | IO22、IO18、IO10/NC、TX |
| I2S_DO | IO19、IO11/NC、IO23、RX |
| I2S_FS | 5/NC、IO13、IO21、USB_DM、IO9/NC |
| I2S_RCLK_O | IO19、IO22、IO18、IO11/NC、IO23、IO10/NC、RX、TX |
| PWM | IO12、IO19、IO18、IO13 |
| PWM0 | 5/NC、4/NC、IO12、IO19、IO22、IO18、IO8/NC、IO11/NC、IO23、IO13、IO21、36/NC、IO20、USB_DM、USB_DP、IO9/NC、IO10/NC、RX、TX |
| RXD | IO19、IO18 |
| SF2_CLK | IO10/NC |
| SF2_D0 | IO9/NC |
| SF2_D2 | IO8/NC |
| SF2_D3 | IO11/NC |
| SPI_CS | IO19、IO13 |
| SPI_SCL | IO12、IO18 |
| SPI_SDA | IO22、IO8/NC、IO11/NC、IO23、IO21、IO20、IO10/NC |
| USB_DM | USB_DM |
| USB_DP | USB_DP |

## 避坑提示

- 标 **NC / 默认不可用** 的引脚不能当普通 IO。
- 标 **与内部 Flash 共用** 的引脚勿用于外设，避免破坏固件。
- 引脚一针多功能，需**核对复用冲突**后再接线。
- 供电/电平、烧录流程以官方规格书为准。

## 数据来源与核对说明

> 本表由官方规格书自动解析生成（引脚页：17, 18）。**以官方规格书/原理图为准**；解析可能存在断行/遗漏，请人工核对后再接入项目。
