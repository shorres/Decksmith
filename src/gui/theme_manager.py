"""
Theme Manager for MTG Arena Deck Manager
Provides comprehensive theming system with dark, light, and cyberpunk themes
"""

import tkinter as tk
from tkinter import ttk
import json
import os
from typing import Dict, Any, Optional

class ThemeManager:
    """Manages application themes and styling"""
    
    def __init__(self, root: tk.Tk):
        self.root = root
        self.current_theme = "dark"
        self.themes = self._load_themes()
        self.settings_file = os.path.join("data", "theme_settings.json")
        
        # Load saved theme preference
        self._load_theme_settings()
        
        # Apply default theme
        self.apply_theme(self.current_theme)
    
    def _load_themes(self) -> Dict[str, Dict[str, Any]]:
        """Load theme definitions"""
        return {
            "dark": {
                "name": "Dark Theme",
                "description": "Professional dark theme with blue accents",
                "colors": {
                    "bg": "#2d2d30",
                    "fg": "#ffffff",
                    "select_bg": "#0e639c",
                    "select_fg": "#ffffff",
                    "button_bg": "#3c3c3c",
                    "button_fg": "#ffffff",
                    "entry_bg": "#1e1e1e",
                    "entry_fg": "#ffffff",
                    "frame_bg": "#2d2d30",
                    "label_fg": "#ffffff",
                    "text_bg": "#1e1e1e",
                    "text_fg": "#000000",
                    "scrollbar_bg": "#3c3c3c",
                    "scrollbar_fg": "#0e639c",
                    "menu_bg": "#2d2d30",
                    "menu_fg": "#ffffff",
                    "menu_select_bg": "#0e639c",
                    "tree_bg": "#1e1e1e",
                    "tree_fg": "#ffffff",
                    "tree_select_bg": "#0e639c",
                    "border": "#555555",
                    "accent": "#0e639c",
                    "success": "#4caf50",
                    "warning": "#ff9800",
                    "error": "#f44336"
                }
            },
            "light": {
                "name": "Light Theme", 
                "description": "Clean light theme with blue accents",
                "colors": {
                    "bg": "#f0f0f0",
                    "fg": "#000000",
                    "select_bg": "#0078d4",
                    "select_fg": "#ffffff",
                    "button_bg": "#e1e1e1",
                    "button_fg": "#000000",
                    "entry_bg": "#ffffff",
                    "entry_fg": "#000000",
                    "frame_bg": "#f0f0f0",
                    "label_fg": "#000000",
                    "text_bg": "#000000",
                    "text_fg": "#000000",
                    "scrollbar_bg": "#e1e1e1",
                    "scrollbar_fg": "#0078d4",
                    "menu_bg": "#f0f0f0",
                    "menu_fg": "#000000",
                    "menu_select_bg": "#0078d4",
                    "tree_bg": "#ffffff",
                    "tree_fg": "#000000",
                    "tree_select_bg": "#0078d4",
                    "border": "#d0d0d0",
                    "accent": "#0078d4",
                    "success": "#228b22",
                    "warning": "#ff8c00",
                    "error": "#dc143c"
                }
            },
            "cyberpunk": {
                "name": "Cyberpunk Theme",
                "description": "Futuristic theme with neon green accents",
                "colors": {
                    "bg": "#0a0a0a",
                    "fg": "#00ff41",
                    "select_bg": "#003d1a",
                    "select_fg": "#00ff41",
                    "button_bg": "#1a1a1a",
                    "button_fg": "#00ff41",
                    "entry_bg": "#0d0d0d",
                    "entry_fg": "#00ff41",
                    "frame_bg": "#0a0a0a",
                    "label_fg": "#00ff41",
                    "text_bg": "#0d0d0d",
                    "text_fg": "#00ff41",
                    "scrollbar_bg": "#1a1a1a",
                    "scrollbar_fg": "#00ff41",
                    "menu_bg": "#0a0a0a",
                    "menu_fg": "#00ff41",
                    "menu_select_bg": "#003d1a",
                    "tree_bg": "#0d0d0d",
                    "tree_fg": "#00ff41",
                    "tree_select_bg": "#003d1a",
                    "border": "#333333",
                    "accent": "#00ff41",
                    "success": "#00ff41",
                    "warning": "#ffff00",
                    "error": "#ff0040"
                }
            }
        }
    
    def apply_theme(self, theme_name: str):
        """Apply a theme to the application"""
        if theme_name not in self.themes:
            print(f"Warning: Theme '{theme_name}' not found, using dark theme")
            theme_name = "dark"
        
        self.current_theme = theme_name
        theme = self.themes[theme_name]
        colors = theme["colors"]
        
        # Apply root window colors
        self.root.configure(bg=colors["bg"])
        
        # Configure TTK styles
        self._configure_ttk_styles(colors)
        
        # Configure standard tkinter colors
        self.root.option_add("*Background", colors["bg"])
        self.root.option_add("*Foreground", colors["fg"])
        self.root.option_add("*selectBackground", colors["select_bg"])
        self.root.option_add("*selectForeground", colors["select_fg"])
        
        # Save theme preference
        self._save_theme_settings()
    
    def _configure_ttk_styles(self, colors: Dict[str, str]):
        """Configure TTK styles for the theme"""
        style = ttk.Style()
        
        # Frame styles
        style.configure("TFrame", background=colors["frame_bg"])
        style.configure("TLabelFrame", background=colors["frame_bg"], 
                       foreground=colors["label_fg"], bordercolor=colors["border"])
        style.configure("TLabelFrame.Label", background=colors["frame_bg"], 
                       foreground=colors["label_fg"])
        
        # Label styles
        style.configure("TLabel", background=colors["frame_bg"], 
                       foreground=colors["label_fg"])
        style.configure("Heading.TLabel", background=colors["frame_bg"], 
                       foreground=colors["accent"], font=('TkDefaultFont', 10, 'bold'))
        
        # Button styles
        style.configure("TButton", 
                       background=colors["button_bg"],
                       foreground=colors["button_fg"],
                       bordercolor=colors["border"],
                       focuscolor=colors["accent"])
        style.map("TButton",
                 background=[('active', colors["select_bg"]),
                           ('pressed', colors["accent"])],
                 foreground=[('active', colors["select_fg"]),
                           ('pressed', colors["select_fg"])])
        
        # Entry styles
        style.configure("TEntry",
                       fieldbackground=colors["entry_bg"],
                       background=colors["entry_bg"],
                       foreground=colors["entry_fg"],
                       bordercolor=colors["border"],
                       insertcolor=colors["fg"])
        style.map("TEntry",
                 focuscolor=[('focus', colors["accent"])])
        
        # Combobox styles
        style.configure("TCombobox",
                       fieldbackground=colors["entry_bg"],
                       background=colors["button_bg"],
                       foreground=colors["entry_fg"],
                       bordercolor=colors["border"])
        style.map("TCombobox",
                 fieldbackground=[('readonly', colors["entry_bg"])],
                 selectbackground=[('readonly', colors["select_bg"])],
                 selectforeground=[('readonly', colors["select_fg"])])
        
        # Notebook styles
        style.configure("TNotebook", background=colors["frame_bg"], 
                       bordercolor=colors["border"])
        style.configure("TNotebook.Tab",
                       background=colors["button_bg"],
                       foreground=colors["button_fg"],
                       padding=[8, 4])
        style.map("TNotebook.Tab",
                 background=[('selected', colors["accent"]),
                           ('active', colors["select_bg"])],
                 foreground=[('selected', colors["select_fg"]),
                           ('active', colors["select_fg"])])
        
        # Treeview styles
        style.configure("Treeview",
                       background=colors["tree_bg"],
                       foreground=colors["tree_fg"],
                       fieldbackground=colors["tree_bg"],
                       bordercolor=colors["border"])
        style.configure("Treeview.Heading",
                       background=colors["button_bg"],
                       foreground=colors["button_fg"],
                       relief="flat")
        style.map("Treeview",
                 background=[('selected', colors["tree_select_bg"])],
                 foreground=[('selected', colors["select_fg"])])
        style.map("Treeview.Heading",
                 background=[('active', colors["select_bg"])],
                 foreground=[('active', colors["select_fg"])])
        
        # Scrollbar styles
        style.configure("TScrollbar",
                       background=colors["scrollbar_bg"],
                       troughcolor=colors["frame_bg"],
                       arrowcolor=colors["scrollbar_fg"],
                       bordercolor=colors["border"])
        style.map("TScrollbar",
                 background=[('active', colors["scrollbar_fg"]),
                           ('pressed', colors["accent"])])
        
        # Scale styles
        style.configure("TScale",
                       background=colors["frame_bg"],
                       troughcolor=colors["scrollbar_bg"],
                       bordercolor=colors["border"])
        style.map("TScale",
                 background=[('active', colors["accent"])])
        
        # Spinbox styles
        style.configure("TSpinbox",
                       fieldbackground=colors["entry_bg"],
                       background=colors["button_bg"],
                       foreground=colors["entry_fg"],
                       bordercolor=colors["border"],
                       insertcolor=colors["fg"])
        
        # Progressbar styles
        style.configure("TProgressbar",
                       background=colors["accent"],
                       troughcolor=colors["scrollbar_bg"],
                       bordercolor=colors["border"])
        
        # Separator styles
        style.configure("TSeparator", background=colors["border"])
        
        # Checkbutton and Radiobutton styles
        style.configure("TCheckbutton",
                       background=colors["frame_bg"],
                       foreground=colors["label_fg"],
                       focuscolor=colors["accent"])
        style.configure("TRadiobutton", 
                       background=colors["frame_bg"],
                       foreground=colors["label_fg"],
                       focuscolor=colors["accent"])
        
        # Menu styles (for context menus)
        style.configure("TMenubutton",
                       background=colors["button_bg"],
                       foreground=colors["button_fg"],
                       bordercolor=colors["border"])
    
    def get_current_theme(self) -> str:
        """Get the current theme name"""
        return self.current_theme
    
    def get_available_themes(self) -> Dict[str, str]:
        """Get available themes as {name: description}"""
        return {name: theme["name"] for name, theme in self.themes.items()}
    
    def get_theme_colors(self, theme_name: Optional[str] = None) -> Dict[str, str]:
        """Get colors for a specific theme (or current theme)"""
        theme_name = theme_name or self.current_theme
        if theme_name in self.themes:
            return self.themes[theme_name]["colors"].copy()
        return {}
    
    def _load_theme_settings(self):
        """Load theme settings from file"""
        try:
            if os.path.exists(self.settings_file):
                with open(self.settings_file, 'r') as f:
                    settings = json.load(f)
                    self.current_theme = settings.get("current_theme", "dark")
        except Exception as e:
            print(f"Warning: Could not load theme settings: {e}")
            self.current_theme = "dark"
    
    def _save_theme_settings(self):
        """Save theme settings to file"""
        try:
            # Ensure data directory exists
            os.makedirs(os.path.dirname(self.settings_file), exist_ok=True)
            
            settings = {
                "current_theme": self.current_theme,
                "version": "1.0"
            }
            
            with open(self.settings_file, 'w') as f:
                json.dump(settings, f, indent=2)
        except Exception as e:
            print(f"Warning: Could not save theme settings: {e}")
    
    def configure_widget_theme(self, widget, widget_type: str = "auto"):
        """Apply theme colors to a specific widget"""
        if widget_type == "auto":
            # Try to determine widget type
            widget_class = widget.winfo_class().lower()
            if "text" in widget_class:
                widget_type = "text"
            elif "listbox" in widget_class:
                widget_type = "listbox"
            elif "menu" in widget_class:
                widget_type = "menu"
            else:
                return  # Unknown widget type
        
        colors = self.get_theme_colors()
        
        try:
            if widget_type == "text":
                widget.configure(
                    bg=colors["text_bg"],
                    fg=colors["text_fg"],
                    insertbackground=colors["fg"],
                    selectbackground=colors["select_bg"],
                    selectforeground=colors["select_fg"]
                )
            elif widget_type == "listbox":
                widget.configure(
                    bg=colors["tree_bg"],
                    fg=colors["tree_fg"],
                    selectbackground=colors["tree_select_bg"],
                    selectforeground=colors["select_fg"]
                )
            elif widget_type == "menu":
                widget.configure(
                    bg=colors["menu_bg"],
                    fg=colors["menu_fg"],
                    activebackground=colors["menu_select_bg"],
                    activeforeground=colors["select_fg"],
                    selectcolor=colors["accent"]
                )
        except tk.TclError:
            # Widget doesn't support these options
            pass
