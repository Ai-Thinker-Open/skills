# BL616/BL618 Reset API Documentation

## Overview

The Reset module provides peripheral and system reset functionality for BL616/BL618 chips. It is part of the LHAL (Low-Level Hardware Abstraction Layer) and is built on top of the GLB (Global) registers.

**Header File:** `drivers/lhal/include/bflb_reset.h`

---

## Include Files

```c
#include "bflb_reset.h"
```

---

## Function Signatures

### LHAL API (Public)

```c
/**
 * @brief  Reset a peripheral
 *
 * @param  peri: BFLB_PERIPHERAL_xxx (peripheral ID)
 * @return int  - 0 on success, -1 on invalid peripheral
 *
 * @note   This is the main public API for resetting peripherals.
 *         Internally calls bflb_peripheral_reset_by_id()
 */
int bflb_peripheral_reset(uint8_t peri);
```

### Chip-Specific API (Internal)

```c
/**
 * @brief  Reset peripheral by ID
 *
 * @param  peri: BFLB_PERIPHERAL_xxx (peripheral ID)
 * @return int  - 0 on success, -1 on invalid peripheral
 *
 * @note   Chip-specific implementation in bl616_reset.c
 *         Maps peripheral ID to GLB reset number and calls
 *         GLB_AHB_MCU_Software_Reset()
 */
int bflb_peripheral_reset_by_id(uint8_t peri);
```

### GLB Low-Level Functions

```c
BL_Err_Type GLB_AHB_MCU_Software_Reset(uint8_t swrst);
BL_Err_Type GLB_MCU_SW_System_Reset(uint8_t sysPart);
BL_Err_Type GLB_SW_System_Reset(void);
BL_Err_Type GLB_SW_CPU_Reset(void);
BL_Err_Type GLB_SW_POR_Reset(void);
BL_Err_Type GLB_Disrst_Set(uint8_t enable, uint8_t disrst);
BL_Err_Type GLB_Clr_Reset_Reason(void);
BL_Err_Type GLB_Get_Reset_Reason(GLB_RESET_RECORD_Type *reason);
```

---

## Peripheral IDs (BFLB_PERIPHERAL_xxx)

### BL616 Peripheral IDs

| Peripheral ID                   | Value | Reset Number |
|---------------------------------|-------|--------------|
| BFLB_PERIPHERAL_CPU             | 0     | N/A          |
| BFLB_PERIPHERAL_SDU0            | 1     | 45           |
| BFLB_PERIPHERAL_SEC0            | 2     | -            |
| BFLB_PERIPHERAL_DMA0            | 3     | 44           |
| BFLB_PERIPHERAL_CCI             | 4     | -            |
| BFLB_PERIPHERAL_GPADC0          | 5     | 34           |
| BFLB_PERIPHERAL_GPDAC0          | 6     | 34           |
| BFLB_PERIPHERAL_TZ1             | 7     | 37           |
| BFLB_PERIPHERAL_TZ2             | 8     | -            |
| BFLB_PERIPHERAL_EF_CTRL         | 9     | 39           |
| BFLB_PERIPHERAL_SF_CTRL         | 10    | 43           |
| BFLB_PERIPHERAL_EMAC0           | 11    | 23           |
| BFLB_PERIPHERAL_UART0           | 12    | 48           |
| BFLB_PERIPHERAL_UART1           | 13    | 49           |
| BFLB_PERIPHERAL_UART2           | 14    | -            |
| BFLB_PERIPHERAL_SPI0            | 15    | 50           |
| BFLB_PERIPHERAL_I2C0            | 16    | 51           |
| BFLB_PERIPHERAL_PWM0            | 17    | 52           |
| BFLB_PERIPHERAL_TIMER0          | 18    | 53           |
| BFLB_PERIPHERAL_IR              | 19    | 54           |
| BFLB_PERIPHERAL_CHECKSUM        | 20    | 55           |
| BFLB_PERIPHERAL_I2S0            | 21    | 59           |
| BFLB_PERIPHERAL_PSRAM1_CTRL     | 22    | 18           |
| BFLB_PERIPHERAL_USB20           | 23    | 19           |
| BFLB_PERIPHERAL_AUDAC0          | 24    | 21           |
| BFLB_PERIPHERAL_SDH0            | 25    | 22           |
| BFLB_PERIPHERAL_I2C1            | 26    | 57           |
| BFLB_PERIPHERAL_DBI             | 27    | 56           |
| BFLB_PERIPHERAL_AUADC0          | 28    | 60           |
| BFLB_PERIPHERAL_DMA_GPIO        | 29    | -            |
| BFLB_PERIPHERAL_MM_MISC          | 30    | 17           |
| BFLB_PERIPHERAL_JENC            | 31    | 27           |
| BFLB_PERIPHERAL_D2XB            | 32    | 26           |
| BFLB_PERIPHERAL_D2XA            | 33    | 25           |
| BFLB_PERIPHERAL_EMI_MISC        | 34    | 16           |
| BFLB_PERIPHERAL_CAM0            | 35    | -            |
| BFLB_PERIPHERAL_RTC             | 36    | -            |
| BFLB_PERIPHERAL_SEC_PKA         | 37    | -            |
| BFLB_PERIPHERAL_GLB             | 38    | 32           |
| BFLB_PERIPHERAL_SEC_ENG         | 39    | 36           |
| BFLB_PERIPHERAL_SEC_DBG         | 40    | 35           |
| BFLB_PERIPHERAL_MIX             | 41    | 33           |
| BFLB_PERIPHERAL_PDS             | 42    | 46           |

