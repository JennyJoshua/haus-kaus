# Building and testing

## What each stage means
| Stage | Gradle task (default) | What a pass proves |
|---|---|---|
| Project validation | script | Required files and module exist |
| Compilation | `:app:compileDebugSources` | Kotlin/Java and resources compile |
| Unit tests | `:app:testDebugUnitTest` | JVM tests passed |
| Debug APK | `:app:assembleDebug` | An installable debug APK was produced |
| Instrumented tests | **not run** | — |

The run summary shows each stage as PASSED, FAILED or NOT RUN. A stage that did not run is never shown as passed.

## Java and Gradle compatibility
Choose the JDK to match your Android Gradle Plugin (AGP) and Gradle versions. Do not pick the newest JDK blindly.
- AGP 8.0 and newer require JDK 17 or newer.
- AGP 7.x works with JDK 11 (7.0–7.4) — set `ANDROID_JAVA_VERSION=11`.
- Gradle can only run on JDK versions it knows; very new JDKs need a recent Gradle.
Always confirm against the official AGP release notes and the Gradle compatibility matrix for your versions. The default is 17 because most current native projects use AGP 8.x. The template never upgrades Gradle or AGP.

## Changing module or tasks
Set repository variables (see README) or fill the inputs when you press **Run workflow**. Examples:
- Module in a subfolder named `mobile`: `ANDROID_MODULE=mobile`.
- Flavor build: `ANDROID_APK_TASK=assembleFreeDebug`, and note the APK folder will differ (see below).

**Known limitation:** the APK is collected from `<module>/build/outputs/apk/debug/`. Flavor builds that output to `apk/<flavor>/debug/` need a one-line change to the path in `android-build.yml`.

## Instrumented tests
Tests under `src/androidTest` need an emulator or device. The template does not run them. Options when you need them: run them on your phone by hand, or add an emulator job (needs hardware acceleration on the runner, more minutes, and a separate workflow). Until then, treat instrumented-test status as **unknown**, not passed.

## Real-device testing is still required
A green build means the code compiles, unit tests pass and an APK exists. It does not prove permissions, connectivity, performance, screen layout or real-device behaviour. Install the APK and test.

## Where outputs go
- APK: artifact `android-debug-apk-run<N>`, kept `ARTIFACT_RETENTION_DAYS` days (default 7).
- On failure: artifact `android-diagnostics-run<N>` (logs and Gradle reports).
- Summary: top of the run page.
