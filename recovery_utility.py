"""
Magic Tool - Collection Recovery Utility
Helps users recover from collection data loss after the persistence bug fix.
"""

import json
import os
import sys
from pathlib import Path

def get_app_data_dir():
    """Get the application data directory"""
    # Get the directory where this script is located
    if getattr(sys, 'frozen', False):
        # If running from PyInstaller bundle
        app_dir = os.path.dirname(sys.executable)
    else:
        # If running from source
        app_dir = os.path.dirname(os.path.abspath(__file__))
    
    return os.path.join(app_dir, "data")

def check_data_integrity():
    """Check the integrity of collection and deck data"""
    data_dir = get_app_data_dir()
    
    print("=== Magic Tool Data Integrity Check ===\n")
    
    # Check collections
    collections_dir = os.path.join(data_dir, "collections")
    collection_file = os.path.join(collections_dir, "default.json")
    
    print("📁 Collection Data:")
    if os.path.exists(collection_file):
        try:
            with open(collection_file, 'r', encoding='utf-8') as f:
                collection_data = json.load(f)
            card_count = len(collection_data.get('cards', []))
            print(f"  ✅ Collection file exists: {collection_file}")
            print(f"  📊 Cards in collection: {card_count}")
            if card_count == 0:
                print("  ⚠️  WARNING: Collection is empty!")
            else:
                print("  ✅ Collection has data")
        except Exception as e:
            print(f"  ❌ Error reading collection file: {e}")
    else:
        print(f"  ❌ Collection file missing: {collection_file}")
        print("  📝 This will be created when you add your first card")
    
    # Check decks
    decks_dir = os.path.join(data_dir, "decks")
    print(f"\n📁 Deck Data:")
    if os.path.exists(decks_dir):
        deck_files = [f for f in os.listdir(decks_dir) if f.endswith('.json')]
        print(f"  ✅ Decks directory exists: {decks_dir}")
        print(f"  📊 Deck files found: {len(deck_files)}")
        
        total_cards = 0
        for deck_file in deck_files:
            deck_path = os.path.join(decks_dir, deck_file)
            try:
                with open(deck_path, 'r', encoding='utf-8') as f:
                    deck_data = json.load(f)
                deck_cards = len(deck_data.get('cards', []))
                total_cards += deck_cards
                print(f"    📋 {deck_file}: {deck_cards} cards")
            except Exception as e:
                print(f"    ❌ Error reading {deck_file}: {e}")
        
        print(f"  📊 Total cards across all decks: {total_cards}")
    else:
        print(f"  ❌ Decks directory missing: {decks_dir}")
    
    # Check cache
    cache_dir = os.path.join(data_dir, "cache")
    cache_file = os.path.join(cache_dir, "card_data.json")
    print(f"\n📁 Cache Data:")
    if os.path.exists(cache_file):
        try:
            with open(cache_file, 'r', encoding='utf-8') as f:
                cache_data = json.load(f)
            cached_cards = len(cache_data)
            print(f"  ✅ Cache file exists: {cache_file}")
            print(f"  📊 Cached cards: {cached_cards}")
            if cached_cards > 0:
                print("  💡 These cards were recently viewed and might help with recovery")
        except Exception as e:
            print(f"  ❌ Error reading cache file: {e}")
    else:
        print(f"  ❌ Cache file missing: {cache_file}")

def suggest_recovery_options():
    """Suggest recovery options based on available data"""
    data_dir = get_app_data_dir()
    
    print("\n=== Recovery Suggestions ===\n")
    
    # Check if we have deck data but no collection data
    collections_dir = os.path.join(data_dir, "collections")
    decks_dir = os.path.join(data_dir, "decks")
    cache_dir = os.path.join(data_dir, "cache")
    
    collection_file = os.path.join(collections_dir, "default.json")
    has_collection = os.path.exists(collection_file)
    
    collection_cards = 0
    if has_collection:
        try:
            with open(collection_file, 'r', encoding='utf-8') as f:
                collection_data = json.load(f)
            collection_cards = len(collection_data.get('cards', []))
        except:
            pass
    
    # Count deck cards
    deck_cards = 0
    unique_deck_cards = set()
    if os.path.exists(decks_dir):
        for deck_file in os.listdir(decks_dir):
            if deck_file.endswith('.json'):
                try:
                    deck_path = os.path.join(decks_dir, deck_file)
                    with open(deck_path, 'r', encoding='utf-8') as f:
                        deck_data = json.load(f)
                    for card in deck_data.get('cards', []):
                        deck_cards += card.get('quantity', 1)
                        unique_deck_cards.add(card.get('name', ''))
                except:
                    pass
    
    if deck_cards > 0 and collection_cards == 0:
        print("🔍 SCENARIO: You have deck data but lost collection data")
        print(f"   📊 Total cards in decks: {deck_cards}")
        print(f"   📊 Unique cards in decks: {len(unique_deck_cards)}")
        print("\n💡 Recovery Options:")
        print("   1. Manually re-add important cards to your collection")
        print("   2. Export deck data and re-import as collection")
        print("   3. Use the 'Import from Deck' feature if available")
        
    elif collection_cards > 0:
        print("✅ GOOD NEWS: Your collection data appears intact")
        print(f"   📊 Collection has {collection_cards} cards")
        
    else:
        print("❌ SCENARIO: Both collection and deck data appear to be missing")
        print("\n💡 Recovery Options:")
        print("   1. Start fresh - the fixed version will properly save your data")
        print("   2. Check if you have any CSV exports or backups")
        print("   3. Re-import any existing deck lists you might have")
    
    # Check cache for potential recovery
    cache_file = os.path.join(cache_dir, "card_data.json")
    if os.path.exists(cache_file):
        try:
            with open(cache_file, 'r', encoding='utf-8') as f:
                cache_data = json.load(f)
            if len(cache_data) > 0:
                print(f"\n💡 CACHE RECOVERY: Found {len(cache_data)} cards in cache")
                print("   These were recently viewed and might include your collection cards")
                print("   You can manually add these back to your collection")
        except:
            pass

def main():
    """Main recovery utility"""
    print("Magic Tool - Collection Recovery Utility")
    print("="*50)
    
    # Check if we're in the right directory
    if not os.path.exists("main.py") and not os.path.exists("Magic Tool.exe"):
        print("❌ This script should be run from the Magic Tool directory")
        print("   Please navigate to the directory containing Magic Tool")
        input("\nPress Enter to exit...")
        return
    
    check_data_integrity()
    suggest_recovery_options()
    
    print(f"\n{'='*50}")
    print("✅ IMPORTANT: Make sure you're using the FIXED version of Magic Tool!")
    print("   The latest build includes complete collection persistence fixes.")
    print("   After using the fixed version, your data will be properly saved.")
    
    input("\nPress Enter to exit...")

if __name__ == "__main__":
    main()
