# MTIMER API Reference (BL616/BL618)

> **Source:** `bouffalo_sdk/drivers/lhal/include/bflb_mtimer.h`  
> **Implementation:** `bouffalo_sdk/drivers/lhal/src/bflb_mtimer.c`  
> **Chip Support:** BL602, BL702/BL702L, BL616/BL618, BL618DG

## Overview

MTIMER (Machine Timer) is a 64-bit high-precision hardware timer interface based on the RISC-V architecture's Machine Timer peripheral. It uses the RISC-V core's `mtime`/`mtimecmp` registers (BL602/BL702) or CSI Core Timer (BL616/BL618) to provide microsecond-level timestamps and precise delay functionality.

**Key Features:**
- 64-bit high-precision timestamp (microsecond level)
- Hardware timer interrupt support
- Microsecond/millisecond delay functions (blocking)
- Default frequency 1 MHz (1 tick = 1 μs)
- Functions located in TCM section for low-latency access

## MTIMER Frequency

The default timer frequency is **1 MHz** (1,000,000 ticks per second), which can be customized by overriding the weak function `bflb_mtimer_get_freq()`. After enabling the `CONFIG_MTIMER_CUSTOM_FREQUENCE` configuration option, time calculations will automatically adapt to the custom frequency.

---

## LHAL API Functions

### bflb_mtimer_config

Configure the Machine Timer interrupt.

```c
void bflb_mtimer_config(uint64_t ticks, void (*interruptfun)(void));
```

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `ticks` | `uint64_t` | Number of ticks needed to trigger the interrupt (default 1 tick = 1 μs) |
| `interruptfun` | `void (*)(void)` | Interrupt callback function pointer |

**Note:** This function configures the timer to trigger an interrupt after `ticks` ticks, using IRQ 7 (Machine Timer interrupt). Thereafter, it repeats every `ticks` cycle.

---

### bflb_mtimer_get_freq

Get the current Machine Timer frequency.

```c
uint32_t bflb_mtimer_get_freq(void);
```

**Returns:** Timer frequency (Hz), default returns `1000000` (1 MHz)

**Note:** This function is a weak function (`__WEAK`) and can be overridden by the user to return the actual frequency.

---

### bflb_mtimer_get_time_us

Get the current Machine Timer time (microseconds).

```c
uint64_t bflb_mtimer_get_time_us(void);
```

**Returns:** 64-bit time value since startup (microseconds), ~584,942 years before overflow

**Note:** The function is located in the TCM section for extremely fast execution. Internally, it uses a double-read anti-rollover mechanism (reads low twice + high to ensure consistency).

---

### bflb_mtimer_get_time_ms

Get the current Machine Timer time (milliseconds).

```c
uint64_t bflb_mtimer_get_time_ms(void);
```

**Returns:** 64-bit time value since startup (milliseconds)

---

### bflb_mtimer_delay_us

Microsecond-level blocking delay.

```c
void bflb_mtimer_delay_us(uint32_t time);
```

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `time` | `uint32_t` | Delay duration (microseconds) |

**Note:** Busy-wait method. For BL616/BL618, ROM API acceleration is supported. The function is located in the TCM section.

---

### bflb_mtimer_delay_ms

Millisecond-level blocking delay.

```c
void bflb_mtimer_delay_ms(uint32_t time);
```

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `time` | `uint32_t` | Delay duration (milliseconds) |

---

### bflb_mtimer_set_val

Directly set the Machine Timer count value (BL616CL only).

```c
void bflb_mtimer_set_val(uint64_t val);
```

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `val` | `uint64_t` | Timer value to set |

---

## Usage Examples

### Example 1: Basic Delay

```c
#include "bflb_mtimer.h"

void delay_example(void)
{
    // Microsecond delay
    bflb_mtimer_delay_us(100);   // Delay 100 μs

    // Millisecond delay
    bflb_mtimer_delay_ms(500);   // Delay 500 ms
}
```

### Example 2: Performance Timing

```c
#include "bflb_mtimer.h"
#include "bflb_platform.h"

void benchmark_example(void)
{
    uint64_t start, end;

    start = bflb_mtimer_get_time_us();

    // Execute code under test
    some_operation();

    end = bflb_mtimer_get_time_us();

    MSG("Operation took %llu us\r\n", (unsigned long long)(end - start));
}
```

### Example 3: Timer Interrupt

