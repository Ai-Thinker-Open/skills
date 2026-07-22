#!/bin/bash
# OTA 固件生成脚本（Linux/macOS）
# 纯参数驱动，无交互式输入
#
# 用法:
#   模式A（已有文件）: ./generate_ota.sh --mode A --input <固件文件> [--output <输出目录>]
#   模式B（重新生成）: ./generate_ota.sh --mode B [--project-root <目录>] [--version <版本>] [--prefix <前缀>] [--output <输出目录>] [--skip-build]
#
# 示例:
#   ./generate_ota.sh --mode A --input FW_OTA.bin
#   ./generate_ota.sh --mode B --version 3.4 --output ./out
#   ./generate_ota.sh --mode B --skip-build --input ./os/tools/flash_tool/chips/bl602/ota/FW_OTA.bin

set -e

# ========== 默认值 ==========
MODE=""
INPUT_FILE=""
TARGET_VERSION=""
PREFIX=""
OUTPUT_PATH="."
PROJECT_ROOT=""
SKIP_BUILD=false

# ========== 参数解析 ==========
while [[ $# -gt 0 ]]; do
    case $1 in
        --mode)
            MODE="$2"
            shift 2
            ;;
        --input|-f)
            INPUT_FILE="$2"
            shift 2
            ;;
        --version|-v)
            TARGET_VERSION="$2"
            shift 2
            ;;
        --prefix|-p)
            PREFIX="$2"
            shift 2
            ;;
        --output|-o)
            OUTPUT_PATH="$2"
            shift 2
            ;;
        --project-root)
            PROJECT_ROOT="$2"
            shift 2
            ;;
        --skip-build)
            SKIP_BUILD=true
            shift
            ;;
        *)
            echo "错误：未知参数 $1"
            echo "用法："
            echo "  模式A: $0 --mode A --input <固件文件> [--output <输出目录>]"
            echo "  模式B: $0 --mode B [--project-root <目录>] [--version <版本>] [--prefix <前缀>] [--output <输出目录>] [--skip-build]"
            exit 1
            ;;
    esac
done

# ========== 参数校验 ==========
if [ -z "$MODE" ]; then
    echo "错误：必须指定 --mode A 或 --mode B"
    exit 1
fi

if [ "$MODE" != "A" ] && [ "$MODE" != "B" ]; then
    echo "错误：--mode 只能是 A 或 B"
    exit 1
fi

# ========== 辅助函数 ==========

# 自动检测项目根目录（向上查找 xiaozhi_project_cfg.h）
detect_project_root() {
    if [ -n "$PROJECT_ROOT" ]; then
        if [ -f "$PROJECT_ROOT/xiaozhi_project_cfg.h" ]; then
            return 0
        fi
        # 可能传入的是 cfg 所在目录的上级
        local candidate
        candidate=$(find "$PROJECT_ROOT" -name "xiaozhi_project_cfg.h" -exec dirname {} \; 2>/dev/null | head -1)
        if [ -n "$candidate" ]; then
            PROJECT_ROOT=$(dirname "$candidate")
            return 0
        fi
        echo "错误：在 $PROJECT_ROOT 下找不到 xiaozhi_project_cfg.h"
        exit 1
    fi

    # 从当前目录向上查找
    local dir="$(pwd)"
    while [ "$dir" != "/" ]; do
        if [ -f "$dir/xiaozhi_project_cfg.h" ]; then
            PROJECT_ROOT="$dir"
            return 0
        fi
        # 检查子目录
        local found
        found=$(find "$dir" -maxdepth 3 -name "xiaozhi_project_cfg.h" -exec dirname {} \; 2>/dev/null | head -1)
        if [ -n "$found" ]; then
            PROJECT_ROOT=$(dirname "$found")
            return 0
        fi
        dir=$(dirname "$dir")
    done

    echo "错误：无法自动检测项目根目录，请使用 --project-root 指定"
    exit 1
}

# 读取项目配置
read_config() {
    local cfg_file="$PROJECT_ROOT/xiaozhi_project_cfg.h"

    # 读取当前版本号
    CURRENT_VERSION=$(grep -o 'FW_VERSION\s*"[^"]*"' "$cfg_file" 2>/dev/null | head -1 | grep -o '"[^"]*"' | tr -d '"')
    if [ -z "$CURRENT_VERSION" ]; then
        echo "错误：无法从 $cfg_file 读取 FW_VERSION"
        exit 1
    fi

    # 检测语言版本和产品密钥
    if grep -q "ASR_LANGUAGE_ENGISH" "$cfg_file" 2>/dev/null; then
        DEFAULT_PREFIX=$(grep -A2 "ASR_LANGUAGE_ENGISH" "$cfg_file" | grep "OTA_PRODUCT_KEY" | head -1 | grep -o '"[^"]*"' | tr -d '"')
        LANG_SUFFIX="En"
    else
        DEFAULT_PREFIX=$(grep "OTA_PRODUCT_KEY" "$cfg_file" | grep -v "En" | head -1 | grep -o '"[^"]*"' | tr -d '"')
        LANG_SUFFIX="zh"
    fi

    if [ -z "$DEFAULT_PREFIX" ]; then
        echo "错误：无法从 $cfg_file 读取 OTA_PRODUCT_KEY"
        exit 1
    fi
}

