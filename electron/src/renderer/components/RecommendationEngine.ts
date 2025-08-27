/**
 * AI-powered Magic: The Gathering card recommendation engine
 * Ported from Python recommendation systems for Electron/TypeScript
 */

import type { Card, Deck, DeckCard } from '../types';

export interface SmartRecommendation {
  cardName: string;
  manaCost: string;
  cardType: string;
  rarity: string;
  confidence: number;
  synergyScore: number;
  metaScore: number;
  deckFit: number;
  costConsideration: 'owned' | 'common_craft' | 'uncommon_craft' | 'rare_craft' | 'mythic_craft';
  reasons: string[];
  cmc: number;
  legality?: { [format: string]: string };
  oracleText?: string;
  powerToughness?: string;
  keywords?: string[];
}

export interface DeckAnalysis {
  strategy: string;
  colors: string[];
  primaryColors: string[];
  curve: { [cmc: number]: number };
  themes: string[];
  typeDistribution: { [type: string]: number };
  totalCards: number;
  archetype: string;
  keywords: string[];
  health: {
    curve: number;
    colorConsistency: number;
    cardBalance: number;
    manaEfficiency: number;
    overall: number;
  };
}

export class RecommendationEngine {
  private archetypePatterns: { [key: string]: any } = {
    aggro: {
      keywords: ['haste', 'double strike', 'first strike', 'trample', 'menace', 'prowess'],
      cmcRange: [1, 3],
      creatureRatioMin: 0.5,
      burnSpells: true,
      cheapRemoval: true
    },
    control: {
      keywords: ['flash', 'hexproof', 'ward', 'vigilance', 'lifelink'],
      cmcRange: [2, 6],
      creatureRatioMax: 0.3,
      counterspells: true,
      boardWipes: true,
      cardDraw: true
    },
    midrange: {
      keywords: ['flying', 'deathtouch', 'lifelink', 'vigilance', 'reach'],
      cmcRange: [2, 5],
      creatureRatio: [0.3, 0.6],
      removal: true,
      valueCreatures: true
    },
    combo: {
      keywords: ['enters', 'activated ability', 'triggered ability', 'sacrifice'],
      tutoring: true,
      protection: true,
      enablers: true
    },
    ramp: {
      keywords: ['reach', 'flying', 'trample'],
      cmcRange: [1, 8],
      manaDorks: true,
      bigThreats: true,
      landRamp: true
    }
  };

  private formatStaples: { [format: string]: any[] } = {
    standard: [
      { name: 'Lightning Bolt', manaCost: 'R', type: 'Instant', rarity: 'common', tags: ['burn', 'removal'], popularity: 95 },
      { name: 'Counterspell', manaCost: 'UU', type: 'Instant', rarity: 'common', tags: ['control', 'counter'], popularity: 90 },
      { name: 'Swords to Plowshares', manaCost: 'W', type: 'Instant', rarity: 'uncommon', tags: ['removal', 'exile'], popularity: 88 },
      { name: 'Path to Exile', manaCost: 'W', type: 'Instant', rarity: 'uncommon', tags: ['removal', 'exile'], popularity: 87 },
      { name: 'Thoughtseize', manaCost: 'B', type: 'Sorcery', rarity: 'rare', tags: ['discard', 'control'], popularity: 82 },
      { name: 'Llanowar Elves', manaCost: 'G', type: 'Creature', rarity: 'common', tags: ['ramp', 'elf', 'early'], popularity: 80 },
      { name: 'Birds of Paradise', manaCost: 'G', type: 'Creature', rarity: 'rare', tags: ['ramp', 'flying', 'fixing'], popularity: 78 },
      { name: 'Sol Ring', manaCost: '1', type: 'Artifact', rarity: 'uncommon', tags: ['ramp', 'colorless'], popularity: 98 },
      { name: 'Wrath of God', manaCost: '2WW', type: 'Sorcery', rarity: 'rare', tags: ['board_wipe', 'control'], popularity: 85 },
      { name: 'Brainstorm', manaCost: 'U', type: 'Instant', rarity: 'common', tags: ['draw', 'selection'], popularity: 92 }
    ],
    modern: [
      { name: 'Lightning Bolt', manaCost: 'R', type: 'Instant', rarity: 'common', tags: ['burn', 'removal'], popularity: 95 },
      { name: 'Fatal Push', manaCost: 'B', type: 'Instant', rarity: 'uncommon', tags: ['removal', 'efficient'], popularity: 88 },
      { name: 'Thoughtseize', manaCost: 'B', type: 'Sorcery', rarity: 'rare', tags: ['discard', 'control'], popularity: 90 },
      { name: 'Path to Exile', manaCost: 'W', type: 'Instant', rarity: 'uncommon', tags: ['removal', 'exile'], popularity: 87 },
      { name: 'Snapcaster Mage', manaCost: '1U', type: 'Creature', rarity: 'rare', tags: ['flash', 'value'], popularity: 75 }
    ]
  };

