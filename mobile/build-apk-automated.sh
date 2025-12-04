#!/bin/bash
# Automated APK Build Script for Hospital Consult Mobile App
# This script automates the entire build process including dependency checks and installation

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "=========================================="
echo "Hospital Consult - Automated APK Builder"
echo "=========================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored messages
print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

print_info() {
    echo -e "  $1"
}

# Track if we need to exit early
EXIT_EARLY=false

# Step 1: Check Java Installation
echo "Step 1: Checking Java installation..."
if command -v java &> /dev/null; then
    JAVA_VERSION=$(java -version 2>&1 | head -n 1)
    print_success "Java found: $JAVA_VERSION"
    
    # Check if it's JDK (has javac)
    if command -v javac &> /dev/null; then
        print_success "JDK found (contains javac)"
    else
        print_error "Java found but javac not found. You need JDK, not just JRE."
        EXIT_EARLY=true
    fi
    
    # Check Java version (need 17+)
    JAVA_MAJOR_VERSION=$(java -version 2>&1 | awk -F '"' '/version/ {print $2}' | cut -d'.' -f1)
    if [ "$JAVA_MAJOR_VERSION" -lt 17 ]; then
        print_error "Java version is $JAVA_MAJOR_VERSION. Java 17 or higher is required."
        EXIT_EARLY=true
    else
        print_success "Java version $JAVA_MAJOR_VERSION is acceptable"
    fi
else
    print_error "Java not found in PATH"
    print_info "To install Java 17, run:"
    print_info "  sudo apt update"
    print_info "  sudo apt install -y openjdk-17-jdk"
    print_info ""
    print_info "Then set JAVA_HOME:"
    print_info "  export JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64"
    print_info "  export PATH=\$JAVA_HOME/bin:\$PATH"
    EXIT_EARLY=true
fi

# Check JAVA_HOME
if [ -z "$JAVA_HOME" ]; then
    print_warning "JAVA_HOME is not set"
    # Try to detect it
    if command -v java &> /dev/null; then
        JAVA_PATH=$(readlink -f $(which java) 2>/dev/null)
        if [ -n "$JAVA_PATH" ]; then
            DETECTED_JAVA_HOME=$(dirname $(dirname "$JAVA_PATH"))
            print_info "Detected Java at: $DETECTED_JAVA_HOME"
            export JAVA_HOME="$DETECTED_JAVA_HOME"
            export PATH="$JAVA_HOME/bin:$PATH"
            print_success "Set JAVA_HOME to $JAVA_HOME"
        fi
    fi
else
    print_success "JAVA_HOME is set: $JAVA_HOME"
fi

echo ""

# Step 2: Check Node.js Installation
echo "Step 2: Checking Node.js installation..."
if command -v node &> /dev/null; then
    NODE_VERSION=$(node -v)
    print_success "Node.js found: $NODE_VERSION"
    
    # Check Node version (need 18+)
    NODE_MAJOR_VERSION=$(node -v | cut -d'.' -f1 | sed 's/v//')
    if [ "$NODE_MAJOR_VERSION" -lt 18 ]; then
        print_error "Node.js version is too old. Node.js 18 or higher is required."
        print_info "Current version: $NODE_VERSION"
        EXIT_EARLY=true
    else
        print_success "Node.js version is acceptable"
    fi
else
    print_error "Node.js not found"
    print_info "To install Node.js 18+, you can:"
    print_info "  1. Install via nvm (recommended):"
    print_info "     curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash"
    print_info "     nvm install 18"
    print_info "  2. Or install via package manager:"
    print_info "     curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -"
    print_info "     sudo apt install -y nodejs"
    EXIT_EARLY=true
fi

if command -v npm &> /dev/null; then
    NPM_VERSION=$(npm -v)
    print_success "npm found: v$NPM_VERSION"
else
    print_error "npm not found"
    EXIT_EARLY=true
fi

echo ""

