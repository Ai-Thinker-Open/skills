# BL616/BL618 Utils - cJSON & Log System Reference

## cJSON Library

**Header:** `components/utils/cjson/cJSON.h`  
**Source:** Standard cJSON v1.7.18 library for JSON parsing and generation.

### Data Types

```c
typedef struct cJSON {
    struct cJSON *next;      // Next sibling
    struct cJSON *prev;      // Previous sibling
    struct cJSON *child;     // First child (for arrays/objects)
    int type;                // Type flags (see below)
    char *valuestring;       // String value
    int valueint;            // Integer value (deprecated)
    double valuedouble;      // Numeric value
    char *string;            // Key name (for object members)
} cJSON;
```

### Type Constants

| Constant | Value | Description |
|----------|-------|-------------|
| `cJSON_Invalid` | 0 | Invalid/uninitialized |
| `cJSON_False` | 1 | Boolean false |
| `cJSON_True` | 2 | Boolean true |
| `cJSON_NULL` | 4 | Null value |
| `cJSON_Number` | 8 | Numeric value |
| `cJSON_String` | 16 | String value |
| `cJSON_Array` | 32 | Array container |
| `cJSON_Object` | 64 | Object container |
| `cJSON_Raw` | 128 | Raw JSON blob |

---

### Parsing Functions

#### `cJSON_Parse` - Parse JSON String

```c
cJSON *cJSON_Parse(const char *value);
```

Parses a null-terminated JSON string into a cJSON tree.

**Parameters:**
- `value` - Null-terminated JSON string

**Returns:** Pointer to root cJSON node, or NULL on parse error

**Example:**
```c
const char *json_str = "{\"name\":\"test\",\"value\":123}";
cJSON *root = cJSON_Parse(json_str);
if (root == NULL) {
    printf("JSON parse error: %s\n", cJSON_GetErrorPtr());
}
```

#### `cJSON_ParseWithOpts` - Parse with Options

```c
cJSON *cJSON_ParseWithOpts(const char *value, const char **return_parse_end, cJSON_bool require_null_terminated);
```

Extended parsing with options.

**Parameters:**
- `value` - JSON string
- `return_parse_end` - If non-NULL, receives pointer to end of parsed region
- `require_null_terminated` - If 1, requires null-terminated input

---

### Print Functions

#### `cJSON_Print` - Pretty Print to String

```c
char *cJSON_Print(const cJSON *item);
```

Renders a cJSON tree to a formatted, human-readable string.

**Returns:** Newly allocated string (caller must `free()`), or NULL on failure

**Example:**
```c
cJSON *root = cJSON_CreateObject();
cJSON_AddStringToObject(root, "status", "ok");
cJSON_AddNumberToObject(root, "temp", 25.5);

char *json_str = cJSON_Print(root);
printf("%s\n", json_str);
free(json_str);
cJSON_Delete(root);
```

**Output:**
```json
{
    "status": "ok",
    "temp": 25.5
}
```

#### `cJSON_PrintUnformatted` - Compact Print

```c
char *cJSON_PrintUnformatted(const cJSON *item);
```

Renders without whitespace/formatting.

**Example Output:** `{"status":"ok","temp":25.5}`

---

### Object Creation Functions

#### `cJSON_CreateObject` - Create Empty Object

```c
cJSON *cJSON_CreateObject(void);
```

Creates an empty JSON object `{}`.

#### `cJSON_CreateArray` - Create Empty Array

```c
cJSON *cJSON_CreateArray(void);
```

Creates an empty JSON array `[]`.

#### `cJSON_AddItemToObject` - Add Item to Object

```c
cJSON_bool cJSON_AddItemToObject(cJSON *object, const char *string, cJSON *item);
```

**Helper Macros (preferred):**

```c
cJSON_AddNullToObject(obj, "key")
cJSON_AddTrueToObject(obj, "key")
cJSON_AddFalseToObject(obj, "key")
cJSON_AddBoolToObject(obj, "key", 1)
cJSON_AddNumberToObject(obj, "key", 3.14)
cJSON_AddStringToObject(obj, "key", "value")
cJSON_AddRawToObject(obj, "key", "raw_json")
cJSON_AddObjectToObject(obj, "key")   // Nested object
cJSON_AddArrayToObject(obj, "key")    // Nested array
```

---

### Query Functions

```c
int cJSON_GetArraySize(const cJSON *array);
cJSON *cJSON_GetArrayItem(const cJSON *array, int index);
cJSON *cJSON_GetObjectItem(const cJSON *object, const char *string);
cJSON *cJSON_GetObjectItemCaseSensitive(const cJSON *object, const char *string);
cJSON_bool cJSON_HasObjectItem(const cJSON *object, const char *string);
```

