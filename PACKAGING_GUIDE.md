# Magic Tool - Packaging & Distribution Guide

## Overview
This guide covers multiple methods to package Magic Tool as a standalone executable for easy distribution.

## 🚀 Quick Start (Recommended Method)

### Windows
```bash
# 1. Activate virtual environment
.venv\Scripts\activate

# 2. Install build dependencies  
pip install -r requirements-build.txt

# 3. Run the build script
build.bat
```

### Linux/macOS
```bash
# 1. Activate virtual environment
source .venv/bin/activate

# 2. Install build dependencies
pip install -r requirements-build.txt

# 3. Make build script executable and run
chmod +x build.sh
./build.sh
```

## 📦 Packaging Methods

### Method 1: PyInstaller (Recommended)

**Advantages:**
- ✅ Best tkinter support
- ✅ Handles PIL/Pillow well
- ✅ Single-file executable option
- ✅ Good cross-platform support
- ✅ Active development

**Simple command:**
```bash
pyinstaller --onefile --windowed --name "Magic Tool" main.py
```

**Advanced command with all features:**
```bash
pyinstaller --onefile --windowed --name "Magic Tool" ^
  --add-data "src;src" ^
  --add-data "data;data" ^
  --hidden-import tkinter ^
  --hidden-import PIL ^
  --hidden-import requests ^
  --icon icon.ico ^
  main.py
```

**Using spec file (recommended):**
```bash
pyinstaller --clean --noconfirm magic_tool.spec
```

### Method 2: Auto-py-to-exe (GUI Interface)

**Advantages:**
- ✅ User-friendly GUI interface
- ✅ Based on PyInstaller
- ✅ Visual configuration

**Usage:**
```bash
pip install auto-py-to-exe
auto-py-to-exe
```

Then configure through the graphical interface.

### Method 3: cx_Freeze

**Advantages:**
- ✅ Cross-platform
- ✅ Good Python 3 support
- ✅ Produces directory distributions

**Usage:**
```bash
pip install cx_freeze
python setup_cx_freeze.py build
```

### Method 4: Nuitka (Advanced)

**Advantages:**
- ✅ Compiles to C++ (faster execution)
- ✅ Smaller executables
- ✅ Better performance

**Usage:**
```bash
pip install nuitka
python -m nuitka --onefile --windows-disable-console --enable-plugin=tk-inter main.py
```

## 📁 File Structure After Building

### PyInstaller Output
```
dist/
└── Magic Tool.exe        # Single executable file (~50-80 MB)

# Or for directory distribution:
dist/
└── Magic Tool/
    ├── Magic Tool.exe    # Main executable
    ├── _internal/        # Dependencies and libraries
    ├── data/             # Application data
    └── src/              # Source files
```

### cx_Freeze Output
```
build/
└── exe.win-amd64-3.13/
    ├── Magic Tool.exe    # Main executable
    ├── lib/              # Python libraries
    ├── data/             # Application data
    └── src/              # Source files
```

## 🔧 Build Configuration

### Included Files
- **Source Code**: Complete `src/` directory
- **Data Directory**: `data/` for collections, decks, cache
- **Documentation**: README.md and other docs
- **Dependencies**: All Python packages and libraries

### Hidden Imports (Automatically Included)
- tkinter and all GUI components
- PIL/Pillow for image handling
- requests for API calls  
- All Magic Tool modules and utilities
- Persistent cache system

### Excluded Packages (For Smaller Size)
- matplotlib, numpy, pandas (not needed)
- Development tools (pytest, setuptools)
- Documentation generators

## 📊 Expected File Sizes

| Method | File Size | Startup Time | Notes |
|--------|-----------|--------------|--------|
| PyInstaller (onefile) | 50-80 MB | 2-3 seconds | Single executable |
| PyInstaller (onedir) | 100-150 MB | 1-2 seconds | Directory distribution |
| cx_Freeze | 80-120 MB | 1-2 seconds | Directory only |
| Nuitka | 30-60 MB | <1 second | Compiled, fastest |

## 🛠️ Troubleshooting

### Common Issues

**1. Missing modules error:**
```
ModuleNotFoundError: No module named 'src.models.card'
```
**Solution:** Add to hidden imports in spec file or use `--hidden-import` flag.

**2. tkinter not found:**
```
ImportError: No module named 'tkinter'
```
**Solution:** Use `--hidden-import tkinter` or install tkinter-dev package.

**3. PIL/Image issues:**
```
ImportError: cannot import name 'Image' from 'PIL'
```
**Solution:** Ensure PIL is in hidden imports and Pillow is installed.

**4. Large executable size:**
**Solutions:**
- Use directory distribution instead of onefile
- Enable UPX compression (may cause antivirus issues)
- Exclude unnecessary packages

**5. Slow startup with onefile:**
**Solution:** Use directory distribution for faster startup.

### Debug Mode
Add `--debug all` to PyInstaller command for verbose output:
```bash
pyinstaller --debug all --onefile main.py
```

## 🚢 Distribution

### Single File Distribution
- Copy `Magic Tool.exe` to any Windows machine
- No installation required
- Runs independently with all dependencies embedded

### Directory Distribution  
- Distribute entire `dist/Magic Tool/` folder
- Slightly faster startup
- Larger file size but same functionality

### Creating an Installer
Use NSIS or Inno Setup to create a proper Windows installer:

```nsis
; Basic NSIS installer script
OutFile "Magic Tool Installer.exe"
InstallDir "$PROGRAMFILES\Magic Tool"
Section
    SetOutPath $INSTDIR
    File /r "dist\Magic Tool\*"
    CreateShortcut "$DESKTOP\Magic Tool.lnk" "$INSTDIR\Magic Tool.exe"
SectionEnd
```

## 🔒 Security Considerations

### Antivirus Detection
- Single-file executables may trigger antivirus warnings
- This is a false positive common with PyInstaller
- Consider code signing for commercial distribution
- Directory distributions have fewer false positives

### Code Signing (Optional)
For professional distribution:
```bash
pyinstaller --codesign-identity "Your Code Signing Certificate" magic_tool.spec
```

## 🏗️ Automation

### CI/CD Pipeline
```yaml
# GitHub Actions example
name: Build Executables
on: [push, release]
jobs:
  build-windows:
    runs-on: windows-latest
    steps:
      - uses: actions/checkout@v2
      - name: Setup Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.13'
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install -r requirements-build.txt
      - name: Build executable
        run: pyinstaller --clean --noconfirm magic_tool.spec
      - name: Upload artifact
        uses: actions/upload-artifact@v2
        with:
          name: magic-tool-windows
          path: dist/Magic Tool.exe
```

## 📝 Final Notes

- **Recommended**: Use PyInstaller with the provided spec file
- **Testing**: Always test the executable on a clean system
- **Updates**: Rebuild when updating dependencies or source code
- **Performance**: Directory distributions start faster than single files
- **Size**: Single files are more portable but larger and slower to start

The build scripts provided automate the entire process and handle common issues automatically!