  private synergyKeywords: { [category: string]: { [theme: string]: string[] } } = {
    tribalSynergies: {
      elf: ['elvish', 'elf', 'heritage druid', 'wirewood', 'llanowar'],
      goblin: ['goblin', 'krenko', 'warren', 'lackey', 'matron'],
      vampire: ['vampire', 'bloodthirst', 'lifelink', 'madness'],
      angel: ['angel', 'flying', 'vigilance', 'lifelink'],
      dragon: ['dragon', 'flying', 'haste', 'treasure']
    },
    mechanicSynergies: {
      artifacts: ['artifact', 'metalcraft', 'affinity', 'improvise'],
      graveyard: ['graveyard', 'flashback', 'dredge', 'delve', 'escape'],
      spellsMatter: ['prowess', 'spell', 'instant', 'sorcery', 'storm'],
      sacrifice: ['sacrifice', 'dies', 'death', 'aristocrats'],
      lifegain: ['lifegain', 'lifelink', 'soul sister', 'ajani\'s pridemate']
    },
    colorSynergies: {
      white: ['lifegain', 'vigilance', 'flying', 'protection'],
      blue: ['card draw', 'counterspell', 'flying', 'scry'],
      black: ['destroy', 'discard', 'sacrifice', 'deathtouch'],
      red: ['haste', 'burn', 'damage', 'sacrifice'],
      green: ['ramp', 'big creatures', 'fight', 'reach']
    }
  };

  /**
   * Analyze a deck to determine its strategy, archetype, and needs
   */
  analyzeDeck(deck: Deck): DeckAnalysis {
    if (!deck || !deck.mainboard || deck.mainboard.length === 0) {
      return this.getEmptyAnalysis();
    }

    const mainboard = deck.mainboard;
    const totalCards = mainboard.reduce((sum, card) => sum + card.quantity, 0);

    // Analyze colors
    const colorCount: { [color: string]: number } = {};
    const colors: string[] = [];

    // Analyze mana curve
    const curve: { [cmc: number]: number } = {};

    // Analyze card types
    const typeCount: { [type: string]: number } = {};
    const themes: string[] = [];
    const keywords: string[] = [];

    for (const deckCard of mainboard) {
      // Count colors
      if (deckCard.colors) {
        deckCard.colors.forEach(color => {
          colorCount[color] = (colorCount[color] || 0) + deckCard.quantity;
          if (!colors.includes(color)) colors.push(color);
        });
      }

      // Count mana curve
      const cmc = deckCard.cmc || this.parseCMC(deckCard.manaCost || '');
      curve[cmc] = (curve[cmc] || 0) + deckCard.quantity;

      // Count types
      if (deckCard.typeLine) {
        const types = this.extractTypes(deckCard.typeLine);
        types.forEach(type => {
          typeCount[type.toLowerCase()] = (typeCount[type.toLowerCase()] || 0) + deckCard.quantity;
        });
      }

      // Extract themes and keywords
      if (deckCard.oracleText) {
        const cardKeywords = this.extractKeywords(deckCard.oracleText);
        keywords.push(...cardKeywords);
        themes.push(...this.extractThemes(deckCard.name, deckCard.oracleText, deckCard.typeLine));
      }
    }

    const primaryColors = Object.entries(colorCount)
      .sort(([,a], [,b]) => b - a)
      .slice(0, 2)
      .map(([color]) => color);

    const strategy = this.determineStrategy(curve, typeCount, themes, colorCount, totalCards);
    const archetype = this.determineArchetype(curve, typeCount, keywords, colors, totalCards);
    const health = this.calculateDeckHealth(curve, colors, typeCount, totalCards);

    return {
      strategy,
      colors,
      primaryColors,
      curve,
      themes: [...new Set(themes)],
      typeDistribution: typeCount,
      totalCards,
      archetype,
      keywords: [...new Set(keywords)],
      health
    };
  }

