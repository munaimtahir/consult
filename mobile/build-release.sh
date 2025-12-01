#!/bin/bash
# Build Release APK/AAB for Hospital Consult Mobile App
# This script builds a signed release APK and Android App Bundle

set -e

echo "🔧 Building Hospital Consult Release APK & AAB..."
echo ""

# Navigate to android directory
cd android

# Clean previous builds
./gradlew clean

# Build release APK and AAB
./gradlew bundleRelease assembleRelease

# Go back to mobile root
cd ..

echo ""
echo "✅ Release builds completed successfully!"
echo ""
echo "📁 APK Location:"
echo "   android/app/build/outputs/apk/release/app-release.apk"
echo ""
echo "📁 AAB Location (for Play Store):"
echo "   android/app/build/outputs/bundle/release/app-release.aab"
echo ""
echo "📱 To install APK on a connected device:"
echo "   adb install android/app/build/outputs/apk/release/app-release.apk"
