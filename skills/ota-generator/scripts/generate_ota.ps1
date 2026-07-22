# OTA 固件生成脚本（Windows PowerShell）
# 纯参数驱动，无交互式输入
#
# 用法:
#   模式A（已有文件）: .\generate_ota.ps1 -Mode A -Input <固件文件> [-Output <输出目录>]
#   模式B（重新生成）: .\generate_ota.ps1 -Mode B [-ProjectRoot <目录>] [-Version <版本>] [-Prefix <前缀>] [-Output <输出目录>] [-SkipBuild]
#
# 示例:
#   .\generate_ota.ps1 -Mode A -Input FW_OTA.bin
#   .\generate_ota.ps1 -Mode B -Version 3.4 -Output .\out
#   .\generate_ota.ps1 -Mode B -SkipBuild -Input .\os\tools\flash_tool\chips\bl602\ota\FW_OTA.bin

param(
    [Parameter(Mandatory=$true)]
    [ValidateSet("A", "B")]
    [string]$Mode,

    [string]$Input = "",
    [string]$Version = "",
    [string]$Prefix = "",
    [string]$Output = ".",
    [string]$ProjectRoot = "",
    [switch]$SkipBuild
)

$ErrorActionPreference = "Stop"

# ========== 辅助函数 ==========

function Find-ProjectRoot {
    param([string]$StartDir)

    if ($StartDir -and (Test-Path "$StartDir\xiaozhi_project_cfg.h")) {
        return $StartDir
    }

    # 向上查找
    $dir = $StartDir
    if (-not $dir) { $dir = Get-Location }

    while ($dir -and $dir -ne [System.IO.Path]::GetPathRoot($dir)) {
        if (Test-Path "$dir\xiaozhi_project_cfg.h") {
            return $dir
        }
        # 检查子目录（最深3层）
        $found = Get-ChildItem -Path $dir -Recurse -Depth 3 -Filter "xiaozhi_project_cfg.h" -ErrorAction SilentlyContinue | Select-Object -First 1
        if ($found) {
            return $found.DirectoryName
        }
        $dir = Split-Path $dir -Parent
    }

    Write-Error "无法自动检测项目根目录，请使用 -ProjectRoot 指定"
    exit 1
}

function Read-ProjectConfig {
    param([string]$ProjectRoot)

    $cfgFile = "$ProjectRoot\xiaozhi_project_cfg.h"
    if (-not (Test-Path $cfgFile)) {
        Write-Error "配置文件不存在: $cfgFile"
        exit 1
    }

    $content = Get-Content $cfgFile -Raw

    # 读取版本号
    $versionMatch = [regex]::Match($content, 'FW_VERSION\s+"([^"]+)"')
    if (-not $versionMatch.Success) {
        Write-Error "无法读取 FW_VERSION"
        exit 1
    }
    $script:CurrentVersion = $versionMatch.Groups[1].Value

    # 检测语言
    if ($content -match 'ASR_LANGUAGE_ENGISH') {
        $keyMatch = [regex]::Match($content, '(?s)ASR_LANGUAGE_ENGISH.*?OTA_PRODUCT_KEY\s+"([^"]+)"')
        $script:LangSuffix = "En"
    } else {
        # 找不带 En 的 OTA_PRODUCT_KEY
        $lines = $content -split "`n"
        $keyMatch = $null
        foreach ($line in $lines) {
            if ($line -match 'OTA_PRODUCT_KEY\s+"([^"]+)"' -and $line -notmatch 'En') {
                $keyMatch = [regex]::Match($line, 'OTA_PRODUCT_KEY\s+"([^"]+)"')
                break
            }
        }
        $script:LangSuffix = "zh"
    }

    if (-not $keyMatch -or -not $keyMatch.Success) {
        Write-Error "无法读取 OTA_PRODUCT_KEY"
        exit 1
    }
    $script:DefaultPrefix = $keyMatch.Groups[1].Value
}

function Add-AiPackHead {
    param(
        [string]$InputFile,
        [string]$OutputFile
    )

    if (-not (Test-Path $InputFile)) {
        Write-Error "输入文件不存在: $InputFile"
        exit 1
    }

    # 检查文件时间（5分钟内）
    $fileTime = (Get-Item $InputFile).LastWriteTime
    $diff = ((Get-Date) - $fileTime).TotalSeconds
    if ($diff -gt 300) {
        Write-Warning "文件可能不是新生成的（$([math]::Round($diff))秒前）"
    }

    # 计算 MD5
    $md5 = (Get-FileHash -Path $InputFile -Algorithm MD5).Hash
    Write-Host "固件 MD5: $md5"

    # 构造 169 字节包头
    $head = New-Object byte[] 169
    $bytes = [System.Text.Encoding]::ASCII.GetBytes("V1.0")
    [Array]::Copy($bytes, 0, $head, 0, 5)  # V1.0 + null
    $head[5] = [byte]0x55  # U
    $head[6] = [byte]0x4E  # N
    $head[7] = [byte]0x4B  # K
    $head[8] = [byte]0x4E  # N

    # MD5 大写十六进制写入 offset 9-40
    $md5Bytes = [System.Text.Encoding]::ASCII.GetBytes($md5)
    [Array]::Copy($md5Bytes, 0, $head, 9, 32)

    # offset 41-168 已经是 0x00（默认初始化）

    # 合并
    $outputDir = Split-Path $OutputFile -Parent
    if ($outputDir -and -not (Test-Path $outputDir)) {
        New-Item -ItemType Directory -Path $outputDir -Force | Out-Null
    }

    $inputBytes = [System.IO.File]::ReadAllBytes($InputFile)
    $outputBytes = New-Object byte[] ($head.Length + $inputBytes.Length)
    [Array]::Copy($head, 0, $outputBytes, 0, $head.Length)
    [Array]::Copy($inputBytes, 0, $outputBytes, $head.Length, $inputBytes.Length)
    [System.IO.File]::WriteAllBytes($OutputFile, $outputBytes)

    Write-Host "已生成: $OutputFile"
}

