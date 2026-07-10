---
name: ai-thinker-c-coding-standard
description: 安信可（Ai-Thinker）嵌入式产品 C 语言编码规范。编写、修改、评审、重构任何嵌入式 C 代码，或生成 .c/.h 文件、加函数头注释、检查代码规范时使用，即使用户没明说"规范"。核心要求：头文件对外接口加 Doxygen 函数头、标识符统一前缀（axk/aiio/ai）、4 空格缩进、参数校验、规范的文件组织。
---

# Ai-Thinker 嵌入式 C 编码规范

写、改、评审嵌入式 C 代码时遵循。新代码与历史代码优化都适用。评审时逐项核对，对不符合处指出问题并给出修正代码，优先级：函数头 > 命名 > 安全 > 格式。

## 统一前缀

变量、宏、结构体等标识符使用统一前缀，可选 **`axk`、`aiio`、`ai`** 三者之一，**同一项目/模块内必须保持一致**，不得混用。下文用 `<pfx>` 表示所选前缀，对应大写记为 `<PFX>`（即 `AXK`/`AIIO`/`AI`）。函数命名按第 2 节的适配层/应用层规则（应用层函数不带前缀）。

## 1. 函数头（最高优先级）

详细函数头**只要求加在头文件 `.h` 中对外公开的接口声明上**，采用 Doxygen 风格、**英文注释**（描述首字母大写、英文句号结尾）。其余位置分级：`.c` 中的定义不重复完整注释，必要时一行简注；静态函数、未对外声明的中断函数也只需一行简注。

`.h` 对外接口固定模板：

```c
/** @brief 函数概述与作用（首字母大写，英文句号结尾）.
 *
 *  @param[in]   param1     Input parameter description.
 *  @param[out]  *param2    Output parameter description (note pointer in/out and nullability).
 *  @return      Return value description.
 *  @retval      AIIO_OK    Success.
 *  @retval      AIIO_ERROR Error.
 *  @note        Usage notes / preconditions. On modification, append modifier/date/change here.
 *  @see         Related function reference.
 */
返回值类型 函数名(参数列表);
```

要点：
- 仅 `@brief` 必填；无参数用 `void` 作入参；多返回码可用枚举类型描述，或多行 `@retval` 逐一说明。

示例（对外接口声明）：

```c
/** @brief Log uart initialization function.
 *
 *  @param[in]  uart        Configure serial port printing, including serial port ID, pin, and baud rate.
 *  @return     Return the operation status. When the return value is AIIO_OK, is successful.
 *  @retval     AIIO_OK     Init successful.
 *  @retval     AIIO_ERROR  Init error.
 *  @note       This function needs to be adapted according to different platforms.
 *  @see
 */
int32_t aiio_uart_log_init(aiio_uart_config_t uart);
```

`.c` 中的定义只需一行简注：`// Init uart, configure baud rate, etc.`。

## 2. 命名

- 函数名（按目录分层）：
  - **适配层（adt）**：`<pfx>_组件名_功能`，小写+下划线，如 `aiio_uart_send`；空参用 `void`
  - **应用层（application）**：`动词_名词`，**不加前缀**，如 `set_led_status`、`get_temp_value`
- 全局变量 `g_<pfx>_`、静态变量 `s_<pfx>_`、局部变量无前缀；避免单字母（循环 `i/j/k` 除外）
- 宏：`<PFX>_` 前缀，全大写+下划线，如 `AIIO_UART_BAUD_115200`
- 枚举/结构体：标签名小写+下划线、`<pfx>_` 前缀，如 `struct aiio_list_node`、`enum aiio_sock`；经 `typedef` 的类型以 `_t` 结尾，如 `aiio_list_t`、`aiio_sock_t`；仅声明不 typedef 时**不带** `_t`；枚举值/结构体成员全大写+下划线，如 `AIIO_SOCK_STG_CONNECTED`
- 标识符：不用汉语拼音、不用非通用缩写；宏名不能以下划线开头或结尾；互斥/相反含义的变量用反义词组命名（如 `min/max`、`begin/end`、`add/delete`）

## 3. 格式

- 4 空格缩进，禁止 Tab
- 一行一语句；`if/for/while` 即使一行也加 `{}`

## 4. 安全

- 所有输入参数做合法性校验（是否为空、范围是否合理）
- 嵌入式尽量避免 `malloc`/`free`；必须用则控制大小、及时释放；禁止野指针/空指针解引用
- 中断函数禁止耗时操作；与主程序共享变量须 `volatile` 修饰
- 含多表达式的宏每个参数和整体都加括号：`#define AIIO_ADD(a, b) ((a) + (b))`

## 5. 可维护性与文件组织

- 函数功能单一，避免超 200 行大函数（特殊场景除外）；重复代码封装为工具函数；避免直接写寄存器地址，优先用封装宏
- 函数参数过多时（一般超过 5 个）用结构体封装传参，避免冗长参数列表
- `.c`/`.h` 以 `<pfx>_` 前缀命名，与功能一致（如 `aiio_uart.c`）
- `.h` 加防重复包含宏 `#ifndef <PFX>_XXX_H` / `#define <PFX>_XXX_H` / `#endif`（宏名同文件名，全大写）
- 关键逻辑/复杂算法/异常处加行注释；禁止无意义注释；`.h` 开头加文件说明注释