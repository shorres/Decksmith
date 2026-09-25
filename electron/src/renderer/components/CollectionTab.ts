import { BaseComponent } from './BaseComponent';
import { CardDetailsModal } from './CardDetailsModal';
import { ScryfallAPI, CSVHandler, CardCache, type ParsedCard } from '../utils';
import { openModal, closeModal, setStatus, setCardCount, escapeHtml } from '../ui';
import type { Card, Collection } from '../types';

export class CollectionTab extends BaseComponent {
  private collection: Collection = { cards: [], lastModified: new Date().toISOString() };
  private filteredCards: Card[] = [];
  private searchTimeout: number = 0;
  private cardModal: CardDetailsModal;
  private selectionMode: boolean = false;
  private selectedCards: Set<string> = new Set();
  private nextCardId = 0;

  constructor() {
    super('#collection-tab');
    this.cardModal = new CardDetailsModal();
  }

  initialize(): void {
    if (this.initialized) return;
    
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
            <button id="import-csv-btn" class="btn btn-primary btn-full" onclick="window.app?.components?.collection?.importCSV?.();">
              Import CSV
            </button>
            <button id="import-clipboard-btn" class="btn btn-secondary btn-full" onclick="window.app?.components?.collection?.importClipboard?.();">
              Import Clipboard
            </button>
            <button id="export-csv-btn" class="btn btn-secondary btn-full" onclick="window.app?.components?.collection?.exportCSV?.();">
              Export CSV
            </button>
            <button id="add-card-btn" class="btn btn-secondary btn-full" onclick="window.app?.components?.collection?.addCard?.();">
              Add Card
            </button>
            <button id="refresh-cache-btn" class="btn btn-secondary btn-full" onclick="window.app?.components?.collection?.refreshCardData?.();" title="Update card information from Scryfall">
              🔄 Update Card Data
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
            <div class="collection-actions">
              <button id="toggle-selection-btn" class="btn btn-secondary" onclick="window.app?.components?.collection?.toggleSelectionMode?.();">
                Select Cards
              </button>
              <div id="bulk-actions" class="bulk-actions hidden">
                <button id="select-all-btn" class="btn btn-secondary" onclick="window.app?.components?.collection?.selectAll?.();">
                  Select All
                </button>
                <button id="deselect-all-btn" class="btn btn-secondary" onclick="window.app?.components?.collection?.deselectAll?.();">
                  Deselect All
                </button>
                <button id="delete-selected-btn" class="btn btn-danger" onclick="window.app?.components?.collection?.deleteSelected?.();">
                  Delete Selected (<span id="selected-count">0</span>)
                </button>
              </div>
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
    console.log('Setting up CollectionTab event listeners...');
    
    // Search functionality
    this.bindEvent('#collection-search', 'input', () => {
      clearTimeout(this.searchTimeout);
      this.searchTimeout = window.setTimeout(() => {
        console.log('Applying search filter');
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

    // Color checkboxes - use more reliable event binding
    this.setupColorFilters();

    // Filter selects - ensure they're bound after render
    this.bindEvent('#type-filter', 'change', () => {
      console.log('Type filter changed');
      this.applyFilters();
    });
    
    this.bindEvent('#rarity-filter', 'change', () => {
      console.log('Rarity filter changed');
      this.applyFilters();
    });

    // Clear filters button
    this.bindEvent('#clear-filters', 'click', () => {
      console.log('Clear all filters clicked');
      this.clearAllFilters();
    });

    // Action buttons - using onclick handlers for reliability
    console.log('CollectionTab event listeners setup complete');
  }

  private setupColorFilters(): void {
    // Set up color checkbox filters with proper event delegation
    const colorCheckboxes = this.element.querySelectorAll('.color-checkbox input[type="checkbox"]');
    colorCheckboxes.forEach(checkbox => {
      const input = checkbox as HTMLInputElement;
      input.addEventListener('change', (e) => {
        const target = e.target as HTMLInputElement;
        console.log(`Color filter ${target.value} ${target.checked ? 'enabled' : 'disabled'}`);
        this.applyFilters();
      });
    });
  }

  // Enhanced filter method with better color matching
  private applyFilters(): void {
    console.log('Applying filters...');
    
    const searchTerm = (this.element.querySelector('#collection-search') as HTMLInputElement)?.value.toLowerCase() || '';
    const rarityFilter = (this.element.querySelector('#rarity-filter') as HTMLSelectElement)?.value || '';
    const typeFilter = (this.element.querySelector('#type-filter') as HTMLSelectElement)?.value || '';

    // Get selected colors
    const selectedColors: string[] = [];
    this.element.querySelectorAll('.color-checkbox input:checked').forEach(checkbox => {
      selectedColors.push((checkbox as HTMLInputElement).value);
    });

    console.log('Filter criteria:', { searchTerm, selectedColors, rarityFilter, typeFilter });

    this.filteredCards = this.collection.cards.filter(card => {
      // Search filter - check name and type
      const matchesSearch = !searchTerm || 
        card.name.toLowerCase().includes(searchTerm) ||
        (card.typeLine && card.typeLine.toLowerCase().includes(searchTerm));

      // Rarity filter
      const matchesRarity = !rarityFilter || card.rarity === rarityFilter;

      // Type filter - more flexible matching
      const matchesType = !typeFilter || 
        (card.typeLine && card.typeLine.toLowerCase().includes(typeFilter.toLowerCase()));

      // Color filter - improved logic
      const matchesColor = selectedColors.length === 0 || this.cardMatchesColors(card, selectedColors);

      const matches = matchesSearch && matchesColor && matchesRarity && matchesType;
      return matches;
    });

    console.log(`Filtered ${this.filteredCards.length} cards from ${this.collection.cards.length} total`);

    this.renderCards();
    this.updateStats();
  }

  // Forward-thinking color matching method that could be reused by other tabs
  private cardMatchesColors(card: Card, selectedColors: string[]): boolean {
    if (!card.colors || card.colors.length === 0) {
      // Colorless cards - could add a specific colorless filter later
      return selectedColors.length === 0;
    }

    // Check if card contains any of the selected colors
    // This allows for flexible color filtering
    return card.colors.some(color => selectedColors.includes(color));
  }

  // Public method to set collection data (can be called from other components)
  setCollection(collection: Collection): void {
    this.collection = collection;
    this.filteredCards = [...collection.cards];
    this.applyFilters();
  }

  getCollection(): Collection {
    return this.collection;
  }

  // Replaces the collection with an empty one (File > New Collection)
  async newCollection(): Promise<void> {
    if (this.collection.cards.length > 0 &&
        !confirm(`Start a new, empty collection? This removes all ${this.collection.cards.length} cards currently in your collection.`)) {
      return;
    }

    this.setCollection({ cards: [], lastModified: new Date().toISOString() });
    await this.saveCollection();
    setStatus('New collection created');
  }

  private renderCards(): void {
    const grid = this.element.querySelector('#collection-grid');
    if (!grid) return;

    if (this.filteredCards.length === 0) {
      grid.innerHTML = `
        <div class="empty-state">
          <p>No cards match your current filters</p>
          <button class="btn btn-secondary" id="clear-filters-btn" onclick="window.app?.components?.collection?.clearAllFilters?.();">Clear Filters</button>
        </div>
      `;
    } else {
      grid.innerHTML = this.filteredCards.map(card => {
        const imageUrl = this.getCardImageUrl(card.name);
        const name = escapeHtml(card.name);
        const typeLine = escapeHtml(card.typeLine);
        const isSelected = this.selectedCards.has(card.id);
        const selectionClass = isSelected ? 'selected' : '';
        const selectionModeClass = this.selectionMode ? 'selection-mode' : '';
        
        return `
          <div class="card-item ${selectionClass} ${selectionModeClass}" data-card-id="${card.id}">
            ${this.selectionMode ? `
              <div class="card-checkbox-wrapper">
                <input type="checkbox" class="card-checkbox" data-card-id="${card.id}" ${isSelected ? 'checked' : ''} 
                       onclick="event.stopPropagation(); window.app?.components?.collection?.toggleCardSelection?.('${card.id}');" />
              </div>
            ` : ''}
            <div class="card-content" onclick="window.app?.components?.collection?.${this.selectionMode ? `toggleCardSelection?.('${card.id}')` : `showCardDetails?.('${card.id}')`};">
              <div class="card-image-container">
                ${imageUrl ? 
                  `<img class="card-image" src="${imageUrl}" alt="${name}"
                       onerror="this.style.display='none'; this.nextElementSibling.style.display='flex';" />
                   <div class="card-image-placeholder" style="display: none;">
                     <div class="placeholder-content">
                       <span class="placeholder-icon">🃏</span>
                       <span class="placeholder-text">${name}</span>
                     </div>
                   </div>` :
                  `<div class="card-image-placeholder">
                     <div class="placeholder-content">
                       <span class="placeholder-icon">🃏</span>
                       <span class="placeholder-text">${name}</span>
                     </div>
                   </div>`}
              </div>
              <div class="card-info">
                <div class="card-name" title="${name}">${name}</div>
                <div class="card-type" title="${typeLine}">${typeLine || 'Unknown'}</div>
                <div class="card-meta">
                  <span class="card-rarity ${escapeHtml(card.rarity || 'common')}">${this.formatRarity(card.rarity || 'common')}</span>
                  <span class="card-quantity">×${card.quantity || 1}</span>
                  ${card.manaCost ? `<span class="mana-cost" title="Mana Cost">${escapeHtml(card.manaCost)}</span>` : ''}
                </div>
                ${card.colors && card.colors.length > 0 ? 
                  `<div class="card-colors">
                     ${card.colors.map(color => `<span class="color-pip color-${color.toLowerCase()}">${color}</span>`).join('')}
                   </div>` : ''}
              </div>
            </div>
          </div>
        `;
      }).join('');
    }
  }

  private getCardImageUrl(cardName: string): string | null {
    if (!cardName) return null;
    
    // Use Scryfall's image API - this will get the small image for performance
    // Format: https://api.scryfall.com/cards/named?exact={name}&format=image&version=small
    const encodedName = encodeURIComponent(cardName);
    return `https://api.scryfall.com/cards/named?exact=${encodedName}&format=image&version=small`;
  }

  private formatRarity(rarity: string): string {
    switch (rarity.toLowerCase()) {
      case 'common': return 'C';
      case 'uncommon': return 'U';
      case 'rare': return 'R';  
      case 'mythic': return 'M';
      default: return 'C';
    }
  }

  showCardDetails(cardId: string): void {
    const card = this.collection.cards.find(c => c.id === cardId);
    if (!card) return;

    console.log('Showing card details for:', card.name);
    
    // Open the card details modal
    this.cardModal.show(card.name);
  }

  private updateStats(): void {
    const countElement = this.element.querySelector('#collection-count');
    if (countElement) {
      countElement.textContent = `${this.filteredCards.length} cards shown`;
    }

    // Update sidebar stats
    const totalCards = this.filteredCards.reduce((sum, card) => sum + (card.quantity || 1), 0);
    const totalElement = this.element.querySelector('#sidebar-total-cards');
    if (totalElement) totalElement.textContent = totalCards.toString();

    setCardCount(this.collection.cards.reduce((sum, card) => sum + (card.quantity || 1), 0));
    
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

  clearAllFilters(): void {
    console.log('Clearing all filters');
    
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

  async importCSV(): Promise<void> {
    try {
      const result = await window.electronAPI?.openTextFile({
        title: 'Import Collection CSV',
        filters: [
          { name: 'CSV Files', extensions: ['csv'] },
          { name: 'All Files', extensions: ['*'] }
        ]
      });
      if (!result || result.canceled || result.content === undefined) return;

      const parsed = CSVHandler.parseCollectionCSV(result.content);
      if (parsed.length === 0) {
        setStatus('No cards found in that CSV file');
        return;
      }

      parsed.forEach(card => this.addOrMergeCard(card));
      await this.commitCollectionChanges(`Imported ${parsed.length} card entries from CSV`);
    } catch (error) {
      console.error('Error importing CSV:', error);
      setStatus('Error importing CSV file');
    }
  }

  async exportCSV(): Promise<void> {
    try {
      const result = await window.electronAPI?.saveTextFile({
        title: 'Export Collection to CSV',
        defaultPath: `collection-export-${new Date().toISOString().split('T')[0]}.csv`,
        filters: [
          { name: 'CSV Files', extensions: ['csv'] },
          { name: 'All Files', extensions: ['*'] }
        ],
        content: CSVHandler.exportCollectionToCSV(this.collection.cards)
      });

      if (result && !result.canceled) {
        setStatus(`Exported ${this.collection.cards.length} cards to ${result.filePath}`);
      }
    } catch (error) {
      console.error('Error exporting CSV:', error);
      setStatus('Error exporting CSV file');
    }
  }

  private async importClipboard(): Promise<void> {
    try {
      const clipboardText = await navigator.clipboard.readText();
      if (!clipboardText.trim()) {
        setStatus('Clipboard is empty');
        return;
      }

      // Accepts deck-list style lines: "4 Lightning Bolt" or "Lightning Bolt"
      const parsed = CSVHandler.parseArenaFormat(clipboardText);
      parsed.forEach(({ sideboard, ...card }) => this.addOrMergeCard(card));
      await this.commitCollectionChanges(`Added ${parsed.length} card entries from clipboard`);
    } catch (error) {
      console.error('Error importing from clipboard:', error);
      setStatus('Error reading clipboard');
    }
  }

  private async refreshCardData(): Promise<void> {
    try {
      const statsBefore = CardCache.getCacheStats();

      const confirmMsg = `This will update card information from Scryfall for all cards in your collection.\n\n` +
                        `Current cache: ${statsBefore.cardCount} cards, ${statsBefore.priceCount} prices\n` +
                        `Cache expiry: Cards (${statsBefore.cardExpiry}), Prices (${statsBefore.priceExpiry})\n\n` +
                        `This may take a few minutes. Continue?`;

      if (!confirm(confirmMsg)) {
        return;
      }

      setStatus('Updating card data from Scryfall...', false);

      // Invalidate all caches to force refresh
      CardCache.invalidateCache();

      let updatedCount = 0;
      const uniqueCards = Array.from(new Set(this.collection.cards.map(c => c.name)));

      for (const cardName of uniqueCards) {
        try {
          await ScryfallAPI.getCardByName(cardName, true);
          updatedCount++;

          if (updatedCount % 10 === 0) {
            setStatus(`Updating... ${updatedCount}/${uniqueCards.length} cards`, false);
          }
        } catch (error) {
          console.error(`Error updating ${cardName}:`, error);
        }
      }

      const statsAfter = CardCache.getCacheStats();
      setStatus(`✓ Updated ${updatedCount} cards! Cache now contains ${statsAfter.cardCount} cards, ${statsAfter.priceCount} prices.`);
    } catch (error) {
      console.error('Error refreshing card data:', error);
      setStatus('Error updating card data');
    }
  }

  private addCard(): void {
    const modalHtml = `
      <div class="add-card-modal">
        <form id="add-card-form">
          <div class="form-group">
            <label for="card-name-input">Card Name:</label>
            <input type="text" id="card-name-input" required placeholder="Enter card name" autocomplete="off">
            <div id="card-suggestions" class="suggestions-dropdown"></div>
          </div>
          <div class="form-group">
            <label for="card-quantity-input">Quantity:</label>
            <input type="number" id="card-quantity-input" value="1" min="1" required>
          </div>
          <div class="form-group">
            <label for="card-type-input">Type (optional):</label>
            <input type="text" id="card-type-input" placeholder="e.g., Creature, Instant, etc.">
          </div>
          <div class="form-group">
            <label for="card-mana-cost-input">Mana Cost (optional):</label>
            <input type="text" id="card-mana-cost-input" placeholder="e.g., {2}{R}, {U}{U}">
          </div>
          <div class="form-group">
            <label for="card-rarity-input">Rarity:</label>
            <select id="card-rarity-input">
              <option value="common">Common</option>
              <option value="uncommon">Uncommon</option>
              <option value="rare">Rare</option>
              <option value="mythic">Mythic Rare</option>
            </select>
          </div>
          <div class="modal-actions">
            <button type="button" class="btn btn-secondary" id="cancel-add-card">Cancel</button>
            <button type="submit" class="btn btn-primary">Add Card</button>
          </div>
        </form>
      </div>
    `;

    // The document-level listener added for autocomplete is removed when the modal closes
    let removeAutocompleteListener: (() => void) | undefined;
    openModal('Add Card', modalHtml, () => removeAutocompleteListener?.());

    const form = document.getElementById('add-card-form') as HTMLFormElement;
    const cancelBtn = document.getElementById('cancel-add-card') as HTMLButtonElement;
    const nameInput = document.getElementById('card-name-input') as HTMLInputElement;

    setTimeout(() => nameInput?.focus(), 100);

    removeAutocompleteListener = this.setupCardNameAutocomplete(nameInput);

    cancelBtn?.addEventListener('click', () => closeModal());

    form?.addEventListener('submit', (e) => {
      e.preventDefault();
      this.handleAddCardSubmit();
    });
  }

  // Wires up autocomplete on the name input. Returns a function that removes the document-level listener.
  private setupCardNameAutocomplete(input: HTMLInputElement): (() => void) | undefined {
    const suggestionsContainer = document.getElementById('card-suggestions') as HTMLElement;
    if (!input || !suggestionsContainer) return undefined;

    let searchTimeout: number;

    input.addEventListener('input', () => {
      clearTimeout(searchTimeout);
      const query = input.value.trim();

      if (query.length < 2) {
        this.hideSuggestions(suggestionsContainer);
        return;
      }

      searchTimeout = window.setTimeout(async () => {
        const suggestions = await ScryfallAPI.autocompleteCard(query);
        if (suggestions.length > 0) {
          this.displaySuggestions(suggestions.slice(0, 8), suggestionsContainer, input);
        } else {
          this.hideSuggestions(suggestionsContainer);
        }
      }, 300);
    });

    input.addEventListener('keydown', (e) => {
      this.handleSuggestionNavigation(e, suggestionsContainer, input);
    });

    // Hide suggestions when clicking outside
    const onDocumentClick = (e: MouseEvent) => {
      if (!input.contains(e.target as Node) && !suggestionsContainer.contains(e.target as Node)) {
        this.hideSuggestions(suggestionsContainer);
      }
    };
    document.addEventListener('click', onDocumentClick);
    return () => document.removeEventListener('click', onDocumentClick);
  }

  private displaySuggestions(suggestions: string[], container: HTMLElement, input: HTMLInputElement): void {
    container.innerHTML = '';
    container.style.display = 'block';

    suggestions.forEach((suggestion, index) => {
      const item = document.createElement('div');
      item.className = 'suggestion-item';
      item.textContent = suggestion;
      item.setAttribute('data-index', index.toString());

      item.addEventListener('click', () => {
        this.selectSuggestion(suggestion, container, input);
      });

      container.appendChild(item);
    });
  }

  private hideSuggestions(container: HTMLElement): void {
    if (container) {
      container.innerHTML = '';
      container.style.display = 'none';
    }
  }

  private selectSuggestion(suggestion: string, container: HTMLElement, input: HTMLInputElement): void {
    input.value = suggestion;
    this.hideSuggestions(container);

    // Automatically fetch and populate card details
    this.populateCardDetails(suggestion);
  }

  private handleSuggestionNavigation(e: KeyboardEvent, container: HTMLElement, input: HTMLInputElement): void {
    const suggestions = container.querySelectorAll('.suggestion-item');
    const currentActive = container.querySelector('.suggestion-item.active');

    if (e.key === 'ArrowDown') {
      e.preventDefault();
      const nextIndex = currentActive ?
        Math.min(parseInt(currentActive.getAttribute('data-index') || '0') + 1, suggestions.length - 1) : 0;
      this.setActiveSuggestion(suggestions, nextIndex);
    } else if (e.key === 'ArrowUp') {
      e.preventDefault();
      const prevIndex = currentActive ?
        Math.max(parseInt(currentActive.getAttribute('data-index') || '0') - 1, 0) : suggestions.length - 1;
      this.setActiveSuggestion(suggestions, prevIndex);
    } else if (e.key === 'Enter' && currentActive) {
      e.preventDefault();
      this.selectSuggestion(currentActive.textContent || '', container, input);
    } else if (e.key === 'Escape') {
      this.hideSuggestions(container);
    }
  }

  private setActiveSuggestion(suggestions: NodeListOf<Element>, index: number): void {
    suggestions.forEach(s => s.classList.remove('active'));
    if (suggestions[index]) {
      suggestions[index].classList.add('active');
    }
  }

  private async populateCardDetails(cardName: string): Promise<void> {
    try {
      const card = await ScryfallAPI.getCard(cardName);
      if (!card) return;

      const typeInput = document.getElementById('card-type-input') as HTMLInputElement;
      const manaCostInput = document.getElementById('card-mana-cost-input') as HTMLInputElement;
      const rarityInput = document.getElementById('card-rarity-input') as HTMLSelectElement;

      if (typeInput && card.typeLine) typeInput.value = card.typeLine;
      if (manaCostInput && card.manaCost) manaCostInput.value = card.manaCost;
      // Only set rarities the dropdown offers (Scryfall also has "special" and "bonus")
      if (rarityInput && card.rarity && rarityInput.querySelector(`option[value="${card.rarity}"]`)) {
        rarityInput.value = card.rarity;
      }
    } catch (error) {
      // Not fatal - the user can still fill in the fields manually
      console.error('Error fetching card details:', error);
    }
  }

  private async handleAddCardSubmit(): Promise<void> {
    const nameInput = document.getElementById('card-name-input') as HTMLInputElement;
    const quantityInput = document.getElementById('card-quantity-input') as HTMLInputElement;
    const typeInput = document.getElementById('card-type-input') as HTMLInputElement;
    const manaCostInput = document.getElementById('card-mana-cost-input') as HTMLInputElement;
    const rarityInput = document.getElementById('card-rarity-input') as HTMLSelectElement;

    const cardName = nameInput?.value?.trim();
    const quantity = parseInt(quantityInput?.value || '1');

    if (!cardName) {
      alert('Card name is required');
      return;
    }

    if (isNaN(quantity) || quantity < 1) {
      alert('Invalid quantity');
      return;
    }

    this.addOrMergeCard({
      name: cardName,
      quantity,
      typeLine: typeInput?.value?.trim() || undefined,
      manaCost: manaCostInput?.value?.trim() || undefined,
      rarity: rarityInput?.value || undefined
    });

    closeModal();
    const total = this.collection.cards.find(c => c.name.toLowerCase() === cardName.toLowerCase())?.quantity ?? quantity;
    await this.commitCollectionChanges(
      total > quantity ? `Added ${quantity}x ${cardName} (now ${total} total)` : `Added ${quantity}x ${cardName}`
    );
  }

  // Adds a card to the collection, or increases the quantity if a card with that name already exists.
  // Callers should follow up with commitCollectionChanges().
  private addOrMergeCard(entry: ParsedCard): void {
    const existingCard = this.collection.cards.find(c => c.name.toLowerCase() === entry.name.toLowerCase());
    if (existingCard) {
      existingCard.quantity = (existingCard.quantity || 1) + entry.quantity;
      return;
    }

    this.collection.cards.push({
      ...entry,
      id: `card-${Date.now()}-${this.nextCardId++}`,
      typeLine: entry.typeLine || 'Unknown',
      manaCost: entry.manaCost || '',
      colors: entry.colors ?? ['W', 'U', 'B', 'R', 'G'].filter(color => entry.manaCost?.includes(color)),
      rarity: entry.rarity || 'common'
    });
  }

  // Re-renders, persists and reports after the collection has been modified
  private async commitCollectionChanges(statusMessage: string): Promise<void> {
    this.setCollection(this.collection);
    await this.saveCollection();
    setStatus(statusMessage);
  }

  // Enhanced loading method with better UX
  async loadCollectionData(): Promise<void> {
    try {
      console.log('Loading collection data...');
      
      // Show loading state
      const grid = this.element.querySelector('#collection-grid');
      if (grid) {
        grid.innerHTML = `
          <div class="loading-state">
            <div class="spinner"></div>
            <p>Loading your collection...</p>
          </div>
        `;
      }

      // Load from storage
      const savedCollection = await window.electronAPI?.store.get('collection');
      
      if (savedCollection && savedCollection.cards) {
        console.log(`Loaded ${savedCollection.cards.length} cards from storage`);
        this.setCollection(savedCollection);
      } else {
        console.log('No existing collection found, creating sample data for testing');
        const sampleCollection = this.createSampleCollection();
        this.setCollection(sampleCollection);
        // Save the sample data
        await this.saveCollection();
      }
      
    } catch (error) {
      console.error('Error loading collection data:', error);
      
      // Show error state
      const grid = this.element.querySelector('#collection-grid');
      if (grid) {
        grid.innerHTML = `
          <div class="error-state">
            <p>⚠️ Error loading collection</p>
            <button class="btn btn-secondary" onclick="window.app?.components?.collection?.loadCollectionData?.();">
              Retry
            </button>
          </div>
        `;
      }
    }
  }

  private async saveCollection(): Promise<void> {
    try {
      this.collection.lastModified = new Date().toISOString();
      await window.electronAPI?.store.set('collection', this.collection);
      console.log('Collection saved successfully');
    } catch (error) {
      console.error('Error saving collection:', error);
    }
  }

  // Create sample collection for testing/demonstration
  private createSampleCollection(): Collection {
    return {
      cards: [
        {
          id: 'sample-1',
          name: 'Lightning Bolt',
          typeLine: 'Instant',
          manaCost: '{R}',
          colors: ['R'],
          rarity: 'common',
          quantity: 4
        },
        {
          id: 'sample-2',
          name: 'Counterspell',
          typeLine: 'Instant',
          manaCost: '{U}{U}',
          colors: ['U'],
          rarity: 'common',
          quantity: 3
        },
        {
          id: 'sample-3',
          name: 'Black Lotus',
          typeLine: 'Artifact',
          manaCost: '{0}',
          colors: [],
          rarity: 'mythic',
          quantity: 1
        },
        {
          id: 'sample-4',
          name: 'Serra Angel',
          typeLine: 'Creature — Angel',
          manaCost: '{3}{W}{W}',
          colors: ['W'],
          rarity: 'uncommon',
          quantity: 2
        },
        {
          id: 'sample-5',
          name: 'Forest',
          typeLine: 'Basic Land — Forest',
          manaCost: '',
          colors: [],
          rarity: 'common',
          quantity: 10
        },
        {
          id: 'sample-6',
          name: 'Jace, the Mind Sculptor',
          typeLine: 'Legendary Planeswalker — Jace',
          manaCost: '{2}{U}{U}',
          colors: ['U'],
          rarity: 'mythic',
          quantity: 1
        },
        {
          id: 'sample-7',
          name: 'Sol Ring',
          typeLine: 'Artifact',
          manaCost: '{1}',
          colors: [],
          rarity: 'uncommon',
          quantity: 1
        },
        {
          id: 'sample-8',
          name: 'Llanowar Elves',
          typeLine: 'Creature — Elf Druid',
          manaCost: '{G}',
          colors: ['G'],
          rarity: 'common',
          quantity: 4
        }
      ],
      lastModified: new Date().toISOString()
    };
  }

  // Selection and deletion methods
  toggleSelectionMode(): void {
    this.selectionMode = !this.selectionMode;
    
    if (!this.selectionMode) {
      // Clear selections when exiting selection mode
      this.selectedCards.clear();
    }
    
    // Update button text
    const toggleBtn = this.element.querySelector('#toggle-selection-btn');
    if (toggleBtn) {
      toggleBtn.textContent = this.selectionMode ? 'Cancel Selection' : 'Select Cards';
    }
    
    // Show/hide bulk actions
    const bulkActions = this.element.querySelector('#bulk-actions');
    if (bulkActions) {
      if (this.selectionMode) {
        bulkActions.classList.remove('hidden');
      } else {
        bulkActions.classList.add('hidden');
      }
    }
    
    // Re-render cards to show/hide checkboxes
    this.renderCards();
    this.updateSelectionCount();
  }

  toggleCardSelection(cardId: string): void {
    if (this.selectedCards.has(cardId)) {
      this.selectedCards.delete(cardId);
    } else {
      this.selectedCards.add(cardId);
    }
    
    // Update the checkbox state and card styling
    const cardElement = this.element.querySelector(`.card-item[data-card-id="${cardId}"]`);
    const checkbox = this.element.querySelector(`.card-checkbox[data-card-id="${cardId}"]`) as HTMLInputElement;
    
    if (cardElement) {
      if (this.selectedCards.has(cardId)) {
        cardElement.classList.add('selected');
      } else {
        cardElement.classList.remove('selected');
      }
    }
    
    if (checkbox) {
      checkbox.checked = this.selectedCards.has(cardId);
    }
    
    this.updateSelectionCount();
  }

  selectAll(): void {
    this.filteredCards.forEach(card => {
      this.selectedCards.add(card.id);
    });
    this.renderCards();
    this.updateSelectionCount();
  }

  deselectAll(): void {
    this.selectedCards.clear();
    this.renderCards();
    this.updateSelectionCount();
  }

  private updateSelectionCount(): void {
    const countElement = this.element.querySelector('#selected-count');
    if (countElement) {
      countElement.textContent = this.selectedCards.size.toString();
    }
  }

  async deleteSelected(): Promise<void> {
    if (this.selectedCards.size === 0) {
      alert('No cards selected');
      return;
    }

    const deletedCount = this.selectedCards.size;
    const cardNames = Array.from(this.selectedCards)
      .map(id => this.collection.cards.find(c => c.id === id)?.name)
      .filter(name => name)
      .slice(0, 5);
    
    const moreText = this.selectedCards.size > 5 ? `\n...and ${this.selectedCards.size - 5} more` : '';
    const confirmMessage = `Are you sure you want to delete ${this.selectedCards.size} card(s)?\n\n${cardNames.join('\n')}${moreText}`;
    
    if (!confirm(confirmMessage)) {
      return;
    }

    // Delete selected cards
    this.collection.cards = this.collection.cards.filter(card => !this.selectedCards.has(card.id));
    
    // Clear selection
    this.selectedCards.clear();
    
    // Save and refresh
    await this.saveCollection();
    this.setCollection(this.collection);
    
    // Exit selection mode
    this.toggleSelectionMode();
    
    setStatus(`Deleted ${deletedCount} card(s)`);
  }
}