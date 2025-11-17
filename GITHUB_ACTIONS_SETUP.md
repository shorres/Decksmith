# GitHub Actions Setup Summary

## ✅ What's Been Configured

### Automated Release Workflow (`.github/workflows/release.yml`)
- **Triggers on:** Version tags (`v*.*.*`) like `v2.0.0`, `v2.1.0`
- **Builds for:** Windows, macOS, and Linux
- **Creates:** GitHub Release with all installers automatically attached
- **Features:**
  - Parallel builds on all platforms
  - Automatic release notes generation
  - Version extraction from tags
  - Manual workflow dispatch option

### Test Build Workflow (`.github/workflows/build-test.yml`)
- **Triggers on:** Pull requests and pushes to `main` or `electron-migration`
- **Purpose:** Verify builds compile without creating releases
- **Platforms:** Windows and Linux
- **Validates:** TypeScript compilation and build artifacts

## 🚀 How to Create a Release

### Step-by-Step Process

1. **Update version in `electron/package.json`:**
   ```json
   {
     "version": "2.1.0"
   }
   ```

2. **Commit and push the version change:**
   ```bash
   git add electron/package.json
   git commit -m "Bump version to 2.1.0"
   git push origin main
   ```

3. **Create and push a version tag:**
   ```bash
   git tag v2.1.0
   git push origin v2.1.0
   ```

4. **Monitor the build:**
   - Go to your GitHub repository
   - Click the "Actions" tab
   - Watch the "Build and Release" workflow
   - Wait for all three platform builds to complete (5-10 minutes)

5. **Release is ready!**
   - Go to "Releases" tab
   - Your new release will be there with:
     - Windows installer (.exe)
     - macOS installer (.dmg)
     - Linux installer (.AppImage)
   - Auto-generated release notes
   - Download counts tracking

## 🔄 Workflow Details

### Windows Build
- Runs on: `windows-latest`
- Creates: NSIS installer with custom install directory
- Output: `Deckmaster Setup X.X.X.exe`

### macOS Build
- Runs on: `macos-latest`
- Creates: DMG disk image
- Output: `Deckmaster-X.X.X.dmg`

### Linux Build
- Runs on: `ubuntu-latest`
- Creates: AppImage portable executable
- Output: `Deckmaster-X.X.X.AppImage`

## 📝 Tag Naming Convention

**Required format:** `v` followed by semantic version

✅ **Correct:**
- `v2.0.0`
- `v2.1.0`
- `v2.1.1`
- `v3.0.0-beta`

❌ **Won't trigger workflow:**
- `2.0.0` (missing 'v' prefix)
- `release-2.0.0`
- `v2.0` (needs three parts)

## 🎯 Manual Workflow Dispatch

You can also trigger builds manually without tags:

1. Go to GitHub → Actions → "Build and Release"
2. Click "Run workflow" button
3. Select branch
4. Enter version number (e.g., "2.0.0")
5. Click "Run workflow"

## 🔍 Monitoring Builds

### View Progress
1. Click "Actions" tab
2. Find your workflow run
3. Click to see detailed logs for each platform

### Download Artifacts
Even before the release is created, you can:
1. Open the workflow run
2. Scroll to "Artifacts" section at bottom
3. Download individual platform builds

## 🐛 Troubleshooting

### Build Fails
- Check the Actions tab for error logs
- Common issues:
  - TypeScript compilation errors
  - Missing dependencies in package.json
  - Icon file path issues

### Tag Already Exists
```bash
# Delete local tag
git tag -d v2.0.0

# Delete remote tag
git push origin :refs/tags/v2.0.0

# Create new tag
git tag v2.0.0
git push origin v2.0.0
```

### No Release Created
- Verify tag format matches `v*.*.*`
- Check GitHub Actions logs
- Ensure GITHUB_TOKEN has write permissions (should be automatic)

## 💡 Best Practices

1. **Test locally first:**
   ```powershell
   .\build_electron.ps1 -Clean
   ```

2. **Use semantic versioning:**
   - Major: Breaking changes (1.0.0 → 2.0.0)
   - Minor: New features (2.0.0 → 2.1.0)
   - Patch: Bug fixes (2.1.0 → 2.1.1)

3. **Write good commit messages:**
   ```bash
   git commit -m "Add dark mode support"
   git commit -m "Fix deck import crash on Windows"
   ```

4. **Monitor the first few releases** to ensure everything works smoothly

## 📊 Benefits of This Setup

- ✅ No manual building on different OS platforms
- ✅ Consistent, reproducible builds
- ✅ Automatic release creation
- ✅ Download statistics tracking
- ✅ Version history preservation
- ✅ Professional release process
- ✅ Easy rollback (just delete bad release)

## 🔜 Next Steps

Consider adding:
- **Code signing** for Windows/macOS (requires certificates)
- **Auto-update functionality** using electron-updater
- **Beta/prerelease channels** for testing
- **Changelog generation** from commit messages
- **Slack/Discord notifications** on release

---

**Questions?** Check the detailed [ELECTRON_BUILD_GUIDE.md](ELECTRON_BUILD_GUIDE.md)
