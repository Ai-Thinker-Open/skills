---
name: coder-ai-wb2
description: Ai-Thinker Ai-WB2 series module development guide (BL602 chip) - Wi-Fi 4 + BLE 5.0 module, supporting GPIO, UART, DMA, Timer, PWM, ADC, I2C, SPI, WiFi, BLE and other peripheral programming, as well as MQTT, HTTP and other network protocol development.
---

# Ai-Thinker Ai-WB2 Series Development Guide (BL602)

## Programming Paradigm

> **Important**: Unless the user explicitly requests **register-level (bare metal) programming**, all code examples in this skill use the **HOSAL (Hardware Operating System Abstraction Layer) library** for development, with loop logic implemented via **FreeRTOS tasks**.

**Default Programming Method** (HOSAL + FreeRTOS):
- Peripheral initialization, configuration: call HOSAL API
- Business logic loops: placed in FreeRTOS tasks (`xTaskCreate`)
- Delays: `vTaskDelay` (not `HAL_Delay`)

**BL602 FreeRTOS Special Notes**:
- **Do NOT call `vTaskStartScheduler()`** - the system automatically starts the scheduler in `main()`
- `main()` executes initialization, then enters main loop (bare metal mode) or hands off to RTOS scheduler
- **If the main loop has no business logic, you MUST call `vTaskDelay` to yield the CPU**, otherwise tasks cannot switch and the system will appear to hang
- Correct approach: `while(1) { process business; vTaskDelay(pdMS_TO_TICKS(100)); }`

**Register-Level Programming** (when explicitly requested by the user):
- Directly manipulate `*(volatile uint32_t *)addr` to access peripheral registers
- All timing and configuration must be controlled manually

---

## Product Overview

**Ai-WB2** series is a Wi-Fi & BLE dual-mode module developed by Ai-Thinker Technology based on **BL602 chip** (Bouffalolab), supporting:
- Wi-Fi 802.11b/g/n, 20MHz bandwidth, up to 72.2 Mbps
- Bluetooth Low Energy 5.0 + Bluetooth Mesh
- 32-bit RISC CPU (276KB RAM)
- Multiple sleep modes, deep sleep current 12μA

### Selection Guide

| Model | Package | Flash | RAM | Antenna | Feature |
|-----|------|-------|-----|------|-----|
| Ai-WB2-01F | SMD | 2MB | 276KB | PCB On-board | Compatible with ESP8285 |
| Ai-WB2-01M | SMD | 2MB | 276KB | Stamp Hole | - |
| Ai-WB2-01S | SMD | 2MB | 276KB | IPEX | - |
| Ai-WB2-05W | SMD | 4MB | 276KB | PCB On-board | - |
| Ai-WB2-07S | SMD | 4MB | 276KB | IPEX | - |
| Ai-WB2-12F | SMD | 4MB | 276KB | PCB On-board | High cost-performance |
| Ai-WB2-12S | SMD | 4MB | 276KB | IPEX | - |
| Ai-WB2-13 | SMD | 4MB | 276KB | Ceramic antenna | - |
| Ai-WB2-13U | SMD | 4MB | 276KB | USB | With USB port |
| Ai-WB2-32S | SMD | 4MB | 276KB | IPEX | - |
| Ai-WB2-M1 | SMD | 2MB | 276KB | - | - |
| Ai-WB2-M1-I | SMD | 2MB | 276KB | IPEX | - |

**Selection table download**: https://aithinker-static.oss-cn-shenzhen.aliyuncs.com/docs/_media_old/ai-wb2_selection_table.xlsx

---

## Development Environment Setup (Required Reading)

> **Important Reminder**: Before writing any code, you must complete the environment setup. **Toolchain installation and SDK cloning are prerequisites for programming**, otherwise you cannot compile and flash firmware.

### Step 1: Determine Current Platform

```bash
# Windows MSYS2/MINGW environment
echo $MSYSTEM
# Output MINGW64 or MSYS indicates MSYS2 environment

# Linux / WSL / macOS
uname -s
# Output Linux indicates Linux/WSL, Darwin indicates macOS
```

### Step 2: Install Toolchain (by Platform)

#### Windows MSYS2 Environment

**Applicable Scenario**: Native Windows development, using MSYS2 for compilation toolchain.

**Step 1: Download and Install MSYS2**

1. Download MSYS2: https://www.msys2.org/
2. Run installer, select installation path (recommended `C:\msys64`)
3. After installation, **open "MSYS2 MINGW64" terminal** (do not use MSYS2 native terminal)

**Step 2: Install Compilation Toolchain**

Execute in MSYS2 MINGW64 terminal:

```bash
# Configure Alibaba Cloud mirror (domestic acceleration)
echo 'Server = https://mirrors.aliyun.com/msys2/$repo' > /etc/pacman.d/mirrorlist

# Update package database
pacman -Sy

# Install compilation toolchain (includes riscv64-unknown-elf-gcc)
pacman -S mingw-w64-x86_64-gcc mingw-w64-x86_64-gdb mingw-w64-x86_64-make

# Install Python3 (flashing tool needs it)
pacman -S python3 python3-pip

# Install PySerial (for serial flashing)
pip install pyserial
```

