"""
AI Recommendations tab for the MTG Arena Deck Manager
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import List, Dict, Optional
import threading
import re

from utils.ai_recommendations import CardRecommendationEngine
from utils.enhanced_recommendations_sync import get_smart_recommendations

class AIRecommendationsTab:
    """AI-powered card recommendations interface"""
    
    def __init__(self, parent, get_current_deck_func, get_collection_func, add_card_callback=None):
        self.parent = parent
        self.get_current_deck = get_current_deck_func
        self.get_collection = get_collection_func
        self.add_card_callback = add_card_callback
        self.recommendation_engine = CardRecommendationEngine()
        self.current_smart_recommendations = []
        self.sort_column = 'confidence'  # Default sort by confidence
        self.sort_reverse = True  # Highest confidence first
        
        # Lazy loading state
        self.total_available_recommendations = 0
        self.is_loading_more = False
        self.has_more_recommendations = True
        self.batch_size = 100  # Fetch recommendations in batches of 100
        
        self.create_widgets()
    
    def create_widgets(self):
        """Create the AI recommendations tab widgets"""
        self.frame = ttk.Frame(self.parent)
        
        # Create deck status header
        self.create_deck_status_header()
        
        # Create main paned window
        paned = ttk.PanedWindow(self.frame, orient=tk.VERTICAL)
        paned.pack(fill=tk.BOTH, expand=True, padx=5, pady=(0, 5))
        
        # Top panel - controls and deck analysis
        top_frame = ttk.Frame(paned)
        paned.add(top_frame, weight=1)
        
        # Bottom panel - recommendations
        bottom_frame = ttk.Frame(paned)
        paned.add(bottom_frame, weight=2)
        
        self.create_control_panel(top_frame)
        self.create_recommendations_panel(bottom_frame)
    
    def create_deck_status_header(self):
        """Create a header showing which deck is being analyzed"""
        header_frame = ttk.Frame(self.frame)
        header_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Main header with deck info
        self.deck_header = ttk.LabelFrame(header_frame, text="🎯 AI Deck Analysis")
        self.deck_header.pack(fill=tk.X, pady=5)
        
        # Deck status frame
        deck_status = ttk.Frame(self.deck_header)
        deck_status.pack(fill=tk.X, padx=10, pady=8)
        
        # Current deck label
        deck_info_frame = ttk.Frame(deck_status)
        deck_info_frame.pack(fill=tk.X)
        
        ttk.Label(deck_info_frame, text="Current Deck:", font=('TkDefaultFont', 9, 'bold')).pack(side=tk.LEFT)
        
        self.current_deck_label = ttk.Label(deck_info_frame, text="No deck selected", 
                                          font=('TkDefaultFont', 11, 'bold'), 
                                          foreground='red')
        self.current_deck_label.pack(side=tk.LEFT, padx=(10, 0))
        
        # Deck details frame
        self.deck_details_frame = ttk.Frame(deck_status)
        self.deck_details_frame.pack(fill=tk.X, pady=(5, 0))
        
        # Format and card count
        self.deck_format_label = ttk.Label(self.deck_details_frame, text="")
        self.deck_format_label.pack(side=tk.LEFT)
        
        self.deck_size_label = ttk.Label(self.deck_details_frame, text="")
        self.deck_size_label.pack(side=tk.LEFT, padx=(20, 0))
        
        # Analysis status
        self.analysis_status_label = ttk.Label(self.deck_details_frame, text="", foreground='blue')
        self.analysis_status_label.pack(side=tk.RIGHT)
        
        # Update the deck info initially
        self.update_deck_header()
    
    def update_deck_header(self):
        """Update the deck header with current deck information"""
        current_deck = self.get_current_deck()
        
        if current_deck:
            # Update deck name with visual indicator
            self.current_deck_label.config(
                text=f"📋 {current_deck.name}", 
                foreground='darkgreen'
            )
            
            # Update deck details
            format_text = f"Format: {current_deck.format}"
            self.deck_format_label.config(text=format_text)
            
            mainboard_count = sum(card.quantity for card in current_deck.get_mainboard_cards())
            sideboard_count = sum(card.quantity for card in current_deck.get_sideboard_cards())
            size_text = f"Cards: {mainboard_count} main"
            if sideboard_count > 0:
                size_text += f", {sideboard_count} side"
            self.deck_size_label.config(text=size_text)
            
            # Show colors
            color_distribution = current_deck.get_color_distribution()
            if color_distribution:
                color_symbols = {'W': '[W]', 'U': '[U]', 'B': '[B]', 'R': '[R]', 'G': '[G]'}
                color_list = []
                for color in sorted(color_distribution.keys()):
                    symbol = color_symbols.get(color, color)
                    if symbol:
                        color_list.append(symbol)
                color_display = ''.join(color_list)
                self.deck_format_label.config(text=f"{format_text} | Colors: {color_display}")
            
            self.analysis_status_label.config(text="Ready for analysis")
            
        else:
            # No deck selected
            self.current_deck_label.config(
                text="❌ No deck selected", 
                foreground='red'
            )
            self.deck_format_label.config(text="Select a deck in the 'Decks' tab to begin analysis")
            self.deck_size_label.config(text="")
            self.analysis_status_label.config(text="")
    
    def on_tab_focus(self):
        """Called when the AI recommendations tab gets focus"""
        self._delayed_tab_update()
    
    def _delayed_tab_update(self):
        """Update tab content when focused"""
        # Only update header if deck actually changed
        current_deck = self.get_current_deck()
        if hasattr(self, '_last_deck_id') and current_deck:
            if self._last_deck_id == id(current_deck):
                return  # No change, skip update
        
        self._last_deck_id = id(current_deck) if current_deck else None
        self.update_deck_header()
    
    def get_frame(self):
        """Get the frame for this tab - useful for external access"""
        return self.frame
    
    def create_control_panel(self, parent):
        """Create the control and analysis panel"""
        # Analysis frame
        analysis_frame = ttk.LabelFrame(parent, text="Deck Analysis")
        analysis_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Create notebook for different analysis views
        analysis_notebook = ttk.Notebook(analysis_frame)
        analysis_notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Archetype & Health Score analysis tab
        archetype_frame = ttk.Frame(analysis_notebook)
        analysis_notebook.add(archetype_frame, text="Archetype & Health")
        
        self.archetype_text = tk.Text(archetype_frame, height=6, wrap=tk.WORD)
        archetype_scroll = ttk.Scrollbar(archetype_frame, orient=tk.VERTICAL, command=self.archetype_text.yview)
        self.archetype_text.configure(yscrollcommand=archetype_scroll.set)
        
        self.archetype_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        archetype_scroll.pack(side=tk.RIGHT, fill=tk.Y, pady=5)
        
        # Visual Mana Curve tab
        curve_frame = ttk.Frame(analysis_notebook)
        analysis_notebook.add(curve_frame, text="Mana Curve")
        
        # Create canvas for visual mana curve
        self.curve_canvas = tk.Canvas(curve_frame, height=200, bg='white')
        self.curve_canvas.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Card Synergy Matrix tab
        synergy_frame = ttk.Frame(analysis_notebook)
        analysis_notebook.add(synergy_frame, text="Card Synergy")
        
        self.synergy_text = tk.Text(synergy_frame, height=6, wrap=tk.WORD)
        synergy_scroll = ttk.Scrollbar(synergy_frame, orient=tk.VERTICAL, command=self.synergy_text.yview)
        self.synergy_text.configure(yscrollcommand=synergy_scroll.set)
        
        self.synergy_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        synergy_scroll.pack(side=tk.RIGHT, fill=tk.Y, pady=5)
        

        
        # Control buttons
        control_frame = ttk.Frame(parent)
        control_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(control_frame, text="Analyze Current Deck", command=self.analyze_deck).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="Get Recommendations", command=self.get_recommendations).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="Refresh", command=self.refresh_all).pack(side=tk.LEFT, padx=5)
        
        # Format selection
        ttk.Label(control_frame, text="Format:").pack(side=tk.LEFT, padx=(20, 5))
        self.format_var = tk.StringVar(value="Standard")
        format_combo = ttk.Combobox(control_frame, textvariable=self.format_var, width=12)
        format_combo['values'] = ('Standard', 'Historic', 'Explorer', 'Pioneer', 'Modern', 'Legacy', 'Commander', 'EDH', 'Brawl')
        format_combo.pack(side=tk.LEFT, padx=5)
        
        # Loading indicator
        self.loading_var = tk.StringVar(value="")
        self.loading_label = ttk.Label(control_frame, textvariable=self.loading_var, foreground="dim gray")
        self.loading_label.pack(side=tk.RIGHT, padx=5)
    
    def create_recommendations_panel(self, parent):
        """Create the recommendations display panel"""
        rec_frame = ttk.LabelFrame(parent, text="AI Card Recommendations")
        rec_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Recommendation list
        columns = ('Card', 'Confidence', 'Synergy', 'CMC', 'Reasons')
        self.rec_tree = ttk.Treeview(rec_frame, columns=columns, show='headings', height=12)
        
        # Configure columns
        self.rec_tree.heading('Card', text='Card Name')
        self.rec_tree.heading('Confidence', text='Confidence')
        self.rec_tree.heading('Synergy', text='Synergy')
        self.rec_tree.heading('CMC', text='CMC')
        self.rec_tree.heading('Reasons', text='Reasons/Notes')
        
        self.rec_tree.column('Card', width=150)
        self.rec_tree.column('Confidence', width=80)
        self.rec_tree.column('Synergy', width=70)
        self.rec_tree.column('CMC', width=50)
        self.rec_tree.column('Reasons', width=400)  # Expanded to take up space from removed Archetype Fit
        
        # Scrollbar
        rec_scrollbar = ttk.Scrollbar(rec_frame, orient=tk.VERTICAL, command=self.rec_tree.yview)
        self.rec_tree.configure(yscrollcommand=rec_scrollbar.set)
        
        # Pack
        self.rec_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        rec_scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=5)
        
        # Context menu for recommendations
        self.create_rec_context_menu()
        self.rec_tree.bind("<Button-3>", self.show_rec_context_menu)
        self.rec_tree.bind("<Double-Button-1>", self.view_card_details)
        self.rec_tree.bind("<Button-1>", self.on_column_click)
        
        # Bind scroll events for lazy loading
        self.rec_tree.bind('<MouseWheel>', self.on_mousewheel)
        self.rec_tree.bind('<Button-4>', self.on_mousewheel)  # Linux scroll up
        self.rec_tree.bind('<Button-5>', self.on_mousewheel)  # Linux scroll down
        
        # Recommendation controls - moved below the table for better visibility
        rec_controls = ttk.Frame(parent)  # Changed from rec_frame to parent
        rec_controls.pack(fill=tk.X, padx=5, pady=5)

        # Filter controls
        filter_frame = ttk.Frame(rec_controls)
        filter_frame.pack(side=tk.LEFT, padx=5)
        
        # Land visibility toggle
        self.show_lands_var = tk.BooleanVar(value=True)
        lands_checkbox = ttk.Checkbutton(filter_frame, text="Show Lands", 
                                        variable=self.show_lands_var,
                                        command=self.toggle_land_visibility)
        lands_checkbox.pack(side=tk.LEFT, padx=5)
        
        # Confidence filter
        ttk.Label(filter_frame, text="Min Confidence:").pack(side=tk.LEFT, padx=(15, 5))
        self.min_confidence_var = tk.DoubleVar(value=0.0)
        confidence_scale = ttk.Scale(filter_frame, from_=0.0, to=1.0, orient=tk.HORIZONTAL, 
                                   length=100, variable=self.min_confidence_var, command=self.filter_recommendations)
        confidence_scale.pack(side=tk.LEFT, padx=5)
        
        self.confidence_label = ttk.Label(filter_frame, text="0%")
        self.confidence_label.pack(side=tk.LEFT, padx=5)
        
        # Card type filter
        ttk.Label(filter_frame, text="Card Type:").pack(side=tk.LEFT, padx=(15, 5))
        self.card_type_var = tk.StringVar(value="All")
        type_combo = ttk.Combobox(filter_frame, textvariable=self.card_type_var, width=12, state="readonly")
        type_combo['values'] = ('All', 'Creature', 'Instant', 'Sorcery', 'Enchantment', 'Artifact', 'Planeswalker', 'Land')
        type_combo.pack(side=tk.LEFT, padx=5)
        type_combo.bind('<<ComboboxSelected>>', lambda e: self.filter_recommendations())
        
        # Total recommendations count
        self.total_count_label = ttk.Label(rec_controls, text="Total: 0 recommendations", 
                                         font=('TkDefaultFont', 9, 'bold'), foreground='black')
        self.total_count_label.pack(side=tk.RIGHT, padx=5)
        
        # Load More button (for manual loading)
        self.load_more_button = ttk.Button(rec_controls, text="Load More", 
                                         command=self.load_more_batch, 
                                         state='disabled')
        self.load_more_button.pack(side=tk.RIGHT, padx=5)
        
        # Update confidence label
        def update_confidence_label(*args):
            self.confidence_label.config(text=f"{int(self.min_confidence_var.get() * 100)}%")
        
        self.min_confidence_var.trace('w', update_confidence_label)
    
    def create_rec_context_menu(self):
        """Create context menu for recommendations"""
        self.rec_context_menu = tk.Menu(self.frame, tearoff=0)
        self.rec_context_menu.add_command(label="🏠 Add to Mainboard", command=self.add_to_mainboard)
        self.rec_context_menu.add_command(label="📋 Add to Sideboard", command=self.add_to_sideboard)
        self.rec_context_menu.add_separator()
        self.rec_context_menu.add_command(label="🔍 View Card Details", command=self.view_card_details)
        self.rec_context_menu.add_command(label="❓ Why This Card?", command=self.explain_recommendation)
        self.rec_context_menu.add_separator()
        self.rec_context_menu.add_command(label="🎯 Similar Cards", command=self.find_similar_cards)
    
    def on_column_click(self, event):
        """Handle column header clicks for sorting"""
        region = self.rec_tree.identify_region(event.x, event.y)
        if region == "heading":
            column = self.rec_tree.identify("column", event.x, event.y)
            column_names = {
                '#1': 'name',
                '#2': 'confidence', 
                '#3': 'synergy',
                '#4': 'cmc',
                '#5': 'fit',
                '#6': 'reasons'
            }
            
            if column in column_names:
                new_sort_column = column_names[column]
                
                # Toggle sort direction if same column, otherwise default to descending for scores
                if new_sort_column == self.sort_column:
                    self.sort_reverse = not self.sort_reverse
                else:
                    self.sort_column = new_sort_column
                    self.sort_reverse = True if new_sort_column != 'name' else False
                
                self.refresh_display()
    
    def on_mousewheel(self, event):
        """Handle mouse wheel scrolling to trigger lazy loading"""
        # Check if we're near the bottom and should load more
        self.parent.after_idle(self.check_scroll_position)
    
    def check_scroll_position(self, event=None):
        """Check if we're near the bottom of the tree and should load more recommendations"""
        if not self.has_more_recommendations or self.is_loading_more:
            return
            
        try:
            # Get the scrollbar associated with the treeview
            scrollbar = None
            for child in self.rec_tree.master.winfo_children():
                if isinstance(child, ttk.Scrollbar):
                    scrollbar = child
                    break
            
            if scrollbar:
                # Get the position of the scrollbar (0.0 to 1.0)
                scroll_position = scrollbar.get()
                if len(scroll_position) >= 2:
                    scroll_top, scroll_bottom = scroll_position[0], scroll_position[1]
                    
                    # If we're near the bottom (85% scrolled), load more
                    if scroll_bottom > 0.85:
                        print("Near bottom of list, loading more recommendations...")
                        self.load_more_batch()
        except Exception as e:
            print(f"Error checking scroll position: {e}")
    
    def on_tree_select(self, event=None):
        """Handle tree selection changes and check for scroll position"""
        self.check_scroll_position()
    
    def refresh_display(self):
        """Refresh the recommendations display with current sort and filter settings"""
        # Simply refresh the enhanced recommendations display
        if self.current_smart_recommendations:
            self.display_enhanced_recommendations()
    
    def show_rec_context_menu(self, event):
        """Show context menu for recommendations"""
        item = self.rec_tree.identify_row(event.y)
        if item:
            self.rec_tree.selection_set(item)
            self.rec_context_menu.post(event.x_root, event.y_root)
    
    def analyze_deck(self):
        """Analyze the current deck"""
        current_deck = self.get_current_deck()
        if not current_deck:
            messagebox.showwarning("Warning", "No deck selected")
            return
        
        # Update header to show current deck
        self.update_deck_header()
        
        self.loading_var.set("Analyzing...")
        self.analysis_status_label.config(text="🔍 Analyzing deck...", foreground='cornflower blue')
        self.frame.update()
        
        def analyze():
            try:
                # Archetype analysis
                archetype_scores = self.recommendation_engine.analyze_deck_archetype(current_deck)
                archetype_text = f"🏗️ DECK ARCHETYPE ANALYSIS for '{current_deck.name}'\n"
                archetype_text += "=" * 60 + "\n\n"
                
                if archetype_scores:
                    sorted_archetypes = sorted(archetype_scores.items(), key=lambda x: x[1], reverse=True)
                    archetype_text += "📊 Archetype Match Scores:\n"
                    for i, (archetype, score) in enumerate(sorted_archetypes[:5], 1):  # Show top 5
                        percentage = score * 100
                        bar = "█" * int(percentage / 10) + "▒" * (10 - int(percentage / 10))
                        archetype_text += f"  {i}. {archetype:15} [{bar}] {percentage:.1f}%\n"
                        
                        if archetype in self.recommendation_engine.card_db.archetype_templates:
                            template = self.recommendation_engine.card_db.archetype_templates[archetype]
                            archetype_text += f"      💡 {template['description']}\n"
                    
                    primary_archetype = sorted_archetypes[0][0]
                    primary_score = sorted_archetypes[0][1] * 100
                    archetype_text += f"\n🎯 PRIMARY ARCHETYPE: {primary_archetype.upper()}"
                    archetype_text += f" ({primary_score:.1f}% match)\n"
                else:
                    archetype_text += "❓ Unable to identify clear archetype pattern.\n"
                    archetype_text += "   This deck may be experimental or need refinement.\n"
                
                
                # Update UI in main thread
                def update_ui():
                    # Update archetype text with health score
                    enhanced_archetype_text = self._add_deck_health_score(current_deck, archetype_text)
                    self.archetype_text.delete(1.0, tk.END)
                    self.archetype_text.insert(1.0, enhanced_archetype_text)
                    
                    # Update visual mana curve
                    self._draw_visual_mana_curve(current_deck)
                    
                    # Update card synergy analysis
                    synergy_analysis = self._analyze_card_synergies(current_deck)
                    self.synergy_text.delete(1.0, tk.END)
                    self.synergy_text.insert(1.0, synergy_analysis)
                    
                    self.loading_var.set("")
                    self.analysis_status_label.config(text="✅ Analysis complete", foreground='black')
                
                self.frame.after(0, update_ui)
                
            except Exception as e:
                def show_error():
                    messagebox.showerror("Analysis Error", f"Analysis failed: {str(e)}")
                    self.loading_var.set("")
                    self.analysis_status_label.config(text="❌ Analysis failed", foreground='red')
                
                self.frame.after(0, show_error)
        
        # Run analysis in background thread
        thread = threading.Thread(target=analyze)
        thread.daemon = True
        thread.start()
    
    def _add_deck_health_score(self, deck, existing_text):
        """Add comprehensive deck health score to the archetype analysis"""
        if not deck:
            return existing_text
        
        # Calculate various health metrics
        mainboard = deck.get_mainboard_cards()
        if not mainboard:
            return existing_text + "\n⚠️ No mainboard cards to analyze."
        
        total_cards = sum(card.quantity for card in mainboard)
        curve = deck.get_mana_curve()
        colors = deck.get_color_distribution()
        types = deck.get_type_distribution()
        
        # Curve health (0-100)
        curve_score = self._calculate_curve_health(curve, total_cards)
        
        # Color consistency (0-100)
        color_score = self._calculate_color_consistency(colors, total_cards)
        
        # Card balance (0-100) - threats vs answers
        balance_score = self._calculate_card_balance(types, total_cards)
        
        # Mana efficiency (0-100)
        efficiency_score = self._calculate_mana_efficiency(curve, total_cards)
        
        # Overall health score
        overall_score = (curve_score + color_score + balance_score + efficiency_score) / 4
        
        # Create health score display
        health_text = f"\n🏥 DECK HEALTH ANALYSIS\n"
        health_text += "=" * 30 + "\n\n"
        
        # Overall score with visual indicator
        health_emoji = "🟢" if overall_score >= 80 else "🟡" if overall_score >= 60 else "🔴"
        health_text += f"📊 OVERALL HEALTH: {health_emoji} {overall_score:.0f}/100\n\n"
        
        # Individual scores
        health_text += f"📈 Mana Curve:     {self._get_score_bar(curve_score)} {curve_score:.0f}/100\n"
        health_text += f"🎨 Color Balance:  {self._get_score_bar(color_score)} {color_score:.0f}/100\n"
        health_text += f"⚖️  Card Balance:   {self._get_score_bar(balance_score)} {balance_score:.0f}/100\n"
        health_text += f"⚡ Mana Efficiency: {self._get_score_bar(efficiency_score)} {efficiency_score:.0f}/100\n\n"
        
        # Health recommendations
        if overall_score < 70:
            health_text += "💡 HEALTH RECOMMENDATIONS:\n"
            if curve_score < 60:
                health_text += "   • Consider adjusting mana curve distribution\n"
            if color_score < 60:
                health_text += "   • Improve mana base or reduce color requirements\n"
            if balance_score < 60:
                health_text += "   • Balance threats and answers better\n"
            if efficiency_score < 60:
                health_text += "   • Consider more efficient mana costs\n"
        else:
            health_text += "✅ Deck health looks good! Minor optimizations available.\n"
        
        return health_text + "\n" + existing_text
    
    def _calculate_curve_health(self, curve, total_cards):
        """Calculate mana curve health score (0-100)"""
        if total_cards == 0:
            return 0
        
        # Ideal curve percentages for a balanced deck
        ideal = {0: 0.05, 1: 0.15, 2: 0.25, 3: 0.20, 4: 0.15, 5: 0.10, 6: 0.05, 7: 0.05}
        
        score = 100
        for cmc, ideal_pct in ideal.items():
            actual_pct = curve.get(cmc, 0) / total_cards
            # Penalize deviations from ideal
            deviation = abs(actual_pct - ideal_pct)
            score -= deviation * 200  # Scale penalty
        
        return max(0, min(100, score))
    
    def _calculate_color_consistency(self, colors, total_cards):
        """Calculate color consistency score (0-100)"""
        if not colors or total_cards == 0:
            return 100  # Colorless is perfectly consistent
        
        num_colors = len(colors)
        if num_colors == 1:
            return 100  # Mono-color is perfectly consistent
        elif num_colors == 2:
            return 85   # Two-color is very good
        elif num_colors == 3:
            return 70   # Three-color is okay but challenging
        elif num_colors == 4:
            return 50   # Four-color is difficult
        else:
            return 30   # Five-color is very challenging
    
    def _calculate_card_balance(self, types, total_cards):
        """Calculate balance between threats and answers (0-100)"""
        if total_cards == 0:
            return 0
        
        # Categorize card types
        threats = types.get('Creature', 0) + types.get('Planeswalker', 0)
        answers = types.get('Instant', 0) + types.get('Sorcery', 0)
        support = types.get('Artifact', 0) + types.get('Enchantment', 0)
        
        threat_ratio = threats / total_cards
        answer_ratio = answers / total_cards
        
        # Ideal ratios vary by archetype, but aim for reasonable balance
        if threat_ratio < 0.2:  # Too few threats
            return 60
        elif threat_ratio > 0.8:  # Too many threats, not enough interaction
            return 60
        elif answer_ratio < 0.1:  # Too few answers
            return 70
        else:
            return 90  # Good balance
    
    def _calculate_mana_efficiency(self, curve, total_cards):
        """Calculate mana efficiency score (0-100)"""
        if total_cards == 0:
            return 0
        
        # Penalize high-cost cards without ramp/fixing
        high_cost_cards = sum(count for cmc, count in curve.items() if cmc >= 5)
        high_cost_ratio = high_cost_cards / total_cards
        
        if high_cost_ratio > 0.3:  # Too many expensive cards
            return 60
        elif high_cost_ratio < 0.05:  # Too few win conditions
            return 75
        else:
            return 90
    
    def _get_score_bar(self, score):
        """Get visual score bar for health metrics"""
        filled = int(score / 10)
        bar = "█" * filled + "░" * (10 - filled)
        return f"[{bar}]"
    
    def _draw_visual_mana_curve(self, deck):
        """Draw visual mana curve chart on canvas"""
        if not deck:
            return
        
        # Clear canvas
        self.curve_canvas.delete("all")
        
        # Get curve data
        curve = deck.get_mana_curve()
        if not curve:
            self.curve_canvas.create_text(
                self.curve_canvas.winfo_width() / 2, 
                self.curve_canvas.winfo_height() / 2,
                text="No mana curve data available", 
                font=("Arial", 12), 
                fill="gray"
            )
            return
        
        # Canvas dimensions
        width = 400
        height = 180
        margin = 40
        bar_width = 35
        
        # Update canvas size
        self.curve_canvas.config(width=width, height=height)
        
        # Calculate max value for scaling
        max_count = max(curve.values()) if curve else 1
        if max_count == 0:
            max_count = 1
        
        # Draw title
        self.curve_canvas.create_text(width/2, 20, text="Mana Curve Distribution", 
                                    font=("Arial", 12, "bold"), fill="black")
        
        # Draw bars for CMCs 0-7+
        colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7', '#DDA0DD', '#F0A0A0', '#FFB74D']
        
        for cmc in range(8):
            count = curve.get(cmc, 0)
            if count > 0 or cmc <= 4:  # Always show 0-4, only show higher if they have cards
                # Calculate bar position and height
                x = margin + cmc * (bar_width + 5)
                bar_height = (count / max_count) * (height - 80) if count > 0 else 3  # Minimum 3px for empty bars
                y = height - margin - bar_height
                
                # Draw bar
                color = colors[cmc % len(colors)]
                self.curve_canvas.create_rectangle(x, y, x + bar_width, height - margin, 
                                                 fill=color, outline="black", width=1)
                
                # Draw count on top of bar
                if count > 0:
                    self.curve_canvas.create_text(x + bar_width/2, y - 10, 
                                                text=str(count), font=("Arial", 10, "bold"))
                
                # Draw CMC label
                cmc_label = f"{cmc}+" if cmc >= 7 else str(cmc)
                self.curve_canvas.create_text(x + bar_width/2, height - margin + 15, 
                                            text=cmc_label, font=("Arial", 10))
        
        # Draw percentage indicators
        total_cards = sum(curve.values())
        if total_cards > 0:
            y_pos = height - 10
            x_start = margin
            for cmc in range(8):
                count = curve.get(cmc, 0)
                if count > 0:
                    percentage = (count / total_cards) * 100
                    x = x_start + cmc * (bar_width + 5)
                    self.curve_canvas.create_text(x + bar_width/2, y_pos, 
                                                text=f"{percentage:.0f}%", 
                                                font=("Arial", 8), fill="gray")
    
    def _analyze_card_synergies(self, deck):
        """Analyze card synergies and relationships in the deck"""
        if not deck:
            return "No deck to analyze."
        
        mainboard = deck.get_mainboard_cards()
        if not mainboard:
            return "No cards in mainboard to analyze."
        
        synergy_text = f"🔗 CARD SYNERGY MATRIX for '{deck.name}'\n"
        synergy_text += "=" * 50 + "\n\n"
        
        # Define synergy keywords and their relationships
        synergy_keywords = {
            'tribal': ['human', 'elf', 'goblin', 'zombie', 'wizard', 'warrior', 'soldier', 'beast'],
            'graveyard': ['graveyard', 'exile', 'discard', 'mill', 'delve', 'flashback'],
            'artifacts': ['artifact', 'equipment', 'vehicle', 'treasure', 'food'],
            'spells': ['instant', 'sorcery', 'spell', 'prowess', 'storm'],
            'lifegain': ['lifegain', 'lifelink', 'gain life', 'life total'],
            'tokens': ['token', 'create', 'populate'],
            'counters': ['+1/+1', 'counter', 'proliferate'],
            'combat': ['first strike', 'double strike', 'trample', 'vigilance', 'haste'],
            'draw': ['draw', 'card draw', 'library'],
            'mana': ['mana', 'ramp', 'treasure', 'ritual']
        }
        
        # Analyze cards for synergy themes
        theme_cards = {}
        for theme, keywords in synergy_keywords.items():
            theme_cards[theme] = []
            
            for deck_card in mainboard:
                card = deck_card.card
                # Check card name, type, and text for synergy keywords
                card_text = f"{card.name} {card.card_type} {card.text or ''}".lower()
                
                for keyword in keywords:
                    if keyword in card_text:
                        if deck_card not in theme_cards[theme]:
                            theme_cards[theme].append(deck_card)
                        break
        
        # Display synergy analysis
        synergy_found = False
        
        for theme, cards in theme_cards.items():
            if len(cards) >= 2:  # Need at least 2 cards to have synergy
                synergy_found = True
                synergy_text += f"🎯 {theme.upper()} SYNERGY ({len(cards)} cards):\n"
                
                for deck_card in sorted(cards, key=lambda x: x.card.name):
                    synergy_text += f"   • {deck_card.quantity}x {deck_card.card.name}"
                    if deck_card.card.card_type:
                        synergy_text += f" ({deck_card.card.card_type.split()[0]})"
                    synergy_text += "\n"
                
                # Calculate synergy strength
                synergy_strength = min(len(cards) / 4, 1.0) * 100  # Scale to percentage
                strength_bar = "█" * int(synergy_strength / 20) + "░" * (5 - int(synergy_strength / 20))
                synergy_text += f"   💪 Synergy Strength: [{strength_bar}] {synergy_strength:.0f}%\n\n"
        
        if not synergy_found:
            synergy_text += "🔍 LIMITED SYNERGIES DETECTED\n\n"
            synergy_text += "This deck appears to focus on individual card power rather than\n"
            synergy_text += "synergistic interactions. Consider these synergy opportunities:\n\n"
            
            # Analyze deck for potential synergy improvements
            colors = deck.get_color_distribution()
            types = deck.get_type_distribution()
            
            if types.get('Creature', 0) >= 8:
                synergy_text += "• TRIBAL SYNERGY: With many creatures, consider tribal themes\n"
            
            if 'U' in colors and (types.get('Instant', 0) + types.get('Sorcery', 0)) >= 6:
                synergy_text += "• SPELL SYNERGY: Blue + spells suggest prowess or spell-based strategy\n"
            
            if 'B' in colors:
                synergy_text += "• GRAVEYARD SYNERGY: Black offers many graveyard-based interactions\n"
                
            if len(colors) >= 3:
                synergy_text += "• MULTICOLOR SYNERGY: Consider cards that reward playing multiple colors\n"
        else:
            # Suggest additional synergies
            synergy_text += "💡 SYNERGY EXPANSION OPPORTUNITIES:\n\n"
            
            strongest_theme = max(theme_cards.keys(), 
                                key=lambda x: len(theme_cards[x]) if theme_cards[x] else 0)
            if theme_cards[strongest_theme]:
                synergy_text += f"• Double down on {strongest_theme} synergy for maximum effect\n"
                synergy_text += f"• Look for cards that explicitly reward {strongest_theme} strategies\n"
        
        # Card interaction matrix (simplified)
        synergy_text += "\n" + "=" * 50 + "\n"
        synergy_text += "🎴 NOTABLE CARD INTERACTIONS:\n\n"
        
        # Look for obvious interactions (simplified heuristic)
        interaction_count = 0
        for i, deck_card1 in enumerate(mainboard):
            for deck_card2 in mainboard[i+1:]:
                card1_text = (deck_card1.card.text or "").lower()
                card2_text = (deck_card2.card.text or "").lower()
                
                # Simple interaction detection
                if (("creature" in card1_text and "creatures" in card2_text) or
                    ("instant" in card1_text and "sorcery" in card2_text) or
                    ("artifact" in card1_text and "artifact" in card2_text)):
                    
                    if interaction_count < 5:  # Limit to top 5 interactions
                        synergy_text += f"• {deck_card1.card.name} ↔ {deck_card2.card.name}\n"
                        interaction_count += 1
        
        if interaction_count == 0:
            synergy_text += "No obvious card interactions detected.\n"
            synergy_text += "Focus on individual card quality and mana curve.\n"
        
        return synergy_text
    
    def _on_curve_canvas_resize(self, event):
        """Handle canvas resize event to redraw mana curve"""
        current_deck = self.get_current_deck()
        if current_deck:
            # Small delay to ensure canvas dimensions are updated
            self.frame.after(100, lambda: self._draw_visual_mana_curve(current_deck))
    
    def get_recommendations(self):
        """Get AI card recommendations using lazy loading for better performance"""
        current_deck = self.get_current_deck()
        if not current_deck:
            messagebox.showwarning("Warning", "No deck selected")
            return
        
        # Update header to show current deck
        self.update_deck_header()
        
        # Reset lazy loading state
        self.current_smart_recommendations = []
        self.total_available_recommendations = 0
        self.has_more_recommendations = True
        self.is_loading_more = False
        
        # Clear display
        for item in self.rec_tree.get_children():
            self.rec_tree.delete(item)
        
        self.loading_var.set("Getting enhanced AI recommendations...")
        self.analysis_status_label.config(text="🤖 Generating Scryfall-powered recommendations...", foreground='dim gray')
        self.frame.update()
        
        def get_recs():
            try:
                collection = self.get_collection()
                format_name = self.format_var.get()
                
                # Load initial batch of recommendations
                enhanced_recommendations = get_smart_recommendations(
                    current_deck, collection, self.batch_size, format_name
                )
                
                print(f"Initial batch loaded: {len(enhanced_recommendations)} recommendations")
                
                def update_recs():
                    self.current_smart_recommendations = enhanced_recommendations
                    self.total_available_recommendations = len(enhanced_recommendations)
                    
                    # Check if we likely have more recommendations available
                    if len(enhanced_recommendations) >= self.batch_size * 0.9:
                        self.has_more_recommendations = True
                    else:
                        self.has_more_recommendations = False
                    
                    self.display_enhanced_recommendations()
                    self.loading_var.set("")
                    
                    status_msg = f"✅ {len(enhanced_recommendations)} recommendations loaded"
                    if self.has_more_recommendations:
                        status_msg += " (scroll down for more)"
                    self.analysis_status_label.config(text=status_msg, foreground='black')
                    
                    # Update Load More button state
                    if self.has_more_recommendations:
                        self.load_more_button.config(state='normal')
                    else:
                        self.load_more_button.config(state='disabled')
                
                self.frame.after(0, update_recs)
                
            except Exception as e:
                def show_error():
                    messagebox.showerror("Recommendation Error", f"Enhanced recommendations failed: {str(e)}")
                    self.loading_var.set("")
                    self.analysis_status_label.config(text="❌ Recommendations failed", foreground='red')
                
                self.frame.after(0, show_error)
        
        thread = threading.Thread(target=get_recs)
        thread.daemon = True
        thread.start()
    
    def load_more_batch(self):
        """Load the next batch of recommendations"""
        if self.is_loading_more or not self.has_more_recommendations:
            return
            
        current_deck = self.get_current_deck()
        if not current_deck:
            return
            
        def get_more_recs():
            try:
                self.is_loading_more = True
                self.loading_var.set("Loading more recommendations...")
                
                # Update Load More button to show loading
                self.load_more_button.config(text="Loading...", state='disabled')
                
                collection = self.get_collection()
                format_name = self.format_var.get()
                
                # Get next batch by requesting more recommendations
                # Since get_smart_recommendations uses randomization, we'll get different results
                current_count = len(self.current_smart_recommendations)
                total_desired = current_count + self.batch_size
                
                all_recommendations = get_smart_recommendations(
                    current_deck, collection, total_desired, format_name
                )
                
                # Extract only the new recommendations (beyond what we already have)
                additional_recommendations = all_recommendations[current_count:]
                
                print(f"Additional batch: {len(additional_recommendations)} new recommendations")
                
                # Filter out duplicates
                existing_names = {rec.card_name for rec in self.current_smart_recommendations}
                new_recommendations = [rec for rec in additional_recommendations 
                                     if rec.card_name not in existing_names]
                
                print(f"After deduplication: {len(new_recommendations)} unique new recommendations")
                
                def update_display():
                    if new_recommendations:
                        self.current_smart_recommendations.extend(new_recommendations)
                        self.total_available_recommendations = len(self.current_smart_recommendations)
                        
                        # Check if we should continue loading more
                        if len(new_recommendations) < self.batch_size * 0.5:
                            self.has_more_recommendations = False
                        
                        self.display_enhanced_recommendations()
                        
                        status_msg = f"✅ {len(self.current_smart_recommendations)} recommendations loaded"
                        if self.has_more_recommendations:
                            status_msg += " (scroll for more)"
                        self.analysis_status_label.config(text=status_msg, foreground='black')
                        
                        # Update Load More button state
                        self.load_more_button.config(
                            text="Load More", 
                            state='normal' if self.has_more_recommendations else 'disabled'
                        )
                    else:
                        self.has_more_recommendations = False
                        self.analysis_status_label.config(
                            text=f"✅ {len(self.current_smart_recommendations)} recommendations (all loaded)", 
                            foreground='green'
                        )
                        
                        # Disable Load More button
                        self.load_more_button.config(text="Load More", state='disabled')
                    
                    self.loading_var.set("")
                    self.is_loading_more = False
                    
                    # Reset Load More button
                    self.load_more_button.config(text="Load More")
                
                self.frame.after(0, update_display)
                
            except Exception as e:
                print(f"Error loading more recommendations: {str(e)}")
                self.frame.after(0, lambda: self.loading_var.set(""))
                self.frame.after(0, lambda: self.load_more_button.config(text="Load More", state='normal'))
                self.is_loading_more = False
        
        thread = threading.Thread(target=get_more_recs)
        thread.daemon = True
        thread.start()
    
    def display_enhanced_recommendations(self):
        """Display the enhanced AI recommendations"""
        if not self.current_smart_recommendations:
            self.update_total_count(0, 0)
            return
        
        # Filter by minimum confidence
        min_confidence = self.min_confidence_var.get()
        filtered_recs = [r for r in self.current_smart_recommendations if r.confidence >= min_confidence]
        
        # Filter by land visibility if toggled off
        if not self.show_lands_var.get():
            # Filter out lands (cards with "Land" in their card_type)
            filtered_recs = [r for r in filtered_recs if "Land" not in r.card_type]
        
        # Filter by card type if not "All"
        selected_type = self.card_type_var.get()
        if selected_type != "All":
            filtered_recs = [r for r in filtered_recs if self._matches_card_type(r.card_type, selected_type)]
        
        # Clear existing items before updating
        for item in self.rec_tree.get_children():
            self.rec_tree.delete(item)
        
        # Update total count display
        total_loaded = len(self.current_smart_recommendations)
        total_displayed = len(filtered_recs)
        self.update_total_count(total_loaded, total_displayed)
        
        # Sort recommendations
        sort_key_map = {
            'name': lambda r: r.card_name.lower(),
            'confidence': lambda r: r.confidence,
            'synergy': lambda r: r.synergy_score,
            'cmc': lambda r: 0 if "Land" in r.card_type else getattr(r, 'cmc', 0),  # Lands sort as CMC 0
            'reasons': lambda r: len(r.reasons)
        }
        
        if self.sort_column in sort_key_map:
            filtered_recs.sort(key=sort_key_map[self.sort_column], reverse=self.sort_reverse)
        
        # Update status info for lazy loading
        if self.has_more_recommendations:
            info_text = f"Showing {len(filtered_recs)} results (more available - scroll down to load)"
        else:
            info_text = f"Showing {len(filtered_recs)} results (all loaded)"
        
        # Display all filtered recommendations (no pagination with lazy loading)
        for rec in filtered_recs:
            # Determine ownership status and display
            if rec.cost_consideration == "owned":
                # Owned cards: clean display without craft icons
                card_display = rec.card_name
                ownership_tag = 'owned'
            else:
                # Craftable cards: show craft icons
                craft_icons = {
                    "common_craft": "🔨", 
                    "uncommon_craft": "🔧", 
                    "rare_craft": "💎", 
                    "mythic_craft": "👑"
                }
                craft_icon = craft_icons.get(rec.cost_consideration, "🔨")
                card_display = f"{craft_icon} {rec.card_name}"
                ownership_tag = 'craftable'
            
            # Add confidence-based coloring
            if rec.confidence >= 0.8:
                confidence_tag = 'high_confidence'
            elif rec.confidence >= 0.6:
                confidence_tag = 'medium_confidence'
            else:
                confidence_tag = 'low_confidence'
            
            # Combine tags for ownership and confidence
            tags = (ownership_tag, confidence_tag)
            
            # Add legality info if available
            if rec.legality:
                format_name = self.format_var.get().lower()
                legality_status = rec.legality.get(format_name, "unknown")
                if legality_status == "legal":
                    card_display += " ✓"
                elif legality_status == "not_legal":
                    card_display += " ❌"
                elif legality_status == "restricted":
                    card_display += " ⚠️"
            
            # Enhanced reasons with Scryfall data
            enhanced_reasons = rec.reasons.copy()
            if rec.keywords:
                keyword_summary = f"Keywords: {', '.join(rec.keywords[:3])}"
                if len(rec.keywords) > 3:
                    keyword_summary += f" (+{len(rec.keywords)-3} more)"
                enhanced_reasons.append(keyword_summary)
            
            if rec.power_toughness:
                enhanced_reasons.append(f"P/T: {rec.power_toughness}")
            
            # Format reasons for display
            reasons_text = "; ".join(enhanced_reasons[:2])
            if len(enhanced_reasons) > 2:
                reasons_text += f" (+{len(enhanced_reasons)-2} more)"
            
            # Enhanced column data
            # Handle CMC display - show "Land" for lands, otherwise show CMC as integer
            cmc_display = "Land" if "Land" in rec.card_type else str(int(getattr(rec, 'cmc', 0)))
            
            values = (
                card_display,
                f"{rec.confidence:.1%}",
                f"{rec.synergy_score:.1%}",
                cmc_display,  # Show "Land" for lands, CMC as integer for others
                reasons_text
            )
            
            self.rec_tree.insert('', 'end', values=values, tags=tags)
        
        # Configure tag colors with minimal contrast for better readability
        # Using light theme colors since we're using built-in ttk themes
        self.rec_tree.tag_configure('craftable', foreground="dark slate gray")
        
        # Configure confidence level row colors
        self.rec_tree.tag_configure('high_confidence', background="#a7df81")
        self.rec_tree.tag_configure('medium_confidence', background="#E0DF8F")
        self.rec_tree.tag_configure('low_confidence', background="#FF3232")
    
    def update_column_headers(self):
        """Update column headers with sort indicators"""
        headers = {
            'card': ('Card', 'name'),
            'confidence': ('Confidence', 'confidence'), 
            'synergy': ('Synergy', 'synergy'),
            'cmc': ('CMC', 'cmc'),
            'reasons': ('Reasons', 'reasons')
        }
        
        for col, (base_text, col_key) in headers.items():
            if col_key == self.sort_column:
                arrow = " ↓" if self.sort_reverse else " ↑"
                text = f"{base_text}{arrow}"
            else:
                text = base_text
            self.rec_tree.heading(col, text=text)
    
    def filter_recommendations(self, *args):
        """Filter recommendations by minimum confidence, land visibility, and card type"""
        self.refresh_display()
        
    def update_total_count(self, total_recommendations, filtered_recommendations):
        """Update the total recommendations count display"""
        if total_recommendations == filtered_recommendations:
            count_text = f"Total: {total_recommendations} recommendations"
        else:
            count_text = f"Total: {filtered_recommendations} of {total_recommendations} recommendations"
        
        # Add filter info if any filters are active
        filter_info = []
        
        # Add land filter info if lands are hidden
        if not self.show_lands_var.get():
            land_count = sum(1 for r in self.current_smart_recommendations if "Land" in r.card_type)
            filter_info.append(f"hiding {land_count} lands")
        
        # Add card type filter info if not "All"
        selected_type = getattr(self, 'card_type_var', None)
        if selected_type and selected_type.get() != "All":
            type_name = selected_type.get()
            type_count = sum(1 for r in self.current_smart_recommendations 
                           if not self._matches_card_type(r.card_type, type_name))
            filter_info.append(f"showing only {type_name}s")
        
        # Add filter info to count text
        if filter_info:
            count_text += f" ({', '.join(filter_info)})"
        
        if hasattr(self, 'total_count_label'):
            self.total_count_label.config(text=count_text)
    
    def _matches_card_type(self, card_type_line: str, filter_type: str) -> bool:
        """Check if a card matches the selected type filter"""
        if not card_type_line:
            return False
        
        # Convert to lowercase for case-insensitive matching
        type_line = card_type_line.lower()
        filter_type_lower = filter_type.lower()
        
        # Handle specific type matching
        if filter_type_lower == "creature":
            return "creature" in type_line
        elif filter_type_lower == "instant":
            return "instant" in type_line and "sorcery" not in type_line  # Exclude instant sorceries
        elif filter_type_lower == "sorcery":
            return "sorcery" in type_line
        elif filter_type_lower == "enchantment":
            return "enchantment" in type_line
        elif filter_type_lower == "artifact":
            return "artifact" in type_line and "creature" not in type_line  # Exclude artifact creatures from artifact filter
        elif filter_type_lower == "planeswalker":
            return "planeswalker" in type_line
        elif filter_type_lower == "land":
            return "land" in type_line
        
        return False
    
    def toggle_land_visibility(self):
        """Toggle the visibility of land recommendations"""
        self.refresh_display()
    
    def refresh_all(self):
        """Refresh all analyses and recommendations"""
        self.update_deck_header()  # Update deck info first
        self.analyze_deck()
        self.get_recommendations()
    
    def add_to_mainboard(self):
        """Add selected recommendation to mainboard"""
        self._add_selected_card(sideboard=False)
    
    def add_to_sideboard(self):
        """Add selected recommendation to sideboard"""
        self._add_selected_card(sideboard=True)
    
    def _add_selected_card(self, sideboard=False):
        """Add selected card to deck"""
        recommendation, card_name = self._get_selected_recommendation()
        if not recommendation:
            messagebox.showwarning("Warning", "No recommendation selected or found")
            return
        
        # Get quantity from user
        from tkinter import simpledialog
        quantity = simpledialog.askinteger(
            "Add Card", 
            f"How many copies of {card_name}?",
            initialvalue=1, minvalue=1, maxvalue=4
        )
        
        if quantity and self.add_card_callback:
            # For enhanced recommendations, we need to create a basic card object
            if hasattr(recommendation, 'card_name') and not hasattr(recommendation, 'card'):
                # Enhanced recommendation - create minimal card object
                from models.card import Card
                card = Card(
                    name=recommendation.card_name,
                    mana_cost=getattr(recommendation, 'mana_cost', ''),
                    card_type=getattr(recommendation, 'card_type', ''),
                    rarity=getattr(recommendation, 'rarity', 'common')
                )
            else:
                # Basic recommendation with card object
                card = recommendation.card
            
            try:
                success = self.add_card_callback(card, quantity, sideboard)
                if success:
                    location = "sideboard" if sideboard else "mainboard"
                    messagebox.showinfo("Card Added", f"Added {quantity}x {card_name} to {location}")
                    
                    # Refresh recommendations after adding
                    self.get_recommendations()
                else:
                    messagebox.showerror("Error", f"Failed to add card - no active deck")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to add card: {str(e)}")
        elif quantity:
            # No callback available - show info message
            location = "sideboard" if sideboard else "mainboard"
            messagebox.showinfo("Info", f"Would add {quantity}x {card_name} to {location}")
    
    def find_similar_cards(self):
        """Find similar cards to the selected recommendation"""
        recommendation, card_name = self._get_selected_recommendation()
        if not recommendation:
            messagebox.showwarning("Warning", "No recommendation selected")
            return
        
        # Simple implementation - could be enhanced with actual similarity search
        similar_info = f"Finding cards similar to {card_name}...\n\n"
        similar_info += "This feature could show:\n"
        similar_info += "• Cards with similar mana costs\n"
        similar_info += "• Cards with similar effects\n"
        similar_info += "• Cards from the same archetype\n"
        similar_info += "• Alternative options\n\n"
        similar_info += "Consider implementing full Scryfall similarity search for better results."
        
        messagebox.showinfo("Similar Cards", similar_info)
    
    def _get_selected_recommendation(self):
        """Get the selected recommendation from the tree"""
        selection = self.rec_tree.selection()
        if not selection:
            return None, None
        
        item = selection[0]
        card_display_name = self.rec_tree.item(item)['values'][0]
        
        # Extract clean card name by removing icons and ownership info
        import re
        # Remove icons and ownership info: "✅ Lightning Bolt (Owned)" -> "Lightning Bolt"
        clean_name = re.sub(r'^[🔨🔧💎👑✅❌⚠️]\s*', '', card_display_name)
        clean_name = re.sub(r'\s*\([^)]*\).*$', '', clean_name)
        clean_name = re.sub(r'\s*[✓❌⚠️]\s*$', '', clean_name)
        clean_name = clean_name.strip()
        
        # Find the recommendation - check both current recommendation lists
        recommendation = None
        
        # Check enhanced recommendations
        if hasattr(self, 'current_smart_recommendations') and self.current_smart_recommendations:
            for rec in self.current_smart_recommendations:
                if rec.card_name.lower() == clean_name.lower():
                    recommendation = rec
                    break
        
        return recommendation, clean_name
        
        # Get quantity from user
        from tkinter import simpledialog
        quantity = simpledialog.askinteger(
            "Add Card", 
            f"How many copies of {card_name}?",
            initialvalue=1, minvalue=1, maxvalue=4
        )
        
        if quantity and self.add_card_callback:
            # Add to deck using callback
            try:
                success = self.add_card_callback(recommendation.card, quantity, sideboard)
                if success:
                    location = "sideboard" if sideboard else "mainboard"
                    messagebox.showinfo("Card Added", f"Added {quantity}x {card_name} to {location}")
                    
                    # Refresh recommendations after adding
                    self.get_recommendations()
                else:
                    messagebox.showerror("Error", f"Failed to add card - no active deck")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to add card: {str(e)}")
        elif quantity:
            # No callback available - show info message
            location = "sideboard" if sideboard else "mainboard"
            messagebox.showinfo("Info", f"Would add {quantity}x {card_name} to {location}")
    
    def view_card_details(self, event=None):
        """View detailed information about selected card using enhanced modal"""
        recommendation, card_name = self._get_selected_recommendation()
        if not recommendation or not card_name:
            messagebox.showwarning("Warning", "No recommendation selected")
            return

        # Create enhanced card details dialog
        details_dialog = tk.Toplevel(self.frame)
        details_dialog.title(f"Card Details - {card_name}")
        details_dialog.geometry("700x600")
        details_dialog.resizable(True, True)
        details_dialog.transient(self.frame.winfo_toplevel())
        details_dialog.grab_set()
        
        # Center the dialog
        details_dialog.update_idletasks()
        x = (details_dialog.winfo_screenwidth() // 2) - (350)
        y = (details_dialog.winfo_screenheight() // 2) - (300)
        details_dialog.geometry(f"700x600+{x}+{y}")
        
        # Main container with padding
        main_frame = ttk.Frame(details_dialog)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Title
        title_frame = ttk.Frame(main_frame)
        title_frame.pack(fill=tk.X, pady=(0, 15))
        
        ttk.Label(title_frame, text=f"CARD DETAILS", 
                 font=('TkDefaultFont', 14, 'bold')).pack()
        ttk.Label(title_frame, text=card_name, 
                 font=('TkDefaultFont', 12)).pack()
        
        # Create notebook for organized sections
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
        
        # Card Info Tab
        info_frame = ttk.Frame(notebook)
        notebook.add(info_frame, text="Card Information")
        
        info_text = tk.Text(info_frame, wrap=tk.WORD, height=20)
        info_scrollbar = ttk.Scrollbar(info_frame, orient=tk.VERTICAL, command=info_text.yview)
        info_text.configure(yscrollcommand=info_scrollbar.set)
        
        info_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        info_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # AI Analysis Tab
        ai_frame = ttk.Frame(notebook)
        notebook.add(ai_frame, text="AI Recommendation Analysis")
        
        ai_text = tk.Text(ai_frame, wrap=tk.WORD, height=20)
        ai_scrollbar = ttk.Scrollbar(ai_frame, orient=tk.VERTICAL, command=ai_text.yview)
        ai_text.configure(yscrollcommand=ai_scrollbar.set)
        
        ai_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        ai_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Populate card information
        self._populate_card_info(info_text, recommendation)
        
        # Populate AI analysis
        self._populate_ai_analysis(ai_text, recommendation)
        
        # Make text areas read-only
        info_text.configure(state=tk.DISABLED)
        ai_text.configure(state=tk.DISABLED)
        
        # Close button
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X)
        
        ttk.Button(button_frame, text="View on Scryfall", 
                  command=lambda: self._open_scryfall_url(card_name)).pack(side=tk.LEFT)
        ttk.Button(button_frame, text="Close", 
                  command=details_dialog.destroy).pack(side=tk.RIGHT)
    
    def _populate_card_info(self, text_widget, recommendation):
        """Populate the card information tab"""
        details = ""
        
        if hasattr(recommendation, 'card_name'):
            # Enhanced recommendation with Scryfall data
            details += f"BASIC INFORMATION\n"
            details += "=" * 40 + "\n\n"
            
            mana_cost = getattr(recommendation, 'mana_cost', 'Unknown')
            details += f"Mana Cost: {mana_cost}\n"
            
            card_type = getattr(recommendation, 'card_type', 'Unknown')
            details += f"Type Line: {card_type}\n"
            
            rarity = getattr(recommendation, 'rarity', 'Unknown')
            details += f"Rarity: {rarity.title()}\n"
            
            cmc = getattr(recommendation, 'cmc', 0)
            details += f"Converted Mana Cost: {int(cmc)}\n"
            
            if hasattr(recommendation, 'power_toughness') and recommendation.power_toughness:
                details += f"Power/Toughness: {recommendation.power_toughness}\n"
            
            details += "\n"
            
            # Oracle text
            oracle_text = getattr(recommendation, 'oracle_text', '')
            if oracle_text:
                details += f"ORACLE TEXT\n"
                details += "=" * 40 + "\n\n"
                details += f"{oracle_text}\n\n"
            
            # Keywords
            if hasattr(recommendation, 'keywords') and recommendation.keywords:
                details += f"KEYWORDS\n"
                details += "=" * 40 + "\n\n"
                details += f"{', '.join(recommendation.keywords)}\n\n"
            
            # Format legality
            if hasattr(recommendation, 'legality') and recommendation.legality:
                details += f"FORMAT LEGALITY\n"
                details += "=" * 40 + "\n\n"
                for format_name, status in recommendation.legality.items():
                    status_icon = {"legal": "[LEGAL]", "not_legal": "[BANNED]", "restricted": "[RESTRICTED]"}.get(status, f"[{status.upper()}]")
                    details += f"{format_name.title()}: {status_icon}\n"
                details += "\n"
        
        elif hasattr(recommendation, 'card'):
            # Basic recommendation with card object
            card = recommendation.card
            details += f"BASIC INFORMATION\n"
            details += "=" * 40 + "\n\n"
            details += f"Mana Cost: {card.mana_cost}\n"
            details += f"Converted Mana Cost: {card.converted_mana_cost}\n"
            details += f"Type Line: {card.card_type}\n"
            details += f"Rarity: {card.rarity}\n"
            details += f"Colors: {', '.join(card.colors) if card.colors else 'Colorless'}\n"
            
            if card.power is not None and card.toughness is not None:
                details += f"Power/Toughness: {card.power}/{card.toughness}\n"
            
            details += f"\nORACLE TEXT\n"
            details += "=" * 40 + "\n\n"
            details += f"{card.text}\n\n"
        
        else:
            details = f"LIMITED INFORMATION AVAILABLE\n"
            details += "=" * 40 + "\n\n"
            details += "Unable to retrieve detailed card information.\n"
        
        text_widget.insert(1.0, details)
    
    def _populate_ai_analysis(self, text_widget, recommendation):
        """Populate the AI analysis tab"""
        analysis = ""
        
        if hasattr(recommendation, 'confidence'):
            analysis += f"RECOMMENDATION METRICS\n"
            analysis += "=" * 40 + "\n\n"
            
            confidence = recommendation.confidence
            analysis += f"Confidence Score: {confidence:.1%}\n"
            analysis += f"  {'[EXCELLENT]' if confidence >= 0.8 else '[GOOD]' if confidence >= 0.6 else '[FAIR]'}\n\n"
            
            synergy = getattr(recommendation, 'synergy_score', 0)
            analysis += f"Synergy Score: {synergy:.1%}\n"
            analysis += f"  {'[HIGH SYNERGY]' if synergy >= 0.7 else '[MODERATE]' if synergy >= 0.5 else '[LOW SYNERGY]'}\n\n"
            
            deck_fit = getattr(recommendation, 'deck_fit', 0)
            analysis += f"Archetype Fit: {deck_fit:.1%}\n"
            analysis += f"  {'[PERFECT FIT]' if deck_fit >= 0.8 else '[GOOD FIT]' if deck_fit >= 0.6 else '[EXPERIMENTAL]'}\n\n"
            
            meta_score = getattr(recommendation, 'meta_score', 0)
            analysis += f"Meta Score: {meta_score:.1%}\n"
            analysis += f"  {'[META STAPLE]' if meta_score >= 0.7 else '[VIABLE]' if meta_score >= 0.4 else '[NICHE]'}\n\n"
            
            cost_consideration = getattr(recommendation, 'cost_consideration', 'unknown')
            analysis += f"Acquisition: {cost_consideration.replace('_', ' ').title()}\n\n"
            
            # Reasons
            if hasattr(recommendation, 'reasons') and recommendation.reasons:
                analysis += f"RECOMMENDATION REASONS\n"
                analysis += "=" * 40 + "\n\n"
                for i, reason in enumerate(recommendation.reasons, 1):
                    analysis += f"{i}. {reason}\n"
                analysis += "\n"
        
        else:
            analysis = f"NO AI ANALYSIS AVAILABLE\n"
            analysis += "=" * 40 + "\n\n"
            analysis += "This recommendation doesn't include AI analysis data.\n"
        
        text_widget.insert(1.0, analysis)
    
    def _open_scryfall_url(self, card_name):
        """Open card page on Scryfall"""
        import webbrowser
        import urllib.parse
        
        encoded_name = urllib.parse.quote(card_name)
        url = f"https://scryfall.com/search?q=%21%22{encoded_name}%22"
        webbrowser.open(url)
    
    def explain_recommendation(self):
        """Explain why a card is recommended"""
        recommendation, card_name = self._get_selected_recommendation()
        if not recommendation or not card_name:
            messagebox.showwarning("Warning", "No recommendation selected")
            return
        
        explanation = f"🤔 WHY IS {card_name.upper()} RECOMMENDED?\n"
        explanation += "=" * 23 + "\n\n"
        
        if hasattr(recommendation, 'reasons') and recommendation.reasons:
            explanation += "💡 RECOMMENDATION REASONS:\n"
            for i, reason in enumerate(recommendation.reasons, 1):
                explanation += f"  {i}. {reason}\n"
        else:
            explanation += "💡 No specific reasons available for this recommendation.\n"
        
        explanation += f"\n📊 DETAILED SCORING BREAKDOWN:\n"
        
        if hasattr(recommendation, 'card_name'):
            # Enhanced recommendation scoring
            explanation += f"🎯 Overall Confidence: {recommendation.confidence:.1%}\n"
            explanation += f"   └─ How sure the AI is about this recommendation\n\n"
            explanation += f"🔗 Synergy Score: {recommendation.synergy_score:.1%}\n" 
            explanation += f"   └─ How well it works with your current cards\n\n"
            explanation += f"📈 Meta Score: {recommendation.meta_score:.1%}\n"
            explanation += f"   └─ How popular/successful this card is in the current meta\n\n"
            explanation += f"🎲 Deck Fit: {recommendation.deck_fit:.1%}\n"
            explanation += f"   └─ How well it fits your deck's strategy and archetype\n\n"
            explanation += f"💰 Cost: {recommendation.cost_consideration.replace('_', ' ').title()}\n"
            explanation += f"   └─ Acquisition difficulty (owned/craft required)\n"
        else:
            # Basic recommendation scoring
            explanation += f"🎯 Overall Confidence: {getattr(recommendation, 'confidence', 0):.1%}\n"
            explanation += f"🔗 Synergy with deck: {getattr(recommendation, 'synergy_score', 0):.1%}\n"
            explanation += f"📊 Meta popularity: {getattr(recommendation, 'popularity_score', 0):.1%}\n"
            explanation += f"🎲 Archetype alignment: {getattr(recommendation, 'archetype_fit', 0):.1%}\n"
        
        messagebox.showinfo("Recommendation Explanation", explanation)
