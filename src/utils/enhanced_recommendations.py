"""
Enhanced AI-powered recommendation system using Scryfall API data
"""

import asyncio
import json
import random
from typing import List, Dict, Any, Optional, Tuple, Set
from collections import Counter, defaultdict
from dataclasses import dataclass
import math

from models.card import Card
from models.deck import Deck, DeckCard
from utils.scryfall_api import ScryfallAPI

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
    legality: Optional[Dict] = None  # Format legality from Scryfall
    oracle_text: Optional[str] = None  # Card text
    power_toughness: Optional[str] = None  # For creatures
    keywords: Optional[List[str]] = None  # Extracted keywords

class EnhancedRecommendationEngine:
    """AI-powered recommendation engine using live Scryfall data"""
    
    def __init__(self):
        self.scryfall = ScryfallAPI()
        self.card_cache = {}  # Cache for Scryfall data
        self.format_cache = {}  # Cache for format-legal cards
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
    
    def _load_synergy_keywords(self) -> Dict[str, List[str]]:
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
    
    async def generate_recommendations(self, deck: Deck, collection=None, count: int = 15, format_name: str = "standard") -> List[SmartRecommendation]:
        """Generate intelligent recommendations using Scryfall data"""
        if not deck or not deck.get_mainboard_cards():
            return []
        
        # Analyze current deck
        deck_analysis = await self._analyze_deck_advanced(deck)
        
        recommendations = []
        current_cards = set(card.card.name.lower() for card in deck.get_mainboard_cards())
        
        # 1. Get format staples using Scryfall
        staple_recs = await self._get_format_staples_scryfall(
            format_name, deck_analysis["colors"], current_cards, limit=8
        )
        recommendations.extend(staple_recs)
        
        # 2. Get archetype-specific cards
        archetype_recs = await self._get_archetype_recommendations_scryfall(
            deck_analysis["archetype"], deck_analysis["colors"], current_cards, limit=6
        )
        recommendations.extend(archetype_recs)
        
        # 3. Get synergy-based recommendations
        synergy_recs = await self._get_synergy_recommendations_scryfall(
            deck, deck_analysis, current_cards, limit=6
        )
        recommendations.extend(synergy_recs)
        
        # 4. Fill mana curve gaps
        curve_recs = await self._get_curve_recommendations_scryfall(
            deck_analysis["curve"], deck_analysis["colors"], current_cards, format_name, limit=5
        )
        recommendations.extend(curve_recs)
        
        # Remove duplicates and sort by confidence
        unique_recs = self._deduplicate_and_rank(recommendations)
        
        # Check collection availability
        if collection:
            self._update_collection_status(unique_recs, collection)
        
        return unique_recs[:count]
    
    async def _analyze_deck_advanced(self, deck: Deck) -> Dict[str, Any]:
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
                scryfall_data = await self._get_card_data_cached(card_name)
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
    
    async def _get_format_staples_scryfall(self, format_name: str, colors: List[str], current_cards: Set[str], limit: int = 8) -> List[SmartRecommendation]:
        """Get format staples using Scryfall search"""
        recommendations = []
        
        try:
            # Build search query for popular cards in format
            query_parts = [f"legal:{format_name.lower()}"]
            
            if colors:
                # Include colorless cards and cards in deck colors
                color_identity = "".join(sorted(colors)).lower()
                if color_identity:
                    query_parts.append(f"ci<={color_identity}")
            
            # Focus on competitive cards
            query_parts.extend([
                "-t:basic",  # Exclude basic lands
                "cmc<=6",    # Reasonable CMC
                "(r:u OR r:r OR r:m)",  # Uncommon, rare, mythic (commons are usually less impactful)
                "is:modern"  # Focus on modern-era cards for better power level
            ])
            
            query = " ".join(query_parts)
            cards_data = await self.scryfall.search_cards(query)
            
            if not cards_data:
                return recommendations
            
            # Process results
            for card_data in cards_data[:limit * 2]:  # Get extra to account for filtering
                card_name = card_data.get("name", "")
                
                if card_name.lower() in current_cards:
                    continue
                
                # Skip cards that don't fit colors
                if not self._is_color_compatible_scryfall(card_data, colors):
                    continue
                
                # Calculate recommendation score
                confidence = self._calculate_staple_confidence(card_data, format_name)
                
                if confidence < 0.5:  # Skip low-confidence recommendations
                    continue
                
                reasons = [
                    f"Format staple in {format_name.title()}",
                    "Proven competitive card",
                    f"High play rate in {format_name} decks"
                ]
                
                # Extract keywords
                oracle_text = card_data.get("oracle_text", "")
                keywords = self._extract_keywords_from_text(oracle_text)
                
                rec = SmartRecommendation(
                    card_name=card_name,
                    mana_cost=card_data.get("mana_cost", ""),
                    card_type=card_data.get("type_line", ""),
                    rarity=card_data.get("rarity", "common"),
                    confidence=confidence,
                    synergy_score=0.6,
                    meta_score=0.8,  # High meta score for staples
                    deck_fit=0.7,
                    cost_consideration="unknown",
                    reasons=reasons,
                    legality=card_data.get("legalities", {}),
                    oracle_text=oracle_text,
                    power_toughness=self._get_power_toughness(card_data),
                    keywords=keywords
                )
                
                recommendations.append(rec)
                
                if len(recommendations) >= limit:
                    break
        
        except Exception as e:
            print(f"Error fetching format staples: {e}")
        
        return recommendations
    
    async def _get_archetype_recommendations_scryfall(self, archetype: str, colors: List[str], current_cards: Set[str], limit: int = 6) -> List[SmartRecommendation]:
        """Get archetype-specific recommendations using Scryfall"""
        recommendations = []
        
        if archetype not in self.archetype_patterns:
            return recommendations
        
        pattern = self.archetype_patterns[archetype]
        
        try:
            # Build archetype-specific search
            query_parts = ["legal:standard"]  # Default to standard, could be made configurable
            
            if colors:
                color_identity = "".join(sorted(colors)).lower()
                query_parts.append(f"ci<={color_identity}")
            
            # Add archetype-specific keywords
            if "keywords" in pattern:
                keyword_query = " OR ".join([f'o:"{kw}"' for kw in pattern["keywords"][:3]])  # Top 3 keywords
                if keyword_query:
                    query_parts.append(f"({keyword_query})")
            
            # Add CMC range
            if "cmc_range" in pattern:
                min_cmc, max_cmc = pattern["cmc_range"]
                query_parts.append(f"cmc>={min_cmc} cmc<={max_cmc}")
            
            query_parts.append("-t:basic")
            
            query = " ".join(query_parts)
            cards_data = await self.scryfall.search_cards(query)
            
            if not cards_data:
                return recommendations
            
            # Process and score results
            for card_data in cards_data[:limit * 2]:
                card_name = card_data.get("name", "")
                
                if card_name.lower() in current_cards:
                    continue
                
                # Calculate archetype fit
                archetype_score = self._calculate_archetype_fit(card_data, pattern)
                
                if archetype_score < 0.4:
                    continue
                
                confidence = 0.6 + archetype_score * 0.3
                
                reasons = [
                    f"Perfect fit for {archetype} strategy",
                    f"Matches {archetype} patterns",
                    "Strong archetype synergy"
                ]
                
                oracle_text = card_data.get("oracle_text", "")
                keywords = self._extract_keywords_from_text(oracle_text)
                
                rec = SmartRecommendation(
                    card_name=card_name,
                    mana_cost=card_data.get("mana_cost", ""),
                    card_type=card_data.get("type_line", ""),
                    rarity=card_data.get("rarity", "common"),
                    confidence=confidence,
                    synergy_score=archetype_score,
                    meta_score=0.7,
                    deck_fit=0.9,
                    cost_consideration="unknown",
                    reasons=reasons,
                    legality=card_data.get("legalities", {}),
                    oracle_text=oracle_text,
                    power_toughness=self._get_power_toughness(card_data),
                    keywords=keywords
                )
                
                recommendations.append(rec)
                
                if len(recommendations) >= limit:
                    break
        
        except Exception as e:
            print(f"Error fetching archetype recommendations: {e}")
        
        return recommendations
    
    async def _get_synergy_recommendations_scryfall(self, deck: Deck, deck_analysis: Dict, current_cards: Set[str], limit: int = 6) -> List[SmartRecommendation]:
        """Get synergy-based recommendations using Scryfall"""
        recommendations = []
        
        # Analyze deck for synergy patterns
        deck_keywords = deck_analysis["keywords"]
        deck_types = deck_analysis["types"]
        colors = deck_analysis["colors"]
        
        # Find strongest synergy themes
        synergy_themes = []
        
        # Check for tribal synergies
        for tribe, tribe_keywords in self.synergy_keywords["tribal_synergies"].items():
            tribe_count = sum(deck_keywords.get(kw, 0) for kw in tribe_keywords)
            if tribe_count >= 2:  # Significant tribal presence
                synergy_themes.append(("tribal", tribe, tribe_count))
        
        # Check for mechanic synergies  
        for mechanic, mechanic_keywords in self.synergy_keywords["mechanic_synergies"].items():
            mechanic_count = sum(deck_keywords.get(kw, 0) for kw in mechanic_keywords)
            if mechanic_count >= 3:  # Strong mechanic theme
                synergy_themes.append(("mechanic", mechanic, mechanic_count))
        
        # Sort by strength
        synergy_themes.sort(key=lambda x: x[2], reverse=True)
        
        # Get recommendations for top synergy themes
        for theme_type, theme_name, theme_strength in synergy_themes[:2]:  # Top 2 themes
            try:
                if theme_type == "tribal":
                    query = f'legal:standard t:creature o:"{theme_name}"'
                elif theme_type == "mechanic":
                    mechanic_keywords = self.synergy_keywords["mechanic_synergies"][theme_name]
                    keyword_query = " OR ".join([f'o:"{kw}"' for kw in mechanic_keywords[:2]])
                    query = f"legal:standard ({keyword_query})"
                else:
                    continue
                
                if colors:
                    color_identity = "".join(sorted(colors)).lower()
                    query += f" ci<={color_identity}"
                
                query += " -t:basic"
                
                cards_data = await self.scryfall.search_cards(query)
                
                if not cards_data:
                    continue
                
                # Process results
                for card_data in cards_data[:limit]:
                    card_name = card_data.get("name", "")
                    
                    if card_name.lower() in current_cards:
                        continue
                    
                    synergy_score = min(1.0, theme_strength / 10.0)
                    confidence = 0.7 + synergy_score * 0.2
                    
                    reasons = [
                        f"Strong {theme_name} synergy",
                        f"Enhances existing {theme_name} theme",
                        f"Works with {theme_strength} cards in deck"
                    ]
                    
                    oracle_text = card_data.get("oracle_text", "")
                    keywords = self._extract_keywords_from_text(oracle_text)
                    
                    rec = SmartRecommendation(
                        card_name=card_name,
                        mana_cost=card_data.get("mana_cost", ""),
                        card_type=card_data.get("type_line", ""),
                        rarity=card_data.get("rarity", "common"),
                        confidence=confidence,
                        synergy_score=synergy_score,
                        meta_score=0.6,
                        deck_fit=0.9,
                        cost_consideration="unknown",
                        reasons=reasons,
                        legality=card_data.get("legalities", {}),
                        oracle_text=oracle_text,
                        power_toughness=self._get_power_toughness(card_data),
                        keywords=keywords
                    )
                    
                    recommendations.append(rec)
                    
                    if len(recommendations) >= limit:
                        break
            
            except Exception as e:
                print(f"Error fetching synergy recommendations: {e}")
                continue
        
        return recommendations
    
    async def _get_curve_recommendations_scryfall(self, curve: Dict[int, int], colors: List[str], current_cards: Set[str], format_name: str, limit: int = 5) -> List[SmartRecommendation]:
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
                query_parts = [f"legal:{format_name.lower()}", f"cmc:{cmc}"]
                
                if colors:
                    color_identity = "".join(sorted(colors)).lower()
                    query_parts.append(f"ci<={color_identity}")
                
                query_parts.extend(["-t:basic", "(r:c OR r:u OR r:r)"])  # Exclude mythics for curve fillers
                
                query = " ".join(query_parts)
                cards_data = await self.scryfall.search_cards(query)
                
                if not cards_data:
                    continue
                
                # Process results
                for card_data in cards_data[:3]:  # Max 3 cards per CMC
                    card_name = card_data.get("name", "")
                    
                    if card_name.lower() in current_cards:
                        continue
                    
                    confidence = 0.6 + gap_size
                    
                    reasons = [
                        f"Fills {cmc}-mana curve gap",
                        f"Improves mana curve balance",
                        f"Good {cmc}-drop option"
                    ]
                    
                    oracle_text = card_data.get("oracle_text", "")
                    keywords = self._extract_keywords_from_text(oracle_text)
                    
                    rec = SmartRecommendation(
                        card_name=card_name,
                        mana_cost=card_data.get("mana_cost", ""),
                        card_type=card_data.get("type_line", ""),
                        rarity=card_data.get("rarity", "common"),
                        confidence=min(confidence, 1.0),
                        synergy_score=0.5,
                        meta_score=0.6,
                        deck_fit=0.8,
                        cost_consideration="unknown",
                        reasons=reasons,
                        legality=card_data.get("legalities", {}),
                        oracle_text=oracle_text,
                        power_toughness=self._get_power_toughness(card_data),
                        keywords=keywords
                    )
                    
                    recommendations.append(rec)
                    
                    if len(recommendations) >= limit:
                        break
            
            except Exception as e:
                print(f"Error fetching curve recommendations: {e}")
                continue
        
        return recommendations
    
    async def _get_card_data_cached(self, card_name: str) -> Optional[Dict]:
        """Get card data from cache or Scryfall"""
        if card_name in self.card_cache:
            return self.card_cache[card_name]
        
        try:
            card_data = await self.scryfall.get_card_by_name(card_name)
            self.card_cache[card_name] = card_data
            return card_data
        except Exception as e:
            print(f"Error fetching card data for {card_name}: {e}")
            return None
    
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
    
    def _is_color_compatible_scryfall(self, card_data: Dict, deck_colors: List[str]) -> bool:
        """Check color compatibility using Scryfall color identity"""
        if not deck_colors:
            return True
        
        card_colors = card_data.get("colors", [])
        
        # Colorless cards are always compatible
        if not card_colors:
            return True
        
        # Check if all card colors are in deck colors
        return all(color in deck_colors for color in card_colors)
    
    def _calculate_staple_confidence(self, card_data: Dict, format_name: str) -> float:
        """Calculate confidence score for format staples"""
        base_confidence = 0.6
        
        # Boost for competitive formats
        legality = card_data.get("legalities", {})
        if legality.get(format_name.lower()) == "legal":
            base_confidence += 0.2
        
        # Boost for rare/mythic (usually more powerful)
        rarity = card_data.get("rarity", "common")
        if rarity in ["rare", "mythic"]:
            base_confidence += 0.1
        elif rarity == "uncommon":
            base_confidence += 0.05
        
        return min(base_confidence, 1.0)
    
    def _calculate_archetype_fit(self, card_data: Dict, archetype_pattern: Dict) -> float:
        """Calculate how well a card fits an archetype"""
        score = 0.0
        
        oracle_text = card_data.get("oracle_text", "").lower()
        type_line = card_data.get("type_line", "").lower()
        cmc = card_data.get("cmc", 0)
        
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
    
    def _get_power_toughness(self, card_data: Dict) -> Optional[str]:
        """Extract power/toughness for creatures"""
        power = card_data.get("power")
        toughness = card_data.get("toughness")
        
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

# Async wrapper for the main recommendation function
async def get_smart_recommendations_async(deck: Deck, collection=None, count: int = 15, format_name: str = "standard") -> List[SmartRecommendation]:
    """Async wrapper for generating smart recommendations"""
    engine = EnhancedRecommendationEngine()
    return await engine.generate_recommendations(deck, collection, count, format_name)

def get_smart_recommendations(deck: Deck, collection=None, count: int = 15, format_name: str = "standard") -> List[SmartRecommendation]:
    """Synchronous wrapper that runs the async recommendation engine"""
    return asyncio.run(get_smart_recommendations_async(deck, collection, count, format_name))