> **If Alibaba Cloud mirror fails**, try Tencent Cloud or Huawei Cloud mirror:
> ```bash
> echo 'Server = https://mirrors.cloud.tencent.com/msys2/$repo' > /etc/pacman.d/mirrorlist
> ```

**Verify Installation**:

```bash
riscv64-unknown-elf-gcc -v    # Should output version info
python3 --version             # Should output version number
pip show pyserial            # Should display pyserial info
```

> **If errors occur, cannot proceed**, must resolve toolchain issues first.

#### Linux (Ubuntu 20.04) Environment

**Applicable Scenario**: Native Ubuntu, Debian and other Linux environments.

```bash
# Update software sources
sudo apt update

# Install compilation toolchain
sudo apt install -y build-essential git python3 python3-pip python3-dev wget sed

# Install Python dependencies (flashing needs it)
pip3 install pyserial

# Add serial port permissions (optional, for real hardware)
sudo usermod -a -G dialout $USER
```

**Verify Installation**:

```bash
riscv64-unknown-elf-gcc -v    # Or gcc -v, BL602 SDK uses system gcc on Linux
python3 --version              # Should output version number
pip3 show pyserial            # Should display pyserial info
```

> **If errors occur, cannot proceed**, must resolve toolchain issues first.

#### macOS Environment

```bash
# Install using Homebrew
brew install gcc git python3

# Install PySerial
pip3 install pyserial
```

**Verify Installation**:

```bash
gcc -v
python3 --version
pip3 show pyserial
```

---

**Windows Alternative: Users with WSL2**

If WSL2 is already installed on Windows, you can skip MSYS2 and directly use WSL2 for development. WSL2 is essentially a Linux environment, please refer to the "Linux (Ubuntu 20.04) Environment" installation steps above.

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

After toolchain installation is complete, all platforms execute the same SDK acquisition steps:

```bash
# Choose an appropriate directory to store projects (e.g. ~/projects or D:\workspace)
git clone https://github.com/Ai-Thinker-Open/Ai-Thinker-WB2.git
cd Ai-Thinker-WB2

# Must execute: Initialize submodules (otherwise compilation will miss critical files)
git submodule update --init --recursive
```

> **For domestic users with unstable GitHub access**, you can use Gitee mirror:
> ```bash
> git clone https://gitee.com/aithinker_open/Ai-Thinker-WB2.git
> cd Ai-Thinker-WB2
> git submodule update --init --recursive
> ```

**Linux/WSL Extra Step**: Set toolchain permissions

```bash
cd toolchain/riscv/Linux/
bash chmod755.sh
```

### Step 4: Compilation Verification

> **Windows Users**: Must execute compilation in **MSYS2 MINGW64** terminal, **do not use CMD, PowerShell or regular MSYS2 terminal**.

```bash
cd applications/get-started/helloworld
make -j8
```

Successful compilation will generate firmware file in the `build/out/` directory.

After executing `make flash` (regardless of whether flashing succeeds), the merged firmware will be generated at:

```
Ai-Thinker-WB2/tools/flash_tool/chips/bl602/img_create_iot/whole_flash_data.bin
```

> This is the complete merged firmware for the current version, containing all partition data. When users need firmware, rename this file as required and deliver it.

### Step 5: Flash Verification

Refer to the "Firmware Flashing" section below. Successful flashing with serial output from the module indicates environment setup is complete.

---

## BL602 GPIO Register Programming

**Prerequisite**: Must have completed "Development Environment Setup" Steps 2 and 3 above.

**GPIO Base Address**:
- GLB_BASE = 0x40000000
- GPIO configuration register: GLB_BASE + 0x100 + (pin/2)*4
- GPIO output value: GLB_BASE + 0x188
- GPIO output enable: GLB_BASE + 0x190

**Every 2 GPIOs share one 32-bit register, bit field layout**:

Even pins (0,2,4...):
```
[0]     IE        (1=input, 0=output)
[1]     SMT
[3:2]   DRV
[4]     PU
[5]     PD
[11:8]  FUNC_SEL  (11=GPIO mode)
```

Odd pins (1,3,5...): High 16 bits same offset

**Configuration Steps**:
1. Clear IE bit (0=output mode)
2. Set FUNC_SEL=11 (GPIO mode)
3. Set OUTPUT_EN register corresponding bit=1

**CPU Frequency**: 40MHz (default, not 120MHz)

**Example Code**:
```c
#define GLB_BASE  0x40000000
#define GLB_REG(off) (*(volatile uint32_t *)(GLB_BASE + off))

static void gpio_set_output(uint8_t pin) {
    uint32_t reg_off = 0x100 + (pin/2)*4;
    uint32_t tmp = GLB_REG(reg_off);
    
    if (pin % 2 == 0) {
        tmp &= ~(1 << 0);           // Clear IE
        tmp &= ~(0xF << 8);         // Clear FUNC_SEL
        tmp |= (11 << 8);           // Set to GPIO mode
    } else {
        tmp &= ~(1 << 16);          // Clear IE
        tmp &= ~(0xF << 24);        // Clear FUNC_SEL
        tmp |= (11 << 24);          // Set to GPIO mode
    }
    GLB_REG(reg_off) = tmp;
    GLB_REG(0x190) |= (1 << pin);  // Enable output
}

static void gpio_write(uint8_t pin, uint8_t val) {
    if (val) GLB_REG(0x188) |= (1 << pin);
    else     GLB_REG(0x188) &= ~(1 << pin);
}
```

