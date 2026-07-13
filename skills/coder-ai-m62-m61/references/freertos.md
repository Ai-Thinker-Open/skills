# FreeRTOS on BL616/BL618

FreeRTOS Kernel V10.6.2 support for Bouffalo Lab BL616/BL618 chips. Based on RISC-V architecture with vendor-specific adaptations.

## Important BL616/BL618 Specific Notes

### Scheduler Startup
**Unlike BL602, BL616/BL618 REQUIRES explicit `vTaskStartScheduler()`.**

The scheduler is NOT auto-started. Tasks must be created BEFORE calling `vTaskStartScheduler()`, and this call never returns. **Do NOT** call `vTaskDelay` before the scheduler starts — it depends on the scheduler being active.

```c
void main(void)
{
    // 1. Hardware init first
    hosal_uart_init(&uart_stdio1);

    // 2. Create all tasks before starting scheduler
    xTaskCreate(proc_main_entry, "main_entry", 1024, NULL, 15, NULL);

    // 3. Start the scheduler — NEVER returns
    vTaskStartScheduler();

    // Code here will NOT execute
}
```

### Tick Configuration
From `FreeRTOSConfig.h`:
- `configCPU_CLOCK_HZ`: 1 MHz (1,000,000 Hz)
- `configTICK_RATE_HZ`: 1000 (1ms tick)
- `portTICK_PERIOD_MS`: 1 (1000 / 1000)

### Heap Configuration
- `configTOTAL_HEAP_SIZE`: 48 KB
- `configMINIMAL_STACK_SIZE`: 128 words

---

## Task Creation

### Dynamic Allocation (`xTaskCreate`)

```c
#include <FreeRTOS.h>
#include <task.h>

void my_task(void *pvParameters)
{
    while (1) {
        // Task logic
        vTaskDelay(pdMS_TO_TICKS(100));
    }
}

void create_my_task(void)
{
    TaskHandle_t handle = NULL;
    BaseType_t result;
    
    result = xTaskCreate(
        my_task,                    // Task function
        "my_task",                 // Task name (max 16 chars)
        512,                       // Stack depth (in words, not bytes)
        NULL,                      // Parameters passed to task
        3,                         // Priority (higher = more priority)
        &handle                    // Task handle
    );
    
    if (result == pdPASS) {
        // Task created successfully
    }
}
```

### Static Allocation (`xTaskCreateStatic`)

```c
#include <FreeRTOS.h>
#include <task.h>

StaticTask_t my_task_tcb;
StackType_t my_task_stack[512];

void my_task(void *pvParameters)
{
    while (1) {
        vTaskDelay(pdMS_TO_TICKS(100));
    }
}

void create_static_task(void)
{
    TaskHandle_t handle = xTaskCreateStatic(
        my_task,
        "static_task",
        512,
        NULL,
        3,
        my_task_stack,
        &my_task_tcb
    );
    
    if (handle != NULL) {
        // Task created successfully
    }
}
```

### Task Priority
- Idle task: priority 0 (`tskIDLE_PRIORITY`)
- Max priorities: 7 (`configMAX_PRIORITIES`)
- Timer task: `configMAX_PRIORITIES - 1`

---

## vTaskDelay

Delays the current task for a specified number of tick periods.

```c
#include <FreeRTOS.h>
#include <task.h>

void periodic_task(void *pvParameters)
{
    // Delay 500ms
    const TickType_t delay_500ms = pdMS_TO_TICKS(500);
    
    while (1) {
        // Do work
        vTaskDelay(delay_500ms);
    }
}

// pdMS_TO_TICKS converts milliseconds to tick periods
// For 1000Hz tick: pdMS_TO_TICKS(100) = 100 ticks
```

**Note**: `vTaskDelay()` specifies relative time. For fixed-frequency execution, use `xTaskDelayUntil()`.

---

## Queues

Queues allow task-to-task and interrupt-to-task communication.

### Creating a Queue

