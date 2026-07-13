# BL616/BL618 Battery Backup Domain Guide

The Battery Backup (BAK) domain preserves critical data during power loss or deep sleep modes. Data stored in backup registers is retained across power cycles and low-power states.

---

## 1. Overview

The backup domain includes:
- **Backup Registers**: 16x 32-bit registers (BAK_REG0 - BAK_REG15) retaining data in sleep/hibernate
- **Backup Power Domain**: Powered by VBAT supply; independent of main power
- **Wake-up Sources**: RTC, GPIO, comparator, and timer triggers

---

## 2. Header Files

```c
#include "bflb_bak.h"           // Backup domain HAL API
#include "hardware/bak_reg.h"   // Register definitions
```

> **Note**: If `bflb_bak.h` is not found in your SDK version, the backup domain may be integrated into `bl616cl_lp.h` or `pds_reg.h`.

---

## 3. Register-Level Definition

### Backup Register Map (from `bak_reg.h`)

| Register | Offset | Description |
|----------|--------|-------------|
| `BAK_REG0` | 0x00 | Backup register 0 |
| `BAK_REG1` | 0x04 | Backup register 1 |
| `BAK_REG2` | 0x08 | Backup register 2 |
| `BAK_REG3` | 0x0C | Backup register 3 |
| `BAK_REG4` | 0x10 | Backup register 4 |
| `BAK_REG5` | 0x14 | Backup register 5 |
| `BAK_REG6` | 0x18 | Backup register 6 |
| `BAK_REG7` | 0x1C | Backup register 7 |
| `BAK_REG8` | 0x20 | Backup register 8 |
| `BAK_REG9` | 0x24 | Backup register 9 |
| `BAK_REG10` | 0x28 | Backup register 10 |
| `BAK_REG11` | 0x2C | Backup register 11 |
| `BAK_REG12` | 0x30 | Backup register 12 |
| `BAK_REG13` | 0x34 | Backup register 13 |
| `BAK_REG14` | 0x38 | Backup register 14 |
| `BAK_REG15` | 0x3C | Backup register 15 |
| `BAK_LOCK` | 0x40 | Backup lock register |
| `BAK_CTL` | 0x44 | Backup control register |

### Key Register Bits

```c
// BAK_CTL bits
#define BAK_CTL_PWR_OFF_DLY_SHIFT    0   // Power off delay config
#define BAK_CTL_BOD_EN               (1 << 8)   // Brown-out detection enable
#define BAK_CTL_BOD_VSEL_SHIFT       9   // Brown-out voltage select

// BAK_LOCK bits  
#define BAK_LOCK_REG_LOCK            (1 << 0)   // Lock backup registers
#define BAK_LOCK_REG_UNLOCK          (0 << 0)   // Unlock backup registers
```

---

## 4. API Reference

### 4.1 `bflb_bak_init()`

Initialize the backup domain.

```c
int bflb_bak_init(struct bflb_device_s *dev);
```

**Parameters:**
- `dev`: Backup domain device handle (e.g., `"bak"`)

**Returns:** 0 on success, negative error code on failure.

**Example:**
```c
struct bflb_device_s *bak_dev;
bak_dev = bflb_device_get_by_name("bak");
if (bak_dev == NULL) {
    printf("BAK device not found\r\n");
    return -1;
}
bflb_bak_init(bak_dev);
```

---

### 4.2 `bflb_bak_write()`

Write data to a backup register.

```c
int bflb_bak_write(struct bflb_device_s *dev, uint8_t reg_idx, uint32_t val);
```

**Parameters:**
- `dev`: Backup device handle
- `reg_idx`: Register index (0-15)
- `val`: 32-bit value to write

**Returns:** 0 on success, negative error code on failure.

**Example:**
```c
// Store boot counter in backup register 0
bflb_bak_write(bak_dev, 0, boot_count);

// Store timestamp in backup register 1
bflb_bak_write(bak_dev, 1, current_timestamp);

// Store WiFi config in registers 2-3
bflb_bak_write(bak_dev, 2, wifi_config_part1);
bflb_bak_write(bak_dev, 3, wifi_config_part2);
```

---

### 4.3 `bflb_bak_read()`

Read data from a backup register.

```c
uint32_t bflb_bak_read(struct bflb_device_s *dev, uint8_t reg_idx);
```

**Parameters:**
- `dev`: Backup device handle
- `reg_idx`: Register index (0-15)

**Returns:** 32-bit register value.

**Example:**
```c
// Recover boot counter after reset/wake
boot_count = bflb_bak_read(bak_dev, 0);
printf("Boot count: %lu\r\n", boot_count);

// Read stored timestamp
timestamp = bflb_bak_read(bak_dev, 1);
```

---

### 4.4 `bflb_bak_lock()`

