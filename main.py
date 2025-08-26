#!/usr/bin/env python3
"""
Magic: The Gathering Arena Deck Manager
A comprehensive tool for managing MTG Arena collections and decks
"""

import sys
import os

def setup_paths():
    """Setup Python paths for both development and packaged environments"""
    # Fix potential stdin/stdout issues in GUI mode
    if getattr(sys, 'frozen', False):
        # When packaged, redirect stdin/stdout to avoid issues
        import io
        if sys.stdin is None:
            sys.stdin = io.StringIO()
        if sys.stdout is None:
            sys.stdout = io.StringIO()
        if sys.stderr is None:
            sys.stderr = io.StringIO()
    
    if getattr(sys, 'frozen', False):
        # Running as PyInstaller bundle
        application_path = sys._MEIPASS
        
        # Add the bundle directory to Python path
        if application_path not in sys.path:
            sys.path.insert(0, application_path)
        
        # Also add src subdirectory if it exists
        src_path = os.path.join(application_path, 'src')
        if os.path.exists(src_path) and src_path not in sys.path:
            sys.path.insert(0, src_path)
            
    else:
        # Running in development
        script_dir = os.path.dirname(os.path.abspath(__file__))
        src_path = os.path.join(script_dir, 'src')
        if src_path not in sys.path:
            sys.path.insert(0, src_path)

def main():
    """Main application entry point"""
    setup_paths()
    
    try:
        # Import after path setup
        import tkinter as tk
        from gui.main_window import MainWindow
        
        # Create root window
        root = tk.Tk()
        
        # Create main window
        app = MainWindow(root)
        
        # Start the application
        root.mainloop()
        
    except ImportError as e:
        import traceback
        error_msg = f"Import error: {e}\n\nFull traceback:\n{traceback.format_exc()}"
        try:
            import tkinter as tk
            from tkinter import messagebox
            root = tk.Tk()
            root.withdraw()
            messagebox.showerror("Import Error", error_msg)
        except:
            print(error_msg)
        sys.exit(1)
        
    except Exception as e:
        import traceback
        error_msg = f"Application error: {e}\n\nFull traceback:\n{traceback.format_exc()}"
        try:
            import tkinter as tk
            from tkinter import messagebox
            root = tk.Tk()
            root.withdraw()
            messagebox.showerror("Application Error", error_msg)
        except:
            print(error_msg)
        sys.exit(1)

if __name__ == "__main__":
    main()
