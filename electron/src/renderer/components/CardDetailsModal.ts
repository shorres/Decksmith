import type { Card } from '../types';

export class CardDetailsModal {
  private modal: HTMLElement | null = null;
  private isLoading = false;

  constructor() {
    this.createModal();
  }

  private createModal(): void {
    const modal = document.createElement('div');
    modal.className = 'card-details-modal';
    modal.innerHTML = `
      <div class="card-details-content">
        <div class="card-details-header">
          <h3 id="card-modal-title">Card Details</h3>
          <button class="close-btn" id="close-card-modal">×</button>
        </div>
        <div class="card-details-body">
          <div class="card-details-left">
            <div class="card-image-container">
              <img id="card-modal-image" class="card-modal-image" alt="Card Image" />
              <div class="card-image-loading" id="card-image-loading">
                <div class="spinner"></div>
                <p>Loading image...</p>
              </div>
            </div>
            <div class="card-actions">
              <button class="btn btn-primary" id="add-to-deck-btn">Add to Deck</button>
              <input type="number" id="card-quantity-input" value="1" min="1" max="4" />
            </div>
          </div>
          <div class="card-details-right">
            <div class="card-info-section">
              <h4>Card Information</h4>
              <div class="card-info-grid">
                <div class="info-row">
                  <span class="info-label">Name:</span>
                  <span class="info-value" id="modal-card-name">-</span>
                </div>
                <div class="info-row">
                  <span class="info-label">Mana Cost:</span>
                  <span class="info-value" id="modal-card-mana">-</span>
                </div>
                <div class="info-row">
                  <span class="info-label">CMC:</span>
                  <span class="info-value" id="modal-card-cmc">-</span>
                </div>
                <div class="info-row">
                  <span class="info-label">Type Line:</span>
                  <span class="info-value" id="modal-card-type">-</span>
                </div>
                <div class="info-row">
                  <span class="info-label">Colors:</span>
                  <span class="info-value" id="modal-card-colors">-</span>
                </div>
                <div class="info-row">
                  <span class="info-label">Rarity:</span>
                  <span class="info-value" id="modal-card-rarity">-</span>
                </div>
                <div class="info-row">
                  <span class="info-label">Set:</span>
                  <span class="info-value" id="modal-card-set">-</span>
                </div>
                <div class="info-row">
                  <span class="info-label">Power/Toughness:</span>
                  <span class="info-value" id="modal-card-pt">-</span>
                </div>
              </div>
            </div>
            
            <div class="card-text-section">
              <h4>Oracle Text</h4>
              <div class="oracle-text" id="modal-oracle-text">
                Loading card data...
              </div>
            </div>
            
            <div class="card-legality-section">
              <h4>Format Legality</h4>
              <div class="legality-grid" id="modal-legality-grid">
                Loading...
              </div>
            </div>
            
            <div class="card-pricing-section">
              <h4>Pricing (USD)</h4>
              <div class="pricing-info" id="modal-pricing-info">
                Loading...
              </div>
            </div>
          </div>
        </div>
        <div class="card-details-footer">
          <button class="btn btn-secondary" id="view-on-scryfall">View on Scryfall</button>
          <button class="btn btn-secondary" id="close-card-modal-footer">Close</button>
        </div>
      </div>
    `;

    this.modal = modal;
    document.body.appendChild(modal);

    // Event listeners
    modal.querySelector('#close-card-modal')?.addEventListener('click', () => this.close());
    modal.querySelector('#close-card-modal-footer')?.addEventListener('click', () => this.close());
    modal.addEventListener('click', (e) => {
      if (e.target === modal) this.close();
    });

    // Hide initially
    modal.style.display = 'none';
  }

  async show(cardName: string): Promise<void> {
    if (this.isLoading || !this.modal) return;

    this.isLoading = true;
    this.modal.style.display = 'flex';

    // Reset content
    this.resetContent();
    
    // Set initial title
    const title = this.modal.querySelector('#card-modal-title');
    if (title) title.textContent = cardName;

    try {
      const cardData = await this.fetchCardData(cardName);
      if (cardData) {
        this.populateCardData(cardData);
      } else {
        this.showError('Card not found');
      }
    } catch (error) {
      console.error('Error fetching card data:', error);
      this.showError('Error loading card data');
    }

    this.isLoading = false;
  }

