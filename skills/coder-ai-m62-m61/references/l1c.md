# L1C (L1 Cache) API Reference (BL616/BL618)

> **Source:** `bouffalo_sdk/drivers/lhal/include/bflb_l1c.h`  
> **Implementation:** `bouffalo_sdk/drivers/lhal/src/bflb_l1c.c`  
> **Chip Support:** BL602, BL702/BL702L, BL616/BL618, BL618DG (except LP core)

## Overview

The L1C module provides control interfaces for L1 Instruction Cache (I-Cache) and Data Cache (D-Cache). On the BL616/BL618 series chips, it is implemented based on the RISC-V NMSIS core layer, controlling caches through ROM API jumps or direct CSI/NMSIS interface operations. Older platforms such as BL602/BL702 have different underlying implementations.

**Key Features:**
- I-Cache enable/disable/invalidate
- D-Cache enable/disable/clean/invalidate
- Cache operations on specified address ranges
- Cache hit/miss count statistics
- Cache write policy configuration (WT/WB/WA)
- Critical functions located in TCM segment to guarantee low latency

## Cache Line Size

```c
// BL616/BL616CL/BL618DG (non-LP core, D0 core)
#define BFLB_CACHE_LINE_SIZE 32  // or 64 (depending on CPU type)

// Other platforms (BL602/BL702, etc.)
#define BFLB_CACHE_LINE_SIZE 4   // word alignment only
```

> **Note:** On BL616/BL618 platforms, D-Cache related operations (such as clean/invalidate range) internally call `bflb_check_cache_addr()` to verify address validity, ensuring operations only target cacheable address ranges.

---

## Base Address (Performance Counters)

| Register Area | Base Address | Description |
|-----------|--------|------|
| L1C Performance Counters | `0x40009000` | BL702/BL702L and some platforms only |

> BL616/BL618 operate caches via the NMSIS core interface and do not directly manipulate registers.

---

## API Functions

### 1. I-Cache Control

#### bflb_l1c_icache_enable

Enable the instruction cache.

```c
void bflb_l1c_icache_enable(void);
```

**Description:** Internally calls ROM API first (`romapi_bflb_l1c_icache_enable`), otherwise enables via NMSIS `EnableICache()`.

---

#### bflb_l1c_icache_disable

Disable the instruction cache.

```c
void bflb_l1c_icache_disable(void);
```

---

#### bflb_l1c_icache_invalid_all

Invalidate the entire instruction cache.

```c
void bflb_l1c_icache_invalid_all(void);
```

**Description:** Located in TCM segment. Internally calls ROM API first, otherwise operates via NMSIS `MInvalICache()`.

---

#### bflb_l1c_icache_invalid_range

Invalidate instruction cache for a specified address range.

```c
void bflb_l1c_icache_invalid_range(void *addr, uint32_t size);
```

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `addr` | `void *` | Start address |
| `size` | `uint32_t` | Invalidation range size (bytes) |

**Description:** Located in TCM segment. Internally calls `bflb_check_cache_addr()` to verify address validity, then executes via NMSIS `MInvalICacheRange()`.

---

### 2. D-Cache Control

#### bflb_l1c_dcache_enable

Enable the data cache.

```c
void bflb_l1c_dcache_enable(void);
```

---

#### bflb_l1c_dcache_disable

Disable the data cache.

```c
void bflb_l1c_dcache_disable(void);
```

---

#### bflb_l1c_dcache_clean_all

Clean (write back) the entire data cache.

```c
void bflb_l1c_dcache_clean_all(void);
```

**Description:** Located in TCM segment. Writes dirty cache lines back to memory, retaining cache data. Internally executes via NMSIS `MFlushDCache()`.

---

#### bflb_l1c_dcache_invalidate_all

Invalidate the entire data cache.

```c
void bflb_l1c_dcache_invalidate_all(void);
```

**Description:** Located in TCM segment. Discards all cached data (no write-back). Internally executes via NMSIS `MInvalDCache()`.

---

#### bflb_l1c_dcache_clean_invalidate_all

Clean and invalidate the entire data cache.

