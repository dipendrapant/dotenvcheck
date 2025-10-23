import json
import pathlib

from envguard.cli import main


def test_cli_json_shape(tmp_path: pathlib.Path, capsys):
    (tmp_path / "app.py").write_text("import os\nx=os.getenv('FOO')\n", encoding="utf-8")
    (tmp_path / ".env").write_text("FOO=1\n", encoding="utf-8")

    code = main([str(tmp_path), "--json"])
    out = capsys.readouterr().out
    data = json.loads(out)

    # Ensure expected keys exist
    for key in ("used", "declared", "missing", "unused", "typos", "bad_values", "sources"):
        assert key in data

    assert code == 0