---

### Memory Management

```c
void cJSON_Delete(cJSON *item);          // Free entire tree
cJSON *cJSON_Duplicate(cJSON *item, cJSON_bool recurse);  // Clone tree
```

**Important:** Always free parsed results with `cJSON_Delete()` and printed strings with `free()`.

---

### Working Example: Complete Parse and Query

```c
#include "cJSON.h"
#include <stdio.h>
#include <stdlib.h>

void json_example(void)
{
    // JSON string to parse
    const char *json_str =
        "{\"device\":\"sensor_01\","
        "\" readings\":{"
        "\"temperature\":23.5,"
        "\"humidity\":65,"
        "\"active\":true"
        "},"
        "\"tags\":[\"kitchen\",\"temp\"]}";

    // Parse JSON
    cJSON *root = cJSON_Parse(json_str);
    if (root == NULL) {
        printf("Parse error at: %s\n", cJSON_GetErrorPtr());
        return;
    }

    // Get object item
    cJSON *device = cJSON_GetObjectItem(root, "device");
    if (device && device->type == cJSON_String) {
        printf("Device: %s\n", device->valuestring);
    }

    // Get nested object
    cJSON *readings = cJSON_GetObjectItem(root, "readings");
    if (readings && cJSON_IsObject(readings)) {
        cJSON *temp = cJSON_GetObjectItem(readings, "temperature");
        cJSON *humid = cJSON_GetObjectItem(readings, "humidity");
        cJSON *active = cJSON_GetObjectItem(readings, "active");

        printf("Temp: %.1f, Humidity: %d, Active: %s\n",
               temp ? temp->valuedouble : 0,
               humid ? humid->valueint : 0,
               active ? (cJSON_IsTrue(active) ? "yes" : "no") : "unknown");
    }

    // Get array
    cJSON *tags = cJSON_GetObjectItem(root, "tags");
    if (tags && cJSON_IsArray(tags)) {
        printf("Tags (%d): ", cJSON_GetArraySize(tags));
        cJSON *tag;
        cJSON_ArrayForEach(tag, tags) {
            if (tag->type == cJSON_String) {
                printf("%s ", tag->valuestring);
            }
        }
        printf("\n");
    }

    cJSON_Delete(root);
}
```

### Working Example: Build JSON

```c
#include "cJSON.h"
#include <stdio.h>
#include <stdlib.h>

void json_build_example(void)
{
    // Create root object
    cJSON *root = cJSON_CreateObject();
    if (!root) return;

    // Add simple values
    cJSON_AddStringToObject(root, "name", "BL616 Sensor");
    cJSON_AddNumberToObject(root, "id", 1001);
    cJSON_AddBoolToObject(root, "enabled", 1);

    // Create nested object
    cJSON *config = cJSON_AddObjectToObject(root, "config");
    cJSON_AddNumberToObject(config, "interval_ms", 1000);
    cJSON_AddStringToObject(config, "mode", "normal");

    // Create array
    cJSON *thresholds = cJSON_AddArrayToObject(root, "thresholds");
    cJSON_AddItemToArray(thresholds, cJSON_CreateNumber(10.0));
    cJSON_AddItemToArray(thresholds, cJSON_CreateNumber(20.0));
    cJSON_AddItemToArray(thresholds, cJSON_CreateNumber(30.0));

    // Print result
    char *json_str = cJSON_Print(root);
    printf("%s\n", json_str);

    // Cleanup
    free(json_str);
    cJSON_Delete(root);
}
```

---

## Log System

**Headers:** 
- `components/utils/log/log.h` - Main log interface
- `components/utils/log/bflb_log/bflb_log.h` - Advanced log backend

---

### Log Levels

| Level | Macro | Value | Description |
|-------|-------|-------|-------------|
| Fatal | `LOG_F` | 0 | System panic |
| Error | `LOG_E` | 1 | Error conditions |
| Warning | `LOG_W` | 2 | Warning conditions |
| Info | `LOG_I` | 3 | Informational |
| Debug | `LOG_D` | 4 | Debug messages |
| Trace | `LOG_T` | 5 | Detailed trace |

---

### Basic Log Functions

#### `log_init` / `log_start` - Initialize Log System

```c
// Declaration (in log.h)
extern void log_start(void);
extern void log_restart(void);
```

Initialize the log system. Typically called once at startup before using log macros.

```c
int main(void)
{
    // Hardware init
    system_init();

    // Initialize log system
    log_start();

    // Now logs are active
    LOG_I("System initialized\n");
    
    return 0;
}
```

