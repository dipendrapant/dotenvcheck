import pathlib

from envguard.cli import main


def test_cli_missing_then_fixed(tmp_path: pathlib.Path):
    # Project with one missing var
    (tmp_path / "app.py").write_text(
        "import os\nURL=os.getenv('DATABASE_URL')\nKEY=os.getenv('SECRET_KEY')\n",
        encoding="utf-8",
    )
    (tmp_path / ".env").write_text('DATABASE_URL="postgres://localhost"\n', encoding="utf-8")

    # default policy fails on missing/typos -> expect 1
    assert main([str(tmp_path)]) == 1

    # Add the missing var -> expect clean (exit 0)
    with (tmp_path / ".env").open("a", encoding="utf-8") as f:
        f.write('SECRET_KEY="s3cr3t"\n')

    assert main([str(tmp_path)]) == 0
