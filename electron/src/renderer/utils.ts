// Scryfall API integration for Electron renderer
import type { Card, Deck, DeckCard } from './types';

// Cache configuration
interface CachedData<T> {
  data: T;
  timestamp: number;
  cachedAt: string;
}

class CardCache {
  private static readonly CARD_CACHE_KEY = 'decksmith_card_cache';
  private static readonly PRICE_CACHE_KEY = 'decksmith_price_cache';
  
  // Cache expiration times (in milliseconds)
  private static readonly CARD_EXPIRY = 180 * 24 * 60 * 60 * 1000; // 6 months - card data rarely changes
  private static readonly PRICE_EXPIRY = 1 * 24 * 60 * 60 * 1000;  // 1 day - prices update more frequently
  
  static getCardData(cardName: string): any | null {
    const cache = this.loadCache(this.CARD_CACHE_KEY);
    const key = cardName.toLowerCase().trim();
    
    if (cache[key]) {
      const entry = cache[key] as CachedData<any>;
      if (!this.isExpired(entry.timestamp, this.CARD_EXPIRY)) {
        console.log(`Cache hit for card: ${cardName}`);
        return entry.data;
      } else {
        // Remove expired entry
        delete cache[key];
        this.saveCache(this.CARD_CACHE_KEY, cache);
      }
    }
    
    return null;
  }
  
  static cacheCardData(cardName: string, cardData: any): void {
    const cache = this.loadCache(this.CARD_CACHE_KEY);
    const key = cardName.toLowerCase().trim();
    
    cache[key] = {
      data: cardData,
      timestamp: Date.now(),
      cachedAt: new Date().toISOString()
    };
    
    this.saveCache(this.CARD_CACHE_KEY, cache);
    console.log(`Cached card data for: ${cardName}`);
  }
  
  static getPriceData(cardName: string): any | null {
    const cache = this.loadCache(this.PRICE_CACHE_KEY);
    const key = cardName.toLowerCase().trim();
    
    if (cache[key]) {
      const entry = cache[key] as CachedData<any>;
      if (!this.isExpired(entry.timestamp, this.PRICE_EXPIRY)) {
        return entry.data;
      } else {
        delete cache[key];
        this.saveCache(this.PRICE_CACHE_KEY, cache);
      }
    }
    
    return null;
  }
  
  static cachePriceData(cardName: string, priceData: any): void {
    const cache = this.loadCache(this.PRICE_CACHE_KEY);
    const key = cardName.toLowerCase().trim();
    
    cache[key] = {
      data: priceData,
      timestamp: Date.now(),
      cachedAt: new Date().toISOString()
    };
    
    this.saveCache(this.PRICE_CACHE_KEY, cache);
  }
  
  static invalidateCache(cardName?: string): void {
    if (cardName) {
      const key = cardName.toLowerCase().trim();
      const cardCache = this.loadCache(this.CARD_CACHE_KEY);
      const priceCache = this.loadCache(this.PRICE_CACHE_KEY);
      
      delete cardCache[key];
      delete priceCache[key];
      
      this.saveCache(this.CARD_CACHE_KEY, cardCache);
      this.saveCache(this.PRICE_CACHE_KEY, priceCache);
      console.log(`Invalidated cache for: ${cardName}`);
    } else {
      localStorage.removeItem(this.CARD_CACHE_KEY);
      localStorage.removeItem(this.PRICE_CACHE_KEY);
      console.log('Invalidated all card caches');
    }
  }
  
  static invalidatePriceCache(): void {
    localStorage.removeItem(this.PRICE_CACHE_KEY);
    console.log('Invalidated price cache');
  }
  
  static getCacheStats(): { cardCount: number; priceCount: number; cardExpiry: string; priceExpiry: string } {
    const cardCache = this.loadCache(this.CARD_CACHE_KEY);
    const priceCache = this.loadCache(this.PRICE_CACHE_KEY);
    
    return {
      cardCount: Object.keys(cardCache).length,
      priceCount: Object.keys(priceCache).length,
      cardExpiry: '6 months',
      priceExpiry: '1 week'
    };
  }
  
  private static loadCache(key: string): Record<string, CachedData<any>> {
    try {
      const cached = localStorage.getItem(key);
      return cached ? JSON.parse(cached) : {};
    } catch (error) {
      console.error(`Error loading cache ${key}:`, error);
      return {};
    }
  }
  