  /**
   * Generate smart recommendations for a deck
   */
  async generateRecommendations(
    deck: Deck, 
    collection: any = null, 
    count: number = 15, 
    formatName: string = 'standard'
  ): Promise<SmartRecommendation[]> {
    if (!deck || !deck.mainboard) {
      return [];
    }

    const deckAnalysis = this.analyzeDeck(deck);
    const recommendations: SmartRecommendation[] = [];
    const currentCards = new Set(deck.mainboard.map(card => card.name.toLowerCase()));

    // 1. Get format staples
    const stapleRecs = await this.getFormatStaplesRecommendations(
      formatName, deckAnalysis.colors, currentCards, 15
    );
    recommendations.push(...stapleRecs);

    // 2. Get archetype-specific cards
    const archetypeRecs = await this.getArchetypeRecommendations(
      deckAnalysis.archetype, deckAnalysis.colors, currentCards, formatName, 10
    );
    recommendations.push(...archetypeRecs);

    // 3. Get synergy-based recommendations
    const synergyRecs = await this.getSynergyRecommendations(
      deck, deckAnalysis, currentCards, formatName, 10
    );
    recommendations.push(...synergyRecs);

    // 4. Fill mana curve gaps
    const curveRecs = await this.getCurveRecommendations(
      deckAnalysis.curve, deckAnalysis.colors, currentCards, formatName, 8
    );
    recommendations.push(...curveRecs);

    // Remove duplicates and sort by confidence
    const uniqueRecs = this.deduplicateAndRank(recommendations);

    // Check collection availability
    if (collection) {
      this.updateCollectionStatus(uniqueRecs, collection);
    }

    return uniqueRecs.slice(0, count);
  }

  private getEmptyAnalysis(): DeckAnalysis {
    return {
      strategy: 'unknown',
      colors: [],
      primaryColors: [],
      curve: {},
      themes: [],
      typeDistribution: {},
      totalCards: 0,
      archetype: 'unknown',
      keywords: [],
      health: {
        curve: 0,
        colorConsistency: 0,
        cardBalance: 0,
        manaEfficiency: 0,
        overall: 0
      }
    };
  }

  private parseCMC(manaCost: string): number {
    if (!manaCost) return 0;
    
    let cmc = 0;
    const genericMatch = manaCost.match(/(\d+)/);
    if (genericMatch) {
      cmc += parseInt(genericMatch[1]);
    }
    
    // Count colored mana symbols
    const coloredSymbols = manaCost.match(/[WUBRG]/g) || [];
    cmc += coloredSymbols.length;
    
    return cmc;
  }

  private extractTypes(typeLine: string): string[] {
    const parts = typeLine.split('—')[0].trim().split(' ');
    return parts.filter(type => type !== '');
  }

  private extractKeywords(oracleText: string): string[] {
    const keywords: string[] = [];
    const text = oracleText.toLowerCase();
    
    const keywordList = ['haste', 'flying', 'trample', 'deathtouch', 'lifelink', 'vigilance', 
                         'first strike', 'double strike', 'flash', 'prowess', 'hexproof', 'ward'];
    
    keywordList.forEach(keyword => {
      if (text.includes(keyword)) {
        keywords.push(keyword);
      }
    });
    
    return keywords;
  }

  private extractThemes(name: string, oracleText: string, typeLine?: string): string[] {
    const themes: string[] = [];
    const text = (name + ' ' + oracleText + ' ' + (typeLine || '')).toLowerCase();
    
    // Check for common themes
    if (text.includes('elf')) themes.push('elf');
    if (text.includes('goblin')) themes.push('goblin');
    if (text.includes('vampire')) themes.push('vampire');
    if (text.includes('burn') || text.includes('damage')) themes.push('burn');
    if (text.includes('counter')) themes.push('control');
    if (text.includes('draw')) themes.push('card_draw');
    if (text.includes('ramp') || text.includes('add') && text.includes('mana')) themes.push('ramp');
    
    return themes;
  }

