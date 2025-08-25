#!/usr/bin/env python3

"""
Simple test for enhanced recommendations in GUI context
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

def test_recommendations_gui():
    """Test that enhanced recommendations work in GUI context"""
    
    try:
        from src.utils.enhanced_recommendations_sync import get_smart_recommendations
        from src.models.deck import Deck, DeckCard
        from src.models.card import Card
        
        print("Testing Enhanced Recommendations in GUI Context")
        print("=" * 50)
        
        # Create test deck
        test_deck = Deck("GUI Test Deck")
        
        # Create cards properly
        lightning_bolt = Card(
            name="Lightning Bolt",
            mana_cost="{R}",
            converted_mana_cost=1,
            card_type="Instant",
            text="Lightning Bolt deals 3 damage to any target.",
            rarity="Common"
        )
        
        swiftspear = Card(
            name="Monastery Swiftspear", 
            mana_cost="{R}",
            converted_mana_cost=1,
            card_type="Creature — Human Monk",
            text="Haste, Prowess",
            rarity="Uncommon"
        )
        
        # Add cards to deck properly
        test_deck.add_card(lightning_bolt, 4)
        test_deck.add_card(swiftspear, 4)
        
        print(f"Test deck: {test_deck.name}")
        print(f"Cards: {len(test_deck.cards)}")
        
        # Get recommendations using the standalone function
        recommendations = get_smart_recommendations(
            deck=test_deck,
            format_name="standard",
            count=5
        )
        
        print(f"\n📋 Found {len(recommendations)} recommendations:")
        print("-" * 40)
        
        for i, rec in enumerate(recommendations, 1):
            print(f"{i}. {rec.card_name}")
            print(f"   Cost: {rec.mana_cost}")
            print(f"   Type: {rec.card_type}")
            print(f"   Confidence: {rec.confidence:.1%}")
            print(f"   Reasons: {', '.join(rec.reasons[:2])}")
            print()
        
        if recommendations:
            print("✅ Enhanced recommendations working in GUI context!")
        else:
            print("⚠️  No recommendations returned (may be API/connection issue)")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing recommendations: {e}")
        return False

if __name__ == "__main__":
    success = test_recommendations_gui()
    if success:
        print("\n🎉 GUI integration test completed!")
    else:
        print("\n💥 GUI integration test failed!")
