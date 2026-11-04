#!/usr/bin/env python3
"""Safely extract ZIP files dropped in _inbox/ into the repository.

Run from the repository root by .github/workflows/process-zip.yml.
Each ZIP is checked completely before anything is written. A ZIP is either
fully extracted (and deleted) or rejected whole (moved to _failed/ with a report).

Exit code: 0 if every ZIP was extracted (or the inbox was empty), 1 if any was rejected.
"""
import datetime
import os
import re
import shutil
import stat
import sys
import tempfile
import zipfile
from pathlib import Path

# ---- Limits and rules (edit here, then commit; ZIPs cannot change this file) ----
MAX_ZIP_BYTES = 50 * 1024 * 1024
MAX_ENTRIES = 1000
MAX_UNCOMPRESSED_BYTES = 100 * 1024 * 1024
SCAN_BYTES = 1024 * 1024            # leading bytes of each file scanned for secrets
MAX_PROBLEMS_REPORTED = 50

ALLOWED_DIRS = {"app", "docs", "examples", "gradle", "scripts", "tests"}
ROOT_DOTFILES_ALLOWED = {".gitignore", ".gitattributes", ".env.example"}
BLOCKED_COMPONENTS = {".git", ".github", "node_modules", ".next", "_inbox", "_failed"}
PROTECTED_PATHS = {"scripts/process-zip-inbox.py"}   # a ZIP may not replace the extractor

ZIP_NAME_RE = re.compile(r"^[a-z0-9][a-z0-9-]*\.zip$")
COMPONENT_RE = re.compile(r"^[A-Za-z0-9._ @+()-]+$")
ROOT_FILE_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")

SECRET_NAMES = {".npmrc", ".netrc", ".htpasswd", ".pypirc", "id_rsa", "id_dsa",
                "id_ecdsa", "id_ed25519", "credentials", "credentials.json"}
SECRET_SUFFIXES = (".pem", ".key", ".p12", ".pfx", ".jks", ".keystore", ".kdbx")
_PK = "-----BEGIN " + r"(?:RSA |EC |DSA |OPENSSH |PGP |ENCRYPTED )?" + "PRIVATE KEY"
SECRET_CONTENT_RES = [
    (re.compile(_PK), "private key block"),
    (re.compile(r"gh[pousr]_[A-Za-z0-9]{36,}"), "GitHub token"),
    (re.compile(r"github_pat_[A-Za-z0-9_]{50,}"), "GitHub fine-grained token"),
    (re.compile(r"AKIA[0-9A-Z]{16}"), "AWS access key id"),
    (re.compile(r"sk-ant-[A-Za-z0-9_-]{20,}"), "API key"),
]


class Rejected(Exception):
    pass


def is_secret_name(base: str) -> bool:
    low = base.lower()
    if low == ".env.example":
        return False
    if low == ".env" or low.startswith(".env."):
        return True
    return (low in SECRET_NAMES or low.endswith(SECRET_SUFFIXES)
            or (low.startswith("serviceaccount") and low.endswith(".json")))


def check_zip_name(name: str) -> list:
    return [] if ZIP_NAME_RE.match(name) else [
        f"ZIP file name '{name}' is not allowed. Use lowercase letters, numbers and hyphens only, ending in .zip (example: phase2-docs.zip)."]


