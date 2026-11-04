# Debugging guide

## 1. Find the failed run
Repository → **Actions** → pick **Android build and test** → the run with a red ✗.

## 2. Open the failed job and find the first error
Tap the job **Build, test, package debug APK**. Open the step with the red ✗. Read the **first** error, not the last. Gradle usually prints a `* What went wrong:` block. Later errors are often side effects. The run summary (top of the run page) shows the stage, a category and the first error lines.

## 3. Failure categories
| Category (shown in summary) | Typical cause | First fix to try |
|---|---|---|
| Missing or invalid Android project files | Upload skipped `gradlew`, `gradle/wrapper/`, or the module | Upload the missing file named in the error |
| Invalid Gradle wrapper | Corrupted or modified `gradle-wrapper.jar` | Re-create the wrapper from a trusted Gradle download |
| Java/Gradle incompatibility | JDK too old/new for AGP or Gradle | Change `ANDROID_JAVA_VERSION` |
| Android SDK configuration error | `compileSdk` platform or build-tools not available, licences | Check `compileSdk`; confirm network was available |
| Dependency resolution failure | Typo in coordinates, repository missing, outage | Check the dependency line; re-run once |
| Kotlin compilation failure | Lines beginning `e: file:///…` | Fix the cited file and line |
| Java compilation failure | `error: cannot find symbol` etc. | Fix the cited file and line |
| Resource-processing failure | Bad XML, missing drawable, wrong `@string/` | Fix the cited resource |
| Unit-test failure | Failing test | Download diagnostics, open `build/reports/tests` |
| APK-generation failure | Packaging, lint or signing config | Read the `Execution failed for task` line |
| Wrong module or task name | Variable points to something that does not exist | Fix `ANDROID_MODULE` or task variables |
| Artifact-upload failure | APK path differs (flavors) or quota reached | Check path; see FREE_USAGE_AND_BILLING.md |

The classifier is keyword-based. It can be wrong; "Unclassified" means read the log yourself.

## 4. Download diagnostics
Open the run page → **Artifacts** → `android-diagnostics-run<N>` → download and unzip. Contains `ci-logs/*.log`, `diagnostics-summary.md` and Gradle reports. On a phone, use your browser (desktop-site mode if Artifacts is hidden).

## 5. Send it to ChatGPT or Claude
Paste: (a) the run summary text, (b) the first 30–50 lines around the first error, (c) the file the error names. Do not paste secrets or whole multi-megabyte logs. Say what you changed last.

## 6. Apply the fix and re-run
Edit or upload the corrected file (GitHub: file → pencil icon → commit). A push to `main` or a pull request starts a new run, or use **Run workflow**. Repeat until green.

## 7. After green
Install the APK and test on the phone. A green run does not prove the app works on a real device.
