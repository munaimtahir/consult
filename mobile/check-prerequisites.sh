#!/bin/bash
# Comprehensive Prerequisites Check for Android APK Build
# This script checks all requirements for building the Android APK

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo "=========================================="
echo "Android APK Build - Prerequisites Check"
echo "=========================================="
echo ""

STATUS_OK=0
STATUS_WARNING=1
STATUS_ERROR=2

check_status=$STATUS_OK

# Function to print status
print_ok() {
    echo -e "${GREEN}✓${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
    check_status=$STATUS_ERROR
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
    if [ $check_status -eq $STATUS_OK ]; then
        check_status=$STATUS_WARNING
    fi
}

print_info() {
    echo -e "${BLUE}ℹ${NC} $1"
}

# 1. Check Java Installation
echo "1. Checking Java Installation..."
if command -v java &> /dev/null; then
    JAVA_VERSION=$(java -version 2>&1 | head -n 1)
    print_ok "Java found: $JAVA_VERSION"
    
    # Check version
    JAVA_MAJOR=$(java -version 2>&1 | awk -F '"' '/version/ {print $2}' | cut -d'.' -f1)
    if [ "$JAVA_MAJOR" -ge 17 ]; then
        print_ok "Java version $JAVA_MAJOR is acceptable (17+ required)"
    else
        print_error "Java version $JAVA_MAJOR is too old. Need Java 17 or higher."
    fi
    
    # Check for javac (JDK vs JRE)
    if command -v javac &> /dev/null; then
        print_ok "JDK found (javac available)"
    else
        print_error "Only JRE found. Need JDK (Java Development Kit) for building."
    fi
    
    # Check JAVA_HOME
    if [ -z "$JAVA_HOME" ]; then
        # Try to detect
        JAVA_PATH=$(readlink -f $(which java) 2>/dev/null)
        if [ -n "$JAVA_PATH" ]; then
            DETECTED_JAVA_HOME=$(dirname $(dirname "$JAVA_PATH"))
            print_warning "JAVA_HOME not set. Detected: $DETECTED_JAVA_HOME"
            print_info "Set it with: export JAVA_HOME=$DETECTED_JAVA_HOME"
        else
            print_warning "JAVA_HOME not set and cannot be auto-detected"
        fi
    else
        if [ -f "$JAVA_HOME/bin/java" ]; then
            print_ok "JAVA_HOME is set: $JAVA_HOME"
        else
            print_error "JAVA_HOME is set to invalid path: $JAVA_HOME"
        fi
    fi
else
    print_error "Java not found in PATH"
    print_info "Install with: sudo apt install -y openjdk-17-jdk"
fi

echo ""

# 2. Check Node.js Installation
echo "2. Checking Node.js Installation..."
if command -v node &> /dev/null; then
    NODE_VERSION=$(node -v)
    print_ok "Node.js found: $NODE_VERSION"
    
    NODE_MAJOR=$(node -v | cut -d'.' -f1 | sed 's/v//')
    if [ "$NODE_MAJOR" -ge 18 ]; then
        print_ok "Node.js version is acceptable (18+ required)"
    else
        print_error "Node.js version is too old. Need Node.js 18 or higher."
    fi
else
    print_error "Node.js not found"
    print_info "Install with NVM: curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash"
fi

if command -v npm &> /dev/null; then
    NPM_VERSION=$(npm -v)
    print_ok "npm found: v$NPM_VERSION"
else
    print_error "npm not found"
fi

echo ""

# 3. Check npm Dependencies
echo "3. Checking npm Dependencies..."
if [ -d "node_modules" ]; then
    PACKAGE_COUNT=$(ls -1 node_modules 2>/dev/null | wc -l)
    if [ "$PACKAGE_COUNT" -gt 0 ]; then
        print_ok "node_modules exists ($PACKAGE_COUNT packages)"
    else
        print_warning "node_modules exists but appears empty"
        print_info "Run: npm install"
    fi
else
    print_warning "node_modules not found"
    print_info "Run: npm install"
fi

# Check package.json
if [ -f "package.json" ]; then
    print_ok "package.json found"
else
    print_error "package.json not found"
fi

echo ""

# 4. Check Gradle Wrapper
echo "4. Checking Gradle Wrapper..."
if [ -f "android/gradlew" ]; then
    print_ok "Gradle wrapper found"
    
    if [ -x "android/gradlew" ]; then
        print_ok "Gradle wrapper is executable"
    else
        print_warning "Gradle wrapper is not executable"
        print_info "Fix with: chmod +x android/gradlew"
    fi
    
    # Test Gradle
    cd android
    if ./gradlew --version > /dev/null 2>&1; then
        GRADLE_VERSION=$(./gradlew --version 2>/dev/null | grep "Gradle" | head -1)
        print_ok "Gradle wrapper works: $GRADLE_VERSION"
    else
        print_warning "Gradle wrapper test failed (may need Java/SDK)"
    fi
    cd ..
