# EasyFlash KV Storage API Reference

> Source file: `components/stage/easyflash4/inc/easyflash.h`  
> Flash-based key-value storage system, supports ENV environment variables, logs, and IAP upgrade.

---

## Overview

EasyFlash is a Flash storage management library providing three features:
- **ENV**: Key-value storage (similar to NVS), persists across power cycles
- **LOG**: Circular log storage
- **IAP**: In-application programming upgrade

---

## Header File

```c
#include "easyflash.h"
```

---

## Type Definitions

### `EfErrCode`

Error code type:

```c
typedef enum {
    EF_NO_ERR = 0,
    EF_ERROR = 1,
    EF_NO_INIT = 2,
    EF_READ_ERR = 3,
    EF_WRITE_ERR = 4,
    /* ... more error codes */
} EfErrCode;
```

### `env_node_obj_t`

ENV node object handle:

```c
typedef struct _env_node_obj {
    struct _env_node_obj *next;
    char *key;
    uint8_t len;
    uint8_t state;
    char value[ENV_NODE_VALUE_SIZE];
} env_node_obj_t;
```

---

## Initialization

### `easyflash_init`

Initialize EasyFlash (automatically loads ENV).

```c
EfErrCode easyflash_init(void);
```

**Return value**: 0=success

---

## ENV Storage (Key-Value)

ENV feature requires `EF_USING_ENV` to be enabled.

### `ef_get_env_blob`

Read ENV value (binary-safe):

```c
size_t ef_get_env_blob(const char *key, void *value_buf,
                       size_t buf_len, size_t *saved_value_len);
```

| Parameter | Description |
|------|------|
| `key` | Key name |
| `value_buf` | Receive buffer |
| `buf_len` | Buffer size |
| `saved_value_len` | Actual stored length (output) |

**Return value**: 0=key does not exist, >0=number of bytes read

---

### `ef_set_env_blob`

Write ENV value (binary-safe):

```c
EfErrCode ef_set_env_blob(const char *key, const void *value_buf, size_t buf_len);
```

---

### `ef_get_env`

Read ENV string value:

```c
char *ef_get_env(const char *key);
```

**Return value**: String pointer, returns NULL if not found

---

### `ef_set_env`

Set ENV string value:

```c
EfErrCode ef_set_env(const char *key, const char *value);
```

---

### `ef_del_env`

Delete ENV:

```c
EfErrCode ef_del_env(const char *key);
```

---

### `ef_save_env`

Write ENV from memory to Flash:

```c
EfErrCode ef_save_env(void);
```

> `ef_set_env` writes to memory only by default; you must manually call `ef_save_env` to persist.

---

### `ef_set_and_save_env`

Set and immediately save:

```c
EfErrCode ef_set_and_save_env(const char *key, const char *value);
```

---

### `ef_print_env`

Print all ENV (for debugging):

```c
void ef_print_env(void);
```

---

### `ef_env_set_default`

Restore default ENV:

```c
EfErrCode ef_env_set_default(void);
```

---

## Log Feature

LOG feature requires `EF_USING_LOG` to be enabled.

### `ef_log_write`

Write log:

```c
EfErrCode ef_log_write(const uint32_t *log, size_t size);
```

---

### `ef_log_read`

Read log:

```c
EfErrCode ef_log_read(size_t index, uint32_t *log, size_t size);
```

---

### `ef_log_clean`

Clear all logs:

```c
EfErrCode ef_log_clean(void);
```

---

### `ef_log_get_used_size`

Get used log space:

```c
size_t ef_log_get_used_size(void);
```

---

## Utility Functions

### `ef_calc_crc32`

Calculate CRC32:

```c
uint32_t ef_calc_crc32(uint32_t crc, const void *buf, size_t size);
```

---

## Usage Examples

### Basic ENV Operations

```c
#include "easyflash.h"

void env_demo(void)
{
    easyflash_init();

    // Write string
    ef_set_env("device_name", "WB2-001");
    ef_set_env("interval", "5000");
    ef_save_env();

    // Read string
    char *name = ef_get_env("device_name");
    if (name) {
        printf("Device: %s\r\n", name);
    }

    // Write binary data
    uint8_t config[4] = {0x01, 0x02, 0x03, 0x04};
    ef_set_env_blob("config", config, sizeof(config));
}
```

### ENV Bulk Operations

```c
// Print with callback (iterate through all ENV)
void my_print_cb(env_node_obj_t *env, void *arg1, void *arg2)
{
    (void)arg1; (void)arg2;
    printf("key=%s, value=%s\r\n", env->key, env->value);
}

ef_print_env_cb(my_print_cb);
```
