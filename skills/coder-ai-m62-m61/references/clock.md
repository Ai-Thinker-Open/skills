# BL616/BL618 Clock API Documentation

## Overview

This document describes the clock system API for BL616/BL618 chips. The Global Block (GLB) manages clock distribution and peripheral clock gating.

**Base Address:** `GLB_BASE = 0x20000000`

---

## Clock Register Map (CGEN Registers)

| Register | Offset | Description |
|----------|--------|-------------|
| `GLB_CGEN_CFG0` | `0x580` | Clock gate for master peripherals (CPU, SDU, SEC, DMA, CCI) |
| `GLB_CGEN_CFG1` | `0x584` | Clock gate for slave peripherals (UART0-2, SPI, I2C0-1, PWM, Timer, IR, CKS, DBI, etc.) |
| `GLB_CGEN_CFG2` | `0x588` | Clock gate for external peripherals (USB, Audio, SDH, EMAC, WiFi, BT/BLE, etc.) |
| `GLB_CGEN_CFG3` | `0x58C` | Clock gate for PLL domains (ISP, TOP) |

---

## System Clock Types

```c
typedef enum {
    BL_SYSTEM_CLOCK_MCU_ROOT_CLK,  // MCU root clock
    BL_SYSTEM_CLOCK_MCU_CLK,       // MCU Fast clock/CPU clock
    BL_SYSTEM_CLOCK_MCU_BCLK,      // MCU BUS clock
    BL_SYSTEM_CLOCK_MCU_PBCLK,     // MCU peripheral BUS clock
    BL_SYSTEM_CLOCK_F32K,          // F32K clock
    BL_SYSTEM_CLOCK_XCLK,          // XCLK: RC32M or XTAL
    BL_SYSTEM_CLOCK_XTAL,          // XTAL clock
    BL_SYSTEM_CLOCK_MAX,
} BL_System_Clock_Type;
```

### System Clock Definitions

| Constant | Value | Description |
|----------|-------|-------------|
| `BFLB_SYSTEM_ROOT_CLOCK` | 0 | Root clock |
| `BFLB_SYSTEM_CPU_CLK` | 1 | CPU clock |
| `BFLB_SYSTEM_PBCLK` | 2 | Peripheral bus clock |
| `BFLB_SYSTEM_XCLK` | 3 | External clock |
| `BFLB_SYSTEM_32K_CLK` | 4 | 32KHz clock |

---

## Peripheral Clock Type Definitions

```c
typedef enum {
    BL_PERIPHERAL_CLOCK_UART0,     // UART0 clock
    BL_PERIPHERAL_CLOCK_UART1,     // UART1 clock
    BL_PERIPHERAL_CLOCK_UART2,     // UART2 clock
    BL_PERIPHERAL_CLOCK_SPI,       // SPI clock
    BL_PERIPHERAL_CLOCK_RESERVED,  // reserved
    BL_PERIPHERAL_CLOCK_DBI,       // DBI clock
    BL_PERIPHERAL_CLOCK_EMI,       // EMI clock
    BL_PERIPHERAL_CLOCK_I2C0,      // I2C0 clock
    BL_PERIPHERAL_CLOCK_I2C1,      // I2C1 clock
    BL_PERIPHERAL_CLOCK_PSRAMB,    // PSRAMB clock
    BL_PERIPHERAL_CLOCK_FLASH,     // FLASH clock
    BL_PERIPHERAL_CLOCK_I2S,       // I2S clock
    BL_PERIPHERAL_CLOCK_IR,        // IR clock
    BL_PERIPHERAL_CLOCK_ADC,       // ADC clock
    BL_PERIPHERAL_CLOCK_GPADC,     // GPADC clock
    BL_PERIPHERAL_CLOCK_GPDAC,     // GPDAC clock
    BL_PERIPHERAL_CLOCK_CAM_REF,   // CAM_REF clock
    BL_PERIPHERAL_CLOCK_CAM,       // CAM clock
    BL_PERIPHERAL_CLOCK_SDH,       // SDH clock
    BL_PERIPHERAL_CLOCK_SEC_PKA,   // PKA clock
    BL_PERIPHERAL_CLOCK_RTC,       // RTC clock
    BL_PERIPHERAL_CLOCK_MAX,
} BL_Peripheral_Type;
```

