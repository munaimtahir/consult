# Build Process Verification Guide

## Overview

This document provides a guide to verify that the Android build process is correctly configured and can generate APK files. The build scripts exist and are configured, but actual builds require proper Java/Gradle setup.

## Build Scripts Status

### Debug Build Script
- **File**: `mobile/build-debug.sh`
- **Purpose**: Builds a debug APK for testing
- **Output**: `android/app/build/outputs/apk/debug/app-debug.apk`
- **Status**: ✅ Script exists and is configured

### Release Build Script
- **File**: `mobile/build-release.sh`
- **Purpose**: Builds signed release APK and Android App Bundle
- **Output**: 
  - APK: `android/app/build/outputs/apk/release/app-release.apk`
  - AAB: `android/app/build/outputs/bundle/release/app-release.aab`
- **Status**: ✅ Script exists and is configured

## Prerequisites for Building

### Required Software

1. **Java Development Kit (JDK) 17**
   - Required for Android Gradle build
   - Setup guide available: `JAVA_SETUP.md`
   - Setup script available: `setup-java.sh`

2. **Android SDK**
   - Required for building Android apps
   - Usually installed via Android Studio
   - Must have Android SDK platforms and build tools

3. **Gradle**
   - Gradle wrapper included in project (`android/gradlew`)
   - No separate installation needed

4. **Node.js and npm**
   - Required for React Native Metro bundler
   - Should have Node.js 18+ installed

5. **React Native Dependencies**
   - Run `npm install` in `mobile/` directory

### Environment Variables

Verify the following environment variables are set:

```bash
# Java
export JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64  # Or your Java path
export PATH=$JAVA_HOME/bin:$PATH

# Android SDK (if not using Android Studio)
export ANDROID_HOME=$HOME/Android/Sdk
export PATH=$PATH:$ANDROID_HOME/platform-tools
export PATH=$PATH:$ANDROID_HOME/tools
```

## Build Configuration Files

### Gradle Configuration

1. **Project-level build.gradle**
   - Location: `mobile/android/build.gradle`
   - Status: ✅ Exists

2. **App-level build.gradle**
   - Location: `mobile/android/app/build.gradle`
   - Status: ✅ Exists and configured
   - Version: Synchronized with package.json (0.2.0)

3. **Gradle Properties**
   - Location: `mobile/android/gradle.properties`
   - Status: ✅ Exists

4. **Gradle Wrapper**
   - Location: `mobile/android/gradlew`
   - Status: ✅ Exists (verification needed)

### React Native Configuration

1. **package.json**
   - Location: `mobile/package.json`
   - Status: ✅ Configured with build scripts

2. **AndroidManifest.xml**
   - Location: `mobile/android/app/src/main/AndroidManifest.xml`
   - Status: ✅ Configured

3. **App Entry Point**
   - Location: `mobile/index.js`
   - Status: ✅ Configured

## Verification Steps

### Step 1: Verify Java Installation

```bash
java -version
# Should show Java 17 or higher

echo $JAVA_HOME
# Should show path to Java 17 installation
```

### Step 2: Verify Android SDK (Optional)

If Android SDK is installed separately:

```bash
echo $ANDROID_HOME
# Should show Android SDK path

$ANDROID_HOME/platform-tools/adb version
# Should show ADB version
```

### Step 3: Verify Node.js and Dependencies

```bash
cd mobile
node -v
# Should show Node.js 18 or higher

npm list react-native
# Should show React Native 0.74.0 installed
```

### Step 4: Verify Gradle Wrapper

```bash
cd mobile/android
./gradlew --version
# Should show Gradle version and Java version
```

If permission denied:
```bash
chmod +x gradlew
```

### Step 5: Check Build Script Permissions

```bash
cd mobile
ls -l build-debug.sh build-release.sh
# Should show executable permissions

# If not executable:
chmod +x build-debug.sh build-release.sh
```

### Step 6: Verify Signing Configuration (Release Build)

For release builds, check that signing is configured:

```bash
cd mobile/android
cat gradle.properties | grep CONSULT_UPLOAD
# Should show signing configuration (may be empty for debug)
```

**Note**: Release builds require signing configuration in `gradle.properties`. If not configured, the build will fail. See `MOBILE_DEV.md` for setup instructions.

## Building the APK

### Debug Build

**Quick Test (Dry Run)**:
```bash
cd mobile/android
./gradlew tasks
# Lists all available Gradle tasks
```

**Actual Build** (requires full setup):
```bash
cd mobile
./build-debug.sh
```

**Manual Build**:
```bash
cd mobile/android
./gradlew assembleDebug
```

**Expected Output**:
- APK file: `mobile/android/app/build/outputs/apk/debug/app-debug.apk`
- File size: ~15-30 MB (approximate)

### Release Build

**Prerequisites**:
1. Signing configuration in `android/gradle.properties`
2. Release keystore file
3. Keystore passwords configured

**Build Command**:
```bash
cd mobile
./build-release.sh
```

**Manual Build**:
```bash
cd mobile/android
./gradlew clean
./gradlew bundleRelease assembleRelease
```

**Expected Output**:
- APK: `mobile/android/app/build/outputs/apk/release/app-release.apk`
- AAB: `mobile/android/app/build/outputs/bundle/release/app-release.aab`