---

### Log Macros

The log system provides two variants for each level:

| Standard | Raw (no prefix) | Description |
|----------|------------------|--------------|
| `LOG_F(...)` | `LOG_RF(...)` | Fatal + prefix / raw |
| `LOG_E(...)` | `LOG_RE(...)` | Error + prefix / raw |
| `LOG_W(...)` | `LOG_RW(...)` | Warning + prefix / raw |
| `LOG_I(...)` | `LOG_RI(...)` | Info + prefix / raw |
| `LOG_D(...)` | `LOG_RD(...)` | Debug + prefix / raw |
| `LOG_T(...)` | `LOG_RT(...)` | Trace + prefix / raw |

**Prefix format:** `[<LEVEL>][<TAG>] message`

---

### Configuration

Log behavior is controlled by these Kconfig options:

```c
CONFIG_LOG_LEVEL=<0-5>     // Compile-time level filter
CONFIG_LOG_DISABLE         // Disable all logs
CONFIG_BFLB_LOG            // Use advanced log backend
CONFIG_LOG_NCOLOR          // Disable ANSI colors
```

---

### Tag Definition

Define a module tag before including log.h:

```c
#ifndef DBG_TAG
#define DBG_TAG "MAIN"
#endif

#include "log.h"
```

---

### Working Examples

#### Basic Logging

```c
#include "log.h"

#ifndef DBG_TAG
#define DBG_TAG "APP"
#endif

int main(void)
{
    log_start();

    LOG_I("Application started\r\n");
    LOG_D("Debug info: value=%d\r\n", 42);
    LOG_W("Warning: low memory\r\n");
    LOG_E("Error: sensor read failed\r\n");

    return 0;
}
```

#### Module-Specific Tags

```c
// In wifi.c
#ifndef DBG_TAG
#define DBG_TAG "WIFI"
#endif
#include "log.h"

void wifi_connect(const char *ssid)
{
    LOG_I("Connecting to %s...\r\n", ssid);
    // ...
    LOG_I("Connected successfully\r\n");
}

// In sensor.c
#ifndef DBG_TAG
#define DBG_TAG "SENSOR"
#endif
#include "log.h"

void sensor_read(void)
{
    LOG_I("Reading sensor data\r\n");
}
```

#### Conditional Compilation for Debug Logs

```c
#include "log.h"

void debug_function(void)
{
#if (CONFIG_LOG_LEVEL >= 4)
    LOG_D("Entering debug function\r\n");
    LOG_D("Local variables: x=%d, y=%d\r\n", x, y);
#endif

    // Critical code path
    perform_operation();

#if (CONFIG_LOG_LEVEL >= 4)
    LOG_D("Operation complete\r\n");
#endif
}
```

#### Error Handling with Logs

```c
#include "log.h"

int sensor_init(void)
{
    int ret;

    ret = hal_i2c_init(I2C_PORT_0);
    if (ret < 0) {
        LOG_E("I2C init failed: %d\r\n", ret);
        return ret;
    }

    ret = sensor_write_reg(SENSOR_REG_MODE, MODE_NORMAL);
    if (ret < 0) {
        LOG_E("Sensor write failed: %d\r\n", ret);
        hal_i2c_deinit(I2C_PORT_0);
        return ret;
    }

    LOG_I("Sensor initialized OK\r\n");
    return 0;
}
```

---

### Log Flush

Force output buffer flush:

```c
LOG_I("Critical message\r\n");
LOG_FLUSH();  // Ensure it's written immediately
```

---

### Advanced Log Backend (bflb_log)

When `CONFIG_BFLB_LOG` is enabled, logs use an advanced backend with:

- **Async mode** - Non-blocking logging via queue
- **Timestamp** - Automatic timestamps
- **Color output** - ANSI terminal colors
- **Multiple outputs** - UART, file, buffer

See `components/utils/log/bflb_log/bflb_log.h` for details.

---

### Quick Reference

```c
// Include log system
#ifndef DBG_TAG
#define DBG_TAG "MODULE"
#endif
#include "log.h"

// Initialize once at startup
log_start();

// Log at various levels
LOG_F("Fatal - system panic\r\n");   // 0
LOG_E("Error condition\r\n");        // 1
LOG_W("Warning condition\r\n");      // 2
LOG_I("Information\r\n");           // 3
LOG_D("Debug message\r\n");          // 4
LOG_T("Trace details\r\n");          // 5

// Raw variants (no prefix)
LOG_RI("Raw info message\r\n");

// Flush output
LOG_FLUSH();
```
