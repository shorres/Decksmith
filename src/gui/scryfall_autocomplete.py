"""
Scryfall-powered autocomplete widget for card names
"""

import tkinter as tk
from tkinter import ttk
from typing import List, Callable, Optional
import threading
import time
from utils.scryfall_api import scryfall_api


class ScryfallAutocompleteEntry(ttk.Frame):
    """Entry widget with Scryfall API-powered autocomplete"""
    
    def __init__(self, parent, width=200, on_card_selected: Optional[Callable] = None):
        super().__init__(parent)
        
        self.on_card_selected = on_card_selected
        self.suggestions = []
        self.current_selection = -1
        self.search_thread = None
        self.last_query = ""
        self.search_delay = 300  # ms delay before searching
        self.search_timer = None
        
        self.create_widgets(width)
    
    def create_widgets(self, width):
        """Create the entry and dropdown widgets"""
        # Entry widget
        self.entry_var = tk.StringVar()
        self.entry = ttk.Entry(self, textvariable=self.entry_var, width=width)
        self.entry.pack(fill=tk.X)
        
        # Bind events
        self.entry.bind('<KeyRelease>', self.on_key_release)
        self.entry.bind('<Button-1>', self.on_click)
        self.entry.bind('<FocusOut>', self.on_focus_out)
        self.entry.bind('<Up>', self.on_up_arrow)
        self.entry.bind('<Down>', self.on_down_arrow)
        self.entry.bind('<Return>', self.on_return)
        self.entry.bind('<Escape>', self.on_escape)
        
        # Loading indicator
        self.loading_var = tk.StringVar()
        self.loading_label = ttk.Label(self, textvariable=self.loading_var, font=('TkDefaultFont', 8))
        self.loading_label.pack(anchor=tk.W)
        
        # Dropdown listbox (initially hidden)
        self.dropdown_frame = tk.Toplevel(self.winfo_toplevel())
        self.dropdown_frame.withdraw()  # Hide initially
        self.dropdown_frame.wm_overrideredirect(True)  # Remove window decorations
        self.dropdown_frame.configure(bg='white', relief='solid', bd=1)
        
        # Listbox for suggestions
        self.listbox = tk.Listbox(self.dropdown_frame, height=10, selectmode=tk.SINGLE)
        
        # Add scrollbar
        scrollbar = tk.Scrollbar(self.dropdown_frame, orient=tk.VERTICAL, command=self.listbox.yview)
        self.listbox.configure(yscrollcommand=scrollbar.set)
        
        # Pack listbox and scrollbar
        self.listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Bind listbox events
        self.listbox.bind('<Button-1>', self.on_listbox_select)
        self.listbox.bind('<Double-Button-1>', self.on_listbox_double_click)
    
    def get(self) -> str:
        """Get the current value"""
        return self.entry_var.get()
    
    def set(self, value: str):
        """Set the current value"""
        self.entry_var.set(value)
    
    def delete(self, first, last=None):
        """Delete characters from the entry"""
        if last is None:
            last = first + 1
        current = self.get()
        self.set(current[:first] + current[last:])
    
    def insert(self, index, string):
        """Insert string at index"""
        current = self.get()
        self.set(current[:index] + string + current[index:])
    
    def bind_return(self, callback):
        """Bind a callback to the Return key"""
        self.return_callback = callback
    
    def search_cards_async(self, query: str):
        """Search for cards asynchronously"""
        if self.search_thread and self.search_thread.is_alive():
            return  # Don't start new search if one is running
        
        def search_worker():
            try:
                # Set loading indicator
                self.after(0, lambda: self.loading_var.set("Searching..."))
                
                suggestions = scryfall_api.autocomplete_card_names(query)
                
                # Update suggestions on main thread
                self.after(0, lambda: self.update_suggestions_from_api(suggestions, query))
                
            except Exception as e:
                print(f"Error searching cards: {e}")
                self.after(0, lambda: self.loading_var.set(""))
        
        self.search_thread = threading.Thread(target=search_worker, daemon=True)
        self.search_thread.start()
    
    def update_suggestions_from_api(self, suggestions: List[str], original_query: str):
        """Update suggestions from API response"""
        self.loading_var.set("")
        
        # Only update if this is still the current query
        if original_query == self.last_query:
            self.suggestions = suggestions
            if suggestions:
                self.show_dropdown()
            else:
                self.hide_dropdown()
    
    def show_dropdown(self):
        """Show the dropdown with suggestions"""
        if not self.suggestions:
            self.hide_dropdown()
            return
        
        # Update listbox
        self.listbox.delete(0, tk.END)
        for suggestion in self.suggestions:
            self.listbox.insert(tk.END, suggestion)
        
        # Position dropdown
        self.update_idletasks()  # Make sure geometry is updated
        
        entry_x = self.entry.winfo_rootx()
        entry_y = self.entry.winfo_rooty() + self.entry.winfo_height()
        entry_width = self.entry.winfo_width()
        
        dropdown_width = max(300, entry_width)  # Minimum 300px for card names
        dropdown_height = min(250, len(self.suggestions) * 20 + 20)  # Adjust height based on suggestions
        
        self.dropdown_frame.geometry(f"{dropdown_width}x{dropdown_height}+{entry_x}+{entry_y}")
        self.dropdown_frame.deiconify()
        
        # Reset selection
        self.current_selection = -1
    
    def hide_dropdown(self):
        """Hide the dropdown"""
        self.dropdown_frame.withdraw()
        self.current_selection = -1
    
    def schedule_search(self, query: str):
        """Schedule a search with delay to avoid too many API calls"""
        # Cancel previous timer
        if self.search_timer:
            self.after_cancel(self.search_timer)
        
        # Only search if query is long enough
        if len(query) >= 2:
            self.search_timer = self.after(self.search_delay, lambda: self.search_cards_async(query))
        else:
            self.hide_dropdown()
            self.loading_var.set("")
    
    def on_key_release(self, event):
        """Handle key release events"""
        if event.keysym in ['Up', 'Down', 'Return', 'Escape']:
            return
        
        query = self.get().strip()
        self.last_query = query
        
        # Clear loading if query is too short
        if len(query) < 2:
            self.loading_var.set("")
            self.hide_dropdown()
            return
        
        # Schedule search with delay
        self.schedule_search(query)
    
    def on_click(self, event):
        """Handle entry click"""
        query = self.get().strip()
        if len(query) >= 2 and self.suggestions:
            self.show_dropdown()
    
    def on_focus_out(self, event):
        """Handle focus out - delay hiding to allow listbox clicks"""
        self.after(500, self.hide_dropdown)
    
    def on_up_arrow(self, event):
        """Handle up arrow key"""
        if self.dropdown_frame.winfo_viewable() and self.suggestions:
            if self.current_selection > 0:
                self.current_selection -= 1
            elif self.current_selection == -1:
                self.current_selection = len(self.suggestions) - 1
            else:
                self.current_selection = len(self.suggestions) - 1
            
            self.listbox.selection_clear(0, tk.END)
            if self.current_selection >= 0:
                self.listbox.selection_set(self.current_selection)
                self.listbox.see(self.current_selection)
            
            return 'break'  # Prevent default behavior
    
    def on_down_arrow(self, event):
        """Handle down arrow key"""
        if self.dropdown_frame.winfo_viewable() and self.suggestions:
            if self.current_selection < len(self.suggestions) - 1:
                self.current_selection += 1
            else:
                self.current_selection = 0
            
            self.listbox.selection_clear(0, tk.END)
            if self.current_selection >= 0:
                self.listbox.selection_set(self.current_selection)
                self.listbox.see(self.current_selection)
            
            return 'break'  # Prevent default behavior
    
    def on_return(self, event):
        """Handle Return key"""
        if self.dropdown_frame.winfo_viewable() and self.current_selection >= 0 and self.current_selection < len(self.suggestions):
            # Select the highlighted suggestion
            selected_suggestion = self.suggestions[self.current_selection]
            self.set(selected_suggestion)
            self.hide_dropdown()
            
            # Trigger card selection callback
            if self.on_card_selected:
                self.on_card_selected(selected_suggestion)
        else:
            # Call the custom return callback if set
            if hasattr(self, 'return_callback'):
                self.return_callback()
        
        return 'break'
    
    def on_escape(self, event):
        """Handle Escape key"""
        self.hide_dropdown()
        return 'break'
    
    def on_listbox_select(self, event):
        """Handle listbox selection"""
        selection = self.listbox.curselection()
        if selection:
            self.current_selection = selection[0]
            # Small delay to distinguish between click-to-highlight and click-to-select
            self.after(100, self._handle_selection)
    
    def _handle_selection(self):
        """Handle delayed selection after click"""
        if (self.current_selection >= 0 and 
            self.current_selection < len(self.suggestions) and
            self.dropdown_frame.winfo_viewable()):
            
            selected_suggestion = self.suggestions[self.current_selection]
            self.set(selected_suggestion)
            self.hide_dropdown()
            
            # Trigger card selection callback
            if self.on_card_selected:
                self.on_card_selected(selected_suggestion)
    
    def on_listbox_double_click(self, event):
        """Handle listbox double-click"""
        selection = self.listbox.curselection()
        if selection and selection[0] < len(self.suggestions):
            selected_suggestion = self.suggestions[selection[0]]
            self.set(selected_suggestion)
            self.hide_dropdown()
            
            # Trigger card selection callback
            if self.on_card_selected:
                self.on_card_selected(selected_suggestion)
            
            # Call the custom return callback if set
            if hasattr(self, 'return_callback'):
                self.return_callback()
