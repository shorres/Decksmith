"""
Enhanced Import Progress Dialog with Card Images
Supports CSV and Arena format imports with visual feedback
"""

import tkinter as tk
from tkinter import ttk
import threading
import time
import csv
from datetime import datetime
from typing import Optional, List, Dict
import os

try:
    from PIL import Image, ImageTk
    import requests
    from io import BytesIO
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

try:
    from ..utils.scryfall_api import scryfall_api
    from ..models.deck import Deck
    from ..models.card import Card
    from ..models.deck import DeckCard
except ImportError:
    from utils.scryfall_api import scryfall_api
    from models.deck import Deck
    from models.card import Card
    from models.deck import DeckCard


class EnhancedImportProgressDialog:
    """Enhanced import dialog with progress bar and card image display"""
    
    def __init__(self, parent, title="Importing Deck..."):
        self.parent = parent
        self.title = title
        self.dialog = None
        self.cancelled = False
        self.current_card_name = ""
        self.progress_var = None
        self.status_var = None
        self.card_image_label = None
        self.card_name_var = None
        self.card_details_var = None
        self.current_image = None
        self.image_cache = {}
        
        self.setup_dialog()
    
    def setup_dialog(self):
        """Setup the progress dialog window"""
        self.dialog = tk.Toplevel(self.parent)
        self.dialog.title(self.title)
        self.dialog.geometry("500x400")
        self.dialog.resizable(False, False)
        self.dialog.transient(self.parent)
        self.dialog.grab_set()
        
        # Center the dialog
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (250)
        y = (self.dialog.winfo_screenheight() // 2) - (200)
        self.dialog.geometry(f"500x400+{x}+{y}")
        
        # Main frame
        main_frame = ttk.Frame(self.dialog)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Header
        header_frame = ttk.Frame(main_frame)
        header_frame.pack(fill=tk.X, pady=(0, 15))
        
        title_label = ttk.Label(header_frame, text="🎴 Importing Magic Cards", 
                               font=('TkDefaultFont', 14, 'bold'))
        title_label.pack()
        
        # Card display section
        card_frame = ttk.LabelFrame(main_frame, text="Current Card", padding=10)
        card_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
        
        # Card image (if PIL available)
        if PIL_AVAILABLE:
            self.card_image_label = ttk.Label(card_frame, text="🎴\nLoading...", 
                                             anchor='center', width=25)
            self.card_image_label.pack(pady=(0, 10))
        
        # Card details
        self.card_name_var = tk.StringVar(value="Waiting for cards...")
        card_name_label = ttk.Label(card_frame, textvariable=self.card_name_var,
                                   font=('TkDefaultFont', 11, 'bold'))
        card_name_label.pack(pady=(0, 5))
        
        self.card_details_var = tk.StringVar(value="Import will begin shortly...")
        card_details_label = ttk.Label(card_frame, textvariable=self.card_details_var,
                                      wraplength=400)
        card_details_label.pack()
        
        # Progress section (below card info)
        progress_frame = ttk.LabelFrame(main_frame, text="Progress", padding=10)
        progress_frame.pack(fill=tk.X, pady=(0, 15))
        
        self.status_var = tk.StringVar(value="Preparing import...")
        status_label = ttk.Label(progress_frame, textvariable=self.status_var)
        status_label.pack(pady=(0, 5))
        
        self.progress_var = tk.DoubleVar()
        progress_bar = ttk.Progressbar(progress_frame, variable=self.progress_var,
                                      maximum=100, mode='determinate')
        progress_bar.pack(fill=tk.X, pady=(0, 5))
        
        self.progress_text_var = tk.StringVar(value="0%")
        self.progress_text = ttk.Label(progress_frame, textvariable=self.progress_text_var)
        self.progress_text.pack()
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X)
        
        self.cancel_button = ttk.Button(button_frame, text="Cancel", 
                                       command=self.cancel_import)
        self.cancel_button.pack(side=tk.RIGHT, padx=(10, 0))
        
        self.minimize_button = ttk.Button(button_frame, text="Minimize",
                                         command=self.minimize_dialog)
        self.minimize_button.pack(side=tk.RIGHT)
        
        # Handle window close
        self.dialog.protocol("WM_DELETE_WINDOW", self.cancel_import)
    
    def update_progress(self, current: int, total: int, status: str = ""):
        """Update progress bar and status with improved responsiveness"""
        if self.cancelled or not self.dialog:
            return
            
        try:
            if total > 0 and self.progress_var:
                percentage = (current / total) * 100
                self.progress_var.set(percentage)
                if self.progress_text_var:
                    self.progress_text_var.set(f"{current}/{total} ({percentage:.0f}%)")
            
            if status and self.status_var:
                self.status_var.set(status)
            
            # Force immediate GUI update for better responsiveness
            self.dialog.update_idletasks()
            self.dialog.update()  # Force a full update
        except tk.TclError:
            pass
    
    def update_card_display(self, card_name: str, scryfall_card=None):
        """Update the card display with current card info"""
        if self.cancelled or not self.dialog:
            return
            
        try:
            self.current_card_name = card_name
            if self.card_name_var:
                self.card_name_var.set(card_name)
            
            if scryfall_card:
                details = f"Type: {getattr(scryfall_card, 'type_line', 'Unknown')}\n"
                details += f"Cost: {getattr(scryfall_card, 'mana_cost', 'N/A')}\n"
                details += f"Set: {getattr(scryfall_card, 'set_code', 'N/A').upper()}"
                if self.card_details_var:
                    self.card_details_var.set(details)
                
                # Load card image if available
                if PIL_AVAILABLE and hasattr(scryfall_card, 'image_uris'):
                    self._load_card_image(scryfall_card)
            else:
                if self.card_details_var:
                    self.card_details_var.set("Loading card data...")
                
        except tk.TclError:
            pass
    
    def _load_card_image(self, scryfall_card):
        """Load and display card image"""
        if not PIL_AVAILABLE or not self.card_image_label:
            return
            
        try:
            # Get image URL
            image_url = None
            if hasattr(scryfall_card, 'image_uris') and scryfall_card.image_uris:
                image_url = scryfall_card.image_uris.get('small') or scryfall_card.image_uris.get('normal')
            
            if not image_url:
                return
                
            # Check cache
            if image_url in self.image_cache and self.card_image_label:
                self.card_image_label.configure(image=self.image_cache[image_url], text="")
                return
            
            # Download in thread
            def download_image():
                try:
                    import requests
                    from io import BytesIO
                    from PIL import Image, ImageTk
                    
                    response = requests.get(image_url, timeout=3)  # Reduced from 5 to 3 seconds
                    if response.status_code == 200:
                        image_data = BytesIO(response.content)
                        pil_image = Image.open(image_data)
                        pil_image = pil_image.resize((120, 168), Image.Resampling.LANCZOS)
                        tk_image = ImageTk.PhotoImage(pil_image)
                        
                        # Cache and display
                        self.image_cache[image_url] = tk_image
                        if not self.cancelled and self.card_image_label:
                            self.parent.after(0, lambda: self._set_image(tk_image))
                except:
                    pass  # Fail silently for images
            
            thread = threading.Thread(target=download_image, daemon=True)
            thread.start()
            
        except:
            pass  # Fail silently
    
    def _set_image(self, tk_image):
        """Set image in main thread"""
        try:
            if self.card_image_label and not self.cancelled:
                self.current_image = tk_image
                self.card_image_label.configure(image=tk_image, text="")
        except tk.TclError:
            pass
    
    def is_cancelled(self):
        """Check if import was cancelled"""
        return self.cancelled
    
    def cancel_import(self):
        """Cancel the import process"""
        self.cancelled = True
        self.close_dialog()
    
    def minimize_dialog(self):
        """Minimize the dialog"""
        try:
            if self.dialog:
                self.dialog.iconify()
        except tk.TclError:
            pass
    
    def close_dialog(self):
        """Close the dialog"""
        try:
            if self.dialog:
                self.dialog.destroy()
        except tk.TclError:
            pass


