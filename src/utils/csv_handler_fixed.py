"""
CSV import/export utilities for Magic: The Gathering data
"""

import csv
import os
from typing import List, Dict, Any, Optional
from datetime import datetime

from models.card import Card
from models.deck import Deck, DeckCard
from models.collection import Collection, CollectionCard

class CSVHandler:
    """Handles CSV import and export operations"""
    
    @staticmethod
    def _safe_int(value) -> Optional[int]:
        """Safely convert value to int or return None"""
        if value and str(value).isdigit():
            return int(value)
        return None
    
    @staticmethod
    def export_collection_to_csv(collection: Collection, filepath: str):
        """Export collection to CSV file"""
        fieldnames = [
            'name', 'quantity', 'quantity_foil', 'mana_cost', 'converted_mana_cost',
            'card_type', 'creature_type', 'rarity', 'colors', 'power', 'toughness',
            'text', 'set_code', 'collector_number', 'arena_id'
        ]
        
        with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            
            for collection_card in collection.cards.values():
                card = collection_card.card
                writer.writerow({
                    'name': card.name,
                    'quantity': collection_card.quantity,
                    'quantity_foil': collection_card.quantity_foil,
                    'mana_cost': card.mana_cost,
                    'converted_mana_cost': card.converted_mana_cost,
                    'card_type': card.card_type,
                    'creature_type': card.creature_type,
                    'rarity': card.rarity,
                    'colors': ','.join(card.colors),
                    'power': card.power if card.power is not None else '',
                    'toughness': card.toughness if card.toughness is not None else '',
                    'text': card.text,
                    'set_code': card.set_code,
                    'collector_number': card.collector_number,
                    'arena_id': card.arena_id if card.arena_id is not None else ''
                })
    
    @staticmethod
    def import_collection_from_csv(filepath: str) -> Collection:
        """Import collection from CSV file"""
        collection = Collection(name=f"Imported Collection {datetime.now().strftime('%Y-%m-%d')}")
        
        with open(filepath, 'r', newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            
            for row in reader:
                # Parse card data
                card = Card(
                    name=row.get('name', ''),
                    mana_cost=row.get('mana_cost', ''),
                    converted_mana_cost=int(row.get('converted_mana_cost', 0)) if row.get('converted_mana_cost') else 0,
                    card_type=row.get('card_type', ''),
                    creature_type=row.get('creature_type', ''),
                    rarity=row.get('rarity', 'Common'),
                    colors=row.get('colors', '').split(',') if row.get('colors') else [],
                    power=CSVHandler._safe_int(row.get('power')),
                    toughness=CSVHandler._safe_int(row.get('toughness')),
                    text=row.get('text', ''),
                    set_code=row.get('set_code', ''),
                    collector_number=row.get('collector_number', ''),
                    arena_id=CSVHandler._safe_int(row.get('arena_id'))
                )
                
                # Add to collection
                quantity = int(row.get('quantity', 0)) if row.get('quantity', '').isdigit() else 0
                quantity_foil = int(row.get('quantity_foil', 0)) if row.get('quantity_foil', '').isdigit() else 0
                
                if quantity > 0 or quantity_foil > 0:
                    collection_card = CollectionCard(card, quantity, quantity_foil)
                    collection.cards[card.name] = collection_card
        
        collection.last_updated = datetime.now().isoformat()
        return collection
    
    @staticmethod
    def export_deck_to_csv(deck: Deck, filepath: str):
        """Export deck to CSV file"""
        fieldnames = [
            'name', 'quantity', 'sideboard', 'mana_cost', 'converted_mana_cost',
            'card_type', 'creature_type', 'rarity', 'colors', 'power', 'toughness',
            'text', 'set_code', 'collector_number', 'arena_id'
        ]
        
        with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            
            for deck_card in deck.cards:
                card = deck_card.card
                writer.writerow({
                    'name': card.name,
                    'quantity': deck_card.quantity,
                    'sideboard': deck_card.sideboard,
                    'mana_cost': card.mana_cost,
                    'converted_mana_cost': card.converted_mana_cost,
                    'card_type': card.card_type,
                    'creature_type': card.creature_type,
                    'rarity': card.rarity,
                    'colors': ','.join(card.colors),
                    'power': card.power if card.power is not None else '',
                    'toughness': card.toughness if card.toughness is not None else '',
                    'text': card.text,
                    'set_code': card.set_code,
                    'collector_number': card.collector_number,
                    'arena_id': card.arena_id if card.arena_id is not None else ''
                })
    
    @staticmethod
    def import_deck_from_csv(filepath: str, deck_name: Optional[str] = None) -> Deck:
        """Import deck from CSV file"""
        if not deck_name:
            deck_name = f"Imported Deck {datetime.now().strftime('%Y-%m-%d')}"
        
        deck = Deck(name=deck_name)
        
        with open(filepath, 'r', newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            
            for row in reader:
                # Parse card data
                card = Card(
                    name=row.get('name', ''),
                    mana_cost=row.get('mana_cost', ''),
                    converted_mana_cost=int(row.get('converted_mana_cost', 0)) if row.get('converted_mana_cost') else 0,
                    card_type=row.get('card_type', ''),
                    creature_type=row.get('creature_type', ''),
                    rarity=row.get('rarity', 'Common'),
                    colors=row.get('colors', '').split(',') if row.get('colors') else [],
                    power=CSVHandler._safe_int(row.get('power')),
                    toughness=CSVHandler._safe_int(row.get('toughness')),
                    text=row.get('text', ''),
                    set_code=row.get('set_code', ''),
                    collector_number=row.get('collector_number', ''),
                    arena_id=CSVHandler._safe_int(row.get('arena_id'))
                )
                
                # Add to deck
                quantity = int(row.get('quantity', 1)) if row.get('quantity', '').isdigit() else 1
                sideboard = row.get('sideboard', '').lower() in ['true', '1', 'yes']
                
                deck.cards.append(DeckCard(card, quantity, sideboard))
        
        deck.created_date = datetime.now().isoformat()
        return deck
    
    @staticmethod
    def export_deck_to_arena_format(deck: Deck, filepath: str):
        """Export deck to MTG Arena format"""
        with open(filepath, 'w', encoding='utf-8') as f:
            # Write deck name as comment
            f.write(f"// {deck.name}\n\n")
            
            # Write mainboard
            f.write("Deck\n")
            for deck_card in deck.get_mainboard_cards():
                f.write(f"{deck_card.quantity} {deck_card.card.name}\n")
            
            # Write sideboard if exists
            sideboard_cards = deck.get_sideboard_cards()
            if sideboard_cards:
                f.write("\nSideboard\n")
                for deck_card in sideboard_cards:
                    f.write(f"{deck_card.quantity} {deck_card.card.name}\n")
    
    @staticmethod
    def import_deck_from_arena_format(filepath: str, deck_name: Optional[str] = None) -> Deck:
        """Import deck from MTG Arena format"""
        if not deck_name:
            deck_name = f"Arena Import {datetime.now().strftime('%Y-%m-%d')}"
        
        deck = Deck(name=deck_name)
        is_sideboard = False
        
        with open(filepath, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                
                # Skip empty lines and comments
                if not line or line.startswith('//'):
                    continue
                
                # Check for section headers
                if line.lower() in ['deck', 'mainboard']:
                    is_sideboard = False
                    continue
                elif line.lower() == 'sideboard':
                    is_sideboard = True
                    continue
                
                # Parse card line (format: "4 Lightning Bolt")
                parts = line.split(' ', 1)
                if len(parts) == 2 and parts[0].isdigit():
                    quantity = int(parts[0])
                    card_name = parts[1]
                    
                    # Create basic card (would need card database for full info)
                    card = Card(name=card_name)
                    deck.cards.append(DeckCard(card, quantity, is_sideboard))
        
        deck.created_date = datetime.now().isoformat()
        return deck
