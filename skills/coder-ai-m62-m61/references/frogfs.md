# FrogFS Embedded Read-Only Filesystem

## Overview

FrogFS is a lightweight read-only filesystem designed specifically for embedded scenarios, primarily used for storing multimedia resources such as fonts and images needed by the LVGL graphics library. The filesystem is deeply optimized with perfect support for XIP (eXecute In Place) mode, allowing data to be read and executed directly from Flash storage without needing to be fully loaded into RAM.

FrogFS's design philosophy is to minimize resource usage while providing efficient file access capabilities, making it ideal for multimedia resource storage scenarios on low-resource embedded chips like the BL618.

## Version and Identification

| Attribute | Value |
|------|-----|
| Version | FROGFS_VER_MAJOR.MINOR = 1.0 |
| Magic Number | FROGFS_MAGIC = 0x474F5246 ('FROG') |

The filesystem image header contains a magic number identifier for quickly identifying and validating FrogFS format validity.

## Core Data Types

### Entry Type

```c
typedef enum frogfs_entry_type_t {
    FROGFS_ENTRY_TYPE_DIR,    // Directory type
    FROGFS_ENTRY_TYPE_FILE,   // File type
} frogfs_entry_type_t;
```

### Filesystem Handle

```c
typedef struct frogfs_fs_t frogfs_fs_t;
```

### File/Directory Handles

```c
typedef struct frogfs_fh_t frogfs_fh_t;  // File handle
typedef struct frogfs_dh_t frogfs_dh_t;  // Directory handle
```

### File Information Structure

```c
typedef struct frogfs_stat_t {
    frogfs_entry_type_t type;      // Entry type
    size_t size;                    // Decompressed file size
    frogfs_comp_algo_t compression; // Compression algorithm type
    size_t compressed_sz;           // Compressed size
} frogfs_stat_t;
```

### Configuration Structure

```c
typedef struct frogfs_config_t {
    const void *addr;  // Filesystem address in memory
} frogfs_config_t;
```

## Core API

### Initialization and Destruction

#### frogfs_mount / frogfs_init

```c
frogfs_fs_t *frogfs_init(const frogfs_config_t *conf);
```

Mount a FrogFS image by passing the filesystem configuration (primarily the image address in memory). Returns a filesystem handle.

#### frogfs_unmount / frogfs_deinit

```c
void frogfs_deinit(frogfs_fs_t *fs);
```

Unmount the filesystem and release associated resources.

### File Operations

#### frogfs_open

```c
frogfs_fh_t *frogfs_open(const frogfs_fs_t *fs, const frogfs_entry_t *entry,
        unsigned int flags);
```

Open a file or directory by path. `flags` supports the `FROGFS_OPEN_RAW` flag to open files in raw mode (without decompression), suitable for scenarios requiring transmission of compressed data (e.g., via HTTP).

#### frogfs_close

```c
void frogfs_close(frogfs_fh_t *fh);
```

Close an opened file handle.

#### frogfs_read

```c
ssize_t frogfs_read(frogfs_fh_t *fh, void *buf, size_t len);
```

Read data from an opened file. Returns the actual number of bytes read.

#### frogfs_lseek / frogfs_seek

```c
ssize_t frogfs_seek(frogfs_fh_t *fh, long offset, int mode);
```

Move the file pointer. `mode` options: `SEEK_SET` (relative to file beginning), `SEEK_CUR` (relative to current position), `SEEK_END` (relative to file end).

#### frogfs_tell

```c
size_t frogfs_tell(frogfs_fh_t *fh);
```

Get the current file pointer position.

### Directory Operations

#### frogfs_list / frogfs_opendir + frogfs_readdir

```c
frogfs_dh_t *frogfs_opendir(frogfs_fs_t *fs, const frogfs_entry_t *entry);
const frogfs_entry_t *frogfs_readdir(frogfs_dh_t *dh);
```

Open a directory and read entry contents one by one.

#### frogfs_closedir

```c
void frogfs_closedir(frogfs_dh_t *dh);
```

Close a directory handle.

### Entry Queries

#### frogfs_stat

```c
void frogfs_stat(const frogfs_fs_t *fs, const frogfs_entry_t *entry,
        frogfs_stat_t *st);
```

Get detailed information about a file or directory (type, size, compression algorithm, etc.).

#### frogfs_get_entry

```c
const frogfs_entry_t *frogfs_get_entry(const frogfs_fs_t *fs,
        const char *path);
```

