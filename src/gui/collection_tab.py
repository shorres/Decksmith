"""
Collection management tab for the MTG Arena Deck Manager
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog
import json
import os
from datetime import datetime
from typing import List, Dict, Optional

from models.card import Card
from models.collection import Collection, CollectionCard
from utils.csv_handler import CSVHandler
from utils.clipboard_handler import ClipboardHandler
from utils.performance_optimizer import get_performance_optimizer, LazyTreeView
from gui.scryfall_autocomplete import ScryfallAutocompleteEntry
from gui.card_details_modal import show_card_details_modal
from utils.scryfall_api import scryfall_api

class CollectionTab:
    """Collection management interface"""
    
    def __init__(self, parent):
        self.parent = parent
        self.collection = Collection()
        self.filtered_cards = []
        self.clipboard_handler = ClipboardHandler()  # Clipboard functionality
        
        self.create_widgets()
        self.load_collection()
        self.refresh_display()
    
    def on_tab_focus(self):
        """Called when the collection tab gets focus - optimized with debouncing"""
        optimizer = get_performance_optimizer()
        if optimizer.debounce_tab_switch(self._perform_tab_focus, "Collection Tab"):
            self._perform_tab_focus()
    
    def _perform_tab_focus(self):
        """Internal method to perform the actual tab focus update"""
        # Only refresh if needed
        if hasattr(self, '_needs_refresh') and self._needs_refresh:
            self.refresh_display()
            self._needs_refresh = False
    
    def create_widgets(self):
        """Create the collection tab widgets"""
        self.frame = ttk.Frame(self.parent)
        
        # Create main paned window
        paned = ttk.PanedWindow(self.frame, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Left panel - filters and stats
        left_frame = ttk.Frame(paned)
        paned.add(left_frame, weight=1)
        
        # Right panel - card list
        right_frame = ttk.Frame(paned)
        paned.add(right_frame, weight=3)
        
        self.create_filter_panel(left_frame)
        self.create_card_list(right_frame)
    
    def create_filter_panel(self, parent):
        """Create the filter and statistics panel"""
        # Filters frame
        filters_frame = ttk.LabelFrame(parent, text="Filters")
        filters_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Name filter
        ttk.Label(filters_frame, text="Card Name:").pack(anchor=tk.W, padx=5)
        self.name_var = tk.StringVar()
        name_entry = ttk.Entry(filters_frame, textvariable=self.name_var)
        name_entry.pack(fill=tk.X, padx=5, pady=2)
        name_entry.bind('<KeyRelease>', self.on_filter_change)
        
        # Color filter
        ttk.Label(filters_frame, text="Colors:").pack(anchor=tk.W, padx=5, pady=(10,0))
        colors_frame = ttk.Frame(filters_frame)
        colors_frame.pack(fill=tk.X, padx=5, pady=2)
        
        self.color_vars = {}
        colors = [("W", "White"), ("U", "Blue"), ("B", "Black"), ("R", "Red"), ("G", "Green")]
        for i, (code, name) in enumerate(colors):
            var = tk.BooleanVar()
            self.color_vars[code] = var
            cb = ttk.Checkbutton(colors_frame, text=code, variable=var, command=self.on_filter_change)
            cb.grid(row=i//3, column=i%3, sticky=tk.W)
        
        # Type filter
        ttk.Label(filters_frame, text="Card Type:").pack(anchor=tk.W, padx=5, pady=(10,0))
        self.type_var = tk.StringVar()
        type_combo = ttk.Combobox(filters_frame, textvariable=self.type_var)
        type_combo['values'] = ('', 'Creature', 'Instant', 'Sorcery', 'Enchantment', 'Artifact', 'Planeswalker', 'Land')
        type_combo.pack(fill=tk.X, padx=5, pady=2)
        type_combo.bind('<<ComboboxSelected>>', self.on_filter_change)
        
        # Rarity filter
        ttk.Label(filters_frame, text="Rarity:").pack(anchor=tk.W, padx=5, pady=(10,0))
        self.rarity_var = tk.StringVar()
        rarity_combo = ttk.Combobox(filters_frame, textvariable=self.rarity_var)
        rarity_combo['values'] = ('', 'Common', 'Uncommon', 'Rare', 'Mythic')
        rarity_combo.pack(fill=tk.X, padx=5, pady=2)
        rarity_combo.bind('<<ComboboxSelected>>', self.on_filter_change)
        
        # Clear filters button
        ttk.Button(filters_frame, text="Clear Filters", command=self.clear_filters).pack(pady=10)
        
        # Statistics frame
        stats_frame = ttk.LabelFrame(parent, text="Collection Statistics")
        stats_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.stats_text = tk.Text(stats_frame, height=8, width=20)
        self.stats_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Import/Export buttons
        buttons_frame = ttk.Frame(parent)
        buttons_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(buttons_frame, text="Import CSV", command=self.import_collection).pack(fill=tk.X, pady=2)
        ttk.Button(buttons_frame, text="Import Clipboard", command=self.import_cards_clipboard).pack(fill=tk.X, pady=2)
        ttk.Button(buttons_frame, text="Export CSV", command=self.export_collection).pack(fill=tk.X, pady=2)
        ttk.Button(buttons_frame, text="Add Card", command=self.add_card).pack(fill=tk.X, pady=2)
    
    def create_card_list(self, parent):
        """Create the card list display"""
        list_frame = ttk.LabelFrame(parent, text="Cards")
        list_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Header frame with trash icons
        header_frame = ttk.Frame(list_frame)
        header_frame.pack(fill=tk.X, padx=5, pady=(5, 2))
        
        # Title label
        ttk.Label(header_frame, text="Collection", font=('TkDefaultFont', 10, 'bold')).pack(side=tk.LEFT)
        
        # Trash operations on the right
        trash_frame = ttk.Frame(header_frame)
        trash_frame.pack(side=tk.RIGHT)
        
        # Remove selected button (trash icon)
        remove_selected_btn = ttk.Button(trash_frame, text="🗑️", width=3, 
                                       command=self.remove_selected_cards)
        remove_selected_btn.pack(side=tk.RIGHT, padx=(0, 2))
        
        # Remove filtered button (trash with funnel icon)
        remove_filtered_btn = ttk.Button(trash_frame, text="🗑️🔽", width=8, 
                                       command=self.remove_filtered_cards)
        remove_filtered_btn.pack(side=tk.RIGHT, padx=(0, 2))
        
        # Treeview for card list
        columns = ('Name', 'Type', 'Rarity', 'Colors', 'CMC', 'Quantity', 'Foil')
        self.tree = ttk.Treeview(list_frame, columns=columns, show='headings')
        
        # Configure columns
        self.tree.heading('Name', text='Card Name')
        self.tree.heading('Type', text='Type')
        self.tree.heading('Rarity', text='Rarity')
        self.tree.heading('Colors', text='Colors')
        self.tree.heading('CMC', text='CMC')
        self.tree.heading('Quantity', text='Qty')
        self.tree.heading('Foil', text='Foil')
        
        self.tree.column('Name', width=200)
        self.tree.column('Type', width=120)
        self.tree.column('Rarity', width=80)
        self.tree.column('Colors', width=80)
        self.tree.column('CMC', width=50)
        self.tree.column('Quantity', width=50)
        self.tree.column('Foil', width=50)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        # Pack
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Context menu and event bindings
        self.create_context_menu()
        self.tree.bind("<Button-3>", self.show_context_menu)
        self.tree.bind("<Double-1>", self.on_card_double_click)
    
    def create_context_menu(self):
        """Create context menu for card list"""
        self.context_menu = tk.Menu(self.frame, tearoff=0)
        self.context_menu.add_command(label="Edit Quantity", command=self.edit_quantity)
        self.context_menu.add_command(label="Remove Card", command=self.remove_card)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="View Details", command=self.view_card_details)
    
    def show_context_menu(self, event):
        """Show context menu"""
        item = self.tree.identify_row(event.y)
        if item:
            self.tree.selection_set(item)
            self.context_menu.post(event.x_root, event.y_root)
    
    def on_filter_change(self, event=None):
        """Handle filter changes"""
        self.apply_filters()
        self.refresh_display()
    
    def apply_filters(self):
        """Apply current filters to card list"""
        filters = {}
        
        # Name filter
        if self.name_var.get().strip():
            filters['name'] = self.name_var.get().strip()
        
        # Color filter
        selected_colors = [color for color, var in self.color_vars.items() if var.get()]
        if selected_colors:
            filters['colors'] = selected_colors
        
        # Type filter
        if self.type_var.get():
            filters['card_type'] = self.type_var.get()
        
        # Rarity filter
        if self.rarity_var.get():
            filters['rarity'] = self.rarity_var.get()
        
        self.filtered_cards = self.collection.filter_cards(**filters)
    
    def clear_filters(self):
        """Clear all filters"""
        self.name_var.set("")
        for var in self.color_vars.values():
            var.set(False)
        self.type_var.set("")
        self.rarity_var.set("")
        self.on_filter_change()
    
    def refresh_display(self):
        """Refresh the card list display with lazy loading optimization"""
        # Use lazy tree view for efficient updates
        lazy_tree = LazyTreeView(self.tree)
        
        # Create data key for change detection
        data_key = tuple((cc.card.name, cc.quantity, cc.quantity_foil) for cc in self.filtered_cards)
        
        # Only update if data has changed
        if lazy_tree.update_data(data_key):
            return  # No changes needed
        
        # Clear existing items only if updating
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Add filtered cards
        for collection_card in self.filtered_cards:
            card = collection_card.card
            values = (
                card.name,
                card.card_type,
                card.rarity,
                ','.join(card.colors),
                card.converted_mana_cost,
                collection_card.quantity,
                collection_card.quantity_foil
            )
            self.tree.insert('', 'end', values=values)
        
        # Update statistics
        self.update_statistics()
    
    def update_statistics(self):
        """Update collection statistics display"""
        stats = self.collection.get_completion_stats()
        
        stats_text = f"Total Cards: {stats['total_cards']}\n"
        stats_text += f"Unique Cards: {stats['unique_cards']}\n\n"
        stats_text += f"Commons: {stats['commons']}\n"
        stats_text += f"Uncommons: {stats['uncommons']}\n"
        stats_text += f"Rares: {stats['rares']}\n"
        stats_text += f"Mythics: {stats['mythics']}\n\n"
        
        # Add color distribution
        color_dist = {}
        for collection_card in self.collection.cards.values():
            for color in collection_card.card.colors:
                color_dist[color] = color_dist.get(color, 0) + collection_card.quantity
        
        if color_dist:
            stats_text += "Color Distribution:\n"
            for color, count in sorted(color_dist.items()):
                stats_text += f"  {color}: {count}\n"
        
        self.stats_text.delete(1.0, tk.END)
        self.stats_text.insert(1.0, stats_text)
    
    def import_collection(self):
        """Import collection from CSV file"""
        filename = filedialog.askopenfilename(
            title="Import Collection",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        
        if filename:
            try:
                csv_handler = CSVHandler()
                self.collection = csv_handler.import_collection_from_csv(filename)
                self.apply_filters()
                self.refresh_display()
                messagebox.showinfo("Success", "Collection imported successfully!")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to import collection: {str(e)}")
    
    def import_cards_clipboard(self):
        """Import cards from clipboard to collection"""
        try:
            cards = self.clipboard_handler.import_cards_from_clipboard()
            if cards:
                # Check clipboard format
                content = self.clipboard_handler.get_clipboard_content()
                format_type = self.clipboard_handler.detect_format(content)
                format_desc = self.clipboard_handler.get_format_description(format_type)
                
                # Ask user to confirm import
                result = messagebox.askyesno(
                    "Import Cards from Clipboard", 
                    f"Found {len(cards)} cards to import.\n"
                    f"Format detected: {format_desc}\n\n"
                    f"Add these cards to your collection?"
                )
                
                if result:
                    # Add cards to collection
                    added_count = 0
                    updated_count = 0
                    
                    for card, quantity in cards:
                        # Check if card already exists in collection
                        if card.name in self.collection.cards:
                            # Update existing card quantity
                            self.collection.cards[card.name].quantity += quantity
                            updated_count += 1
                        else:
                            # Add new card to collection
                            self.collection.add_card(card, quantity)
                            added_count += 1
                    
                    self.apply_filters()
                    self.refresh_display()
                    self.save_collection()
                    
                    messagebox.showinfo("Success", 
                        f"Imported {len(cards)} card entries from clipboard!\n"
                        f"{added_count} new unique cards added.\n"
                        f"{updated_count} existing cards updated.")
            else:
                content = self.clipboard_handler.get_clipboard_content()
                if not content:
                    messagebox.showwarning("Warning", "Clipboard is empty")
                else:
                    messagebox.showerror("Error", "Could not parse clipboard content as card list")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to import from clipboard: {str(e)}")
    
    def export_collection(self):
        """Export collection to CSV file"""
        filename = filedialog.asksaveasfilename(
            title="Export Collection",
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        
        if filename:
            try:
                CSVHandler.export_collection_to_csv(self.collection, filename)
                messagebox.showinfo("Success", "Collection exported successfully!")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to export collection: {str(e)}")
    
    def add_card(self):
        """Add a new card to the collection"""
        dialog = AddCardDialog(self.frame)
        if dialog.result:
            card_data, quantity, foil = dialog.result
            card = Card(**card_data)
            self.collection.add_card(card, quantity, foil)
            self.apply_filters()
            self.refresh_display()
    
    def edit_quantity(self):
        """Edit the quantity of selected card"""
        selection = self.tree.selection()
        if not selection:
            return
        
        item = selection[0]
        card_name = self.tree.item(item)['values'][0]
        current_qty = self.tree.item(item)['values'][5]
        current_foil = self.tree.item(item)['values'][6]
        
        new_qty = simpledialog.askinteger("Edit Quantity", f"Quantity for {card_name}:", initialvalue=int(current_qty), minvalue=0)
        if new_qty is not None:
            new_foil = simpledialog.askinteger("Edit Foil Quantity", f"Foil quantity for {card_name}:", initialvalue=int(current_foil), minvalue=0)
            if new_foil is not None:
                # Update the collection
                if card_name in self.collection.cards:
                    self.collection.cards[card_name].quantity = new_qty
                    self.collection.cards[card_name].quantity_foil = new_foil
                    if new_qty == 0 and new_foil == 0:
                        del self.collection.cards[card_name]
                
                self.apply_filters()
                self.refresh_display()
    
    def remove_card(self):
        """Remove selected card from collection"""
        selection = self.tree.selection()
        if not selection:
            return
        
        item = selection[0]
        card_name = self.tree.item(item)['values'][0]
        
        if messagebox.askyesno("Confirm", f"Remove {card_name} from collection?"):
            if card_name in self.collection.cards:
                del self.collection.cards[card_name]
                self.apply_filters()
                self.refresh_display()
    
    def view_card_details(self):
        """View detailed information about selected card"""
        selection = self.tree.selection()
        if not selection:
            return
        
        item = selection[0]
        card_name = self.tree.item(item)['values'][0]
        
        if card_name in self.collection.cards:
            card = self.collection.cards[card_name].card
            details = f"Name: {card.name}\n"
            details += f"Mana Cost: {card.mana_cost}\n"
            details += f"CMC: {card.converted_mana_cost}\n"
            details += f"Type: {card.card_type}\n"
            details += f"Rarity: {card.rarity}\n"
            details += f"Colors: {', '.join(card.colors)}\n"
            if card.power is not None and card.toughness is not None:
                details += f"P/T: {card.power}/{card.toughness}\n"
            if card.text:
                details += f"\nText: {card.text}"
            
            messagebox.showinfo(f"Card Details - {card_name}", details)
    
    def load_collection(self):
        """Load collection from file if it exists"""
        collection_file = os.path.join("data", "collections", "default.json")
        if os.path.exists(collection_file):
            try:
                with open(collection_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                self.collection = Collection.from_dict(data)
                self.apply_filters()
            except Exception as e:
                print(f"Failed to load collection: {e}")
    
    def save_collection(self):
        """Save collection to file"""
        os.makedirs(os.path.join("data", "collections"), exist_ok=True)
        collection_file = os.path.join("data", "collections", "default.json")
        try:
            with open(collection_file, 'w', encoding='utf-8') as f:
                json.dump(self.collection.to_dict(), f, indent=2)
        except Exception as e:
            print(f"Failed to save collection: {e}")

    def on_card_double_click(self, event):
        """Handle double-click on a card to show details modal"""
        selection = self.tree.selection()
        if not selection:
            return
        
        item = selection[0]
        values = self.tree.item(item)['values']
        card_name = values[0]
        
        if card_name in self.collection.cards:
            collection_card = self.collection.cards[card_name]
            card = collection_card.card
            
            # Show the card details modal
            show_card_details_modal(self.parent, card, collection_card)
    
    def remove_selected_cards(self):
        """Remove all currently selected cards from collection"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select cards to remove.")
            return
        
        card_names = []
        for item in selection:
            card_name = self.tree.item(item)['values'][0]
            card_names.append(card_name)
        
        if len(card_names) == 1:
            message = f"Remove '{card_names[0]}' from collection?"
            title = "Confirm Removal"
        else:
            message = f"Remove {len(card_names)} selected cards from collection?\n\nCards to remove:\n"
            message += "\n".join(f"• {name}" for name in card_names[:10])
            if len(card_names) > 10:
                message += f"\n... and {len(card_names) - 10} more cards"
            title = "Confirm Mass Removal"
        
        if messagebox.askyesno(title, message):
            removed_count = 0
            for card_name in card_names:
                if card_name in self.collection.cards:
                    del self.collection.cards[card_name]
                    removed_count += 1
            
            self.apply_filters()
            self.refresh_display()
            self.save_collection()
            
            messagebox.showinfo("Success", f"Removed {removed_count} cards from collection.")
    
    def remove_filtered_cards(self):
        """Remove all cards currently shown in the filtered view"""
        if not self.filtered_cards:
            messagebox.showwarning("No Cards", "No cards to remove in current filter.")
            return
        
        card_count = len(self.filtered_cards)
        
        # Show confirmation with details about what will be removed
        message = f"Remove ALL {card_count} cards currently shown in the filtered view?\n\n"
        message += "This will permanently remove:\n"
        
        # Show first few cards as examples
        for i, collection_card in enumerate(self.filtered_cards[:5]):
            message += f"• {collection_card.card.name}\n"
        
        if card_count > 5:
            message += f"... and {card_count - 5} more cards\n"
        
        message += f"\n⚠️ This action cannot be undone!"
        
        if messagebox.askyesno("Confirm Mass Removal", message):
            # Additional confirmation for large removals
            if card_count > 50:
                confirm_msg = f"Are you absolutely sure you want to remove {card_count} cards?\n\nType 'REMOVE' to confirm:"
                user_input = simpledialog.askstring("Final Confirmation", confirm_msg)
                if user_input != "REMOVE":
                    messagebox.showinfo("Cancelled", "Mass removal cancelled.")
                    return
            
            removed_count = 0
            cards_to_remove = [cc.card.name for cc in self.filtered_cards]
            
            for card_name in cards_to_remove:
                if card_name in self.collection.cards:
                    del self.collection.cards[card_name]
                    removed_count += 1
            
            # Clear filters to show full collection
            self.clear_filters()
            self.refresh_display()
            self.save_collection()
            
            messagebox.showinfo("Success", f"Removed {removed_count} cards from collection.")

