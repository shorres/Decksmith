import { BaseComponent } from './BaseComponent';
import { CardDetailsModal } from './CardDetailsModal';
import type { Deck, DeckCard, Card, Collection } from '../types';

export class DecksTab extends BaseComponent {
  private decks: Deck[] = [];
  private selectedDeck: Deck | null = null;
  private collection: Collection = { cards: [], lastModified: new Date().toISOString() };
  private cardModal: CardDetailsModal;

  constructor() {
    super('#decks-tab');
    this.cardModal = new CardDetailsModal();
  }

  initialize(): void {
    if (this.isInitialized) return;
    
    this.render();
    this.setupEventListeners();
    this.loadDecks();
    this.isInitialized = true;
  }

  render(): void {
    this.element.innerHTML = `
      <div class="decks-layout">
        <!-- Deck List Sidebar -->
        <div class="deck-sidebar">
          <div class="sidebar-header">
            <h3>Decks</h3>
            <button id="new-deck-btn" class="btn btn-primary" onclick="window.decksmithApp?.components?.decks?.createNewDeck?.();">+ New</button>
          </div>
          
          <div class="deck-list" id="deck-list">
            <div class="loading-state">
              <div class="spinner"></div>
              <p>Loading decks...</p>
            </div>
          </div>
          
          <div class="deck-info-panel" id="deck-info">
            <h4>Deck Information</h4>
            <div class="deck-name-input">
              <label for="deck-name">Name:</label>
              <input type="text" id="deck-name" placeholder="Deck Name" />
            </div>
            <div class="deck-format-input">
              <label for="deck-format">Format:</label>
              <select id="deck-format">
                <option value="Standard">Standard</option>
                <option value="Modern">Modern</option>
                <option value="Legacy">Legacy</option>
                <option value="Commander">Commander</option>
                <option value="Pioneer">Pioneer</option>
                <option value="Historic">Historic</option>
                <option value="Explorer">Explorer</option>
                <option value="Alchemy">Alchemy</option>
                <option value="Brawl">Brawl</option>
              </select>
            </div>
            <div class="deck-stats">
              <div class="stat-row">
                <span>Total Cards:</span>
                <span id="deck-total-cards">0</span>
              </div>
              <div class="stat-row">
                <span>Mainboard:</span>
                <span id="deck-mainboard-cards">0</span>
              </div>
              <div class="stat-row">
                <span>Sideboard:</span>
                <span id="deck-sideboard-cards">0</span>
              </div>
            </div>
            <div class="deck-actions">
              <button id="copy-deck-btn" class="btn btn-secondary btn-full" onclick="window.decksmithApp?.components?.decks?.copyDeck?.();">Copy Deck</button>
              <button id="delete-deck-btn" class="btn btn-secondary btn-full" onclick="window.decksmithApp?.components?.decks?.deleteDeck?.();">Delete Deck</button>
              <button id="clear-selection-btn" class="btn btn-secondary btn-full" onclick="window.decksmithApp?.components?.decks?.clearDeckSelection?.();">Clear Selection</button>
              <button id="import-deck-btn" class="btn btn-secondary btn-full" onclick="window.decksmithApp?.components?.decks?.importDeck?.();">Import CSV</button>
              <button id="import-clipboard-btn" class="btn btn-secondary btn-full" onclick="window.decksmithApp?.components?.decks?.importFromClipboard?.();">Import Clipboard</button>
              <button id="export-deck-btn" class="btn btn-secondary btn-full" onclick="window.decksmithApp?.components?.decks?.exportDeck?.();">Export CSV</button>
              <button id="copy-to-clipboard-btn" class="btn btn-secondary btn-full" onclick="window.decksmithApp?.components?.decks?.copyToClipboard?.();">Copy to Clipboard</button>
            </div>
          </div>
        </div>

        <!-- Deck Editor -->
        <div class="deck-main">
          <div class="deck-tabs">
            <button class="deck-tab-btn active" data-section="mainboard">
              Mainboard (<span id="mainboard-count">0</span>)
            </button>
            <button class="deck-tab-btn" data-section="sideboard">
              Sideboard (<span id="sideboard-count">0</span>)
            </button>
          </div>

          <div class="deck-content">
            <div id="deck-mainboard" class="deck-section active">
              <div class="deck-header">
                <div class="add-card-section">
                  <input type="text" id="add-card-input" placeholder="Add card..." autocomplete="off" />
                  <input type="number" id="add-card-qty" value="1" min="1" max="4" />
                  <button id="add-card-mainboard" class="btn btn-primary" onclick="window.decksmithApp?.components?.decks?.addCardToMainboard?.();">Add</button>
                </div>
              </div>
              <div class="deck-cards" id="mainboard-cards">
                <div class="empty-state">
                  <p>Select or create a deck to start building</p>
                </div>
              </div>
            </div>

            <div id="deck-sideboard" class="deck-section">
              <div class="deck-header">
                <div class="add-card-section">
                  <input type="text" id="add-card-input-sb" placeholder="Add card to sideboard..." autocomplete="off" />
                  <input type="number" id="add-card-qty-sb" value="1" min="1" max="4" />
                  <button id="add-card-sideboard" class="btn btn-primary" onclick="window.decksmithApp?.components?.decks?.addCardToSideboard?.();">Add</button>
                </div>
              </div>
              <div class="deck-cards" id="sideboard-cards">
                <div class="empty-state">
                  <p>No sideboard cards</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    `;
  }

