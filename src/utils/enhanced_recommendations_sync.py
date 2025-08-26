"""
Enhanced AI-powered recommendation system using Scryfall API data (Synchronous Version)
"""

import json
import random
from typing import List, Dict, Any, Optional, Tuple, Set
from collections import Counter, defaultdict
from dataclasses import dataclass
import math

try:
    from ..models.card import Card
    from ..models.deck import Deck, DeckCard
    from .scryfall_api import ScryfallAPI
    from .persistent_cache import get_cache
except ImportError:
    from models.card import Card
    from models.deck import Deck, DeckCard
    from utils.scryfall_api import ScryfallAPI
    from utils.persistent_cache import get_cache

@dataclass
class SmartRecommendation:
    """Enhanced recommendation with Scryfall-powered analysis"""
    card_name: str
    mana_cost: str
    card_type: str
    rarity: str
    confidence: float
    synergy_score: float
    meta_score: float
    deck_fit: float
    cost_consideration: str  # owned, common_craft, uncommon_craft, rare_craft, mythic_craft
    reasons: List[str]
    cmc: float = 0.0  # Converted mana cost from Scryfall
    legality: Optional[Dict] = None  # Format legality from Scryfall
    oracle_text: Optional[str] = None  # Card text
    power_toughness: Optional[str] = None  # For creatures
    keywords: Optional[List[str]] = None  # Extracted keywords

