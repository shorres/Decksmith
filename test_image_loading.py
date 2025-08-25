#!/usr/bin/env python3
"""Test image loading from Scryfall"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from utils.scryfall_api import scryfall_api

def test_image_loading():
    print("Testing Scryfall image loading...")
    
    # Test card lookup
    card = scryfall_api.get_card_fuzzy('Lightning Bolt')
    if not card:
        print("❌ Failed to find Lightning Bolt")
        return
    
    print(f"✅ Found card: {card.name}")
    print(f"   Set: {card.set_code}")
    
    # Check image URIs
    if hasattr(card, 'image_uris'):
        print(f"✅ Has image_uris attribute")
        if card.image_uris:
            print(f"   Image URIs available: {type(card.image_uris)}")
            if hasattr(card.image_uris, 'small'):
                print(f"   Small image: {card.image_uris.small}")
            if hasattr(card.image_uris, 'normal'):
                print(f"   Normal image: {card.image_uris.normal}")
        else:
            print("❌ image_uris is None")
    else:
        print("❌ No image_uris attribute")
    
    # Test image download
    try:
        import requests
        from PIL import Image
        from io import BytesIO
        
        if hasattr(card, 'image_uris') and card.image_uris:
            image_url = card.image_uris.get('small') if card.image_uris else None
            if image_url:
                print(f"✅ Attempting to download: {image_url}")
                response = requests.get(image_url, timeout=5)
                if response.status_code == 200:
                    print(f"✅ Downloaded {len(response.content)} bytes")
                    
                    # Test PIL processing
                    image_data = BytesIO(response.content)
                    pil_image = Image.open(image_data)
                    print(f"✅ PIL image opened: {pil_image.size}")
                else:
                    print(f"❌ Download failed: {response.status_code}")
            else:
                print("❌ No image URL found")
        
    except Exception as e:
        print(f"❌ Image processing error: {e}")

if __name__ == "__main__":
    test_image_loading()
