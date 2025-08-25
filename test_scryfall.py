"""
Simple test to verify Scryfall API is working
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from utils.scryfall_api import ScryfallAPI

def test_scryfall_api():
    """Test basic Scryfall API functionality"""
    print("Testing Scryfall API connectivity...")
    
    api = ScryfallAPI()
    
    # Test autocomplete
    print("\n1. Testing autocomplete:")
    autocomplete_results = api.autocomplete_card_names("Lightning")
    print(f"Autocomplete for 'Lightning': {autocomplete_results[:5]}")
    
    # Test card search
    print("\n2. Testing card search:")
    search_results = api.search_cards("Lightning Bolt")
    print(f"Search results for 'Lightning Bolt': {len(search_results)} cards found")
    
    if search_results:
        card = search_results[0]
        print(f"First result: {card.name} - {card.mana_cost} - {card.type_line}")
        print(f"Oracle text: {card.oracle_text[:100]}...")
        print(f"Legalities: {card.legalities}")
    
    # Test exact name lookup
    print("\n3. Testing exact name lookup:")
    exact_card = api.get_card_by_name("Lightning Bolt")
    if exact_card:
        print(f"Exact match: {exact_card.name} - {exact_card.mana_cost}")
        print(f"Standard legal: {exact_card.legalities.get('standard', 'unknown')}")
    else:
        print("No exact match found")
    
    # Test format search
    print("\n4. Testing format search:")
    try:
        format_search = api.search_cards("f:standard c:r cmc:1")
        print(f"Standard red 1-CMC cards: {len(format_search)} found")
        if format_search:
            for card in format_search[:3]:
                print(f"  - {card.name} ({card.mana_cost})")
    except Exception as e:
        print(f"Format search error: {e}")

if __name__ == "__main__":
    test_scryfall_api()
