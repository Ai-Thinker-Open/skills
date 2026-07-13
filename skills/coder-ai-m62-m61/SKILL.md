---
name: coder-ai-m62-m61
description: Ai-Thinker BL616/BL618 series module development guide - Wi-Fi 6 + BLE 5.0 module, based on bouffalo_sdk, supporting GPIO, UART, SPI, I2C, DMA, Timer, PWM, ADC, DAC, Flash, WiFi, BLE and other peripheral programming.
---

# Ai-Thinker BL616/BL618 Series Development Guide

## Programming Paradigm

> **Important**: Unless the user explicitly requests **register-level (bare metal) programming**, all code examples in this skill use the **LHAL (Low Level Hardware Abstraction Layer) library** for development, with loop logic implemented via **FreeRTOS tasks**.

**Default Programming Method** (LHAL + FreeRTOS):
- Peripheral initialization, configuration: call LHAL APIs (e.g. `bflb_gpio_init`, `bflb_uart_init`)
- Business logic loops: placed in FreeRTOS tasks (`xTaskCreate`)
- Delays: `vTaskDelay` (not `HAL_Delay`)

**BL616/BL618 FreeRTOS Special Notes**:
- **Must call `vTaskStartScheduler()`** to start the task scheduler — this is **NOT** automatic on BL616/BL618
- After `vTaskStartScheduler()` is called, it never returns; place task creation before it
- **Before the scheduler starts, `vTaskDelay` CANNOT be used** — the delay relies on the scheduler being active
- **If a task's loop has no delay, `vTaskDelay` must be called to yield the CPU**, otherwise other tasks cannot run and the system will appear to hang
- Correct approach: create tasks → call `vTaskStartScheduler()`; inside tasks: `while(1) { process business; vTaskDelay(pdMS_TO_TICKS(100)); }`

**Register-Level Programming** (when explicitly requested by the user):
- Directly manipulate `*(volatile uint32_t *)addr` to access peripheral registers
- BL616/BL618 peripheral base addresses differ from BL602; refer to the register mapping tables in each chapter

---

## Product Overview

**BL616/BL618** are Wi-Fi 6 & BLE 5.0 dual-mode modules developed by Ai-Thinker Technology based on Bouffalolab BL616/BL618 chips, supporting:

- Wi-Fi 802.11a/b/g/n/ac/ax (Wi-Fi 6), supporting 2.4GHz and 5GHz
- Bluetooth Low Energy 5.0 + Bluetooth Mesh
- 32-bit RISC-V CPU (up to 320MHz)
- Rich peripheral interfaces: GPIO, UART, SPI, I2C, PWM, ADC, DAC, DMA, Timer, etc.
- Multiple low-power modes

### Selection Guide

| Model | Chip | Package | Antenna | Key Feature |
|-----|------|------|-----|------|
| **Ai-M61 Series** (BL618) | | | | |
| Ai-M61-32S | BL618 | SMD-38 | PCB On-board | Audio Codec, DVP Camera, Display |
| Ai-M61-32SU | BL618 | SMD-38 | IPEX | Audio Codec, DVP Camera, Display |
| **Ai-M62 Series** (BL616) | | | | |
| Ai-M62-07S | BL616 | SMD-22 | PCB On-board | Ultra-compact, Wi-Fi 6 |
| Ai-M62-12F | BL616 | SMD-22 | PCB On-board | Classic, Wi-Fi 6 |
| Ai-M62-13 | BL616 | SMD-18 | Stamp Hole | Open board, Wi-Fi 6 |
| Ai-M62-13U | BL616 | SMD-18 | IPEX | Open board, IPEX |
| Ai-M62-32S | BL616 | SMD-38 | PCB On-board | More GPIO, Wi-Fi 6 |
| Ai-M62-M2-I | BL616 | M.2 | IPEX | M.2 form factor |
| Ai-M62-M01L | BL616 | SMD-16 | PCB On-board | Ultra-compact |
| Ai-M62-CBS | BL616 | CBS-61 | — | SDIO/USB slave interface |
| **Development Boards** | | | | |
| Ai-M61-32S-Kit | BL618 | NodeMCU | — | Ai-M61 dev board |
| Ai-M62-12F-Kit | BL616 | NodeMCU | — | Ai-M62 dev board |
| Ai-M62-13-Kit | BL616 | NodeMCU | — | Ai-M62 dev board |
| Ai-M62-32S-Kit | BL616 | NodeMCU | — | Ai-M62 dev board |
| Ai-M62-M2-I-Kit | BL616 | NodeMCU | — | Ai-M62 M.2 dev board |

---

## Development Environment Setup (Required Reading)

> **Important Reminder**: Before writing any code, you must complete the environment setup. **Toolchain installation and SDK cloning are prerequisites for programming**, otherwise you cannot compile and flash firmware.

### Step 1: Determine Current Platform

**Windows** (PowerShell):

```powershell
echo $env:OS
# Output Windows_NT indicates Windows system
```

**Linux / WSL / macOS** (Terminal):

```bash
uname -s
# Output Linux indicates Linux/WSL, Darwin indicates macOS
```

### Step 2: Install Toolchain (by Platform)

#### Windows Environment

**Applicable Scenario**: Native Windows development, using Bouffalolab's officially pre-compiled RISC-V toolchain.

**Step 1: Download Toolchain**

> ⚠️ **Do not use GCC for Windows (e.g. mingw-w64-gcc)**, BL616/BL618 must use the `riscv64-unknown-elf-gcc` RISC-V cross-compilation toolchain officially provided by Bouffalolab.

