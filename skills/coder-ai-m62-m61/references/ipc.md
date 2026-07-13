# IPC API Reference (BL616/BL618)

> **Source:** `bouffalo_sdk/drivers/lhal/include/bflb_ipc.h`  
> **Register Header:** `bouffalo_sdk/drivers/lhal/include/hardware/ipc_reg.h`  
> **Implementation:** `bouffalo_sdk/drivers/lhal/src/bflb_ipc.c`
>
> **⚠️ Chip Support:** IPC (Inter-Processor Communication) is only available on **BL618DG** multi-core chips. BL616 single-core chips do not have this peripheral.

## Overview

The IPC (Inter-Processor Communication) module provides a hardware-level communication mechanism between the AP core (Application Processor) and NP core (Network Processor) in the BL618DG multi-core system. Each IPC instance provides 32 bidirectional signal bits, implementing inter-core synchronization and message passing through a trigger-acknowledge-interrupt mechanism.

**Key Features:**
- 2 IPC instances (IPC0, IPC1)
- 32-bit communication channels per instance
- Bidirectional communication: AP → NP and NP → AP
- Hardware interrupt trigger mechanism
- Independently maskable interrupts per bit

## Base Address

| Peripheral | Base Address | Description |
|------|--------|------|
| IPC0 | `0x20013000` | IPC Instance 0 |
| IPC1 | `0x20016000` | IPC Instance 1 |

> BL616 does not have this peripheral.

---

## Bit Mask Macros

For operating on IPC channel bits:

```c
#define IPC_BITS_MAX   (32)            /* Max number of bits */
#define IPC_BITS_ALL   (0xffffffff)    /* All 32 bits */
#define IPC_BIT_NUM(n) ((0x01 << n) & IPC_BITS_ALL)  /* Specific bit n (0-31) */
```

**Example:**
```c
uint32_t channel_0 = IPC_BIT_NUM(0);   // 0x00000001
uint32_t channel_5 = IPC_BIT_NUM(5);   // 0x00000020
uint32_t multiple  = IPC_BIT_NUM(0) | IPC_BIT_NUM(3);  // 0x00000009
```

---

## LHAL API Functions

### bflb_ipc_init

Initialize the IPC instance.

```c
void bflb_ipc_init(struct bflb_device_s *dev);
```

**Description:** Clear all IPC channels (ACK) and mask all interrupts. Select AP→NP or NP→AP direction based on `dev->sub_idx`:
- `sub_idx = 0`: AP core side (clears AP2NP_ACK and AP2NP_UNMASK)
- `sub_idx = 1`: NP core side (clears NP2AP_ACK and NP2AP_UNMASK)

---

### bflb_ipc_deinit

Deinitialize the IPC instance.

```c
void bflb_ipc_deinit(struct bflb_device_s *dev);
```

---

### bflb_ipc_int_mask

Mask the specified IPC interrupt channels.

```c
void bflb_ipc_int_mask(struct bflb_device_s *dev, uint32_t ipc_bits);
```

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `dev` | `struct bflb_device_s *` | IPC device handle |
| `ipc_bits` | `uint32_t` | Bit mask to mask (use `IPC_BIT_NUM(n)` or `IPC_BITS_ALL`) |

---

### bflb_ipc_int_unmask

Unmask (enable) the specified IPC interrupt channels.

```c
void bflb_ipc_int_unmask(struct bflb_device_s *dev, uint32_t ipc_bits);
```

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `dev` | `struct bflb_device_s *` | IPC device handle |
| `ipc_bits` | `uint32_t` | Bit mask to unmask |

---

### bflb_ipc_trig

Trigger IPC signals, sending an interrupt to the peer core.

```c
void bflb_ipc_trig(struct bflb_device_s *dev, uint32_t ipc_bits);
```

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `dev` | `struct bflb_device_s *` | IPC device handle |
| `ipc_bits` | `uint32_t` | Bit mask to trigger |

**Description:** Writes to the trigger register for the specified bits; hardware automatically generates an interrupt to the peer core (if the bit is not masked).

---

### bflb_ipc_clear

Clear (acknowledge) received IPC signals.

```c
void bflb_ipc_clear(struct bflb_device_s *dev, uint32_t ipc_bits);
```

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `dev` | `struct bflb_device_s *` | IPC device handle |
| `ipc_bits` | `uint32_t` | Bit mask to clear |

**Description:** Writes to the ACK register to clear the specified IPC bits. The receiver should call this function to clear the status after processing signals.

---

### bflb_ipc_get_sta

Get the IPC raw status.

```c
uint32_t bflb_ipc_get_sta(struct bflb_device_s *dev);
```

**Returns:** 32-bit raw status value (bits triggered by peer but not yet acknowledged)

---

### bflb_ipc_get_intsta

Get the IPC interrupt status (Masked Status).

```c
uint32_t bflb_ipc_get_intsta(struct bflb_device_s *dev);
```

**Returns:** 32-bit interrupt status value (bits triggered and not masked), i.e., `RAW_STATUS & ~MASK`

---

## Communication Model

### AP → NP Communication Flow