---

## PLL Clock Types

```c
typedef enum {
    CLOCK_AUPLL_DIV1,    // AUPLL / 1
    CLOCK_AUPLL_DIV2,    // AUPLL / 2
    CLOCK_AUPLL_DIV2P5,  // AUPLL / 2.5
    CLOCK_AUPLL_DIV3,    // AUPLL / 3
    CLOCK_AUPLL_DIV4,    // AUPLL / 4
    CLOCK_AUPLL_DIV5,    // AUPLL / 5
    CLOCK_AUPLL_DIV6,    // AUPLL / 6
    CLOCK_AUPLL_DIV10,   // AUPLL / 10
    CLOCK_AUPLL_DIV15,   // AUPLL / 15
} CLOCK_AUPLL_Type;
```

---

## Clock Source Selection Definitions

### MCU System Clock

| Constant | Value | Description |
|----------|-------|-------------|
| `GLB_MCU_SYS_CLK_RC32M` | 0 | Use RC32M as system clock |
| `GLB_MCU_SYS_CLK_XTAL` | 1 | Use XTAL as system clock |
| `GLB_MCU_SYS_CLK_TOP_AUPLL_DIV2` | 2 | Use TOP_AUPLL_DIV2 as system clock |
| `GLB_MCU_SYS_CLK_TOP_AUPLL_DIV1` | 3 | Use TOP_AUPLL_DIV1 as system clock |
| `GLB_MCU_SYS_CLK_TOP_WIFIPLL_240M` | 4 | Use TOP_WIFIPLL_240M as system clock |
| `GLB_MCU_SYS_CLK_TOP_WIFIPLL_320M` | 5 | Use TOP_WIFIPLL_320M as system clock |

### MCU MUXPLL 160M Clock

| Constant | Value | Description |
|----------|-------|-------------|
| `GLB_MCU_MUXPLL_SEL_WIFIPLL_160M` | 0 | Select WIFIPLL 160M |
| `GLB_MCU_MUXPLL_SEL_AUPLL_DIV3` | 1 | Select AUPLL_DIV3 |
| `GLB_MCU_MUXPLL_SEL_TOP_AUPLL_DIV2` | 2 | Select TOP_AUPLL_DIV2 |
| `GLB_MCU_MUXPLL_SEL_AUPLL_DIV2P5` | 3 | Select AUPLL_DIV2P5 |

### MCU MUXPLL 80M Clock

| Constant | Value | Description |
|----------|-------|-------------|
| `GLB_MCU_MUXPLL_SEL_WIFIPLL_80M` | 0 | Select WIFIPLL 80M |
| `GLB_MCU_MUXPLL_SEL_TOP_AUPLL_DIV5` | 1 | Select TOP_AUPLL_DIV5 |
| `GLB_MCU_MUXPLL_SEL_TOP_AUPLL_DIV6` | 2 | Select TOP_AUPLL_DIV6 |

### PLL Reference Clock

| Constant | Value | Description |
|----------|-------|-------------|
| `GLB_PLL_REFCLK_XTAL` | 0 | Use XTAL as PLL reference |
| `GLB_PLL_REFCLK_RC32M` | 3 | Use RC32M as PLL reference |

### UART Clock

| Constant | Value | Description |
|----------|-------|-------------|
| `GLB_UART_CLK_BCLK` | 0 | Select bclk as UART clock |
| `GLB_UART_CLK_PLL_160M` | 1 | Select PLL 160M as UART clock |

### SPI Clock

| Constant | Value | Description |
|----------|-------|-------------|
| `GLB_SPI_CLK_MCU_MUXPLL_160M` | 0 | Select MCU MUXPLL 160M as SPI clock |
| `GLB_SPI_CLK_XCLK` | 1 | Select xclk as SPI clock |

### I2C Clock

| Constant | Value | Description |
|----------|-------|-------------|
| `GLB_I2C_CLK_BCLK` | 0 | Select bus clk as I2C clock |
| `GLB_I2C_CLK_XCLK` | 1 | Select xclk as I2C clock |

---

## CGEN Register Bit Definitions

### GLB_CGEN_CFG0 (0x580) - Master Clock Enable

