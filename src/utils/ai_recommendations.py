"""
AI-powered card recommendation system for Magic: The Gathering Arena
"""

import json
import os
from typing import List, Dict, Any, Optional, Tuple, Set
from collections import defaultdict, Counter
from dataclasses import dataclass
import random
import math

from models.card import Card
from models.deck import Deck, DeckCard

@dataclass
class CardRecommendation:
    """Represents a card recommendation with reasoning"""
    card: Card
    confidence: float  # 0.0 to 1.0
    reasons: List[str]
    synergy_score: float
    popularity_score: float
    archetype_fit: float

@dataclass
class SynergyRule:
    """Represents a synergy relationship between cards"""
    card_names: List[str]
    synergy_type: str  # "combo", "tribe", "theme", "curve", "removal"
    strength: float  # 0.0 to 1.0
    description: str

class CardDatabase:
    """Extended card database with synergy and meta information"""
    
    def __init__(self):
        self.cards_db = {}
        self.synergy_rules = []
        self.archetype_templates = {}
        self.popularity_data = {}
        self.load_card_database()
        self.load_synergy_rules()
        self.load_archetype_templates()
    
    def load_card_database(self):
        """Load extended card database with synergy information"""
        # This would typically load from a comprehensive database
        # For now, I'll include some popular cards as examples
        sample_cards = [
            {
                "name": "Lightning Bolt",
                "mana_cost": "R",
                "converted_mana_cost": 1,
                "card_type": "Instant",
                "rarity": "Common",
                "colors": ["R"],
                "text": "Lightning Bolt deals 3 damage to any target.",
                "tags": ["burn", "removal", "aggressive"],
                "popularity": 0.9
            },
            {
                "name": "Counterspell",
                "mana_cost": "UU",
                "converted_mana_cost": 2,
                "card_type": "Instant",
                "rarity": "Common",
                "colors": ["U"],
                "text": "Counter target spell.",
                "tags": ["control", "counterspell", "permission"],
                "popularity": 0.8
            },
            {
                "name": "Llanowar Elves",
                "mana_cost": "G",
                "converted_mana_cost": 1,
                "card_type": "Creature — Elf Druid",
                "creature_type": "Elf Druid",
                "rarity": "Common",
                "colors": ["G"],
                "power": 1,
                "toughness": 1,
                "text": "T: Add G.",
                "tags": ["ramp", "elf", "mana", "aggressive"],
                "popularity": 0.7
            },
            {
                "name": "Goblin Guide",
                "mana_cost": "R",
                "converted_mana_cost": 1,
                "card_type": "Creature — Goblin Scout",
                "creature_type": "Goblin Scout",
                "rarity": "Rare",
                "colors": ["R"],
                "power": 2,
                "toughness": 2,
                "text": "Haste. Whenever Goblin Guide attacks, defending player reveals the top card of their library.",
                "tags": ["aggressive", "goblin", "haste", "burn"],
                "popularity": 0.75
            },
            {
                "name": "Path to Exile",
                "mana_cost": "W",
                "converted_mana_cost": 1,
                "card_type": "Instant",
                "rarity": "Uncommon",
                "colors": ["W"],
                "text": "Exile target creature. Its controller may search their library for a basic land card.",
                "tags": ["removal", "exile", "control"],
                "popularity": 0.85
            },
            {
                "name": "Thoughtseize",
                "mana_cost": "B",
                "converted_mana_cost": 1,
                "card_type": "Sorcery",
                "rarity": "Rare",
                "colors": ["B"],
                "text": "Target player reveals their hand. You choose a nonland card from it and exile that card.",
                "tags": ["discard", "control", "hand_attack"],
                "popularity": 0.8
            },
            {
                "name": "Monastery Swiftspear",
                "mana_cost": "R",
                "converted_mana_cost": 1,
                "card_type": "Creature — Human Monk",
                "creature_type": "Human Monk",
                "rarity": "Common",
                "colors": ["R"],
                "power": 1,
                "toughness": 2,
                "text": "Haste. Prowess",
                "tags": ["aggressive", "prowess", "spells_matter", "burn"],
                "popularity": 0.7
            }
        ]
        
        for card_data in sample_cards:
            card = Card(
                name=card_data["name"],
                mana_cost=card_data["mana_cost"],
                converted_mana_cost=card_data["converted_mana_cost"],
                card_type=card_data["card_type"],
                creature_type=card_data.get("creature_type", ""),
                rarity=card_data["rarity"],
                colors=card_data["colors"],
                power=card_data.get("power"),
                toughness=card_data.get("toughness"),
                text=card_data["text"]
            )
            
            self.cards_db[card.name] = {
                "card": card,
                "tags": card_data["tags"],
                "popularity": card_data["popularity"]
            }
    
    def load_synergy_rules(self):
        """Load synergy rules between cards"""
        self.synergy_rules = [
            SynergyRule(
                card_names=["Lightning Bolt", "Goblin Guide", "Monastery Swiftspear"],
                synergy_type="theme",
                strength=0.8,
                description="Aggressive red burn strategy"
            ),
            SynergyRule(
                card_names=["Counterspell", "Thoughtseize"],
                synergy_type="theme",
                strength=0.7,
                description="Control and disruption package"
            ),
            SynergyRule(
                card_names=["Llanowar Elves", "Lightning Bolt"],
                synergy_type="curve",
                strength=0.6,
                description="Early mana acceleration into threats"
            ),
            SynergyRule(
                card_names=["Monastery Swiftspear", "Lightning Bolt"],
                synergy_type="combo",
                strength=0.9,
                description="Prowess triggers from instant/sorcery spells"
            )
        ]
    
    def load_archetype_templates(self):
        """Load deck archetype templates"""
        self.archetype_templates = {
            "Burn/Aggro": {
                "description": "Fast aggressive strategy focusing on direct damage",
                "key_cards": ["Lightning Bolt", "Goblin Guide", "Monastery Swiftspear"],
                "mana_curve": {0: 0, 1: 12, 2: 8, 3: 4, 4: 2, 5: 0, 6: 0, 7: 0},
                "colors": ["R"],
                "tags": ["aggressive", "burn", "haste", "prowess"],
                "card_types": {"Creature": 0.4, "Instant": 0.3, "Sorcery": 0.2, "Other": 0.1}
            },
            "Control": {
                "description": "Late-game control strategy with counterspells and removal",
                "key_cards": ["Counterspell", "Path to Exile", "Thoughtseize"],
                "mana_curve": {0: 0, 1: 4, 2: 8, 3: 6, 4: 4, 5: 2, 6: 2, 7: 2},
                "colors": ["U", "W", "B"],
                "tags": ["control", "counterspell", "removal", "card_draw"],
                "card_types": {"Instant": 0.3, "Sorcery": 0.2, "Creature": 0.2, "Other": 0.3}
            },
            "Midrange": {
                "description": "Balanced strategy with efficient threats and answers",
                "key_cards": ["Llanowar Elves", "Path to Exile", "Lightning Bolt"],
                "mana_curve": {0: 0, 1: 6, 2: 8, 3: 8, 4: 6, 5: 2, 6: 0, 7: 0},
                "colors": ["G", "W", "R"],
                "tags": ["ramp", "removal", "efficient"],
                "card_types": {"Creature": 0.5, "Instant": 0.2, "Sorcery": 0.2, "Other": 0.1}
            }
        }

