# Filesystem Documentation (BL616/BL618)

This document covers the two filesystem implementations available in the Bouffalo SDK: **FATFS** (for SD cards, USB storage) and **LittleFS** (for internal/external Flash, optimized for embedded systems).

---

## FATFS

FATFS is a generic FAT files system module (R0.15) for embedded systems. It's ideal for SD cards and USB storage devices.

### Header
```c
#include "ff.h"
```

### Data Structures

#### FATFS (Filesystem Object)
```c
typedef struct {
    BYTE fs_type;    // Filesystem type (0:not mounted)
    BYTE pdrv;       // Volume hosting physical drive
    BYTE ldrv;       // Logical drive number
    BYTE n_fats;     // Number of FATs (1 or 2)
    WORD id;         // Volume mount ID
    DWORD n_fatent;  // Number of FAT entries
    DWORD fsize;     // Sectors per FAT
    LBA_t volbase;   // Volume base sector
    LBA_t fatbase;   // FAT base sector
    LBA_t dirbase;   // Root directory base sector
    LBA_t database;  // Data base sector
    BYTE win[FF_MAX_SS]; // Disk access window
} FATFS;
```

#### FIL (File Object)
```c
typedef struct {
    FFOBJID obj;     // Object identifier
    BYTE flag;       // File status flags
    BYTE err;        // Abort flag (error code)
    FSIZE_t fptr;    // File read/write pointer
    DWORD clust;     // Current cluster
    LBA_t sect;      // Current sector
    BYTE buf[FF_MAX_SS]; // File data buffer
} FIL;
```

### Key Functions

#### `f_mount` - Mount/Unmount a Logical Drive
```c
FRESULT f_mount(FATFS *fs, const TCHAR *path, BYTE opt);
```
| Parameter | Description |
|-----------|-------------|
| `fs` | Pointer to the filesystem object (can be NULL to unmount) |
| `path` | Drive path (e.g., `"0:"`, `"1:"`) |
| `opt` | Mount option: `0`=unmount, `1`=mount now, `2`=force mount |

**Returns:** `FR_OK` (0) on success, or error code.

---

#### `f_open` - Open or Create a File
```c
FRESULT f_open(FIL *fp, const TCHAR *path, BYTE mode);
```
| Parameter | Description |
|-----------|-------------|
| `fp` | Pointer to the file object |
| `path` | Null-terminated file path |
| `mode` | Access mode flags (see below) |

**Mode Flags:**
| Flag | Value | Description |
|------|-------|-------------|
| `FA_READ` | 0x01 | Read access |
| `FA_WRITE` | 0x02 | Write access |
| `FA_OPEN_EXISTING` | 0x00 | Open existing file |
| `FA_CREATE_NEW` | 0x04 | Create new file (fails if exists) |
| `FA_CREATE_ALWAYS` | 0x08 | Create or truncate to zero length |
| `FA_OPEN_ALWAYS` | 0x10 | Open or create |
| `FA_OPEN_APPEND` | 0x30 | Open and seek to end |

**Returns:** `FR_OK` on success.

---

#### `f_read` - Read Data from File
```c
FRESULT f_read(FIL *fp, void *buff, UINT btr, UINT *br);
```
| Parameter | Description |
|-----------|-------------|
| `fp` | Pointer to file object |
| `buff` | Buffer to store read data |
| `btr` | Number of bytes to read |
| `br` | Pointer to store actual bytes read |

**Returns:** `FR_OK` on success.

---

#### `f_write` - Write Data to File
```c
FRESULT f_write(FIL *fp, const void *buff, UINT btw, UINT *bw);
```
| Parameter | Description |
|-----------|-------------|
| `fp` | Pointer to file object |
| `buff` | Buffer containing data to write |
| `btw` | Number of bytes to write |
| `bw` | Pointer to store actual bytes written |

**Returns:** `FR_OK` on success.

---

### Return Codes (FRESULT)
| Code | Value | Description |
|------|-------|-------------|
| `FR_OK` | 0 | Success |
| `FR_DISK_ERR` | 1 | Disk I/O error |
| `FR_NOT_READY` | 3 | Drive not ready |
| `FR_NO_FILE` | 4 | File not found |
| `FR_NO_PATH` | 5 | Path not found |
| `FR_INVALID_NAME` | 6 | Invalid path name |
| `FR_DENIED` | 7 | Access denied |
| `FR_EXIST` | 8 | File exists |
| `FR_INVALID_OBJECT` | 9 | Invalid object |
| `FR_WRITE_PROTECTED` | 10 | Write protected |
| `FR_INVALID_DRIVE` | 11 | Invalid drive |
| `FR_NOT_ENABLED` | 12 | Volume not enabled |
| `FR_NO_FILESYSTEM` | 13 | No valid FAT volume |
| `FR_TIMEOUT` | 15 | Timeout |

