"""Tests for scripts/process-zip-inbox.py. Run: python3 -m unittest tests/test_process_zip_inbox.py -v"""
import importlib.util
import os
import stat
import tempfile
import unittest
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
spec = importlib.util.spec_from_file_location("pzi", ROOT / "scripts" / "process-zip-inbox.py")
pzi = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pzi)

PK = "-----BEGIN " + "RSA PRIVATE KEY-----"


def make_zip(path, entries):
    """entries: dict name -> bytes/str, or (name, bytes, 'symlink')."""
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as z:
        for name, data in entries.items():
            if isinstance(data, tuple) and data[0] == "symlink":
                zi = zipfile.ZipInfo(name)
                zi.create_system = 3
                zi.external_attr = (stat.S_IFLNK | 0o777) << 16
                z.writestr(zi, data[1])
            else:
                z.writestr(name, data)


class Base(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.repo = Path(self._tmp.name)
        (self.repo / "_inbox").mkdir()

    def tearDown(self):
        self._tmp.cleanup()

    def run_zip(self, entries, name="test.zip", **kw):
        p = self.repo / "_inbox" / name
        make_zip(p, entries)
        return pzi.process_zip(p, self.repo, **kw)

    def assertRejected(self, entries, text, name="test.zip", **kw):
        ok, new, upd, problems = self.run_zip(entries, name, **kw)
        self.assertFalse(ok, problems)
        self.assertTrue(any(text in p for p in problems), problems)
        self.assertEqual([p for p in self.repo.rglob("*") if p.is_file() and p.parent.name != "_inbox"], [])


class Accepts(Base):
    def test_extracts_new_files(self):
        ok, new, upd, _ = self.run_zip({"docs/a.md": "hi", "README.md": "r", "scripts/x.sh": "echo", ".gitignore": "b/"})
        self.assertTrue(ok)
        self.assertEqual(new, [".gitignore", "README.md", "docs/a.md", "scripts/x.sh"])
        self.assertEqual((self.repo / "docs/a.md").read_text(), "hi")
        self.assertEqual(stat.S_IMODE(os.stat(self.repo / "scripts/x.sh").st_mode), 0o644)

    def test_overwrites_and_keeps_others(self):
        (self.repo / "docs").mkdir()
        (self.repo / "docs/a.md").write_text("old")
        (self.repo / "docs/keep.md").write_text("keep")
        ok, new, upd, _ = self.run_zip({"docs/a.md": "new"})
        self.assertTrue(ok)
        self.assertEqual(upd, ["docs/a.md"])
        self.assertEqual((self.repo / "docs/a.md").read_text(), "new")
        self.assertEqual((self.repo / "docs/keep.md").read_text(), "keep")

    def test_env_example_and_directory_entries(self):
        ok, *_ = self.run_zip({"docs/": "", "docs/sub/": "", "docs/sub/n.md": "x", ".env.example": "KEY="})
        self.assertTrue(ok)


class Rejects(Base):
    def test_traversal(self):
        self.assertRejected({"docs/../../evil.txt": "x"}, "traversal")

    def test_absolute(self):
        self.assertRejected({"/etc/passwd": "x"}, "absolute")

    def test_backslash(self):
        self.assertRejected({"docs\\a.md": "x"}, "backslash")

    def test_symlink(self):
        self.assertRejected({"docs/link": ("symlink", "/etc/passwd")}, "symbolic link")

    def test_duplicate_case_insensitive(self):
        import warnings
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            self.assertRejected({"docs/A.md": "1", "docs/a.md": "2"}, "duplicate")

    def test_file_and_folder_conflict(self):
        self.assertRejected({"docs/a": "1", "docs/a/b.md": "2"}, "both a file and a folder")

    def test_env_file(self):
        self.assertRejected({"docs/.env": "A=1"}, "secret-like")
        self.assertRejected({".env.local": "A=1"}, "secret-like")

    def test_key_files(self):
        self.assertRejected({"docs/release.keystore": "x"}, "secret-like")
        self.assertRejected({"docs/id_rsa": "x"}, "secret-like")

    def test_secret_content(self):
        self.assertRejected({"docs/notes.md": "x\n" + PK + "\nabc"}, "secret")
        self.assertRejected({"docs/notes.md": "t=ghp_" + "a" * 36}, "secret")

    def test_blocked_dirs(self):
        self.assertRejected({".github/workflows/x.yml": "x"}, "not allowed anywhere")
        self.assertRejected({"docs/.git/config": "x"}, "not allowed anywhere")
        self.assertRejected({"docs/node_modules/a.js": "x"}, "not allowed anywhere")
        self.assertRejected({"_inbox/x.zip": "x"}, "not allowed anywhere")

    def test_unlisted_top_level(self):
        self.assertRejected({"app/page.tsx": "x"}, "not in the allowed list")
        self.assertRejected({"app/": ""}, "not in the allowed list")

    def test_protected_extractor(self):
        self.assertRejected({"scripts/process-zip-inbox.py": "print(1)"}, "protected")

    def test_too_many_entries(self):
        self.assertRejected({f"docs/{i}.md": "x" for i in range(5)}, "limit is 3", max_entries=3)

    def test_too_large(self):
        self.assertRejected({"docs/big.txt": "a" * 5000}, "exceeds", max_total=1000)

    def test_bad_names(self):
        for bad in ("bad name.zip", "Upper.zip", "under_score.zip", "-lead.zip"):
            p = self.repo / "_inbox" / bad
            make_zip(p, {"docs/a.md": "x"})
            ok, _, _, problems = pzi.process_zip(p, self.repo)
            self.assertFalse(ok, bad)

    def test_not_a_zip(self):
        p = self.repo / "_inbox" / "junk.zip"
        p.write_bytes(b"not a zip")
        ok, _, _, problems = pzi.process_zip(p, self.repo)
        self.assertFalse(ok)
        self.assertIn("not a valid ZIP", problems[0])

    def test_empty_zip(self):
        self.assertRejected({}, "empty")

    def test_unsafe_names(self):
        self.assertRejected({"docs/a;rm.md": "x"}, "unsafe")
        self.assertRejected({"docs/a$b.md": "x"}, "unsafe")

    def test_dest_is_symlink(self):
        (self.repo / "docs").mkdir()
        os.symlink("/etc", self.repo / "docs" / "sub")
        ok, _, _, problems = self.run_zip({"docs/sub/x.md": "x"})
        self.assertFalse(ok)
        self.assertFalse(Path("/etc/x.md").exists())

    def test_all_or_nothing(self):
        ok, *_ = self.run_zip({"docs/good.md": "x", "docs/.env": "bad"})
        self.assertFalse(ok)
        self.assertFalse((self.repo / "docs/good.md").exists())


class EndToEnd(Base):
    def test_main_mixed_inbox(self):
        make_zip(self.repo / "_inbox" / "good-one.zip", {"docs/a.md": "x"})
        make_zip(self.repo / "_inbox" / "bad name.zip", {"docs/b.md": "x"})
        (self.repo / "_inbox" / "README.md").write_text("ignore me")
        rc = pzi.main(self.repo)
        self.assertEqual(rc, 1)
        self.assertTrue((self.repo / "docs/a.md").exists())
        self.assertFalse((self.repo / "docs/b.md").exists())
        self.assertFalse((self.repo / "_inbox/good-one.zip").exists())
        self.assertTrue((self.repo / "_inbox/README.md").exists())
        self.assertTrue((self.repo / "_failed/bad_name.zip").exists())
        self.assertIn("not allowed", (self.repo / "_failed/bad_name.zip.report.md").read_text())

    def test_main_empty_inbox(self):
        self.assertEqual(pzi.main(self.repo), 0)


if __name__ == "__main__":
    unittest.main()
