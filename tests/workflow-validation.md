# Workflow validation record

## Performed (offline, in the build environment)
| Check | Tool | Result |
|---|---|---|
| Workflow syntax and expressions | actionlint | Pass, no findings |
| YAML parse | PyYAML | Pass |
| Shell syntax and style | `bash -n`, shellcheck | Pass, no findings |
| Validator: empty repo, missing wrapper jar, wrong module, library module, Flutter, React Native, unsafe task string, Groovy and Kotlin DSL good projects | mock projects | Exit codes and messages as designed |
| Diagnostics: Kotlin, dependency, Java-version and unit-test log samples | sample logs | Classified correctly |
| Pinned SHAs | `git ls-remote` against github.com | Each SHA resolved from the named tag (annotated tags resolved to their commit) |
| Billing statements | GitHub Docs pages, 16 Oct 2026 | Reflected in docs |

## ZIP inbox (added 0.2.0)
| Check | Result |
|---|---|
| `python3 -m unittest tests/test_process_zip_inbox.py` (25 tests: traversal, absolute, backslash, symlink, duplicates, secrets, blocked dirs, limits, bad names, all-or-nothing, mixed inbox) | Pass |
| pyflakes, actionlint | Clean |
| Local git simulation with a bare remote: good ZIP extracted and overwrote a file, bad ZIP moved to `_failed/` with a report, commit and push succeeded | Pass |
| Live run on GitHub (upload from phone, bot push, protected-branch behaviour) | **Not performed** |

## Not performed
- **No real Android build has been run on GitHub Actions.** Gradle, the Android SDK and Maven repositories were not reachable from the build environment.
- Not verified: `gradle/actions/wrapper-validation` at the pinned SHA on a live run, `android-actions/setup-android` behaviour on `ubuntu-24.04`, artifact download on a phone, the release and publish jobs.
- Not tested: signing, flavors, multi-module projects, Flutter, React Native, instrumented tests.

## First-build checklist (do this before trusting the template)
1. Create a repository from the template and upload a small known-good Gradle Android project (Kotlin).
2. Run the workflow. Expect green; note the run time.
3. Download the artifact on the phone; install and open the app.
4. Break something on purpose (typo in a Kotlin file); confirm the summary says "Kotlin compilation failure" and diagnostics upload.
5. Remove `gradlew` in a test branch; confirm a clear missing-file error and no success report.
6. Run twice quickly; confirm the older run is cancelled.
7. Open a pull request from a fork (or a second account); confirm it runs with no secrets.
8. Release workflow: run with `sign=false`, `publish=false`; confirm warning about unsigned APK.
9. ZIP inbox: upload a good ZIP, then a ZIP containing `.github/x.yml`, then `bad name.zip`; confirm extract, reject and report, and that the build workflow did not run.
10. Record the results here and update `CHANGELOG.md`.
