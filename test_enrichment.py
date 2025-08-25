#!/usr/bin/env python3
"""
Test script for Scryfall auto-enrichment feature
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from utils.csv_handler import CSVHandler
from utils.clipboard_handler import ClipboardHandler

def test_collection_import():
    """Test collection import with Scryfall enrichment"""
    print("Testing Collection Import with Scryfall Auto-Enrichment")
    print("=" * 60)
    
    csv_handler = CSVHandler()
    collection = csv_handler.import_collection_from_csv("test_collection.csv")
    
    print(f"\nImported collection with {len(collection.cards)} cards:")
    for card_name, collection_card in collection.cards.items():
        card = collection_card.card
        print(f"\n📄 {card.name}")
        print(f"   Mana Cost: {card.mana_cost or 'Not available'}")
        print(f"   Type: {card.card_type or 'Not available'}")
        print(f"   Rarity: {card.rarity or 'Not available'}")
        print(f"   Colors: {', '.join(card.colors) if card.colors else 'Not available'}")
        print(f"   Power/Toughness: {card.power}/{card.toughness}" if card.power is not None and card.toughness is not None else "   Power/Toughness: Not applicable")
        print(f"   Set: {card.set_code or 'Not available'}")
        print(f"   Quantity: {collection_card.quantity} regular, {collection_card.quantity_foil} foil")

def test_deck_import():
    """Test deck import with Scryfall enrichment"""
    print("\n\nTesting Arena Deck Import with Scryfall Auto-Enrichment")
    print("=" * 60)
    
    csv_handler = CSVHandler()
    deck = csv_handler.import_deck_from_arena_format("test_deck.txt")
    
    print(f"\nImported deck '{deck.name}' with {len(deck.cards)} cards:")
    
    mainboard = deck.get_mainboard_cards()
    sideboard = deck.get_sideboard_cards()
    
    print(f"\n🃏 Mainboard ({len(mainboard)} cards):")
    for deck_card in mainboard:
        card = deck_card.card
        print(f"   {deck_card.quantity}x {card.name}")
        print(f"      Mana Cost: {card.mana_cost or 'Not available'}")
        print(f"      Type: {card.card_type or 'Not available'}")
        print(f"      Rarity: {card.rarity or 'Not available'}")
    
    if sideboard:
        print(f"\n🗂️  Sideboard ({len(sideboard)} cards):")
        for deck_card in sideboard:
            card = deck_card.card
            print(f"   {deck_card.quantity}x {card.name}")
            print(f"      Mana Cost: {card.mana_cost or 'Not available'}")
            print(f"      Type: {card.card_type or 'Not available'}")
            print(f"      Rarity: {card.rarity or 'Not available'}")

def test_clipboard_import():
    """Test clipboard import with Scryfall enrichment"""
    print("\n\nTesting Clipboard Import with Scryfall Auto-Enrichment")
    print("=" * 60)
    
    # Test with simple format
    test_content = """4 Lightning Bolt
3 Counterspell
2 Brainstorm
1 Time Walk

Sideboard
2 Pyroblast
1 Red Elemental Blast"""
    
    print("Simulating clipboard content:")
    print(test_content)
    
    clipboard_handler = ClipboardHandler()
    
    # Simulate clipboard content by directly parsing it
    mainboard, sideboard = clipboard_handler.parse_simple_format(test_content)
    
    print(f"\n🃏 Parsed Mainboard ({len(mainboard)} cards):")
    for deck_card in mainboard:
        card = deck_card.card
        print(f"   {deck_card.quantity}x {card.name}")
        print(f"      Mana Cost: {card.mana_cost or 'Not available'}")
        print(f"      Type: {card.card_type or 'Not available'}")
        print(f"      Rarity: {card.rarity or 'Not available'}")
    
    if sideboard:
        print(f"\n🗂️  Parsed Sideboard ({len(sideboard)} cards):")
        for deck_card in sideboard:
            card = deck_card.card
            print(f"   {deck_card.quantity}x {card.name}")
            print(f"      Mana Cost: {card.mana_cost or 'Not available'}")
            print(f"      Type: {card.card_type or 'Not available'}")
            print(f"      Rarity: {card.rarity or 'Not available'}")

if __name__ == "__main__":
    try:
        test_collection_import()
        test_deck_import()
        test_clipboard_import()
        print("\n✅ All tests completed!")
    except Exception as e:
        print(f"\n❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()
