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
  private cache: Map<string, any> = new Map();
  private cacheExpiry: Map<string, number> = new Map();
  private readonly CACHE_DURATION = 5 * 60 * 1000; // 5 minutes
  private readonly REQUEST_DELAY = 100; // 100ms between requests to avoid rate limiting

  private archetypePatterns: { [key: string]: any } = {
    aggro: {
      keywords: ['haste', 'double strike', 'first strike', 'trample', 'menace', 'prowess'],
      cmcRange: [1, 3],
      creatureRatioMin: 0.5,
      burnSpells: true,
      cheapRemoval: true,
      searchQueries: [
        'cmc<=3 t:creature (o:haste or o:trample or o:"first strike")',
        'cmc<=2 (t:instant or t:sorcery) o:damage',
        'cmc<=1 t:creature power>=2'
      ]
    },
    control: {
      keywords: ['flash', 'hexproof', 'ward', 'vigilance', 'lifelink'],
      cmcRange: [2, 6],
      creatureRatioMax: 0.3,
      counterspells: true,
      boardWipes: true,
      cardDraw: true,
      searchQueries: [
        't:instant o:counter o:spell',
        'cmc>=3 (t:sorcery or t:instant) o:destroy o:creature',
        't:instant o:draw o:card',
        'o:"enters the battlefield" o:draw'
      ]
    },
    midrange: {
      keywords: ['flying', 'deathtouch', 'lifelink', 'vigilance', 'reach'],
      cmcRange: [2, 5],
      creatureRatio: [0.3, 0.6],
      removal: true,
      valueCreatures: true,
      searchQueries: [
        'cmc>=2 cmc<=5 t:creature (o:flying or o:deathtouch or o:lifelink)',
        't:instant o:destroy o:target',
        'cmc>=3 cmc<=5 t:creature power>=3'
      ]
    },
    combo: {
      keywords: ['enters', 'activated ability', 'triggered ability', 'sacrifice'],
      tutoring: true,
      protection: true,
      enablers: true,
      searchQueries: [
        'o:"search your library"',
        'o:"enters the battlefield" o:sacrifice',
        'o:"activated ability" or o:"triggered ability"',
        't:instant o:protection'
      ]
    },
    ramp: {
      keywords: ['reach', 'flying', 'trample'],
      cmcRange: [1, 8],
      manaDorks: true,
      bigThreats: true,
      landRamp: true,
      searchQueries: [
        'cmc<=2 t:creature o:"add" o:mana',
        't:sorcery o:"search your library" o:land',
        'cmc>=6 t:creature power>=6',
        't:artifact o:"add" o:mana'
      ]
    }
  };

  /**
   * Cache management and API utilities
   */
  private getCacheKey(query: string, params?: any): string {
    return `${query}_${JSON.stringify(params || {})}`;
  }

  private isExpired(key: string): boolean {
    const expiry = this.cacheExpiry.get(key);
    return !expiry || Date.now() > expiry;
  }

  private setCache(key: string, data: any): void {
    this.cache.set(key, data);
    this.cacheExpiry.set(key, Date.now() + this.CACHE_DURATION);
  }

  private async delay(ms: number): Promise<void> {
    return new Promise(resolve => setTimeout(resolve, ms));
  }

  /**
   * Scryfall API integration methods
   */
  private async searchCards(query: string, options: {
    format?: string;
    page?: number;
    unique?: string;
    order?: string;
  } = {}): Promise<any[]> {
    const cacheKey = this.getCacheKey('search', { query, ...options });
    
    if (this.cache.has(cacheKey) && !this.isExpired(cacheKey)) {
      return this.cache.get(cacheKey);
    }

    await this.delay(this.REQUEST_DELAY);

    try {
      const params = new URLSearchParams({
        q: query,
        unique: options.unique || 'cards',
        order: options.order || 'name',
        page: (options.page || 1).toString()
      });

      if (options.format) {
        params.append('q', `${query} legal:${options.format}`);
      }

      const response = await fetch(`https://api.scryfall.com/cards/search?${params}`);
      const data = await response.json();

      if (data.object === 'error') {
        console.warn('Scryfall search error:', data.details);
        return [];
      }

      const cards = data.data || [];
      this.setCache(cacheKey, cards);
      return cards;
    } catch (error) {
      console.error('Error searching Scryfall:', error);
      return [];
    }
  }

  private async getCardByName(cardName: string): Promise<any | null> {
    const cacheKey = this.getCacheKey('named', { name: cardName });
    
    if (this.cache.has(cacheKey) && !this.isExpired(cacheKey)) {
      return this.cache.get(cacheKey);
    }

    await this.delay(this.REQUEST_DELAY);

    try {
      const response = await fetch(`https://api.scryfall.com/cards/named?exact=${encodeURIComponent(cardName)}`);
      const data = await response.json();

      if (data.object === 'error') {
        return null;
      }

      this.setCache(cacheKey, data);
      return data;
    } catch (error) {
      console.error('Error fetching card by name:', error);
      return null;
    }
  }

  private async getRandomCards(colors: string[] = [], count: number = 10): Promise<any[]> {
    const colorQuery = colors.length > 0 ? `c:${colors.join('')}` : '';
    const query = colorQuery || 't:creature OR t:instant OR t:sorcery';
    
    try {
      return await this.searchCards(query, { 
        order: 'random',
        unique: 'cards'
      });
    } catch (error) {
      console.error('Error getting random cards:', error);
      return [];
    }
  }

  private scryfallToRecommendation(scryfallCard: any, confidence: number = 75): SmartRecommendation {
    const colors = scryfallCard.colors || [];
    const cmc = scryfallCard.cmc || 0;
    
    return {
      cardName: scryfallCard.name,
      manaCost: scryfallCard.mana_cost || '',
      cardType: scryfallCard.type_line || 'Unknown',
      rarity: scryfallCard.rarity || 'common',
      confidence: confidence,
      synergyScore: this.calculateSynergyScore(scryfallCard),
      metaScore: this.calculateMetaScore(scryfallCard),
      deckFit: this.calculateDeckFit(scryfallCard),
      costConsideration: this.getCostConsideration(scryfallCard.rarity || 'common'),
      reasons: this.generateReasons(scryfallCard),
      cmc: cmc,
      legality: scryfallCard.legalities || {},
      oracleText: scryfallCard.oracle_text || '',
      powerToughness: scryfallCard.power && scryfallCard.toughness ? 
        `${scryfallCard.power}/${scryfallCard.toughness}` : '',
      keywords: this.extractKeywordsFromText(scryfallCard.oracle_text || '')
    };
  }

  private calculateSynergyScore(scryfallCard: any): number {
    // Base synergy calculation - can be enhanced based on deck analysis
    let score = 50;
    
    if (scryfallCard.oracle_text) {
      const text = scryfallCard.oracle_text.toLowerCase();
      if (text.includes('draw')) score += 10;
      if (text.includes('search')) score += 15;
      if (text.includes('enters the battlefield')) score += 12;
      if (text.includes('flying') || text.includes('trample')) score += 8;
    }
    
    return Math.min(100, score);
  }

  private calculateMetaScore(scryfallCard: any): number {
    // Approximate meta score based on card characteristics
    let score = 60;
    
    if (scryfallCard.rarity === 'mythic') score += 20;
    if (scryfallCard.rarity === 'rare') score += 15;
    if (scryfallCard.cmc <= 3) score += 10;
    if (scryfallCard.colors && scryfallCard.colors.length <= 2) score += 10;
    
    return Math.min(100, score);
  }

  private calculateDeckFit(scryfallCard: any): number {
    // Basic deck fit calculation - can be enhanced with deck analysis context
    return 70 + Math.floor(Math.random() * 30);
  }

  private generateReasons(scryfallCard: any): string[] {
    const reasons: string[] = [];
    
    if (scryfallCard.oracle_text) {
      const text = scryfallCard.oracle_text.toLowerCase();
      if (text.includes('draw')) reasons.push('Provides card advantage');
      if (text.includes('search')) reasons.push('Tutoring effect for consistency');
      if (text.includes('enters the battlefield')) reasons.push('Immediate board impact');
      if (text.includes('flying')) reasons.push('Evasive threat');
      if (text.includes('haste')) reasons.push('Immediate pressure');
    }
    
    if (scryfallCard.cmc <= 2) reasons.push('Low mana cost for early game');
    if (scryfallCard.rarity === 'mythic' || scryfallCard.rarity === 'rare') {
      reasons.push('Powerful rare effect');
    }
    
    if (reasons.length === 0) {
      reasons.push('Solid card for the format');
    }
    
    return reasons;
  }

  private extractKeywordsFromText(oracleText: string): string[] {
    const keywords: string[] = [];
    const text = oracleText.toLowerCase();
    
    const keywordList = [
      'flying', 'first strike', 'double strike', 'deathtouch', 'haste',
      'hexproof', 'indestructible', 'lifelink', 'menace', 'reach',
      'trample', 'vigilance', 'flash', 'prowess', 'ward'
    ];
    
    keywordList.forEach(keyword => {
      if (text.includes(keyword)) {
        keywords.push(keyword);
      }
    });
    
    return keywords;
  }

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
    count: number = 100, 
    formatName: string = 'standard'
  ): Promise<SmartRecommendation[]> {
    if (!deck || !deck.mainboard) {
      return [];
    }

    console.log(`🎯 Generating ${count} recommendations for deck: ${deck.name}`);
    const deckAnalysis = this.analyzeDeck(deck);
    const recommendations: SmartRecommendation[] = [];
    const currentCards = new Set(deck.mainboard.map(card => card.name.toLowerCase()));

    // Calculate how many recs to get from each source to reach target count
    const stapleCount = Math.ceil(count * 0.4); // 40% format staples
    const archetypeCount = Math.ceil(count * 0.3); // 30% archetype cards  
    const synergyCount = Math.ceil(count * 0.2); // 20% synergy cards
    const curveCount = Math.ceil(count * 0.1); // 10% curve fillers

    console.log(`📊 Recommendation distribution: ${stapleCount} staples, ${archetypeCount} archetype, ${synergyCount} synergy, ${curveCount} curve`);

    // 1. Get format staples
    const stapleRecs = await this.getFormatStaplesRecommendations(
      formatName, deckAnalysis.colors, currentCards, stapleCount
    );
    recommendations.push(...stapleRecs);

    // 2. Get archetype-specific cards
    const archetypeRecs = await this.getArchetypeRecommendations(
      deckAnalysis.archetype, deckAnalysis.colors, currentCards, formatName, archetypeCount
    );
    recommendations.push(...archetypeRecs);

    // 3. Get synergy-based recommendations
    const synergyRecs = await this.getSynergyRecommendations(
      deck, deckAnalysis, currentCards, formatName, synergyCount
    );
    recommendations.push(...synergyRecs);

    // 4. Fill mana curve gaps
    const curveRecs = await this.getCurveRecommendations(
      deckAnalysis.curve, deckAnalysis.colors, currentCards, formatName, curveCount
    );
    recommendations.push(...curveRecs);

    console.log(`🔍 Found ${recommendations.length} total recommendations before deduplication`);

    // Remove duplicates and sort by confidence
    const uniqueRecs = this.deduplicateAndRank(recommendations);

    console.log(`✨ Final result: ${uniqueRecs.length} unique recommendations after deduplication`);

    // Check collection availability
    if (collection) {
      this.updateCollectionStatus(uniqueRecs, collection);
    }

    return uniqueRecs.slice(0, count);
  }

  /**
   * Generate recommendations with progressive loading feedback
   */
  async generateRecommendationsWithProgress(
    deck: Deck,
    collection: any = null,
    count: number = 100,
    formatName: string = 'standard',
    progressCallback: (progress: { phase: string, count: number, total: number, recommendations: any[] }) => void
  ): Promise<SmartRecommendation[]> {
    if (!deck || !deck.mainboard) {
      return [];
    }

    console.log(`🎯 Generating ${count} recommendations with progress for deck: ${deck.name}`);
    const deckAnalysis = this.analyzeDeck(deck);
    const recommendations: SmartRecommendation[] = [];
    const currentCards = new Set(deck.mainboard.map(card => card.name.toLowerCase()));

    // Calculate how many recs to get from each source
    const stapleCount = Math.ceil(count * 0.4);
    const archetypeCount = Math.ceil(count * 0.3);
    const synergyCount = Math.ceil(count * 0.2);
    const curveCount = Math.ceil(count * 0.1);

    const totalExpected = stapleCount + archetypeCount + synergyCount + curveCount;

    // Phase 1: Format staples
    progressCallback({ 
      phase: '🔍 Finding popular format staples...', 
      count: 0, 
      total: totalExpected, 
      recommendations: [] 
    });

    const stapleRecs = await this.getFormatStaplesRecommendations(
      formatName, deckAnalysis.colors, currentCards, stapleCount
    );
    recommendations.push(...stapleRecs);
    
    progressCallback({ 
      phase: '🎯 Searching archetype-specific cards...', 
      count: recommendations.length, 
      total: totalExpected, 
      recommendations: [...recommendations] 
    });

    // Phase 2: Archetype cards
    const archetypeRecs = await this.getArchetypeRecommendations(
      deckAnalysis.archetype, deckAnalysis.colors, currentCards, formatName, archetypeCount
    );
    recommendations.push(...archetypeRecs);

    progressCallback({ 
      phase: '🧩 Finding synergy cards...', 
      count: recommendations.length, 
      total: totalExpected, 
      recommendations: [...recommendations] 
    });

    // Phase 3: Synergy cards
    const synergyRecs = await this.getSynergyRecommendations(
      deck, deckAnalysis, currentCards, formatName, synergyCount
    );
    recommendations.push(...synergyRecs);

    progressCallback({ 
      phase: '📊 Filling mana curve gaps...', 
      count: recommendations.length, 
      total: totalExpected, 
      recommendations: [...recommendations] 
    });

    // Phase 4: Curve fillers
    const curveRecs = await this.getCurveRecommendations(
      deckAnalysis.curve, deckAnalysis.colors, currentCards, formatName, curveCount
    );
    recommendations.push(...curveRecs);

    progressCallback({ 
      phase: '✨ Finalizing recommendations...', 
      count: recommendations.length, 
      total: totalExpected, 
      recommendations: [...recommendations] 
    });

    console.log(`🔍 Found ${recommendations.length} total recommendations before deduplication`);

    // Remove duplicates and sort by confidence
    const uniqueRecs = this.deduplicateAndRank(recommendations);

    console.log(`✨ Final result: ${uniqueRecs.length} unique recommendations after deduplication`);

    // Check collection availability
    if (collection) {
      this.updateCollectionStatus(uniqueRecs, collection);
    }

    const finalRecs = uniqueRecs.slice(0, count);
    
    progressCallback({ 
      phase: `✅ Complete! Found ${finalRecs.length} recommendations`, 
      count: finalRecs.length, 
      total: finalRecs.length, 
      recommendations: finalRecs 
    });

    return finalRecs;
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
    const recommendations: SmartRecommendation[] = [];
    
    try {
      // Search for popular format staples based on colors
      const colorQuery = colors.length > 0 ? `c:${colors.join('')}` : '';
      const popularQuery = `${colorQuery} is:popular`;
      
      console.log(`🔍 Searching for ${limit} format staples: ${popularQuery} legal:${formatName}`);
      
      // Get more cards than requested to account for duplicates and filtering
      const searchLimit = Math.min(limit * 2, 175); // Scryfall max per page is 175
      
      const stapleCards = await this.searchCards(popularQuery, {
        format: formatName,
        order: 'usd',
        unique: 'cards'
      });

      console.log(`📦 Scryfall returned ${stapleCards.length} staple cards`);

      for (const card of stapleCards.slice(0, searchLimit)) {
        if (currentCards.has(card.name.toLowerCase())) continue;
        if (recommendations.length >= limit) break;
        
        const recommendation = this.scryfallToRecommendation(card, 85);
        recommendation.reasons = [
          `Popular ${formatName} staple`,
          'High play rate in competitive decks',
          ...recommendation.reasons.slice(0, 2)
        ];
        recommendation.metaScore = 90;
        
        recommendations.push(recommendation);
      }
      
      console.log(`✅ Found ${recommendations.length} format staple recommendations`);
    } catch (error) {
      console.error('❌ Error getting format staples:', error);
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
    const recommendations: SmartRecommendation[] = [];
    
    try {
      const archetypePatterns = this.archetypePatterns[archetype];
      if (!archetypePatterns || !archetypePatterns.searchQueries) {
        console.log(`⚠️ No patterns found for archetype: ${archetype}`);
        return recommendations;
      }

      const colorQuery = colors.length > 0 ? `c:${colors.join('')}` : '';
      const cardsPerQuery = Math.ceil(limit / archetypePatterns.searchQueries.length);
      
      console.log(`🎯 Searching for ${limit} ${archetype} cards across ${archetypePatterns.searchQueries.length} queries`);
      
      for (const searchQuery of archetypePatterns.searchQueries) {
        if (recommendations.length >= limit) break;
        
        const fullQuery = colorQuery ? `${colorQuery} ${searchQuery}` : searchQuery;
        
        console.log(`🔍 ${archetype} query: ${fullQuery}`);
        
        const archetypeCards = await this.searchCards(fullQuery, {
          format: formatName,
          order: 'cmc',
          unique: 'cards'
        });

        console.log(`📦 Query returned ${archetypeCards.length} ${archetype} cards`);

        for (const card of archetypeCards.slice(0, cardsPerQuery * 2)) { // Get extra to filter
          if (currentCards.has(card.name.toLowerCase())) continue;
          if (recommendations.length >= limit) break;
          
          const recommendation = this.scryfallToRecommendation(card, 80);
          recommendation.reasons = [
            `Perfect fit for ${archetype} strategy`,
            `Matches your deck's archetype pattern`,
            ...recommendation.reasons.slice(0, 2)
          ];
          recommendation.deckFit = 95;
          
          recommendations.push(recommendation);
        }
      }
      
      console.log(`✅ Found ${recommendations.length} archetype recommendations`);
    } catch (error) {
      console.error('❌ Error getting archetype recommendations:', error);
    }

    return recommendations.slice(0, limit);
  }

  private async getSynergyRecommendations(
    deck: Deck,
    deckAnalysis: DeckAnalysis,
    currentCards: Set<string>,
    formatName: string,
    limit: number
  ): Promise<SmartRecommendation[]> {
    const recommendations: SmartRecommendation[] = [];
    
    try {
      // Get synergy recommendations based on deck themes
      const colorQuery = deckAnalysis.colors.length > 0 ? 
        `c:${deckAnalysis.colors.join('')}` : '';
      
      const themes = deckAnalysis.themes.slice(0, 4); // Use more themes
      const cardsPerTheme = Math.ceil(limit / Math.max(themes.length, 1));
      
      console.log(`🧩 Searching for ${limit} synergy cards across themes: ${themes.join(', ')}`);
      
      for (const theme of themes) {
        if (recommendations.length >= limit) break;
        
        let themeQuery = '';
        
        switch (theme) {
          case 'elf':
            themeQuery = 't:elf OR o:elf';
            break;
          case 'goblin':
            themeQuery = 't:goblin OR o:goblin';
            break;
          case 'vampire':
            themeQuery = 't:vampire OR o:vampire OR o:lifelink';
            break;
          case 'burn':
            themeQuery = 'o:damage o:target';
            break;
          case 'control':
            themeQuery = 'o:counter o:spell OR o:destroy o:target';
            break;
          case 'card_draw':
            themeQuery = 'o:draw o:card';
            break;
          case 'ramp':
            themeQuery = 'o:"add" o:mana OR o:"search your library" o:land';
            break;
          default:
            continue;
        }
        
        const fullQuery = colorQuery ? `${colorQuery} ${themeQuery}` : themeQuery;
        console.log(`🔍 ${theme} synergy: ${fullQuery}`);
        
        const synergyCards = await this.searchCards(fullQuery, {
          format: formatName,
          order: 'name',
          unique: 'cards'
        });

        console.log(`📦 ${theme} returned ${synergyCards.length} synergy cards`);

        for (const card of synergyCards.slice(0, cardsPerTheme * 2)) { // Get extra to filter
          if (currentCards.has(card.name.toLowerCase())) continue;
          if (recommendations.length >= limit) break;
          
          const recommendation = this.scryfallToRecommendation(card, 75);
          recommendation.reasons = [
            `Strong ${theme} synergy`,
            `Enhances your deck's theme`,
            ...recommendation.reasons.slice(0, 2)
          ];
          recommendation.synergyScore = 90;
          
          recommendations.push(recommendation);
        }
      }
      
      console.log(`✅ Found ${recommendations.length} synergy recommendations`);
    } catch (error) {
      console.error('❌ Error getting synergy recommendations:', error);
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
    
    try {
      const totalCards = Object.values(curve).reduce((sum, count) => sum + count, 0);
      const colorQuery = colors.length > 0 ? `c:${colors.join('')}` : '';
      
      // Find mana curve gaps
      const curveGaps: number[] = [];
      for (let cmc = 1; cmc <= 5; cmc++) { // Extended range to 5
        const percentage = (curve[cmc] || 0) / totalCards;
        if (percentage < 0.15) { // Less than 15% at this CMC
          curveGaps.push(cmc);
        }
      }
      
      if (curveGaps.length === 0) {
        console.log('📈 No significant curve gaps found');
        return recommendations;
      }
      
      const cardsPerGap = Math.ceil(limit / curveGaps.length);
      console.log(`📊 Found curve gaps at CMC: ${curveGaps.join(', ')}, getting ${cardsPerGap} cards each`);
      
      for (const gapCmc of curveGaps) {
        if (recommendations.length >= limit) break;
        
        const cmcQuery = `cmc:${gapCmc}`;
        const fullQuery = colorQuery ? `${colorQuery} ${cmcQuery}` : cmcQuery;
        
        console.log(`🔍 Curve filler at CMC ${gapCmc}: ${fullQuery}`);
        
        const curveCards = await this.searchCards(fullQuery, {
          format: formatName,
          order: 'name',
          unique: 'cards'
        });

        console.log(`📦 CMC ${gapCmc} returned ${curveCards.length} curve cards`);

        for (const card of curveCards.slice(0, cardsPerGap * 2)) { // Get extra to filter
          if (currentCards.has(card.name.toLowerCase())) continue;
          if (recommendations.length >= limit) break;
          
          const recommendation = this.scryfallToRecommendation(card, 70);
          recommendation.reasons = [
            `Fills mana curve gap at ${gapCmc} CMC`,
            `Improves deck's tempo consistency`,
            ...recommendation.reasons.slice(0, 1)
          ];
          recommendation.deckFit = 85;
          
          recommendations.push(recommendation);
        }
      }
      
      console.log(`✅ Found ${recommendations.length} curve recommendations`);
    } catch (error) {
      console.error('❌ Error getting curve recommendations:', error);
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

    // Sort by: 1) Owned cards first, 2) Confidence descending, 3) Synergy score descending
    return unique.sort((a, b) => {
      // Prioritize owned cards
      if (a.costConsideration === 'owned' && b.costConsideration !== 'owned') return -1;
      if (b.costConsideration === 'owned' && a.costConsideration !== 'owned') return 1;
      
      // Then by confidence
      if (Math.abs(a.confidence - b.confidence) > 0.1) {
        return b.confidence - a.confidence;
      }
      
      // Finally by synergy score
      return b.synergyScore - a.synergyScore;
    });
  }

  private updateCollectionStatus(recommendations: SmartRecommendation[], collection: any): void {
    if (!collection || !collection.cards) {
      console.log('⚠️ No collection data available for ownership checking');
      return;
    }

    // Create a map of collection cards for fast lookup
    const collectionMap = new Map<string, number>();
    for (const card of collection.cards) {
      const cardName = card.name.toLowerCase();
      collectionMap.set(cardName, (card.quantity || 1));
    }

    console.log(`🔍 Checking ${recommendations.length} recommendations against ${collectionMap.size} collection cards`);
    
    let ownedCount = 0;
    for (const rec of recommendations) {
      const cardName = rec.cardName.toLowerCase();
      if (collectionMap.has(cardName)) {
        const quantity = collectionMap.get(cardName)!;
        rec.costConsideration = 'owned';
        rec.reasons.unshift(`✅ Already in collection (${quantity}x)`); // Add to front
        ownedCount++;
      }
    }
    
    console.log(`✅ Found ${ownedCount} owned cards in recommendations`);
  }
}
