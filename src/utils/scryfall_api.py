"""
Scryfall API integration for MTG card data
"""

import requests
import json
import time
from typing import List, Dict, Optional
from dataclasses import dataclass
from models.card import Card

@dataclass
class ScryfallCard:
    """Represents a card from Scryfall API"""
    name: str
    mana_cost: str
    cmc: float
    type_line: str
    oracle_text: str
    colors: List[str]
    color_identity: List[str]
    power: Optional[str]
    toughness: Optional[str]
    rarity: str
    set_code: str
    set_name: str
    collector_number: str
    image_uri: Optional[str]
    scryfall_id: str

class ScryfallAPI:
    """Scryfall API client for card data and autocomplete"""
    
    BASE_URL = "https://api.scryfall.com"
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'MTG Arena Deck Manager/1.0'
        })
        self.last_request_time = 0
        self.min_request_interval = 0.1  # 100ms between requests as per Scryfall guidelines
    
    def _rate_limit(self):
        """Ensure we don't exceed rate limits"""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        if time_since_last < self.min_request_interval:
            time.sleep(self.min_request_interval - time_since_last)
        self.last_request_time = time.time()
    
    def _make_request(self, endpoint: str, params: Optional[Dict] = None) -> Optional[Dict]:
        """Make a request to Scryfall API with rate limiting"""
        self._rate_limit()
        
        try:
            url = f"{self.BASE_URL}{endpoint}"
            response = self.session.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 404:
                return None
            else:
                print(f"Scryfall API error: {response.status_code}")
                return None
                
        except requests.RequestException as e:
            print(f"Request error: {e}")
            return None
    
    def autocomplete_card_names(self, query: str) -> List[str]:
        """Get card name suggestions for autocomplete"""
        if len(query) < 2:
            return []
        
        endpoint = "/cards/autocomplete"
        params = {"q": query}
        
        data = self._make_request(endpoint, params)
        if data and 'data' in data:
            return data['data'][:15]  # Limit to 15 suggestions
        return []
    
    def search_cards(self, query: str, limit: int = 20) -> List[ScryfallCard]:
        """Search for cards by name"""
        if len(query) < 2:
            return []
        
        endpoint = "/cards/search"
        params = {
            "q": f"name:{query}",
            "order": "name",
            "dir": "asc",
            "unique": "cards"
        }
        
        data = self._make_request(endpoint, params)
        if not data or 'data' not in data:
            return []
        
        cards = []
        for card_data in data['data'][:limit]:
            try:
                card = self._parse_card_data(card_data)
                if card:
                    cards.append(card)
            except Exception as e:
                print(f"Error parsing card data: {e}")
                continue
        
        return cards
    
    def get_card_by_name(self, name: str) -> Optional[ScryfallCard]:
        """Get detailed card information by exact name"""
        endpoint = "/cards/named"
        params = {"exact": name}
        
        data = self._make_request(endpoint, params)
        if data:
            return self._parse_card_data(data)
        return None
    
    def get_card_fuzzy(self, name: str) -> Optional[ScryfallCard]:
        """Get card information by fuzzy name matching"""
        endpoint = "/cards/named"
        params = {"fuzzy": name}
        
        data = self._make_request(endpoint, params)
        if data:
            return self._parse_card_data(data)
        return None
    
    def _parse_card_data(self, data: Dict) -> Optional[ScryfallCard]:
        """Parse card data from Scryfall API response"""
        try:
            # Handle double-faced cards
            if 'card_faces' in data and data['card_faces']:
                # Use the front face for most data
                front_face = data['card_faces'][0]
                name = data.get('name', front_face.get('name', ''))
                mana_cost = front_face.get('mana_cost', '')
                type_line = front_face.get('type_line', '')
                oracle_text = front_face.get('oracle_text', '')
                power = front_face.get('power')
                toughness = front_face.get('toughness')
            else:
                name = data.get('name', '')
                mana_cost = data.get('mana_cost', '')
                type_line = data.get('type_line', '')
                oracle_text = data.get('oracle_text', '')
                power = data.get('power')
                toughness = data.get('toughness')
            
            # Get image URI
            image_uri = None
            if 'image_uris' in data:
                image_uri = data['image_uris'].get('normal')
            elif 'card_faces' in data and data['card_faces'] and 'image_uris' in data['card_faces'][0]:
                image_uri = data['card_faces'][0]['image_uris'].get('normal')
            
            return ScryfallCard(
                name=name,
                mana_cost=mana_cost,
                cmc=float(data.get('cmc', 0)),
                type_line=type_line,
                oracle_text=oracle_text,
                colors=data.get('colors', []),
                color_identity=data.get('color_identity', []),
                power=power,
                toughness=toughness,
                rarity=data.get('rarity', 'common').title(),
                set_code=data.get('set', '').upper(),
                set_name=data.get('set_name', ''),
                collector_number=data.get('collector_number', ''),
                image_uri=image_uri,
                scryfall_id=data.get('id', '')
            )
        except Exception as e:
            print(f"Error parsing Scryfall card data: {e}")
            return None
    
    def convert_to_card_model(self, scryfall_card: ScryfallCard) -> Card:
        """Convert ScryfallCard to our Card model"""
        return Card(
            name=scryfall_card.name,
            mana_cost=scryfall_card.mana_cost,
            converted_mana_cost=int(scryfall_card.cmc),
            card_type=scryfall_card.type_line,
            rarity=scryfall_card.rarity,
            colors=scryfall_card.colors,
            power=int(scryfall_card.power) if scryfall_card.power and scryfall_card.power.isdigit() else None,
            toughness=int(scryfall_card.toughness) if scryfall_card.toughness and scryfall_card.toughness.isdigit() else None,
            text=scryfall_card.oracle_text,
            set_code=scryfall_card.set_code,
            collector_number=scryfall_card.collector_number
        )
    
    def get_random_cards(self, count: int = 1) -> List[ScryfallCard]:
        """Get random cards (useful for testing)"""
        endpoint = "/cards/random"
        cards = []
        
        for _ in range(min(count, 10)):  # Limit to avoid excessive requests
            data = self._make_request(endpoint)
            if data:
                card = self._parse_card_data(data)
                if card:
                    cards.append(card)
        
        return cards

# Global instance for reuse
scryfall_api = ScryfallAPI()
