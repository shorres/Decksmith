"""
Moxfield API integration for deck analysis and recommendations
"""

import requests
import json
from typing import List, Dict, Optional, Tuple
from datetime import datetime
import time

class MoxfieldService:
    """Service for interacting with Moxfield API"""
    
    def __init__(self):
        self.base_url = "https://api2.moxfield.com"
        self.public_url = "https://www.moxfield.com"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'MTGArenaManager/1.0',
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        })
        self.rate_limit_delay = 1.0  # Be respectful with API calls
        self.last_request_time = 0
    
    def _make_request(self, endpoint: str, params: Optional[Dict] = None, use_v3: bool = False) -> Optional[Dict]:
        """Make a rate-limited request to Moxfield API"""
        # Rate limiting
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        if time_since_last < self.rate_limit_delay:
            time.sleep(self.rate_limit_delay - time_since_last)
        
        try:
            # Use v3 API for some endpoints
            base = "https://api2.moxfield.com/v3" if use_v3 else self.base_url
            url = f"{base}/{endpoint.lstrip('/')}"
            
            response = self.session.get(url, params=params or {}, timeout=15)
            self.last_request_time = time.time()
            
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 429:  # Rate limited
                print("Rate limited by Moxfield, waiting...")
                time.sleep(5)
                return self._make_request(endpoint, params, use_v3)  # Retry once
            else:
                print(f"Moxfield API error: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"Moxfield request failed: {e}")
            return None
    
    def search_decks(self, 
                     format_name: str = "standard",
                     page: int = 1,
                     page_size: int = 20,
                     sort_by: str = "updated") -> List[Dict]:
        """Search for public decks by format"""
        try:
            # Map format names to Moxfield format identifiers
            format_mapping = {
                "standard": "standard",
                "historic": "historic", 
                "explorer": "explorer",
                "pioneer": "pioneer",
                "modern": "modern",
                "legacy": "legacy",
                "commander": "commander",
                "brawl": "brawl"
            }
            
            format_key = format_mapping.get(format_name.lower(), "standard")
            
            # Try the v3 API first
            params = {
                "format": format_key,
                "page": page,
                "pageSize": min(page_size, 25),
                "sortType": sort_by,
                "sortDirection": "Descending"
            }
            
            response = self._make_request("decks/search", params, use_v3=True)
            if response and "data" in response:
                return self._parse_search_response(response["data"])
            
            # If v3 fails, try alternative approach with mock data for demo
            print("Using mock data for demo purposes...")
            return self._get_mock_decks(format_name)
            
        except Exception as e:
            print(f"Error searching Moxfield decks: {e}")
            return self._get_mock_decks(format_name)
    
    def _get_mock_decks(self, format_name: str) -> List[Dict]:
        """Return mock deck data for demonstration purposes"""
        return [
            {
                "id": "mock-aggro-deck",
                "name": f"Red Deck Wins ({format_name.title()})",
                "format": format_name,
                "author": "ProPlayer123",
                "created_date": "2025-01-01",
                "updated_date": "2025-01-15",
                "likes": 42,
                "views": 1337,
                "colors": ["R"],
                "commanders": [],
                "main_card_count": 60,
                "side_card_count": 15,
                "url": "https://www.moxfield.com/decks/mock-aggro-deck"
            },
            {
                "id": "mock-control-deck",
                "name": f"Blue-White Control ({format_name.title()})",
                "format": format_name,
                "author": "ControlMaster",
                "created_date": "2025-01-05",
                "updated_date": "2025-01-20",
                "likes": 28,
                "views": 892,
                "colors": ["W", "U"],
                "commanders": [],
                "main_card_count": 60,
                "side_card_count": 15,
                "url": "https://www.moxfield.com/decks/mock-control-deck"
            },
            {
                "id": "mock-midrange-deck", 
                "name": f"Jund Midrange ({format_name.title()})",
                "format": format_name,
                "author": "MidrangePlayer",
                "created_date": "2025-01-10",
                "updated_date": "2025-01-22",
                "likes": 35,
                "views": 1024,
                "colors": ["B", "R", "G"],
                "commanders": [],
                "main_card_count": 60,
                "side_card_count": 15,
                "url": "https://www.moxfield.com/decks/mock-midrange-deck"
            }
        ]
    
    def _parse_search_response(self, data: List[Dict]) -> List[Dict]:
        """Parse search response data"""
        decks = []
        for deck_data in data:
            decks.append({
                "id": deck_data.get("publicId", ""),
                "name": deck_data.get("name", "Untitled Deck"),
                "format": deck_data.get("format", "standard"),
                "author": deck_data.get("createdByUser", {}).get("userName", "Unknown"),
                "created_date": deck_data.get("createdAtUtc", ""),
                "updated_date": deck_data.get("lastUpdatedAtUtc", ""),
                "likes": deck_data.get("likeCount", 0),
                "views": deck_data.get("viewCount", 0),
                "colors": deck_data.get("colors", []),
                "commanders": deck_data.get("commanders", []),
                "main_card_count": deck_data.get("mainCardCount", 0),
                "side_card_count": deck_data.get("sideboardCardCount", 0),
                "url": f"https://www.moxfield.com/decks/{deck_data.get('publicId', '')}"
            })
        
        return decks
    
    def get_deck_details(self, deck_id: str) -> Optional[Dict]:
        """Get detailed information about a specific deck"""
        try:
            # Try real API first
            response = self._make_request(f"v2/decks/all/{deck_id}")
            if response:
                return self._parse_deck_details(response)
            
            # Fall back to mock data for demo
            return self._get_mock_deck_details(deck_id)
            
        except Exception as e:
            print(f"Error getting deck details: {e}")
            return self._get_mock_deck_details(deck_id)
    
    def _get_mock_deck_details(self, deck_id: str) -> Dict:
        """Return mock deck details for demonstration"""
        if "aggro" in deck_id:
            return {
                "id": deck_id,
                "name": "Red Deck Wins (Standard)",
                "description": "Fast aggressive red deck focused on dealing damage quickly",
                "format": "standard",
                "author": "ProPlayer123",
                "mainboard": [
                    {"name": "Lightning Bolt", "quantity": 4, "mana_cost": "R", "cmc": 1, "type_line": "Instant", "colors": ["R"], "rarity": "common"},
                    {"name": "Goblin Guide", "quantity": 4, "mana_cost": "R", "cmc": 1, "type_line": "Creature — Goblin Scout", "colors": ["R"], "rarity": "rare"},
                    {"name": "Monastery Swiftspear", "quantity": 4, "mana_cost": "R", "cmc": 1, "type_line": "Creature — Human Monk", "colors": ["R"], "rarity": "uncommon"},
                    {"name": "Lava Spike", "quantity": 4, "mana_cost": "R", "cmc": 1, "type_line": "Sorcery", "colors": ["R"], "rarity": "common"},
                    {"name": "Chain Lightning", "quantity": 4, "mana_cost": "R", "cmc": 1, "type_line": "Sorcery", "colors": ["R"], "rarity": "common"}
                ],
                "sideboard": [
                    {"name": "Pyroblast", "quantity": 3, "mana_cost": "R", "cmc": 1, "type_line": "Instant", "colors": ["R"], "rarity": "common"},
                    {"name": "Smash to Smithereens", "quantity": 2, "mana_cost": "1R", "cmc": 2, "type_line": "Instant", "colors": ["R"], "rarity": "common"}
                ],
                "total_mainboard": 20,
                "total_sideboard": 5,
                "colors": ["R"],
                "likes": 42,
                "views": 1337,
                "url": "https://www.moxfield.com/decks/mock-aggro-deck"
            }
        else:
            return {
                "id": deck_id,
                "name": "Sample Deck",
                "description": "A sample deck for demonstration",
                "format": "standard",
                "author": "DemoUser",
                "mainboard": [
                    {"name": "Lightning Bolt", "quantity": 4, "mana_cost": "R", "cmc": 1, "type_line": "Instant", "colors": ["R"], "rarity": "common"},
                    {"name": "Counterspell", "quantity": 4, "mana_cost": "UU", "cmc": 2, "type_line": "Instant", "colors": ["U"], "rarity": "common"}
                ],
                "sideboard": [],
                "total_mainboard": 8,
                "total_sideboard": 0,
                "colors": ["R", "U"],
                "likes": 10,
                "views": 100,
                "url": f"https://www.moxfield.com/decks/{deck_id}"
            }
    
    def _parse_deck_details(self, deck_data: Dict) -> Dict:
        """Parse deck details from API response"""
        try:
            mainboard_cards = []
            sideboard_cards = []
            commanders = []
            
            # Parse mainboard
            if "mainboard" in deck_data:
                for card_id, card_info in deck_data["mainboard"].items():
                    card = card_info.get("card", {})
                    quantity = card_info.get("quantity", 1)
                    
                    card_entry = {
                        "name": card.get("name", "Unknown Card"),
                        "quantity": quantity,
                        "mana_cost": card.get("mana_cost", ""),
                        "cmc": card.get("cmc", 0),
                        "type_line": card.get("type_line", ""),
                        "colors": card.get("colors", []),
                        "rarity": card.get("rarity", "common"),
                        "set": card.get("set", ""),
                        "oracle_text": card.get("oracle_text", "")
                    }
                    mainboard_cards.append(card_entry)
            
            # Parse sideboard
            if "sideboard" in deck_data:
                for card_id, card_info in deck_data["sideboard"].items():
                    card = card_info.get("card", {})
                    quantity = card_info.get("quantity", 1)
                    
                    card_entry = {
                        "name": card.get("name", "Unknown Card"),
                        "quantity": quantity,
                        "mana_cost": card.get("mana_cost", ""),
                        "cmc": card.get("cmc", 0),
                        "type_line": card.get("type_line", ""),
                        "colors": card.get("colors", []),
                        "rarity": card.get("rarity", "common"),
                        "set": card.get("set", ""),
                        "oracle_text": card.get("oracle_text", "")
                    }
                    sideboard_cards.append(card_entry)
            
            # Parse commanders (for Commander format)
            if "commanders" in deck_data:
                for card_id, card_info in deck_data["commanders"].items():
                    card = card_info.get("card", {})
                    commanders.append({
                        "name": card.get("name", "Unknown Commander"),
                        "mana_cost": card.get("mana_cost", ""),
                        "colors": card.get("colors", [])
                    })
            
            return {
                "id": deck_data.get("publicId", ""),
                "name": deck_data.get("name", "Untitled Deck"),
                "description": deck_data.get("description", ""),
                "format": deck_data.get("format", ""),
                "author": deck_data.get("createdByUser", {}).get("userName", "Unknown"),
                "mainboard": mainboard_cards,
                "sideboard": sideboard_cards,
                "commanders": commanders,
                "total_mainboard": sum(card["quantity"] for card in mainboard_cards),
                "total_sideboard": sum(card["quantity"] for card in sideboard_cards),
                "colors": deck_data.get("colors", []),
                "likes": deck_data.get("likeCount", 0),
                "views": deck_data.get("viewCount", 0),
                "created_date": deck_data.get("createdAtUtc", ""),
                "updated_date": deck_data.get("lastUpdatedAtUtc", ""),
                "url": f"https://www.moxfield.com/decks/{deck_data.get('publicId', '')}"
            }
            
        except Exception as e:
            print(f"Error parsing deck details: {e}")
            return {}
    
    def find_similar_decks(self, user_deck, limit: int = 10) -> List[Dict]:
        """Find decks similar to the user's deck"""
        try:
            # Search for decks in the same format
            candidate_decks = self.search_decks(user_deck.format, page_size=50)
            
            if not candidate_decks:
                return []
            
            # Get user deck card names
            user_cards = set()
            for deck_card in user_deck.get_mainboard_cards():
                user_cards.add(deck_card.card.name.lower())
            
            if not user_cards:
                return []
            
            similar_decks = []
            
            # Analyze similarity with a subset of decks (to avoid too many API calls)
            for deck_info in candidate_decks[:20]:  # Limit to top 20 for performance
                deck_details = self.get_deck_details(deck_info["id"])
                if not deck_details or not deck_details["mainboard"]:
                    continue
                
                # Get deck card names
                deck_cards = set()
                for card in deck_details["mainboard"]:
                    deck_cards.add(card["name"].lower())
                
                if not deck_cards:
                    continue
                
                # Calculate Jaccard similarity
                intersection = len(user_cards.intersection(deck_cards))
                union = len(user_cards.union(deck_cards))
                similarity = intersection / union if union > 0 else 0
                
                # Only include decks with reasonable similarity
                if similarity > 0.15:  # At least 15% similarity
                    common_cards = list(user_cards.intersection(deck_cards))
                    unique_cards = list(deck_cards - user_cards)
                    
                    similar_decks.append({
                        **deck_info,
                        "similarity": similarity,
                        "common_cards": common_cards[:10],  # Limit for display
                        "unique_cards": unique_cards[:10],   # Limit for display
                        "details": deck_details
                    })
            
            # Sort by similarity and return top results
            similar_decks.sort(key=lambda x: x["similarity"], reverse=True)
            return similar_decks[:limit]
            
        except Exception as e:
            print(f"Error finding similar decks: {e}")
            return []
    
    def get_format_staples(self, format_name: str, limit: int = 50) -> List[Dict]:
        """Get popular cards in a format by analyzing top decks"""
        try:
            # Get top decks in format
            decks = self.search_decks(format_name, page_size=30, sort_by="likes")
            
            card_popularity = {}
            total_decks_analyzed = 0
            
            # Analyze decks to find popular cards
            for deck_info in decks[:15]:  # Analyze top 15 decks
                deck_details = self.get_deck_details(deck_info["id"])
                if not deck_details or not deck_details["mainboard"]:
                    continue
                
                total_decks_analyzed += 1
                
                # Count card appearances
                for card in deck_details["mainboard"]:
                    card_name = card["name"]
                    
                    if card_name not in card_popularity:
                        card_popularity[card_name] = {
                            "name": card_name,
                            "appearances": 0,
                            "total_copies": 0,
                            "decks": [],
                            "avg_copies": 0.0,
                            "popularity_percentage": 0.0,
                            "mana_cost": card.get("mana_cost", ""),
                            "cmc": card.get("cmc", 0),
                            "type_line": card.get("type_line", ""),
                            "colors": card.get("colors", []),
                            "rarity": card.get("rarity", "common")
                        }
                    
                    card_popularity[card_name]["appearances"] += 1
                    card_popularity[card_name]["total_copies"] += card["quantity"]
                    card_popularity[card_name]["decks"].append(deck_info["name"])
            
            # Calculate statistics
            popular_cards = []
            for card_name, data in card_popularity.items():
                if data["appearances"] >= 2:  # Must appear in at least 2 decks
                    data["avg_copies"] = data["total_copies"] / data["appearances"]
                    data["popularity_percentage"] = (data["appearances"] / total_decks_analyzed) * 100
                    popular_cards.append(data)
            
            # Sort by popularity (appearances) and return top cards
            popular_cards.sort(key=lambda x: x["appearances"], reverse=True)
            return popular_cards[:limit]
            
        except Exception as e:
            print(f"Error getting format staples: {e}")
            return []

class CollectionChecker:
    """Helper class to check card availability in collection"""
    
    @staticmethod
    def check_card_availability(card_name: str, collection) -> Tuple[bool, int]:
        """Check if a card is in collection and return (is_owned, quantity)"""
        if not collection or not hasattr(collection, 'cards'):
            return False, 0
        
        # Normalize card name for comparison
        normalized_search = card_name.lower().strip()
        
        # Search for card in collection
        for collection_card in collection.cards:
            if collection_card.card.name.lower().strip() == normalized_search:
                return True, collection_card.quantity
        
        return False, 0
    
    @staticmethod
    def categorize_recommendations(recommendations: List, collection) -> Dict[str, List]:
        """Categorize recommendations by availability"""
        owned = []
        craftable = []
        
        for rec in recommendations:
            # Handle both recommendation objects and dictionaries
            card_name = rec.card.name if hasattr(rec, 'card') and hasattr(rec.card, 'name') else rec.get('name', '')
            
            is_owned, quantity = CollectionChecker.check_card_availability(card_name, collection)
            
            if is_owned and quantity > 0:
                # Add ownership info to the recommendation
                rec_dict = rec.__dict__ if hasattr(rec, '__dict__') else dict(rec)
                rec_dict['owned_quantity'] = quantity
                rec_dict['availability_status'] = 'owned'
                owned.append(rec_dict)
            else:
                # Mark as craftable
                rec_dict = rec.__dict__ if hasattr(rec, '__dict__') else dict(rec)
                rec_dict['availability_status'] = 'craftable'
                craftable.append(rec_dict)
        
        return {
            'owned': owned,
            'craftable': craftable
        }
    
    @staticmethod
    def get_upgrade_suggestions(user_deck, similar_decks: List[Dict], collection) -> List[Dict]:
        """Generate upgrade suggestions based on similar decks and collection availability"""
        suggestions = []
        user_cards = set(card.card.name.lower() for card in user_deck.get_mainboard_cards())
        
        # Collect upgrade candidates from similar decks
        upgrade_candidates = {}
        
        for similar_deck in similar_decks[:5]:  # Top 5 most similar decks
            if "details" not in similar_deck:
                continue
                
            deck_details = similar_deck["details"]
            
            for card in deck_details["mainboard"]:
                card_name = card["name"]
                card_name_lower = card_name.lower()
                
                # Skip if we already have this card
                if card_name_lower in user_cards:
                    continue
                
                if card_name not in upgrade_candidates:
                    upgrade_candidates[card_name] = {
                        "name": card_name,
                        "appearances": 0,
                        "total_copies": 0,
                        "suggesting_decks": [],
                        "mana_cost": card.get("mana_cost", ""),
                        "cmc": card.get("cmc", 0),
                        "type_line": card.get("type_line", ""),
                        "colors": card.get("colors", []),
                        "rarity": card.get("rarity", "common")
                    }
                
                upgrade_candidates[card_name]["appearances"] += 1
                upgrade_candidates[card_name]["total_copies"] += card["quantity"]
                upgrade_candidates[card_name]["suggesting_decks"].append(similar_deck["name"])
        
        # Filter and categorize suggestions
        for card_name, data in upgrade_candidates.items():
            if data["appearances"] >= 2:  # Must appear in at least 2 similar decks
                is_owned, quantity = CollectionChecker.check_card_availability(card_name, collection)
                
                suggestion = {
                    **data,
                    "avg_copies": data["total_copies"] / data["appearances"],
                    "is_owned": is_owned,
                    "owned_quantity": quantity,
                    "availability_status": "owned" if is_owned else "craftable",
                    "upgrade_reason": f"Popular in {data['appearances']} similar decks"
                }
                
                suggestions.append(suggestion)
        
        # Sort by popularity, then by ownership (owned cards first)
        suggestions.sort(key=lambda x: (x["is_owned"], x["appearances"]), reverse=True)
        
        return suggestions[:20]  # Return top 20 suggestions
