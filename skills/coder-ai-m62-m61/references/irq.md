# IRQ/Interrupt API Documentation

**Chip Support:** BL602, BL616/BL618, BL618DG, BL702, BL702L

**Header:** `drivers/lhal/include/bflb_irq.h`  
**Source:** `drivers/lhal/src/bflb_irq.c`

---

## Overview

The IRQ module provides a unified interrupt management interface for Bouffalo Lab chips. It wraps the underlying RISC-V interrupt controllers (CLIC on BL602/BL702, ECLIC on BL616/BL618) and provides:

- Global interrupt enable/disable with state preservation
- Interrupt handler registration/deregistration  
- Per-IRQ enable/disable control
- Pending bit manipulation
- Interrupt priority configuration

---

## Data Structures

### `irq_callback`

```c
#ifndef BL_IOT_SDK
typedef void (*irq_callback)(int irq, void *arg);  // BL616/BL618: receives irq number + user arg
#else
typedef void (*irq_callback)(void *arg);           // BL_IOT_SDK variant: only user arg
#endif
```

### `struct bflb_irq_info_s`

```c
struct bflb_irq_info_s {
    irq_callback handler;  // Interrupt handler function pointer
    void *arg;            // User data passed to handler
};
```

---

## API Reference

### `void bflb_irq_initialize(void)`

Initializes the interrupt subsystem. Sets all IRQ vectors to a default unexpected-isr handler that prints an error message.

**Notes:**
- Called automatically by the startup code / `bflb_main` 
- Not needed for normal use; provided for completeness

---

### `uintptr_t bflb_irq_save(void)`

**Atomically** disables global interrupts (MIE bit in `mstatus`) and returns the previous interrupt state.

**Returns:** Previous `mstatus` value (bits containing prior MIE state)

**Implementation (register-level):**
```c
// RISC-V CSR operation: clear MIE bit in mstatus, return old value
asm volatile("csrrc %0, mstatus, %1"
              : "=r"(oldstat)
              : "r"(MSTATUS_MIE));
```

**Usage - Critical Section:**
```c
uintptr_t flags = bflb_irq_save();
// ... critical code that must not be interrupted ...
bflb_irq_restore(flags);
```

---

### `void bflb_irq_restore(uintptr_t flags)`

Restores global interrupt state from a previous `bflb_irq_save()` call.

**Parameters:**
- `flags` - Value returned by `bflb_irq_save()`

**Implementation (register-level):**
```c
// RISC-V CSR write: restore mstatus
asm volatile("csrw mstatus, %0"
              : /* no output */
              : "r"(flags));
```

---

### `int bflb_irq_attach(int irq, irq_callback isr, void *arg)`

Registers an interrupt handler for the specified IRQ number.

**Parameters:**
- `irq` - IRQ number (per chip, typically 0-63)
- `isr` - Callback function
- `arg` - User data passed to callback

**Returns:** `0` on success, `-EINVAL` if `irq >= CONFIG_IRQ_NUM`

**Usage:**
```c
void my_uart_isr(int irq, void *arg) {
    // Handle UART interrupt
    uint8_t c = bflb_uart_getchar(uartx);
    // ...
}

// In main():
bflb_irq_attach(uartx->irq_num, my_uart_isr, NULL);
bflb_irq_enable(uartx->irq_num);
```

**Notes:**
- For BL618DG LP core with level-2 interrupts (`irq >= BL618DG_IRQ_LEVEL2_BASE`), the LP core routes through a single parent IRQ
- For BL_IOT_SDK variant, calls `bl_irq_register_with_ctx()` internally

---

### `int bflb_irq_detach(int irq)`

Removes the interrupt handler for the specified IRQ, resetting it to the unexpected-isr stub.

**Parameters:**
- `irq` - IRQ number

**Returns:** `0` on success, `-EINVAL` if `irq >= CONFIG_IRQ_NUM`

---

### `void bflb_irq_enable(int irq)`

Enables the specified interrupt line at the interrupt controller.

**Parameters:**
- `irq` - IRQ number

**Implementation (chip variants):**

| Chip | Implementation |
|------|----------------|
| BL602/BL702/BL702L | `putreg8(1, CLIC_HART0_BASE + CLIC_INTIE_OFFSET + irq)` |
| BL616/BL618 (ROM API) | `romapi_bflb_irq_enable(irq)` |
| BL618DG LP core | `csi_vic_enable_irq()` (routes level-2 if needed) |
| BL618DG (non-A0) | `__ECLIC_EnableIRQ(irq)` |
| Others | `csi_vic_enable_irq(irq)` |

