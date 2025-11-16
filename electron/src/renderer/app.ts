// Main application script file
import './styles.css';
import { CollectionTab } from './components/CollectionTab';
import { DecksTab } from './components/DecksTab';
// Temporarily disabled - AI Recommendations feature
// import { AIRecommendationsTab } from './components/AIRecommendationsTab';
import type { Card, Deck, Collection } from './types';

// Feature flags
const ENABLE_AI_RECOMMENDATIONS = false; // Set to true to re-enable AI recommendations

class DecksmithApp {
  private currentTab = 'collection';
  private collectionData: Collection = { cards: [], lastModified: new Date().toISOString() };
  private decksData: Deck[] = [];
  
  // Tab components
  private collectionTab!: CollectionTab;
  private decksTab!: DecksTab;
  // private aiTab!: AIRecommendationsTab;

  // Expose components for global access
  get components() {
    return {
      collection: this.collectionTab,
      decks: this.decksTab,
      // ai: this.aiTab
    };
  }

  // Direct component access for window.app
  get collection() {
    return this.collectionTab;
  }

  get decks() {
    return this.decksTab;
  }

  // get ai() {
  //   return this.aiTab;
  // }

  getDecks(): Deck[] {
    return this.decksData;
  }

  constructor() {
    this.init();
  }

  private async init(): Promise<void> {
    await this.loadData();
    this.hideModalAtStartup(); // Ensure modal is hidden
    this.initializeComponents();
    this.setupEventListeners();
    this.updateUI();
  }

  private hideModalAtStartup(): void {
    const modal = document.getElementById('modal');
    if (modal) {
      modal.classList.add('hidden');
      console.log('Modal hidden at startup');
    }
  }

  private initializeComponents(): void {
    console.log('Initializing components...');
    
    this.collectionTab = new CollectionTab();
    this.decksTab = new DecksTab();
    // Temporarily disabled - AI Recommendations
    // if (ENABLE_AI_RECOMMENDATIONS) {
    //   this.aiTab = new AIRecommendationsTab();
    // }
    
    // Initialize components
    console.log('Calling initialize on components...');
    this.collectionTab.initialize();
    this.decksTab.initialize();
    // if (ENABLE_AI_RECOMMENDATIONS && this.aiTab) {
    //   this.aiTab.initialize();
    // }
    
    // Load collection data asynchronously
    this.collectionTab.loadCollectionData();
    
    // Pass data to other components
    this.decksTab.setDecks(this.decksData);
    // if (ENABLE_AI_RECOMMENDATIONS && this.aiTab) {
    //   this.aiTab.setDecks(this.decksData);
    //   this.aiTab.setCollection(this.collectionData);
    // }
    
    // Connect AI tab with deck selection (if enabled)
    // if (ENABLE_AI_RECOMMENDATIONS) {
    //   this.setupInterComponentCommunication();
    // }
    
    console.log('Components initialized');
  }

  private setupInterComponentCommunication(): void {
    // Temporarily disabled - AI Recommendations
    // Set up communication between components
    // When a deck is selected in the decks tab, notify the AI tab
    
    // this.decksTab.setOnDeckSelectionChange((deck: Deck | null) => {
    //   if (this.aiTab && deck) {
    //     this.aiTab.setSelectedDeck(deck);
    //     console.log(`Deck selection changed to: ${deck.name}`);
    //   }
    // });

    // Initial setup - if there's already a current deck, set it in AI tab
    // const currentDeck = this.decksTab.getCurrentDeck();
    // if (currentDeck && this.aiTab) {
    //   this.aiTab.setSelectedDeck(currentDeck);
    // }
  }

