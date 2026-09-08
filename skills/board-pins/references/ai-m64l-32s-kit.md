# Ai-M64L-32S-Kit 开发板引脚配置

> 本文件是 `board-pins` skill 的**单板参考文档**。内容由官方规格书自动解析生成，**使用前请人工核对**。

## 板卡概要

| 项目 | 值 |
|------|----|
| 开发板型号 | Ai-M64L-32S-Kit |
| 分类 | WiFi |
| 规格书版本 | Ai-M64L-32S-Kit Specification V1.0.0 |
| 数据来源 | [官方规格书](https://aithinker-static.oss-cn-shenzhen.aliyuncs.com/docs/Public%20Document%20Center/WiFi/ai_m64/Specification/Ai-M64L-32S-Kit_V1.0.0%20Specification-20260805A.pdf) |

## 引脚定义表（41 脚）

| 脚序 | 名称 | 功能说明 |
|:---:|:---:|:---------|
| 2 | GND | Ground |
| 3 | EN | Chip enable by default; active high |
| 4 | IO5 | GPIO5/SPI0_SCLK/SPI1_SCLK/I2S_FS/I2C_SCL/UART_SIG5/ADC_C H5/PWM0_CH1P/PWM0_CH2N/DBI_TypeC_DCn/JTAG_TCK (Available by default. Shared with the module’s internal 32.768kHz crystal pin and internal DC-DC control pin. This I/O pin is NC if an integrated 32.768kHz crystal or integrated DC-DC is customized.) |
| 5 | IO4 | GPIO4/SPI0_SS/SPI1_SS/I2S_BCLK/I2C_SCL/UART_SIG4/ADC_CH4/ PWM0_CH0P/PWM0_CH2P/DBI_TypeC_SDA/JTAG_TMS (Available by default. Shared with the module’s internal 32.768kHz crystal input pin. This I/O pin is NC if an integrated 32.768kHz crystal is customized.) |
| 6 | IO18 | GPIO18/SPI0_MISO/SPI1_MISO/I2S_DI/I2S_RCLK_O/I2C_SCL/UART _SIG6/RMII_RXD[1]/CAM_DAT6/PWM0_CH2P/PWM0_CH1P/DBI_Ty peB_DB6/DBI_TypeC_SCL/DISP_QSPI_SCL/AUPWM_P/JTAG_TDO |
| 7 | IO12 | GPIO12/SPI0_SS/SPI1_SS/I2S_BCLK/I2C_SCL/UART_SIG0/RMII_MD IO/CAM_DAT0/ADC_CH8/PWM0_CH0P/PWM0_CH2P/DBI_TypeB_D B0/DBI_TypeC_SDA/DISP_QSPI_SCL/AUPWM_P/JTAG_TMS |
| 8 | IO13 | GPIO13/SPI0_SCLK/SPI1_SCLK/I2S_FS/I2C_SCL/UART_SIG1/RMII_ MDC/CAM_DAT1/ADC_CH9/PWM0_CH1P/PWM0_CH2N/DBI_TypeB _DB1/DBI_TypeC_DCn/DISP_QSPI_CSn/AUPWM_N/JTAG_TCK |
| 9 | IO8/IO21 | GPIO8/SPI0_SS/SPI1_SS/I2S_BCLK/I2C_SCL/UART_SIG8/SF2_D2/SD IO_CMD/PWM0_CH0P/DBI_TypeC_SDA/DISP_QSPI_SDA0/JTAG_TM S (Not available by default because it is shared with module’s internal Flash pins. This I/O is available on module versions with on-chip Flash. IO8 and IO21 can be swapped by customization; please contact Ai-Thinker if this option is required.) |
| 10 | IO20 | GPIO20/SPI0_SS/SPI1_SS/I2S_BCLK/I2C_SCL/UART_SIG8/PDM_CL K/RMII_RX_DV/CAM_VSYNC/PWM0_CH0P/PWM0_CH2P/DBI_Type C_SDA/DISP_QSPI_SDA0/JTAG_TMS |
| 11 | IO19 | GPIO19/SPI0_MOSI/SPI1_MOSI/I2S_DO/I2S_RCLK_O/I2C_SCL/UAR T_SIG7/RMII_RXD[0]/CAM_DAT7/PWM0_CH3P/PWM0_CH1N/DBI_ TypeB_DB7/DBI_TypeC_CSn/DISP_QSPI_CSn/AUPWM_N/JTAG_TDI |
| 12 | IO33 | USB_DM/GPIO33/SPI0_SCLK/SPI1_SCLK/I2S_FS/I2C_SCL/UART_SI G9/PDM_IN/ADC_CH11/PWM0_CH1P/PWM0_CH0N/DBI_TypeC_DC n/JTAG_TCK |
| 13 | IO32 | USB_DP/GPIO32/SPI0_SS/SPI1_SS/I2S_BCLK/I2C_SCL/UART_SIG8/P DM_CLK/ADC_CH10/PWM0_CH0P/DBI_TypeC_SDA/JTAG_TMS |
| 14 | NC | No connection |
| 15 | NC | No connection |
| 16 | GND | Ground Form Number: B&T-QR-RF-064-2 Version: A0 |
| 17 | 5V | 5V power supply, current recommended to be above 500mA |
| 18 | NC | No connection |
| 19 | NC | No connection |
| 20 | NC | No connection |
| 21 | NC | No connection |
| 22 | NC | No connection |
| 23 | NC | No connection |
| 24 | NC | No connection |
| 25 | NC | No connection |
| 26 | NC | No connection |
| 27 | NC | No connection |
| 28 | NC | No connection |
| 29 | NC | No connection |
| 30 | IO11 | GPIO11/SPI0_MOSI/SPI1_MOSI/I2S_DO/I2S_RCLK_O/I2C_SCL/UAR T_SIG11/SF2_D3/SDIO_DAT1/PWM0_CH3P/PWM0_CH1N/DBI_Type C_CSn/DISP_QSPI_SDA3/JTAG_TDI (Not available by default because it is shared with module’s internal Flash pins. If this I/O pin is required, please contact Ai-Thinker to customize a module with on-chip Flash.) |
| 31 | IO10 | GPIO10/SPI0_MISO/SPI1_MISO/I2S_DI/I2S_RCLK_O/I2C_SCL/UART _SIG10/SF2_CLK/SDIO_DAT0/PWM0_CH2P/PWM0_CH1P/DBI_Type C_SCL/DISP_QSPI_SDA2/JTAG_TDO (Not available by default because it is shared with module’s internal Flash pins. If this I/O pin is required, please contact Ai-Thinker to customize a module with on-chip Flash.) |
| 32 | IO9 | GPIO9/SPI0_SCLK/SPI1_SCLK/I2S_FS/I2C_SCL/UART_SIG9/SF2_D0 /SDIO_CLK/PWM0_CH1P/PWM0_CH0N/DBI_TypeC_DCn/DISP_QSPI _SDA1/JTAG_TCK (Not available by default because it is shared with module’s internal Flash pins. If this I/O pin is required, please contact Ai-Thinker to customize a module with on-chip Flash.) |
| 33 | IO21/IO8 | GPIO21/SPI0_SCLK/SPI1_SCLK/I2S_FS/I2C_SCL/UART_SIG9/PDM_I N/CAM_CLK/PWM0_CH1P/PWM0_CH2N/DBI_TypeC_DCn/DISP_QS PI_SDA1/JTAG_TCK (Available by default. IO21 and IO8 may be swapped by customization; please contact Ai-Thinker if this option is required.) Form Number: B&T-QR-RF-064-2 Version: A0 |
| 34 | BOOT | BOOT/GPIO36/SPI0_SS/SPI1_SS/I2S_BCLK/I2C_SCL/UART_SIG0/PWM0_CH0P/PWM0_CH2P/DBI_TypeB_DCn/JTAG_TMS (Only available on module version with suffix “A” on the shield cover marking, exposed to the module edge castellated pads) |
| 35 | IO6 | GPIO6/SPI0_MISO/SPI1_MISO/I2S_DI/I2S_RCLK_O/I2C_SCL/UART_ SIG6/SF2_CS/ADC_CH6/SDIO_DAT2/PWM0_CH2P/PWM0_CH3P/DBI _TypeC_SCL/DISP_QSPI_SCL/JTAG_TDO (Not available by default because it is shared with module’s internal Flash pins. If this I/O pin is required, please contact Ai-Thinker to customize a module with on-chip Flash.) |
| 36 | IO7 | GPIO7/SPI0_MOSI/SPI1_MOSI/I2S_DO/I2S_RCLK_O/I2C_SCL/UART _SIG7/SF2_D1/ADC_CH7/SDIO_DAT3/PWM0_CH3P/PWM0_CH3N/D BI_TypeC_CSn/DISP_QSPI_CSn/JTAG_TDI (Not available by default because it is shared with module’s internal Flash pins. If this I/O pin is required, please contact Ai-Thinker to customize a module with on-chip Flash.) |
| 37 | IO22 | GPIO22/SPI0_MISO/SPI1_MISO/I2S_DI/I2S_RCLK_O/I2C_SCL/UART _SIG10/CAM_HSYNC/PWM0_CH2P/PWM0_CH3P/DBI_TypeC_SCL/D ISP_QSPI_SDA2/JTAG_TDO |
| 38 | RX | GPIO35/SPI0_MOSI/SPI1_MOSI/I2S_DO/I2S_RCLK_O/I2C_SCL/UAR T_SIG11/PWM0_CH3P/PWM0_CH1N/DBI_TypeC_CSn/JTAG_TDI |
| 39 | TX | GPIO34/SPI0_MISO/SPI1_MISO/I2S_DI/I2S_RCLK_O/I2C_SCL/UART _SIG10/PWM0_CH2P/PWM0_CH1P/DBI_TypeC_SCL/JTAG_TDO |
| 40 | GND | Ground |
| 41 | CORE | Internal core-voltage input. (Floating by default. For an ultra-low-power module, a DC-DC circuit needs to be configured on this pin. For detailed solutions, please contact Ai-Thinker.) |
| 42 | IO23 | GPIO23/SPI0_MOSI/SPI1_MOSI/I2S_DO/I2S_RCLK_O/I2C_SCL/UAR T_SIG11/RMII_MDIO/CAM_VSYNC/SWGPIO[23]/PWM0_CH3P/PWM 0_CH3N/DBI_TypeC_CSn/DISP_QSPI_SDA3/JTAG_TDI Note: Both BOOT and the test point on the back of the module can be used as Bootstrap. When the voltage is high at power-up, the module enters programming mode; when the voltage is low at power-up, the module boots normally. The internal default level of the module is low. |

## 功能索引

| ADC_CH10 | IO32 |
| ADC_CH11 | IO33 |
| ADC_CH4 | IO4 |
| ADC_CH6 | IO6 |
| ADC_CH7 | IO7 |
| ADC_CH8 | IO12 |
| ADC_CH9 | IO13 |
| GPIO10 | IO10 |
| GPIO11 | IO11 |
| GPIO12 | IO12 |
| GPIO13 | IO13 |
| GPIO18 | IO18 |
| GPIO19 | IO19 |
| GPIO20 | IO20 |
| GPIO21 | IO21/IO8 |
| GPIO22 | IO22 |
| GPIO23 | IO23 |
| GPIO32 | IO32 |
| GPIO33 | IO33 |
| GPIO34 | TX |
| GPIO35 | RX |
| GPIO36 | BOOT |
| GPIO4 | IO4 |
| GPIO5 | IO5 |
| GPIO6 | IO6 |
| GPIO7 | IO7 |
| GPIO8 | IO8/IO21 |
| GPIO9 | IO9 |
| I2C_SCL | IO4、IO18、IO12、IO8/IO21、IO20、IO32、IO10、BOOT、IO6、IO22、TX |
| I2C_SDA | IO5、IO13、IO19、IO33、IO11、IO9、IO21/IO8、IO7、RX、IO23 |
| I2S_BCLK | IO4、IO12、IO8/IO21、IO20、IO32、BOOT |
| I2S_DI | IO18、IO10、IO6、IO22、TX |
| I2S_DO | IO19、IO11、IO7、RX、IO23 |
| I2S_FS | IO5、IO13、IO33、IO9、IO21/IO8 |
| I2S_RCLK_O | IO18、IO19、IO11、IO10、IO6、IO7、IO22、RX、TX、IO23 |
| PWM | IO18、IO12、IO13、IO19、IO23 |
| PWM0 | IO5、IO4、IO18、IO12、IO13、IO8/IO21、IO20、IO19、IO33、IO32、IO11、IO10、IO9、IO21/IO8、BOOT、IO6、IO7、IO22、RX、TX、IO23 |
| RXD | IO18、IO19 |
| SF2_CLK | IO10 |
| SF2_CS | IO6 |
| SF2_D0 | IO9 |
| SF2_D1 | IO7 |
| SF2_D2 | IO8/IO21 |
| SF2_D3 | IO11 |
| SPI_CS | IO13、IO19、IO7 |
| SPI_SCL | IO18、IO12、IO6 |
| SPI_SDA | IO8/IO21、IO20、IO11、IO10、IO22、IO23 |
| USB_DM | IO33 |
| USB_DP | IO32 |

## 避坑提示

- 标 **NC / 默认不可用** 的引脚不能当普通 IO。
- 标 **与内部 Flash 共用** 的引脚勿用于外设，避免破坏固件。
- 引脚一针多功能，需**核对复用冲突**后再接线。
- 供电/电平、烧录流程以官方规格书为准。

## 数据来源与核对说明

> 本表由官方规格书自动解析生成（引脚页：17, 18, 19）。**以官方规格书/原理图为准**；解析可能存在断行/遗漏，请人工核对后再接入项目。