**Project Structure**: `applications/get-started/<project>/<project>/main.c`

---

## Firmware Flashing

### Flashing Tools

| Tool | Download | Description |
|-----|------|-----|
| BL602 Flash Download Tool | [Click to download](https://aithinker-static.oss-cn-shenzhen.aliyuncs.com/docs/_media_old/bl602_flash_download_tool.zip) | Official tool |
| Development board specific tool (with GUI) | [Click to download](https://aithinker-static.oss-cn-shenzhen.aliyuncs.com/docs/_media_old/v1.7.4-release.zip) | With graphical interface |

### Flashing Steps

**Step 1: List available serial ports for user selection**

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

Common serial chip mappings:
| Chip | Windows Port | Linux Device |
|------|-------------|-----------|
| CH340 | COM3/COM4 etc. | /dev/ttyUSB0 |
| CP2102 | COM5/COM6 etc. | /dev/ttyUSB0 |
| FTDI | COM10+ | /dev/ttyUSB0 |

**Step 2: Enter Flashing Mode**

Pull the module's **BOOT pin low**, then reset (re-power or pull RST low).

**Step 3: Flash**

```bash
# Use command line flashing (Linux/macOS/MSYS2)
# Replace /dev/ttyUSB0 with actual serial port name
make flash p=/dev/ttyUSB0 b=921600
```

After successful flashing, the firmware file `whole_flash_data.bin` will be generated at:
```
Ai-Thinker-WB2/tools/flash_tool/chips/bl602/img_create_iot/whole_flash_data.bin
```

**Detailed tutorial**: https://blog.csdn.net/Boantong_/article/details/125781602

---

## AT Command Development

### AT Firmware

| Firmware No. | Version | Description |
|-------|------|-----|
| 2939 | V4.18_P23.2.1 | Combo-AT middleware regular firmware |
| 2328 | V4.18_P23.1.0 | Combo-AT middleware |
| 1923 | V4.18_P1.4.4 | Combo-AT V2 |
| 2103 | V2.3.7 | AT firmware |

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

### AT Firmware Update Log

Document: `docs/zh/wifi/wb2/fw_server.md` (document path in this skill repository)

---

## Secondary Development - Peripheral Programming

> Complete API function signatures and type definitions can be found in the standalone documents under the `references/` directory.
> This chapter demonstrates peripheral initialization and operation flow through specific examples.

### GPIO

```c
#include "hal_gpio.h"

// Initialize GPIO
gpio_init_t gpio_init = {
    .port = GPIO_PORT_A,
    .pin = 0,
    .mode = GPIO_MODE_OUTPUT_PP,
    .pull = GPIO_PULLUP_PULLDOWN,
    .strength = GPIO_STRENGTH_MEDIUM,
};
gpio_init(&gpio_init);

// Write GPIO
gpio_set_pin(GPIO_PORT_A, 0, 1);  // Set high
gpio_set_pin(GPIO_PORT_A, 0, 0);  // Set low

// Read GPIO
uint8_t value = gpio_get_pin(GPIO_PORT_A, 0);

// Toggle
gpio_toggle_pin(GPIO_PORT_A, 0);
```

### UART

```c
#include "hal_uart.h"

uart_config_t uart_config = {
    .baud_rate = 115200,
    .data_bits = UART_DATA_BITS_8,
    .stop_bits = UART_STOP_BITS_1,
    .parity = UART_PARITY_NONE,
    .flow_control = UART_FLOW_CONTROL_NONE,
    .rx_buffer_size = 256,
    .tx_buffer_size = 256,
};

uart_init(UART_ID_0, &uart_config);

// Send data
uint8_t tx_data[] = "Hello\r\n";
uart_send(UART_ID_0, tx_data, sizeof(tx_data));

// Receive data (interrupt mode)
void uart0_irq_handler(void)
{
    uint8_t data;
    if (uart_receive(UART_ID_0, &data, 1) > 0) {
        // Process data
    }
}
```

### DMA

```c
#include "hal_dma.h"

dma_config_t dma_config = {
    .channel = DMA_CHANNEL_0,
    .src_addr = (uint32_t)src_buffer,
    .dst_addr = (uint32_t)dst_buffer,
    .transfer_mode = DMA_TRANSFER_MODE_MEM_TO_MEM,
    .data_width = DMA_DATA_WIDTH_8BIT,
    .block_size = 256,
};

dma_init(DMA_CHANNEL_0, &dma_config);
dma_start(DMA_CHANNEL_0);

// Wait for completion
while (!dma_transfer_done(DMA_CHANNEL_0));
```

### Timer

```c
#include "hal_timer.h"

timer_config_t timer_config = {
    .timer_id = TIMER_ID_0,
    .mode = TIMER_MODE_PERIODIC,
    .period = 1000,  // 1ms
    .callback = timer0_callback,
};

timer_init(&timer_config);
timer_start(TIMER_ID_0);

void timer0_callback(void)
{
    // Periodic processing
}
```

### PWM

```c
#include "hal_pwm.h"

pwm_config_t pwm_config = {
    .pwm_id = PWM_ID_0,
    .channel = 0,
    .frequency = 1000,  // 1kHz
    .duty_cycle = 50,  // 50%
    .pin = GPIO_PIN_0,
};

pwm_init(&pwm_config);
pwm_start(PWM_ID_0);

// Change duty cycle
pwm_set_duty_cycle(PWM_ID_0, 75);  // 75%
```

### ADC

```c
#include "hal_adc.h"

adc_config_t adc_config = {
    .adc_id = ADC_ID_0,
    .channel = ADC_CHANNEL_0,
    .resolution = ADC_RESOLUTION_12BIT,
    .sample_rate = ADC_SAMPLE_RATE_1MSPS,
};

adc_init(&adc_config);

uint16_t adc_value;
adc_read(ADC_ID_0, ADC_CHANNEL_0, &adc_value);
// adc_value range 0-4095 (12bit)
```

### I2C

```c
#include "hal_i2c.h"

i2c_config_t i2c_config = {
    .i2c_id = I2C_ID_0,
    .mode = I2C_MODE_MASTER,
    .speed = I2C_SPEED_400K,
    .scl_pin = GPIO_PIN_1,
    .sda_pin = GPIO_PIN_2,
};

i2c_init(&i2c_config);

// Write register
uint8_t write_data[2] = {reg_addr, value};
i2c_master_write(I2C_ID_0, device_addr, write_data, 2);

// Read register
uint8_t read_data[2];
i2c_master_read(I2C_ID_0, device_addr, read_data, 2);
```

### SPI

```c
#include "hal_spi.h"

spi_config_t spi_config = {
    .spi_id = SPI_ID_0,
    .mode = SPI_MODE_MASTER,
    .clock_freq = 1000000,  // 1MHz
    .clock_polarity = SPI_CPOL_0,
    .clock_phase = SPI_CPHA_0,
    .data_width = SPI_DATA_WIDTH_8BIT,
    .cs_pin = GPIO_PIN_10,
};

spi_init(&spi_config);

// Send and receive
uint8_t tx_data[] = {0x01, 0x02, 0x03};
uint8_t rx_data[3];
spi_master_transfer(SPI_ID_0, tx_data, rx_data, 3);
```

---

## FreeRTOS Task Development

### Task Creation Example

BL602 FreeRTOS applications typically complete peripheral initialization in `main()`, then create business tasks.

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

    // Create task (priority 5, stack 512 words)
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
    }

    // BL602 does NOT need to manually call vTaskStartScheduler()
    // The scheduler has already been started during system initialization
}
```

### Key Points

| Key Point | Description |
|-----|------|
| **Do NOT call `vTaskStartScheduler()`** | Scheduler is started automatically by the system, `app_main()` executes with scheduler already running |
| **Main loop must delay** | If bare metal main loop or idle task has no delay, system cannot schedule other tasks and appears to hang |
| **Use `vTaskDelay`** | Do not use non-RTOS delays like `HAL_Delay`, `usleep` |
| **`pdMS_TO_TICKS`** | Converts milliseconds to ticks, e.g. `pdMS_TO_TICKS(500)` = 500ms |
| **Stack depth unit** | FreeRTOS stack depth is measured in **words (4 bytes)**, 512 = 2048 bytes |

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

wifi_conf_t wifi_conf = {
    .country_code = "CN",
};

wifi_manager_init(&wifi_conf);

// Connect Wi-Fi
int ret = wifi_sta_connect("SSID", "PASSWORD");
if (ret == 0) {
    printf("WiFi connected\r\n");
    
    // Get IP
    wifi_sta_info_t info;
    wifi_sta_get_info(&info);
    printf("IP: %s\r\n", info.ipaddr);
}
```

