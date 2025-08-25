"""
Demo script to test Moxfield integration
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from utils.moxfield_service import MoxfieldService

def test_moxfield():
    """Test basic Moxfield functionality"""
    print("Testing Moxfield integration...")
    
    service = MoxfieldService()
    
    # Test deck search
    print("\n1. Searching for Standard decks...")
    decks = service.search_decks("standard", page_size=5)
    
    if decks:
        print(f"Found {len(decks)} decks:")
        for i, deck in enumerate(decks, 1):
            print(f"  {i}. {deck['name']} by {deck['author']}")
            print(f"     Likes: {deck['likes']} | Views: {deck['views']}")
            print(f"     URL: {deck['url']}")
            print()
        
        # Test getting deck details for the first deck
        if decks[0]['id']:
            print(f"\n2. Getting details for: {decks[0]['name']}")
            details = service.get_deck_details(decks[0]['id'])
            if details:
                print(f"   Mainboard cards: {len(details['mainboard'])}")
                print(f"   Sideboard cards: {len(details['sideboard'])}")
                print(f"   Total mainboard: {details['total_mainboard']}")
                if details['mainboard']:
                    print("   Sample cards:")
                    for card in details['mainboard'][:5]:
                        print(f"     {card['quantity']}x {card['name']}")
            else:
                print("   Failed to get deck details")
    else:
        print("No decks found")
    
    print("\n3. Testing format staples...")
    staples = service.get_format_staples("standard", limit=10)
    if staples:
        print(f"Found {len(staples)} popular cards:")
        for card in staples[:5]:
            print(f"  {card['name']} - {card['appearances']} decks ({card['popularity_percentage']:.1f}%)")
    else:
        print("No staples found")

if __name__ == "__main__":
    test_moxfield()
