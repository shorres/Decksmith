import { BaseComponent } from './BaseComponent';
import type { Card, Collection } from '../types';

export class CollectionTab extends BaseComponent {
  private collection: Collection = { cards: [], lastModified: new Date().toISOString() };
  private filteredCards: Card[] = [];

  constructor() {
    super('#collection-tab');
  }

  initialize(): void {
    if (this.isInitialized) return;
    
    this.render();
    this.setupEventListeners();
    this.isInitialized = true;
  }

  render(): void {
    this.element.innerHTML = `
      <div class="collection-layout">
        <!-- Sidebar -->
        <div class="collection-sidebar">
          <div class="sidebar-section">
            <h3>Filters</h3>
            <button id="clear-filters" class="btn-link">Clear</button>
          </div>
          
          <!-- Search -->
          <div class="filter-group">
            <label class="filter-label">Card Name</label>
            <div class="search-input-wrapper">
              <input type="text" id="collection-search" placeholder="Search cards..." />
              <button id="clear-search" class="btn-icon">×</button>
            </div>
          </div>

          <!-- Colors -->
          <div class="filter-group">
            <label class="filter-label">Colors</label>
            <div class="color-filters">
              <label class="color-checkbox">
                <input type="checkbox" value="W" />
                <span class="color-symbol white">W</span>
              </label>
              <label class="color-checkbox">
                <input type="checkbox" value="U" />
                <span class="color-symbol blue">U</span>
              </label>
              <label class="color-checkbox">
                <input type="checkbox" value="B" />
                <span class="color-symbol black">B</span>
              </label>
              <label class="color-checkbox">
                <input type="checkbox" value="R" />
                <span class="color-symbol red">R</span>
              </label>
              <label class="color-checkbox">
                <input type="checkbox" value="G" />
                <span class="color-symbol green">G</span>
              </label>
            </div>
          </div>

          <!-- Type Filter -->
          <div class="filter-group">
            <label class="filter-label">Card Type</label>
            <select id="type-filter" class="filter-select">
              <option value="">All Types</option>
              <option value="creature">Creature</option>
              <option value="instant">Instant</option>
              <option value="sorcery">Sorcery</option>
              <option value="enchantment">Enchantment</option>
              <option value="artifact">Artifact</option>
              <option value="planeswalker">Planeswalker</option>
              <option value="land">Land</option>
            </select>
          </div>

          <!-- Rarity Filter -->
          <div class="filter-group">
            <label class="filter-label">Rarity</label>
            <select id="rarity-filter" class="filter-select">
              <option value="">All Rarities</option>
              <option value="common">Common</option>
              <option value="uncommon">Uncommon</option>
              <option value="rare">Rare</option>
              <option value="mythic">Mythic</option>
            </select>
          </div>

          <!-- Collection Stats -->
          <div class="collection-stats">
            <h4>Collection Statistics</h4>
            <div class="stat-row">
              <span class="stat-label">Total Cards:</span>
              <span class="stat-value" id="sidebar-total-cards">0</span>
            </div>
            <div class="stat-row">
              <span class="stat-label">Unique Cards:</span>
              <span class="stat-value" id="sidebar-unique-cards">0</span>
            </div>
            <div class="stat-row">
              <span class="stat-label">Commons:</span>
              <span class="stat-value" id="sidebar-commons">0</span>
            </div>
            <div class="stat-row">
              <span class="stat-label">Uncommons:</span>
              <span class="stat-value" id="sidebar-uncommons">0</span>
            </div>
            <div class="stat-row">
              <span class="stat-label">Rares:</span>
              <span class="stat-value" id="sidebar-rares">0</span>
            </div>
            <div class="stat-row">
              <span class="stat-label">Mythics:</span>
              <span class="stat-value" id="sidebar-mythics">0</span>
            </div>
            <div class="stat-row">
              <span class="stat-label">Collection Value:</span>
              <span class="stat-value" id="sidebar-collection-value">$0.00</span>
            </div>
          </div>

          <!-- Action Buttons -->
          <div class="sidebar-actions">
            <button id="import-csv-btn" class="btn btn-primary btn-full">
              Import CSV
            </button>
            <button id="import-clipboard-btn" class="btn btn-secondary btn-full">
              Import Clipboard
            </button>
            <button id="export-csv-btn" class="btn btn-secondary btn-full">
              Export CSV
            </button>
            <button id="add-card-btn" class="btn btn-secondary btn-full">
              Add Card
            </button>
          </div>
        </div>

        <!-- Main Content Area -->
        <div class="collection-main">
          <div class="collection-header">
            <div class="collection-title">
              <h2>Collection</h2>
              <span class="collection-count" id="collection-count">0 cards shown</span>
            </div>
          </div>

          <!-- Collection Content -->
          <div id="collection-content" class="collection-content">
            <div id="collection-grid" class="card-grid">
              <div class="loading-state">
                <div class="spinner"></div>
                <p>Loading your collection...</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    `;
  }