class AddCardDialog:
    """Dialog for adding new cards to collection"""
    
    def __init__(self, parent):
        self.result = None
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Add Card")
        self.dialog.geometry("400x500")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        self.create_widgets()
        self.dialog.wait_window()
    
    def on_card_selected(self, card_name: str):
        """Called when a card is selected from autocomplete"""
        # Auto-fill card data when a card is selected
        self.auto_fill_card_data()
    
    def auto_fill_card_data(self):
        """Auto-fill card data from Scryfall"""
        card_name = self.card_autocomplete.get().strip()
        if not card_name:
            return
        
        # Show that we're loading data
        original_button_text = "Auto-Fill"  # Default text
        auto_fill_button = None
        
        # Find the auto-fill button to show loading state
        for widget in self.dialog.winfo_children():
            if isinstance(widget, ttk.Frame):
                for child in widget.winfo_children():
                    if isinstance(child, ttk.Button) and "Auto-Fill" in str(child.cget('text')):
                        auto_fill_button = child
                        original_button_text = str(child.cget('text'))
                        child.configure(text="Loading...", state='disabled')
                        break
        
        try:
            # Get card data from Scryfall
            scryfall_card = scryfall_api.get_card_fuzzy(card_name)
            if scryfall_card:
                # Fill in all the fields
                self.mana_cost_var.set(scryfall_card.mana_cost)
                self.cmc_var.set(int(scryfall_card.cmc))
                self.type_var.set(scryfall_card.type_line)
                
                # Extract creature type from type line
                if "Creature" in scryfall_card.type_line and "—" in scryfall_card.type_line:
                    creature_type = scryfall_card.type_line.split("—")[1].strip()
                    self.creature_type_var.set(creature_type)
                else:
                    self.creature_type_var.set("")  # Clear if not a creature
                
                self.rarity_var.set(scryfall_card.rarity)
                
                # Set colors - clear all first, then set the ones that apply
                for color_code in self.color_vars:
                    self.color_vars[color_code].set(color_code in scryfall_card.colors)
                
                # Visual feedback that auto-fill worked
                if auto_fill_button:
                    auto_fill_button.configure(text="✓ Auto-Filled", state='normal')
                    # Reset button text after a delay
                    self.dialog.after(2000, lambda: auto_fill_button.configure(text=original_button_text) if auto_fill_button.winfo_exists() else None)
            else:
                # Card not found
                if auto_fill_button:
                    auto_fill_button.configure(text="Card Not Found", state='normal')
                    self.dialog.after(2000, lambda: auto_fill_button.configure(text=original_button_text) if auto_fill_button.winfo_exists() else None)
                
        except Exception as e:
            print(f"Error auto-filling card data: {e}")
            if auto_fill_button:
                auto_fill_button.configure(text="Error", state='normal')
                self.dialog.after(2000, lambda: auto_fill_button.configure(text=original_button_text) if auto_fill_button.winfo_exists() else None)
    
    def create_widgets(self):
        """Create dialog widgets"""
        main_frame = ttk.Frame(self.dialog)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Card name with Scryfall autocomplete
        ttk.Label(main_frame, text="Card Name:").grid(row=0, column=0, sticky=tk.W, pady=2)
        
        self.card_autocomplete = ScryfallAutocompleteEntry(
            main_frame, 
            width=30,
            on_card_selected=self.on_card_selected
        )
        self.card_autocomplete.grid(row=0, column=1, sticky="ew", pady=2)
        
        # Auto-fill button
        ttk.Button(main_frame, text="Auto-Fill", command=self.auto_fill_card_data).grid(row=0, column=2, padx=5)
        
        # Mana cost
        ttk.Label(main_frame, text="Mana Cost:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.mana_cost_var = tk.StringVar()
        ttk.Entry(main_frame, textvariable=self.mana_cost_var).grid(row=1, column=1, sticky="ew", pady=2)
        
        # CMC
        ttk.Label(main_frame, text="CMC:").grid(row=2, column=0, sticky=tk.W, pady=2)
        self.cmc_var = tk.IntVar()
        ttk.Entry(main_frame, textvariable=self.cmc_var).grid(row=2, column=1, sticky="ew", pady=2)
        
        # Card type
        ttk.Label(main_frame, text="Card Type:").grid(row=3, column=0, sticky=tk.W, pady=2)
        self.type_var = tk.StringVar()
        ttk.Entry(main_frame, textvariable=self.type_var).grid(row=3, column=1, sticky="ew", pady=2)
        
        # Creature type
        ttk.Label(main_frame, text="Creature Type:").grid(row=4, column=0, sticky=tk.W, pady=2)
        self.creature_type_var = tk.StringVar()
        ttk.Entry(main_frame, textvariable=self.creature_type_var).grid(row=4, column=1, sticky="ew", pady=2)
        
        # Rarity
        ttk.Label(main_frame, text="Rarity:").grid(row=5, column=0, sticky=tk.W, pady=2)
        self.rarity_var = tk.StringVar(value="Common")
        rarity_combo = ttk.Combobox(main_frame, textvariable=self.rarity_var)
        rarity_combo['values'] = ('Common', 'Uncommon', 'Rare', 'Mythic')
        rarity_combo.grid(row=5, column=1, sticky="ew", pady=2)
        
        # Colors
        ttk.Label(main_frame, text="Colors:").grid(row=6, column=0, sticky=tk.W, pady=2)
        colors_frame = ttk.Frame(main_frame)
        colors_frame.grid(row=6, column=1, sticky="ew", pady=2)
        
        self.color_vars = {}
        colors = [("W", "White"), ("U", "Blue"), ("B", "Black"), ("R", "Red"), ("G", "Green")]
        for i, (code, name) in enumerate(colors):
            var = tk.BooleanVar()
            self.color_vars[code] = var
            ttk.Checkbutton(colors_frame, text=code, variable=var).grid(row=0, column=i)
        
        # Quantity
        ttk.Label(main_frame, text="Quantity:").grid(row=7, column=0, sticky=tk.W, pady=2)
        self.quantity_var = tk.IntVar(value=1)
        ttk.Entry(main_frame, textvariable=self.quantity_var).grid(row=7, column=1, sticky="ew", pady=2)
        
        # Foil
        self.foil_var = tk.BooleanVar()
        ttk.Checkbutton(main_frame, text="Foil", variable=self.foil_var).grid(row=8, column=1, sticky=tk.W, pady=2)
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=9, column=0, columnspan=2, pady=20)
        
        ttk.Button(button_frame, text="Add", command=self.ok_clicked).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=self.cancel_clicked).pack(side=tk.LEFT, padx=5)
        
        # Configure column weights
        main_frame.columnconfigure(1, weight=1)
    
    def ok_clicked(self):
        """Handle OK button click"""
        card_name = self.card_autocomplete.get().strip()
        if not card_name:
            messagebox.showerror("Error", "Card name is required")
            return
        
        colors = [color for color, var in self.color_vars.items() if var.get()]
        
        card_data = {
            'name': card_name,
            'mana_cost': self.mana_cost_var.get(),
            'converted_mana_cost': self.cmc_var.get(),
            'card_type': self.type_var.get(),
            'creature_type': self.creature_type_var.get(),
            'rarity': self.rarity_var.get(),
            'colors': colors
        }
        
        self.result = (card_data, self.quantity_var.get(), self.foil_var.get())
        self.dialog.destroy()
    
    def cancel_clicked(self):
        """Handle Cancel button click"""
        self.dialog.destroy()
