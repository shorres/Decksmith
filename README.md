# Magic: The Gathering Arena Deck Manager

A comprehensive tool for managing your Magic: The Gathering Arena collection and decks with advanced Scryfall integration.

## Features

- **Collection Management**: Track your card collection with quantities and rarities
- **Scryfall Integration**: Real-time card search and auto-fill from the complete MTG database
- **🆕 Auto-Enrichment**: Import lists are automatically enriched with complete card data from Scryfall
- **Deck Builder**: Create and manage multiple decks
- **Smart Autocomplete**: Intelligent card suggestions while building decks from your collection
- **Import/Export**: Import and export decks and collections via CSV
- **Clipboard Support**: Import/export decks and cards directly from system clipboard
- **Advanced Sorting**: Sort cards by color, creature type, mana cost, and more
- **Deck Analysis**: View deck statistics and mana curves
- **AI Recommendations**: Get intelligent card suggestions based on synergy and popularity

## 🚀 **NEW: Scryfall Auto-Enrichment**

When importing card lists, the tool now automatically fetches complete card information from Scryfall:

### ✨ What Gets Auto-Enriched:
- **Mana Cost**: Exact mana symbols and costs
- **Card Type**: Complete type line (e.g., "Legendary Creature — Human Wizard")
- **Creature Types**: Automatically extracted from type lines
- **Rarity**: Common, Uncommon, Rare, Mythic, etc.
- **Colors**: Color identity for deck building
- **Power/Toughness**: For creatures
- **Oracle Text**: Complete rules text
- **Set Information**: Set codes and collector numbers
- **Much More**: All official card data

### 📥 Import Sources That Get Auto-Enriched:
- **CSV Collections**: `name,quantity,quantity_foil` → Complete card data
- **Arena Deck Files**: Simple name lists → Full card information
- **Clipboard Imports**: Any format → Enriched with Scryfall data
- **Manual Imports**: Just provide card names → Get everything else automatically

### 🎯 Benefits:
- **⏱️ No Manual Data Entry**: Just provide card names, get everything else
- **📊 Accurate Statistics**: Proper mana curves, color distribution, etc.  
- **🔍 Better Search/Filter**: Complete data enables advanced filtering
- **🎨 Rich Display**: See mana costs, types, rarities immediately
- **🔄 Always Current**: Data comes fresh from Scryfall's database

### 🖥️ How It Works:
Simply import your card lists as before - the tool handles the rest:
```
# Your simple CSV:
name,quantity
Lightning Bolt,4
Counterspell,3

# Becomes enriched with:
✓ Mana Cost: {R} and {U}{U}
✓ Type: Instant
✓ Rarity: Uncommon  
✓ Colors: R and U
✓ Set Information: Latest printing data
✓ Oracle Text: Complete rules text
```

## Clipboard Functionality

The tool supports importing and exporting decks directly from your system clipboard with **automatic Scryfall enrichment**:

### Supported Formats:
- **Arena Format**: `4 Lightning Bolt (M21) 159`
- **Simple Format**: `4 Lightning Bolt` or `Lightning Bolt`

### Import from Clipboard:
1. Copy a deck list from any source (Arena export, website, etc.)
2. Click "Import Clipboard" in the Decks tab
3. The tool will automatically detect the format and import your deck
4. **🆕 Auto-Enrichment**: All cards are automatically enriched with complete Scryfall data
5. **NEW**: Cards are automatically added to your collection (max 4 per card)

### Export to Clipboard:
1. Select a deck in the Decks tab
2. Click "Copy to Clipboard"
3. Choose between Arena format (with set codes) or Simple format
4. Paste anywhere you need the deck list

### Collection Import:
- Use "Import Clipboard" in the Collection tab to add cards from clipboard to your collection
- **🆕 Auto-Enrichment**: Cards imported this way get full Scryfall data automatically
- Perfect for importing from Arena collection exports or card lists from websites

## 🃏 **Arena Playset Management**

The tool automatically manages Arena playset limits:
- **Maximum 4 copies** per card are added to your collection
- When importing decks, cards are automatically added to your collection
- Duplicate imports across decks won't exceed the 4-card limit
- Import status shows how many cards were added, updated, or skipped due to limits

## 🎯 **Smart Autocomplete**

Enhanced deck building with intelligent card suggestions:
- **Collection-based suggestions**: Only shows cards you actually own
- **Quantity display**: See how many copies you have available (e.g., "Lightning Bolt (4 available)")
- **Real-time filtering**: Type to filter suggestions as you build
- **Keyboard navigation**: Use arrow keys and Enter to select suggestions
- **Smart extraction**: Automatically handles card names with quantity info

## 🔮 **Scryfall Integration**

Powered by Scryfall's comprehensive MTG database:
- **Real-time search**: Type any card name to get instant suggestions from the entire MTG database
- **One-click auto-fill**: Click any suggestion to automatically populate ALL card fields
- **Auto-fill card data**: Complete card information (mana cost, type, rarity, colors) filled instantly
- **Fuzzy matching**: Find cards even with partial or slightly incorrect names
- **Complete database**: Access to every MTG card ever printed
- **Visual feedback**: Loading indicators and confirmation when data is populated
- **Rate-limited API calls**: Respectful API usage following Scryfall guidelines
- **Offline-friendly**: Graceful handling when internet is unavailable

## 💫 **How to Use the Enhanced Features**

### **Adding Cards to Collection:**
1. **Click "Add Card"** in the Collection tab
2. **Start typing** any MTG card name (e.g., "Lightning")
3. **See suggestions** appear from Scryfall's database  
4. **Click any suggestion** → ALL fields auto-populate instantly! ✨
5. **Adjust quantity** if needed and add to collection

### **Enhanced Workflow:**
- **Type "Light"** → See "Lightning Bolt", "Light Up the Stage", etc.
- **Click "Lightning Bolt"** → Mana cost: {R}, Type: Instant, Colors: Red all filled!
- **Just click "Add"** → Card added with complete, accurate data

### **Building Decks:**
- **Use deck builder** with collection-aware autocomplete
- **Import from clipboard** for instant deck creation
- **Get AI recommendations** for card synergies
- **Export to Arena** format for easy import

## Installation

1. Clone this repository
2. Install Python 3.8 or higher
3. Install required dependencies:
   ```
   pip install -r requirements.txt
   ```

## Usage

Run the application:
```
python main.py
```

## Project Structure

```
Magic Tool/
├── main.py                 # Main application entry point
├── src/
│   ├── __init__.py
│   ├── gui/                # GUI components
│   │   ├── __init__.py
│   │   ├── main_window.py  # Main application window
│   │   ├── collection_tab.py  # Collection management tab
│   │   ├── deck_tab.py     # Deck management tab
│   │   └── import_export.py   # Import/export dialogs
│   ├── models/             # Data models
│   │   ├── __init__.py
│   │   ├── card.py         # Card model
│   │   ├── deck.py         # Deck model
│   │   └── collection.py   # Collection model
│   └── utils/              # Utility functions
│       ├── __init__.py
│       ├── csv_handler.py  # CSV import/export
│       └── card_data.py    # Card data utilities
├── data/                   # Data storage
│   ├── collections/        # Collection files
│   └── decks/              # Deck files
└── requirements.txt        # Python dependencies
```



## License

MIT License
