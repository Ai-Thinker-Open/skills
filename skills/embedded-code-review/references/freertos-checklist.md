# FreeRTOS 代码审查清单

针对 BL602/BL616/BL618 平台的 FreeRTOS 代码审查详细检查项。

## 1. 任务创建审查

### 1.1 调度器启动
| 检查项 | BL602 | BL616/BL618 | 说明 |
|--------|-------|-------------|------|
| `vTaskStartScheduler()` 调用 | 自动 | **必须显式调用** | BL616/BL618 不自动启动调度器 |
| 调用位置 | main() 末尾 | main() 末尾 | 调用后永不返回 |
| 调度器前延时 | 禁止 | **禁止** | `vTaskDelay` 依赖调度器运行 |

### 1.2 任务创建 API
```c
// 审查要点：
BaseType_t xTaskCreate(
    TaskFunction_t pvTaskCode,      // ✓ 函数指针有效
    const char * const pcName,      // ✓ 名称有意义，≤16字符
    configSTACK_DEPTH_TYPE usStackDepth, // ✓ 单位是 words (4 bytes)
    void * const pvParameters,      // ✓ 参数有效或 NULL
    UBaseType_t uxPriority,        // ✓ 优先级 0-6 (configMAX_PRIORITIES-1)
    TaskHandle_t * const pxCreatedTask // ✓ 句柄指针有效
);
```

### 1.3 栈大小配置
| 任务类型 | 推荐栈大小 (words) | 说明 |
|----------|-------------------|------|
| 空闲任务 | 128 (configMINIMAL_STACK_SIZE) | 系统保留 |
| 简单传感器任务 | 256-512 | 无复杂计算 |
| 网络任务 | 1024-2048 | 协议栈需要较大栈 |
| MQTT/HTTP 客户端 | 2048-4096 | 协议解析复杂 |
| OTA 升级任务 | 2048+ | 固件处理需要 |

**注意事项**：
- 栈大小单位是 **words**，不是 bytes
- 512 words = 2048 bytes
- 过小会导致栈溢出，过大浪费 RAM

### 1.4 任务优先级
```
优先级分配建议（configMAX_PRIORITIES=7）：

Priority 6: Timer task (系统保留，configTIMER_TASK_PRIORITY)
Priority 5: 紧急控制任务（电机控制、安全监控）
Priority 4: 关键业务任务（MQTT 通信、数据采集）
Priority 3: 普通业务任务（LED 控制、按键处理）
Priority 2: 后台任务（日志、统计）
Priority 1: 低优先级任务（OTA 下载、固件校验）
Priority 0: Idle task (系统保留)
```

---

## 2. 任务函数审查

### 2.1 函数结构
```c
// ✓ 正确的任务函数模板
void my_task(void *pvParameters)
{
    // 1. 初始化代码（如有）
    my_context_t *ctx = (my_context_t *)pvParameters;
    
    // 2. 主循环
    while (1) {
        // 2.1 业务逻辑
        process_data();
        
        // 2.2 让出 CPU（必须！）
        vTaskDelay(pdMS_TO_TICKS(100));
        // 或使用阻塞 API：
        // xQueueReceive(queue, &data, portMAX_DELAY);
        // xSemaphoreTake(semaphore, portMAX_DELAY);
        // ulTaskNotifyTake(pdTRUE, portMAX_DELAY);
    }
    
    // 3. 不应执行到这里（如果需要删除使用 vTaskDelete(NULL)）
}
```

### 2.2 常见错误
| 错误 | 问题 | 修正 |
|------|------|------|
| 无延时循环 | `while(1) { process(); }` | 添加 `vTaskDelay` 或使用阻塞 API |
| 使用 `HAL_Delay` | 依赖 HAL 层，非 RTOS 感知 | 改用 `vTaskDelay` |
| 使用 `usleep` | 可能阻塞整个系统 | 改用 `vTaskDelay` |
| 函数直接 return | 任务不会被删除，泄漏 | 使用 `vTaskDelete(NULL)` |
| 调度器前使用 vTaskDelay | BL616/BL618 上会崩溃 | 移到任务中使用 |

---

## 3. 同步机制审查

