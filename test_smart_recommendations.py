#!/usr/bin/env python3
"""
Test script to verify smart recommendations functionality
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.models.deck import Deck
from src.models.collection import Collection
from src.models.card import Card
from src.utils.smart_recommendations import IntelligentRecommendationEngine

def test_smart_recommendations():
    print("Testing Smart Recommendations Engine...")
    
    # Create test deck
    deck = Deck("Test Angels Deck")
    
    # Add some angel-themed cards to test the recommendations
    test_cards = [
        Card("Serra Angel", "{3}{W}{W}", 5, "Creature — Angel", "Angel", "rare", ["W"], 4, 4),
        Card("Angel of Mercy", "{4}{W}", 5, "Creature — Angel", "Angel", "uncommon", ["W"], 3, 3),
        Card("Plains", "", 0, "Basic Land — Plains", "", "common", ["W"]),
        Card("Lightning Bolt", "{R}", 1, "Instant", "", "common", ["R"])
    ]
    
    deck.add_card(test_cards[0], 4)  # Serra Angel x4
    deck.add_card(test_cards[1], 2)  # Angel of Mercy x2
    deck.add_card(test_cards[2], 20)  # Plains x20
    deck.add_card(test_cards[3], 4)  # Lightning Bolt x4
    
    # Create test collection
    collection = Collection("Test Collection")
    baneslayer = Card("Baneslayer Angel", "{3}{W}{W}", 5, "Creature — Angel", "Angel", "mythic", ["W"], 5, 5)
    wrath = Card("Wrath of God", "{2}{W}{W}", 4, "Sorcery", "", "rare", ["W"])
    
    collection.add_card(baneslayer, 2)
    collection.add_card(wrath, 1)
    
    # Create engine and get recommendations
    engine = IntelligentRecommendationEngine()
    recommendations = engine.generate_recommendations(deck, collection, count=10, format_name="standard")
    
    print(f"\nGenerated {len(recommendations)} recommendations:")
    print("=" * 60)
    
    for i, rec in enumerate(recommendations, 1):
        print(f"{i}. {rec.card_name} ({rec.mana_cost})")
        print(f"   Confidence: {rec.confidence:.1%} | Synergy: {rec.synergy_score:.1%} | Meta: {rec.meta_score:.1%}")
        print(f"   Status: {rec.cost_consideration}")
        print(f"   Reasons: {', '.join(rec.reasons[:2])}")
        print()

if __name__ == "__main__":
    test_smart_recommendations()