def validate_entries(zf: zipfile.ZipFile, max_entries=MAX_ENTRIES, max_total=MAX_UNCOMPRESSED_BYTES):
    """Return (files, problems). files = list of (ZipInfo, relpath)."""
    problems, files = [], []
    infos = zf.infolist()
    if not infos:
        return [], ["ZIP is empty."]
    if len(infos) > max_entries:
        problems.append(f"ZIP has {len(infos)} entries; the limit is {max_entries}.")
        return [], problems
    declared = sum(i.file_size for i in infos)
    if declared > max_total:
        problems.append(f"Uncompressed size {declared} bytes exceeds the limit of {max_total} bytes.")
    seen, file_paths, dir_paths = {}, set(), set()

    def bad(entry, msg):
        problems.append(f"{entry!r}: {msg}")

    for info in infos:
        name = info.filename
        if any(ord(c) < 32 or ord(c) == 127 for c in name):
            bad(name, "contains control characters"); continue
        if "\\" in name:
            bad(name, "contains a backslash"); continue
        if name.startswith("/") or re.match(r"^[A-Za-z]:", name):
            bad(name, "absolute path"); continue
        is_dir = name.endswith("/")
        parts = name.rstrip("/").split("/")
        part_problem = None
        for p in parts:
            if p in ("", ".", ".."):
                part_problem = "path traversal or empty path segment"; break
            if p in BLOCKED_COMPONENTS:
                part_problem = f"'{p}' is not allowed anywhere in a path"; break
            if len(p) > 150 or not COMPONENT_RE.match(p) or p.endswith((".", " ")):
                part_problem = f"unsafe file or folder name '{p}'"; break
        if part_problem:
            bad(name, part_problem); continue
        if info.flag_bits & 0x1:
            bad(name, "encrypted entry"); continue
        mode = info.external_attr >> 16
        if info.create_system == 3 and mode:
            ftype = stat.S_IFMT(mode)
            if ftype == stat.S_IFLNK:
                bad(name, "symbolic link"); continue
            if ftype not in (0, stat.S_IFREG, stat.S_IFDIR):
                bad(name, "special file type"); continue
        rel = "/".join(parts)
        if len(rel) > 240:
            bad(name, "path too long"); continue
        if not is_dir and is_secret_name(parts[-1]):
            bad(name, "secret-like file name"); continue
        if len(parts) == 1:
            if is_dir:
                if parts[0] not in ALLOWED_DIRS:
                    bad(name, f"top-level folder '{parts[0]}' is not in the allowed list ({', '.join(sorted(ALLOWED_DIRS))})")
                    continue
            elif not (ROOT_FILE_RE.match(parts[0]) or parts[0] in ROOT_DOTFILES_ALLOWED):
                bad(name, "root file name not allowed"); continue
        elif parts[0] not in ALLOWED_DIRS:
            bad(name, f"top-level folder '{parts[0]}' is not in the allowed list ({', '.join(sorted(ALLOWED_DIRS))})"); continue
        if is_dir:
            dir_paths.add(rel.lower())
            continue
        if rel in PROTECTED_PATHS:
            bad(name, "protected file; it cannot be replaced by a ZIP"); continue
        key = rel.lower()
        if key in seen:
            bad(name, f"duplicate path (same as {seen[key]!r}, ignoring letter case)"); continue
        seen[key] = name
        file_paths.add(key)
        files.append((info, rel))

    # a path cannot be both a file and a folder inside the ZIP
    for fp in file_paths:
        parent = fp
        while "/" in parent:
            parent = parent.rsplit("/", 1)[0]
            if parent in file_paths:
                problems.append(f"'{parent}' is used as both a file and a folder.")
    if not files and not problems:
        problems.append("ZIP contains no files.")
    return files, problems


def scan_secrets(head: bytes):
    text = head.decode("latin-1")
    for rx, label in SECRET_CONTENT_RES:
        if rx.search(text):
            return label
    return None


def extract_to_staging(zf, files, staging: Path, max_total=MAX_UNCOMPRESSED_BYTES):
    """Extract into a temp folder, counting real bytes (headers can lie). Raises Rejected."""
    total = 0
    for info, rel in files:
        dest = staging / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        head = b""
        try:
            with zf.open(info) as src, open(dest, "wb") as out:
                while True:
                    chunk = src.read(65536)
                    if not chunk:
                        break
                    total += len(chunk)
                    if total > max_total:
                        raise Rejected(f"Actual uncompressed size exceeds the limit of {max_total} bytes.")
                    if len(head) < SCAN_BYTES:
                        head += chunk[: SCAN_BYTES - len(head)]
                    out.write(chunk)
        except (zipfile.BadZipFile, RuntimeError, NotImplementedError, EOFError, OSError) as exc:
            raise Rejected(f"{rel!r}: cannot be read ({type(exc).__name__}).")
        label = scan_secrets(head)
        if label:
            raise Rejected(f"{rel!r}: looks like it contains a secret ({label}).")


def check_destinations(files, repo: Path):
    repo_real = os.path.realpath(repo)
    problems = []
    for _, rel in files:
        dest = repo / rel
        cur = repo
        for part in rel.split("/")[:-1]:
            cur = cur / part
            if os.path.islink(cur) or (cur.exists() and not cur.is_dir()):
                problems.append(f"{rel!r}: '{cur.relative_to(repo)}' already exists and is not a normal folder.")
                break
        else:
            if os.path.islink(dest) or dest.is_dir():
                problems.append(f"{rel!r}: destination already exists and is not a normal file.")
            elif not os.path.realpath(dest.parent).startswith(repo_real + os.sep) and os.path.realpath(dest.parent) != repo_real:
                problems.append(f"{rel!r}: resolves outside the repository.")
    return problems


