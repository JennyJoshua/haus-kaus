#!/usr/bin/env bash
# Validates that the checked-out repository is a buildable Gradle Android project.
# Inputs (environment): PROJECT_DIR (default "."), MODULE (default "app"); optional COMPILE_TASK,
# TEST_TASK, APK_TASK, JAVA_VERSION are checked for unsafe characters only.
# Exit codes: 0 ok, 2 missing/invalid project files, 3 unsupported framework, 4 bad input.
set -euo pipefail

PROJECT_DIR="${PROJECT_DIR:-.}"
MODULE="${MODULE:-app}"

err() { echo "::error title=Android project check failed::$*"; echo "ERROR: $*" >&2; }

# Reject anything unusual in values that end up in shell commands or paths.
for pair in "PROJECT_DIR=$PROJECT_DIR" "MODULE=$MODULE" "COMPILE_TASK=${COMPILE_TASK:-x}" "TEST_TASK=${TEST_TASK:-x}" "APK_TASK=${APK_TASK:-x}" "JAVA_VERSION=${JAVA_VERSION:-17}"; do
  v="${pair#*=}"
  if [[ ! "$v" =~ ^[A-Za-z0-9_./-]+$ ]] || [[ "$v" == *..* ]]; then
    err "${pair%%=*} contains unsupported characters: '$v' (allowed: letters, digits, _ . / -)"
    exit 4
  fi
done

if [[ ! -d "$PROJECT_DIR" ]]; then
  err "PROJECT_DIR '$PROJECT_DIR' does not exist. Upload your Android project to the repository root, or set the ANDROID_PROJECT_DIR repository variable."
  exit 2
fi
cd "$PROJECT_DIR"

# Framework detection: this workflow builds native Gradle projects only.
if [[ -f pubspec.yaml ]]; then
  err "Flutter project detected (pubspec.yaml). This workflow builds native Gradle projects only. See docs/FRAMEWORK_COMPATIBILITY.md."
  exit 3
fi
if [[ -f package.json ]] && grep -q '"react-native"' package.json; then
  err "React Native project detected (package.json). JavaScript bundling needs Node.js, which this workflow does not install. See docs/FRAMEWORK_COMPATIBILITY.md."
  exit 3
fi

missing=0
need() { if [[ ! -e "$1" ]]; then err "Missing required file: $PROJECT_DIR/$1 — $2"; missing=1; fi; }

need gradlew "the Gradle wrapper script. Android Studio creates it; upload it with the project."
need gradle/wrapper/gradle-wrapper.properties "the wrapper settings file (gradle/wrapper/ folder). Folders starting with a dot or named 'gradle' are sometimes skipped by phone uploads."
need gradle/wrapper/gradle-wrapper.jar "the wrapper JAR (gradle/wrapper/ folder). Make sure .gitignore does not exclude *.jar."

if [[ ! -f settings.gradle && ! -f settings.gradle.kts ]]; then
  err "Missing settings.gradle or settings.gradle.kts in $PROJECT_DIR."; missing=1
fi
if [[ ! -f build.gradle && ! -f build.gradle.kts ]]; then
  err "Missing root build.gradle or build.gradle.kts in $PROJECT_DIR."; missing=1
fi
[[ $missing -eq 0 ]] || exit 2

# Module checks
if [[ ! -d "$MODULE" ]]; then
  found="$(grep -rlE 'com\.android\.application|android\.application' --include=build.gradle --include=build.gradle.kts . 2>/dev/null | head -5 | tr '\n' ' ' || true)"
  err "Module directory '$MODULE' not found. Android application module build files found: ${found:-none}. Set the ANDROID_MODULE repository variable (or the 'module' input) to the correct module name."
  exit 2
fi
if [[ ! -f "$MODULE/build.gradle" && ! -f "$MODULE/build.gradle.kts" ]]; then
  err "Module '$MODULE' has no build.gradle or build.gradle.kts."; exit 2
fi
mb="$MODULE/build.gradle"; [[ -f "$mb" ]] || mb="$MODULE/build.gradle.kts"
if ! grep -qE 'com\.android\.application|android\.application' "$mb"; then
  err "Module '$MODULE' does not apply the Android application plugin (looked in $mb). It may be a library module; choose the application module."
  exit 2
fi
if ! grep -qE "include\(?[^)]*[\"':]${MODULE##*/}[\"']" settings.gradle* 2>/dev/null; then
  echo "::warning::Module '$MODULE' was not found in an include(...) line of settings.gradle*. Gradle may fail with 'project not found'."
fi

# Hand the repository's own wrapper permission; phone uploads often drop the executable bit.
chmod +x gradlew

echo "OK: Gradle Android project detected (dir='$PROJECT_DIR', module='$MODULE')."
if [[ -n "${GITHUB_OUTPUT:-}" ]]; then
  { echo "project_dir=$PROJECT_DIR"; echo "module=$MODULE"; } >> "$GITHUB_OUTPUT"
fi
