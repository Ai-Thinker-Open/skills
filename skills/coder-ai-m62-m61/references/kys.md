# KYS API Reference (BL616/BL618)

> **Source:** `bouffalo_sdk/drivers/lhal/include/bflb_kys.h`  
> **Register Header:** `bouffalo_sdk/drivers/lhal/include/hardware/kys_reg.h`  
> **Implementation:** `bouffalo_sdk/drivers/lhal/src/bflb_kys.c`
>
> **⚠️ Chip Support:** The KYS (Key Scan) peripheral is **not available** on BL616. It is only provided on the **BL618DG** multi-core chip.

## Overview

The KYS (Key Scan / Matrix Keyboard Scan) module provides hardware matrix keyboard scanning functionality. It automatically drives column-by-column scanning, reading row inputs to detect key presses. It supports deglitch (debounce) and ghost key detection, as well as FIFO buffering of key events.

Supports a maximum of 8 columns × 8 rows matrix keyboard.

## Base Address

| Chip | Peripheral | Base Address |
|------|------|--------|
| BL618DG | KYS | `0x2000F800` |

> BL616 does not have this peripheral.

---

## Configuration Structure

### bflb_kys_config_s

```c
struct bflb_kys_config_s {
    uint8_t col;           /* Number of keyboard columns, max 8 */
    uint8_t row;           /* Number of keyboard rows, max 8 */
    uint8_t deglitch_en;   /* Deglitch (debounce) enable */
    uint8_t deglitch_cnt;  /* Deglitch count */
    uint8_t idle_duration; /* Idle time between column scan intervals */
    uint8_t ghost_en;      /* Ghost key detection enable */
};
```

| Field | Type | Description |
|------|------|------|
| `col` | `uint8_t` | Number of matrix keyboard columns (1–8) |
| `row` | `uint8_t` | Number of matrix keyboard rows (1–8) |
| `deglitch_en` | `uint8_t` | Deglitch enable (0=disabled, 1=enabled) |
| `deglitch_cnt` | `uint8_t` | Deglitch count (0–15, debounce threshold) |
| `idle_duration` | `uint8_t` | Column scan idle interval (0–3, time units) |
| `ghost_en` | `uint8_t` | Ghost key detection enable (0=disabled, 1=enabled) |

---

## Interrupt Flag Macros

### Interrupt Enable Flags (KEYSCAN_INT_EN_*)

Used for the `flag` parameter of `bflb_kys_int_enable()`:

| Macro | Bit | Description |
|----|-----|------|
| `KEYSCAN_INT_EN_DONE` | 7 | Scan complete interrupt |
| `KEYSCAN_INT_EN_FIFOFULL` | 8 | FIFO full interrupt |
| `KEYSCAN_INT_EN_FIFOHALF` | 9 | FIFO half-full interrupt |
| `KEYSCAN_INT_EN_FIFOQUARTER` | 10 | FIFO quarter-full interrupt |
| `KEYSCAN_INT_EN_FIFO_NONEMPTY` | 11 | FIFO non-empty interrupt |
| `KEYSCAN_INT_EN_GHOST` | 12 | Ghost key detection interrupt |

> BL702L chip interrupt clear flags:
> - `KEYSCAN_INT_CLR_DONE` — Clear scan complete status
> - `KEYSCAN_INT_CLR_FIFO` — Clear FIFO status
> - `KEYSCAN_INT_CLR_GHOST` — Clear ghost key status

---

## LHAL API Functions

### bflb_kys_init

Initialize the matrix keyboard scan controller.

```c
void bflb_kys_init(struct bflb_device_s *dev, const struct bflb_kys_config_s *config);
```

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `dev` | `struct bflb_device_s *` | KYS device handle |
| `config` | `const struct bflb_kys_config_s *` | Keyboard scan configuration parameters |

---

### bflb_kys_enable

Enable keyboard scanning.

```c
void bflb_kys_enable(struct bflb_device_s *dev);
```

---

### bflb_kys_disable

Disable keyboard scanning.

```c
void bflb_kys_disable(struct bflb_device_s *dev);
```

---

