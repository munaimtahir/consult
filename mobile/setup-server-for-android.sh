#!/bin/bash
# Master Server Setup Script for Android Debug APK Builds
# This script automatically installs and configures all prerequisites needed
# to build Android debug APK files on the server.
#
# Usage:
#   ./setup-server-for-android.sh          # Interactive mode
#   ./setup-server-for-android.sh --yes    # Non-interactive mode (for CI/CD)

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Parse arguments
NON_INTERACTIVE=false
if [[ "$1" == "--yes" ]] || [[ "$1" == "-y" ]]; then
    NON_INTERACTIVE=true
fi

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
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
    echo -e "${BLUE}ℹ${NC} $1"
}

print_header() {
    echo ""
    echo "=========================================="
    echo "$1"
    echo "=========================================="
}

# Function to prompt user (if not in non-interactive mode)
prompt_user() {
    if [ "$NON_INTERACTIVE" = true ]; then
        return 0  # Auto-accept in non-interactive mode
    fi
    read -p "$1 (y/n) " -n 1 -r
    echo
    [[ $REPLY =~ ^[Yy]$ ]]
}

# Track installation status
JAVA_INSTALLED=false
NODE_INSTALLED=false
SDK_INSTALLED=false
DEPS_INSTALLED=false

echo "=========================================="
echo "Android Debug APK - Server Setup"
echo "=========================================="
echo ""
echo "This script will set up your server for Android development:"
echo "  1. Install Java JDK 17"
echo "  2. Install Node.js 18+"
echo "  3. Install Android SDK command-line tools"
echo "  4. Configure environment variables"
echo "  5. Install npm dependencies"
echo "  6. Configure project files"
echo "  7. Verify setup"
echo ""

if [ "$NON_INTERACTIVE" = false ]; then
    if ! prompt_user "Continue with setup?"; then
        echo "Setup cancelled."
        exit 0
    fi
fi

# ============================================================================
# Step 1: Java JDK 17 Setup
# ============================================================================
print_header "Step 1: Java JDK 17 Setup"

JAVA_NEEDS_INSTALL=false
JAVA_NEEDS_UPGRADE=false

if command -v java &> /dev/null; then
    JAVA_VERSION=$(java -version 2>&1 | head -n 1)
    JAVA_MAJOR=$(java -version 2>&1 | awk -F '"' '/version/ {print $2}' | cut -d'.' -f1)
    
    if [ "$JAVA_MAJOR" -ge 17 ] && command -v javac &> /dev/null; then
        print_success "Java JDK $JAVA_MAJOR already installed: $JAVA_VERSION"
        JAVA_INSTALLED=true
    else
        if [ "$JAVA_MAJOR" -lt 17 ]; then
            print_warning "Java version $JAVA_MAJOR is too old. Need Java 17+"
            JAVA_NEEDS_UPGRADE=true
        else
            print_warning "Java found but javac not found. Need JDK, not just JRE."
            JAVA_NEEDS_INSTALL=true
        fi
    fi
else
    print_warning "Java not found"
    JAVA_NEEDS_INSTALL=true
fi

if [ "$JAVA_NEEDS_INSTALL" = true ] || [ "$JAVA_NEEDS_UPGRADE" = true ]; then
    if [ "$NON_INTERACTIVE" = true ] || prompt_user "Install Java JDK 17? (requires sudo)"; then
        print_info "Installing Java JDK 17..."
        sudo apt update
        sudo apt install -y openjdk-17-jdk
        print_success "Java JDK 17 installed"
        JAVA_INSTALLED=true
    else
        print_error "Java JDK 17 is required. Please install manually and run this script again."
        exit 1
    fi
fi