  private setupEventListeners(): void {
    console.log('Setting up DecksTab event listeners...');

    // Tab switching
    this.element.querySelectorAll('.deck-tab-btn').forEach(btn => {
      btn.addEventListener('click', (e) => {
        const target = e.target as HTMLElement;
        const section = target.dataset.section;
        if (section) {
          this.switchSection(section);
        }
      });
    });

    // Deck name and format inputs
    this.bindEvent('#deck-name', 'input', () => this.updateDeckName());
    this.bindEvent('#deck-format', 'change', () => this.updateDeckFormat());
  }

  // Public methods for global access
  setCollection(collection: Collection): void {
    this.collection = collection;
  }

  setDecks(decks: Deck[]): void {
    this.decks = decks;
    this.renderDeckList();
  }

  getAllDecks(): Deck[] {
    return [...this.decks];
  }

  getCurrentDeck(): Deck | null {
    return this.selectedDeck;
  }

  createNewDeck(): void {
    const newDeck: Deck = {
      id: 'deck-' + Date.now(),
      name: 'New Deck',
      format: 'Standard',
      mainboard: [],
      sideboard: [],
      lastModified: new Date().toISOString()
    };

    this.decks.push(newDeck);
    this.renderDeckList();
    this.selectDeck(newDeck);
    this.saveDecks();
  }

  copyDeck(): void {
    if (!this.selectedDeck) return;

    const copiedDeck: Deck = {
      ...this.selectedDeck,
      id: 'deck-' + Date.now(),
      name: this.selectedDeck.name + ' Copy',
      mainboard: [...this.selectedDeck.mainboard],
      sideboard: [...this.selectedDeck.sideboard],
      lastModified: new Date().toISOString()
    };

    this.decks.push(copiedDeck);
    this.renderDeckList();
    this.selectDeck(copiedDeck);
    this.saveDecks();
  }

  deleteDeck(): void {
    if (!this.selectedDeck) return;

    const confirmed = confirm(`Delete deck "${this.selectedDeck.name}"?`);
    if (!confirmed) return;

    const index = this.decks.indexOf(this.selectedDeck);
    if (index > -1) {
      this.decks.splice(index, 1);
      this.selectedDeck = null;
      
      this.renderDeckList();
      
      if (this.decks.length > 0) {
        this.selectDeck(this.decks[0]);
      } else {
        this.clearDeckEditor();
      }
      
      this.saveDecks();
    }
  }

  selectDeckById(deckId: string): void {
    const deck = this.decks.find(d => d.id === deckId);
    if (deck) {
      this.selectDeck(deck);
    }
  }

