import { BaseComponent } from './BaseComponent';
import type { Deck, Card } from '../types';

export interface Recommendation {
  card: Card;
  confidence: number;
  synergy: number;
  cmc: number;
  reasons: string[];
}

export class AIRecommendationsTab extends BaseComponent {
  private selectedDeck: Deck | null = null;
  private recommendations: Recommendation[] = [];
  private isLoading = false;

  constructor() {
    super('#ai-recommendations-tab');
  }

  initialize(): void {
    if (this.isInitialized) return;
    
    this.render();
    this.setupEventListeners();
    this.isInitialized = true;
  }

  render(): void {
    this.element.innerHTML = `
      <div class="ai-recommendations-layout">
        <div class="recommendations-header">
          <h2>🤖 AI Deck Analysis</h2>
          <div class="deck-selector">
            <label for="deck-select">Current Deck:</label>
            <select id="deck-select">
              <option value="">Select a deck...</option>
            </select>
          </div>
          <div class="recommendation-actions">
            <button id="analyze-deck-btn" class="btn btn-primary" disabled>
              Analyze Deck
            </button>
            <button id="get-recommendations-btn" class="btn btn-secondary" disabled>
              Get Recommendations
            </button>
            <button id="refresh-btn" class="btn btn-secondary">
              Refresh
            </button>
          </div>
        </div>

        <div class="recommendations-content">
          <!-- Deck Analysis Panel -->
          <div class="analysis-panel">
            <h3>Quick Analysis</h3>
            <div id="deck-analysis" class="deck-analysis">
              <div class="analysis-placeholder">
                <p>Select a deck to begin analysis</p>
              </div>
            </div>

            <!-- Mana Curve -->
            <div class="mana-curve-section">
              <h4>📊 Mana Curve Breakdown</h4>
              <div id="mana-curve" class="mana-curve">
                <div class="curve-placeholder">
                  <p>Deck analysis will show mana curve here</p>
                </div>
              </div>
            </div>

            <!-- Health Recommendations -->
            <div class="health-section">
              <h4>🏥 Health</h4>
              <h4>⚡ Synergy</h4>
              <h4>📈 Overall Health</h4>
              <div id="health-analysis" class="health-analysis">
                <div class="health-placeholder">
                  <p>• Consider adjusting mana curve distribution</p>
                  <p>• Deck archetype analysis for 'Wolves'</p>
                </div>
              </div>
            </div>
          </div>

          <!-- Recommendations Panel -->
          <div class="recommendations-panel">
            <div class="recommendations-header-section">
              <h3>AI Card Recommendations</h3>
              <div class="recommendation-filters">
                <div class="filter-controls">
                  <label>
                    Show Lands
                    <input type="checkbox" id="show-lands" />
                  </label>
                  <label>
                    Min Confidence: <span id="confidence-value">75%</span>
                    <input type="range" id="confidence-slider" min="0" max="100" value="75" />
                  </label>
                  <select id="card-type-filter">
                    <option value="">All Types</option>
                    <option value="creature">Creature</option>
                    <option value="instant">Instant</option>
                    <option value="sorcery">Sorcery</option>
                  </select>
                </div>
              </div>
            </div>

            <div id="recommendations-list" class="recommendations-list">
              <div class="recommendations-placeholder">
                <p>💡 <strong>100 recommendations loaded (scroll down for more)</strong></p>
                <p>Select a deck and get AI-powered card recommendations</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    `;
  }

  private setupEventListeners(): void {
    // Deck selection
    this.bindEvent('#deck-select', 'change', () => {
      const select = this.element.querySelector('#deck-select') as HTMLSelectElement;
      if (select.value) {
        this.selectDeck(select.value);
        this.enableAnalysisButtons();
      } else {
        this.selectedDeck = null;
        this.disableAnalysisButtons();
      }
    });

    // Analysis buttons
    this.bindEvent('#analyze-deck-btn', 'click', () => this.analyzeDeck());
    this.bindEvent('#get-recommendations-btn', 'click', () => this.getRecommendations());
    this.bindEvent('#refresh-btn', 'click', () => this.refresh());

    // Filter controls
    this.bindEvent('#show-lands', 'change', () => this.filterRecommendations());
    this.bindEvent('#card-type-filter', 'change', () => this.filterRecommendations());
    
    const confidenceSlider = this.element.querySelector('#confidence-slider') as HTMLInputElement;
    confidenceSlider?.addEventListener('input', () => {
      const value = confidenceSlider.value;
      const display = this.element.querySelector('#confidence-value');
      if (display) display.textContent = `${value}%`;
      this.filterRecommendations();
    });
  }

