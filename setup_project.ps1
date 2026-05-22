# PowerShell 腳本：將項目文件組織到 project 資料夾中
# 運行方式: .\setup_project.ps1

param(
    [string]$SourcePath = (Get-Location),
    [string]$DestPath = "project"
)

$ErrorActionPreference = "Stop"

Write-Host "╔════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║ DJ 器材預購平台 - 項目結構組織工具                ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

# 目標路徑
$ProjectPath = Join-Path $SourcePath $DestPath

# 檢查源路徑
if (-not (Test-Path $SourcePath)) {
    Write-Host "❌ 源路徑不存在: $SourcePath" -ForegroundColor Red
    exit 1
}

Write-Host "📁 源路徑: $SourcePath" -ForegroundColor Green
Write-Host "📁 目標路徑: $ProjectPath" -ForegroundColor Green
Write-Host ""

# 檢查是否已存在 project 資料夾
if (Test-Path $ProjectPath) {
    Write-Host "⚠️  目標資料夾已存在" -ForegroundColor Yellow
    $response = Read-Host "是否要清空現有 project 資料夾？ (y/n)"
    if ($response -eq "y") {
        Write-Host "正在刪除現有 project 資料夾..." -ForegroundColor Yellow
        Remove-Item $ProjectPath -Recurse -Force
    } else {
        Write-Host "操作已取消" -ForegroundColor Yellow
        exit 0
    }
}

# 建立新的 project 資料夾
Write-Host "建立 project 資料夾結構..." -ForegroundColor Cyan
New-Item -ItemType Directory -Path $ProjectPath -Force | Out-Null

# 需要複製的目錄和文件
$itemsToCopy = @(
    "app",
    "templates",
    "static",
    "sql",
    "main.py",
    "requirements.txt",
    ".env.example",
    ".gitignore",
    "README.md",
    "QUICK_START.md",
    "PROJECT_STRUCTURE.md",
    "ARCHITECTURE_VERIFICATION.md"
)

# 複製文件和資料夾
$copiedCount = 0
foreach ($item in $itemsToCopy) {
    $sourcePath = Join-Path $SourcePath $item
    $destPath = Join-Path $ProjectPath $item
    
    if (Test-Path $sourcePath) {
        if ((Get-Item $sourcePath).PSIsContainer) {
            Write-Host "  ✅ 複製資料夾: $item" -ForegroundColor Green
            Copy-Item -Path $sourcePath -Destination $destPath -Recurse -Force
        } else {
            Write-Host "  ✅ 複製文件: $item" -ForegroundColor Green
            Copy-Item -Path $sourcePath -Destination $destPath -Force
        }
        $copiedCount++
    } else {
        Write-Host "  ⚠️  未找到: $item" -ForegroundColor Yellow
    }
}

Write-Host ""
Write-Host "╔════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║ ✅ 項目組織完成！" -ForegroundColor Green
Write-Host "╚════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""
Write-Host "📊 統計信息:" -ForegroundColor Cyan
Write-Host "  • 已複製項目: $copiedCount"
Write-Host "  • 目標位置: $ProjectPath"
Write-Host ""
Write-Host "📝 下一步:" -ForegroundColor Yellow
Write-Host "  1. cd $DestPath"
Write-Host "  2. python -m venv venv"
Write-Host "  3. venv\Scripts\activate"
Write-Host "  4. pip install -r requirements.txt"
Write-Host "  5. 配置 .env 文件中的數據庫連接"
Write-Host "  6. 導入 SQL 文件到 MySQL"
Write-Host "  7. uvicorn main:app --reload --port 8000"
Write-Host ""