---

### FATFS Working Example

```c
#include "ff.h"
#include "diskio.h"      // For block device drivers

static FATFS fatfs;       // Filesystem object
static FIL fil;           // File object
static uint8_t buffer[256];

void fatfs_example(void)
{
    FRESULT ret;
    UINT bw, br;

    // 1. Mount the filesystem
    ret = f_mount(&fatfs, "0:", 1);
    if (ret != FR_OK) {
        printf("Mount failed: %d\r\n", ret);
        return;
    }

    // 2. Open or create file for writing
    ret = f_open(&fil, "0:/test.txt", FA_CREATE_ALWAYS | FA_WRITE);
    if (ret != FR_OK) {
        printf("Open failed: %d\r\n", ret);
        return;
    }

    // 3. Write data to file
    const char *data = "Hello from FATFS!";
    ret = f_write(&fil, data, strlen(data), &bw);
    if (ret != FR_OK) {
        printf("Write failed: %d\r\n", ret);
    } else {
        printf("Wrote %u bytes\r\n", bw);
    }

    // 4. Close the file
    f_close(&fil);

    // 5. Reopen for reading
    ret = f_open(&fil, "0:/test.txt", FA_READ);
    if (ret != FR_OK) {
        printf("Read open failed: %d\r\n", ret);
        return;
    }

    // 6. Read file contents
    memset(buffer, 0, sizeof(buffer));
    ret = f_read(&fil, buffer, sizeof(buffer) - 1, &br);
    if (ret == FR_OK) {
        printf("Read %u bytes: %s\r\n", br, buffer);
    }

    // 7. Close and unmount
    f_close(&fil);
    f_mount(0, "0:", 0);  // Unmount
}
```

---

## LittleFS

LittleFS is a Flash-friendly filesystem designed for embedded systems. It provides power-loss resilience and is optimized for internal/external Flash storage.

### Header
```c
#include "lfs.h"
```

### Data Structures

#### lfs_config (Block Device Configuration)
```c
struct lfs_config {
    // Opaque user context
    void *context;

    // Block device operations (required)
    int (*read)(const struct lfs_config *c, lfs_block_t block,
            lfs_off_t off, void *buffer, lfs_size_t size);
    int (*prog)(const struct lfs_config *c, lfs_block_t block,
            lfs_off_t off, const void *buffer, lfs_size_t size);
    int (*erase)(const struct lfs_config *c, lfs_block_t block);
    int (*sync)(const struct lfs_config *c);

    // Block device configuration
    lfs_size_t read_size;      // Minimum read size
    lfs_size_t prog_size;       // Minimum program size
    lfs_size_t block_size;      // Erasable block size (bytes)
    lfs_size_t block_count;     // Number of erasable blocks
    int32_t block_cycles;       // Erase cycles before wear leveling
    lfs_size_t cache_size;      // Read/write cache size
    lfs_size_t lookahead_size;  // Allocation lookahead size

    // Optional buffers (use NULL for dynamic allocation)
    void *read_buffer;
    void *prog_buffer;
    void *lookahead_buffer;
};
```

#### lfs_t (Filesystem Instance)
```c
typedef struct lfs {
    lfs_cache_t rcache;
    lfs_cache_t pcache;
    lfs_block_t root[2];
    // ... internal fields
    const struct lfs_config *cfg;
} lfs_t;
```

#### lfs_file_t (File Handle)
```c
typedef struct lfs_file {
    uint16_t id;
    uint8_t type;
    lfs_mdir_t m;
    struct lfs_ctz {
        lfs_block_t head;
        lfs_size_t size;
    } ctz;
    uint32_t flags;
    lfs_off_t pos;
    lfs_block_t block;
    lfs_off_t off;
    lfs_cache_t cache;
    const struct lfs_file_config *cfg;
} lfs_file_t;
```

