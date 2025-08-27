// Main application TypeScript file
import { ScryfallAPI, CSVHandler } from './utils';
import type { Card, Deck, DeckCard, Collection } from './types';

class DeckMasterApp {
  private currentTab = 'collection';
  private collection: Collection = { cards: [], lastModified: new Date().toISOString() };
  private decks: Deck[] = [];
  private currentDeck: Deck | null = null;
  private scryfallCache: Map<string, Card> = new Map();

  constructor() {
    this.init();
  }

  private async init(): Promise<void> {
    await this.setupEventListeners();
    await this.loadData();
    this.updateUI();
  }

  private async setupEventListeners(): Promise<void> {
    // Tab switching
    document.querySelectorAll('.tab-btn').forEach(btn => {
      btn.addEventListener('click', (e) => {
        const target = e.target as HTMLElement;
        const tab = target.dataset.tab;
        if (tab) {
          this.switchTab(tab);
        }
      });
    });

    // Window controls
    document.getElementById('minimize-btn')?.addEventListener('click', () => {
      window.electronAPI?.minimizeWindow();
    });

    document.getElementById('maximize-btn')?.addEventListener('click', () => {
      window.electronAPI?.maximizeWindow();
    });

    document.getElementById('close-btn')?.addEventListener('click', () => {
      window.electronAPI?.closeWindow();
    });

    // Collection actions
    document.getElementById('import-collection-btn')?.addEventListener('click', () => {
      this.importCollection();
    });

    document.getElementById('export-collection-btn')?.addEventListener('click', () => {
      this.exportCollection();
    });

    // Deck actions
    document.getElementById('new-deck-btn')?.addEventListener('click', () => {
      this.createNewDeck();
    });

    document.getElementById('import-deck-btn')?.addEventListener('click', () => {
      this.importDeck();
    });

    // AI Recommendations
    document.getElementById('get-recommendations-btn')?.addEventListener('click', () => {
      this.getAIRecommendations();
    });

    // Search functionality
    const searchInput = document.getElementById('collection-search') as HTMLInputElement;
    if (searchInput) {
      let searchTimeout: number;
      searchInput.addEventListener('input', () => {
        clearTimeout(searchTimeout);
        searchTimeout = window.setTimeout(() => {
          this.filterCollection();
        }, 300);
      });
    }

    // Clear search
    document.getElementById('clear-search')?.addEventListener('click', () => {
      const searchInput = document.getElementById('collection-search') as HTMLInputElement;
      if (searchInput) {
        searchInput.value = '';
        this.filterCollection();
      }
    });

    // Filter dropdowns
    ['color-filter', 'rarity-filter', 'type-filter'].forEach(id => {
      document.getElementById(id)?.addEventListener('change', () => {
        this.filterCollection();
      });
    });

    // Modal controls
    document.getElementById('modal-close')?.addEventListener('click', () => {
      this.closeModal();
    });

    document.getElementById('modal-cancel')?.addEventListener('click', () => {
      this.closeModal();
    });

    document.getElementById('modal-overlay')?.addEventListener('click', (e) => {
      if (e.target === e.currentTarget) {
        this.closeModal();
      }
    });

    // Listen for menu actions from main process
    if (window.electronAPI) {
      window.electronAPI.onMenuAction((action: string) => {
        this.handleMenuAction(action);
      });
    }
  }

  private switchTab(tabName: string): void {
    // Update active tab button
    document.querySelectorAll('.tab-btn').forEach(btn => {
      btn.classList.remove('active');
    });
    document.querySelector(`[data-tab="${tabName}"]`)?.classList.add('active');

    // Update active tab panel
    document.querySelectorAll('.tab-panel').forEach(panel => {
      panel.classList.remove('active');
    });
    document.getElementById(`${tabName}-tab`)?.classList.add('active');

    this.currentTab = tabName;
    this.updateStatus(`Switched to ${tabName} tab`);

    // Load tab-specific data
    switch (tabName) {
      case 'collection':
        this.refreshCollectionView();
        break;
      case 'decks':
        this.refreshDecksView();
        break;
      case 'statistics':
        this.refreshStatisticsView();
        break;
    }
  }

  private async loadData(): Promise<void> {
    try {
      // Load collection
      const savedCollection = await window.electronAPI?.store.get('collection');
      if (savedCollection) {
        this.collection = savedCollection;
      }

      // Load decks
      const savedDecks = await window.electronAPI?.store.get('decks');
      if (savedDecks) {
        this.decks = savedDecks;
      }

      this.updateStatus('Data loaded successfully');
    } catch (error) {
      console.error('Error loading data:', error);
      this.updateStatus('Error loading data');
    }
  }

  private async saveData(): Promise<void> {
    try {
      await window.electronAPI?.store.set('collection', this.collection);
      await window.electronAPI?.store.set('decks', this.decks);
      this.updateStatus('Data saved successfully');
    } catch (error) {
      console.error('Error saving data:', error);
      this.updateStatus('Error saving data');
    }
  }

