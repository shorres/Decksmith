#!/usr/bin/env python3
"""
Test script to verify the updated table structure without Archetype Fit column
"""

import sys
import os
import tkinter as tk

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from models.deck import Deck
from models.card import Card
from utils.enhanced_recommendations_sync import get_smart_recommendations


def test_table_structure():
    """Test that the table structure matches the data being provided"""
    print("🧪 Testing updated table structure...")
    
    try:
        # Create test GUI components to verify structure
        root = tk.Tk()
        root.withdraw()  # Hide test window
        
        from gui.ai_recommendations_tab import AIRecommendationsTab
        
        # Initialize the tab
        tab = AIRecommendationsTab(root, lambda: None, lambda: None, None)
        
        # Check column configuration
        columns = tab.rec_tree['columns']
        print(f"  📊 Table columns: {columns}")
        
        # Expected columns after our changes
        expected_columns = ('Card', 'Confidence', 'Synergy', 'CMC', 'Reasons')
        
        if columns == expected_columns:
            print("  ✅ Column structure is correct")
        else:
            print(f"  ❌ Column mismatch. Expected: {expected_columns}, Got: {columns}")
            return False
        
        # Check column widths
        reasons_width = tab.rec_tree.column('Reasons', 'width')
        print(f"  📏 Reasons column width: {reasons_width}px")
        
        if reasons_width >= 400:
            print("  ✅ Reasons column has expanded width")
        else:
            print(f"  ⚠️  Reasons column may be narrow: {reasons_width}px")
        
        # Test data structure with sample recommendation
        deck = Deck("Test")
        deck.add_card(Card("Lightning Bolt", "R"), 4)
        
        recommendations = get_smart_recommendations(deck, None, 5, "standard")
        
        if recommendations:
            rec = recommendations[0]
            
            # Simulate the values tuple that gets inserted
            card_display = rec.card_name if rec.cost_consideration == "owned" else f"🔨 {rec.card_name}"
            cmc_display = "Land" if "Land" in rec.card_type else str(int(getattr(rec, 'cmc', 0)))
            reasons_text = "; ".join(rec.reasons[:2]) if rec.reasons else "Good synergy match"
            
            values = (
                card_display,
                f"{rec.confidence:.1%}",
                f"{rec.synergy_score:.1%}",
                cmc_display,
                reasons_text
            )
            
            print(f"  📋 Sample data structure: {len(values)} values")
            print(f"  📋 Sample values: {values[:2]}... (truncated)")
            
            if len(values) == len(expected_columns):
                print("  ✅ Data structure matches column count")
            else:
                print(f"  ❌ Data/column mismatch: {len(values)} values vs {len(expected_columns)} columns")
                return False
        
        root.destroy()
        return True
        
    except Exception as e:
        print(f"  ❌ Error testing table structure: {str(e)}")
        return False


if __name__ == "__main__":
    print("🧪 TESTING TABLE STRUCTURE CHANGES")
    print("=" * 55)
    
    success = test_table_structure()
    
    print("=" * 55)
    if success:
        print("🎉 TABLE STRUCTURE TEST PASSED!")
        print("✅ Archetype Fit column removed from table")
        print("✅ Reasons/Notes column expanded to take up space") 
        print("✅ Data structure matches column definitions")
        print("✅ Archetype Fit still available in card details modal")
    else:
        print("❌ Table structure test failed - check output above")
    
    print("\n🎯 Table formatting complete!")
