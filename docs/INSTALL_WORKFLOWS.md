# Install the workflows (one time)

This package was made without a `.github/` folder so it can pass ZIP-inbox checks that reject it. GitHub only runs workflows from `.github/workflows/`, so copy them there by hand.

Copies are in `docs/install-workflows/`.

## Required (the build will not run without the first two)
For each file below:
1. In your repository tap **Add file → Create new file**.
2. In the name box type the full path, for example `.github/workflows/android-build.yml` (typing `/` creates folders).
3. Open the copy in `docs/install-workflows/`, select all, copy, and paste it into the new file.
4. Tap **Commit changes**.

| Copy in docs/install-workflows/ | Create as |
|---|---|
| `android-build.yml` | `.github/workflows/android-build.yml` |
| `android-release.yml` | `.github/workflows/android-release.yml` |
| `process-zip.yml` | `.github/workflows/process-zip.yml` (enables the ZIP inbox) |

## Optional
| Copy | Create as |
|---|---|
| `pull_request_template.md` | `.github/pull_request_template.md` |
| `bug_report.md` | `.github/ISSUE_TEMPLATE/bug_report.md` |
| `build_failure.md` | `.github/ISSUE_TEMPLATE/build_failure.md` |

## Then
Open **Actions**; you should see **Android build and test**. Tick **Template repository** in Settings, then follow `docs/PHONE_WORKFLOW.md`.
You can delete `docs/install-workflows/` afterwards. Keep the pinned SHA comments if you edit the workflows.

Note: the workflows run `scripts/validate-android-project.sh`, so the `scripts/` folder must be present in the repository root.
