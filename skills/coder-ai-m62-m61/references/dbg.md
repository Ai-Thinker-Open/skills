# Debug Peripheral Documentation (BL616/BL618)

## Overview

The BL616/BL618 chips support JTAG/SWD debug interface for hardware debugging and programming. The debug subsystem is controlled via the `SEC_DBG` (Security Debug) peripheral.

## SWD/JTAG Debug Interface

### Debug Pins

The default JTAG pins for BL616/BL618 are:

| Signal | GPIO Pin | Description |
|--------|----------|-------------|
| TMS    | GPIO0    | Test Mode Select / SWDIO |
| TCK    | GPIO1    | Test Clock / SWCLK |
| TDO    | GPIO2    | Test Data Out |
| TDI    | GPIO3    | Test Data In |

### Debug Modes

The SEC_DBG peripheral supports three debug states:

| Mode | Value | Description |
|------|-------|-------------|
| `SEC_DBG_STATE_OPEN_MODE` | 0 | Debug fully open - JTAG accessible |
| `SEC_DBG_STATE_PASSWORD_MODE` | 1 | Debug password protected (modes 1-3 with partial enable) |
| `SEC_DBG_STATE_CLOSE_MODE` | 2 | Debug fully closed |

### Debug Status Register (SEC_DBG_SD_STATUS)

Located at base address `SEC_DBG_BASE` (0x2000F000).

| Field | Bits | Description |
|-------|------|-------------|
| sd_dbg_ena | [31:28] | Debug enable status (0xF = fully enabled) |
| sd_dbg_mode | [27:24] | Debug mode (0=open, 1-3=password mode, 4+=closed) |
| sd_dbg_pwd_cnt | [23:4] | Password attempt counter |
| sd_dbg_cci_clk_sel | [3] | CCI clock select |
| sd_dbg_cci_read_en | [2] | CCI read enable |
| sd_dbg_pwd_trig | [1] | Password trigger (write 1 to apply) |
| sd_dbg_pwd_busy | [0] | Password operation busy flag |

## Register Definitions

From `sec_dbg_reg.h`:

```
SEC_DBG_BASE                   0x2000F000
SEC_DBG_SD_CHIP_ID_LOW        (0x0)  - Chip ID lower 32 bits
SEC_DBG_SD_CHIP_ID_HIGH       (0x4)  - Chip ID upper 32 bits
SEC_DBG_SD_DBG_PWD_LOW        (0x8)  - Debug password low
SEC_DBG_SD_DBG_PWD_HIGH       (0xC)  - Debug password high
SEC_DBG_SD_DBG_PWD2_LOW       (0x10) - Debug password 2 low
SEC_DBG_SD_DBG_PWD2_HIGH      (0x14) - Debug password 2 high
SEC_DBG_SD_STATUS             (0x18) - Debug status
SEC_DBG_SD_DBG_RESERVED       (0x1C) - Reserved
```

## Driver API (`bl616_sec_dbg.h`)

### Functions

```c
/**
 * Read chip ID (8 bytes)
 * @param id[8] - buffer to store chip ID
 */
void Sec_Dbg_Read_Chip_ID(uint8_t id[8]);

/**
 * Read current debug state
 * @return SEC_DBG_STATE_OPEN_MODE / PASSWORD_MODE / CLOSE_MODE
 */
uint32_t Sec_Dbg_Read_Dbg_State(void);

/**
 * Read debug mode value
 * @return raw mode value (0-15)
 */
uint32_t Sec_Dbg_Read_Dbg_Mode(void);

/**
 * Read debug enable status
 * @return enable value
 */
uint32_t Sec_Dbg_Read_Dbg_Enable(void);

/**
 * Set debug password (128-bit, 4 x 32-bit words)
 * @param pwd[4] - password array
 */
void Sec_Dbg_Set_Dbg_Pwd(const uint32_t pwd[4]);

/**
 * Trigger debug password application
 */
void Sec_Dbg_Set_Dbg_Trigger(void);

/**
 * Wait for password operation to complete
 * @return 0 if ready, non-zero if busy timeout
 */
uint32_t Sec_Dbg_Wait_Ready(void);
```

## Working Code Example

```c
#include "bl616_sec_dbg.h"
#include "bflb_mtimer.h"

static void show_debug_state(void)
{
    uint32_t state = Sec_Dbg_Read_Dbg_State();
    
    if (state == SEC_DBG_STATE_OPEN_MODE) {
        printf("Debug is OPEN - JTAG accessible\r\n");
    } else if (state == SEC_DBG_STATE_PASSWORD_MODE) {
        printf("Debug is PASSWORD protected\r\n");
    } else {
        printf("Debug is CLOSED\r\n");
    }
}

int main(void)
{
    uint32_t pwd[4] = {
        0x12345678,
        0x22345678,
        0x32345678,
        0x42345678
    };
    
    /* Show initial debug state */
    show_debug_state();
    
    /* Set password and trigger debug mode change */
    Sec_Dbg_Set_Dbg_Pwd(pwd);
    Sec_Dbg_Set_Dbg_Trigger();
    
    /* Wait for operation to complete */
    if (Sec_Dbg_Wait_Ready() == 0) {
        printf("Debug password set successfully\r\n");
    }
    
    /* Show new debug state */
    show_debug_state();
    
    /* Read chip ID */
    uint8_t chip_id[8];
    Sec_Dbg_Read_Chip_ID(chip_id);
    printf("Chip ID: %02X%02X%02X%02X-%02X%02X%02X%02X\r\n",
           chip_id[0], chip_id[1], chip_id[2], chip_id[3],
           chip_id[4], chip_id[5], chip_id[6], chip_id[7]);
    
    while (1) {
        bflb_mtimer_delay_ms(1000);
    }
}
```

## GPIO Configuration for JTAG

To use JTAG debug interface, configure the appropriate GPIO pins:

```c
#include "bflb_gpio.h"

/* For BL616/BL618 default JTAG pins */
void jtag_gpio_init(void)
{
    bflb_gpio_init(gpio, GPIO_PIN_0, GPIO_FUNC_JTAG | GPIO_ALTERNATE | GPIO_PULLUP | GPIO_SMT_EN | GPIO_DRV_1);  /* TMS */
    bflb_gpio_init(gpio, GPIO_PIN_1, GPIO_FUNC_JTAG | GPIO_ALTERNATE | GPIO_PULLUP | GPIO_SMT_EN | GPIO_DRV_1);  /* TCK */
    bflb_gpio_init(gpio, GPIO_PIN_2, GPIO_FUNC_JTAG | GPIO_ALTERNATE | GPIO_PULLUP | GPIO_SMT_EN | GPIO_DRV_1);  /* TDO */
    bflb_gpio_init(gpio, GPIO_PIN_3, GPIO_FUNC_JTAG | GPIO_ALTERNATE | GPIO_PULLUP | GPIO_SMT_EN | GPIO_DRV_1);  /* TDI */
}
```

## Debug Security Notes

1. **Factory Default**: Chips typically ship with debug in OPEN mode
2. **Password Mode**: When using password mode, JTAG is unavailable until valid password is provided
3. **EFUSE Settings**: Debug mode can also be controlled via eFuse configuration
4. **Close Mode**: Completely disables debug interface

## Related Files

- Driver: `drivers/soc/bl616/std/src/bl616_sec_dbg.c`
- Header: `drivers/soc/bl616/std/include/bl616_sec_dbg.h`
- Registers: `drivers/soc/bl616/std/include/hardware/sec_dbg_reg.h`
- Example: `examples/peripherals/sec_dbg/sec_dbg_password/main.c`