  private setupEventListeners(): void {
    // Search
    this.bindEvent('#collection-search', 'input', () => {
      clearTimeout(this.searchTimeout);
      this.searchTimeout = window.setTimeout(() => {
        this.applyFilters();
      }, 300);
    });

    // Clear search
    this.bindEvent('#clear-search', 'click', () => {
      const searchInput = this.element.querySelector('#collection-search') as HTMLInputElement;
      if (searchInput) {
        searchInput.value = '';
        this.applyFilters();
      }
    });

    // Color checkboxes
    this.element.querySelectorAll('.color-checkbox input').forEach(checkbox => {
      checkbox.addEventListener('change', () => {
        this.applyFilters();
      });
    });

    // Filter selects
    this.bindEvent('#type-filter', 'change', () => this.applyFilters());
    this.bindEvent('#rarity-filter', 'change', () => this.applyFilters());

    // Clear filters
    this.bindEvent('#clear-filters', 'click', () => {
      this.clearAllFilters();
    });

    // Action buttons
    this.bindEvent('#import-csv-btn', 'click', () => this.importCSV());
    this.bindEvent('#import-clipboard-btn', 'click', () => this.importClipboard());
    this.bindEvent('#export-csv-btn', 'click', () => this.exportCSV());
    this.bindEvent('#add-card-btn', 'click', () => this.addCard());
  }

  private searchTimeout: number = 0;

  setCollection(collection: Collection): void {
    this.collection = collection;
    this.filteredCards = [...collection.cards];
    this.applyFilters();
  }

  private applyFilters(): void {
    const searchTerm = (this.element.querySelector('#collection-search') as HTMLInputElement)?.value.toLowerCase() || '';
    const rarityFilter = (this.element.querySelector('#rarity-filter') as HTMLSelectElement)?.value || '';
    const typeFilter = (this.element.querySelector('#type-filter') as HTMLSelectElement)?.value || '';

    // Get selected colors
    const selectedColors: string[] = [];
    this.element.querySelectorAll('.color-checkbox input:checked').forEach(checkbox => {
      selectedColors.push((checkbox as HTMLInputElement).value);
    });

    this.filteredCards = this.collection.cards.filter(card => {
      const matchesSearch = !searchTerm || card.name.toLowerCase().includes(searchTerm);
      const matchesRarity = !rarityFilter || card.rarity === rarityFilter;
      const matchesType = !typeFilter || card.typeLine?.toLowerCase().includes(typeFilter);
      const matchesColor = selectedColors.length === 0 || 
        (card.colors && card.colors.some(color => selectedColors.includes(color)));

      return matchesSearch && matchesColor && matchesRarity && matchesType;
    });

    this.renderCards();
    this.updateStats();
  }

