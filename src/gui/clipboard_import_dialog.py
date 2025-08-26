"""
Clipboard Import Dialog with Enhanced Progress and Card Images
Extends the existing import system to support clipboard imports
"""

import tkinter as tk
from tkinter import ttk, messagebox
import threading
import time
from datetime import datetime
from typing import Optional

try:
    from PIL import Image, ImageTk
    import requests
    from io import BytesIO
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

try:
    from ..utils.scryfall_api import scryfall_api
    from ..utils.clipboard_handler import ClipboardHandler
    from ..models.deck import Deck
    from ..models.card import Card
    from ..models.deck import DeckCard
    from .enhanced_import_dialog import EnhancedImportProgressDialog
except ImportError:
    from utils.scryfall_api import scryfall_api
    from utils.clipboard_handler import ClipboardHandler
    from models.deck import Deck
    from models.card import Card
    from models.deck import DeckCard
    from gui.enhanced_import_dialog import EnhancedImportProgressDialog


class ClipboardImporter:
    """Enhanced clipboard importer with visual progress dialog"""
    
    def __init__(self, parent_window):
        self.parent = parent_window
        self.progress_dialog = None
        self.clipboard_handler = ClipboardHandler()
    
    def import_from_clipboard_with_progress(self, clipboard_content: Optional[str] = None, 
                                          deck_name: Optional[str] = None) -> Optional[Deck]:
        """Import deck from clipboard with enhanced progress dialog"""
        
        try:
            # Create progress dialog
            title = "Importing Deck from Clipboard..."
            self.progress_dialog = EnhancedImportProgressDialog(self.parent, title)
            
            if not self.progress_dialog:
                raise Exception("Failed to create progress dialog")
            
            # Import in background thread
            result_deck = None
            import_error = None
            
            def import_thread():
                nonlocal result_deck, import_error
                try:
                    result_deck = self._import_clipboard_with_progress(clipboard_content, deck_name)
                except Exception as e:
                    import_error = e
                finally:
                    # Close dialog in main thread
                    if self.progress_dialog and not self.progress_dialog.cancelled:
                        try:
                            self.parent.after(0, self.progress_dialog.close_dialog)
                        except tk.TclError:
                            pass
            
            # Start import thread
            thread = threading.Thread(target=import_thread, daemon=True)
            thread.start()
            
            # Show dialog (blocks until closed)
            try:
                self.parent.wait_window(self.progress_dialog.dialog)
            except tk.TclError:
                pass
            
            # Wait for thread to complete
            thread.join(timeout=2)
            
            if import_error:
                raise import_error
            
            return result_deck
            
        except Exception as e:
            # Fallback to simple import without progress dialog
            print(f"Enhanced import failed, falling back to simple import: {e}")
            return self._simple_import_fallback(clipboard_content, deck_name)
    
    def _import_clipboard_with_progress(self, clipboard_content: Optional[str] = None, 
                                       deck_name: Optional[str] = None) -> Optional[Deck]:
        """Import deck from clipboard with progress updates"""
        
        # Get clipboard content if not provided
        if clipboard_content is None:
            clipboard_content = self.clipboard_handler.get_clipboard_content()
        
        if not clipboard_content:
            raise Exception("Clipboard is empty")
        
        # Detect format and parse cards
        format_type = self.clipboard_handler.detect_format(clipboard_content)
        
        if format_type == "arena":
            mainboard, sideboard = self.clipboard_handler.parse_arena_format(clipboard_content)
        elif format_type == "simple":
            mainboard, sideboard = self.clipboard_handler.parse_simple_format(clipboard_content)
        else:
            raise Exception("Unknown clipboard format - cannot parse deck list")
        
        # Combine all cards for processing
        all_deck_cards = mainboard + sideboard
        total_cards = len(all_deck_cards)
        
        if total_cards == 0:
            raise Exception("No valid cards found in clipboard")
        
        # Generate deck name if not provided
        if not deck_name:
            format_desc = self.clipboard_handler.get_format_description(format_type)
            deck_name = f"Clipboard Import ({format_desc}) {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        
        deck = Deck(name=deck_name)
        
        if self.progress_dialog:
            self.progress_dialog.update_progress(0, total_cards, "Starting clipboard import...")
        
        # Process each card with enhanced data from Scryfall
        current_card = 0
        for deck_card in all_deck_cards:
            if self.progress_dialog and self.progress_dialog.is_cancelled():
                return None
            
            card_name = deck_card.card.name
            quantity = deck_card.quantity
            is_sideboard = deck_card.sideboard
            
            current_card += 1
            
            # Update progress
            if self.progress_dialog:
                self.progress_dialog.update_progress(
                    current_card, total_cards,
                    f"Enhancing: {card_name}"
                )
            
            # Get enhanced card data from Scryfall
            scryfall_card = None
            enhanced_card = None
            try:
                scryfall_card = scryfall_api.get_card_fuzzy(card_name)
                if scryfall_card:
                    enhanced_card = scryfall_api.convert_to_card_model(scryfall_card)
                else:
                    # Use the card from clipboard handler (may have basic Scryfall data)
                    enhanced_card = deck_card.card
            except Exception as e:
                print(f"Failed to get Scryfall data for {card_name}: {e}")
                enhanced_card = deck_card.card
            
            # Update display
            if self.progress_dialog:
                self.progress_dialog.update_card_display(card_name, scryfall_card)
            
            # Add to deck with enhanced data
            deck.add_card(enhanced_card, quantity, is_sideboard)
            
            # Show each card for a brief moment
            time.sleep(0.1)
        
        deck.created_date = datetime.now().isoformat()
        
        if self.progress_dialog:
            self.progress_dialog.update_progress(total_cards, total_cards, "✅ Clipboard import complete!")
            time.sleep(1)
        
        return deck


    def _simple_import_fallback(self, clipboard_content: Optional[str] = None, 
                               deck_name: Optional[str] = None) -> Optional[Deck]:
        """Simple import fallback without progress dialog"""
        
        # Get clipboard content if not provided
        if clipboard_content is None:
            clipboard_content = self.clipboard_handler.get_clipboard_content()
        
        if not clipboard_content:
            raise Exception("Clipboard is empty")
        
        # Detect format and parse cards
        format_type = self.clipboard_handler.detect_format(clipboard_content)
        
        if format_type == "arena":
            mainboard, sideboard = self.clipboard_handler.parse_arena_format(clipboard_content)
        elif format_type == "simple":
            mainboard, sideboard = self.clipboard_handler.parse_simple_format(clipboard_content)
        else:
            raise Exception("Unknown clipboard format - cannot parse deck list")
        
        # Combine all cards for processing
        all_deck_cards = mainboard + sideboard
        
        if len(all_deck_cards) == 0:
            raise Exception("No valid cards found in clipboard")
        
        # Generate deck name if not provided
        if not deck_name:
            format_desc = self.clipboard_handler.get_format_description(format_type)
            deck_name = f"Clipboard Import ({format_desc}) {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        
        deck = Deck(name=deck_name)
        
        # Process each card
        for deck_card in all_deck_cards:
            card_name = deck_card.card.name
            quantity = deck_card.quantity
            is_sideboard = deck_card.sideboard
            
            # Use basic card data
            deck.add_card(deck_card.card, quantity, is_sideboard)
        
        deck.created_date = datetime.now().isoformat()
        return deck


def import_clipboard_with_enhanced_dialog(parent_window, clipboard_content: Optional[str] = None, 
                                        deck_name: Optional[str] = None) -> Optional[Deck]:
    """
    Convenience function to import from clipboard with enhanced progress dialog
    
    Args:
        parent_window: Parent tkinter window
        clipboard_content: Optional clipboard content (will get from system clipboard if None)
        deck_name: Optional deck name (will generate if None)
        
    Returns:
        Imported Deck object or None if cancelled/failed
    """
    try:
        importer = ClipboardImporter(parent_window)
        return importer.import_from_clipboard_with_progress(clipboard_content, deck_name)
    except Exception as e:
        messagebox.showerror("Import Error", f"Failed to import from clipboard: {str(e)}")
        return None
