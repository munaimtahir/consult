# Automated APK Build Script for Windows
# Hospital Consult Mobile App - Android APK Builder

$ErrorActionPreference = "Stop"

$SCRIPT_DIR = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $SCRIPT_DIR

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Hospital Consult - Automated APK Builder" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

$EXIT_CODE = 0

# Function to print colored messages
function Print-Success {
    param([string]$Message)
    Write-Host "✓ " -NoNewline -ForegroundColor Green
    Write-Host $Message
}

function Print-Error {
    param([string]$Message)
    Write-Host "✗ " -NoNewline -ForegroundColor Red
    Write-Host $Message
    $script:EXIT_CODE = 1
}

function Print-Warning {
    param([string]$Message)
    Write-Host "⚠ " -NoNewline -ForegroundColor Yellow
    Write-Host $Message
}

function Print-Info {
    param([string]$Message)
    Write-Host "  $Message" -ForegroundColor Gray
}

# Step 1: Check Java Installation
Write-Host "Step 1: Checking Java installation..." -ForegroundColor Cyan
try {
    $javaVersion = java -version 2>&1 | Select-Object -First 1
    Print-Success "Java found: $javaVersion"
    
    # Check if javac exists (JDK vs JRE)
    try {
        $javacVersion = javac -version 2>&1
        Print-Success "JDK found (javac available)"
    } catch {
        Print-Error "Java found but javac not found. You need JDK, not just JRE."
        exit 1
    }
    
    # Check Java version (need 17+)
    $javaMajorVersion = [int]((java -version 2>&1 | Select-String -Pattern 'version "(\d+)' | ForEach-Object { $_.Matches.Groups[1].Value }))
    if ($javaMajorVersion -lt 17) {
        Print-Error "Java version is $javaMajorVersion. Java 17 or higher is required."
        exit 1
    } else {
        Print-Success "Java version $javaMajorVersion is acceptable"
    }
} catch {
    Print-Error "Java not found in PATH"
    Print-Info "To install Java 17, run:"
    Print-Info "  winget install Microsoft.OpenJDK.17"
    Print-Info ""
    Print-Info "Then set JAVA_HOME environment variable"
    exit 1
}

# Check JAVA_HOME
if (-not $env:JAVA_HOME) {
    Print-Warning "JAVA_HOME is not set"
    # Try to detect it
    try {
        $javaPath = (Get-Command java).Source
        $detectedJavaHome = Split-Path -Parent (Split-Path -Parent $javaPath)
        Print-Info "Detected Java at: $detectedJavaHome"
        $env:JAVA_HOME = $detectedJavaHome
        Print-Success "Set JAVA_HOME to $detectedJavaHome (current session only)"
        Print-Warning "To make permanent, set JAVA_HOME in System Environment Variables"
    } catch {
        Print-Warning "Could not auto-detect JAVA_HOME"
    }
} else {
    if (Test-Path "$env:JAVA_HOME\bin\java.exe") {
        Print-Success "JAVA_HOME is set: $env:JAVA_HOME"
    } else {
        Print-Warning "JAVA_HOME is set but path may be invalid: $env:JAVA_HOME"
    }
}

Write-Host ""

# Step 2: Check Node.js Installation
Write-Host "Step 2: Checking Node.js installation..." -ForegroundColor Cyan
try {
    $nodeVersion = node -v
    Print-Success "Node.js found: $nodeVersion"
    
    # Check Node version (need 18+)
    $nodeMajorVersion = [int]($nodeVersion -replace 'v(\d+).*', '$1')
    if ($nodeMajorVersion -lt 18) {
        Print-Error "Node.js version is too old. Node.js 18 or higher is required."
        Print-Info "Current version: $nodeVersion"
        exit 1
    } else {
        Print-Success "Node.js version is acceptable"
    }
} catch {
    Print-Error "Node.js not found"
    Print-Info "Install Node.js 18+ from https://nodejs.org/"
    exit 1
}

try {
    $npmVersion = npm -v
    Print-Success "npm found: v$npmVersion"
} catch {
    Print-Error "npm not found"
    exit 1
}

Write-Host ""

# Step 3: Install/Update Node Dependencies
Write-Host "Step 3: Installing Node.js dependencies..." -ForegroundColor Cyan
if (-not (Test-Path "node_modules")) {
    Print-Info "node_modules not found. Installing dependencies..."
    npm install
    if ($LASTEXITCODE -ne 0) {
        Print-Error "Failed to install npm dependencies"
        exit 1
    }
    Print-Success "Dependencies installed"
} else {
    Print-Info "node_modules exists. Checking for updates..."
    npm install
    if ($LASTEXITCODE -ne 0) {
        Print-Warning "npm install had issues, but continuing..."
    } else {
        Print-Success "Dependencies up to date"
    }
}

Write-Host ""

# Step 4: Check Gradle Wrapper
Write-Host "Step 4: Checking Gradle wrapper..." -ForegroundColor Cyan
if (-not (Test-Path "android\gradlew.bat")) {
    Print-Error "Gradle wrapper not found at android\gradlew.bat"
    exit 1
} else {
    Print-Success "Gradle wrapper found"
}

# Test Gradle
Print-Info "Testing Gradle configuration..."
Set-Location android
try {
    $gradleVersion = .\gradlew.bat --version 2>&1 | Select-String -Pattern "Gradle" | Select-Object -First 1
    if ($LASTEXITCODE -eq 0) {
        Print-Success "Gradle configuration is valid: $gradleVersion"
    } else {
        Print-Warning "Gradle test had issues (may need Android SDK)"
    }
} catch {
    Print-Warning "Could not test Gradle (may need Android SDK)"
}
Set-Location ..

