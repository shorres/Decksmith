#!/usr/bin/env python3
"""
Test script for the lazy loading recommendation system
"""

import sys
sys.path.insert(0, 'src')

from models.deck import Deck, DeckCard
from models.card import Card
from utils.enhanced_recommendations_sync import get_smart_recommendations

def test_lazy_loading():
    """Test the lazy loading recommendation system"""
    print("🔬 Testing Lazy Loading Recommendation System")
    print("=" * 50)
    
    # Create a simple test deck
    test_deck = Deck("Test Deck", "Standard")
    
    # Add some cards to create a meaningful deck
    cards = [
        ("Lightning Bolt", "R", "Instant", "uncommon", 4),
        ("Mountain", "", "Basic Land — Mountain", "common", 10),
        ("Monastery Swiftspear", "R", "Creature — Human Monk", "uncommon", 4),
        ("Shock", "R", "Instant", "common", 2),
    ]
    
    for name, mana_cost, card_type, rarity, quantity in cards:
        card = Card(name=name, mana_cost=mana_cost, card_type=card_type, rarity=rarity)
        test_deck.add_card(card, quantity, False)  # mainboard
    
    print(f"📋 Test Deck: {test_deck.name}")
    print(f"   Cards: {sum(card.quantity for card in test_deck.get_mainboard_cards())}")
    print(f"   Colors: {', '.join(test_deck.get_color_distribution().keys())}")
    print()
    
    # Test different batch sizes
    batch_sizes = [50, 100, 200]
    
    for batch_size in batch_sizes:
        print(f"🔄 Testing batch size: {batch_size}")
        try:
            recommendations = get_smart_recommendations(
                test_deck, 
                collection=None, 
                count=batch_size, 
                format_name="Standard"
            )
            
            print(f"   ✅ Generated: {len(recommendations)} recommendations")
            
            # Show top 5 recommendations
            print(f"   🏆 Top 5 recommendations:")
            for i, rec in enumerate(recommendations[:5], 1):
                print(f"      {i}. {rec.card_name} ({rec.confidence:.1%} confidence)")
            
            # Check for variety in card types
            card_types = set()
            for rec in recommendations:
                card_types.add(rec.card_type.split()[0])  # Get first word of card type
            
            print(f"   📊 Card type variety: {len(card_types)} types ({', '.join(sorted(card_types)[:5])})")
            
        except Exception as e:
            print(f"   ❌ Error: {str(e)}")
        
        print()
    
    # Test randomization by generating multiple batches
    print("🎲 Testing randomization (generating 3 batches of 50):")
    all_cards = set()
    
    for i in range(3):
        try:
            batch = get_smart_recommendations(
                test_deck, 
                collection=None, 
                count=50, 
                format_name="Standard",
                randomize=True
            )
            
            batch_cards = set(rec.card_name for rec in batch)
            overlap_with_previous = len(batch_cards & all_cards)
            unique_new_cards = len(batch_cards - all_cards)
            
            print(f"   Batch {i+1}: {len(batch)} cards, {unique_new_cards} new, {overlap_with_previous} overlap")
            
            all_cards.update(batch_cards)
            
        except Exception as e:
            print(f"   Batch {i+1}: Error - {str(e)}")
    
    print(f"\n🎯 Total unique cards across all batches: {len(all_cards)}")
    print("\n✅ Lazy loading test complete!")

if __name__ == "__main__":
    test_lazy_loading()
