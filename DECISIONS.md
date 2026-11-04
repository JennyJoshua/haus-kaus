# Decisions

| # | Decision | Reason |
|---|---|---|
| 1 | Standard `ubuntu-24.04` runner | Free for public repos, cheapest for private (Linux 2-core) |
| 2 | Cache via `actions/setup-java` (`cache: gradle`) | First-party, no extra third-party action or binary |
| 3 | Pin every third-party action to a full commit SHA | Tags can be moved; SHAs cannot |
| 4 | Pinned to older, established releases | Avoids brand-new releases; update deliberately (see SECURITY.md) |
| 5 | `gradle/actions/wrapper-validation` | Detects tampered `gradle-wrapper.jar` |
| 6 | Plain `pull_request`, never `pull_request_target` | Fork code gets read-only token and no secrets |
| 7 | Inputs reach shell only via `env` and are regex-checked | Prevents script injection through workflow inputs |
| 8 | Tasks default to `compileDebugSources`, `testDebugUnitTest`, `assembleDebug` | Standard AGP tasks, work for Kotlin and Java modules |
| 9 | Instrumented tests not run | Need an emulator (KVM, slow, costly minutes); documented instead |
| 10 | Release workflow is manual, separate, publishes only a **draft** release from `main` for a signed build | No accidental publication |
| 11 | Release publish uses `gh` CLI with `GITHUB_TOKEN` | No third-party release action, no personal access token |
| 12 | Flutter and React Native detected and refused | Different toolchains; honest limits beat untested support |
| 13 | No sample app included | Could not verify a build offline; a fake app would mislead |
| 14 | `chmod +x gradlew` in the validator | Phone uploads often lose the executable bit |
| 15 | ZIP extraction in a Python standard-library script, not shell | Safer path and size handling; unit-testable |
| 16 | Allowed ZIP folders: docs, examples, scripts, tests; `.github` never | A ZIP must not be able to change workflows |
| 17 | Extractor file is protected from replacement by a ZIP | A bad ZIP cannot loosen its own checks |
| 18 | Rejected ZIP makes the run red but results are still committed | Visible on a phone; good ZIPs in the same batch are not lost |
| 19 | Android build skipped when `repository.is_template` is true | The template has no project to build |
