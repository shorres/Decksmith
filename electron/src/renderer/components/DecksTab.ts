import { BaseComponent } from './BaseComponent';
import { CardDetailsModal } from './CardDetailsModal';
import { ScryfallAPI, CSVHandler } from '../utils';
import { setStatus, escapeHtml } from '../ui';
import type { Deck, DeckCard } from '../types';

export class DecksTab extends BaseComponent {
  private decks: Deck[] = [];
  private selectedDeck: Deck | null = null;
  private cardModal: CardDetailsModal;
  private onDeckSelectionChange: ((deck: Deck | null) => void) | null = null;

  constructor() {
    super('#decks-tab');
    this.cardModal = new CardDetailsModal();
  }

  initialize(): void {
    if (this.initialized) return;
    
    this.render();
    this.setupEventListeners();
    this.loadDecks();
    this.isInitialized = true;
  }

  render(): void {
    this.element.innerHTML = `
      <div class="decks-layout">
        <!-- Deck Selection View (shown when no deck is selected) -->
        <div class="deck-selection-view" id="deck-selection-view">
          <div class="deck-selection-header">
            <h2>My Decks</h2>
            <button id="new-deck-btn-main" class="btn btn-primary" onclick="window.app?.components?.decks?.createNewDeck?.();">
              + New Deck
            </button>
          </div>
          
          <div class="deck-grid" id="deck-grid">
            <div class="loading-state">
              <div class="spinner"></div>
              <p>Loading decks...</p>
            </div>
          </div>
        </div>

        <!-- Deck Editor View (shown when a deck is selected) -->
        <div class="deck-editor-view hidden" id="deck-editor-view">
          <div class="deck-editor-header">
            <div class="deck-header-left">
              <button id="back-to-decks" class="btn btn-secondary" onclick="window.app?.components?.decks?.clearDeckSelection?.();">
                ← Back to Decks
              </button>
              <div class="deck-title-section">
                <input type="text" id="deck-name" class="deck-name-input-large" placeholder="Deck Name" />
                <select id="deck-format" class="deck-format-select">
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
            </div>
            <div class="deck-header-right">
              <div class="deck-stats-inline">
                <span class="stat-badge">
                  <strong id="deck-total-cards">0</strong> cards
                </span>
                <span class="stat-badge">
                  Main: <strong id="deck-mainboard-cards">0</strong>
                </span>
                <span class="stat-badge">
                  Side: <strong id="deck-sideboard-cards">0</strong>
                </span>
              </div>
              <div class="deck-actions-inline">
                <button id="copy-deck-btn" class="btn btn-secondary btn-sm" onclick="window.app?.components?.decks?.copyDeck?.();" title="Copy Deck">📋 Copy</button>
                <button id="deck-import-clipboard-btn" class="btn btn-secondary btn-sm" onclick="window.app?.components?.decks?.importFromClipboard?.();" title="Import from Clipboard">📥 Import</button>
                <button id="export-deck-btn" class="btn btn-secondary btn-sm" onclick="window.app?.components?.decks?.exportDeck?.();" title="Export Deck">📤 Export</button>
                <button id="delete-deck-btn" class="btn btn-danger btn-sm" onclick="window.app?.components?.decks?.deleteDeck?.();" title="Delete Deck">🗑️ Delete</button>
              </div>
            </div>
          </div>

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
                  <button id="add-card-mainboard" class="btn btn-primary" onclick="window.app?.components?.decks?.addCardToMainboard?.();">Add</button>
                </div>
              </div>
              <div class="deck-cards" id="mainboard-cards">
                <div class="empty-state">
                  <p>No cards in mainboard</p>
                </div>
              </div>
            </div>

            <div id="deck-sideboard" class="deck-section">
              <div class="deck-header">
                <div class="add-card-section">
                  <input type="text" id="add-card-input-sb" placeholder="Add card to sideboard..." autocomplete="off" />
                  <input type="number" id="add-card-qty-sb" value="1" min="1" max="4" />
                  <button id="add-card-sideboard" class="btn btn-primary" onclick="window.app?.components?.decks?.addCardToSideboard?.();">Add</button>
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
  getAllDecks(): Deck[] {
    return [...this.decks];
  }

  getCurrentDeck(): Deck | null {
    return this.selectedDeck;
  }

  setOnDeckSelectionChange(callback: (deck: Deck | null) => void): void {
    this.onDeckSelectionChange = callback;
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

  // Cards are addressed by their position in the section so names never have to be
  // embedded in inline onclick strings (names like "Urza's Saga" would break them).
  adjustCardQuantity(cardIndex: number, isSideboard: boolean, change: number): void {
    if (!this.selectedDeck) return;

    const section = isSideboard ? this.selectedDeck.sideboard : this.selectedDeck.mainboard;
    if (!section[cardIndex]) return;

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

  removeCard(cardIndex: number, isSideboard: boolean): void {
    if (!this.selectedDeck) return;

    const section = isSideboard ? this.selectedDeck.sideboard : this.selectedDeck.mainboard;
    const card = section[cardIndex];
    if (!card) return;

    const confirmed = confirm(`Remove all copies of "${card.name}"?`);
    if (!confirmed) return;

    section.splice(cardIndex, 1);
    this.selectedDeck.lastModified = new Date().toISOString();
    this.renderDeckEditor();
    this.saveDecks();
  }

  showCardDetails(cardIndex: number, isSideboard: boolean): void {
    const section = isSideboard ? this.selectedDeck?.sideboard : this.selectedDeck?.mainboard;
    const card = section?.[cardIndex];
    if (card) {
      this.cardModal.show(card.name);
    }
  }

  clearDeckSelection(): void {
    this.selectedDeck = null;
    
    // Show selection view, hide editor view
    const selectionView = this.element.querySelector('#deck-selection-view');
    const editorView = this.element.querySelector('#deck-editor-view');
    
    if (selectionView) selectionView.classList.remove('hidden');
    if (editorView) editorView.classList.add('hidden');
    
    this.renderDeckList();
    this.clearDeckEditor();
  }

  importDeck(): void {
    this.showImportDialog();
  }

  importFromClipboard(): void {
    this.showImportDialog(true);
  }

  async exportDeck(): Promise<void> {
    const deck = this.selectedDeck;
    if (!deck) {
      setStatus('Open a deck to export it');
      return;
    }

    // Deck list text by default; CSV if the user picks a .csv file name
    const baseName = (deck.name || 'deck').replace(/[\\/:*?"<>|]/g, '_');
    try {
      const result = await window.electronAPI?.saveTextFile({
        title: 'Export Deck',
        defaultPath: `${baseName}.txt`,
        filters: [
          { name: 'Deck List (Arena/MTGO)', extensions: ['txt'] },
          { name: 'CSV Files', extensions: ['csv'] }
        ],
        content: CSVHandler.exportDeckToArenaFormat(deck),
        contentByExtension: { csv: CSVHandler.exportDeckToCSV(deck) }
      });

      if (result && !result.canceled) {
        setStatus(`Exported "${deck.name}" to ${result.filePath}`);
      }
    } catch (error) {
      console.error('Error exporting deck:', error);
      setStatus('Error exporting deck');
    }
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
      
      // Don't auto-select first deck - let user choose
      // if (this.decks.length > 0) {
      //   this.selectDeck(this.decks[0]);
      // }
      
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
    const deckGrid = this.element.querySelector('#deck-grid');
    if (!deckGrid) return;

    if (this.decks.length === 0) {
      deckGrid.innerHTML = `
        <div class="empty-state-large">
          <div class="empty-icon">🃏</div>
          <h3>No Decks Yet</h3>
          <p>Create your first deck to get started!</p>
          <button class="btn btn-primary btn-lg" onclick="window.app?.components?.decks?.createNewDeck?.();">
            + Create First Deck
          </button>
        </div>
      `;
    } else {
      deckGrid.innerHTML = this.decks.map(deck => {
        const mainboardCount = deck.mainboard.reduce((sum, card) => sum + card.quantity, 0);
        const sideboardCount = deck.sideboard.reduce((sum, card) => sum + card.quantity, 0);
        const totalCards = mainboardCount + sideboardCount;
        
        // Get color identity from deck cards
        const colors = new Set<string>();
        [...deck.mainboard, ...deck.sideboard].forEach(card => {
          if (card.colors) {
            card.colors.forEach(c => colors.add(c));
          }
        });
        const colorBadges = Array.from(colors).map(c => {
          const colorClass = c === 'W' ? 'white' : 
                            c === 'U' ? 'blue' : 
                            c === 'B' ? 'black' :
                            c === 'R' ? 'red' : 'green';
          return `<span class="mana-symbol ${colorClass}">${c}</span>`;
        }).join('');
        
        return `
          <div class="deck-card" onclick="window.app?.components?.decks?.selectDeckById?.('${deck.id}');">
            <div class="deck-card-header">
              <h3 class="deck-card-name">${escapeHtml(deck.name)}</h3>
              <span class="deck-card-format">${escapeHtml(deck.format)}</span>
            </div>
            <div class="deck-card-colors">
              ${colorBadges || '<span class="text-muted">Colorless</span>'}
            </div>
            <div class="deck-card-stats">
              <div class="deck-stat">
                <span class="deck-stat-label">Total</span>
                <span class="deck-stat-value">${totalCards}</span>
              </div>
              <div class="deck-stat">
                <span class="deck-stat-label">Main</span>
                <span class="deck-stat-value">${mainboardCount}</span>
              </div>
              <div class="deck-stat">
                <span class="deck-stat-label">Side</span>
                <span class="deck-stat-value">${sideboardCount}</span>
              </div>
            </div>
            <div class="deck-card-footer">
              <span class="deck-modified">Modified: ${deck.lastModified ? new Date(deck.lastModified).toLocaleDateString() : 'Never'}</span>
            </div>
          </div>
        `;
      }).join('');
    }
  }

  private selectDeck(deck: Deck): void {
    this.selectedDeck = deck;
    
    // Show editor view, hide selection view
    const selectionView = this.element.querySelector('#deck-selection-view');
    const editorView = this.element.querySelector('#deck-editor-view');
    
    if (selectionView) selectionView.classList.add('hidden');
    if (editorView) editorView.classList.remove('hidden');
    
    this.renderDeckEditor();
    this.updateDeckInfo();
    
    // Notify listeners of deck selection change
    if (this.onDeckSelectionChange) {
      this.onDeckSelectionChange(deck);
    }
  }

  private renderDeckEditor(): void {
    if (!this.selectedDeck) {
      this.clearDeckEditor();
      return;
    }

    this.renderDeckSection('#mainboard-cards', this.selectedDeck.mainboard, false, 'No cards in mainboard');
    this.renderDeckSection('#sideboard-cards', this.selectedDeck.sideboard, true, 'No sideboard cards');
    this.updateCardCounts();
  }

  private renderDeckSection(selector: string, cards: DeckCard[], isSideboard: boolean, emptyText: string): void {
    const container = this.element.querySelector(selector);
    if (!container) return;

    if (cards.length === 0) {
      container.innerHTML = `
        <div class="empty-state">
          <p>${emptyText}</p>
        </div>
      `;
      return;
    }

    const decks = 'window.app?.components?.decks';
    container.innerHTML = cards.map((card, index) => `
      <div class="deck-card-item" onclick="${decks}?.showCardDetails?.(${index}, ${isSideboard});">
        <div class="deck-card-info">
          <span class="deck-card-quantity">${card.quantity}x</span>
          <span class="deck-card-name">${escapeHtml(card.name)}</span>
          <span class="deck-card-type">${escapeHtml(card.typeLine)}</span>
        </div>
        <div class="deck-card-actions">
          <button class="btn-icon" onclick="event.stopPropagation(); ${decks}?.adjustCardQuantity?.(${index}, ${isSideboard}, -1);" title="Remove one">−</button>
          <button class="btn-icon" onclick="event.stopPropagation(); ${decks}?.adjustCardQuantity?.(${index}, ${isSideboard}, 1);" title="Add one">+</button>
          <button class="btn-icon remove" onclick="event.stopPropagation(); ${decks}?.removeCard?.(${index}, ${isSideboard});" title="Remove all">×</button>
        </div>
      </div>
    `).join('');
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
    const existingCard = section.find(card => card.name.toLowerCase() === cardName.toLowerCase());

    if (existingCard) {
      existingCard.quantity += quantity;
    } else {
      let cardData = null;
      try {
        cardData = await ScryfallAPI.getCard(cardName);
      } catch (error) {
        console.error('Error fetching card data:', error);
      }

      // Fall back to a bare entry if Scryfall doesn't know the card (or is unreachable)
      section.push(cardData
        ? {
            id: cardData.id,
            name: cardData.name,
            quantity,
            typeLine: cardData.typeLine || 'Unknown',
            manaCost: cardData.manaCost || '',
            colors: cardData.colors || [],
            cmc: cardData.cmc || 0,
            rarity: cardData.rarity || 'common',
            power: cardData.power,
            toughness: cardData.toughness,
            setCode: cardData.setCode,
            collectorNumber: cardData.collectorNumber,
            imageUri: cardData.imageUri,
            scryfallId: cardData.scryfallId
          }
        : this.createPlaceholderCard(cardName, quantity));
    }

    this.selectedDeck.lastModified = new Date().toISOString();
    this.renderDeckEditor();
    this.saveDecks();
  }

  private createPlaceholderCard(name: string, quantity: number): DeckCard {
    return {
      id: `${name.toLowerCase().replace(/[^a-z0-9]/g, '-')}-${Date.now()}`,
      name,
      quantity,
      typeLine: 'Unknown',
      manaCost: '',
      colors: []
    };
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
            <label>Paste deck list (e.g. "4 Lightning Bolt"; put sideboard cards after a "Sideboard" line):</label>
            <textarea class="import-textarea" id="import-text" placeholder="4 Lightning Bolt&#10;20 Mountain&#10;&#10;Sideboard&#10;3 Searing Blaze"></textarea>
          </div>
        </div>
        <div class="import-footer">
          <button class="btn btn-secondary" onclick="this.parentElement.parentElement.parentElement.remove()">Cancel</button>
          <button class="btn btn-primary" onclick="window.app?.components?.decks?.processImport?.()">Import</button>
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

    const parsed = CSVHandler.parseArenaFormat(textarea.value);
    const mainboard = parsed.filter(card => !card.sideboard).map(card => this.createPlaceholderCard(card.name, card.quantity));
    const sideboard = parsed.filter(card => card.sideboard).map(card => this.createPlaceholderCard(card.name, card.quantity));

    if (parsed.length > 0) {
      const newDeck: Deck = {
        id: 'imported-deck-' + Date.now(),
        name: 'Imported Deck',
        format: 'Standard',
        mainboard,
        sideboard,
        lastModified: new Date().toISOString()
      };

      this.decks.push(newDeck);
      this.renderDeckList();
      this.selectDeck(newDeck);
      this.saveDecks();
      setStatus(`Imported ${parsed.length} card entries`);
    }

    dialog?.remove();
  }
}
