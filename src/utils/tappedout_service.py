"""
TappedOut integration service for deck analysis and recommendations
"""

import requests
from typing import List, Dict, Optional, Tuple
from datetime import datetime
import time
import re
from bs4 import BeautifulSoup
import json

from models.card import Card
from models.deck import Deck, DeckCard

class TappedOutService:
    """Service for interacting with TappedOut website and scraping deck data"""
    
    def __init__(self):
        self.base_url = "https://tappedout.net"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        })
        self.rate_limit_delay = 2.0  # Be respectful with scraping
        self.last_request_time = 0
    
    def _make_request(self, url: str, params: Optional[Dict] = None) -> Optional[requests.Response]:
        """Make a rate-limited request to TappedOut"""
        # Rate limiting
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        if time_since_last < self.rate_limit_delay:
            time.sleep(self.rate_limit_delay - time_since_last)
        
        try:
            response = self.session.get(url, params=params or {}, timeout=10)
            self.last_request_time = time.time()
            
            if response.status_code == 200:
                return response
            elif response.status_code == 429:  # Rate limited
                print("Rate limited by TappedOut, waiting...")
                time.sleep(10)
                return self._make_request(url, params)  # Retry once
            else:
                print(f"TappedOut request failed: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"TappedOut request failed: {e}")
            return None
    
    def search_decks_by_format(self, format_name: str = "standard", limit: int = 10) -> List[Dict]:
        """Search for popular decks by format"""
        try:
            # Map format names to TappedOut format slugs
            format_mapping = {
                "standard": "standard",
                "historic": "historic",
                "explorer": "explorer", 
                "pioneer": "pioneer",
                "modern": "modern",
                "legacy": "legacy",
                "commander": "edh"
            }
            
            format_slug = format_mapping.get(format_name.lower(), "standard")
            url = f"{self.base_url}/mtg-decks/search/"
            
            params = {
                'format': format_slug,
                'o': '-rating',  # Order by rating descending
                'p': 1  # Page 1
            }
            
            response = self._make_request(url, params)
            if not response:
                return []
            
            return self._parse_deck_search_results(response.text, limit)
            
        except Exception as e:
            print(f"Error searching TappedOut decks: {e}")
            return []
    
    def _parse_deck_search_results(self, html: str, limit: int) -> List[Dict]:
        """Parse deck search results from HTML"""
        try:
            soup = BeautifulSoup(html, 'html.parser')
            decks = []
            
            # Find deck entries (this will need to be adjusted based on actual HTML structure)
            deck_elements = soup.find_all('div', class_='deck-tile') or soup.find_all('article', class_='deck')
            
            for deck_elem in deck_elements[:limit]:
                try:
                    # Extract deck information
                    title_elem = deck_elem.find('a', class_='deck-title') or deck_elem.find('h3')
                    if not title_elem:
                        continue
                    
                    deck_name = title_elem.get_text(strip=True)
                    deck_url = title_elem.get('href', '')
                    if deck_url and not deck_url.startswith('http'):
                        deck_url = self.base_url + deck_url
                    
                    # Extract additional metadata if available
                    author_elem = deck_elem.find('a', class_='user-link') or deck_elem.find('.user')
                    author = author_elem.get_text(strip=True) if author_elem else "Unknown"
                    
                    # Extract rating or popularity if available
                    rating_elem = deck_elem.find('.rating') or deck_elem.find('.score')
                    rating = rating_elem.get_text(strip=True) if rating_elem else "0"
                    
                    decks.append({
                        'name': deck_name,
                        'url': deck_url,
                        'author': author,
                        'rating': rating,
                        'source': 'TappedOut'
                    })
                    
                except Exception as e:
                    print(f"Error parsing deck element: {e}")
                    continue
            
            return decks
            
        except Exception as e:
            print(f"Error parsing search results: {e}")
            return []
    
    def get_deck_details(self, deck_url: str) -> Optional[Dict]:
        """Get detailed information about a specific deck"""
        try:
            response = self._make_request(deck_url)
            if not response:
                return None
            
            return self._parse_deck_details(response.text, deck_url)
            
        except Exception as e:
            print(f"Error getting deck details: {e}")
            return None
    
    def _parse_deck_details(self, html: str, deck_url: str) -> Dict:
        """Parse deck details from HTML"""
        try:
            soup = BeautifulSoup(html, 'html.parser')
            
            # Extract deck name
            title_elem = soup.find('h1') or soup.find('.deck-title')
            deck_name = title_elem.get_text(strip=True) if title_elem else "Unknown Deck"
            
            # Extract description
            desc_elem = soup.find('.deck-description') or soup.find('.description')
            description = desc_elem.get_text(strip=True) if desc_elem else ""
            
            # Parse card list
            mainboard_cards = []
            sideboard_cards = []
            
            # Look for deck list container
            deck_list = soup.find('.deck-list') or soup.find('#deck-list')
            if deck_list:
                current_section = 'mainboard'
                
                # Parse each line of the deck list
                lines = deck_list.get_text().split('\n')
                for line in lines:
                    line = line.strip()
                    if not line:
                        continue
                    
                    # Check for sideboard marker
                    if line.lower() in ['sideboard', 'sideboard:', 'side board', 'sb']:
                        current_section = 'sideboard'
                        continue
                    
                    # Parse card line (e.g., "4x Lightning Bolt" or "4 Lightning Bolt")
                    match = re.match(r'(\d+)x?\s+(.+)', line)
                    if match:
                        quantity = int(match.group(1))
                        card_name = match.group(2).strip()
                        
                        card_info = {
                            'name': card_name,
                            'quantity': quantity
                        }
                        
                        if current_section == 'sideboard':
                            sideboard_cards.append(card_info)
                        else:
                            mainboard_cards.append(card_info)
            
            return {
                'name': deck_name,
                'url': deck_url,
                'description': description,
                'mainboard': mainboard_cards,
                'sideboard': sideboard_cards,
                'total_mainboard': sum(card['quantity'] for card in mainboard_cards),
                'total_sideboard': sum(card['quantity'] for card in sideboard_cards)
            }
            
        except Exception as e:
            print(f"Error parsing deck details: {e}")
            return {
                'name': 'Unknown Deck',
                'url': deck_url,
                'description': '',
                'mainboard': [],
                'sideboard': [],
                'total_mainboard': 0,
                'total_sideboard': 0
            }
    
    def find_similar_decks(self, user_deck: Deck, limit: int = 5) -> List[Dict]:
        """Find decks similar to the user's deck"""
        try:
            # Get decks in the same format
            similar_decks = self.search_decks_by_format(user_deck.format, limit * 2)
            
            # Calculate similarity and filter
            deck_similarities = []
            user_cards = set(card.card.name.lower() for card in user_deck.get_mainboard_cards())
            
            for deck_info in similar_decks:
                if not deck_info.get('url'):
                    continue
                
                # Get detailed deck list
                deck_details = self.get_deck_details(deck_info['url'])
                if not deck_details or not deck_details['mainboard']:
                    continue
                
                # Calculate similarity
                other_cards = set(card['name'].lower() for card in deck_details['mainboard'])
                if not other_cards:
                    continue
                
                # Jaccard similarity
                intersection = len(user_cards.intersection(other_cards))
                union = len(user_cards.union(other_cards))
                similarity = intersection / union if union > 0 else 0
                
                if similarity > 0.2:  # At least 20% similarity
                    deck_similarities.append({
                        **deck_info,
                        'similarity': similarity,
                        'details': deck_details,
                        'common_cards': list(user_cards.intersection(other_cards)),
                        'unique_cards': list(other_cards - user_cards)
                    })
            
            # Sort by similarity and return top results
            deck_similarities.sort(key=lambda x: x['similarity'], reverse=True)
            return deck_similarities[:limit]
            
        except Exception as e:
            print(f"Error finding similar decks: {e}")
            return []
    
    def get_popular_cards_in_format(self, format_name: str, limit: int = 20) -> List[Dict]:
        """Get popular cards in a format based on deck analysis"""
        try:
            decks = self.search_decks_by_format(format_name, 10)
            card_popularity = {}
            
            for deck_info in decks:
                if not deck_info.get('url'):
                    continue
                
                deck_details = self.get_deck_details(deck_info['url'])
                if not deck_details:
                    continue
                
                # Count card appearances
                for card in deck_details['mainboard']:
                    card_name = card['name']
                    if card_name not in card_popularity:
                        card_popularity[card_name] = {
                            'name': card_name,
                            'appearances': 0,
                            'total_copies': 0,
                            'avg_copies': 0.0
                        }
                    
                    card_popularity[card_name]['appearances'] += 1
                    card_popularity[card_name]['total_copies'] += card['quantity']
            
            # Calculate averages and sort by popularity
            popular_cards = []
            for card_name, data in card_popularity.items():
                if data['appearances'] >= 2:  # Appears in at least 2 decks
                    data['avg_copies'] = data['total_copies'] / data['appearances']
                    popular_cards.append(data)
            
            popular_cards.sort(key=lambda x: x['appearances'], reverse=True)
            return popular_cards[:limit]
            
        except Exception as e:
            print(f"Error getting popular cards: {e}")
            return []

class CollectionChecker:
    """Helper class to check card availability in collection"""
    
    @staticmethod
    def check_card_availability(card_name: str, collection) -> Tuple[bool, int]:
        """Check if a card is in collection and return (is_owned, quantity)"""
        if not collection:
            return False, 0
        
        # Search for card in collection
        for collection_card in collection.cards:
            if collection_card.card.name.lower() == card_name.lower():
                return True, collection_card.quantity
        
        return False, 0
    
    @staticmethod
    def categorize_recommendations(recommendations: List, collection) -> Dict[str, List]:
        """Categorize recommendations by availability"""
        owned = []
        craftable = []
        
        for rec in recommendations:
            is_owned, quantity = CollectionChecker.check_card_availability(
                rec.card.name if hasattr(rec, 'card') else rec['name'], 
                collection
            )
            
            if is_owned and quantity > 0:
                owned.append({**rec if isinstance(rec, dict) else rec.__dict__, 'owned_quantity': quantity})
            else:
                craftable.append(rec)
        
        return {
            'owned': owned,
            'craftable': craftable
        }