### SoftAP Mode

```c
#include "wifi_mgmr.h"

// Create hotspot
wifi_softap_config_t ap_config = {
    .ssid = "Ai-WB2-Setup",
    .password = "12345678",
    .channel = 6,
    .authmode = WIFI_AUTH_WPA2_PSK,
};

int ret = wifi_softap_start(&ap_config);
if (ret == 0) {
    printf("AP started\r\n");
}
```

### MQTT

```c
#include "mqtt_client.h"

mqtt_client_config_t mqtt_config = {
    .broker_url = "mqtt://broker.emqx.io:1883",
    .client_id = "ai-wb2-client",
    .username = "user",
    .password = "pass",
    .publish_topic = "/aiwb2/pub",
    .subscribe_topic = "/aiwb2/sub",
};

mqtt_client_handle_t mqtt = mqtt_client_new(&mqtt_config);

// Subscribe callback
void mqtt_subscribe_callback(char *topic, uint8_t *data, uint32_t len)
{
    printf("Received on %s: %.*s\r\n", topic, len, data);
}

mqtt_client_subscribe(mqtt, "/aiwb2/sub", mqtt_subscribe_callback);

// Publish message
mqtt_client_publish(mqtt, "/aiwb2/pub", (uint8_t *)"Hello", 5, 0);
```

