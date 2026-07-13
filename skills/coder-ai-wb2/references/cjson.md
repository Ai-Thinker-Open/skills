# cjson - C JSON Parser/Generator

## Overview

cjson is a lightweight JSON parser and generator for C. It provides a simple API to parse JSON strings into a tree structure, create JSON objects programmatically, and render JSON back to strings. It is widely used in embedded systems for configuration files and network protocols.

## Location

```
components/stage/cjson/
```

## Key Files

- `cJSON.h` - Header with all type definitions and API declarations
- `cJSON.c` - Full implementation

## License

cJSON is distributed under the MIT license. Copyright (c) 2009 Dave Gamble.

## Data Types

### cJSON Types

| Type | Value | Description |
|------|-------|-------------|
| `cJSON_False` | 0 | Boolean false |
| `cJSON_True` | 1 | Boolean true |
| `cJSON_NULL` | 2 | Null value |
| `cJSON_Number` | 3 | Number (integer or floating-point) |
| `cJSON_String` | 4 | String value |
| `cJSON_Array` | 5 | Array of cJSON items |
| `cJSON_Object` | 6 | Key-value object |

### Type Flags

| Flag | Value | Description |
|------|-------|-------------|
| `cJSON_IsReference` | 256 | Item is a reference (not a copy) |
| `cJSON_StringIsConst` | 512 | String is const/immutable |

### cJSON Structure

```c
typedef struct cJSON {
    struct cJSON *next,*prev;    // Linked list pointers
    struct cJSON *child;         // Child array/object items
    
    int type;                    // Item type
    
    char *valuestring;           // String value (if type==cJSON_String)
    int valueint;                // Integer value (if type==cJSON_Number)
    double valuedouble;          // Double value (if type==cJSON_Number)
    
    char *string;                // Object key name
} cJSON;
```

## Core API

### Memory Hooks

```c
typedef struct cJSON_Hooks {
    void *(*malloc_fn)(size_t sz);
    void (*free_fn)(void *ptr);
} cJSON_Hooks;

void cJSON_InitHooks(cJSON_Hooks* hooks);
```

Override default malloc/free for custom memory management.

---

### Parsing

```c
cJSON *cJSON_Parse(const char *value);
```

Parse a JSON string into a cJSON tree.

**Parameters:**
- `value` - Null-terminated JSON string

**Returns:** Pointer to root cJSON item, or NULL on parse error

---

```c
cJSON *cJSON_ParseWithOpts(const char *value, const char **return_parse_end, 
                           int require_null_terminated);
```

Parse with advanced options.

**Parameters:**
- `return_parse_end` - If not NULL, receives pointer to end of parsed region
- `require_null_terminated` - If 1, JSON must be null-terminated

**Returns:** Pointer to root cJSON item, or NULL on parse error

---

```c
const char *cJSON_GetErrorPtr(void);
```

Get the parse error location. Call after `cJSON_Parse` returns NULL.

**Returns:** Pointer to error location in JSON string

---

### Rendering (JSON String Output)

```c
char *cJSON_Print(cJSON *item);
```

Render a cJSON item to a formatted JSON string (with indentation).

**Returns:** Dynamically allocated string, caller must `free()` when done

---

```c
char *cJSON_PrintUnformatted(cJSON *item);
```

Render to a compact JSON string (no whitespace).

**Returns:** Dynamically allocated string, caller must `free()` when done

---

```c
char *cJSON_PrintBuffered(cJSON *item, int prebuffer, int fmt);
```

Render with pre-allocated buffer hint.

**Parameters:**
- `prebuffer` - Estimated output size for optimization
- `fmt` - 0=unformatted, 1=formatted

**Returns:** Dynamically allocated string

---

### Memory Management

```c
void cJSON_Delete(cJSON *c);
```

Delete a cJSON tree and all its children.

---

### Array Operations

```c
int cJSON_GetArraySize(cJSON *array);
```

Get number of items in an array.

**Returns:** Item count, or 0 if not an array

---

```c
cJSON *cJSON_GetArrayItem(cJSON *array, int item);
```

Get array element by index.

**Returns:** Pointer to item, or NULL if out of bounds or not an array

---

### Object Operations

```c
cJSON *cJSON_GetObjectItem(cJSON *object, const char *string);
```

Get object member by key (case-insensitive).

