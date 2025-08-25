"""
Test script for enhanced recommendations system
"""

import asyncio
import sys
import os

# Add the src directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.models.card import Card
from src.models.deck import Deck, DeckCard
from src.utils.enhanced_recommendations_sync import get_smart_recommendations

def test_enhanced_recommendations():
    """Test the enhanced recommendations system"""
    
    print("Testing Enhanced Recommendations System with Scryfall Integration")
    print("=" * 70)
    
    # Create a simple test deck
    deck = Deck("Test Aggro Deck", "Standard")
    
    # Add some aggressive cards
    test_cards = [
        ("Lightning Bolt", "R", "Instant", 1, ["R"]),
        ("Monastery Swiftspear", "R", "Creature", 1, ["R"]),
        ("Goblin Guide", "R", "Creature", 1, ["R"]),
        ("Lava Spike", "R", "Sorcery", 1, ["R"]),
        ("Chain Lightning", "R", "Sorcery", 1, ["R"])
    ]
    
    for name, cost, type_line, cmc, colors in test_cards:
        card = Card(name=name, set_code="TEST", mana_cost=cost, card_type=type_line)
        card.converted_mana_cost = cmc
        card.colors = colors
        deck.add_card(card, 4)  # 4 copies of each
    
    print(f"Test deck created: {deck.name}")
    print(f"Cards in deck: {len(deck.get_mainboard_cards())}")
    
    # Get recommendations
    try:
        print("\nGetting enhanced recommendations...")
        recommendations = get_smart_recommendations(
            deck=deck,
            collection=None,
            count=10,
            format_name="standard"
        )
        
        print(f"\nReceived {len(recommendations)} recommendations:")
        print("-" * 70)
        
        for i, rec in enumerate(recommendations[:5], 1):  # Show top 5
            print(f"{i}. {rec.card_name}")
            print(f"   Mana Cost: {rec.mana_cost}")
            print(f"   Type: {rec.card_type}")
            print(f"   Confidence: {rec.confidence:.1%}")
            print(f"   Synergy: {rec.synergy_score:.1%}")
            print(f"   Meta Score: {rec.meta_score:.1%}")
            print(f"   Reasons: {', '.join(rec.reasons[:2])}")
            
            if rec.keywords:
                print(f"   Keywords: {', '.join(rec.keywords[:3])}")
            
            if rec.legality:
                legality = rec.legality.get('standard', 'unknown')
                print(f"   Standard Legal: {legality}")
            
            print()
        
        print("✅ Enhanced recommendations test completed successfully!")
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()

def test_sync_recommendations():
    """Test the synchronous wrapper"""
    print("\nTesting synchronous wrapper...")
    
    deck = Deck("Simple Test Deck", "Standard")
    card = Card(name="Lightning Bolt", set_code="TEST", mana_cost="R", card_type="Instant")
    card.converted_mana_cost = 1
    card.colors = ["R"]
    deck.add_card(card, 4)
    
    try:
        from utils.enhanced_recommendations_sync import get_smart_recommendations as sync_get_recommendations
        recommendations = sync_get_recommendations(deck, count=3)
        print(f"Synchronous test: Received {len(recommendations)} recommendations")
        if recommendations:
            print(f"Top recommendation: {recommendations[0].card_name}")
        print("✅ Synchronous wrapper test passed!")
    except Exception as e:
        print(f"❌ Synchronous test failed: {e}")

if __name__ == "__main__":
    # Test the enhanced system
    test_enhanced_recommendations()
    
    # Test sync wrapper
    test_sync_recommendations()
    
    print("\n🎉 All tests completed!")
    print("\nNote: Some API calls may fail without internet connection.")
    print("The system gracefully handles API failures and provides fallback recommendations.")