class EnhancedCSVImporter:
    """Enhanced CSV importer with visual progress dialog"""
    
    def __init__(self, parent_window):
        self.parent = parent_window
        self.progress_dialog = None
    
    def import_deck_with_progress(self, filepath: str, import_type: str = "csv", 
                                 deck_name: Optional[str] = None) -> Optional[Deck]:
        """Import deck with enhanced progress dialog"""
        
        # Create progress dialog
        title = f"Importing {import_type.upper()} Deck..."
        self.progress_dialog = EnhancedImportProgressDialog(self.parent, title)
        
        # Import in background thread
        result_deck = None
        import_error = None
        
        def import_thread():
            nonlocal result_deck, import_error
            try:
                if import_type.lower() == "csv":
                    result_deck = self._import_csv_with_progress(filepath, deck_name)
                elif import_type.lower() == "arena":
                    result_deck = self._import_arena_with_progress(filepath, deck_name)
                else:
                    raise ValueError(f"Unknown import type: {import_type}")
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
    
    def _import_csv_with_progress(self, filepath: str, deck_name: Optional[str] = None) -> Optional[Deck]:
        """Import CSV with progress updates"""
        if not deck_name:
            deck_name = f"CSV Import {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        
        deck = Deck(name=deck_name)
        
        # Count total cards first
        total_cards = 0
        try:
            with open(filepath, 'r', encoding='utf-8', newline='') as csvfile:
                reader = csv.DictReader(csvfile)
                for _ in reader:
                    total_cards += 1
        except Exception as e:
            raise Exception(f"Error reading CSV file: {str(e)}")
        
        if total_cards == 0:
            raise Exception("No cards found in CSV file")
        
        if self.progress_dialog:
            self.progress_dialog.update_progress(0, total_cards, "Starting CSV import...")
        
        # Import cards
        current_card = 0
        with open(filepath, 'r', encoding='utf-8', newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            
            for row in reader:
                if self.progress_dialog and self.progress_dialog.is_cancelled():
                    return None
                
                card_name = row.get('name', '').strip()
                if not card_name:
                    continue
                
                current_card += 1
                
                # Update progress with better responsiveness
                if self.progress_dialog:
                    self.progress_dialog.update_progress(
                        current_card, total_cards,
                        f"Importing cards from CSV..."
                    )
                
                # Get enhanced card data (with shorter timeout for speed)
                scryfall_card = None
                try:
                    scryfall_card = scryfall_api.get_card_fuzzy(card_name)
                except Exception as e:
                    print(f"Failed to get Scryfall data for {card_name}: {e}")
                
                # Update display
                if self.progress_dialog:
                    self.progress_dialog.update_card_display(card_name, scryfall_card)
                
                # Create card object
                if scryfall_card:
                    card = scryfall_api.convert_to_card_model(scryfall_card)
                else:
                    # Fallback to CSV data
                    card = Card(
                        name=card_name,
                        mana_cost=row.get('mana_cost', ''),
                        converted_mana_cost=int(row.get('converted_mana_cost', 0)) if row.get('converted_mana_cost', '').isdigit() else 0,
                        card_type=row.get('card_type', ''),
                        rarity=row.get('rarity', 'Common')
                    )
                
                # Add to deck
                quantity = int(row.get('quantity', 1)) if row.get('quantity', '').isdigit() else 1
                sideboard = row.get('sideboard', '').lower() in ['true', '1', 'yes']
                
                deck.cards.append(DeckCard(card, quantity, sideboard))
                
                # Process next card immediately (removed artificial delay)
        
        deck.created_date = datetime.now().isoformat()
        
        if self.progress_dialog:
            self.progress_dialog.update_progress(total_cards, total_cards, "✅ Import complete!")
        time.sleep(0.5)  # Reduced from 1 to 0.5 seconds for faster completion
        
        return deck
    
    def _import_arena_with_progress(self, filepath: str, deck_name: Optional[str] = None) -> Optional[Deck]:
        """Import Arena format with progress updates"""
        if not deck_name:
            deck_name = f"Arena Import {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        
        deck = Deck(name=deck_name)
        
        # Count cards
        total_cards = 0
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith('//') or line.lower() in ['deck', 'mainboard', 'sideboard']:
                        continue
                    
                    parts = line.split(' ', 1)
                    if len(parts) == 2 and parts[0].isdigit():
                        total_cards += 1
        except Exception as e:
            raise Exception(f"Error reading Arena file: {str(e)}")
        
        if total_cards == 0:
            raise Exception("No valid cards found in Arena file")
        
        if self.progress_dialog:
            self.progress_dialog.update_progress(0, total_cards, "Starting Arena import...")
        
        # Import cards
        current_card = 0
        is_sideboard = False
        
        with open(filepath, 'r', encoding='utf-8') as f:
            for line in f:
                if self.progress_dialog and self.progress_dialog.is_cancelled():
                    return None
                
                line = line.strip()
                
                # Skip empty lines and comments
                if not line or line.startswith('//'):
                    continue
                
                # Check for section headers
                if line.lower() in ['deck', 'mainboard']:
                    is_sideboard = False
                    continue
                elif line.lower() == 'sideboard':
                    is_sideboard = True
                    continue
                
                # Parse card line
                parts = line.split(' ', 1)
                if len(parts) == 2 and parts[0].isdigit():
                    quantity = int(parts[0])
                    card_name = parts[1]
                    
                    current_card += 1
                    
                    # Update progress
                    if self.progress_dialog:
                        self.progress_dialog.update_progress(
                            current_card, total_cards,
                            f"Importing cards from Arena deck..."
                        )
                    
                    # Get enhanced card data
                    scryfall_card = None
                    try:
                        scryfall_card = scryfall_api.get_card_fuzzy(card_name)
                    except Exception as e:
                        print(f"Failed to get Scryfall data for {card_name}: {e}")
                    
                    # Update display
                    if self.progress_dialog:
                        self.progress_dialog.update_card_display(card_name, scryfall_card)
                    
                    # Create card object
                    if scryfall_card:
                        card = scryfall_api.convert_to_card_model(scryfall_card)
                    else:
                        card = Card(name=card_name)
                    
                    deck.cards.append(DeckCard(card, quantity, is_sideboard))
                    
                    # Process next card immediately (removed artificial delay)
        
        deck.created_date = datetime.now().isoformat()
        
        if self.progress_dialog:
            self.progress_dialog.update_progress(total_cards, total_cards, "✅ Import complete!")
        time.sleep(0.5)  # Reduced completion delay for faster performance
        
        return deck
