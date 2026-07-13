# HBN (Hibernate) and PDS (Power Down Sleep) API Reference

> Source files:  
> `components/platform/soc/bl602/bl602_std/bl602_std/StdDriver/Inc/bl602_hbn.h`  
> `components/platform/soc/bl602/bl602_std/bl602_std/StdDriver/Inc/bl602_pds.h`  
> `components/platform/hosal/bl602_hal/bl_hbn.h` (HOSAL wrapper)  
> `components/platform/hosal/bl602_hal/bl_pds.h` (HOSAL wrapper)  
> BL602 power management — HBN (deepest sleep with RTC backup) and PDS (flexible power-down sleep).

---

## Overview

BL602 provides two main sleep modes:

- **HBN (Hibernate)**: Deepest sleep. Most of the chip is powered off; only RTC domain and AON (always-on) registers remain powered. Used for ultra-low-power standby. Wakeup via GPIO, RTC, PIR, BOR, or ACOMP.
- **PDS (Power Down Sleep)**: Intermediate sleep. More power savings than idle but faster wakeup than HBN. PLL and flash can be optionally kept powered.

---

## Header Files

```c
// Standard driver (register-level)
#include "bl602_hbn.h"
#include "bl602_pds.h"

// HOSAL wrapper (simplified API)
#include "bl_hbn.h"
#include "bl_pds.h"
```

---

## HBN Types

### HBN Level

```c
typedef enum {
    HBN_LEVEL_0,  // pd_core powered down
    HBN_LEVEL_1,  // pd_aon_hbncore + pd_core
    HBN_LEVEL_2,  // pd_aon_hbnrtc + pd_aon_hbncore + pd_core
    HBN_LEVEL_3,  // same as LEVEL_2
} HBN_LEVEL_Type;
```

### HBN LDO Voltage

```c
typedef enum {
    HBN_LDO_LEVEL_0P60V = 0,
    HBN_LDO_LEVEL_0P65V = 1,
    HBN_LDO_LEVEL_0P70V = 2,
    HBN_LDO_LEVEL_0P75V = 3,
    HBN_LDO_LEVEL_0P80V = 4,
    HBN_LDO_LEVEL_0P85V = 5,
    HBN_LDO_LEVEL_0P90V = 6,
    HBN_LDO_LEVEL_0P95V = 7,
    HBN_LDO_LEVEL_1P00V = 8,
    HBN_LDO_LEVEL_1P05V = 9,
    HBN_LDO_LEVEL_1P10V = 10,
    HBN_LDO_LEVEL_1P15V = 11,
    HBN_LDO_LEVEL_1P20V = 12,
    HBN_LDO_LEVEL_1P25V = 13,
    HBN_LDO_LEVEL_1P30V = 14,
    HBN_LDO_LEVEL_1P35V = 15,
} HBN_LDO_LEVEL_Type;
```

### HBN 32K Clock Source

```c
typedef enum {
    HBN_32K_RC   = 0,   // Internal RC32K (less accurate, faster startup)
    HBN_32K_XTAL = 1,   // External 32K crystal (accurate, slower startup)
    HBN_32K_DIG  = 2,   // Digital 32K source
} HBN_32K_CLK_Type;
```

### HBN Interrupt Source

```c
typedef enum {
    HBN_INT_GPIO7 = 0,
    HBN_INT_GPIO8 = 1,
    HBN_INT_RTC   = 2,
    HBN_INT_PIR   = 3,
    HBN_INT_BOR   = 4,
    HBN_INT_ACOMP0 = 5,
    HBN_INT_ACOMP1 = 6,
} HBN_INT_Type;
```

### HBN GPIO Trigger Type

```c
typedef enum {
    HBN_GPIO_INT_TRIGGER_SYNC_FALLING_EDGE,
    HBN_GPIO_INT_TRIGGER_SYNC_RISING_EDGE,
    HBN_GPIO_INT_TRIGGER_SYNC_LOW_LEVEL,
    HBN_GPIO_INT_TRIGGER_SYNC_HIGH_LEVEL,
    HBN_GPIO_INT_TRIGGER_ASYNC_FALLING_EDGE,
    HBN_GPIO_INT_TRIGGER_ASYNC_RISING_EDGE,
    HBN_GPIO_INT_TRIGGER_ASYNC_LOW_LEVEL,
    HBN_GPIO_INT_TRIGGER_ASYNC_HIGH_LEVEL,
} HBN_GPIO_INT_Trigger_Type;
```

