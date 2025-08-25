#!/bin/bash

# Magic Tool Build Script for Linux/macOS
# This script packages the Magic Tool application into a standalone executable

echo "Magic Tool - Build Script (Linux/macOS)"
echo "======================================="
echo

# Check if virtual environment is activated
if [ -z "$VIRTUAL_ENV" ]; then
    echo "Error: Virtual environment not activated"
    echo "Please activate the virtual environment first:"
    echo "  source .venv/bin/activate"
    echo
    exit 1
fi

# Check if PyInstaller is installed
if ! python -c "import PyInstaller" 2>/dev/null; then
    echo "Installing PyInstaller..."
    python -m pip install pyinstaller
    if [ $? -ne 0 ]; then
        echo "Error: Failed to install PyInstaller"
        exit 1
    fi
fi

# Clean previous builds
echo "Cleaning previous builds..."
rm -rf build dist "Magic Tool" "Magic Tool.app"

echo
echo "Building Magic Tool executable..."
echo "This may take several minutes..."
echo

# Build using the spec file
python -m PyInstaller --clean --noconfirm magic_tool.spec

if [ $? -ne 0 ]; then
    echo
    echo "Error: Build failed!"
    echo "Check the output above for error messages."
    exit 1
fi

# Check if the executable was created
if [ -f "dist/Magic Tool" ] || [ -d "dist/Magic Tool.app" ]; then
    echo
    echo "========================================"
    echo "BUILD SUCCESSFUL!"
    echo "========================================"
    echo
    echo "The executable has been created at:"
    if [ -f "dist/Magic Tool" ]; then
        echo "  dist/Magic Tool"
        echo
        echo "File size:"
        ls -lh "dist/Magic Tool" | awk '{print $5, $9}'
    elif [ -d "dist/Magic Tool.app" ]; then
        echo "  dist/Magic Tool.app"
        echo
        echo "App bundle size:"
        du -sh "dist/Magic Tool.app"
    fi
    echo
    echo "You can now distribute this file/bundle!"
    echo
    
    # Offer to test the executable
    read -p "Would you like to test the executable now? (y/n): " test
    if [ "$test" = "y" ] || [ "$test" = "Y" ]; then
        echo "Starting Magic Tool..."
        if [ -f "dist/Magic Tool" ]; then
            ./dist/Magic\ Tool &
        elif [ -d "dist/Magic Tool.app" ]; then
            open "dist/Magic Tool.app"
        fi
    fi
else
    echo
    echo "Error: Executable was not created successfully."
    echo "Check the PyInstaller output for errors."
fi

echo
echo "Build process complete."
