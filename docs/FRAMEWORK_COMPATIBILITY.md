# Framework compatibility

| Project type | Status | Notes |
|---|---|---|
| Native Android, Kotlin, Gradle | **Supported** (not yet run on a real project) | Default configuration |
| Native Android, Java, Gradle | **Supported** (not yet run on a real project) | Same tasks |
| Multi-module native projects | Supported if one module is the application module | Set `ANDROID_MODULE` |
| Flutter | **Not supported** | Detected via `pubspec.yaml`; workflow stops with an explanation |
| React Native | **Not supported** | Detected via `package.json`; needs Node.js and JS bundling |
| Kotlin Multiplatform with Android app | Untested | May work if the Android app module is Gradle-based |
| Other (Unity, Cordova, etc.) | Not covered | — |

Nothing here claims universal compatibility.

## Why Flutter and React Native are separate
Flutter needs the Flutter SDK (`flutter build apk`). React Native needs Node.js, dependency install and a JavaScript bundle before Gradle runs. Installing these in the native workflow would add large toolchains and minutes to every native build. A separate workflow file per framework is the right design when you need one.

## Starting points (untested, for a future workflow)
**Flutter:** `subosito/flutter-action` (pin to a commit SHA), then `flutter pub get`, `flutter test`, `flutter build apk --debug`; APK in `build/app/outputs/flutter-apk/`. Needs Java and the Android SDK steps from `android-build.yml`.
**React Native:** `actions/setup-node` (pin), `npm ci`, then `cd android && ./gradlew assembleDebug`; the debug build needs the Metro bundle step configured by your project.
Create these as new files (`flutter-build.yml`, `react-native-build.yml`) only when needed, and test them before relying on them.
