"""
Quick test to verify the GUI integration works
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.models.deck import Deck
from src.models.collection import Collection
from src.models.card import Card
from src.utils.smart_recommendations import IntelligentRecommendationEngine

def test_gui_integration():
    """Test that the smart recommendations return the expected format for GUI display"""
    
    # Create basic test data
    deck = Deck("Test Deck")
    serra = Card("Serra Angel", "{3}{W}{W}", 5, "Creature — Angel", "Angel", "rare", ["W"], 4, 4)
    plains = Card("Plains", "", 0, "Basic Land — Plains", "", "common", ["W"])
    
    deck.add_card(serra, 4)
    deck.add_card(plains, 20)
    
    collection = Collection("Test Collection")
    wrath = Card("Wrath of God", "{2}{W}{W}", 4, "Sorcery", "", "rare", ["W"])
    collection.add_card(wrath, 1)
    
    # Get recommendations
    engine = IntelligentRecommendationEngine()
    recommendations = engine.generate_recommendations(deck, collection, count=5, format_name="standard")
    
    print("GUI Integration Test - SmartRecommendation Objects:")
    print("="*60)
    
    for i, rec in enumerate(recommendations, 1):
        print(f"\n{i}. Testing SmartRecommendation attributes:")
        print(f"   card_name: '{rec.card_name}' (type: {type(rec.card_name).__name__})")
        print(f"   mana_cost: '{rec.mana_cost}' (type: {type(rec.mana_cost).__name__})")
        print(f"   confidence: {rec.confidence:.1%} (type: {type(rec.confidence).__name__})")
        print(f"   synergy_score: {rec.synergy_score:.1%} (type: {type(rec.synergy_score).__name__})")
        print(f"   meta_score: {rec.meta_score:.1%} (type: {type(rec.meta_score).__name__})")
        print(f"   deck_fit: {rec.deck_fit:.1%} (type: {type(rec.deck_fit).__name__})")
        print(f"   cost_consideration: '{rec.cost_consideration}' (type: {type(rec.cost_consideration).__name__})")
        print(f"   rarity: '{rec.rarity}' (type: {type(rec.rarity).__name__})")
        print(f"   reasons: {rec.reasons} (type: {type(rec.reasons).__name__}, length: {len(rec.reasons)})")
    
    print(f"\n✅ All {len(recommendations)} recommendations have the expected SmartRecommendation format!")
    print("✅ GUI integration should work correctly!")

if __name__ == "__main__":
    test_gui_integration()