| Bit | Name | Description |
|-----|------|-------------|
| 0 | `GLB_CGEN_M_CPU` | CPU clock enable |
| 1 | `GLB_CGEN_M_SDU` | SDU clock enable |
| 2 | `GLB_CGEN_M_SEC` | Security engine clock enable |
| 3 | `GLB_CGEN_M_DMA` | DMA clock enable |
| 4 | `GLB_CGEN_M_CCI` | CCI clock enable |

### GLB_CGEN_CFG1 (0x584) - Slave1 Clock Enable

| Bit | Name | Description |
|-----|------|-------------|
| 2 | `GLB_CGEN_S1_GPIP` | GPIP clock enable |
| 3 | `GLB_CGEN_S1_SEC_DBG` | SEC_DBG clock enable |
| 4 | `GLB_CGEN_S1_SEC_ENG` | SEC_ENG clock enable |
| 5 | `GLB_CGEN_S1_TZ` | TZ clock enable |
| 7 | `GLB_CGEN_S1_EF_CTRL` | EF_CTRL clock enable |
| 11 | `GLB_CGEN_S1_SF_CTRL` | SF_CTRL clock enable |
| 12 | `GLB_CGEN_S1_DMA` | DMA clock enable |
| 16 | `GLB_CGEN_S1A_UART0` | UART0 clock enable |
| 17 | `GLB_CGEN_S1A_UART1` | UART1 clock enable |
| 18 | `GLB_CGEN_S1A_SPI` | SPI clock enable |
| 19 | `GLB_CGEN_S1A_I2C` | I2C0 clock enable |
| 20 | `GLB_CGEN_S1A_PWM` | PWM clock enable |
| 21 | `GLB_CGEN_S1A_TIMER` | Timer clock enable |
| 22 | `GLB_CGEN_S1A_IR` | IR clock enable |
| 23 | `GLB_CGEN_S1A_CKS` | CKS clock enable |
| 24 | `GLB_CGEN_S1A_DBI` | DBI clock enable |
| 25 | `GLB_CGEN_S1A_I2C1` | I2C1 clock enable |

### GLB_CGEN_CFG2 (0x588) - Slave2/External Clock Enable

| Bit | Name | Description |
|-----|------|-------------|
| 4 | `GLB_CGEN_S2_WIFI` | WiFi clock enable |
| 10 | `GLB_CGEN_S3_BT_BLE2` | BT_BLE2 clock enable |
| 11 | `GLB_CGEN_S3_M1542` | M1542 clock enable |
| 16 | `GLB_CGEN_S1_EXT_EMI_MISC` | EMI_MISC clock enable |
| 17 | `GLB_CGEN_S1_EXT_PSRAM0_CTRL` | PSRAM0_CTRL clock enable |
| 18 | `GLB_CGEN_S1_EXT_PSRAM_CTRL` | PSRAM_CTRL clock enable |
| 19 | `GLB_CGEN_S1_EXT_USB` | USB clock enable |
| 20 | `GLB_CGEN_S1_EXT_MIX2` | MIX2 clock enable |
| 21 | `GLB_CGEN_S1_EXT_AUDIO` | Audio clock enable |
| 22 | `GLB_CGEN_S1_EXT_SDH` | SDH clock enable |
| 23 | `GLB_CGEN_S1_EXT_EMAC` | EMAC clock enable |
| 24 | `GLB_CGEN_S1_EXT_DMA2` | DMA2 clock enable |
| 25 | `GLB_CGEN_S1_EXT_PIO` | PIO clock enable |

---

## API Functions

### LHAL Clock API (bflb_clock.h)

