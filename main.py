#!/usr/bin/env python3
"""
Magic: The Gathering Arena Deck Manager
Main application entry point
"""

import tkinter as tk
from tkinter import ttk
import sys
import os

# Add src directory to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from gui.main_window import MainWindow

def main():
    """Main application entry point"""
    root = tk.Tk()
    
    # Apply theme once at startup for better performance
    try:
        import sv_ttk
        sv_ttk.set_theme("dark")
        print("✓ Applied Sun Valley dark theme")
    except Exception as e:
        print(f"Failed to apply theme: {e}")
    
    app = MainWindow(root)
    root.mainloop()

if __name__ == "__main__":
    main()
