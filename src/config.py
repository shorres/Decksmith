"""
Configuration management for Decksmith
Centralizes all configuration constants and settings
"""

import os
from pathlib import Path
from typing import Dict, Any
from dataclasses import dataclass


@dataclass
class AppConfig:
    """Application configuration settings"""
    
    # Application metadata
    APP_NAME: str = "Decksmith"
    VERSION: str = "1.0.5"
    DESCRIPTION: str = "Magic: The Gathering Arena Deck Manager"
    
    # File paths and directories
    DATA_DIR: str = "data"
    CACHE_DIR: str = "data/cache"
    COLLECTIONS_DIR: str = "data/collections"
    DECKS_DIR: str = "data/decks"
    
    # Cache files
    CARD_CACHE_FILE: str = "data/cache/card_data.json"
    META_CACHE_FILE: str = "data/cache/meta_data.json"
    
    # Default collection file
    DEFAULT_COLLECTION_FILE: str = "data/collections/default.json"
    
    # API settings
    SCRYFALL_API_BASE: str = "https://api.scryfall.com"
    REQUEST_TIMEOUT: float = 10.0
    MAX_RETRIES: int = 3
    RATE_LIMIT_DELAY: float = 0.1
    
    # UI settings
    DEFAULT_WINDOW_SIZE: str = "1200x800"
    MIN_WINDOW_SIZE: str = "800x600"
    DEFAULT_THEME: str = "clam"
    
    # Import/Export settings
    SUPPORTED_IMAGE_FORMATS: tuple = (".png", ".jpg", ".jpeg", ".gif", ".bmp")
    MAX_IMAGE_SIZE: tuple = (400, 560)  # width, height
    
    # Performance settings
    CARD_SEARCH_DELAY: float = 0.5  # seconds before triggering search
    MAX_SEARCH_RESULTS: int = 50
    THREAD_TIMEOUT: float = 2.0
    
    @classmethod
    def get_data_path(cls, relative_path: str = "") -> Path:
        """Get absolute path to data directory or file within it"""
        base_path = Path(__file__).parent.parent
        if relative_path:
            return base_path / relative_path
        return base_path / cls.DATA_DIR
    
    @classmethod
    def ensure_directories(cls) -> None:
        """Ensure all required directories exist"""
        dirs_to_create = [
            cls.DATA_DIR,
            cls.CACHE_DIR,
            cls.COLLECTIONS_DIR,
            cls.DECKS_DIR
        ]
        
        for dir_path in dirs_to_create:
            full_path = cls.get_data_path(dir_path)
            full_path.mkdir(parents=True, exist_ok=True)


# Global configuration instance
config = AppConfig()
