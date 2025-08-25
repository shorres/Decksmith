#!/usr/bin/env python3

"""
Test simple Scryfall queries to debug search issues
"""

from src.utils.scryfall_api import ScryfallAPI

def test_simple_queries():
    """Test basic Scryfall queries"""
    api = ScryfallAPI()
    
    print("Testing basic Scryfall queries...")
    print("=" * 50)
    
    # Test 1: Very basic query
    print("\n1. Testing basic red cards:")
    query1 = "c:r"
    try:
        results1 = api.search_cards(query1)
        print(f"Query: {query1}")
        print(f"Results: {len(results1)} cards found")
        if results1:
            print(f"First card: {results1[0].name} - {results1[0].mana_cost}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Test 2: Standard legal cards
    print("\n2. Testing standard legal cards:")
    query2 = "legal:standard"
    try:
        results2 = api.search_cards(query2)
        print(f"Query: {query2}")
        print(f"Results: {len(results2)} cards found")
        if results2:
            print(f"First card: {results2[0].name} - {results2[0].mana_cost}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Test 3: Red standard cards
    print("\n3. Testing red standard cards:")
    query3 = "c:r legal:standard"
    try:
        results3 = api.search_cards(query3)
        print(f"Query: {query3}")
        print(f"Results: {len(results3)} cards found")
        if results3:
            for i, card in enumerate(results3[:3]):
                print(f"  {i+1}. {card.name} - {card.mana_cost} - {card.type_line}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Test 4: Simple mana cost filter
    print("\n4. Testing mana cost filter:")
    query4 = "c:r cmc<=3"
    try:
        results4 = api.search_cards(query4)
        print(f"Query: {query4}")
        print(f"Results: {len(results4)} cards found")
        if results4:
            for i, card in enumerate(results4[:3]):
                print(f"  {i+1}. {card.name} - {card.mana_cost} - {card.type_line}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Test 5: Creatures only
    print("\n5. Testing red creatures:")
    query5 = "c:r t:creature"
    try:
        results5 = api.search_cards(query5)
        print(f"Query: {query5}")
        print(f"Results: {len(results5)} cards found")
        if results5:
            for i, card in enumerate(results5[:3]):
                print(f"  {i+1}. {card.name} - {card.mana_cost} - {card.type_line}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_simple_queries()
