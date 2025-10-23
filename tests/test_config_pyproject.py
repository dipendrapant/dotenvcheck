import pathlib

from envguard.cli import main


def test_pyproject_config_changes_fail_policy(tmp_path: pathlib.Path):
    # App uses only API_KEY; .env also has UNUSED -> will be "unused"
    (tmp_path / "app.py").write_text("import os\nk=os.getenv('API_KEY')\n", encoding="utf-8")
    (tmp_path / ".env").write_text("API_KEY=abc\nUNUSED=1\n", encoding="utf-8")

    # Set project policy to fail on UNUSED only
    (tmp_path / "pyproject.toml").write_text(
        "[tool.envguard]\nfail_on = ['unused']\n", encoding="utf-8"
    )

    # With policy, unused should cause non-zero exit
    assert main([str(tmp_path)]) == 1
