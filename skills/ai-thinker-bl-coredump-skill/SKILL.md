---
name: ai-thinker-bl-coredump-skill
description: >
  Ai-Thinker 博流系列模组 coredump 崩溃调试 skill。当用户提供 crash log、
  coredump 文件路径,或请求分析崩溃/coredump/gdb 调试时使用。自动完成日志解析、
  端口分配、GDB 服务器启动、GDB 连接全流程。
---

# Coredump 调试 Skill

## 适用场景

- 用户提供 crash log 文件、coredump 文件路径(串口 log 或 flash 读出的 `crash.bin`)
- 请求分析崩溃、coredump、gdb 调试
- 需要恢复崩溃任务调用栈、参数、内存现场

## 关键路径

- 解析脚本:`tools/byai/coredump.py`
- 分割脚本:`tools/byai/crash_capture.py`(多 coredump 时使用)
- GDB 辅助:`tools/bouffalo_sdk.gdb`(由 coredump.py 自动 `-x` 加载,含 `task_dump` 等命令)
- 工具链探测:`tools/byai/toolchain.py`(`get_tool('gdb')` 在 PATH 找 `riscv64-unknown-*-gdb` 或 `riscv64-zephyr-*-gdb`)
- 输出目录:`tools/byai/output/`

## 流程

### 1. 确认输入

- **coredump 文件**(必须):串口 log(含 `BFLB COREDUMP v0.0.1` 标记)或从 flash core 分区读出的 `crash.bin`(magic `BKCD`,BIN v1,见 crash demo README)
- **ELF 文件**(必须):通常在 `<example>/build/build_out/<name>_bl616.elf`
- 未提供 ELF 时用 `file_search` 在工程目录查找

### 2. 分割多 coredump(可选)

```bash
python3 tools/byai/crash_capture.py <log_file> -o tools/byai/output/
```

只有 1 个时跳过。多个时默认用最后一个(最新崩溃)。

### 3. 启动调试(一条命令)

```bash
python3 tools/byai/coredump.py <coredump> <elf> [-x <extra.init>]
```

自动完成:解析 coredump → 服务端预载 ELF PT_LOAD@LMA + coredump@VMA → 选空闲端口 → 启动 GDB RSP 服务器 → 启动 `get_tool('gdb')` 探测到的 `riscv64-unknown-*-gdb`/`riscv64-zephyr-*-gdb` → 执行 `file`/`target remote`;`bouffalo_sdk.gdb` 由 coredump.py 自动 `-x` 加载。`-x` 可在自动 init 之外再追加一份额外 init。

### 4. GDB 调试

> ⚠️ **`coredump.py` 的 `RiscvRegs` 默认全 0**,所以 `bt`、`info registers`、`p $pc/$sp` 都无效。
> **用仓库自带的 `task_dump`(已自动 source)恢复崩溃任务现场**,不要手写偏移。
>
> **调用栈怎么来的**:FreeRTOS 异常时把 `mepc/mstatus/x1~x31` 压在当前任务栈顶,`pxCurrentTCB->pxTopOfStack` 指向它 → `task_dump` 从这帧重建 `$pc/$sp/$ra/$fp` → `bt` 走 ELF 的 DWARF(`.debug_frame`/`.eh_frame`)逐帧展开,**不依赖 target memory 里的代码段**。

**快速分析(GDB 启动后粘贴)**:

```gdb
set pagination off
task_dump            # 恢复崩溃任务全部寄存器(自动判 FPU dirty/clean)+ bt
task_list_ready      # 列就绪任务(tcb/mstatus/FPU 状态/任务名)
task_list_wait       # 列阻塞/挂起任务
# WiFi/MAC 排查:
stailq_len macsw_txq[0]   # 数 BSD STAILQ 队列长度(如发送队列)
debug_wl80211             # 一键打印 macsw_txq[0] 长度
```

`task_dump` 做的事:读 `pxCurrentTCB`、按 `mstatus` FS 位[14:13] 判 FPU( dirty=0x3 → 下方再压 33 words FPU 上下文)、动态算 sp 偏移( clean=31 words / dirty=64 words)、恢复 x1~x31、`set $pc=$mepc-4`、`bt`。手写 `pxTopOfStack + 0x68` 之类的固定偏移对不上 c906 端口实际帧,别用。

**FreeRTOS RISC-V(c906 端口)上下文帧布局**(从 `pxTopOfStack` 起,每项 4 字节,与 `task_dump` 读取顺序一致):

