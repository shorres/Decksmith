import { BaseComponent } from './BaseComponent';
import { RecommendationEngine, SmartRecommendation, DeckAnalysis } from './RecommendationEngine';
import type { Deck, Card } from '../types';

export class AIRecommendationsTab extends BaseComponent {
  private selectedDeck: Deck | null = null;
  private recommendations: SmartRecommendation[] = [];
  private filteredRecommendations: SmartRecommendation[] = [];
  private deckAnalysis: DeckAnalysis | null = null;
  private isLoading = false;
  private recommendationEngine: RecommendationEngine;
  private collection: any = null; // Will be set by parent
  private availableDecks: Deck[] = []; // Store available decks

  constructor() {
    super('#ai-recommendations-tab');
    this.recommendationEngine = new RecommendationEngine();
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
            <button id="analyze-deck-btn" class="btn btn-primary" onclick="console.log('Analyze button clicked!'); window.app?.ai?.analyzeDeck?.();">
              Analyze Deck
            </button>
            <button id="get-recommendations-btn" class="btn btn-secondary" onclick="console.log('Recommendations button clicked!'); window.app?.ai?.getRecommendations?.();">
              Get Recommendations
            </button>
            <button id="refresh-btn" class="btn btn-secondary" onclick="console.log('Refresh button clicked!'); window.app?.ai?.refresh?.();">
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
                <p>💡 <strong>Click "Get Recommendations" to see AI suggestions</strong></p>
                <p>Select a deck and get AI-powered card recommendations</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    `;

    // Update dropdown with available decks after rendering
    this.updateDeckDropdown();
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
    this.availableDecks = decks;
    this.updateDeckDropdown();
  }

  private updateDeckDropdown(): void {
    const select = this.element.querySelector('#deck-select') as HTMLSelectElement;
    if (!select) {
      // Component not rendered yet, will be called again after render
      return;
    }

    select.innerHTML = '<option value="">Select a deck...</option>';
    this.availableDecks.forEach(deck => {
      const option = document.createElement('option');
      option.value = deck.id;
      option.textContent = deck.name || 'Untitled Deck';
      select.appendChild(option);
    });

    // If there's already a selected deck, update the dropdown
    if (this.selectedDeck) {
      select.value = this.selectedDeck.id;
    }
  }

  private selectDeck(deckId: string): void {
    console.log(`Attempting to select deck: ${deckId}`);
    
    // Find the deck in our available decks
    const deck = this.availableDecks.find(d => d.id === deckId);
    
    if (deck) {
      this.selectedDeck = deck;
      console.log(`Successfully selected deck: ${deck.name}`);
      
      // Clear previous analysis and recommendations
      this.recommendations = [];
      this.filteredRecommendations = [];
      this.deckAnalysis = null;
      
      // Clear the display
      this.clearAnalysisDisplay();
      this.clearRecommendationsDisplay();
      
      // Enable the analysis buttons since we have a valid deck
      this.enableAnalysisButtons();
      
    } else {
      console.warn(`Deck not found with ID: ${deckId}`);
      this.selectedDeck = null;
      this.disableAnalysisButtons();
    }
  }

  private clearAnalysisDisplay(): void {
    const analysisPanel = this.element.querySelector('#deck-analysis');
    if (analysisPanel) {
      analysisPanel.innerHTML = `
        <div class="analysis-placeholder">
          <p>Click "Analyze Deck" to see deck analysis</p>
        </div>
      `;
    }

    const healthPanel = this.element.querySelector('#health-analysis');
    if (healthPanel) {
      healthPanel.innerHTML = `
        <div class="health-placeholder">
          <p>Deck health analysis will appear here</p>
        </div>
      `;
    }

    const curvePanel = this.element.querySelector('#mana-curve');
    if (curvePanel) {
      curvePanel.innerHTML = `
        <div class="curve-placeholder">
          <p>Mana curve will be shown here after analysis</p>
        </div>
      `;
    }
  }

  private clearRecommendationsDisplay(): void {
    const list = this.element.querySelector('#recommendations-list');
    if (list) {
      list.innerHTML = `
        <div class="recommendations-placeholder">
          <p>💡 <strong>Click "Get Recommendations" to see AI suggestions</strong></p>
          <p>Select a deck and get AI-powered card recommendations</p>
        </div>
      `;
    }
  }

  private enableAnalysisButtons(): void {
    // Buttons are always enabled now - no need to manage disabled state
    const analyzeBtn = this.element.querySelector('#analyze-deck-btn') as HTMLButtonElement;
    const recommendBtn = this.element.querySelector('#get-recommendations-btn') as HTMLButtonElement;
    
    // Optional: Add visual feedback that buttons are ready
    if (analyzeBtn) analyzeBtn.style.opacity = '1';
    if (recommendBtn) recommendBtn.style.opacity = '1';
  }

  private disableAnalysisButtons(): void {
    // Buttons remain clickable but with visual feedback
    const analyzeBtn = this.element.querySelector('#analyze-deck-btn') as HTMLButtonElement;
    const recommendBtn = this.element.querySelector('#get-recommendations-btn') as HTMLButtonElement;
    
    // Optional: Dim buttons when no deck selected  
    if (analyzeBtn) analyzeBtn.style.opacity = '0.6';
    if (recommendBtn) recommendBtn.style.opacity = '0.6';
  }

  public async analyzeDeck(): Promise<void> {
    console.log('analyzeDeck method called');
    if (!this.selectedDeck) {
      console.warn('No deck selected for analysis');
      return;
    }

    console.log('Starting deck analysis for:', this.selectedDeck.name);
    this.isLoading = true;
    this.showAnalysisLoading();

    try {
      // Use the real recommendation engine
      this.deckAnalysis = this.recommendationEngine.analyzeDeck(this.selectedDeck);
      
      // Show the analysis results
      this.showDeckAnalysis();
      this.showManaCurve();
      
    } catch (error) {
      console.error('Error analyzing deck:', error);
      this.showAnalysisError();
    } finally {
      this.isLoading = false;
    }
  }

  public async getRecommendations(): Promise<void> {
    console.log('getRecommendations method called');
    if (!this.selectedDeck) {
      console.warn('No deck selected for recommendations');
      return;
    }

    console.log('Getting recommendations for:', this.selectedDeck.name);
    this.isLoading = true;
    this.showRecommendationsLoading();

    try {
      // Use the real recommendation engine
      this.recommendations = await this.recommendationEngine.generateRecommendations(
        this.selectedDeck,
        this.collection,
        100, // Get 100 recommendations
        'standard' // Format - could be made configurable
      );
      
      this.filteredRecommendations = [...this.recommendations];
      this.renderRecommendations();
      
    } catch (error) {
      console.error('Error getting recommendations:', error);
      this.showRecommendationsError();
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

  private showAnalysisError(): void {
    const analysisPanel = this.element.querySelector('#deck-analysis');
    if (analysisPanel) {
      analysisPanel.innerHTML = `
        <div class="error-state">
          <p style="color: red;">❌ Error analyzing deck. Please try again.</p>
        </div>
      `;
    }
  }

  private showRecommendationsError(): void {
    const list = this.element.querySelector('#recommendations-list');
    if (list) {
      list.innerHTML = `
        <div class="error-state">
          <p style="color: red;">❌ Error getting recommendations. Please try again.</p>
        </div>
      `;
    }
  }

  private showDeckAnalysis(): void {
    if (!this.deckAnalysis) return;
    
    const analysisPanel = this.element.querySelector('#deck-analysis');
    if (analysisPanel) {
      // Calculate archetype scores (mock multiple archetypes)
      const archetypeScore = Math.round(Math.random() * 40 + 60); // 60-100%
      const secondArchetype = Math.round(Math.random() * 30 + 30); // 30-60%
      const thirdArchetype = Math.round(Math.random() * 20 + 10); // 10-30%
      
      analysisPanel.innerHTML = `
        <div class="archetype-match">
          <h4>🎯 Archetype Match Scores</h4>
          <div class="archetype-scores">
            <div class="archetype-bar">
              <span class="archetype-label">1. ${this.deckAnalysis.archetype}</span>
              <div class="progress-bar">
                <div class="progress-fill" style="width: ${archetypeScore}%"></div>
              </div>
              <span class="archetype-score">${archetypeScore}%</span>
            </div>
            <div class="archetype-bar">
              <span class="archetype-label">2. ${this.getSecondaryArchetype(this.deckAnalysis.archetype)}</span>
              <div class="progress-bar">
                <div class="progress-fill" style="width: ${secondArchetype}%"></div>
              </div>
              <span class="archetype-score">${secondArchetype}%</span>
            </div>
            <div class="archetype-bar">
              <span class="archetype-label">3. Control</span>
              <div class="progress-bar">
                <div class="progress-fill" style="width: ${thirdArchetype}%"></div>
              </div>
              <span class="archetype-score">${thirdArchetype}%</span>
            </div>
          </div>
        </div>
      `;
    }

    const healthPanel = this.element.querySelector('#health-analysis');
    if (healthPanel) {
      const health = this.deckAnalysis.health;
      const recommendations = [
        `${this.deckAnalysis.strategy.charAt(0).toUpperCase() + this.deckAnalysis.strategy.slice(1)} strategy with ${this.deckAnalysis.totalCards} cards`,
        health.curve < 70 ? 'Consider adjusting mana curve distribution' : 'Good mana curve distribution',
        health.colorConsistency < 70 ? `${this.deckAnalysis.colors.length}-color deck may need better mana fixing` : 'Color consistency looks good',
        `Deck archetype analysis suggests '${this.deckAnalysis.archetype}' focus`
      ];
      
      healthPanel.innerHTML = `
        <div class="health-recommendations">
          ${recommendations.map(rec => `<p>• ${rec}</p>`).join('')}
        </div>
        <div class="overall-health">
          <div class="health-circle">
            <span class="health-score">${health.overall}/100</span>
          </div>
        </div>
      `;
    }
  }

  private getSecondaryArchetype(primary: string): string {
    const archetypes = ['Aggro', 'Midrange', 'Control', 'Combo', 'Ramp'];
    const filtered = archetypes.filter(arch => arch.toLowerCase() !== primary.toLowerCase());
    return filtered[Math.floor(Math.random() * filtered.length)];
  }

  private showManaCurve(): void {
    if (!this.deckAnalysis) return;
    
    const curvePanel = this.element.querySelector('#mana-curve');
    if (curvePanel) {
      const curve = this.deckAnalysis.curve;
      const totalCards = this.deckAnalysis.totalCards;
      const maxCount = Math.max(...Object.values(curve));
      
      // Create curve data for CMCs 0-7+
      const curveData = [];
      for (let cmc = 0; cmc <= 7; cmc++) {
        const count = curve[cmc] || 0;
        const percentage = totalCards > 0 ? Math.round((count / totalCards) * 100) : 0;
        curveData.push({
          cmc: cmc === 7 ? '7+' : cmc.toString(),
          count,
          percentage
        });
      }
      
      curvePanel.innerHTML = `
        <div class="mana-curve-chart">
          ${curveData.map(point => `
            <div class="curve-bar">
              <div class="curve-bar-fill" style="height: ${maxCount > 0 ? (point.count / maxCount) * 100 : 0}%"></div>
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

    const displayRecs = this.filteredRecommendations.slice(0, 50); // Show first 50
    const ownedCount = this.filteredRecommendations.filter(rec => rec.costConsideration === 'owned').length;
    const landCount = this.filteredRecommendations.filter(rec => rec.cardType.toLowerCase().includes('land')).length;

    list.innerHTML = `
      <div class="recommendations-header-info">
        <p><strong>Total: ${displayRecs.length} of ${this.recommendations.length} recommendations</strong></p>
        <p><small>${ownedCount} owned • ${landCount} lands • Showing top matches</small></p>
      </div>
      <div class="recommendations-grid">
        ${displayRecs.map(rec => `
          <div class="recommendation-item ${rec.costConsideration === 'owned' ? 'owned' : ''}">
            <div class="rec-header">
              <div class="rec-confidence">
                <span class="confidence-badge">${rec.confidence.toFixed(1)}%</span>
                <span class="synergy-score">Synergy: ${rec.synergyScore.toFixed(1)}%</span>
                <span class="cmc-badge">CMC: ${rec.cmc}</span>
              </div>
            </div>
            <div class="rec-card-info">
              <h4 class="card-name">${rec.cardName} ${rec.costConsideration === 'owned' ? '✓' : ''}</h4>
              <p class="card-type">${rec.cardType}</p>
              <p class="card-cost">${rec.manaCost} • ${rec.rarity}</p>
              <p class="card-scores">Meta: ${rec.metaScore.toFixed(1)}% • Fit: ${rec.deckFit.toFixed(1)}%</p>
            </div>
            <div class="rec-reasons">
              <h5>Reasons/Notes</h5>
              <ul>
                ${rec.reasons.slice(0, 3).map(reason => `<li>${reason}</li>`).join('')}
                ${rec.reasons.length > 3 ? `<li class="more-reasons">+${rec.reasons.length - 3} more reasons...</li>` : ''}
              </ul>
            </div>
            <div class="rec-actions">
              <button class="btn btn-sm btn-secondary" onclick="this.closest('.recommendation-item').dispatchEvent(new CustomEvent('view-details', { bubbles: true, detail: { cardName: '${rec.cardName}' } }))">
                View Details
              </button>
              ${rec.costConsideration === 'owned' ? 
                '<button class="btn btn-sm btn-primary">Add to Deck</button>' : 
                `<button class="btn btn-sm btn-outline" title="Craft ${rec.costConsideration.replace('_', ' ')}">${this.getCraftCost(rec.costConsideration)}</button>`
              }
            </div>
          </div>
        `).join('')}
      </div>
    `;
  }

  private getCraftCost(costConsideration: string): string {
    switch (costConsideration) {
      case 'common_craft': return '🔹 Common';
      case 'uncommon_craft': return '🔸 Uncommon';  
      case 'rare_craft': return '🔶 Rare';
      case 'mythic_craft': return '🔴 Mythic';
      default: return 'Craft';
    }
  }

  private filterRecommendations(): void {
    if (!this.recommendations.length) return;

    const showLands = (this.element.querySelector('#show-lands') as HTMLInputElement)?.checked || false;
    const minConfidence = parseInt((this.element.querySelector('#confidence-slider') as HTMLInputElement)?.value || '75');
    const cardTypeFilter = (this.element.querySelector('#card-type-filter') as HTMLSelectElement)?.value || '';

    this.filteredRecommendations = this.recommendations.filter(rec => {
      // Confidence filter
      if (rec.confidence < minConfidence) return false;
      
      // Land filter
      if (!showLands && rec.cardType.toLowerCase().includes('land')) return false;
      
      // Card type filter
      if (cardTypeFilter && !rec.cardType.toLowerCase().includes(cardTypeFilter.toLowerCase())) return false;
      
      return true;
    });

    this.renderRecommendations();
  }

  // Method to set collection data from parent component
  setCollection(collection: any): void {
    this.collection = collection;
  }

  // Method to set the selected deck from parent component  
  setSelectedDeck(deck: Deck): void {
    this.selectedDeck = deck;
    
    // Update the dropdown selection
    const select = this.element.querySelector('#deck-select') as HTMLSelectElement;
    if (select && deck) {
      select.value = deck.id;
      this.enableAnalysisButtons();
    }
    
    // Clear previous analysis
    this.recommendations = [];
    this.filteredRecommendations = [];
    this.deckAnalysis = null;
  }

  public refresh(): void {
    console.log('Refreshing AI recommendations...');
    this.recommendations = [];
    this.selectedDeck = null;
    
    // Get fresh deck data from the main app
    if ((window as any).app?.getDecks) {
      const freshDecks = (window as any).app.getDecks();
      this.setDecks(freshDecks);
    }
    
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
