"""
Performance optimizations for Magic Tool GUI
Reduces tab switching delays and improves overall responsiveness
"""

import tkinter as tk
from typing import Optional, Dict, Any
import threading
import time

class PerformanceOptimizer:
    """Handles performance optimizations for GUI operations"""
    
    def __init__(self):
        self.last_tab_switch = 0
        self.tab_switch_debounce = 0.1  # 100ms debounce
        self.update_queued = {}  # Track queued updates by widget/tab
        self.cache_enabled = True
        
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
    
    def clear_queued_updates(self):
        """Clear all queued updates (useful when switching tabs)"""
        for timer in self.update_queued.values():
            timer.cancel()
        self.update_queued.clear()

class LazyTreeView:
    """Optimized tree view that only updates when necessary"""
    
    def __init__(self, tree_widget):
        self.tree = tree_widget
        self._cached_data = None
        self._data_hash = None
        self.visible = True
        
    def update_data(self, data, force_refresh=False):
        """Update tree data only if it has changed"""
        new_hash = hash(str(data)) if data else None
        
        if not force_refresh and new_hash == self._data_hash and self.visible:
            return  # No changes, skip update
        
        self._data_hash = new_hash
        self._cached_data = data
        
        if self.visible:
            self._refresh_display()
    
    def _refresh_display(self):
        """Refresh the tree display efficiently"""
        if not self._cached_data:
            return
            
        # Store current selection
        selected_items = self.tree.selection()
        selected_values = []
        for item in selected_items:
            try:
                selected_values.append(self.tree.item(item)['values'])
            except:
                pass
        
        # Clear and repopulate (more efficient than individual updates)
        self.tree.delete(*self.tree.get_children())
        
        # Add new data
        for values in self._cached_data:
            item = self.tree.insert('', 'end', values=values)
            
            # Restore selection if it matches
            if values in selected_values:
                self.tree.selection_add(item)
    
    def set_visible(self, visible: bool):
        """Set visibility state and refresh if becoming visible"""
        was_visible = self.visible
        self.visible = visible
        
        if visible and not was_visible and self._cached_data:
            self._refresh_display()

class CachedStatistics:
    """Cache statistics to avoid recalculation on every update"""
    
    def __init__(self):
        self._cache = {}
        self._cache_timeout = 1.0  # 1 second cache timeout
        
    def get_stats(self, data_source, calculator_func, cache_key: str):
        """Get statistics with caching"""
        current_time = time.time()
        
        # Check if we have valid cached data
        if cache_key in self._cache:
            cached_data, timestamp = self._cache[cache_key]
            if current_time - timestamp < self._cache_timeout:
                return cached_data
        
        # Calculate new statistics
        stats = calculator_func(data_source)
        self._cache[cache_key] = (stats, current_time)
        return stats
    
    def invalidate_cache(self, cache_key: Optional[str] = None):
        """Invalidate cache for specific key or all keys"""
        if cache_key:
            self._cache.pop(cache_key, None)
        else:
            self._cache.clear()

# Global optimizer instances
_performance_optimizer = None
_stats_cache = None

def get_performance_optimizer() -> PerformanceOptimizer:
    """Get global performance optimizer instance"""
    global _performance_optimizer
    if _performance_optimizer is None:
        _performance_optimizer = PerformanceOptimizer()
    return _performance_optimizer

def get_stats_cache() -> CachedStatistics:
    """Get global statistics cache instance"""
    global _stats_cache
    if _stats_cache is None:
        _stats_cache = CachedStatistics()
    return _stats_cache

def optimize_tree_update(tree_widget, data_generator):
    """Decorator to optimize tree updates"""
    def decorator(update_func):
        def wrapper(*args, **kwargs):
            # Generate new data
            new_data = data_generator()
            
            # Create lazy tree view if not exists
            if not hasattr(tree_widget, '_lazy_view'):
                tree_widget._lazy_view = LazyTreeView(tree_widget)
            
            # Update with lazy loading
            tree_widget._lazy_view.update_data(new_data)
            
            # Call original function for any additional processing
            return update_func(*args, **kwargs)
        return wrapper
    return decorator

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

def cached_property(cache_key: str, timeout: float = 1.0):
    """Decorator for cached property calculations"""
    def decorator(calc_func):
        def wrapper(self, *args, **kwargs):
            stats_cache = get_stats_cache()
            full_cache_key = f"{self.__class__.__name__}_{cache_key}"
            
            def calculator(data):
                return calc_func(self, *args, **kwargs)
            
            return stats_cache.get_stats(self, calculator, full_cache_key)
        return wrapper
    return decorator
