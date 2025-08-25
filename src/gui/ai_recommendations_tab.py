"""
AI Recommendations tab for the MTG Arena Deck Manager
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import List, Dict, Optional
import threading

from models.deck import Deck
from models.collection import Collection
from utils.ai_recommendations import CardRecommendationEngine, CardRecommendation
from utils.smart_recommendations import IntelligentRecommendationEngine, SmartRecommendation
from utils.enhanced_recommendations_sync import get_smart_recommendations

class AIRecommendationsTab:
    """AI-powered card recommendations interface"""
    
    def __init__(self, parent, get_current_deck_func, get_collection_func, add_card_callback=None):
        self.parent = parent
        self.get_current_deck = get_current_deck_func
        self.get_collection = get_collection_func
        self.add_card_callback = add_card_callback
        self.recommendation_engine = CardRecommendationEngine()
        self.smart_engine = IntelligentRecommendationEngine()
        self.current_recommendations = []
        self.current_smart_recommendations = []
        
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
                color_symbols = {'W': '⚪', 'U': '🔵', 'B': '⚫', 'R': '🔴', 'G': '🟢'}
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
        
        # Archetype analysis tab
        archetype_frame = ttk.Frame(analysis_notebook)
        analysis_notebook.add(archetype_frame, text="Archetype")
        
        self.archetype_text = tk.Text(archetype_frame, height=6, wrap=tk.WORD)
        archetype_scroll = ttk.Scrollbar(archetype_frame, orient=tk.VERTICAL, command=self.archetype_text.yview)
        self.archetype_text.configure(yscrollcommand=archetype_scroll.set)
        
        self.archetype_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        archetype_scroll.pack(side=tk.RIGHT, fill=tk.Y, pady=5)
        
        # Suggestions tab
        suggestions_frame = ttk.Frame(analysis_notebook)
        analysis_notebook.add(suggestions_frame, text="Improvements")
        
        self.suggestions_text = tk.Text(suggestions_frame, height=6, wrap=tk.WORD)
        suggestions_scroll = ttk.Scrollbar(suggestions_frame, orient=tk.VERTICAL, command=self.suggestions_text.yview)
        self.suggestions_text.configure(yscrollcommand=suggestions_scroll.set)
        
        self.suggestions_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        suggestions_scroll.pack(side=tk.RIGHT, fill=tk.Y, pady=5)
        
        # Similar decks tab
        similar_frame = ttk.Frame(analysis_notebook)
        analysis_notebook.add(similar_frame, text="Similar Decks")
        
        self.similar_text = tk.Text(similar_frame, height=6, wrap=tk.WORD)
        similar_scroll = ttk.Scrollbar(similar_frame, orient=tk.VERTICAL, command=self.similar_text.yview)
        self.similar_text.configure(yscrollcommand=similar_scroll.set)
        
        self.similar_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        similar_scroll.pack(side=tk.RIGHT, fill=tk.Y, pady=5)
        
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
        self.loading_label = ttk.Label(control_frame, textvariable=self.loading_var, foreground="blue")
        self.loading_label.pack(side=tk.RIGHT, padx=5)
    
    def create_recommendations_panel(self, parent):
        """Create the recommendations display panel"""
        rec_frame = ttk.LabelFrame(parent, text="AI Card Recommendations")
        rec_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Recommendation list
        columns = ('Card', 'Confidence', 'Synergy', 'Popularity', 'Archetype Fit', 'Reasons')
        self.rec_tree = ttk.Treeview(rec_frame, columns=columns, show='headings', height=12)
        
        # Configure columns
        self.rec_tree.heading('Card', text='Card Name')
        self.rec_tree.heading('Confidence', text='Confidence')
        self.rec_tree.heading('Synergy', text='Synergy')
        self.rec_tree.heading('Popularity', text='Meta Usage')
        self.rec_tree.heading('Archetype Fit', text='Arch Fit')
        self.rec_tree.heading('Reasons', text='Reasons/Notes')
        
        self.rec_tree.column('Card', width=150)
        self.rec_tree.column('Confidence', width=80)
        self.rec_tree.column('Synergy', width=70)
        self.rec_tree.column('Popularity', width=80)
        self.rec_tree.column('Archetype Fit', width=80)
        self.rec_tree.column('Reasons', width=300)
        
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
        
        # Recommendation controls - moved below the table for better visibility
        rec_controls = ttk.Frame(parent)  # Changed from rec_frame to parent
        rec_controls.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(rec_controls, text="Show:").pack(side=tk.LEFT)
        self.rec_count_var = tk.IntVar(value=50)
        rec_count_spin = ttk.Spinbox(rec_controls, from_=5, to=50, width=5, textvariable=self.rec_count_var)
        rec_count_spin.pack(side=tk.LEFT, padx=5)
        ttk.Label(rec_controls, text="recommendations").pack(side=tk.LEFT)
        
        # Filter controls
        ttk.Label(rec_controls, text="Min Confidence:").pack(side=tk.LEFT, padx=(20, 5))
        self.min_confidence_var = tk.DoubleVar(value=0.0)
        confidence_scale = ttk.Scale(rec_controls, from_=0.0, to=1.0, orient=tk.HORIZONTAL, 
                                   length=100, variable=self.min_confidence_var, command=self.filter_recommendations)
        confidence_scale.pack(side=tk.LEFT, padx=5)
        
        self.confidence_label = ttk.Label(rec_controls, text="0%")
        self.confidence_label.pack(side=tk.LEFT, padx=5)
        
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
        self.analysis_status_label.config(text="🔍 Analyzing deck...", foreground='blue')
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
                
                # Deck improvements
                improvements = self.recommendation_engine.suggest_deck_improvements(current_deck)
                improvements_text = f"⚡ DECK IMPROVEMENT SUGGESTIONS for '{current_deck.name}'\n"
                improvements_text += "=" * 60 + "\n\n"
                
                if improvements:
                    improvements_text += "🔧 Recommended Changes:\n\n"
                    for i, suggestion in enumerate(improvements, 1):
                        improvements_text += f"  {i}. 📝 {suggestion}\n\n"
                else:
                    improvements_text += "✅ DECK LOOKS GREAT!\n\n"
                    improvements_text += "Your deck appears to be well-balanced with no major issues detected.\n"
                    improvements_text += "Consider fine-tuning based on your local meta or playstyle preferences.\n"
                
                # Similar decks
                similar_decks = self.recommendation_engine.find_similar_decks(current_deck)
                similar_text = f"🔍 SIMILAR SUCCESSFUL DECKS to '{current_deck.name}'\n"
                similar_text += "=" * 60 + "\n\n"
                
                if similar_decks:
                    similar_text += "🏆 Tournament-Proven Similar Builds:\n\n"
                    for i, deck_info in enumerate(similar_decks, 1):
                        similarity_percentage = deck_info['similarity'] * 100
                        stars = "⭐" * min(5, int(similarity_percentage / 20))
                        
                        similar_text += f"  {i}. 🎴 {deck_info['name']}\n"
                        similar_text += f"     👤 Pilot: {deck_info['pilot']}\n"
                        similar_text += f"     🏟️  Event: {deck_info['event']}\n"
                        similar_text += f"     📊 Similarity: {stars} {similarity_percentage:.1f}%\n"
                        if deck_info['key_differences']:
                            similar_text += f"     🔄 Key Differences: {', '.join(deck_info['key_differences'])}\n"
                        similar_text += "\n"
                else:
                    similar_text += "🔍 No similar decks found in the tournament database.\n\n"
                    similar_text += "This could mean:\n"
                    similar_text += "• Your deck is unique/innovative\n"
                    similar_text += "• The archetype is underrepresented in competitive play\n"
                    similar_text += "• Consider exploring established archetypes for reference\n"
                
                # Update UI in main thread
                def update_ui():
                    self.archetype_text.delete(1.0, tk.END)
                    self.archetype_text.insert(1.0, archetype_text)
                    
                    self.suggestions_text.delete(1.0, tk.END)
                    self.suggestions_text.insert(1.0, improvements_text)
                    
                    self.similar_text.delete(1.0, tk.END)
                    self.similar_text.insert(1.0, similar_text)
                    
                    self.loading_var.set("")
                    self.analysis_status_label.config(text="✅ Analysis complete", foreground='green')
                
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
    
    def get_recommendations(self):
        """Get AI card recommendations using the enhanced Scryfall-powered system"""
        current_deck = self.get_current_deck()
        if not current_deck:
            messagebox.showwarning("Warning", "No deck selected")
            return
        
        # Update header to show current deck
        self.update_deck_header()
        
        self.loading_var.set("Getting enhanced AI recommendations...")
        self.analysis_status_label.config(text="🤖 Generating Scryfall-powered recommendations...", foreground='blue')
        self.frame.update()
        
        def get_recs():
            try:
                collection = self.get_collection()
                format_name = self.format_var.get()
                count = self.rec_count_var.get()
                
                # Use the enhanced recommendation engine with Scryfall data
                enhanced_recommendations = get_smart_recommendations(
                    current_deck, collection, count, format_name
                )
                
                def update_recs():
                    self.current_smart_recommendations = enhanced_recommendations
                    self.display_enhanced_recommendations()
                    self.loading_var.set("")
                    self.analysis_status_label.config(text="✅ Enhanced recommendations ready", foreground='green')
                
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
    
    def display_recommendations(self):
        """Display the current recommendations"""
        # Clear existing items
        for item in self.rec_tree.get_children():
            self.rec_tree.delete(item)
        
        # Filter by minimum confidence
        min_confidence = self.min_confidence_var.get()
        filtered_recs = [r for r in self.current_recommendations if r.confidence >= min_confidence]
        
        # Get collection to check ownership
        collection = self.get_collection()
        
        # Simple ownership check function
        def check_card_ownership(card_name):
            if not collection or not hasattr(collection, 'cards'):
                return False, 0
            
            if card_name in collection.cards:
                collection_card = collection.cards[card_name]
                return True, collection_card.quantity + collection_card.quantity_foil
            
            # Try case-insensitive search
            for name, collection_card in collection.cards.items():
                if name.lower() == card_name.lower():
                    return True, collection_card.quantity + collection_card.quantity_foil
            
            return False, 0
        
        # Separate owned and craftable recommendations
        owned_recs = []
        craftable_recs = []
        
        for rec in filtered_recs:
            # Get card name from recommendation
            card_name = rec.card.name if hasattr(rec, 'card') and hasattr(rec.card, 'name') else getattr(rec, 'name', 'Unknown')
            is_owned, quantity = check_card_ownership(card_name)
            
            if is_owned and quantity > 0:
                owned_recs.append((rec, quantity))
            else:
                craftable_recs.append(rec)
        
        # Add owned cards first (with green highlighting)
        for rec, owned_qty in owned_recs:
            card_name = rec.card.name if hasattr(rec, 'card') and hasattr(rec.card, 'name') else getattr(rec, 'name', 'Unknown')
            reasons_text = "; ".join(getattr(rec, 'reasons', ['No reasons available'])[:2])
            if len(getattr(rec, 'reasons', [])) > 2:
                reasons_text += f" (+{len(rec.reasons)-2} more)"
            
            values = (
                f"✅ {card_name} (Own: {owned_qty})",
                f"{getattr(rec, 'confidence', 0):.1%}",
                f"{getattr(rec, 'synergy_score', 0):.1%}",
                f"{getattr(rec, 'popularity_score', 0):.1%}",
                f"{getattr(rec, 'archetype_fit', 0):.1%}",
                reasons_text
            )
            
            self.rec_tree.insert('', 'end', values=values, tags=('owned',))
        
        # Add craftable cards (with different highlighting)
        for rec in craftable_recs:
            card_name = rec.card.name if hasattr(rec, 'card') and hasattr(rec.card, 'name') else getattr(rec, 'name', 'Unknown')
            reasons_text = "; ".join(getattr(rec, 'reasons', ['No reasons available'])[:2])
            if len(getattr(rec, 'reasons', [])) > 2:
                reasons_text += f" (+{len(rec.reasons)-2} more)"
            
            values = (
                f"🔨 {card_name} (Need to craft)",
                f"{getattr(rec, 'confidence', 0):.1%}",
                f"{getattr(rec, 'synergy_score', 0):.1%}",
                f"{getattr(rec, 'popularity_score', 0):.1%}",
                f"{getattr(rec, 'archetype_fit', 0):.1%}",
                reasons_text
            )
            
            self.rec_tree.insert('', 'end', values=values, tags=('craftable',))
        
        # Configure tag colors
        self.rec_tree.tag_configure('owned', background='lightgreen')
        self.rec_tree.tag_configure('craftable', background='lightyellow')
    
    def display_enhanced_recommendations(self):
        """Display the enhanced AI recommendations with Scryfall data"""
        # Clear existing items
        for item in self.rec_tree.get_children():
            self.rec_tree.delete(item)
        
        if not self.current_smart_recommendations:
            return
        
        # Filter by minimum confidence
        min_confidence = self.min_confidence_var.get()
        filtered_recs = [r for r in self.current_smart_recommendations if r.confidence >= min_confidence]
        
        # Display enhanced recommendations with rich Scryfall data
        for rec in filtered_recs:
            # Determine ownership status and display
            if rec.cost_consideration == "owned":
                card_display = f"✅ {rec.card_name} (Owned)"
                tag = 'owned'
            else:
                craft_icons = {
                    "common_craft": "🔨", 
                    "uncommon_craft": "🔧", 
                    "rare_craft": "💎", 
                    "mythic_craft": "👑"
                }
                craft_icon = craft_icons.get(rec.cost_consideration, "🔨")
                card_display = f"{craft_icon} {rec.card_name}"
                tag = 'craftable'
            
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
            values = (
                card_display,
                f"{rec.confidence:.1%}",
                f"{rec.synergy_score:.1%}",
                f"{rec.meta_score:.1%}",
                f"{rec.deck_fit:.1%}",
                reasons_text
            )
            
            self.rec_tree.insert('', 'end', values=values, tags=(tag,))
        
        # Configure tag colors
        self.rec_tree.tag_configure('owned', background='lightgreen')
        self.rec_tree.tag_configure('craftable', background='lightyellow')
    
    def display_smart_recommendations(self):
        """Display the smart AI recommendations"""
        # Clear existing items
        for item in self.rec_tree.get_children():
            self.rec_tree.delete(item)
        
        if not self.current_smart_recommendations:
            return
        
        # Display smart recommendations with ownership info
        for rec in self.current_smart_recommendations:
            # Determine ownership status and display
            if rec.cost_consideration == "owned":
                card_display = f"✅ {rec.card_name} (Owned)"
                tag = 'owned'
            else:
                craft_icon = {"common_craft": "🔨", "uncommon_craft": "🔧", "rare_craft": "💎", "mythic_craft": "👑"}.get(rec.cost_consideration, "🔨")
                card_display = f"{craft_icon} {rec.card_name} (Craft: {rec.rarity.title()})"
                tag = 'craftable'
            
            # Format reasons for display
            reasons_text = "; ".join(rec.reasons[:2])
            if len(rec.reasons) > 2:
                reasons_text += f" (+{len(rec.reasons)-2} more)"
            
            values = (
                card_display,
                f"{rec.confidence:.1%}",
                f"{rec.synergy_score:.1%}",
                f"{rec.meta_score:.1%}",
                f"{rec.deck_fit:.1%}",
                reasons_text
            )
            
            self.rec_tree.insert('', 'end', values=values, tags=(tag,))
        
        # Configure tag colors
        self.rec_tree.tag_configure('owned', background='lightgreen')
        self.rec_tree.tag_configure('craftable', background='lightyellow')
    
    def filter_recommendations(self, *args):
        """Filter recommendations by minimum confidence"""
        # Use enhanced display if we have enhanced recommendations
        if hasattr(self, 'current_smart_recommendations') and self.current_smart_recommendations:
            self.display_enhanced_recommendations()
        else:
            self.display_recommendations()
    
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
        
        # First check enhanced recommendations
        if hasattr(self, 'current_smart_recommendations') and self.current_smart_recommendations:
            for rec in self.current_smart_recommendations:
                if rec.card_name.lower() == clean_name.lower():
                    recommendation = rec
                    break
        
        # Fallback to basic recommendations
        if not recommendation and hasattr(self, 'current_recommendations') and self.current_recommendations:
            for rec in self.current_recommendations:
                card_name = rec.card.name if hasattr(rec, 'card') and hasattr(rec.card, 'name') else getattr(rec, 'name', '')
                if card_name.lower() == clean_name.lower():
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
        """View detailed information about selected card"""
        recommendation, card_name = self._get_selected_recommendation()
        if not recommendation or not card_name:
            messagebox.showwarning("Warning", "No recommendation selected")
            return
        
        details = ""  # Initialize details variable
        
        # Build card details based on recommendation type
        if hasattr(recommendation, 'card_name'):
            # Enhanced recommendation with Scryfall data
            details = f"🎴 CARD DETAILS: {recommendation.card_name}\n"
            details += "=" * 50 + "\n\n"
            details += f"💰 Mana Cost: {getattr(recommendation, 'mana_cost', 'Unknown')}\n"
            details += f"🎭 Type: {getattr(recommendation, 'card_type', 'Unknown')}\n"
            details += f"💎 Rarity: {getattr(recommendation, 'rarity', 'Unknown').title()}\n"
            
            if hasattr(recommendation, 'power_toughness') and recommendation.power_toughness:
                details += f"⚔️ Power/Toughness: {recommendation.power_toughness}\n"
            
            if hasattr(recommendation, 'oracle_text') and recommendation.oracle_text:
                details += f"\n📜 Oracle Text:\n{recommendation.oracle_text}\n"
            
            if hasattr(recommendation, 'keywords') and recommendation.keywords:
                details += f"\n🏷️ Keywords: {', '.join(recommendation.keywords)}\n"
            
            if hasattr(recommendation, 'legality') and recommendation.legality:
                details += f"\n⚖️ Format Legality:\n"
                for format_name, status in recommendation.legality.items():
                    if status == "legal":
                        details += f"  ✅ {format_name.title()}: Legal\n"
                    elif status == "not_legal":
                        details += f"  ❌ {format_name.title()}: Not Legal\n"
                    elif status == "restricted":
                        details += f"  ⚠️ {format_name.title()}: Restricted\n"
            
            # AI Analysis for enhanced recommendations
            details += f"\n🤖 AI RECOMMENDATION ANALYSIS:\n"
            details += f"🎯 Confidence: {recommendation.confidence:.1%}\n"
            details += f"🔗 Synergy Score: {recommendation.synergy_score:.1%}\n"
            details += f"📈 Meta Score: {recommendation.meta_score:.1%}\n"
            details += f"🎲 Deck Fit: {recommendation.deck_fit:.1%}\n"
            details += f"💡 Cost Consideration: {recommendation.cost_consideration.replace('_', ' ').title()}\n"
            
        elif hasattr(recommendation, 'card'):
            # Basic recommendation with card object
            card = recommendation.card
            details = f"🎴 CARD DETAILS: {card.name}\n"
            details += "=" * 50 + "\n\n"
            details += f"💰 Mana Cost: {card.mana_cost}\n"
            details += f"🔢 CMC: {card.converted_mana_cost}\n"
            details += f"🎭 Type: {card.card_type}\n"
            details += f"💎 Rarity: {card.rarity}\n"
            details += f"🎨 Colors: {', '.join(card.colors) if card.colors else 'Colorless'}\n"
            
            if card.power is not None and card.toughness is not None:
                details += f"⚔️ Power/Toughness: {card.power}/{card.toughness}\n"
            
            details += f"\n📜 Oracle Text:\n{card.text}\n"
            
            # AI Analysis for basic recommendations
            details += f"\n🤖 AI RECOMMENDATION ANALYSIS:\n"
            details += f"🎯 Confidence: {getattr(recommendation, 'confidence', 0):.1%}\n"
            details += f"🔗 Synergy Score: {getattr(recommendation, 'synergy_score', 0):.1%}\n"
            details += f"📊 Popularity: {getattr(recommendation, 'popularity_score', 0):.1%}\n"
            details += f"🎲 Archetype Fit: {getattr(recommendation, 'archetype_fit', 0):.1%}\n"
        else:
            # Fallback for unknown recommendation format
            details = f"🎴 CARD DETAILS: {card_name}\n"
            details += "=" * 50 + "\n\n"
            details += "⚠️ Limited information available for this recommendation.\n"
        
        messagebox.showinfo(f"Card Details", details)
    
    def explain_recommendation(self):
        """Explain why a card is recommended"""
        recommendation, card_name = self._get_selected_recommendation()
        if not recommendation or not card_name:
            messagebox.showwarning("Warning", "No recommendation selected")
            return
        
        explanation = f"🤔 WHY IS {card_name.upper()} RECOMMENDED?\n"
        explanation += "=" * 49 + "\n\n"
        
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