  private async setupEventListeners(): Promise<void> {
    // Tab switching
    document.querySelectorAll('.tab-btn').forEach(btn => {
      btn.addEventListener('click', (e) => {
        const target = e.target as HTMLElement;
        const tab = target.dataset.tab || target.closest('.tab-btn')?.getAttribute('data-tab');
        if (tab) {
          this.switchTab(tab);
        }
      });
    });

    // Modal controls
    document.getElementById('modal-close')?.addEventListener('click', () => {
      this.closeModal();
    });

    document.getElementById('modal')?.addEventListener('click', (e) => {
      if (e.target === e.currentTarget) {
        this.closeModal();
      }
    });

    // Handle escape key for modals
    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape') {
        this.closeModal();
      }
    });

    // IPC event handlers
    if (window.electronAPI?.onMenuAction) {
      window.electronAPI.onMenuAction((action: string) => {
        this.handleMenuAction(action);
      });
    }
  }

  private switchTab(tabName: string): void {
    console.log(`Switching to tab: ${tabName}`);
    
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

    // Initialize components only if not already initialized (to preserve state)
    console.log(`Ensuring component initialization for tab: ${tabName}`);
    switch (tabName) {
      case 'collection':
        if (!this.collectionTab?.initialized) {
          this.collectionTab?.initialize();
        }
        break;
      case 'decks':
        if (!this.decksTab?.initialized) {
          this.decksTab?.initialize();
        }
        break;
      // Temporarily disabled - AI Recommendations
      // case 'ai-recommendations':
      //   if (!this.aiTab?.initialized) {
      //     this.aiTab?.initialize();
      //   } else {
      //     // Just refresh the deck dropdown without re-rendering everything
      //     this.aiTab.refreshDecksDropdown();
      //   }
      //   break;
    }

    this.currentTab = tabName;
    this.updateStatus(`Switched to ${tabName} tab`);
  }

  private async loadData(): Promise<void> {
    try {
      // Load collection
      const savedCollection = await window.electronAPI?.store.get('collection');
      if (savedCollection) {
        this.collectionData = savedCollection;
      } else {
        // Add some sample data for demonstration
        this.collectionData = {
          cards: [
            {
              id: '1',
              name: 'Lightning Bolt',
              typeLine: 'Instant',
              manaCost: '{R}',
              colors: ['R'],
              rarity: 'common',
              quantity: 4
            },
            {
              id: '2',
              name: 'Counterspell',
              typeLine: 'Instant',
              manaCost: '{U}{U}',
              colors: ['U'],
              rarity: 'common',
              quantity: 3
            },
            {
              id: '3',
              name: 'Black Lotus',
              typeLine: 'Artifact',
              manaCost: '{0}',
              colors: [],
              rarity: 'mythic',
              quantity: 1
            },
            {
              id: '4',
              name: 'Serra Angel',
              typeLine: 'Creature — Angel',
              manaCost: '{3}{W}{W}',
              colors: ['W'],
              rarity: 'uncommon',
              quantity: 2
            },
            {
              id: '5',
              name: 'Forest',
              typeLine: 'Basic Land — Forest',
              manaCost: '',
              colors: [],
              rarity: 'common',
              quantity: 10
            },
            {
              id: '6',
              name: 'Jace, the Mind Sculptor',
              typeLine: 'Legendary Planeswalker — Jace',
              manaCost: '{2}{U}{U}',
              colors: ['U'],
              rarity: 'mythic',
              quantity: 1
            }
          ],
          lastModified: new Date().toISOString()
        };
      }

      // Load decks
      const savedDecks = await window.electronAPI?.store.get('decks');
      if (savedDecks) {
        this.decksData = savedDecks;
      } else {
        // Add sample decks with more realistic content
        this.decksData = [
          {
            id: '1',
            name: 'Sample Burn Deck',
            format: 'Standard',
            mainboard: [
              { id: '1', name: 'Lightning Bolt', quantity: 4, typeLine: 'Instant', rarity: 'common', manaCost: '{R}', colors: ['R'], cmc: 1 },
              { id: '2', name: 'Monastery Swiftspear', quantity: 4, typeLine: 'Creature — Human Monk', rarity: 'common', manaCost: '{R}', colors: ['R'], cmc: 1 },
              { id: '3', name: 'Goblin Guide', quantity: 4, typeLine: 'Creature — Goblin Scout', rarity: 'rare', manaCost: '{R}', colors: ['R'], cmc: 1 },
              { id: '4', name: 'Lava Spike', quantity: 4, typeLine: 'Sorcery', rarity: 'common', manaCost: '{R}', colors: ['R'], cmc: 1 },
              { id: '5', name: 'Rift Bolt', quantity: 4, typeLine: 'Sorcery', rarity: 'common', manaCost: '{2}{R}', colors: ['R'], cmc: 3 },
              { id: '6', name: 'Lightning Helix', quantity: 4, typeLine: 'Instant', rarity: 'uncommon', manaCost: '{R}{W}', colors: ['R', 'W'], cmc: 2 },
              { id: '7', name: 'Boros Charm', quantity: 4, typeLine: 'Instant', rarity: 'uncommon', manaCost: '{R}{W}', colors: ['R', 'W'], cmc: 2 },
              { id: '8', name: 'Mountain', quantity: 12, typeLine: 'Basic Land — Mountain', rarity: 'common', manaCost: '', colors: [], cmc: 0 },
              { id: '9', name: 'Sacred Foundry', quantity: 4, typeLine: 'Land — Mountain Plains', rarity: 'rare', manaCost: '', colors: [], cmc: 0 }
            ],
            sideboard: [
              { id: '10', name: 'Searing Blaze', quantity: 3, typeLine: 'Instant', rarity: 'common', manaCost: '{1}{R}', colors: ['R'], cmc: 2 }
            ],
            lastModified: new Date().toISOString()
          },
          {
            id: '2', 
            name: 'Control Deck',
            format: 'Standard',
            mainboard: [
              { id: '11', name: 'Counterspell', quantity: 4, typeLine: 'Instant', rarity: 'common', manaCost: '{U}{U}', colors: ['U'], cmc: 2 },
              { id: '12', name: 'Wrath of God', quantity: 3, typeLine: 'Sorcery', rarity: 'rare', manaCost: '{2}{W}{W}', colors: ['W'], cmc: 4 },
              { id: '13', name: 'Jace, the Mind Sculptor', quantity: 2, typeLine: 'Legendary Planeswalker — Jace', rarity: 'mythic', manaCost: '{2}{U}{U}', colors: ['U'], cmc: 4 },
              { id: '14', name: 'Path to Exile', quantity: 4, typeLine: 'Instant', rarity: 'uncommon', manaCost: '{W}', colors: ['W'], cmc: 1 },
              { id: '15', name: 'Brainstorm', quantity: 4, typeLine: 'Instant', rarity: 'common', manaCost: '{U}', colors: ['U'], cmc: 1 },
              { id: '16', name: 'Island', quantity: 10, typeLine: 'Basic Land — Island', rarity: 'common', manaCost: '', colors: [], cmc: 0 },
              { id: '17', name: 'Plains', quantity: 8, typeLine: 'Basic Land — Plains', rarity: 'common', manaCost: '', colors: [], cmc: 0 },
              { id: '18', name: 'Hallowed Fountain', quantity: 4, typeLine: 'Land — Plains Island', rarity: 'rare', manaCost: '', colors: [], cmc: 0 },
              { id: '19', name: 'Serra Angel', quantity: 3, typeLine: 'Creature — Angel', rarity: 'uncommon', manaCost: '{3}{W}{W}', colors: ['W'], cmc: 5 }
            ],
            sideboard: [],
            lastModified: new Date().toISOString()
          }
        ];
      }

      this.updateStatus('Data loaded successfully');
    } catch (error) {
      console.error('Error loading data:', error);
      this.updateStatus('Error loading data');
    }
  }

  private updateUI(): void {
    this.updateStatus('Application ready');
  }

  private updateStatus(message: string): void {
    const statusElement = document.getElementById('status-message');
    if (statusElement) {
      statusElement.textContent = message;
    }
  }

  private closeModal(): void {
    const modal = document.getElementById('modal');
    if (modal) {
      modal.classList.add('hidden');
    }
  }

  private handleMenuAction(action: string): void {
    switch (action) {
      case 'menu:new-collection':
        this.newCollection();
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

  private newCollection(): void {
    this.collectionData = { cards: [], lastModified: new Date().toISOString() };
    this.collectionTab?.setCollection(this.collectionData);
    this.updateStatus('New collection created');
  }

  private importCollection(): void {
    // TODO: Implement import collection
    console.log('Import collection');
  }

  private exportCollection(): void {
    // TODO: Implement export collection
    console.log('Export collection');
  }

  private createNewDeck(): void {
    // TODO: Implement create new deck
    console.log('Create new deck');
  }

  private importDeck(): void {
    // TODO: Implement import deck
    console.log('Import deck');
  }

  private showAbout(): void {
    const modal = document.getElementById('modal');
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
  const app = new DecksmithApp();
  // Expose app to global scope for direct onclick handlers
  (window as any).app = app;
});
