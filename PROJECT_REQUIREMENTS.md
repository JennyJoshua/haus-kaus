# Project requirements (summary of the owner's handover)

**Goal:** a reusable repository template that builds and tests Android apps with GitHub Actions, produces a downloadable debug APK, and can be operated from an Android phone.

## Owner constraints
- Android phone is the main device; no Android Studio locally.
- Free tools only; no paid plans, paid APIs or unnecessary subscriptions.
- GitHub for source; ChatGPT for planning/review; Claude for coding/handovers.

## Must have
- Triggers: manual, push, pull request; concurrency cancellation.
- Project detection with actionable errors; never report success when nothing was built.
- Configurable module and Gradle tasks; Gradle wrapper only; dependency caching.
- Separate reporting of compile, unit-test, instrumented-test and APK results.
- Debug APK artifact with documented retention; failure diagnostics with categories.
- Least-privilege permissions, no secrets in logs, no `pull_request_target` for untrusted code.
- Optional manual release workflow with optional signing; no app-store publishing.
- Accurate, verified billing documentation.
- Documentation set listed in the handover (`docs/`, `examples/`, `tests/`).

## Out of scope / not claimed
- Proof that an app works on a physical device.
- Universal framework compatibility.
