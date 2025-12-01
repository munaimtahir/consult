#!/bin/bash
# Build Debug APK for Hospital Consult Mobile App
# This script builds a debug APK that can be installed on Android devices/emulators

set -e

echo "🔧 Building Hospital Consult Debug APK..."
echo ""

# Navigate to android directory
cd android

# Build debug APK
./gradlew assembleDebug

# Go back to mobile root
cd ..

echo ""
echo "✅ Debug APK built successfully!"
echo ""
echo "📁 APK Location:"
echo "   android/app/build/outputs/apk/debug/app-debug.apk"
echo ""
echo "📱 To install on a connected device:"
echo "   adb install android/app/build/outputs/apk/debug/app-debug.apk"