### HTTP

```c
#include "http_client.h"

http_client_config_t http_config = {
    .url = "http://httpbin.org/get",
    .method = HTTP_METHOD_GET,
};

http_client_handle_t http = http_client_new(&http_config);

int ret = http_client_perform(http);
if (ret == 0) {
    char *response = http_client_get_response_body(http);
    printf("Response: %s\r\n", response);
}

http_client_free(http);
```

---

## Secondary Development - BLE Programming

### BLE Advertising

```c
#include "ble_lib.h"

ble_gap_adv_params_t adv_params = {
    .adv_type = BLE_GAP_ADV_TYPE_IND,
    .adv_interval = 160,  // 100ms
    .own_addr_type = BLE_ADDR_TYPE_PUBLIC,
};

ble_adv_data_set_t adv_data = {
    .name = "Ai-WB2",
    .flags = BLE_GAP_ADV_FLAG_LE_GENERAL_DISC,
};

ble_stack_init();
ble_gap_adv_start(&adv_params, &adv_data);
```

### BLE Connection

```c
#include "ble_lib.h"

// BLE service and characteristic definition
ble_uuid_t service_uuid = BLE_UUID16_DECLARE(0xFFF0);
ble_uuid_t char_uuid = BLE_UUID16_DECLARE(0xFFF1);

ble_attr_db_t att_db[] = {
    {
        .uuid = service_uuid,
        .type = BLE_ATTR_TYPE_PRIMARY_SERVICE,
    },
    {
        .uuid = char_uuid,
        .type = BLE_ATTR_TYPE_CHARACTERISTIC,
        .properties = BLE_CHAR_PROP_READ | BLE_CHAR_PROP_WRITE | BLE_CHAR_PROP_NOTIFY,
    },
};

// Create service
ble_svc_gatt_init();
ble_svc_gatt_add_service(service_uuid, att_db, sizeof(att_db));
```

---

## API Reference

Detailed API documentation is stored independently in the `references/` directory, categorized by peripheral:

| Document | Content |
|------|------|
| [GPIO](./references/gpio.md) | GPIO initialization, output, input, interrupt |
| [UART](./references/uart.md) | UART configuration, send, receive, ioctl, DMA |
| [I2C](./references/i2c.md) | I2C master/slave send, receive, memory read/write |
| [SPI](./references/spi.md) | SPI initialization, send, receive, chip select |
| [DMA](./references/dma.md) | DMA channel allocation, start/stop, interrupt callback |
| [Timer](./references/timer.md) | Hardware timer initialization, start, stop |
| [PWM](./references/pwm.md) | PWM output, frequency/duty cycle dynamic adjustment |
| [WS2812](./references/ws2812.md) | RGB LED control, SPI/IR dual drive, HSV color space |
| [ADC](./references/adc.md) | ADC sampling, channel management, continuous sampling |
| [DAC](./references/dac.md) | DAC output, voltage setting, DMA mode |
| [Flash](./references/flash.md) | Flash partition read/write, erase |
| [Watchdog](./references/watchdog.md) | Watchdog initialization, feed dog |
| [RTC](./references/rtc.md) | RTC time set/read (DEC/BCD format) |
| [Efuse](./references/efuse.md) | Efuse one-time storage read/write, MAC address read |
| [RNG](./references/rng.md) | Random number generator initialization, data filling |
| [BL_MTD](./references/bl_mtd.md) | Flash partition management, PSM/FW/ROMFS read/write/erase |

### System Tools

| Document | Content |
|------|------|
| [Blog](./references/blog.md) | Log framework, component-level DEBUG/INFO/WARN/ERROR, Hex Dump |
| [CLI](./references/cli.md) | Command line interface, static/dynamic command registration, parameter parsing |
| [EasyFlash](./references/easyflash.md) | KV storage, ENV environment variables, log cyclic writing |
| [System Time](./references/bl_sys_time.md) | System Epoch time get/update, NTP sync callback |
| [Yloop](./references/yloop.md) | AliOS event loop, event filtering, delayed callback, os_task_v Yield |
| [Utils](./references/utils.md) | CRC32/MD5/SHA256/Hex/Base64 utility functions |
| [cJSON](./references/cjson.md) | JSON parse/build, array/object traversal |
| [FastLZ](./references/fastlz.md) | Lossless compression/decompression, Level 1/2 algorithm selection |

### Wireless Communication

