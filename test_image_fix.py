#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from utils.scryfall_api import scryfall_api

def test_image_loading():
    print("Testing Scryfall API image loading...")
    
    # Test getting a card
    card = scryfall_api.get_card_fuzzy('Lightning Bolt')
    
    if card:
        print(f"✓ Card found: {card.name}")
        print(f"✓ Has image_uris attribute: {hasattr(card, 'image_uris')}")
        
        if hasattr(card, 'image_uris') and card.image_uris:
            print(f"✓ Image URLs available: {list(card.image_uris.keys())}")
            small_url = card.image_uris.get('small')
            normal_url = card.image_uris.get('normal')
            print(f"✓ Small image URL: {small_url[:50] + '...' if small_url else 'Not found'}")
            print(f"✓ Normal image URL: {normal_url[:50] + '...' if normal_url else 'Not found'}")
            
            # Test image download
            if small_url:
                try:
                    import requests
                    response = requests.get(small_url, timeout=5)
                    if response.status_code == 200:
                        print(f"✓ Image download successful: {len(response.content)} bytes")
                    else:
                        print(f"✗ Image download failed: HTTP {response.status_code}")
                except Exception as e:
                    print(f"✗ Image download error: {e}")
        else:
            print("✗ No image_uris found")
    else:
        print("✗ Card not found")

if __name__ == "__main__":
    test_image_loading()
