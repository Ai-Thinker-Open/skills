# fastlz - Lightning-Fast Lossless Compression

## Overview

fastlz is a fast, lossless compression library designed for real-time compression needs. It offers an excellent balance between compression speed and ratio, making it suitable for embedded systems where CPU resources are limited. The library is written in pure C and has no external dependencies.

## Location

```
components/stage/fastlz/
```

## Key Files

- `fastlz.h` - Header with API declarations
- `fastlz.c` - Implementation
- `fastlz_wrapper.h` - Wrapper macros for easier use
- `fastlz_sample.c` - Example compression/decompression program

## License

MIT License. Copyright (C) 2005-2007 Ariya Hidayat. Official website: http://www.fastlz.org

## Features

- **Lossless compression**: No data loss during compression/decompression
- **Fast**: Optimized for speed, especially on embedded CPUs
- **Small memory footprint**: Can work with limited RAM
- **Portable**: Pure C, no external dependencies
- **Two compression levels**: Level 1 (fastest) and Level 2 (better ratio)

## Buffer Requirements

- **Output buffer**: Must be at least 5% larger than input + 66 bytes overhead
- **Macro**: `FASTLZ_BUFFER_PADDING(x)` calculates safe padding
- **Minimum input**: 16 bytes

## API Reference

### Compression

```c
int fastlz_compress(const void* input, int length, void* output);
```

Compress a block of data using Level 1 compression.

**Parameters:**
- `input` - Source data buffer
- `length` - Size of input in bytes (minimum 16)
- `output` - Destination buffer (must be >= `FASTLZ_BUFFER_PADDING(length)`)

**Returns:** Size of compressed data, or > length if incompressible

---

```c
int fastlz_compress_level(int level, const void* input, int length, void* output);
```

Compress with specified level.

**Parameters:**
- `level` - Compression level (1 or 2)
- `input` - Source data buffer
- `length` - Size of input in bytes (minimum 16)
- `output` - Destination buffer

**Returns:** Size of compressed data

**Notes:**
- Level 1: Fastest compression, good for short data
- Level 2: Slightly slower, better compression ratio

---

### Decompression

```c
int fastlz_decompress(const void* input, int length, void* output, int maxout);
```

Decompress data.

**Parameters:**
- `input` - Compressed data buffer
- `length` - Size of compressed data
- `output` - Destination buffer
- `maxout` - Maximum output buffer size

**Returns:** Size of decompressed data, or 0 on error

**Notes:**
- Memory-safe: Will not write beyond `maxout` bytes
- Input and output buffers must not overlap

## Version Information

```c
#define FASTLZ_VERSION           0x000100  // Version as hex
#define FASTLZ_VERSION_MAJOR     0
#define FASTLZ_VERSION_MINOR     0
#define FASTLZ_VERSION_REVISION  0
#define FASTLZ_VERSION_STRING    "0.1.0"
```

## Implementation Details

### Algorithm

fastlz uses LZ77-based compression with:
- 12-bit literal match length (up to 264 bytes)
- 12-bit backward distance (up to 2048 byte offset)
- Inline literal runs
- Optimized for 16-byte aligned data

### Hash Table

The library uses a hash table for finding matching sequences. Dynamic memory allocation is used instead of static 32KB buffer to reduce stack usage on embedded systems.

## Usage Example

```c
#include "fastlz.h"

// Compression
uint8_t input[1024];
uint8_t output[FASTLZ_BUFFER_PADDING(1024)];

int compressed = fastlz_compress(input, sizeof(input), output);

// Decompression
uint8_t decompressed[1024];
int decompressed_size = fastlz_decompress(output, compressed, 
                                            decompressed, sizeof(decompressed));
```

## Sample Program

The repository includes `fastlz_sample.c` with a command-line tool:

```bash
# Compile (from fastlz directory)
gcc -o 6pack 6pack.c fastlz.c
gcc -o 6unpack 6unpack.c fastlz.c

# Compress
6pack original.bin compressed.bin

# Decompress
6unpack compressed.bin original.bin
```

## Embedded Optimization Tips

1. **Use level 1** for time-critical applications
2. **Use level 2** when compression ratio matters more than speed
3. **Align buffers** to 16-byte boundaries when possible
4. **Reuse buffers** to reduce memory allocations
5. **Process in chunks** for streaming data

## Limitations

- Minimum input size: 16 bytes
- Maximum compression ratio worst case: may expand slightly
- Not suitable for already-compressed data (images, zip, etc.)
- No error recovery - corrupted data returns 0

## Differences from Official Version

The embedded version uses dynamic memory allocation instead of the original static 32KB hash table to reduce stack consumption on resource-constrained MCUs.
