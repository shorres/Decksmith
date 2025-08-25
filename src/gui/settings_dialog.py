"""
Settings Dialog for MTG Arena Deck Manager
Provides theme selection and other application preferences
"""

import tkinter as tk
from tkinter import ttk
from typing import Dict, Any, Callable, Optional

class SettingsDialog:
    """Settings dialog for application preferences"""
    
    def __init__(self, parent: tk.Tk, theme_manager, on_settings_changed: Optional[Callable] = None):
        self.parent = parent
        self.theme_manager = theme_manager
        self.on_settings_changed = on_settings_changed
        
        self.dialog = None  # type: Optional[tk.Toplevel]
        self.theme_var = tk.StringVar(value=theme_manager.get_current_theme())
        self.font_size_var = tk.IntVar(value=9)
        self.font_family_var = tk.StringVar(value="TkDefaultFont")
        
        # Settings storage
        self.settings = {
            "auto_save": tk.BooleanVar(value=True),
            "show_tooltips": tk.BooleanVar(value=True),
            "check_updates": tk.BooleanVar(value=True),
            "use_scryfall": tk.BooleanVar(value=True),
            "cache_images": tk.BooleanVar(value=True)
        }
    
    def show(self):
        """Show the settings dialog"""
        if self.dialog and self.dialog.winfo_exists():
            self.dialog.focus()
            return
        
        self.dialog = tk.Toplevel(self.parent)
        self.dialog.title("Settings")
        self.dialog.geometry("500x400")
        self.dialog.resizable(False, False)
        
        # Make modal
        self.dialog.transient(self.parent)
        self.dialog.grab_set()
        
        # Center on parent
        self._center_dialog()
        
        # Create UI
        self._create_ui()
        
        # Apply current theme
        self._apply_current_theme()
    
    def _center_dialog(self):
        """Center dialog on parent window"""
        if self.dialog is None:
            return
            
        self.dialog.update_idletasks()
        
        # Get parent position and size
        parent_x = self.parent.winfo_x()
        parent_y = self.parent.winfo_y()
        parent_width = self.parent.winfo_width()
        parent_height = self.parent.winfo_height()
        
        # Calculate center position
        dialog_width = 500
        dialog_height = 400
        x = parent_x + (parent_width - dialog_width) // 2
        y = parent_y + (parent_height - dialog_height) // 2
        
        self.dialog.geometry(f"{dialog_width}x{dialog_height}+{x}+{y}")
    
    def _create_ui(self):
        """Create the settings dialog UI"""
        # Main frame
        main_frame = ttk.Frame(self.dialog)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create notebook for different settings categories
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Theme settings tab
        self._create_theme_tab(notebook)
        
        # Font settings tab
        self._create_font_tab(notebook)
        
        # Behavior settings tab
        self._create_behavior_tab(notebook)
        
        # Button frame
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(5, 0))
        
        # Buttons
        ttk.Button(button_frame, text="Apply", command=self._apply_settings).pack(side=tk.RIGHT, padx=(5, 0))
        ttk.Button(button_frame, text="OK", command=self._ok_clicked).pack(side=tk.RIGHT, padx=(5, 0))
        ttk.Button(button_frame, text="Cancel", command=self._cancel_clicked).pack(side=tk.RIGHT, padx=(5, 0))
        ttk.Button(button_frame, text="Reset to Defaults", command=self._reset_defaults).pack(side=tk.LEFT)
    
    def _create_theme_tab(self, notebook):
        """Create theme settings tab"""
        theme_frame = ttk.Frame(notebook)
        notebook.add(theme_frame, text="🎨 Themes")
        
        # Theme selection
        theme_group = ttk.LabelFrame(theme_frame, text="Color Theme")
        theme_group.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(theme_group, text="Select theme:").pack(anchor=tk.W, padx=10, pady=(10, 5))
        
        # Theme radiobuttons with previews
        available_themes = self.theme_manager.get_available_themes()
        
        for theme_id, theme_name in available_themes.items():
            theme_colors = self.theme_manager.get_theme_colors(theme_id)
            
            # Frame for each theme option
            theme_option_frame = ttk.Frame(theme_group)
            theme_option_frame.pack(fill=tk.X, padx=10, pady=2)
            
            # Radiobutton
            radio = ttk.Radiobutton(
                theme_option_frame, 
                text=theme_name, 
                variable=self.theme_var, 
                value=theme_id,
                command=self._preview_theme
            )
            radio.pack(side=tk.LEFT)
            
            # Color preview
            preview_frame = tk.Frame(theme_option_frame, width=100, height=20)
            preview_frame.pack(side=tk.RIGHT, padx=(10, 0))
            preview_frame.pack_propagate(False)
            
            # Create color squares
            colors_to_show = ["bg", "fg", "accent", "select_bg"]
            square_width = 25
            for i, color_key in enumerate(colors_to_show):
                color = theme_colors.get(color_key, "#ffffff")
                color_square = tk.Frame(
                    preview_frame, 
                    bg=color, 
                    width=square_width, 
                    height=20,
                    relief=tk.SOLID,
                    borderwidth=1
                )
                color_square.place(x=i * square_width, y=0)
        
        # Theme description
        self.theme_description = ttk.Label(theme_group, text="", wraplength=400)
        self.theme_description.pack(fill=tk.X, padx=10, pady=(5, 10))
        
        self._update_theme_description()
    
    def _create_font_tab(self, notebook):
        """Create font settings tab"""
        font_frame = ttk.Frame(notebook)
        notebook.add(font_frame, text="🔤 Fonts")
        
        # Font family
        family_group = ttk.LabelFrame(font_frame, text="Font Family")
        family_group.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(family_group, text="Font family:").pack(anchor=tk.W, padx=10, pady=(10, 5))
        
        font_combo = ttk.Combobox(family_group, textvariable=self.font_family_var, width=30)
        font_combo['values'] = ('TkDefaultFont', 'Arial', 'Helvetica', 'Consolas', 'Courier New', 'Times New Roman')
        font_combo.pack(padx=10, pady=(0, 10))
        
        # Font size
        size_group = ttk.LabelFrame(font_frame, text="Font Size")
        size_group.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(size_group, text="Font size:").pack(anchor=tk.W, padx=10, pady=(10, 5))
        
        size_frame = ttk.Frame(size_group)
        size_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        size_scale = ttk.Scale(size_frame, from_=8, to=16, orient=tk.HORIZONTAL, 
                              variable=self.font_size_var, length=200)
        size_scale.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        self.size_label = ttk.Label(size_frame, text=f"{self.font_size_var.get()}pt")
        self.size_label.pack(side=tk.RIGHT, padx=(10, 0))
        
        # Update label when scale changes
        def update_size_label(*args):
            self.size_label.config(text=f"{int(self.font_size_var.get())}pt")
        
        self.font_size_var.trace('w', update_size_label)
        
        # Font preview
        preview_group = ttk.LabelFrame(font_frame, text="Preview")
        preview_group.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.font_preview = tk.Text(preview_group, height=4, wrap=tk.WORD)
        self.font_preview.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        self.font_preview.insert(1.0, "This is a preview of the selected font.\nAaBbCc 123456 !@#$%^")
        self.font_preview.config(state=tk.DISABLED)
    
    def _create_behavior_tab(self, notebook):
        """Create behavior settings tab"""
        behavior_frame = ttk.Frame(notebook)
        notebook.add(behavior_frame, text="⚙️ Behavior")
        
        # General behavior
        general_group = ttk.LabelFrame(behavior_frame, text="General")
        general_group.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Checkbutton(general_group, text="Auto-save changes", 
                       variable=self.settings["auto_save"]).pack(anchor=tk.W, padx=10, pady=5)
        
        ttk.Checkbutton(general_group, text="Show tooltips", 
                       variable=self.settings["show_tooltips"]).pack(anchor=tk.W, padx=10, pady=5)
        
        ttk.Checkbutton(general_group, text="Check for updates on startup", 
                       variable=self.settings["check_updates"]).pack(anchor=tk.W, padx=10, pady=5)
        
        # Data sources
        data_group = ttk.LabelFrame(behavior_frame, text="Data Sources")
        data_group.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Checkbutton(data_group, text="Use Scryfall API for enhanced card data", 
                       variable=self.settings["use_scryfall"]).pack(anchor=tk.W, padx=10, pady=5)
        
        ttk.Checkbutton(data_group, text="Cache card images locally", 
                       variable=self.settings["cache_images"]).pack(anchor=tk.W, padx=10, pady=5)
        
        # Performance
        perf_group = ttk.LabelFrame(behavior_frame, text="Performance")
        perf_group.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(perf_group, text="These settings affect application performance:").pack(anchor=tk.W, padx=10, pady=(10, 5))
        
        info_text = tk.Text(perf_group, height=4, wrap=tk.WORD)
        info_text.pack(fill=tk.X, padx=10, pady=(0, 10))
        info_text.insert(1.0, 
            "• Scryfall API provides richer card data but requires internet\n"
            "• Image caching improves performance but uses disk space\n"
            "• Auto-save prevents data loss but may slow down large operations\n"
            "• Tooltips provide helpful information but may feel cluttered"
        )
        info_text.config(state=tk.DISABLED)
    
    def _preview_theme(self):
        """Preview the selected theme"""
        selected_theme = self.theme_var.get()
        self.theme_manager.apply_theme(selected_theme)
        self._apply_current_theme()
        self._update_theme_description()
    
    def _update_theme_description(self):
        """Update theme description"""
        current_theme = self.theme_var.get()
        if current_theme in self.theme_manager.themes:
            description = self.theme_manager.themes[current_theme]["description"]
            self.theme_description.config(text=description)
    
    def _apply_current_theme(self):
        """Apply current theme to dialog"""
        if self.dialog is None:
            return
            
        colors = self.theme_manager.get_theme_colors()
        
        # Apply to dialog
        self.dialog.configure(bg=colors["bg"])
        
        # Apply to text widgets
        if hasattr(self, 'font_preview'):
            self.theme_manager.configure_widget_theme(self.font_preview, "text")
    
    def _apply_settings(self):
        """Apply current settings"""
        # Apply theme
        self.theme_manager.apply_theme(self.theme_var.get())
        
        # Notify of settings change
        if self.on_settings_changed:
            self.on_settings_changed()
        
        self._apply_current_theme()
    
    def _ok_clicked(self):
        """Handle OK button click"""
        self._apply_settings()
        if self.dialog:
            self.dialog.destroy()
    
    def _cancel_clicked(self):
        """Handle Cancel button click"""
        # Restore original theme
        original_theme = self.theme_manager.get_current_theme()
        self.theme_var.set(original_theme)
        self.theme_manager.apply_theme(original_theme)
        
        if self.dialog:
            self.dialog.destroy()
    
    def _reset_defaults(self):
        """Reset all settings to defaults"""
        self.theme_var.set("dark")
        self.font_size_var.set(9)
        self.font_family_var.set("TkDefaultFont")
        
        for setting in self.settings.values():
            if isinstance(setting, tk.BooleanVar):
                setting.set(True)
        
        # Apply defaults
        self._preview_theme()
