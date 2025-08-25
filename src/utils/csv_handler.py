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
from utils.scryfall_api import ScryfallAPI

class CSVHandler:
    """Handles CSV import and export operations"""
    
    def __init__(self):
        """Initialize CSV handler with Scryfall API"""
        self.scryfall_api = ScryfallAPI()
    
    def _create_enriched_card(self, name: str, existing_data: Optional[Dict[str, Any]] = None) -> Card:
        """
        Create a Card object enriched with Scryfall data when possible
        
        Args:
            name: Card name
            existing_data: Dictionary of existing card data from CSV
            
        Returns:
            Card object with enriched data from Scryfall or basic data
        """
        # Try to get card data from Scryfall
        scryfall_card = self.scryfall_api.get_card_fuzzy(name)
        
        if scryfall_card:
            print(f"✓ Enriched '{name}' with Scryfall data")
            # Use Scryfall data as primary source, fall back to existing data
            return Card(
                name=scryfall_card.name,
                mana_cost=scryfall_card.mana_cost,
                converted_mana_cost=int(scryfall_card.cmc),
                card_type=scryfall_card.type_line,
                creature_type=self._extract_creature_types(scryfall_card.type_line),
                rarity=scryfall_card.rarity,
                colors=scryfall_card.colors,
                power=int(scryfall_card.power) if scryfall_card.power and scryfall_card.power.isdigit() else None,
                toughness=int(scryfall_card.toughness) if scryfall_card.toughness and scryfall_card.toughness.isdigit() else None,
                text=scryfall_card.oracle_text,
                set_code=scryfall_card.set_code,
                collector_number=scryfall_card.collector_number,
                arena_id=existing_data.get('arena_id') if existing_data else None  # Keep existing Arena ID if available
            )
        else:
            print(f"⚠ Could not find '{name}' in Scryfall, using basic data")
            # Fall back to creating card from existing data or minimal info
            if existing_data:
                return Card(
                    name=existing_data.get('name', name),
                    mana_cost=existing_data.get('mana_cost', ''),
                    converted_mana_cost=int(existing_data.get('converted_mana_cost', 0)) if existing_data.get('converted_mana_cost') else 0,
                    card_type=existing_data.get('card_type', ''),
                    creature_type=existing_data.get('creature_type', ''),
                    rarity=existing_data.get('rarity', 'Common'),
                    colors=existing_data.get('colors', '').split(',') if existing_data.get('colors') else [],
                    power=self._safe_int(existing_data.get('power')),
                    toughness=self._safe_int(existing_data.get('toughness')),
                    text=existing_data.get('text', ''),
                    set_code=existing_data.get('set_code', ''),
                    collector_number=existing_data.get('collector_number', ''),
                    arena_id=self._safe_int(existing_data.get('arena_id'))
                )
            else:
                # Minimal card with just the name
                return Card(name=name)
    
    def _extract_creature_types(self, type_line: str) -> str:
        """Extract creature types from type line"""
        if '—' in type_line:
            # Split on em dash and take the part after it
            parts = type_line.split('—', 1)
            if len(parts) > 1:
                return parts[1].strip()
        return ''
    
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
    
    def import_collection_from_csv(self, filepath: str) -> Collection:
        """Import collection from CSV file with Scryfall auto-enrichment"""
        collection = Collection(name=f"Imported Collection {datetime.now().strftime('%Y-%m-%d')}")
        
        print(f"Importing collection from {filepath} with Scryfall enrichment...")
        
        with open(filepath, 'r', newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            
            for row in reader:
                card_name = row.get('name', '').strip()
                if not card_name:
                    continue
                
                # Create enriched card with Scryfall data
                card = self._create_enriched_card(card_name, row)
                
                # Add to collection
                quantity = int(row.get('quantity', 0)) if row.get('quantity', '').isdigit() else 0
                quantity_foil = int(row.get('quantity_foil', 0)) if row.get('quantity_foil', '').isdigit() else 0
                
                if quantity > 0 or quantity_foil > 0:
                    collection_card = CollectionCard(card, quantity, quantity_foil)
                    collection.cards[card.name] = collection_card
        
        collection.last_updated = datetime.now().isoformat()
        print(f"✓ Collection import complete with {len(collection.cards)} cards")
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
    
    def import_deck_from_csv(self, filepath: str, deck_name: Optional[str] = None) -> Deck:
        """Import deck from CSV file with Scryfall auto-enrichment"""
        if not deck_name:
            deck_name = f"Imported Deck {datetime.now().strftime('%Y-%m-%d')}"
        
        deck = Deck(name=deck_name)
        
        print(f"Importing deck from {filepath} with Scryfall enrichment...")
        
        with open(filepath, 'r', newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            
            for row in reader:
                card_name = row.get('name', '').strip()
                if not card_name:
                    continue
                
                # Create enriched card with Scryfall data
                card = self._create_enriched_card(card_name, row)
                
                # Add to deck
                quantity = int(row.get('quantity', 1)) if row.get('quantity', '').isdigit() else 1
                sideboard = row.get('sideboard', '').lower() in ['true', '1', 'yes']
                
                deck.cards.append(DeckCard(card, quantity, sideboard))
        
        deck.created_date = datetime.now().isoformat()
        print(f"✓ Deck import complete with {len(deck.cards)} cards")
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
    
    def import_deck_from_arena_format(self, filepath: str, deck_name: Optional[str] = None) -> Deck:
        """Import deck from MTG Arena format with Scryfall auto-enrichment"""
        if not deck_name:
            deck_name = f"Arena Import {datetime.now().strftime('%Y-%m-%d')}"
        
        deck = Deck(name=deck_name)
        is_sideboard = False
        
        print(f"Importing Arena deck from {filepath} with Scryfall enrichment...")
        
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
                    
                    # Create enriched card with Scryfall data
                    card = self._create_enriched_card(card_name)
                    deck.cards.append(DeckCard(card, quantity, is_sideboard))
        
        deck.created_date = datetime.now().isoformat()
        print(f"✓ Arena deck import complete with {len(deck.cards)} cards")
        return deck
