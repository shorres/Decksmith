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
  
  static getCacheStats(): { cardCount: number; priceCount: number; cardExpiry: string; priceExpiry: string } {
    const cardCache = this.loadCache(this.CARD_CACHE_KEY);
    const priceCache = this.loadCache(this.PRICE_CACHE_KEY);
    
    return {
      cardCount: Object.keys(cardCache).length,
      priceCount: Object.keys(priceCache).length,
      cardExpiry: '6 months',
      priceExpiry: '1 day'
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

  // Fetches a card by exact name (cached) and converts it to our Card shape.
  // With withPrices, re-fetches when the cached card data no longer has fresh prices.
  static async getCard(name: string, withPrices = false): Promise<Card | null> {
    let data = await this.getCardByName(name);
    if (!data) return null;

    if (withPrices && !data.prices) {
      const cachedPrices = CardCache.getPriceData(name);
      if (cachedPrices) {
        data = { ...data, prices: cachedPrices };
      } else {
        data = await this.getCardByName(name, true);
        if (!data) return null;
      }
    }

    return this.transformScryfallCard(data);
  }

  static transformScryfallCard(scryfallCard: any): Card {
    const imageUris = scryfallCard.image_uris || scryfallCard.card_faces?.[0]?.image_uris;
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
      imageUri: imageUris?.normal || imageUris?.large,
      scryfallId: scryfallCard.id,
      scryfallUri: scryfallCard.scryfall_uri || '',
      legalities: scryfallCard.legalities || {},
      prices: scryfallCard.prices || {},
      quantity: 1
    };
  }
}

// A card row read from an import file: name and quantity plus whatever other columns were present
export type ParsedCard = Partial<Card> & { name: string; quantity: number };

// CSV and deck-list handling utilities
class CSVHandler {
  // Splits one CSV line into fields, honouring double quotes and "" escapes
  static parseCSVLine(line: string): string[] {
    const fields: string[] = [];
    let field = '';
    let inQuotes = false;

    for (let i = 0; i < line.length; i++) {
      const ch = line[i];
      if (inQuotes) {
        if (ch === '"') {
          if (line[i + 1] === '"') {
            field += '"';
            i++;
          } else {
            inQuotes = false;
          }
        } else {
          field += ch;
        }
      } else if (ch === '"') {
        inQuotes = true;
      } else if (ch === ',') {
        fields.push(field);
        field = '';
      } else {
        field += ch;
      }
    }

    fields.push(field);
    return fields;
  }

  // Reads a collection CSV. Uses the header row to find columns when present,
  // otherwise assumes "name,quantity".
  static parseCollectionCSV(csvText: string): ParsedCard[] {
    const rows = csvText.split(/\r?\n/).filter(line => line.trim()).map(line => this.parseCSVLine(line));
    if (rows.length === 0) return [];

    const header = rows[0].map(h => h.trim().toLowerCase());
    const column = (...names: string[]) => header.findIndex(h => names.includes(h));

    const headerNameCol = column('card name', 'name', 'card');
    const hasHeader = headerNameCol !== -1;
    const nameCol = hasHeader ? headerNameCol : 0;
    const qtyCol = hasHeader ? column('quantity', 'qty', 'count') : 1;
    const manaCol = hasHeader ? column('mana cost', 'mana_cost') : -1;
    const typeCol = hasHeader ? column('type', 'type line', 'type_line') : -1;
    const rarityCol = hasHeader ? column('rarity') : -1;
    const setCol = hasHeader ? column('set', 'set name', 'edition') : -1;

    const cell = (row: string[], index: number) => (index >= 0 ? (row[index] ?? '').trim() : '');

    const cards: ParsedCard[] = [];
    for (const row of rows.slice(hasHeader ? 1 : 0)) {
      const name = cell(row, nameCol);
      const quantity = parseInt(cell(row, qtyCol)) || 1;
      if (!name || quantity <= 0) continue;

      cards.push({
        name,
        quantity,
        manaCost: cell(row, manaCol) || undefined,
        typeLine: cell(row, typeCol) || undefined,
        rarity: cell(row, rarityCol).toLowerCase() || undefined,
        setName: cell(row, setCol) || undefined
      });
    }

    return cards;
  }

  // Reads a deck list: "4 Lightning Bolt", "4x Lightning Bolt", "4 Lightning Bolt (M21) 159" or
  // just "Lightning Bolt". "Sideboard" headers (or "SB:" prefixes) mark sideboard cards.
  static parseArenaFormat(text: string): Array<ParsedCard & { sideboard: boolean }> {
    const cards: Array<ParsedCard & { sideboard: boolean }> = [];
    let inSideboard = false;

    for (const rawLine of text.split(/\r?\n/)) {
      let line = rawLine.trim();
      if (!line || line.startsWith('//')) continue;

      const heading = line.toLowerCase().replace(/:$/, '');
      if (heading === 'sideboard') {
        inSideboard = true;
        continue;
      }
      if (['deck', 'main', 'mainboard', 'commander', 'companion'].includes(heading)) {
        inSideboard = false;
        continue;
      }

      let sideboard = inSideboard;
      if (/^SB:\s*/i.test(line)) {
        sideboard = true;
        line = line.replace(/^SB:\s*/i, '');
      }

      const match = line.match(/^(?:(\d+)x?\s+)?(.+?)(?:\s+\(([A-Za-z0-9]+)\)(?:\s+\S+)?)?$/);
      if (!match) continue;

      const quantity = match[1] ? parseInt(match[1]) : 1;
      const name = match[2].trim();
      if (name && quantity > 0) {
        cards.push({ name, quantity, sideboard, setCode: match[3]?.toLowerCase() });
      }
    }

    return cards;
  }

  private static toCSV(rows: string[][]): string {
    return rows
      .map(row => row.map(field => `"${field.replace(/"/g, '""')}"`).join(','))
      .join('\n');
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

    return this.toCSV([headers, ...rows]);
  }

  static exportDeckToCSV(deck: Deck): string {
    const headers = ['Quantity', 'Name', 'Type', 'Section'];
    const rows = [
      ...deck.mainboard.map(card => [card.quantity.toString(), card.name, card.typeLine || '', 'Mainboard']),
      ...deck.sideboard.map(card => [card.quantity.toString(), card.name, card.typeLine || '', 'Sideboard'])
    ];

    return this.toCSV([headers, ...rows]);
  }

  static exportDeckToArenaFormat(deck: Deck): string {
    const formatLine = (card: DeckCard) =>
      `${card.quantity} ${card.name}` +
      (card.setCode ? ` (${card.setCode.toUpperCase()})${card.collectorNumber ? ` ${card.collectorNumber}` : ''}` : '');

    let arenaFormat = `Deck\n${deck.mainboard.map(formatLine).join('\n')}\n`;

    if (deck.sideboard.length > 0) {
      arenaFormat += `\nSideboard\n${deck.sideboard.map(formatLine).join('\n')}\n`;
    }

    return arenaFormat;
  }
}

// Export for use in other modules
export { ScryfallAPI, CSVHandler, CardCache };