```c
/**
 * @brief Enable/disable peripheral clock
 * @param peri: Peripheral ID (BFLB_PERIPHERAL_xxx)
 * @param enable: true to enable, false to disable
 * @return 0 on success, error code on failure
 */
int bflb_peripheral_clock_control(uint8_t peri, bool enable);

/**
 * @brief Get peripheral clock frequency
 * @param peri: Peripheral ID (BFLB_PERIPHERAL_xxx)
 * @return Clock frequency in Hz
 */
uint32_t bflb_peripheral_clock_get(uint8_t peri);

/**
 * @brief Get peripheral clock status
 * @param peri: Peripheral ID (BFLB_PERIPHERAL_xxx)
 * @return 1 if enabled, 0 if disabled
 */
int bflb_peripheral_clock_status_get(uint8_t peri);

/**
 * @brief Get system clock frequency
 * @param type: System clock type (BL_System_Clock_Type)
 * @return Clock frequency in Hz
 */
uint32_t bflb_clk_get_system_clock(uint8_t type);

/**
 * @brief Get peripheral clock frequency
 * @param type: Peripheral type
 * @param idx: Peripheral index
 * @return Clock frequency in Hz
 */
uint32_t bflb_clk_get_peripheral_clock(uint8_t type, uint8_t idx);
```

### SOC Clock API (bl616_clock.h)

```c
/**
 * @brief Get system clock frequency
 * @param type: System clock type
 * @return Clock frequency in Hz
 */
uint32_t Clock_System_Clock_Get(BL_System_Clock_Type type);

/**
 * @brief Get peripheral clock frequency
 * @param type: Peripheral type
 * @return Clock frequency in Hz
 */
uint32_t Clock_Peripheral_Clock_Get(BL_Peripheral_Type type);

/**
 * @brief Get Audio ADC clock frequency
 * @return Clock frequency in Hz
 */
uint32_t Clock_Audio_ADC_Clock_Get(void);

/**
 * @brief Get Audio DAC clock frequency
 * @return Clock frequency in Hz
 */
uint32_t Clock_Audio_DAC_Clock_Get(void);

/**
 * @brief Get current CPU core clock
 * @return CPU core clock frequency in Hz
 */
uint32_t SystemCoreClockGet(void);

/**
 * @brief Set MCU timer reset
 * @param rstEn: Reset enable
 * @return Error status
 */
BL_Err_Type CPU_Set_MTimer_RST(uint8_t rstEn);

/**
 * @brief Reset MCU timer
 * @return Error status
 */
BL_Err_Type CPU_Reset_MTimer(void);

/**
 * @brief Set MCU timer clock
 * @param enable: Clock enable
 * @param mTimerSourceClockType: Source clock type
 * @param div: Divider value
 * @return Error status
 */
BL_Err_Type CPU_Set_MTimer_CLK(uint8_t enable, 
                                BL_MTimer_Source_Clock_Type mTimerSourceClockType, 
                                uint16_t div);

/**
 * @brief Get MCU timer source clock
 * @return Source clock frequency in Hz
 */
uint32_t CPU_Get_MTimer_Source_Clock(void);

/**
 * @brief Get MCU timer clock
 * @return Timer clock frequency in Hz
 */
uint32_t CPU_Get_MTimer_Clock(void);

/**
 * @brief Get MCU timer counter
 * @return Timer counter value
 */
uint64_t CPU_Get_MTimer_Counter(void);

/**
 * @brief Get CPU cycle count
 * @return CPU cycle count
 */
uint64_t CPU_Get_CPU_Cycle(void);

/**
 * @brief Get MCU timer value in microseconds
 * @return Microseconds value
 */
uint64_t CPU_Get_MTimer_US(void);

/**
 * @brief Get MCU timer value in milliseconds
 * @return Milliseconds value
 */
uint64_t CPU_Get_MTimer_MS(void);

/**
 * @brief Microsecond delay
 * @param cnt: Microseconds to delay
 * @return Error status
 */
BL_Err_Type CPU_MTimer_Delay_US(uint32_t cnt);

/**
 * @brief Millisecond delay
 * @param cnt: Milliseconds to delay
 * @return Error status
 */
BL_Err_Type CPU_MTimer_Delay_MS(uint32_t cnt);

/**
 * @brief Get EMI clock frequency
 * @return EMI clock frequency in Hz
 */
uint32_t Clock_Get_EMI_Clk(void);

/**
 * @brief Get BLAI clock frequency
 * @return BLAI clock frequency in Hz
 */
uint32_t Clock_Get_BLAI_Clk(void);

/**
 * @brief Get Display clock frequency
 * @return Display clock frequency in Hz
 */
uint32_t Clock_Get_Display_Clk(void);

/**
 * @brief Get PSRAMB clock frequency
 * @return PSRAMB clock frequency in Hz
 */
uint32_t Clock_Get_PSRAMB_Clk(void);

/**
 * @brief Get H264 clock frequency
 * @return H264 clock frequency in Hz
 */
uint32_t Clock_Get_H264_Clk(void);

/**
 * @brief Get peripheral clock by ID
 * @param peri: Peripheral ID
 * @return Clock frequency in Hz
 */
uint32_t bflb_peripheral_clock_get_by_id(uint8_t peri);

/**
 * @brief Control peripheral clock by ID
 * @param peri: Peripheral ID
 * @param enable: Enable/disable flag
 * @return Error status
 */
int bflb_peripheral_clock_control_by_id(uint8_t peri, bool enable);

/**
 * @brief Get peripheral clock status by ID
 * @param peri: Peripheral ID
 * @return Clock status (1=enabled, 0=disabled)
 */
int bflb_peripheral_clock_status_get_by_id(uint8_t peri);
```

