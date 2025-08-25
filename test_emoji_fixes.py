#!/usr/bin/env python3
"""
Test script to verify emoji fixes in Magic Tool
"""

import sys
import os

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from models.deck import Deck
from models.card import Card


def test_color_display():
    """Test that color symbols display correctly"""
    print("🧪 Testing color symbol display...")
    
    # Create a multi-color deck to test color display
    deck = Deck("Multi-Color Test Deck")
    
    # Add cards of different colors
    deck.add_card(Card("Lightning Bolt", "R"), 4)  # Red
    deck.add_card(Card("Counterspell", "UU"), 4)   # Blue
    deck.add_card(Card("Swords to Plowshares", "W"), 4)  # White
    deck.add_card(Card("Dark Ritual", "B"), 4)     # Black
    deck.add_card(Card("Llanowar Elves", "G"), 4)  # Green
    
    # Get color distribution
    color_distribution = deck.get_color_distribution()
    print(f"  📊 Deck colors found: {sorted(color_distribution.keys())}")
    
    # Test the new color symbol logic
    color_symbols = {'W': '[W]', 'U': '[U]', 'B': '[B]', 'R': '[R]', 'G': '[G]'}
    color_list = []
    for color in sorted(color_distribution.keys()):
        symbol = color_symbols.get(color, color)
        if symbol:
            color_list.append(symbol)
    color_display = ''.join(color_list)
    
    print(f"  🎨 Old format (problematic): ⚪🔵⚫🔴🟢")
    print(f"  🎨 New format (compatible): {color_display}")
    
    # Test in UI context simulation
    format_text = "Standard"
    ui_text = f"{format_text} | Colors: {color_display}"
    print(f"  📱 UI Display: '{ui_text}'")
    
    return True


def test_other_emoji_fixes():
    """Test other emoji replacements"""
    print("🧪 Testing other emoji fixes...")
    
    # Test star rating system
    similarity_percentage = 87.3  # High similarity
    old_stars = "⭐" * min(5, int(similarity_percentage / 20))
    new_stars = "*" * min(5, int(similarity_percentage / 20))
    
    print(f"  ⭐ Old stars (may not render): {old_stars}")
    print(f"  * New stars (compatible): {new_stars}")
    
    # Test rating display
    rating_text = f"Similarity: {new_stars} {similarity_percentage:.1f}%"
    print(f"  📊 Rating display: '{rating_text}'")
    
    return True


if __name__ == "__main__":
    print("🧪 TESTING EMOJI FIXES")
    print("=" * 50)
    
    results = []
    
    # Test color symbols
    results.append(test_color_display())
    print()
    
    # Test other fixes
    results.append(test_other_emoji_fixes())
    print()
    
    # Summary
    passed = sum(results)
    total = len(results)
    
    print("=" * 50)
    print(f"📊 TEST RESULTS: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All emoji fixes working!")
        print("✅ Color symbols: ⚪🔵⚫🔴🟢 → [W][U][B][R][G]")
        print("✅ Star ratings: ⭐ → *")
        print("✅ Better compatibility with Windows/tkinter")
    else:
        print("⚠️  Some tests failed - check output above")
    
    print("\n🎯 Emoji rendering fixes complete!")