  private async fetchCardData(cardName: string): Promise<Card | null> {
    try {
      const encodedName = encodeURIComponent(cardName);
      const response = await fetch(`https://api.scryfall.com/cards/named?exact=${encodedName}`);
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const data = await response.json();
      
      // Transform Scryfall data to our Card interface
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
        legalities: data.legalities || {},
        prices: data.prices || {},
        scryfallUri: data.scryfall_uri || ''
      };
    } catch (error) {
      console.error('Error fetching from Scryfall:', error);
      return null;
    }
  }

  private populateCardData(card: Card): void {
    if (!this.modal) return;

    // Basic info
    this.setTextContent('#modal-card-name', card.name);
    this.setTextContent('#modal-card-mana', card.manaCost || 'None');
    this.setTextContent('#modal-card-cmc', card.cmc?.toString() || '0');
    this.setTextContent('#modal-card-type', card.typeLine || 'Unknown');
    this.setTextContent('#modal-card-colors', card.colors?.join(', ') || 'Colorless');
    this.setTextContent('#modal-card-rarity', this.capitalizeFirst(card.rarity || 'unknown'));
    this.setTextContent('#modal-card-set', `${card.setName} (${card.setCode?.toUpperCase()})`);
    
    // Power/Toughness
    const ptText = card.power && card.toughness ? `${card.power}/${card.toughness}` : '-';
    this.setTextContent('#modal-card-pt', ptText);

    // Oracle text
    this.setTextContent('#modal-oracle-text', card.oracleText || 'No oracle text available.');

    // Image
    this.loadCardImage(card.imageUri || '');

    // Legalities
    this.populateLegalities(card.legalities || {});

    // Pricing
    this.populatePricing(card.prices || {});

    // Scryfall link
    const scryfallBtn = this.modal.querySelector('#view-on-scryfall') as HTMLButtonElement;
    if (scryfallBtn && card.scryfallUri) {
      scryfallBtn.onclick = () => window.electronAPI?.shell?.openExternal(card.scryfallUri!);
    }
  }

  private loadCardImage(imageUri: string): void {
    if (!this.modal || !imageUri) return;

    const img = this.modal.querySelector('#card-modal-image') as HTMLImageElement;
    const loading = this.modal.querySelector('#card-image-loading') as HTMLElement;

    if (!img || !loading) return;

    loading.style.display = 'flex';
    img.style.display = 'none';

    img.onload = () => {
      loading.style.display = 'none';
      img.style.display = 'block';
    };

    img.onerror = () => {
      loading.innerHTML = '<p>Failed to load image</p>';
    };

    img.src = imageUri;
  }

  private populateLegalities(legalities: any): void {
    if (!this.modal) return;

    const grid = this.modal.querySelector('#modal-legality-grid');
    if (!grid) return;

    const formats = ['standard', 'pioneer', 'modern', 'legacy', 'vintage', 'commander'];
    
    grid.innerHTML = formats.map(format => {
      const status = legalities[format] || 'not_legal';
      const statusClass = status === 'legal' ? 'legal' : status === 'restricted' ? 'restricted' : 'not-legal';
      
      return `
        <div class="legality-item">
          <span class="format-name">${this.capitalizeFirst(format)}:</span>
          <span class="legality-status ${statusClass}">${this.capitalizeFirst(status.replace('_', ' '))}</span>
        </div>
      `;
    }).join('');
  }

  private populatePricing(prices: any): void {
    if (!this.modal) return;

    const pricingInfo = this.modal.querySelector('#modal-pricing-info');
    if (!pricingInfo) return;

    const priceTypes = [
      { key: 'usd', label: 'Regular' },
      { key: 'usd_foil', label: 'Foil' },
      { key: 'usd_etched', label: 'Etched' }
    ];

    const priceItems = priceTypes
      .filter(type => prices[type.key])
      .map(type => `
        <div class="price-item">
          <span class="price-label">${type.label}:</span>
          <span class="price-value">$${parseFloat(prices[type.key]).toFixed(2)}</span>
        </div>
      `);

    if (priceItems.length === 0) {
      pricingInfo.innerHTML = '<p>No pricing data available</p>';
    } else {
      pricingInfo.innerHTML = priceItems.join('');
    }
  }

  private resetContent(): void {
    if (!this.modal) return;

    // Reset all info fields
    const infoFields = ['#modal-card-name', '#modal-card-mana', '#modal-card-cmc', 
                       '#modal-card-type', '#modal-card-colors', '#modal-card-rarity', 
                       '#modal-card-set', '#modal-card-pt'];
    
    infoFields.forEach(selector => {
      this.setTextContent(selector, 'Loading...');
    });

    this.setTextContent('#modal-oracle-text', 'Loading card data...');
    this.setTextContent('#modal-legality-grid', 'Loading...');
    this.setTextContent('#modal-pricing-info', 'Loading...');

    // Reset image
    const img = this.modal.querySelector('#card-modal-image') as HTMLImageElement;
    const loading = this.modal.querySelector('#card-image-loading') as HTMLElement;
    if (img && loading) {
      img.style.display = 'none';
      loading.style.display = 'flex';
      loading.innerHTML = '<div class="spinner"></div><p>Loading image...</p>';
    }
  }

  private showError(message: string): void {
    if (!this.modal) return;

    this.setTextContent('#modal-oracle-text', `Error: ${message}`);
    this.setTextContent('#modal-legality-grid', 'Unable to load data');
    this.setTextContent('#modal-pricing-info', 'Unable to load data');
  }

  private setTextContent(selector: string, text: string): void {
    const element = this.modal?.querySelector(selector);
    if (element) element.textContent = text;
  }

  private capitalizeFirst(str: string): string {
    return str.charAt(0).toUpperCase() + str.slice(1);
  }

  close(): void {
    if (this.modal) {
      this.modal.style.display = 'none';
    }
  }

  destroy(): void {
    if (this.modal) {
      this.modal.remove();
      this.modal = null;
    }
  }
}
