# Java/JDK Setup for Windows

This project requires **JDK 17 or higher** for Android development and Java Language Server support in VS Code/Cursor.

## Quick Installation Guide

### Option 1: Install using Chocolatey (Recommended)

If you have Chocolatey installed:

```powershell
choco install openjdk17
```

Or for JDK 21 (LTS):

```powershell
choco install openjdk21
```

### Option 2: Manual Installation

1. **Download JDK 17 or higher:**
   - **Eclipse Adoptium (Recommended):** https://adoptium.net/temurin/releases/
   - **Microsoft Build of OpenJDK:** https://www.microsoft.com/openjdk
   - **Oracle JDK:** https://www.oracle.com/java/technologies/downloads/

2. **Install the JDK:**
   - Run the installer
   - Note the installation path (usually `C:\Program Files\Java\jdk-17` or similar)

3. **Set JAVA_HOME Environment Variable:**
   - Open **System Properties** → **Environment Variables**
   - Under **System Variables**, click **New**
   - Variable name: `JAVA_HOME`
   - Variable value: `C:\Program Files\Java\jdk-17` (or your actual JDK path)
   - Click **OK**

4. **Add Java to PATH:**
   - In **System Variables**, find **Path** and click **Edit**
   - Click **New** and add: `%JAVA_HOME%\bin`
   - Click **OK** on all dialogs

5. **Verify Installation:**
   Open a new PowerShell window and run:
   ```powershell
   java -version
   javac -version
   echo $env:JAVA_HOME
   ```

### Option 3: Install using winget (Windows Package Manager)

```powershell
winget install Microsoft.OpenJDK.17
```

Or for JDK 21:

```powershell
winget install Microsoft.OpenJDK.21
```

## Configure VS Code/Cursor

After installing JDK, update `.vscode/settings.json`:

1. Find your JDK installation path (common locations):
   - `C:\Program Files\Java\jdk-17`
   - `C:\Program Files\Eclipse Adoptium\jdk-17.0.x-hotspot`
   - `C:\Program Files\Microsoft\jdk-17.0.x`

2. Open `.vscode/settings.json` in this project

3. Update the `java.configuration.runtimes` path to match your installation:

   ```json
   {
     "java.configuration.runtimes": [
       {
         "name": "JavaSE-17",
         "path": "C:\\Program Files\\Java\\jdk-17",  // Update this path
         "default": true
       }
     ]
   }
   ```

4. **Restart VS Code/Cursor** for changes to take effect

## Verify Configuration

1. Open any Java file in the project (or the Android Gradle files)
2. Check the bottom-right status bar - it should show the Java version
3. The Java Language Server should start automatically

## Troubleshooting

### Java not found after installation
- Make sure you **restarted your terminal/PowerShell** after setting environment variables
- Verify JAVA_HOME is set: `echo $env:JAVA_HOME` in PowerShell
- Check PATH includes: `%JAVA_HOME%\bin`

### VS Code/Cursor still shows error
- **Reload the window**: Press `Ctrl+Shift+P` → "Developer: Reload Window"
- Check that the path in `settings.json` matches your actual JDK installation
- Verify the path uses double backslashes (`\\`) in JSON

### Wrong Java version
- Make sure you installed JDK (not just JRE)
- Verify version: `java -version` should show 17 or higher
- Update `settings.json` to point to the correct JDK version

## For Android Development

The Android build also requires Java. After setting up Java as above:
- The Gradle build should work correctly
- You can build the Android app using the scripts in `mobile/` directory

