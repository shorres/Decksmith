# Release Build Script for Decksmith
# This script creates a release build with proper versioning

param(
    [string]$Version = "",
    [switch]$CreateBranch = $false
)

# Colors for output
$Red = "Red"
$Green = "Green" 
$Yellow = "Yellow"
$Blue = "Blue"

Write-Host "Decksmith Release Builder" -ForegroundColor $Blue
Write-Host "=========================" -ForegroundColor $Blue

# Check if virtual environment is activated
if (-not $env:VIRTUAL_ENV) {
    Write-Host "Activating virtual environment..." -ForegroundColor $Yellow
    & ".\.venv\Scripts\Activate.ps1"
}

# Get version from version file or prompt
if (-not $Version) {
    if (Test-Path "src\__version__.py") {
        $content = Get-Content "src\__version__.py" | Where-Object { $_ -match '__version__' }
        if ($content -match '"([^"]+)"') {
            $CurrentVersion = $matches[1]
            Write-Host "Current version: $CurrentVersion" -ForegroundColor $Yellow
            $Version = Read-Host "Enter new version (or press Enter to use $CurrentVersion)"
            if (-not $Version) { $Version = $CurrentVersion }
        }
    }
    if (-not $Version) {
        $Version = Read-Host "Enter version number (e.g., 1.0.0)"
    }
}

Write-Host "Building version: $Version" -ForegroundColor $Green

# Create release branch if requested
if ($CreateBranch) {
    Write-Host "Creating release branch: release/$Version" -ForegroundColor $Yellow
    git checkout -b "release/$Version"
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Failed to create release branch" -ForegroundColor $Red
        exit 1
    }
}

# Update version file
Write-Host "Updating version information..." -ForegroundColor $Yellow
$versionContent = @"
__version__ = "$Version"
__app_name__ = "Decksmith"
__description__ = "Magic: The Gathering Arena Deck Manager"
"@
$versionContent | Out-File -FilePath "src\__version__.py" -Encoding UTF8

# Create release directory
$releaseDir = "release\$Version"
if (Test-Path $releaseDir) {
    Write-Host "Removing existing release directory..." -ForegroundColor $Yellow
    Remove-Item $releaseDir -Recurse -Force
}
New-Item -ItemType Directory -Path $releaseDir -Force | Out-Null

# Install/update build dependencies
Write-Host "Installing build dependencies..." -ForegroundColor $Yellow
pip install --upgrade pyinstaller

# Create version info for Windows executable
$versionInfoContent = @"
# UTF-8
VSVersionInfo(
  ffi=FixedFileInfo(
    filevers=(1,0,0,0),
    prodvers=(1,0,0,0),
    mask=0x3f,
    flags=0x0,
    OS=0x40004,
    fileType=0x1,
    subtype=0x0,
    date=(0, 0)
    ),
  kids=[
    StringFileInfo(
      [
      StringTable(
        u'040904B0',
        [StringStruct(u'CompanyName', u''),
        StringStruct(u'FileDescription', u'Magic: The Gathering Arena Deck Manager'),
        StringStruct(u'FileVersion', u'$Version'),
        StringStruct(u'InternalName', u'MagicTool'),
        StringStruct(u'LegalCopyright', u''),
        StringStruct(u'OriginalFilename', u'Decksmith v$Version.exe'),
        StringStruct(u'ProductName', u'Decksmith'),
        StringStruct(u'ProductVersion', u'$Version')])
      ]),
    VarFileInfo([VarStruct(u'Translation', [1033, 1200])])
  ]
)
"@
$versionInfoContent | Out-File -FilePath "$releaseDir\version_info.txt" -Encoding UTF8

# Validate imports before building
Write-Host "Validating imports before building..." -ForegroundColor $Yellow
& python validate_imports.py
if ($LASTEXITCODE -ne 0) {
    Write-Host "Import validation failed! Please fix missing dependencies before building." -ForegroundColor Red
    exit 1
}
Write-Host "Import validation passed!" -ForegroundColor Green

# Run PyInstaller
Write-Host "Building executable with PyInstaller..." -ForegroundColor $Yellow

# Use absolute paths for add-data
$srcPath = Join-Path $PWD "src"
$dataPath = Join-Path $PWD "data" 
$mainPath = Join-Path $PWD "main.py"
$versionPath = Join-Path $PWD "$releaseDir\version_info.txt"
$iconPath = Join-Path $PWD "assets\decksmith_icon.ico"

