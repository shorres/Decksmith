"""
PyInstaller spec file for Magic Tool
This provides fine-grained control over the packaging process
"""

# -*- mode: python ; coding: utf-8 -*-

import os

# Get the current directory - spec files need to use SPECPATH
current_dir = os.path.dirname(SPECPATH)

# Use absolute path as fallback
if not os.path.exists(os.path.join(current_dir, 'main.py')):
    # Use the directory containing the spec file directly
    current_dir = r'D:\Repos\Magic Tool'

# Define standard library imports only
hiddenimports = [
    'tkinter',
    'tkinter.ttk',
    'tkinter.filedialog',
    'tkinter.messagebox',
    'tkinter.simpledialog',
    'PIL',
    'PIL.Image',
    'PIL.ImageTk',
    'requests',
    'json',
    'csv',
    'datetime',
    'threading',
    'pyperclip',  # For clipboard handling
    'sv_ttk',     # Sun Valley theme
]

# Data files to include
datas = []

# Include data directory if it exists
data_dir = os.path.join(current_dir, 'data')
if os.path.exists(data_dir):
    datas.append((data_dir, 'data'))

# Include the entire src directory as data
src_dir = os.path.join(current_dir, 'src')
if os.path.exists(src_dir):
    datas.append((src_dir, 'src'))

a = Analysis(
    ['main.py'],
    pathex=[current_dir],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['matplotlib', 'numpy', 'pandas', 'scipy', 'pytest'],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=None,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=None)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='Magic Tool',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,  # Disable console for clean GUI launch
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name='Magic Tool',
)