  setDecks(decks: Deck[]): void {
    const select = this.element.querySelector('#deck-select') as HTMLSelectElement;
    if (!select) return;

    select.innerHTML = '<option value="">Select a deck...</option>';
    decks.forEach(deck => {
      const option = document.createElement('option');
      option.value = deck.id;
      option.textContent = deck.name || 'Untitled Deck';
      select.appendChild(option);
    });
  }

  private selectDeck(deckId: string): void {
    // This would normally fetch the deck from storage/parent component
    console.log(`Selected deck: ${deckId}`);
  }

  private enableAnalysisButtons(): void {
    const analyzeBtn = this.element.querySelector('#analyze-deck-btn') as HTMLButtonElement;
    const recommendBtn = this.element.querySelector('#get-recommendations-btn') as HTMLButtonElement;
    
    if (analyzeBtn) analyzeBtn.disabled = false;
    if (recommendBtn) recommendBtn.disabled = false;
  }

  private disableAnalysisButtons(): void {
    const analyzeBtn = this.element.querySelector('#analyze-deck-btn') as HTMLButtonElement;
    const recommendBtn = this.element.querySelector('#get-recommendations-btn') as HTMLButtonElement;
    
    if (analyzeBtn) analyzeBtn.disabled = true;
    if (recommendBtn) recommendBtn.disabled = true;
  }

  private async analyzeDeck(): Promise<void> {
    if (!this.selectedDeck) return;

    this.isLoading = true;
    this.showAnalysisLoading();

    try {
      // Simulate analysis
      await new Promise(resolve => setTimeout(resolve, 2000));
      
      // Mock analysis results
      this.showDeckAnalysis({
        archetype: 'Midrange',
        curveScore: 40.8,
        synergy: 34.5,
        control: 5.8,
        health: 62,
        recommendations: [
          'Fast aggressive strategy focusing on direct damage and answers',
          'Consider adjusting mana curve distribution',
          'Late-game control strategy with counterspells and removal'
        ]
      });

      this.showManaCurve([
        { cmc: 0, count: 21, percentage: 35 },
        { cmc: 1, count: 3, percentage: 5 },
        { cmc: 2, count: 2, percentage: 3 },
        { cmc: 3, count: 14, percentage: 19 },
        { cmc: 4, count: 1, percentage: 2 },
        { cmc: 5, count: 2, percentage: 3 }
      ]);
      
    } finally {
      this.isLoading = false;
    }
  }

  private async getRecommendations(): Promise<void> {
    if (!this.selectedDeck) return;

    this.isLoading = true;
    this.showRecommendationsLoading();

    try {
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 3000));
      
      // Mock recommendations
      this.recommendations = [
        {
          card: { id: '1', name: 'Bloodthirsty Adversary', typeLine: 'Creature — Human Warrior', rarity: 'mythic' },
          confidence: 90.3,
          synergy: 73.0,
          cmc: 2,
          reasons: ['Strong aggro synergy', 'Excellent synergy potential (+4)', 'Strong aggro synergy', 'Good synergy with current card']
        },
        {
          card: { id: '2', name: 'Robber of the Rich', typeLine: 'Creature — Human Archer Rogue', rarity: 'mythic' },
          confidence: 89.9,
          synergy: 73.0,
          cmc: 2,
          reasons: ['Strong aggro synergy', 'Excellent synergy potential (+4)', 'Strong aggro synergy']
        },
        {
          card: { id: '3', name: 'Walking Ballista', typeLine: 'Artifact Creature — Construct', rarity: 'rare' },
          confidence: 89.1,
          synergy: 70.0,
          cmc: 0,
          reasons: ['Format staple in Modern', 'Proven competitive card (+4)', 'Strong aggro synergy']
        }
        // Add more mock recommendations...
      ];

