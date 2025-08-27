import { BaseComponent } from './BaseComponent';
import type { Deck } from '../types';

export class DecksTab extends BaseComponent {
  private decks: Deck[] = [];
  private selectedDeck: Deck | null = null;

  constructor() {
    super('#decks-tab');
  }

  initialize(): void {
    if (this.isInitialized) return;
    
    this.render();
    this.setupEventListeners();
    this.isInitialized = true;
  }

  render(): void {
    this.element.innerHTML = `
      <div class="decks-layout">
        <!-- Deck List Sidebar -->
        <div class="deck-sidebar">
          <div class="sidebar-header">
            <h3>Decks</h3>
            <button id="new-deck-btn" class="btn btn-primary">+ New</button>
          </div>
          
          <div class="deck-list" id="deck-list">
            <div class="empty-state" id="deck-list-empty">
              <p>No decks yet. Create your first deck!</p>
            </div>
          </div>
          
          <div class="deck-info-panel" id="deck-info">
            <h4>Deck Information</h4>
            <div class="deck-name-input">
              <input type="text" id="deck-name" placeholder="Deck Name" />
            </div>
            <div class="deck-format">
              <label>Format:</label>
              <select id="deck-format">
                <option value="Standard">Standard</option>
                <option value="Modern">Modern</option>
                <option value="Legacy">Legacy</option>
                <option value="Commander">Commander</option>
                <option value="Pioneer">Pioneer</option>
                <option value="Historic">Historic</option>
              </select>
            </div>
            <div class="deck-stats">
              <div class="stat-row">
                <span>Total Cards:</span>
                <span id="deck-total-cards">0</span>
              </div>
              <div class="stat-row">
                <span>Sideboard:</span>
                <span id="deck-sideboard-cards">0</span>
              </div>
            </div>
            <div class="deck-actions">
              <button id="import-deck-btn" class="btn btn-secondary btn-full">Import CSV</button>
              <button id="export-deck-btn" class="btn btn-secondary btn-full">Export CSV</button>
              <button id="copy-to-clipboard-btn" class="btn btn-secondary btn-full">Copy to Clipboard</button>
            </div>
          </div>
        </div>

        <!-- Deck Editor -->
        <div class="deck-main">
          <div class="deck-tabs">
            <button class="deck-tab-btn active" data-section="mainboard">
              Mainboard
            </button>
            <button class="deck-tab-btn" data-section="sideboard">
              Sideboard
            </button>
          </div>

          <div class="deck-content">
            <div id="deck-mainboard" class="deck-section active">
              <div class="deck-header">
                <div class="add-card-section">
                  <input type="text" id="add-card-input" placeholder="Add card..." />
                  <input type="number" id="add-card-qty" value="1" min="1" max="4" />
                  <button id="add-card-mainboard" class="btn btn-primary">Add</button>
                </div>
              </div>
              <div class="deck-cards" id="mainboard-cards">
                <div class="empty-state">
                  <p>Select a deck to edit</p>
                </div>
              </div>
            </div>

            <div id="deck-sideboard" class="deck-section">
              <div class="deck-header">
                <div class="add-card-section">
                  <input type="text" id="add-card-input-sb" placeholder="Add card to sideboard..." />
                  <input type="number" id="add-card-qty-sb" value="1" min="1" max="4" />
                  <button id="add-card-sideboard" class="btn btn-primary">Add</button>
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
    // New deck button
    this.bindEvent('#new-deck-btn', 'click', () => this.createNewDeck());

    // Import/Export buttons
    this.bindEvent('#import-deck-btn', 'click', () => this.importDeck());
    this.bindEvent('#export-deck-btn', 'click', () => this.exportDeck());
    this.bindEvent('#copy-to-clipboard-btn', 'click', () => this.copyToClipboard());

    // Deck tabs
    this.element.querySelectorAll('.deck-tab-btn').forEach(btn => {
      btn.addEventListener('click', (e) => {
        const target = e.target as HTMLElement;
        const section = target.dataset.section;
        if (section) {
          this.switchSection(section);
        }
      });
    });

    // Add card buttons
    this.bindEvent('#add-card-mainboard', 'click', () => this.addCardToMainboard());
    this.bindEvent('#add-card-sideboard', 'click', () => this.addCardToSideboard());

    // Deck name input
    this.bindEvent('#deck-name', 'input', () => this.updateDeckName());

    // Deck format select
    this.bindEvent('#deck-format', 'change', () => this.updateDeckFormat());
  }

  setDecks(decks: Deck[]): void {
    this.decks = decks;
    this.renderDeckList();
  }

  private renderDeckList(): void {
    const deckList = this.element.querySelector('#deck-list');
    const emptyState = this.element.querySelector('#deck-list-empty');
    
    if (!deckList) return;

    if (this.decks.length === 0) {
      emptyState?.classList.remove('hidden');
      deckList.innerHTML = `
        <div class="empty-state">
          <p>No decks yet. Create your first deck!</p>
        </div>
      `;
    } else {
      emptyState?.classList.add('hidden');
      deckList.innerHTML = this.decks.map(deck => `
        <div class="deck-item ${deck === this.selectedDeck ? 'selected' : ''}" data-deck-id="${deck.id}">
          <div class="deck-item-header">
            <h4 class="deck-item-name">${deck.name || 'Untitled Deck'}</h4>
            <span class="deck-item-count">${deck.mainboard.length + deck.sideboard.length} cards</span>
          </div>
          <div class="deck-item-format">${deck.format || 'Standard'}</div>
        </div>
      `).join('');

      // Add click listeners for deck selection
      deckList.querySelectorAll('.deck-item').forEach(item => {
        item.addEventListener('click', (e) => {
          const deckId = (e.currentTarget as HTMLElement).dataset.deckId;
          const deck = this.decks.find(d => d.id === deckId);
          if (deck) {
            this.selectDeck(deck);
          }
        });
      });
    }
  }

  private selectDeck(deck: Deck): void {
    this.selectedDeck = deck;
    this.renderDeckList(); // Re-render to update selection
    this.renderDeckEditor();
    this.updateDeckInfo();
  }

  private renderDeckEditor(): void {
    if (!this.selectedDeck) return;

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
          <div class="deck-card-item">
            <span class="card-quantity">${card.quantity}</span>
            <span class="card-name">${card.name}</span>
            <button class="btn-icon remove-card" data-card-name="${card.name}" data-section="mainboard">×</button>
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
          <div class="deck-card-item">
            <span class="card-quantity">${card.quantity}</span>
            <span class="card-name">${card.name}</span>
            <button class="btn-icon remove-card" data-card-name="${card.name}" data-section="sideboard">×</button>
          </div>
        `).join('');
      }
    }
  }

  private updateDeckInfo(): void {
    if (!this.selectedDeck) return;

    const nameInput = this.element.querySelector('#deck-name') as HTMLInputElement;
    if (nameInput) nameInput.value = this.selectedDeck.name || '';

    const formatSelect = this.element.querySelector('#deck-format') as HTMLSelectElement;
    if (formatSelect) formatSelect.value = this.selectedDeck.format || 'Standard';

    const totalCards = this.selectedDeck.mainboard.reduce((sum, card) => sum + card.quantity, 0);
    const sideboardCards = this.selectedDeck.sideboard.reduce((sum, card) => sum + card.quantity, 0);

    const totalElement = this.element.querySelector('#deck-total-cards');
    if (totalElement) totalElement.textContent = totalCards.toString();

    const sideboardElement = this.element.querySelector('#deck-sideboard-cards');
    if (sideboardElement) sideboardElement.textContent = sideboardCards.toString();
  }

  private switchSection(section: string): void {
    // Update tab buttons
    this.element.querySelectorAll('.deck-tab-btn').forEach(btn => {
      btn.classList.remove('active');
    });
    this.element.querySelector(`[data-section="${section}"]`)?.classList.add('active');

    // Update sections
    this.element.querySelectorAll('.deck-section').forEach(section => {
      section.classList.remove('active');
    });
    this.element.querySelector(`#deck-${section}`)?.classList.add('active');
  }

  private createNewDeck(): void {
    const newDeck: Deck = {
      id: Date.now().toString(),
      name: 'New Deck',
      format: 'Standard',
      mainboard: [],
      sideboard: [],
      lastModified: new Date().toISOString()
    };

    this.decks.push(newDeck);
    this.renderDeckList();
    this.selectDeck(newDeck);
  }

  private addCardToMainboard(): void {
    // TODO: Implement add card logic
    console.log('Add card to mainboard');
  }

  private addCardToSideboard(): void {
    // TODO: Implement add card logic
    console.log('Add card to sideboard');
  }

  private updateDeckName(): void {
    if (!this.selectedDeck) return;
    const nameInput = this.element.querySelector('#deck-name') as HTMLInputElement;
    if (nameInput) {
      this.selectedDeck.name = nameInput.value;
      this.renderDeckList();
    }
  }

  private updateDeckFormat(): void {
    if (!this.selectedDeck) return;
    const formatSelect = this.element.querySelector('#deck-format') as HTMLSelectElement;
    if (formatSelect) {
      this.selectedDeck.format = formatSelect.value;
      this.renderDeckList();
    }
  }

  private importDeck(): void {
    console.log('Import deck');
  }

  private exportDeck(): void {
    console.log('Export deck');
  }

  private copyToClipboard(): void {
    console.log('Copy to clipboard');
  }
}