class EnhancedRecommendationEngine:
    """AI-powered recommendation engine using live Scryfall data"""
    
    def __init__(self):
        self.scryfall = ScryfallAPI()
        self.card_cache = {}  # Cache for Scryfall data (session-only for recommendations)
        self.format_cache = {}  # Cache for format-legal cards (session-only for recommendations)
        self.persistent_cache = get_cache()  # Persistent cache instance
        self.archetype_patterns = self._load_archetype_patterns()
        self.synergy_keywords = self._load_synergy_keywords()
    
    def _load_archetype_patterns(self) -> Dict[str, Dict]:
        """Load enhanced archetype detection patterns"""
        return {
            "aggro": {
                "keywords": ["haste", "double strike", "first strike", "trample", "menace", "prowess"],
                "cmc_range": (1, 3),
                "creature_ratio_min": 0.5,
                "burn_spells": True,
                "cheap_removal": True
            },
            "control": {
                "keywords": ["flash", "hexproof", "ward", "vigilance", "lifelink"],
                "cmc_range": (2, 6),
                "creature_ratio_max": 0.3,
                "counterspells": True,
                "board_wipes": True,
                "card_draw": True
            },
            "midrange": {
                "keywords": ["flying", "deathtouch", "lifelink", "vigilance", "reach"],
                "cmc_range": (2, 5),
                "creature_ratio": (0.3, 0.6),
                "removal": True,
                "value_creatures": True
            },
            "combo": {
                "keywords": ["enters", "activated ability", "triggered ability", "sacrifice"],
                "tutoring": True,
                "protection": True,
                "enablers": True
            },
            "ramp": {
                "keywords": ["reach", "flying", "trample"],
                "cmc_range": (1, 8),
                "mana_dorks": True,
                "big_threats": True,
                "land_ramp": True
            }
        }
    
    def _load_synergy_keywords(self) -> Dict[str, Dict[str, List[str]]]:
        """Load keyword synergy patterns"""
        return {
            "tribal_synergies": {
                "elf": ["elvish", "elf", "heritage druid", "wirewood", "llanowar"],
                "goblin": ["goblin", "krenko", "warren", "lackey", "matron"],
                "vampire": ["vampire", "bloodthirst", "lifelink", "madness"],
                "angel": ["angel", "flying", "vigilance", "lifelink"],
                "dragon": ["dragon", "flying", "haste", "treasure"]
            },
            "mechanic_synergies": {
                "artifacts": ["artifact", "metalcraft", "affinity", "improvise"],
                "graveyard": ["graveyard", "flashback", "dredge", "delve", "escape"],
                "spells_matter": ["prowess", "spell", "instant", "sorcery", "storm"],
                "sacrifice": ["sacrifice", "dies", "death", "aristocrats"],
                "lifegain": ["lifegain", "lifelink", "soul sister", "ajani's pridemate"]
            },
            "color_synergies": {
                "white": ["lifegain", "vigilance", "flying", "protection"],
                "blue": ["card draw", "counterspell", "flying", "scry"],
                "black": ["destroy", "discard", "sacrifice", "deathtouch"],
                "red": ["haste", "burn", "damage", "sacrifice"],
                "green": ["ramp", "big creatures", "fight", "reach"]
            }
        }
    
    def generate_recommendations(self, deck: Deck, collection=None, count: int = 15, format_name: str = "standard", randomize: bool = True) -> List[SmartRecommendation]:
        """Generate intelligent recommendations using Scryfall data with meta caching"""
        if not deck or not deck.get_mainboard_cards():
            return []
        
        # Analyze current deck
        deck_analysis = self._analyze_deck_advanced(deck)
        
        # Create cache key for meta recommendations based on deck characteristics
        # This allows caching of meta-relevant recommendations for similar deck archetypes
        cache_key = self._create_meta_cache_key(deck_analysis, format_name, count)
        
        # Check if we have cached recommendations for this archetype/format
        if not randomize:  # Only use cache for non-randomized requests
            cached_recommendations = self.persistent_cache.get_meta_data(cache_key)
            if cached_recommendations:
                print(f"Using cached recommendations for {deck_analysis['archetype']} in {format_name}")
                return cached_recommendations[:count]
        
        # Add randomization for varied results
        if randomize:
            import time
            random.seed(int(time.time() * 1000) % 1000000)  # Use current time for seed variation
        
        recommendations = []
        current_cards = set(card.card.name.lower() for card in deck.get_mainboard_cards())
        
        # Increase limits significantly to support larger result sets
        # Scale limits based on the requested count
        base_multiplier = max(1, count // 50)  # Scale up for larger requests
        
        # 1. Get format staples using Scryfall
        staple_recs = self._get_format_staples_scryfall(
            format_name, deck_analysis["colors"], current_cards, limit=50 * base_multiplier
        )
        recommendations.extend(staple_recs)
        
        # 2. Get archetype-specific cards
        archetype_recs = self._get_archetype_recommendations_scryfall(
            deck_analysis["archetype"], deck_analysis["colors"], current_cards, format_name, limit=40 * base_multiplier
        )
        recommendations.extend(archetype_recs)
        
        # 3. Get synergy-based recommendations
        synergy_recs = self._get_synergy_recommendations_scryfall(
            deck, deck_analysis, current_cards, format_name, limit=40 * base_multiplier
        )
        recommendations.extend(synergy_recs)
        
        # 4. Fill mana curve gaps
        curve_recs = self._get_curve_recommendations_scryfall(
            deck_analysis["curve"], deck_analysis["colors"], current_cards, format_name, limit=30 * base_multiplier
        )
        recommendations.extend(curve_recs)
        
        # Remove duplicates and sort by confidence
        unique_recs = self._deduplicate_and_rank(recommendations)
        
        # Check collection availability
        if collection:
            self._update_collection_status(unique_recs, collection)
        
        # Cache the recommendations for future use (only for non-randomized requests)
        if not randomize and unique_recs:
            self.persistent_cache.cache_meta_data(cache_key, unique_recs)
            print(f"Cached recommendations for {deck_analysis['archetype']} in {format_name}")
        
        return unique_recs[:count]
    
    def _create_meta_cache_key(self, deck_analysis: Dict, format_name: str, count: int) -> str:
        """Create cache key for meta recommendations based on deck characteristics"""
        # Create a stable key based on archetype, colors, and format
        colors_str = ''.join(sorted(deck_analysis["colors"]))
        archetype = deck_analysis["archetype"]
        
        # Include count range to avoid cache misses for different request sizes
        count_range = "small" if count <= 50 else "medium" if count <= 100 else "large"
        
        cache_key = f"meta_recs_{format_name}_{archetype}_{colors_str}_{count_range}"
        return cache_key
    
    def _analyze_deck_advanced(self, deck: Deck) -> Dict[str, Any]:
        """Advanced deck analysis using Scryfall data"""
        mainboard = deck.get_mainboard_cards()
        
        # Basic analysis
        color_count = Counter()
        curve = Counter()
        type_count = Counter()
        keywords = Counter()
        total_cards = 0
        
        # Get Scryfall data for deck cards
        deck_card_data = {}
        for deck_card in mainboard:
            card_name = deck_card.card.name
            total_cards += deck_card.quantity
            
            # Get enhanced card data
            if card_name not in deck_card_data:
                scryfall_data = self._get_card_data_cached(card_name)
                deck_card_data[card_name] = scryfall_data
            
            card_data = deck_card_data[card_name]
            
            # Analyze with Scryfall data if available
            if card_data:
                # Colors
                for color in card_data.get("colors", []):
                    color_count[color] += deck_card.quantity
                
                # Mana curve
                cmc = card_data.get("cmc", deck_card.card.converted_mana_cost)
                curve[min(cmc, 7)] += deck_card.quantity
                
                # Types
                type_line = card_data.get("type_line", deck_card.card.card_type or "")
                primary_type = type_line.split()[0].lower() if type_line else "unknown"
                type_count[primary_type] += deck_card.quantity
                
                # Extract keywords from oracle text
                oracle_text = card_data.get("oracle_text", "")
                extracted_keywords = self._extract_keywords_from_text(oracle_text)
                for keyword in extracted_keywords:
                    keywords[keyword] += deck_card.quantity
            else:
                # Fallback to basic card data
                for color in deck_card.card.colors:
                    color_count[color] += deck_card.quantity
                curve[min(deck_card.card.converted_mana_cost, 7)] += deck_card.quantity
        
        # Determine archetype
        archetype = self._determine_archetype_advanced(curve, type_count, keywords, color_count, total_cards)
        
        return {
            "archetype": archetype,
            "colors": list(color_count.keys()),
            "primary_colors": [color for color, _ in color_count.most_common(2)],
            "curve": dict(curve),
            "keywords": dict(keywords.most_common(10)),
            "types": dict(type_count),
            "total_cards": total_cards,
            "creature_ratio": type_count.get("creature", 0) / total_cards if total_cards > 0 else 0
        }
    
    def _get_card_data_cached(self, card_name: str) -> Optional[Dict]:
        """Get card data from cache or Scryfall"""
        if card_name in self.card_cache:
            return self.card_cache[card_name]
        
        try:
            # Search for the card using Scryfall API
            search_results = self.scryfall.search_cards(card_name)
            
            if search_results:
                card = search_results[0]  # Take first result
                card_data = {
                    "name": card.name,
                    "mana_cost": card.mana_cost,
                    "cmc": card.cmc,
                    "type_line": card.type_line,
                    "oracle_text": card.oracle_text,
                    "colors": card.colors,
                    "rarity": card.rarity,
                    "legalities": card.legalities,
                    "power": getattr(card, 'power', None),
                    "toughness": getattr(card, 'toughness', None)
                }
                self.card_cache[card_name] = card_data
                return card_data
        except Exception as e:
            print(f"Error fetching card data for {card_name}: {e}")
        
        return None
    
    def _get_format_staples_scryfall(self, format_name: str, colors: List[str], current_cards: Set[str], limit: int = 8) -> List[SmartRecommendation]:
        """Get format staples using Scryfall search"""
        recommendations = []
        
        try:
            # Search for popular cards in the format - use simpler query
            query = f"legal:{format_name.lower()}"
            
            if colors:
                # Use color identity instead of exact colors for better matches
                color_identity = "".join(sorted(colors)).lower()
                if color_identity:
                    query += f" ci<={color_identity}"
            
            # Focus on competitive cards but less restrictive
            query += " -t:basic cmc<=4 (r:u OR r:r)"  # Removed mythic restriction and lowered CMC
            
            print(f"Format staples query: {query}")  # Debug print
            cards_data = self.scryfall.search_cards(query, limit=300, max_pages=2)  # Much more aggressive - up to 2 pages
            
            if not cards_data:
                # Fallback to even simpler query for more variety
                fallback_query = f"legal:{format_name.lower()} -t:basic cmc<=5"  # More inclusive CMC
                print(f"Fallback query: {fallback_query}")
                cards_data = self.scryfall.search_cards(fallback_query, limit=300, max_pages=2)  # More results
            
            print(f"Found {len(cards_data) if cards_data else 0} format staples")  # Debug print
            
            if not cards_data:
                return recommendations
            
            # Shuffle results for variety in lazy loading
            random.shuffle(cards_data)
            
            # Process results with increased limit
            for card in cards_data[:limit * 5]:  # Much more generous limit (increased from limit * 3)
                card_name = card.name
                
                if card_name.lower() in current_cards:
                    continue
                
                # Skip cards that don't fit colors
                if not self._is_color_compatible_scryfall_card(card, colors, format_name):
                    continue
                
                # Calculate recommendation score
                confidence = self._calculate_staple_confidence(card, format_name)
                
                if confidence < 0.5:  # Skip low-confidence recommendations
                    continue
                
                reasons = [
                    f"Format staple in {format_name.title()}",
                    "Proven competitive card",
                    f"High play rate in {format_name} decks"
                ]
                
                # Add specific reasons based on card characteristics
                cmc = card.cmc
                if cmc <= 2:
                    reasons.append("Efficient early game play")
                elif cmc >= 5:
                    reasons.append("Powerful late game threat")
                else:
                    reasons.append("Solid midrange option")
                
                # Calculate dynamic synergy and deck fit scores
                temp_analysis = {
                    "colors": colors,  # Use the colors parameter passed to this method
                    "archetype": "midrange",
                    "curve": {},
                    "keywords": {}
                }
                
                synergy_score = self._calculate_color_synergy(card, temp_analysis, format_name)
                deck_fit_score = self._calculate_deck_fit_score(card, temp_analysis, format_name)
                meta_score = self._calculate_meta_score(card, "midrange")
                
                # Extract keywords
                keywords = self._extract_keywords_from_text(card.oracle_text)
                
                rec = SmartRecommendation(
                    card_name=card_name,
                    mana_cost=card.mana_cost,
                    card_type=card.type_line,
                    rarity=card.rarity,
                    confidence=confidence,
                    synergy_score=synergy_score,
                    meta_score=meta_score,
                    deck_fit=deck_fit_score,
                    cost_consideration="unknown",
                    reasons=reasons,
                    cmc=card.cmc,
                    legality=card.legalities,
                    oracle_text=card.oracle_text,
                    power_toughness=self._get_power_toughness_from_card(card),
                    keywords=keywords
                )
                
                recommendations.append(rec)
                
                if len(recommendations) >= limit:
                    break
        
        except Exception as e:
            print(f"Error fetching format staples: {e}")
        
        return recommendations
    
    def _get_archetype_recommendations_scryfall(self, archetype: str, colors: List[str], current_cards: Set[str], format_name: str = "standard", limit: int = 6) -> List[SmartRecommendation]:
        """Get archetype-specific recommendations using Scryfall"""
        recommendations = []
        
        if archetype not in self.archetype_patterns:
            return recommendations
        
        pattern = self.archetype_patterns[archetype]
        
        try:
            # Build archetype-specific search - use simpler query
            query = f"legal:{format_name.lower()}"
            
            if colors:
                color_identity = "".join(sorted(colors)).lower()
                query += f" ci<={color_identity}"
            
            # Add archetype-specific keywords with OR logic
            if "keywords" in pattern:
                keyword_query = " OR ".join([f'o:"{kw}"' for kw in pattern["keywords"][:2]])  # Top 2 keywords
                if keyword_query:
                    query += f" ({keyword_query})"
            
            # Add CMC range
            if "cmc_range" in pattern:
                min_cmc, max_cmc = pattern["cmc_range"]
                query += f" cmc>={min_cmc} cmc<={max_cmc}"
            
            query += " -t:basic"
            
            print(f"Archetype query: {query}")  # Debug
            cards_data = self.scryfall.search_cards(query, limit=200, max_pages=2)  # Use pagination for more results
            
            if not cards_data:
                return recommendations
            
            # Shuffle results for variety in lazy loading
            random.shuffle(cards_data)
            
            # Process and score results with increased limit
            for card in cards_data[:limit * 5]:  # Much more generous limit
                card_name = card.name
                
                if card_name.lower() in current_cards:
                    continue
                
                # Calculate advanced archetype fit with full deck analysis
                temp_analysis = {
                    "colors": colors,
                    "archetype": archetype,
                    "curve": {},
                    "keywords": {}
                }
                
                archetype_score = self._calculate_archetype_synergy(card, temp_analysis)
                synergy_score = self._calculate_color_synergy(card, temp_analysis, format_name)
                deck_fit_score = self._calculate_deck_fit_score(card, temp_analysis, format_name)
                
                if archetype_score < 0.4:
                    continue
                
                # Advanced confidence calculation
                confidence = self._calculate_advanced_confidence_score(
                    card, temp_analysis, (archetype_score + synergy_score) / 2
                )
                
                # Generate detailed reasons
                reasons = self._generate_synergy_reasons(
                    card, temp_analysis, f"archetype_{archetype}", archetype_score
                )
                
                keywords = self._extract_keywords_from_text(card.oracle_text)
                
                rec = SmartRecommendation(
                    card_name=card_name,
                    mana_cost=card.mana_cost,
                    card_type=card.type_line,
                    rarity=card.rarity,
                    confidence=confidence,
                    synergy_score=synergy_score,
                    meta_score=self._calculate_meta_score(card, archetype),
                    deck_fit=deck_fit_score,
                    cost_consideration="unknown",
                    reasons=reasons,
                    cmc=card.cmc,  # Add CMC field
                    legality=card.legalities,
                    oracle_text=card.oracle_text,
                    power_toughness=self._get_power_toughness_from_card(card),
                    keywords=keywords
                )
                
                recommendations.append(rec)
                
                if len(recommendations) >= limit:
                    break
        
        except Exception as e:
            print(f"Error fetching archetype recommendations: {e}")
        
        return recommendations
    
    def _get_synergy_recommendations_scryfall(self, deck: Deck, deck_analysis: Dict, current_cards: Set[str], format_name: str = "standard", limit: int = 6) -> List[SmartRecommendation]:
        """Get synergy-based recommendations using advanced scoring"""
        recommendations = []
        
        # Get deck analysis info
        colors = deck_analysis["colors"]
        keywords = deck_analysis["keywords"]
        archetype = deck_analysis["archetype"]
        curve = deck_analysis["curve"]
        
        # Advanced synergy approach - recommend cards based on multiple factors
        if not colors:
            return recommendations
        
        try:
            # Build sophisticated synergy queries based on deck characteristics
            queries = self._build_synergy_queries(colors, keywords, archetype, curve)
            
            for query_data in queries:
                query = query_data["query"]
                weight = query_data["weight"]
                synergy_type = query_data["type"]
                
                print(f"Synergy query ({synergy_type}): {query}")  # Debug
                cards_data = self.scryfall.search_cards(query, limit=100, max_pages=2)
                
                if not cards_data:
                    continue
                
                # Process results with advanced scoring
                for card in cards_data[:limit * 3]:
                    card_name = card.name
                    
                    if card_name.lower() in current_cards:
                        continue
                    
                    # Calculate advanced synergy score
                    synergy_score = self._calculate_advanced_synergy_score(
                        card, deck_analysis, synergy_type, weight
                    )
                    
                    # Calculate advanced confidence score
                    confidence = self._calculate_advanced_confidence_score(
                        card, deck_analysis, synergy_score
                    )
                    
                    # Generate detailed reasons
                    reasons = self._generate_synergy_reasons(
                        card, deck_analysis, synergy_type, synergy_score
                    )
                    
                    keywords_extracted = self._extract_keywords_from_text(card.oracle_text)
                    
                    rec = SmartRecommendation(
                        card_name=card_name,
                        mana_cost=card.mana_cost,
                        card_type=card.type_line,
                        rarity=card.rarity,
                        confidence=confidence,
                        synergy_score=synergy_score,
                        meta_score=self._calculate_meta_score(card, archetype),
                        deck_fit=self._calculate_deck_fit_score(card, deck_analysis),
                        cost_consideration="unknown",
                        reasons=reasons,
                        cmc=card.cmc,
                        legality=card.legalities,
                        oracle_text=card.oracle_text,
                        power_toughness=self._get_power_toughness_from_card(card),
                        keywords=keywords_extracted
                    )
                
                    recommendations.append(rec)
                
                if len(recommendations) >= limit:
                    break
        
        except Exception as e:
            print(f"Error fetching synergy recommendations: {e}")
        
        return recommendations
    
    def _build_synergy_queries(self, colors: List[str], keywords: Dict, archetype: str, curve: Dict) -> List[Dict]:
        """Build sophisticated synergy queries based on deck characteristics"""
        queries = []
        
        # Color-based synergy
        if colors:
            color_str = "".join(sorted(colors)).lower()
            queries.append({
                "query": f"legal:standard ci<={color_str} -t:basic",
                "weight": 1.0,
                "type": "color_synergy"
            })
        
        # Archetype-specific synergy
        archetype_keywords = self._get_archetype_search_terms(archetype)
        if archetype_keywords:
            for keyword in archetype_keywords[:2]:  # Top 2 keywords
                queries.append({
                    "query": f"legal:standard o:\"{keyword}\" -t:basic",
                    "weight": 0.8,
                    "type": f"archetype_{keyword}"
                })
        
        # Curve-based synergy (fill gaps)
        curve_gaps = self._identify_curve_gaps(curve)
        for cmc in curve_gaps[:2]:  # Top 2 gaps
            queries.append({
                "query": f"legal:standard cmc:{cmc} (r:c OR r:u) -t:basic",
                "weight": 0.6,
                "type": f"curve_cmc{cmc}"
            })
        
        # Keyword synergy
        top_keywords = sorted(keywords.items(), key=lambda x: x[1], reverse=True)[:3]
        for keyword, count in top_keywords:
            if count >= 2:  # Only if we have multiple instances
                queries.append({
                    "query": f"legal:standard o:\"{keyword}\" -t:basic",
                    "weight": 0.7,
                    "type": f"keyword_{keyword}"
                })
        
        return queries
    
    def _get_archetype_search_terms(self, archetype: str) -> List[str]:
        """Get search terms for specific archetypes"""
        archetype_terms = {
            "aggro": ["haste", "prowess", "first strike", "menace"],
            "control": ["counter", "draw", "exile", "destroy"],
            "midrange": ["enters", "whenever", "tap:", "untap"],
            "combo": ["search", "tutor", "sacrifice", "graveyard"],
            "ramp": ["mana", "land", "search", "ramp"],
            "burn": ["damage", "target", "player", "burn"],
            "tribal": ["elf", "goblin", "zombie", "human"],
            "artifacts": ["artifact", "tap:", "enters"]
        }
        return archetype_terms.get(archetype.lower(), [])
    
    def _identify_curve_gaps(self, curve: Dict) -> List[int]:
        """Identify the biggest gaps in mana curve"""
        total_cards = sum(curve.values())
        if total_cards == 0:
            return [1, 2, 3]  # Default curve positions
        
        ideal_percentages = {1: 0.20, 2: 0.30, 3: 0.25, 4: 0.15, 5: 0.10}
        gaps = []
        
        for cmc, ideal_pct in ideal_percentages.items():
            current_pct = curve.get(cmc, 0) / total_cards
            if current_pct < ideal_pct * 0.6:  # 40% below ideal
                gap_size = ideal_pct - current_pct
                gaps.append((cmc, gap_size))
        
        # Sort by gap size and return CMCs
        gaps.sort(key=lambda x: x[1], reverse=True)
        return [cmc for cmc, _ in gaps]
    
    def _calculate_advanced_synergy_score(self, card, deck_analysis: Dict, synergy_type: str, weight: float, format_name: str = "standard") -> float:
        """Calculate advanced synergy score based on multiple factors"""
        base_score = 0.0
        
        # Type-specific synergy calculation
        if synergy_type == "color_synergy":
            base_score = self._calculate_color_synergy(card, deck_analysis, format_name)
        elif synergy_type.startswith("archetype_"):
            base_score = self._calculate_archetype_synergy(card, deck_analysis)
        elif synergy_type.startswith("curve_"):
            base_score = self._calculate_curve_synergy(card, deck_analysis)
        elif synergy_type.startswith("keyword_"):
            base_score = self._calculate_keyword_synergy(card, deck_analysis, synergy_type)
        
        # Apply weight and additional factors
        synergy_score = base_score * weight
        
        # Bonus for efficient cards
        if hasattr(card, 'cmc') and card.cmc <= 3:
            synergy_score += 0.05
        
        # Bonus for versatile cards
        oracle_text = getattr(card, 'oracle_text', '').lower()
        if any(word in oracle_text for word in ['choose', 'either', 'or']):
            synergy_score += 0.1
        
        return min(synergy_score, 1.0)
    
    def _calculate_color_synergy(self, card, deck_analysis: Dict, format_name: str = "standard") -> float:
        """Calculate color-based synergy score with format-specific weighting"""
        deck_colors = set(deck_analysis.get("colors", []))
        card_colors = set(getattr(card, 'colors', []))
        
        # Determine if this is a singleton format where color identity is critical
        singleton_formats = {"commander", "edh", "brawl", "oathbreaker"}
        is_singleton = format_name.lower() in singleton_formats
        
        if not deck_colors:
            return 0.6 if not card_colors else 0.4  # Neutral for colorless in colorless deck
        
        if not card_colors:
            return 0.75 if is_singleton else 0.7  # Colorless cards slightly better in singleton
        
        # Perfect color identity match
        if card_colors <= deck_colors:  # Card colors are subset of deck colors
            color_overlap = len(card_colors.intersection(deck_colors))
            deck_size = len(deck_colors)
            
            if is_singleton:
                # In singleton formats, perfect color identity is MUCH more important
                if deck_size == 1:  # Mono-colored commander
                    return 0.88 + (color_overlap * 0.05)  # Max 0.93
                elif deck_size == 2:  # Two-color commander
                    return 0.82 + (color_overlap * 0.06)  # Max 0.94
                elif deck_size == 3:  # Three-color commander
                    return 0.78 + (color_overlap * 0.07)  # Max 0.99
                else:  # Four+ color commander
                    return 0.75 + (color_overlap * 0.08)  # Max 0.99
            else:
                # Standard constructed formats - color flexibility is less critical
                if deck_size == 1:  # Mono-colored deck
                    return 0.75 + (color_overlap * 0.05)  # Max 0.8
                elif deck_size == 2:  # Two-color deck
                    return 0.65 + (color_overlap * 0.08)  # Max 0.81
                else:  # Three+ color deck
                    return 0.55 + (color_overlap * 0.1)   # Max 0.85
        
        # Cards with colors outside commander's identity are UNPLAYABLE in singleton
        if is_singleton:
            # If any card color is not in deck colors, this card cannot be played
            if not card_colors <= deck_colors:
                return 0.05  # Nearly unplayable - severe penalty
        
        # Partial match gets lower score (only relevant for non-singleton)
        overlap = len(card_colors.intersection(deck_colors))
        if overlap > 0:
            overlap_ratio = overlap / len(card_colors)
            if is_singleton:
                # Even partial matches are problematic in singleton formats
                return 0.15 + (overlap_ratio * 0.15)  # Max 0.30
            else:
                return 0.3 + (overlap_ratio * 0.25)  # Max 0.55
        
        # No overlap - very low synergy, catastrophic in singleton
        return 0.02 if is_singleton else 0.15
    
    def _calculate_archetype_synergy(self, card, deck_analysis: Dict) -> float:
        """Calculate archetype-specific synergy with realistic scoring"""
        archetype = deck_analysis.get("archetype", "midrange").lower()
        oracle_text = getattr(card, 'oracle_text', '').lower()
        type_line = getattr(card, 'type_line', '').lower()
        cmc = getattr(card, 'cmc', 0)
        
        archetype_patterns = {
            "aggro": {
                "keywords": ["haste", "prowess", "first strike", "menace", "trample"],
                "cmc_sweet_spot": (1, 3),
                "creature_bonus": 0.15,
                "preferred_stats": ["power", "aggressive"]
            },
            "control": {
                "keywords": ["counter", "draw", "exile", "destroy", "flash"],
                "cmc_sweet_spot": (2, 6),
                "instant_sorcery_bonus": 0.2,
                "preferred_effects": ["removal", "card_advantage"]
            },
            "midrange": {
                "keywords": ["enters", "whenever", "tap", "untap", "value"],
                "cmc_sweet_spot": (2, 5),
                "versatility_bonus": 0.1,
                "preferred_effects": ["incremental_advantage"]
            },
            "combo": {
                "keywords": ["search", "tutor", "sacrifice", "graveyard", "storm"],
                "cmc_sweet_spot": (1, 4),
                "synergy_bonus": 0.25,
                "preferred_effects": ["engine", "enabler"]
            }
        }
        
        pattern = archetype_patterns.get(archetype, archetype_patterns["midrange"])
        score = 0.4  # Base archetype compatibility
        
        # Keyword matching (max +0.25)
        keyword_matches = sum(1 for kw in pattern["keywords"] if kw in oracle_text)
        keyword_bonus = min(keyword_matches * 0.08, 0.25)
        score += keyword_bonus
        
        # CMC curve fit (max +0.2)
        min_cmc, max_cmc = pattern["cmc_sweet_spot"]
        if min_cmc <= cmc <= max_cmc:
            if cmc == min_cmc + 1:  # Sweet spot
                score += 0.2
            else:
                score += 0.1
        elif cmc < min_cmc:
            score += 0.05  # Slightly early but okay
        else:
            score -= 0.05  # Too expensive for archetype
        
        # Type-specific bonuses (max +0.2)
        if archetype == "aggro" and "creature" in type_line:
            score += pattern.get("creature_bonus", 0)
        elif archetype == "control" and ("instant" in type_line or "sorcery" in type_line):
            score += pattern.get("instant_sorcery_bonus", 0)
        elif archetype == "combo" and any(word in oracle_text for word in ["search", "tutor", "sacrifice"]):
            score += pattern.get("synergy_bonus", 0)
        elif archetype == "midrange":
            # Midrange likes versatile cards
            if any(word in oracle_text for word in ["choose", "either", "mode"]):
                score += pattern.get("versatility_bonus", 0)
        
        # Cap the score at reasonable maximum (0.85)
        return min(score, 0.85)
    
    def _calculate_curve_synergy(self, card, deck_analysis: Dict) -> float:
        """Calculate curve-filling synergy with balanced scoring"""
        curve = deck_analysis.get("curve", {})
        cmc = getattr(card, 'cmc', 0)
        
        total_cards = sum(curve.values())
        if total_cards == 0:
            return 0.5  # Neutral if no curve data
        
        current_pct = curve.get(cmc, 0) / total_cards
        
        # Ideal percentages for different CMCs
        ideal_percentages = {
            1: 0.20, 2: 0.30, 3: 0.25, 4: 0.15, 5: 0.08, 6: 0.02, 7: 0.01
        }
        ideal_pct = ideal_percentages.get(cmc, 0.005)  # Very low for 8+ CMC
        
        # Calculate gap size
        gap_size = ideal_pct - current_pct
        
        if gap_size > 0.15:  # Big gap (>15% below ideal)
            return 0.75
        elif gap_size > 0.10:  # Medium gap (>10% below ideal)
            return 0.65
        elif gap_size > 0.05:  # Small gap (>5% below ideal)
            return 0.55
        elif gap_size > -0.05:  # Near ideal
            return 0.45
        elif gap_size > -0.10:  # Slightly oversaturated
            return 0.35
        else:  # Very oversaturated
            return 0.25
    
    def _calculate_keyword_synergy(self, card, deck_analysis: Dict, synergy_type: str) -> float:
        """Calculate keyword-based synergy"""
        keyword = synergy_type.split("_", 1)[1]  # Extract keyword from "keyword_X"
        oracle_text = getattr(card, 'oracle_text', '').lower()
        deck_keywords = deck_analysis.get("keywords", {})
        
        # Base score for having the keyword
        score = 0.4 if keyword in oracle_text else 0.2
        
        # Bonus based on how prevalent the keyword is in the deck
        keyword_count = deck_keywords.get(keyword, 0)
        if keyword_count >= 3:
            score += 0.3
        elif keyword_count >= 2:
            score += 0.2
        elif keyword_count >= 1:
            score += 0.1
        
        return min(score, 1.0)
    
    def _calculate_advanced_confidence_score(self, card, deck_analysis: Dict, synergy_score: float) -> float:
        """Calculate advanced confidence score using weighted multiplication for better distribution"""
        
        # Start with a base multiplier instead of additive
        confidence_multipliers = []
        
        # Synergy contribution (most important factor)
        synergy_weight = 0.5 + (synergy_score * 0.4)  # Range: 0.5 to 0.9
        confidence_multipliers.append(synergy_weight)
        
        # Rarity consideration (power correlation)
        rarity = getattr(card, 'rarity', 'common').lower()
        rarity_weights = {
            "mythic": 0.95,   # Very high confidence multiplier
            "rare": 0.85,     # High confidence multiplier  
            "uncommon": 0.75, # Good confidence multiplier
            "common": 0.65    # Moderate confidence multiplier
        }
        confidence_multipliers.append(rarity_weights.get(rarity, 0.65))
        
        # CMC efficiency factor
        cmc = getattr(card, 'cmc', 0)
        if cmc <= 1:
            cmc_weight = 0.9   # Very efficient
        elif cmc <= 2:
            cmc_weight = 0.85  # Highly efficient  
        elif cmc <= 3:
            cmc_weight = 0.8   # Efficient
        elif cmc <= 4:
            cmc_weight = 0.75  # Reasonable
        elif cmc <= 5:
            cmc_weight = 0.7   # Acceptable
        elif cmc <= 6:
            cmc_weight = 0.6   # Expensive
        else:
            cmc_weight = 0.5   # Very expensive
        
        confidence_multipliers.append(cmc_weight)
        
        # Type relevance factor
        type_line = getattr(card, 'type_line', '').lower()
        archetype = deck_analysis.get("archetype", "midrange").lower()
        
        if archetype == "aggro" and "creature" in type_line:
            type_weight = 0.9  # Perfect match
        elif archetype == "control" and ("instant" in type_line or "sorcery" in type_line):
            type_weight = 0.9  # Perfect match
        elif archetype == "midrange" and "creature" in type_line:
            type_weight = 0.85 # Good match
        elif "planeswalker" in type_line:
            type_weight = 0.88 # Usually powerful
        elif "creature" in type_line:
            type_weight = 0.75 # General creature
        elif "instant" in type_line or "sorcery" in type_line:
            type_weight = 0.7  # Spell
        else:
            type_weight = 0.65 # Other permanent
        
        confidence_multipliers.append(type_weight)
        
        # Card complexity/power indicator
        oracle_text = getattr(card, 'oracle_text', '')
        text_length = len(oracle_text)
        
        if text_length > 120:
            complexity_weight = 0.9  # Very complex, likely powerful
        elif text_length > 80:
            complexity_weight = 0.85 # Moderately complex
        elif text_length > 40:
            complexity_weight = 0.8  # Some complexity
        elif text_length > 15:
            complexity_weight = 0.75 # Simple but functional
        else:
            complexity_weight = 0.65 # Very simple
        
        confidence_multipliers.append(complexity_weight)
        
        # Keyword density (abilities indicator)
        keywords = self._extract_keywords_from_text(oracle_text)
        keyword_count = len(keywords)
        
        if keyword_count >= 3:
            keyword_weight = 0.9   # Many keywords, high power
        elif keyword_count >= 2:
            keyword_weight = 0.85  # Multiple keywords
        elif keyword_count >= 1:
            keyword_weight = 0.8   # Some keywords
        else:
            keyword_weight = 0.7   # No recognized keywords
        
        confidence_multipliers.append(keyword_weight)
        
        # Calculate final confidence using geometric mean for better distribution
        # This prevents any single factor from dominating
        product = 1.0
        for multiplier in confidence_multipliers:
            product *= multiplier
        
        # Take the nth root where n is number of factors
        final_confidence = product ** (1.0 / len(confidence_multipliers))
        
        # Apply slight randomization for more natural distribution (±2%)
        import random
        randomization = random.uniform(-0.02, 0.02)
        final_confidence += randomization
        
        # Ensure reasonable bounds (0.2 to 0.98 to avoid perfect scores)
        return max(0.2, min(final_confidence, 0.98))
    
    def _calculate_meta_score(self, card, archetype: str) -> float:
        """Calculate meta-game relevance score"""
        base_score = 0.5
        rarity = getattr(card, 'rarity', 'common').lower()
        
        # Rarity usually correlates with power level
        rarity_multipliers = {"mythic": 1.3, "rare": 1.2, "uncommon": 1.1, "common": 1.0}
        base_score *= rarity_multipliers.get(rarity, 1.0)
        
        # Archetype relevance
        oracle_text = getattr(card, 'oracle_text', '').lower()
        type_line = getattr(card, 'type_line', '').lower()
        
        archetype_relevance = {
            "aggro": ["haste", "prowess", "damage", "attack", "creature"],
            "control": ["counter", "draw", "destroy", "exile", "instant", "sorcery"],
            "midrange": ["enters", "whenever", "creature", "versatile"],
            "combo": ["search", "tutor", "sacrifice", "graveyard"]
        }
        
        relevant_terms = archetype_relevance.get(archetype.lower(), [])
        matches = sum(1 for term in relevant_terms if term in oracle_text or term in type_line)
        base_score += matches * 0.05
        
        return min(base_score, 1.0)
    
    def _calculate_deck_fit_score(self, card, deck_analysis: Dict, format_name: str = "standard") -> float:
        """Calculate how well card fits the deck's strategy"""
        score = 0.4
        
        # Color fit (25% - more important in singleton formats)
        color_score = self._calculate_color_synergy(card, deck_analysis, format_name)
        
        # Increase color weight for singleton formats
        singleton_formats = {"commander", "edh", "brawl", "oathbreaker"}
        is_singleton = format_name.lower() in singleton_formats
        color_weight = 0.4 if is_singleton else 0.25  # Higher weight for singleton
        
        score += color_score * color_weight
        
        # Adjust other weights for singleton formats
        curve_weight = 0.15 if is_singleton else 0.25  # Less important in singleton
        archetype_weight = 0.25 if is_singleton else 0.30  # Slightly less important  
        versatility_weight = 0.2 if is_singleton else 0.2  # Same importance
        
        # Curve fit
        curve_score = self._calculate_curve_synergy(card, deck_analysis)
        score += curve_score * curve_weight
        
        # Archetype fit
        archetype_score = self._calculate_archetype_synergy(card, deck_analysis)
        score += archetype_score * archetype_weight
        
        # Versatility bonus
        oracle_text = getattr(card, 'oracle_text', '').lower()
        if any(word in oracle_text for word in ['choose', 'either', 'or', 'mode', 'additional cost']):
            score += versatility_weight * 0.75  # 15% of base score
        
        # Multi-use bonus
        if any(word in oracle_text for word in ['tap:', 'activated ability', 'enters']):
            score += 0.05
        
        return min(score, 1.0)
    
    def _generate_synergy_reasons(self, card, deck_analysis: Dict, synergy_type: str, synergy_score: float, format_name: str = "standard") -> List[str]:
        """Generate detailed reasons for the recommendation"""
        reasons = []
        
        # Primary synergy reason with format-specific details
        if synergy_type == "color_synergy":
            colors = deck_analysis.get("colors", [])
            card_colors = getattr(card, 'colors', [])
            singleton_formats = {"commander", "edh", "brawl", "oathbreaker"}
            is_singleton = format_name.lower() in singleton_formats
            
            if set(card_colors) <= set(colors):
                if is_singleton:
                    reasons.append(f"✓ Legal in color identity ({'/'.join(card_colors) if card_colors else 'Colorless'})")
                else:
                    reasons.append(f"Perfect color match ({'/'.join(card_colors) if card_colors else 'Colorless'})")
            else:
                overlap = set(card_colors) & set(colors)
                if is_singleton:
                    off_colors = set(card_colors) - set(colors)
                    if off_colors:
                        reasons.append(f"⚠ Color identity violation ({'/'.join(off_colors)} not allowed)")
                    else:
                        reasons.append(f"Color identity compatible")
                else:
                    reasons.append(f"Color overlap with {'/'.join(overlap)}")
        
        elif synergy_type.startswith("archetype_"):
            archetype_keyword = synergy_type.split("_", 1)[1]
            reasons.append(f"Strong {archetype_keyword} synergy")
            
        elif synergy_type.startswith("curve_"):
            cmc = synergy_type.split("cmc")[1]
            reasons.append(f"Fills {cmc}-mana curve gap")
            
        elif synergy_type.startswith("keyword_"):
            keyword = synergy_type.split("_", 1)[1]
            reasons.append(f"Synergizes with existing {keyword} cards")
        
        # Quality indicators with format context
        if synergy_score > 0.8:
            if format_name.lower() in {"commander", "edh"}:
                reasons.append("Excellent Commander staple")
            else:
                reasons.append("Excellent synergy potential")
        elif synergy_score > 0.6:
            reasons.append("Good synergy with current cards")
        elif synergy_score > 0.4:
            reasons.append("Reasonable fit for deck")
        elif synergy_score < 0.2 and format_name.lower() in {"commander", "edh", "brawl"}:
            reasons.append("Not playable in this color identity")
        
        # Efficiency notes
        cmc = getattr(card, 'cmc', 0)
        if cmc <= 1:
            reasons.append("Highly efficient (low CMC)")
        elif cmc <= 3:
            reasons.append("Efficient mana cost")
        
        # Rarity consideration
        rarity = getattr(card, 'rarity', 'common').lower()
        if rarity in ["rare", "mythic"]:
            reasons.append(f"Powerful {rarity} with strong effects")
        elif rarity == "uncommon":
            reasons.append("Solid uncommon with good value")
        else:
            reasons.append("Accessible common with consistent effects")
        
        # Versatility
        oracle_text = getattr(card, 'oracle_text', '').lower()
        if 'choose' in oracle_text or 'either' in oracle_text:
            reasons.append("Versatile with multiple modes")
        
        return reasons[:10]  # Limit to 4 most relevant reasons
    
    def _get_curve_recommendations_scryfall(self, curve: Dict[int, int], colors: List[str], current_cards: Set[str], format_name: str, limit: int = 5) -> List[SmartRecommendation]:
        """Get mana curve improvement recommendations using Scryfall"""
        recommendations = []
        
        total_cards = sum(curve.values())
        if total_cards == 0:
            return recommendations
        
        # Define ideal curve (adjustable by archetype in future)
        ideal_curve = {1: 0.20, 2: 0.30, 3: 0.25, 4: 0.15, 5: 0.10}
        
        # Find biggest curve gaps
        curve_gaps = []
        for cmc, ideal_percentage in ideal_curve.items():
            current_percentage = curve.get(cmc, 0) / total_cards
            if current_percentage < ideal_percentage * 0.6:  # 40% below ideal
                gap_size = ideal_percentage - current_percentage
                curve_gaps.append((cmc, gap_size))
        
        # Sort by gap size
        curve_gaps.sort(key=lambda x: x[1], reverse=True)
        
        # Get recommendations for biggest gaps
        for cmc, gap_size in curve_gaps[:2]:  # Top 2 gaps
            try:
                query = f"f:{format_name.lower()} cmc:{cmc}"
                
                if colors:
                    color_identity = "".join(sorted(colors)).lower()
                    query += f" ci<={color_identity}"
                
                query += " -t:basic (r:c OR r:u OR r:r)"  # Exclude mythics for curve fillers
                
                cards_data = self.scryfall.search_cards(query, limit=150, max_pages=2)  # Use pagination for curve fillers
                
                if not cards_data:
                    continue
                
                # Process results with increased limit
                for card in cards_data[:limit * 4]:  # More generous limit for curve fillers
                    card_name = card.name
                    
                    if card_name.lower() in current_cards:
                        continue
                    
                    # Calculate advanced curve-filling scores
                    temp_analysis = {
                        "colors": colors,
                        "archetype": "midrange",
                        "curve": curve,
                        "keywords": {}
                    }
                    
                    curve_synergy = self._calculate_curve_synergy(card, temp_analysis)
                    confidence = self._calculate_advanced_confidence_score(
                        card, temp_analysis, curve_synergy
                    )
                    
                    # Boost confidence for filling big gaps
                    confidence = min(confidence + gap_size * 0.3, 1.0)
                    
                    reasons = [
                        f"Fills critical {cmc}-mana gap ({gap_size:.1%} below ideal)",
                        f"Improves mana curve balance",
                        f"Efficient {cmc}-drop for curve"
                    ]
                    
                    # Add efficiency note
                    if cmc <= 3:
                        reasons.append("Strong early-to-mid game presence")
                    
                    synergy_score = self._calculate_color_synergy(card, temp_analysis, format_name)
                    deck_fit_score = self._calculate_deck_fit_score(card, temp_analysis, format_name)
                    meta_score = self._calculate_meta_score(card, "midrange")
                    
                    keywords = self._extract_keywords_from_text(card.oracle_text)
                    
                    rec = SmartRecommendation(
                        card_name=card_name,
                        mana_cost=card.mana_cost,
                        card_type=card.type_line,
                        rarity=card.rarity,
                        confidence=confidence,
                        synergy_score=synergy_score,
                        meta_score=meta_score,
                        deck_fit=deck_fit_score,
                        cost_consideration="unknown",
                        reasons=reasons,
                        cmc=card.cmc,  # Add CMC field
                        legality=card.legalities,
                        oracle_text=card.oracle_text,
                        power_toughness=self._get_power_toughness_from_card(card),
                        keywords=keywords
                    )
                    
                    recommendations.append(rec)
                    
                    if len(recommendations) >= limit:
                        break
            
            except Exception as e:
                print(f"Error fetching curve recommendations: {e}")
                continue
        
        return recommendations
    
    def _determine_archetype_advanced(self, curve, types, keywords, colors, total_cards):
        """Determine archetype using advanced patterns"""
        if total_cards == 0:
            return "unknown"
        
        scores = {}
        
        for archetype, pattern in self.archetype_patterns.items():
            score = 0
            
            # Check CMC range
            if "cmc_range" in pattern:
                min_cmc, max_cmc = pattern["cmc_range"]
                cards_in_range = sum(count for cmc, count in curve.items() if min_cmc <= cmc <= max_cmc)
                range_ratio = cards_in_range / total_cards
                if range_ratio > 0.5:
                    score += 0.3
            
            # Check creature ratio
            creature_ratio = types.get("creature", 0) / total_cards
            if "creature_ratio_min" in pattern and creature_ratio >= pattern["creature_ratio_min"]:
                score += 0.2
            elif "creature_ratio_max" in pattern and creature_ratio <= pattern["creature_ratio_max"]:
                score += 0.2
            elif "creature_ratio" in pattern:
                min_ratio, max_ratio = pattern["creature_ratio"]
                if min_ratio <= creature_ratio <= max_ratio:
                    score += 0.2
            
            # Check keywords
            if "keywords" in pattern:
                keyword_matches = sum(keywords.get(kw, 0) for kw in pattern["keywords"])
                if keyword_matches > 0:
                    score += min(0.4, keyword_matches / total_cards * 2)
            
            # Check special flags
            for flag in ["burn_spells", "counterspells", "board_wipes", "tutoring"]:
                if pattern.get(flag) and self._check_deck_feature(keywords, types, flag):
                    score += 0.15
            
            scores[archetype] = score
        
        best_archetype = max(scores.items(), key=lambda x: x[1])
        return best_archetype[0] if best_archetype[1] > 0.3 else "midrange"
    
    def _check_deck_feature(self, keywords, types, feature):
        """Check if deck has specific features"""
        feature_keywords = {
            "burn_spells": ["damage", "burn", "lightning"],
            "counterspells": ["counter", "negate"],
            "board_wipes": ["destroy all", "exile all"],
            "tutoring": ["search", "tutor"]
        }
        
        if feature in feature_keywords:
            return any(kw in str(keywords) for kw in feature_keywords[feature])
        return False
    
    def _extract_keywords_from_text(self, oracle_text: str) -> List[str]:
        """Extract keywords and abilities from oracle text"""
        if not oracle_text:
            return []
        
        text_lower = oracle_text.lower()
        keywords = []
        
        # Define keyword patterns
        keyword_patterns = {
            "haste": ["haste"],
            "flying": ["flying"],
            "trample": ["trample"],
            "lifelink": ["lifelink"],
            "deathtouch": ["deathtouch"],
            "vigilance": ["vigilance"],
            "first strike": ["first strike"],
            "double strike": ["double strike"],
            "hexproof": ["hexproof"],
            "ward": ["ward"],
            "menace": ["menace"],
            "prowess": ["prowess"],
            "reach": ["reach"],
            "indestructible": ["indestructible"],
            "lifegain": ["gain", "life"],
            "card draw": ["draw", "card"],
            "removal": ["destroy", "exile"],
            "counter": ["counter", "target spell"],
            "sacrifice": ["sacrifice"],
            "graveyard": ["graveyard"],
            "artifact": ["artifact"],
            "enters": ["enters the battlefield", "when ~ enters"]
        }
        
        for keyword, patterns in keyword_patterns.items():
            if any(pattern in text_lower for pattern in patterns):
                keywords.append(keyword)
        
        return keywords
    
    def _is_color_compatible_scryfall_card(self, card, deck_colors: List[str], format_name: str = "standard") -> bool:
        """Check color compatibility using Scryfall card with format-specific rules"""
        if not deck_colors:
            return True
        
        card_colors = card.colors
        
        # Colorless cards are always compatible
        if not card_colors:
            return True
        
        # For singleton formats, check color identity more strictly
        singleton_formats = {"commander", "edh", "brawl", "oathbreaker"}
        is_singleton = format_name.lower() in singleton_formats
        
        if is_singleton:
            # In singleton formats, ALL colors in the card must be in commander's identity
            # This is stricter than just mana cost - includes colors in rules text too
            card_color_identity = getattr(card, 'color_identity', card_colors)
            return all(color in deck_colors for color in card_color_identity)
        else:
            # In constructed formats, just check mana cost colors
            return all(color in deck_colors for color in card_colors)
    
    def _calculate_staple_confidence(self, card, format_name: str) -> float:
        """Calculate confidence score for format staples with balanced distribution"""
        
        # Use multiplicative factors instead of additive for better distribution
        confidence_factors = []
        
        # Format legality factor
        legality = card.legalities
        if legality.get(format_name.lower()) == "legal":
            legality_factor = 0.9  # High confidence for legal cards
        else:
            legality_factor = 0.6  # Lower confidence for non-legal
        confidence_factors.append(legality_factor)
        
        # Rarity power correlation factor
        rarity = card.rarity.lower() if hasattr(card, 'rarity') else 'common'
        rarity_factors = {
            "mythic": 0.95,   # Mythics are usually format defining
            "rare": 0.88,     # Rares are often powerful  
            "uncommon": 0.78, # Uncommons can be very good
            "common": 0.68    # Commons are accessible but lower power
        }
        confidence_factors.append(rarity_factors.get(rarity, 0.68))
        
        # CMC efficiency factor
        cmc = getattr(card, 'cmc', 0)
        if cmc <= 1:
            cmc_factor = 0.95  # Very efficient
        elif cmc == 2:
            cmc_factor = 0.9   # Highly efficient
        elif cmc == 3:
            cmc_factor = 0.85  # Efficient
        elif cmc == 4:
            cmc_factor = 0.8   # Reasonable
        elif cmc == 5:
            cmc_factor = 0.75  # Acceptable
        elif cmc == 6:
            cmc_factor = 0.65  # Expensive
        else:
            cmc_factor = 0.55  # Very expensive
        confidence_factors.append(cmc_factor)
        
        # Text complexity factor (indicator of power/versatility)
        oracle_text = getattr(card, 'oracle_text', '')
        text_length = len(oracle_text)
        
        if text_length > 100:
            text_factor = 0.9   # Very complex, likely powerful
        elif text_length > 60:
            text_factor = 0.85  # Moderately complex
        elif text_length > 30:
            text_factor = 0.8   # Some complexity
        elif text_length > 10:
            text_factor = 0.75  # Basic effects
        else:
            text_factor = 0.65  # Very simple
        confidence_factors.append(text_factor)
        
        # Type relevance factor
        type_line = getattr(card, 'type_line', '').lower()
        if "planeswalker" in type_line:
            type_factor = 0.92  # Planeswalkers are usually impactful
        elif "instant" in type_line or "sorcery" in type_line:
            type_factor = 0.85  # Spells often define formats
        elif "creature" in type_line:
            type_factor = 0.82  # Creatures are format staples
        elif "artifact" in type_line or "enchantment" in type_line:
            type_factor = 0.78  # Permanents provide value
        else:
            type_factor = 0.7   # Other types
        confidence_factors.append(type_factor)
        
        # Calculate geometric mean for balanced distribution
        product = 1.0
        for factor in confidence_factors:
            product *= factor
            
        confidence = product ** (1.0 / len(confidence_factors))
        
        # Add slight variance for natural distribution
        import random
        variance = random.uniform(-0.03, 0.03)
        confidence += variance
        
        # Ensure bounds (0.35 to 0.95 for staples)
        return max(0.35, min(confidence, 0.95))
    
    def _calculate_archetype_fit_card(self, card, archetype_pattern: Dict) -> float:
        """Calculate how well a card fits an archetype"""
        score = 0.0
        
        oracle_text = card.oracle_text.lower()
        type_line = card.type_line.lower()
        cmc = card.cmc
        
        # Check keywords
        if "keywords" in archetype_pattern:
            keyword_matches = sum(1 for kw in archetype_pattern["keywords"] if kw in oracle_text)
            score += min(0.4, keyword_matches * 0.1)
        
        # Check CMC range
        if "cmc_range" in archetype_pattern:
            min_cmc, max_cmc = archetype_pattern["cmc_range"]
            if min_cmc <= cmc <= max_cmc:
                score += 0.3
        
        # Check creature ratio preference
        is_creature = "creature" in type_line
        if archetype_pattern.get("creature_ratio_min") and is_creature:
            score += 0.2
        elif archetype_pattern.get("creature_ratio_max") and not is_creature:
            score += 0.2
        
        return min(score, 1.0)
    
    def _get_power_toughness_from_card(self, card) -> Optional[str]:
        """Extract power/toughness for creatures"""
        power = getattr(card, 'power', None)
        toughness = getattr(card, 'toughness', None)
        
        if power is not None and toughness is not None:
            return f"{power}/{toughness}"
        return None
    
    def _deduplicate_and_rank(self, recommendations: List[SmartRecommendation]) -> List[SmartRecommendation]:
        """Remove duplicates and rank by confidence"""
        seen_cards = set()
        unique_recs = []
        
        for rec in recommendations:
            if rec.card_name.lower() not in seen_cards:
                seen_cards.add(rec.card_name.lower())
                unique_recs.append(rec)
        
        # Sort by confidence (primary) and synergy score (secondary)
        unique_recs.sort(key=lambda x: (x.confidence, x.synergy_score), reverse=True)
        
        return unique_recs
    
    def _update_collection_status(self, recommendations: List[SmartRecommendation], collection) -> None:
        """Update cost consideration based on collection"""
        for rec in recommendations:
            is_owned, quantity = self._check_collection(rec.card_name, collection)
            
            if is_owned:
                rec.cost_consideration = "owned"
                rec.confidence += 0.1  # Boost for owned cards
            else:
                rarity_costs = {
                    "common": "common_craft",
                    "uncommon": "uncommon_craft", 
                    "rare": "rare_craft",
                    "mythic": "mythic_craft"
                }
                rec.cost_consideration = rarity_costs.get(rec.rarity, "unknown")
    
    def _check_collection(self, card_name: str, collection) -> Tuple[bool, int]:
        """Check if card is owned in collection"""
        if not collection or not hasattr(collection, 'cards'):
            return False, 0
        
        # Direct lookup
        if card_name in collection.cards:
            collection_card = collection.cards[card_name]
            return True, collection_card.quantity + collection_card.quantity_foil
        
        # Case-insensitive search
        for name, collection_card in collection.cards.items():
            if name.lower() == card_name.lower():
                return True, collection_card.quantity + collection_card.quantity_foil
        
        return False, 0

def get_smart_recommendations(deck: Deck, collection=None, count: int = 15, format_name: str = "standard", randomize: bool = True) -> List[SmartRecommendation]:
    """Main function to get smart recommendations using Scryfall data"""
    engine = EnhancedRecommendationEngine()
    return engine.generate_recommendations(deck, collection, count, format_name, randomize)
