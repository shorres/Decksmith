#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

import tkinter as tk
from tkinter import ttk
from utils.scryfall_api import scryfall_api
from gui.enhanced_import_dialog import EnhancedImportProgressDialog

def test_image_in_gui():
    """Test image loading in a simple GUI"""
    
    root = tk.Tk()
    root.title("Image Loading Test")
    root.geometry("600x500")
    
    # Apply theme
    try:
        import sv_ttk
        sv_ttk.set_theme("dark")
    except:
        pass
    
    # Create test button
    def test_import():
        # Create test deck content
        test_deck = """Deck
4 Lightning Bolt
2 Counterspell
1 Black Lotus"""
        
        # Create enhanced import dialog
        dialog = EnhancedImportProgressDialog(
            parent=root,
            title="Test Import with Images",
            deck_content=test_deck,
            deck_name="Test Deck"
        )
        
        # Start import
        result = dialog.show_and_import()
        if result:
            print(f"Import successful: {result.name} with {len(result.cards)} cards")
        else:
            print("Import cancelled or failed")
    
    test_button = ttk.Button(root, text="Test Enhanced Import with Images", 
                            command=test_import)
    test_button.pack(pady=20)
    
    # Manual image test
    frame = ttk.Frame(root)
    frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
    
    image_label = ttk.Label(frame, text="Card image will appear here")
    image_label.pack()
    
    def load_test_image():
        card = scryfall_api.get_card_fuzzy('Lightning Bolt')
        if card and hasattr(card, 'image_uris') and card.image_uris:
            image_url = card.image_uris.get('small')
            if image_url:
                try:
                    import requests
                    from PIL import Image, ImageTk
                    from io import BytesIO
                    
                    response = requests.get(image_url, timeout=5)
                    if response.status_code == 200:
                        image_data = BytesIO(response.content)
                        pil_image = Image.open(image_data)
                        pil_image = pil_image.resize((120, 168), Image.Resampling.LANCZOS)
                        tk_image = ImageTk.PhotoImage(pil_image)
                        image_label.configure(image=tk_image, text="")
                        image_label.image = tk_image  # Keep reference
                        print("✓ Image loaded successfully!")
                    else:
                        print(f"✗ HTTP {response.status_code}")
                except Exception as e:
                    print(f"✗ Error loading image: {e}")
            else:
                print("✗ No image URL found")
        else:
            print("✗ No card or image_uris found")
    
    image_button = ttk.Button(frame, text="Load Lightning Bolt Image", 
                             command=load_test_image)
    image_button.pack(pady=10)
    
    root.mainloop()

if __name__ == "__main__":
    test_image_in_gui()