| [Wi-Fi STA](./references/wifi-sta.md) | Wi-Fi STA connection, scan, IP configuration, low power |
| [Wi-Fi AP](./references/wifi-ap.md) | Wi-Fi AP hotspot, DHCP, terminal management |
| [LwIP Socket](./references/lwip.md) | TCP/UDP Socket, domain name resolution, select multiplexing |
| [HTTP Server](./references/httpd.md) | HTTPD CGI callback, SSI tag, URI route registration |
| [HTTP Client](./references/httpc.md) | HTTPC GET/POST request, HTTPS, response callback |
| [HTTPS](./references/https.md) | blTcpSslConnect/Send/Read encrypted TCP send/receive |
| [TLS/SSL](./references/tls-ssl.md) | mbedTLS certificate authentication, PSK, session recovery |
| [TCP Transport](./references/tcp-transport.md) | Transport layer abstraction, unified TCP/WS interface |
| [WebSocket](./references/websocket.md) | WS/WSS text/binary frames, Ping/Pong, path setting |
| [MQTT](./references/mqtt.md) | MQTT client, QoS 0/1/2, LWT, auto-reconnect |
| [DNS Server](./references/dns-server.md) | Local DNS hijacking, Captive Portal redirect |
| [BLE GAP/GATT](./references/ble-gap-gatt.md) | BLE advertising/scanning/connection, GATT service/notification/read/write |
| [BLE Mesh](./references/ble-mesh.md) | BLE Mesh provisioning, model message, switch/level control |
| [BLUFI](./references/blufi.md) | BLUFI BLE provisioning, event callback, Wi-Fi status reporting |
| [SmartConfig](./references/smartconfig.md) | SmartConfig/AirKiss one-click provisioning, sniffer mode |
| [SNTP](./references/sntp.md) | NTP time synchronization, multi-server polling, sync callback |
| [mDNS](./references/mdns.md) | Local service discovery, hostname registration, service announcement |
| [Ping](./references/ping.md) | ICMP Ping, connectivity detection, RTT statistics |
| [OTA](./references/ota.md) | HTTP/HTTPS OTA firmware upgrade, multi-chip header parsing, MD5 verification |
| [DHCP Server](./references/dhcp-server.md) | lwIP DHCPv4 server, automatic IP assignment |
| [Wi-Fi HOSAL](./references/wifi-hosal.md) | Wi-Fi RF/power abstraction layer, transmit power configuration |
| [Wi-Fi BT Coex](./references/wifi-bt-coex.md) | Wi-Fi/BT coexistence mode switching, timing coordination |
| [Power Management](./references/pm.md) | Power management, RF control, Wi-Fi low power, PSM |

---

## Peripheral Driver Porting

### SHT30 (Temperature and Humidity Sensor)

```c
#include "i2c_lib.h"

#define SHT30_ADDR 0x44

void sht30_init(void)
{
    uint8_t cmd[2] = {0x30, 0x93};  // High precision mode
    i2c_master_write(I2C_ID_0, SHT30_ADDR, cmd, 2);
    vTaskDelay(pdMS_TO_TICKS(20));
}

int sht30_read(float *temp, float *humidity)
{
    uint8_t data[6];
    uint8_t cmd[2] = {0x24, 0x00};  // Read command
    i2c_master_write(I2C_ID_0, SHT30_ADDR, cmd, 2);
    vTaskDelay(pdMS_TO_TICKS(15));
    i2c_master_read(I2C_URL, SHT30_ADDR, data, 6);
    
    // Parse data
    uint16_t temp_raw = (data[0] << 8) | data[1];
    uint16_t hum_raw = (data[3] << 8) | data[4];
    
    *temp = -45 + 175 * ((float)temp_raw / 65535);
    *humidity = 100 * ((float)hum_raw / 65535);
    
    return 0;
}
```

### WS2812B (RGB LED)

```c
#include "spi_lib.h"

#define WS2812_BITS 24  // 8bits per color

void ws2812_set_color(uint8_t r, uint8_t g, uint8_t b)
{
    uint8_t tx_data[WS2812_BITS];
    
    // GRB order
    for (int i = 0; i < 8; i++) {
        tx_data[i] = (g & (0x80 >> i)) ? 0x7E : 0x10;  // Green
        tx_data[i + 8] = (r & (0x80 >> i)) ? 0x7E : 0x10;  // Red
        tx_data[i + 16] = (b & (0x80 >> i)) ? 0x7E : 0x10;  // Blue
    }
    
    spi_master_transfer(SPI_ID_0, tx_data, NULL, WS2812_BITS);
}
```

---

## Development Tutorials

### Getting Started

| Tutorial | Link |
|-----|------|
| Ai-WB2 Overview | https://bbs.ai-thinker.com/forum.php?mod=viewthread&tid=45158 |
| GPIO Usage | https://bbs.ai-thinker.com/forum.php?mod=viewthread&tid=45174 |
| UART Data Transceiver | https://bbs.ai-thinker.com/forum.php?mod=viewthread&tid=45176 |
| DMA Data Transfer | https://bbs.ai-thinker.com/forum.php?mod=viewthread&tid=45184 |
| Timer Usage | https://bbs.ai-thinker.com/forum.php?mod=viewthread&tid=45185 |
| Watchdog Usage | https://bbs.ai-thinker.com/forum.php?mod=viewthread&tid=45189 |
| PWM Usage | https://bbs.ai-thinker.com/forum.php?mod=viewthread&tid=45208 |