  private determineStrategy(
    curve: { [cmc: number]: number }, 
    types: { [type: string]: number }, 
    themes: string[], 
    colors: { [color: string]: number },
    totalCards: number
  ): string {
    if (totalCards === 0) return 'unknown';

    const lowCurvePercentage = ((curve[1] || 0) + (curve[2] || 0)) / totalCards;
    const spellPercentage = ((types['instant'] || 0) + (types['sorcery'] || 0)) / totalCards;
    const highCurvePercentage = ((curve[5] || 0) + (curve[6] || 0) + (curve[7] || 0)) / totalCards;

    if (lowCurvePercentage > 0.6 && themes.includes('burn')) {
      return 'aggro';
    }
    
    if (spellPercentage > 0.4 && themes.includes('control')) {
      return 'control';
    }
    
    if (highCurvePercentage > 0.3) {
      return 'ramp';
    }
    
    if (Object.keys(colors).length >= 3) {
      return 'multicolor';
    }
    
    return 'midrange';
  }

  private determineArchetype(
    curve: { [cmc: number]: number },
    types: { [type: string]: number },
    keywords: string[],
    colors: string[],
    totalCards: number
  ): string {
    const creatureRatio = (types['creature'] || 0) / totalCards;
    const avgCMC = Object.entries(curve).reduce((sum, [cmc, count]) => sum + (parseInt(cmc) * count), 0) / totalCards;

    if (creatureRatio > 0.6 && avgCMC < 3) {
      return 'aggro';
    }
    
    if (keywords.includes('counterspell') || keywords.includes('draw')) {
      return 'control';
    }
    
    if (avgCMC > 4 && keywords.includes('ramp')) {
      return 'ramp';
    }
    
    return 'midrange';
  }

  private calculateDeckHealth(
    curve: { [cmc: number]: number },
    colors: string[],
    types: { [type: string]: number },
    totalCards: number
  ): DeckAnalysis['health'] {
    const curveHealth = this.calculateCurveHealth(curve, totalCards);
    const colorConsistency = this.calculateColorConsistency(colors, totalCards);
    const cardBalance = this.calculateCardBalance(types, totalCards);
    const manaEfficiency = this.calculateManaEfficiency(curve, totalCards);
    
    const overall = Math.round((curveHealth + colorConsistency + cardBalance + manaEfficiency) / 4);

    return {
      curve: curveHealth,
      colorConsistency,
      cardBalance,
      manaEfficiency,
      overall
    };
  }

  private calculateCurveHealth(curve: { [cmc: number]: number }, totalCards: number): number {
    const earlyGame = ((curve[1] || 0) + (curve[2] || 0)) / totalCards;
    const midGame = ((curve[3] || 0) + (curve[4] || 0)) / totalCards;
    const lateGame = ((curve[5] || 0) + (curve[6] || 0)) / totalCards;
    
    // Ideal distribution: 30% early, 40% mid, 30% late
    const earlyScore = Math.max(0, 100 - Math.abs(earlyGame - 0.3) * 200);
    const midScore = Math.max(0, 100 - Math.abs(midGame - 0.4) * 200);
    const lateScore = Math.max(0, 100 - Math.abs(lateGame - 0.3) * 200);
    
    return Math.round((earlyScore + midScore + lateScore) / 3);
  }

  private calculateColorConsistency(colors: string[], totalCards: number): number {
    if (colors.length <= 2) return 90;
    if (colors.length === 3) return 70;
    if (colors.length === 4) return 50;
    return 30;
  }

  private calculateCardBalance(types: { [type: string]: number }, totalCards: number): number {
    const creatureRatio = (types['creature'] || 0) / totalCards;
    const spellRatio = ((types['instant'] || 0) + (types['sorcery'] || 0)) / totalCards;
    
    // Good balance: 40-60% creatures, 20-40% spells
    const creatureScore = creatureRatio >= 0.4 && creatureRatio <= 0.6 ? 100 : 
                         Math.max(0, 100 - Math.abs(creatureRatio - 0.5) * 200);
    const spellScore = spellRatio >= 0.2 && spellRatio <= 0.4 ? 100 :
                      Math.max(0, 100 - Math.abs(spellRatio - 0.3) * 200);
    
    return Math.round((creatureScore + spellScore) / 2);
  }

  private calculateManaEfficiency(curve: { [cmc: number]: number }, totalCards: number): number {
    const avgCMC = Object.entries(curve).reduce((sum, [cmc, count]) => sum + (parseInt(cmc) * count), 0) / totalCards;
    
    // Ideal average CMC is around 2.5-3.5
    if (avgCMC >= 2.5 && avgCMC <= 3.5) return 100;
    return Math.max(0, 100 - Math.abs(avgCMC - 3) * 30);
  }