  private renderCards(): void {
    const grid = this.element.querySelector('#collection-grid');
    if (!grid) return;

    if (this.filteredCards.length === 0) {
      grid.innerHTML = `
        <div class="empty-state">
          <p>No cards match your current filters</p>
          <button class="btn btn-secondary" id="clear-filters-btn">Clear Filters</button>
        </div>
      `;
    } else {
      grid.innerHTML = this.filteredCards.map(card => `
        <div class="card-item" data-card-id="${card.id}">
          <div class="card-image-placeholder"></div>
          <div class="card-info">
            <div class="card-name">${card.name}</div>
            <div class="card-type">${card.typeLine || ''}</div>
            <div class="card-meta">
              <span class="card-rarity ${card.rarity}">${card.rarity || 'common'}</span>
              <span class="card-quantity">×${card.quantity || 1}</span>
            </div>
          </div>
        </div>
      `).join('');
    }
  }

  private updateStats(): void {
    const countElement = this.element.querySelector('#collection-count');
    if (countElement) {
      countElement.textContent = `${this.filteredCards.length} cards shown`;
    }

    // Update sidebar stats
    const totalElement = this.element.querySelector('#sidebar-total-cards');
    if (totalElement) totalElement.textContent = this.filteredCards.length.toString();
    
    const uniqueCards = new Set(this.filteredCards.map(card => card.name)).size;
    const uniqueElement = this.element.querySelector('#sidebar-unique-cards');
    if (uniqueElement) uniqueElement.textContent = uniqueCards.toString();
    
    const rarityCount = {
      common: this.filteredCards.filter(card => card.rarity === 'common').length,
      uncommon: this.filteredCards.filter(card => card.rarity === 'uncommon').length,
      rare: this.filteredCards.filter(card => card.rarity === 'rare').length,
      mythic: this.filteredCards.filter(card => card.rarity === 'mythic').length
    };
    
    const commonsElement = this.element.querySelector('#sidebar-commons');
    if (commonsElement) commonsElement.textContent = rarityCount.common.toString();
    
    const uncommonsElement = this.element.querySelector('#sidebar-uncommons');
    if (uncommonsElement) uncommonsElement.textContent = rarityCount.uncommon.toString();
    
    const raresElement = this.element.querySelector('#sidebar-rares');
    if (raresElement) raresElement.textContent = rarityCount.rare.toString();
    
    const mythicsElement = this.element.querySelector('#sidebar-mythics');
    if (mythicsElement) mythicsElement.textContent = rarityCount.mythic.toString();
    
    // Calculate collection value (simplified calculation)
    const collectionValue = this.filteredCards.reduce((total, card) => {
      // Basic price estimation based on rarity
      const priceEstimate = card.rarity === 'mythic' ? 5.00 :
                           card.rarity === 'rare' ? 1.50 :
                           card.rarity === 'uncommon' ? 0.25 : 0.10;
      const quantity = card.quantity ?? 1;
      return total + (priceEstimate * quantity);
    }, 0);
    
    const valueElement = this.element.querySelector('#sidebar-collection-value');
    if (valueElement) valueElement.textContent = `$${collectionValue.toFixed(2)}`;
  }

  private clearAllFilters(): void {
    const searchInput = this.element.querySelector('#collection-search') as HTMLInputElement;
    if (searchInput) searchInput.value = '';

    const typeFilter = this.element.querySelector('#type-filter') as HTMLSelectElement;
    if (typeFilter) typeFilter.value = '';

    const rarityFilter = this.element.querySelector('#rarity-filter') as HTMLSelectElement;
    if (rarityFilter) rarityFilter.value = '';

    this.element.querySelectorAll('.color-checkbox input').forEach(checkbox => {
      (checkbox as HTMLInputElement).checked = false;
    });

    this.applyFilters();
  }

  private importCSV(): void {
    // TODO: Implement CSV import
    console.log('Import CSV clicked');
  }

  private importClipboard(): void {
    // TODO: Implement clipboard import
    console.log('Import Clipboard clicked');
  }

  private exportCSV(): void {
    // TODO: Implement CSV export
    console.log('Export CSV clicked');
  }

  private addCard(): void {
    // TODO: Implement add card modal
    console.log('Add Card clicked');
  }
}
