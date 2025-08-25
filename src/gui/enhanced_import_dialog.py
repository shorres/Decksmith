"""
Enhanced Import Progress Dialog with Card Images
"""

import tkinter as tk
from tkinter import ttk
import threading
import time
from typing import Optional
import requests
from io import BytesIO

try:
    from PIL import Image, ImageTk
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
    """Enhanced import dialog with progress bar and card images"""
    
    def __init__(self, parent, title="Importing Deck..."):
        self.parent = parent
        self.title = title
        self.dialog = None
        self.cancelled = False
        self.current_card_name = ""
        self.image_cache = {}
        self.current_image = None
        
        # Create dialog window
        self.setup_dialog()
    
    def setup_dialog(self):
        """Setup the progress dialog window"""
        self.dialog = tk.Toplevel(self.parent)
        self.dialog.title(self.title)
        self.dialog.geometry("600x450")
        self.dialog.resizable(False, False)
        self.dialog.transient(self.parent)
        self.dialog.grab_set()
        
        # Center the dialog
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - 300
        y = (self.dialog.winfo_screenheight() // 2) - 225
        self.dialog.geometry(f"600x450+{x}+{y}")
        
        # Configure dark theme
        self.dialog.configure(bg='#2d2d30')
        
        # Main frame
        main_frame = ttk.Frame(self.dialog)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        # Header
        header_frame = ttk.Frame(main_frame)
        header_frame.pack(fill=tk.X, pady=(0, 15))
        
        title_label = ttk.Label(header_frame, text="🎴 Importing Magic Cards", 
                               font=('TkDefaultFont', 16, 'bold'))
        title_label.pack()
        
        subtitle_label = ttk.Label(header_frame, text="Fetching enhanced card data and artwork from Scryfall...",
                                  font=('TkDefaultFont', 9))
        subtitle_label.pack(pady=(3, 0))
        
        # Progress section
        progress_frame = ttk.LabelFrame(main_frame, text="Import Progress", padding=8)
        progress_frame.pack(fill=tk.X, pady=(0, 15))
        
        self.status_var = tk.StringVar(value="Preparing import...")
        status_label = ttk.Label(progress_frame, textvariable=self.status_var,
                                font=('TkDefaultFont', 10, 'bold'))
        status_label.pack(pady=(0, 8))
        
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(progress_frame, variable=self.progress_var,
                                          maximum=100, length=500, mode='determinate')
        self.progress_bar.pack(fill=tk.X, pady=(0, 5))
        
        self.progress_text_var = tk.StringVar(value="0%")
        self.progress_text = ttk.Label(progress_frame, textvariable=self.progress_text_var)
        self.progress_text.pack()
        
        # Card display section
        card_frame = ttk.LabelFrame(main_frame, text="Current Card", padding=10)
        card_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
        
        # Content frame for image and details
        content_frame = ttk.Frame(card_frame)
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Left side - Card image
        if PIL_AVAILABLE:
            image_frame = ttk.Frame(content_frame)
            image_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 15))
            
            self.card_image_label = ttk.Label(image_frame, text="🎴\\n\\nCard Image\\nLoading...",
                                             font=('TkDefaultFont', 10), anchor='center',
                                             relief='solid', borderwidth=1, width=20)
            self.card_image_label.pack()
        
        # Right side - Card details  
        details_frame = ttk.Frame(content_frame)
        details_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        self.card_name_var = tk.StringVar(value="Waiting for cards...")
        self.card_name_label = ttk.Label(details_frame, textvariable=self.card_name_var,
                                        font=('TkDefaultFont', 12, 'bold'))
        self.card_name_label.pack(anchor='w', pady=(0, 10))
        
        # Card details
        self.card_details_var = tk.StringVar(value="Import will begin shortly...")
        self.card_details_label = ttk.Label(details_frame, textvariable=self.card_details_var,
                                           wraplength=350, justify=tk.LEFT)
        self.card_details_label.pack(fill=tk.BOTH, expand=True, anchor='nw')
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X)
        
        self.cancel_button = ttk.Button(button_frame, text="Cancel Import",
                                       command=self.cancel_import)
        self.cancel_button.pack(side=tk.RIGHT, padx=(10, 0))
        
        self.minimize_button = ttk.Button(button_frame, text="Minimize",
                                         command=self.minimize_dialog)
        self.minimize_button.pack(side=tk.RIGHT)
        
        # Handle window close
        self.dialog.protocol("WM_DELETE_WINDOW", self.cancel_import)
    
    def update_progress(self, current: int, total: int, status: str = ""):
        """Update the progress bar and status"""
        if self.cancelled or not self.dialog:
            return
        
        try:
            percentage = (current / total) * 100 if total > 0 else 0
            self.progress_var.set(percentage)
            self.progress_text_var.set(f"{current}/{total} ({percentage:.1f}%)")
            
            if status:
                self.status_var.set(status)
            
            self.dialog.update()
        except tk.TclError:
            # Dialog was destroyed
            pass
    
    def update_card_display(self, card_name: str, scryfall_card=None):
        """Update the card display with current card info"""
        if self.cancelled or not self.dialog:
            return
        
        try:
            self.current_card_name = card_name
            self.card_name_var.set(f"📋 {card_name}")
            
            # Update card details
            if scryfall_card:
                details = f"💰 Mana Cost: {scryfall_card.mana_cost or 'N/A'}\\n"
                details += f"🎭 Type: {scryfall_card.type_line or 'N/A'}\\n"
                details += f"💎 Rarity: {scryfall_card.rarity or 'N/A'}\\n"
                details += f"🎨 Colors: {', '.join(scryfall_card.colors) if scryfall_card.colors else 'Colorless'}\\n"
                details += f"📦 Set: {scryfall_card.set_name} ({scryfall_card.set_code})" if scryfall_card.set_name else f"Set: {scryfall_card.set_code or 'N/A'}"
                
                if scryfall_card.power and scryfall_card.toughness:
                    details += f"\\n⚔️ P/T: {scryfall_card.power}/{scryfall_card.toughness}"
                
                # Load card image
                if PIL_AVAILABLE and hasattr(self, 'card_image_label') and scryfall_card.image_uri:
                    threading.Thread(target=self._load_card_image, 
                                   args=(scryfall_card.image_uri, card_name),
                                   daemon=True).start()
            else:
                details = "⏳ Fetching card data from Scryfall...\\n🔍 Looking up card information\\n🎨 Downloading artwork"
                if PIL_AVAILABLE and hasattr(self, 'card_image_label'):
                    self._set_placeholder_image()
            
            self.card_details_var.set(details)
            self.dialog.update()
        except tk.TclError:
            # Dialog was destroyed
            pass
    
    def _load_card_image(self, image_url: str, card_name: str):
        """Load card image from URL in background thread"""
        if not PIL_AVAILABLE or self.cancelled:
            return
        
        try:
            # Check cache first
            if image_url in self.image_cache:
                self._update_image_display(self.image_cache[image_url], card_name)
                return
            
            # Download image with timeout
            response = requests.get(image_url, timeout=5, stream=True)
            if response.status_code == 200:
                image_data = BytesIO(response.content)
                pil_image = Image.open(image_data)
                
                # Resize to fit display (maintain aspect ratio)
                display_width = 150
                aspect_ratio = pil_image.height / pil_image.width
                display_height = int(display_width * aspect_ratio)
                
                pil_image = pil_image.resize((display_width, display_height), Image.Resampling.LANCZOS)
                tk_image = ImageTk.PhotoImage(pil_image)
                
                # Cache the image
                self.image_cache[image_url] = tk_image
                
                # Update display in main thread
                if self.dialog:
                    self.dialog.after(0, self._update_image_display, tk_image, card_name)
            else:
                if self.dialog:
                    self.dialog.after(0, self._set_error_image)
        
        except Exception as e:
            print(f"Error loading image for {card_name}: {e}")
            if self.dialog:
                self.dialog.after(0, self._set_error_image)
    
    def _update_image_display(self, tk_image, card_name: str):
        """Update image display in main thread"""
        if self.cancelled or not self.dialog or self.current_card_name != card_name:
            return  # Skip if we've moved on or cancelled
        
        try:
            self.current_image = tk_image  # Keep reference to prevent garbage collection
            if hasattr(self, 'card_image_label'):
                self.card_image_label.configure(image=tk_image, text="")
        except tk.TclError:
            pass
    
    def _set_placeholder_image(self):
        """Set placeholder image while loading"""
        if hasattr(self, 'card_image_label'):
            try:
                placeholder_text = f"🎴\\n\\n{self.current_card_name[:12]}...\\n\\nLoading\\nImage..."
                self.card_image_label.configure(image="", text=placeholder_text)
            except tk.TclError:
                pass
    
    def _set_error_image(self):
        """Set error placeholder when image fails to load"""
        if hasattr(self, 'card_image_label'):
            try:
                error_text = f"🚫\\n\\n{self.current_card_name[:12]}...\\n\\nImage\\nUnavailable"
                self.card_image_label.configure(image="", text=error_text)
            except tk.TclError:
                pass
    
    def cancel_import(self):
        """Cancel the import process"""
        self.cancelled = True
        if self.dialog:
            try:
                self.dialog.destroy()
            except tk.TclError:
                pass
    
    def minimize_dialog(self):
        """Minimize the dialog"""
        if self.dialog:
            try:
                self.dialog.iconify()
            except tk.TclError:
                pass
    
    def close_dialog(self):
        """Close the dialog normally"""
        if self.dialog:
            try:
                self.dialog.destroy()
            except tk.TclError:
                pass
    
    def is_cancelled(self) -> bool:
        """Check if import was cancelled"""
        return self.cancelled

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
        """Import CSV deck with progress updates"""
        import csv
        from datetime import datetime
        
        if not deck_name:
            deck_name = f"Imported Deck {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        
        deck = Deck(name=deck_name)
        
        # First pass: count total cards
        total_cards = 0
        try:
            with open(filepath, 'r', newline='', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    card_name = row.get('name', '').strip()
                    if card_name:
                        total_cards += 1
        except Exception as e:
            raise Exception(f"Error reading CSV file: {str(e)}")
        
        if total_cards == 0:
            raise Exception("No valid cards found in CSV file")
        
        self.progress_dialog.update_progress(0, total_cards, "Starting enhanced import...")
        
        # Second pass: import cards with progress
        current_card = 0
        with open(filepath, 'r', newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            
            for row in reader:
                if self.progress_dialog.is_cancelled():
                    return None
                
                card_name = row.get('name', '').strip()
                if not card_name:
                    continue
                
                current_card += 1
                
                # Update progress
                self.progress_dialog.update_progress(
                    current_card, total_cards,
                    f"Enhancing: {card_name}"
                )
                
                # Get enhanced card data from Scryfall
                scryfall_card = None
                try:
                    scryfall_card = scryfall_api.get_card_fuzzy(card_name)
                except Exception as e:
                    print(f"Failed to get Scryfall data for {card_name}: {e}")
                
                # Update display
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
                
                # Show each card for a brief moment
                time.sleep(0.1)
        
        deck.created_date = datetime.now().isoformat()
        
        self.progress_dialog.update_progress(total_cards, total_cards, "✅ Import complete!")
        time.sleep(1)  # Show completion
        
        return deck
    
    def _import_arena_with_progress(self, filepath: str, deck_name: Optional[str] = None) -> Optional[Deck]:
        """Import Arena format deck with progress updates"""
        from datetime import datetime
        
        if not deck_name:
            deck_name = f"Arena Import {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        
        deck = Deck(name=deck_name)
        
        # First pass: count cards
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
        
        self.progress_dialog.update_progress(0, total_cards, "Starting Arena deck import...")
        
        # Second pass: import cards
        current_card = 0
        is_sideboard = False
        
        with open(filepath, 'r', encoding='utf-8') as f:
            for line in f:
                if self.progress_dialog.is_cancelled():
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
                    self.progress_dialog.update_progress(
                        current_card, total_cards,
                        f"Enhancing: {card_name}"
                    )
                    
                    # Get enhanced card data from Scryfall
                    scryfall_card = None
                    try:
                        scryfall_card = scryfall_api.get_card_fuzzy(card_name)
                    except Exception as e:
                        print(f"Failed to get Scryfall data for {card_name}: {e}")
                    
                    # Update display
                    self.progress_dialog.update_card_display(card_name, scryfall_card)
                    
                    # Create card object
                    if scryfall_card:
                        card = scryfall_api.convert_to_card_model(scryfall_card)
                    else:
                        # Basic fallback card
                        card = Card(name=card_name)
                    
                    deck.cards.append(DeckCard(card, quantity, is_sideboard))
                    
                    # Show each card for a brief moment
                    time.sleep(0.1)
        
        deck.created_date = datetime.now().isoformat()
        
        self.progress_dialog.update_progress(total_cards, total_cards, "✅ Import complete!")
        time.sleep(1)
        
        return deck
