"""
Main window for the Magic: The Gathering Arena Deck Manager
"""

import tkinter as tk
from tkinter import ttk, messagebox
import sys
import os

from gui.collection_tab import CollectionTab
from gui.deck_tab import DeckTab
from gui.ai_recommendations_tab import AIRecommendationsTab
from gui.theme_manager import ThemeManager
from gui.settings_dialog import SettingsDialog

class MainWindow:
    """Main application window"""
    
    def __init__(self, root):
        self.root = root
        
        # Initialize theme manager first
        self.theme_manager = ThemeManager(root)
        self.settings_dialog = None
        
        self.setup_window()
        self.create_widgets()
    
    def setup_window(self):
        """Configure the main window"""
        self.root.title("Magic: The Gathering Arena Deck Manager")
        self.root.geometry("1200x800")
        self.root.minsize(800, 600)
        
        # Configure grid weights
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
    
    def create_widgets(self):
        """Create and arrange widgets"""
        # Create main menu
        self.create_menu()
        
        # Create main notebook for tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        
        # Add tabs
        self.collection_tab = CollectionTab(self.notebook)
        self.deck_tab = DeckTab(self.notebook, collection=self.collection_tab.collection)
        self.ai_tab = AIRecommendationsTab(
            self.notebook, 
            get_current_deck_func=lambda: self.deck_tab.current_deck,
            get_collection_func=lambda: self.collection_tab.collection,
            add_card_callback=self.deck_tab.add_card_from_ai
        )
        
        self.notebook.add(self.collection_tab.frame, text="Collection")
        self.notebook.add(self.deck_tab.frame, text="Decks")
        self.notebook.add(self.ai_tab.frame, text="AI Recommendations")
        
        # Bind tab selection event to update AI tab when selected
        self.notebook.bind("<<NotebookTabChanged>>", self.on_tab_changed)
        
        # Status bar
        self.status_bar = ttk.Label(self.root, text="Ready", relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.grid(row=1, column=0, sticky="ew", padx=5, pady=2)
    
    def on_tab_changed(self, event):
        """Handle tab change events"""
        selection = event.widget.select()
        tab_text = event.widget.tab(selection, "text")
        
        # Update AI tab when it's selected
        if tab_text == "AI Recommendations":
            self.ai_tab.on_tab_focus()
    
    def create_menu(self):
        """Create the main menu bar"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        
        # Collection menu
        collection_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Collection", menu=collection_menu)
        collection_menu.add_command(label="Import from CSV", command=self.import_collection)
        collection_menu.add_command(label="Export to CSV", command=self.export_collection)
        
        # Deck menu
        deck_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Deck", menu=deck_menu)
        deck_menu.add_command(label="New Deck", command=self.new_deck)
        deck_menu.add_command(label="Import from CSV", command=self.import_deck_csv)
        deck_menu.add_command(label="Import from Arena", command=self.import_deck_arena)
        deck_menu.add_command(label="Export to CSV", command=self.export_deck_csv)
        deck_menu.add_command(label="Export to Arena", command=self.export_deck_arena)
        
        # View menu with themes
        view_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="View", menu=view_menu)
        
        # Theme submenu
        theme_menu = tk.Menu(view_menu, tearoff=0)
        view_menu.add_cascade(label="Themes", menu=theme_menu)
        
        # Add theme options
        available_themes = self.theme_manager.get_available_themes()
        for theme_id, theme_name in available_themes.items():
            theme_menu.add_command(
                label=theme_name, 
                command=lambda t=theme_id: self.change_theme(t)
            )
        
        view_menu.add_separator()
        view_menu.add_command(label="Settings...", command=self.show_settings)
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About AI Features", command=self.show_ai_help)
        help_menu.add_command(label="About", command=self.show_about)
        
        # Apply theme to menus
        self.theme_manager.configure_widget_theme(menubar, "menu")
        self.theme_manager.configure_widget_theme(file_menu, "menu")
        self.theme_manager.configure_widget_theme(collection_menu, "menu")
        self.theme_manager.configure_widget_theme(deck_menu, "menu")
        self.theme_manager.configure_widget_theme(view_menu, "menu")
        self.theme_manager.configure_widget_theme(theme_menu, "menu")
        self.theme_manager.configure_widget_theme(help_menu, "menu")
    
    def import_collection(self):
        """Import collection from CSV"""
        self.collection_tab.import_collection()
        self.update_status("Collection import completed")
    
    def export_collection(self):
        """Export collection to CSV"""
        self.collection_tab.export_collection()
        self.update_status("Collection export completed")
    
    def new_deck(self):
        """Create a new deck"""
        self.deck_tab.new_deck()
        self.update_status("New deck created")
    
    def import_deck_csv(self):
        """Import deck from CSV"""
        self.deck_tab.import_deck_csv()
        self.update_status("Deck import from CSV completed")
    
    def import_deck_arena(self):
        """Import deck from Arena format"""
        self.deck_tab.import_deck_arena()
        self.update_status("Deck import from Arena completed")
    
    def export_deck_csv(self):
        """Export deck to CSV"""
        self.deck_tab.export_deck_csv()
        self.update_status("Deck export to CSV completed")
    
    def export_deck_arena(self):
        """Export deck to Arena format"""
        self.deck_tab.export_deck_arena()
        self.update_status("Deck export to Arena completed")
    
    def show_ai_help(self):
        """Show AI features help dialog"""
        messagebox.showinfo(
            "AI Features Help",
            "AI-Powered Card Recommendations\\n\\n"
            "The AI system analyzes your deck and provides intelligent card suggestions based on:\\n\\n"
            "🎯 Synergy Analysis: Cards that work well with your current deck\\n"
            "📊 Meta Popularity: Cards that are successful in the current format\\n"
            "🏗️ Archetype Fitting: Cards that match your deck's strategy\\n"
            "📈 Mana Curve Optimization: Cards that improve your deck's balance\\n\\n"
            "Features:\\n"
            "• Deck archetype identification\\n"
            "• Personalized card recommendations\\n"
            "• Deck improvement suggestions\\n"
            "• Similar deck analysis\\n"
            "• Confidence scoring for all suggestions\\n\\n"
            "Click 'Analyze Current Deck' to get started!"
        )
    
    def show_about(self):
        """Show about dialog"""
        messagebox.showinfo(
            "About",
            "Magic: The Gathering Arena Deck Manager\\n\\n"
            "A comprehensive tool for managing your MTG Arena collection and decks.\\n\\n"
            "Features:\\n"
            "• Collection management with filtering and statistics\\n"
            "• Advanced deck building tools\\n"
            "• CSV import/export capabilities\\n"
            "• Arena format support\\n"
            "• AI-powered card recommendations\\n"
            "• Deck archetype analysis\\n"
            "• Meta-based suggestions\\n"
            "• Synergy detection\\n\\n"
            "Built with Python and powered by AI for the best deck building experience!"
        )
    
    def change_theme(self, theme_name: str):
        """Change the application theme"""
        self.theme_manager.apply_theme(theme_name)
        self.update_status(f"Theme changed to {self.theme_manager.themes[theme_name]['name']}")
    
    def show_settings(self):
        """Show settings dialog"""
        if not self.settings_dialog:
            self.settings_dialog = SettingsDialog(
                self.root, 
                self.theme_manager, 
                on_settings_changed=self.on_settings_changed
            )
        self.settings_dialog.show()
    
    def on_settings_changed(self):
        """Called when settings are changed"""
        # Refresh UI elements that might be affected by settings changes
        self.update_status("Settings updated")
    
    def update_status(self, message):
        """Update the status bar"""
        print(f"Status: {message}")  # For now print to console
