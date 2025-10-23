import json
import pathlib

from envguard.cli import main


def test_cli_skips_common_venv_vendor_dirs_by_default(tmp_path: pathlib.Path, capsys):
    # Simulate a virtualenv/vendor file that references a var we don't want to see
    pkg_dir = tmp_path / ".venv" / "lib" / "python3.12" / "site-packages"
    pkg_dir.mkdir(parents=True)
    (pkg_dir / "vendormod.py").write_text(
        "import os\nV=os.getenv('VENV_SHOULD_NOT_APPEAR')\n", encoding="utf-8"
    )

    # Real app code references FOO only; .env defines it
    (tmp_path / "app.py").write_text("import os\nx=os.getenv('FOO')\n", encoding="utf-8")
    (tmp_path / ".env").write_text("FOO=1\n", encoding="utf-8")

    # Run with JSON for easy assertions (no explicit --exclude)
    code = main([str(tmp_path), "--json"])
    out = capsys.readouterr().out
    data = json.loads(out)

    # Should not include the venv var in "used" or "missing"
    assert "VENV_SHOULD_NOT_APPEAR" not in data["used"]
    assert "VENV_SHOULD_NOT_APPEAR" not in data["missing"]
    assert code == 0