### 3.1 互斥锁 (Mutex)
```c
// ✓ 正确使用
SemaphoreHandle_t mutex = xSemaphoreCreateMutex();

void access_resource(void)
{
    if (xSemaphoreTake(mutex, pdMS_TO_TICKS(1000)) == pdTRUE) {
        // 临界区
        modify_shared_data();
        xSemaphoreGive(mutex);  // ✓ 必须释放
    } else {
        // 超时处理
        handle_timeout();
    }
}

// ✗ 错误使用 - 忘记释放
void bad_example(void)
{
    xSemaphoreTake(mutex, portMAX_DELAY);
    if (error_condition) {
        return;  // ✗ 忘记释放！
    }
    xSemaphoreGive(mutex);
}
```

### 3.2 递归互斥锁
```c
// 用于递归函数需要获取同一把锁
SemaphoreHandle_t recursive_mutex = xSemaphoreCreateRecursiveMutex();

void recursive_function(int depth)
{
    xSemaphoreTakeRecursive(recursive_mutex, pdMS_TO_TICKS(100));
    
    if (depth > 0) {
        recursive_function(depth - 1);  // 递归调用
    }
    
    xSemaphoreGiveRecursive(recursive_mutex);
}
```

### 3.3 信号量 (Semaphore)
```c
// 二值信号量 - 任务同步
SemaphoreHandle_t event_sem = xSemaphoreCreateBinary();

// 生产者（ISR 或任务）
void signal_event(void)
{
    xSemaphoreGive(event_sem);
}

// 消费者
void wait_event(void)
{
    if (xSemaphoreTake(event_sem, pdMS_TO_TICKS(1000)) == pdTRUE) {
        // 事件发生
    }
}

// 计数信号量 - 资源计数
SemaphoreHandle_t count_sem = xSemaphoreCreateCounting(5, 0);  // 最大5，初始0
```

### 3.4 信号量 vs 互斥锁选择
| 场景 | 使用 | 原因 |
|------|------|------|
| 保护共享资源 | Mutex | 支持优先级继承 |
| 任务间通知/同步 | Binary Semaphore | 轻量级 |
| 资源池管理 | Counting Semaphore | 支持多实例 |
| ISR 到任务通知 | Binary Semaphore 或 Task Notification | 性能更好 |

---

## 4. 队列使用审查

### 4.1 队列创建
```c
// ✓ 正确创建
QueueHandle_t queue = xQueueCreate(10, sizeof(uint32_t));
if (queue == NULL) {
    // 创建失败处理
}

// ✓ 结构体队列
typedef struct {
    uint8_t type;
    uint32_t value;
} message_t;

QueueHandle_t msg_queue = xQueueCreate(5, sizeof(message_t));
// 注意：队列存储的是结构体副本，不是指针
```

### 4.2 队列操作
```c
// 任务中发送
message_t msg = { .type = 1, .value = 42 };
if (xQueueSend(queue, &msg, pdMS_TO_TICKS(100)) != pdTRUE) {
    // 发送失败（队列满）
}

// ISR 中发送（必须使用 FromISR 版本）
BaseType_t xHigherPriorityTaskWoken = pdFALSE;
xQueueSendFromISR(queue, &msg, &xHigherPriorityTaskWoken);
portYIELD_FROM_ISR(xHigherPriorityTaskWoken);

// 任务中接收
message_t received;
if (xQueueReceive(queue, &received, pdMS_TO_TICKS(1000)) == pdTRUE) {
    // 接收成功
}
```

### 4.3 队列大小建议
| 场景 | 队列深度 | 说明 |
|------|----------|------|
| 简单命令队列 | 5-10 | 命令一般不会积压 |
| 数据缓冲队列 | 10-20 | 考虑生产消费速率差 |
| 事件通知队列 | 3-5 | 只需通知，数据量小 |
| ISR 到任务队列 | 5-10 | ISR 不能阻塞，需要足够深度 |

---

## 5. 软件定时器审查

### 5.1 定时器创建
```c
// ✓ 正确创建
TimerHandle_t timer = xTimerCreate(
    "my_timer",           // 名称（调试用）
    pdMS_TO_TICKS(1000),  // 周期（ticks）
    pdTRUE,               // 自动重载 (pdTRUE=周期性, pdFALSE=单次)
    (void *)0,            // 定时器 ID
    timer_callback        // 回调函数
);

if (timer != NULL) {
    xTimerStart(timer, 0);
}
```