### HBN_APP_CFG_Type

```c
typedef struct {
    uint8_t useXtal32k;                      // 1=use XTAL 32K, 0=use RC32K
    uint32_t sleepTime;                       // Sleep duration
    uint8_t gpioWakeupSrc;                   // GPIO wakeup source
    HBN_GPIO_INT_Trigger_Type gpioTrigType;  // GPIO trigger type
    SPI_Flash_Cfg_Type *flashCfg;           // Flash config (for flash power-down)
    HBN_LEVEL_Type hbnLevel;                // HBN sleep level
    HBN_LDO_LEVEL_Type ldoLevel;            // LDO voltage level
} HBN_APP_CFG_Type;
```

---

## PDS Types

### PDS LDO Voltage

```c
typedef enum {
    PDS_LDO_LEVEL_0P60V = 0,
    PDS_LDO_LEVEL_0P65V = 1,
    // ... same range as HBN_LDO_LEVEL, up to 1.35V
    PDS_LDO_LEVEL_1P35V = 15,
} PDS_LDO_LEVEL_Type;
```

### PDS PLL Output Clock

```c
typedef enum {
    PDS_PLL_CLK_480M,
    PDS_PLL_CLK_240M,
    PDS_PLL_CLK_192M,
    PDS_PLL_CLK_160M,
    PDS_PLL_CLK_120M,
    PDS_PLL_CLK_96M,
    PDS_PLL_CLK_80M,
    PDS_PLL_CLK_48M,
    PDS_PLL_CLK_32M,
} PDS_PLL_CLK_Type;
```

### PDS_APP_CFG_Type

```c
typedef struct {
    uint8_t pdsLevel;                         // PDS sleep level
    uint8_t turnOffRF;                        // 1=turn off RF
    uint8_t useXtal32k;                       // 1=use XTAL 32K
    uint8_t pdsAonGpioWakeupSrc;             // AON GPIO wakeup source
    PDS_AON_GPIO_INT_Trigger_Type pdsAonGpioTrigType;
    uint8_t powerDownFlash;                   // 1=power down flash
    uint8_t turnOffFlashPad;
    uint8_t ocramRetetion;
    uint8_t turnoffPLL;
    uint8_t xtalType;
    uint8_t flashContRead;
    uint32_t sleepTime;
    SPI_Flash_Cfg_Type *flashCfg;
    PDS_LDO_LEVEL_Type ldoLevel;
    void (*preCbFun)(void);                   // Pre-sleep callback
    void (*postCbFun)(void);                  // Post-wakeup callback
} PDS_APP_CFG_Type;
```

---

## HBN Functions

### `HBN_Mode_Enter`

Enter HBN (hibernate) mode.

```c
void HBN_Mode_Enter(HBN_APP_CFG_Type *cfg);
```

### `HBN_Enable`

Enable HBN with specified level and LDO voltage.

```c
void HBN_Enable(uint8_t aGPIOIeCfg, HBN_LDO_LEVEL_Type ldoLevel, HBN_LEVEL_Type hbnLevel);
```

### `HBN_Disable`

Disable HBN and wake up.

```c
BL_Err_Type HBN_Disable(void);
```

### `HBN_Reset`

Reset the system from HBN.

```c
BL_Err_Type HBN_Reset(void);
```

### `HBN_32K_Sel`

Select 32K clock source.

```c
BL_Err_Type HBN_32K_Sel(HBN_32K_CLK_Type clkType);
```

### `HBN_Set_RTC_Timer`

Set RTC timer for timed wakeup.

```c
BL_Err_Type HBN_Set_RTC_Timer(HBN_RTC_INT_Delay_Type delay,
                               uint32_t compValLow, uint32_t compValHigh,
                               uint8_t compMode);
```

### `HBN_GPIO_INT_Enable`

Enable GPIO wakeup interrupt.

```c
BL_Err_Type HBN_GPIO_INT_Enable(HBN_GPIO_INT_Trigger_Type gpioIntTrigType);
```

### `HBN_GPIO_INT_Disable`

Disable GPIO wakeup interrupt.

```c
BL_Err_Type HBN_GPIO_INT_Disable(void);
```

### `HBN_Clear_IRQ`

Clear HBN interrupt flag.

```c
BL_Err_Type HBN_Clear_IRQ(HBN_INT_Type irqType);
```

### `HBN_Out0_Callback_Install`

Install callback for HBN_OUT0 interrupt (GPIO7 or GPIO8 or RTC).