```c
#include "bflb_mtimer.h"

static volatile uint32_t tick_count = 0;

void my_timer_callback(void)
{
    tick_count++;
    // Called every 1 ms
}

void timer_interrupt_example(void)
{
    // Configure 1 ms periodic interrupt (default 1 MHz, 1000 ticks = 1 ms)
    bflb_mtimer_config(1000, my_timer_callback);

    while (1) {
        // Timer generates interrupts in background
        // tick_count increments by 1000 every second
    }
}
```

### Example 4: Timeout Detection

```c
#include "bflb_mtimer.h"

bool wait_for_condition_with_timeout(uint32_t timeout_ms)
{
    uint64_t start = bflb_mtimer_get_time_ms();

    while (!condition_met()) {
        if (bflb_mtimer_get_time_ms() - start >= timeout_ms) {
            return false;  // Timeout
        }
    }
    return true;  // Condition met
}
```

### Example 5: Microsecond Delay Accuracy Test

```c
#include "bflb_mtimer.h"
#include "bflb_platform.h"

void delay_accuracy_test(void)
{
    uint64_t start, end;
    uint32_t delays[] = {1, 10, 50, 100, 500, 1000};

    for (int i = 0; i < sizeof(delays) / sizeof(delays[0]); i++) {
        start = bflb_mtimer_get_time_us();
        bflb_mtimer_delay_us(delays[i]);
        end = bflb_mtimer_get_time_us();

        MSG("Requested: %u us, Actual: %llu us\r\n",
            delays[i], (unsigned long long)(end - start));
    }
}
```

---

## Architecture Details

### BL602 / BL702 / BL702L

These chips directly use the MTIME/MTIMECMP registers in the RISC-V CLIC (Core Local Interrupt Controller):

- `CLIC_MTIME`: 64-bit monotonically incrementing counter
- `CLIC_MTIMECMP`: 64-bit compare value register

Addresses are accessed via `CLIC_CTRL_BASE + CLIC_MTIME_OFFSET` and `CLIC_CTRL_BASE + CLIC_MTIMECMP_OFFSET`.

### BL616 / BL618 / BL618DG

These chips use the CSI Core Timer (C-SKY architecture core timer):

- `csi_coret_get_value()` / `csi_coret_get_valueh()`: Read 64-bit timer value
- `csi_coret_config()`: Configure compare value and interrupt
- `SysTimer_*` family functions (NMSIS Core API)

The interrupt number is fixed to **IRQ 7** (Machine Timer Interrupt).

### BL616CL

The BL616CL variant uses the E907 RTC timer in the MCU_MISC module:

| Register Offset | Purpose |
|-----------|------|
| `0x08` | RTC load value lower 32 bits |
| `0x0C` | RTC load value upper 32 bits |
| `0x14` | RTC control (bit 0: enable, bit 1: reset, bit 28: load pulse) |

Base address: `BFLB_MISC_BASE = 0x20009000`

---

## Interrupt Configuration

MTIMER uses the RISC-V standard Machine Timer interrupt (IRQ 7).

**Interrupt Registration Example:**

```c
void mtimer_handler(int irq, void *arg)
{
    // Timer interrupt handling
    // The framework automatically resets mtimecmp to maintain periodic interrupts
}

// Configure timer to trigger after 1000 ticks
bflb_mtimer_config(1000, mtimer_handler);
```

The internal implementation automatically:
1. Saves the ticks value and callback function
2. Disables IRQ 7
3. Sets the mtimecmp compare value
4. Registers the ISR callback (`bflb_irq_attach(7, systick_isr, NULL)`)
5. Enables IRQ 7

In the ISR, the compare value is automatically incremented by `current_set_ticks` to achieve periodic timing.

---

## Important Notes

1. **TCM Resident:** Functions such as `bflb_mtimer_get_time_us()`, `bflb_mtimer_delay_us()`, `bflb_mtimer_delay_ms()` are marked `ATTR_TCM_SECTION` and reside in TCM (Tightly Coupled Memory) for the lowest access latency.

2. **Busy-Wait:** Delay functions use busy-wait and will continuously occupy the CPU. For low-power scenarios, consider using the RTC timer or hardware Timer peripherals.

3. **Frequency Accuracy:** The default 1 MHz is an approximate value. If precise timing is required, measure the actual frequency and return the exact value via `bflb_mtimer_get_freq()`, while also enabling `CONFIG_MTIMER_CUSTOM_FREQUENCE`.

4. **Interrupt Conflict:** The timer interrupt uses IRQ 7. Do not share this interrupt number with other peripherals.

5. **32-bit Safety:** When reading the 64-bit `mtime` register on 32-bit RISC-V platforms, the library function internally uses a double-read anti-rollover mechanism to ensure read consistency.
