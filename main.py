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
    app = MainWindow(root)
    root.mainloop()

if __name__ == "__main__":
    main()