Download the pre-compiled toolchain from GitHub (Windows 64-bit):

- Official link: https://github.com/bouffalolab/toolchain_gcc_t-head_windows
- Select the latest version in the `x86_64` directory (e.g. `x86_64-YYYY.MM.DD-mingw-w64.zip`)
- Extract to `C:\toolchain\` or any directory
- **Add the toolchain `bin` directory to the system environment variable PATH**
- Also add the SDK's `tools/ninja` subdirectory to PATH

**Verify Installation**:

```powershell
# Open "Command Prompt (CMD)" or "PowerShell", execute:
riscv64-unknown-elf-gcc -v
# Should output version info including "riscv64-unknown-elf"

# Verify ninja (built into SDK)
# Assuming SDK cloned to C:\bouffalo_sdk
C:\bouffalo_sdk\tools\ninja\ninja --version
# Should output version number
```

**Set PATH Environment Variable** (execute after toolchain verification passes):

```powershell
# Method 1: Temporary for current terminal (must re-execute each time terminal opens)
set PATH=C:\toolchain\riscv64-unknown-elf\bin;%PATH%
set PATH=C:\bouffalo_sdk\tools\ninja;%PATH%

# Method 2: Permanent (recommended)
# 1. Open "System Properties" → "Advanced" → "Environment Variables"
# 2. Find Path in "System Variables", click "Edit"
# 3. Add the following two absolute paths (adjust based on actual path):
#    C:\toolchain\riscv64-unknown-elf\bin
#    C:\bouffalo_sdk\tools\ninja
# 4. Click "OK" to save, restart terminal for changes to take effect
```

> **Critical Paths**: All three of the following paths need to be added to PATH:
> 1. Toolchain `bin` directory (e.g. `C:\toolchain\riscv64-unknown-elf\bin`) — provides `riscv64-unknown-elf-gcc`
> 2. SDK `tools/ninja` directory (e.g. `C:\bouffalo_sdk\tools\ninja`) — provides `ninja` build tool
> ⚠️ Must be **absolute paths**, relative paths cannot be used.

**Step 2: Install Python and Flashing Tools**

```powershell
# Install Python3 (from python.org or Microsoft Store)
# Make sure to check "Add Python to PATH" during installation

# Install PySerial (for serial flashing)
pip install pyserial
```

**Verify Installation**:

```powershell
python --version
pip show pyserial
```

> **If errors occur, cannot proceed**, must resolve toolchain issues first.

#### Linux (Ubuntu 20.04) Environment

**Applicable Scenario**: Native Ubuntu, Debian, WSL2 and other Linux environments.

**Step 1: Download Toolchain**

Bouffalolab official Linux toolchain:

- Official link: https://github.com/bouffalolab/toolchain_gcc_t-head_linux
- Select `x86_64-YYYY.MM.DD-linux-glibc-x86_64.tar.xz` or similar file
- Extract to `/opt/toolchain/`:

```bash
cd /tmp
wget https://github.com/bouffalolab/toolchain_gcc_t-head_linux/releases/download/v1.2.0/x86_64-2024.10.08-linux-glibc-x86_64.tar.xz
sudo mkdir -p /opt/toolchain
sudo tar -xf x86_64-2024.10.08-linux-glibc-x86_64.tar.xz -C /opt/toolchain/
export PATH=/opt/toolchain/x86_64-2024.10.08-linux-glibc-x86_64/bin:$PATH

# Verify
riscv64-unknown-elf-gcc -v
```

**Step 2: Configure System Environment Variables (Permanent)**

```bash
# Append the following to ~/.bashrc (path must match actual extraction directory)
echo 'export PATH=/opt/toolchain/x86_64-2024.10.08-linux-glibc-x86_64/bin:$PATH' >> ~/.bashrc
source ~/.bashrc
```

**Step 3: Install Dependencies**

```bash
sudo apt update
sudo apt install -y build-essential git python3 python3-pip python3-dev
pip3 install pyserial
```

**Verify Installation**:

```bash
riscv64-unknown-elf-gcc -v
python3 --version
pip3 show pyserial
```

> **If errors occur, cannot proceed**, must resolve toolchain issues first.

#### macOS Environment

**Step 1: Download Toolchain**

Bouffalolab **does not provide macOS pre-compiled toolchain**, must compile from source:

```bash
# Install dependencies
brew install python3 git

# Clone build scripts
git clone https://github.com/p4ddy1/pine_ox64.git
cd pine_ox64
# Refer to https://github.com/p4ddy1/pine_ox64/blob/main/build_toolchain_macos.md
# Follow documentation to compile riscv64-unknown-elf-gcc
```

**Step 2: Install Python**

```bash
brew install python3
pip3 install pyserial
```

**Verify Installation**:

```bash
riscv64-unknown-elf-gcc -v
python3 --version
pip3 show pyserial
```

> macOS toolchain compilation takes a long time (approximately 30~60 minutes), it is recommended to use Linux/WSL2 for development if possible.

#### WSL2 Environment

WSL2 is essentially a Linux environment, please refer to the installation steps in the "Linux (Ubuntu 20.04) Environment" section above (download the Linux version toolchain).

> **WSL2 Serial Port Mapping**: Windows 11 does not support automatic serial port mapping, manual mapping is required in Windows PowerShell (Administrator):
> ```powershell
> # List devices
> usbipd list
> # Bind and attach to WSL
> usbipd bind --busid <busid>
> usbipd attach --wsl --busid <busid>
> ```
> Then verify in WSL with `ls /dev/ttyACM*`.

---

### Step 3: Clone SDK (All Platforms)

> **Users with existing local SDK**: If the SDK is already cloned locally (e.g. `/path/to/bouffalo_sdk`), set the environment variable directly and skip the cloning step:
> ```bash
> export SDK_ROOT=/path/to/bouffalo_sdk
> ```

After toolchain installation is complete, all platforms execute the same SDK acquisition steps:

```bash
# Choose an appropriate directory to store projects (e.g. ~/projects or D:\workspace)