#### lfs_info (File/Directory Information)
```c
struct lfs_info {
    uint8_t type;           // LFS_TYPE_REG or LFS_TYPE_DIR
    lfs_size_t size;        // File size (REG files only)
    char name[LFS_NAME_MAX+1]; // Null-terminated name
};
```

### Key Functions

#### `lfs_mount` - Mount Filesystem
```c
int lfs_mount(lfs_t *lfs, const struct lfs_config *config);
```
| Parameter | Description |
|-----------|-------------|
| `lfs` | Pointer to lfs_t instance |
| `config` | Block device configuration |

**Returns:** 0 on success, negative error code on failure.

---

#### `lfs_file_open` - Open a File
```c
int lfs_file_open(lfs_t *lfs, lfs_file_t *file,
        const char *path, int flags);
```
| Parameter | Description |
|-----------|-------------|
| `lfs` | Pointer to filesystem instance |
| `file` | Pointer to file handle |
| `path` | Path to file |
| `flags` | Open flags (bitwise OR of flags) |

**Open Flags:**
| Flag | Value | Description |
|------|-------|-------------|
| `LFS_O_RDONLY` | 1 | Read-only access |
| `LFS_O_WRONLY` | 2 | Write-only access |
| `LFS_O_RDWR` | 3 | Read and write |
| `LFS_O_CREAT` | 0x0100 | Create file if not exists |
| `LFS_O_EXCL` | 0x0200 | Fail if file exists |
| `LFS_O_TRUNC` | 0x0400 | Truncate to zero length |
| `LFS_O_APPEND` | 0x0800 | Append to end on write |

**Returns:** 0 on success, negative error code on failure.

---

#### `lfs_file_read` - Read from File
```c
lfs_ssize_t lfs_file_read(lfs_t *lfs, lfs_file_t *file,
        void *buffer, lfs_size_t size);
```
| Parameter | Description |
|-----------|-------------|
| `lfs` | Pointer to filesystem instance |
| `file` | Pointer to open file handle |
| `buffer` | Buffer to store read data |
| `size` | Number of bytes to read |

**Returns:** Number of bytes read, or negative error code.

---

#### `lfs_file_write` - Write to File
```c
lfs_ssize_t lfs_file_write(lfs_t *lfs, lfs_file_t *file,
        const void *buffer, lfs_size_t size);
```
| Parameter | Description |
|-----------|-------------|
| `lfs` | Pointer to filesystem instance |
| `file` | Pointer to open file handle |
| `buffer` | Data to write |
| `size` | Number of bytes to write |

**Returns:** Number of bytes written, or negative error code.

---

### Error Codes
| Code | Value | Description |
|------|-------|-------------|
| `LFS_ERR_OK` | 0 | No error |
| `LFS_ERR_IO` | -5 | I/O error |
| `LFS_ERR_CORRUPT` | -84 | Corrupted filesystem |
| `LFS_ERR_NOENT` | -2 | Entry not found |
| `LFS_ERR_EXIST` | -17 | Entry exists |
| `LFS_ERR_NOTDIR` | -20 | Not a directory |
| `LFS_ERR_ISDIR` | -21 | Is a directory |
| `LFS_ERR_NOTEMPTY` | -39 | Directory not empty |
| `LFS_ERR_BADF` | -9 | Bad file descriptor |
| `LFS_ERR_FBIG` | -27 | File too large |
| `LFS_ERR_INVAL` | -22 | Invalid parameter |
| `LFS_ERR_NOSPC` | -28 | No space left |
| `LFS_ERR_NOMEM` | -12 | Out of memory |
| `LFS_ERR_NOATTR` | -61 | No attribute |
| `LFS_ERR_NAMETOOLONG` | -36 | Name too long |

---

### LittleFS Working Example