#### RGB LED Demo (Pure Register Programming)

**Path**: `applications/get-started/rgb_demo/`

**GPIO Mapping** (Ai-WB2-12F-Kit):
| Color | GPIO | Note |
|------|------|------|
| Red | IO14 | |
| Green | IO17 | |
| Blue | IO3 | Main LED |

**Compilation**:
```bash
cd applications/get-started/rgb_demo && make
```

**Flashing**:
```bash
make flash p=/dev/ttyUSB0 b=921600
```

**Four blinking modes**:
1. **Breathing light** - Smooth brightness change, comfortable for eyes
2. **SOS signal** - Three short, three long, three short distress code
3. **Seven-color gradient** - Blue→Purple→Red→Cyan→Green→Blue
4. **Fast blink** - Short blink 5 times

**Mode switching**: Fade-in/fade-out transition, loop execution

---

#### BL602 GPIO Register Details (Verified)

**Important**: BL602 GPIO register layout differs from common MCUs, must use the following definitions:

```c
/* BL602 Register Addresses */
#define GLB_BASE                 0x40000000
#define GLB_GPIO_CFGCTL0        0x100   /* GPIO 0-1 configuration register */
#define GLB_GPIO_OUTPUT_OFFSET   0x188   /* GPIO output value register */
#define GLB_GPIO_OUTPUT_EN_OFFSET 0x190  /* GPIO output enable register */

#define GLB_REG(off)  (*(volatile uint32_t *)(GLB_BASE + (off)))
```

**GPIO Configuration Register (starting at 0x100) Bit Field Layout** (every 2 GPIOs share one 32-bit register):

| GPIO 0 (low 16 bits) | Position | GPIO 1 (high 16 bits) | Position |
|-------------------|------|-------------------|------|
| IE (input enable) | bit[0] | IE | bit[16] |
| SMT | bit[1] | SMT | bit[17] |
| DRV | bits[3:2] | DRV | bits[19:18] |
| PU | bit[4] | PU | bit[20] |
| PD | bit[5] | PD | bit[21] |
| **FUNC_SEL** | **bits[11:8]** | **FUNC_SEL** | **bits[27:24]** |

```c
/** GPIO configured as output mode - pure register operation (verified correct) */
static void gpio_set_output(uint8_t pin)
{
    uint32_t reg_off;
    uint32_t tmp;
    uint8_t func_sel_pos;
    uint8_t ie_pos;
    
    reg_off = GLB_GPIO_CFGCTL0 + (pin / 2) * 4;
    tmp = GLB_REG(reg_off);
    
    if (pin % 2 == 0) {
        /* Even pins (0, 2, 4...): FUNC_SEL at bits[11:8], IE at bit[0] */
        func_sel_pos = 8;
        ie_pos = 0;
    } else {
        /* Odd pins (1, 3, 5...): FUNC_SEL at bits[27:24], IE at bit[16] */
        func_sel_pos = 24;
        ie_pos = 16;
    }
    
    /* Clear IE bit (0=output mode) */
    tmp &= ~(1 << ie_pos);
    /* Set FUNC_SEL=11 (GPIO_FUN_GPIO) */
    tmp &= ~(0xF << func_sel_pos);
    tmp |= (11 << func_sel_pos);
    
    GLB_REG(reg_off) = tmp;
    
    /* Enable output: set corresponding bit to 1 in OUTPUT_EN register */
    GLB_REG(GLB_GPIO_OUTPUT_EN_OFFSET) |= (1 << pin);
}

/** GPIO output control */
static void gpio_write(uint8_t pin, uint8_t value)
{
    if (value)
        GLB_REG(GLB_GPIO_OUTPUT_OFFSET) |= (1 << pin);
    else
        GLB_REG(GLB_GPIO_OUTPUT_OFFSET) &= ~(1 << pin);
}
```

**Key Experience**:
1. **FUNC_SEL = 11** is GPIO mode
2. **Output enable is independent register** `0x190`, not part of configuration register
3. **Every 2 pins share configuration register**, indexed by `pin / 2`
4. **Even pins**: FUNC_SEL at bits[11:8], IE at bit[0]
5. **Odd pins**: FUNC_SEL at bits[27:24], IE at bit[16]
6. **CPU frequency 40MHz** (BL602 default), 1us ≈ 10 cycles

**Delay functions**:
```c
#define CPU_FREQ 40000000

static void delay_us(uint32_t us)
{
    volatile uint32_t count = us * (CPU_FREQ / 1000000 / 4);
    while (count--) { __asm__("nop"); }
}

static void delay_ms(uint32_t ms)
{
    delay_us(ms * 1000);
}
```

**Reference source**: `components/platform/soc/bl602/bl602_std/bl602_std/StdDriver/Src/bl602_glb.c` lines 1856-1935

### Intermediate