**Register-level (ECLIC on BL616/BL618):**
```
ECLIC INTIE[irq] = 1   // Interrupt enable bit for this IRQ
```

---

### `void bflb_irq_disable(int irq)`

Disables the specified interrupt line at the interrupt controller.

**Parameters:**
- `irq` - IRQ number

**Implementation (chip variants):**

| Chip | Implementation |
|------|----------------|
| BL602/BL702/BL702L | `putreg8(0, CLIC_HART0_BASE + CLIC_INTIP_OFFSET + irq)` |
| BL616/BL618 (ROM API) | `romapi_bflb_irq_disable(irq)` |
| BL618DG LP core | `csi_vic_disable_irq()` |
| BL618DG (non-A0) | `__ECLIC_DisableIRQ(irq)` |
| Others | `csi_vic_disable_irq(irq)` |

---

### `void bflb_irq_set_pending(int irq)`

Forces the interrupt to be pending (software-triggered).

**Parameters:**
- `irq` - IRQ number

**Implementation:**
- BL602/BL702: `putreg8(1, CLIC_HART0_BASE + CLIC_INTIP_OFFSET + irq)`
- Others: `__ECLIC_SetPendingIRQ(irq)` or `csi_vic_set_pending_irq(irq)`

---

### `void bflb_irq_clear_pending(int irq)`

Clears the pending status of an interrupt.

**Parameters:**
- `irq` - IRQ number

**Implementation:**
- BL602/BL702: `putreg8(0, CLIC_HART0_BASE + CLIC_INTIP_OFFSET + irq)`
- Others: `__ECLIC_ClearPendingIRQ(irq)` or `csi_vic_clear_pending_irq(irq)`

---

### `void bflb_irq_set_nlbits(uint8_t nlbits)`

Sets the number of level bits (`nlbits`) in the CLIC/ECLIC configuration. This controls how many bits are used for interrupt level vs. priority.

**Parameters:**
- `nlbits` - Number of level bits (0-15), stored as `NLbits[3:0]`

**Register-level (CLIC):**
```
CLIC CFG = (CLIC CFG & 0xe1) | (nlbits << 1)
```

**Register-level (ECLIC):**
```
ECLIC->CLICCFG = (nlbits << 1) | 1
```

**Notes:**
- Only meaningful for chips with CLIC/ECLIC
- Default value is typically set in startup code

---

### `void bflb_irq_set_priority(int irq, uint8_t preemptprio, uint8_t subprio)`

Sets the priority for an interrupt.

**Parameters:**
- `irq` - IRQ number
- `preemptprio` - Preemption priority (higher = can preempt lower)
- `subprio` - Sub-priority (used when multiple IRQs with same preemptprio are pending)

**Implementation (ECLIC on BL616/BL618):**
```c
__ECLIC_SetLevelIRQ(irq, preemptprio);   // Set level
__ECLIC_SetPriorityIRQ(irq, subprio);     // Set priority within level
```

**Register-level (ECLIC):**
```
ECLIC INTATTR[irq] = (preemptprio << (8 - nlbits)) | (subprio << 4)
```

**Implementation (CLIC on BL602/BL702):**
```c
// nlbits from CLIC CFG register
clicIntCfg = getreg8(CLIC_HART0_BASE + CLIC_INTCFG_OFFSET + irq);
putreg8((clicIntCfg & 0xf) | (preemptprio << (8 - nlbits)) | ((subprio & (0xf >> nlbits)) << 4),
        CLIC_HART0_BASE + CLIC_INTCFG_OFFSET + irq);
```

---

## Complete Working Example

### UART Interrupt (BL616/BL618)

