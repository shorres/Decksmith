"""
Sun Valley Theme Manager for MTG Arena Deck Manager
"""

import tkinter as tk
from tkinter import ttk
import sv_ttk
from typing import Optional

class SunValleyThemeManager:
    """Manages Sun Valley theme application and customization"""
    
    def __init__(self, root: tk.Tk):
        self.root = root
        self.current_theme = "dark"  # Start with dark theme
        self.theme_initialized = False
        
        # Apply the initial theme
        self.apply_theme()
    
    def apply_theme(self, theme_name: Optional[str] = None):
        """Apply Sun Valley theme"""
        if theme_name:
            self.current_theme = theme_name
        
        try:
            # Apply Sun Valley theme
            if self.current_theme == "dark":
                sv_ttk.set_theme("dark")
            else:
                sv_ttk.set_theme("light")
            
            # Apply custom styling for MTG-specific elements
            self._apply_custom_styles()
            
            self.theme_initialized = True
            print(f"✓ Applied Sun Valley {self.current_theme} theme")
            
        except Exception as e:
            print(f"Error applying Sun Valley theme: {e}")
            # Fallback to default theme
            self._apply_fallback_theme()
    
    def _apply_custom_styles(self):
        """Apply custom styles for MTG-specific elements"""
        style = ttk.Style()
        
        # Custom styles for card elements
        if self.current_theme == "dark":
            # Dark theme customizations
            
            # Header styles for deck info
            style.configure("Header.TLabel", 
                          font=('Segoe UI', 12, 'bold'),
                          foreground='#ffffff')
            
            # Card name styles
            style.configure("CardName.TLabel",
                          font=('Segoe UI', 11, 'bold'),
                          foreground='#e3e3e3')
            
            # Mana cost styles
            style.configure("ManaCost.TLabel",
                          font=('Consolas', 10),
                          foreground='#ffdd44')
            
            # Rarity styles
            style.configure("Common.TLabel", foreground='#c0c0c0')
            style.configure("Uncommon.TLabel", foreground='#1e90ff')
            style.configure("Rare.TLabel", foreground='#ffd700')
            style.configure("Mythic.TLabel", foreground='#ff8c00')
            
            # Collection stats
            style.configure("Stats.TLabel",
                          font=('Segoe UI', 9),
                          foreground='#b0b0b0')
            
            # Import progress elements
            style.configure("Progress.TLabel",
                          font=('Segoe UI', 10, 'bold'),
                          foreground='#4CAF50')
            
            # AI recommendation elements
            style.configure("Confidence.TLabel",
                          font=('Segoe UI', 9, 'bold'),
                          foreground='#2196F3')
            
        else:
            # Light theme customizations
            
            # Header styles for deck info
            style.configure("Header.TLabel", 
                          font=('Segoe UI', 12, 'bold'),
                          foreground='#2c2c2c')
            
            # Card name styles
            style.configure("CardName.TLabel",
                          font=('Segoe UI', 11, 'bold'),
                          foreground='#1a1a1a')
            
            # Mana cost styles
            style.configure("ManaCost.TLabel",
                          font=('Consolas', 10),
                          foreground='#b8860b')
            
            # Rarity styles
            style.configure("Common.TLabel", foreground='#666666')
            style.configure("Uncommon.TLabel", foreground='#1565c0')
            style.configure("Rare.TLabel", foreground='#f57c00')
            style.configure("Mythic.TLabel", foreground='#d32f2f')
            
            # Collection stats
            style.configure("Stats.TLabel",
                          font=('Segoe UI', 9),
                          foreground='#555555')
            
            # Import progress elements
            style.configure("Progress.TLabel",
                          font=('Segoe UI', 10, 'bold'),
                          foreground='#2e7d32')
            
            # AI recommendation elements
            style.configure("Confidence.TLabel",
                          font=('Segoe UI', 9, 'bold'),
                          foreground='#1976d2')
        
        # Common styles for both themes
        
        # Treeview enhancements
        style.configure("Treeview",
                       rowheight=25,
                       font=('Segoe UI', 9))
        
        style.configure("Treeview.Heading",
                       font=('Segoe UI', 9, 'bold'))
        
        # Button enhancements
        style.configure("Action.TButton",
                       font=('Segoe UI', 9, 'bold'))
        
        # Progress bar styling
        style.configure("Import.Horizontal.TProgressbar",
                       troughcolor='#404040' if self.current_theme == "dark" else '#e0e0e0',
                       background='#4CAF50',
                       borderwidth=0,
                       lightcolor='#4CAF50',
                       darkcolor='#2e7d32')
    
    def _apply_fallback_theme(self):
        """Apply fallback theme if Sun Valley fails"""
        try:
            style = ttk.Style()
            
            if self.current_theme == "dark":
                # Simple dark theme fallback
                self.root.configure(bg='#2d2d30')
                style.theme_use('alt')
                
                # Configure dark colors
                style.configure("TLabel", background='#2d2d30', foreground='#ffffff')
                style.configure("TFrame", background='#2d2d30')
                style.configure("TLabelFrame", background='#2d2d30', foreground='#ffffff')
                style.configure("TButton", background='#404040', foreground='#ffffff')
                style.configure("TEntry", fieldbackground='#404040', foreground='#ffffff')
                style.configure("Treeview", background='#3d3d40', foreground='#ffffff', 
                              fieldbackground='#3d3d40')
                
            print("✓ Applied fallback theme")
        except Exception as e:
            print(f"Error applying fallback theme: {e}")
    
    def toggle_theme(self):
        """Toggle between light and dark themes"""
        new_theme = "light" if self.current_theme == "dark" else "dark"
        self.apply_theme(new_theme)
        return new_theme
    
    def get_current_theme(self) -> str:
        """Get the current theme name"""
        return self.current_theme
    
    def configure_widget_theme(self, widget, widget_type: str = "default"):
        """Apply theme-specific configuration to a widget"""
        if not self.theme_initialized:
            return
        
        try:
            if widget_type == "header":
                widget.configure(style="Header.TLabel")
            elif widget_type == "card_name":
                widget.configure(style="CardName.TLabel")
            elif widget_type == "mana_cost":
                widget.configure(style="ManaCost.TLabel")
            elif widget_type == "stats":
                widget.configure(style="Stats.TLabel")
            elif widget_type == "progress":
                widget.configure(style="Progress.TLabel")
            elif widget_type == "confidence":
                widget.configure(style="Confidence.TLabel")
            elif widget_type == "action_button":
                widget.configure(style="Action.TButton")
            elif widget_type == "rarity":
                # This will be set dynamically based on rarity
                pass
                
        except Exception as e:
            print(f"Error configuring widget theme: {e}")
    
    def get_rarity_style(self, rarity: str) -> str:
        """Get the appropriate style for a card rarity"""
        rarity_lower = rarity.lower()
        if rarity_lower in ['common', 'c']:
            return "Common.TLabel"
        elif rarity_lower in ['uncommon', 'u']:
            return "Uncommon.TLabel"
        elif rarity_lower in ['rare', 'r']:
            return "Rare.TLabel"
        elif rarity_lower in ['mythic', 'mythic rare', 'm']:
            return "Mythic.TLabel"
        else:
            return "TLabel"  # Default style
    
    def apply_treeview_tags(self, treeview: ttk.Treeview):
        """Apply theme-appropriate tags to treeview"""
        if self.current_theme == "dark":
            # Dark theme treeview tags
            treeview.tag_configure('owned', background='#1b5e20', foreground='#a5d6a7')
            treeview.tag_configure('craftable', background='#3e2723', foreground='#ffcc02')
            treeview.tag_configure('missing', background='#b71c1c', foreground='#ffcdd2')
            treeview.tag_configure('common', foreground='#c0c0c0')
            treeview.tag_configure('uncommon', foreground='#1e90ff')
            treeview.tag_configure('rare', foreground='#ffd700')
            treeview.tag_configure('mythic', foreground='#ff8c00')
        else:
            # Light theme treeview tags
            treeview.tag_configure('owned', background='#e8f5e8', foreground='#2e7d32')
            treeview.tag_configure('craftable', background='#fff3e0', foreground='#ef6c00')
            treeview.tag_configure('missing', background='#ffebee', foreground='#c62828')
            treeview.tag_configure('common', foreground='#666666')
            treeview.tag_configure('uncommon', foreground='#1565c0')
            treeview.tag_configure('rare', foreground='#f57c00')
            treeview.tag_configure('mythic', foreground='#d32f2f')

# Global theme manager instance
theme_manager: Optional[SunValleyThemeManager] = None

def initialize_theme(root: tk.Tk) -> SunValleyThemeManager:
    """Initialize the global theme manager"""
    global theme_manager
    theme_manager = SunValleyThemeManager(root)
    return theme_manager

def get_theme_manager() -> Optional[SunValleyThemeManager]:
    """Get the global theme manager instance"""
    return theme_manager
