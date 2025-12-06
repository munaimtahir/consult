# Installation Scripts Guide

## Quick Start

To set up everything needed for building the Android APK:

```bash
cd /home/munaim/apps/consult/mobile
./setup-all-prerequisites.sh
```

This single command will:
- ✅ Check/Install Java JDK 17
- ✅ Check/Install Node.js 18+
- ✅ Install Android SDK
- ✅ Configure all environment variables
- ✅ Set up project configuration

## Individual Scripts

### 1. Complete Setup (Recommended)
**File:** `setup-all-prerequisites.sh`

Sets up everything in one go:
```bash
./setup-all-prerequisites.sh
```

### 2. Android SDK Installation Only
**File:** `install-android-sdk.sh`

Installs Android SDK command-line tools:
```bash
./install-android-sdk.sh
```

This script:
- Downloads Android SDK command-line tools
- Installs platform-tools, SDK platform, and build-tools
- Configures ANDROID_HOME environment variable
- Creates local.properties file
- Accepts all licenses automatically

### 3. Prerequisites Check
**File:** `check-prerequisites.sh`

Checks what's installed and what's missing:
```bash
./check-prerequisites.sh
```

### 4. Automated Build
**File:** `build-apk-automated.sh`

Builds the APK after prerequisites are met:
```bash
./build-apk-automated.sh
```

## What Gets Installed

### Android SDK Installation Includes:
- **Platform Tools** (adb, fastboot, etc.)
- **SDK Platform** (android-33 or android-34)
- **Build Tools** (33.0.0 or latest)
- Total size: ~1-2 GB

### Environment Variables Set:
- `ANDROID_HOME` - Points to Android SDK directory
- `JAVA_HOME` - Points to Java JDK 17 installation
- `PATH` - Updated to include Android SDK tools

### Files Created:
- `android/local.properties` - SDK location for Gradle
- Updated `~/.bashrc` - Environment variables

## Installation Time

- **Complete setup:** 15-45 minutes (depending on internet speed)
- **Android SDK only:** 10-30 minutes
- **Quick check:** 30 seconds

## After Installation

1. **Reload environment:**
   ```bash
   source ~/.bashrc
   ```

2. **Verify installation:**
   ```bash
   ./check-prerequisites.sh
   ```

3. **Build APK:**
   ```bash
   ./build-apk-automated.sh
   ```

## Troubleshooting

### Installation Fails

**Check internet connection:**
- Android SDK download requires stable internet
- File size: ~200 MB for command-line tools

**Check disk space:**
- Need at least 5 GB free space
- SDK installation uses ~1-2 GB

**Check permissions:**
- Scripts need execute permission: `chmod +x *.sh`
- Some operations may need sudo (for Java installation)

### SDK Installation Issues

**Download fails:**
- Check internet connection
- Try again (downloads are resumable)
- Manual download link is in the script

**Extraction fails:**
- Check disk space
- Ensure unzip is installed: `sudo apt install unzip`

**License acceptance fails:**
- Run manually: `sdkmanager --licenses`
- Accept each license with 'y'

## Manual Installation

If scripts don't work, see:
- `BUILD_ERROR_ANALYSIS.md` - Detailed error solutions
- `PREREQUISITES_STATUS.md` - Status report format

## Script Locations

All scripts are in `/home/munaim/apps/consult/mobile/`:

- `setup-all-prerequisites.sh` - Complete setup
- `install-android-sdk.sh` - SDK installation
- `check-prerequisites.sh` - Prerequisites check
- `build-apk-automated.sh` - APK build
- `setup-and-build.sh` - Interactive setup

## Next Steps

Once installation is complete:
1. ✅ Run `source ~/.bashrc` to load environment
2. ✅ Run `./check-prerequisites.sh` to verify
3. ✅ Run `./build-apk-automated.sh` to build APK

Your APK will be at:
`android/app/build/outputs/apk/debug/app-debug.apk`