### bflb_kys_int_enable

Enable or disable keyboard scan interrupts.

```c
void bflb_kys_int_enable(struct bflb_device_s *dev, uint32_t flag, bool enable);
```

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `dev` | `struct bflb_device_s *` | Device handle |
| `flag` | `uint32_t` | Interrupt flags (use `KEYSCAN_INT_EN_*` macros, can be OR-combined) |
| `enable` | `bool` | `true` = enable interrupt, `false` = disable interrupt |

---

### bflb_kys_int_clear

Clear interrupt flags.

```c
void bflb_kys_int_clear(struct bflb_device_s *dev, uint32_t flag);
```

---

### bflb_kys_get_int_status

Get current interrupt status (returns only enabled interrupt bits).

```c
uint32_t bflb_kys_get_int_status(struct bflb_device_s *dev);
```

**Returns:** Interrupt status bitmask

---

### bflb_kys_get_fifo_info

Get FIFO buffer information (BL702L only).

```c
void bflb_kys_get_fifo_info(struct bflb_device_s *dev, uint8_t *fifo_head, uint8_t *fifo_tail, uint8_t *fifo_valid_cnt);
```

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `dev` | `struct bflb_device_s *` | Device handle |
| `fifo_head` | `uint8_t *` | Output: FIFO head pointer |
| `fifo_tail` | `uint8_t *` | Output: FIFO tail pointer |
| `fifo_valid_cnt` | `uint8_t *` | Output: FIFO valid data count |

---

### bflb_kys_read_keyvalue

Read key value.

```c
uint8_t bflb_kys_read_keyvalue(struct bflb_device_s *dev, uint8_t index);
```

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `dev` | `struct bflb_device_s *` | Device handle |
| `index` | `uint8_t` | Key index (BL702: 0–3, BL702L: ignored) |

**Returns:** Key code value (uint8_t)

---

## Usage Examples

### Example 1: Basic Keyboard Scan Initialization

```c
#include "bflb_kys.h"

void keyscan_init(void)
{
    struct bflb_device_s *kys;

    // Get KYS device handle
    kys = bflb_device_get_by_name("kys");

    // Configure 4x4 matrix keyboard
    struct bflb_kys_config_s cfg = {
        .col = 4,            // 4 columns
        .row = 4,            // 4 rows
        .deglitch_en = 1,    // Enable deglitch
        .deglitch_cnt = 5,   // Deglitch count 5
        .idle_duration = 1,  // Scan interval
        .ghost_en = 1,       // Enable ghost key detection
    };

    bflb_kys_init(kys, &cfg);
    bflb_kys_enable(kys);
}
```

### Example 2: Interrupt-Driven Keyboard Scanning

```c
#include "bflb_kys.h"

void keyscan_interrupt_init(void)
{
    struct bflb_device_s *kys;
    kys = bflb_device_get_by_name("kys");

    // Initialize keyboard
    struct bflb_kys_config_s cfg = {
        .col = 3, .row = 3,
        .deglitch_en = 1, .deglitch_cnt = 3,
        .idle_duration = 0, .ghost_en = 1,
    };
    bflb_kys_init(kys, &cfg);

    // Enable FIFO non-empty interrupt and scan complete interrupt
    bflb_kys_int_enable(kys, KEYSCAN_INT_EN_FIFO_NONEMPTY | KEYSCAN_INT_EN_DONE, true);

    // Enable scanning
    bflb_kys_enable(kys);

    // Handle keys in interrupt callback
    bflb_irq_attach(KYS_IRQ_NUM, kys_irq_handler, NULL);
    bflb_irq_enable(KYS_IRQ_NUM);
}

void kys_irq_handler(int irq, void *arg)
{
    struct bflb_device_s *kys;
    kys = bflb_device_get_by_name("kys");

    uint32_t int_status = bflb_kys_get_int_status(kys);

    if (int_status & KEYSCAN_INT_EN_FIFO_NONEMPTY) {
        // Read key value
        uint8_t key = bflb_kys_read_keyvalue(kys, 0);
        // Process key value...
        bflb_kys_int_clear(kys, KEYSCAN_INT_CLR_FIFO);
    }

    if (int_status & KEYSCAN_INT_EN_DONE) {
        bflb_kys_int_clear(kys, KEYSCAN_INT_CLR_DONE);
    }
}
```

