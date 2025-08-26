# Magic Tool - Enhanced Build Script (PowerShell)
# Reduces Windows Defender False Positives

Write-Host "=====================================================" -ForegroundColor Cyan
Write-Host " Magic Tool - Enhanced Build Script" -ForegroundColor White
Write-Host " Reduces Windows Defender False Positives" -ForegroundColor Green
Write-Host "=====================================================" -ForegroundColor Cyan
Write-Host

# Activate virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor Yellow
& ".venv\Scripts\Activate.ps1"

# Clean previous builds
Write-Host "Cleaning previous builds..." -ForegroundColor Yellow
if (Test-Path "build") { Remove-Item "build" -Recurse -Force }
if (Test-Path "dist") { Remove-Item "dist" -Recurse -Force }

# Build with enhanced configuration
Write-Host "Building Magic Tool with enhanced configuration..." -ForegroundColor Yellow
& pyinstaller --clean --noconfirm magic_tool.spec

if ($LASTEXITCODE -ne 0) {
    Write-Host "Build failed!" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

# Check if build was successful
$exePath = "dist\Magic Tool\Magic Tool.exe"
if (Test-Path $exePath) {
    Write-Host
    Write-Host "=====================================================" -ForegroundColor Green
    Write-Host " Build completed successfully!" -ForegroundColor White
    Write-Host "=====================================================" -ForegroundColor Green
    Write-Host
    Write-Host "Location: $exePath" -ForegroundColor Cyan
    Write-Host
    Write-Host "IMPORTANT: To reduce Windows Defender false positives:" -ForegroundColor Yellow
    Write-Host
    Write-Host "1. Add the executable to Windows Defender exclusions" -ForegroundColor White
    Write-Host "2. Submit to VirusTotal for analysis if needed" -ForegroundColor White
    Write-Host "3. Consider code signing for production distribution" -ForegroundColor White
    Write-Host
    Write-Host "The executable now includes:" -ForegroundColor Green
    Write-Host "- Version information" -ForegroundColor White
    Write-Host "- Windows manifest" -ForegroundColor White
    Write-Host "- Application icon" -ForegroundColor White
    Write-Host "- Stripped debug symbols" -ForegroundColor White
    Write-Host
    
    # Get file size
    $fileSize = (Get-Item $exePath).Length
    $fileSizeMB = [Math]::Round($fileSize / 1MB, 2)
    Write-Host "File size: $fileSizeMB MB" -ForegroundColor Cyan
    
    Read-Host "Press Enter to exit"
} else {
    Write-Host "Build failed - executable not found!" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}