Lock backup registers to prevent accidental writes.

```c
int bflb_bak_lock(struct bflb_device_s *dev, uint8_t lock);
```

**Parameters:**
- `dev`: Backup device handle
- `lock`: 1 to lock, 0 to unlock

**Example:**
```c
// After writing critical data, lock registers
bflb_bak_write(bak_dev, 0, important_data);
bflb_bak_lock(bak_dev, 1);  // Lock to prevent corruption
```

---

## 5. Wake-up Sources

The backup domain supports multiple wake-up sources configured via LP (Low Power) subsystem:

### 5.1 Wake-up Source Types

| Source | Description | Configuration |
|--------|-------------|---------------|
| **RTC** | Real-time clock alarm | `rtc_wakeup_en`, `rtc_wakeup_cmp_cnt` |
| **GPIO** | GPIO pin trigger | `io_wakeup_unmask`, trigger mode |
| **ACOMP** | Analog comparator | `acomp0_en`, `acomp1_en` |
| **TIM** | Timer wake-up | `tim_wakeup_en` |
| **PDS** | Power down sleep | Combined wake sources |

### 5.2 Wake-up Configuration Structure

```c
typedef struct {
    uint8_t tim_wakeup_en;           /* TIM bit wakeup enable */
    uint8_t rtc_wakeup_en;           /* RTC timer wakeup enable */
    uint32_t rtc_wakeup_cmp_cnt;     /* RTC compare count */
    uint32_t rtc_timeout_us;         /* RTC timeout in microseconds */
    lp_fw_gpio_cfg_t *io_wakeup_parameter;  /* GPIO wakeup config */
} bl_lp_fw_cfg_t;
```

### 5.3 Check Wake-up Source

```c
#include "bl616cl_lp.h"

uint32_t wake_reason = bl_lp_get_wake_reason();

if (wake_reason & LPFW_WAKEUP_TIME_OUT) {
    printf("Wake-up by RTC timeout\r\n");
}
if (wake_reason & LPFW_WAKEUP_GPIO) {
    printf("Wake-up by GPIO\r\n");
}
if (wake_reason & LPFW_WAKEUP_ACOMP) {
    printf("Wake-up by analog comparator\r\n");
}
```

---

## 6. Working Code Examples

### 6.1 Basic Backup Register Usage

```c
#include "bflb_device.h"
#include "bflb_bak.h"

void backup_example(void)
{
    struct bflb_device_s *bak_dev;
    
    // Get backup device
    bak_dev = bflb_device_get_by_name("bak");
    if (bak_dev == NULL) {
        return -1;
    }
    
    // Initialize backup domain
    bflb_bak_init(bak_dev);
    
    // Write data to backup registers
    bflb_bak_write(bak_dev, 0, 0x12345678);  // Boot marker
    bflb_bak_write(bak_dev, 1, 0xAABBCCDD);  // User data
    
    // Read back data
    uint32_t val0 = bflb_bak_read(bak_dev, 0);
    uint32_t val1 = bflb_bak_read(bak_dev, 1);
    
    printf("BAK_REG0 = 0x%08X\r\n", val0);
    printf("BAK_REG1 = 0x%08X\r\n", val1);
    
    // Lock registers after writing
    bflb_bak_lock(bak_dev, 1);
}
```

### 6.2 Store Counter Across Deep Sleep

```c
#include "bflb_device.h"
#include "bflb_bak.h"
#include "bl616cl_lp.h"

#define BAK_BOOT_CNT_REG    0
#define BAK_BOOT_FLAG_REG   1

static uint32_t g_boot_count = 0;

void boot_counter_init(void)
{
    struct bflb_device_s *bak_dev;
    
    bak_dev = bflb_device_get_by_name("bak");
    if (bak_dev == NULL) {
        return;
    }
    
    bflb_bak_init(bak_dev);
    
    // Check for valid boot marker
    uint32_t flag = bflb_bak_read(bak_dev, BAK_BOOT_FLAG_REG);
    
    if (flag == 0xB00B5EED) {
        // Valid marker found, increment counter
        g_boot_count = bflb_bak_read(bak_dev, BAK_BOOT_CNT_REG) + 1;
    } else {
        // First boot or corrupted, reset
        g_boot_count = 1;
    }
    
    // Store updated counter
    bflb_bak_write(bak_dev, BAK_BOOT_FLAG_REG, 0xB00B5EED);
    bflb_bak_write(bak_dev, BAK_BOOT_CNT_REG, g_boot_count);
    
    printf("Boot count: %lu\r\n", g_boot_count);
}
```

### 6.3 Deep Sleep with GPIO Wake-up

