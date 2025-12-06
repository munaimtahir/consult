# Quick APK Build Guide

## 🚀 Quick Start - Build Your APK in 5 Steps

To build the APK file, you need to install prerequisites first, then run the automated build script.

### Prerequisites Installation

#### 1. Install Java JDK 17

```bash
sudo apt update
sudo apt install -y openjdk-17-jdk
```

#### 2. Set JAVA_HOME

```bash
export JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64
export PATH=$JAVA_HOME/bin:$PATH
```

To make this permanent, add to `~/.bashrc`:
```bash
echo 'export JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64' >> ~/.bashrc
echo 'export PATH=$JAVA_HOME/bin:$PATH' >> ~/.bashrc
source ~/.bashrc
```

#### 3. Install Node.js 18+

**Option A: Using NVM (Recommended)**
```bash
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash
source ~/.bashrc
nvm install 18
nvm use 18
```

**Option B: Using NodeSource**
```bash
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install -y nodejs
```

Verify installation:
```bash
java -version  # Should show Java 17+
node -v        # Should show v18+
npm -v         # Should show npm version
```

### Build the APK

Once prerequisites are installed, simply run:

```bash
cd /home/munaim/apps/consult/mobile
./build-apk-automated.sh
```

The script will:
- ✅ Check all prerequisites
- ✅ Install npm dependencies automatically
- ✅ Build the debug APK
- ✅ Show you the APK location

### APK Location

After successful build, your APK will be at:
```
/home/munaim/apps/consult/mobile/android/app/build/outputs/apk/debug/app-debug.apk
```

### Install on Device

**Option 1: Using ADB**
```bash
adb install android/app/build/outputs/apk/debug/app-debug.apk
```

**Option 2: Manual Install**
- Copy the APK file to your Android device
- Open the APK file on your device
- Allow installation from unknown sources if prompted
- Install the app

## One-Command Setup (After Installing Prerequisites)

If you've already installed Java and Node.js, you can build immediately:

```bash
cd /home/munaim/apps/consult/mobile && ./build-apk-automated.sh
```

## Troubleshooting

### "Java not found"
- Install Java: `sudo apt install -y openjdk-17-jdk`
- Set JAVA_HOME: `export JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64`

### "Node.js not found"
- Install Node.js using one of the methods above

### "Permission denied: ./gradlew"
```bash
chmod +x android/gradlew
```

### "SDK location not found"
The build should work without Android SDK for debug builds. If it fails:
- Install Android Studio (it includes the SDK)
- Or create `android/local.properties` with: `sdk.dir=/path/to/android/sdk`

## What the Build Script Does

The automated build script (`build-apk-automated.sh`) performs these steps automatically:

1. ✅ Checks Java installation (JDK 17+)
2. ✅ Checks Node.js installation (18+)
3. ✅ Installs/updates npm dependencies
4. ✅ Verifies Gradle wrapper
5. ✅ Checks Android SDK (optional)
6. ✅ Builds the debug APK
7. ✅ Shows APK location and installation instructions

## Build Time

- First build: 5-15 minutes (downloads dependencies)
- Subsequent builds: 2-5 minutes

## Need Help?

If you encounter issues:
1. Check the error message - the script provides helpful hints
2. Verify all prerequisites are installed correctly
3. Check `BUILD_VERIFICATION.md` for detailed troubleshooting