```c
void bflb_l1c_dcache_clean_invalidate_all(void);
```

**Description:** Located in TCM segment. Writes dirty data back to memory first, then invalidates. Internally executes via NMSIS `MFlushInvalDCache()`. This is the safest full cache flush operation.

---

#### bflb_l1c_dcache_clean_range

Clean (write back) data cache for a specified address range.

```c
void bflb_l1c_dcache_clean_range(void *addr, uint32_t size);
```

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `addr` | `void *` | Start address |
| `size` | `uint32_t` | Range size (bytes) |

**Description:** Located in TCM segment. Writes dirty cache lines within the specified range back to memory.

---

#### bflb_l1c_dcache_invalidate_range

Invalidate data cache for a specified address range.

```c
void bflb_l1c_dcache_invalidate_range(void *addr, uint32_t size);
```

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `addr` | `void *` | Start address |
| `size` | `uint32_t` | Range size (bytes) |

**Description:** Located in TCM segment. Discards cached data within the specified range (no write-back). Ensure data has been written back before use.

---

#### bflb_l1c_dcache_clean_invalidate_range

Clean and invalidate data cache for a specified address range.

```c
void bflb_l1c_dcache_clean_invalidate_range(void *addr, uint32_t size);
```

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `addr` | `void *` | Start address |
| `size` | `uint32_t` | Range size (bytes) |

**Description:** Located in TCM segment. Writes dirty data back to memory first, then invalidates. This is the safest partial cache flush method.

---

### 3. Performance Counters

#### bflb_l1c_hit_count_get

Get cache hit count (64-bit).

```c
void bflb_l1c_hit_count_get(uint32_t *hit_count_low, uint32_t *hit_count_high);
```

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `hit_count_low` | `uint32_t *` | Output: Lower 32 bits of hit count |
| `hit_count_high` | `uint32_t *` | Output: Upper 32 bits of hit count |

**Description:** Weak function (`__WEAK`). Reads registers `0x40009004` and `0x40009008`. Only valid on BL702/BL702L and similar platforms.

---

#### bflb_l1c_miss_count_get

Get cache miss count.

```c
uint32_t bflb_l1c_miss_count_get(void);
```

**Returns:** Miss count value (32-bit)

**Description:** Weak function (`__WEAK`). Reads register `0x4000900C`.

---

### 4. Write Policy Configuration

#### bflb_l1c_cache_write_set

Configure cache write policy.

```c
void bflb_l1c_cache_write_set(uint8_t wt_en, uint8_t wb_en, uint8_t wa_en);
```

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `wt_en` | `uint8_t` | Write-Through enable (1=enable) |
| `wb_en` | `uint8_t` | Write-Back enable (1=enable) |
| `wa_en` | `uint8_t` | Write-Allocate enable (1=enable) |

**Description:** Weak function (`__WEAK`), located in TCM segment. Configures register `0x40009000`:
- Bit 4: Write-Through
- Bit 5: Write-Back  
- Bit 6: Write-Allocate

Only valid on BL702/BL702L platforms.

---

## Usage Examples

### Example 1: Cache Synchronization Before and After DMA Transfer

```c
#include "bflb_l1c.h"

uint8_t dma_buffer[1024] __attribute__((aligned(32)));

void dma_transfer_example(void)
{
    // Prepare DMA send data
    fill_buffer(dma_buffer, sizeof(dma_buffer));
    
    // Before DMA send: write data from cache back to memory
    bflb_l1c_dcache_clean_range(dma_buffer, sizeof(dma_buffer));
    
    // Start DMA transfer
    dma_start_transfer(dma_buffer, sizeof(dma_buffer));
    
    // ... wait for DMA to complete ...
    
    // Before DMA receive: invalidate cache to avoid reading stale data
    bflb_l1c_dcache_invalidate_range(dma_buffer, sizeof(dma_buffer));
    
    // Now reading dma_buffer will fetch fresh data directly from memory
}
```

### Example 2: Flush Instruction Cache After Firmware OTA