```
AP Core (sender)                    NP Core (receiver)
     |                                     |
     |-- bflb_ipc_trig(bits) -->           |
     |   (write AP2NP_TRIGGER)             |
     |                                     |--- IPC interrupt fires
     |                                     |-- bflb_ipc_get_intsta()
     |                                     |-- process signal
     |                                     |-- bflb_ipc_clear(bits)
     |                                     |   (write NP2AP_ACK)
```

### NP → AP Communication Flow

```
NP Core (sender)                    AP Core (receiver)
     |                                     |
     |-- bflb_ipc_trig(bits) -->           |
     |   (write NP2AP_TRIGGER)             |
     |                                     |--- IPC interrupt fires
     |                                     |-- bflb_ipc_get_intsta()
     |                                     |-- process signal
     |                                     |-- bflb_ipc_clear(bits)
     |                                     |   (write AP2NP_ACK)
```

---

## Usage Examples

### Example 1: AP-Side Initialization (Receiver)

```c
#include "bflb_ipc.h"

void ap_ipc_init(void)
{
    struct bflb_device_s *ipc0;

    // Get IPC0 device handle (AP side: sub_idx=0)
    ipc0 = bflb_device_get_by_name("ipc0");

    // Initialize IPC
    bflb_ipc_init(ipc0);

    // Unmask interrupts for channel 0 and channel 1
    bflb_ipc_int_unmask(ipc0, IPC_BIT_NUM(0) | IPC_BIT_NUM(1));
}
```

### Example 2: NP Sends Signal to AP

```c
#include "bflb_ipc.h"

void np_send_signal_to_ap(void)
{
    struct bflb_device_s *ipc0;

    // NP side gets IPC0 (sub_idx=1)
    ipc0 = bflb_device_get_by_name("ipc0_np");

    // Trigger channel 0 to AP
    bflb_ipc_trig(ipc0, IPC_BIT_NUM(0));
}
```

### Example 3: AP-Side Interrupt Handling

```c
#include "bflb_ipc.h"

void ipc_interrupt_handler(void)
{
    struct bflb_device_s *ipc0;
    ipc0 = bflb_device_get_by_name("ipc0");

    // Get interrupt status
    uint32_t status = bflb_ipc_get_intsta(ipc0);

    // Process each channel
    if (status & IPC_BIT_NUM(0)) {
        // Process channel 0 signal
        handle_channel_0_message();
        bflb_ipc_clear(ipc0, IPC_BIT_NUM(0));
    }

    if (status & IPC_BIT_NUM(1)) {
        // Process channel 1 signal
        handle_channel_1_message();
        bflb_ipc_clear(ipc0, IPC_BIT_NUM(1));
    }

    // Poll until all signals are processed
    while (bflb_ipc_get_intsta(ipc0)) {
        uint32_t remaining = bflb_ipc_get_intsta(ipc0);
        // Process remaining signals...
        bflb_ipc_clear(ipc0, remaining);
    }
}
```

### Example 4: Inter-Core Sync Example

```c
#include "bflb_ipc.h"

// Signal definitions
#define IPC_SIGNAL_DATA_READY   IPC_BIT_NUM(0)
#define IPC_SIGNAL_ACK          IPC_BIT_NUM(1)
#define IPC_SIGNAL_ERROR        IPC_BIT_NUM(2)

// AP side
void ap_ipc_sync_example(void)
{
    struct bflb_device_s *ipc0;
    ipc0 = bflb_device_get_by_name("ipc0");

    bflb_ipc_init(ipc0);
    bflb_ipc_int_unmask(ipc0, IPC_SIGNAL_DATA_READY | IPC_SIGNAL_ERROR);

    // Wait for NP's data ready signal
    // ... handle in interrupt ...
}

// NP side
void np_ipc_sync_example(void)
{
    struct bflb_device_s *ipc0;
    ipc0 = bflb_device_get_by_name("ipc0_np");

    bflb_ipc_init(ipc0);

    // Prepare data...
    prepare_data();

    // Notify AP data is ready
    bflb_ipc_trig(ipc0, IPC_SIGNAL_DATA_READY);

    // Wait for AP ACK
    bflb_ipc_int_unmask(ipc0, IPC_SIGNAL_ACK);
    // ... handle in interrupt ...
}
```

---

## Register-Level Reference

### IPC Register Layout

The IPC module contains two symmetric register sets: AP→NP channel and NP→AP channel.

#### AP → NP Channel Registers

| Register | Offset | Description |
|--------|------|------|
| `IPC_AP2NP_TRIGGER` | `0x00` | AP→NP trigger register (write to send trigger signal) |
| `IPC_NP2AP_RAW_STATUS` | `0x04` | NP→AP raw status (readable by AP) |
| `IPC_NP2AP_ACK` | `0x08` | NP→AP acknowledge/clear (AP writes to clear) |
| `IPC_NP2AP_UNMASK_SET` | `0x0C` | NP→AP interrupt enable (write 1 to unmask) |
| `IPC_NP2AP_UNMASK_CLEAR` | `0x10` | NP→AP interrupt disable (write 1 to mask) |
| `IPC_NP2AP_LINE_SEL_LOW` | `0x14` | NP→AP line select low 32 bits |
| `IPC_NP2AP_LINE_SEL_HIGH` | `0x18` | NP→AP line select high 32 bits |
| `IPC_NP2AP_STATUS` | `0x1C` | NP→AP interrupt status (masked) |

