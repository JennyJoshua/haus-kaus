# ZIP inbox operations

Drop a ZIP into `_inbox/` and GitHub Actions unpacks it into the repository for you. Built for uploads from an Android phone.

## Use it
1. Make a ZIP whose paths are **relative to the repository root** with **no wrapper folder** (for example `docs/NOTES.md`, not `my-folder/docs/NOTES.md`).
2. Name it with lowercase letters, numbers and hyphens only, ending `.zip` (example `update-docs.zip`).
3. In GitHub (browser): open `_inbox/` → **Add file → Upload files** → pick the ZIP → commit to **main**.
4. Open **Actions → Process ZIP inbox**. A green run means the files were extracted, committed, and the ZIP deleted. Pull or refresh the repository to see them.
5. A red run means a ZIP was rejected. Open the run summary, or `_failed/<name>.zip.report.md`, fix the problems and upload a corrected ZIP. Delete the old files in `_failed/`.

You can also start it by hand: **Actions → Process ZIP inbox → Run workflow** (on `main`), which processes whatever is in `_inbox/`.

## What gets checked (the whole ZIP is checked before anything is written)
| Rule | Limit / behaviour |
|---|---|
| ZIP size | 50 MB |
| Entries | 1,000 |
| Uncompressed size | 100 MB (real bytes are counted while extracting, not just the ZIP's claimed sizes) |
| Paths | No absolute paths, `..`, backslashes, odd characters, or over-long names |
| Symbolic links, encrypted entries, special files | Rejected |
| Duplicates (ignoring letter case), or a path used as both file and folder | Rejected |
| Top-level folders | Only `docs`, `examples`, `scripts`, `tests`; root files allowed |
| Never allowed anywhere | `.git`, `.github`, `node_modules`, `.next`, `_inbox`, `_failed` |
| Secret-like files | `.env` (not `.env.example`), `.pem`, `.key`, `.p12`, `.pfx`, `.jks`, `.keystore`, `id_rsa`, `.npmrc`, `.netrc` and similar |
| Secret-like content | Private key blocks, GitHub tokens, AWS key ids, API keys in the first 1 MB of each file |
| Protected file | `scripts/process-zip-inbox.py` cannot be replaced by a ZIP |

Behaviour: all-or-nothing per ZIP. Files at the same path are overwritten without asking; other files are left alone. Several ZIPs in the inbox are handled one at a time, in name order, independently. Permissions inside the ZIP are ignored (files are written as normal files).

## Why `.github/` is blocked
GitHub's built-in token cannot change workflow files anyway, and a ZIP that could edit workflows could weaken its own checks. Add or change anything under `.github/` by hand (**Add file → Create new file**, or edit in the browser).

## Changing the rules
Edit the constants at the top of `scripts/process-zip-inbox.py` in the GitHub browser editor (for example add a folder to `ALLOWED_DIRS`). Commit to `main`. Run the tests on a computer: `python3 -m unittest tests/test_process_zip_inbox.py -v`.

## Troubleshooting
| Symptom | Cause / fix |
|---|---|
| Nothing happened | ZIP not on `main`, or not inside `_inbox/`, or the upload was a non-ZIP. Check **Actions** for a run. Re-run manually. |
| "Push failed" | `main` is protected. Allow GitHub Actions to push, or turn the protection off for this repository. |
| ZIP rejected for folder not allowed | You zipped a wrapper folder, or used a folder outside the allowed list. |
| Run skipped | Runs started by the workflow's own commit are skipped on purpose. |
| Build workflow also ran | Pushes touching only `_inbox/` or `_failed/` are ignored by the Android build. |

## Cost
Each run takes well under a minute on a standard Linux runner (free in public repositories; counts against the monthly allowance in private ones, see `FREE_USAGE_AND_BILLING.md`). Extracted files are normal repository content, not artifacts. No paid services are used.

## Security notes
- The workflow runs only on `main` and has `contents: write`, which it needs to commit. It does not run for pull requests and is not triggered by forks.
- Anyone who can push to `main` can use the inbox. Treat write access as the key.
- Extraction never executes anything from the ZIP.