  private async getFormatStaplesRecommendations(
    formatName: string,
    colors: string[],
    currentCards: Set<string>,
    limit: number
  ): Promise<SmartRecommendation[]> {
    const staples = this.formatStaples[formatName.toLowerCase()] || this.formatStaples.standard;
    const recommendations: SmartRecommendation[] = [];

    for (const staple of staples.slice(0, limit)) {
      if (currentCards.has(staple.name.toLowerCase())) continue;
      
      if (this.isColorCompatible(staple, colors)) {
        recommendations.push({
          cardName: staple.name,
          manaCost: staple.manaCost,
          cardType: staple.type,
          rarity: staple.rarity,
          confidence: staple.popularity,
          synergyScore: 60,
          metaScore: staple.popularity,
          deckFit: 70,
          costConsideration: this.getCostConsideration(staple.rarity),
          reasons: [`Format staple in ${formatName}`, `Highly played card (${staple.popularity}% popularity)`],
          cmc: this.parseCMC(staple.manaCost)
        });
      }
    }

    return recommendations;
  }

  private async getArchetypeRecommendations(
    archetype: string,
    colors: string[],
    currentCards: Set<string>,
    formatName: string,
    limit: number
  ): Promise<SmartRecommendation[]> {
    // Mock archetype-specific recommendations
    const archetypeCards: { [key: string]: any[] } = {
      aggro: [
        { name: 'Monastery Swiftspear', manaCost: 'R', type: 'Creature', rarity: 'common' },
        { name: 'Goblin Guide', manaCost: 'R', type: 'Creature', rarity: 'rare' }
      ],
      control: [
        { name: 'Supreme Verdict', manaCost: '1WWU', type: 'Sorcery', rarity: 'rare' },
        { name: 'Teferi, Hero of Dominaria', manaCost: '3WU', type: 'Planeswalker', rarity: 'mythic' }
      ],
      midrange: [
        { name: 'Tarmogoyf', manaCost: '1G', type: 'Creature', rarity: 'rare' },
        { name: 'Bloodbraid Elf', manaCost: '2RG', type: 'Creature', rarity: 'uncommon' }
      ]
    };

    const cards = archetypeCards[archetype] || [];
    const recommendations: SmartRecommendation[] = [];

    for (const card of cards.slice(0, limit)) {
      if (currentCards.has(card.name.toLowerCase())) continue;
      
      recommendations.push({
        cardName: card.name,
        manaCost: card.manaCost,
        cardType: card.type,
        rarity: card.rarity,
        confidence: 85,
        synergyScore: 90,
        metaScore: 75,
        deckFit: 95,
        costConsideration: this.getCostConsideration(card.rarity),
        reasons: [`Perfect fit for ${archetype} strategy`, 'Strong archetype synergy'],
        cmc: this.parseCMC(card.manaCost)
      });
    }

    return recommendations;
  }

  private async getSynergyRecommendations(
    deck: Deck,
    deckAnalysis: DeckAnalysis,
    currentCards: Set<string>,
    formatName: string,
    limit: number
  ): Promise<SmartRecommendation[]> {
    const recommendations: SmartRecommendation[] = [];
    
    // Mock synergy recommendations based on themes
    const synergyCards: { [theme: string]: any[] } = {
      elf: [
        { name: 'Heritage Druid', manaCost: 'G', type: 'Creature', rarity: 'uncommon' },
        { name: 'Nettle Sentinel', manaCost: 'G', type: 'Creature', rarity: 'common' }
      ],
      burn: [
        { name: 'Lava Spike', manaCost: 'R', type: 'Sorcery', rarity: 'common' },
        { name: 'Rift Bolt', manaCost: '2R', type: 'Sorcery', rarity: 'common' }
      ],
      control: [
        { name: 'Cryptic Command', manaCost: '1UUU', type: 'Instant', rarity: 'rare' },
        { name: 'Jace, the Mind Sculptor', manaCost: '2UU', type: 'Planeswalker', rarity: 'mythic' }
      ]
    };

    for (const theme of deckAnalysis.themes) {
      const cards = synergyCards[theme] || [];
      
      for (const card of cards.slice(0, 2)) {
        if (currentCards.has(card.name.toLowerCase())) continue;
        
        recommendations.push({
          cardName: card.name,
          manaCost: card.manaCost,
          cardType: card.type,
          rarity: card.rarity,
          confidence: 80,
          synergyScore: 95,
          metaScore: 65,
          deckFit: 90,
          costConsideration: this.getCostConsideration(card.rarity),
          reasons: [`Strong ${theme} synergy`, 'Excellent combo with existing cards'],
          cmc: this.parseCMC(card.manaCost)
        });
      }
    }

    return recommendations.slice(0, limit);
  }

