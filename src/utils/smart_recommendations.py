"""
Enhanced AI-powered recommendation system using intelligent analysis patterns
"""

import json
import random
from typing import List, Dict, Any, Optional, Tuple
from collections import Counter, defaultdict
from dataclasses import dataclass
import math

from models.card import Card
from models.deck import Deck, DeckCard

@dataclass
class SmartRecommendation:
    """Enhanced recommendation with detailed reasoning"""
    card_name: str
    mana_cost: str
    card_type: str
    rarity: str
    confidence: float
    reasons: List[str]
    synergy_score: float
    meta_score: float
    deck_fit: float
    cost_consideration: str  # "owned", "common_craft", "rare_craft", "mythic_craft"
    cmc: float = 0.0  # Converted mana cost from Scryfall
    legality: Optional[Dict[str, str]] = None  # Format legality information
    oracle_text: str = ""  # Card oracle text
    power_toughness: Optional[str] = None  # Power/Toughness for creatures
    keywords: Optional[List[str]] = None  # Extracted keywords

class IntelligentRecommendationEngine:
    """AI-powered recommendation engine that analyzes deck patterns"""
    
    def __init__(self):
        self.format_staples = self._load_format_staples()
        self.synergy_patterns = self._load_synergy_patterns()
        self.archetype_cards = self._load_archetype_cards()
        self.mana_curve_suggestions = self._load_curve_suggestions()
    
    def _load_format_staples(self) -> Dict[str, List[Dict]]:
        """Load popular cards by format"""
        return {
            "standard": [
                {"name": "Lightning Bolt", "mana_cost": "R", "type": "Instant", "rarity": "common", "tags": ["burn", "removal"], "popularity": 95},
                {"name": "Counterspell", "mana_cost": "UU", "type": "Instant", "rarity": "common", "tags": ["control", "counter"], "popularity": 90},
                {"name": "Swords to Plowshares", "mana_cost": "W", "type": "Instant", "rarity": "uncommon", "tags": ["removal", "exile"], "popularity": 88},
                {"name": "Dark Ritual", "mana_cost": "B", "type": "Instant", "rarity": "common", "tags": ["ramp", "fast_mana"], "popularity": 75},
                {"name": "Giant Growth", "mana_cost": "G", "type": "Instant", "rarity": "common", "tags": ["pump", "combat"], "popularity": 65},
                {"name": "Brainstorm", "mana_cost": "U", "type": "Instant", "rarity": "common", "tags": ["draw", "selection"], "popularity": 92},
                {"name": "Sol Ring", "mana_cost": "1", "type": "Artifact", "rarity": "uncommon", "tags": ["ramp", "colorless"], "popularity": 98},
                {"name": "Llanowar Elves", "mana_cost": "G", "type": "Creature", "rarity": "common", "tags": ["ramp", "elf", "early"], "popularity": 80},
                {"name": "Serra Angel", "mana_cost": "3WW", "type": "Creature", "rarity": "uncommon", "tags": ["flying", "vigilance", "midrange"], "popularity": 60},
                {"name": "Shivan Dragon", "mana_cost": "4RR", "type": "Creature", "rarity": "rare", "tags": ["flying", "big", "finisher"], "popularity": 55},
                {"name": "Wrath of God", "mana_cost": "2WW", "type": "Sorcery", "rarity": "rare", "tags": ["board_wipe", "control"], "popularity": 85},
                {"name": "Birds of Paradise", "mana_cost": "G", "type": "Creature", "rarity": "rare", "tags": ["ramp", "flying", "fixing"], "popularity": 78},
                {"name": "Thoughtseize", "mana_cost": "B", "type": "Sorcery", "rarity": "rare", "tags": ["discard", "control"], "popularity": 82},
                {"name": "Path to Exile", "mana_cost": "W", "type": "Instant", "rarity": "uncommon", "tags": ["removal", "exile"], "popularity": 87},
                {"name": "Ancestral Recall", "mana_cost": "U", "type": "Instant", "rarity": "mythic", "tags": ["draw", "power"], "popularity": 100},
            ],
            "historic": [
                {"name": "Teferi, Time Raveler", "mana_cost": "1WU", "type": "Planeswalker", "rarity": "rare", "tags": ["control", "tempo"], "popularity": 85},
                {"name": "Collected Company", "mana_cost": "3G", "type": "Instant", "rarity": "rare", "tags": ["creature", "value"], "popularity": 80},
                {"name": "Thoughtseize", "mana_cost": "B", "type": "Sorcery", "rarity": "rare", "tags": ["discard", "control"], "popularity": 90},
                {"name": "Lightning Bolt", "mana_cost": "R", "type": "Instant", "rarity": "common", "tags": ["burn", "removal"], "popularity": 95},
                {"name": "Fatal Push", "mana_cost": "B", "type": "Instant", "rarity": "uncommon", "tags": ["removal", "efficient"], "popularity": 88},
            ]
        }
    
    def _load_synergy_patterns(self) -> Dict[str, List[str]]:
        """Define synergy patterns for recommendations"""
        return {
            "burn_spells": ["Lightning Bolt", "Lava Spike", "Chain Lightning", "Rift Bolt", "Shard Volley"],
            "counterspells": ["Counterspell", "Mana Leak", "Force of Negation", "Cryptic Command", "Remand"],
            "card_draw": ["Brainstorm", "Ponder", "Preordain", "Divination", "Opt"],
            "removal": ["Swords to Plowshares", "Path to Exile", "Lightning Bolt", "Fatal Push", "Terminate"],
            "ramp": ["Llanowar Elves", "Birds of Paradise", "Sol Ring", "Rampant Growth", "Nature's Lore"],
            "aggressive_creatures": ["Goblin Guide", "Monastery Swiftspear", "Champion of the Parish", "Delver of Secrets"],
            "control_finishers": ["Serra Angel", "Teferi, Hero of Dominaria", "Jace, the Mind Sculptor", "Elspeth, Sun's Champion"],
            "board_wipes": ["Wrath of God", "Day of Judgment", "Supreme Verdict", "Pyroclasm", "Anger of the Gods"],
            "combo_pieces": ["Dark Ritual", "Entomb", "Reanimate", "Show and Tell", "Sneak Attack"],
            "tribal_elves": ["Llanowar Elves", "Elvish Mystic", "Heritage Druid", "Nettle Sentinel", "Wirewood Symbiote"],
            "tribal_goblins": ["Goblin Guide", "Goblin Lackey", "Goblin Matron", "Goblin Ringleader", "Goblin Chieftain"],
        }
    
    def _load_archetype_cards(self) -> Dict[str, List[str]]:
        """Cards that define specific archetypes"""
        return {
            "aggro": ["Lightning Bolt", "Goblin Guide", "Monastery Swiftspear", "Chain Lightning", "Lava Spike"],
            "control": ["Counterspell", "Wrath of God", "Serra Angel", "Brainstorm", "Swords to Plowshares"],
            "midrange": ["Thoughtseize", "Lightning Bolt", "Tarmogoyf", "Dark Confidant", "Bloodbraid Elf"],
            "ramp": ["Llanowar Elves", "Rampant Growth", "Sol Ring", "Birds of Paradise", "Shivan Dragon"],
            "combo": ["Dark Ritual", "Entomb", "Reanimate", "Show and Tell", "Sneak Attack"],
            "tempo": ["Delver of Secrets", "Daze", "Force of Will", "Lightning Bolt", "Brainstorm"],
        }
    
    def _load_curve_suggestions(self) -> Dict[int, List[str]]:
        """Mana curve improvement suggestions"""
        return {
            1: ["Lightning Bolt", "Swords to Plowshares", "Brainstorm", "Thoughtseize", "Llanowar Elves", "Path to Exile"],
            2: ["Counterspell", "Lightning Helix", "Remand", "Tarmogoyf", "Dark Confidant"],
            3: ["Collected Company", "Teferi, Time Raveler", "Kolaghan's Command", "Electrolyze"],
            4: ["Wrath of God", "Cryptic Command", "Bloodbraid Elf", "Restoration Angel"],
            5: ["Serra Angel", "Force of Will", "Baneslayer Angel", "Mulldrifter"],
            6: ["Shivan Dragon", "Primeval Titan", "Inferno Titan", "Sun Titan"]
        }
    
    def analyze_deck_strategy(self, deck: Deck) -> Dict[str, Any]:
        """Analyze deck to determine its strategy and needs"""
        if not deck or not deck.get_mainboard_cards():
            return {"strategy": "unknown", "colors": [], "curve": {}, "themes": []}
        
        mainboard = deck.get_mainboard_cards()
        
        # Analyze colors
        color_count = Counter()
        for deck_card in mainboard:
            for color in deck_card.card.colors:
                color_count[color] += deck_card.quantity
        
        # Analyze mana curve
        curve = Counter()
        for deck_card in mainboard:
            cmc = deck_card.card.converted_mana_cost
            curve[min(cmc, 7)] += deck_card.quantity  # Cap at 7+
        
        # Analyze card types
        type_count = Counter()
        themes = []
        
        for deck_card in mainboard:
            card_type = deck_card.card.card_type.split()[0].lower() if deck_card.card.card_type else "unknown"
            type_count[card_type] += deck_card.quantity
            
            # Check for themes in card text
            text = deck_card.card.text.lower() if deck_card.card.text else ""
            if "haste" in text or "attack" in text:
                themes.append("aggressive")
            if "counter" in text and "spell" in text:
                themes.append("control")
            if "search" in text or "library" in text:
                themes.append("tutor")
            if "draw" in text:
                themes.append("card_draw")
        
        # Determine strategy
        strategy = self._determine_strategy(curve, type_count, themes, color_count)
        
        return {
            "strategy": strategy,
            "colors": list(color_count.keys()),
            "primary_colors": [color for color, count in color_count.most_common(2)],
            "curve": dict(curve),
            "themes": list(set(themes)),
            "type_distribution": dict(type_count),
            "total_cards": sum(card.quantity for card in mainboard)
        }
    
    def _determine_strategy(self, curve: Counter, types: Counter, themes: List[str], colors: Counter) -> str:
        """Determine deck strategy from analysis"""
        total_cards = sum(curve.values())
        if total_cards == 0:
            return "unknown"
        
        # Low curve with aggressive themes
        low_curve_percentage = (curve[1] + curve[2]) / total_cards
        if low_curve_percentage > 0.6 and "aggressive" in themes:
            return "aggro"
        
        # High instant/sorcery count with control themes
        spell_percentage = (types.get("instant", 0) + types.get("sorcery", 0)) / total_cards
        if spell_percentage > 0.4 and "control" in themes:
            return "control"
        
        # Balanced curve with mix of threats and answers
        if 0.3 < low_curve_percentage < 0.6 and spell_percentage > 0.2:
            return "midrange"
        
        # High mana curve
        high_curve_percentage = (curve[5] + curve[6] + curve[7]) / total_cards
        if high_curve_percentage > 0.3:
            return "ramp"
        
        # Multiple colors and tutors/search effects
        if len(colors) >= 3 and "tutor" in themes:
            return "combo"
        
        return "midrange"  # Default
    
    def generate_recommendations(self, deck: Deck, collection=None, count: int = 15, format_name: str = "standard") -> List[SmartRecommendation]:
        """Generate intelligent recommendations for a deck"""
        if not deck:
            return []
        
        analysis = self.analyze_deck_strategy(deck)
        strategy = analysis["strategy"]
        colors = analysis["primary_colors"]
        curve = analysis["curve"]
        
        recommendations = []
        
        # Get current deck cards for avoiding duplicates
        current_cards = set(card.card.name.lower() for card in deck.get_mainboard_cards())
        
        # 1. Strategy-based recommendations
        strategy_recs = self._get_strategy_recommendations(strategy, colors, current_cards)
        recommendations.extend(strategy_recs)
        
        # 2. Mana curve improvements
        curve_recs = self._get_curve_recommendations(curve, colors, current_cards)
        recommendations.extend(curve_recs)
        
        # 3. Format staples
        staple_recs = self._get_format_staples_recommendations(format_name, colors, current_cards)
        recommendations.extend(staple_recs)
        
        # 4. Synergy improvements
        synergy_recs = self._get_synergy_recommendations(deck, current_cards)
        recommendations.extend(synergy_recs)
        
        # Remove duplicates and sort by confidence
        seen_cards = set()
        unique_recs = []
        for rec in recommendations:
            if rec.card_name.lower() not in seen_cards:
                seen_cards.add(rec.card_name.lower())
                unique_recs.append(rec)
        
        # Sort by confidence and return top recommendations
        unique_recs.sort(key=lambda x: x.confidence, reverse=True)
        
        # Check collection availability if provided
        if collection:
            for rec in unique_recs:
                is_owned, quantity = self._check_collection(rec.card_name, collection)
                if is_owned:
                    rec.cost_consideration = "owned"
                    rec.confidence += 0.1  # Boost confidence for owned cards
                elif rec.rarity == "common":
                    rec.cost_consideration = "common_craft"
                elif rec.rarity == "uncommon":
                    rec.cost_consideration = "uncommon_craft"
                elif rec.rarity == "rare":
                    rec.cost_consideration = "rare_craft"
                else:
                    rec.cost_consideration = "mythic_craft"
        
        return unique_recs[:count]
    
    def _get_strategy_recommendations(self, strategy: str, colors: List[str], current_cards: set) -> List[SmartRecommendation]:
        """Get recommendations based on deck strategy"""
        recommendations = []
        
        if strategy not in self.archetype_cards:
            return recommendations
        
        archetype_cards = self.archetype_cards[strategy]
        
        for card_name in archetype_cards[:8]:  # Top 8 cards for strategy
            if card_name.lower() in current_cards:
                continue
            
            card_data = self._find_card_data(card_name)
            if not card_data:
                continue
            
            # Check color compatibility
            if not self._is_color_compatible(card_data, colors):
                continue
            
            confidence = 0.8 + random.uniform(-0.1, 0.1)
            reasons = [f"Essential {strategy} card", f"Fits {strategy} strategy perfectly"]
            
            rec = SmartRecommendation(
                card_name=card_name,
                mana_cost=card_data["mana_cost"],
                card_type=card_data["type"],
                rarity=card_data["rarity"],
                confidence=confidence,
                reasons=reasons,
                synergy_score=0.9,
                meta_score=card_data.get("popularity", 50) / 100.0,
                deck_fit=0.9,
                cost_consideration="unknown"
            )
            recommendations.append(rec)
        
        return recommendations
    
    def _get_curve_recommendations(self, curve: Dict[int, int], colors: List[str], current_cards: set) -> List[SmartRecommendation]:
        """Get recommendations to improve mana curve"""
        recommendations = []
        total_cards = sum(curve.values())
        
        if total_cards == 0:
            return recommendations
        
        # Find curve gaps
        ideal_curve = {1: 0.25, 2: 0.3, 3: 0.2, 4: 0.15, 5: 0.1}
        
        for cmc, ideal_percentage in ideal_curve.items():
            current_percentage = curve.get(cmc, 0) / total_cards
            if current_percentage < ideal_percentage * 0.7:  # 30% below ideal
                # Suggest cards for this slot
                candidates = self.mana_curve_suggestions.get(cmc, [])
                
                for card_name in candidates[:3]:
                    if card_name.lower() in current_cards:
                        continue
                    
                    card_data = self._find_card_data(card_name)
                    if not card_data or not self._is_color_compatible(card_data, colors):
                        continue
                    
                    confidence = 0.7 + (ideal_percentage - current_percentage)
                    reasons = [f"Improves {cmc}-mana curve", f"Fills gap at {cmc} mana"]
                    
                    rec = SmartRecommendation(
                        card_name=card_name,
                        mana_cost=card_data["mana_cost"],
                        card_type=card_data["type"],
                        rarity=card_data["rarity"],
                        confidence=min(confidence, 1.0),
                        reasons=reasons,
                        synergy_score=0.6,
                        meta_score=card_data.get("popularity", 50) / 100.0,
                        deck_fit=0.8,
                        cost_consideration="unknown"
                    )
                    recommendations.append(rec)
        
        return recommendations
    
    def _get_format_staples_recommendations(self, format_name: str, colors: List[str], current_cards: set) -> List[SmartRecommendation]:
        """Get popular format staples"""
        recommendations = []
        
        staples = self.format_staples.get(format_name.lower(), self.format_staples.get("standard", []))
        
        for card_data in staples[:10]:  # Top 10 staples
            card_name = card_data["name"]
            if card_name.lower() in current_cards:
                continue
            
            if not self._is_color_compatible(card_data, colors):
                continue
            
            popularity = card_data.get("popularity", 50)
            confidence = 0.5 + (popularity / 100.0) * 0.3
            
            reasons = [f"Format staple ({popularity}% play rate)", "Proven competitive card"]
            
            rec = SmartRecommendation(
                card_name=card_name,
                mana_cost=card_data["mana_cost"],
                card_type=card_data["type"],
                rarity=card_data["rarity"],
                confidence=confidence,
                reasons=reasons,
                synergy_score=0.5,
                meta_score=popularity / 100.0,
                deck_fit=0.6,
                cost_consideration="unknown"
            )
            recommendations.append(rec)
        
        return recommendations
    
    def _get_synergy_recommendations(self, deck: Deck, current_cards: set) -> List[SmartRecommendation]:
        """Get recommendations based on synergies with current cards"""
        recommendations = []
        
        # Analyze current cards for synergy patterns
        deck_cards = [card.card.name for card in deck.get_mainboard_cards()]
        
        for pattern_name, pattern_cards in self.synergy_patterns.items():
            # Check how many cards from this pattern we already have
            matching_cards = [card for card in deck_cards if card in pattern_cards]
            
            if len(matching_cards) >= 2:  # We have synergy potential
                # Suggest more cards from this pattern
                for card_name in pattern_cards:
                    if card_name.lower() in current_cards:
                        continue
                    
                    card_data = self._find_card_data(card_name)
                    if not card_data:
                        continue
                    
                    confidence = 0.6 + (len(matching_cards) * 0.1)
                    reasons = [f"Synergizes with {', '.join(matching_cards[:2])}", f"Strengthens {pattern_name} theme"]
                    
                    rec = SmartRecommendation(
                        card_name=card_name,
                        mana_cost=card_data["mana_cost"],
                        card_type=card_data["type"],
                        rarity=card_data["rarity"],
                        confidence=min(confidence, 1.0),
                        reasons=reasons,
                        synergy_score=0.8,
                        meta_score=card_data.get("popularity", 50) / 100.0,
                        deck_fit=0.9,
                        cost_consideration="unknown"
                    )
                    recommendations.append(rec)
        
        return recommendations
    
    def _find_card_data(self, card_name: str) -> Optional[Dict]:
        """Find card data across all format databases"""
        for format_cards in self.format_staples.values():
            for card_data in format_cards:
                if card_data["name"] == card_name:
                    return card_data
        return None
    
    def _is_color_compatible(self, card_data: Dict, deck_colors: List[str]) -> bool:
        """Check if card colors are compatible with deck colors"""
        if not deck_colors:
            return True  # No color restriction
        
        mana_cost = card_data.get("mana_cost", "")
        
        # Colorless cards are always compatible
        if not any(c in mana_cost for c in "WUBRG"):
            return True
        
        # Check if card's colors are subset of deck colors
        card_colors = []
        for color in "WUBRG":
            if color in mana_cost:
                card_colors.append(color)
        
        return all(color in deck_colors for color in card_colors)
    
    def _check_collection(self, card_name: str, collection) -> Tuple[bool, int]:
        """Check if card is owned in collection"""
        if not collection or not hasattr(collection, 'cards'):
            return False, 0
        
        # collection.cards is a dictionary mapping card_name -> CollectionCard
        if card_name in collection.cards:
            collection_card = collection.cards[card_name]
            return True, collection_card.quantity + collection_card.quantity_foil
        
        # Try case-insensitive search
        for name, collection_card in collection.cards.items():
            if name.lower() == card_name.lower():
                return True, collection_card.quantity + collection_card.quantity_foil
        
        return False, 0
