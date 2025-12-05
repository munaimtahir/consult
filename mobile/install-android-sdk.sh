#!/bin/bash
# Android SDK Installation Script for Server/CI Environments
# This script installs Android SDK command-line tools without Android Studio

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
echo "Android SDK Installation Script"
echo "=========================================="
echo ""

# Configuration
SDK_DIR="$HOME/Android/Sdk"
COMMAND_LINE_TOOLS_VERSION="11076708_latest"
ANDROID_PLATFORM="android-33"
BUILD_TOOLS_VERSION="33.0.0"

# Check if SDK already exists
if [ -d "$SDK_DIR" ] && [ -f "$SDK_DIR/platform-tools/adb" ]; then
    print_warning "Android SDK appears to already be installed at: $SDK_DIR"
    read -p "Continue installation anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Installation cancelled."
        exit 0
    fi
fi

# Step 1: Create SDK directory
echo "Step 1: Creating SDK directory..."
mkdir -p "$SDK_DIR"
cd "$SDK_DIR"
print_success "SDK directory created: $SDK_DIR"

# Step 2: Download command-line tools
echo ""
echo "Step 2: Downloading Android SDK command-line tools..."
TOOLS_URL="https://dl.google.com/android/repository/commandlinetools-linux-${COMMAND_LINE_TOOLS_VERSION}.zip"
TOOLS_ZIP="commandlinetools-linux-${COMMAND_LINE_TOOLS_VERSION}.zip"

if [ -f "$TOOLS_ZIP" ]; then
    print_warning "Command-line tools zip already exists. Skipping download."
else
    print_info "Downloading from: $TOOLS_URL"
    print_info "This may take a few minutes..."
    
    if command -v wget &> /dev/null; then
        wget -q --show-progress "$TOOLS_URL" -O "$TOOLS_ZIP"
    elif command -v curl &> /dev/null; then
        curl -L --progress-bar "$TOOLS_URL" -o "$TOOLS_ZIP"
    else
        print_error "Neither wget nor curl found. Please install one of them."
        exit 1
    fi
    
    if [ ! -f "$TOOLS_ZIP" ]; then
        print_error "Download failed. Please check your internet connection."
        exit 1
    fi
    
    print_success "Download complete"
fi

