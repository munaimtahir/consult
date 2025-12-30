# Building Android APK on Windows

Complete guide for building the Hospital Consult mobile app APK on Windows.

## Prerequisites

### 1. Java JDK 17+

**Check if installed:**
```powershell
java -version
```

**If not installed, install via:**

**Option A: Using winget (Recommended)**
```powershell
winget install Microsoft.OpenJDK.17
```

**Option B: Using Chocolatey**
```powershell
choco install openjdk17
```

**Option C: Manual Download**
- Download from [Eclipse Adoptium](https://adoptium.net/)
- Install and note the installation path

**Set JAVA_HOME:**
1. Open **System Properties** → **Environment Variables**
2. Under **System Variables**, click **New**
3. Variable name: `JAVA_HOME`
4. Variable value: `C:\Program Files\Java\jdk-17` (or your actual JDK path)
5. Click **OK**

**Add to PATH:**
1. In **System Variables**, find **Path** and click **Edit**
2. Click **New** and add: `%JAVA_HOME%\bin`
3. Click **OK** on all dialogs

**Verify:**
```powershell
java -version
javac -version
echo $env:JAVA_HOME
```

### 2. Node.js 18+

**Check if installed:**
```powershell
node -v
```

**If not installed:**
- Download from [nodejs.org](https://nodejs.org/)
- Install with default settings
- Verify: `node -v` and `npm -v`

### 3. Android SDK

You have two options:

#### Option A: Android Studio (Recommended - Full SDK)

1. Download from [developer.android.com/studio](https://developer.android.com/studio)
2. Install with default settings
3. SDK will be at: `C:\Users\<YourUsername>\AppData\Local\Android\Sdk`
4. Set `ANDROID_HOME` environment variable to SDK path

#### Option B: Command-Line Tools Only (Lightweight)

**Automated Installation:**
```powershell
cd mobile
.\install-android-sdk.ps1
```

**Manual Installation:**
1. Download command-line tools from [developer.android.com/studio#command-tools](https://developer.android.com/studio#command-tools)
2. Extract to `C:\Users\<YourUsername>\AppData\Local\Android\Sdk`
3. Install required components:
   ```powershell
   cd C:\Users\<YourUsername>\AppData\Local\Android\Sdk\cmdline-tools\latest\bin
   .\sdkmanager.bat --licenses
   .\sdkmanager.bat "platform-tools" "platforms;android-34" "build-tools;34.0.0"
   ```

**Set ANDROID_HOME:**
1. Open **System Properties** → **Environment Variables**
2. Under **System Variables**, click **New**
3. Variable name: `ANDROID_HOME`
4. Variable value: `C:\Users\<YourUsername>\AppData\Local\Android\Sdk`
5. Click **OK**

**Add to PATH:**
Add these to your PATH environment variable:
- `%ANDROID_HOME%\platform-tools`
- `%ANDROID_HOME%\tools`
- `%ANDROID_HOME%\cmdline-tools\latest\bin`

**Important:** Restart your terminal/PowerShell after setting environment variables.

## Quick Build

Once prerequisites are installed:

```powershell
cd mobile
.\build-apk-windows.ps1
```

The script will:
- ✅ Check all prerequisites automatically
- ✅ Install npm dependencies if needed
- ✅ Build the debug APK
- ✅ Show you the APK location

## Manual Build Steps

If you prefer to build manually:

### 1. Install Dependencies
```powershell
cd mobile
npm install
```

### 2. Verify Configuration

Check that `mobile/android/local.properties` exists with your SDK path:
```properties
sdk.dir=C:\\Users\\<YourUsername>\\AppData\\Local\\Android\\Sdk
```

### 3. Build APK
```powershell
cd mobile\android
.\gradlew.bat assembleDebug
```

### 4. Find Your APK

After successful build, your APK will be at:
```
mobile\android\app\build\outputs\apk\debug\app-debug.apk
```

## Installing the APK

### Option 1: Using ADB (Android Debug Bridge)

If you have ADB installed (comes with Android SDK):
```powershell
adb install mobile\android\app\build\outputs\apk\debug\app-debug.apk
```

### Option 2: Manual Install

1. Copy the APK file to your Android device
2. Open the APK file on your device
3. Allow installation from unknown sources if prompted
4. Install the app

## Troubleshooting

### "SDK location not found"

**Solution:**
1. Verify `ANDROID_HOME` is set: `echo $env:ANDROID_HOME`
2. Check `mobile/android/local.properties` exists with correct path
3. Update `local.properties` if SDK is in a different location:
   ```properties
   sdk.dir=C:\\Path\\To\\Your\\Android\\Sdk
   ```
   (Use double backslashes for Windows paths)

### "Java not found"

**Solution:**
1. Verify Java is installed: `java -version`
2. Set `JAVA_HOME` environment variable
3. Add `%JAVA_HOME%\bin` to PATH
4. Restart terminal/PowerShell

### "Gradle build failed"

**Common causes:**
1. **Missing Android SDK components:**
   ```powershell
   cd $env:ANDROID_HOME\cmdline-tools\latest\bin
   .\sdkmanager.bat "platform-tools" "platforms;android-34" "build-tools;34.0.0"
   ```

2. **Incorrect SDK path in local.properties:**
   - Check the path uses double backslashes: `C:\\Users\\...`
   - Verify the path actually exists

3. **Java version mismatch:**
   - Ensure Java 17+ is installed
   - Verify `JAVA_HOME` points to JDK (not JRE)

### "Permission denied"

**Solution:**
- Run PowerShell as Administrator if needed
- Check file permissions on `gradlew.bat`

### Build takes too long

**First build:**
- First build downloads Gradle and dependencies (5-15 minutes)
- Subsequent builds are faster (2-5 minutes)

**Speed up:**
- Ensure you have good internet connection
- Use Android Studio's SDK Manager to pre-download components

## Environment Variables Summary

Set these in System Environment Variables:

| Variable | Example Value |
|----------|---------------|
| `JAVA_HOME` | `C:\Program Files\Java\jdk-17` |
| `ANDROID_HOME` | `C:\Users\<YourUsername>\AppData\Local\Android\Sdk` |

Add to PATH:
- `%JAVA_HOME%\bin`
- `%ANDROID_HOME%\platform-tools`
- `%ANDROID_HOME%\tools`
- `%ANDROID_HOME%\cmdline-tools\latest\bin`

## Build Scripts

### Automated Build Script
- **File:** `mobile/build-apk-windows.ps1`
- **Usage:** `.\build-apk-windows.ps1`
- **Features:**
  - Checks all prerequisites
  - Installs dependencies automatically
  - Builds APK
  - Shows APK location

### SDK Installation Script
- **File:** `mobile/install-android-sdk.ps1`
- **Usage:** `.\install-android-sdk.ps1`
- **Features:**
  - Downloads Android SDK command-line tools
  - Installs required SDK components
  - Sets up environment variables

## Release Build

To build a release APK (signed for production):

1. **Generate a keystore:**
   ```powershell
   keytool -genkeypair -v -keystore consult-release-key.keystore -alias consultKeyAlias -keyalg RSA -keysize 2048 -validity 10000
   ```

2. **Configure signing in `mobile/android/gradle.properties`:**
   ```properties
   CONSULT_UPLOAD_STORE_FILE=consult-release-key.keystore
   CONSULT_UPLOAD_KEY_ALIAS=consultKeyAlias
   CONSULT_UPLOAD_STORE_PASSWORD=your_secure_password
   CONSULT_UPLOAD_KEY_PASSWORD=your_secure_password
   ```

3. **Build release APK:**
   ```powershell
   cd mobile\android
   .\gradlew.bat assembleRelease
   ```

Release APK will be at:
```
mobile\android\app\build\outputs\apk\release\app-release.apk
```

## Verification Checklist

Before building, verify:
- [ ] Java JDK 17+ installed and `JAVA_HOME` set
- [ ] Node.js 18+ installed
- [ ] Android SDK installed and `ANDROID_HOME` set
- [ ] `mobile/android/local.properties` exists with correct SDK path
- [ ] All npm dependencies installed (`npm install` completed)
- [ ] Environment variables set and terminal restarted

## Getting Help

If you encounter issues:
1. Check the error message carefully
2. Verify all prerequisites are installed correctly
3. Ensure environment variables are set
4. Try cleaning the build: `cd mobile\android && .\gradlew.bat clean`
5. Check `BUILD_ERROR_ANALYSIS.md` for common issues

## Next Steps

After successfully building the APK:
1. Test on a physical device or emulator
2. Verify app functionality (login, consults, etc.)
3. Build release APK when ready for production
4. Set up push notifications (Firebase) if needed