#### NP → AP Channel Registers

| Register | Offset | Description |
|--------|------|------|
| `IPC_NP2AP_TRIGGER` | `0x20` | NP→AP trigger register (NP writes to send trigger signal) |
| `IPC_AP2NP_RAW_STATUS` | `0x24` | AP→NP raw status (readable by NP) |
| `IPC_AP2NP_ACK` | `0x28` | AP→NP acknowledge/clear (NP writes to clear) |
| `IPC_AP2NP_UNMASK_SET` | `0x2C` | AP→NP interrupt enable (write 1 to unmask) |
| `IPC_AP2NP_UNMASK_CLEAR` | `0x30` | AP→NP interrupt disable (write 1 to mask) |
| `IPC_AP2NP_LINE_SEL_LOW` | `0x34` | AP→NP line select low 32 bits |
| `IPC_AP2NP_LINE_SEL_HIGH` | `0x38` | AP→NP line select high 32 bits |
| `IPC_AP2NP_STATUS` | `0x3C` | AP→NP interrupt status (masked) |

### Register Bit Fields

All IPC registers are 32 bits wide, with each bit corresponding to an IPC channel (0–31):

| Bit | Corresponding Channel |
|-----|---------|
| 0 | Channel 0 |
| 1 | Channel 1 |
| ... | ... |
| 31 | Channel 31 |

**Trigger Register** (offset 0x00 / 0x20): Writing `1` to a bit triggers an interrupt on the peer side (the bit must be unmasked).

**RAW_STATUS Register** (offset 0x04 / 0x24): Read-only, shows all bits triggered by the peer that have not yet been acknowledged.

**ACK Register** (offset 0x08 / 0x28): Write `1` to clear the corresponding RAW_STATUS bits.

**UNMASK_SET Register** (offset 0x0C / 0x2C): Write `1` to allow the corresponding channel to generate interrupts.

**UNMASK_CLEAR Register** (offset 0x10 / 0x30): Write `1` to mask interrupts for the corresponding channel (does not clear already-triggered status).

**STATUS Register** (offset 0x1C / 0x3C): Read-only, returns `RAW_STATUS & UNMASK` (bits triggered and not masked).

### Direct Register Access Example

```c
#include "hardware/ipc_reg.h"
#include "bl618dg_memorymap.h"

void ipc_direct_send_signal(uint32_t bits)
{
    // Direct write to AP→NP trigger register
    putreg32(bits, IPC0_BASE + IPC_AP2NP_TRIGGER_OFFSET);
}

uint32_t ipc_direct_read_status(void)
{
    // Read NP→AP interrupt status
    return getreg32(IPC0_BASE + IPC_NP2AP_STATUS_OFFSET);
}

void ipc_direct_clear(uint32_t bits)
{
    // Clear NP→AP interrupt
    putreg32(bits, IPC0_BASE + IPC_NP2AP_ACK_OFFSET);
}
```

---

## Device Table Configuration

IPC configuration in the BL618DG device table:

| Device Name | Base Address | IRQ Number | sub_idx | Direction |
|--------|--------|--------|---------|------|
| `ipc0` | `IPC0_BASE` (0x20013000) | `BL618DG_IRQ_IPC0_CH0` | 0 | AP side |
| `ipc0_np` | `IPC0_BASE` (0x20013000) | `BL618DG_IRQ_IPC0_CH0` | 1 | NP side |
| `ipc1` | `IPC1_BASE` (0x20016000) | `BL618DG_IRQ_IPC1_CH0` | 0 | AP side |
| `ipc1_np` | `IPC1_BASE` (0x20016000) | `BL618DG_IRQ_IPC1_CH0` | 1 | NP side |

Obtaining device handles:
```c
struct bflb_device_s *ipc0_ap = bflb_device_get_by_name("ipc0");     // AP side
struct bflb_device_s *ipc0_np = bflb_device_get_by_name("ipc0_np");  // NP side
```

---

## Notes

1. **BL618DG Only:** The IPC peripheral is designed specifically for the multi-core BL618DG. BL616 single-core chips do not include this module.

2. **Direction Distinction:** The AP side and NP side of the same IPC instance are distinguished by the `sub_idx` field (0 = AP, 1 = NP); they operate on different register sets.

3. **Interrupt Handling Requirement:** After processing a signal in the ISR, the receiver must call `bflb_ipc_clear()` to clear the corresponding bit; otherwise the interrupt will keep firing.

4. **ROM API Acceleration:** Most IPC functions have corresponding `romapi_bflb_ipc_*` implementations in ROM. The SDK prioritizes ROM versions via conditional compilation for faster execution.

5. **Multi-Channel Concurrency:** All 32 channels can be used simultaneously; multi-channel parallel communication is achieved by combining `IPC_BIT_NUM(n)`.
