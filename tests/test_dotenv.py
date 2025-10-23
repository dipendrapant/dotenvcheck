import pathlib

from envguard.dotenv import load_dotenv_vars


def test_dotenv_parsing_and_bad_values(tmp_path: pathlib.Path):
    p = tmp_path / ".env"
    p.write_text(
        "# comment\n"
        "FOO=bar\n"
        "BAR=\"baz\"\n"
        "UNBAL='oops\n"  # unbalanced quote
        "SPC=  value\n",  # leading spaces in value
        encoding="utf-8",
    )

    env, bad = load_dotenv_vars(p)
    assert env["FOO"] == "bar"
    assert env["BAR"] == "baz"
    assert "UNBAL" in bad
    assert "SPC" in bad

def test_balanced_quotes_not_flagged(tmp_path: pathlib.Path):
    p = tmp_path / ".env"
    p.write_text('QUOTED="ok"\nSQUOTE=\'ok2\'\n', encoding="utf-8")
    env, bad = load_dotenv_vars(p)
    assert env["QUOTED"] == "ok"
    assert env["SQUOTE"] == "ok2"
    assert bad == []
