# BL616/BL618 Shell CLI Documentation

This document describes the Shell CLI component in the Bouffalo SDK.

## Overview

The Shell is a command-line interface component based on RT-Thread's FinShell. It provides:
- Command registration via linker symbol tables
- Command history (up/down arrows)
- Tab completion
- Built-in help command
- Echo control

## Header

```c
#include "shell.h"
```

## Core Types

### Command Function Type

```c
typedef int (*cmd_function_t)(int argc, char **argv);
```

Commands must follow this signature:
- `argc` - argument count (including command name)
- `argv` - array of argument strings
- Return `0` on success

## Key Functions

### shell_init

Initializes the shell and registers command symbols from linker sections.

```c
void shell_init(void);
```

**Example:**
```c
int main(void)
{
    board_init();
    shell_init();  // Initialize shell with default prompt
    // ...
}
```

---

### shell_init_with_task

Initializes shell running in an RTOS task (when using FreeRTOS).

```c
void shell_init_with_task(struct bflb_device_s *shell);
```

---

### shell_handler

Processes incoming character data from UART. Call this in your main loop.

```c
void shell_handler(uint8_t data);
```

**Typical usage pattern:**
```c
int main(void)
{
    board_init();
    struct bflb_device_s *uart0 = bflb_device_get_by_name("uart0");
    shell_init();
    
    int ch;
    while (1) {
        if ((ch = bflb_uart_getchar(uart0)) != -1) {
            shell_handler(ch);  // Feed each character to shell
        }
    }
}
```

---

### shell_set_prompt

Sets a custom shell prompt.

```c
int shell_set_prompt(const char *prompt);
```

**Example:**
```c
shell_set_prompt("BL618> ");
```

---

### shell_set_print

Sets the print function (defaults to `printf`).

```c
int shell_set_print(void (*shell_printf)(char *fmt, ...));
```

---

### shell_set_echo

Enables or disables character echo.

```c
int shell_set_echo(bool enabled);
```

---

### shell_exec

Executes a command string programmatically.

```c
int shell_exec(char *cmd, uint32_t length);
```

**Example:**
```c
shell_exec("help", 4);
```

---

## Command Registration Macros

### SHELL_CMD_EXPORT

Exports a function as a shell command. The function name becomes the command name.

```c
SHELL_CMD_EXPORT(command, description)
```

**Parameters:**
- `command` - Function name (becomes command name)
- `description` - Help text shown with `help` command

**Example:**
```c
int my_command(int argc, char **argv)
{
    printf("My command executed!\r\n");
    return 0;
}
SHELL_CMD_EXPORT(my_command, "My custom command.);
```

---

### SHELL_CMD_EXPORT_ALIAS

Exports a function with a different command name than the function name.

```c
SHELL_CMD_EXPORT_ALIAS(actual_function, command_name, description)
```

**Example:**
```c
static void led_on(int argc, char **argv)
{
    // Turn LED on
}
SHELL_CMD_EXPORT_ALIAS(led_on, led_on, Turn LED on);
SHELL_CMD_EXPORT_ALIAS(led_on, led_off, Turn LED off);
SHELL_CMD_EXPORT_ALIAS(led_on, led_toggle, Toggle LED);
```

---

## Working Example

```c
#include "bflb_mtimer.h"
#include "bflb_uart.h"
#include "shell.h"
#include "board.h"

static struct bflb_device_s *uart0;

/* Custom command: hello */
static int cmd_hello(int argc, char **argv)
{
    if (argc < 2) {
        printf("Usage: hello <name>\r\n");
        return 0;
    }
    printf("Hello, %s!\r\n", argv[1]);
    return 0;
}
SHELL_CMD_EXPORT_ALIAS(cmd_hello, hello, Say hello);

/* Custom command: gpio_status */
static int cmd_gpio_status(int argc, char **argv)
{
    printf("GPIO Status:\r\n");
    printf("  LED Pin: %d\r\n", 2);
    printf("  Button Pin: %d\r\n", 3);
    return 0;
}
SHELL_CMD_EXPORT_ALIAS(cmd_gpio_status, gpio_status, Show GPIO status);

/* Custom command: add */
static int cmd_add(int argc, char **argv)
{
    int a, b;
    if (argc < 3) {
        printf("Usage: add <a> <b>\r\n");
        return 0;
    }
    a = atoi(argv[1]);
    b = atoi(argv[2]);
    printf("%d + %d = %d\r\n", a, b, a + b);
    return 0;
}
SHELL_CMD_EXPORT_ALIAS(cmd_add, add, Add two numbers);

int main(void)
{
    board_init();
    uart0 = bflb_device_get_by_name("uart0");
    
    shell_init();
    shell_set_prompt("BL618> ");
    
    while (1) {
        int ch = bflb_uart_getchar(uart0);
        if (ch != -1) {
            shell_handler(ch);
        }
    }
}
```

**Usage:**
```
BL618> hello world
Hello, world!
BL618> add 5 3
5 + 3 = 8
BL618> gpio_status
GPIO Status:
  LED Pin: 2
  Button Pin: 3
BL618> help
shell commands list:
hello
gpio_status
add
help
memtrace
```

## Built-in Commands

| Command | Description |
|---------|-------------|
| `help` | List all available commands |
| `memtrace` | Memory read/write: `memtrace <addr> [count]` or `memtrace <addr> <value> <count>` |

## Notes

- Commands are registered via linker symbols (`__fsymtab_start`, `__fsymtab_end`) placed in the `FSymTab` section
- The shell uses `SHELL_CMD_SIZE` (typically 128 bytes) for line buffer
- Command history supports `SHELL_HISTORY_LINES` (typically 8) entries
- Maximum arguments: `SHELL_ARG_NUM` (typically 32)
- Tab completion works for both commands and file paths (when `SHELL_USING_FS` enabled)
