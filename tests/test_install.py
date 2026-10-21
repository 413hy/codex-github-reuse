"""Integration checks with isolated user/project directories; no network calls."""

import importlib.util
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch


SPEC = importlib.util.spec_from_file_location("kit_installer", Path(__file__).resolve().parents[1] / "install.py")
installer = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(installer)

RULE_V1 = b"<!-- github-reuse-first:start -->\nUse $github-reuse-first before substantial development.\n<!-- github-reuse-first:end -->\n"
RULE_V2 = RULE_V1.replace(b"before substantial development", b"before new projects and substantial features")


class InstallerTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="reuse-installer-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.home = self.root / "用户 home"
        self.home.mkdir()
        self.package = self.root / "安装 package"
        self.source = self.package / "skills" / "github-reuse-first"
        self.source.mkdir(parents=True)
        (self.source / "SKILL.md").write_bytes(b"---\nname: github-reuse-first\ndescription: Reuse projects.\n---\nVersion one.\n")
        (self.package / "rules").mkdir()
        self.template = self.package / "rules" / "AGENTS.github-reuse.md"
        self.template.write_bytes(RULE_V1)
        self.destination = self.home / ".agents" / "skills" / "github-reuse-first"
        self.rules = self.home / ".codex" / "AGENTS.md"
        self.addCleanup(patch.stopall)
        patch.object(installer.Path, "home", return_value=self.home).start()
        patch.dict(os.environ, {}, clear=True).start()

    def call(self, **kwargs):
        return installer.install(self.package, **kwargs)

    def test_fresh_global_then_repeat_is_noop(self):
        result = self.call()
        self.assertEqual((self.destination / "SKILL.md").read_bytes(), (self.source / "SKILL.md").read_bytes())
        self.assertEqual(self.rules.read_bytes(), RULE_V1)
        self.assertEqual(result["backups"], [])
        modified_at = self.rules.stat().st_mtime_ns
        result = self.call()
        self.assertFalse(result["skill_changed"])
        self.assertFalse(result["rule_changed"])
        self.assertEqual(result["backups"], [])
        self.assertEqual(self.rules.stat().st_mtime_ns, modified_at)
        self.assertFalse(list(self.home.rglob("*.bak-*")))

    def test_preserves_bom_crlf_and_unrelated_rules_on_update(self):
        self.rules.parent.mkdir()
        original = b"\xef\xbb\xbf# My rules\r\nKeep exact bytes.\r\n"
        self.rules.write_bytes(original)
        first = self.call()
        self.assertEqual(Path(first["backups"][0]).read_bytes(), original)
        installed = self.rules.read_bytes()
        self.assertTrue(installed.startswith(original))
        self.assertNotIn(b"\n", installed.replace(b"\r\n", b""))
        suffix = b"\r\n## Another section\r\nLeave me unchanged.\r\n"
        self.rules.write_bytes(installed + suffix)
        self.template.write_bytes(RULE_V2)
        self.call()
        current = self.rules.read_bytes()
        self.assertTrue(current.startswith(original))
        self.assertTrue(current.endswith(suffix))
        self.assertEqual(current.count(installer.START), 1)
        self.assertIn(b"substantial features", current)

    def test_nonempty_override_is_active_and_codex_home_is_respected(self):
        custom = self.root / "custom profile"
        custom.mkdir()
        os.environ["CODEX_HOME"] = str(custom)
        override = custom / "AGENTS.override.md"
        normal = custom / "AGENTS.md"
        override.write_bytes(b"Override rules.\n")
        normal.write_bytes(b"Normal rules.\n")
        result = self.call()
        self.assertEqual(Path(result["rule_path"]), override)
        self.assertIn(installer.START, override.read_bytes())
        self.assertEqual(normal.read_bytes(), b"Normal rules.\n")
        self.assertTrue(self.destination.is_dir())
        self.assertFalse((self.home / ".codex").exists())

    def test_project_scope_uses_existing_override_and_keeps_global_untouched(self):
        cases = (
            ("missing", None),
            ("empty", b""),
            ("ascii whitespace", b" \t\r\n"),
            ("unicode whitespace", "\u3000\u00a0\n".encode("utf-8")),
            ("BOM only", b"\xef\xbb\xbf"),
            ("BOM and whitespace", b"\xef\xbb\xbf \r\n"),
        )
        for index, (label, previous) in enumerate(cases):
            with self.subTest(override=label):
                project = self.root / ("项目 with spaces " + str(index))
                project.mkdir()
                override = project / "AGENTS.override.md"
                normal = project / "AGENTS.md"
                normal.write_bytes(b"Existing project rules.\n")
                if previous is not None:
                    override.write_bytes(previous)
                result = self.call(project=project)
                expected = override if previous is not None else normal
                self.assertEqual(Path(result["rule_path"]), expected)
                self.assertIn(installer.START, expected.read_bytes())
                if previous is not None:
                    self.assertTrue(override.read_bytes().startswith(previous))
                    self.assertEqual(normal.read_bytes(), b"Existing project rules.\n")
                    self.assertEqual(Path(result["backups"][0]).read_bytes(), previous)
                self.assertTrue((project / ".agents/skills/github-reuse-first/SKILL.md").is_file())
        self.assertFalse(self.rules.exists())
        self.assertFalse(self.destination.exists())

    def test_global_unicode_whitespace_override_keeps_normal_rules_active(self):
        self.rules.parent.mkdir()
        override = self.rules.parent / "AGENTS.override.md"
        blank = " \t\r\n\u0085\u00a0\u1680\u2000\u2007\u2028\u2029\u202f\u205f\u3000".encode("utf-8")
        override.write_bytes(blank)
        original = b"Existing global rules.\n"
        self.rules.write_bytes(original)
        result = self.call()
        self.assertEqual(Path(result["rule_path"]), self.rules)
        self.assertEqual(override.read_bytes(), blank)
        self.assertTrue(self.rules.read_bytes().startswith(original))
        self.assertIn(installer.START, self.rules.read_bytes())
        self.assertEqual(Path(result["backups"][0]).read_bytes(), original)

    def test_global_bom_only_override_receives_rules_and_preserves_bom(self):
        self.rules.parent.mkdir()
        override = self.rules.parent / "AGENTS.override.md"
        override.write_bytes(b"\xef\xbb\xbf")
        original = b"Existing global rules.\n"
        self.rules.write_bytes(original)
        result = self.call()
        self.assertEqual(Path(result["rule_path"]), override)
        self.assertTrue(override.read_bytes().startswith(b"\xef\xbb\xbf"))
        self.assertIn(installer.START, override.read_bytes())
        self.assertEqual(self.rules.read_bytes(), original)
        self.assertEqual(Path(result["backups"][0]).read_bytes(), b"\xef\xbb\xbf")
        repeat = self.call()
        self.assertFalse(repeat["skill_changed"])
        self.assertFalse(repeat["rule_changed"])

    def test_global_c0_separators_are_content_under_rust_whitespace_rules(self):
        for codepoint in range(0x1c, 0x20):
            with self.subTest(codepoint=codepoint):
                profile = self.root / ("C0 profile " + str(codepoint))
                profile.mkdir()
                os.environ["CODEX_HOME"] = str(profile)
                override = profile / "AGENTS.override.md"
                override.write_bytes(bytes([codepoint]))
                normal = profile / "AGENTS.md"
                normal.write_bytes(b"Existing global rules.\n")
                result = self.call()
                self.assertEqual(Path(result["rule_path"]), override)
                self.assertIn(installer.START, override.read_bytes())
                self.assertEqual(normal.read_bytes(), b"Existing global rules.\n")

    def test_changed_skill_is_backed_up_and_updated_by_default(self):
        self.call()
        old = (self.destination / "SKILL.md").read_bytes()
        (self.source / "SKILL.md").write_bytes(old + b"Version two.\n")
        rule_before = self.rules.read_bytes()
        result = self.call()
        self.assertEqual(len(result["backups"]), 1)
        self.assertEqual((Path(result["backups"][0]) / "SKILL.md").read_bytes(), old)
        self.assertEqual(Path(result["backups"][0]).parent, self.home / ".agents" / "skill-backups")
        self.assertEqual(len(list(self.destination.parent.rglob("SKILL.md"))), 1)
        self.assertEqual((self.destination / "SKILL.md").read_bytes(), old + b"Version two.\n")
        self.assertEqual(self.rules.read_bytes(), rule_before)

    def test_dry_run_writes_nothing(self):
        result = self.call(dry_run=True)
        self.assertTrue(result["skill_changed"])
        self.assertTrue(result["rule_changed"])
        self.assertEqual(list(self.home.iterdir()), [])

    def test_bad_markers_fail_before_any_skill_write(self):
        self.rules.parent.mkdir()
        for malformed in (installer.START + b"\nMissing end.\n", RULE_V1 + RULE_V1,
                          installer.END + b"\n" + installer.START,
                          b"<!-- github-reuse-first:star -->\nDamaged marker.\n",
                          b"<!-- github-reuse-first :start -->\nDamaged marker.\n"):
            with self.subTest(malformed=malformed):
                self.rules.write_bytes(malformed)
                with self.assertRaises(installer.InstallError):
                    self.call()
                self.assertEqual(self.rules.read_bytes(), malformed)
                self.assertFalse(self.destination.exists())
                self.assertFalse(list(self.home.rglob("*.bak-*")))

    def test_symlink_and_source_overlap_are_rejected(self):
        outside = self.root / "outside"
        outside.mkdir()
        self.rules.parent.mkdir()
        target = outside / "rules.md"
        target.write_bytes(b"Do not change.\n")
        try:
            self.rules.symlink_to(target)
        except (OSError, NotImplementedError):
            self.skipTest("Symlink creation is unavailable on this host.")
        with self.assertRaises(installer.InstallError):
            self.call()
        self.assertEqual(target.read_bytes(), b"Do not change.\n")
        self.assertFalse(self.destination.exists())
        self.rules.unlink()
        with self.assertRaises(installer.InstallError):
            self.call(project=self.source)
        self.assertFalse((self.source / ".agents").exists())

    def test_rule_write_failure_rolls_back_skill_update(self):
        self.call()
        previous = (self.destination / "SKILL.md").read_bytes()
        (self.source / "SKILL.md").write_bytes(previous + b"New content.\n")
        self.template.write_bytes(RULE_V2)
        original_rule = self.rules.read_bytes()
        with patch.object(installer, "atomic_write", side_effect=OSError("simulated write failure")):
            with self.assertRaises(OSError):
                self.call(update=True)
        self.assertEqual((self.destination / "SKILL.md").read_bytes(), previous)
        self.assertEqual(self.rules.read_bytes(), original_rule)


if __name__ == "__main__":
    unittest.main()
