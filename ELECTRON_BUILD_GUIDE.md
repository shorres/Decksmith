# Decksmith - Build & Deployment Guide

## 🚀 Quick Start - Building a Release

### Windows Build (Recommended)

```powershell
# Full production build with installer
.\build_electron.ps1

# Clean build (removes previous builds first)
.\build_electron.ps1 -Clean

# Development build only (no installer)
.\build_electron.ps1 -Mode dev

# Skip npm install (faster if dependencies haven't changed)
.\build_electron.ps1 -SkipInstall
```

### Manual Build Commands

```bash
cd electron

# Install dependencies (first time only)
npm install

# Build the application
npm run build

# Create Windows installer
npm run dist:win

# Create macOS installer (on Mac)
npm run dist:mac

# Create Linux installer (on Linux)
npm run dist:linux
```

## 📦 Build Output

After building, you'll find the installer in:
```
electron/release/
```

**Generated files:**
- **Deckmaster Setup X.X.X.exe** - Windows NSIS installer (distributable)
- **Deckmaster-X.X.X.exe** - Unpacked executable
- **win-unpacked/** - Unpacked application directory

## 🔧 Build Configuration

The build is configured in `electron/package.json` under the `build` section:

```json
{
  "build": {
    "appId": "com.shorres.deckmaster",
    "productName": "Deckmaster",
    "directories": {
      "output": "release",
      "buildResources": "build"
    },
    "win": {
      "target": "nsis",
      "icon": "../assets/decksmith_icon.ico"
    },
    "nsis": {
      "oneClick": false,
      "allowToChangeInstallationDirectory": true
    }
  }
}
```

## 📋 Version Management

To update the version number:

1. Edit `electron/package.json`:
   ```json
   {
     "version": "2.0.0"
   }
   ```

2. Commit and push the change

3. Create a git tag:
   ```bash
   git tag v2.0.0
   git push origin v2.0.0
   ```

4. GitHub Actions will automatically build and create a release!

## 🤖 Automated Builds with GitHub Actions

### Release Builds (Automatic)

When you push a version tag (e.g., `v2.0.0`), GitHub Actions will automatically:
1. Build installers for Windows, macOS, and Linux
2. Create a GitHub Release
3. Upload all installers to the release
4. Generate release notes

**To create a release:**
```bash
# Update version in electron/package.json first
git add electron/package.json
git commit -m "Bump version to 2.1.0"
git push

# Create and push tag
git tag v2.1.0
git push origin v2.1.0

# Watch the Actions tab on GitHub for build progress
```

### Test Builds (Pull Requests)

Every pull request and push to `main` or `electron-migration` branches will:
- Build TypeScript to verify no compilation errors
- Test that all build artifacts are created
- Report build status on the PR

This ensures code quality without creating releases.

### Manual Workflow Dispatch

You can also trigger a release build manually:
1. Go to GitHub → Actions → "Build and Release"
2. Click "Run workflow"
3. Enter the version number
4. Click "Run workflow"

## 🔄 Workflow Files

- **`.github/workflows/release.yml`** - Creates releases on tags
- **`.github/workflows/build-test.yml`** - Tests builds on PRs

## 📋 Version Management (Manual)

For manual builds without GitHub Actions:

1. Edit `electron/package.json`:
   ```json
   {
     "version": "2.0.0"
   }
   ```

2. The installer will automatically use this version number

## 🎯 Build Targets

### Windows (NSIS Installer)
- **Format:** `.exe` installer
- **Features:**
  - User-selectable install directory
  - Start menu shortcuts
  - Uninstaller
  - Desktop shortcut option

### macOS (DMG)
- **Format:** `.dmg` disk image
- **Requires:** Building on macOS
- **Command:** `npm run dist:mac`

### Linux (AppImage)
- **Format:** `.AppImage` portable executable
- **Requires:** Building on Linux
- **Command:** `npm run dist:linux`

## 🔍 Build Process Details

### 1. TypeScript Compilation
- Compiles `src/main/**/*.ts` → `dist/main/**/*.js`
- Compiles `src/renderer/**/*.ts` → `dist/renderer/**/*.js`

### 2. Webpack Bundling
- Bundles renderer process code
- Processes CSS files
- Copies HTML templates

### 3. Electron Packaging
- Packages the app with Electron runtime
- Includes all dependencies
- Creates installer with electron-builder

## 🚨 Troubleshooting

### "electron-builder not found"
```bash
cd electron
npm install
```

### Build fails at TypeScript compilation
```bash
cd electron
npm run clean
npm run build
```

### Installer icon missing
- Ensure `assets/decksmith_icon.ico` exists
- Icon should be 256x256 pixels minimum

### Build is slow
Use the `-SkipInstall` flag if dependencies haven't changed:
```powershell
.\build_electron.ps1 -SkipInstall
```

## 📤 Distribution

### Automated (Recommended)
1. Update version in `electron/package.json`
2. Commit and push
3. Create and push a tag:
   ```bash
   git tag v2.0.0
   git push origin v2.0.0
   ```
4. GitHub Actions builds all platforms automatically
5. Release is created with all installers attached

### Manual Distribution
Distribute the **Deckmaster Setup X.X.X.exe** file from `electron/release/`

Users can:
1. Download the installer
2. Run the `.exe` file
3. Choose installation directory
4. Application installs and creates shortcuts

## 📝 Build Checklist

Before creating a release:

- [ ] Update version in `electron/package.json`
- [ ] Test the application in development mode (`npm run dev`)
- [ ] Run local test build: `.\build_electron.ps1 -Clean`
- [ ] Test the installer on a clean system
- [ ] Verify all features work in installed version
- [ ] Commit version change and push
- [ ] Create and push tag: `git tag vX.X.X && git push origin vX.X.X`
- [ ] Monitor GitHub Actions for successful build
- [ ] Test downloaded installers from GitHub Release

## 🎨 Custom Installer

To customize the installer:

1. **Change app name:** Edit `productName` in package.json
2. **Change icon:** Replace `assets/decksmith_icon.ico`
3. **Add license:** Create `electron/build/license.txt`
4. **Custom installer UI:** Modify `nsis` section in package.json

## 💡 Development vs Production

**Development:**
```bash
cd electron
npm run dev  # Live reload during development
```

**Production Build:**
```powershell
.\build_electron.ps1  # Creates installer
```

---

**Need help?** Check the [electron-builder documentation](https://www.electron.build/)
