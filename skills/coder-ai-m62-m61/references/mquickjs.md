# MQuickJS - QuickJS JavaScript Engine for Embedded Systems

MQuickJS is a compact JavaScript engine for embedded MCUs (BL616/BL618/BL808) requiring as little as **10KB RAM** and **100KB ROM**.

## Quick Reference

### Core API Functions

| Function | Description |
|----------|-------------|
| `mqjs_init()` | Initialize the MQuickJS engine |
| `mqjs_eval()` | Evaluate JavaScript code |
| `mqjs_register_func()` | Register a C function to be called from JavaScript |
| `mqjs_cleanup()` | Free the JS context and cleanup |

### Header Files

```c
#include "bouffalo_mquickjs.h"  // Bouffalo SDK adaptation
#include "mquickjs.h"            // Core engine API
```

---

## `mqjs_init` - Initialize JavaScript Engine

```c
void bouffalo_mquickjs_init(void);
```

Initializes the Bouffalo SDK adaptation for MQuickJS. Call this before using any MQuickJS functionality.

**Note:** The underlying `JS_NewContext()` creates a new JavaScript execution context:

```c
JSContext *JS_NewContext(void *mem_start, size_t mem_size, const JSSTDLibraryDef *stdlib_def);
```

**Parameters:**
- `mem_start` - Pointer to memory buffer for the JS heap
- `mem_size` - Size of the memory buffer (recommend 64KB minimum)
- `stdlib_def` - Standard library definition (use `&js_stdlib` for full stdlib)

**Example:**
```c
#define JS_MEMORY_SIZE 65536  // 64KB
static uint8_t js_memory[JS_MEMORY_SIZE];

// Initialize JS context
JSContext *ctx = JS_NewContext(js_memory, JS_MEMORY_SIZE, &js_stdlib);
if (!ctx) {
    printf("Failed to create JS context\n");
    return -1;
}
```

---

## `mqjs_eval` - Execute JavaScript Code

```c
JSValue JS_Eval(JSContext *ctx, const char *input, size_t input_len,
                const char *filename, int eval_flags);
```

Parses and executes JavaScript source code.

**Parameters:**
- `ctx` - JavaScript context (from `JS_NewContext`)
- `input` - JavaScript source code string
- `input_len` - Length of source code
- `filename` - Filename for error reporting (can be NULL)
- `eval_flags` - Evaluation flags (see below)

**Eval Flags:**
```c
#define JS_EVAL_RETVAL     (1 << 0)  // Return last value instead of undefined
#define JS_EVAL_REPL       (1 << 1)  // REPL mode (implicit global vars)
#define JS_EVAL_STRIP_COL (1 << 2)  // Strip column numbers (save memory)
#define JS_EVAL_JSON      (1 << 3)  // Parse as JSON
```

**Return Value:**
- Returns `JSValue` (number, string, object, etc.)
- Returns `JS_EXCEPTION` on error - check with `JS_IsException()`

**Example:**
```c
const char *js_code = "print('Hello from JavaScript!'); 1 + 2;";

JSValue result = JS_Eval(ctx, js_code, strlen(js_code), "test.js", 0);

if (JS_IsException(result)) {
    JSValue err = JS_GetException(ctx);
    // Handle error - print with JS_PrintValueF(ctx, err, JS_DUMP_LONG);
} else {
    // Success - result contains the last evaluated value
    int value = JS_VALUE_GET_INT(result);
    printf("Result: %d\n", value);
}
```

---

## `mqjs_register_func` - Register C Functions for JS

Use `JS_SetPropertyStr()` to register C functions as global JS functions:

```c
JSValue JS_SetPropertyStr(JSContext *ctx, JSValue this_obj,
                          const char *str, JSValue val);
```

**C Function Signature:**
```c
typedef JSValue JSCFunction(JSContext *ctx, JSValue *this_val, int argc, JSValue *argv);

// argc includes FRAME_CF_CTOR flag for constructors
// argv[0] to argv[argc-1] are the arguments
```

**Example - Register a Custom Function:**
```c
// Custom C function to be called from JavaScript
static JSValue js_led_control(JSContext *ctx, JSValue *this_val, 
                               int argc, JSValue *argv)
{
    int led_num;
    int state;
    
    // Parse arguments
    JS_ToInt32(ctx, &led_num, argv[0]);
    JS_ToInt32(ctx, &state, argv[1]);
    
    // Control LED (your hardware code here)
    printf("LED %d -> %s\n", led_num, state ? "ON" : "OFF");
    
    return JS_NewInt32(ctx, 0);  // Return 0 for success
}

// Register function as global 'ledControl'
JSValue led_func = JS_NewCFunction(ctx, js_led_control, "ledControl", 2);
JS_SetPropertyStr(ctx, JS_GetGlobalObject(ctx), "ledControl", led_func);
```

