# Blog Logging System API Reference

> Source file: `components/stage/blog/blog.h`  
> BL602 logging framework, supports component-level/file-level/private log partition control, with hex dump and color output.

---

## Overview

Blog is the logging system for BL602. The core is a set of C macros that use `__attribute__((section))` at compile time to place log level information in separate sections, supporting component-level and file-level dynamic log switching.

```
blog_info("Hello %s", "world");
// Output: INFO (100)[main.c:  42] Hello world
```

---

## Header File

```c
#include "blog.h"
```

---

## Log Level Macros

### Component-Level Logs (switch by component name)

| Macro | Description | Example Output |
|-------|-------------|----------------|
| `blog_debug("msg")` | Debug level | `DEBUG (tick)[file:  42] msg` |
| `blog_info("msg")` | Info level | `INFO (tick)[file:  42] msg` |
| `blog_warn("msg")` | Warning level | `WARN (tick)[file:  42] msg` |
| `blog_error("msg")` | Error level | `ERROR (tick)[file:  42] msg` |
| `blog_assert(expr)` | Assert (fails and halts) | `assert, file:42` |

### Raw Format (no color prefix)

| Macro | Description |
|-------|-------------|
| `blog_debug_raw("msg")` | Raw debug |
| `blog_info_raw("msg")` | Raw info |
| `blog_warn_raw("msg")` | Raw warning |
| `blog_error_raw("msg")` | Raw error |

### Private Partition Logs (fine-grained control by module name)

| Macro | Description |
|-------|-------------|
| `blog_debug_user(name, "msg")` | Private debug |
| `blog_info_user(name, "msg")` | Private info |
| `blog_warn_user(name, "msg")` | Private warning |
| `blog_error_user(name, "msg")` | Private error |

Raw versions: `blog_debug_user_raw` / `blog_info_user_raw` / `blog_warn_user_raw` / `blog_error_user_raw`

### Hex Dump

| Macro | Description |
|-------|-------------|
| `blog_debug_hexdump(name, buf, size)` | Hex dump debug |
| `blog_info_hexdump(name, buf, size)` | Hex dump info |
| `blog_warn_hexdump(name, buf, size)` | Hex dump warning |
| `blog_error_hexdump(name, buf, size)` | Hex dump error |

---

## Private Partition Declaration

Before using `blog_xxx_user` series macros, you need to declare a private partition:

```c
BLOG_DECLARE(my_module);
```

This macro expands to two weak symbol definitions (can be overridden):
- `blog_level_t _fsymp_level_my_module` (log level)
- `const blog_info_t _fsymp_info_my_module` (module info)

---

## Function API

### `blog_init`

Initialize the logging system. Call during system startup.

```c
void blog_init(void);
```

---

### `blog_set_level_log_component`

Dynamically set log level for component/file at runtime.

```c
int blog_set_level_log_component(char *level, char *component_name);
```

| Parameter | Description |
|-----------|-------------|
| `level` | Log level string: `DEBUG` `INFO` `WARN` `ERROR` |
| `component_name` | Component name or file name |

**Return value**: 0=success

---

### `blog_hexdump_out`

Low-level hex output function (called by Hex Dump macros).

```c
void blog_hexdump_out(const char *name, uint8_t width, uint8_t *buf, uint16_t size);
```

---

## Usage Examples

### Basic Logging

```c
#include "blog.h"

void my_task(void *param)
{
    (void)param;
    blog_info("Task started");
    blog_debug("Debug info: value=%d", 42);
    blog_warn("Warning: low memory");
    blog_error("Error: connection failed");
}
```

### Private Partition Logging

```c
// Declare private partition at the beginning of the file
BLOG_DECLARE(my_driver);

// Use private logging
void driver_init(void)
{
    blog_info_user(my_driver, "Driver init");
    blog_error_user(my_driver, "HW error detected");
}
```

### Hex Dump

```c
uint8_t packet[] = {0x01, 0x02, 0x03, 0x04};
blog_info_hexdump("packet", packet, sizeof(packet));
// Output similar to:
// INFO (100)[main.c:  42] packet: 01 02 03 04
```

### Runtime Log Level Adjustment

```c
// Disable DEBUG output (save log overhead)
blog_set_level_log_component("INFO", "my_driver");
```
