# 📱 Build Android APK - Complete Instructions

## ✅ What I've Prepared For You

I've created automated build scripts and comprehensive documentation. Here's everything that's ready:

### Build Scripts Created

1. **`mobile/build-apk-automated.sh`** ⭐ **USE THIS ONE**
   - Fully automated build script
   - Checks all prerequisites
   - Installs dependencies automatically
   - Builds the APK
   - Shows you exactly where the APK is

2. **`mobile/setup-and-build.sh`**
   - Interactive script that helps install prerequisites
   - Then runs the automated build

### Documentation Created

1. **`mobile/BUILD_APK_NOW.md`** - Simple 3-step instructions
2. **`mobile/QUICK_BUILD_GUIDE.md`** - Detailed guide
3. **`mobile/README_BUILD.md`** - Quick reference

## 🚀 How to Get Your APK (3 Steps)

### Step 1: Install Prerequisites

You need Java 17 and Node.js 18+ installed. Run these commands:

```bash
# Install Java 17
sudo apt update
sudo apt install -y openjdk-17-jdk
export JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64
export PATH=$JAVA_HOME/bin:$PATH

# Add to ~/.bashrc (make permanent)
echo 'export JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64' >> ~/.bashrc
echo 'export PATH=$JAVA_HOME/bin:$PATH' >> ~/.bashrc
source ~/.bashrc

# Install Node.js 18 (using NVM - recommended)
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash
source ~/.bashrc
nvm install 18
nvm use 18

# Verify installations
java -version  # Should show Java 17+
node -v        # Should show v18+
npm -v         # Should show npm version
```

### Step 2: Run the Build Script

Once prerequisites are installed:

```bash
cd /home/munaim/apps/consult/mobile
./build-apk-automated.sh
```

The script will automatically:
- ✅ Check Java and Node.js
- ✅ Install npm dependencies
- ✅ Verify Gradle setup
- ✅ Build the debug APK
- ✅ Show you the APK location

### Step 3: Get Your APK

After the build completes, your APK will be at:

```
/home/munaim/apps/consult/mobile/android/app/build/outputs/apk/debug/app-debug.apk
```

The script will show you the exact path and installation instructions.

## 📋 What the Build Script Does

The automated build script (`build-apk-automated.sh`) performs these checks and steps:

1. ✅ **Checks Java Installation**
   - Verifies Java 17+ is installed
   - Checks for JDK (not just JRE)
   - Verifies JAVA_HOME is set

2. ✅ **Checks Node.js Installation**
   - Verifies Node.js 18+ is installed
   - Checks npm is available

3. ✅ **Installs Dependencies**
   - Runs `npm install` in mobile directory
   - Installs all React Native dependencies

4. ✅ **Verifies Gradle**
   - Checks Gradle wrapper exists
   - Makes it executable if needed
   - Tests Gradle configuration

5. ✅ **Builds the APK**
   - Runs `./gradlew assembleDebug`
   - Creates debug APK file
   - Shows success message with APK location

## ⏱️ Time Estimates

- **Prerequisites Installation:** 5-10 minutes (one-time)
- **First Build:** 5-15 minutes (downloads dependencies)
- **Subsequent Builds:** 2-5 minutes

## 🔧 Troubleshooting

### "Java not found"
```bash
sudo apt install -y openjdk-17-jdk
export JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64
```

### "Node.js not found"
```bash
# Using NVM (recommended)
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash
source ~/.bashrc
nvm install 18
```

### "Permission denied: ./gradlew"
```bash
cd mobile/android
chmod +x gradlew
```

### Build Errors
- Check the error message - the script provides helpful hints
- Make sure all prerequisites are installed correctly
- Try cleaning the build: `cd mobile/android && ./gradlew clean`

## 📱 Installing the APK

### Option 1: Copy to Phone
1. Copy `app-debug.apk` to your Android phone
2. Open the file on your phone
3. Allow installation from unknown sources
4. Install

### Option 2: Using ADB
```bash
adb install /home/munaim/apps/consult/mobile/android/app/build/outputs/apk/debug/app-debug.apk
```

## 📁 All Files Created

### Build Scripts
- ✅ `mobile/build-apk-automated.sh` - Main automated build script
- ✅ `mobile/setup-and-build.sh` - Interactive setup script
- ✅ `mobile/build-debug.sh` - Original debug build script
- ✅ `mobile/build-release.sh` - Release build script

### Documentation
- ✅ `mobile/BUILD_APK_NOW.md` - Simple instructions
- ✅ `mobile/QUICK_BUILD_GUIDE.md` - Detailed guide
- ✅ `mobile/BUILD_VERIFICATION.md` - Build verification guide
- ✅ `mobile/README_BUILD.md` - Quick reference

### Status Documents
- ✅ `ANDROID_APP_STATUS.md` - Complete status review
- ✅ `mobile/PUSH_NOTIFICATIONS_SETUP.md` - Push notifications guide
- ✅ `mobile/TOKEN_REFRESH_IMPLEMENTATION.md` - Token refresh guide

## 🎯 Quick Start (TL;DR)

If you just want the APK quickly:

```bash
# 1. Install Java 17
sudo apt update && sudo apt install -y openjdk-17-jdk
export JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64

# 2. Install Node.js 18
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash
source ~/.bashrc && nvm install 18

# 3. Build APK
cd /home/munaim/apps/consult/mobile
./build-apk-automated.sh
```

That's it! Your APK will be ready in 10-15 minutes.

## 📞 Next Steps

1. **Install Prerequisites** (if not already installed)
2. **Run the Build Script:** `./build-apk-automated.sh`
3. **Find Your APK:** The script will show you the exact location
4. **Install on Phone:** Copy APK to your device and install

## ✨ What's Already Done

- ✅ Version mismatch resolved (package.json ↔ build.gradle)
- ✅ All build scripts created and configured
- ✅ Comprehensive documentation
- ✅ Automated build verification
- ✅ Complete Android app status review
- ✅ Push notifications setup guide
- ✅ Token refresh implementation guide

Everything is ready - you just need to install the prerequisites and run the build script!

---

**Ready to build? Run:**
```bash
cd /home/munaim/apps/consult/mobile && ./build-apk-automated.sh
```