# Preferred: Clone from GitHub (official source)
git clone https://github.com/bouffalolab/bouffalo_sdk.git
# If domestic access is unstable, use mirror:
# git clone https://gitee.com/Ai-Thinker-Open/bouffalo_sdk.git

cd bouffalo_sdk

# Must execute: Check and switch to stable version branch (recommended)
git checkout v1.0.0      # Or git checkout v0.9.6 or other stable version
# If no version specified, default clone is main branch (may be unstable)

# If specific chip support is needed, initialize submodules
git submodule update --init --recursive

**Linux/WSL Extra Step**: Set toolchain permissions

```bash
cd toolchain/riscv/Linux/
bash chmod755.sh
# Or manually grant permissions
chmod +x riscv64-elf-x86_64/bin/*
```

### Step 4: Compilation Verification

> **Windows Users**: Execute compilation directly in **PowerShell** or **Command Prompt (CMD)**, **no need to install MSYS2 or MinGW environment**.
> **Linux/WSL Users**: Execute in standard Linux terminal.

```bash
cd bouffalo_sdk

# List supported chips and development boards
ls bsp/board/     # View supported development boards
ls examples/      # View example projects

# Compile Hello World example (BL616)
cd examples/helloworld
make CHIP=bl616 BOARD=bl616dk -j8

# Compile Hello World example (BL618)
make CHIP=bl618 BOARD=bl618dk -j8
```

Successful compilation will generate firmware file (`.bin`) in the `build/out/` directory.

### Step 5: Flash Verification

#### List Available Serial Ports

Before flashing, **actively list** currently available serial ports and let the user confirm which port the module is connected to:

```bash
# Linux - List all serial devices
ls -l /dev/ttyUSB* /dev/ttyACM* /dev/ttyS* 2>/dev/null

# macOS - List USB serial ports
ls /dev/tty.usbserial* /dev/tty.usbmodem* 2>/dev/null

# Windows - List COM ports
mode | grep -i "com"
```

> **AI should actively execute the above commands to get the available port list**, then ask the user: "The following serial ports were detected, please confirm which one the module is connected to?"

#### Flash Command

```bash
# BL616 flash (replace /dev/ttyUSB0 with actual serial port name)
make flash CHIP=bl616 BOARD=bl616dk COMX=/dev/ttyUSB0 BAUDRATE=2000000

# BL618 flash
make flash CHIP=bl618 BOARD=bl618dk COMX=/dev/ttyUSB0 BAUDRATE=2000000
```

> For detailed flashing tutorials and tool downloads, please refer to https://dev.bouffalolab.com/

---

## BL616/BL618 GPIO Register Programming

**Prerequisite**: Must have completed "Development Environment Setup" Steps 2 and 3 above.

**Important**: BL616/BL618 peripheral base addresses are completely different from BL602, **do not mix BL602 addresses**.

### BL616/BL618 Memory Map (Peripheral Section)

| Peripheral | Base Address | Description |
|------|--------|------|
| GLB (Global Control) | `0x20000000` | Contains GPIO configuration |
| GPIP (General Input) | `0x20002000` | GPIO input, interrupts, etc. |
| UART0 | `0x2000A000` | Serial 0 |
| UART1 | `0x2000A100` | Serial 1 |
| SPI | `0x2000A200` | SPI master/slave controller |
| I2C0 | `0x2000A300` | I2C master/slave controller |
| PWM | `0x2000A400` | PWM output |
| TIMER | `0x2000A500` | Timer/Watchdog |
| DMA | `0x2000C000` | DMA controller |

### GPIO Base Address

