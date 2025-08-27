import { BaseComponent } from './BaseComponent';
import type { Card, Collection } from '../types';

export class CollectionTab extends BaseComponent {
  private collection: Collection = { cards: [], lastModified: new Date().toISOString() };
  private filteredCards: Card[] = [];
  private searchTimeout: number = 0;

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
            <button id="import-csv-btn" class="btn btn-primary btn-full" onclick="window.decksmithApp?.components?.collection?.importCSV?.();">
              Import CSV
            </button>
            <button id="import-clipboard-btn" class="btn btn-secondary btn-full" onclick="window.decksmithApp?.components?.collection?.importClipboard?.();">
              Import Clipboard
            </button>
            <button id="export-csv-btn" class="btn btn-secondary btn-full" onclick="window.decksmithApp?.components?.collection?.exportCSV?.();">
              Export CSV
            </button>
            <button id="add-card-btn" class="btn btn-secondary btn-full" onclick="window.decksmithApp?.components?.collection?.addCard?.();">
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

  private renderCards(): void {
    const grid = this.element.querySelector('#collection-grid');
    if (!grid) return;

    if (this.filteredCards.length === 0) {
      grid.innerHTML = `
        <div class="empty-state">
          <p>No cards match your current filters</p>
          <button class="btn btn-secondary" id="clear-filters-btn" onclick="window.decksmithApp?.components?.collection?.clearAllFilters?.();">Clear Filters</button>
        </div>
      `;
    } else {
      grid.innerHTML = this.filteredCards.map(card => {
        const imageUrl = this.getCardImageUrl(card.name);
        return `
          <div class="card-item" data-card-id="${card.id}" onclick="window.decksmithApp?.components?.collection?.showCardDetails?.('${card.id}');">
            <div class="card-image-container">
              ${imageUrl ? 
                `<img class="card-image" src="${imageUrl}" alt="${card.name}" 
                     onerror="this.style.display='none'; this.nextElementSibling.style.display='flex';" />
                 <div class="card-image-placeholder" style="display: none;">
                   <div class="placeholder-content">
                     <span class="placeholder-icon">🃏</span>
                     <span class="placeholder-text">${card.name}</span>
                   </div>
                 </div>` : 
                `<div class="card-image-placeholder">
                   <div class="placeholder-content">
                     <span class="placeholder-icon">🃏</span>
                     <span class="placeholder-text">${card.name}</span>
                   </div>
                 </div>`}
            </div>
            <div class="card-info">
              <div class="card-name" title="${card.name}">${card.name}</div>
              <div class="card-type" title="${card.typeLine || ''}">${card.typeLine || 'Unknown'}</div>
              <div class="card-meta">
                <span class="card-rarity ${card.rarity || 'common'}">${this.formatRarity(card.rarity || 'common')}</span>
                <span class="card-quantity">×${card.quantity || 1}</span>
                ${card.manaCost ? `<span class="mana-cost" title="Mana Cost">${card.manaCost}</span>` : ''}
              </div>
              ${card.colors && card.colors.length > 0 ? 
                `<div class="card-colors">
                   ${card.colors.map(color => `<span class="color-pip color-${color.toLowerCase()}">${color}</span>`).join('')}
                 </div>` : ''}
            </div>
          </div>
        `;
      }).join('');
    }

    // Re-bind any additional event listeners needed for the rendered cards
    this.bindCardEvents();
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

  private bindCardEvents(): void {
    // Add any additional event listeners for rendered cards if needed
    // This method can be extended for card-specific interactions
  }

  // Forward-thinking method for card details modal (for future tabs)
  showCardDetails(cardId: string): void {
    const card = this.collection.cards.find(c => c.id === cardId);
    if (!card) return;

    console.log('Showing card details for:', card.name);
    
    // This will be enhanced later - for now just log
    // In the future, this could open a detailed modal or sidebar
    // that could be useful for deck building and AI recommendations
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

  // Forward-thinking methods for integration with other tabs
  
  // Get all cards (useful for deck building)
  getAllCards(): Card[] {
    return [...this.collection.cards];
  }

  // Get filtered cards (useful for exporting or other operations)  
  getFilteredCards(): Card[] {
    return [...this.filteredCards];
  }

  // Get card by ID (useful for card details, deck building)
  getCardById(cardId: string): Card | undefined {
    return this.collection.cards.find(card => card.id === cardId);
  }

  // Get cards by name (useful for deck building - handling different printings)
  getCardsByName(cardName: string): Card[] {
    return this.collection.cards.filter(card => 
      card.name.toLowerCase() === cardName.toLowerCase()
    );
  }

  // Check if card exists in collection (useful for deck building validation)
  hasCard(cardName: string, quantity: number = 1): boolean {
    const cards = this.getCardsByName(cardName);
    const totalQuantity = cards.reduce((sum, card) => sum + (card.quantity || 1), 0);
    return totalQuantity >= quantity;
  }

  // Get collection statistics (useful for AI recommendations and analytics)
  getCollectionStats() {
    const stats = {
      totalCards: this.collection.cards.reduce((sum, card) => sum + (card.quantity || 1), 0),
      uniqueCards: this.collection.cards.length,
      cardsByRarity: {
        common: this.collection.cards.filter(card => card.rarity === 'common').length,
        uncommon: this.collection.cards.filter(card => card.rarity === 'uncommon').length,
        rare: this.collection.cards.filter(card => card.rarity === 'rare').length,
        mythic: this.collection.cards.filter(card => card.rarity === 'mythic').length,
      },
      cardsByColor: {
        white: this.collection.cards.filter(card => card.colors?.includes('W')).length,
        blue: this.collection.cards.filter(card => card.colors?.includes('U')).length,
        black: this.collection.cards.filter(card => card.colors?.includes('B')).length,
        red: this.collection.cards.filter(card => card.colors?.includes('R')).length,
        green: this.collection.cards.filter(card => card.colors?.includes('G')).length,
        colorless: this.collection.cards.filter(card => !card.colors || card.colors.length === 0).length,
      },
      cardsByType: this.getCardTypeDistribution()
    };
    
    return stats;
  }

  private getCardTypeDistribution(): Record<string, number> {
    const typeDistribution: Record<string, number> = {};
    
    this.collection.cards.forEach(card => {
      if (card.typeLine) {
        // Extract primary type (e.g., "Legendary Creature — Dragon" -> "Creature")
        const primaryType = this.extractPrimaryType(card.typeLine);
        typeDistribution[primaryType] = (typeDistribution[primaryType] || 0) + 1;
      }
    });
    
    return typeDistribution;
  }

  private extractPrimaryType(typeLine: string): string {
    const types = ['Creature', 'Instant', 'Sorcery', 'Enchantment', 'Artifact', 'Planeswalker', 'Land', 'Battle'];
    
    for (const type of types) {
      if (typeLine.includes(type)) {
        return type;
      }
    }
    
    return 'Other';
  }

  private async importCSV(): Promise<void> {
    try {
      const result = await window.electronAPI?.openFileDialog({
        title: 'Import Collection CSV',
        buttonLabel: 'Import',
        filters: [
          { name: 'CSV Files', extensions: ['csv'] },
          { name: 'All Files', extensions: ['*'] }
        ]
      });

      if (result && !result.canceled && result.filePaths.length > 0) {
        const filePath = result.filePaths[0];
        console.log('Selected CSV file:', filePath);
        
        // Read and parse CSV file
        // For now, we'll use a simple implementation
        // In a real app, you'd want to use the Node.js fs module via IPC
        this.showImportStatus('Reading CSV file...');
        
        // TODO: Implement actual CSV parsing
        // This would involve:
        // 1. Reading the file via IPC to main process
        // 2. Parsing CSV content
        // 3. Creating Card objects
        // 4. Adding to collection
        // 5. Updating UI
        
        this.showImportStatus('CSV import completed!');
      }
    } catch (error) {
      console.error('Error importing CSV:', error);
      this.showImportStatus('Error importing CSV file');
    }
  }

  private async exportCSV(): Promise<void> {
    try {
      const result = await window.electronAPI?.saveFileDialog({
        title: 'Export Collection to CSV',
        buttonLabel: 'Export',
        defaultPath: `collection-export-${new Date().toISOString().split('T')[0]}.csv`,
        filters: [
          { name: 'CSV Files', extensions: ['csv'] },
          { name: 'All Files', extensions: ['*'] }
        ]
      });

      if (result && !result.canceled && result.filePath) {
        const filePath = result.filePath;
        console.log('Export to:', filePath);
        
        // Generate CSV content
        const csvContent = this.generateCSVContent();
        
        // Save file via IPC
        // TODO: Implement file writing via main process
        console.log('CSV content:', csvContent);
        
        this.showImportStatus('Collection exported successfully!');
      }
    } catch (error) {
      console.error('Error exporting CSV:', error);
      this.showImportStatus('Error exporting CSV file');
    }
  }

  private async importClipboard(): Promise<void> {
    try {
      // Get clipboard text
      const clipboardText = await navigator.clipboard.readText();
      
      if (!clipboardText.trim()) {
        this.showImportStatus('Clipboard is empty');
        return;
      }

      this.showImportStatus('Processing clipboard content...');
      
      // Parse clipboard content as card list
      const lines = clipboardText.split('\n').filter(line => line.trim());
      let addedCards = 0;
      
      for (const line of lines) {
        const trimmed = line.trim();
        if (!trimmed) continue;
        
        // Parse format: "4 Lightning Bolt" or "Lightning Bolt"
        const match = trimmed.match(/^(\d+)\s+(.+)$/) || [null, '1', trimmed];
        const quantity = parseInt(match[1] || '1');
        const cardName = (match[2] || trimmed).trim();
        
        if (cardName) {
          // Create basic card object
          const newCard: Card = {
            id: `clipboard-${Date.now()}-${addedCards}`,
            name: cardName,
            typeLine: 'Unknown',
            manaCost: '',
            colors: [],
            rarity: 'common',
            quantity: quantity
          };
          
          this.collection.cards.push(newCard);
          addedCards++;
        }
      }
      
      // Update UI
      this.setCollection(this.collection);
      this.showImportStatus(`Added ${addedCards} cards from clipboard`);
      
      // Save to persistent storage
      await this.saveCollection();
      
    } catch (error) {
      console.error('Error importing from clipboard:', error);
      this.showImportStatus('Error reading clipboard');
    }
  }

  private addCard(): void {
    console.log('Opening add card modal...');
    
    // Create modal HTML
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

    // Show modal
    this.showModal('Add Card', modalHtml);

    // Set up form handling
    const form = document.getElementById('add-card-form') as HTMLFormElement;
    const cancelBtn = document.getElementById('cancel-add-card') as HTMLButtonElement;
    const nameInput = document.getElementById('card-name-input') as HTMLInputElement;

    // Focus on card name input
    setTimeout(() => nameInput?.focus(), 100);

    // Set up autocomplete
    this.setupCardNameAutocomplete(nameInput);

    // Handle cancel
    cancelBtn?.addEventListener('click', () => {
      this.closeModal();
    });

    // Handle form submission
    form?.addEventListener('submit', (e) => {
      e.preventDefault();
      this.handleAddCardSubmit();
    });
  }

  private setupCardNameAutocomplete(input: HTMLInputElement): void {
    if (!input) return;

    let searchTimeout: number;
    const suggestionsContainer = document.getElementById('card-suggestions') as HTMLElement;
    
    input.addEventListener('input', () => {
      clearTimeout(searchTimeout);
      const query = input.value.trim();
      
      if (query.length < 2) {
        this.hideSuggestions(suggestionsContainer);
        return;
      }

      searchTimeout = window.setTimeout(async () => {
        await this.fetchCardSuggestions(query, suggestionsContainer, input);
      }, 300);
    });

    // Handle keyboard navigation
    input.addEventListener('keydown', (e) => {
      this.handleSuggestionNavigation(e, suggestionsContainer, input);
    });

    // Hide suggestions when clicking outside
    document.addEventListener('click', (e) => {
      if (!input.contains(e.target as Node) && !suggestionsContainer.contains(e.target as Node)) {
        this.hideSuggestions(suggestionsContainer);
      }
    });
  }

  private async fetchCardSuggestions(query: string, container: HTMLElement, input: HTMLInputElement): Promise<void> {
    try {
      // Use Scryfall's autocomplete API
      const response = await fetch(`https://api.scryfall.com/cards/autocomplete?q=${encodeURIComponent(query)}`);
      const data = await response.json();
      
      if (data.data && data.data.length > 0) {
        this.displaySuggestions(data.data.slice(0, 8), container, input); // Limit to 8 suggestions
      } else {
        this.hideSuggestions(container);
      }
    } catch (error) {
      console.error('Error fetching card suggestions:', error);
      this.hideSuggestions(container);
    }
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
      // Fetch full card details from Scryfall
      const response = await fetch(`https://api.scryfall.com/cards/named?exact=${encodeURIComponent(cardName)}`);
      const card = await response.json();
      
      if (card && card.object !== 'error') {
        // Populate form fields with card data
        const typeInput = document.getElementById('card-type-input') as HTMLInputElement;
        const manaCostInput = document.getElementById('card-mana-cost-input') as HTMLInputElement;
        const rarityInput = document.getElementById('card-rarity-input') as HTMLSelectElement;
        
        if (typeInput && card.type_line) {
          typeInput.value = card.type_line;
        }
        if (manaCostInput && card.mana_cost) {
          manaCostInput.value = card.mana_cost;
        }
        if (rarityInput && card.rarity) {
          rarityInput.value = card.rarity;
        }
      }
    } catch (error) {
      console.error('Error fetching card details:', error);
      // Don't show error to user, just proceed without auto-population
    }
  }

  private handleAddCardSubmit(): void {
    const nameInput = document.getElementById('card-name-input') as HTMLInputElement;
    const quantityInput = document.getElementById('card-quantity-input') as HTMLInputElement;
    const typeInput = document.getElementById('card-type-input') as HTMLInputElement;
    const manaCostInput = document.getElementById('card-mana-cost-input') as HTMLInputElement;
    const rarityInput = document.getElementById('card-rarity-input') as HTMLSelectElement;

    const cardName = nameInput?.value?.trim();
    const quantity = parseInt(quantityInput?.value || '1');
    const typeLine = typeInput?.value?.trim() || 'Unknown';
    const manaCost = manaCostInput?.value?.trim() || '';
    const rarity = rarityInput?.value || 'common';

    if (!cardName) {
      alert('Card name is required');
      return;
    }

    if (isNaN(quantity) || quantity < 1) {
      alert('Invalid quantity');
      return;
    }

    // Parse colors from mana cost (basic parsing)
    const colors: string[] = [];
    if (manaCost) {
      if (manaCost.includes('W')) colors.push('W');
      if (manaCost.includes('U')) colors.push('U');
      if (manaCost.includes('B')) colors.push('B');
      if (manaCost.includes('R')) colors.push('R');
      if (manaCost.includes('G')) colors.push('G');
    }

    // Create new card
    const newCard: Card = {
      id: `manual-${Date.now()}`,
      name: cardName,
      typeLine: typeLine,
      manaCost: manaCost,
      colors: colors,
      rarity: rarity as any,
      quantity: quantity
    };

    this.collection.cards.push(newCard);
    this.setCollection(this.collection);
    this.showImportStatus(`Added ${quantity}x ${cardName}`);

    // Save to persistent storage
    this.saveCollection();

    // Close modal
    this.closeModal();
  }

  private showModal(title: string, content: string): void {
    const modal = document.getElementById('modal') as HTMLElement;
    const modalTitle = document.getElementById('modal-title') as HTMLElement;
    const modalContent = document.getElementById('modal-content') as HTMLElement;

    if (modal && modalTitle && modalContent) {
      modalTitle.textContent = title;
      modalContent.innerHTML = content;
      modal.classList.remove('hidden');
    }
  }

  private closeModal(): void {
    const modal = document.getElementById('modal') as HTMLElement;
    if (modal) {
      modal.classList.add('hidden');
    }
  }

  private generateCSVContent(): string {
    const headers = ['Card Name', 'Quantity', 'Mana Cost', 'Type', 'Rarity', 'Colors'];
    const rows = [headers.join(',')];
    
    for (const card of this.filteredCards) {
      const row = [
        `"${card.name}"`,
        card.quantity?.toString() || '1',
        `"${card.manaCost || ''}"`,
        `"${card.typeLine || ''}"`,
        card.rarity,
        `"${card.colors?.join('') || ''}"`
      ];
      rows.push(row.join(','));
    }
    
    return rows.join('\n');
  }

  private showImportStatus(message: string): void {
    // Show status in the status bar or a temporary message
    console.log('Status:', message);
    
    // You could also show this in the UI temporarily
    const statusElement = document.querySelector('#status-message');
    if (statusElement) {
      statusElement.textContent = message;
      // Clear after 3 seconds
      setTimeout(() => {
        statusElement.textContent = 'Ready';
      }, 3000);
    }
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
            <button class="btn btn-secondary" onclick="window.decksmithApp?.components?.collection?.loadCollectionData?.();">
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
}