---

## Data Structures

### GLB_RESET_RECORD_Type

```c
typedef struct {
    uint8_t reset_recorder_rst_n        : 1;  /* reset record bit [0] */
    uint8_t reset_recorder_swd_rst_n    : 1;  /* reset record bit [1] */
    uint8_t reset_recorder_cpu_rst_n     : 1;  /* reset record bit [2] */
    uint8_t reset_recorder_wdt_rst_n     : 1;  /* reset record bit [3] */
    uint8_t reset_recorder_cpu_porst_n   : 1;  /* reset record bit [4] */
    uint8_t reset_recorder_sys_reset_n  : 1;  /* reset record bit [5] */
    uint8_t reset_recorder_cpu_sys_rstreq_n : 1; /* reset record bit [6] */
    uint8_t reset_recorder_rsvd          : 1;  /* reset record bit [7] */
} GLB_RESET_RECORD_Type;
```

---

## Register-Level Information

### GLB Reset Register Map

The software reset is controlled via the GLB registers. The base address is defined in the chip-specific header.

#### Key Reset-Related Registers

| Register Name     | Address Offset | Description                      |
|------------------|----------------|----------------------------------|
| GLB_RST          | 0x?            | AHB MCU Software Reset control    |

### GLB_AHB_MCU_Software_Reset

This function performs a software reset on a specific peripheral by writing to the GLB reset control register.

**Implementation (ROM API):**
```c
BL_Err_Type GLB_AHB_MCU_Software_Reset(uint8_t swrst)
{
    return RomDriver_GLB_AHB_MCU_Software_Reset(swrst);
}
```

**Parameter:** `swrst` - Reset number (0-63, maps to specific peripheral reset signals)

**Return:** `BL_Err_Type` - SUCCESS or error code

---

## Working Code Examples

### Example 1: Reset UART0 Peripheral

```c
#include "bflb_reset.h"

void reset_uart0_example(void)
{
    int ret;

    /* Reset UART0 peripheral */
    ret = bflb_peripheral_reset(BFLB_PERIPHERAL_UART0);
    if (ret < 0) {
        printf("Reset UART0 failed\r\n");
    } else {
        printf("UART0 reset successfully\r\n");
    }
}
```

### Example 2: Reset Multiple Peripherals

```c
#include "bflb_reset.h"

void reset_spi_and_i2c_example(void)
{
    /* Reset SPI0 */
    bflb_peripheral_reset(BFLB_PERIPHERAL_SPI0);

    /* Reset I2C0 */
    bflb_peripheral_reset(BFLB_PERIPHERAL_I2C0);

    /* Both peripherals are now in reset state */
}
```

### Example 3: Check Reset Reason

```c
#include "bflb_glb.h"

void check_reset_reason_example(void)
{
    GLB_RESET_RECORD_Type resetReason;

    /* Get reset reason */
    GLB_Get_Reset_Reason(&resetReason);

    if (resetReason.reset_recorder_wdt_rst_n == 0) {
        printf("Reset caused by Watchdog\r\n");
    }
    if (resetReason.reset_recorder_cpu_rst_n == 0) {
        printf("Reset caused by CPU reset\r\n");
    }
    if (resetReason.reset_recorder_sys_reset_n == 0) {
        printf("Reset caused by System reset\r\n");
    }

    /* Clear reset reason */
    GLB_Clr_Reset_Reason();
}
```

### Example 4: System Reset

```c
#include "bflb_glb.h"

void system_reset_example(void)
{
    /* Perform a full system reset */
    GLB_SW_System_Reset();

    /* Code will not reach here as system resets */
}
```

### Example 5: CPU Reset

```c
#include "bflb_glb.h"

void cpu_reset_example(void)
{
    /* Reset only the CPU (not full system) */
    GLB_SW_CPU_Reset();

    /* CPU will restart from reset vector */
}
```

### Example 6: POR Reset

```c
#include "bflb_glb.h"

void por_reset_example(void)
{
    /* Power-On Reset - resets everything including power domains */
    GLB_SW_POR_Reset();

    /* System performs full power-on reset sequence */
}
```

---

## Reset Mapping Table (BL616)

The `bflb_peripheral_reset_by_id()` function maps peripheral IDs to GLB reset numbers:

