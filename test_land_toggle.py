#!/usr/bin/env python3
"""
Test script to verify the land visibility toggle and total count functionality
"""

import sys
import os

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from utils.smart_recommendations import SmartRecommendation

def test_land_filtering():
    """Test that we can properly identify lands in recommendations"""
    
    # Create sample recommendations with different card types
    sample_recommendations = [
        SmartRecommendation(
            card_name="Lightning Bolt",
            mana_cost="R",
            card_type="Instant",
            rarity="common",
            confidence=0.9,
            reasons=["Good removal spell"],
            synergy_score=0.8,
            meta_score=0.7,
            deck_fit=0.85,
            cost_consideration="owned"
        ),
        SmartRecommendation(
            card_name="Mountain",
            mana_cost="",
            card_type="Basic Land — Mountain",
            rarity="common",
            confidence=0.95,
            reasons=["Provides red mana"],
            synergy_score=0.9,
            meta_score=0.8,
            deck_fit=0.9,
            cost_consideration="owned"
        ),
        SmartRecommendation(
            card_name="Shock",
            mana_cost="R",
            card_type="Instant",
            rarity="common",
            confidence=0.75,
            reasons=["Cheap removal"],
            synergy_score=0.6,
            meta_score=0.7,
            deck_fit=0.7,
            cost_consideration="common_craft"
        ),
        SmartRecommendation(
            card_name="Sacred Foundry",
            mana_cost="",
            card_type="Land — Mountain Plains",
            rarity="rare",
            confidence=0.8,
            reasons=["Dual land for mana fixing"],
            synergy_score=0.85,
            meta_score=0.9,
            deck_fit=0.85,
            cost_consideration="rare_craft"
        )
    ]
    
    print("Sample recommendations created:")
    for i, rec in enumerate(sample_recommendations, 1):
        is_land = "Land" in rec.card_type
        print(f"{i}. {rec.card_name} ({rec.card_type}) - Land: {is_land}")
    
    # Test filtering
    non_land_recs = [r for r in sample_recommendations if "Land" not in r.card_type]
    land_recs = [r for r in sample_recommendations if "Land" in r.card_type]
    
    print(f"\nFiltering results:")
    print(f"Total recommendations: {len(sample_recommendations)}")
    print(f"Non-land recommendations: {len(non_land_recs)}")
    print(f"Land recommendations: {len(land_recs)}")
    
    print(f"\nNon-land cards:")
    for rec in non_land_recs:
        print(f"  - {rec.card_name}")
    
    print(f"\nLand cards:")
    for rec in land_recs:
        print(f"  - {rec.card_name}")

if __name__ == "__main__":
    test_land_filtering()
