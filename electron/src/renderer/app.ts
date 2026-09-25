// Main application script file
import './styles.css';
import { CollectionTab } from './components/CollectionTab';
import { DecksTab } from './components/DecksTab';
import { AIRecommendationsTab } from './components/AIRecommendationsTab';
import { openModal, closeModal, setStatus } from './ui';
import type { Deck } from './types';

// Feature flags
const ENABLE_AI_RECOMMENDATIONS = false; // Set to true to re-enable AI recommendations

class DecksmithApp {
  private collectionTab!: CollectionTab;
  private decksTab!: DecksTab;
  private aiTab: AIRecommendationsTab | null = null;
  private version = '';

  // Used by the inline onclick handlers in the tab components (window.app.components.*)
  get components() {
    return {
      collection: this.collectionTab,
      decks: this.decksTab,
    };
  }

  // Used by the AI tab's inline onclick handlers (window.app.ai.*)
  get ai() {
    return this.aiTab;
  }

  constructor() {
    this.init();
  }

  private async init(): Promise<void> {
    if (ENABLE_AI_RECOMMENDATIONS) {
      this.addAITabMarkup();
    }

    this.initializeComponents();
    this.setupEventListeners();
    await this.showVersion();
    setStatus('Application ready', false);
  }

  private initializeComponents(): void {
    this.collectionTab = new CollectionTab();
    this.decksTab = new DecksTab();

    this.collectionTab.initialize();
    this.decksTab.initialize(); // also loads saved decks

    const collectionLoaded = this.collectionTab.loadCollectionData();

    if (ENABLE_AI_RECOMMENDATIONS) {
      this.aiTab = new AIRecommendationsTab();
      this.aiTab.initialize();
      this.aiTab.setDecks(this.decksTab.getAllDecks());
      collectionLoaded.then(() => this.aiTab?.setCollection(this.collectionTab.getCollection()));
      this.setupInterComponentCommunication();
    }
  }

  // Adds the AI Recommendations tab button and panel (only when the feature flag is on)
  private addAITabMarkup(): void {
    document.querySelector('.tab-nav')?.insertAdjacentHTML('beforeend', `
      <button class="tab-btn" data-tab="ai-recommendations">
        <span class="tab-icon">🤖</span>
        AI Recommendations
      </button>
    `);
    document.querySelector('.tab-content')?.insertAdjacentHTML('beforeend', `
      <div id="ai-recommendations-tab" class="tab-panel"></div>
    `);
  }

  private setupInterComponentCommunication(): void {
    // When a deck is selected in the decks tab, notify the AI tab
    this.decksTab.setOnDeckSelectionChange((deck: Deck | null) => {
      if (this.aiTab && deck) {
        this.aiTab.setSelectedDeck(deck);
      }
    });

    const currentDeck = this.decksTab.getCurrentDeck();
    if (currentDeck && this.aiTab) {
      this.aiTab.setSelectedDeck(currentDeck);
    }
  }

  private setupEventListeners(): void {
    // Tab switching
    document.querySelectorAll('.tab-btn').forEach(btn => {
      btn.addEventListener('click', (e) => {
        const tab = (e.currentTarget as HTMLElement).dataset.tab;
        if (tab) {
          this.switchTab(tab);
        }
      });
    });

    // Modal controls
    document.getElementById('modal-close')?.addEventListener('click', () => closeModal());

    document.getElementById('modal')?.addEventListener('click', (e) => {
      if (e.target === e.currentTarget) {
        closeModal();
      }
    });

    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape') {
        closeModal();
      }
    });

    // Menu events from the main process
    window.electronAPI?.onMenuAction((action: string) => {
      this.handleMenuAction(action);
    });
  }

  private switchTab(tabName: string): void {
    document.querySelectorAll('.tab-btn').forEach(btn => {
      btn.classList.toggle('active', btn.getAttribute('data-tab') === tabName);
    });

    document.querySelectorAll('.tab-panel').forEach(panel => {
      panel.classList.toggle('active', panel.id === `${tabName}-tab`);
    });

    if (tabName === 'ai-recommendations') {
      // Pick up decks created or renamed since the tab was last shown
      this.aiTab?.refreshDecksDropdown();
    }
  }

  private handleMenuAction(action: string): void {
    switch (action) {
      case 'menu:new-collection':
        this.switchTab('collection');
        this.collectionTab.newCollection();
        break;
      case 'menu:import-collection':
        this.switchTab('collection');
        this.collectionTab.importCSV();
        break;
      case 'menu:export-collection':
        this.collectionTab.exportCSV();
        break;
      case 'menu:new-deck':
        this.switchTab('decks');
        this.decksTab.createNewDeck();
        break;
      case 'menu:import-deck':
        this.switchTab('decks');
        this.decksTab.importDeck();
        break;
      case 'menu:export-deck':
        this.switchTab('decks');
        this.decksTab.exportDeck();
        break;
      case 'menu:about':
        this.showAbout();
        break;
    }
  }

  private async showVersion(): Promise<void> {
    try {
      this.version = (await window.electronAPI?.getAppVersion()) ?? '';
    } catch (error) {
      console.error('Could not read app version:', error);
    }

    const versionElement = document.getElementById('app-version');
    if (versionElement && this.version) {
      versionElement.textContent = `v${this.version}`;
    }
  }

  private showAbout(): void {
    const version = this.version ? ` v${this.version}` : '';
    openModal('About Decksmith', `
      <div class="about-content">
        <h3>🃏 Decksmith${version}</h3>
        <p>Modern Magic: The Gathering collection and deck manager built with Electron.</p>
        <br>
        <p><strong>Features:</strong></p>
        <ul>
          <li>Collection management with Scryfall integration</li>
          <li>Deck building with mainboard and sideboard</li>
          <li>Import/Export CSV and Arena deck lists</li>
          <li>Collection statistics</li>
        </ul>
        <br>
        <p>Built with ❤️ for the MTG community</p>
      </div>
    `);
  }
}

// Initialize the app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
  // Exposed globally for the components' inline onclick handlers
  window.app = new DecksmithApp();
});