$buildCommand = "pyinstaller --onefile --windowed --name `"Decksmith v$Version`" --distpath `"$releaseDir`" --workpath `"$releaseDir\build`" --specpath `"$releaseDir`" `"$mainPath`""

# Add version info if on Windows
$buildCommand += " --version-file=`"$versionPath`""

# Add icon if it exists
if (Test-Path $iconPath) {
    $buildCommand += " --icon=`"$iconPath`""
    Write-Host "Using icon: $iconPath" -ForegroundColor Green
} else {
    Write-Host "Icon not found: $iconPath" -ForegroundColor Yellow
}

# Add additional options with absolute paths
$buildCommand += " --add-data `"$srcPath;src`" --add-data `"$dataPath;data`""
$buildCommand += " --hidden-import=tkinter --hidden-import=tkinter.ttk --hidden-import=tkinter.filedialog --hidden-import=tkinter.messagebox --hidden-import=tkinter.simpledialog"
$buildCommand += " --hidden-import=requests --hidden-import=urllib3 --hidden-import=certifi --hidden-import=charset_normalizer"
$buildCommand += " --hidden-import=json --hidden-import=threading --hidden-import=queue --hidden-import=csv --hidden-import=re"
$buildCommand += " --hidden-import=pyperclip --hidden-import=datetime --hidden-import=os --hidden-import=time --hidden-import=math"
$buildCommand += " --hidden-import=collections --hidden-import=dataclasses --hidden-import=typing"

Invoke-Expression $buildCommand

if ($LASTEXITCODE -ne 0) {
    Write-Host "Build failed!" -ForegroundColor $Red
    exit 1
}

# Create release package
Write-Host "Creating minimal release package..." -ForegroundColor $Yellow
$packageName = "Decksmith-v$Version-Windows.zip"
$exePath = "$releaseDir\Decksmith v$Version.exe"

if (Test-Path $exePath) {
    # Create minimal release directory structure
    $releasePackageDir = "$releaseDir\package"
    New-Item -ItemType Directory -Path $releasePackageDir -Force | Out-Null
    
    # Copy only the executable (no README or other files)
    Copy-Item $exePath -Destination "$releasePackageDir\Decksmith v$Version.exe"
    
    # Create the minimal ZIP package with just the executable
    Compress-Archive -Path "$releasePackageDir\*" -DestinationPath "$releaseDir\$packageName" -Force
    
    # Clean up temporary package directory
    Remove-Item $releasePackageDir -Recurse -Force

    Write-Host "Minimal build completed successfully!" -ForegroundColor $Green
    Write-Host "Executable: $exePath" -ForegroundColor $Green  
    Write-Host "Minimal Package: $releaseDir\$packageName" -ForegroundColor $Green
    Write-Host "Package contains: Decksmith v$Version.exe only" -ForegroundColor $Green
    
    # Test the executable
    Write-Host "Testing executable..." -ForegroundColor $Yellow
    $testResult = Test-Path $exePath
    if ($testResult) {
        $fileSize = (Get-Item $exePath).Length / 1MB
        Write-Host "Executable size: $([math]::Round($fileSize, 2)) MB" -ForegroundColor $Green
    }
} else {
    Write-Host "Build failed - executable not found!" -ForegroundColor $Red
    exit 1
}

Write-Host "`nBuild Summary:" -ForegroundColor $Blue
Write-Host "- Version: $Version" -ForegroundColor White
Write-Host "- Release directory: $releaseDir" -ForegroundColor White  
Write-Host "- Executable: Decksmith v$Version.exe" -ForegroundColor White
Write-Host "- Package: $packageName" -ForegroundColor White

if ($CreateBranch) {
    Write-Host "`nNext steps for release:" -ForegroundColor $Yellow
    Write-Host "1. Test the executable thoroughly" -ForegroundColor White
    Write-Host "2. Commit version changes: git add . && git commit -m 'Release v$Version'" -ForegroundColor White
    Write-Host "3. Merge to main: git checkout main && git merge release/$Version" -ForegroundColor White
    Write-Host "4. Create GitHub release with the ZIP package" -ForegroundColor White
    Write-Host "5. Tag the release: git tag v$Version && git push origin v$Version" -ForegroundColor White
}
