// Shared type definitions for Deckmaster

export interface Card {
  id: string;
  name: string;
  manaCost?: string;
  cmc?: number;
  typeLine?: string;
  oracleText?: string;
  colors?: string[];
  colorIdentity?: string[];
  power?: string;
  toughness?: string;
  rarity?: string;
  setCode?: string;
  setName?: string;
  collectorNumber?: string;
  imageUri?: string;
  scryfallId?: string;
  scryfallUri?: string;
  legalities?: { [format: string]: string };
  prices?: { [type: string]: string };
  quantity?: number;
}

export interface Deck {
  id: string;
  name: string;
  format?: string;
  mainboard: DeckCard[];
  sideboard: DeckCard[];
  created?: string;
  lastModified?: string;
}

export interface DeckCard extends Card {
  quantity: number;
}

export interface Collection {
  cards: Card[];
  lastModified: string;
}

// Global window type extension
declare global {
  interface Window {
    decksmithApp?: any;
  }
}
