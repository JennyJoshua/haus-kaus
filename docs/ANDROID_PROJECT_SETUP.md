# Android project setup

## Required layout
```
your-repo/
  gradlew
  gradle/wrapper/gradle-wrapper.jar
  gradle/wrapper/gradle-wrapper.properties
  settings.gradle(.kts)      # include(":app")
  build.gradle(.kts)
  app/build.gradle(.kts)     # applies com.android.application
  app/src/...
```
If your project lives in a subfolder, set `ANDROID_PROJECT_DIR` to it (that folder must contain `gradlew`).

## Checklist
1. The wrapper exists and is committed, including the JAR (`.gitignore` here keeps it).
2. `settings.gradle*` includes your application module.
3. The module applies the Android **application** plugin (not library).
4. `compileSdk`, `minSdk`, `targetSdk` are set; `namespace` is set (AGP 8+).
5. No `local.properties` committed (it holds your PC's SDK path).
6. Choose the JDK to match AGP (see `BUILDING_AND_TESTING.md`) and set `ANDROID_JAVA_VERSION` if not 17.
7. Dependencies come from public repositories (`google()`, `mavenCentral()`). Private repositories need credentials, which this template does not provide.

## Creating a new project without Android Studio
This template does not generate Android projects. Get the starting project from a source you trust (an official sample, an AI-generated project reviewed by you, or an existing repository), then upload it. The wrapper JAR is a binary file; verify it comes from a trusted source (the workflow also validates it).

## Variables
See README for the full table of repository variables.
