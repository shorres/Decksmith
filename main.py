#!/usr/bin/env python3
"""
Magic: The Gathering Arena Deck Manager
A comprehensive tool for managing MTG Arena collections and decks
"""

import sys
import os

def setup_paths():
    """Setup Python paths for both development and packaged environments"""
    if getattr(sys, 'frozen', False):
        # Running as PyInstaller bundle
        application_path = sys._MEIPASS
        print(f"Running from bundle: {application_path}")
        
        # Add the bundle directory to Python path
        if application_path not in sys.path:
            sys.path.insert(0, application_path)
        
        # Also add src subdirectory if it exists
        src_path = os.path.join(application_path, 'src')
        if os.path.exists(src_path) and src_path not in sys.path:
            sys.path.insert(0, src_path)
            print(f"Added src path: {src_path}")
        
        # List contents of bundle for debugging
        print("Bundle contents:")
        for item in os.listdir(application_path):
            print(f"  {item}")
            
    else:
        # Running in development
        script_dir = os.path.dirname(os.path.abspath(__file__))
        src_path = os.path.join(script_dir, 'src')
        if src_path not in sys.path:
            sys.path.insert(0, src_path)
        print(f"Running in development: {script_dir}")
    
    print(f"Python path entries: {sys.path[:3]}...")

def main():
    """Main application entry point"""
    setup_paths()
    
    try:
        # Import after path setup
        from gui.main_window import MagicToolGUI
        
        # Create and run the application
        app = MagicToolGUI()
        app.run()
        
    except ImportError as e:
        print(f"Import error: {e}")
        print(f"Current working directory: {os.getcwd()}")
        
        # More detailed debugging
        if getattr(sys, 'frozen', False):
            bundle_path = sys._MEIPASS
            src_path = os.path.join(bundle_path, 'src')
            print(f"Bundle path: {bundle_path}")
            print(f"Looking for src at: {src_path}")
            
            if os.path.exists(src_path):
                print("Contents of src directory:")
                for item in os.listdir(src_path):
                    print(f"  {item}")
                    if item == 'gui' and os.path.isdir(os.path.join(src_path, item)):
                        gui_path = os.path.join(src_path, item)
                        print(f"Contents of gui directory:")
                        for gui_item in os.listdir(gui_path):
                            print(f"    {gui_item}")
            else:
                print("src directory not found in bundle!")
        
        input("Press Enter to exit...")
        sys.exit(1)
        
    except Exception as e:
        print(f"Application error: {e}")
        import traceback
        traceback.print_exc()
        input("Press Enter to exit...")
        sys.exit(1)

if __name__ == "__main__":
    main()
