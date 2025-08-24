"""
Collection model for managing Magic: The Gathering card collection
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional
from collections import defaultdict
import json

from .card import Card

@dataclass
class CollectionCard:
    """Represents a card in collection with quantity"""
    card: Card
    quantity: int = 0
    quantity_foil: int = 0

@dataclass
class Collection:
    """Represents a Magic: The Gathering card collection"""
    name: str = "My Collection"
    cards: Dict[str, CollectionCard] = field(default_factory=dict)
    last_updated: Optional[str] = None
    
    def add_card(self, card: Card, quantity: int = 1, foil: bool = False):
        """Add cards to collection"""
        if card.name not in self.cards:
            self.cards[card.name] = CollectionCard(card, 0, 0)
        
        if foil:
            self.cards[card.name].quantity_foil += quantity
        else:
            self.cards[card.name].quantity += quantity
    
    def remove_card(self, card_name: str, quantity: int = 1, foil: bool = False):
        """Remove cards from collection"""
        if card_name in self.cards:
            if foil:
                self.cards[card_name].quantity_foil = max(0, self.cards[card_name].quantity_foil - quantity)
            else:
                self.cards[card_name].quantity = max(0, self.cards[card_name].quantity - quantity)
            
            # Remove card if no copies left
            if (self.cards[card_name].quantity == 0 and 
                self.cards[card_name].quantity_foil == 0):
                del self.cards[card_name]
    
    def get_card_quantity(self, card_name: str, include_foil: bool = True) -> int:
        """Get total quantity of a card in collection"""
        if card_name not in self.cards:
            return 0
        
        quantity = self.cards[card_name].quantity
        if include_foil:
            quantity += self.cards[card_name].quantity_foil
        
        return quantity
    
    def get_total_cards(self) -> int:
        """Get total number of cards in collection"""
        return sum(
            card.quantity + card.quantity_foil 
            for card in self.cards.values()
        )
    
    def get_unique_cards(self) -> int:
        """Get number of unique cards in collection"""
        return len(self.cards)
    
    def filter_cards(self, **filters) -> List[CollectionCard]:
        """Filter cards in collection"""
        filtered_cards = []
        
        for collection_card in self.cards.values():
            if collection_card.card.matches_filter(**filters):
                filtered_cards.append(collection_card)
        
        return filtered_cards
    
    def get_cards_by_color(self) -> Dict[str, List[CollectionCard]]:
        """Group cards by color"""
        color_groups = defaultdict(list)
        
        for collection_card in self.cards.values():
            if not collection_card.card.colors:
                color_groups["Colorless"].append(collection_card)
            elif len(collection_card.card.colors) == 1:
                color_name = self._get_color_name(collection_card.card.colors[0])
                color_groups[color_name].append(collection_card)
            else:
                color_groups["Multicolored"].append(collection_card)
        
        return dict(color_groups)
    
    def get_cards_by_type(self) -> Dict[str, List[CollectionCard]]:
        """Group cards by type"""
        type_groups = defaultdict(list)
        
        for collection_card in self.cards.values():
            card_type = collection_card.card.card_type.split()[0] if collection_card.card.card_type else "Unknown"
            type_groups[card_type].append(collection_card)
        
        return dict(type_groups)
    
    def get_cards_by_rarity(self) -> Dict[str, List[CollectionCard]]:
        """Group cards by rarity"""
        rarity_groups = defaultdict(list)
        
        for collection_card in self.cards.values():
            rarity_groups[collection_card.card.rarity].append(collection_card)
        
        return dict(rarity_groups)
    
    def get_completion_stats(self, set_code: Optional[str] = None) -> Dict[str, int]:
        """Get collection completion statistics"""
        stats = {
            "total_cards": self.get_total_cards(),
            "unique_cards": self.get_unique_cards(),
            "commons": 0,
            "uncommons": 0,
            "rares": 0,
            "mythics": 0
        }
        
        for collection_card in self.cards.values():
            if set_code and collection_card.card.set_code != set_code:
                continue
                
            rarity = collection_card.card.rarity.lower()
            if "common" in rarity:
                stats["commons"] += 1
            elif "uncommon" in rarity:
                stats["uncommons"] += 1
            elif "rare" in rarity and "mythic" not in rarity:
                stats["rares"] += 1
            elif "mythic" in rarity:
                stats["mythics"] += 1
        
        return stats
    
    def _get_color_name(self, color_code: str) -> str:
        """Convert color code to name"""
        color_map = {
            "W": "White",
            "U": "Blue", 
            "B": "Black",
            "R": "Red",
            "G": "Green",
            "C": "Colorless"
        }
        return color_map.get(color_code, "Unknown")
    
    def to_dict(self) -> dict:
        """Convert collection to dictionary for serialization"""
        return {
            "name": self.name,
            "last_updated": self.last_updated,
            "cards": {
                name: {
                    "quantity": card.quantity,
                    "quantity_foil": card.quantity_foil,
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
                for name, card in self.cards.items()
            }
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Collection':
        """Create collection from dictionary"""
        collection = cls(
            name=data.get("name", "My Collection"),
            last_updated=data.get("last_updated")
        )
        
        for name, card_data in data.get("cards", {}).items():
            card = Card(**card_data["card_data"])
            collection.cards[name] = CollectionCard(
                card=card,
                quantity=card_data.get("quantity", 0),
                quantity_foil=card_data.get("quantity_foil", 0)
            )
        
        return collection
