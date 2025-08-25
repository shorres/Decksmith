"""
Autocomplete widget for card name suggestions
"""

import tkinter as tk
from tkinter import ttk
from typing import List, Callable, Optional


class AutocompleteEntry(ttk.Frame):
    """Entry widget with autocomplete dropdown based on collection"""
    
    def __init__(self, parent, width=200, get_suggestions_func: Optional[Callable[[], List[str]]] = None):
        super().__init__(parent)
        
        self.get_suggestions_func = get_suggestions_func or (lambda: [])
        self.suggestions = []
        self.filtered_suggestions = []
        self.current_selection = -1
        
        self.create_widgets(width)
        self.update_suggestions()
    
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
        
        # Dropdown listbox (initially hidden)
        self.dropdown_frame = tk.Toplevel(self.winfo_toplevel())
        self.dropdown_frame.withdraw()  # Hide initially
        self.dropdown_frame.wm_overrideredirect(True)  # Remove window decorations
        self.dropdown_frame.configure(bg='white', relief='solid', bd=1)
        
        # Listbox for suggestions
        self.listbox = tk.Listbox(self.dropdown_frame, height=8, selectmode=tk.SINGLE)
        self.listbox.pack(fill=tk.BOTH, expand=True)
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
    
    def update_suggestions(self):
        """Update the list of available suggestions"""
        if self.get_suggestions_func:
            self.suggestions = sorted(self.get_suggestions_func())
    
    def filter_suggestions(self, query: str) -> List[str]:
        """Filter suggestions based on query"""
        if not query:
            return []
        
        query_lower = query.lower()
        
        # First, exact matches at the beginning
        exact_matches = [s for s in self.suggestions if s.lower().startswith(query_lower)]
        
        # Then, contains matches
        contains_matches = [s for s in self.suggestions 
                          if query_lower in s.lower() and not s.lower().startswith(query_lower)]
        
        # Combine and limit results
        results = exact_matches + contains_matches
        return results[:20]  # Limit to 20 suggestions
    
    def show_dropdown(self):
        """Show the dropdown with filtered suggestions"""
        if not self.filtered_suggestions:
            self.hide_dropdown()
            return
        
        # Update listbox
        self.listbox.delete(0, tk.END)
        for suggestion in self.filtered_suggestions:
            self.listbox.insert(tk.END, suggestion)
        
        # Position dropdown
        self.update_idletasks()  # Make sure geometry is updated
        
        entry_x = self.entry.winfo_rootx()
        entry_y = self.entry.winfo_rooty() + self.entry.winfo_height()
        entry_width = self.entry.winfo_width()
        
        self.dropdown_frame.geometry(f"{max(200, entry_width)}x160+{entry_x}+{entry_y}")
        self.dropdown_frame.deiconify()
        
        # Reset selection
        self.current_selection = -1
    
    def hide_dropdown(self):
        """Hide the dropdown"""
        self.dropdown_frame.withdraw()
        self.current_selection = -1
    
    def on_key_release(self, event):
        """Handle key release events"""
        if event.keysym in ['Up', 'Down', 'Return', 'Escape']:
            return
        
        query = self.get()
        self.filtered_suggestions = self.filter_suggestions(query)
        
        if len(query) >= 1:  # Start suggesting after 1 character
            self.show_dropdown()
        else:
            self.hide_dropdown()
    
    def on_click(self, event):
        """Handle entry click"""
        query = self.get()
        if len(query) >= 1:
            self.filtered_suggestions = self.filter_suggestions(query)
            self.show_dropdown()
    
    def on_focus_out(self, event):
        """Handle focus out - delay hiding to allow listbox clicks"""
        self.after(200, self.hide_dropdown)
    
    def on_up_arrow(self, event):
        """Handle up arrow key"""
        if self.dropdown_frame.winfo_viewable():
            if self.current_selection > 0:
                self.current_selection -= 1
            elif self.current_selection == -1:
                self.current_selection = len(self.filtered_suggestions) - 1
            else:
                self.current_selection = len(self.filtered_suggestions) - 1
            
            self.listbox.selection_clear(0, tk.END)
            if self.current_selection >= 0:
                self.listbox.selection_set(self.current_selection)
                self.listbox.see(self.current_selection)
            
            return 'break'  # Prevent default behavior
    
    def on_down_arrow(self, event):
        """Handle down arrow key"""
        if self.dropdown_frame.winfo_viewable():
            if self.current_selection < len(self.filtered_suggestions) - 1:
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
        if self.dropdown_frame.winfo_viewable() and self.current_selection >= 0:
            # Select the highlighted suggestion
            selected_suggestion = self.filtered_suggestions[self.current_selection]
            self.set(selected_suggestion)
            self.hide_dropdown()
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
    
    def on_listbox_double_click(self, event):
        """Handle listbox double-click"""
        selection = self.listbox.curselection()
        if selection:
            selected_suggestion = self.filtered_suggestions[selection[0]]
            self.set(selected_suggestion)
            self.hide_dropdown()
            
            # Call the custom return callback if set
            if hasattr(self, 'return_callback'):
                self.return_callback()