```c
#include "bflb_uart.h"
#include "bflb_irq.h"
#include "bflb_mtimer.h"
#include "board.h"

struct bflb_device_s *uartx;
static uint8_t rx_buf[1024];
static uint32_t rx_count = 0;

void uart_isr(int irq, void *arg)
{
    uint32_t intstatus = bflb_uart_get_intstatus(uartx);

    // RX FIFO threshold reached
    if (intstatus & UART_INTSTS_RX_FIFO) {
        while (bflb_uart_rxavailable(uartx)) {
            rx_buf[rx_count++] = bflb_uart_getchar(uartx);
        }
    }
    
    // RX timeout (no activity)
    if (intstatus & UART_INTSTS_RTO) {
        bflb_uart_int_clear(uartx, UART_INTCLR_RTO);
        while (bflb_uart_rxavailable(uartx)) {
            rx_buf[rx_count++] = bflb_uart_getchar(uartx);
        }
    }
    
    // TX FIFO empty
    if (intstatus & UART_INTSTS_TX_FIFO) {
        // Handle TX
        bflb_uart_txint_mask(uartx, true);
    }
}

int main(void)
{
    board_init();
    board_uartx_gpio_init();

    // Get UART device handle
    uartx = bflb_device_get_by_name(DEFAULT_TEST_UART);

    // Configure UART
    struct bflb_uart_config_s cfg = {
        .baudrate = 2000000,
        .data_bits = UART_DATA_BITS_8,
        .stop_bits = UART_STOP_BITS_1,
        .parity = UART_PARITY_NONE,
        .flow_ctrl = 0,
        .tx_fifo_threshold = 7,
        .rx_fifo_threshold = 7,
    };
    bflb_uart_init(uartx, &cfg);

    // Unmask UART interrupts at UART level
    bflb_uart_txint_mask(uartx, false);
    bflb_uart_rxint_mask(uartx, false);

    // Register and enable UART IRQ
    bflb_irq_attach(uartx->irq_num, uart_isr, NULL);
    bflb_irq_enable(uartx->irq_num);

    while (1) {
        if (rx_count > 0) {
            // Process received data
            for (uint32_t i = 0; i < rx_count; i++) {
                printf("0x%02x\r\n", rx_buf[i]);
            }
            rx_count = 0;
        }
        bflb_mtimer_delay_ms(100);
    }
}
```

### Timer Interrupt (SysTick/MTimer)

```c
#include "bflb_mtimer.h"
#include "bflb_irq.h"

volatile uint32_t tick_count = 0;

void systick_handler(void)
{
    tick_count++;
    printf("Tick: %lu\r\n", tick_count);
}

int main(void)
{
    // Configure 1ms tick - this internally uses bflb_irq_attach/enable
    bflb_mtimer_config(1000, systick_handler);  // 1000 ticks @ 1MHz = 1ms

    while (1) {
        // Do work
    }
}
```

### Critical Section Example

```c
#include "bflb_irq.h"

// Shared variable modified in ISR and main code
static volatile uint32_t shared_counter = 0;

void timer_isr(int irq, void *arg)
{
    shared_counter++;
}

int main(void)
{
    // Setup timer interrupt
    bflb_mtimer_config(1000, systick_handler);
    
    // Critical section - disable interrupts for atomic access
    uintptr_t flags = bflb_irq_save();
    
    // Safe to access shared_counter - no interrupt can fire now
    shared_counter++;
    if (shared_counter > 100) {
        shared_counter = 0;
    }
    
    // Restore interrupts
    bflb_irq_restore(flags);
}
```

---

## Interrupt Controller Register Map

### CLIC (BL602/BL702)

| Register | Offset | Description |
|----------|--------|-------------|
| `CLIC_HART0_BASE` | 0xD2000000 | Base address |
| `CLIC_CFG_OFFSET` | 0x0 | Configuration (nlbits) |
| `CLIC_INTIE_OFFSET` | 0x1000 + irq | Interrupt Enable |
| `CLIC_INTIP_OFFSET` | 0x2000 + irq | Interrupt Pending |
| `CLIC_INTCFG_OFFSET` | 0x3000 + irq | Interrupt Config (priority) |

### ECLIC (BL616/BL618)

The ECLIC is an enhanced CLIC with additional features. Registers are similar but with ECLIC prefix.

---

## IRQ Numbers (BL616/BL618)

Typical IRQ assignments (see chip-specific header for full list):

| IRQ | Source |
|-----|--------|
| 0-3 | Reserved (SOC) |
| 4 | TIMER0 |
| 5 | TIMER1 |
| 6 | TIMER2 |
| 7 | SysTick / MTimer |
| 8 | UART0 |
| 9 | UART1 |
| ... | See `bflb_irq.h` or chip RM |

**Note:** IRQ numbers are chip-specific. Use `device->irq_num` from the bflb device handle rather than hardcoding numbers.

---

## Error Handling

All functions that return an error code use the standard pattern:
- `0` or positive: Success
- Negative (`-EINVAL`): Invalid argument (irq out of range)

---

## Thread Safety

- `bflb_irq_save()` / `bflb_irq_restore()` are safe for use in both ISR and thread context
- `bflb_irq_attach()` / `bflb_irq_detach()` should only be called when the IRQ is disabled
- Do not call `bflb_irq_attach()` from within an ISR handler

---

## See Also

- `bflb_uart.h` - UART driver (uses IRQ)
- `bflb_mtimer.h` - Millisecond timer (uses IRQ 7)
- Chip Reference Manual for ECLIC/CLIC details
