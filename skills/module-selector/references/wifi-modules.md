# WiFi 模组选型参考

数据来源: D:\Users\Seahi\Desktop\vitpress_docs_resoure\docs\zh\wifi\ (官方文档源仓库，各系列 index 为准)
> 在售板卡全集/官方规格书链接以 `board-pins` skill 的 `kit-boards-index.md` 交叉核对。
> Ai-WB3（亮牛 LN882H）、Ai-WB1（联盛德 W800）、BW21/BW60（瑞昱 RTL87xx）芯片均已从官方源确认。

## 0. 快速选型总览（方案C · 矩阵表）

按**芯片平台 → 协议代际 → 系列 → 功能定位**组织，横向对比 Wi-Fi 模组：

| 芯片平台 | 协议代际 | 系列 | 典型型号 | 功能定位 | 天线 | 封装 | 功耗级别 |
|---|---|---|---|---|---|---|---|
| BL602 (博流) | Wi-Fi 4 + BLE 5.0 | **Ai-WB2** | Ai-WB2-12F / 32S / 13 | 高性价比、通用智能硬件 | PCB / IPEX | SMD-22 / 38 / 18 | 深度睡眠 12μA |
| LN882H (亮牛) | Wi-Fi 4 + BLE 5.1 | **Ai-WB3** | Ai-WB3-01C / 12F | 另一起 Wi-Fi + BLE 方案 | PCB | SMD | 中 |
| W800 (联盛德) | Wi-Fi 4 + BLE 4.2 | **Ai-WB1** | Ai-WB1-12F / 32S / A1S | 早期经典双模 | PCB / IPEX | SMD | 早期平台 |
| BL618 (博流) | Wi-Fi 6 + BLE 5.3 + Thread | **Ai-M61** | Ai-M61-32S / 32SU | 音视频 / 摄像头 / 带屏 | PCB / IPEX | SMD-38 / 41 | 中 |
| BL616 (博流) | Wi-Fi 6 + BLE 5.3 + Thread | **Ai-M62** | Ai-M62-12F / 13 / 32S | 均衡低功耗、多封装 | PCB / IPEX / 半孔 | SMD-18 / 22 / 38 | 低至 120μA |
| BL616CL (博流) | Wi-Fi 6 + BLE 5.3 | **Ai-M64** | Ai-M64P-32S / M64L-12F / M64L-32S | 超低功耗（TWT/OFDMA） | PCB / IPEX | SMD | 保活 90μA |
| RTL8720DN (瑞昱) | 双频 Wi-Fi 4 (2.4G+5.8G) + BLE 5.0 | **BW16** | BW16 | 双频基础款、Mesh | PCB | SMD | 中 |
| RTL8711DAx (瑞昱) | 双频 Wi-Fi 4 + BLE 5.0 | **BW20** | BW20-07S / 12F | 双频增强、CSI / Mesh | PCB / IPEX | SMD | 中 |
| RTL87xx (瑞昱) | 双频 Wi-Fi + BLE | **BW21 / BW60** | BW21-CBV / BW60-12F | 双频新平台 | PCB / IPEX | SMD | 中 |
| ESP8266/ESP32 | Wi-Fi 4 经典 | **ESP 系列** | ESP8266 | 经典、生态成熟 | PCB | SMD | 中 |
| 平台专供 | Wi-Fi（绑定生态） | **TG 系列** | TG-12F | 直连天猫精灵等平台 | PCB | SMD | 中 |

> 更细的引脚/开发板规格书入口见 `board-pins` skill 的 `kit-boards-index.md`。

---

# 一、Wi-Fi 4 + BLE 双模（低成本经典）

## Ai-WB2 系列 (Wi-Fi 4 + BLE 5.0)

**芯片**: BL602 | **协议**: Wi-Fi 802.11b/g/n, BLE 5.0 | **CPU**: 32-bit RISC 192MHz | **RAM**: 276KB

### 功能定位
**高性价比** · 智能硬件主力 · AT 指令快速上手 · 生态最成熟

