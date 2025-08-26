"""
Import Validation Script for Decksmith
=====================================

This script validates that all critical imports are available and working
before building the executable. Run this before every build to catch
missing dependencies early.

Usage: python validate_imports.py
"""

import os
import sys

# Critical system imports that must be available for the executable to work
CRITICAL_IMPORTS = [
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
    # HTTP and networking
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
    # Image processing
    'PIL',
    'PIL.Image',
    'PIL.ImageTk',
]

# Application-specific imports (these may have path issues in dev but should work in build)
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

def validate_import(module_name: str) -> tuple[bool, str]:
    """
    Test if a module can be imported successfully.
    
    Args:
        module_name: Name of the module to test
        
    Returns:
        Tuple of (success: bool, error_message: str)
    """
    try:
        __import__(module_name)
        return True, ""
    except Exception as e:
        return False, str(e)

def run_import_validation() -> bool:
    """
    Run complete import validation.
    
    Returns:
        True if all critical imports pass, False otherwise
    """
    print("DECKSMITH IMPORT VALIDATION")
    print("=" * 40)
    
    all_passed = True
    failed_critical = []
    failed_app = []
    
    # Test critical imports
    print("\nTesting Critical Dependencies:")
    for module in CRITICAL_IMPORTS:
        success, error = validate_import(module)
        if success:
            print(f"  [OK] {module}")
        else:
            print(f"  [FAIL] {module}: {error}")
            failed_critical.append(module)
            all_passed = False
    
    # Test app imports
    print(f"\nTesting Application Modules:")
    for module in APP_IMPORTS:
        success, error = validate_import(module)
        if success:
            print(f"  [OK] {module}")
        else:
            print(f"  [WARN] {module}: {error}")
            failed_app.append(module)
    
    # Summary
    print(f"\nValidation Summary:")
    print(f"  Critical imports: {len(CRITICAL_IMPORTS) - len(failed_critical)}/{len(CRITICAL_IMPORTS)} passed")
    print(f"  App imports: {len(APP_IMPORTS) - len(failed_app)}/{len(APP_IMPORTS)} passed")
    
    # Report failures
    if failed_critical:
        print(f"\nCRITICAL FAILURES ({len(failed_critical)}):")
        for module in failed_critical:
            print(f"  * {module}")
        print("   [ERROR] DO NOT build executable until issues are resolved")
        return False
    
    if failed_app:
        print(f"\nAPP MODULE ISSUES ({len(failed_app)}):")
        for module in failed_app:
            print(f"  * {module}")
        print("  These may indicate development environment issues.")
    
    if not failed_critical:
        print("\nALL CRITICAL IMPORTS PASSED!")
        print("   [OK] Safe to build executable")
    
    return True

def validate_spec_file() -> bool:
    """
    Validate that the spec file includes all critical imports.
    """
    print(f"\nValidating PyInstaller Spec File:")
    
    # Check if spec file exists
    if not os.path.exists('decksmith_release.spec'):
        print(f"  [INFO] Spec file not found (decksmith_release.spec)")
        print(f"         This is expected during GitHub Actions builds")
        return True
    
    try:
        with open('decksmith_release.spec', 'r') as f:
            spec_content = f.read()
        
        missing_imports = []
        for module in CRITICAL_IMPORTS:
            if f"'{module}'" not in spec_content and f'"{module}"' not in spec_content:
                missing_imports.append(module)
        
        if missing_imports:
            print(f"  [FAIL] Missing from spec file: {len(missing_imports)} modules")
            for module in missing_imports:
                print(f"    * {module}")
            return False
        else:
            print(f"  [OK] All critical imports found in spec file")
            return True
            
    except Exception as e:
        print(f"  [ERROR] Error reading spec file: {e}")
        return False

if __name__ == "__main__":
    print("Starting comprehensive import validation...")
    
    # Run import validation
    imports_valid = run_import_validation()
    
    # Validate spec file
    spec_valid = validate_spec_file()
    
    # Final result
    if imports_valid and spec_valid:
        print(f"\n[SUCCESS] VALIDATION COMPLETE - ALL CHECKS PASSED!")
        print(f"   Ready for executable build")
        sys.exit(0)
    else:
        print(f"\n[FAILED] VALIDATION FAILED!")
        print(f"   Please fix issues before building")
        sys.exit(1)