  private static saveCache(key: string, cache: Record<string, CachedData<any>>): void {
    try {
      localStorage.setItem(key, JSON.stringify(cache));
    } catch (error) {
      console.error(`Error saving cache ${key}:`, error);
    }
  }
  
  private static isExpired(timestamp: number, expiryMs: number): boolean {
    return (Date.now() - timestamp) > expiryMs;
  }
}

class ScryfallAPI {
  private static readonly BASE_URL = 'https://api.scryfall.com';
  private static readonly REQUEST_DELAY = 100; // 100ms between requests
  private static lastRequestTime = 0;

  static async searchCards(query: string, page = 1): Promise<any> {
    await this.rateLimit();
    
    const url = new URL(`${this.BASE_URL}/cards/search`);
    url.searchParams.set('q', query);
    url.searchParams.set('page', page.toString());
    
    try {
      const response = await fetch(url.toString());
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      return await response.json();
    } catch (error) {
      console.error('Scryfall API error:', error);
      throw error;
    }
  }

  static async getCardByName(name: string, forceRefresh = false): Promise<any> {
    // Check cache first unless force refresh is requested
    if (!forceRefresh) {
      const cached = CardCache.getCardData(name);
      if (cached) {
        return cached;
      }
    }
    
    await this.rateLimit();
    
    const url = new URL(`${this.BASE_URL}/cards/named`);
    url.searchParams.set('exact', name);
    
    try {
      const response = await fetch(url.toString());
      
      if (!response.ok) {
        if (response.status === 404) {
          return null; // Card not found
        }
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const data = await response.json();
      
      // Cache the card data (excluding prices)
      const cardDataWithoutPrices = { ...data };
      delete cardDataWithoutPrices.prices;
      CardCache.cacheCardData(name, cardDataWithoutPrices);
      
      // Cache prices separately with shorter expiry
      if (data.prices) {
        CardCache.cachePriceData(name, data.prices);
      }
      
      return data;
    } catch (error) {
      console.error('Scryfall API error:', error);
      throw error;
    }
  }

  static async getCardByFuzzyName(name: string, forceRefresh = false): Promise<any> {
    const cacheKey = name.trim().toLowerCase();
    
    // Check cache first unless force refresh is requested
    if (!forceRefresh) {
      const cached = CardCache.getCardData(cacheKey);
      if (cached) {
        return cached;
      }
    }
    
    await this.rateLimit();
    
    const url = new URL(`${this.BASE_URL}/cards/named`);
    url.searchParams.set('fuzzy', name);
    
    try {
      const response = await fetch(url.toString());
      
      if (!response.ok) {
        if (response.status === 404) {
          return null; // Card not found
        }
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const data = await response.json();
      
      // Cache the card data (excluding prices)
      const cardDataWithoutPrices = { ...data };
      delete cardDataWithoutPrices.prices;
      const actualName = data.name || cacheKey;
      CardCache.cacheCardData(actualName, cardDataWithoutPrices);
      
      // Also cache under search term for future fuzzy searches
      if (actualName.toLowerCase() !== cacheKey) {
        CardCache.cacheCardData(cacheKey, cardDataWithoutPrices);
      }
      
      // Cache prices separately
      if (data.prices) {
        CardCache.cachePriceData(actualName, data.prices);
      }
      
      return data;
    } catch (error) {
      console.error('Scryfall API error:', error);
      throw error;
    }
  }

  static async autocompleteCard(query: string): Promise<string[]> {
    await this.rateLimit();
    
    const url = new URL(`${this.BASE_URL}/cards/autocomplete`);
    url.searchParams.set('q', query);
    
    try {
      const response = await fetch(url.toString());
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const data = await response.json();
      return data.data || [];
    } catch (error) {
      console.error('Scryfall autocomplete error:', error);
      return [];
    }
  }

  private static async rateLimit(): Promise<void> {
    const now = Date.now();
    const timeSinceLastRequest = now - this.lastRequestTime;
    
    if (timeSinceLastRequest < this.REQUEST_DELAY) {
      await new Promise(resolve => 
        setTimeout(resolve, this.REQUEST_DELAY - timeSinceLastRequest)
      );
    }
    
    this.lastRequestTime = Date.now();
  }

  static transformScryfallCard(scryfallCard: any): Card {
    return {
      id: scryfallCard.id,
      name: scryfallCard.name,
      manaCost: scryfallCard.mana_cost || '',
      cmc: scryfallCard.cmc || 0,
      typeLine: scryfallCard.type_line || '',
      oracleText: scryfallCard.oracle_text || '',
      colors: scryfallCard.colors || [],
      colorIdentity: scryfallCard.color_identity || [],
      power: scryfallCard.power,
      toughness: scryfallCard.toughness,
      rarity: scryfallCard.rarity || '',
      setCode: scryfallCard.set || '',
      setName: scryfallCard.set_name || '',
      collectorNumber: scryfallCard.collector_number || '',
      imageUri: scryfallCard.image_uris?.normal || scryfallCard.image_uris?.large,
      scryfallId: scryfallCard.id,
      quantity: 1
    };
  }
}

// CSV handling utilities
class CSVHandler {
  static parseCollectionCSV(csvText: string): Array<{name: string, quantity: number}> {
    const lines = csvText.split('\n').map(line => line.trim()).filter(line => line);
    const cards: Array<{name: string, quantity: number}> = [];
    
    // Skip header if it exists
    const startIndex = lines[0]?.toLowerCase().includes('card') || lines[0]?.toLowerCase().includes('name') ? 1 : 0;
    
    for (let i = startIndex; i < lines.length; i++) {
      const line = lines[i];
      if (!line) continue;
      
      // Handle different CSV formats
      const parts = line.split(',').map(part => part.trim().replace(/"/g, ''));
      
      if (parts.length >= 2) {
        const name = parts[0];
        const quantity = parseInt(parts[1]) || 1;
        
        if (name && quantity > 0) {
          cards.push({ name, quantity });
        }
      } else if (parts.length === 1) {
        // Single column - assume card name with quantity 1
        const name = parts[0];
        if (name) {
          cards.push({ name, quantity: 1 });
        }
      }
    }
    
    return cards;
  }

  static parseArenaFormat(arenaText: string): Array<{name: string, quantity: number}> {
    const lines = arenaText.split('\n').map(line => line.trim()).filter(line => line);
    const cards: Array<{name: string, quantity: number}> = [];
    
    for (const line of lines) {
      if (!line || line.startsWith('//')) continue; // Skip comments
      
      // Arena format: "4 Lightning Bolt (M21) 159"
      const match = line.match(/^(\d+)\s+([^(]+?)(?:\s+\([^)]+\)\s*\d*)?$/);
      
      if (match) {
        const quantity = parseInt(match[1]) || 1;
        const name = match[2].trim();
        
        if (name && quantity > 0) {
          cards.push({ name, quantity });
        }
      }
    }
    
    return cards;
  }

  static exportCollectionToCSV(cards: Card[]): string {
    const headers = ['Card Name', 'Quantity', 'Mana Cost', 'Type', 'Rarity', 'Set'];
    const rows = cards.map(card => [
      card.name,
      (card.quantity || 1).toString(),
      card.manaCost || '',
      card.typeLine || '',
      card.rarity || '',
      card.setName || ''
    ]);
    
    const csvContent = [headers, ...rows]
      .map(row => row.map(field => `"${field.replace(/"/g, '""')}"`).join(','))
      .join('\n');
    
    return csvContent;
  }

  static exportDeckToArenaFormat(deck: Deck): string {
    const allCards = [...deck.mainboard, ...deck.sideboard];
    const mainboard = allCards.filter(card => !card.typeLine?.toLowerCase().includes('basic land'));
    const lands = allCards.filter(card => card.typeLine?.toLowerCase().includes('basic land'));
    
    let arenaFormat = `Deck\n`;
    
    // Add mainboard cards
    for (const card of mainboard) {
      arenaFormat += `${card.quantity} ${card.name}${card.setCode ? ` (${card.setCode.toUpperCase()})` : ''} ${card.collectorNumber || ''}\n`;
    }
    
    // Add lands if any
    if (lands.length > 0) {
      arenaFormat += `\n`;
      for (const card of lands) {
        arenaFormat += `${card.quantity} ${card.name}${card.setCode ? ` (${card.setCode.toUpperCase()})` : ''} ${card.collectorNumber || ''}\n`;
      }
    }
    
    // Add sideboard if any
    if (deck.sideboard.length > 0) {
      arenaFormat += `\nSideboard\n`;
      for (const card of deck.sideboard) {
        arenaFormat += `${card.quantity} ${card.name}${card.setCode ? ` (${card.setCode.toUpperCase()})` : ''} ${card.collectorNumber || ''}\n`;
      }
    }
    
    return arenaFormat;
  }
}

// Export for use in other modules
export { ScryfallAPI, CSVHandler, CardCache };
