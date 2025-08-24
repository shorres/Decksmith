"""
Card model for Magic: The Gathering cards
"""

from dataclasses import dataclass, field
from typing import List, Optional
from enum import Enum

class CardType(Enum):
    """Magic card types"""
    CREATURE = "Creature"
    INSTANT = "Instant"
    SORCERY = "Sorcery"
    ENCHANTMENT = "Enchantment"
    ARTIFACT = "Artifact"
    PLANESWALKER = "Planeswalker"
    LAND = "Land"

class Rarity(Enum):
    """Card rarities"""
    COMMON = "Common"
    UNCOMMON = "Uncommon"
    RARE = "Rare"
    MYTHIC_RARE = "Mythic Rare"

class Color(Enum):
    """Magic colors"""
    WHITE = "W"
    BLUE = "U"
    BLACK = "B"
    RED = "R"
    GREEN = "G"
    COLORLESS = "C"

@dataclass
class Card:
    """Represents a Magic: The Gathering card"""
    name: str
    mana_cost: str = ""
    converted_mana_cost: int = 0
    card_type: str = ""
    creature_type: str = ""
    rarity: str = "Common"
    colors: List[str] = field(default_factory=list)
    power: Optional[int] = None
    toughness: Optional[int] = None
    text: str = ""
    set_code: str = ""
    collector_number: str = ""
    arena_id: Optional[int] = None
    
    def __post_init__(self):
        """Process card data after initialization"""
        if isinstance(self.colors, str):
            self.colors = [c.strip() for c in self.colors.split(",") if c.strip()]
    
    @property
    def is_creature(self) -> bool:
        """Check if card is a creature"""
        return "Creature" in self.card_type
    
    @property
    def color_identity(self) -> List[str]:
        """Get color identity of the card"""
        return sorted(self.colors)
    
    @property
    def is_multicolored(self) -> bool:
        """Check if card is multicolored"""
        return len(self.colors) > 1
    
    def matches_filter(self, **filters) -> bool:
        """Check if card matches given filters"""
        for key, value in filters.items():
            if not value:  # Skip empty filters
                continue
                
            if key == "name" and value.lower() not in self.name.lower():
                return False
            elif key == "colors" and not any(color in self.colors for color in value):
                return False
            elif key == "creature_type" and value.lower() not in self.creature_type.lower():
                return False
            elif key == "card_type" and value.lower() not in self.card_type.lower():
                return False
            elif key == "rarity" and value != self.rarity:
                return False
            elif key == "cmc_min" and self.converted_mana_cost < value:
                return False
            elif key == "cmc_max" and self.converted_mana_cost > value:
                return False
        
        return True
