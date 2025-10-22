from __future__ import annotations
import pathlib
import re
from typing import Dict, List, Tuple

ENV_LINE = re.compile(r"""
    ^\s*
    (?:export\s+)?                # allow optional 'export '
    (?P<key>[A-Za-z_][A-Za-z0-9_]*)
    \s*=\s*
    (?P<val>.*?)
    \s*$
""", re.VERBOSE)

QUOTE_UNBALANCED = re.compile(r"""^(['"]).*[^'"]$""")

def parse_line(line: str):
    if not line.strip():
        return None
    if line.strip().startswith("#"):
        return None
    m = ENV_LINE.match(line)
    if not m:
        return None
    key = m.group("key")
    val = m.group("val").strip()
    # strip quotes if balanced
    if (val.startswith("'") and val.endswith("'")) or (val.startswith('"') and val.endswith('"')):
        val = val[1:-1]
    return key, val


def load_dotenv_vars(path: pathlib.Path) -> Tuple[Dict[str, str], List[str]]:
    """
    Returns (vars, bad_values_keys)
    bad_values_keys includes unbalanced quotes or suspicious leading spaces.
    """
    env: Dict[str, str] = {}
    bad: List[str] = []

    if not path or not path.exists():
        return env, bad

    for i, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        parsed = parse_line(line)
        if not parsed:
            continue
        k, v = parsed
        env[k] = v
        if v.startswith(" ") or QUOTE_UNBALANCED.match(line.strip()):
            bad.append(k)

    return env, bad
