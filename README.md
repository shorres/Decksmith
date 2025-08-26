# Decksmith

A comprehensive desktop application for managing your Magic: The Gathering Arena collection and decks with advanced AI recommendations and Scryfall integration.

🚀 **Ready to use!** Download the latest release - no Python installation required.

**[📥 Download Latest Release](https://github.com/shorres/Magic-Tool/releases/latest)**

## Key Features

✨ **Smart Collection Management**: Track your card collection with quantities and rarities  
🔍 **Scryfall Integration**: Real-time card search and auto-enrichment from the complete MTG database  
🤖 **AI Recommendations**: Get intelligent card suggestions based on synergy and deck analysis  
🏗️ **Advanced Deck Builder**: Create and manage multiple decks with smart autocomplete  
📊 **Deck Analysis**: Statistics, mana curves, and deck health scoring  
📋 **Import/Export**: Support for CSV, Arena formats, and clipboard operations  
💾 **Portable Data**: All your data stays in the application folder

## Auto-Enrichment

Import simple card lists and get complete card data automatically:

```
# Your simple input:
Lightning Bolt,4
Counterspell,3

# Automatically enriched with:
✓ Mana Cost: {R} and {U}{U}
✓ Type: Instant
✓ Rarity: Uncommon  
✓ Colors: Red and Blue
✓ Oracle Text: Complete rules text
```

## Supported Import Formats

- **CSV Collections**: `name,quantity,quantity_foil`
- **Arena Format**: `4 Lightning Bolt (M21) 159`
- **Simple Format**: `4 Lightning Bolt` or just `Lightning Bolt`
- **Clipboard**: Copy/paste from any source

## Installation

### Option 1: Download Pre-built Release (Recommended)
1. Go to the [Releases page](https://github.com/shorres/Magic-Tool/releases)
2. Download the latest `Decksmith-vX.X.X-Windows.zip` file
3. Extract all files to a folder of your choice
4. Navigate to the `Decksmith vX.X.X` folder
5. Run `Decksmith vX.X.X.exe` to start the application

**No Python installation required!** The release includes everything you need.

### Option 2: Run from Source
1. Clone this repository
2. Install Python 3.8 or higher
3. Install dependencies: `pip install -r requirements.txt`
4. Run: `python main.py`

## Data Storage

- **Collections**: Stored in `data/collections/`
- **Decks**: Stored in `data/decks/` 
- **Cache**: API cache stored in `data/cache/`
- **Portable**: All data files are in the application directory

## Quick Start

1. **Download**: Get the latest release from the [Releases page](https://github.com/shorres/Magic-Tool/releases)
2. **Extract**: Unzip to any folder
3. **Run**: Launch `Decksmith vX.X.X.exe`
4. **Import**: Start by importing your collection via CSV or clipboard
5. **Build**: Create decks with AI recommendations and Scryfall integration

## Usage

1. **Collection**: Add cards manually or import from CSV/clipboard
2. **Decks**: Build decks with smart autocomplete from your collection
3. **AI Recommendations**: Get card suggestions and deck analysis
4. **Import/Export**: Use clipboard or files to transfer data

## Project Structure

```
Decksmith/
├── main.py                 # Application entry point
├── src/
│   ├── gui/                # User interface
│   ├── models/             # Data models (Card, Deck, Collection)
│   └── utils/              # Utilities (CSV, Scryfall API, AI)
├── data/                   # Storage (collections, decks, cache)
└── requirements.txt        # Dependencies
```

## License

MIT License
