"""
PyInstaller spec file for Magic Tool
This provides fine-grained control over the packaging process
"""

# -*- mode: python ; coding: utf-8 -*-

import os
import sys
from pathlib import Path

# Get the application root directory
app_root = Path(__file__).parent

block_cipher = None

# Define all the data files and directories to include
datas = [
    # Include the entire src directory
    (str(app_root / 'src'), 'src'),
    # Include data directory (for collections, decks, cache)
    (str(app_root / 'data'), 'data'),
    # Include any README or documentation
    (str(app_root / 'README.md'), '.'),
    # Include requirements for reference
    (str(app_root / 'requirements.txt'), '.'),
]

# Define hidden imports (modules that PyInstaller might miss)
hidden_imports = [
    'tkinter',
    'tkinter.ttk',
    'tkinter.messagebox',
    'tkinter.simpledialog',
    'tkinter.filedialog',
    'PIL',
    'PIL.Image',
    'PIL.ImageTk',
    'requests',
    'json',
    'threading',
    'webbrowser',
    'urllib.parse',
    'dataclasses',
    'typing',
    'collections',
    'pathlib',
    'datetime',
    'time',
    'os',
    'sys',
    # Application-specific modules
    'src.models.card',
    'src.models.collection',
    'src.models.deck',
    'src.gui.main_window',
    'src.gui.collection_tab',
    'src.gui.deck_tab',
    'src.gui.ai_recommendations_tab',
    'src.gui.card_details_modal',
    'src.gui.sun_valley_theme',
    'src.utils.scryfall_api',
    'src.utils.persistent_cache',
    'src.utils.enhanced_recommendations_sync',
    'src.utils.clipboard_handler',
    'src.utils.csv_handler',
]

# Analysis phase - what files to include and analyze
a = Analysis(
    ['main.py'],  # Entry point script
    pathex=[str(app_root)],  # Paths to search for modules
    binaries=[],  # Additional binary files (none needed for this app)
    datas=datas,  # Data files to include
    hiddenimports=hidden_imports,  # Hidden imports to include
    hookspath=[],  # Custom hooks directory
    hooksconfig={},  # Hooks configuration
    runtime_hooks=[],  # Runtime hooks
    excludes=[  # Modules to exclude to reduce size
        'matplotlib',
        'numpy',
        'pandas',
        'scipy',
        'pytest',
        'setuptools',
        'wheel',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

# PYZ phase - create the Python zip archive
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

# EXE phase - create the executable
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='Magic Tool',  # Executable name
    debug=False,  # Set to True for debugging
    bootloader_ignore_signals=False,
    strip=False,  # Set to True to reduce size (may break some functionality)
    upx=False,  # UPX compression (can cause issues with some antivirus)
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # False for GUI app, True for console output
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    # Windows-specific options
    version=None,  # Version information file (optional)
    icon=None,  # Application icon (none available)
)

# Optional: Create a COLLECT for directory distribution instead of single file
# Uncomment the following lines if you want a directory distribution:

# coll = COLLECT(
#     exe,
#     a.binaries,
#     a.zipfiles,
#     a.datas,
#     strip=False,
#     upx=False,
#     upx_exclude=[],
#     name='Magic Tool'
# )