```c
#include "lfs.h"
#include "lfs_util.h"     // Platform-specific block device

// LittleFS instance
static lfs_t lfs;

// Block device configuration
static const struct lfs_config cfg = {
    .context = NULL,

    // Block device operations (implement these for your hardware)
    .read  = block_read,
    .prog  = block_prog,
    .erase = block_erase,
    .sync  = block_sync,

    // Configuration (adjust for your Flash)
    .read_size      = 256,
    .prog_size      = 256,
    .block_size     = 4096,
    .block_count    = 1024,       // 4MB Flash
    .block_cycles   = 1000,
    .cache_size     = 256,
    .lookahead_size = 256,

    // Dynamic allocation (can use static buffers)
    .read_buffer    = NULL,
    .prog_buffer    = NULL,
    .lookahead_buffer = NULL,
};

void littlefs_example(void)
{
    int ret;
    lfs_file_t file;
    uint8_t buffer[256];

    // 1. Mount the filesystem
    ret = lfs_mount(&lfs, &cfg);
    if (ret < 0) {
        printf("Mount failed: %d\r\n", ret);
        // May need to format on first use:
        // lfs_format(&lfs, &cfg);
        // lfs_mount(&lfs, &cfg);
        return;
    }

    // 2. Open file for writing (create if not exists)
    ret = lfs_file_open(&lfs, &file, "/test.txt",
                        LFS_O_WRONLY | LFS_O_CREAT | LFS_O_TRUNC);
    if (ret < 0) {
        printf("Open write failed: %d\r\n", ret);
        lfs_unmount(&lfs);
        return;
    }

    // 3. Write data
    const char *data = "Hello from LittleFS!";
    lfs_ssize_t bw = lfs_file_write(&lfs, &file, data, strlen(data));
    if (bw < 0) {
        printf("Write failed: %ld\r\n", (long)bw);
    } else {
        printf("Wrote %ld bytes\r\n", (long)bw);
    }

    // 4. Close file
    lfs_file_close(&lfs, &file);

    // 5. Open for reading
    ret = lfs_file_open(&lfs, &file, "/test.txt", LFS_O_RDONLY);
    if (ret < 0) {
        printf("Open read failed: %d\r\n", ret);
        lfs_unmount(&lfs);
        return;
    }

    // 6. Read data
    memset(buffer, 0, sizeof(buffer));
    lfs_ssize_t br = lfs_file_read(&lfs, &file, buffer, sizeof(buffer) - 1);
    if (br >= 0) {
        printf("Read %ld bytes: %s\r\n", (long)br, buffer);
    }

    // 7. Close and unmount
    lfs_file_close(&lfs, &file);
    lfs_unmount(&lfs);
}
```

---

## Comparison

| Feature | FATFS | LittleFS |
|---------|-------|----------|
| **Target Storage** | SD cards, USB | Internal/External Flash |
| **Power Loss Safety** | Limited | Yes (copy-on-write) |
| **Wear Leveling** | No | Yes (built-in) |
| **RAM Usage** | Higher | Lower |
| **Max File Name** | 255 (with LFN) | 255 |
| **Directory Structure** | Flat | Hierarchical |
| **Example Use Case** | Data logging to SD | Config storage in Flash |

---

## Flash Block Device Implementation (LittleFS)

For LittleFS, you must implement block device operations for your specific Flash hardware. Example for SPI Flash:

```c
// SPI Flash device context
typedef struct {
    spi_device_t *spi;
    uint32_t flash_size;
} spi_flash_ctx_t;

// Read from Flash
int spi_flash_read(const struct lfs_config *c, lfs_block_t block,
        lfs_off_t off, void *buffer, lfs_size_t size)
{
    spi_flash_ctx_t *ctx = c->context;
    uint32_t addr = block * c->block_size + off;

    spi_transfer(ctx->spi, addr, buffer, size);
    return LFS_ERR_OK;
}

// Erase Flash block
int spi_flash_erase(const struct lfs_config *c, lfs_block_t block)
{
    spi_flash_ctx_t *ctx = c->context;
    uint32_t addr = block * c->block_size;

    spi_erase(ctx->spi, addr, c->block_size);
    return LFS_ERR_OK;
}

// Program Flash
int spi_flash_prog(const struct lfs_config *c, lfs_block_t block,
        lfs_off_t off, const void *buffer, lfs_size_t size)
{
    spi_flash_ctx_t *ctx = c->context;
    uint32_t addr = block * c->block_size + off;

    spi_write(ctx->spi, addr, buffer, size);
    return LFS_ERR_OK;
}

// Sync Flash
int spi_flash_sync(const struct lfs_config *c)
{
    // Wait for pending operations
    spi_wait_ready();
    return LFS_ERR_OK;
}
```

---

## Notes

- Both filesystems use `FRESULT` (FATFS) and negative error codes (LittleFS) for error handling
- Always check return values and close files properly
- For LittleFS, implement proper block device drivers for your specific Flash hardware
- Consider using FATFS for large removable storage and LittleFS for embedded Flash
