# 🚀 Build APK Now - Simple Instructions

## You Need These First (One-Time Setup)

### Step 1: Install Java 17

Run these commands in your terminal:

```bash
sudo apt update
sudo apt install -y openjdk-17-jdk
```

Then set JAVA_HOME (add to ~/.bashrc to make permanent):

```bash
export JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64
export PATH=$JAVA_HOME/bin:$PATH
```

Add to ~/.bashrc:
```bash
echo 'export JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64' >> ~/.bashrc
echo 'export PATH=$JAVA_HOME/bin:$PATH' >> ~/.bashrc
source ~/.bashrc
```

### Step 2: Install Node.js 18+

**Easy way (using NVM):**
```bash
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash
source ~/.bashrc
nvm install 18
nvm use 18
```

**Or using package manager:**
```bash
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install -y nodejs
```

### Step 3: Verify Installation

```bash
java -version   # Should show Java 17+
node -v         # Should show v18+
npm -v          # Should show npm version
```

## Build Your APK

Once Java and Node.js are installed, run:

```bash
cd /home/munaim/apps/consult/mobile
./build-apk-automated.sh
```

That's it! The script will:
- Check everything automatically
- Install dependencies
- Build your APK
- Show you where it is

## Your APK Will Be Here

After build completes:
```
/home/munaim/apps/consult/mobile/android/app/build/outputs/apk/debug/app-debug.apk
```

## Install on Your Phone

1. Copy the APK file to your Android phone
2. Open the APK file on your phone
3. Allow installation from unknown sources
4. Install!

Or use ADB (if you have it):
```bash
adb install android/app/build/outputs/apk/debug/app-debug.apk
```

## Quick Start (If Prerequisites Already Installed)

```bash
cd /home/munaim/apps/consult/mobile
./build-apk-automated.sh
```

## Need Help?

- Check `QUICK_BUILD_GUIDE.md` for detailed instructions
- Check `BUILD_VERIFICATION.md` for troubleshooting
- The build script will show helpful error messages if something is missing

---

**Time Required:**
- Installing prerequisites: 5-10 minutes (one-time)
- Building APK: 5-15 minutes (first time), 2-5 minutes (after that)