  async addCardToMainboard(): Promise<void> {
    const input = this.element.querySelector('#add-card-input') as HTMLInputElement;
    const qtyInput = this.element.querySelector('#add-card-qty') as HTMLInputElement;
    
    if (!input || !qtyInput || !this.selectedDeck) return;
    
    const cardName = input.value.trim();
    const quantity = parseInt(qtyInput.value) || 1;
    
    if (!cardName) return;
    
    await this.addCardToDeck(cardName, quantity, false);
    input.value = '';
    qtyInput.value = '1';
  }

  async addCardToSideboard(): Promise<void> {
    const input = this.element.querySelector('#add-card-input-sb') as HTMLInputElement;
    const qtyInput = this.element.querySelector('#add-card-qty-sb') as HTMLInputElement;
    
    if (!input || !qtyInput || !this.selectedDeck) return;
    
    const cardName = input.value.trim();
    const quantity = parseInt(qtyInput.value) || 1;
    
    if (!cardName) return;
    
    await this.addCardToDeck(cardName, quantity, true);
    input.value = '';
    qtyInput.value = '1';
  }

  adjustCardQuantity(cardName: string, isSideboard: boolean, change: number): void {
    if (!this.selectedDeck) return;
    
    const section = isSideboard ? this.selectedDeck.sideboard : this.selectedDeck.mainboard;
    const cardIndex = section.findIndex(card => card.name === cardName);
    
    if (cardIndex === -1) return;
    
    const newQuantity = section[cardIndex].quantity + change;
    
    if (newQuantity <= 0) {
      section.splice(cardIndex, 1);
    } else {
      section[cardIndex].quantity = newQuantity;
    }
    
    this.selectedDeck.lastModified = new Date().toISOString();
    this.renderDeckEditor();
    this.saveDecks();
  }

  removeCard(cardName: string, isSideboard: boolean): void {
    if (!this.selectedDeck) return;
    
    const confirmed = confirm(`Remove all copies of "${cardName}"?`);
    if (!confirmed) return;
    
    const section = isSideboard ? this.selectedDeck.sideboard : this.selectedDeck.mainboard;
    const cardIndex = section.findIndex(card => card.name === cardName);
    
    if (cardIndex > -1) {
      section.splice(cardIndex, 1);
      this.selectedDeck.lastModified = new Date().toISOString();
      this.renderDeckEditor();
      this.saveDecks();
    }
  }

  showCardDetails(cardName: string): void {
    this.cardModal.show(cardName);
  }

  clearDeckSelection(): void {
    this.selectedDeck = null;
    this.renderDeckList();
    this.clearDeckEditor();
  }

  importDeck(): void {
    this.showImportDialog();
  }

  importFromClipboard(): void {
    this.showImportDialog(true);
  }

