"""
Persistent cache for Magic Tool to reduce API calls
Implements different caching strategies for different data types
"""

import json
import os
import time
from typing import Dict, Optional, Any
from datetime import datetime, timedelta
from pathlib import Path

class PersistentCache:
    """
    Multi-tier persistent cache with different expiration policies
    
    Cache Types:
    - Card Data: Long-term cache (30 days) - card info rarely changes
    - Meta Data: Short-term cache (1 day) - recommendation/meta data changes frequently
    - Image URLs: Medium-term cache (7 days) - image links are fairly stable
    """
    
    def __init__(self, cache_dir: str = "data/cache"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Different cache files for different data types
        self.card_cache_file = self.cache_dir / "card_data.json"
        self.meta_cache_file = self.cache_dir / "meta_data.json"
        self.image_cache_file = self.cache_dir / "image_urls.json"
        
        # Expiration times (in hours)
        self.CARD_EXPIRY = 24 * 30  # 30 days for card data
        self.META_EXPIRY = 24  # 1 day for meta/recommendation data
        self.IMAGE_EXPIRY = 24 * 7  # 7 days for image URLs
        
        # Load existing caches
        self.card_cache = self._load_cache(self.card_cache_file)
        self.meta_cache = self._load_cache(self.meta_cache_file)
        self.image_cache = self._load_cache(self.image_cache_file)
    
    def _load_cache(self, cache_file: Path) -> Dict[str, Dict]:
        """Load cache from file or create empty cache"""
        try:
            if cache_file.exists():
                with open(cache_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            print(f"Warning: Could not load cache {cache_file}: {e}")
        
        return {}
    
    def _save_cache(self, cache_data: Dict, cache_file: Path) -> None:
        """Save cache to file"""
        try:
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, indent=2, ensure_ascii=False)
        except IOError as e:
            print(f"Warning: Could not save cache {cache_file}: {e}")
    
    def _is_expired(self, timestamp: float, expiry_hours: int) -> bool:
        """Check if cached data is expired"""
        current_time = time.time()
        expiry_seconds = expiry_hours * 3600
        return (current_time - timestamp) > expiry_seconds
    
    def _create_cache_entry(self, data: Any) -> Dict:
        """Create a cache entry with timestamp"""
        return {
            "data": data,
            "timestamp": time.time(),
            "cached_at": datetime.now().isoformat()
        }
    
    # Card Data Cache Methods (30-day expiry)
    def get_card_data(self, card_name: str) -> Optional[Dict]:
        """Get cached card data if valid"""
        key = card_name.lower().strip()
        
        if key in self.card_cache:
            entry = self.card_cache[key]
            if not self._is_expired(entry["timestamp"], self.CARD_EXPIRY):
                return entry["data"]
            else:
                # Remove expired entry
                del self.card_cache[key]
                self._save_cache(self.card_cache, self.card_cache_file)
        
        return None
    
    def cache_card_data(self, card_name: str, card_data: Dict) -> None:
        """Cache card data with long-term expiry"""
        key = card_name.lower().strip()
        self.card_cache[key] = self._create_cache_entry(card_data)
        self._save_cache(self.card_cache, self.card_cache_file)
    
    # Meta Data Cache Methods (1-day expiry)
    def get_meta_data(self, meta_key: str) -> Optional[Any]:
        """Get cached meta/recommendation data if valid"""
        if meta_key in self.meta_cache:
            entry = self.meta_cache[meta_key]
            if not self._is_expired(entry["timestamp"], self.META_EXPIRY):
                return entry["data"]
            else:
                # Remove expired entry
                del self.meta_cache[meta_key]
                self._save_cache(self.meta_cache, self.meta_cache_file)
        
        return None
    
    def cache_meta_data(self, meta_key: str, meta_data: Any) -> None:
        """Cache meta/recommendation data with short-term expiry"""
        self.meta_cache[meta_key] = self._create_cache_entry(meta_data)
        self._save_cache(self.meta_cache, self.meta_cache_file)
    
    # Image URL Cache Methods (7-day expiry)
    def get_image_url(self, card_name: str) -> Optional[str]:
        """Get cached image URL if valid"""
        key = card_name.lower().strip()
        
        if key in self.image_cache:
            entry = self.image_cache[key]
            if not self._is_expired(entry["timestamp"], self.IMAGE_EXPIRY):
                return entry["data"]
            else:
                # Remove expired entry
                del self.image_cache[key]
                self._save_cache(self.image_cache, self.image_cache_file)
        
        return None
    
    def cache_image_url(self, card_name: str, image_url: str) -> None:
        """Cache image URL with medium-term expiry"""
        key = card_name.lower().strip()
        self.image_cache[key] = self._create_cache_entry(image_url)
        self._save_cache(self.image_cache, self.image_cache_file)
    
    # Maintenance Methods
    def cleanup_expired_entries(self) -> Dict[str, int]:
        """Remove all expired entries from all caches"""
        cleanup_stats = {
            "card_data": 0,
            "meta_data": 0,
            "image_urls": 0
        }
        
        # Clean card cache
        expired_cards = []
        for key, entry in self.card_cache.items():
            if self._is_expired(entry["timestamp"], self.CARD_EXPIRY):
                expired_cards.append(key)
        
        for key in expired_cards:
            del self.card_cache[key]
            cleanup_stats["card_data"] += 1
        
        # Clean meta cache
        expired_meta = []
        for key, entry in self.meta_cache.items():
            if self._is_expired(entry["timestamp"], self.META_EXPIRY):
                expired_meta.append(key)
        
        for key in expired_meta:
            del self.meta_cache[key]
            cleanup_stats["meta_data"] += 1
        
        # Clean image cache
        expired_images = []
        for key, entry in self.image_cache.items():
            if self._is_expired(entry["timestamp"], self.IMAGE_EXPIRY):
                expired_images.append(key)
        
        for key in expired_images:
            del self.image_cache[key]
            cleanup_stats["image_urls"] += 1
        
        # Save cleaned caches
        if cleanup_stats["card_data"] > 0:
            self._save_cache(self.card_cache, self.card_cache_file)
        if cleanup_stats["meta_data"] > 0:
            self._save_cache(self.meta_cache, self.meta_cache_file)
        if cleanup_stats["image_urls"] > 0:
            self._save_cache(self.image_cache, self.image_cache_file)
        
        return cleanup_stats
    
    def get_cache_stats(self) -> Dict[str, Dict]:
        """Get statistics about cache usage"""
        current_time = time.time()
        
        def analyze_cache(cache_data: Dict, expiry_hours: int) -> Dict:
            total = len(cache_data)
            valid = 0
            expired = 0
            
            for entry in cache_data.values():
                if self._is_expired(entry["timestamp"], expiry_hours):
                    expired += 1
                else:
                    valid += 1
            
            return {
                "total_entries": total,
                "valid_entries": valid,
                "expired_entries": expired,
                "expiry_hours": expiry_hours
            }
        
        return {
            "card_data": analyze_cache(self.card_cache, self.CARD_EXPIRY),
            "meta_data": analyze_cache(self.meta_cache, self.META_EXPIRY),
            "image_urls": analyze_cache(self.image_cache, self.IMAGE_EXPIRY)
        }
    
    def clear_all_caches(self) -> None:
        """Clear all caches (useful for debugging or forcing refresh)"""
        self.card_cache = {}
        self.meta_cache = {}
        self.image_cache = {}
        
        # Remove cache files
        for cache_file in [self.card_cache_file, self.meta_cache_file, self.image_cache_file]:
            if cache_file.exists():
                cache_file.unlink()
        
        print("All caches cleared")

# Global cache instance
_persistent_cache = None

def get_cache() -> PersistentCache:
    """Get the global persistent cache instance"""
    global _persistent_cache
    if _persistent_cache is None:
        _persistent_cache = PersistentCache()
    return _persistent_cache