# If prerequisites are missing, exit
if [ "$EXIT_EARLY" = true ]; then
    print_error "Missing prerequisites. Please install the required software and run this script again."
    echo ""
    echo "Quick setup guide:"
    echo "  1. Install Java 17: sudo apt install -y openjdk-17-jdk"
    echo "  2. Install Node.js 18+: Use nvm or package manager"
    echo "  3. Set JAVA_HOME: export JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64"
    echo "  4. Run this script again"
    exit 1
fi

# Step 3: Install/Update Node Dependencies
echo "Step 3: Installing Node.js dependencies..."
if [ ! -d "node_modules" ]; then
    print_info "node_modules not found. Installing dependencies..."
    npm install
    print_success "Dependencies installed"
else
    print_info "node_modules exists. Checking for updates..."
    npm install
    print_success "Dependencies up to date"
fi

echo ""

# Step 4: Check Gradle Wrapper
echo "Step 4: Checking Gradle wrapper..."
if [ ! -f "android/gradlew" ]; then
    print_error "Gradle wrapper not found at android/gradlew"
    exit 1
fi

if [ ! -x "android/gradlew" ]; then
    print_info "Making gradlew executable..."
    chmod +x android/gradlew
    print_success "gradlew is now executable"
else
    print_success "Gradle wrapper is executable"
fi

# Test Gradle
print_info "Testing Gradle configuration..."
cd android
if ./gradlew --version > /dev/null 2>&1; then
    print_success "Gradle configuration is valid"
else
    print_error "Gradle configuration error"
    cd ..
    exit 1
fi
cd ..

echo ""

# Step 5: Check Android SDK (optional but recommended)
echo "Step 5: Checking Android SDK..."
if [ -n "$ANDROID_HOME" ]; then
    print_success "ANDROID_HOME is set: $ANDROID_HOME"
elif [ -d "$HOME/Android/Sdk" ]; then
    export ANDROID_HOME="$HOME/Android/Sdk"
    print_success "Found Android SDK at: $ANDROID_HOME"
else
    print_warning "Android SDK not found. Build may fail if SDK is required."
    print_info "To set up Android SDK:"
    print_info "  1. Install Android Studio (recommended)"
    print_info "  2. Or set ANDROID_HOME environment variable"
fi

# Create local.properties if ANDROID_HOME is set
if [ -n "$ANDROID_HOME" ] && [ ! -f "android/local.properties" ]; then
    print_info "Creating android/local.properties..."
    echo "sdk.dir=$ANDROID_HOME" > android/local.properties
    print_success "Created local.properties"
fi

echo ""

# Step 6: Clean previous builds (optional)
echo "Step 6: Preparing build environment..."
read -p "Clean previous builds? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    print_info "Cleaning previous builds..."
    cd android
    ./gradlew clean
    cd ..
    print_success "Build cleaned"
fi

echo ""

# Step 7: Build the APK
echo "Step 7: Building Debug APK..."
echo ""
cd android

print_info "Starting Gradle build (this may take several minutes)..."
echo ""

if ./gradlew assembleDebug; then
    cd ..
    echo ""
    print_success "APK built successfully!"
    echo ""
    
    APK_PATH="android/app/build/outputs/apk/debug/app-debug.apk"
    if [ -f "$APK_PATH" ]; then
        APK_SIZE=$(du -h "$APK_PATH" | cut -f1)
        print_success "APK Location: $APK_PATH"
        print_success "APK Size: $APK_SIZE"
        echo ""
        echo "=========================================="
        echo "✅ BUILD SUCCESSFUL!"
        echo "=========================================="
        echo ""
        echo "Your APK is ready at:"
        echo "  $(pwd)/$APK_PATH"
        echo ""
        echo "To install on a connected Android device:"
        echo "  adb install $APK_PATH"
        echo ""
        echo "Or copy the APK to your device and install manually."
        echo ""
        
        # Try to get absolute path
        ABS_APK_PATH=$(readlink -f "$APK_PATH")
        echo "Full path: $ABS_APK_PATH"
    else
        print_error "APK file not found at expected location: $APK_PATH"
        exit 1
    fi
else
    cd ..
    print_error "Build failed. Check the error messages above."
    exit 1
fi