### 5.2 定时器回调函数
```c
// ✓ 定时器回调函数运行在 Timer Daemon Task 中
void timer_callback(TimerHandle_t xTimer)
{
    // 1. 保持简短（运行在高优先级 daemon task 中）
    // 2. 不要使用阻塞 API（如 vTaskDelay, xQueueReceive with timeout）
    // 3. 可以使用：xQueueSend (non-blocking), xSemaphoreGive (non-blocking)
    // 4. 可以使用 FromISR 版本的 API
    
    uint32_t id = (uint32_t)pvTimerGetTimerID(xTimer);
    timer_expired_count[id]++;
}
```

### 5.3 定时器操作
```c
xTimerStart(timer, 0);                    // 启动
xTimerStop(timer, 0);                     // 停止
xTimerReset(timer, 0);                    // 重置（重新开始计时）
xTimerChangePeriod(timer, pdMS_TO_TICKS(500), 0);  // 修改周期
xTimerDelete(timer, 0);                   // 删除

// ISR 版本
xTimerStartFromISR(timer, &xHigherPriorityTaskWoken);
xTimerStopFromISR(timer, &xHigherPriorityTaskWoken);
```

---

## 6. 临界区审查

### 6.1 任务级临界区
```c
// ✓ 短临界区
taskENTER_CRITICAL();
// 关键操作（尽量短，影响中断响应）
modify_shared_variable();
taskEXIT_CRITICAL();

// ✓ 带返回值（ISR 中使用）
void ISR_Handler(void)
{
    uint32_t mask = taskENTER_CRITICAL_FROM_ISR();
    // ISR 关键操作
    taskEXIT_CRITICAL_FROM_ISR(mask);
}
```

### 6.2 临界区注意事项
| 检查项 | 说明 |
|--------|------|
| 临界区长度 | 尽量短，只保护必要的操作 |
| 嵌套 | 临界区可嵌套（计数器管理） |
| 中断延迟 | 临界区期间中断被屏蔽 |
| 禁止操作 | 临界区内禁止调用阻塞 API |
| 适用场景 | 简单变量保护；复杂场景用 Mutex |

---

## 7. 任务通知审查

### 7.1 任务通知使用
```c
// ✓ 任务通知比信号量更轻量
TaskHandle_t task_handle;

void notify_task(void *pvParameters)
{
    while (1) {
        // 等待通知（阻塞）
        ulTaskNotifyTake(pdTRUE, portMAX_DELAY);
        
        // 处理通知
        process_event();
    }
}

void send_notification(void)
{
    xTaskNotifyGive(task_handle);
}

// ISR 中发送通知
void ISR_Handler(void)
{
    BaseType_t xHigherPriorityTaskWoken = pdFALSE;
    vTaskNotifyGiveFromISR(task_handle, &xHigherPriorityTaskWoken);
    portYIELD_FROM_ISR(xHigherPriorityTaskWoken);
}
```

### 7.2 任务通知 vs 信号量
| 特性 | 任务通知 | 信号量 |
|------|----------|--------|
| RAM 开销 | 0 (使用 TCB 字段) | 需要句柄 |
| 性能 | 更快 | 稍慢 |
| 广播 | 不支持 | 支持（二值信号量） |
| 计数 | 需要显式管理 | 计数信号量自动管理 |
| 多任务通知 | 需要不同任务 | 需要不同信号量 |

---

## 8. 内存管理审查

### 8.1 内存分配
```c
// ✓ 使用 FreeRTOS 内存管理
void *ptr = pvPortMalloc(size);
if (ptr == NULL) {
    // 分配失败处理
}

// 使用完毕释放
vPortFree(ptr);
ptr = NULL;  // 防止野指针
```

### 8.2 内存池使用
```c
// ✓ 静态内存池（确定性，无碎片）
#define POOL_SIZE 10
typedef struct {
    uint8_t data[64];
} pool_item_t;

static pool_item_t pool[POOL_SIZE];
static bool pool_used[POOL_SIZE] = {false};

void *pool_alloc(void)
{
    for (int i = 0; i < POOL_SIZE; i++) {
        if (!pool_used[i]) {
            pool_used[i] = true;
            return &pool[i];
        }
    }
    return NULL;  // 池满
}

void pool_free(void *item)
{
    pool_item_t *p = (pool_item_t *)item;
    int index = p - pool;
    if (index >= 0 && index < POOL_SIZE) {
        pool_used[index] = false;
    }
}
```