## Common Build Issues

### Issue 1: Java Version Mismatch

**Error**: "Unsupported class file major version"

**Solution**:
- Verify Java version: `java -version`
- Ensure JAVA_HOME points to JDK 17
- Restart terminal/IDE after setting JAVA_HOME

### Issue 2: Gradle Wrapper Permission Denied

**Error**: "Permission denied: ./gradlew"

**Solution**:
```bash
cd mobile/android
chmod +x gradlew
```

### Issue 3: Android SDK Not Found

**Error**: "SDK location not found"

**Solution**:
- Install Android Studio (recommended)
- Or set ANDROID_HOME environment variable
- Create `local.properties` in `android/` directory:
  ```
  sdk.dir=/path/to/android/sdk
  ```

### Issue 4: Missing Dependencies

**Error**: "Could not find or load main class"

**Solution**:
```bash
cd mobile
rm -rf node_modules
npm install

cd android
./gradlew clean
```

### Issue 5: Metro Bundler Not Running

**Error**: "Unable to load script"

**Solution**:
- Start Metro bundler before building:
  ```bash
  cd mobile
  npm start
  ```
- Or ensure bundle is included in APK (automatic for release builds)

### Issue 6: Signing Configuration Missing

**Error**: "Keystore file not found"

**Solution**:
- For debug builds: Uses default debug keystore (auto-generated)
- For release builds: Configure signing in `gradle.properties` or generate keystore (see `MOBILE_DEV.md`)

## Build Verification Checklist

### Pre-Build Checks
- [ ] Java JDK 17+ installed and JAVA_HOME set
- [ ] Node.js 18+ installed
- [ ] npm dependencies installed (`npm install` in mobile/)
- [ ] Gradle wrapper exists and is executable
- [ ] Build scripts are executable
- [ ] Android SDK accessible (if building without Android Studio)

### Debug Build Checks
- [ ] Debug build script runs without errors
- [ ] APK file is generated at expected location
- [ ] APK file size is reasonable (15-30 MB)
- [ ] APK can be installed on device/emulator

### Release Build Checks
- [ ] Release keystore configured (for release builds)
- [ ] Signing configuration in gradle.properties
- [ ] Release APK generated successfully
- [ ] Release AAB generated successfully
- [ ] APK is signed correctly

### Post-Build Checks
- [ ] APK installs on Android device/emulator
- [ ] App launches successfully
- [ ] App connects to backend API
- [ ] Authentication works
- [ ] Core features functional

## Automated Build Verification

### CI/CD Integration

For continuous integration, use these commands:

```bash
# Setup
cd mobile
npm install

# Build verification (without full build)
cd android
./gradlew tasks --all > /dev/null && echo "Gradle configuration valid" || echo "Gradle configuration error"

# Full build (in CI environment)
./build-debug.sh
```

### Build Validation Script

Create a validation script to check build readiness:

```bash
#!/bin/bash
# build-check.sh - Validate build configuration

echo "Checking build configuration..."

# Check Java
if command -v java &> /dev/null; then
    echo "✅ Java found: $(java -version 2>&1 | head -n 1)"
else
    echo "❌ Java not found"
    exit 1
fi

# Check Node.js
if command -v node &> /dev/null; then
    echo "✅ Node.js found: $(node -v)"
else
    echo "❌ Node.js not found"
    exit 1
fi

# Check Gradle wrapper
if [ -f "android/gradlew" ]; then
    echo "✅ Gradle wrapper exists"
else
    echo "❌ Gradle wrapper not found"
    exit 1
fi

# Check build scripts
if [ -f "build-debug.sh" ] && [ -f "build-release.sh" ]; then
    echo "✅ Build scripts exist"
else
    echo "❌ Build scripts missing"
    exit 1
fi

echo ""
echo "✅ All build prerequisites met!"
```

## Next Steps

After verifying build configuration:

1. **Test Debug Build**
   - Run `./build-debug.sh`
   - Install APK on test device
   - Verify app functionality

2. **Prepare Release Build**
   - Generate release keystore (if not done)
   - Configure signing in `gradle.properties`
   - Test release build process

3. **Document Build Process**
   - Document any environment-specific setup
   - Create CI/CD build pipeline
   - Set up automated testing

4. **Production Deployment**
   - Test release AAB on Google Play Console
   - Verify app signing
   - Prepare for app store submission

## Additional Resources

- **Java Setup**: See `JAVA_SETUP.md`
- **Mobile Development Guide**: See `mobile/MOBILE_DEV.md`
- **React Native Docs**: https://reactnative.dev/docs/signed-apk-android
- **Android Build Guide**: https://developer.android.com/studio/build

## Summary

**Build Scripts Status**: ✅ Configured and ready
**Configuration Files**: ✅ All present and configured
**Build Verification**: ⚠️ Requires Java/Gradle setup to test
**Recommendation**: Set up Java 17 and test build process when ready to build APKs

The build infrastructure is in place and appears correctly configured. Actual builds require:
- Java JDK 17 installation
- React Native dependencies (`npm install`)
- Optional: Android SDK (for testing)

Once these prerequisites are met, the build scripts should work correctly to generate APK files.


