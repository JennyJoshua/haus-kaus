# Free usage and billing

Source: GitHub Docs, "GitHub Actions billing" and "Product usage included with each plan" (checked 16 October 2026):
- https://docs.github.com/en/billing/concepts/product-billing/github-actions
- https://docs.github.com/en/billing/reference/product-usage-included

GitHub changes these terms. **Re-check both pages before relying on this file.**

## Public repositories
Standard GitHub-hosted runners are free in public repositories. This is the cheapest way to use the template, but anyone can read the source, workflows and (if you leave them on) artifacts. Never put secrets or private code in a public repository.

## Private repositories
Each account gets an included monthly quota; usage above it is billed. Minutes are charged to the repository owner, not the person who ran the workflow. Included amounts per the docs:

| Plan | Minutes / month | Artifact storage | Cache storage |
|---|---|---|---|
| GitHub Free (and Free for organizations) | 2,000 | 500 MB | 10 GB per repository |
| GitHub Pro | 3,000 | 1 GB | 10 GB per repository |
| GitHub Team | 3,000 | 2 GB | 10 GB per repository |

Minutes reset each billing cycle. Standard Linux 2-core runners are what this template uses (`ubuntu-24.04`). The docs list a baseline rate of $0.006 per Linux 2-core minute beyond your quota.

## Storage
- Artifact storage is **shared** with GitHub Packages.
- Storage is billed by hourly accrual (GB-hours). Deleting artifacts lowers current storage but does **not** remove charges already accrued this cycle.
- Logs and job summaries do not count towards artifact storage.
- Cache storage is a separate 10 GB allowance per repository. Gradle caches can be large; if the repository exceeds its cache limit, old entries are evicted.
- The template keeps artifacts for 7 days by default (`ARTIFACT_RETENTION_DAYS`). Check your account's maximum and default under Settings → Actions → General.

## Other things that can cost money
Larger runners (always billed, even in public repositories), macOS/Windows runners (higher per-minute rates), Codespaces, Packages storage and transfer, Git LFS, Copilot code review minutes in private repositories. **The template uses none of these.**

## If you run out
With no payment method on file, usage is blocked once the quota is used up. With a payment method, spending can be capped with a budget set to stop usage. Do not add a payment method unless you intend to pay.

## How the template saves minutes
- `concurrency` cancels superseded runs.
- Docs-only changes do not trigger builds (`paths-ignore`).
- Gradle dependency cache; `timeout-minutes` stops runaway jobs.
- Diagnostics are uploaded only on failure.

## What this file does not claim
It does not guarantee any build stays free. It does not cover account-specific conditions (education/nonprofit discounts, enterprise terms, budgets someone else set). Check Settings → Billing → Usage.
