import pathlib

from envguard.scanner import scan_project


def test_scan_project_used_declared_missing(tmp_path: pathlib.Path):
    (tmp_path / "main.py").write_text(
        "import os\nA=os.getenv('A')\nB=os.environ.get('B')\nC=os.environ['C']\n",
        encoding="utf-8",
    )
    envf = tmp_path / ".env"
    envf.write_text("A=1\nB=2\n", encoding="utf-8")

    f = scan_project(
        root=tmp_path,
        dotenv_path=envf,
        compose_path=None,
        include_glob="*.py",
        exclude_globs=[],
    )

    assert f.used.issuperset({"A", "B", "C"})
    assert "C" in f.missing
    assert "A" in f.declared and "B" in f.declared
