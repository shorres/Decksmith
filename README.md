# Magic: The Gathering Arena Deck Manager

A comprehensive tool for managing your Magic: The Gathering Arena collection and decks with advanced AI recommendations and Scryfall integration.

## Key Features

- **Collection Management**: Track your card collection with quantities and rarities
- **Deck Builder**: Create and manage multiple decks with smart autocomplete
- **Scryfall Integration**: Real-time card search and auto-enrichment from the complete MTG database
- **AI Recommendations**: Get intelligent card suggestions based on synergy and deck analysis
- **Import/Export**: Support for CSV, Arena formats, and clipboard operations
- **Advanced Analysis**: Deck statistics, mana curves, and deck health scoring

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

1. Clone this repository
2. Install Python 3.8 or higher
3. Install dependencies: `pip install -r requirements.txt`
4. Run: `python main.py`

## Usage

1. **Collection**: Add cards manually or import from CSV/clipboard
2. **Decks**: Build decks with smart autocomplete from your collection
3. **AI Recommendations**: Get card suggestions and deck analysis
4. **Import/Export**: Use clipboard or files to transfer data

## Project Structure

```
Magic Tool/
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