# ========== 模式 A ==========
if ($Mode -eq "A") {
    Write-Host "=== 模式A：添加 MD5 包头 ==="

    if (-not $Input) {
        Write-Error "模式A 需要 -Input 参数指定固件文件"
        exit 1
    }

    if (-not (Test-Path $Input)) {
        Write-Error "固件文件不存在: $Input"
        exit 1
    }

    # 输出文件名
    $baseName = [System.IO.Path]::GetFileNameWithoutExtension($Input)
    $outputFilename = "${baseName}_md5.bin"
    $outputPath = Join-Path $Output $outputFilename

    Add-AiPackHead -InputFile $Input -OutputFile $outputPath

    Write-Host ""
    Write-Host "=== 完成 ==="
    Get-Item $outputPath | Format-Table Name, Length, LastWriteTime

# ========== 模式 B ==========
} elseif ($Mode -eq "B") {
    Write-Host "=== 模式B：生成 OTA 固件 ==="

    # 检测项目根目录
    if ($ProjectRoot) {
        $script:ProjectRoot = Find-ProjectRoot -StartDir $ProjectRoot
    } else {
        $script:ProjectRoot = Find-ProjectRoot -StartDir (Get-Location)
    }

    # 读取配置
    Read-ProjectConfig -ProjectRoot $script:ProjectRoot

    Write-Host "项目目录: $script:ProjectRoot"
    Write-Host "当前版本: $script:CurrentVersion"
    Write-Host "默认前缀: $script:DefaultPrefix"
    Write-Host "语言: $script:LangSuffix"

    # 确定参数
    $finalPrefix = if ($Prefix) { $Prefix } else { $script:DefaultPrefix }
    $finalVersion = if ($Version) { $Version } else { $script:CurrentVersion }

    Write-Host "目标版本: $finalVersion"
    Write-Host "文件名前缀: $finalPrefix"

    $fwVersion = $script:CurrentVersion
    $cfgFile = "$script:ProjectRoot\xiaozhi_project_cfg.h"

    if (-not $SkipBuild) {
        # 修改版本号
        if ($finalVersion -ne $script:CurrentVersion) {
            $content = Get-Content $cfgFile -Raw
            $content = $content -replace '#define FW_VERSION\s+"[^"]*"', "#define FW_VERSION `"$finalVersion`""
            Set-Content -Path $cfgFile -Value $content -NoNewline
            $fwVersion = $finalVersion
            Write-Host "版本号已修改为: $fwVersion"
        }

        # 编译
        Write-Host ""
        Write-Host "--- 执行 make flash ---"
        Push-Location $script:ProjectRoot
        try {
            make flash
        } finally {
            Pop-Location
        }

        $fwOta = "$script:ProjectRoot\os\tools\flash_tool\chips\bl602\ota\FW_OTA.bin"
        if (-not (Test-Path $fwOta)) {
            Write-Error "FW_OTA.bin 未生成"
            # 恢复版本号
            if ($script:CurrentVersion -ne $fwVersion) {
                $content = Get-Content $cfgFile -Raw
                $content = $content -replace '#define FW_VERSION\s+"[^"]*"', "#define FW_VERSION `"$($script:CurrentVersion)`""
                Set-Content -Path $cfgFile -Value $content -NoNewline
            }
            exit 1
        }

        $Input = $fwOta
    } else {
        # skip-build 模式
        if (-not $Input) {
            $Input = "$script:ProjectRoot\os\tools\flash_tool\chips\bl602\ota\FW_OTA.bin"
        }
        if (-not (Test-Path $Input)) {
            Write-Error "FW_OTA.bin 不存在: $Input"
            Write-Error "请使用 -Input 指定路径，或先执行编译"
            exit 1
        }
    }

    # 添加 MD5 包头
    $otaFilename = "${finalPrefix}_${fwVersion}_$($script:LangSuffix)_ota.bin"
    $outputPath = Join-Path $Output $otaFilename
    Add-AiPackHead -InputFile $Input -OutputFile $outputPath

    # 恢复版本号
    if ($script:CurrentVersion -ne $fwVersion) {
        Write-Host ""
        Write-Host "--- 恢复版本号 ---"
        $content = Get-Content $cfgFile -Raw
        $content = $content -replace '#define FW_VERSION\s+"[^"]*"', "#define FW_VERSION `"$($script:CurrentVersion)`""
        Set-Content -Path $cfgFile -Value $content -NoNewline
        Write-Host "版本号已恢复为: $($script:CurrentVersion)"
    }

    Write-Host ""
    Write-Host "=== 完成 ==="
    Get-Item $outputPath | Format-Table Name, Length, LastWriteTime
}