  private async getCurveRecommendations(
    curve: { [cmc: number]: number },
    colors: string[],
    currentCards: Set<string>,
    formatName: string,
    limit: number
  ): Promise<SmartRecommendation[]> {
    const recommendations: SmartRecommendation[] = [];
    const totalCards = Object.values(curve).reduce((sum, count) => sum + count, 0);
    
    // Identify curve gaps
    const gaps: number[] = [];
    for (let cmc = 1; cmc <= 6; cmc++) {
      const percentage = (curve[cmc] || 0) / totalCards;
      if (percentage < 0.1) { // Less than 10% representation
        gaps.push(cmc);
      }
    }

    // Mock curve filler cards
    const curveFillers: { [cmc: number]: any[] } = {
      1: [
        { name: 'Champion of the Parish', manaCost: 'W', type: 'Creature', rarity: 'rare' },
        { name: 'Monastery Swiftspear', manaCost: 'R', type: 'Creature', rarity: 'common' }
      ],
      2: [
        { name: 'Tarmogoyf', manaCost: '1G', type: 'Creature', rarity: 'rare' },
        { name: 'Dark Confidant', manaCost: '1B', type: 'Creature', rarity: 'rare' }
      ],
      3: [
        { name: 'Knight of the Reliquary', manaCost: '1GW', type: 'Creature', rarity: 'rare' },
        { name: 'Geist of Saint Traft', manaCost: '1WU', type: 'Creature', rarity: 'mythic' }
      ],
      4: [
        { name: 'Bloodbraid Elf', manaCost: '2RG', type: 'Creature', rarity: 'uncommon' },
        { name: 'Restoration Angel', manaCost: '3W', type: 'Creature', rarity: 'rare' }
      ]
    };

    for (const gap of gaps.slice(0, 3)) {
      const cards = curveFillers[gap] || [];
      
      for (const card of cards.slice(0, 2)) {
        if (currentCards.has(card.name.toLowerCase())) continue;
        
        recommendations.push({
          cardName: card.name,
          manaCost: card.manaCost,
          cardType: card.type,
          rarity: card.rarity,
          confidence: 75,
          synergyScore: 60,
          metaScore: 70,
          deckFit: 85,
          costConsideration: this.getCostConsideration(card.rarity),
          reasons: [`Fills gap in mana curve at ${gap} CMC`, 'Improves deck consistency'],
          cmc: gap
        });
      }
    }

    return recommendations.slice(0, limit);
  }

  private isColorCompatible(card: any, deckColors: string[]): boolean {
    if (!card.manaCost) return true;
    
    const cardColors = this.extractColorsFromManaCost(card.manaCost);
    return cardColors.every(color => deckColors.includes(color));
  }

  private extractColorsFromManaCost(manaCost: string): string[] {
    const colors: string[] = [];
    const colorRegex = /[WUBRG]/g;
    const matches = manaCost.match(colorRegex) || [];
    
    matches.forEach(color => {
      if (!colors.includes(color)) {
        colors.push(color);
      }
    });
    
    return colors;
  }

  private getCostConsideration(rarity: string): SmartRecommendation['costConsideration'] {
    switch (rarity.toLowerCase()) {
      case 'common': return 'common_craft';
      case 'uncommon': return 'uncommon_craft';
      case 'rare': return 'rare_craft';
      case 'mythic': case 'mythic rare': return 'mythic_craft';
      default: return 'common_craft';
    }
  }

  private deduplicateAndRank(recommendations: SmartRecommendation[]): SmartRecommendation[] {
    const seen = new Set<string>();
    const unique: SmartRecommendation[] = [];

    for (const rec of recommendations) {
      const key = rec.cardName.toLowerCase();
      if (!seen.has(key)) {
        seen.add(key);
        unique.push(rec);
      }
    }

    return unique.sort((a, b) => b.confidence - a.confidence);
  }

  private updateCollectionStatus(recommendations: SmartRecommendation[], collection: any): void {
    // Mock collection checking - would integrate with actual collection data
    for (const rec of recommendations) {
      // Simulate some cards being owned
      if (Math.random() > 0.7) {
        rec.costConsideration = 'owned';
        rec.reasons.push('✓ Already in collection');
      }
    }
  }
}