# Step 3: Extract command-line tools
echo ""
echo "Step 3: Extracting command-line tools..."
if [ ! -d "cmdline-tools" ]; then
    unzip -q "$TOOLS_ZIP" || {
        print_error "Failed to extract command-line tools. The zip file may be corrupted."
        exit 1
    }
    
    # Organize cmdline-tools structure
    if [ -d "cmdline-tools" ]; then
        # Already in correct structure
        true
    elif [ -d "tools" ]; then
        # Old structure - need to reorganize
        mkdir -p cmdline-tools/latest
        mv tools/* cmdline-tools/latest/ 2>/dev/null || true
        rmdir tools 2>/dev/null || true
    fi
    
    # Ensure latest directory exists
    if [ ! -d "cmdline-tools/latest" ]; then
        mkdir -p cmdline-tools/latest
        # Move contents if they're in wrong place
        if [ -d "cmdline-tools/bin" ]; then
            mv cmdline-tools/* cmdline-tools/latest/ 2>/dev/null || true
        fi
    fi
    
    print_success "Command-line tools extracted"
else
    print_warning "cmdline-tools directory already exists. Skipping extraction."
fi

# Step 4: Set up environment variables
echo ""
echo "Step 4: Setting up environment variables..."

# Set for current session
export ANDROID_HOME="$SDK_DIR"
export PATH="$PATH:$ANDROID_HOME/cmdline-tools/latest/bin"
export PATH="$PATH:$ANDROID_HOME/platform-tools"

# Add to bashrc if not already there
BASH_RC="$HOME/.bashrc"
if ! grep -q "ANDROID_HOME" "$BASH_RC" 2>/dev/null; then
    echo "" >> "$BASH_RC"
    echo "# Android SDK Configuration" >> "$BASH_RC"
    echo "export ANDROID_HOME=\"$SDK_DIR\"" >> "$BASH_RC"
    echo "export PATH=\"\$PATH:\$ANDROID_HOME/cmdline-tools/latest/bin\"" >> "$BASH_RC"
    echo "export PATH=\"\$PATH:\$ANDROID_HOME/platform-tools\"" >> "$BASH_RC"
    print_success "Added Android SDK paths to ~/.bashrc"
else
    print_warning "Android SDK paths already in ~/.bashrc"
fi

print_success "Environment variables configured"

# Step 5: Accept licenses
echo ""
echo "Step 5: Accepting Android SDK licenses..."
print_info "This will accept all Android SDK licenses automatically..."

# Try to accept licenses
if [ -f "$SDK_DIR/cmdline-tools/latest/bin/sdkmanager" ]; then
    yes | "$SDK_DIR/cmdline-tools/latest/bin/sdkmanager" --licenses > /dev/null 2>&1 || {
        print_warning "Could not automatically accept licenses"
        print_info "You may need to run: sdkmanager --licenses manually"
    }
    print_success "Licenses accepted"
else
    print_warning "sdkmanager not found yet. Will accept licenses after installing platform-tools."
fi

# Step 6: Install SDK components
echo ""
echo "Step 6: Installing Android SDK components..."
print_info "Installing platform-tools, SDK platform, and build-tools..."
print_info "This may take several minutes..."

SDKMANAGER="$SDK_DIR/cmdline-tools/latest/bin/sdkmanager"

if [ ! -f "$SDKMANAGER" ]; then
    print_error "sdkmanager not found at: $SDKMANAGER"
    print_info "Please check the cmdline-tools directory structure"
    exit 1
fi

# Install components
print_info "Installing platform-tools..."
"$SDKMANAGER" "platform-tools" || {
    print_error "Failed to install platform-tools"
    exit 1
}

print_info "Installing SDK Platform $ANDROID_PLATFORM..."
"$SDKMANAGER" "platforms;$ANDROID_PLATFORM" || {
    print_warning "Failed to install platform $ANDROID_PLATFORM, trying android-34..."
    ANDROID_PLATFORM="android-34"
    "$SDKMANAGER" "platforms;$ANDROID_PLATFORM" || {
        print_error "Failed to install SDK platform"
        exit 1
    }
}

print_info "Installing build-tools $BUILD_TOOLS_VERSION..."
"$SDKMANAGER" "build-tools;$BUILD_TOOLS_VERSION" || {
    print_warning "Failed to install build-tools $BUILD_TOOLS_VERSION, trying latest..."
    "$SDKMANAGER" "build-tools;latest" || {
        print_error "Failed to install build-tools"
        exit 1
    }
}

print_success "SDK components installed"

# Step 7: Accept licenses again (now that sdkmanager works properly)
echo ""
echo "Step 7: Accepting SDK licenses..."
yes | "$SDKMANAGER" --licenses > /dev/null 2>&1 || true
print_success "Licenses configured"

# Step 8: Create local.properties for the project
echo ""
echo "Step 8: Configuring project..."
PROJECT_LOCAL_PROPERTIES="$SCRIPT_DIR/android/local.properties"
if [ ! -f "$PROJECT_LOCAL_PROPERTIES" ]; then
    echo "sdk.dir=$SDK_DIR" > "$PROJECT_LOCAL_PROPERTIES"
    print_success "Created local.properties: $PROJECT_LOCAL_PROPERTIES"
else
    # Update if exists
    if ! grep -q "sdk.dir" "$PROJECT_LOCAL_PROPERTIES"; then
        echo "sdk.dir=$SDK_DIR" >> "$PROJECT_LOCAL_PROPERTIES"
    else
        sed -i "s|sdk.dir=.*|sdk.dir=$SDK_DIR|" "$PROJECT_LOCAL_PROPERTIES"
    fi
    print_success "Updated local.properties"
fi

# Step 9: Verify installation
echo ""
echo "Step 9: Verifying installation..."

if [ -f "$SDK_DIR/platform-tools/adb" ]; then
    ADB_VERSION=$("$SDK_DIR/platform-tools/adb" version 2>&1 | head -1)
    print_success "ADB found: $ADB_VERSION"
else
    print_error "ADB not found - installation may have failed"
    exit 1
fi

if [ -d "$SDK_DIR/platforms" ]; then
    PLATFORM_COUNT=$(ls -1 "$SDK_DIR/platforms" 2>/dev/null | wc -l)
    print_success "SDK platforms installed: $PLATFORM_COUNT"
else
    print_error "No SDK platforms found"
    exit 1
fi

if [ -d "$SDK_DIR/build-tools" ]; then
    BUILD_TOOLS_COUNT=$(ls -1 "$SDK_DIR/build-tools" 2>/dev/null | wc -l)
    print_success "Build tools installed: $BUILD_TOOLS_COUNT"
else
    print_error "No build tools found"
    exit 1
fi

# Summary
echo ""
echo "=========================================="
echo "Installation Complete!"
echo "=========================================="
echo ""
print_success "Android SDK installed at: $SDK_DIR"
echo ""
echo "Configuration:"
echo "  - ANDROID_HOME: $SDK_DIR"
echo "  - Platform: $ANDROID_PLATFORM"
echo "  - Build Tools: $BUILD_TOOLS_VERSION"
echo "  - local.properties: $PROJECT_LOCAL_PROPERTIES"
echo ""
echo "Environment variables have been added to ~/.bashrc"
echo ""
print_warning "Important: Run 'source ~/.bashrc' or restart your terminal"
echo "           to load the new environment variables."
echo ""
echo "You can now run: ./build-apk-automated.sh"
echo ""