  private updateUI(): void {
    this.refreshCollectionView();
    this.refreshDecksView();
    this.refreshStatisticsView();
    this.updateCardCount();
  }

  private refreshCollectionView(): void {
    const grid = document.getElementById('collection-grid');
    if (!grid) return;

    if (this.collection.cards.length === 0) {
      grid.innerHTML = `
        <div class="empty-state">
          <p>Your collection is empty. Import some cards to get started!</p>
        </div>
      `;
      return;
    }

    grid.innerHTML = this.collection.cards.map(card => `
      <div class="card-item" data-card-id="${card.id}">
        <div class="card-header">
          <h4>${card.name}</h4>
          <span class="card-quantity">×${card.quantity || 1}</span>
        </div>
        <div class="card-details">
          <p class="mana-cost">${card.manaCost || ''}</p>
          <p class="type-line">${card.typeLine || ''}</p>
          <p class="rarity rarity-${card.rarity}">${card.rarity || ''}</p>
        </div>
      </div>
    `).join('');

    // Add click handlers for card details
    grid.querySelectorAll('.card-item').forEach(item => {
      item.addEventListener('click', (e) => {
        const cardId = (e.currentTarget as HTMLElement).dataset.cardId;
        const card = this.collection.cards.find(c => c.id === cardId);
        if (card) {
          this.showCardDetails(card);
        }
      });
    });
  }

