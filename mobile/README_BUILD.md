# Build APK - Quick Reference

## Fastest Way to Get Your APK

1. **Install Java 17:**
   ```bash
   sudo apt update && sudo apt install -y openjdk-17-jdk
   export JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64
   ```

2. **Install Node.js 18:**
   ```bash
   curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash
   source ~/.bashrc && nvm install 18
   ```

3. **Build APK:**
   ```bash
   cd /home/munaim/apps/consult/mobile
   ./build-apk-automated.sh
   ```

## Files Created

✅ `build-apk-automated.sh` - Automated build script (checks everything, builds APK)
✅ `setup-and-build.sh` - Interactive setup script (installs prerequisites then builds)
✅ `BUILD_APK_NOW.md` - Simple step-by-step instructions
✅ `QUICK_BUILD_GUIDE.md` - Detailed build guide

## APK Location After Build

`android/app/build/outputs/apk/debug/app-debug.apk`

Run the build script and it will show you the exact path!
