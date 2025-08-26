#!/usr/bin/env python3
"""
Test script to verify collection persistence issue
"""
import os
import sys
import json
import tkinter as tk

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from models.collection import Collection
from models.card import Card
from gui.collection_tab import CollectionTab

def test_collection_persistence_issue():
    """Test collection persistence with GUI simulation"""
    print("Testing collection persistence issue...")
    
    # Create a minimal tkinter setup
    root = tk.Tk()
    root.withdraw()  # Hide the window
    
    try:
        # Create collection tab
        collection_tab = CollectionTab(root)
        
        print(f"Initial collection has {len(collection_tab.collection.cards)} cards")
        
        # Add some test cards
        test_cards = [
            Card(name="Lightning Bolt", mana_cost="{R}", card_type="Instant", rarity="Common"),
            Card(name="Counterspell", mana_cost="{1}{U}", card_type="Instant", rarity="Common"),
            Card(name="Giant Growth", mana_cost="{G}", card_type="Instant", rarity="Common"),
        ]
        
        for card in test_cards:
            collection_tab.collection.add_card(card, 4)
        
        print(f"After adding cards, collection has {len(collection_tab.collection.cards)} cards")
        
        # Save collection explicitly
        collection_tab.save_collection()
        
        print("Collection saved. Checking file exists...")
        collection_file = os.path.join("data", "collections", "default.json")
        
        if os.path.exists(collection_file):
            # Read the file back
            with open(collection_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            loaded_collection = Collection.from_dict(data)
            print(f"File exists and contains {len(loaded_collection.cards)} cards")
            
            # Test the save/load cycle
            print("\nTesting save/load cycle:")
            print(f"Original collection cards: {list(collection_tab.collection.cards.keys())}")
            print(f"Loaded collection cards: {list(loaded_collection.cards.keys())}")
            
            return len(loaded_collection.cards) == 3
        else:
            print("❌ Collection file was not created!")
            return False
            
    except Exception as e:
        print(f"Error during test: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        root.destroy()

def check_existing_collection():
    """Check what's in the existing collection file"""
    collection_file = os.path.join("data", "collections", "default.json")
    
    if os.path.exists(collection_file):
        print(f"\nExisting collection file found: {collection_file}")
        try:
            with open(collection_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            collection = Collection.from_dict(data)
            print(f"Existing collection has {len(collection.cards)} cards")
            
            if collection.cards:
                print("Cards in collection:")
                for name, collection_card in collection.cards.items():
                    print(f"  - {name}: {collection_card.quantity} regular, {collection_card.quantity_foil} foil")
            else:
                print("Collection is empty")
                
        except Exception as e:
            print(f"Error reading existing collection: {e}")
    else:
        print("No existing collection file found")

if __name__ == "__main__":
    print("=== Collection Persistence Investigation ===\n")
    
    check_existing_collection()
    success = test_collection_persistence_issue()
    
    print(f"\n=== Results ===")
    print(f"Collection persistence test: {'✓ PASS' if success else '✗ FAIL'}")
    
    if not success:
        print("\nPossible causes:")
        print("1. Collection not being saved properly")
        print("2. File permissions issue")  
        print("3. Collection being cleared after save")
        print("4. Built app using old version without fixes")
