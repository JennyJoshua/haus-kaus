#!/usr/bin/env bash
# Builds a concise diagnostics summary from the Gradle logs captured by the workflow.
# Inputs (environment): PROJECT_DIR, LOG_DIR (default ci-logs), plus step outcomes:
#   OUTCOME_VALIDATE, OUTCOME_COMPILE, OUTCOME_TEST, OUTCOME_APK  (success|failure|skipped|cancelled|"")
# Never prints environment variables. Always exits 0 so it cannot mask the real failure.
set -uo pipefail

PROJECT_DIR="${PROJECT_DIR:-.}"
LOG_DIR="${LOG_DIR:-ci-logs}"
OUT="$LOG_DIR/diagnostics-summary.md"
mkdir -p "$LOG_DIR"

label() { case "${1:-}" in success) echo "PASSED";; failure) echo "FAILED";; skipped|"") echo "NOT RUN";; cancelled) echo "CANCELLED";; *) echo "$1";; esac; }

# Classify a failure from log text. First match wins; order is most specific first.
classify() {
  local f="$1"
  [[ -s "$f" ]] || { echo "No log captured"; return; }
  if   grep -qE 'Wrapper.*(checksum|not valid)|gradle-wrapper.jar.*(corrupt|invalid)' "$f"; then echo "Invalid Gradle wrapper"
  elif grep -qE 'Unsupported class file major version|requires Java [0-9]+|Android Gradle plugin requires Java|Unsupported Java|incompatible with.*Java' "$f"; then echo "Java/Gradle incompatibility (change ANDROID_JAVA_VERSION)"
  elif grep -qE 'SDK location not found|Failed to find (Build Tools|target with hash)|Failed to install the following Android SDK|licen[cs]e.*not been accepted|ANDROID_HOME' "$f"; then echo "Android SDK configuration error"
  elif grep -qE 'Could not resolve|Could not GET|Could not HEAD|Read timed out|Connection reset|Could not download|Could not find [a-zA-Z0-9_.-]+:' "$f"; then echo "Dependency resolution failure"
  elif grep -qE '^e: .*\.kt|Kotlin.*(compil|error)|org\.jetbrains\.kotlin.*Compilation error' "$f"; then echo "Kotlin compilation failure"
  elif grep -qE 'error: .*(cannot find symbol|incompatible types|package .* does not exist)|\.java:[0-9]+: error' "$f"; then echo "Java compilation failure"
  elif grep -qE 'AAPT|Android resource (linking|compilation) failed|processDebugResources|mergeDebugResources|resource .* not found' "$f"; then echo "Resource-processing failure"
  elif grep -qE 'There were failing tests|Test.*FAILED|tests completed, [0-9]+ failed' "$f"; then echo "Unit-test failure"
  elif grep -qE 'Execution failed for task .*(package|assemble|lint|sign)' "$f"; then echo "APK-generation failure"
  elif grep -qE "Project '.*' not found|Task '.*' not found|Could not determine the dependencies of task" "$f"; then echo "Wrong module or task name"
  else echo "Unclassified (read the first 'What went wrong' block in the log)"
  fi
}

first_errors() {
  local f="$1"
  [[ -s "$f" ]] || return 0
  # Gradle's own explanation first, then compiler/error lines. Truncated and secret-free (logs only).
  awk '/\* What went wrong:/{p=1} p{print} /\* Try:/{if(p){exit}}' "$f" | head -n 25
  grep -nE '^e: |error:|FAILED|Execution failed for task' "$f" | head -n 15
}

{
  echo "## Android build result"
  echo
  echo "| Stage | Result |"
  echo "|---|---|"
  echo "| Project validation | $(label "${OUTCOME_VALIDATE:-}") |"
  echo "| Compilation | $(label "${OUTCOME_COMPILE:-}") |"
  echo "| Unit tests | $(label "${OUTCOME_TEST:-}") |"
  echo "| Debug APK generation | $(label "${OUTCOME_APK:-}") |"
  echo "| Instrumented tests | NOT RUN (this template never runs them; see docs/BUILDING_AND_TESTING.md) |"
  echo
  echo "_A green build does not prove the app works on a real phone. Install the APK and test it._"

  for pair in "compile:${OUTCOME_COMPILE:-}" "unit-tests:${OUTCOME_TEST:-}" "apk:${OUTCOME_APK:-}"; do
    name="${pair%%:*}"; res="${pair#*:}"
    if [[ "$res" == "failure" ]]; then
      log="$LOG_DIR/$name.log"
      echo
      echo "### Failed stage: $name"
      echo "Category: **$(classify "$log")**"
      echo
      echo '```'
      first_errors "$log"
      echo '```'
    fi
  done
  if [[ "${OUTCOME_VALIDATE:-}" == "failure" ]]; then
    echo
    echo "### Failed stage: project validation"
    echo "Category: **Missing or invalid Android project files** — see the red error annotation on this run."
  fi
} > "$OUT"

cat "$OUT"
if [[ -n "${GITHUB_STEP_SUMMARY:-}" ]]; then cat "$OUT" >> "$GITHUB_STEP_SUMMARY"; fi
exit 0
