# Security

## Built-in protections
- Workflows run with `permissions: contents: read`. Only the release **publish** job has `contents: write`, and only when you deliberately start it.
- No personal access token is needed; the built-in `GITHUB_TOKEN` is enough.
- `actions/checkout` runs with `persist-credentials: false`.
- Third-party actions are pinned to full commit SHAs.
- Workflow inputs and variables are never pasted into shell code. They pass through `env` and are regex-checked by `scripts/validate-android-project.sh`.
- The build workflow uses no secrets. Debug APKs need no signing key.
- Fork pull requests use `pull_request`, which gives forks a read-only token and no secrets. **Never switch to `pull_request_target` to run pull-request code.**
- Scripts never print environment variables.

## Fork pull requests
GitHub may require a maintainer to approve workflow runs from first-time contributors. Keep that setting on (Settings → Actions → General → Fork pull request workflows). Review a fork's changes to `.github/`, `scripts/` and any `build.gradle*` before approving; Gradle build files run code.

## Updating pinned actions
Each `uses:` line is `owner/action@<40-character SHA> # vX.Y.Z`. To update: look up the new release's commit SHA (for an annotated tag use the commit the tag points to), skip releases less than two weeks old, read the release notes, change the SHA and comment together, run the workflow, record it in `CHANGELOG.md`. Dependabot can propose these updates for GitHub Actions if you add `.github/dependabot.yml` (not included).

## Release signing (optional)
Never commit a keystore. Create four repository secrets (Settings → Secrets and variables → Actions):
`ANDROID_KEYSTORE_BASE64`, `ANDROID_KEYSTORE_PASSWORD`, `ANDROID_KEY_ALIAS`, `ANDROID_KEY_PASSWORD`.
The keystore is decoded to a temporary file only in the manual release workflow and deleted afterwards. Secrets are exposed to a single step and only when you choose `sign=true`.
Your `build.gradle` must read `RELEASE_STORE_FILE`, `RELEASE_STORE_PASSWORD`, `RELEASE_KEY_ALIAS` and `RELEASE_KEY_PASSWORD` (see `examples/gradle-project-configuration.md`).
**Back up the keystore somewhere safe and private. If it is lost you cannot update an app signed with it.**

## Handling secrets
- Do not paste secrets into issues, chats with ChatGPT or Claude, or workflow files.
- Secret values are masked in logs, but derived values (for example a re-encoded copy) are not.
- If a secret leaks, delete it in GitHub, create a new keystore or password, and treat the old one as compromised.

## Public repositories
Artifacts from public repositories can be downloaded by anyone signed in to GitHub. A debug APK contains your code in compiled form. Do not build apps with embedded private keys or tokens in a public repository.

## Optional extra approval for publishing
The publish job uses an environment named `release-publish`. Add required reviewers to it in Settings → Environments if your plan supports that for your repository type.

## ZIP inbox
`process-zip.yml` has `contents: write` (needed to commit extracted files), runs only on `main`, never for pull requests or forks, and executes nothing from a ZIP. It rejects path traversal, symbolic links, secret-like files and content, `.github/`, and replacement of its own script. Anyone with write access to `main` can use it. Details: `ZIP_INBOX_OPERATIONS.md`.