class CardRecommendationEngine:
    """AI-powered card recommendation engine"""
    
    def __init__(self):
        self.card_db = CardDatabase()
        self.learning_data = self.load_learning_data()
    
    def load_learning_data(self):
        """Load historical deck performance data for learning"""
        # This would typically load from match results and deck performance
        return {
            "card_win_rates": {},
            "deck_archetypes": {},
            "meta_trends": {}
        }
    
    def analyze_deck_archetype(self, deck: Deck) -> Dict[str, float]:
        """Analyze what archetype a deck most closely resembles"""
        archetype_scores = {}
        
        if not deck.cards:
            return archetype_scores
        
        # Get deck characteristics
        deck_colors = set()
        deck_tags = Counter()
        deck_curve = deck.get_mana_curve()
        deck_types = deck.get_type_distribution()
        
        for deck_card in deck.cards:
            if not deck_card.sideboard:
                deck_colors.update(deck_card.card.colors)
                # Get tags from database if available
                if deck_card.card.name in self.card_db.cards_db:
                    card_data = self.card_db.cards_db[deck_card.card.name]
                    for tag in card_data["tags"]:
                        deck_tags[tag] += deck_card.quantity
        
        # Score against each archetype
        for archetype_name, template in self.card_db.archetype_templates.items():
            score = 0.0
            factors = 0
            
            # Color similarity
            template_colors = set(template["colors"])
            if deck_colors and template_colors:
                color_overlap = len(deck_colors.intersection(template_colors))
                color_penalty = len(deck_colors.difference(template_colors)) * 0.2
                score += (color_overlap / len(template_colors)) - color_penalty
                factors += 1
            
            # Mana curve similarity
            if deck_curve:
                curve_similarity = 0
                for cmc in range(8):
                    deck_count = deck_curve.get(cmc, 0)
                    template_count = template["mana_curve"].get(cmc, 0)
                    if template_count > 0:
                        curve_similarity += min(deck_count / template_count, 1.0)
                score += curve_similarity / 8
                factors += 1
            
            # Tag similarity
            if deck_tags:
                tag_score = 0
                for tag in template["tags"]:
                    if tag in deck_tags:
                        tag_score += min(deck_tags[tag] / 10, 1.0)  # Normalize
                score += tag_score / len(template["tags"])
                factors += 1
            
            # Key card presence
            key_card_score = 0
            for key_card in template["key_cards"]:
                for deck_card in deck.cards:
                    if deck_card.card.name == key_card and not deck_card.sideboard:
                        key_card_score += deck_card.quantity / 4  # Max 4 copies
            score += key_card_score / len(template["key_cards"])
            factors += 1
            
            archetype_scores[archetype_name] = score / factors if factors > 0 else 0
        
        return archetype_scores
    
    def calculate_synergy_score(self, candidate_card: str, deck: Deck) -> float:
        """Calculate how well a card synergizes with the current deck"""
        synergy_score = 0.0
        
        deck_card_names = {dc.card.name for dc in deck.cards if not dc.sideboard}
        
        # Check direct synergy rules
        for rule in self.card_db.synergy_rules:
            if candidate_card in rule.card_names:
                overlap = len(set(rule.card_names).intersection(deck_card_names))
                if overlap > 0:
                    synergy_score += rule.strength * (overlap / len(rule.card_names))
        
        # Check tag-based synergy
        if candidate_card in self.card_db.cards_db:
            candidate_tags = set(self.card_db.cards_db[candidate_card]["tags"])
            
            for deck_card in deck.cards:
                if not deck_card.sideboard and deck_card.card.name in self.card_db.cards_db:
                    deck_card_tags = set(self.card_db.cards_db[deck_card.card.name]["tags"])
                    tag_overlap = len(candidate_tags.intersection(deck_card_tags))
                    if tag_overlap > 0:
                        synergy_score += 0.1 * tag_overlap * (deck_card.quantity / 4)
        
        return min(synergy_score, 1.0)  # Cap at 1.0
    
    def get_popularity_score(self, card_name: str, format_name: str = "Standard") -> float:
        """Get popularity score for a card in the current meta"""
        if card_name in self.card_db.cards_db:
            return self.card_db.cards_db[card_name]["popularity"]
        return 0.0
    
    def recommend_cards(self, deck: Deck, collection=None, count: int = 10, 
                       format_name: str = "Standard") -> List[CardRecommendation]:
        """Generate card recommendations for a deck"""
        recommendations = []
        
        # Analyze current deck archetype
        archetype_scores = self.analyze_deck_archetype(deck)
        primary_archetype = max(archetype_scores.items(), key=lambda x: x[1])[0] if archetype_scores else None
        
        # Get all available cards
        available_cards = list(self.card_db.cards_db.keys())
        
        # Filter by collection if provided
        if collection:
            available_cards = [name for name in available_cards if name in collection.cards]
        
        # Current deck card names for duplicate checking
        deck_card_names = {dc.card.name for dc in deck.cards}
        
        # Score each candidate card
        for card_name in available_cards:
            if card_name in deck_card_names:
                continue  # Skip cards already in deck
            
            card_data = self.card_db.cards_db[card_name]
            card = card_data["card"]
            
            # Calculate component scores
            synergy_score = self.calculate_synergy_score(card_name, deck)
            popularity_score = self.get_popularity_score(card_name, format_name)
            
            # Archetype fit score
            archetype_fit = 0.0
            if primary_archetype and primary_archetype in self.card_db.archetype_templates:
                template = self.card_db.archetype_templates[primary_archetype]
                if card_name in template["key_cards"]:
                    archetype_fit = 1.0
                else:
                    # Check tag alignment
                    candidate_tags = set(card_data["tags"])
                    template_tags = set(template["tags"])
                    archetype_fit = len(candidate_tags.intersection(template_tags)) / len(template_tags)
            
            # Overall confidence score (weighted combination)
            confidence = (
                synergy_score * 0.4 +
                popularity_score * 0.3 +
                archetype_fit * 0.3
            )
            
            # Generate reasons
            reasons = []
            if synergy_score > 0.5:
                reasons.append(f"High synergy with current deck ({synergy_score:.1%})")
            if popularity_score > 0.7:
                reasons.append(f"Popular in {format_name} meta ({popularity_score:.1%})")
            if archetype_fit > 0.6:
                reasons.append(f"Fits {primary_archetype} archetype ({archetype_fit:.1%})")
            if not reasons:
                reasons.append("General utility card")
            
            # Mana curve considerations
            deck_curve = deck.get_mana_curve()
            card_cmc = card.converted_mana_cost
            if card_cmc <= 2 and deck_curve.get(card_cmc, 0) < 8:
                reasons.append("Improves early game presence")
            elif card_cmc >= 5 and sum(deck_curve.get(i, 0) for i in range(5, 8)) < 4:
                reasons.append("Provides late game threat")
            
            recommendation = CardRecommendation(
                card=card,
                confidence=confidence,
                reasons=reasons,
                synergy_score=synergy_score,
                popularity_score=popularity_score,
                archetype_fit=archetype_fit
            )
            
            recommendations.append(recommendation)
        
        # Sort by confidence and return top recommendations
        recommendations.sort(key=lambda x: x.confidence, reverse=True)
        return recommendations[:count]
    
    def suggest_deck_improvements(self, deck: Deck) -> List[str]:
        """Suggest general improvements to a deck"""
        suggestions = []
        
        # Analyze mana curve
        curve = deck.get_mana_curve()
        total_cards = deck.get_total_cards(include_sideboard=False)
        
        if total_cards < 60:
            suggestions.append(f"Consider adding {60 - total_cards} more cards to reach minimum deck size")
        
        # Check mana curve balance
        early_game = sum(curve.get(i, 0) for i in range(0, 3))
        if early_game < total_cards * 0.3:
            suggestions.append("Consider adding more low-cost cards for early game")
        
        late_game = sum(curve.get(i, 0) for i in range(5, 8))
        if late_game > total_cards * 0.2:
            suggestions.append("Consider reducing high-cost cards to improve consistency")
        
        # Color balance
        colors = deck.get_color_distribution()
        if len(colors) > 3:
            suggestions.append("Consider focusing on fewer colors for better mana consistency")
        
        # Archetype analysis
        archetype_scores = self.analyze_deck_archetype(deck)
        if archetype_scores:
            best_archetype = max(archetype_scores.items(), key=lambda x: x[1])
            if best_archetype[1] < 0.5:
                suggestions.append("Deck seems unfocused - consider committing more to a specific strategy")
        
        return suggestions
    
    def find_similar_decks(self, deck: Deck) -> List[Dict[str, Any]]:
        """Find similar successful deck lists from the meta"""
        # This would typically query a deck database
        # For now, return example similar decks based on archetype
        archetype_scores = self.analyze_deck_archetype(deck)
        if not archetype_scores:
            return []
        
        primary_archetype = max(archetype_scores.items(), key=lambda x: x[1])[0]
        
        # Return mock similar decks
        similar_decks = []
        if primary_archetype == "Burn/Aggro":
            similar_decks = [
                {
                    "name": "Red Deck Wins",
                    "pilot": "Pro Player",
                    "event": "Championship",
                    "similarity": 0.85,
                    "key_differences": ["Includes Goblin Chainwhirler", "More burn spells"]
                }
            ]
        elif primary_archetype == "Control":
            similar_decks = [
                {
                    "name": "Azorius Control",
                    "pilot": "Another Pro",
                    "event": "GP Winner",
                    "similarity": 0.78,
                    "key_differences": ["More card draw", "Different win conditions"]
                }
            ]
        
        return similar_decks