---

## Register-Level Reference

### KYS Register Offsets

| Register | Offset | Description |
|--------|------|------|
| `KYS_KS_CTRL` | `0x00` | Control register |
| `KYS_KS_INT_EN` | `0x10` | Interrupt enable register |
| `KYS_KS_INT_STS` | `0x14` | Interrupt status register |
| `KYS_KEYCODE_CLR` | `0x18` | Key code / interrupt clear register |
| `KYS_KEYFIFO_IDX` | `0x30` | FIFO index register (BL702L+) |
| `KYS_KEYFIFO_VALUE` | `0x34` | FIFO value register |

### KS_CTRL Control Register (0x00)

| Bits | Field | Description |
|------|-------|-------------|
| 0 | `KYS_KS_EN` | Keyboard scan enable |
| 1 | `KYS_FIFO_MODE` | FIFO mode enable (BL702L+) |
| 2 | `KYS_GHOST_EN` | Ghost key detection enable |
| 3 | `KYS_DEG_EN` | Deglitch enable |
| 7–4 | `KYS_DEG_CNT` | Deglitch count (0–15) |
| 9–8 | `KYS_RC_EXT` | Row/Column extension (idle interval: 0–3) |
| 18–16 | `KYS_ROW_NUM` | Number of rows (0–7, corresponds to 1–8 rows) |
| 23–20 | `KYS_COL_NUM` | Number of columns (BL702L: 0–31, BL702: 0–7) |

### KS_INT_EN Interrupt Enable Register (0x10)

| Bits | Field | Description |
|------|-------|-------------|
| 7 | `KYS_DONE_INT_EN` | Scan complete interrupt enable |
| 8 | `KEYFIFO_FULL_INT_EN` | FIFO full interrupt enable |
| 9 | `KEYFIFO_HALF_INT_EN` | FIFO half-full interrupt enable |
| 10 | `KEYFIFO_QUARTER_INT_EN` | FIFO 1/4 full interrupt enable |
| 11 | `KEYFIFO_NONEMPTY_INT_EN` | FIFO non-empty interrupt enable |
| 12 | `GHOST_INT_EN` | Ghost key interrupt enable |

### KS_INT_STS Interrupt Status Register (0x14)

| Bits | Field | Description |
|------|-------|-------------|
| 7 | `KEYCODE_DONE` | Scan complete |
| 8 | `KEYFIFO_FULL` | FIFO full |
| 9 | `KEYFIFO_HALF` | FIFO half-full |
| 10 | `KEYFIFO_QUARTER` | FIFO 1/4 full |
| 11 | `KEYFIFO_NONEMPTY` | FIFO non-empty |
| 12 | `GHOST_DET` | Ghost key detected |

### KEYFIFO_IDX Index Register (0x30, BL702L+)

| Bits | Field | Description |
|------|-------|-------------|
| 2–0 | `FIFO_HEAD` | FIFO head pointer |
| 10–8 | `FIFO_TAIL` | FIFO tail pointer |
| 19–16 | `FIFO_VALID_CNT` | FIFO valid data count |

### Direct Register Access Example

```c
#include "hardware/kys_reg.h"
#include "bl618dg_memorymap.h"

void kys_direct_enable(void)
{
    uint32_t reg_val;

    // Read control register
    reg_val = getreg32(KYS_BASE + KYS_KS_CTRL_OFFSET);

    // Enable keyboard scan
    reg_val |= KYS_KS_EN_MASK;

    putreg32(reg_val, KYS_BASE + KYS_KS_CTRL_OFFSET);
}

uint32_t kys_direct_get_int_status(void)
{
    uint32_t int_sts = getreg32(KYS_BASE + KYS_KS_INT_STS_OFFSET);
    uint32_t int_en = getreg32(KYS_BASE + KYS_KS_INT_EN_OFFSET);
    return (int_sts & int_en);
}
```