      this.renderRecommendations();
      
    } finally {
      this.isLoading = false;
    }
  }

  private showAnalysisLoading(): void {
    const analysisPanel = this.element.querySelector('#deck-analysis');
    if (analysisPanel) {
      analysisPanel.innerHTML = `
        <div class="loading-state">
          <div class="spinner"></div>
          <p>Analyzing deck...</p>
        </div>
      `;
    }
  }

  private showDeckAnalysis(analysis: any): void {
    const analysisPanel = this.element.querySelector('#deck-analysis');
    if (analysisPanel) {
      analysisPanel.innerHTML = `
        <div class="archetype-match">
          <h4>🎯 Archetype Match Scores</h4>
          <div class="archetype-scores">
            <div class="archetype-bar">
              <span class="archetype-label">1. Midrange</span>
              <div class="progress-bar">
                <div class="progress-fill" style="width: ${analysis.curveScore}%"></div>
              </div>
              <span class="archetype-score">${analysis.curveScore}%</span>
            </div>
            <div class="archetype-bar">
              <span class="archetype-label">2. Burn/Aggro</span>
              <div class="progress-bar">
                <div class="progress-fill" style="width: ${analysis.synergy}%"></div>
              </div>
              <span class="archetype-score">${analysis.synergy}%</span>
            </div>
            <div class="archetype-bar">
              <span class="archetype-label">3. Control</span>
              <div class="progress-bar">
                <div class="progress-fill" style="width: ${analysis.control}%"></div>
              </div>
              <span class="archetype-score">${analysis.control}%</span>
            </div>
          </div>
        </div>
      `;
    }

    const healthPanel = this.element.querySelector('#health-analysis');
    if (healthPanel) {
      healthPanel.innerHTML = `
        <div class="health-recommendations">
          ${analysis.recommendations.map((rec: string) => `<p>• ${rec}</p>`).join('')}
        </div>
        <div class="overall-health">
          <div class="health-circle">
            <span class="health-score">${analysis.health}/100</span>
          </div>
        </div>
      `;
    }
  }

  private showManaCurve(curve: any[]): void {
    const curvePanel = this.element.querySelector('#mana-curve');
    if (curvePanel) {
      const maxCount = Math.max(...curve.map(c => c.count));
      curvePanel.innerHTML = `
        <div class="mana-curve-chart">
          ${curve.map(point => `
            <div class="curve-bar">
              <div class="curve-bar-fill" style="height: ${(point.count / maxCount) * 100}%"></div>
              <div class="curve-bar-label">
                <div class="cmc-label">CMC ${point.cmc}</div>
                <div class="count-label">${point.count} cards</div>
                <div class="percentage-label">${point.percentage}%</div>
              </div>
            </div>
          `).join('')}
        </div>
      `;
    }
  }

  private showRecommendationsLoading(): void {
    const list = this.element.querySelector('#recommendations-list');
    if (list) {
      list.innerHTML = `
        <div class="loading-state">
          <div class="spinner"></div>
          <p>Getting AI recommendations...</p>
        </div>
      `;
    }
  }

  private renderRecommendations(): void {
    const list = this.element.querySelector('#recommendations-list');
    if (!list) return;

    list.innerHTML = `
      <div class="recommendations-header-info">
        <p><strong>Total: ${this.recommendations.length} of 100 recommendations (hiding 50 lands, showing only Creatures)</strong></p>
      </div>
      <div class="recommendations-grid">
        ${this.recommendations.map(rec => `
          <div class="recommendation-item">
            <div class="rec-header">
              <div class="rec-confidence">
                <span class="confidence-badge">${rec.confidence.toFixed(1)}%</span>
                <span class="synergy-score">Synergy: ${rec.synergy.toFixed(1)}%</span>
                <span class="cmc-badge">CMC: ${rec.cmc}</span>
              </div>
            </div>
            <div class="rec-card-info">
              <h4 class="card-name">${rec.card.name} ✓</h4>
              <p class="card-type">${rec.card.typeLine}</p>
            </div>
            <div class="rec-reasons">
              <h5>Reasons/Notes</h5>
              <ul>
                ${rec.reasons.map(reason => `<li>${reason}</li>`).join('')}
              </ul>
            </div>
          </div>
        `).join('')}
      </div>
    `;
  }

  private filterRecommendations(): void {
    // TODO: Implement filtering logic
    this.renderRecommendations();
  }

  private refresh(): void {
    this.recommendations = [];
    this.selectedDeck = null;
    
    const select = this.element.querySelector('#deck-select') as HTMLSelectElement;
    if (select) select.value = '';
    
    this.disableAnalysisButtons();
    
    // Reset panels
    const analysisPanel = this.element.querySelector('#deck-analysis');
    if (analysisPanel) {
      analysisPanel.innerHTML = `
        <div class="analysis-placeholder">
          <p>Select a deck to begin analysis</p>
        </div>
      `;
    }

    const list = this.element.querySelector('#recommendations-list');
    if (list) {
      list.innerHTML = `
        <div class="recommendations-placeholder">
          <p>💡 <strong>100 recommendations loaded (scroll down for more)</strong></p>
          <p>Select a deck and get AI-powered card recommendations</p>
        </div>
      `;
    }
  }
}