| Tutorial | Link |
|-----|------|
| ADC Analog-to-Digital Conversion | https://bbs.ai-thinker.com/forum.php?mod=viewthread&tid=45179 |
| DAC Digital-to-Analog Conversion | https://bbs.ai-thinker.com/forum.php?mod=viewthread&tid=45211 |
| RTC Real-Time Clock | https://bbs.ai-thinker.com/forum.php?mod=viewthread&tid=45214 |
| I2C Communication | https://bbs.ai-thinker.com/forum.php?mod=viewthread&tid=45215 |
| SPI Communication | https://bbs.ai-thinker.com/forum.php?mod=viewthread&tid=45212 |
| SPI with WS2812B | https://bbs.ai-thinker.com/forum.php?mod=viewthread&tid=45228 |

### Network

| Tutorial | Link |
|-----|------|
| TCP Wireless Communication | https://bbs.ai-thinker.com/forum.php?mod=viewthread&tid=45254 |
| UDP Wireless Communication | https://bbs.ai-thinker.com/forum.php?mod=viewthread&tid=45260 |
| MQTT Protocol Connection | https://bbs.ai-thinker.com/forum.php?mod=viewthread&tid=45256 |
| HTTP Weather Request | https://bbs.ai-thinker.com/forum.php?mod=viewthread&tid=45238 |
| BLE Bluetooth Communication | https://bbs.ai-thinker.com/forum.php?mod=viewthread&tid=45268 |

### Peripheral Porting

| Tutorial | Link |
|-----|------|
| BH1750 Light Sensor | https://bbs.ai-thinker.com/forum.php?mod=viewthread&tid=45213 |
| SHT30 Temperature and Humidity Sensor | https://bbs.ai-thinker.com/forum.php?mod=viewthread&tid=45241 |
| AHT20 Temperature and Humidity Sensor | https://bbs.ai-thinker.com/forum.php?mod=viewthread&tid=45242 |
| Modbus 485 RTU | https://bbs.ai-thinker.com/forum.php?mod=viewthread&tid=45244 |
| TM1637 NTP Clock | https://bbs.ai-thinker.com/forum.php?mod=viewthread&tid=45246 |
| Servo Control SG90 | https://bbs.ai-thinker.com/forum.php?mod=viewthread&tid=45247 |
| MPU6050 | https://bbs.ai-thinker.com/forum.php?mod=viewthread&tid=45302 |

---

## Common Resource Links

| Resource | Link |
|-----|------|
| SDK Source Code | https://github.com/Ai-Thinker-Open/Ai-Thinker-WB2 |
| AT Command Set (Chinese) | https://aithinker-static.oss-cn-shenzhen.aliyuncs.com/docs/_media_old/combo%E6%A8%A1%E7%BB%84%E9%80%9A%E7%94%A8%E6%8C%87%E4%BB%A4_v4.18p_3.8.0.pdf |
| AT Command Set (English) | https://aithinker-static.oss-cn-shenzhen.aliyuncs.com/docs/_media_old/Combo_AT_General_instructions_V4.18P_3.6.0_EN.pdf |
| Programming Guide | https://wb2-api-web.readthedocs.io/en/latest/docs/api-guides/index.html |
| Firmware Flashing Tool | https://aithinker-static.oss-cn-shenzhen.aliyuncs.com/docs/_media_old/bl602_flash_download_tool.zip |
| Static Memory Analysis | https://aithinker-static.oss-cn-shenzhen.aliyuncs.com/docs/_media_old/bouffalo_parse_tool-win32.zip |
| Debugging Tool | https://aithinker-static.oss-cn-shenzhen.aliyuncs.com/docs/_media_old/ComAssistant_2.0.2.9.zip |
| Aithings Platform Firmware | https://aithinker-static.oss-cn-shenzhen.aliyuncs.com/docs/media/WiFi/WB2/Firmware/wb2-aithings-illumination-v4.18_p0.0.1.zip |

---

## Chip Reference Manuals

| Document | Link |
|-----|------|
| BL602 Datasheet (Chinese) | https://dev.bouffalolab.com/media/doc/602/open/datasheet/zh/html/index.html |
| BL602 Datasheet (EN) | https://dev.bouffalolab.com/media/doc/602/open/datasheet/en/html/index.html |
| BL602 Reference Manual (Chinese) | https://dev.bouffalolab.com/media/doc/602/open/reference_manual/zh/html/index.html |
| BL602 Reference Manual (EN) | https://dev.bouffalolab.com/media/doc/602/open/reference_manual/en/html/index.html |

---

## FAQ (Frequently Asked Questions)

**Q: Compilation error "No such file or directory"**
```bash
# Re-initialize submodules
git submodule update --init --recursive
```

**Q: Flash failure**
- Check if BOOT pin is pulled low
- Check if serial driver is installed
- Check if serial port selection is correct

**Q: WiFi connection failure**
- Check if SSID and password are correct
- Check if router supports 2.4G band
- Check country code setting

**Q: BLE connection unstable**
- Check if antenna is properly connected
- Reduce obstacles and interference sources

**Full FAQ**: https://aithinker.readthedocs.io/zh-cn/latest/docs/software-framework/WiFi/index.html#id2
