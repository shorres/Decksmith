@echo off
REM Magic Tool Build Script
REM This script packages the Magic Tool application into a standalone executable

echo Magic Tool - Build Script
echo ===========================
echo.

REM Check if virtual environment is activated
if "%VIRTUAL_ENV%"=="" (
    echo Error: Virtual environment not activated
    echo Please activate the virtual environment first:
    echo   .venv\Scripts\activate
    echo.
    pause
    exit /b 1
)

REM Check if PyInstaller is installed
python -c "import PyInstaller" 2>nul
if errorlevel 1 (
    echo Installing PyInstaller...
    python -m pip install pyinstaller
    if errorlevel 1 (
        echo Error: Failed to install PyInstaller
        pause
        exit /b 1
    )
)

REM Clean previous builds
echo Cleaning previous builds...
if exist "build" rmdir /s /q "build"
if exist "dist" rmdir /s /q "dist"
if exist "Magic Tool.exe" del "Magic Tool.exe"

echo.
echo Building Magic Tool executable...
echo This may take several minutes...
echo.

REM Build using the spec file
python -m PyInstaller --clean --noconfirm magic_tool.spec

if errorlevel 1 (
    echo.
    echo Error: Build failed!
    echo Check the output above for error messages.
    pause
    exit /b 1
)

REM Check if the executable was created
if exist "dist\Magic Tool.exe" (
    echo.
    echo ========================================
    echo BUILD SUCCESSFUL!
    echo ========================================
    echo.
    echo The executable has been created at:
    echo   dist\Magic Tool.exe
    echo.
    echo File size:
    dir "dist\Magic Tool.exe" | find "Magic Tool.exe"
    echo.
    echo You can now distribute this single file!
    echo.
    
    REM Offer to test the executable
    set /p test="Would you like to test the executable now? (y/n): "
    if /i "%test%"=="y" (
        echo Starting Magic Tool...
        start "" "dist\Magic Tool.exe"
    )
) else (
    echo.
    echo Error: Executable was not created successfully.
    echo Check the PyInstaller output for errors.
)

echo.
echo Build process complete.
pause