# 添加 ai_pack_head（MD5 包头）
add_ai_pack_head() {
    local input="$1"
    local output="$2"

    if [ ! -f "$input" ]; then
        echo "错误：输入文件不存在: $input"
        exit 1
    fi

    # 检查文件时间（5 分钟内）
    local file_time current_time diff
    if stat -c %Y "$input" >/dev/null 2>&1; then
        file_time=$(stat -c %Y "$input")
    else
        file_time=$(stat -f %m "$input")
    fi
    current_time=$(date +%s)
    diff=$((current_time - file_time))
    if [ "$diff" -gt 300 ]; then
        echo "警告：文件可能不是新生成的（${diff}秒前）"
    fi

    # 计算 MD5
    local ota_body_md5
    if md5sum "$input" >/dev/null 2>&1; then
        ota_body_md5=$(md5sum "$input" | cut -d" " -f1 | tr 'a-f' 'A-F')
    else
        ota_body_md5=$(md5 -q "$input" | tr 'a-f' 'A-F')
    fi
    echo "固件 MD5: $ota_body_md5"

    # 构造 169 字节包头
    local ota_head
    ota_head=$(mktemp /tmp/ota_head_XXXXXX)
    printf 'V1.0\x00UNKN' > "$ota_head"
    printf '%s' "$ota_body_md5" >> "$ota_head"
    dd if=/dev/zero bs=1 count=128 >> "$ota_head" 2>/dev/null

    # 合并
    mkdir -p "$(dirname "$output")"
    cat "$ota_head" "$input" > "$output"
    rm -f "$ota_head"

    echo "已生成: $output"
}

# ========== 模式 A ==========
if [ "$MODE" = "A" ]; then
    echo "=== 模式A：添加 MD5 包头 ==="

    if [ -z "$INPUT_FILE" ]; then
        echo "错误：模式A 需要 --input 参数指定固件文件"
        exit 1
    fi

    if [ ! -f "$INPUT_FILE" ]; then
        echo "错误：固件文件不存在: $INPUT_FILE"
        exit 1
    fi

    # 输出文件名：原文件名 + _md5 后缀
    local_basename=$(basename "$INPUT_FILE")
    output_filename="${local_basename%.*}_md5.bin"

    add_ai_pack_head "$INPUT_FILE" "$OUTPUT_PATH/$output_filename"

    echo ""
    echo "=== 完成 ==="
    ls -la "$OUTPUT_PATH/$output_filename"

# ========== 模式 B ==========
elif [ "$MODE" = "B" ]; then
    echo "=== 模式B：生成 OTA 固件 ==="

    # 检测项目根目录
    detect_project_root

    # 读取配置
    read_config

    echo "项目目录: $PROJECT_ROOT"
    echo "当前版本: $CURRENT_VERSION"
    echo "默认前缀: $DEFAULT_PREFIX"
    echo "语言: $LANG_SUFFIX"

    # 使用用户指定的前缀，否则用默认值
    if [ -z "$PREFIX" ]; then
        PREFIX="$DEFAULT_PREFIX"
    fi

    # 使用用户指定的版本，否则用当前版本
    if [ -z "$TARGET_VERSION" ]; then
        TARGET_VERSION="$CURRENT_VERSION"
    fi

    echo "目标版本: $TARGET_VERSION"
    echo "文件名前缀: $PREFIX"

    FW_VERSION="$CURRENT_VERSION"

    if [ "$SKIP_BUILD" = false ]; then
        # 修改版本号（如果需要）
        if [ "$TARGET_VERSION" != "$CURRENT_VERSION" ]; then
            cfg_file="$PROJECT_ROOT/xiaozhi_project_cfg.h"
            sed -i "s/#define FW_VERSION \".*\"/#define FW_VERSION \"$TARGET_VERSION\"/" "$cfg_file"
            FW_VERSION="$TARGET_VERSION"
            echo "版本号已修改为: $FW_VERSION"
        fi

        # 编译
        echo ""
        echo "--- 执行 make flash ---"
        (cd "$PROJECT_ROOT" && make flash)

        fw_ota="$PROJECT_ROOT/os/tools/flash_tool/chips/bl602/ota/FW_OTA.bin"
        if [ ! -f "$fw_ota" ]; then
            echo "错误：FW_OTA.bin 未生成"
            # 恢复版本号
            if [ "$CURRENT_VERSION" != "$FW_VERSION" ]; then
                sed -i "s/#define FW_VERSION \".*\"/#define FW_VERSION \"$CURRENT_VERSION\"/" "$cfg_file"
            fi
            exit 1
        fi

        INPUT_FILE="$fw_ota"
    else
        # skip-build 模式：需要 --input 指定 FW_OTA.bin
        if [ -z "$INPUT_FILE" ]; then
            # 尝试默认路径
            INPUT_FILE="$PROJECT_ROOT/os/tools/flash_tool/chips/bl602/ota/FW_OTA.bin"
        fi
        if [ ! -f "$INPUT_FILE" ]; then
            echo "错误：FW_OTA.bin 不存在: $INPUT_FILE"
            echo "请使用 --input 指定路径，或先执行编译"
            exit 1
        fi
    fi

    # 添加 MD5 包头
    OTA_FILENAME="${PREFIX}_${FW_VERSION}_${LANG_SUFFIX}_ota.bin"
    add_ai_pack_head "$INPUT_FILE" "$OUTPUT_PATH/$OTA_FILENAME"

    # 恢复版本号
    if [ "$CURRENT_VERSION" != "$FW_VERSION" ]; then
        echo ""
        echo "--- 恢复版本号 ---"
        cfg_file="$PROJECT_ROOT/xiaozhi_project_cfg.h"
        sed -i "s/#define FW_VERSION \".*\"/#define FW_VERSION \"$CURRENT_VERSION\"/" "$cfg_file"
        echo "版本号已恢复为: $CURRENT_VERSION"
    fi

    echo ""
    echo "=== 完成 ==="
    ls -la "$OUTPUT_PATH/$OTA_FILENAME"
fi
