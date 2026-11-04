# Changelog

## 0.2.0 — ZIP inbox
- Added `process-zip.yml`, `scripts/process-zip-inbox.py`, 25 unit tests, `_inbox/` and `_failed/`, and `docs/ZIP_INBOX_OPERATIONS.md`.
- Android build workflow now ignores pushes that only touch `_inbox/` or `_failed/`, and skips itself in the template repository.
- Verified: actionlint, pyflakes, unit tests, a local git end-to-end simulation (good ZIP, rejected ZIP, commit and push). Not verified on live GitHub.

## 0.1.0 — initial version
- Build workflow (compile, unit tests, debug APK, artifacts, diagnostics).
- Manual release workflow (optional signing, optional draft GitHub Release).
- Validation and diagnostics scripts, documentation set.
- Verified: actionlint, shellcheck, YAML parse, mock-project script tests.
- Not yet verified: a real Android build on GitHub (see `tests/workflow-validation.md`).