```c
#include <FreeRTOS.h>
#include <queue.h>

QueueHandle_t my_queue;

// Create queue holding 10 uint32_t values
my_queue = xQueueCreate(10, sizeof(uint32_t));

if (my_queue == NULL) {
    // Queue creation failed
}

// Create queue holding pointers to structures
typedef struct {
    uint8_t id;
    uint32_t value;
} Message_t;

QueueHandle_t msg_queue;
msg_queue = xQueueCreate(10, sizeof(Message_t*));
```

### Sending to Queue

```c
// From task (blocking)
uint32_t data = 42;
if (xQueueSend(my_queue, &data, pdMS_TO_TICKS(100)) == pdTRUE) {
    // Sent successfully
}

// From ISR (non-blocking, use FromISR version)
BaseType_t higher_priority_woken = pdFALSE;
xQueueSendFromISR(my_queue, &data, &higher_priority_woken);
portYIELD_FROM_ISR(higher_priority_woken);

// Send to front (urgent)
xQueueSendToFront(my_queue, &data, 0);
```

### Receiving from Queue

```c
uint32_t received_data;

if (xQueueReceive(my_queue, &received_data, pdMS_TO_TICKS(1000)) == pdTRUE) {
    // Data received: received_data
} else {
    // Timeout - no data available
}
```

### Complete Producer-Consumer Example

```c
#include <FreeRTOS.h>
#include <task.h>
#include <queue.h>

QueueHandle_t data_queue;

void producer(void *pvParameters)
{
    uint32_t counter = 0;
    while (1) {
        xQueueSend(data_queue, &counter, 0);
        counter++;
        vTaskDelay(pdMS_TO_TICKS(500));
    }
}

void consumer(void *pvParameters)
{
    uint32_t data;
    while (1) {
        if (xQueueReceive(data_queue, &data, pdMS_TO_TICKS(1000)) == pdTRUE) {
            printf("Received: %lu\r\n", data);
        }
    }
}

void queue_example_init(void)
{
    data_queue = xQueueCreate(10, sizeof(uint32_t));
    
    xTaskCreate(producer, "producer", 512, NULL, 2, NULL);
    xTaskCreate(consumer, "consumer", 512, NULL, 2, NULL);
}
```

---

## Semaphores

### Binary Semaphore

Used for task synchronization (signaling).

```c
#include <FreeRTOS.h>
#include <semphr.h>

SemaphoreHandle_t bin_sem;

void task_a(void *pvParameters)
{
    bin_sem = xSemaphoreCreateBinary();
    
    while (1) {
        // Wait for signal
        if (xSemaphoreTake(bin_sem, pdMS_TO_TICKS(1000)) == pdTRUE) {
            // Signal received - do work
        }
    }
}

void task_b(void *pvParameters)
{
    while (1) {
        // Do something
        
        // Give semaphore to signal task_a
        xSemaphoreGive(bin_sem);
        
        vTaskDelay(pdMS_TO_TICKS(2000));
    }
}
```

### Counting Semaphore

```c
SemaphoreHandle_t count_sem;

void counting_sem_example(void)
{
    // Create counting semaphore, max count 5, initial count 0
    count_sem = xSemaphoreCreateCounting(5, 0);
    
    // Take (decrement)
    xSemaphoreTake(count_sem, 0);
    
    // Give (increment)
    xSemaphoreGive(count_sem);
}
```

---

## Mutexes

Mutexes protect shared resources with priority inheritance to prevent priority inversion.

```c
#include <FreeRTOS.h>
#include <semphr.h>

SemaphoreHandle_t resource_mutex;

void resource_init(void)
{
    resource_mutex = xSemaphoreCreateMutex();
}

void access_shared_resource(void)
{
    if (xSemaphoreTake(resource_mutex, pdMS_TO_TICKS(1000)) == pdTRUE) {
        // Critical section - access shared resource
        
        xSemaphoreGive(resource_mutex);
    }
}
```

### Recursive Mutex

For recursive function calls needing the same mutex:

```c
SemaphoreHandle_t recursive_mutex;

void recursive_mutex_example(void)
{
    recursive_mutex = xSemaphoreCreateRecursiveMutex();
}

void recursive_function(int depth)
{
    xSemaphoreTakeRecursive(recursive_mutex, pdMS_TO_TICKS(100));
    
    if (depth > 0) {
        recursive_function(depth - 1);
    }
    
    xSemaphoreGiveRecursive(recursive_mutex);
}
```

---

## Software Timers

Timers run in a timer daemon task with callbacks.

### Timer Configuration (FreeRTOSConfig.h)
```c
#define configUSE_TIMERS            1
#define configTIMER_TASK_PRIORITY   (configMAX_PRIORITIES - 1)
#define configTIMER_QUEUE_LENGTH    4
#define configTIMER_TASK_STACK_DEPTH configMINIMAL_STACK_SIZE
```

### Creating a Timer

```c
#include <FreeRTOS.h>
#include <timers.h>

TimerHandle_t my_timer;

void timer_callback(TimerHandle_t xTimer)
{
    static uint32_t count = 0;
    count++;
    
    uint32_t id = (uint32_t)pvTimerGetTimerID(xTimer);
    printf("Timer %lu expired, count=%lu\r\n", id, count);
}

void timer_example(void)
{
    // One-shot timer: 1000ms, auto-reload=false
    my_timer = xTimerCreate(
        "my_timer",                // Name
        pdMS_TO_TICKS(1000),       // Period in ticks
        pdFALSE,                   // Auto-reload (pdTRUE = repeating)
        (void*)0,                  // Timer ID
        timer_callback             // Callback function
    );
    
    if (my_timer != NULL) {
        xTimerStart(my_timer, 0);
    }
}

void repeating_timer_example(void)
{
    // Auto-reload timer every 500ms
    TimerHandle_t auto_timer = xTimerCreate(
        "auto_timer",
        pdMS_TO_TICKS(500),
        pdTRUE,                    // Auto-reload
        (void*)1,
        timer_callback
    );
    
    if (auto_timer != NULL) {
        xTimerStart(auto_timer, 0);
    }
}
```

### Timer Control Functions

```c
// Start/Stop
xTimerStart(timer, 0);
xTimerStop(timer, 0);

// Reset (restart from now)
xTimerReset(timer, 0);

// Change period
xTimerChangePeriod(timer, pdMS_TO_TICKS(2000), 0);

// Delete
xTimerDelete(timer, 0);

// From ISR versions
xTimerStartFromISR(timer, &higher_priority_woken);
xTimerStopFromISR(timer, &higher_priority_woken);
```

---

## Critical Sections

### Task-Level Critical Sections

```c
// Enter critical section - disable interrupts
taskENTER_CRITICAL();

// Critical code - no context switch, no interrupts

taskEXIT_CRITICAL();
```

### ISR-Safe Critical Sections

```c
void vISR_Handler(void)
{
    uint32_t mask = taskENTER_CRITICAL_FROM_ISR();
    
    // ISR critical code
    
    taskEXIT_CRITICAL_FROM_ISR(mask);
}
```

**Warning**: Keep critical sections short to avoid affecting interrupt response time.

---

## Application Hooks

Implement these weak functions in `freertos_port.c` or your code:

### Malloc Failed Hook
```c
void vApplicationMallocFailedHook(void)
{
    printf("Memory allocation failed!\r\n");
    while (1); // Hang
}
```

### Stack Overflow Hook
```c
void vApplicationStackOverflowHook(TaskHandle_t xTask, char *pcTaskName)
{
    printf("Stack overflow in task: %s\r\n", pcTaskName);
    while (1);
}
```

### Tick Hook (called every tick interrupt)
```c
void vApplicationTickHook(void)
{
    // Called from tick ISR - keep very short
}
```

---

## Complete Application Template