```c
#include "bflb_l1c.h"

void ota_firmware_update(void)
{
    uint32_t new_fw_addr = 0x23000000;
    uint32_t new_fw_size = 0x80000;
    
    // Write new firmware to Flash (via PSRAM or other cached areas)
    flash_write(new_fw_addr, new_firmware_data, new_fw_size);
    
    // Firmware area may be in D-Cache, write back first
    bflb_l1c_dcache_clean_range((void *)new_fw_addr, new_fw_size);
    
    // Invalidate I-Cache to ensure new firmware is executed
    bflb_l1c_icache_invalid_range((void *)new_fw_addr, new_fw_size);
    
    // Jump to new firmware
    jump_to_firmware(new_fw_addr);
}
```

### Example 3: Cache Performance Statistics

```c
#include "bflb_l1c.h"

void cache_perf_test(void)
{
    uint32_t hit_low = 0, hit_high = 0;
    uint32_t miss_before, miss_after;
    
    // Record counters before test
    miss_before = bflb_l1c_miss_count_get();
    
    // Execute operation under test
    data_processing_benchmark();
    
    // Record counters after test
    miss_after = bflb_l1c_miss_count_get();
    bflb_l1c_hit_count_get(&hit_low, &hit_high);
    
    printf("Cache misses during test: %u\n", miss_after - miss_before);
    printf("Total hit count: 0x%08x%08x\n", hit_high, hit_low);
}
```

### Example 4: Cache Maintenance in Multicore Environment

```c
#include "bflb_l1c.h"

void shared_memory_update(void *shared_buf, uint32_t size)
{
    // CPU0 updates shared memory data
    update_data(shared_buf, size);
    
    // Write back D-Cache to make data visible to NP core
    bflb_l1c_dcache_clean_range(shared_buf, size);
    
    // Notify NP core that data has been updated
    notify_np_core();
}

void shared_memory_read(void *shared_buf, uint32_t size)
{
    // NP core has updated data; CPU0 invalidates cache before reading
    bflb_l1c_dcache_invalidate_range(shared_buf, size);
    
    // Now reading the latest data written by NP core
    process_data(shared_buf, size);
}
```

---

## Operation Summary

| Operation | I-Cache | D-Cache | Cache Line |
|------|---------|---------|------------|
| **Enable** | `bflb_l1c_icache_enable()` | `bflb_l1c_dcache_enable()` | — |
| **Disable** | `bflb_l1c_icache_disable()` | `bflb_l1c_dcache_disable()` | — |
| **Clean** | — | `bflb_l1c_dcache_clean_all()` | `bflb_l1c_dcache_clean_range()` |
| **Invalidate** | `bflb_l1c_icache_invalid_all()` | `bflb_l1c_dcache_invalidate_all()` | `bflb_l1c_icache_invalid_range()` / `_dcache_invalidate_range()` |
| **Clean+Invalidate** | — | `bflb_l1c_dcache_clean_invalidate_all()` | `bflb_l1c_dcache_clean_invalidate_range()` |

### Quick Reference by Scenario

| Scenario | Recommended Operation |
|------|---------|
| Before DMA send data | `bflb_l1c_dcache_clean_range()` |
| After DMA receive data | `bflb_l1c_dcache_invalidate_range()` |
| After OTA/Flash firmware write | `bflb_l1c_icache_invalid_range()` |
| After multicore shared memory write | `bflb_l1c_dcache_clean_range()` |
| Before multicore shared memory read | `bflb_l1c_dcache_invalidate_range()` |
| System reset / initialization | `bflb_l1c_dcache_clean_invalidate_all()` + `bflb_l1c_icache_invalid_all()` |

---

## Platform Differences

| Platform | I-Cache | D-Cache | Performance Counters | Write Policy Config |
|------|---------|---------|-----------|-----------|
| BL616/BL618 | NMSIS core | NMSIS core | ❌ | ❌ |
| BL618DG (AP/NP) | NMSIS core | NMSIS core | ❌ | ❌ |
| BL702/BL702L | L1C registers | L1C registers | ✅ | ✅ |
| BL602 | No-op | No-op | ❌ | ❌ |

> On BL616/BL618, the performance counter and write policy configuration functions are weak function stubs; they are only effective on BL702/BL702L.
