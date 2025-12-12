# Server Setup for Android Debug APK Builds

This guide explains how to set up your server for building Android debug APK files.

## Overview

The server setup script (`setup-server-for-android.sh`) automatically installs and configures all prerequisites needed to build Android debug APK files on a Linux server.

## What Gets Installed

The setup script installs and configures:

1. **Java JDK 17** - Required for Android Gradle builds
2. **Node.js 18+** - Required for React Native Metro bundler
3. **Android SDK** - Command-line tools, platform SDK, and build tools
4. **npm Dependencies** - All React Native project dependencies
5. **Environment Variables** - JAVA_HOME, ANDROID_HOME, PATH configurations
6. **Project Configuration** - local.properties, Gradle wrapper permissions

## Quick Start

### Interactive Mode (Recommended for First-Time Setup)

```bash
cd /home/consult/apps/consult/mobile
./setup-server-for-android.sh
```

The script will:
- Check what's already installed
- Prompt you before installing new components
- Show progress for each step
- Verify the setup at the end

### Non-Interactive Mode (For CI/CD)

```bash
cd /home/consult/apps/consult/mobile
./setup-server-for-android.sh --yes
```

This mode automatically accepts all prompts and is suitable for automated environments.

## Prerequisites

The setup script requires:

- **Linux Server** - Ubuntu/Debian-based distribution recommended
- **sudo Access** - Required to install Java JDK
- **Internet Connection** - Required to download Android SDK and npm packages
- **Disk Space** - At least 5GB free (Android SDK is ~1GB)

## Detailed Setup Process

### Step 1: Java JDK 17 Installation

The script checks for Java installation:

- If Java 17+ JDK is found, it skips installation
- If Java is missing or outdated, it installs OpenJDK 17
- Automatically configures `JAVA_HOME` environment variable
- Adds Java to `PATH` in `~/.bashrc`

**Manual Installation (if needed):**
```bash
sudo apt update
sudo apt install -y openjdk-17-jdk
export JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64
export PATH=$JAVA_HOME/bin:$PATH
```

### Step 2: Node.js 18+ Installation

The script checks for Node.js:

- If Node.js 18+ is found, it skips installation
- If missing, it installs NVM (Node Version Manager) and Node.js 18
- Configures NVM in `~/.bashrc` for persistence

**Manual Installation (if needed):**
```bash
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash
source ~/.bashrc
nvm install 18
nvm use 18
nvm alias default 18
```

### Step 3: Android SDK Installation

The script installs Android SDK command-line tools:

- Downloads Android SDK command-line tools (~150MB)
- Installs required SDK components:
  - Platform tools (adb, etc.)
  - Android SDK Platform 34 (matches project requirements)
  - Build tools 34.0.0
- Configures `ANDROID_HOME` environment variable
- Creates/updates `android/local.properties` file

**Installation Location:** `$HOME/Android/Sdk`

**Time Required:** 5-10 minutes (depends on internet speed)

### Step 4: npm Dependencies

The script installs all React Native dependencies:

- Runs `npm install` in the mobile directory
- Installs all packages listed in `package.json`
- Creates `node_modules` directory

**Time Required:** 3-5 minutes (first time)

### Step 5: Project Configuration

The script configures project files:

- Creates/updates `android/local.properties` with SDK path
- Ensures Gradle wrapper (`gradlew`) is executable
- Verifies all configuration files are in place

### Step 6: Verification

The script runs final verification:

- Checks Java installation and version
- Checks Node.js installation and version
- Checks npm availability
- Verifies Android SDK installation
- Checks npm dependencies
- Verifies Gradle wrapper

## After Setup

### Reload Environment Variables

After running the setup script, reload your environment:

```bash
source ~/.bashrc
```

Or restart your terminal session.

### Build Debug APK

Once setup is complete, build the debug APK:

```bash
cd /home/consult/apps/consult/mobile
./build-apk-automated.sh
```