Write-Host ""

# Step 5: Check Android SDK
Write-Host "Step 5: Checking Android SDK..." -ForegroundColor Cyan
$SDK_FOUND = $false

# Check ANDROID_HOME
if ($env:ANDROID_HOME) {
    if (Test-Path $env:ANDROID_HOME) {
        Print-Success "ANDROID_HOME is set: $env:ANDROID_HOME"
        $SDK_FOUND = $true
        
        # Check for required SDK components
        if (Test-Path "$env:ANDROID_HOME\platform-tools") {
            Print-Success "SDK platform-tools found"
        } else {
            Print-Warning "SDK platform-tools not found"
        }
        
        if (Test-Path "$env:ANDROID_HOME\platforms") {
            $platformCount = (Get-ChildItem "$env:ANDROID_HOME\platforms" -ErrorAction SilentlyContinue | Measure-Object).Count
            Print-Success "SDK platforms found ($platformCount installed)"
        } else {
            Print-Warning "SDK platforms directory not found"
        }
    } else {
        Print-Warning "ANDROID_HOME points to non-existent directory: $env:ANDROID_HOME"
    }
} else {
    Print-Warning "ANDROID_HOME not set"
}

# Check default location
if (-not $SDK_FOUND) {
    $defaultSdkPath = "$env:LOCALAPPDATA\Android\Sdk"
    if (Test-Path $defaultSdkPath) {
        Print-Warning "Found Android SDK at default location: $defaultSdkPath"
        Print-Info "Set with: `$env:ANDROID_HOME = '$defaultSdkPath'"
        $env:ANDROID_HOME = $defaultSdkPath
        $SDK_FOUND = $true
    }
}

# Check local.properties
if (Test-Path "android\local.properties") {
    $sdkDir = (Get-Content "android\local.properties" | Select-String -Pattern 'sdk\.dir=(.+)' | ForEach-Object { $_.Matches.Groups[1].Value })
    if ($sdkDir -and (Test-Path $sdkDir)) {
        Print-Success "local.properties found with SDK location: $sdkDir"
        $SDK_FOUND = $true
    } else {
        Print-Warning "local.properties exists but SDK path may be invalid"
    }
} else {
    Print-Warning "android\local.properties not found"
    if ($SDK_FOUND -and $env:ANDROID_HOME) {
        Print-Info "Creating local.properties..."
        $sdkPathEscaped = $env:ANDROID_HOME -replace '\\', '\\'
        "sdk.dir=$sdkPathEscaped" | Out-File -FilePath "android\local.properties" -Encoding ASCII
        Print-Success "Created local.properties"
    }
}

if (-not $SDK_FOUND) {
    Print-Error "Android SDK not found or not configured"
    Print-Info "Options:"
    Print-Info "  1. Run: .\install-android-sdk.ps1"
    Print-Info "  2. Install Android Studio (includes SDK)"
    Print-Info "  3. Set ANDROID_HOME environment variable"
    Write-Host ""
    $response = Read-Host "Continue anyway? Build will likely fail. (Y/N)"
    if ($response -ne "Y" -and $response -ne "y") {
        exit 1
    }
}

Write-Host ""

# Step 6: Clean previous builds (optional)
Write-Host "Step 6: Preparing build environment..." -ForegroundColor Cyan
$cleanResponse = Read-Host "Clean previous builds? (Y/N)"
if ($cleanResponse -eq "Y" -or $cleanResponse -eq "y") {
    Print-Info "Cleaning previous builds..."
    Set-Location android
    .\gradlew.bat clean
    Set-Location ..
    if ($LASTEXITCODE -eq 0) {
        Print-Success "Build cleaned"
    } else {
        Print-Warning "Clean had issues, but continuing..."
    }
}

Write-Host ""

# Step 7: Build the APK
Write-Host "Step 7: Building Debug APK..." -ForegroundColor Cyan
Write-Host ""
Set-Location android

Print-Info "Starting Gradle build (this may take several minutes)..."
Write-Host ""

try {
    .\gradlew.bat assembleDebug
    
    if ($LASTEXITCODE -eq 0) {
        Set-Location ..
        Write-Host ""
        Print-Success "APK built successfully!"
        Write-Host ""
        
        $APK_PATH = "android\app\build\outputs\apk\debug\app-debug.apk"
        if (Test-Path $APK_PATH) {
            $apkSize = (Get-Item $APK_PATH).Length / 1MB
            $apkSizeFormatted = "{0:N2}" -f $apkSize
            Print-Success "APK Location: $APK_PATH"
            Print-Success "APK Size: $apkSizeFormatted MB"
            Write-Host ""
            Write-Host "==========================================" -ForegroundColor Cyan
            Write-Host "✓ BUILD SUCCESSFUL!" -ForegroundColor Green
            Write-Host "==========================================" -ForegroundColor Cyan
            Write-Host ""
            Write-Host "Your APK is ready at:" -ForegroundColor Green
            $fullPath = (Resolve-Path $APK_PATH).Path
            Write-Host "  $fullPath" -ForegroundColor White
            Write-Host ""
            Write-Host "To install on a connected Android device:" -ForegroundColor Cyan
            Write-Host "  adb install `"$fullPath`"" -ForegroundColor White
            Write-Host ""
            Write-Host "Or copy the APK to your device and install manually." -ForegroundColor Gray
            Write-Host ""
        } else {
            Print-Error "APK file not found at expected location: $APK_PATH"
            exit 1
        }
    } else {
        Set-Location ..
        Print-Error "Build failed. Check the error messages above."
        exit 1
    }
} catch {
    Set-Location ..
    Print-Error "Build failed with error: $_"
    exit 1
}

