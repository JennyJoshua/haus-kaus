# Workflow usage examples

## Run a build manually
Actions → **Android build and test** → **Run workflow** → leave fields blank for defaults.

## Build a different module
Run workflow → `module` = `mobile`. Or set variable `ANDROID_MODULE=mobile` permanently.

## Skip unit tests for one run
Run workflow → `run_tests` = `false`. The summary will show "Unit tests: NOT RUN".

## Use Java 11 for an older project
Run workflow → `java_version` = `11`, or set `ANDROID_JAVA_VERSION=11`.

## Project in a subfolder
Set variable `ANDROID_PROJECT_DIR=my-app-folder`.

## Manual release (signed, draft release)
1. Add the four signing secrets (docs/SECURITY.md).
2. Actions → **Android release (manual only)** → Run workflow from `main`.
3. `tag` = `v1.0.0`, `sign` = `true`, `publish` = `true`.
4. Review the **draft** release under Releases, then publish it yourself.
For a build you only want to download: `sign` = `true`, `publish` = `false`; the APK is an artifact.