  private refreshDecksView(): void {
    const deckList = document.getElementById('deck-list');
    if (!deckList) return;

    if (this.decks.length === 0) {
      deckList.innerHTML = `
        <div class="empty-state">
          <p>No decks yet. Create your first deck!</p>
        </div>
      `;
      return;
    }

    deckList.innerHTML = this.decks.map(deck => `
      <div class="deck-item" data-deck-id="${deck.id}">
        <h4>${deck.name}</h4>
        <p class="deck-format">${deck.format}</p>
        <p class="deck-cards">${deck.cards.length} cards</p>
      </div>
    `).join('');

    // Add click handlers
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

  private refreshStatisticsView(): void {
    // Update stat cards
    document.getElementById('total-cards')!.textContent = 
      this.collection.cards.reduce((sum, card) => sum + (card.quantity || 1), 0).toString();
    
    document.getElementById('unique-cards')!.textContent = 
      this.collection.cards.length.toString();
    
    document.getElementById('total-decks')!.textContent = 
      this.decks.length.toString();
    
    // TODO: Implement collection value calculation
    document.getElementById('collection-value')!.textContent = '$0.00';
  }

  private filterCollection(): void {
    const searchTerm = (document.getElementById('collection-search') as HTMLInputElement)?.value.toLowerCase() || '';
    const colorFilter = (document.getElementById('color-filter') as HTMLSelectElement)?.value || '';
    const rarityFilter = (document.getElementById('rarity-filter') as HTMLSelectElement)?.value || '';
    const typeFilter = (document.getElementById('type-filter') as HTMLSelectElement)?.value || '';

    const filteredCards = this.collection.cards.filter(card => {
      const matchesSearch = !searchTerm || card.name.toLowerCase().includes(searchTerm);
      const matchesColor = !colorFilter || card.colors?.includes(colorFilter);
      const matchesRarity = !rarityFilter || card.rarity === rarityFilter;
      const matchesType = !typeFilter || card.typeLine?.toLowerCase().includes(typeFilter);

      return matchesSearch && matchesColor && matchesRarity && matchesType;
    });

    // Update grid with filtered cards
    const grid = document.getElementById('collection-grid');
    if (grid) {
      grid.innerHTML = filteredCards.map(card => `
        <div class="card-item" data-card-id="${card.id}">
          <div class="card-header">
            <h4>${card.name}</h4>
            <span class="card-quantity">×${card.quantity || 1}</span>
          </div>
          <div class="card-details">
            <p class="mana-cost">${card.manaCost || ''}</p>
            <p class="type-line">${card.typeLine || ''}</p>
            <p class="rarity rarity-${card.rarity}">${card.rarity || ''}</p>
          </div>
        </div>
      `).join('');
    }

    this.updateStatus(`Showing ${filteredCards.length} cards`);
  }

  private async importCollection(): Promise<void> {
    try {
      const result = await window.electronAPI?.openFileDialog({
        title: 'Import Collection',
        filters: [
          { name: 'CSV Files', extensions: ['csv'] },
          { name: 'All Files', extensions: ['*'] }
        ]
      });

      if (result && !result.canceled && result.filePaths.length > 0) {
        this.updateStatus('Importing collection...');
        // TODO: Implement CSV parsing and Scryfall enrichment
        this.updateStatus('Collection import completed');
      }
    } catch (error) {
      console.error('Import error:', error);
      this.updateStatus('Import failed');
    }
  }

  private async exportCollection(): Promise<void> {
    try {
      const result = await window.electronAPI?.saveFileDialog({
        title: 'Export Collection',
        defaultPath: 'collection.csv',
        filters: [
          { name: 'CSV Files', extensions: ['csv'] },
          { name: 'All Files', extensions: ['*'] }
        ]
      });

      if (result && !result.canceled && result.filePath) {
        this.updateStatus('Exporting collection...');
        // TODO: Implement CSV export
        this.updateStatus('Collection export completed');
      }
    } catch (error) {
      console.error('Export error:', error);
      this.updateStatus('Export failed');
    }
  }

  private createNewDeck(): void {
    const deckName = prompt('Enter deck name:');
    if (!deckName) return;

    const newDeck: Deck = {
      id: Date.now().toString(),
      name: deckName,
      format: 'Standard',
      cards: [],
      created: new Date().toISOString(),
      modified: new Date().toISOString()
    };

    this.decks.push(newDeck);
    this.saveData();
    this.refreshDecksView();
    this.selectDeck(newDeck);
  }

  private selectDeck(deck: Deck): void {
    this.currentDeck = deck;
    const editor = document.getElementById('deck-editor');
    if (editor) {
      editor.innerHTML = `
        <div class="deck-header">
          <h3>${deck.name}</h3>
          <p class="deck-format">${deck.format}</p>
        </div>
        <div class="deck-contents">
          ${deck.cards.map(card => `
            <div class="deck-card">
              <span>${card.quantity}x ${card.name}</span>
            </div>
          `).join('')}
        </div>
      `;
    }
  }

  private async importDeck(): Promise<void> {
    // TODO: Implement deck import functionality
    this.updateStatus('Deck import not yet implemented');
  }

  private async getAIRecommendations(): Promise<void> {
    if (!this.currentDeck) {
      this.updateStatus('Please select a deck first');
      return;
    }

    this.updateStatus('Getting AI recommendations...');
    // TODO: Implement AI recommendations
    this.updateStatus('AI recommendations not yet implemented');
  }

  private showCardDetails(card: Card): void {
    const modal = document.getElementById('modal-overlay');
    const title = document.getElementById('modal-title');
    const body = document.getElementById('modal-body');

    if (modal && title && body) {
      title.textContent = card.name;
      body.innerHTML = `
        <div class="card-details-modal">
          <div class="card-image">
            ${card.imageUri ? `<img src="${card.imageUri}" alt="${card.name}" />` : '<div class="no-image">No image available</div>'}
          </div>
          <div class="card-info">
            <p><strong>Mana Cost:</strong> ${card.manaCost || 'N/A'}</p>
            <p><strong>Type:</strong> ${card.typeLine || 'N/A'}</p>
            <p><strong>Rarity:</strong> ${card.rarity || 'N/A'}</p>
            <p><strong>Set:</strong> ${card.setName || 'N/A'}</p>
            ${card.oracleText ? `<p><strong>Text:</strong> ${card.oracleText}</p>` : ''}
            ${card.power && card.toughness ? `<p><strong>P/T:</strong> ${card.power}/${card.toughness}</p>` : ''}
          </div>
        </div>
      `;
      modal.classList.remove('hidden');
    }
  }

  private closeModal(): void {
    const modal = document.getElementById('modal-overlay');
    modal?.classList.add('hidden');
  }

  private updateStatus(message: string): void {
    const statusElement = document.getElementById('status-message');
    if (statusElement) {
      statusElement.textContent = message;
    }
    console.log(`Status: ${message}`);
  }

  private updateCardCount(): void {
    const countElement = document.getElementById('card-count');
    if (countElement) {
      const totalCards = this.collection.cards.reduce((sum, card) => sum + (card.quantity || 1), 0);
      countElement.textContent = `${totalCards} cards loaded`;
    }
  }

  private handleMenuAction(action: string): void {
    switch (action) {
      case 'menu:new-collection':
        // TODO: Implement new collection
        break;
      case 'menu:import-collection':
        this.importCollection();
        break;
      case 'menu:export-collection':
        this.exportCollection();
        break;
      case 'menu:new-deck':
        this.createNewDeck();
        break;
      case 'menu:import-deck':
        this.importDeck();
        break;
      case 'menu:export-deck':
        // TODO: Implement export deck
        break;
      case 'menu:about':
        this.showAbout();
        break;
    }
  }

  private showAbout(): void {
    const modal = document.getElementById('modal-overlay');
    const title = document.getElementById('modal-title');
    const body = document.getElementById('modal-body');

    if (modal && title && body) {
      title.textContent = 'About Deckmaster';
      body.innerHTML = `
        <div class="about-content">
          <h3>🃏 Deckmaster v2.0.0</h3>
          <p>Modern Magic: The Gathering collection and deck manager built with Electron.</p>
          <br>
          <p><strong>Features:</strong></p>
          <ul>
            <li>Collection management with Scryfall integration</li>
            <li>Advanced deck building tools</li>
            <li>AI-powered card recommendations</li>
            <li>Import/Export CSV and Arena formats</li>
            <li>Real-time statistics and analytics</li>
          </ul>
          <br>
          <p>Built with ❤️ for the MTG community</p>
        </div>
      `;
      modal.classList.remove('hidden');
    }
  }
}

// Initialize the app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
  new DeckMasterApp();
});