# Set JAVA_HOME
if [ -z "$JAVA_HOME" ]; then
    JAVA_PATH=$(readlink -f $(which java) 2>/dev/null || echo "")
    if [ -n "$JAVA_PATH" ]; then
        DETECTED_JAVA_HOME=$(dirname $(dirname "$JAVA_PATH"))
        export JAVA_HOME="$DETECTED_JAVA_HOME"
        export PATH="$JAVA_HOME/bin:$PATH"
        
        # Add to bashrc if not already there
        if ! grep -q "JAVA_HOME.*$DETECTED_JAVA_HOME" ~/.bashrc 2>/dev/null; then
            if ! grep -q "^export JAVA_HOME" ~/.bashrc 2>/dev/null; then
                echo "" >> ~/.bashrc
                echo "# Java Configuration - Android Build Setup" >> ~/.bashrc
                echo "export JAVA_HOME=\"$DETECTED_JAVA_HOME\"" >> ~/.bashrc
                echo "export PATH=\"\$JAVA_HOME/bin:\$PATH\"" >> ~/.bashrc
                print_success "JAVA_HOME configured: $DETECTED_JAVA_HOME"
            else
                # Update existing JAVA_HOME
                sed -i "s|^export JAVA_HOME=.*|export JAVA_HOME=\"$DETECTED_JAVA_HOME\"|" ~/.bashrc
                print_success "JAVA_HOME updated: $DETECTED_JAVA_HOME"
            fi
        else
            print_info "JAVA_HOME already configured in ~/.bashrc"
        fi
    fi
else
    if [ -f "$JAVA_HOME/bin/java" ]; then
        print_success "JAVA_HOME already set: $JAVA_HOME"
    else
        print_warning "JAVA_HOME is set but path is invalid: $JAVA_HOME"
    fi
fi

# Verify Java is accessible
if ! command -v java &> /dev/null || ! command -v javac &> /dev/null; then
    print_error "Java setup incomplete. Please check JAVA_HOME configuration."
    exit 1
fi

# ============================================================================
# Step 2: Node.js Setup
# ============================================================================
print_header "Step 2: Node.js 18+ Setup"

NODE_NEEDS_INSTALL=false

if command -v node &> /dev/null; then
    NODE_VERSION=$(node -v)
    NODE_MAJOR=$(node -v | cut -d'.' -f1 | sed 's/v//')
    
    if [ "$NODE_MAJOR" -ge 18 ]; then
        print_success "Node.js already installed: $NODE_VERSION"
        NODE_INSTALLED=true
    else
        print_warning "Node.js version $NODE_VERSION is too old. Need 18+"
        NODE_NEEDS_INSTALL=true
    fi
else
    print_warning "Node.js not found"
    NODE_NEEDS_INSTALL=true
fi