| word offset | 字节 | 寄存器 |
|:---:|:---:|---|
| 0 | +0x00 | mepc(崩溃 PC) |
| 1 | +0x04 | mstatus |
| 2 | +0x08 | x1(ra) |
| 3~5 | +0x0c~0x14 | x5~x7(t0~t2) |
| 6~7 | +0x18~0x1c | x8~x9(s0/fp,s1) |
| 8~15 | +0x20~0x3c | x10~x17(a0~a7) |
| 16~25 | +0x40~0x64 | x18~x27(s2~s11) |
| 26~29 | +0x68~0x74 | x28~x31(t3~t6) |
| 30 | +0x78 | critical nesting count |
| 31 | +0x7c | 整型帧到此结束 → `task_dump` clean 把 sp 设到此处 |
| 32~ | +0x80~ | FPU 上下文(f0~f31 + fcsr,33 words),仅 FPU dirty 时存在 |

**栈溢出检查**:栈底应有 `0xa5a5a5a5` 填充。剩余空间 = `pxTopOfStack - pxStack`。

### 支持/不支持的操作

| 支持 | 不支持 |
|------|--------|
| `x`、`p` 读内存 | `bt`/`info registers`(寄存器全 0) |
| `task_dump` 后 `bt` | `step`/`next`/`stepi` |
| `disassemble`、`info symbol` | `continue`、`break` |
| 代码段已由服务端预载(无需 `restore`) | 任何运行时操作 |

## 常见错误

| 现象 | 原因/解法 |
|------|----------|
| `bt` 显示 `#0 0x00000000 in ?? ()` | 跑 `task_dump`(自动恢复寄存器并 bt) |
| `No COREDUMP sections found in log` | 检查 `BFLB COREDUMP v0.0.1` 标记,确认编码;`.bin` 输入需 magic `BKCD` |
| `riscv64-unknown/zephyr-*-gdb: not found` | `export PATH=$PATH:/path/to/riscv/bin`(需匹配 `riscv64-unknown-*-gdb` 或 `riscv64-zephyr-*-gdb`) |
| 内存读取返回 `E0A` | 代码段已由服务端预载;若仍 E0A 说明该地址不在 ELF/coredump 范围 |

## 调用栈展开优化

`bt` 遇到闭源 WiFi 库(RAM 动态代码,无 DWARF)会断链。两种编译期方案 + 一种片上回溯:

### 方案一:`-fno-omit-frame-pointer`(推荐开发阶段)

在 `cmake/compiler_flags.cmake` 添加:

```cmake
sdk_add_compile_options(-fno-omit-frame-pointer)
```

编译器用 `s0`(fp)维护帧链,GDB 通过 fp 链展开,不依赖 DWARF,`bt` 直接干净输出。
代价:代码 +1~3%,栈 +4B/帧。闭源库那层仍会断。

### 方案二:DWARF unwind(默认)

无需配置,用 ELF 的 `.debug_frame`/`.eh_frame`。对用户代码良好,闭源库会断。

**参数恢复**:`task_dump` 从保存帧恢复 `a0~a7`,崩溃点参数直接可读;深帧靠 DWARF CFI 回溯。默认 `-O2` 会优化掉部分参数(显示 `<optimized out>`),要看全参数设 `CONFIG_GCC_OPTIMISE_LEVEL=-O0`(或 `-Og`);别开 `-flto`(破坏 DWARF)。

**断链后手动扫描栈**:

```gdb
x/200x $sp
# 对每个落在 0x800xxxxx 的候选地址:
info symbol 0x800a548c
# 过滤:栈地址低→高(深→浅)、代码段范围、偏移合理
```

### 片上回溯(无需 coredump):`backtrace_tasks_all_isr`

SDK 自带片上 CFI 回溯,已取代手写 walk fp 链:`CONFIG_BACKTRACE=y` 时,`coredump_run()` dump 完内存后自动调 `backtrace_tasks_all_isr`(`components/debug/src/backtrace.c`),用 flash 里 `DWARFCFI` 紧凑表 + `unwind_6byte.c` 对**全部任务**逐个回溯,把调用栈地址打进度。不依赖方案一,崩溃当场就有结果,离线 `info symbol` 解名即可。前提:工程带 `DWARFCFI` 表(`get_cfi_table_base()` 找得到)。

### 对比

| 方案 | 无噪声 | 覆盖闭源库 | 开销 | 改动 |
|------|:----:|:----:|------|------|
| 一:fp | ✅ | ❌ | 代码 ~2% | 一行 cmake |
| 二:DWARF | ❌ | ❌ | 无 | 无 |
| 片上 backtrace | ✅ | ❌ | 紧凑 CFI 表 | `CONFIG_BACKTRACE=y` |

**推荐**:开发阶段用方案一(离线 GDB `bt` 更干净);片上回溯用 `CONFIG_BACKTRACE`(现成、覆盖全部任务);两者可共存。

## 完整示例

```bash
cd dump/
python3 ../tools/byai/coredump.py dev.log dev_project.elf
```

```gdb
(gdb) task_dump
$1 = "socket"
FPU is CLEAN (FS=0x0) - using offset +31 words
#0  wifi_recv_task () at wifi.c:234
#1  prvTaskExitError ()
```