- **GLB_BASE = `0x20000000`**
- GPIO configuration register: `GLB_BASE + 0x??` (each pin has independent configuration registers, not BL602's shared register approach)
- GPIO output value: `GLB_BASE + 0x??`
- GPIO output enable: `GLB_BASE + 0x??`

> **Note**: BL616/BL618 GPIO register layout differs from BL602, each pin has independent configuration registers (per-pin register) instead of sharing one register per 2 pins. Before writing register-level code, please refer to `drivers/soc/bl616/std/include/hardware/glb_reg.h` and `drivers/soc/bl616/std/include/bl616_glb_gpio.h`.

### GPIO Pin Limitations

BL616 pins: `GPIO0 ~ GPIO3, GPIO10 ~ GPIO17, GPIO20 ~ GPIO22, GPIO27 ~ GPIO30`
BL618 pins: `GPIO0 ~ GPIO34` (more pins)

> **Before configuring GPIO**, the pin's function must be selected as **GPIO mode** (rather than UART/SPI/I2C or other alternate functions) via the GLB register. This is done through the `GLB_GPIO_FUNC_SEL` register.

### Project Structure

Project structure in `bouffalo_sdk`:

```
bouffalo_sdk/
├── examples/
│   └── helloworld/              # Example project
│       └── main.c               # Entry file
├── drivers/
│   ├── lhal/                    # LHAL peripheral abstraction layer (cross-chip common)
│   └── soc/                     # Chip-specific drivers
│       └── bl616/               # BL616 chip driver
├── bsp/
│   └── board/bl616dk/           # BL616 development board configuration
└── tools/                       # Flashing tools
```

---

## Firmware Flashing

### Flashing Tools

| Tool | Download | Description |
|-----|------|-----|
| BouffaloLab Dev Kit | https://dev.bouffalolab.com/ | Official flashing + debugging tool |
| BL Dev Cube | https://github.com/bouffalolab/bouffalo_sdk/releases | Command-line flashing tool |

### Flashing Steps

1. **Confirm Serial Port**: Refer to "List Available Serial Ports" above
2. **Enter Flash Mode**: Pull the module's **BOOT pin low**, then reset
3. **Execute Flash**:

```bash
make flash CHIP=bl616 BOARD=bl616dk COMX=/dev/ttyUSB0 BAUDRATE=2000000
```

4. **Verify**: After successful flashing, the module will automatically reboot, serial output should appear

---

## AT Command Development

### AT Firmware

BL616/BL618 modules support standard AT command set. For details, please refer to the AT firmware and AT command documentation provided by Ai-Thinker.

### Common AT Commands

```c
// System
AT                  // Test command
AT+RST              // Restart
AT+GMR              // Query version

// Wi-Fi
AT+CWMODE=1         // Set station mode
AT+CWLAP            // Scan hotspots
AT+CWJAP="SSID","PASSWORD"  // Connect Wi-Fi
AT+CWQAP            // Disconnect Wi-Fi
AT+CIFSR            // Query IP address

// TCP/UDP
AT+CIPSTART="TCP","192.168.1.100",8080  // Establish TCP connection
AT+CIPSEND=10       // Send data
AT+CIPCLOSE         // Close connection

// BLE
AT+BLEINIT=1        // Initialize BLE
AT+BLEADVISENABLE=1 // Start advertising
AT+BLESEND=5,"12345"  // Send data
```

---

## Secondary Development - Peripheral Programming

> Complete API function signatures and type definitions can be found in the standalone documents under the `references/` directory.
> This chapter demonstrates peripheral initialization and operation flow through specific examples.

### GPIO

```c
#include "bflb_gpio.h"

struct bflb_device_s *gpio;

// Initialize GPIO
gpio = bflb_device_get_by_name("gpio");
bflb_gpio_init(gpio, GPIO_PIN_0, GPIO_MODE_OUTPUT_PP, GPIO puxx_pull_up);
bflb_gpio_init(gpio, GPIO_PIN_1, GPIO_MODE_INPUT, GPIO_PULL_UP);

// Write GPIO
bflb_gpio_set(gpio, GPIO_PIN_0);  // Set high
bflb_gpio_reset(gpio, GPIO_PIN_0);  // Set low

// Read GPIO
uint32_t value = bflb_gpio_read(gpio, GPIO_PIN_1);

// Toggle
bflb_gpio_toggle(gpio, GPIO_PIN_0);
```

### UART

```c
#include "bflb_uart.h"

struct bflb_device_s *uart;

// Initialize UART
uart = bflb_device_get_by_name("uart0");
struct bflb_uart_config_s cfg = {
    .data_bits = UART_DATA_BITS_8,
    .stop_bits = UART_STOP_BITS_1,
    .parity = UART_PARITY_NONE,
    .bit_order = UART_BIT_ORDER_LSB,
    .flow_control = UART_FLOW_CONTROL_NONE,
    .baudrate = 115200,
};
bflb_uart_init(uart, &cfg);

// Send data
bflb_uart_putchar(uart, 'A');

// Receive data (polling)
uint8_t ch;
bflb_uart_getchar(uart, &ch);
```

### DMA

```c
#include "bflb_dma.h"

struct bflb_device_s *dma;
struct bflb_dma_channel_lli_pool_s lli_pool[1];
struct bflb_dma_channel_lli_transfer_s transfer;

dma = bflb_device_get_by_name("dma0");
bflb_dma_channel_init(dma, DMA_CH0, &dma_cfg);
bflb_dma_channel_lli_reinit(dma, DMA_CH0, lli_pool, 1);
bflb_dma_channel_lli_add_node(dma, DMA_CH0, &transfer);
bflb_dma_channel_start(dma, DMA_CH0);
```

### Timer

```c
#include "bflb_timer.h"

struct bflb_device_s *timer;

timer = bflb_device_get_by_name("timer0");
struct bflb_timer_config_s cfg = {
    .prescale = 250,
    .counter_mode = TIMER_COUNTER_MODE_PERIODIC,
    .trigger_cmp = 0,
};
bflb_timer_init(timer, &cfg);
bflb_timer_start(timer, 1000);  // 1ms period

// Stop
bflb_timer_stop(timer);
```

### PWM

```c
#include "bflb_pwm.h"

struct bflb_device_s *pwm;

pwm = bflb_device_get_by_name("pwm0");
struct bflb_pwm_config_s cfg = {
    .freq = 1000,       // 1kHz
    .channel = PWM_CH0,
};
bflb_pwm_init(pwm, &cfg);
bflb_pwm_set_pulsewidth(pwm, PWM_CH0, 500);  // 50% duty cycle
bflb_pwm_start(pwm);
```

### ADC

```c
#include "bflb_adc.h"

struct bflb_device_s *adc;

adc = bflb_device_get_by_name("adc");
struct bflb_adc_config_s cfg = {
    .res = ADC_RES6,        // 6-bit resolution (or other)
    .chan = ADC_CHAN0,
};
bflb_adc_init(adc, &cfg);

uint16_t value;
bflb_adc_read_raw(adc, &value);
```

### SPI

```c
#include "bflb_spi.h"

struct bflb_device_s *spi;

spi = bflb_device_get_by_name("spi0");
struct bflb_spi_config_s cfg = {
    .freq = 1000000,   // 1MHz
    .role = SPI_ROLE_MASTER,
    .mode = SPI_MODE_0,
    .data_width = SPI_DATA_WIDTH_8BIT,
};
bflb_spi_init(spi, &cfg);

uint8_t tx_buf[4] = {0x01, 0x02, 0x03, 0x04};
uint8_t rx_buf[4];
bflb_spi_transfer(spi, tx_buf, rx_buf, 4);
```

### I2C

```c
#include "bflb_i2c.h"

struct bflb_device_s *i2c;

i2c = bflb_device_get_by_name("i2c0");
struct bflb_i2c_config_s cfg = {
    .freq = 400000,   // 400kHz
    .addr = 0x00,
};
bflb_i2c_init(i2c, &cfg);

// Send
uint8_t data[2] = {0x30, 0x93};
bflb_i2c_send(i2c, 0x44, data, 2);

// Receive
uint8_t buf[6];
bflb_i2c_recv(i2c, 0x44, buf, 6);
```

---

## FreeRTOS Task Development

### Task Creation Example

BL616/BL618 FreeRTOS applications typically complete peripheral initialization, create business tasks, then call `vTaskStartScheduler()` to start the scheduler. **Do NOT** call `vTaskDelay` before the scheduler starts.

```c
#include "FreeRTOS.h"
#include "task.h"

// Task function
static void my_task(void *param)
{
    (void)param;
    while (1) {
        // Business logic
        printf("Task running\r\n");

        // Must call delay to yield CPU, otherwise system hangs
        vTaskDelay(pdMS_TO_TICKS(1000));
    }
}

void app_main(void)
{
    printf("System init\r\n");

    // 1. Initialize peripherals
    // ...

    // 2. Create tasks (before scheduler starts)
    BaseType_t ret = xTaskCreate(
        my_task,               // Task function
        "my_task",             // Task name (for debugging only)
        512,                   // Stack depth (words)
        NULL,                  // Parameter
        5,                     // Priority (1-15)
        NULL                   // Task handle (can be NULL if not needed)
    );

    if (ret != pdPASS) {
        printf("Task create failed\r\n");
        return;
    }

    // 3. Start the scheduler — this call NEVER returns
    vTaskStartScheduler();

    // Code after this line will NOT execute
}
```

### Key Points

| Key Point | Description |
|-----|------|
| **Must call `vTaskStartScheduler()`** | Scheduler is **NOT** auto-started. Create all tasks first, then call it. This call never returns. |
| **No `vTaskDelay` before scheduler** | `vTaskDelay` relies on the scheduler being active. Calling it before `vTaskStartScheduler()` will fail. |
| **Main loop must delay** | Inside tasks, if the loop has no delay, other tasks cannot be scheduled and the system will appear to hang. |
| **Use `vTaskDelay`** | Do not use non-RTOS delays like `HAL_Delay`, `usleep`. |
| **`pdMS_TO_TICKS`** | Converts milliseconds to ticks, e.g. `pdMS_TO_TICKS(500)` = 500ms. |
| **Stack depth unit** | FreeRTOS stack depth is measured in **words (4 bytes)**, 512 = 2048 bytes. |

### Common FreeRTOS API

```c
// Delay (recommended)
vTaskDelay(pdMS_TO_TICKS(100));         // Delay 100ms

// Get current tick count
TickType_t now = xTaskGetTickCount();

// Delete task
vTaskDelete(NULL);                     // Delete self
// vTaskDelete(task_handle);          // Delete specified task

// Suspend/Resume scheduler (critical section)
vTaskSuspendAll();                     // Suspend scheduler
// ... critical section code ...
xTaskResumeAll();                      // Resume scheduler

// Message queue
QueueHandle_t q = xQueueCreate(10, sizeof(uint32_t));
xQueueSend(q, &value, portMAX_DELAY);
xQueueReceive(q, &value, portMAX_DELAY);

// Binary semaphore (for interrupt synchronization)
SemaphoreHandle_t sem = xSemaphoreCreateBinary();
xSemaphoreGive(sem);
xSemaphoreTake(sem, portMAX_DELAY);
```

---

## Secondary Development - WiFi Programming

### Station Mode

```c
#include "wifi_mgmr.h"

wifi_mgmr_sta_connect_params_t params = {
    .ssid = "SSID",
    .password = "PASSWORD",
    .country_code = "CN",
};

int ret = wifi_mgmr_sta_connect(&params);
if (ret == 0) {
    printf("WiFi connected\r\n");
}
```

### SoftAP Mode

```c
#include "wifi_mgmr.h"

wifi_mgmr_ap_params_t ap_params = {
    .ssid = "BL616-Setup",
    .password = "12345678",
    .channel = 6,
};

int ret = wifi_mgmr_ap_start(&ap_params);
```

### MQTT

```c
#include "mqtt_client.h"

mqtt_client_config_t mqtt_config = {
    .broker_url = "mqtt://broker.emqx.io:1883",
    .client_id = "bl616-client",
};

mqtt_client_handle_t mqtt = mqtt_client_new(&mqtt_config);
mqtt_client_subscribe(mqtt, "/topic", callback);
mqtt_client_publish(mqtt, "/topic", "Hello", 5, 0);
```

---

## Secondary Development - BLE Programming

```c
#include "ble_lib.h"

ble_gap_adv_params_t adv_params = {
    .adv_type = BLE_GAP_ADV_TYPE_IND,
    .adv_interval = 160,  // 100ms
};

ble_stack_init();
ble_gap_adv_start(&adv_params, "BL616");
```

---

## API Reference

Detailed API documentation is stored independently in the `references/` directory, totaling **107 documents**, covering peripheral drivers, system components, network protocols, wireless communication, security encryption, and all other functions.

### Peripheral Drivers

| Document | Content |
|------|------|
| [GPIO](./references/gpio.md) | GPIO initialization, per-pin configuration (0x188+n×4), output, input, interrupt |
| [UART](./references/uart.md) | UART configuration, send, receive, ioctl, DMA, auto-baudrate |
| [I2C](./references/i2c.md) | I2C master send/receive, memory address, DMA, slave mode |
| [I2C Slave](./references/i2c_slave.md) | I2C slave address configuration, TX/RX interrupt callback |
| [SPI](./references/spi.md) | SPI initialization, full-duplex, FIFO polling, chip select management |
| [DMA](./references/dma.md) | DMA channel allocation, 8 channels, LLI chain, UART/SPI handshake |
| [DMAC](./references/dmac.md) | DMA controller upper-layer API, multi-block transfer, ping-pong buffer |
| [Timer](./references/timer.md) | Hardware timer, PWM output, watchdog mode, FreeRTOS delay |
| [PWM](./references/pwm.md) | PWM channel, clock divider, 16-bit period/threshold, servo control |
| [ADC](./references/adc.md) | 12-bit SAR ADC, 8 channels, continuous sampling, DMA |
| [DAC](./references/dac.md) | AUDAC audio DAC, PWM/GPDAC output, stereo mixing, DMA |
| [Flash](./references/flash.md) | SF_CTRL, XIP direct read, encrypted partition, Flash ID |
| [Watchdog](./references/watchdog.md) | Watchdog timeout, reset generation, feeding timing |
| [WO](./references/wo.md) | Waveform output, WS2812 LED driver, WO UART bit-banging, dual-level signal |
| [RTC](./references/rtc.md) | HBN RTC, 40-bit counter, BCD time, alarm |
| [Efuse](./references/efuse.md) | Efuse programming control, MAC address read, boot mode |
| [RNG](./references/rng.md) | TRNG random number, 256-bit output, hardware self-test |
| [Touch](./references/touch.md) | Capacitive touch keys, 16 channels, scanning, frequency hopping |
| [I2S](./references/i2s.md) | I2S audio interface, master/slave mode, DMA, audio codec |
| [IR](./references/ir.md) | Infrared remote control, NEC/RC5 protocol, TX/RX, FIFO |
| [Camera](./references/camera.md) | DVP interface, MJPEG encode/decode, geometric transform |
| [SDIO](./references/sdio.md) | SDH/SDIO3 interface, ADMA2, Wi-Fi/SD card |
| [Display](./references/display.md) | DPI/DSI/DBI display interface, OSD layer, framebuffer |
| [ACOMP](./references/comp.md) | Analog comparator, 16 channels, threshold selection, hysteresis configuration |
| [AUADC](./references/auadc.md) | Audio ADC, PDM microphone, analog input, DMA recording |
| [CAN-FD](./references/canfd.md) | CAN 2.0B/CAN-FD, ISO/Bosch dual-mode, TTCAN |
| [DPI](./references/dpi.md) | Display parallel interface, RGB888, test pattern, YUV420 |
| [GMAC](./references/gmac.md) | Gigabit Ethernet MAC, TX/RX descriptor, MDIO |
| [EMAC](./references/emac.md) | Fast Ethernet EMAC, RMII interface, buffer descriptor |
| [KYS](./references/kys.md) | Matrix keyboard scan, key value read, FIFO interrupt |
| [MJPEG](./references/mjpeg.md) | MJPEG hardware codec, camera mode, quantization table |
| [MTimer](./references/mtimer.md) | 64-bit high-precision timer, microsecond/millisecond delay, architecture-adaptive |
| [SDH](./references/sdh.md) | SD Host controller, ADMA2, SD card/SDIO |
| [SPI PSRAM](./references/spi_psram.md) | SPI PSRAM external RAM, QPI mode, Burst Wrap |
| [AUDAC](./references/audac.md) | Audio DAC, sample rate 8K-48K, volume control, zero-cross detection |
| [bak](./references/bak.md) | Backup domain register, VBAT power, RTC/GPIO wake source |
| [DBG](./references/dbg.md) | SWD/JTAG debug interface, password mode, chip ID |

### System & Clock

| Document | Content |
|------|------|
| [Clock](./references/clock.md) | CPU frequency, PLL configuration, clock gating, peripheral clock source |
| [Reset](./references/reset.md) | Peripheral reset control, 36+ reset number mapping table |
| [IRQ](./references/irq.md) | ECLIC interrupt controller, register, enable/disable, priority |
| [PM](./references/pm.md) | Power management, deep sleep, hibernate, clock gating, Wi-Fi power consumption |
| [FreeRTOS](./references/freertos.md) | Tasks, queues, semaphores, mutexes, tick delay (no vTaskStartScheduler needed) |
| [CKS](./references/cks.md) | Clock security system, hardware checksum, tamper detection |
| [EF Ctrl](./references/ef_ctrl.md) | eFuse controller, common trim read/write, auto-load |
| [IPC](./references/ipc.md) | Inter-core communication, AP↔NP sync, 32-bit message channel |
| [L1C](./references/l1c.md) | L1 Cache, I-Cache/D-Cache, write policy, performance counters |
| [MultiCore Sync](./references/multi_core_sync.md) | Multi-core sync, Flash operation mutual exclusion, IPC Suspend/Resume |

### Security & Encryption

| Document | Content |
|------|------|
| [sec_sha](./references/sec_sha.md) | SHA-1/224/256/384/512 hardware acceleration, DMA linked mode |
| [sec_aes](./references/sec_aes.md) | AES ECB/CBC/CTR mode, hardware key, linked mode |
| [sec_dsa](./references/sec_dsa.md) | DSA digital signature, PKA hardware acceleration, CRT optimization |
| [sec_ecdsa](./references/sec_ecdsa.md) | ECDSA elliptic curve signature, ECDH key exchange, secp256r1/k1 |
| [sec_gmac](./references/sec_gmac.md) | Galois message authentication, GCM GHASH, DMA linked mode |
| [sec_pka](./references/sec_pka.md) | PKA public key accelerator, 4096-bit big number operations, Montgomery domain |
| [sec_trng](./references/sec_trng.md) | TRNG true random number, 256-bit entropy output, group access protection |
| [HMAC](./references/hmac.md) | HMAC-SHA256 software implementation (no dedicated hardware), register-level optimization |

### Network Protocol Stack

| Document | Content |
|------|------|
| [LwIP](./references/lwip.md) | TCP/IP stack, Socket API, UDP/TCP, netif |
| [MQTT](./references/mqtt.md) | MQTT client, QoS 0/1/2, LWT, keep-alive |
| [HTTP Client](./references/http.md) | HTTP/HTTPS client, GET/POST, Zephyr net/http, mbedtls integration |
| [HTTPD Server](./references/httpd.md) | HTTP server, CGI dynamic routing, SSI tag replacement, POST handling, lwIP built-in |
| [mbedtls](./references/mbedtls.md) | TLS 1.0-1.3, SSL context, certificate verification, mutual authentication |
| [AT](./references/at.md) | AT command framework, command registration, Wi-Fi/BLE/MQTT/HTTP AT |
| [netbus](./references/netbus.md) | Passthrough mode, UART-WiFi bridge, Socket client/server |
| [RTSP](./references/rtsp.md) | RTSP server, DESCRIBE/SETUP/PLAY, RTP over UDP |
| [NetHub](./references/nethub.md) | Streaming server, RTSP/HTTP-FLV/HLS, Wi-Fi packet filter distribution |
| [SRTP](./references/srtp.md) | SRTP secure real-time transport, AES-CM/GCM, ROC sync |
| [HTTPS](./references/https.md) | HTTPS Client, TLS 1.2/1.3, mbedtls integration |
| [iPerf](./references/iperf.md) | TCP/UDP throughput test, Wi-Fi performance verification |
| [SmartAudio](./references/smart_audio.md) | BL618 unified audio framework, local/Bluetooth music, prompts, volume management |
| [XAV](./references/xav.md) | Multimedia framework, player/codec/format/filter, MP3/AAC playback |
| [WebSocket](./references/websocket.md) | librws WebSocket client, async I/O, ws://wss:// |

### Wireless Communication (Wi-Fi)

| Document | Content |
|------|------|
| [wifi_mgmr](./references/wifi_mgmr.md) | Wi-Fi manager, STA/AP connection, scan, country code, auto-reconnect |
| [wpa_supplicant](./references/wpa_supplicant.md) | WPA2-Personal/Enterprise, WPA3, WPS-PBC/PIN, DPP, RRM/WNM |
| [net80211](./references/net80211.md) | Wi-Fi MLME layer, scan/auth/assoc, beacon monitoring, rx/tx frame handling |
| [coex](./references/coex.md) | Wi-Fi/BLE coexistence, priority configuration, activity notification |
| [Wi-Fi 6](./references/wifi6.md) | 802.11ax, MU-MIMO, OFDMA, BSS Color, TWT |
| [Wi-Fi 4](./references/wifi4.md) | 802.11n compatibility, MCS 0~15, Short GI, APSD power saving |
| [MACSW](./references/macsw.md) | MAC software layer, frame tx/rx control, encryption engine, firmware API |
| [wl80211](./references/wl80211.md) | wl80211 driver interface, cntrl commands, scan_ops, input_cb |

### Wireless Communication (BT & Thread)

| Document | Content |
|------|------|
| [BLE](./references/ble.md) | BLE controller, iBeacon, GATT service, notification/indication |
| [ble_mesh](./references/ble_mesh.md) | BLE Mesh provisioning, model message sending, node roles |
| [bt_a2dp](./references/bt_a2dp.md) | A2DP audio, SBC codec, AVRCP remote control, Stream management |
| [bt_hfp_spp](./references/bt_hfp_spp.md) | HFP hands-free, AT commands, SPP serial port, SDP service discovery, RFCOMM |
| [openthread](./references/openthread.md) | OpenThread protocol, IPv6, CoAP, UDP Socket, device roles |
| [bt_avrcp](./references/bt_avrcp.md) | BT AVRCP remote control, playback control, song info browsing, event notification |
| [bt_sdp](./references/bt_sdp.md) | BT SDP service discovery, Browse Group, Attribute query |
| [lmac154](./references/lmac154.md) | 802.15.4 MAC, Thread/Zigbee baseband, channels 11~26 |
| [Matter](./references/matter.md) | Matter smart home, DAC certificate chain, SPAKE2+ authentication, provisioning |

### Components & Middleware

| Document | Content |
|------|------|
| [lvgl](./references/lvgl.md) | LVGL v9 graphics library, object system, display/input driver, timers |
| [Shell](./references/shell.md) | Command-line interface, SHELL_CMD_EXPORT, built-in commands |
| [Filesystem](./references/filesystem.md) | FATFS/LittleFS filesystem, partition mount, read/write |
| [OTA](./references/ota.md) | HTTP/HTTPS OTA firmware upgrade, TCP OTA, rollback |
| [USB](./references/usb.md) | USB device/host, CDC ACM, MSC class driver |
| [mquickjs](./references/mquickjs.md) | QuickJS JavaScript engine, embedded JS script execution |
| [Utils](./references/utils.md) | cJSON, log system, log level, DBG_TAG |
| [AI](./references/ai.md) | DNN accelerator, image recognition, voice wake-up, gesture recognition |
| [MTD](./references/mtd.md) | Flash partition abstraction, XIP access, PSM persistent storage |
| [Thread](./references/thread.md) | 802.15.4 Thread network, IPv6 mesh, self-healing |
| [FOTA](./references/fota.md) | Firmware OTA upgrade, TCP/HTTPS, dual-partition rollback |

### Multimedia & Audio Codec

| Document | Content |
|------|------|
| [SmartAudio](./references/smart_audio.md) | Unified audio framework, local/Bluetooth music, prompts, volume management |
| [XAV](./references/xav.md) | Multimedia framework, player/codec/format/filter |
| [AAC](./references/aacdec.md) | AAC-LC/AAC+/eAAC+ decode, PVMP4AudioDecoder |
| [Opus](./references/opus.md) | Opus codec, VoIP/music, SILK+CELT, 6~510kbps |
| [Speex](./references/speex.md) | Speex voice codec, VoIP, NB/WB/UWB |
| [Vorbis](./references/vorbis.md) | Vorbis audio decode, OGG container, Xiph.Org |
| [AMR](./references/amr.md) | AMR-NB/WB voice decode, 3GPP standard, VoIP |
| [FVAD](./references/fvad.md) | Voice activity detection, WebRTC VAD, speech recognition frontend |
| [AudioCodec](./references/audio_codec.md) | Sound card driver SndBl616, AudioFlowctrlBridge, SBC→PCM |
| [FrogFS](./references/frogfs.md) | Lightweight read-only filesystem, LVGL resource storage, XIP |

---

## Development Tutorials

### Getting Started

| Tutorial | Link |
|-----|------|
| BL616 Overview | https://dev.bouffalolab.com/ |
| GPIO Usage | Refer to `examples/peripherals/gpio` |
| UART Data Transceiver | Refer to `examples/peripherals/uart` |
| DMA Data Transfer | Refer to `examples/peripherals/dma` |

### Advanced

| Tutorial | Link |
|-----|------|
| Wi-Fi Station Connection | Refer to `examples/wifi/wifi_station` |
| BLE Advertising | Refer to `examples/ble/ble_peripheral` |
| MQTT Connection | Refer to `examples/net/mqtt` |

---

## Chip Reference Manuals

| Document | Link |
|-----|------|
| BL616 Datasheet | https://dev.bouffalolab.com/media/doc/bl616/datasheet |
| BL618 Datasheet | https://dev.bouffalolab.com/media/doc/bl618/datasheet |
| BL616 Reference Manual | https://dev.bouffalolab.com/media/doc/bl616/reference_manual |
| Bouffalo SDK Documentation | https://dev.bouffalolab.com/ |

---

## FAQ (Frequently Asked Questions)

**Q: Compilation error "No such file or directory"**
```bash
# Check if SDK is fully cloned
ls bouffalo_sdk/components/
# If components directory is empty or sparse, re-clone
git submodule update --init --recursive
```

**Q: Flash failure**
- Check if BOOT pin is pulled low
- Check if serial driver is installed
- Check if serial port selection is correct
- Try lowering baudrate (e.g. 115200)

**Q: WiFi connection failure**
- Check if SSID and password are correct
- Check if router supports 2.4G band (BL616 Wi-Fi 6 may require router support)
- Check country code setting

**Q: BLE connection unstable**
- Check if antenna is properly connected
- Reduce obstacles and interference sources

---

## Appendix: BL616/BL618 vs BL602 Key Differences

| Item | BL602 | BL616/BL618 |
|------|-------|-------------|
| CPU Frequency | 40MHz | Up to 320MHz |
| Wi-Fi | 802.11b/g/n | 802.11a/b/g/n/ac/ax (Wi-Fi 6) |
| BLE | 5.0 | 5.0 + Mesh |
| GLB_BASE | 0x40000000 | **0x20000000** |
| UART0_BASE | 0x4000A000 | **0x2000A000** |
| GPIO Config | Shared register per 2 pins | **Per-pin independent register** |
| Peripheral Driver | HOSAL | **LHAL** |
| Toolchain | riscv64-unknown-elf-gcc | riscv64-unknown-elf-gcc |
