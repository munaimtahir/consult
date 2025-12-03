#!/bin/bash

# Java Setup Script for VS Code/Cursor Java Language Server
# This script helps detect and configure Java for this project

echo "Java Setup Script"
echo "=================="
echo ""

# Check if Java is installed
if command -v java &> /dev/null; then
    echo "✓ Java found in PATH"
    java -version
    echo ""
    
    # Try to find JAVA_HOME
    JAVA_PATH=$(readlink -f $(which java) 2>/dev/null)
    if [ -n "$JAVA_PATH" ]; then
        # Remove /bin/java from path
        DETECTED_JAVA_HOME=$(dirname $(dirname "$JAVA_PATH"))
        echo "Detected Java installation at: $DETECTED_JAVA_HOME"
        
        # Check if it's a valid JDK (has javac)
        if [ -f "$DETECTED_JAVA_HOME/bin/javac" ]; then
            echo "✓ Valid JDK found (contains javac)"
            echo ""
            echo "To set JAVA_HOME, add this to your ~/.bashrc or ~/.zshrc:"
            echo "  export JAVA_HOME=$DETECTED_JAVA_HOME"
            echo "  export PATH=\$JAVA_HOME/bin:\$PATH"
            echo ""
            echo "Then run: source ~/.bashrc  # or source ~/.zshrc"
        else
            echo "⚠ Warning: This appears to be a JRE, not a JDK (javac not found)"
            echo "  For VS Code Java Language Server, you need a JDK."
        fi
    fi
else
    echo "✗ Java not found in PATH"
    echo ""
    echo "To install Java 17, run:"
    echo "  sudo apt update"
    echo "  sudo apt install -y openjdk-17-jdk"
    echo ""
fi

# Check common Java installation locations
echo ""
echo "Checking common Java installation locations:"
FOUND_JAVA=false

for JAVA_DIR in /usr/lib/jvm/java-*-openjdk* /usr/lib/jvm/default-java; do
    if [ -d "$JAVA_DIR" ] && [ -f "$JAVA_DIR/bin/java" ]; then
        echo "  ✓ Found: $JAVA_DIR"
        if [ -f "$JAVA_DIR/bin/javac" ]; then
            echo "    (JDK - contains javac)"
            FOUND_JAVA=true
        else
            echo "    (JRE only - no javac)"
        fi
    fi
done

if [ "$FOUND_JAVA" = false ]; then
    echo "  No Java installations found in common locations"
fi

# Check current JAVA_HOME
echo ""
if [ -n "$JAVA_HOME" ]; then
    echo "Current JAVA_HOME: $JAVA_HOME"
    if [ -f "$JAVA_HOME/bin/java" ]; then
        echo "✓ JAVA_HOME points to a valid Java installation"
        "$JAVA_HOME/bin/java" -version
    else
        echo "✗ JAVA_HOME is set but doesn't point to a valid Java installation"
    fi
else
    echo "JAVA_HOME is not currently set"
fi

echo ""
echo "For VS Code/Cursor configuration:"
echo "  The .vscode/settings.json file is configured to use JAVA_HOME"
echo "  Make sure JAVA_HOME is set before opening VS Code/Cursor"
echo ""


