"""
Window utility functions for centering dialogs and managing window positions
"""

import tkinter as tk


def center_window_on_parent(child_window, parent_window, width=None, height=None):
    """
    Center a child window on its parent window
    
    Args:
        child_window: The window to center
        parent_window: The parent window to center on
        width: Optional width for the child window
        height: Optional height for the child window
    """
    try:
        # Validate that parent_window is a tkinter widget with positioning methods
        if not hasattr(parent_window, 'winfo_x'):
            center_window_on_screen(child_window, width, height)
            return
            
        # Update both windows to get current position and size
        parent_window.update_idletasks()
        child_window.update_idletasks()
        
        # Get parent window position and size
        parent_x = parent_window.winfo_x()
        parent_y = parent_window.winfo_y()
        parent_width = parent_window.winfo_width()
        parent_height = parent_window.winfo_height()
        
        # Get child window dimensions
        child_width = width or child_window.winfo_reqwidth()
        child_height = height or child_window.winfo_reqheight()
        
        # If requested dimensions are 0 or very small, use reasonable defaults
        if child_width < 100:
            child_width = width or 400
        if child_height < 50:
            child_height = height or 300
        
        # Calculate center position relative to parent
        x = parent_x + (parent_width // 2) - (child_width // 2)
        y = parent_y + (parent_height // 2) - (child_height // 2)
        
        # Make sure the window doesn't go off screen
        screen_width = child_window.winfo_screenwidth()
        screen_height = child_window.winfo_screenheight()
        
        # Ensure window stays on screen
        x = max(10, min(x, screen_width - child_width - 10))
        y = max(10, min(y, screen_height - child_height - 50))  # Leave room for taskbar
        
        # Set the window geometry
        if width and height:
            child_window.geometry(f"{width}x{height}+{x}+{y}")
        else:
            child_window.geometry(f"{child_width}x{child_height}+{x}+{y}")
            
    except (tk.TclError, AttributeError):
        # Fallback to screen centering if parent centering fails
        center_window_on_screen(child_window, width, height)


def center_window_on_screen(window, width=None, height=None):
    """
    Center a window on the screen (fallback for when parent isn't available)
    
    Args:
        window: The window to center
        width: Optional width for the window
        height: Optional height for the window
    """
    window.update_idletasks()
    
    # Get screen dimensions
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    
    # Get window dimensions
    window_width = width or window.winfo_width()
    window_height = height or window.winfo_height()
    
    # Calculate center position
    x = (screen_width // 2) - (window_width // 2)
    y = (screen_height // 2) - (window_height // 2)
    
    # Set the window geometry
    if width and height:
        window.geometry(f"{width}x{height}+{x}+{y}")
    else:
        window.geometry(f"+{x}+{y}")


def get_main_window(widget):
    """
    Find the main application window from any widget
    
    Args:
        widget: Any tkinter widget
        
    Returns:
        The main application window or None if not found
    """
    current = widget
    root_window = None
    
    # First try to get the root window using tkinter's built-in method
    try:
        if hasattr(widget, 'winfo_toplevel'):
            toplevel = widget.winfo_toplevel()
            # Check if this is the root window (not a Toplevel)
            if not hasattr(toplevel, 'master') or toplevel.master is None:
                root_window = toplevel
        
        if hasattr(widget, '_root') and widget._root:
            root_window = widget._root
    except tk.TclError:
        pass
    
    # If we found a root window, return it
    if root_window:
        return root_window
    
    # Fallback: traverse up the hierarchy manually
    while current:
        if hasattr(current, 'master') and current.master:
            current = current.master
        elif hasattr(current, 'parent') and current.parent:
            current = current.parent
        else:
            # Check if this looks like a main window
            if hasattr(current, 'winfo_class'):
                try:
                    if current.winfo_class() == 'Tk':  # This is the root Tk window
                        return current
                except tk.TclError:
                    pass
            
            # Fallback check
            if hasattr(current, 'title') and not hasattr(current, 'master'):
                return current
            break
    
    return None


def ensure_window_visible(window):
    """
    Ensure a window is visible on screen and not minimized
    
    Args:
        window: The window to make visible
    """
    try:
        window.deiconify()  # Restore if minimized
        window.lift()       # Bring to front
        window.focus_force()  # Give focus
    except tk.TclError:
        pass
