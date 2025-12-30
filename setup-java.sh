{
  // Java Language Server uses Cursor's built-in JRE on macOS.
  // No manual java.jdt.ls.java.home override needed.

  // Gradle and tools will also follow system/default JDK.
  // (If you want to pin SDKMAN Java later, we can add that.)

  "java.compile.nullAnalysis.mode": "automatic"
}
