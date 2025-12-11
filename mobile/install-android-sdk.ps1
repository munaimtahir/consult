# Android SDK Installation Script for Windows
# This script installs Android SDK command-line tools

$ErrorActionPreference = "Stop"

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Android SDK Installation for Windows" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

# Determine SDK location
$SDK_DIR = "$env:LOCALAPPDATA\Android\Sdk"
$SDK_DIR_FULL = [System.IO.Path]::GetFullPath($SDK_DIR)

Write-Host "SDK will be installed to: $SDK_DIR_FULL" -ForegroundColor Yellow
Write-Host ""

# Create SDK directory
if (-not (Test-Path $SDK_DIR)) {
    Write-Host "Creating SDK directory..." -ForegroundColor Green
    New-Item -ItemType Directory -Path $SDK_DIR -Force | Out-Null
}

# Check if SDK already exists
if (Test-Path "$SDK_DIR\cmdline-tools") {
    Write-Host "Android SDK command-line tools already exist!" -ForegroundColor Green
    Write-Host "SDK location: $SDK_DIR_FULL" -ForegroundColor Green
    Write-Host ""
    Write-Host "To set ANDROID_HOME, run:" -ForegroundColor Yellow
    Write-Host "  [System.Environment]::SetEnvironmentVariable('ANDROID_HOME', '$SDK_DIR_FULL', 'User')" -ForegroundColor White
    Write-Host ""
    Write-Host "Then restart your terminal." -ForegroundColor Yellow
    exit 0
}

Write-Host "This script will download and install Android SDK command-line tools." -ForegroundColor Yellow
Write-Host "This requires:" -ForegroundColor Yellow
Write-Host "  1. Internet connection" -ForegroundColor Yellow
Write-Host "  2. Approximately 500MB disk space" -ForegroundColor Yellow
Write-Host "  3. Accepting Android SDK licenses" -ForegroundColor Yellow
Write-Host ""

# Auto-proceed in non-interactive mode, otherwise prompt
try {
    $response = Read-Host "Continue? (Y/N)"
    if ($response -ne "Y" -and $response -ne "y") {
        Write-Host "Installation cancelled." -ForegroundColor Red
        exit 1
    }
} catch {
    # Non-interactive mode - auto-proceed
    Write-Host "Non-interactive mode detected. Proceeding automatically..." -ForegroundColor Gray
}

# Download command-line tools
Write-Host ""
Write-Host "Step 1: Downloading Android SDK command-line tools..." -ForegroundColor Cyan
$CLI_TOOLS_URL = "https://dl.google.com/android/repository/commandlinetools-win-11076708_latest.zip"
$ZIP_FILE = "$env:TEMP\android-commandlinetools.zip"

try {
    Write-Host "Downloading from: $CLI_TOOLS_URL" -ForegroundColor Gray
    Invoke-WebRequest -Uri $CLI_TOOLS_URL -OutFile $ZIP_FILE -UseBasicParsing
    Write-Host "Download complete!" -ForegroundColor Green
} catch {
    Write-Host "Error downloading Android SDK tools: $_" -ForegroundColor Red
    Write-Host ""
    Write-Host "Alternative: Install Android Studio from https://developer.android.com/studio" -ForegroundColor Yellow
    Write-Host "Android Studio includes the full SDK and is easier to set up." -ForegroundColor Yellow
    exit 1
}

# Extract command-line tools
Write-Host ""
Write-Host "Step 2: Extracting command-line tools..." -ForegroundColor Cyan
$EXTRACT_DIR = "$env:TEMP\android-cli-extract"

if (Test-Path $EXTRACT_DIR) {
    Remove-Item -Path $EXTRACT_DIR -Recurse -Force
}
New-Item -ItemType Directory -Path $EXTRACT_DIR -Force | Out-Null

Expand-Archive -Path $ZIP_FILE -DestinationPath $EXTRACT_DIR -Force

# Organize command-line tools structure
Write-Host "Organizing SDK structure..." -ForegroundColor Gray
$CMD_TOOLS_DIR = "$SDK_DIR\cmdline-tools\latest"
New-Item -ItemType Directory -Path $CMD_TOOLS_DIR -Force | Out-Null

# Move files to correct location
$EXTRACTED_CONTENTS = Get-ChildItem -Path $EXTRACT_DIR
foreach ($item in $EXTRACTED_CONTENTS) {
    Move-Item -Path $item.FullName -Destination $CMD_TOOLS_DIR -Force
}

# Cleanup
Remove-Item -Path $ZIP_FILE -Force -ErrorAction SilentlyContinue
Remove-Item -Path $EXTRACT_DIR -Recurse -Force -ErrorAction SilentlyContinue

Write-Host "Extraction complete!" -ForegroundColor Green

# Set ANDROID_HOME
Write-Host ""
Write-Host "Step 3: Setting ANDROID_HOME environment variable..." -ForegroundColor Cyan
[System.Environment]::SetEnvironmentVariable('ANDROID_HOME', $SDK_DIR_FULL, 'User')
$env:ANDROID_HOME = $SDK_DIR_FULL

# Add to PATH
Write-Host "Adding Android SDK to PATH..." -ForegroundColor Gray
$PATH_ADDITIONS = @(
    "$SDK_DIR_FULL\platform-tools",
    "$SDK_DIR_FULL\tools",
    "$SDK_DIR_FULL\cmdline-tools\latest\bin"
)

$currentPath = [System.Environment]::GetEnvironmentVariable('Path', 'User')
foreach ($pathItem in $PATH_ADDITIONS) {
    if ($currentPath -notlike "*$pathItem*") {
        $currentPath = "$currentPath;$pathItem"
    }
}
[System.Environment]::SetEnvironmentVariable('Path', $currentPath, 'User')

# Update current session PATH
$env:Path = "$env:Path;$($PATH_ADDITIONS -join ';')"

Write-Host "Environment variables set!" -ForegroundColor Green

# Install SDK components
Write-Host ""
Write-Host "Step 4: Installing required SDK components..." -ForegroundColor Cyan
Write-Host "This may take several minutes..." -ForegroundColor Yellow
Write-Host ""

$SDKMANAGER = "$SDK_DIR_FULL\cmdline-tools\latest\bin\sdkmanager.bat"

# Accept licenses
Write-Host "Accepting Android SDK licenses..." -ForegroundColor Gray
& $SDKMANAGER --licenses | ForEach-Object {
    if ($_ -match "y/n") {
        "y"
    }
} | & $SDKMANAGER --licenses

# Install required components
Write-Host ""
Write-Host "Installing SDK platform and build tools..." -ForegroundColor Gray
$SDK_COMPONENTS = @(
    "platform-tools",
    "platforms;android-34",
    "build-tools;34.0.0"
)

foreach ($component in $SDK_COMPONENTS) {
    Write-Host "Installing: $component" -ForegroundColor Gray
    & $SDKMANAGER $component
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Warning: Failed to install $component" -ForegroundColor Yellow
    }
}

Write-Host ""
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Installation Complete!" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Android SDK installed at: $SDK_DIR_FULL" -ForegroundColor Green
Write-Host ""
Write-Host "IMPORTANT: Please restart your terminal/PowerShell for environment" -ForegroundColor Yellow
Write-Host "variables to take effect." -ForegroundColor Yellow
Write-Host ""
Write-Host "After restarting, verify installation:" -ForegroundColor Cyan
Write-Host "  echo `$env:ANDROID_HOME" -ForegroundColor White
Write-Host "  sdkmanager --version" -ForegroundColor White
Write-Host ""