**Returns:** Pointer to item, or NULL if key not found

---

### Creating Items

```c
cJSON *cJSON_CreateNull(void);
cJSON *cJSON_CreateTrue(void);
cJSON *cJSON_CreateFalse(void);
cJSON *cJSON_CreateBool(int b);
cJSON *cJSON_CreateNumber(double num);
cJSON *cJSON_CreateString(const char *string);
cJSON *cJSON_CreateArray(void);
cJSON *cJSON_CreateObject(void);
```

Create primitive and container cJSON items.

---

```c
cJSON *cJSON_CreateIntArray(const int *numbers, int count);
cJSON *cJSON_CreateFloatArray(const float *numbers, int count);
cJSON *cJSON_CreateDoubleArray(const double *numbers, int count);
cJSON *cJSON_CreateStringArray(const char **strings, int count);
```

Create arrays of numbers or strings.

---

### Adding Items to Arrays/Objects

```c
void cJSON_AddItemToArray(cJSON *array, cJSON *item);
void cJSON_AddItemToObject(cJSON *object, const char *string, cJSON *item);
void cJSON_AddItemToObjectCS(cJSON *object, const char *string, cJSON *item);
```

Add items to containers. `cJSON_AddItemToObjectCS` treats string as const.

---

```c
void cJSON_AddItemReferenceToArray(cJSON *array, cJSON *item);
void cJSON_AddItemReferenceToObject(cJSON *object, const char *string, cJSON *item);
```

Add a reference to an existing cJSON item (item is not copied).

---

### Removing/Detaching Items

```c
cJSON *cJSON_DetachItemFromArray(cJSON *array, int which);
void cJSON_DeleteItemFromArray(cJSON *array, int which);
cJSON *cJSON_DetachItemFromObject(cJSON *object, const char *string);
void cJSON_DeleteItemFromObject(cJSON *object, const char *string);
```

Remove and optionally delete items.

---

### Replacing Items

```c
void cJSON_InsertItemInArray(cJSON *array, int which, cJSON *newitem);
void cJSON_ReplaceItemInArray(cJSON *array, int which, cJSON *newitem);
void cJSON_ReplaceItemInObject(cJSON *object, const char *string, cJSON *newitem);
```

Replace items in arrays/objects.

---

### Duplication

```c
cJSON *cJSON_Duplicate(cJSON *item, int recurse);
```

Duplicate a cJSON item. If `recurse` is non-zero, also duplicate children.

**Returns:** New cJSON tree (caller must delete)

---

### Utility

```c
void cJSON_Minify(char *json);
```

Remove whitespace from JSON string to minimize size.

---

## Convenience Macros

```c
#define cJSON_AddNullToObject(object, name)
#define cJSON_AddTrueToObject(object, name)
#define cJSON_AddFalseToObject(object, name)
#define cJSON_AddBoolToObject(object, name, b)
#define cJSON_AddNumberToObject(object, name, n)
#define cJSON_AddStringToObject(object, name, s)
```

Quickly add items to an object.

---

```c
#define cJSON_SetIntValue(object, val)
#define cJSON_SetNumberValue(object, val)
```

Set numeric values (updates both valueint and valuedouble).

---

## Usage Example

```c
// Parse JSON
const char *json_str = "{\"role\":\"assistant\",\"msgType\":1,\"data\":42}";
cJSON *root = cJSON_Parse(json_str);
if (root == NULL) {
    // Parse error
}

// Extract values
cJSON *role = cJSON_GetObjectItem(root, "role");
if (role && role->type == cJSON_String) {
    printf("Role: %s\n", role->valuestring);
}

cJSON *msgType = cJSON_GetObjectItem(root, "msgType");
if (msgType && msgType->type == cJSON_Number) {
    printf("msgType: %d\n", msgType->valueint);
}

// Create JSON
cJSON *obj = cJSON_CreateObject();
cJSON_AddStringToObject(obj, "name", "test");
cJSON_AddNumberToObject(obj, "value", 123);

char *out = cJSON_Print(obj);
printf("%s\n", out);
free(out);

cJSON_Delete(obj);
cJSON_Delete(root);
```

## Embedded Considerations

- No dynamic memory by default (use `cJSON_InitHooks` for custom allocators)
- Recursive descent parser - stack usage depends on nesting depth
- Suitable for resource-constrained systems
