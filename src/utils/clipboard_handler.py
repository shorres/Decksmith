"""
Clipboard import functionality for MTG Arena Deck Manager
Handles importing decks and cards from system clipboard
"""

import re
import pyperclip
from typing import List, Dict, Tuple, Optional
from models.card import Card
from models.deck import Deck, DeckCard
from utils.scryfall_api import ScryfallAPI

class ClipboardHandler:
    """Handles importing decks and cards from clipboard"""
    
    def __init__(self):
        """Initialize clipboard handler with Scryfall API"""
        self.scryfall_api = ScryfallAPI()
        self._card_cache = {}  # Cache cards to avoid duplicate API calls
    
    def _create_enriched_card(self, name: str) -> Card:
        """
        Create a Card object enriched with Scryfall data when possible
        Uses caching to avoid duplicate API calls for the same card
        
        Args:
            name: Card name
            
        Returns:
            Card object with enriched data from Scryfall or basic data
        """
        # Check cache first
        if name in self._card_cache:
            return self._card_cache[name]
        
        # Try to get card data from Scryfall
        scryfall_card = self.scryfall_api.get_card_fuzzy(name)
        
        if scryfall_card:
            print(f"✓ Enriched '{name}' with Scryfall data")
            card = Card(
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
                collector_number=scryfall_card.collector_number
            )
        else:
            print(f"⚠ Could not find '{name}' in Scryfall, using basic data")
            # Fall back to creating card with minimal info
            card = Card(name=name)
        
        # Cache the result
        self._card_cache[name] = card
        return card
    
    def _extract_creature_types(self, type_line: str) -> str:
        """Extract creature types from type line"""
        if '—' in type_line:
            # Split on em dash and take the part after it
            parts = type_line.split('—', 1)
            if len(parts) > 1:
                return parts[1].strip()
        return ''
        """Initialize clipboard handler"""
        # Regular expressions for parsing different formats
        self.arena_deck_pattern = re.compile(r'^(\d+)\s+(.+?)(?:\s+\(([A-Z]{3})\)\s+(\d+))?$', re.MULTILINE)
        self.simple_card_pattern = re.compile(r'^(?:(\d+)x?\s+)?(.+?)(?:\s*$)', re.MULTILINE)
        self.mtgo_pattern = re.compile(r'^(\d+)\s+(.+?)$', re.MULTILINE)
        
    def get_clipboard_content(self) -> str:
        """Get content from system clipboard"""
        try:
            content = pyperclip.paste()
            return content.strip() if content else ""
        except Exception as e:
            print(f"Error accessing clipboard: {e}")
            return ""
    
    def detect_format(self, content: str) -> str:
        """Detect the format of clipboard content"""
        if not content:
            return "empty"
        
        lines = [line.strip() for line in content.split('\n') if line.strip()]
        if not lines:
            return "empty"
        
        # Check for Arena format (with set codes)
        arena_matches = 0
        simple_matches = 0
        
        for line in lines:
            # Skip section headers
            if line.lower() in ['deck', 'sideboard', 'maindeck', 'main deck']:
                continue
            if line.startswith('//') or line.startswith('#'):
                continue
            
            # Arena format: "4 Lightning Bolt (M21) 159"
            if re.match(r'^\d+\s+.+?\s+\([A-Z0-9]{3,4}\)\s+\d+', line):
                arena_matches += 1
            # Simple format: "4 Lightning Bolt" or "Lightning Bolt"
            elif re.match(r'^(?:\d+x?\s+)?[A-Za-z]', line):
                simple_matches += 1
        
        if arena_matches > 0:
            return "arena"
        elif simple_matches > 0:
            return "simple"
        else:
            return "unknown"
    
    def parse_arena_format(self, content: str) -> Tuple[List[DeckCard], List[DeckCard]]:
        """Parse Arena format deck list with Scryfall auto-enrichment"""
        mainboard = []
        sideboard = []
        current_section = "mainboard"
        
        lines = content.split('\n')
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Check for section headers
            if line.lower() in ['sideboard', 'side board']:
                current_section = "sideboard"
                continue
            elif line.lower() in ['deck', 'maindeck', 'main deck', 'mainboard', 'main board']:
                current_section = "mainboard"
                continue
            
            # Skip comments
            if line.startswith('//') or line.startswith('#'):
                continue
            
            # Parse card line: "4 Lightning Bolt (M21) 159"
            match = re.match(r'^(\d+)\s+(.+?)\s+\(([A-Z0-9]{3,4})\)\s+(\d+)', line)
            if match:
                quantity = int(match.group(1))
                name = match.group(2)
                set_code = match.group(3)
                collector_number = match.group(4)
                
                # Create enriched card with Scryfall data
                card = self._create_enriched_card(name)
                # Preserve set/collector info from Arena format
                if hasattr(card, 'set_code') and not card.set_code:
                    card.set_code = set_code
                if hasattr(card, 'collector_number') and not card.collector_number:
                    card.collector_number = collector_number
                
                deck_card = DeckCard(card=card, quantity=quantity)
                
                if current_section == "sideboard":
                    sideboard.append(deck_card)
                else:
                    mainboard.append(deck_card)
        
        return mainboard, sideboard
    
    def parse_simple_format(self, content: str) -> Tuple[List[DeckCard], List[DeckCard]]:
        """Parse simple format deck list (quantity + name) with Scryfall auto-enrichment"""
        mainboard = []
        sideboard = []
        current_section = "mainboard"
        
        lines = content.split('\n')
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Check for section headers
            if line.lower() in ['sideboard', 'side board', 'sb']:
                current_section = "sideboard"
                continue
            elif line.lower() in ['deck', 'maindeck', 'main deck', 'mainboard', 'main board', 'mb']:
                current_section = "mainboard"
                continue
            
            # Skip comments
            if line.startswith('//') or line.startswith('#'):
                continue
            
            # Parse card line: "4 Lightning Bolt" or "Lightning Bolt"
            match = re.match(r'^(?:(\d+)x?\s+)?(.+?)$', line)
            if match:
                quantity_str = match.group(1)
                name = match.group(2).strip()
                
                # Default quantity to 1 if not specified
                quantity = int(quantity_str) if quantity_str else 1
                
                # Skip empty names
                if not name:
                    continue
                
                # Create enriched card with Scryfall data
                card = self._create_enriched_card(name)
                
                deck_card = DeckCard(card=card, quantity=quantity)
                
                if current_section == "sideboard":
                    sideboard.append(deck_card)
                else:
                    mainboard.append(deck_card)
        
        return mainboard, sideboard
    
    def import_deck_from_clipboard(self) -> Optional[Deck]:
        """Import a deck from clipboard content"""
        content = self.get_clipboard_content()
        if not content:
            return None
        
        format_type = self.detect_format(content)
        
        if format_type == "arena":
            mainboard, sideboard = self.parse_arena_format(content)
        elif format_type == "simple":
            mainboard, sideboard = self.parse_simple_format(content)
        else:
            return None
        
        # Create deck name based on first few cards or timestamp
        if mainboard:
            deck_name = f"Imported Deck ({mainboard[0].card.name})"
        else:
            from datetime import datetime
            deck_name = f"Imported Deck {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        
        deck = Deck(name=deck_name)
        
        # Add cards to deck
        for deck_card in mainboard:
            deck.add_card(deck_card.card, deck_card.quantity, sideboard=False)
        
        for deck_card in sideboard:
            deck.add_card(deck_card.card, deck_card.quantity, sideboard=True)
        
        return deck
    
    def import_cards_from_clipboard(self) -> List[Tuple[Card, int]]:
        """Import individual cards from clipboard (returns list of card, quantity tuples)"""
        content = self.get_clipboard_content()
        if not content:
            return []
        
        format_type = self.detect_format(content)
        cards = []
        
        if format_type == "arena":
            mainboard, sideboard = self.parse_arena_format(content)
            cards.extend([(dc.card, dc.quantity) for dc in mainboard + sideboard])
        elif format_type == "simple":
            mainboard, sideboard = self.parse_simple_format(content)
            cards.extend([(dc.card, dc.quantity) for dc in mainboard + sideboard])
        
        return cards
    
    def export_deck_to_clipboard(self, deck: Deck, format_type: str = "arena") -> bool:
        """Export deck to clipboard in specified format"""
        if not deck:
            return False
        
        try:
            if format_type == "arena":
                content = self._format_deck_arena(deck)
            elif format_type == "simple":
                content = self._format_deck_simple(deck)
            else:
                return False
            
            pyperclip.copy(content)
            return True
        except Exception as e:
            print(f"Error copying to clipboard: {e}")
            return False
    
    def _format_deck_arena(self, deck: Deck) -> str:
        """Format deck in Arena export format"""
        lines = ["Deck"]
        
        # Mainboard
        for deck_card in deck.get_mainboard_cards():
            card = deck_card.card
            set_code = getattr(card, 'set_code', 'UNK') or 'UNK'
            collector_number = getattr(card, 'collector_number', '1') or '1'
            lines.append(f"{deck_card.quantity} {card.name} ({set_code}) {collector_number}")
        
        # Sideboard
        sideboard_cards = deck.get_sideboard_cards()
        if sideboard_cards:
            lines.append("")
            lines.append("Sideboard")
            for deck_card in sideboard_cards:
                card = deck_card.card
                set_code = getattr(card, 'set_code', 'UNK') or 'UNK'
                collector_number = getattr(card, 'collector_number', '1') or '1'
                lines.append(f"{deck_card.quantity} {card.name} ({set_code}) {collector_number}")
        
        return '\n'.join(lines)
    
    def _format_deck_simple(self, deck: Deck) -> str:
        """Format deck in simple format"""
        lines = ["Mainboard"]
        
        # Mainboard
        for deck_card in deck.get_mainboard_cards():
            lines.append(f"{deck_card.quantity} {deck_card.card.name}")
        
        # Sideboard
        sideboard_cards = deck.get_sideboard_cards()
        if sideboard_cards:
            lines.append("")
            lines.append("Sideboard")
            for deck_card in sideboard_cards:
                lines.append(f"{deck_card.quantity} {deck_card.card.name}")
        
        return '\n'.join(lines)
    
    def get_format_description(self, format_type: str) -> str:
        """Get description of format for user"""
        descriptions = {
            "arena": "MTG Arena format with set codes (e.g., '4 Lightning Bolt (M21) 159')",
            "simple": "Simple format with quantities (e.g., '4 Lightning Bolt' or 'Lightning Bolt')",
            "empty": "Clipboard is empty",
            "unknown": "Unrecognized format"
        }
        return descriptions.get(format_type, "Unknown format")
