# Java Setup Guide

This project requires JDK 17 or higher for the Java Language Server and Android development.

## Quick Start

1. **Install JDK 17:**
   ```bash
   sudo apt update
   sudo apt install -y openjdk-17-jdk
   ```

2. **Set JAVA_HOME** (add to `~/.bashrc` or `~/.zshrc`):
   ```bash
   export JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64
   export PATH=$JAVA_HOME/bin:$PATH
   source ~/.bashrc  # or source ~/.zshrc
   ```

3. **Verify installation:**
   ```bash
   ./setup-java.sh  # Run the helper script
   java -version     # Should show Java 17+
   ```

4. **Restart VS Code/Cursor** for changes to take effect.

### Workspace Defaults

- The repo's `.vscode/settings.json` now pins `java.jdt.ls.java.home` and the Gradle tooling to `/usr/lib/jvm/java-21-openjdk-amd64`, which exists in the Cursor/Linux containers.
- On macOS or Windows, override that value locally (either by editing your global Cursor `settings.json` at `%APPDATA%/Cursor/User/settings.json` or by updating the workspace copy) so it points to your installed JDK directory.

---

## Detailed Instructions

## Installation Steps

### 1. Install JDK 17

Run the following command to install OpenJDK 17:

```bash
sudo apt update
sudo apt install -y openjdk-17-jdk
```

### 2. Verify Installation

After installation, verify Java is installed:

```bash
java -version
```

You should see output indicating Java 17 or higher.

### 3. Set JAVA_HOME Environment Variable

Find the Java installation path:

```bash
sudo update-alternatives --config java
```

Or find it manually:

```bash
readlink -f $(which java) | sed "s:bin/java::"
```

Then set JAVA_HOME in your shell profile (e.g., `~/.bashrc` or `~/.zshrc`):

```bash
export JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64
export PATH=$JAVA_HOME/bin:$PATH
```

**Note:** The exact path may vary. Common locations:
- `/usr/lib/jvm/java-17-openjdk-amd64`
- `/usr/lib/jvm/java-17-openjdk`
- `/usr/lib/jvm/default-java`

After adding to your profile, reload it:

```bash
source ~/.bashrc  # or source ~/.zshrc
```

### 4. Verify JAVA_HOME

```bash
echo $JAVA_HOME
java -version
```

### 5. Restart VS Code/Cursor

After setting JAVA_HOME, restart VS Code/Cursor for the changes to take effect.

## Alternative: Manual Configuration in VS Code/Cursor

If you prefer not to set JAVA_HOME globally, you can set it directly in the workspace settings:

1. Open `.vscode/settings.json` (already created in this project)
2. Replace `${env:JAVA_HOME}` with the actual path, for example:
   ```json
   {
     "java.jdt.ls.java.home": "/usr/lib/jvm/java-17-openjdk-amd64"
   }
   ```

## Troubleshooting

- **Java not found**: Make sure Java is installed and in your PATH
- **Wrong version**: Ensure JDK 17 or higher is installed (not just JRE)
- **JAVA_HOME not set**: Verify the environment variable is set correctly
- **VS Code/Cursor still shows error**: Restart the editor after setting JAVA_HOME

## For Android Development

The mobile Android app also requires Java. After setting up Java as above, the Gradle build should work correctly.