| Peripheral ID              | Reset Num | Description                    |
|----------------------------|-----------|--------------------------------|
| BFLB_PERIPHERAL_EMI_MISC   | 16        | EMI Miscellaneous reset        |
| BFLB_PERIPHERAL_MM_MISC    | 17        | Multimedia miscellaneous reset |
| BFLB_PERIPHERAL_PSRAM1_CTRL| 18        | PSRAM1 controller reset        |
| BFLB_PERIPHERAL_USB20      | 19        | USB 2.0 reset                  |
| BFLB_PERIPHERAL_AUDAC0     | 21        | Audio DAC reset                |
| BFLB_PERIPHERAL_SDH0       | 22        | SD Host reset                  |
| BFLB_PERIPHERAL_EMAC0      | 23        | Ethernet MAC reset             |
| BFLB_PERIPHERAL_D2XA       | 25        | D2XA reset                     |
| BFLB_PERIPHERAL_D2XB       | 26        | D2XB reset                     |
| BFLB_PERIPHERAL_JENC       | 27        | JPEG encoder reset             |
| BFLB_PERIPHERAL_GLB        | 32        | Global reset                   |
| BFLB_PERIPHERAL_MIX        | 33        | Mixed signal reset             |
| BFLB_PERIPHERAL_GPADC0     | 34        | GPADC reset                    |
| BFLB_PERIPHERAL_GPDAC0     | 34        | GPDAC reset                    |
| BFLB_PERIPHERAL_SEC_DBG    | 35        | Security debug reset           |
| BFLB_PERIPHERAL_SEC_ENG    | 36        | Security engine reset          |
| BFLB_PERIPHERAL_TZ1        | 37        | TrustZone 1 reset              |
| BFLB_PERIPHERAL_EF_CTRL    | 39        | EFuse controller reset         |
| BFLB_PERIPHERAL_SF_CTRL    | 43        | Serial Flash controller reset   |
| BFLB_PERIPHERAL_DMA0       | 44        | DMA0 reset                     |
| BFLB_PERIPHERAL_SDU0       | 45        | SDU0 reset                     |
| BFLB_PERIPHERAL_PDS        | 46        | PDS reset                      |
| BFLB_PERIPHERAL_UART0      | 48        | UART0 reset                    |
| BFLB_PERIPHERAL_UART1      | 49        | UART1 reset                    |
| BFLB_PERIPHERAL_SPI0       | 50        | SPI0 reset                     |
| BFLB_PERIPHERAL_I2C0       | 51        | I2C0 reset                     |
| BFLB_PERIPHERAL_PWM0       | 52        | PWM0 reset                     |
| BFLB_PERIPHERAL_TIMER0     | 53        | Timer0 reset                   |
| BFLB_PERIPHERAL_IR         | 54        | IR reset                       |
| BFLB_PERIPHERAL_CHECKSUM   | 55        | Checksum reset                 |
| BFLB_PERIPHERAL_DBI        | 56        | DBI reset                      |
| BFLB_PERIPHERAL_I2C1       | 57        | I2C1 reset                     |
| BFLB_PERIPHERAL_I2S0       | 59        | I2S0 reset                     |
| BFLB_PERIPHERAL_AUADC0     | 60        | Audio ADC reset                |

---

## Architecture

```
┌─────────────────────────────────────────────┐
│         Application Code                    │
└─────────────────┬───────────────────────────┘
                  │ bflb_peripheral_reset(peri)
┌─────────────────▼───────────────────────────┐
│      bflb_reset.c (LHAL Layer)              │
│   int bflb_peripheral_reset(uint8_t peri)  │
└─────────────────┬───────────────────────────┘
                  │ bflb_peripheral_reset_by_id(peri)
┌─────────────────▼───────────────────────────┐
│    bl616_reset.c (Chip-Specific Layer)      │
│ int bflb_peripheral_reset_by_id(uint8_t peri)│
└─────────────────┬───────────────────────────┘
                  │ GLB_AHB_MCU_Software_Reset(rst_num)
┌─────────────────▼───────────────────────────┐
│         GLB Registers (Hardware)           │
│    - Reset Control Register                │
│    - Reset Number → Peripheral Reset Signal │
└─────────────────────────────────────────────┘
```

---

## Notes

1. **Peripheral reset** only resets the specified peripheral, not the entire system.
2. **System reset** (`GLB_SW_System_Reset`) resets the entire MCU system.
3. **CPU reset** (`GLB_SW_CPU_Reset`) resets only the CPU core.
4. **POR reset** (`GLB_SW_POR_Reset`) performs a full power-on reset.
5. After resetting a peripheral, allow a small delay before re-initializing it.
6. Some peripherals share the same reset line (e.g., GPADC0 and GPDAC0 both use reset number 34).

---

## Revision History

| Version | Date       | Description           |
|---------|------------|-----------------------|
| 1.0     | 2026-04-28 | Initial documentation |