**Example - Register a Constructor (Class):**
```c
// Rectangle class example from SDK
typedef struct {
    int x;
    int y;
} RectangleData;

static JSValue js_rectangle_constructor(JSContext *ctx, JSValue *this_val,
                                        int argc, JSValue *argv)
{
    JSValue obj;
    RectangleData *d;
    
    if (!(argc & FRAME_CF_CTOR))
        return JS_ThrowTypeError(ctx, "must be called with new");
    argc &= ~FRAME_CF_CTOR;
    
    obj = JS_NewObjectClassUser(ctx, JS_CLASS_RECTANGLE);
    d = malloc(sizeof(*d));
    JS_SetOpaque(ctx, obj, d);
    
    JS_ToInt32(ctx, &d->x, argv[0]);
    JS_ToInt32(ctx, &d->y, argv[1]);
    
    return obj;
}

// Property getter
static JSValue js_rectangle_get_x(JSContext *ctx, JSValue *this_val,
                                   int argc, JSValue *argv)
{
    RectangleData *d = JS_GetOpaque(ctx, *this_val);
    return JS_NewInt32(ctx, d->x);
}

// Define class properties
static const JSPropDef js_rectangle_proto[] = {
    JS_CGETSET_DEF("x", js_rectangle_get_x, NULL),
    JS_CGETSET_DEF("y", js_rectangle_get_y, NULL),
    JS_PROP_END,
};

// Define class
static const JSClassDef js_rectangle_class =
    JS_CLASS_DEF("Rectangle", 2, js_rectangle_constructor, JS_CLASS_RECTANGLE,
                 NULL, js_rectangle_proto, NULL, js_rectangle_finalizer);
```

---

## Working Example - Running JS on BL616/BL618

### Full Embedded Example

```c
#include <stdio.h>
#include <string.h>
#include <stdlib.h>

#include "bflb_mtimer.h"
#include "mquickjs.h"
#include "example_stdlib.h"  // Contains js_stdlib definition

// Memory for JS engine (64KB recommended minimum)
#define JS_HEAP_SIZE 65536
static uint8_t js_heap[JS_HEAP_SIZE];

// LED control from JavaScript
static JSValue js_led_on(JSContext *ctx, JSValue *this_val, int argc, JSValue *argv)
{
    int led_num;
    JS_ToInt32(ctx, &led_num, argv[0]);
    
    // bflb_gpio_set(gpio, led_num, 1);  // Actual GPIO call
    printf("LED %d ON\n", led_num);
    
    return JS_UNDEFINED;
}

static JSValue js_led_off(JSContext *ctx, JSValue *this_val, int argc, JSValue *argv)
{
    int led_num;
    JS_ToInt32(ctx, &led_num, argv[0]);
    
    // bflb_gpio_clear(gpio, led_num, 0);  // Actual GPIO call
    printf("LED %d OFF\n", led_num);
    
    return JS_UNDEFINED;
}

static JSValue js_get_temperature(JSContext *ctx, JSValue *this_val, 
                                  int argc, JSValue *argv)
{
    // Read temperature sensor
    int temp = 25;  // bflb_temp_sensor_read();
    return JS_NewInt32(ctx, temp);
}

// Log function for JS console output
static void js_log_func(void *opaque, const void *buf, size_t buf_len)
{
    printf("%.*s", (int)buf_len, (const char *)buf);
}

int main(void)
{
    JSContext *ctx;
    JSValue result;
    
    // 1. Initialize Bouffalo SDK MQuickJS
    bouffalo_mquickjs_init();
    
    // 2. Create JS context with memory buffer
    ctx = JS_NewContext(js_heap, JS_HEAP_SIZE, &js_stdlib);
    if (!ctx) {
        printf("ERROR: Failed to create JS context\n");
        return -1;
    }
    
    // 3. Set log function for print() output
    JS_SetLogFunc(ctx, js_log_func);
    
    // 4. Register custom C functions
    JSValue led_on = JS_NewCFunction(ctx, js_led_on, "ledOn", 1);
    JS_SetPropertyStr(ctx, JS_GetGlobalObject(ctx), "ledOn", led_on);
    
    JSValue led_off = JS_NewCFunction(ctx, js_led_off, "ledOff", 1);
    JS_SetPropertyStr(ctx, JS_GetGlobalObject(ctx), "ledOff", led_off);
    
    JSValue get_temp = JS_NewCFunction(ctx, js_get_temperature, "getTemperature", 0);
    JS_SetPropertyStr(ctx, JS_GetGlobalObject(ctx), "getTemperature", get_temp);
    
    // 5. Run JavaScript code
    const char *script = 
        "// Hello World!\n"
        "print('=== MQuickJS Demo ===');\n"
        "\n"
        "// Basic calculations\n"
        "var sum = 1 + 2 + 3;\n"
        "print('Sum 1+2+3 = ' + sum);\n"
        "\n"
        "// Control hardware from JS\n"
        "ledOn(0);      // Turn on LED 0\n"
        "ledOff(0);     // Turn off LED 0\n"
        "\n"
        "// Read sensor data\n"
        "var temp = getTemperature();\n"
        "print('Temperature: ' + temp + 'C');\n"
        "\n"
        "// Use built-in functions\n"
        "print('Math test: ' + Math.sqrt(16));\n"
        "\n"
        "// Object example\n"
        "var rect = new Rectangle(10, 20);\n"
        "print('Rectangle: ' + rect.x + 'x' + rect.y);\n"
        "\n"
        "print('=== Done ===');\n";
    
    printf("Executing JavaScript...\n\n");
    
    result = JS_Eval(ctx, script, strlen(script), "demo.js", 0);
    
    if (JS_IsException(result)) {
        printf("\nJS ERROR:\n");
        JSValue err = JS_GetException(ctx);
        JS_PrintValueF(ctx, err, JS_DUMP_LONG);
        printf("\n");
    } else {
        printf("\nJS completed successfully!\n");
    }
    
    // 6. Cleanup
    JS_FreeContext(ctx);
    
    return 0;
}
```

