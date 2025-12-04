#!/bin/bash
# One-command setup and build script
# This script helps set up prerequisites and then builds the APK

set -e

echo "=========================================="
echo "Hospital Consult - Setup & Build Script"
echo "=========================================="
echo ""

# Check if we're running as root (for installations)
if [ "$EUID" -eq 0 ]; then 
    echo "Please don't run this script as root/sudo."
    echo "Run as normal user, the script will prompt for sudo when needed."
    exit 1
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo "This script will help you:"
echo "  1. Check prerequisites (Java, Node.js)"
echo "  2. Install missing prerequisites (with your permission)"
echo "  3. Build the APK"
echo ""

read -p "Continue? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Aborted."
    exit 0
fi

# Check Java
echo ""
echo "Checking Java..."
if command -v java &> /dev/null; then
    JAVA_VERSION=$(java -version 2>&1 | head -n 1)
    echo -e "${GREEN}✓${NC} Java found: $JAVA_VERSION"
    
    # Check version
    JAVA_MAJOR=$(java -version 2>&1 | awk -F '"' '/version/ {print $2}' | cut -d'.' -f1)
    if [ "$JAVA_MAJOR" -lt 17 ]; then
        echo -e "${YELLOW}⚠${NC} Java version is $JAVA_MAJOR. Java 17+ recommended."
        read -p "Install Java 17? (y/n) " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            echo "Installing Java 17..."
            sudo apt update
            sudo apt install -y openjdk-17-jdk
            echo "Setting JAVA_HOME..."
            export JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64
            export PATH=$JAVA_HOME/bin:$PATH
        fi
    fi
else
    echo "Java not found."
    read -p "Install Java 17? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "Installing Java 17..."
        sudo apt update
        sudo apt install -y openjdk-17-jdk
        export JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64
        export PATH=$JAVA_HOME/bin:$PATH
        echo 'export JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64' >> ~/.bashrc
        echo 'export PATH=$JAVA_HOME/bin:$PATH' >> ~/.bashrc
        echo -e "${GREEN}✓${NC} Java installed. Please restart your terminal or run: source ~/.bashrc"
    else
        echo "Java is required. Please install manually and run again."
        exit 1
    fi
fi

# Check Node.js
echo ""
echo "Checking Node.js..."
if command -v node &> /dev/null; then
    NODE_VERSION=$(node -v)
    echo -e "${GREEN}✓${NC} Node.js found: $NODE_VERSION"
    
    NODE_MAJOR=$(node -v | cut -d'.' -f1 | sed 's/v//')
    if [ "$NODE_MAJOR" -lt 18 ]; then
        echo -e "${YELLOW}⚠${NC} Node.js version is old. Node.js 18+ recommended."
        echo "Please install Node.js 18+ manually using nvm or NodeSource."
    fi
else
    echo "Node.js not found."
    echo "Please install Node.js 18+ using one of these methods:"
    echo "  1. NVM: curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash"
    echo "  2. NodeSource: curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash - && sudo apt install -y nodejs"
    exit 1
fi

# Now run the automated build script
echo ""
echo "All prerequisites met! Starting build..."
echo ""
exec ./build-apk-automated.sh

