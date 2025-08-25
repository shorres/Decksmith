"""
Setup script for Magic Tool using cx_Freeze
Alternative packaging method to PyInstaller
"""

from cx_Freeze import setup, Executable
import sys
import os
from pathlib import Path

# Get application information
app_root = Path(__file__).parent

# Include files and directories
include_files = [
    (str(app_root / 'src'), 'src'),
    (str(app_root / 'data'), 'data'),
    (str(app_root / 'README.md'), 'README.md'),
]

# Packages to include
packages = [
    'tkinter',
    'PIL',
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
]

# Modules to include
includes = [
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

# Build options
build_exe_options = {
    'packages': packages,
    'includes': includes,
    'include_files': include_files,
    'excludes': [
        'matplotlib',
        'numpy', 
        'pandas',
        'scipy',
        'pytest',
        'setuptools',
        'wheel',
    ],
    'zip_include_packages': ['encodings', 'PySide6'],
}

# Executable configuration
executables = [
    Executable(
        'main.py',
        base='Win32GUI' if sys.platform == 'win32' else None,  # Hide console on Windows
        target_name='Magic Tool',
        icon='icon.ico' if os.path.exists('icon.ico') else None,
    )
]

# Setup configuration
setup(
    name='Magic Tool',
    version='1.0.0',
    description='Magic: The Gathering Arena Deck Manager with AI Recommendations',
    author='Magic Tool Team',
    options={'build_exe': build_exe_options},
    executables=executables,
)