### JavaScript Code Run on Device

```javascript
// Available built-in APIs
print("Hello");                    // Console output
console.log("Debug");              // Same as print
Math.sqrt(16);                    // Math functions
Math.sin(Math.PI / 2);
JSON.parse('{"a":1}');           // JSON support
Array.of(1, 2, 3);               // Arrays
performance.now();               // Timing

// Custom registered functions
ledOn(0);                        // Hardware control
ledOff(0);
getTemperature();                // Sensor reading

// Custom classes
var rect = new Rectangle(10, 20);
rect.x;                          // 10
rect.y;                          // 20

// Typed arrays (for sensor data)
var buf = new Uint8Array(16);
buf[0] = 0x55;
```

---

## Memory Requirements

| Use Case | RAM | ROM |
|----------|-----|-----|
| Minimal (simple scripts) | 10 KB | ~100 KB |
| Standard (with stdlib) | 64 KB | ~150 KB |
| Complex (with classes) | 128 KB | ~200 KB |

---

## Error Handling

```c
// Check for exceptions
if (JS_IsException(result)) {
    JSValue err = JS_GetException(ctx);
    // Get error message
    JSCStringBuf buf;
    const char *msg = JS_ToCString(ctx, err, &buf);
    printf("Error: %s\n", msg);
}

// Throw errors from C
return JS_ThrowTypeError(ctx, "Invalid argument");
return JS_ThrowRangeError(ctx, "Value out of range");
return JS_ThrowReferenceError(ctx, "Undefined variable");
```

---

## Type Conversions

```c
// JavaScript to C
int i;
double d;
JS_ToInt32(ctx, &i, js_value);
JS_ToNumber(ctx, &d, js_value);

// C to JavaScript
JS_NewInt32(ctx, 42);
JS_NewFloat64(ctx, 3.14);
JS_NewString(ctx, "hello");

// Check types
JS_IsNumber(ctx, val);
JS_IsString(ctx, val);
JS_IsBool(ctx, val);
JS_IsNull(ctx, val);
JS_IsUndefined(ctx, val);
```

---

## File Structure (SDK)

```
bouffalo_sdk/components/utils/mquickjs/
├── mquickjs.h              # Main API header
├── mquickjs.c              # Core engine (parser, compiler, VM, GC)
├── mquickjs_priv.h         # Private internal headers
├── mquickjs_build.h        # Stdlib build macros
├── mquickjs_build.c        # Stdlib table generator
├── bouffalo_mquickjs.h     # Bouffalo SDK adaptation
├── bouffalo_mquickjs.c     # SDK-specific init
├── example.c               # Full usage example
├── example_stdlib.c        # Custom Rectangle class example
└── CLAUDE.md               // Detailed documentation
```

---

## See Also

- [MQuickJS CLAUDE.md](CLAUDE.md) - Detailed engine documentation
- [Bouffalo SDK Documentation](../CLAUDE.md) - BL616/BL618 development guide