def install(files, staging: Path, repo: Path):
    new, updated = [], []
    for _, rel in files:
        dest = repo / rel
        existed = dest.exists()
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(staging / rel, dest)
        os.chmod(dest, 0o644)
        (updated if existed else new).append(rel)
    return sorted(new), sorted(updated)


def process_zip(zip_path: Path, repo: Path, max_entries=MAX_ENTRIES, max_total=MAX_UNCOMPRESSED_BYTES):
    """Return (ok, new, updated, problems). Writes into repo only when everything passed."""
    problems = check_zip_name(zip_path.name)
    if zip_path.stat().st_size > MAX_ZIP_BYTES:
        problems.append(f"ZIP is larger than {MAX_ZIP_BYTES // (1024 * 1024)} MB.")
    if problems:
        return False, [], [], problems
    try:
        zf = zipfile.ZipFile(zip_path)
    except (zipfile.BadZipFile, OSError):
        return False, [], [], ["File is not a valid ZIP archive."]
    with zf:
        files, problems = validate_entries(zf, max_entries, max_total)
        if problems:
            return False, [], [], problems[:MAX_PROBLEMS_REPORTED]
        problems = check_destinations(files, repo)
        if problems:
            return False, [], [], problems[:MAX_PROBLEMS_REPORTED]
        with tempfile.TemporaryDirectory() as tmp:
            staging = Path(tmp)
            try:
                extract_to_staging(zf, files, staging, max_total)
            except Rejected as exc:
                return False, [], [], [str(exc)]
            new, updated = install(files, staging, repo)
    return True, new, updated, []


def move_to_failed(zip_path: Path, repo: Path, problems):
    failed = repo / "_failed"
    failed.mkdir(exist_ok=True)
    safe = re.sub(r"[^A-Za-z0-9._-]+", "_", zip_path.name).strip("._") or "upload.zip"
    if not safe.lower().endswith(".zip"):
        safe += ".zip"
    target, n = failed / safe, 1
    while target.exists():
        target = failed / f"{n}-{safe}"; n += 1
    shutil.move(str(zip_path), str(target))
    report = target.with_name(target.name + ".report.md")
    now = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    lines = [f"# Rejected ZIP: {zip_path.name}", "", f"Time: {now}", "",
             "Nothing from this ZIP was extracted.", "", "## Problems", ""]
    lines += [f"- {p}" for p in problems]
    lines += ["", "## What to do", "",
              "Fix the problems, build a new ZIP and upload it to `_inbox/`. "
              "You can delete this ZIP and report from `_failed/` afterwards.", ""]
    report.write_text("\n".join(lines), encoding="utf-8")
    return target


def main(repo: Path = None) -> int:
    repo = Path(repo or os.getcwd())
    inbox = repo / "_inbox"
    summary = ["## ZIP inbox result", ""]
    rc = 0
    zips = sorted(p for p in inbox.iterdir() if p.is_file() or p.is_symlink()) if inbox.is_dir() else []
    zips = [p for p in zips if p.name.lower().endswith(".zip")]
    if not zips:
        summary.append("No ZIP files found in `_inbox/`.")
    for zp in zips:
        if zp.is_symlink():
            zp.unlink()
            summary.append(f"- **{zp.name}**: REJECTED (symbolic link); removed.")
            rc = 1
            continue
        ok, new, updated, problems = process_zip(zp, repo)
        if ok:
            zp.unlink()
            summary.append(f"- **{zp.name}**: extracted ({len(new)} new, {len(updated)} updated).")
            summary += [f"  - new: `{p}`" for p in new[:100]] + [f"  - updated: `{p}`" for p in updated[:100]]
            print(f"OK {zp.name}: {len(new)} new, {len(updated)} updated")
        else:
            dest = move_to_failed(zp, repo, problems)
            rc = 1
            summary.append(f"- **{zp.name}**: REJECTED, moved to `_failed/{dest.name}` (report alongside).")
            summary += [f"  - {p}" for p in problems[:10]]
            print(f"::error title=ZIP rejected::{zp.name}: {problems[0]}")
    text = "\n".join(summary) + "\n"
    print(text)
    out = os.environ.get("GITHUB_STEP_SUMMARY")
    if out:
        with open(out, "a", encoding="utf-8") as fh:
            fh.write(text)
    return rc


if __name__ == "__main__":
    sys.exit(main())
