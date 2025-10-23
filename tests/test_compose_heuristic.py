import pathlib

from envguard.scanner import scan_project


def test_compose_list_heuristic_without_pyyaml(tmp_path: pathlib.Path):
    # Compose with env list entries that the heuristic can detect
    dc = tmp_path / "docker-compose.yml"
    dc.write_text(
        "version: '3.8'\n"
        "services:\n"
        "  web:\n"
        "    image: demo\n"
        "    environment:\n"
        "      - PORT=8080\n"
        "      - DEBUG=true\n",
        encoding="utf-8",
    )

    (tmp_path / "app.py").write_text(
        "import os\np=os.getenv('PORT'); d=os.getenv('DEBUG')\n", encoding="utf-8"
    )
    envf = tmp_path / ".env"
    envf.write_text("", encoding="utf-8")

    f = scan_project(
        root=tmp_path,
        dotenv_path=envf,
        compose_path=dc,
        include_glob="*.py",
        exclude_globs=[],
    )

    # Compose should contribute declared names
    assert "PORT" in f.declared and "DEBUG" in f.declared
    assert "PORT" not in f.missing and "DEBUG" not in f.missing
