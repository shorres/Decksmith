// Scryfall API integration for Electron renderer
import type { Card, Deck, DeckCard } from './types';

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

  static async getCardByName(name: string): Promise<any> {
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
      
      return await response.json();
    } catch (error) {
      console.error('Scryfall API error:', error);
      throw error;
    }
  }

  static async getCardByFuzzyName(name: string): Promise<any> {
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
      
      return await response.json();
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
    const mainboard = deck.cards.filter(card => !card.typeLine?.toLowerCase().includes('basic land'));
    const lands = deck.cards.filter(card => card.typeLine?.toLowerCase().includes('basic land'));
    
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
    
    return arenaFormat;
  }
}

// Export for use in other modules
export { ScryfallAPI, CSVHandler };
