"""
Unit tests for the bump-version.js script.

Run tests with:
    pytest tests/test_bump_version.py
    pytest tests/test_bump_version.py -v  # verbose
"""

import json
import os
import re
import subprocess
import tempfile
from pathlib import Path


class TestBumpVersion:
    """Tests for the version bump script."""

    def setup_method(self):
        """Create a temporary project structure for testing."""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name)

        # Create directory structure
        dirs = [
            "frontend",
            "desktop/frontend",
            "desktop/src-tauri",
            "backend",
            "desktop/frontend/src/app/startup",
            "desktop/frontend/messages",
        ]
        for d in dirs:
            (self.root / d).mkdir(parents=True, exist_ok=True)

        # Create sample files with version 0.1.0
        self._write_json("frontend/package.json", {"name": "web", "version": "0.1.0"})
        self._write_json("desktop/frontend/package.json", {"name": "desktop", "version": "0.1.0"})
        self._write_json("desktop/frontend/package-lock.json", {"name": "desktop", "version": "0.1.0", "packages": {}})
        self._write_json("desktop/src-tauri/tauri.conf.json", {"version": "0.1.0", "build": {}})
        self._write_toml("desktop/src-tauri/Cargo.toml", '[package]\nname = "app"\nversion = "0.1.0"\nedition = "2021"\n')
        self._write_toml("backend/pyproject.toml", '[project]\nname = "backend"\nversion = "0.1.0"\n')
        self._write_tsx("desktop/frontend/src/app/startup/page.tsx", 'const version = "v0.1.0";\n')
        self._write_json("desktop/frontend/messages/en.json", {"version": "0.1.0", "app.title": "App"})
        self._write_json("desktop/frontend/messages/it.json", {"version": "0.1.0", "app.title": "App"})

    def teardown_method(self):
        self.temp_dir.cleanup()

    def _write_json(self, rel_path, data):
        with open(self.root / rel_path, "w") as f:
            json.dump(data, f, indent=2)

    def _write_toml(self, rel_path, content):
        with open(self.root / rel_path, "w") as f:
            f.write(content)

    def _write_tsx(self, rel_path, content):
        with open(self.root / rel_path, "w") as f:
            f.write(content)

    def _run_script(self, version):
        """Run bump-version.js in the temp directory."""
        script_path = Path(__file__).parent.parent / "scripts" / "bump-version.js"
        result = subprocess.run(
            ["node", str(script_path), version],
            capture_output=True,
            text=True,
            cwd=str(self.root),
        )
        return result

    def test_bump_all_files(self):
        """Test that all files are updated to the new version."""
        result = self._run_script("1.2.3")
        assert result.returncode == 0, f"Script failed: {result.stderr}"

        # Verify each file
        assert json.load(open(self.root / "frontend/package.json"))["version"] == "1.2.3"
        assert json.load(open(self.root / "desktop/frontend/package.json"))["version"] == "1.2.3"
        assert json.load(open(self.root / "desktop/frontend/package-lock.json"))["version"] == "1.2.3"
        assert json.load(open(self.root / "desktop/src-tauri/tauri.conf.json"))["version"] == "1.2.3"

        cargo = open(self.root / "desktop/src-tauri/Cargo.toml").read()
        assert re.search(r'^version = "1\.2\.3"', cargo, re.MULTILINE)

        pyproject = open(self.root / "backend/pyproject.toml").read()
        assert re.search(r'^version = "1\.2\.3"', pyproject, re.MULTILINE)

        tsx = open(self.root / "desktop/frontend/src/app/startup/page.tsx").read()
        assert "v1.2.3" in tsx

        assert json.load(open(self.root / "desktop/frontend/messages/en.json"))["version"] == "1.2.3"
        assert json.load(open(self.root / "desktop/frontend/messages/it.json"))["version"] == "1.2.3"

    def test_missing_version_argument(self):
        """Test that script fails without version argument."""
        result = self._run_script("")
        assert result.returncode != 0

    def test_invalid_semver(self):
        """Test that script rejects invalid semver strings."""
        result = self._run_script("invalid")
        assert result.returncode != 0
        assert "not a valid semver" in result.stderr

    def test_missing_files_are_skipped(self):
        """Test that missing files are skipped gracefully."""
        # Remove one file
        os.remove(self.root / "desktop/frontend/messages/it.json")
        result = self._run_script("2.0.0")
        assert result.returncode == 0
        # Other files should still be updated
        assert json.load(open(self.root / "frontend/package.json"))["version"] == "2.0.0"


if __name__ == "__main__":
    subprocess.run(["pytest", __file__, "-v"])
