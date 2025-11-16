# Decksmith Electron Build Script
# Builds the Electron application for Windows distribution

param(
    [Parameter(Mandatory=$false)]
    [ValidateSet('dev', 'production')]
    [string]$Mode = 'production',
    
    [Parameter(Mandatory=$false)]
    [switch]$SkipInstall,
    
    [Parameter(Mandatory=$false)]
    [switch]$Clean
)

$ErrorActionPreference = "Stop"

# Define colors for output
function Write-Step {
    param([string]$Message)
    Write-Host "`n==> $Message" -ForegroundColor Cyan
}

function Write-Success {
    param([string]$Message)
    Write-Host "✓ $Message" -ForegroundColor Green
}

function Write-Error-Custom {
    param([string]$Message)
    Write-Host "✗ $Message" -ForegroundColor Red
}

# Banner
Write-Host ""
Write-Host "=============================================================" -ForegroundColor Magenta
Write-Host "                                                             " -ForegroundColor Magenta
Write-Host "             Decksmith Electron Build Script                " -ForegroundColor Magenta
Write-Host "                                                             " -ForegroundColor Magenta
Write-Host "=============================================================" -ForegroundColor Magenta

# Verify we're in the right directory
if (-not (Test-Path "electron/package.json")) {
    Write-Error-Custom "Must run from the root of the Magic Tool repository"
    exit 1
}

Write-Host "`nBuild Mode: $Mode" -ForegroundColor Yellow
Write-Host "Skip Install: $SkipInstall" -ForegroundColor Yellow
Write-Host "Clean Build: $Clean`n" -ForegroundColor Yellow

try {
    # Change to electron directory
    Write-Step "Navigating to electron directory"
    Set-Location electron
    Write-Success "Changed to electron directory"

    # Clean previous builds if requested
    if ($Clean) {
        Write-Step "Cleaning previous builds"
        if (Test-Path "dist") {
            Remove-Item -Recurse -Force "dist"
            Write-Success "Removed dist directory"
        }
        if (Test-Path "release") {
            Remove-Item -Recurse -Force "release"
            Write-Success "Removed release directory"
        }
    }

    # Install dependencies if needed
    if (-not $SkipInstall) {
        Write-Step "Installing/updating dependencies"
        npm install
        if ($LASTEXITCODE -ne 0) {
            throw "npm install failed"
        }
        Write-Success "Dependencies installed"
    }

    # Build TypeScript files
    Write-Step "Building TypeScript files"
    npm run build
    if ($LASTEXITCODE -ne 0) {
        throw "TypeScript build failed"
    }
    Write-Success "TypeScript compilation complete"

    # Build distribution package
    if ($Mode -eq 'production') {
        Write-Step "Building Windows distribution package (NSIS installer)"
        npm run dist:win
        if ($LASTEXITCODE -ne 0) {
            throw "Distribution build failed"
        }
        Write-Success "Distribution package created"

        # Display output location
        Write-Host ""
        Write-Host "=============================================================" -ForegroundColor Green
        Write-Host "                   BUILD SUCCESSFUL!                         " -ForegroundColor Green
        Write-Host "=============================================================" -ForegroundColor Green
        Write-Host "`nInstaller created at:" -ForegroundColor Cyan
        
        $releasePath = Resolve-Path "release"
        Write-Host "  $releasePath" -ForegroundColor Yellow
        
        # List the generated files
        Write-Host "`nGenerated files:" -ForegroundColor Cyan
        Get-ChildItem "release" -File | ForEach-Object {
            $size = [math]::Round($_.Length / 1MB, 2)
            $sizeText = "{0:N2} MB" -f $size
            Write-Host "  - $($_.Name) ($sizeText)" -ForegroundColor White
        }
        
    } else {
        Write-Step "Development build complete - skipping packaging"
        Write-Success "You can now run 'npm run electron' to start the app"
    }

} catch {
    Write-Error-Custom "Build failed: $_"
    Set-Location ..
    exit 1
} finally {
    # Return to original directory
    Set-Location ..
}

Write-Host "`n✓ All done!" -ForegroundColor Green
Write-Host ""
