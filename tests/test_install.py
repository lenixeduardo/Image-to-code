"""Contract and integration tests for the multi-agent installer (no agent CLI needed)."""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

SCRIPT = Path(__file__).resolve().parents[1] / "scripts/install.py"
spec = importlib.util.spec_from_file_location("skill_install", SCRIPT)
installer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(installer)


class MultiAgentInstallerTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.source = self.root / "source"
        self.source.mkdir()
        (self.source / "SKILL.md").write_text("---\nname: image-to-code\ndescription: Convert an image to code\n---\n\n# Image to Code\n", encoding="utf-8")
        (self.source / "LICENSE").write_text("MIT", encoding="utf-8")
        (self.source / "references").mkdir()
        (self.source / "references" / "about.md").write_text("Reference", encoding="utf-8")
        (self.source / "scripts").mkdir()
        (self.source / "scripts" / "example.py").write_text("print('safe')", encoding="utf-8")
        (self.source / "scripts" / "__pycache__").mkdir()
        (self.source / "scripts" / "__pycache__" / "compiled.pyc").write_bytes(b"garbage")
        self.project = self.root / "project"
        self.project.mkdir()

    def run_cli(self, *args):
        return subprocess.run([sys.executable, str(SCRIPT), "--source", str(self.source),
                               "--project", str(self.project), *args],
                              capture_output=True, text=True, check=False)

    def test_freebuff_codex_and_generic_share_portable_skill(self):
        result = self.run_cli("--agent", "freebuff,codex,generic")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout.count("Installed:"), 1)
        dest = self.project / ".agents/skills/image-to-code"
        self.assertTrue((dest / "SKILL.md").exists())
        self.assertTrue((dest / "references/about.md").exists())
        self.assertFalse((dest / "scripts/__pycache__").exists())
        self.assertEqual(self.run_cli("--agent", "freebuff,codex", "--verify").returncode, 0)

    def test_all_agents_install_in_six_distinct_paths(self):
        result = self.run_cli("--agent", "all")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout.count("Installed:"), 6)
        for location in [".agents", ".claude", ".opencode", ".hermes", ".cursor", ".gemini"]:
            self.assertTrue((self.project / location / "skills/image-to-code/SKILL.md").exists(), location)
        self.assertEqual(self.run_cli("--agent", "all", "--verify").returncode, 0)

    def test_dry_run_does_not_write(self):
        result = self.run_cli("--agent", "claude", "--dry-run")
        self.assertEqual(result.returncode, 0)
        self.assertIn("WOULD INSTALL", result.stdout)
        self.assertFalse((self.project / ".claude").exists())

    def test_existing_installation_not_overwritten_without_force(self):
        self.assertEqual(self.run_cli("--agent", "claude").returncode, 0)
        target = self.project / ".claude/skills/image-to-code/SKILL.md"
        target.write_text("custom user edits")
        failure = self.run_cli("--agent", "claude")
        self.assertNotEqual(failure.returncode, 0)
        self.assertEqual(target.read_text(), "custom user edits")
        verified = self.run_cli("--agent", "claude", "--verify")
        self.assertNotEqual(verified.returncode, 0)
        self.assertIn("changed: SKILL.md", verified.stdout)
        restored = self.run_cli("--agent", "claude", "--force")
        self.assertEqual(restored.returncode, 0, restored.stderr)
        backups = list(target.parent.parent.glob("image-to-code.backup-*"))
        self.assertEqual(len(backups), 1)
        self.assertEqual((backups[0] / "SKILL.md").read_text(), "custom user edits")
        self.assertEqual(self.run_cli("--agent", "claude", "--verify").returncode, 0)

    def test_unknown_agent_fails_without_creating_files(self):
        error = self.run_cli("--agent", "foobar")
        self.assertNotEqual(error.returncode, 0)
        self.assertIn("Unknown agent", error.stderr)
        self.assertEqual(list(self.project.iterdir()), [])

    def test_hermes_project_displays_trust_step(self):
        result = self.run_cli("--agent", "hermes")
        self.assertEqual(result.returncode, 0)
        self.assertIn("hermes skills trust", result.stdout)

    def test_paths_global_and_project(self):
        home = self.root / "home"
        with patch.dict("os.environ", {"XDG_CONFIG_HOME": str(self.root / "xdg")}):
            paths = installer.paths_for(["claude", "opencode", "freebuff", "hermes", "gemini"], "global", self.project, home)
        found = {name: path for path, names in paths for name in names}
        self.assertEqual(found["claude"], home / ".claude/skills/image-to-code")
        self.assertEqual(found["freebuff"], home / ".agents/skills/image-to-code")
        self.assertEqual(found["opencode"], self.root / "xdg/opencode/skills/image-to-code")
        self.assertEqual(found["hermes"], home / ".hermes/skills/image-to-code")
        self.assertEqual(found["gemini"], home / ".gemini/skills/image-to-code")

    def test_rejects_untrusted_symlinks(self):
        target = self.source / "assets"
        target.mkdir()
        file = self.root / "private.txt"
        file.write_text("secret")
        try:
            (target / "bad-link.txt").symlink_to(file)
        except (OSError, NotImplementedError):
            self.skipTest("symlinks not supported on this platform")
        result = self.run_cli("--agent", "claude")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("symlink", result.stderr.lower())

    def test_missing_project_is_not_created(self):
        result = subprocess.run([sys.executable, str(SCRIPT), "--source", str(self.source),
                                 "--project", str(self.root / "missing"), "--agent", "claude"],
                                capture_output=True, text=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertFalse((self.root / "missing").exists())


if __name__ == "__main__":
    unittest.main()
