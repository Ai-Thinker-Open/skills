# CLI Command Line Interface API Reference

> Source file: `components/stage/cli/cli/include/cli.h`  
> Lightweight command-line interface, supports static/dynamic command registration, history, and auto-completion (partial configuration).

---

## Overview

CLI is the command-line debugging tool for BL602. After registering commands via `aos_cli_register_command`, you can type commands in a serial terminal to execute the corresponding functions. Supports static commands (determined at compile time) and dynamic commands (added/removed at runtime).

```
> help
> mycommand arg1 arg2
Command executed with result: 0
```

---

## Header File

```c
#include "cli.h"
```

---

## Type Definitions

### `cli_command`

Structure for registering a command; each command contains a name, help text, and a function pointer:

```c
struct cli_command {
    const char *name;      // Command name, e.g., "reboot"
    const char *help;      // Help text, e.g., "Reboot the device"

    void (*function)(char *pcWriteBuffer, int xWriteBufferLen,
                     int argc, char **argv);
};
```

---

## Function API

### `aos_cli_init`

Initialize CLI (creates a task).

```c
int aos_cli_init(int use_thread);
```

| Parameter | Description |
|------|------|
| `use_thread` | 1=create independent task, 0=synchronous mode |

**Return value**: 0=success

---

### `aos_cli_register_command`

Register a single command.

```c
int aos_cli_register_command(const struct cli_command *command);
```

**Return value**: 0=success

---

### `aos_cli_register_commands`

Register multiple commands in bulk.

```c
int aos_cli_register_commands(const struct cli_command *commands, int num_commands);
```

| Parameter | Description |
|------|------|
| `commands` | Command array |
| `num_commands` | Number of commands |

**Return value**: 0=success

---

### `aos_cli_unregister_command`

Unregister a single command.

```c
int aos_cli_unregister_command(const struct cli_command *command);
```

**Return value**: 0=success

---

### `aos_cli_unregister_commands`

Unregister multiple commands in bulk.

```c
int aos_cli_unregister_commands(const struct cli_command *commands, int num_commands);
```

---

### `aos_cli_stop`

Stop CLI task and clean up.

```c
int aos_cli_stop(void);
```

---

### `aos_cli_printf`

CLI-specific print function (outputs to command-line buffer).

```c
int aos_cli_printf(const char *buff, ...);
// or via the cmd_printf macro
cmd_printf("Result: %d\r\n", value);
```

---

### `aos_cli_task_create`

Create CLI task (can be called independently).

```c
int aos_cli_task_create(void);
```

---

### `aos_cli_task_get`

Get CLI task handle.

```c
void *aos_cli_task_get(void);
```

---

### `aos_cli_input_direct`

Feed data directly to CLI (bypass serial port, used for automated testing).

```c
void aos_cli_input_direct(char *buffer, int count);
```

---

## Macro Description

### `cmd_printf`

CLI-specific print macro (automatically writes to output buffer):

```c
cmd_printf("Value=%d\r\n", value);
```

> Unlike regular `printf`, `cmd_printf` writes data to the CLI output buffer, making it suitable for use in command callback functions.

---

## Usage Examples

### Define and Register a Command

```c
#include "cli.h"

static void my_cmd_handler(char *pcWriteBuffer, int xWriteBufferLen,
                           int argc, char **argv)
{
    if (argc < 2) {
        cmd_printf("Usage: mycmd <arg1>\r\n");
        return;
    }
    cmd_printf("arg1 = %s\r\n", argv[1]);
}

// Define a static command
static const struct cli_command my_commands[] = {
    {
        .name = "mycmd",
        .help = "My custom command",
        .function = my_cmd_handler,
    },
};

// Register the command
aos_cli_register_commands(my_commands, 1);
```

### Command with Argument Parsing

```c
static void set_led_handler(char *pcWriteBuffer, int xWriteBufferLen,
                            int argc, char **argv)
{
    if (argc != 3) {
        cmd_printf("Usage: led <on|off> <color>\r\n");
        return;
    }

    const char *action = argv[1];  // "on" or "off"
    const char *color = argv[2];   // "red", "green", "blue"

    if (strcmp(action, "on") == 0) {
        cmd_printf("LED %s ON\r\n", color);
    } else {
        cmd_printf("LED %s OFF\r\n", color);
    }
}

static const struct cli_command led_commands[] = {
    {
        .name = "led",
        .help = "Control LED: led <on|off> <color>",
        .function = set_led_handler,
    },
};

aos_cli_register_command(&led_commands[0]);
```

### Static Command Attribute

Commands defined in a specific section can be auto-registered (no need to manually call the registration function):

```c
// Automatically placed in .static_cli_cmds section at compile time
static const struct cli_command hello_cmd
    __attribute__((used, section(".static_cli_cmds"))) = {
    .name = "hello",
    .help = "Say hello",
    .function = hello_handler,
};
```
