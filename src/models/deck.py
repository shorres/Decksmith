"""
Deck model for Magic: The Gathering decks
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional
from collections import Counter
import json

from .card import Card

@dataclass
class DeckCard:
    """Represents a card in a deck with quantity"""
    card: Card
    quantity: int = 1
    sideboard: bool = False

@dataclass
class Deck:
    """Represents a Magic: The Gathering deck"""
    name: str
    format: str = "Standard"
    cards: List[DeckCard] = field(default_factory=list)
    description: str = ""
    created_date: Optional[str] = None
    last_modified: Optional[str] = None
    
    def add_card(self, card: Card, quantity: int = 1, sideboard: bool = False):
        """Add a card to the deck"""
        # Check if card already exists in deck
        for deck_card in self.cards:
            if deck_card.card.name == card.name and deck_card.sideboard == sideboard:
                deck_card.quantity += quantity
                return
        
        # Add new card
        self.cards.append(DeckCard(card, quantity, sideboard))
    
    def remove_card(self, card_name: str, quantity: int = 1, sideboard: bool = False):
        """Remove cards from the deck"""
        for i, deck_card in enumerate(self.cards):
            if deck_card.card.name == card_name and deck_card.sideboard == sideboard:
                deck_card.quantity -= quantity
                if deck_card.quantity <= 0:
                    self.cards.pop(i)
                break
    
    def get_total_cards(self, include_sideboard: bool = False) -> int:
        """Get total number of cards in deck"""
        return sum(
            card.quantity for card in self.cards 
            if include_sideboard or not card.sideboard
        )
    
    def get_mainboard_cards(self) -> List[DeckCard]:
        """Get mainboard cards only"""
        return [card for card in self.cards if not card.sideboard]
    
    def get_sideboard_cards(self) -> List[DeckCard]:
        """Get sideboard cards only"""
        return [card for card in self.cards if card.sideboard]
    
    def get_color_distribution(self) -> Dict[str, int]:
        """Get color distribution of the deck"""
        color_count = Counter()
        
        for deck_card in self.get_mainboard_cards():
            for color in deck_card.card.colors:
                color_count[color] += deck_card.quantity
        
        return dict(color_count)
    
    def get_mana_curve(self) -> Dict[int, int]:
        """Get mana curve of the deck"""
        curve = Counter()
        
        for deck_card in self.get_mainboard_cards():
            cmc = deck_card.card.converted_mana_cost
            if cmc >= 7:
                cmc = 7  # Group 7+ together
            curve[cmc] += deck_card.quantity
        
        return dict(curve)
    
    def get_type_distribution(self) -> Dict[str, int]:
        """Get card type distribution"""
        type_count = Counter()
        
        for deck_card in self.get_mainboard_cards():
            # Extract primary type
            card_type = deck_card.card.card_type.split()[0] if deck_card.card.card_type else "Unknown"
            type_count[card_type] += deck_card.quantity
        
        return dict(type_count)
    
    def is_legal_format(self, format_name: Optional[str] = None) -> bool:
        """Check if deck is legal in specified format"""
        format_name = format_name or self.format
        
        # Basic legality checks
        mainboard_count = self.get_total_cards(include_sideboard=False)
        sideboard_count = len(self.get_sideboard_cards())
        
        if format_name.lower() in ["standard", "historic", "explorer"]:
            if mainboard_count < 60:
                return False
            if sideboard_count > 15:
                return False
        
        # Check card limits (simplified - doesn't account for basic lands)
        card_counts = Counter()
        for deck_card in self.cards:
            card_counts[deck_card.card.name] += deck_card.quantity
        
        for card_name, count in card_counts.items():
            if count > 4 and not card_name.startswith("Basic"):
                return False
        
        return True
    
    def to_dict(self) -> dict:
        """Convert deck to dictionary for serialization"""
        return {
            "name": self.name,
            "format": self.format,
            "description": self.description,
            "created_date": self.created_date,
            "last_modified": self.last_modified,
            "cards": [
                {
                    "name": card.card.name,
                    "quantity": card.quantity,
                    "sideboard": card.sideboard,
                    "card_data": {
                        "name": card.card.name,
                        "mana_cost": card.card.mana_cost,
                        "converted_mana_cost": card.card.converted_mana_cost,
                        "card_type": card.card.card_type,
                        "creature_type": card.card.creature_type,
                        "rarity": card.card.rarity,
                        "colors": card.card.colors,
                        "power": card.card.power,
                        "toughness": card.card.toughness,
                        "text": card.card.text,
                        "set_code": card.card.set_code,
                        "collector_number": card.card.collector_number,
                        "arena_id": card.card.arena_id
                    }
                }
                for card in self.cards
            ]
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Deck':
        """Create deck from dictionary"""
        deck = cls(
            name=data["name"],
            format=data.get("format", "Standard"),
            description=data.get("description", ""),
            created_date=data.get("created_date"),
            last_modified=data.get("last_modified")
        )
        
        for card_data in data.get("cards", []):
            card = Card(**card_data["card_data"])
            deck.cards.append(DeckCard(
                card=card,
                quantity=card_data["quantity"],
                sideboard=card_data.get("sideboard", False)
            ))
        
        return deck
