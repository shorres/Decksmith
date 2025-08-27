@echo off
echo 🚀 Setting up Deckmaster Electron App
echo ====================================

echo.
echo 📦 Installing Node.js dependencies...
cd electron
call npm install

echo.
echo 🏗️ Building the application...
call npm run build

echo.
echo ✅ Setup complete!
echo.
echo 🎯 Quick commands:
echo   npm run dev     - Start development server
echo   npm run build   - Build for production  
echo   npm run dist    - Create distributable
echo.
echo 🚀 Ready to launch Deckmaster 2.0!
