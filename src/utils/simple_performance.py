"""
Simplified performance optimizations for Decksmith GUI
Focused on essential optimizations after theme switcher removal
"""

import time
import threading
from typing import Dict, Any

class SimplePerformanceOptimizer:
    """Lightweight performance optimizations for GUI operations"""
    
    def __init__(self):
        self.last_tab_switch = 0
        self.tab_switch_debounce = 0.1  # 100ms debounce
        self.update_queued = {}  # Track queued updates by widget/tab
        
    def debounce_tab_switch(self, callback, tab_name: str) -> bool:
        """Debounce tab switching to prevent rapid updates"""
        current_time = time.time()
        if current_time - self.last_tab_switch < self.tab_switch_debounce:
            return False  # Skip this update
        
        self.last_tab_switch = current_time
        return True
    
    def queue_update(self, widget_id: str, callback, delay_ms: int = 50):
        """Queue an update with debouncing to prevent excessive refreshes"""
        # Cancel any existing queued update for this widget
        if widget_id in self.update_queued:
            self.update_queued[widget_id].cancel()
        
        # Schedule new update
        timer = threading.Timer(delay_ms / 1000.0, callback)
        self.update_queued[widget_id] = timer
        timer.start()
    
    def with_debounced_update(self, callback):
        """Execute callback with simple debouncing"""
        return callback()
    
    def clear_queued_updates(self):
        """Clear all queued updates (useful when switching tabs)"""
        for timer in self.update_queued.values():
            timer.cancel()
        self.update_queued.clear()

# Global optimizer instance
_simple_optimizer = None

def get_performance_optimizer() -> SimplePerformanceOptimizer:
    """Get global performance optimizer instance"""
    global _simple_optimizer
    if _simple_optimizer is None:
        _simple_optimizer = SimplePerformanceOptimizer()
    return _simple_optimizer

def debounce_update(delay_ms: int = 100):
    """Decorator to debounce frequent updates"""
    def decorator(update_func):
        def wrapper(self, *args, **kwargs):
            optimizer = get_performance_optimizer()
            widget_id = f"{self.__class__.__name__}_{update_func.__name__}"
            
            def delayed_update():
                update_func(self, *args, **kwargs)
            
            optimizer.queue_update(widget_id, delayed_update, delay_ms)
        return wrapper
    return decorator