```c
BL_Err_Type HBN_Out0_Callback_Install(HBN_OUT0_INT_Type intType, intCallback_Type *cbFun);
```

### `HBN_Out1_Callback_Install`

Install callback for HBN_OUT1 interrupt (PIR, BOR, ACOMP0, ACOMP1).

```c
BL_Err_Type HBN_Out1_Callback_Install(HBN_OUT1_INT_Type intType, intCallback_Type *cbFun);
```

### `HBN_Power_On_Xtal_32K` / `HBN_Power_Off_Xtal_32K`

Manually control 32K crystal power.

```c
BL_Err_Type HBN_Power_On_Xtal_32K(void);
BL_Err_Type HBN_Power_Off_Xtal_32K(void);
```

---

## PDS Functions

### `PDS_Enable`

Enter PDS mode with full configuration.

```c
BL_Err_Type PDS_Enable(PDS_CTL_Type *cfg, PDS_CTL4_Type *cfg4, uint32_t pdsSleepCnt);
```

### `PDS_Default_Level_Config`

Configure and enter PDS at a specific level.

```c
BL_Err_Type PDS_Default_Level_Config(PDS_DEFAULT_LV_CFG_Type *defaultLvCfg,
                                      PDS_RAM_CFG_Type *ramCfg,
                                      uint32_t pdsSleepCnt);
```

### `PDS_RAM_Config`

Configure which RAM blocks to retain in PDS.

```c
BL_Err_Type PDS_RAM_Config(PDS_RAM_CFG_Type *ramCfg);
```

### `PDS_Reset`

Reset system from PDS.

```c
BL_Err_Type PDS_Reset(void);
```

### `PDS_Int_Callback_Install`

Install callback for PDS wakeup interrupt.

```c
BL_Err_Type PDS_Int_Callback_Install(PDS_INT_Type intType, intCallback_Type *cbFun);
```

### `PDS_Power_On_PLL` / `PDS_Power_Off_PLL`

Manually control PLL power in PDS.

```c
BL_Err_Type PDS_Power_On_PLL(PDS_PLL_XTAL_Type xtalType);
BL_Err_Type PDS_Power_Off_PLL(void);
```

### `PDS_Enable_PLL_Clk` / `PDS_Disable_PLL_Clk`

Enable or disable specific PLL output clocks.

```c
BL_Err_Type PDS_Enable_PLL_Clk(PDS_PLL_CLK_Type pllClk);
BL_Err_Type PDS_Disable_PLL_Clk(PDS_PLL_CLK_Type pllClk);
```

---

## HOSAL Wrapper Functions

### `bl_hbn_enter`

Enter HBN via HOSAL wrapper.

```c
int bl_hbn_enter(hbn_type_t *hbn, uint32_t *time);
```

### `bl_pds_init`

Initialize PDS.

```c
void bl_pds_init(void);
```

### `bl_pds_enter`

Enter PDS at a specific level.

```c
void bl_pds_enter(uint32_t pdsLevel, uint32_t pdsSleepCycles);
```

### `bl_pds_rf_turnon` / `bl_pds_rf_turnoff`

Control RF state in PDS.

```c
int bl_pds_rf_turnon(void *arg);
int bl_pds_rf_turnoff(void *arg);
```

---

## Usage Example

### HBN GPIO Wakeup

```c
#include "bl602_hbn.h"

void hbn_gpio_wakeup_example(void)
{
    HBN_APP_CFG_Type cfg = {
        .useXtal32k = 1,
        .sleepTime = 0,
        .gpioWakeupSrc = HBN_WAKEUP_GPIO_7,
        .gpioTrigType = HBN_GPIO_INT_TRIGGER_RISING_EDGE,
        .flashCfg = NULL,
        .hbnLevel = HBN_LEVEL_0,
        .ldoLevel = HBN_LDO_LEVEL_1P00V,
    };

    HBN_Mode_Enter(&cfg);
}
```

### PDS with RF Off

```c
#include "bl602_pds.h"

void pds_rf_off_example(void)
{
    PDS_APP_CFG_Type cfg = {
        .pdsLevel = 1,
        .turnOffRF = 1,
        .useXtal32k = 1,
        .powerDownFlash = 0,
        .turnoffPLL = 1,
        .sleepTime = 1000,
        .ldoLevel = PDS_LDO_LEVEL_0P90V,
    };

    PDS_Default_Level_Config(NULL, NULL, cfg.sleepTime);
}
```