### 型号列表

| 型号 | 封装 | IO口(内置FLASH) | 尺寸(mm) | 天线 | FLASH | 规格书 |
|------|------|-----------------|----------|------|-------|--------|
| Ai-WB2-12F | SMD-22 | 15 | 24.0×16.0×3.1 | PCB天线 | 4MB | [中文](https://aithinker-static.oss-cn-shenzhen.aliyuncs.com/docs/_media_old/ai-wb2-12f_v1.1.3_product_specification_cn.pdf) / [EN](https://aithinker-static.oss-cn-shenzhen.aliyuncs.com/docs/_media_old/ai-wb2-12f_v1.1.3_product_specification_en.pdf) |
| Ai-WB2-12S | SMD-16 | 11 | 24.0×16.0×3.1 | PCB天线 | 4MB | [中文](https://aithinker-static.oss-cn-shenzhen.aliyuncs.com/docs/_media_old/ai-wb2-12s_v1.1.2_product_specification_cn.pdf) / [EN](https://aithinker-static.oss-cn-shenzhen.aliyuncs.com/docs/_media_old/ai-wb2-12s_v1.1.2_product_specification_en.pdf) |
| Ai-WB2-32S | SMD-38 | 15 | 25.5×18.0×3.1 | PCB/IPEX | 4MB | [中文](https://aithinker-static.oss-cn-shenzhen.aliyuncs.com/docs/_media_old/ai-wb2-32s_v1.0.2_product_specification_cn.pdf) / [EN](https://aithinker-static.oss-cn-shenzhen.aliyuncs.com/docs/_media_old/ai-wb2-32s_v1.0.2_product_specification_en.pdf) |
| Ai-WB2-07S | SMD-16 | 11 | 17.0×16.0×3.1 | IPEX | 4MB | [中文](https://aithinker-static.oss-cn-shenzhen.aliyuncs.com/docs/_media_old/ai-wb2-07s_v1.1.2_product_specification_cn.pdf) / [EN](https://aithinker-static.oss-cn-shenzhen.aliyuncs.com/docs/_media_old/ai-wb2-07s_v1.1.2_product_specification_en.pdf) |
| Ai-WB2-13 | SMD-18 | 11 | 20.0×18.0×3.1 | PCB天线 | 4MB | [中文](https://aithinker-static.oss-cn-shenzhen.aliyuncs.com/docs/_media_old/ai-wb2-13_v1.1.2_product_specification_cn.pdf) / [EN](https://aithinker-static.oss-cn-shenzhen.aliyuncs.com/docs/_media_old/ai-wb2-13_v1.1.2_product_specification_en.pdf) |
| Ai-WB2-13U | SMD-18 | 11 | 14.0×18.0×3.1 | IPEX | 4MB | [中文](https://aithinker-static.oss-cn-shenzhen.aliyuncs.com/docs/_media_old/ai-wb2-13u_v1.1.1_product_specification_cn.pdf) / [EN](https://aithinker-static.oss-cn-shenzhen.aliyuncs.com/docs/media/WiFi/WB2/Module_Specification/ai-wb2-13u_v1.1.1_product_specification_en.pdf) |
| Ai-WB2-01M | DIP-18 | 14 | 18.0×18.0×2.8 | PCB天线 | 2MB | [中文](https://aithinker-static.oss-cn-shenzhen.aliyuncs.com/docs/_media_old/ai-wb2-01m_v1.0.2_product_specification_cn.pdf) / [EN](https://aithinker-static.oss-cn-shenzhen.aliyuncs.com/docs/_media_old/ai-wb2-01m_v1.0.2_product_specification_en.pdf) |
| Ai-WB2-M1-I | SMD-61 | 15 | 12.5×13.2×2.4 | IPEX | 4MB | [中文](https://aithinker-static.oss-cn-shenzhen.aliyuncs.com/docs/_media_old/ai-wb2-m1-i_v1.0.0_product_specification_cn.pdf) / [EN](https://aithinker-static.oss-cn-shenzhen.aliyuncs.com/docs/_media_old/ai-wb2-m1-i_v1.0.0_product_specification_en.pdf) |
| Ai-WB2-M1 | SMD-61 | 15 | 16.6×13.2×2.4 | PCB天线 | 4MB | [中文](https://aithinker-static.oss-cn-shenzhen.aliyuncs.com/docs/_media_old/ai-wb2-m1_v1.0.1_product_specification_cn.pdf) / [EN](https://aithinker-static.oss-cn-shenzhen.aliyuncs.com/docs/_media_old/ai-wb2-m1_v1.0.1_product_specification_en.pdf) |
| Ai-WB2-05W | SMD-22 | 15 | 13.0×19.0×2.4 | PCB天线 | 2MB | [中文](https://aithinker-static.oss-cn-shenzhen.aliyuncs.com/docs/_media_old/ai-wb2-05w_v1.1.2_product_specification_cn.pdf) / [EN](https://aithinker-static.oss-cn-shenzhen.aliyuncs.com/docs/_media_old/ai-wb2-05w_v1.1.2_product_specification_en.pdf) |
| Ai-WB2-01F | SMD-18 | 11 | 11.0×10.0×2.0 | 半孔天线 | 2MB | [中文](https://aithinker-static.oss-cn-shenzhen.aliyuncs.com/docs/_media_old/ai-wb2-01f_v1.0.2_product_specification_cn.pdf) / [EN](https://aithinker-static.oss-cn-shenzhen.aliyuncs.com/docs/_media_old/ai-wb2-01f_v1.0.2_product_specification_en.pdf) |
| Ai-WB2-01S | DIP-8 | 3 | 14.5×24.5×11.2 | PCB天线 | 2MB | [中文](https://aithinker-static.oss-cn-shenzhen.aliyuncs.com/docs/_media_old/ai-wb2-01s_v1.0.0_product_specification_cn.pdf) / [EN](https://aithinker-static.oss-cn-shenzhen.aliyuncs.com/docs/_media_old/ai-wb2-01s_v1.0.0_product_specification_en.pdf) |

### 通用规格
- **供电**: 2.7V~3.6V, ≥500mA
- **工作温度**: -40℃~85℃
- **功耗**: 深度睡眠 12μA
- **传输距离**: 480~524米
- **安全**: WPS/WEP/WPA/WPA2/WPA3
- **协议**: TCP/UDP/HTTP/HTTPS/MQTT/MQTTS

### 资源链接
- **芯片数据手册**: [中文](https://dev.bouffalolab.com/media/doc/602/open/datasheet/zh/html/index.html) / [EN](https://dev.bouffalolab.com/media/doc/602/open/datasheet/en/html/index.html)
- **芯片参考手册**: [中文](https://dev.bouffalolab.com/media/doc/602/open/reference_manual/zh/html/index.html) / [EN](https://dev.bouffalolab.com/media/doc/602/open/reference_manual/en/html/index.html)
- **SDK源码**: [GitHub](https://github.com/Ai-Thinker-Open/Ai-Thinker-WB2)

---

## Ai-WB3 系列 (Wi-Fi 4 + BLE 5.1)

**芯片**: 亮牛 LN882H | **协议**: Wi-Fi 802.11b/g/n, BLE 5.1 | **CPU**: Cortex-M4F 160MHz | **RAM**: 296KB SRAM + 128KB ROM | **定位**: 另一起的 Wi-Fi + BLE 方案

### 型号列表

| 型号 | 天线 | 规格书 |
|------|------|--------|
| Ai-WB3-12F | PCB | [中文](https://aithinker-static.oss-cn-shenzhen.aliyuncs.com/docs/_media_old/ai-wb3-12f_v1.0_规格书.pdf) / [EN](https://aithinker-static.oss-cn-shenzhen.aliyuncs.com/docs/_media_old/ai-wb3-12f_v1.0_specification.pdf) |
| Ai-WB3-01C | PCB | [中文](https://aithinker-static.oss-cn-shenzhen.aliyuncs.com/docs/media/WiFi/WB3/specification/Ai-WB3-01C_V1.0.0%20%E8%A7%84%E6%A0%BC%E4%B9%A620230307.pdf) / [EN](https://aithinker-static.oss-cn-shenzhen.aliyuncs.com/docs/_media_old/ai-wb3-01c_v1.0.0_specification_20230308.pdf) |

### 特性
- 支持长距离传输（125/500Kbps）及高速传输（2Mbps）
- 多通道 ADC + 可编程放大器（适合声音传感器）
- AES-128/192/256 硬件加密、TRNG、256 位 EFUSE
- CHKSUM 加速器提升 TCP/UDP 效率
- 支持 AT 指令 + 二次开发（Windows 环境）

---

## Ai-WB1 系列 (Wi-Fi 4 + BLE 4.2 · 早期经典)

**芯片**: 联盛德 W800 | **协议**: Wi-Fi 802.11b/g/n, BLE 4.2 | **CPU**: 32-bit XT804 240MHz | **RAM**: 288KB / 2MB Flash | **定位**: 早期经典双模系列

### 型号列表

| 型号 | 天线 | 特点 | 规格书 |
|------|------|------|--------|
| Ai-WB1-12F | PCB | 基础款 | [中文](https://aithinker-static.oss-cn-shenzhen.aliyuncs.com/docs/_media_old/ai-wb1-12f_v1.1_规格书.pdf) / [EN](https://aithinker-static.oss-cn-shenzhen.aliyuncs.com/docs/_media_old/ai-wb1-12f_v1.1_specification.pdf) |
| Ai-WB1-32S | PCB / IPEX | 标准款 | [中文](https://aithinker-static.oss-cn-shenzhen.aliyuncs.com/docs/_media_old/ai-wb1-32s_v1.1_规格书.pdf) / [EN](https://aithinker-static.oss-cn-shenzhen.aliyuncs.com/docs/_media_old/ai-wb1-32s_v1.1_specification.pdf) |
| Ai-WB1-A1S | - | 语音版 | [中文](https://aithinker-static.oss-cn-shenzhen.aliyuncs.com/docs/_media_old/ai-wb1-a1s_v1.0_规格书.pdf) / [EN](https://aithinker-static.oss-cn-shenzhen.aliyuncs.com/docs/_media_old/ai-wb1-a1s_v1.0_specification.pdf) |
| Ai-WB1-32S-CAM | - | 摄像头版 | [中文](https://aithinker-static.oss-cn-shenzhen.aliyuncs.com/docs/_media_old/ai-wb1-32s-cam规格书v1.2.0.pdf) / [EN](https://aithinker-static.oss-cn-shenzhen.aliyuncs.com/docs/_media_old/ai-wb1-32s-cam_specification_v1.2.0.pdf) |

- **芯片数据手册**: [W800 规格书](https://aithinker-static.oss-cn-shenzhen.aliyuncs.com/docs/_media_old/w800芯片产品规格书_v3.0.pdf)

> 较老方案。若用新项目，建议优先选择生态更成熟的 Ai-WB2 系列（同为 Wi-Fi 4 + BLE 双模）。

---

# 二、Wi-Fi 6 + BLE 双模（新一代）

## Ai-M61 系列 (Wi-Fi 6 + BLE 5.3 + 音视频)

**芯片**: BL618 | **协议**: Wi-Fi 802.11b/g/n/ax, BLE 5.3, Thread | **CPU**: RISC-V 320MHz | **RAM**: 532KB SRAM + 4MB PSRAM

### 功能定位
**音视频首选** · 摄像头 / 带屏 / 音频 · 高性能外设最全

### 型号列表

| 型号 | 封装 | 可用IO | 尺寸(mm) | 天线 | 规格书 |
|------|------|--------|----------|------|--------|
| Ai-M61-32S | SMD-40 | 26 | 25.5×18.0×3.1 | PCB/IPEX | [中文](https://aithinker-static.oss-cn-shenzhen.aliyuncs.com/docs/_media_old/ai-m61-32s_v1.3.0_product_specification_cn.pdf) / [EN](https://aithinker-static.oss-cn-shenzhen.aliyuncs.com/docs/_media_old/ai-m61-32s_v1.3.0_product_specification_en.pdf) |
| Ai-M61-32SU | SMD-41 | 26 | 19.0×18.0×3.1 | IPEX | [中文](https://aithinker-static.oss-cn-shenzhen.aliyuncs.com/docs/_media_old/ai-m61-32su_v1.1.0_product_specification_cn.pdf) / [EN](https://aithinker-static.oss-cn-shenzhen.aliyuncs.com/docs/_media_old/ai-m61-32su_v1.1.0_product_specification_en.pdf) |

### 特性
- **接口**: Camera、MJPEG、Display、Audio Codec、USB2.0、SDU、以太网(EMAC)、SD/MMC、SPI、UART、I2C、I2S、PWM、GPDAC、GPADC、ACOMP、GPIO
- **FLASH**: 默认 8MB，最大 16MB
- **供电**: 2.97V~3.6V, ≥500mA
- **安全**: WPS/WEP/WPA/WPA2/WPA3

### 资源链接
- **芯片数据手册**: [中文](https://aithinker-static.oss-cn-shenzhen.aliyuncs.com/docs/_media_old/bl616_bl618_ds_zh_cn_2.5_open_.pdf) / [EN](https://aithinker-static.oss-cn-shenzhen.aliyuncs.com/docs/_media_old/bl616_bl618_ds_en_2.5_open_.pdf)
- **芯片参考手册**: [中文](https://aithinker-static.oss-cn-shenzhen.aliyuncs.com/docs/_media_old/bl616_bl618_rm_zh_cn_0.98_open_.pdf) / [EN](https://aithinker-static.oss-cn-shenzhen.aliyuncs.com/docs/_media_old/bl616_bl618_rm_en_0.98_open_.pdf)
- **SDK源码**: [GitHub](https://github.com/bouffalolab/bouffalo_sdk/tree/master)

---

## Ai-M62 系列 (Wi-Fi 6 + BLE 5.3 低功耗)

**芯片**: BL616 | **协议**: Wi-Fi 802.11b/g/n/ax, BLE 5.3, Thread | **CPU**: RISC-V 320MHz | **RAM**: 532KB SRAM

### 功能定位
**均衡低功耗** · 封装形态最全（含 M.2 / CBS） · 无音视频需求时的首选

### 型号列表

| 型号 | 封装 | 尺寸(mm) | 天线 | 规格书 |
|------|------|----------|------|--------|
| Ai-M62-07S | SMD | - | IPEX | [中文](https://aithinker-static.oss-cn-shenzhen.aliyuncs.com/docs/_media_old/ai-m62-07s_v2.0.0_product_specification_cn.pdf) / [EN](https://aithinker-static.oss-cn-shenzhen.aliyuncs.com/docs/_media_old/ai-m62-07s_v2.0.0_product_specification_en.pdf) |
| Ai-M62-12F | SMD-22 | 24.0×16.0×3.1 | PCB天线 | [中文](https://aithinker-static.oss-cn-shenzhen.aliyuncs.com/docs/_media_old/ai-m62-12f_v1.0.1_product_specification_cn.pdf) / [EN](https://aithinker-static.oss-cn-shenzhen.aliyuncs.com/docs/_media_old/ai-m62-12f_v1.0.1_specification-20240626.pdf) |
| Ai-M62-13 | SMD-18 | 20.0×18.0×3.1 | PCB天线 | [中文](https://aithinker-static.oss-cn-shenzhen.aliyuncs.com/docs/_media_old/ai-m62-13_v1.0.1_product_specification_cn.pdf) / [EN](https://aithinker-static.oss-cn-shenzhen.aliyuncs.com/docs/_media_old/ai-m62-13_v1.0.1_product_specification_en.pdf) |
| Ai-M62-13U | SMD-18 | 14.0×18.0×3.1 | IPEX | [中文](https://aithinker-static.oss-cn-shenzhen.aliyuncs.com/docs/_media_old/ai-m62-13u_v1.0.1_product_specification_cn.pdf) / [EN](https://aithinker-static.oss-cn-shenzhen.aliyuncs.com/docs/_media_old/ai-m62-13u_v1.0.1_product_specification_en.pdf) |
| Ai-M62-32S | SMD-38 | 25.5×18.0×3.1 | PCB/IPEX | [中文](https://aithinker-static.oss-cn-shenzhen.aliyuncs.com/docs/_media_old/ai-m62-32s_v1.0.1_规格书-20240703.pdf) / [EN](https://aithinker-static.oss-cn-shenzhen.aliyuncs.com/docs/_media_old/ai-m62-32s_v1.0.1_specification-20240703.pdf) |
| Ai-M62-M2-I | SMD | - | IPEX | [中文](https://aithinker-static.oss-cn-shenzhen.aliyuncs.com/docs/_media_old/ai-m62-m2-i_v1.0.1规格书-20240705.pdf) / [EN](https://aithinker-static.oss-cn-shenzhen.aliyuncs.com/docs/_media_old/ai-m62-m2-i_v1.0.1_specification-20240705.pdf) |
| Ai-M62-M01L | SMD | - | - | [中文](https://aithinker-static.oss-cn-shenzhen.aliyuncs.com/docs/_media_old/ai-m62-m01l_v1.0.1规格书-20250620.pdf) / [EN](https://aithinker-static.oss-cn-shenzhen.aliyuncs.com/docs/_media_old/ai-m62-m01l_v1.0.1_sepcification-20250620.pdf) |
| Ai-M62-CBS | CBS | - | - | [中文](https://aithinker-static.oss-cn-shenzhen.aliyuncs.com/docs/_media_old/ai-m62-cbs_v1.0.0规格书-20240613.pdf) / [EN](https://aithinker-static.oss-cn-shenzhen.aliyuncs.com/docs/_media_old/ai-m62-cbs_v1.0.0_specification-20240613.pdf) |

### 特性
- **接口**: USB2.0、SDU、SPI、UART、I2C、I2S、PWM、GPADC、GPDAC、ACOMP、GPIO
- **FLASH**: 可选 2/4/8MB
- **PSRAM**: 可选 4/8MB
- **功耗**: 低至 120μA

### 资源链接
- **芯片数据手册**: [中文](https://aithinker-static.oss-cn-shenzhen.aliyuncs.com/docs/_media_old/bl616_bl618_ds_zh_cn_2.5_open_.pdf) / [EN](https://aithinker-static.oss-cn-shenzhen.aliyuncs.com/docs/_media_old/bl616_bl618_ds_en_2.5_open_.pdf)
- **芯片参考手册**: [中文](https://aithinker-static.oss-cn-shenzhen.aliyuncs.com/docs/_media_old/bl616_bl618_rm_zh_cn_0.98_open_.pdf) / [EN](https://aithinker-static.oss-cn-shenzhen.aliyuncs.com/docs/_media_old/bl616_bl618_rm_en_0.98_open_.pdf)
- **SDK源码**: [GitHub](https://github.com/bouffalolab/bouffalo_sdk/tree/master)

---

## Ai-M64 系列 (Wi-Fi 6 + BLE 5.3 超低功耗)

**芯片**: BL616CL | **协议**: Wi-Fi 802.11b/g/n/ax, BLE 5.3 | **CPU**: RISC-V 320MHz | **RAM**: 388KB SRAM + 4/8MB PSRAM

### 功能定位
**超低功耗（电池供电首选）** · 支持 TWT / OFDMA / RX 分集

### 型号列表

| 型号 | 封装 | 可用IO | 天线 | 规格书 |
|------|------|--------|------|--------|
| Ai-M64P-32S | SMD | 37 | PCB/IPEX | [中文](https://aithinker-static.oss-cn-shenzhen.aliyuncs.com/docs/media/WiFi/M64/M64P/Specification/CN/Ai-M64P-32S_V1.0.1%20%E8%A7%84%E6%A0%BC%E4%B9%A6%2020260716G.pdf) / [EN](https://aithinker-static.oss-cn-shenzhen.aliyuncs.com/docs/media/WiFi/M64/M64P/Specification/EN/Ai-M64P-32S_V1.0.1%20Specification%2020260716A.pdf) |
| Ai-M64L-12F | SMD | - | - | [中文](https://aithinker-static.oss-cn-shenzhen.aliyuncs.com/docs/media/WiFi/M64/M64L/Specification/CN/Ai-M64L-12F_V1.0.1%E8%A7%84%E6%A0%BC%E4%B9%A620260717B(1).pdf) / [EN](https://aithinker-static.oss-cn-shenzhen.aliyuncs.com/docs/media/WiFi/M64/M64L/Specification/EN/Ai-M64L-12F_V1.0.1%20Specification%2020260717A.pdf) |
| Ai-M64L-32S | SMD | - | - | [官方规格书](https://aithinker-static.oss-cn-shenzhen.aliyuncs.com/docs/Public%20Document%20Center/WiFi/ai_m64/Specification/Ai-M64L-32S-Kit_V1.0.0%20Specification-20260805A.pdf) |

> M64P（Power）与 M64L（Low-power）为同一芯片平台的两个细分系列，按封装/IO/功耗取舍。

### 特性
- **接口**: USB2.0、EMAC、Camera、Display(DBI)、MJPEG、SDIO2.0、SPI、UART、I2C、I2S、PWM、GPADC
- **功耗**: WiFi保活低至 90μA
- **支持**: OFDMA、TWT、LDPC、STBC、Beamformee、RX分集

### 资源链接
- **芯片数据手册**: [中文](https://aithinker-static.oss-cn-shenzhen.aliyuncs.com/docs/media/WiFi/M64/M64P/Datasheets/BL616CL_DS_zh_CN_0.9.4.pdf) / [EN](https://aithinker-static.oss-cn-shenzhen.aliyuncs.com/docs/media/WiFi/M64/M64P/Datasheets/BL616CL_DS_en_0.9.4.pdf)

---

# 三、双频 Wi-Fi（2.4G + 5.8G）

## BW 系列

**芯片**: RTL8720DN / RTL8711 / RTL8735B / RTL8711F | **协议**: 双频 Wi-Fi（2.4GHz + 5.8GHz）, BLE 5.0/5.4

### 功能定位
**双频抗干扰** · Mesh 组网 · Wi-Fi CSI（高精度定位/感知） · 摄像头（BW21） · Wi-Fi 6（BW60）

### 型号列表

| 型号 | 芯片 | 协议 | CPU | BLE | 特点 |
|------|------|------|-----|-----|------|
| BW16 | RTL8720DN | 双频 802.11a/b/g/n | Cortex-M4F 200MHz + M23 20MHz | 5.0 | 双频基础款 |
| BW20-07S | RTL8711 | 双频 802.11a/b/g/n | Cortex-M4F 330MHz + M23 100MHz | 5.0 | 双频增强，CSI/Mesh |
| BW20-12F | RTL8711 | 双频 802.11a/b/g/n | Cortex-M4F 330MHz + M23 100MHz | 5.0 | 双频增强，CSI/Mesh |
| BW21-CBV | RTL8735B | 双频 802.11a/b/g/n | ARM v8M 500MHz | 5.1 | 摄像头模组，含 ISP + H264/H265 + 神经网络 |
| BW60-12F | RTL8711F | **双频 Wi-Fi 6** 802.11a/b/g/n/ac/ax | Armv8.1-M 320MHz 双核 | 5.4 | 双频 Wi-Fi 6 + 超低功耗 |

> BW16/BW20 为双频 Wi-Fi 4；**BW60 为双频 Wi-Fi 6**（支持 ax）；BW21 为双频摄像头模组。选型时注意区分代际。

### 型号规格书链接（官方源 rtl87xx）
> - BW16: https://aithinker-static.oss-cn-shenzhen.aliyuncs.com/docs/Public%20Document%20Center/WiFi/rtl87xx/bw16/Specification/BW16_V1.2.2%E8%A7%84%E6%A0%BC%E4%B9%A6-20240325.pdf
> - BW20-12F: https://aithinker-static.oss-cn-shenzhen.aliyuncs.com/docs/Public%20Document%20Center/WiFi/rtl87xx/bw20/Specification/BW20-12F_V1.0.2%E8%A7%84%E6%A0%BC%E4%B9%A6-20250417.pdf
> - BW20-07S: https://aithinker-static.oss-cn-shenzhen.aliyuncs.com/docs/Public%20Document%20Center/WiFi/rtl87xx/bw20/Specification/BW20-07S_V1.0.2%E8%A7%84%E6%A0%BC%E4%B9%A6-20250417.pdf
> - BW21-CBV: https://aithinker-static.oss-cn-shenzhen.aliyuncs.com/docs/Public%20Document%20Center/WiFi/rtl87xx/bw21/Specification/BW21-CBV_V1.0.0%E8%A7%84%E6%A0%BC%E4%B9%A6-20241219.pdf
> - BW60-12F: https://aithinker-static.oss-cn-shenzhen.aliyuncs.com/docs/Public%20Document%20Center/WiFi/rtl87xx/bw60/Specification/BW60-12F_V1.0.0%E8%A7%84%E6%A0%BC%E4%B9%A6-20260409.pdf

### 特性
- **FLASH**: 默认 4MB，可选 8MB/16MB
- **PSRAM**: BW20 可选 4MB
- **吞吐量**: TCP 17-19Mbps, UDP 26-55Mbps
- **安全**: WPA/WPA2/WPA3 Personal/Enterprise
- **BW60**: 支持 802.11ax、Bluetooth 5.4（含 LE Long-Range 125/500kbps）、Arm TrustZone-M
- **BW21**: 集成 ISP + H264/H265 视频编码器，支持 AI 神经网络

---

# 四、经典 Wi-Fi

## ESP8266 / ESP32 系列

**协议**: Wi-Fi 802.11b/g/n（部分支持 b/g/n + BLE）

### 功能定位
**生态最成熟 · 社区最大** · 适合快速验证 / 二次开发资料丰富的项目

### 型号
- ESP8266 系列模组（Wi-Fi 4）
- ESP32 系列模组（Wi-Fi 4 + BLE）

---

# 五、平台专供

## TG 系列

**定位**: 直连天猫精灵等生态平台（绑定平台认证）

### 型号
- **TG-12F**: 官方规格书见 https://aithinker-static.oss-cn-shenzhen.aliyuncs.com/docs/Public%20Document%20Center/WiFi/tg/Specification/TG-12F-Kit%20Specification-20201126.pdf

---

## Wi-Fi 选型建议

| 需求 | 推荐系列 | 理由 |
|------|----------|------|
| 高性价比 Wi-Fi + BLE | Ai-WB2 | 生态成熟、AT 快上手 |
| 音视频 / 摄像头 / 带屏 | Ai-M61 | 外设最全（Camera/Display/Audio） |
| Wi-Fi 6 低功耗 (电池) | Ai-M64 | 保活 90μA，TWT |
| Wi-Fi 6 均衡低功耗 | Ai-M62 | 多封装、性价比均衡 |
| 双频抗干扰 / Mesh | BW 系列 | 2.4G+5.8G，CSI/Mesh |
| 直连天猫精灵 | TG 系列 | 平台认证 |
| 经典 / 生态最熟 | ESP 系列 | 资料多、社区大 |