---

## Peripheral Clock Enable Macros

These macros directly manipulate the CGEN registers to enable peripheral clocks:

```c
// ADC/DAC Clock Enable
PERIPHERAL_CLOCK_ADC_DAC_ENABLE()

// Security Engine Clock Enable
PERIPHERAL_CLOCK_SEC_ENABLE()

// DMA0 Clock Enable
PERIPHERAL_CLOCK_DMA0_ENABLE()

// UART0 Clock Enable
PERIPHERAL_CLOCK_UART0_ENABLE()

// UART1 Clock Enable
PERIPHERAL_CLOCK_UART1_ENABLE()

// SPI0 Clock Enable
PERIPHERAL_CLOCK_SPI0_ENABLE()

// I2C0 Clock Enable
PERIPHERAL_CLOCK_I2C0_ENABLE()

// I2C1 Clock Enable (BL616/BL616CL/BL618DG)
PERIPHERAL_CLOCK_I2C1_ENABLE()

// PWM0 Clock Enable
PERIPHERAL_CLOCK_PWM0_ENABLE()

// Timer0/Timer1/WDG Clock Enable
PERIPHERAL_CLOCK_TIMER0_1_WDG_ENABLE()

// IR Clock Enable
PERIPHERAL_CLOCK_IR_ENABLE()

// CKS Clock Enable
PERIPHERAL_CLOCK_CKS_ENABLE()

// CAN Clock Enable (BL616/BL616CL/BL618DG)
PERIPHERAL_CLOCK_CAN_ENABLE()

// USB Clock Enable
PERIPHERAL_CLOCK_USB_ENABLE()

// I2S Clock Enable (BL616/BL616CL/BL618DG)
PERIPHERAL_CLOCK_I2S_ENABLE()

// SDH Clock Enable (BL616/BL616CL/BL618DG)
PERIPHERAL_CLOCK_SDH_ENABLE()

// EMAC Clock Enable (BL616/BL616CL/BL618DG)
PERIPHERAL_CLOCK_EMAC_ENABLE()

// Audio Clock Enable (BL616/BL616CL)
PERIPHERAL_CLOCK_AUDIO_ENABLE()

// DBI Clock Enable (BL616/BL616CL)
PERIPHERAL_CLOCK_DBI_ENABLE()

// PEC Clock Enable (BL618DG/BL616CL)
PERIPHERAL_CLOCK_PEC_ENABLE()
```

### Example Implementation

```c
#define PERIPHERAL_CLOCK_UART0_ENABLE()                           \
    do {                                                          \
        volatile uint32_t regval = getreg32(BFLB_GLB_CGEN1_BASE); \
        regval |= (1 << 16);                                      \
        putreg32(regval, BFLB_GLB_CGEN1_BASE);                    \
    } while (0)
```

Where:
- `BFLB_GLB_CGEN1_BASE = GLB_BASE + 0x584 = 0x20000584`
- Bit 16 in CGEN1 corresponds to UART0

---

## Clock Tree Summary

