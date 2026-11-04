# Android GitHub Actions template

Build and test native Android apps on GitHub's cloud runners and download the debug APK to your phone. No Android Studio needed.

**Status:** workflows pass actionlint, shellcheck and YAML checks, and the helper scripts were tested against mock projects. **No real Android build has been run yet** (see `tests/workflow-validation.md`). Run the first-build checklist before trusting it.

## What it does
1. Checks the repository is a Gradle Android project (clear errors if not).
2. Sets up Java, the Android SDK and Gradle caching.
3. Validates the Gradle wrapper, compiles, runs unit tests, builds a debug APK.
4. Uploads the APK as an Actions artifact (`android-debug-apk-run<N>`).
5. On failure, writes a classified summary and uploads logs and reports.

## Quick start (phone)
1. Tap **Use this template** → **Create a new repository** (see `docs/PHONE_WORKFLOW.md`).
2. Upload your Android project to the repository root (`gradlew`, `gradle/`, `settings.gradle*`, `build.gradle*`, `app/`).
3. Open **Actions → Android build and test → Run workflow**.
4. When it finishes, open the run, scroll to **Artifacts**, download, unzip, install.

## Scope
- Supported: native Gradle Android projects (Kotlin or Java).
- Detected and stopped with an explanation: Flutter, React Native. See `docs/FRAMEWORK_COMPATIBILITY.md`.
- Not run: instrumented (emulator) tests. Not included: Play Store publishing.

## Configuration (repository variables, optional)
Settings → Secrets and variables → Actions → Variables.

| Variable | Default | Meaning |
|---|---|---|
| `ANDROID_MODULE` | `app` | Application module |
| `ANDROID_PROJECT_DIR` | `.` | Folder containing `gradlew` |
| `ANDROID_JAVA_VERSION` | `17` | JDK (Temurin) |
| `ANDROID_COMPILE_TASK` | `compileDebugSources` | Compile task |
| `ANDROID_TEST_TASK` | `testDebugUnitTest` | Unit-test task |
| `ANDROID_APK_TASK` | `assembleDebug` | APK task |
| `ANDROID_RUN_TESTS` | `true` | Set `false` to skip unit tests |
| `ARTIFACT_RETENTION_DAYS` | `7` | Artifact retention |

## ZIP inbox (optional)
Upload a ZIP to `_inbox/` and the **Process ZIP inbox** workflow extracts it into the repository after safety checks. See `docs/ZIP_INBOX_OPERATIONS.md`.

The Android build workflow is skipped inside the template repository itself (it has no Android project). Repositories created from the template build normally.

Docs index: `docs/`. Billing facts: `docs/FREE_USAGE_AND_BILLING.md`.
