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
    # Update parent to get current position and size
    parent_window.update_idletasks()
    
    # Get parent window position and size
    parent_x = parent_window.winfo_x()
    parent_y = parent_window.winfo_y()
    parent_width = parent_window.winfo_width()
    parent_height = parent_window.winfo_height()
    
    # Update child to get its size if not specified
    child_window.update_idletasks()
    child_width = width or child_window.winfo_width()
    child_height = height or child_window.winfo_height()
    
    # Calculate center position
    x = parent_x + (parent_width // 2) - (child_width // 2)
    y = parent_y + (parent_height // 2) - (child_height // 2)
    
    # Make sure the window doesn't go off screen
    screen_width = child_window.winfo_screenwidth()
    screen_height = child_window.winfo_screenheight()
    
    x = max(0, min(x, screen_width - child_width))
    y = max(0, min(y, screen_height - child_height))
    
    # Set the window geometry
    if width and height:
        child_window.geometry(f"{width}x{height}+{x}+{y}")
    else:
        child_window.geometry(f"+{x}+{y}")


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
    while current:
        if hasattr(current, 'master') and current.master:
            current = current.master
        elif hasattr(current, 'parent') and current.parent:
            current = current.parent
        else:
            # Check if this looks like a main window
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
