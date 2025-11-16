# 🚀 Deckmaster 2.0 - Electron Migration

Modern Magic: The Gathering collection and deck manager built with Electron, TypeScript, and modern web technologies.

## ⚡ Why Electron?

The original Python/Tkinter version had some performance limitations:
- **Slow startup times** (10+ seconds for standalone app)
- **Limited UI capabilities** (basic styling, no animations)
- **Threading issues** with GUI updates
- **Large bundle sizes** (50MB+ with PyInstaller)

Deckmaster 2.0 with Electron delivers:
- **Lightning-fast startup** (2-3 seconds)
- **Modern, responsive UI** with smooth animations
- **Better performance** with V8 JavaScript engine
- **Smaller, signed packages** with auto-updates
- **Native system integration**

## 🎯 Features

- 📚 **Smart Collection Management** - Import/export CSV, Arena format
- 🏗️ **Advanced Deck Builder** - Visual deck construction with statistics
- 🤖 **AI Recommendations** - Intelligent card suggestions
- 🔍 **Scryfall Integration** - Real-time card search and data
- 📊 **Analytics & Statistics** - Collection insights and deck analysis
- 💾 **Persistent Storage** - All data saved locally with electron-store

## 🛠️ Development Setup

### Prerequisites
- Node.js 16+ 
- npm or yarn

### Quick Start
```bash
# Run the setup script
setup_electron.bat

# Or manually:
cd electron
npm install
npm run build
npm run dev
```

### Development Commands
```bash
# Start development with hot reload
npm run dev

# Build for production
npm run build

# Create distributable packages
npm run dist

# Platform-specific builds
npm run dist:win    # Windows
npm run dist:mac    # macOS  
npm run dist:linux  # Linux
```

## 📁 Project Structure

```
electron/
├── src/
│   ├── main/           # Electron main process
│   │   ├── main.ts     # Main application logic
│   │   └── tsconfig.json
│   └── renderer/       # Web UI (renderer process)
│       ├── index.html  # Main HTML template
│       ├── app.ts      # TypeScript application logic
│       ├── preload.ts  # Secure IPC bridge
│       ├── styles.css  # Modern CSS styling
│       ├── utils.ts    # Utilities (Scryfall API, CSV)
│       └── tsconfig.json
├── dist/               # Built files
├── package.json        # Dependencies and scripts
└── webpack.config.js   # Bundling configuration
```

## 🔧 Architecture

### Main Process (`main.ts`)
- Window management
- File system operations  
- Menu creation
- IPC handling
- App lifecycle

### Renderer Process (`app.ts`)
- UI management
- Tab switching
- Collection/deck handling
- Scryfall API integration
- User interactions

### Secure IPC Bridge (`preload.ts`)  
- Safe communication between main and renderer
- File dialogs
- Storage operations
- App information

## 🚢 Distribution

### Platform Packages
- **Windows**: NSIS installer (.exe)
- **macOS**: DMG package (.dmg)
- **Linux**: AppImage (.AppImage)

**Ready to build the future of MTG collection management! 🃏✨**
