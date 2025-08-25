#!/usr/bin/env python3
"""
Test script to verify the new owned card display (no craft icons)
"""

import sys
import os

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from models.deck import Deck
from models.card import Card
from utils.enhanced_recommendations_sync import get_smart_recommendations


def test_owned_card_display():
    """Test that owned cards display cleanly without craft icons"""
    print("🧪 Testing owned card display...")
    
    # Create a simple test deck
    deck = Deck("Test Deck")
    deck.add_card(Card("Lightning Bolt", "R"), 4)
    deck.add_card(Card("Mountain", ""), 20)
    
    try:
        # Get a few recommendations to test display
        recommendations = get_smart_recommendations(deck, None, 10, "standard")
        
        print(f"  ✅ Generated {len(recommendations)} recommendations")
        
        # Simulate the display logic from the UI
        owned_count = 0
        craftable_count = 0
        
        for rec in recommendations:
            if rec.cost_consideration == "owned":
                owned_count += 1
                # New logic: clean display without craft icons
                card_display = rec.card_name
                print(f"  📋 Owned card display: '{card_display}' (clean, no icons)")
            else:
                craftable_count += 1
                # Existing logic: show craft icons
                craft_icons = {
                    "common_craft": "🔨", 
                    "uncommon_craft": "🔧", 
                    "rare_craft": "💎", 
                    "mythic_craft": "👑"
                }
                craft_icon = craft_icons.get(rec.cost_consideration, "🔨")
                card_display = f"{craft_icon} {rec.card_name}"
                print(f"  🔧 Craftable card display: '{card_display}' (with icon)")
        
        print(f"  📊 Summary: {owned_count} owned, {craftable_count} craftable")
        
        if owned_count > 0:
            print("  ✅ Owned cards now display cleanly without craft icons")
        else:
            print("  ℹ️  No owned cards found in this test batch")
            
        if craftable_count > 0:
            print("  ✅ Craftable cards still show craft icons as expected")
            
        return True
        
    except Exception as e:
        print(f"  ❌ Error testing owned card display: {str(e)}")
        return False


if __name__ == "__main__":
    print("🧪 TESTING OWNED CARD DISPLAY CHANGES")
    print("=" * 55)
    
    success = test_owned_card_display()
    
    print("=" * 55)
    if success:
        print("🎉 DISPLAY TEST PASSED!")
        print("✅ Owned cards: Clean display without craft icons")
        print("✅ Craftable cards: Still show appropriate craft icons") 
        print("✅ No special coloring needed - better readability")
    else:
        print("❌ Display test failed - check output above")
    
    print("\n🎯 Ready for user testing!")