```
                    +-----------------+
                    |    XTAL/RC32M   |
                    +--------+--------+
                             |
                             v
                    +-----------------+
                    |   Root Clock    |
                    | (XCLK or PLL)   |
                    +--------+--------+
                             |
           +-----------------+-----------------+
           |                 |                 |
           v                 v                 v
    +------------+    +------------+    +------------+
    | MCU_ROOT   |    |  F32K      |    | XCLK       |
    | (CPU CLK)  |    | (32.768KHz)|    | (RC/XTAL)  |
    +-----+------+    +------------+    +------------+
          |
          v
    +-----------------+
    |  HCLK Divider   |
    | (System Clock)  |
    +--------+--------+
          |
          v
    +-----------------+
    |  PBCLK Divider  |
    | (Peripheral)    |
    +-----------------+

PLL Sources:
- WIFIPLL: 480MHz (for WiFi)
- AUPLL: ~491MHz (for Audio)
```

---

## Usage Examples

### Example 1: Enable UART0 Clock and Get Clock Frequency

```c
#include "bflb_clock.h"

// Enable UART0 peripheral clock
bflb_peripheral_clock_control(BL_PERIPHERAL_CLOCK_UART0, true);

// Get UART0 clock frequency
uint32_t uart0_freq = bflb_peripheral_clock_get(BL_PERIPHERAL_CLOCK_UART0);

// Check if clock is enabled
int status = bflb_peripheral_clock_status_get(BL_PERIPHERAL_CLOCK_UART0);
```

### Example 2: Get System Clock Frequencies

```c
#include "bl616_clock.h"

// Get CPU core clock (e.g., 120MHz)
uint32_t cpu_clk = Clock_System_Clock_Get(BL_SYSTEM_CLOCK_MCU_CLK);

// Get peripheral bus clock
uint32_t pb_clk = Clock_System_Clock_Get(BL_SYSTEM_CLOCK_MCU_PBCLK);

// Get 32K clock
uint32_t f32k = Clock_System_Clock_Get(BL_SYSTEM_CLOCK_F32K);

// Get current SystemCoreClock
uint32_t core_clk = SystemCoreClockGet();
```

### Example 3: Microsecond Delay

```c
#include "bl616_clock.h"

// Initialize timer if needed
CPU_Set_MTimer_CLK(1, BL_MTIMER_SOURCE_CLOCK_MCU_CLK, 0);

// Delay 1 second
CPU_MTimer_Delay_MS(1000);

// Delay 500 microseconds
CPU_MTimer_Delay_US(500);
```

### Example 4: Direct Register Access for Clock Enable

```c
#include "bflb_clock.h"

// Direct register access to enable SPI clock
volatile uint32_t *cgen1 = (volatile uint32_t *)(GLB_BASE + 0x584);
*cgen1 |= (1 << 18);  // Enable SPI (bit 18)

// Or use the macro
PERIPHERAL_CLOCK_SPI0_ENABLE();
```

### Example 5: Configure UART Clock Source

```c
// UART can use bclk or PLL_160M
// Default is bclk (peripheral bus clock)
// To switch to PLL_160M, configure GLB_UART_CFG0

volatile uint32_t *uart_cfg0 = (volatile uint32_t *)(GLB_BASE + 0x150);
uint32_t val = *uart_cfg0;
val &= ~(0x1 << 7);  // Clear HBN_UART_CLK_SEL
val |= (0x1 << 22);  // Set HBN_UART_CLK_SEL2
*uart_cfg0 = val;
```

---

## XTAL Type Definitions

```c
#define GLB_XTAL_NONE     0   // No XTAL
#define GLB_XTAL_24M      1   // 24 MHz
#define GLB_XTAL_32M      2   // 32 MHz
#define GLB_XTAL_38P4M    3   // 38.4 MHz
#define GLB_XTAL_40M      4   // 40 MHz
#define GLB_XTAL_26M      5   // 26 MHz
#define GLB_XTAL_RC32M    6   // RC32M (32 MHz internal)
```

---

## PLL Power Control

```c
#define GLB_PLL_NONE      0   // Power on XTAL and PLL
#define GLB_PLL_WIFIPLL   1   // Power on WIFIPLL
#define GLB_PLL_AUPLL     2   // Power on AUPLL
```

---

## Clock Configuration Magic Number

```c
#define SYS_CLOCK_CFG_MAGIC  0x12345678
#define SYS_CLOCK_CFG_ADDR   (0x20010000 + 4 * 1024 - 512)
```

This is used for storing clock configuration in retention RAM across power cycles.
