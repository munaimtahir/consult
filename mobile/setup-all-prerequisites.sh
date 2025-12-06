#!/bin/bash
# Complete Prerequisites Setup Script
# Installs Java, Node.js (if needed), Android SDK, and configures everything

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

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

echo "=========================================="
echo "Complete Prerequisites Setup"
echo "=========================================="
echo ""
echo "This script will:"
echo "  1. Check/Install Java JDK 17"
echo "  2. Check/Install Node.js 18+"
echo "  3. Install Android SDK"
echo "  4. Configure all environment variables"
echo "  5. Set up project configuration"
echo ""
read -p "Continue? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Setup cancelled."
    exit 0
fi

echo ""

# Step 1: Check/Setup Java
echo "=========================================="
echo "Step 1: Java JDK 17 Setup"
echo "=========================================="

if command -v java &> /dev/null; then
    JAVA_VERSION=$(java -version 2>&1 | head -n 1)
    JAVA_MAJOR=$(java -version 2>&1 | awk -F '"' '/version/ {print $2}' | cut -d'.' -f1)
    
    if [ "$JAVA_MAJOR" -ge 17 ] && command -v javac &> /dev/null; then
        print_success "Java JDK $JAVA_MAJOR already installed: $JAVA_VERSION"
    else
        print_warning "Java found but version is $JAVA_MAJOR or not JDK"
        print_info "Please install Java JDK 17 manually"
    fi
else
    print_error "Java not found"
    print_info "Install with: sudo apt install -y openjdk-17-jdk"
    read -p "Install Java now? (requires sudo) (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        sudo apt update
        sudo apt install -y openjdk-17-jdk
        print_success "Java installed"
    else
        print_error "Java is required. Please install manually and run this script again."
        exit 1
    fi
fi

# Set JAVA_HOME
if [ -z "$JAVA_HOME" ]; then
    JAVA_PATH=$(readlink -f $(which java) 2>/dev/null)
    if [ -n "$JAVA_PATH" ]; then
        DETECTED_JAVA_HOME=$(dirname $(dirname "$JAVA_PATH"))
        export JAVA_HOME="$DETECTED_JAVA_HOME"
        export PATH="$JAVA_HOME/bin:$PATH"
        
        # Add to bashrc
        if ! grep -q "JAVA_HOME" ~/.bashrc 2>/dev/null; then
            echo "" >> ~/.bashrc
            echo "# Java Configuration" >> ~/.bashrc
            echo "export JAVA_HOME=\"$DETECTED_JAVA_HOME\"" >> ~/.bashrc
            echo "export PATH=\"\$JAVA_HOME/bin:\$PATH\"" >> ~/.bashrc
            print_success "JAVA_HOME configured: $DETECTED_JAVA_HOME"
        else
            print_info "JAVA_HOME already in ~/.bashrc"
        fi
    fi
else
    print_success "JAVA_HOME already set: $JAVA_HOME"
fi

echo ""

# Step 2: Check/Setup Node.js
echo "=========================================="
echo "Step 2: Node.js Setup"
echo "=========================================="

if command -v node &> /dev/null; then
    NODE_VERSION=$(node -v)
    NODE_MAJOR=$(node -v | cut -d'.' -f1 | sed 's/v//')
    
    if [ "$NODE_MAJOR" -ge 18 ]; then
        print_success "Node.js already installed: $NODE_VERSION"
    else
        print_warning "Node.js version $NODE_VERSION is too old. Need 18+"
    fi
else
    print_warning "Node.js not found"
    
    # Check for NVM
    if [ -s "$HOME/.nvm/nvm.sh" ]; then
        print_info "NVM found. Installing Node.js 18..."
        export NVM_DIR="$HOME/.nvm"
        [ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"
        nvm install 18
        nvm use 18
        nvm alias default 18
        print_success "Node.js 18 installed via NVM"
    else
        print_info "Installing NVM and Node.js 18..."
        curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash
        export NVM_DIR="$HOME/.nvm"
        [ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"
        nvm install 18
        nvm use 18
        nvm alias default 18
        print_success "NVM and Node.js 18 installed"
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

echo ""

# Step 3: Install npm dependencies
echo "=========================================="
echo "Step 3: Installing npm Dependencies"
echo "=========================================="

if [ ! -d "node_modules" ]; then
    print_info "Installing npm dependencies (this may take a few minutes)..."
    npm install
    print_success "npm dependencies installed"
else
    print_info "Updating npm dependencies..."
    npm install
    print_success "npm dependencies up to date"
fi

echo ""

# Step 4: Install Android SDK
echo "=========================================="
echo "Step 4: Android SDK Installation"
echo "=========================================="

if [ -n "$ANDROID_HOME" ] && [ -f "$ANDROID_HOME/platform-tools/adb" ]; then
    print_success "Android SDK already installed at: $ANDROID_HOME"
    read -p "Reinstall Android SDK? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        print_info "Skipping Android SDK installation"
        SKIP_SDK=true
    fi
fi

if [ "$SKIP_SDK" != "true" ]; then
    print_info "Running Android SDK installation script..."
    ./install-android-sdk.sh
fi

echo ""

# Step 5: Final Verification
echo "=========================================="
echo "Step 5: Final Verification"
echo "=========================================="

print_info "Running prerequisites check..."
./check-prerequisites.sh

echo ""
echo "=========================================="
echo "Setup Complete!"
echo "=========================================="
echo ""
print_warning "Important: Run 'source ~/.bashrc' or restart your terminal"
echo "           to load all environment variables."
echo ""
echo "Next steps:"
echo "  1. Reload environment: source ~/.bashrc"
echo "  2. Build APK: ./build-apk-automated.sh"
echo ""

