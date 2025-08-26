# Decksmith Release Guide 🚀

## ⚡ Quick Release (Recommended)

```powershell
# The ONE-LINER: Just push a tag, GitHub Actions does everything!
git tag v1.0.4; git push origin v1.0.4
```

**What happens automatically:**
- ✅ Builds executable with all dependencies  
- ✅ Creates minimal ZIP package (exe only)
- ✅ Publishes GitHub release
- ✅ Generates release notes

---

## 🛠️ Manual Release (If needed)

```powershell
# Build locally and upload manually
.\build_release.ps1 -Version "1.0.3" -CreateBranch
# Test: & ".\release\1.0.3\Decksmith v1.0.3.exe" 
git add .; git commit -m "Release v1.0.3"
git checkout main; git merge release/1.0.3; git push
git tag v1.0.3; git push origin v1.0.3
# Then upload ZIP at: https://github.com/shorres/Magic-Tool/releases
```

---

## 📦 What Users Get

```
Decksmith-v1.0.3-Windows.zip
└── Decksmith v1.0.3.exe  (13.9 MB - everything included)
```

---

## 🚨 Quick Fixes

**Build fails locally:**
```powershell
.\.venv\Scripts\Activate.ps1
pip install --upgrade pyinstaller
Remove-Item release -Recurse -Force  # Clear old builds
```

**GitHub Actions fails:**
- Update deprecated actions in `.github/workflows/release.yml`  
- Check permissions are set: `contents: write`
- Path issues: Convert `\` to `/` in file paths

**Tag management:**
```powershell
# Delete and recreate tag (for testing fixes)
git tag -d v1.0.3 && git push origin :refs/tags/v1.0.3
git tag v1.0.3 && git push origin v1.0.3
```

---

## 🎯 Useful Commands

```powershell
# Check current version
Get-Content src\__version__.py

# List tags
git tag -l

# Test build size
Get-Item "release\1.0.3\Decksmith v1.0.3.exe" | Select-Object @{Name="Size(MB)";Expression={[math]::Round($_.Length/1MB,2)}}
```

---

**That's it! Keep it simple.** 🎉

*For regular releases: `git tag v1.0.X && git push origin v1.0.X` and wait 5 minutes.*

### 🛠️ Method 1: Manual Release Process

#### Step 1: Build Release
```powershell
# Navigate to project directory
cd "D:\Repos\Magic Tool"

# Build with version and branch creation
.\build_release.ps1 -Version "1.0.3" -CreateBranch
```

**What this does:**
- Creates release branch `release/1.0.3`
- Updates version in `src\__version__.py`
- Builds executable with PyInstaller
- Creates minimal ZIP package

#### Step 2: Test the Build
```powershell
# Test the executable
& ".\release\1.0.3\Magic Tool v1.0.3.exe"

# Verify package contents
Expand-Archive -Path ".\release\1.0.3\Magic-Tool-v1.0.3-Windows.zip" -DestinationPath "test" -Force
ls test
```

#### Step 3: Commit and Push Release Branch
```powershell
git add .
git commit -m "Release v1.0.3"
git push origin release/1.0.3
```

#### Step 4: Merge to Main
```powershell
git checkout main
git merge release/1.0.3
git push origin main
```

#### Step 5: Create Git Tag
```powershell
git tag v1.0.3
git push origin v1.0.3
```

#### Step 6: Create GitHub Release
1. Go to https://github.com/shorres/Magic-Tool/releases
2. Click **"Create a new release"**
3. Choose tag: `v1.0.3`
4. Release title: `Magic Tool v1.0.3`
5. Description: Let GitHub generate release notes or write custom
6. Upload file: `release\1.0.3\Magic-Tool-v1.0.3-Windows.zip`
7. Click **"Publish release"**

### 🤖 Method 2: Automated Release Process

#### Super Simple: Just Push a Tag
```powershell
# Make sure main branch is ready
git checkout main
git pull

# Create and push tag
git tag v1.0.3
git push origin v1.0.3
```

**GitHub Actions will automatically:**
- Build the executable
- Create the GitHub release
- Upload the ZIP package
- Generate release notes

#### Manual Trigger (Alternative)
1. Go to https://github.com/shorres/Magic-Tool/actions
2. Click "Build and Release" workflow
3. Click "Run workflow"
4. Enter version: `1.0.3`
5. Click "Run workflow"

---

## 📁 Release Package Contents

Your users will get:
```
Magic-Tool-v1.0.3-Windows.zip
├── Magic Tool v1.0.3.exe  (13.9 MB - everything included)
```

GitHub automatically provides:
- Source code (zip)
- Source code (tar.gz)

---

## 🔧 Build Script Options

```powershell
# Basic build (no branch creation)
.\build_release.ps1 -Version "1.0.3"

# Build with release branch creation
.\build_release.ps1 -Version "1.0.3" -CreateBranch

# Interactive mode (prompts for version)
.\build_release.ps1
```

---

## 🚨 Troubleshooting

### Build Fails
```powershell
# Check virtual environment
.\.venv\Scripts\Activate.ps1

# Update PyInstaller
pip install --upgrade pyinstaller

# Clear old builds
Remove-Item release -Recurse -Force
```

### Executable Won't Run
- Test on clean Windows machine
- Check Windows Defender/Antivirus
- Verify all dependencies in hidden imports

### GitHub Actions Fails
- Check Python version compatibility
- Verify requirements.txt is current
- Check workflow file syntax
- **Common Fix**: Update deprecated action versions:
  ```yaml
  # Update these in .github/workflows/release.yml
  uses: actions/upload-artifact@v4    # was @v3
  uses: actions/setup-python@v5       # was @v4
  uses: softprops/action-gh-release@v2 # was @v1
  ```
- **Permission Errors (403)**: Add permissions to workflow:
  ```yaml
  permissions:
    contents: write
    actions: read
  ```
- **File Path Issues**: Ensure proper path handling in PowerShell scripts
  ```powershell
  # Convert Windows paths to Unix format for GitHub Actions
  $packagePathForGitHub = $packagePath -replace '\\', '/'
  ```
- **Pattern Match Errors**: Files not found due to path separator issues (Windows \ vs Unix /)
- **Missing Hidden Imports**: Add all required imports to PyInstaller command

---

## 📋 Version Numbering

**Semantic Versioning (recommended):**
- `1.0.0` - Major release
- `1.0.1` - Bug fixes
- `1.1.0` - New features
- `2.0.0` - Breaking changes

**Current Version:** Check `src\__version__.py`

---

## 🎯 Quick Commands Reference

```powershell
# Check current version
Get-Content src\__version__.py

# List existing tags
git tag -l

# Delete tag (if mistake or need to retest)
git tag -d v1.0.3
git push origin :refs/tags/v1.0.3

# Recreate tag (for testing workflow fixes)
git tag v1.0.3
git push origin v1.0.3

# Check build size
Get-Item "release\1.0.3\Magic Tool v1.0.3.exe" | Select-Object Name, @{Name="Size(MB)";Expression={[math]::Round($_.Length/1MB,2)}}

# Test ZIP contents
Expand-Archive "release\1.0.3\Magic-Tool-v1.0.3-Windows.zip" -DestinationPath "test-extract" -Force; ls test-extract
```

---

## ⚡ The Fastest Release Process

For regular releases, use **Method 2** (Automated):

1. **Test locally:** `python main.py`
2. **Create tag:** `git tag v1.0.3 && git push origin v1.0.3`
3. **Wait 5 minutes:** GitHub Actions builds and publishes
4. **Done!** ✅

---

*Keep this guide handy for stress-free releases! 🎉*
