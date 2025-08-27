// Main application TypeScript file
import { CollectionTab } from './components/CollectionTab';
import { DecksTab } from './components/DecksTab';
import { AIRecommendationsTab } from './components/AIRecommendationsTab';
import type { Card, Deck, Collection } from './types';

class DeckMasterApp {
  private currentTab = 'collection';
  private collection: Collection = { cards: [], lastModified: new Date().toISOString() };
  private decks: Deck[] = [];
  
  // Tab components
  private collectionTab!: CollectionTab;
  private decksTab!: DecksTab;
  private aiTab!: AIRecommendationsTab;

  constructor() {
    this.init();
  }

  private async init(): Promise<void> {
    await this.loadData();
    this.initializeComponents();
    this.setupEventListeners();
    this.updateUI();
  }

  private initializeComponents(): void {
    this.collectionTab = new CollectionTab();
    this.decksTab = new DecksTab();
    this.aiTab = new AIRecommendationsTab();
    
    // Initialize components
    this.collectionTab.initialize();
    this.decksTab.initialize();
    this.aiTab.initialize();
    
    // Pass data to components
    this.collectionTab.setCollection(this.collection);
    this.decksTab.setDecks(this.decks);
    this.aiTab.setDecks(this.decks);
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

    // Modal controls
    document.getElementById('modal-close')?.addEventListener('click', () => {
      this.closeModal();
    });

    document.getElementById('modal-overlay')?.addEventListener('click', (e) => {
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
  }

  private async loadData(): Promise<void> {
    try {
      // Load collection
      const savedCollection = await window.electronAPI?.store.get('collection');
      if (savedCollection) {
        this.collection = savedCollection;
      } else {
        // Add some sample data for demonstration
        this.collection = {
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
        this.decks = savedDecks;
      } else {
        // Add sample deck
        this.decks = [
          {
            id: '1',
            name: 'Sample Deck',
            format: 'Standard',
            mainboard: [
              { id: '1', name: 'Lightning Bolt', quantity: 4, typeLine: 'Instant', rarity: 'common' }
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
    const modal = document.getElementById('modal-overlay');
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
    this.collection = { cards: [], lastModified: new Date().toISOString() };
    this.collectionTab?.setCollection(this.collection);
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