```c
#include <FreeRTOS.h>
#include <task.h>
#include <queue.h>
#include <semphr.h>
#include <timers.h>
#include <stdio.h>
#include <hosal_uart.h>

HOSAL_UART_DEV_DECL(uart_stdio, 1, 4, 3, 2000000);

static QueueHandle_t data_queue;
static SemaphoreHandle_t mutex;

void producer_task(void *pvParameters)
{
    uint32_t counter = 0;
    while (1) {
        xQueueSend(data_queue, &counter, pdMS_TO_TICKS(100));
        counter++;
        vTaskDelay(pdMS_TO_TICKS(500));
    }
}

void consumer_task(void *pvParameters)
{
    uint32_t data;
    while (1) {
        if (xQueueReceive(data_queue, &data, pdMS_TO_TICKS(2000)) == pdTRUE) {
            xSemaphoreTake(mutex, portMAX_DELAY);
            printf("Got: %lu\r\n", data);
            xSemaphoreGive(mutex);
        }
    }
}

void main(void)
{
    hosal_uart_init(&uart_stdio);
    printf("FreeRTOS BL616/BL618 Demo\r\n");
    
    // Create IPC primitives
    data_queue = xQueueCreate(10, sizeof(uint32_t));
    mutex = xSemaphoreCreateMutex();
    
    // Create tasks
    xTaskCreate(producer_task, "producer", 512, NULL, 2, NULL);
    xTaskCreate(consumer_task, "consumer", 512, NULL, 2, NULL);

    // Must explicitly start the scheduler
    vTaskStartScheduler();
}
```

---

## Build Configuration

Key `FreeRTOSConfig.h` settings for BL616/BL618:

```c
#define configSUPPORT_STATIC_ALLOCATION  1
#define configUSE_PREEMPTION            1
#define configUSE_IDLE_HOOK             0
#define configUSE_TICK_HOOK             0
#define configCPU_CLOCK_HZ              1000000
#define configTICK_RATE_HZ              1000
#define configMAX_PRIORITIES            7
#define configMINIMAL_STACK_SIZE        128
#define configTOTAL_HEAP_SIZE           (48 * 1024)
#define configUSE_MUTEXES              1
#define configUSE_RECURSIVE_MUTEXES    1
#define configUSE_COUNTING_SEMAPHORES   1
#define configUSE_TIMERS                1
#define configTIMER_TASK_PRIORITY      (configMAX_PRIORITIES - 1)
#define configTIMER_QUEUE_LENGTH       4
#define configTIMER_TASK_STACK_DEPTH   configMINIMAL_STACK_SIZE

// Include necessary API functions
#define INCLUDE_vTaskDelay            1
#define INCLUDE_vTaskDelayUntil       1
#define INCLUDE_vTaskDelete          1
#define INCLUDE_vTaskSuspend         1
```

---

## Header Files

```c
#include <FreeRTOS.h>    // Main kernel header
#include <task.h>        // Task API
#include <queue.h>       // Queue API
#include <semphr.h>      // Semaphore/Mutex API
#include <timers.h>      // Timer API
#include <projdefs.h>    // pdPASS, pdFALSE, etc.
```

---

## API Reference Summary

| Function | Header | Description |
|----------|--------|-------------|
| `xTaskCreate` | task.h | Create dynamically allocated task |
| `xTaskCreateStatic` | task.h | Create statically allocated task |
| `vTaskDelay` | task.h | Delay task for tick count |
| `xTaskDelayUntil` | task.h | Delay until absolute time |
| `vTaskDelete` | task.h | Delete task |
| `vTaskSuspend` | task.h | Suspend task |
| `vTaskResume` | task.h | Resume task |
| `xQueueCreate` | queue.h | Create queue |
| `xQueueSend` | queue.h | Send to queue |
| `xQueueReceive` | queue.h | Receive from queue |
| `xSemaphoreCreateBinary` | semphr.h | Create binary semaphore |
| `xSemaphoreCreateMutex` | semphr.h | Create mutex |
| `xSemaphoreTake` | semphr.h | Take semaphore |
| `xSemaphoreGive` | semphr.h | Give semaphore |
| `xTimerCreate` | timers.h | Create software timer |
| `xTimerStart` | timers.h | Start timer |
| `xTimerStop` | timers.h | Stop timer |
| `xTimerReset` | timers.h | Reset timer |
