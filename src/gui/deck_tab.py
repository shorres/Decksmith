"""
Deck management tab for the MTG Arena Deck Manager
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog
import json
import os
from datetime import datetime
from typing import List, Dict, Optional

from models.card import Card
from models.deck import Deck, DeckCard
from utils.csv_handler import CSVHandler
from utils.clipboard_handler import ClipboardHandler
from gui.autocomplete_entry import AutocompleteEntry

class DeckTab:
    """Deck management interface"""
    
    def __init__(self, parent, collection=None):
        self.parent = parent
        self.collection = collection  # Reference to collection for auto-adding cards
        self.decks = []
        self.current_deck = None
        self.current_deck_index = 0
        self.ai_add_card_callback = None  # Callback for AI recommendations
        self.clipboard_handler = ClipboardHandler()  # Clipboard functionality
        self.autocomplete_entries = []  # Store autocomplete entry references
        
        self.create_widgets()
        self.load_decks()
        self.refresh_display()
    
    def create_widgets(self):
        """Create the deck tab widgets"""
        self.frame = ttk.Frame(self.parent)
        
        # Create main paned window
        paned = ttk.PanedWindow(self.frame, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Left panel - deck list and stats
        left_frame = ttk.Frame(paned)
        paned.add(left_frame, weight=1)
        
        # Right panel - deck contents
        right_frame = ttk.Frame(paned)
        paned.add(right_frame, weight=3)
        
        self.create_deck_panel(left_frame)
        self.create_deck_contents(right_frame)
    
    def create_deck_panel(self, parent):
        """Create the deck list and management panel"""
        # Deck selection frame
        deck_frame = ttk.LabelFrame(parent, text="Decks")
        deck_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Deck listbox
        self.deck_listbox = tk.Listbox(deck_frame, height=8)
        self.deck_listbox.pack(fill=tk.X, padx=5, pady=5)
        self.deck_listbox.bind('<<ListboxSelect>>', self.on_deck_select)
        
        # Deck management buttons
        deck_buttons = ttk.Frame(deck_frame)
        deck_buttons.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(deck_buttons, text="New", command=self.new_deck).pack(side=tk.LEFT, padx=2)
        ttk.Button(deck_buttons, text="Copy", command=self.copy_deck).pack(side=tk.LEFT, padx=2)
        ttk.Button(deck_buttons, text="Delete", command=self.delete_deck).pack(side=tk.LEFT, padx=2)
        
        # Deck info frame
        info_frame = ttk.LabelFrame(parent, text="Deck Information")
        info_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Deck name
        ttk.Label(info_frame, text="Name:").pack(anchor=tk.W, padx=5)
        self.deck_name_var = tk.StringVar()
        name_entry = ttk.Entry(info_frame, textvariable=self.deck_name_var)
        name_entry.pack(fill=tk.X, padx=5, pady=2)
        name_entry.bind('<KeyRelease>', self.on_deck_name_change)
        
        # Deck format
        ttk.Label(info_frame, text="Format:").pack(anchor=tk.W, padx=5, pady=(10,0))
        self.format_var = tk.StringVar(value="Standard")
        format_combo = ttk.Combobox(info_frame, textvariable=self.format_var)
        format_combo['values'] = ('Standard', 'Historic', 'Explorer', 'Alchemy', 'Brawl')
        format_combo.pack(fill=tk.X, padx=5, pady=2)
        format_combo.bind('<<ComboboxSelected>>', self.on_format_change)
        
        # Statistics frame
        stats_frame = ttk.LabelFrame(parent, text="Deck Statistics")
        stats_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.stats_text = tk.Text(stats_frame, height=8, width=20)
        self.stats_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Import/Export buttons
        buttons_frame = ttk.Frame(parent)
        buttons_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(buttons_frame, text="Import CSV", command=self.import_deck_csv).pack(fill=tk.X, pady=1)
        ttk.Button(buttons_frame, text="Import Arena", command=self.import_deck_arena).pack(fill=tk.X, pady=1)
        ttk.Button(buttons_frame, text="Import Clipboard", command=self.import_deck_clipboard).pack(fill=tk.X, pady=1)
        ttk.Button(buttons_frame, text="Export CSV", command=self.export_deck_csv).pack(fill=tk.X, pady=1)
        ttk.Button(buttons_frame, text="Export Arena", command=self.export_deck_arena).pack(fill=tk.X, pady=1)
        ttk.Button(buttons_frame, text="Copy to Clipboard", command=self.export_deck_clipboard).pack(fill=tk.X, pady=1)
    
    def create_deck_contents(self, parent):
        """Create the deck contents display"""
        notebook = ttk.Notebook(parent)
        notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Mainboard tab
        mainboard_frame = ttk.Frame(notebook)
        notebook.add(mainboard_frame, text="Mainboard")
        
        # Sideboard tab
        sideboard_frame = ttk.Frame(notebook)
        notebook.add(sideboard_frame, text="Sideboard")
        
        self.create_card_list(mainboard_frame, "mainboard")
        self.create_card_list(sideboard_frame, "sideboard")
    
    def create_card_list(self, parent, list_type):
        """Create a card list (mainboard or sideboard)"""
        # Add card frame
        add_frame = ttk.Frame(parent)
        add_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(add_frame, text="Add Card:").pack(side=tk.LEFT)
        
        # Create autocomplete entry for card names
        card_entry = AutocompleteEntry(
            add_frame, 
            width=30,
            get_suggestions_func=self.get_collection_card_names
        )
        card_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        # Store reference for later updates
        self.autocomplete_entries.append(card_entry)
        
        qty_var = tk.IntVar(value=1)
        ttk.Label(add_frame, text="Qty:").pack(side=tk.LEFT, padx=(10,0))
        qty_spin = ttk.Spinbox(add_frame, from_=1, to=4, width=5, textvariable=qty_var)
        qty_spin.pack(side=tk.LEFT, padx=5)
        
        add_btn = ttk.Button(add_frame, text="Add", 
                           command=lambda: self.add_card_to_deck(card_entry.get(), qty_var.get(), list_type == "sideboard"))
        add_btn.pack(side=tk.LEFT, padx=5)
        
        # Bind Enter key to add card
        card_entry.bind_return(lambda: add_btn.invoke())
        
        # Card list
        list_frame = ttk.Frame(parent)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        columns = ('Quantity', 'Name', 'Type', 'CMC', 'Colors')
        tree = ttk.Treeview(list_frame, columns=columns, show='headings')
        
        # Configure columns
        tree.heading('Quantity', text='Qty')
        tree.heading('Name', text='Card Name')
        tree.heading('Type', text='Type')
        tree.heading('CMC', text='CMC')
        tree.heading('Colors', text='Colors')
        
        tree.column('Quantity', width=50)
        tree.column('Name', width=200)
        tree.column('Type', width=120)
        tree.column('CMC', width=50)
        tree.column('Colors', width=80)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        
        # Pack
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Store references
        if list_type == "mainboard":
            self.mainboard_tree = tree
        else:
            self.sideboard_tree = tree
        
        # Context menu
        context_menu = tk.Menu(parent, tearoff=0)
        context_menu.add_command(label="Edit Quantity", 
                               command=lambda: self.edit_card_quantity(tree, list_type == "sideboard"))
        context_menu.add_command(label="Remove Card", 
                               command=lambda: self.remove_card_from_deck(tree, list_type == "sideboard"))
        context_menu.add_separator()
        context_menu.add_command(label="Move to " + ("Mainboard" if list_type == "sideboard" else "Sideboard"),
                               command=lambda: self.move_card(tree, list_type == "sideboard"))
        
        def show_context_menu(event):
            item = tree.identify_row(event.y)
            if item:
                tree.selection_set(item)
                context_menu.post(event.x_root, event.y_root)
        
        tree.bind("<Button-3>", show_context_menu)
    
    def on_deck_select(self, event=None):
        """Handle deck selection change"""
        selection = self.deck_listbox.curselection()
        if selection:
            self.current_deck_index = selection[0]
            self.current_deck = self.decks[self.current_deck_index]
            self.update_deck_info()
            self.refresh_deck_contents()
    
    def on_deck_name_change(self, event=None):
        """Handle deck name change"""
        if self.current_deck:
            new_name = self.deck_name_var.get()
            self.current_deck.name = new_name
            self.refresh_deck_list()
            self.save_decks()
    
    def on_format_change(self, event=None):
        """Handle format change"""
        if self.current_deck:
            self.current_deck.format = self.format_var.get()
            self.save_decks()
    
    def new_deck(self):
        """Create a new deck"""
        name = simpledialog.askstring("New Deck", "Enter deck name:")
        if name:
            deck = Deck(name=name.strip())
            deck.created_date = datetime.now().isoformat()
            self.decks.append(deck)
            self.refresh_deck_list()
            self.deck_listbox.selection_set(len(self.decks) - 1)
            self.on_deck_select()
            self.save_decks()
    
    def copy_deck(self):
        """Copy the current deck"""
        if not self.current_deck:
            return
        
        name = simpledialog.askstring("Copy Deck", "Enter name for copy:", 
                                    initialvalue=f"{self.current_deck.name} Copy")
        if name:
            deck_data = self.current_deck.to_dict()
            deck_data['name'] = name.strip()
            deck_data['created_date'] = datetime.now().isoformat()
            
            new_deck = Deck.from_dict(deck_data)
            self.decks.append(new_deck)
            self.refresh_deck_list()
            self.deck_listbox.selection_set(len(self.decks) - 1)
            self.on_deck_select()
            self.save_decks()
    
    def delete_deck(self):
        """Delete the current deck"""
        if not self.current_deck:
            return
        
        if messagebox.askyesno("Confirm Delete", f"Delete deck '{self.current_deck.name}'?"):
            self.decks.remove(self.current_deck)
            self.current_deck = None
            self.refresh_deck_list()
            if self.decks:
                self.deck_listbox.selection_set(0)
                self.on_deck_select()
            else:
                self.update_deck_info()
                self.refresh_deck_contents()
            self.save_decks()
    
    def add_card_to_deck(self, card_name, quantity, sideboard=False):
        """Add card to current deck"""
        if not self.current_deck or not card_name.strip():
            return
        
        # Extract just the card name (remove quantity info if present)
        clean_card_name = self.extract_card_name(card_name.strip())
        
        # Check if card exists in collection for better card data
        card = None
        if self.collection and clean_card_name in self.collection.cards:
            # Use card from collection (has better data)
            collection_card = self.collection.cards[clean_card_name]
            card = collection_card.card
        else:
            # Create basic card (for cards not in collection)
            card = Card(name=clean_card_name)
        
        self.current_deck.add_card(card, quantity, sideboard)
        
        self.refresh_deck_contents()
        self.update_statistics()
        self.save_decks()
        
        # Update autocomplete suggestions in case collection changed
        self.refresh_autocomplete_suggestions()
    
    def add_card_from_ai(self, card: Card, quantity: int = 1, sideboard: bool = False):
        """Add card to current deck from AI recommendations"""
        if not self.current_deck:
            return False
        
        self.current_deck.add_card(card, quantity, sideboard)
        self.refresh_deck_contents()
        self.update_statistics()
        self.save_decks()
        return True
    
    def get_collection_card_names(self) -> List[str]:
        """Get list of card names from collection for autocomplete"""
        if not self.collection or not self.collection.cards:
            return []
        
        card_names = []
        for card_name, collection_card in self.collection.cards.items():
            # Only suggest cards that have quantity > 0
            if collection_card.quantity > 0 or collection_card.quantity_foil > 0:
                # Add quantity info to help user know how many they have
                total_qty = collection_card.quantity + collection_card.quantity_foil
                display_name = f"{card_name} ({total_qty} available)"
                card_names.append(display_name)
        
        return sorted(card_names)
    
    def extract_card_name(self, display_name: str) -> str:
        """Extract just the card name from display name with quantity"""
        # Remove the quantity part: "Lightning Bolt (4 available)" -> "Lightning Bolt"
        if " (" in display_name and display_name.endswith(" available)"):
            return display_name.split(" (")[0]
        return display_name
    
    def refresh_autocomplete_suggestions(self):
        """Refresh autocomplete suggestions for all card entry widgets"""
        for entry in self.autocomplete_entries:
            entry.update_suggestions()
    
    def add_deck_cards_to_collection(self, deck: Deck, update_collection_display=True) -> Dict[str, int]:
        """Add deck cards to collection with playset limits (max 4 per card)"""
        if not self.collection:
            return {'cards_added': 0, 'cards_updated': 0, 'cards_skipped': 0}
        
        cards_added = 0
        cards_updated = 0
        cards_skipped = 0
        
        # Get all cards from deck (mainboard + sideboard)
        all_deck_cards = deck.get_mainboard_cards() + deck.get_sideboard_cards()
        
        # Group cards by name to handle duplicates within the deck
        card_totals = {}
        for deck_card in all_deck_cards:
            card_name = deck_card.card.name
            if card_name not in card_totals:
                card_totals[card_name] = {'card': deck_card.card, 'quantity': 0}
            card_totals[card_name]['quantity'] += deck_card.quantity
        
        for card_name, card_info in card_totals.items():
            card = card_info['card']
            deck_quantity = card_info['quantity']
            
            # Check current collection quantity
            current_quantity = self.collection.get_card_quantity(card_name, include_foil=True)
            
            # Calculate how many we can add (max 4 total)
            max_allowed = 4
            can_add = max(0, max_allowed - current_quantity)
            
            if can_add > 0:
                # Add up to the limit
                to_add = min(deck_quantity, can_add)
                
                if card_name in self.collection.cards:
                    # Update existing card
                    self.collection.cards[card_name].quantity += to_add
                    cards_updated += 1
                else:
                    # Add new card
                    self.collection.add_card(card, to_add)
                    cards_added += 1
                
                if deck_quantity > to_add:
                    cards_skipped += 1
            else:
                cards_skipped += 1
        
        # Save collection if any changes were made
        if cards_added > 0 or cards_updated > 0:
            if hasattr(self, 'collection') and hasattr(self.collection, 'save'):
                try:
                    # Try to save collection if it has a save method
                    # Otherwise, we'll need the collection tab to handle saving
                    pass
                except:
                    pass
            
                    # Update collection display if requested and we have access to collection tab
            if update_collection_display:
                # Find the collection tab through the main window
                try:
                    main_window = self.parent.master  # Get the main window
                    if hasattr(main_window, 'collection_tab'):
                        main_window.collection_tab.apply_filters()
                        main_window.collection_tab.refresh_display()
                        main_window.collection_tab.save_collection()
                        # Refresh our autocomplete suggestions since collection changed
                        self.refresh_autocomplete_suggestions()
                except:
                    pass
        
        return {
            'cards_added': cards_added,
            'cards_updated': cards_updated, 
            'cards_skipped': cards_skipped
        }
    
    def edit_card_quantity(self, tree, sideboard=False):
        """Edit quantity of selected card"""
        selection = tree.selection()
        if not selection or not self.current_deck:
            return
        
        item = selection[0]
        card_name = tree.item(item)['values'][1]
        current_qty = tree.item(item)['values'][0]
        
        new_qty = simpledialog.askinteger("Edit Quantity", f"Quantity for {card_name}:", 
                                        initialvalue=int(current_qty), minvalue=0, maxvalue=4)
        if new_qty is not None:
            # Find and update the card
            for deck_card in self.current_deck.cards:
                if deck_card.card.name == card_name and deck_card.sideboard == sideboard:
                    if new_qty == 0:
                        self.current_deck.cards.remove(deck_card)
                    else:
                        deck_card.quantity = new_qty
                    break
            
            self.refresh_deck_contents()
            self.update_statistics()
            self.save_decks()
    
    def remove_card_from_deck(self, tree, sideboard=False):
        """Remove card from deck"""
        selection = tree.selection()
        if not selection or not self.current_deck:
            return
        
        item = selection[0]
        card_name = tree.item(item)['values'][1]
        
        if messagebox.askyesno("Confirm", f"Remove {card_name} from deck?"):
            self.current_deck.remove_card(card_name, 999, sideboard)  # Remove all copies
            self.refresh_deck_contents()
            self.update_statistics()
            self.save_decks()
    
    def move_card(self, tree, from_sideboard=False):
        """Move card between mainboard and sideboard"""
        selection = tree.selection()
        if not selection or not self.current_deck:
            return
        
        item = selection[0]
        card_name = tree.item(item)['values'][1]
        quantity = int(tree.item(item)['values'][0])
        
        # Find and move the card
        for deck_card in self.current_deck.cards:
            if deck_card.card.name == card_name and deck_card.sideboard == from_sideboard:
                deck_card.sideboard = not from_sideboard
                break
        
        self.refresh_deck_contents()
        self.save_decks()
    
    def refresh_deck_list(self):
        """Refresh the deck list display"""
        self.deck_listbox.delete(0, tk.END)
        for deck in self.decks:
            card_count = deck.get_total_cards()
            self.deck_listbox.insert(tk.END, f"{deck.name} ({card_count})")
    
    def update_deck_info(self):
        """Update deck information display"""
        if self.current_deck:
            self.deck_name_var.set(self.current_deck.name)
            self.format_var.set(self.current_deck.format)
        else:
            self.deck_name_var.set("")
            self.format_var.set("Standard")
        
        self.update_statistics()
    
    def refresh_deck_contents(self):
        """Refresh the deck contents display"""
        # Clear existing items
        for item in self.mainboard_tree.get_children():
            self.mainboard_tree.delete(item)
        for item in self.sideboard_tree.get_children():
            self.sideboard_tree.delete(item)
        
        if not self.current_deck:
            return
        
        # Add mainboard cards
        mainboard_cards = self.current_deck.get_mainboard_cards()
        for deck_card in sorted(mainboard_cards, key=lambda x: (x.card.converted_mana_cost, x.card.name)):
            card = deck_card.card
            values = (
                deck_card.quantity,
                card.name,
                card.card_type,
                card.converted_mana_cost,
                ','.join(card.colors)
            )
            self.mainboard_tree.insert('', 'end', values=values)
        
        # Add sideboard cards
        sideboard_cards = self.current_deck.get_sideboard_cards()
        for deck_card in sorted(sideboard_cards, key=lambda x: (x.card.converted_mana_cost, x.card.name)):
            card = deck_card.card
            values = (
                deck_card.quantity,
                card.name,
                card.card_type,
                card.converted_mana_cost,
                ','.join(card.colors)
            )
            self.sideboard_tree.insert('', 'end', values=values)
    
    def update_statistics(self):
        """Update deck statistics display"""
        if not self.current_deck:
            self.stats_text.delete(1.0, tk.END)
            return
        
        mainboard_count = self.current_deck.get_total_cards(include_sideboard=False)
        sideboard_count = len(self.current_deck.get_sideboard_cards())
        
        stats_text = f"Total Cards: {mainboard_count}\\n"
        stats_text += f"Sideboard: {sideboard_count}\\n"
        stats_text += f"Format: {self.current_deck.format}\\n\\n"
        
        # Mana curve
        mana_curve = self.current_deck.get_mana_curve()
        if mana_curve:
            stats_text += "Mana Curve:\\n"
            for cmc in sorted(mana_curve.keys()):
                cmc_label = f"{cmc}+" if cmc >= 7 else str(cmc)
                stats_text += f"  {cmc_label}: {mana_curve[cmc]}\\n"
            stats_text += "\\n"
        
        # Color distribution
        colors = self.current_deck.get_color_distribution()
        if colors:
            stats_text += "Colors:\\n"
            for color, count in sorted(colors.items()):
                stats_text += f"  {color}: {count}\\n"
            stats_text += "\\n"
        
        # Type distribution
        types = self.current_deck.get_type_distribution()
        if types:
            stats_text += "Card Types:\\n"
            for card_type, count in sorted(types.items()):
                stats_text += f"  {card_type}: {count}\\n"
        
        # Format legality
        is_legal = self.current_deck.is_legal_format()
        stats_text += f"\\nFormat Legal: {'Yes' if is_legal else 'No'}"
        
        self.stats_text.delete(1.0, tk.END)
        self.stats_text.insert(1.0, stats_text)
    
    def refresh_display(self):
        """Refresh all displays"""
        self.refresh_deck_list()
        if self.decks:
            self.deck_listbox.selection_set(0)
            self.on_deck_select()
        else:
            self.update_deck_info()
            self.refresh_deck_contents()
    
    def import_deck_csv(self):
        """Import deck from CSV file"""
        filename = filedialog.askopenfilename(
            title="Import Deck (CSV)",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        
        if filename:
            try:
                csv_handler = CSVHandler()
                deck = csv_handler.import_deck_from_csv(filename)
                self.decks.append(deck)
                self.refresh_deck_list()
                self.deck_listbox.selection_set(len(self.decks) - 1)
                self.on_deck_select()
                self.save_decks()
                
                # Add deck cards to collection with playset limits
                if self.collection:
                    result = self.add_deck_cards_to_collection(deck)
                    collection_msg = f"\n\nCollection updated:\n"
                    collection_msg += f"• {result['cards_added']} new cards added\n"
                    collection_msg += f"• {result['cards_updated']} existing cards updated\n"
                    if result['cards_skipped'] > 0:
                        collection_msg += f"• {result['cards_skipped']} cards skipped (already at 4-card limit)"
                    
                    messagebox.showinfo("Success", f"Deck imported successfully!{collection_msg}")
                else:
                    messagebox.showinfo("Success", "Deck imported successfully!")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to import deck: {str(e)}")
    
    def import_deck_arena(self):
        """Import deck from Arena format file"""
        filename = filedialog.askopenfilename(
            title="Import Deck (Arena Format)",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        
        if filename:
            try:
                csv_handler = CSVHandler()
                deck = csv_handler.import_deck_from_arena_format(filename)
                self.decks.append(deck)
                self.refresh_deck_list()
                self.deck_listbox.selection_set(len(self.decks) - 1)
                self.on_deck_select()
                self.save_decks()
                
                # Add deck cards to collection with playset limits
                if self.collection:
                    result = self.add_deck_cards_to_collection(deck)
                    collection_msg = f"\n\nCollection updated:\n"
                    collection_msg += f"• {result['cards_added']} new cards added\n"
                    collection_msg += f"• {result['cards_updated']} existing cards updated\n"
                    if result['cards_skipped'] > 0:
                        collection_msg += f"• {result['cards_skipped']} cards skipped (already at 4-card limit)"
                    
                    messagebox.showinfo("Success", f"Deck imported successfully!{collection_msg}")
                else:
                    messagebox.showinfo("Success", "Deck imported successfully!")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to import deck: {str(e)}")
    
    def export_deck_csv(self):
        """Export current deck to CSV"""
        if not self.current_deck:
            messagebox.showwarning("Warning", "No deck selected")
            return
        
        filename = filedialog.asksaveasfilename(
            title="Export Deck (CSV)",
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            initialfile=f"{self.current_deck.name}.csv"
        )
        
        if filename:
            try:
                CSVHandler.export_deck_to_csv(self.current_deck, filename)
                messagebox.showinfo("Success", "Deck exported successfully!")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to export deck: {str(e)}")
    
    def export_deck_arena(self):
        """Export current deck to Arena format"""
        if not self.current_deck:
            messagebox.showwarning("Warning", "No deck selected")
            return
        
        filename = filedialog.asksaveasfilename(
            title="Export Deck (Arena Format)",
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
            initialfile=f"{self.current_deck.name}.txt"
        )
        
        if filename:
            try:
                CSVHandler.export_deck_to_arena_format(self.current_deck, filename)
                messagebox.showinfo("Success", "Deck exported successfully!")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to export deck: {str(e)}")
    
    def import_deck_clipboard(self):
        """Import deck from clipboard"""
        try:
            deck = self.clipboard_handler.import_deck_from_clipboard()
            if deck:
                # Check clipboard format
                content = self.clipboard_handler.get_clipboard_content()
                format_type = self.clipboard_handler.detect_format(content)
                format_desc = self.clipboard_handler.get_format_description(format_type)
                
                # Ask user to confirm import
                result = messagebox.askyesno(
                    "Import Deck from Clipboard", 
                    f"Found deck with {deck.get_total_cards()} total cards.\n"
                    f"Format detected: {format_desc}\n\n"
                    f"Import this deck?\n\n"
                    f"Note: Cards will also be added to your collection\n"
                    f"(max 4 copies per card as per Arena playset rules)"
                )
                
                if result:
                    self.decks.append(deck)
                    self.refresh_deck_list()
                    self.deck_listbox.selection_clear(0, tk.END)
                    self.deck_listbox.selection_set(len(self.decks) - 1)
                    self.on_deck_select()
                    self.save_decks()
                    
                    # Add deck cards to collection with playset limits
                    if self.collection:
                        collection_result = self.add_deck_cards_to_collection(deck)
                        collection_msg = f"\n\nCollection updated:\n"
                        collection_msg += f"• {collection_result['cards_added']} new cards added\n"
                        collection_msg += f"• {collection_result['cards_updated']} existing cards updated\n"
                        if collection_result['cards_skipped'] > 0:
                            collection_msg += f"• {collection_result['cards_skipped']} cards skipped (already at 4-card limit)"
                        
                        messagebox.showinfo("Success", f"Imported deck '{deck.name}' from clipboard!{collection_msg}")
                    else:
                        messagebox.showinfo("Success", f"Imported deck '{deck.name}' from clipboard!")
            else:
                content = self.clipboard_handler.get_clipboard_content()
                if not content:
                    messagebox.showwarning("Warning", "Clipboard is empty")
                else:
                    messagebox.showerror("Error", "Could not parse clipboard content as a deck list")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to import from clipboard: {str(e)}")
    
    def export_deck_clipboard(self):
        """Export current deck to clipboard"""
        if not self.current_deck:
            messagebox.showwarning("Warning", "No deck selected")
            return
        
        # Ask user for format preference
        from tkinter import simpledialog
        format_choice = messagebox.askyesnocancel(
            "Export Format",
            "Choose export format:\n\n"
            "Yes = Arena format (with set codes)\n"
            "No = Simple format (card names only)\n"
            "Cancel = Cancel export"
        )
        
        if format_choice is None:  # Cancel
            return
        
        format_type = "arena" if format_choice else "simple"
        
        try:
            success = self.clipboard_handler.export_deck_to_clipboard(self.current_deck, format_type)
            if success:
                format_desc = "Arena format" if format_choice else "Simple format"
                messagebox.showinfo("Success", f"Deck copied to clipboard in {format_desc}!")
            else:
                messagebox.showerror("Error", "Failed to copy deck to clipboard")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export to clipboard: {str(e)}")
    
    def load_decks(self):
        """Load decks from files"""
        decks_dir = os.path.join("data", "decks")
        if not os.path.exists(decks_dir):
            return
        
        for filename in os.listdir(decks_dir):
            if filename.endswith('.json'):
                filepath = os.path.join(decks_dir, filename)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    deck = Deck.from_dict(data)
                    self.decks.append(deck)
                except Exception as e:
                    print(f"Failed to load deck {filename}: {e}")
    
    def save_decks(self):
        """Save all decks to files"""
        decks_dir = os.path.join("data", "decks")
        os.makedirs(decks_dir, exist_ok=True)
        
        # Clear existing files
        for filename in os.listdir(decks_dir):
            if filename.endswith('.json'):
                os.remove(os.path.join(decks_dir, filename))
        
        # Save current decks
        for i, deck in enumerate(self.decks):
            filename = f"deck_{i:03d}_{deck.name.replace(' ', '_')}.json"
            filepath = os.path.join(decks_dir, filename)
            try:
                with open(filepath, 'w', encoding='utf-8') as f:
                    json.dump(deck.to_dict(), f, indent=2)
            except Exception as e:
                print(f"Failed to save deck {deck.name}: {e}")
