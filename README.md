# Magic: The Gathering Arena Deck Manager

A comprehensive tool for managing your Magic: The Gathering Arena collection and decks.

## Features

- **Collection Management**: Track your card collection with quantities and rarities
- **Deck Builder**: Create and manage multiple decks
- **Import/Export**: Import and export decks and collections via CSV
- **Advanced Sorting**: Sort cards by color, creature type, mana cost, and more
- **Deck Analysis**: View deck statistics and mana curves

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