  exportDeck(): void {
    if (!this.selectedDeck) return;
    
    const csvContent = this.generateDeckCSV(this.selectedDeck);
    const blob = new Blob([csvContent], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    
    const a = document.createElement('a');
    a.href = url;
    a.download = `${this.selectedDeck.name || 'deck'}.csv`;
    a.click();
    
    URL.revokeObjectURL(url);
  }

  copyToClipboard(): void {
    if (!this.selectedDeck) return;
    
    const deckText = this.generateDeckText(this.selectedDeck);
    navigator.clipboard.writeText(deckText).then(() => {
      console.log('Deck copied to clipboard');
    }).catch(err => {
      console.error('Failed to copy deck to clipboard:', err);
    });
  }

  private async loadDecks(): Promise<void> {
    try {
      console.log('Loading decks data...');
      const savedDecks = await window.electronAPI?.store.get('decks');
      
      if (savedDecks && Array.isArray(savedDecks)) {
        console.log(`Loaded ${savedDecks.length} decks from storage`);
        this.decks = savedDecks;
      } else {
        console.log('No existing decks found, creating sample deck');
        this.decks = [this.createSampleDeck()];
        await this.saveDecks();
      }
      
      this.renderDeckList();
      
      if (this.decks.length > 0) {
        this.selectDeck(this.decks[0]);
      }
      
    } catch (error) {
      console.error('Error loading decks:', error);
      this.decks = [];
      this.renderDeckList();
    }
  }

  private async saveDecks(): Promise<void> {
    try {
      await window.electronAPI?.store.set('decks', this.decks);
      console.log('Decks saved successfully');
    } catch (error) {
      console.error('Error saving decks:', error);
    }
  }

  private createSampleDeck(): Deck {
    return {
      id: 'sample-deck-' + Date.now(),
      name: 'Sample Red Deck',
      format: 'Standard',
      mainboard: [
        {
          id: 'lightning-bolt-sample',
          name: 'Lightning Bolt',
          quantity: 4,
          typeLine: 'Instant',
          manaCost: '{R}',
          colors: ['R'],
          cmc: 1,
          rarity: 'common'
        },
        {
          id: 'mountain-sample',
          name: 'Mountain',
          quantity: 20,
          typeLine: 'Basic Land — Mountain',
          manaCost: '',
          colors: [],
          cmc: 0,
          rarity: 'basic'
        }
      ],
      sideboard: [],
      lastModified: new Date().toISOString()
    };
  }

  private renderDeckList(): void {
    const deckList = this.element.querySelector('#deck-list');
    if (!deckList) return;

    if (this.decks.length === 0) {
      deckList.innerHTML = `
        <div class="empty-state">
          <p>No decks yet. Create your first deck!</p>
        </div>
      `;
    } else {
      deckList.innerHTML = this.decks.map(deck => {
        const mainboardCount = deck.mainboard.reduce((sum, card) => sum + card.quantity, 0);
        const sideboardCount = deck.sideboard.reduce((sum, card) => sum + card.quantity, 0);
        
        return `
          <div class="deck-item ${deck === this.selectedDeck ? 'selected' : ''}" 
               onclick="window.decksmithApp?.components?.decks?.selectDeckById?.('${deck.id}');">
            <div class="deck-item-header">
              <h4 class="deck-item-name">${deck.name}</h4>
              <span class="deck-item-count">${mainboardCount + sideboardCount}</span>
            </div>
            <div class="deck-item-details">
              <span class="deck-item-format">${deck.format}</span>
            </div>
          </div>
        `;
      }).join('');
    }
  }

  private selectDeck(deck: Deck): void {
    this.selectedDeck = deck;
    this.renderDeckList();
    this.renderDeckEditor();
    this.updateDeckInfo();
  }

  private renderDeckEditor(): void {
    if (!this.selectedDeck) {
      this.clearDeckEditor();
      return;
    }

    const mainboardCards = this.element.querySelector('#mainboard-cards');
    const sideboardCards = this.element.querySelector('#sideboard-cards');

    if (mainboardCards) {
      if (this.selectedDeck.mainboard.length === 0) {
        mainboardCards.innerHTML = `
          <div class="empty-state">
            <p>No cards in mainboard</p>
          </div>
        `;
      } else {
        mainboardCards.innerHTML = this.selectedDeck.mainboard.map(card => `
          <div class="deck-card-item" onclick="window.decksmithApp?.components?.decks?.showCardDetails?.('${card.name}');">
            <div class="deck-card-info">
              <span class="deck-card-quantity">${card.quantity}x</span>
              <span class="deck-card-name">${card.name}</span>
              <span class="deck-card-type">${card.typeLine || ''}</span>
            </div>
            <div class="deck-card-actions">
              <button class="btn-icon" onclick="event.stopPropagation(); window.decksmithApp?.components?.decks?.adjustCardQuantity?.('${card.name}', false, -1);" title="Remove one">−</button>
              <button class="btn-icon" onclick="event.stopPropagation(); window.decksmithApp?.components?.decks?.adjustCardQuantity?.('${card.name}', false, 1);" title="Add one">+</button>
              <button class="btn-icon remove" onclick="event.stopPropagation(); window.decksmithApp?.components?.decks?.removeCard?.('${card.name}', false);" title="Remove all">×</button>
            </div>
          </div>
        `).join('');
      }
    }

    if (sideboardCards) {
      if (this.selectedDeck.sideboard.length === 0) {
        sideboardCards.innerHTML = `
          <div class="empty-state">
            <p>No sideboard cards</p>
          </div>
        `;
      } else {
        sideboardCards.innerHTML = this.selectedDeck.sideboard.map(card => `
          <div class="deck-card-item" onclick="window.decksmithApp?.components?.decks?.showCardDetails?.('${card.name}');">
            <div class="deck-card-info">
              <span class="deck-card-quantity">${card.quantity}x</span>
              <span class="deck-card-name">${card.name}</span>
              <span class="deck-card-type">${card.typeLine || ''}</span>
            </div>
            <div class="deck-card-actions">
              <button class="btn-icon" onclick="event.stopPropagation(); window.decksmithApp?.components?.decks?.adjustCardQuantity?.('${card.name}', true, -1);" title="Remove one">−</button>
              <button class="btn-icon" onclick="event.stopPropagation(); window.decksmithApp?.components?.decks?.adjustCardQuantity?.('${card.name}', true, 1);" title="Add one">+</button>
              <button class="btn-icon remove" onclick="event.stopPropagation(); window.decksmithApp?.components?.decks?.removeCard?.('${card.name}', true);" title="Remove all">×</button>
            </div>
          </div>
        `).join('');
      }
    }

    this.updateCardCounts();
  }

  private clearDeckEditor(): void {
    const mainboardCards = this.element.querySelector('#mainboard-cards');
    const sideboardCards = this.element.querySelector('#sideboard-cards');

    if (mainboardCards) {
      mainboardCards.innerHTML = `
        <div class="empty-state">
          <p>Select or create a deck to start building</p>
        </div>
      `;
    }

    if (sideboardCards) {
      sideboardCards.innerHTML = `
        <div class="empty-state">
          <p>No sideboard cards</p>
        </div>
      `;
    }

    const nameInput = this.element.querySelector('#deck-name') as HTMLInputElement;
    if (nameInput) nameInput.value = '';

    this.updateCardCounts();
  }

  private updateDeckInfo(): void {
    if (!this.selectedDeck) return;

    const nameInput = this.element.querySelector('#deck-name') as HTMLInputElement;
    if (nameInput) nameInput.value = this.selectedDeck.name || '';

    const formatSelect = this.element.querySelector('#deck-format') as HTMLSelectElement;
    if (formatSelect) formatSelect.value = this.selectedDeck.format || 'Standard';

    this.updateCardCounts();
  }

  private updateCardCounts(): void {
    if (!this.selectedDeck) {
      const elements = ['#deck-total-cards', '#deck-mainboard-cards', '#deck-sideboard-cards', '#mainboard-count', '#sideboard-count'];
      elements.forEach(selector => {
        const element = this.element.querySelector(selector);
        if (element) element.textContent = '0';
      });
      return;
    }

    const mainboardCount = this.selectedDeck.mainboard.reduce((sum, card) => sum + card.quantity, 0);
    const sideboardCount = this.selectedDeck.sideboard.reduce((sum, card) => sum + card.quantity, 0);
    const totalCount = mainboardCount + sideboardCount;

    const totalElement = this.element.querySelector('#deck-total-cards');
    if (totalElement) totalElement.textContent = totalCount.toString();

    const mainboardElement = this.element.querySelector('#deck-mainboard-cards');
    if (mainboardElement) mainboardElement.textContent = mainboardCount.toString();

    const sideboardElement = this.element.querySelector('#deck-sideboard-cards');
    if (sideboardElement) sideboardElement.textContent = sideboardCount.toString();

    const mainboardCountSpan = this.element.querySelector('#mainboard-count');
    if (mainboardCountSpan) mainboardCountSpan.textContent = mainboardCount.toString();

    const sideboardCountSpan = this.element.querySelector('#sideboard-count');
    if (sideboardCountSpan) sideboardCountSpan.textContent = sideboardCount.toString();
  }

  private switchSection(section: string): void {
    this.element.querySelectorAll('.deck-tab-btn').forEach(btn => {
      btn.classList.remove('active');
    });
    this.element.querySelector(`[data-section="${section}"]`)?.classList.add('active');

    this.element.querySelectorAll('.deck-section').forEach(sectionEl => {
      sectionEl.classList.remove('active');
    });
    this.element.querySelector(`#deck-${section}`)?.classList.add('active');
  }

  private updateDeckName(): void {
    if (!this.selectedDeck) return;
    const nameInput = this.element.querySelector('#deck-name') as HTMLInputElement;
    if (nameInput) {
      this.selectedDeck.name = nameInput.value;
      this.selectedDeck.lastModified = new Date().toISOString();
      this.renderDeckList();
      this.saveDecks();
    }
  }

  private updateDeckFormat(): void {
    if (!this.selectedDeck) return;
    const formatSelect = this.element.querySelector('#deck-format') as HTMLSelectElement;
    if (formatSelect) {
      this.selectedDeck.format = formatSelect.value;
      this.selectedDeck.lastModified = new Date().toISOString();
      this.renderDeckList();
      this.saveDecks();
    }
  }

  private async addCardToDeck(cardName: string, quantity: number, isSideboard: boolean): Promise<void> {
    if (!this.selectedDeck) return;
    
    const section = isSideboard ? this.selectedDeck.sideboard : this.selectedDeck.mainboard;
    const existingCard = section.find(card => card.name === cardName);
    
    if (existingCard) {
      existingCard.quantity += quantity;
    } else {
      // Fetch real card data from Scryfall
      try {
        const cardData = await this.fetchCardData(cardName);
        if (cardData) {
          const newCard: DeckCard = {
            id: cardData.id,
            name: cardData.name,
            quantity: quantity,
            typeLine: cardData.typeLine || 'Unknown',
            manaCost: cardData.manaCost || '',
            colors: cardData.colors || [],
            cmc: cardData.cmc || 0,
            rarity: cardData.rarity || 'common',
            power: cardData.power,
            toughness: cardData.toughness,
            imageUri: cardData.imageUri,
            scryfallId: cardData.scryfallId
          };
          section.push(newCard);
        } else {
          // Fallback if card not found
          const newCard: DeckCard = {
            id: `${cardName.toLowerCase().replace(/[^a-z0-9]/g, '-')}-${Date.now()}`,
            name: cardName,
            quantity: quantity,
            typeLine: 'Unknown',
            manaCost: '',
            colors: []
          };
          section.push(newCard);
        }
      } catch (error) {
        console.error('Error fetching card data:', error);
        // Fallback card
        const newCard: DeckCard = {
          id: `${cardName.toLowerCase().replace(/[^a-z0-9]/g, '-')}-${Date.now()}`,
          name: cardName,
          quantity: quantity,
          typeLine: 'Unknown',
          manaCost: '',
          colors: []
        };
        section.push(newCard);
      }
    }
    
    this.selectedDeck.lastModified = new Date().toISOString();
    this.renderDeckEditor();
    this.saveDecks();
  }

  private async fetchCardData(cardName: string): Promise<Card | null> {
    try {
      const encodedName = encodeURIComponent(cardName);
      const response = await fetch(`https://api.scryfall.com/cards/named?exact=${encodedName}`);
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const data = await response.json();
      
      return {
        id: data.id,
        name: data.name,
        manaCost: data.mana_cost || '',
        cmc: data.cmc || 0,
        typeLine: data.type_line || '',
        oracleText: data.oracle_text || '',
        colors: data.colors || [],
        colorIdentity: data.color_identity || [],
        power: data.power || '',
        toughness: data.toughness || '',
        rarity: data.rarity || '',
        setCode: data.set || '',
        setName: data.set_name || '',
        collectorNumber: data.collector_number || '',
        imageUri: data.image_uris?.normal || data.image_uris?.large || '',
        scryfallId: data.id,
        scryfallUri: data.scryfall_uri || '',
        legalities: data.legalities || {},
        prices: data.prices || {}
      };
    } catch (error) {
      console.error('Error fetching from Scryfall:', error);
      return null;
    }
  }

  private showImportDialog(fromClipboard: boolean = false): void {
    const dialog = document.createElement('div');
    dialog.className = 'import-dialog';
    
    dialog.innerHTML = `
      <div class="import-content">
        <div class="import-header">
          <h3>${fromClipboard ? 'Import from Clipboard' : 'Import Deck'}</h3>
          <button class="close-btn" onclick="this.parentElement.parentElement.parentElement.remove()">×</button>
        </div>
        <div class="import-body">
          <div class="import-format">
            <label>Paste deck list (format: quantity name, e.g., "4 Lightning Bolt"):</label>
            <textarea class="import-textarea" id="import-text" placeholder="4 Lightning Bolt&#10;20 Mountain&#10;3 Goblin Guide"></textarea>
          </div>
        </div>
        <div class="import-footer">
          <button class="btn btn-secondary" onclick="this.parentElement.parentElement.parentElement.remove()">Cancel</button>
          <button class="btn btn-primary" onclick="window.decksmithApp?.components?.decks?.processImport?.()">Import</button>
        </div>
      </div>
    `;
    
    document.body.appendChild(dialog);
    
    const textarea = dialog.querySelector('#import-text') as HTMLTextAreaElement;
    if (fromClipboard && textarea) {
      navigator.clipboard.readText().then(text => {
        textarea.value = text;
      }).catch(() => {
        console.log('Could not read clipboard');
      });
    }
  }

  processImport(): void {
    const dialog = document.querySelector('.import-dialog');
    const textarea = dialog?.querySelector('#import-text') as HTMLTextAreaElement;
    
    if (!textarea || !textarea.value.trim()) return;
    
    const lines = textarea.value.trim().split('\n');
    const importedCards: DeckCard[] = [];
    
    for (const line of lines) {
      const match = line.trim().match(/^(\d+)\s+(.+)$/);
      if (match) {
        const quantity = parseInt(match[1]);
        const name = match[2].trim();
        
        importedCards.push({
          id: `${name.toLowerCase().replace(/[^a-z0-9]/g, '-')}-${Date.now()}`,
          name: name,
          quantity: quantity,
          typeLine: 'Unknown',
          manaCost: '',
          colors: []
        });
      }
    }
    
    if (importedCards.length > 0) {
      // Create new deck with imported cards
      const newDeck: Deck = {
        id: 'imported-deck-' + Date.now(),
        name: 'Imported Deck',
        format: 'Standard',
        mainboard: importedCards,
        sideboard: [],
        lastModified: new Date().toISOString()
      };
      
      this.decks.push(newDeck);
      this.renderDeckList();
      this.selectDeck(newDeck);
      this.saveDecks();
    }
    
    dialog?.remove();
  }

  private generateDeckCSV(deck: Deck): string {
    let csv = 'Quantity,Name,Type,Section\n';
    
    deck.mainboard.forEach(card => {
      csv += `${card.quantity},"${card.name}","${card.typeLine || 'Unknown'}",Mainboard\n`;
    });
    
    deck.sideboard.forEach(card => {
      csv += `${card.quantity},"${card.name}","${card.typeLine || 'Unknown'}",Sideboard\n`;
    });
    
    return csv;
  }

  private generateDeckText(deck: Deck): string {
    let text = `${deck.name}\n\nMainboard:\n`;
    
    deck.mainboard.forEach(card => {
      text += `${card.quantity} ${card.name}\n`;
    });
    
    if (deck.sideboard.length > 0) {
      text += `\nSideboard:\n`;
      deck.sideboard.forEach(card => {
        text += `${card.quantity} ${card.name}\n`;
      });
    }
    
    return text;
  }
}
