# LLCC68 寄存器参考

> 来源:Semtech DS_LLCC68 V1.0 手册第 12 章(寄存器表)、第 9.2.1(校准)、第 15 章(已知缺陷)。寄存器通过 WriteRegister(0x0D)/ReadRegister(0x1D) 访问,16 位地址。

## 关键寄存器表

| 寄存器 | 地址 | 复位值 | 说明 |
|--------|------|--------|------|
| Whitening 初值 MSB | 0x06B8 | 0xX1 | FSK 白化 LFSR 初值高位(高 7 位不可改) |
| Whitening 初值 LSB | 0x06B9 | 0x00 | FSK 白化 LFSR 初值低位 |
| CRC 初值 MSB | 0x06BC | 0x1D | FSK CRC 多项式初值高位 |
| CRC 初值 LSB | 0x06BD | 0x0F | FSK CRC 多项式初值低位 |
| CRC 多项式 MSB | 0x06BE | 0x10 | FSK CRC 多项式高位 |
| CRC 多项式 LSB | 0x06BF | 0x21 | FSK CRC 多项式低位 |
| SyncWord[0..7] | 0x06C0~0x06C7 | - | FSK 同步字,最多 8 字节 |
| 节点地址 | 0x06CD | 0x00 | FSK 地址过滤节点地址 |
| 广播地址 | 0x06CE | 0x00 | FSK 地址过滤广播地址 |
| IQ 极性 | 0x0736 | 0x0D | **bit2:1=标准 IQ(默认),0=反向 IQ** |
| LoRa 同步字 MSB | 0x0740 | 0x14 | 0x1424=私有网(默认),0x3444=公共网 |
| LoRa 同步字 LSB | 0x0741 | 0x24 | 同上 |
| 随机数 | 0x0819~0x081C | - | 32 位硬件随机数 |
| TxModulation | 0x0889 | 0x01 | **bit2:LoRa BW=500kHz 时写 0,其他配置写 1**(缺陷 workaround) |
| Rx 增益 | 0x08AC | 0x94 | 0x94=省电增益(默认),0x96=Boosted 增益(更灵敏) |
| TxClampConfig | 0x08D8 | 0xC8 | **bits[4:1] 设为 1111(即 0xDE)改善天线失配时的输出功率**(缺陷 workaround) |
| OCP 配置 | 0x08E7 | 0x18(复位 0x38) | 过流保护,步进 2.5mA;SetPaConfig 后会被自动重设,自定义需在其后二次写入 |
| RTC 控制 | 0x0902 | 0x00 | 停 RTC 计时器(隐式头超时 workaround 用) |
| XTA 微调电容 | 0x0911 | 0x05 | 0x00=11.3pF ~ 0x2F=33.4pF,步进 0.47pF;**仅在 STDBY_XOSC 下修改**(状态机入 STDBY_XOSC 会覆盖为 0x12) |
| XTB 微调电容 | 0x0912 | 0x05 | 同 XTA |
| DIO3 输出电压 | 0x0920 | 0x01 | 非标准 DIO3 控制(TCXO 电压) |
| 事件掩码 | 0x0944 | 0x00 | 清事件(隐式头超时 workaround 用) |

## Rx Boosted 增益保留到睡眠(必要时)

默认 0x08AC 不在 warm-start 保留内存中,如需在 SetRxDutyCycle 场景保持 Rx Boosted 增益:

```c
/* 将 0x08AC 加入保留内存:依次写 3 个寄存器 */
llcc68_write_reg(0x029F, (uint8_t[]){0x01}, 1);
llcc68_write_reg(0x02A0, (uint8_t[]){0x08}, 1);
llcc68_write_reg(0x02A1, (uint8_t[]){0xAC}, 1);
```

## PA 最优配置(SetPaConfig 0x95 + SetTxParams 0x8E)

| 目标输出功率 | paDutyCycle | hpMax | deviceSel | paLut | SetTxParams 功率 |
|-------------|-------------|-------|-----------|-------|-----------------|
| +22 dBm | 0x04 | 0x07 | 0x00 | 0x01 | +22 dBm |
| +20 dBm | 0x03 | 0x05 | 0x00 | 0x01 | +22 dBm |
| +17 dBm | 0x02 | 0x03 | 0x00 | 0x01 | +22 dBm |
| +14 dBm | 0x02 | 0x02 | 0x00 | 0x01 | +22 dBm |

> **注意**:
> 1. paDutyCycle 不可高于 0x04,否则功放过压损坏
> 2. 最优配置针对特定匹配网络,需与模组硬件匹配(模组内已固定匹配,按官方推荐使用)
> 3. 使用最优配置后,标称 +22dBm 输出将不可达(功率受限)
> 4. OCP 默认 140mA(0x38),SetPaConfig 会自动重设,需自定义须在其后二次写 0x08E7
> 5. **适用型号**:本表为 LLCC68 芯片手册配置,适用于标准型号 Ra-01SC / Ra-01SCH(+22dBm);**-P 变体(大功率版本,最高 +29dBm)芯片同为 LLCC68、命令层一致,但模组射频前端为大功率设计,功率配置方法以官网设计指导为准**,勿照搬本表

## 镜像校准频段(CalibrateImage 0x98)

| 频段 [MHz] | freq1 | freq2 |
|-----------|-------|-------|
| 430 - 440 | 0x6B | 0x6F |
| 470 - 510 | 0x75 | 0x81 |
| 779 - 787 | 0xC1 | 0xC5 |
| 863 - 870 | 0xD7 | 0xDB |
| 902 - 928 | 0xE1(默认) | 0xE9(默认) |

> 冷启动默认校准 902~928MHz 频段。若使用 TCXO,默认镜像校准会失败,需在 SetDIO3AsTcxoCtrl 后重新发起完整校准。使用 803~930MHz 频段(如 868MHz)时建议显式调用 CalibrateImage(0xD7, 0xDB)。

## 已知缺陷 workaround 汇总(手册第 15 章)

### 1. 500kHz LoRa 带宽调制质量(15.1)

每次发射前设置:

```c
uint8_t val = (lora_bw == 0x06) ? 0x00 : 0x01;  /* 500kHz→0,其余→1 */
/* 读 0x0889,写回 bit2 */
```

### 2. PA 天线失配钳制(15.2)

冷启动(POR/复位)后的初始化阶段执行一次:

```c
/* TxClampConfig: bits[4:1]=1111 */
llcc68_write_reg(0x08D8, (uint8_t[]){0xDE}, 1);
```

### 3. 隐式头模式超时(15.3)

任何带超时的 RX 之后(尤其是隐式头/无头模式):

```c
/* 停 RTC 计数 + 清超时事件 */
llcc68_write_reg(0x0902, (uint8_t[]){0x00}, 1);
llcc68_write_reg(0x0944, (uint8_t[]){0x00}, 1);
```

### 4. 反向 IQ 优化(15.4)

```c
/* 0x0736 bit2: 0=反向IQ, 1=标准IQ */
uint8_t iq = (invert_iq) ? 0x09 : 0x0D;   /* 0x0D 复位值即标准 IQ */
llcc68_write_reg(0x0736, &iq, 1);
```

## 应用笔记

- **AN1200.37**: 最佳性能推荐(PCB 散热设计等)
- **AN1200.48**: CAD 参数(cadDetPeak/cadDetMin)选择指导
- 官网:https://www.semtech.com/products/wireless-rf/lora-connect/llcc68