if [ "$NODE_NEEDS_INSTALL" = true ]; then
    # Check for NVM
    if [ -s "$HOME/.nvm/nvm.sh" ]; then
        print_info "NVM found. Installing Node.js 18..."
        export NVM_DIR="$HOME/.nvm"
        [ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"
        nvm install 18
        nvm use 18
        nvm alias default 18
        print_success "Node.js 18 installed via NVM"
        NODE_INSTALLED=true
    else
        if [ "$NON_INTERACTIVE" = true ] || prompt_user "Install NVM and Node.js 18?"; then
            print_info "Installing NVM and Node.js 18..."
            curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash
            export NVM_DIR="$HOME/.nvm"
            [ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"
            nvm install 18
            nvm use 18
            nvm alias default 18
            
            # Add NVM to bashrc if not already there
            if ! grep -q "NVM_DIR" ~/.bashrc 2>/dev/null; then
                echo "" >> ~/.bashrc
                echo "# NVM Configuration" >> ~/.bashrc
                echo 'export NVM_DIR="$HOME/.nvm"' >> ~/.bashrc
                echo '[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"' >> ~/.bashrc
                echo '[ -s "$NVM_DIR/bash_completion" ] && \. "$NVM_DIR/bash_completion"' >> ~/.bashrc
            fi
            
            print_success "NVM and Node.js 18 installed"
            NODE_INSTALLED=true
        else
            print_error "Node.js 18+ is required. Please install manually and run this script again."
            exit 1
        fi
    fi
fi

# Verify npm
if command -v npm &> /dev/null; then
    NPM_VERSION=$(npm -v)
    print_success "npm found: v$NPM_VERSION"
else
    print_error "npm not found"
    exit 1
fi

# ============================================================================
# Step 3: Android SDK Installation
# ============================================================================
print_header "Step 3: Android SDK Installation"

SDK_DIR="$HOME/Android/Sdk"

if [ -n "$ANDROID_HOME" ] && [ -f "$ANDROID_HOME/platform-tools/adb" ]; then
    print_success "Android SDK already installed at: $ANDROID_HOME"
    SDK_INSTALLED=true
    
    if [ "$NON_INTERACTIVE" = false ]; then
        if prompt_user "Reinstall Android SDK?"; then
            SDK_INSTALLED=false
        fi
    fi
fi

if [ "$SDK_INSTALLED" = false ]; then
    if [ "$NON_INTERACTIVE" = true ] || prompt_user "Install Android SDK? (This may take 5-10 minutes)"; then
        print_info "Running Android SDK installation script..."
        if [ -f "./install-android-sdk.sh" ]; then
            # Make it executable
            chmod +x ./install-android-sdk.sh
            # Run in non-interactive mode if we're in non-interactive mode
            if [ "$NON_INTERACTIVE" = true ]; then
                # Temporarily modify install script to be non-interactive
                # or just run it and accept defaults
                echo "y" | ./install-android-sdk.sh || {
                    # If it still prompts, try running with expect or just proceed
                    print_warning "SDK installation may have prompted. Continuing..."
                }
            else
                ./install-android-sdk.sh
            fi
            SDK_INSTALLED=true
        else
            print_error "install-android-sdk.sh not found"
            exit 1
        fi
    else
        print_warning "Skipping Android SDK installation"
    fi
fi

# Ensure ANDROID_HOME is set
if [ -z "$ANDROID_HOME" ]; then
    if [ -d "$SDK_DIR" ] && [ -f "$SDK_DIR/platform-tools/adb" ]; then
        export ANDROID_HOME="$SDK_DIR"
        if ! grep -q "ANDROID_HOME" ~/.bashrc 2>/dev/null; then
            echo "" >> ~/.bashrc
            echo "# Android SDK Configuration" >> ~/.bashrc
            echo "export ANDROID_HOME=\"$SDK_DIR\"" >> ~/.bashrc
            echo "export PATH=\"\$PATH:\$ANDROID_HOME/cmdline-tools/latest/bin\"" >> ~/.bashrc
            echo "export PATH=\"\$PATH:\$ANDROID_HOME/platform-tools\"" >> ~/.bashrc
        fi
        print_success "ANDROID_HOME configured: $ANDROID_HOME"
    fi
fi

# ============================================================================
# Step 4: Install npm Dependencies
# ============================================================================
print_header "Step 4: Installing npm Dependencies"

if [ ! -d "node_modules" ] || [ ! -f "node_modules/.package-lock.json" ]; then
    print_info "Installing npm dependencies (this may take a few minutes)..."
    npm install
    print_success "npm dependencies installed"
    DEPS_INSTALLED=true
else
    print_info "node_modules exists. Updating dependencies..."
    npm install
    print_success "npm dependencies up to date"
    DEPS_INSTALLED=true
fi

# ============================================================================
# Step 5: Configure Project Files
# ============================================================================
print_header "Step 5: Configuring Project Files"

# Create/update local.properties
if [ -n "$ANDROID_HOME" ]; then
    LOCAL_PROPERTIES="android/local.properties"
    if [ ! -f "$LOCAL_PROPERTIES" ]; then
        echo "sdk.dir=$ANDROID_HOME" > "$LOCAL_PROPERTIES"
        print_success "Created $LOCAL_PROPERTIES"
    else
        if ! grep -q "sdk.dir" "$LOCAL_PROPERTIES"; then
            echo "sdk.dir=$ANDROID_HOME" >> "$LOCAL_PROPERTIES"
            print_success "Added SDK path to $LOCAL_PROPERTIES"
        else
            # Update existing sdk.dir
            sed -i "s|sdk.dir=.*|sdk.dir=$ANDROID_HOME|" "$LOCAL_PROPERTIES"
            print_success "Updated $LOCAL_PROPERTIES"
        fi
    fi
fi

# Ensure Gradle wrapper is executable
if [ -f "android/gradlew" ]; then
    if [ ! -x "android/gradlew" ]; then
        chmod +x android/gradlew
        print_success "Made gradlew executable"
    else
        print_info "Gradle wrapper is already executable"
    fi
else
    print_warning "Gradle wrapper not found at android/gradlew"
fi

# ============================================================================
# Step 6: Final Verification
# ============================================================================
print_header "Step 6: Final Verification"

VERIFICATION_PASSED=true

# Check Java
if command -v java &> /dev/null && command -v javac &> /dev/null; then
    JAVA_VER=$(java -version 2>&1 | head -n 1)
    print_success "Java: $JAVA_VER"
else
    print_error "Java verification failed"
    VERIFICATION_PASSED=false
fi

# Check Node.js
if command -v node &> /dev/null; then
    NODE_VER=$(node -v)
    print_success "Node.js: $NODE_VER"
else
    print_error "Node.js verification failed"
    VERIFICATION_PASSED=false
fi

# Check npm
if command -v npm &> /dev/null; then
    NPM_VER=$(npm -v)
    print_success "npm: v$NPM_VER"
else
    print_error "npm verification failed"
    VERIFICATION_PASSED=false
fi

# Check Android SDK
if [ -n "$ANDROID_HOME" ] && [ -f "$ANDROID_HOME/platform-tools/adb" ]; then
    print_success "Android SDK: $ANDROID_HOME"
else
    print_warning "Android SDK verification: SDK may not be fully installed"
fi

# Check node_modules
if [ -d "node_modules" ]; then
    MODULE_COUNT=$(ls -1 node_modules 2>/dev/null | wc -l)
    if [ "$MODULE_COUNT" -gt 0 ]; then
        print_success "npm dependencies: $MODULE_COUNT packages installed"
    else
        print_warning "npm dependencies: node_modules exists but appears empty"
    fi
else
    print_warning "npm dependencies: node_modules not found"
fi

# Check Gradle wrapper
if [ -f "android/gradlew" ] && [ -x "android/gradlew" ]; then
    print_success "Gradle wrapper: Ready"
else
    print_warning "Gradle wrapper: Not found or not executable"
fi

# ============================================================================
# Summary
# ============================================================================
echo ""
print_header "Setup Summary"

if [ "$VERIFICATION_PASSED" = true ]; then
    print_success "Server setup completed successfully!"
    echo ""
    echo "Installed components:"
    [ "$JAVA_INSTALLED" = true ] && echo "  ✓ Java JDK 17"
    [ "$NODE_INSTALLED" = true ] && echo "  ✓ Node.js 18+"
    [ "$SDK_INSTALLED" = true ] && echo "  ✓ Android SDK"
    [ "$DEPS_INSTALLED" = true ] && echo "  ✓ npm dependencies"
    echo ""
    print_warning "Important: Run 'source ~/.bashrc' or restart your terminal"
    echo "           to load all environment variables."
    echo ""
    echo "Next steps:"
    echo "  1. Reload environment: source ~/.bashrc"
    echo "  2. Build debug APK: ./build-apk-automated.sh"
    echo ""
    echo "The debug APK will be generated at:"
    echo "  android/app/build/outputs/apk/debug/app-debug.apk"
    echo ""
    exit 0
else
    print_error "Setup completed with warnings or errors."
    echo ""
    echo "Please review the verification output above and fix any issues."
    echo "You can run this script again - it's safe to run multiple times."
    echo ""
    exit 1
fi





