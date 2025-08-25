# Magic: The Gathering Arena Deck Manager

A comprehensive tool for managing your Magic: The Gathering Arena collection and decks.

## Features

- **Collection Management**: Track your card collection with quantities and rarities
- **Deck Builder**: Create and manage multiple decks
- **Smart Autocomplete**: Intelligent card suggestions while building decks from your collection
- **Import/Export**: Import and export decks and collections via CSV
- **Clipboard Support**: Import/export decks and cards directly from system clipboard
- **Advanced Sorting**: Sort cards by color, creature type, mana cost, and more
- **Deck Analysis**: View deck statistics and mana curves
- **AI Recommendations**: Get intelligent card suggestions based on synergy and popularity

## Clipboard Functionality

The tool now supports importing and exporting decks directly from your system clipboard:

### Supported Formats:
- **Arena Format**: `4 Lightning Bolt (M21) 159`
- **Simple Format**: `4 Lightning Bolt` or `Lightning Bolt`

### Import from Clipboard:
1. Copy a deck list from any source (Arena export, website, etc.)
2. Click "Import Clipboard" in the Decks tab
3. The tool will automatically detect the format and import your deck
4. **NEW**: Cards are automatically added to your collection (max 4 per card)

### Export to Clipboard:
1. Select a deck in the Decks tab
2. Click "Copy to Clipboard"
3. Choose between Arena format (with set codes) or Simple format
4. Paste anywhere you need the deck list

### Collection Import:
- Use "Import Clipboard" in the Collection tab to add cards from clipboard to your collection
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