```c
#include "bflb_device.h"
#include "bflb_bak.h"
#include "bl616cl_lp.h"
#include "gpio.h"

#define BAK_STATE_REG   0
#define BAK_WAKE_PIN    10

void sleep_with_gpio_wake(void)
{
    struct bflb_device_s *bak_dev;
    bl_lp_fw_cfg_t lp_cfg = { 0 };
    
    bak_dev = bflb_device_get_by_name("bak");
    if (bak_dev == NULL) return;
    
    bflb_bak_init(bak_dev);
    
    // Save state before sleep
    bflb_bak_write(bak_dev, BAK_STATE_REG, 0xDEADBEEF);
    
    // Configure GPIO wake-up
    lp_cfg.io_wakeup_parameter = &(lp_fw_gpio_cfg_t){
        .io_8_15_pds_trig_mode = BL_LP_GPIO_TRIG_EDGE_RISING,
        .io_wakeup_unmask = (1 << BAK_WAKE_PIN),
    };
    
    // Enter deep sleep
    bl_lp_fw_enter(&lp_cfg);
    
    // Upon wake-up, check source
    uint32_t wake_reason = bl_lp_get_wake_reason();
    if (wake_reason & LPFW_WAKEUP_GPIO) {
        printf("Woke up from GPIO pin %d\r\n", BAK_WAKE_PIN);
    }
    
    // Recover state
    uint32_t state = bflb_bak_read(bak_dev, BAK_STATE_REG);
    printf("Recovered state: 0x%08X\r\n", state);
}
```

### 6.4 RTC Timer Wake-up

```c
#include "bflb_device.h"
#include "bflb_bak.h"
#include "bl616cl_lp.h"

#define BAK_RTC_TARGET_REG    2

void sleep_with_rtc_wake(uint32_t timeout_us)
{
    struct bflb_device_s *bak_dev;
    bl_lp_fw_cfg_t lp_cfg = { 0 };
    
    bak_dev = bflb_device_get_by_name("bak");
    if (bak_dev == NULL) return;
    
    bflb_bak_init(bak_dev);
    
    // Configure RTC wake-up
    lp_cfg.rtc_wakeup_en = 1;
    lp_cfg.rtc_timeout_us = timeout_us;  // Microseconds
    
    // Store target time in backup register
    uint32_t target = bflb_bak_read(bak_dev, BAK_RTC_TARGET_REG);
    bflb_bak_write(bak_dev, BAK_RTC_TARGET_REG, target + timeout_us);
    
    // Enter low power mode
    bl_lp_fw_enter(&lp_cfg);
    
    // After wake-up
    printf("Woke up after %lu us\r\n", timeout_us);
}
```

---

## 7. Integration with Power Management

The backup domain works closely with the PDS/HBN power management:

```c
// Enter Hibernate with backup retention
void enter_hibernate(void)
{
    struct bflb_device_s *bak_dev;
    
    bak_dev = bflb_device_get_by_name("bak");
    if (bak_dev == NULL) return;
    
    // Ensure data is stored
    bflb_bak_write(bak_dev, 0, application_state);
    
    // Configure LP firmware for hibernate
    bl_lp_fw_cfg_t cfg = {
        .rtc_wakeup_en = 1,
        .rtc_timeout_us = 60 * 1000000,  // 1 minute minimum
    };
    
    bl_lp_fw_enter(&cfg);
}
```

---

## 8. Register Access without HAL

Direct register access when HAL is unavailable:

```c
// Base address for BAK registers (see datasheet)
#define BAK_BASE     0x4000A000

// Register access macros
#define BAK_REG(n)   (*(volatile uint32_t *)(BAK_BASE + (n) * 4))
#define BAK_LOCK     (*(volatile uint32_t *)(BAK_BASE + 0x40))
#define BAK_CTL      (*(volatile uint32_t *)(BAK_BASE + 0x44))

// Direct write
BAK_REG(0) = 0x12345678;

// Direct read
uint32_t val = BAK_REG(0);

// Lock registers
BAK_LOCK = 0x1;  // Lock
BAK_LOCK = 0x0;  // Unlock
```

---

## 9. Data Retention Checklist

- [ ] Initialize backup domain with `bflb_bak_init()`
- [ ] Store critical data before entering low-power mode
- [ ] Use magic numbers/flags to validate data integrity
- [ ] Implement error recovery for corrupted backup data
- [ ] Lock registers after writing to prevent corruption
- [ ] Check wake-up source after waking from sleep

---

## 10. Common Issues

| Issue | Cause | Solution |
|-------|-------|----------|
| Data lost after reset | VBAT power interrupted | Check VBAT supply and backup capacitor |
| Read returns 0xFFFFFFFF | Registers locked or no power | Verify BAK domain clock and power |
| Wake-up fails | Wake source not configured | Enable wake source in LP configuration |
| Write fails silently | Registers locked | Call `bflb_bak_lock(dev, 0)` before writing |
