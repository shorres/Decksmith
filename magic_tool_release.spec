# Build configuration for PyInstaller
# -*- mode: python ; coding: utf-8 -*-

import os
from pathlib import Path

# Import version
spec_dir = Path(os.path.dirname(os.path.abspath(SPEC)))
version_file = spec_dir / "src" / "__version__.py"
version_info = {}
if version_file.exists():
    exec(open(version_file).read(), version_info)
    app_version = version_info.get('__version__', '1.0.0')
    app_name = version_info.get('__app_name__', 'Magic Tool')
else:
    app_version = '1.0.0'
    app_name = 'Magic Tool'

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('src', 'src'),
        ('data', 'data'),
    ],
    hiddenimports=[
        'tkinter',
        'tkinter.ttk',
        'tkinter.filedialog',
        'tkinter.messagebox',
        'tkinter.simpledialog',
        'requests',
        'urllib3',
        'certifi',
        'charset_normalizer',
        'json',
        'threading',
        'queue',
        'csv',
        're',
        'pyperclip',
        'datetime',
        'os',
        'time',
        'math',
        'collections',
        'dataclasses',
        'typing',
        'PIL',
        'PIL.Image',
        'PIL.ImageTk',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name=f'{app_name} v{app_version}',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    version=f'release/{app_version}/version_info.txt',
    icon=f'release/{app_version}/magic_tool.ico' if os.path.exists(f'release/{app_version}/magic_tool.ico') else None,
)
