"""
Import Validation Script for Decksmith
=====================================

This script validates that all critical imports are available and working
before building the executable. Run this before every build to catch
missing dependencies early.

Usage: python validate_imports.py
"""

import sys
import importlib
from typing import List, Tuple
import traceback

# Critical modules that MUST be available in the executable
CRITICAL_IMPORTS = [
    # Core Python modules
    'tkinter',
    'tkinter.ttk', 
    'tkinter.filedialog',
    'tkinter.messagebox',
    'tkinter.simpledialog',
    'json',
    'threading',
    'queue',
    'csv',
    're',
    'datetime',
    'os',
    'time',
    'math',
    'collections',
    'dataclasses',
    'typing',
    'io',
    'sys',
    'pathlib',
    'logging',
    
    # External dependencies
    'requests',
    'requests.adapters',
    'requests.auth', 
    'requests.cookies',
    'requests.models',
    'requests.sessions',
    'urllib3',
    'urllib3.connection',
    'urllib3.connectionpool',
    'urllib3.poolmanager',
    'urllib3.util',
    'urllib3.util.retry',
    'certifi',
    'charset_normalizer',
    'pyperclip',
    'PIL',
    'PIL.Image',
    'PIL.ImageTk',
]

# Application-specific modules that should work in development
APP_IMPORTS = [
    'src.models.card',
    'src.models.deck', 
    'src.models.collection',
    'src.utils.scryfall_api',
    'src.utils.persistent_cache',
    'src.utils.enhanced_recommendations_sync',
    'src.gui.main_window',
    'src.gui.enhanced_import_dialog',
    'src.gui.ai_recommendations_tab',
]

def validate_import(module_name: str) -> Tuple[bool, str]:
    """
    Validate that a module can be imported successfully.
    
    Returns:
        Tuple of (success: bool, error_message: str)
    """
    try:
        importlib.import_module(module_name)
        return True, ""
    except Exception as e:
        return False, str(e)

def run_import_validation() -> bool:
    """
    Run complete import validation.
    
    Returns:
        True if all critical imports pass, False otherwise
    """
    print("🔍 Decksmith Import Validation")
    print("=" * 40)
    
    all_passed = True
    failed_critical = []
    failed_app = []
    
    # Test critical imports
    print("\n📦 Testing Critical Dependencies:")
    for module in CRITICAL_IMPORTS:
        success, error = validate_import(module)
        if success:
            print(f"  ✅ {module}")
        else:
            print(f"  ❌ {module}: {error}")
            failed_critical.append((module, error))
            all_passed = False
    
    # Test application imports
    print(f"\n🏠 Testing Application Modules:")
    for module in APP_IMPORTS:
        success, error = validate_import(module)
        if success:
            print(f"  ✅ {module}")
        else:
            print(f"  ⚠️  {module}: {error}")
            failed_app.append((module, error))
    
    # Summary
    print(f"\n📊 Validation Summary:")
    print(f"  Critical imports: {len(CRITICAL_IMPORTS) - len(failed_critical)}/{len(CRITICAL_IMPORTS)} passed")
    print(f"  App imports: {len(APP_IMPORTS) - len(failed_app)}/{len(APP_IMPORTS)} passed")
    
    if failed_critical:
        print(f"\n❌ CRITICAL FAILURES ({len(failed_critical)}):")
        for module, error in failed_critical:
            print(f"  • {module}: {error}")
        print("\n⚠️  These modules MUST be fixed before building the executable!")
    
    if failed_app:
        print(f"\n⚠️  APP MODULE ISSUES ({len(failed_app)}):")
        for module, error in failed_app:
            print(f"  • {module}: {error}")
        print("  These may indicate development environment issues.")
    
    if all_passed:
        print("\n🎯 ALL CRITICAL IMPORTS PASSED!")
        print("   ✅ Safe to build executable")
    else:
        print(f"\n🚨 VALIDATION FAILED!")
        print("   ❌ DO NOT build executable until issues are resolved")
    
    return all_passed

def validate_spec_file() -> bool:
    """
    Validate that the spec file includes all critical imports.
    """
    print(f"\n🔧 Validating PyInstaller Spec File:")
    
    try:
        with open('magic_tool_release.spec', 'r') as f:
            spec_content = f.read()
        
        missing_imports = []
        for module in CRITICAL_IMPORTS:
            if f"'{module}'" not in spec_content and f'"{module}"' not in spec_content:
                missing_imports.append(module)
        
        if missing_imports:
            print(f"  ❌ Missing from spec file: {len(missing_imports)} modules")
            for module in missing_imports:
                print(f"    • {module}")
            return False
        else:
            print(f"  ✅ All critical imports found in spec file")
            return True
            
    except Exception as e:
        print(f"  ❌ Error reading spec file: {e}")
        return False

if __name__ == "__main__":
    print("Starting comprehensive import validation...")
    
    imports_valid = run_import_validation()
    spec_valid = validate_spec_file()
    
    if imports_valid and spec_valid:
        print(f"\n🎉 VALIDATION COMPLETE - ALL CHECKS PASSED!")
        print("   Ready for executable build")
        sys.exit(0)
    else:
        print(f"\n💥 VALIDATION FAILED!")
        print("   Fix issues before building")
        sys.exit(1)