### 8.3 内存监控
```c
// 获取堆剩余空间
size_t free_heap = xPortGetFreeHeapSize();
size_t min_ever = xPortGetMinimumEverFreeHeapSize();

// 获取任务栈使用情况
UBaseType_t high_water_mark = uxTaskGetStackHighWaterMark(task_handle);
// 返回值是最小剩余栈空间（words）
// 如果返回值很小（如 < 10），说明栈即将溢出
```

---

## 9. Hook 函数审查

### 9.1 必须实现的 Hook
```c
// ✓ 内存分配失败 Hook
void vApplicationMallocFailedHook(void)
{
    printf("ERROR: Malloc failed!\r\n");
    // 可以：记录日志、触发看门狗复位、进入安全模式
    while (1);  // 挂起，等待看门狗复位
}

// ✓ 栈溢出 Hook
void vApplicationStackOverflowHook(TaskHandle_t xTask, char *pcTaskName)
{
    printf("ERROR: Stack overflow in task: %s\r\n", pcTaskName);
    while (1);
}
```

### 9.2 可选 Hook
```c
// Tick Hook（每 tick 调用，保持极短）
void vApplicationTickHook(void)
{
    // 可以用于：看门狗喂狗、时间统计
}

// 空闲 Hook（空闲任务每次循环调用）
void vApplicationIdleHook(void)
{
    // 可以用于：低功耗处理、后台垃圾回收
}
```

---

## 10. 常见问题速查

### 10.1 问题：任务不执行
**检查项**：
1. 是否调用了 `vTaskStartScheduler()`（BL616/BL618）
2. 任务优先级是否高于其他任务
3. 任务函数是否有死循环
4. 栈大小是否足够

### 10.2 问题：系统卡死
**检查项**：
1. 是否有任务占用 CPU 不释放（无延时循环）
2. 是否有优先级反转
3. 互斥锁是否死锁
4. 栈是否溢出

### 10.3 问题：内存不足
**检查项**：
1. 是否有内存泄漏
2. 任务栈是否过大
3. 队列是否创建过多
4. 堆大小 `configTOTAL_HEAP_SIZE` 是否足够

### 10.4 问题：ISR 中行为异常
**检查项**：
1. 是否使用 FromISR 版本 API
2. 共享变量是否用 volatile 修饰
3. 是否在 ISR 中调用阻塞 API
4. ISR 执行时间是否过长

---

## 11. BL616/BL618 特有注意事项

### 11.1 调度器启动
```c
// ✓ BL616/BL618 正确启动流程
int main(void)
{
    // 1. 硬件初始化
    system_init();
    hosal_uart_init(&uart_stdio);
    
    // 2. 创建所有任务
    xTaskCreate(task1, "task1", 512, NULL, 3, NULL);
    xTaskCreate(task2, "task2", 1024, NULL, 4, NULL);
    
    // 3. 启动调度器（永不返回）
    vTaskStartScheduler();
    
    // 4. 不应执行到这里
    printf("ERROR: Scheduler returned!\r\n");
    while (1);
}
```

### 11.2 不要在调度器前调用
```c
// ✗ 错误
void main(void)
{
    vTaskDelay(pdMS_TO_TICKS(100));  // ✗ 调度器未启动
    
    xTaskCreate(my_task, ...);
    
    vTaskStartScheduler();
}

// ✓ 正确
void main(void)
{
    xTaskCreate(my_task, ...);
    
    vTaskStartScheduler();
    
    // 如果需要启动前延时，使用硬件定时器或轮询
}
```

---

## 12. 审查输出模板

```markdown
# FreeRTOS 代码审查清单结果

## 任务创建
- [x/✗] 调度器正确启动
- [x/✗] 任务栈大小合适
- [x/✗] 任务优先级合理
- [x/✗] 检查 xTaskCreate 返回值

## 任务函数
- [x/✗] 有延时/阻塞机制
- [x/✗] 无阻塞 API 调用
- [x/✗] 不使用 HAL_Delay

## 同步机制
- [x/✗] 互斥锁正确使用
- [x/✗] 信号量正确使用
- [x/✗] 所有路径都释放锁

## 中断处理
- [x/✗] 使用 FromISR 版本 API
- [x/✗] 共享变量用 volatile
- [x/✗] ISR 执行时间短

## 内存管理
- [x/✗] 内存分配有检查
- [x/✗] 无内存泄漏
- [x/✗] 实现 Hook 函数

## 问题列表
1. [严重/警告/信息] 问题描述
   - 位置：文件:行号
   - 修正：修正建议
```
