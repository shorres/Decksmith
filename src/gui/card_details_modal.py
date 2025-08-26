"""
Card Details Modal Dialog with Scryfall Integration
Shows detailed card information including images
"""

import tkinter as tk
from tkinter import ttk
import threading
import requests
from io import BytesIO

try:
    from PIL import Image, ImageTk
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

try:
    from ..utils.scryfall_api import scryfall_api
    from ..models.card import Card
except ImportError:
    from utils.scryfall_api import scryfall_api
    from models.card import Card


class CardDetailsModal:
    """Modal dialog showing detailed card information"""
    
    def __init__(self, parent, card: Card, collection_card=None):
        self.parent = parent
        self.card = card
        self.collection_card = collection_card
        self.dialog = None
        self.current_image = None
        self.scryfall_card = None
        
        self.create_dialog()
        self.load_scryfall_data()
    
    def create_dialog(self):
        """Create the modal dialog"""
        self.dialog = tk.Toplevel(self.parent)
        self.dialog.title(f"Card Details - {self.card.name}")
        self.dialog.geometry("600x500")
        self.dialog.resizable(True, True)
        self.dialog.transient(self.parent)
        self.dialog.grab_set()
        
        # Center the dialog
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (300)
        y = (self.dialog.winfo_screenheight() // 2) - (250)
        self.dialog.geometry(f"600x500+{x}+{y}")
        
        # Create main layout
        self.create_layout()
        
        # Handle window close
        self.dialog.protocol("WM_DELETE_WINDOW", self.close_dialog)
        
        # Focus on dialog
        self.dialog.focus_set()
    
    def create_layout(self):
        """Create the dialog layout"""
        # Main container
        main_frame = ttk.Frame(self.dialog)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        # Content frame with card image and details side by side
        content_frame = ttk.Frame(main_frame)
        content_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
        
        # Left side - Card image
        self.image_frame = ttk.LabelFrame(content_frame, text="Card Image", padding=10)
        self.image_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 15))
        
        self.card_image_label = ttk.Label(self.image_frame, text="🎴\n\nLoading\nImage...", 
                                         anchor='center', width=20)
        self.card_image_label.pack()
        
        # Right side - Card details
        details_frame = ttk.LabelFrame(content_frame, text="Card Information", padding=10)
        details_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Card name
        name_frame = ttk.Frame(details_frame)
        name_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(name_frame, text="Name:", font=('TkDefaultFont', 10, 'bold')).pack(anchor='w')
        ttk.Label(name_frame, text=self.card.name, font=('TkDefaultFont', 12)).pack(anchor='w')
        
        # Details in scrollable text area
        self.details_text = tk.Text(details_frame, height=15, width=40, wrap=tk.WORD)
        details_scrollbar = ttk.Scrollbar(details_frame, orient=tk.VERTICAL, 
                                         command=self.details_text.yview)
        self.details_text.configure(yscrollcommand=details_scrollbar.set)
        
        self.details_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        details_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Collection info if available
        if self.collection_card:
            collection_frame = ttk.LabelFrame(main_frame, text="Collection Info", padding=10)
            collection_frame.pack(fill=tk.X, pady=(0, 15))
            
            info_text = f"Regular Copies: {self.collection_card.quantity}\n"
            info_text += f"Foil Copies: {self.collection_card.quantity_foil}\n"
            info_text += f"Total Value: {self.collection_card.quantity + self.collection_card.quantity_foil} copies"
            
            ttk.Label(collection_frame, text=info_text).pack(anchor='w')
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X)
        
        ttk.Button(button_frame, text="View on Scryfall", 
                  command=self.view_on_scryfall).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="Close", 
                  command=self.close_dialog).pack(side=tk.RIGHT)
        
        # Initial details
        self.update_details()
    
    def update_details(self):
        """Update the details text with current card info"""
        self.details_text.delete(1.0, tk.END)
        
        # Basic card info
        details = f"Mana Cost: {self.card.mana_cost or 'N/A'}\n"
        details += f"Converted Mana Cost: {self.card.converted_mana_cost}\n"
        details += f"Type: {self.card.card_type or 'N/A'}\n"
        
        if self.card.creature_type:
            details += f"Creature Types: {self.card.creature_type}\n"
        
        details += f"Rarity: {self.card.rarity or 'Unknown'}\n"
        details += f"Colors: {', '.join(self.card.colors) if self.card.colors else 'Colorless'}\n"
        
        if self.card.power is not None and self.card.toughness is not None:
            details += f"Power/Toughness: {self.card.power}/{self.card.toughness}\n"
        
        if self.card.set_code:
            details += f"Set: {self.card.set_code.upper()}"
            if self.card.collector_number:
                details += f" #{self.card.collector_number}"
            details += "\n"
        
        details += "\n"
        
        if self.card.text:
            details += f"Oracle Text:\n{self.card.text}\n\n"
        
        # Add loading message for Scryfall data
        if not self.scryfall_card:
            details += "Loading enhanced information from Scryfall..."
        
        self.details_text.insert(1.0, details)
        self.details_text.configure(state=tk.DISABLED)
    
    def load_scryfall_data(self):
        """Load enhanced card data from Scryfall in background thread"""
        def fetch_data():
            try:
                self.scryfall_card = scryfall_api.get_card_fuzzy(self.card.name)
                if self.scryfall_card:
                    # Update in main thread
                    self.parent.after(0, self.update_with_scryfall_data)
                    # Load image
                    self.parent.after(0, self.load_card_image)
            except Exception as e:
                print(f"Failed to load Scryfall data for {self.card.name}: {e}")
                self.parent.after(0, self.set_image_error)
        
        thread = threading.Thread(target=fetch_data, daemon=True)
        thread.start()
    
    def update_with_scryfall_data(self):
        """Update details with Scryfall data"""
        if not self.scryfall_card:
            return
        
        self.details_text.configure(state=tk.NORMAL)
        self.details_text.delete(1.0, tk.END)
        
        # Enhanced card info from Scryfall
        details = f"Mana Cost: {getattr(self.scryfall_card, 'mana_cost', 'N/A')}\n"
        details += f"Converted Mana Cost: {getattr(self.scryfall_card, 'cmc', 0)}\n"
        details += f"Type Line: {getattr(self.scryfall_card, 'type_line', 'N/A')}\n"
        details += f"Rarity: {getattr(self.scryfall_card, 'rarity', 'Unknown').title()}\n"
        details += f"Colors: {', '.join(getattr(self.scryfall_card, 'colors', []))}\n"
        
        if hasattr(self.scryfall_card, 'power') and hasattr(self.scryfall_card, 'toughness'):
            if self.scryfall_card.power and self.scryfall_card.toughness:
                details += f"Power/Toughness: {self.scryfall_card.power}/{self.scryfall_card.toughness}\n"
        
        details += f"Set: {getattr(self.scryfall_card, 'set_name', 'Unknown')} ({getattr(self.scryfall_card, 'set_code', '').upper()})\n"
        
        if hasattr(self.scryfall_card, 'collector_number'):
            details += f"Collector Number: {self.scryfall_card.collector_number}\n"
        
        if hasattr(self.scryfall_card, 'artist'):
            details += f"Artist: {self.scryfall_card.artist}\n"
        
        if hasattr(self.scryfall_card, 'released_at'):
            details += f"Release Date: {self.scryfall_card.released_at}\n"
        
        details += "\n"
        
        oracle_text = getattr(self.scryfall_card, 'oracle_text', '')
        if oracle_text:
            details += f"Oracle Text:\n{oracle_text}\n\n"
        
        flavor_text = getattr(self.scryfall_card, 'flavor_text', '')
        if flavor_text:
            details += f"Flavor Text:\n{flavor_text}\n\n"
        
        # Legality information
        if hasattr(self.scryfall_card, 'legalities'):
            details += "Format Legality:\n"
            legalities = self.scryfall_card.legalities
            for format_name in ['standard', 'pioneer', 'modern', 'legacy', 'vintage', 'commander']:
                if hasattr(legalities, format_name):
                    status = getattr(legalities, format_name, 'unknown')
                    details += f"  {format_name.title()}: {status.title()}\n"
            details += "\n"
        
        # Pricing info if available
        if hasattr(self.scryfall_card, 'prices') and self.scryfall_card.prices:
            details += "Pricing (USD):\n"
            prices = self.scryfall_card.prices
            if hasattr(prices, 'usd') and prices.usd:
                details += f"  Regular: ${prices.usd}\n"
            if hasattr(prices, 'usd_foil') and prices.usd_foil:
                details += f"  Foil: ${prices.usd_foil}\n"
        
        self.details_text.insert(1.0, details)
        self.details_text.configure(state=tk.DISABLED)
    
    def load_card_image(self):
        """Load and display card image from Scryfall"""
        if not PIL_AVAILABLE or not self.scryfall_card:
            return
        
        def download_image():
            try:
                if not PIL_AVAILABLE:
                    return
                    
                # Import here to ensure they're available
                from PIL import Image, ImageTk
                
                # Get image URL
                image_url = None
                if self.scryfall_card and hasattr(self.scryfall_card, 'image_uris') and self.scryfall_card.image_uris:
                    # Prefer normal size, fall back to small
                    image_url = self.scryfall_card.image_uris.get('normal') or self.scryfall_card.image_uris.get('small')
                
                if not image_url:
                    self.parent.after(0, self.set_image_error)
                    return
                
                # Download image with faster timeout
                response = requests.get(image_url, timeout=5)  # Reduced from 10 to 5 seconds
                if response.status_code == 200:
                    image_data = BytesIO(response.content)
                    pil_image = Image.open(image_data)
                    
                    # Resize to fit dialog
                    pil_image = pil_image.resize((200, 280), Image.Resampling.LANCZOS)
                    tk_image = ImageTk.PhotoImage(pil_image)
                    
                    # Update in main thread
                    self.parent.after(0, lambda: self.set_card_image(tk_image))
                else:
                    self.parent.after(0, self.set_image_error)
            except Exception as e:
                print(f"Failed to load card image: {e}")
                self.parent.after(0, self.set_image_error)
        
        thread = threading.Thread(target=download_image, daemon=True)
        thread.start()
    
    def set_card_image(self, tk_image):
        """Set the card image in the label"""
        try:
            self.current_image = tk_image  # Keep reference
            self.card_image_label.configure(image=tk_image, text="")
        except tk.TclError:
            pass
    
    def set_image_error(self):
        """Set error message when image fails to load"""
        try:
            error_text = f"🚫\n\n{self.card.name}\n\nImage\nUnavailable"
            self.card_image_label.configure(text=error_text, image="")
        except tk.TclError:
            pass
    
    def view_on_scryfall(self):
        """Open card page on Scryfall website"""
        try:
            import webbrowser
            if self.scryfall_card and hasattr(self.scryfall_card, 'scryfall_uri'):
                webbrowser.open(self.scryfall_card.scryfall_uri)
            else:
                # Fallback to search
                search_name = self.card.name.replace(' ', '+')
                url = f"https://scryfall.com/search?q={search_name}"
                webbrowser.open(url)
        except Exception as e:
            print(f"Failed to open Scryfall: {e}")
    
    def close_dialog(self):
        """Close the dialog"""
        try:
            if self.dialog:
                self.dialog.destroy()
        except tk.TclError:
            pass


def show_card_details_modal(parent, card: Card, collection_card=None):
    """
    Convenience function to show card details modal
    
    Args:
        parent: Parent widget
        card: Card object to display
        collection_card: Optional CollectionCard with quantity info
    """
    CardDetailsModal(parent, card, collection_card)