else
    print_error "Gradle wrapper not found at android/gradlew"
fi

echo ""

# 5. Check Android SDK
echo "5. Checking Android SDK..."
ANDROID_SDK_FOUND=false

# Check ANDROID_HOME
if [ -n "$ANDROID_HOME" ]; then
    if [ -d "$ANDROID_HOME" ]; then
        print_ok "ANDROID_HOME is set: $ANDROID_HOME"
        ANDROID_SDK_FOUND=true
        
        # Check for required SDK components
        if [ -d "$ANDROID_HOME/platform-tools" ]; then
            print_ok "SDK platform-tools found"
        else
            print_warning "SDK platform-tools not found"
        fi
        
        if [ -d "$ANDROID_HOME/platforms" ]; then
            PLATFORM_COUNT=$(ls -1 "$ANDROID_HOME/platforms" 2>/dev/null | wc -l)
            print_ok "SDK platforms found ($PLATFORM_COUNT installed)"
        else
            print_warning "SDK platforms directory not found"
        fi
    else
        print_error "ANDROID_HOME points to non-existent directory: $ANDROID_HOME"
    fi
else
    print_warning "ANDROID_HOME not set"
fi

# Check default location
if [ "$ANDROID_SDK_FOUND" = false ] && [ -d "$HOME/Android/Sdk" ]; then
    print_warning "Found Android SDK at default location: $HOME/Android/Sdk"
    print_info "Set with: export ANDROID_HOME=$HOME/Android/Sdk"
    ANDROID_SDK_FOUND=true
fi

# Check local.properties
if [ -f "android/local.properties" ]; then
    SDK_DIR=$(grep "sdk.dir" android/local.properties 2>/dev/null | cut -d'=' -f2)
    if [ -n "$SDK_DIR" ] && [ -d "$SDK_DIR" ]; then
        print_ok "local.properties found with SDK location: $SDK_DIR"
        ANDROID_SDK_FOUND=true
    else
        print_warning "local.properties exists but SDK path is invalid"
    fi
else
    print_warning "android/local.properties not found"
    if [ "$ANDROID_SDK_FOUND" = true ] && [ -n "$ANDROID_HOME" ]; then
        print_info "Create it with: echo 'sdk.dir=$ANDROID_HOME' > android/local.properties"
    fi
fi

if [ "$ANDROID_SDK_FOUND" = false ]; then
    print_error "Android SDK not found or not configured"
    print_info "Options:"
    print_info "  1. Install Android Studio (includes SDK)"
    print_info "  2. Install command-line tools only"
    print_info "  3. Download SDK manually"
fi

echo ""

# 6. Check Build Configuration
echo "6. Checking Build Configuration..."
if [ -f "android/app/build.gradle" ]; then
    print_ok "App build.gradle found"
    
    # Check version
    VERSION_NAME=$(grep "versionName" android/app/build.gradle 2>/dev/null | head -1 | sed 's/.*versionName "\(.*\)".*/\1/')
    if [ -n "$VERSION_NAME" ]; then
        print_ok "App version: $VERSION_NAME"
    fi
else
    print_error "App build.gradle not found"
fi

if [ -f "android/build.gradle" ]; then
    print_ok "Project build.gradle found"
else
    print_error "Project build.gradle not found"
fi

if [ -f "android/app/src/main/AndroidManifest.xml" ]; then
    print_ok "AndroidManifest.xml found"
else
    print_error "AndroidManifest.xml not found"
fi

echo ""

# 7. Check Disk Space
echo "7. Checking Disk Space..."
AVAILABLE_SPACE=$(df -BG . | tail -1 | awk '{print $4}' | sed 's/G//')
if [ "$AVAILABLE_SPACE" -gt 10 ]; then
    print_ok "Sufficient disk space available: ${AVAILABLE_SPACE}GB"
elif [ "$AVAILABLE_SPACE" -gt 5 ]; then
    print_warning "Low disk space: ${AVAILABLE_SPACE}GB (recommend 10GB+)"
else
    print_error "Very low disk space: ${AVAILABLE_SPACE}GB (need at least 5GB)"
fi

echo ""

# Summary
echo "=========================================="
echo "Summary"
echo "=========================================="

case $check_status in
    $STATUS_OK)
        echo -e "${GREEN}✓ All prerequisites met! Ready to build.${NC}"
        echo ""
        echo "Next step: Run ./build-apk-automated.sh"
        exit 0
        ;;
    $STATUS_WARNING)
        echo -e "${YELLOW}⚠ Some warnings found. Build may work but issues detected.${NC}"
        echo ""
        echo "Review warnings above and fix if needed."
        echo "You can try building anyway: ./build-apk-automated.sh"
        exit 1
        ;;
    $STATUS_ERROR)
        echo -e "${RED}✗ Critical errors found. Please fix before building.${NC}"
        echo ""
        echo "Fix the errors above and run this check again."
        exit 2
        ;;
esac

