# Icon Setup Instructions for Decksmith

## Steps to Add the Icon:

1. **Save the Icon Image:**
   - Save the provided icon image as: `assets/decksmith_icon.png`

2. **Install Pillow (if not already installed):**
   ```powershell
   pip install Pillow
   ```

3. **Convert to ICO Format:**
   ```powershell
   python convert_icon.py
   ```
   
   This will create: `assets/decksmith_icon.ico`

4. **Build with Icon:**
   ```powershell
   # The icon will automatically be included in future builds
   .\build_release.ps1 -Version "1.0.5"
   ```

## Alternative Method (Manual Conversion):

If you prefer to convert manually:
1. Save the image as `assets/decksmith_icon.png`
2. Use an online converter like `convertio.co` or `icoconvert.com`
3. Convert to ICO format with multiple sizes (16x16, 32x32, 48x48, 64x64, 128x128, 256x256)
4. Save as `assets/decksmith_icon.ico`

## Verification:

After adding the icon, the build script will show:
- ✅ "Using icon: assets/decksmith_icon.ico" (if found)
- ⚠️ "Icon not found: assets/decksmith_icon.ico" (if missing)

The icon will appear in:
- Windows Explorer (file icon)
- Taskbar when running
- Alt+Tab window switcher
- Windows properties dialog