Get an entry pointer by path.

#### frogfs_is_dir / frogfs_is_file

```c
int frogfs_is_dir(const frogfs_entry_t *entry);
int frogfs_is_file(const frogfs_entry_t *entry);
```

Determine entry type.

## FROGFS_OPEN_RAW Flag

```c
#define FROGFS_OPEN_RAW (1 << 0)
```

This flag is used to open files in raw (uncompressed) mode. When this flag is set, `frogfs_read` will return the pre-compression raw data, suitable for scenarios where source data needs to be obtained bypassing filesystem decompression, such as transmitting compressed files via HTTP.

## Compression Algorithm Support

FrogFS supports multiple compression algorithms:

| Algorithm ID | Description |
|---------|------|
| FROGFS_COMP_ALGO_NONE | No compression |
| FROGFS_COMP_ALGO_ZLIB | ZLIB compression |
| FROGFS_COMP_ALGO_HEATSHRINK | Heatshrink compression |
| FROGFS_COMP_ALGO_GZIP | GZIP compression |

## Features

- **Read-only design**: The filesystem is read-only, ensuring data integrity, suitable for embedded storage
- **XIP support**: Supports executing code/resources directly from Flash addresses without fully loading into RAM
- **Embedded optimization**: Minimized RAM usage, suitable for resource-constrained MCU environments
- **Compression support**: Built-in multiple compression algorithms to save storage space
- **LVGL integration**: Specifically designed for LVGL graphics library resource files

## Usage Examples

### Basic Mount and Read

```c
#include "frogfs.h"

// Configure and mount filesystem
frogfs_config_t config = {
    .addr = (void *)0x8000000,  // Flash start address
};
frogfs_fs_t *fs = frogfs_init(&config);
if (fs == NULL) {
    // Mount failed
    return -1;
}

// Open file
const frogfs_entry_t *entry = frogfs_get_entry(fs, "/fonts/myfont.bin");
if (entry && frogfs_is_file(entry)) {
    frogfs_fh_t *fh = frogfs_open(fs, entry, 0);
    if (fh) {
        uint8_t buffer[256];
        ssize_t len = frogfs_read(fh, buffer, sizeof(buffer));
        
        // Process read data
        // ...
        
        frogfs_close(fh);
    }
}

// Unmount filesystem
frogfs_deinit(fs);
```

### Traverse Directory

```c
#include "frogfs.h"

void list_directory(frogfs_fs_t *fs, const frogfs_entry_t *dir) {
    frogfs_dh_t *dh = frogfs_opendir(fs, dir);
    if (!dh) return;
    
    const frogfs_entry_t *entry;
    while ((entry = frogfs_readdir(dh)) != NULL) {
        frogfs_stat_t st;
        frogfs_stat(fs, entry, &st);
        
        printf("Name: %s, Type: %s, Size: %zu\n",
               frogfs_get_name(entry),
               frogfs_is_dir(entry) ? "DIR" : "FILE",
               st.size);
    }
    
    frogfs_closedir(dh);
}
```

### Get File Statistics

```c
#include "frogfs.h"

void show_file_info(frogfs_fs_t *fs, const char *path) {
    const frogfs_entry_t *entry = frogfs_get_entry(fs, path);
    if (!entry) {
        printf("File not found: %s\n", path);
        return;
    }
    
    frogfs_stat_t st;
    frogfs_stat(fs, entry, &st);
    
    printf("Path: %s\n", path);
    printf("Type: %s\n", frogfs_is_dir(entry) ? "Directory" : "File");
    printf("Size: %zu bytes\n", st.size);
    printf("Compressed: %zu bytes\n", st.compressed_sz);
    printf("Compression: %d\n", st.compression);
}
```

## Notes

1. FrogFS is a read-only filesystem and does not support write operations
2. Image files must be pre-flashed to Flash or other non-volatile storage
3. When using XIP functionality, ensure Flash address mapping is correct
4. Filesystem access automatically handles decompression (unless `FROGFS_OPEN_RAW` is used)
5. Directory and file names are case-sensitive

## References

- [FrogFS Official Source](https://github.com/lvgl/lv_lib_freetype) (part of the LVGL ecosystem)
- Bouffalo SDK component: `components/graphics/lvgl_v9/libs/frogfs`
- Header files:
  - `include/frogfs/frogfs.h` - Main header file
  - `include/frogfs/frogfs_types.h` - Type definitions
