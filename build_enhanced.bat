@echo off
echo =====================================================
echo  Magic Tool - Enhanced Build Script
echo  Reduces Windows Defender False Positives
echo =====================================================
echo.

:: Activate virtual environment
call .venv\Scripts\activate.bat

:: Clean previous builds
echo Cleaning previous builds...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist

:: Build with enhanced configuration
echo Building Magic Tool with enhanced configuration...
pyinstaller --clean --noconfirm magic_tool.spec

if %errorlevel% neq 0 (
    echo Build failed!
    pause
    exit /b 1
)

:: Check if build was successful
if exist "dist\Magic Tool\Magic Tool.exe" (
    echo.
    echo =====================================================
    echo  Build completed successfully!
    echo =====================================================
    echo.
    echo Location: dist\Magic Tool\Magic Tool.exe
    echo.
    echo IMPORTANT: To reduce Windows Defender false positives:
    echo.
    echo 1. Add the executable to Windows Defender exclusions
    echo 2. Submit to VirusTotal for analysis if needed
    echo 3. Consider code signing for production distribution
    echo.
    echo The executable now includes:
    echo - Version information
    echo - Windows manifest
    echo - Application icon
    echo - Stripped debug symbols
    echo.
    pause
) else (
    echo Build failed - executable not found!
    pause
    exit /b 1
)