The debug APK will be generated at:
```
android/app/build/outputs/apk/debug/app-debug.apk
```

## Idempotency

The setup script is **idempotent** - it's safe to run multiple times:

- Checks for existing installations before installing
- Updates configuration only if needed
- Won't duplicate environment variable entries
- Can be run to verify or fix setup issues

## Troubleshooting

### Java Issues

**Problem:** "Java not found" or "javac not found"

**Solution:**
```bash
sudo apt update
sudo apt install -y openjdk-17-jdk
export JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64
export PATH=$JAVA_HOME/bin:$PATH
source ~/.bashrc
```

### Node.js Issues

**Problem:** "Node.js not found" or "version too old"

**Solution:**
```bash
# Install/update NVM
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash
source ~/.bashrc

# Install Node.js 18
nvm install 18
nvm use 18
nvm alias default 18
```

### Android SDK Issues

**Problem:** "SDK location not found" or "SDK components missing"

**Solution:**
```bash
# Re-run Android SDK installation
cd /home/consult/apps/consult/mobile
./install-android-sdk.sh

# Or manually set ANDROID_HOME
export ANDROID_HOME=$HOME/Android/Sdk
echo "export ANDROID_HOME=$HOME/Android/Sdk" >> ~/.bashrc
source ~/.bashrc
```

### Build Errors

**Problem:** Build fails with Gradle errors

**Solution:**
```bash
# Clean and rebuild
cd /home/consult/apps/consult/mobile/android
./gradlew clean
cd ..
./build-apk-automated.sh
```

### Permission Issues

**Problem:** "Permission denied: ./gradlew"

**Solution:**
```bash
chmod +x /home/consult/apps/consult/mobile/android/gradlew
```

## Environment Variables

The setup script adds these to `~/.bashrc`:

```bash
# Java Configuration
export JAVA_HOME="/usr/lib/jvm/java-17-openjdk-amd64"
export PATH="$JAVA_HOME/bin:$PATH"

# NVM Configuration (if installed)
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"

# Android SDK Configuration
export ANDROID_HOME="$HOME/Android/Sdk"
export PATH="$PATH:$ANDROID_HOME/cmdline-tools/latest/bin"
export PATH="$PATH:$ANDROID_HOME/platform-tools"
```

## File Locations

After setup, important files are located at:

- **Setup Script:** `mobile/setup-server-for-android.sh`
- **Build Script:** `mobile/build-apk-automated.sh`
- **Android SDK:** `$HOME/Android/Sdk`
- **Project Config:** `mobile/android/local.properties`
- **Gradle Wrapper:** `mobile/android/gradlew`
- **Debug APK Output:** `mobile/android/app/build/outputs/apk/debug/app-debug.apk`

## Verification

To verify your setup is complete, run:

```bash
cd /home/consult/apps/consult/mobile
./check-prerequisites.sh
```

This will check all prerequisites and show what's installed.

## Next Steps

After successful setup:

1. **Reload environment:** `source ~/.bashrc`
2. **Build debug APK:** `./build-apk-automated.sh`
3. **Locate APK:** Check `android/app/build/outputs/apk/debug/app-debug.apk`
4. **Install on device:** Copy APK to Android device or use `adb install`

## Support

If you encounter issues:

1. Check the troubleshooting section above
2. Review the script output for error messages
3. Verify all prerequisites are installed: `./check-prerequisites.sh`
4. Try running the setup script again (it's idempotent)

## Summary

The server setup process:

1. ✅ Installs Java JDK 17
2. ✅ Installs Node.js 18+
3. ✅ Installs Android SDK with required components
4. ✅ Configures all environment variables
5. ✅ Installs npm dependencies
6. ✅ Configures project files
7. ✅ Verifies setup

**Total Setup Time:** 10-20 minutes (depending on internet speed)

**Ready to build?** Run `./build-apk-automated.sh` after setup!



