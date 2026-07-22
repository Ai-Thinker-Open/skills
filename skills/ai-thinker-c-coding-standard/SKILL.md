---
name: ai-thinker-c-coding-standard
description: 安信可（Ai-Thinker）嵌入式产品 C 语言编码规范。编写、修改、评审、重构任何嵌入式 C 代码，或生成 .c/.h 文件、加函数头注释、检查代码规范时使用，即使用户没明说"规范"。核心要求：头文件对外接口加 Doxygen 函数头、标识符统一前缀 axk、4 空格缩进、参数校验、规范的文件组织。
---

# Ai-Thinker 嵌入式 C 编码规范

写、改、评审嵌入式 C 代码时遵循。新代码与历史代码优化都适用。评审时逐项核对，对不符合处指出问题并给出修正代码，优先级：函数头 > 命名 > 安全 > 格式。

## 统一前缀

变量、宏、结构体等标识符统一使用前缀 **`axk`**（大写 `AXK`），**同一项目/模块内必须保持一致**，不得混用。下文用 `<pfx>` 表示前缀 `axk`，对应大写记为 `<PFX>` 即 `AXK`。函数命名按第 2 节的适配层/应用层规则（应用层函数不带前缀）。

## 1. 函数头（最高优先级）

详细函数头**只要求加在头文件 `.h` 中对外公开的接口声明上**，采用 Doxygen 风格、**英文注释**（描述首字母大写、英文句号结尾）。其余位置分级：`.c` 中的定义不重复完整注释，**函数超过 30 行或逻辑不直观时**加一行简注；静态函数、未对外声明的中断函数同理。

`.h` 对外接口固定模板：

```c
/** @brief 函数概述与作用（首字母大写，英文句号结尾）.
 *
 *  @param[in]   param1     Input parameter description.
 *  @param[out]  *param2    Output parameter description (note pointer in/out and nullability).
 *  @return      Return value description.
 *  @retval      AXK_OK     Success.
 *  @retval      AXK_ERROR  Error.
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
 *  @return     Return the operation status. When the return value is AXK_OK, is successful.
 *  @retval     AXK_OK     Init successful.
 *  @retval     AXK_ERROR  Init error.
 *  @note       This function needs to be adapted according to different platforms.
 *  @see
 */
int32_t axk_uart_log_init(axk_uart_config_t uart);
```

`.c` 中的简注格式：`// 功能简述（英文，首字母大写，无句号）`，如 `// Init uart and configure baud rate.`。简注位于函数定义上方，不加 Doxygen 前缀。

## 2. 命名

- 函数名（按目录分层，目录映射见下方规则）：
  - **适配层（adt/）**：`<pfx>_组件名_功能`，小写+下划线，如 `axk_uart_send`；空参用 `void`
  - **应用层（application/）**：`动词_名词`，**不加前缀**，如 `set_led_status`、`get_temp_value`
  - **目录判定**：文件位于 `adt/`、`adapter/`、`driver/`、`hal/` 目录下 → 适配层；位于 `application/`、`app/`、`src/` 根目录 → 应用层；不在上述目录时，**被上层调用且与硬件相关 → 适配层，面向用户业务 → 应用层**
  - **返回值枚举**：无论哪一层，返回值枚举类型始终带 `AXK_` 前缀（如 `AXK_OK`、`AXK_ERROR`），与函数名是否带前缀无关
- 全局变量 `g_<pfx>_`、静态变量 `s_<pfx>_`、局部变量无前缀；避免单字母（循环 `i/j/k` 除外）
- 宏：`<PFX>_` 前缀，全大写+下划线，如 `AXK_UART_BAUD_115200`、`AXK_MUTEX_LOCK(m)`、`#ifdef AXK_DEBUG`
- 枚举/结构体：标签名小写+下划线、`<pfx>_` 前缀，如 `struct axk_list_node`、`enum axk_sock`；经 `typedef` 的类型以 `_t` 结尾，如 `axk_list_t`、`axk_sock_t`；仅声明不 typedef 时**不带** `_t`；枚举值/结构体成员全大写+下划线，如 `AXK_SOCK_STG_CONNECTED`
- 标识符：不用汉语拼音；缩写仅限嵌入式/计算机领域通用形式（如 `init`、`cfg`、`buf`、`len`、`cnt`、`idx`、`tmp`、`err`、`ret`、`dev`、`reg`、`irq`、`dma`、`adc`、`gpio`），其他缩写须展开全称；宏名不能以下划线开头或结尾；互斥/相反含义的变量用反义词组命名（如 `min/max`、`begin/end`、`add/delete`）

## 3. 格式

- 4 空格缩进，禁止 Tab
- 一行一语句；`if/for/while` 即使一行也加 `{}`

## 4. 安全

- 所有输入参数做合法性校验：指针参数检查非空；整型参数检查范围（通过宏或常量定义上下限）；数组参数检查长度不超界
- **禁止**在嵌入式代码中使用 `malloc`/`free`；必须动态分配时（如协议栈等不可避免场景），单次分配不超过 4KB，并在使用完毕后立即释放；禁止野指针/空指针解引用
- 中断函数内禁止：阻塞等待（如 `while` 轮询外设）、大块内存拷贝（超过 64 字节）、浮点运算；单次中断执行目标 < 50μs。与主程序共享变量须 `volatile` 修饰
- 含多表达式的宏每个参数和整体都加括号：`#define AXK_ADD(a, b) ((a) + (b))`

## 5. 可维护性与文件组织

- 函数功能单一，单个函数不超过 200 行（状态机解析、自动生成代码除外）；重复代码封装为工具函数；避免直接写寄存器地址，优先用封装宏
- 函数参数超过 5 个时，用结构体封装传参，避免冗长参数列表
- `.c`/`.h` 以 `<pfx>_` 前缀命名，与功能一致（如 `axk_uart.c`）
- `.h` 加防重复包含宏 `#ifndef <PFX>_XXX_H` / `#define <PFX>_XXX_H` / `#endif`（宏名同文件名，全大写）
- 以下位置加行注释：硬件寄存器操作、位域拼接/掩码运算、状态机跳转条件、中断保护/临界区、超时重试逻辑。禁止无意义注释（如 `// 增加 i`）；`.h` 开头加文件说明注释（模块功能、作者、日期）