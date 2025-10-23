from __future__ import annotations

import pathlib
import re
from typing import Dict, List, Tuple

ENV_LINE = re.compile(
    r"""
    ^\s*
    (?:export\s+)?                     # optional 'export '
    (?P<key>[A-Za-z_][A-Za-z0-9_]*)    # KEY
    \s*=
    (?P<val_ws>[ \t]*)                 # whitespace immediately after '=' (spaces/tabs only)
    (?P<val_body>.*)                   # remainder of the value (raw body)
    \s*$
    """,
    re.VERBOSE,
)


def parse_line(line: str):
    """
    Returns (key, normalized_value, val_body, had_leading_ws) or None.

    - normalized_value: trimmed; strips balanced surrounding quotes (single/double).
    - val_body: raw value body (without the immediate post '=' whitespace).
    - had_leading_ws: True if there were spaces/tabs immediately after '='.
    """
    s = line.strip()
    if not s or s.startswith("#"):
        return None
    m = ENV_LINE.match(line)
    if not m:
        return None

    key = m.group("key")
    val_ws = m.group("val_ws")
    val_body = m.group("val_body")

    had_leading_ws = bool(val_ws)

    norm = val_body.strip()
    if len(norm) >= 2 and (
        (norm.startswith('"') and norm.endswith('"')) or
        (norm.startswith("'") and norm.endswith("'"))
    ):
        norm = norm[1:-1]

    return key, norm, val_body, had_leading_ws


def load_dotenv_vars(path: pathlib.Path) -> Tuple[Dict[str, str], List[str]]:
    """
    Returns (vars, bad_values_keys).

    'bad' includes:
      - leading whitespace immediately after '=', e.g. KEY=<space>value
      - unbalanced surrounding quotes in the raw value body, e.g. KEY="oops
    """
    env: Dict[str, str] = {}
    bad: List[str] = []

    if not path or not path.exists():
        return env, bad

    for i, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        parsed = parse_line(line)
        if not parsed:
            continue

        k, normalized, val_body, had_leading_ws = parsed
        env[k] = normalized

        if had_leading_ws:
            bad.append(k)
            continue

        body_stripped = val_body.strip()
        if body_stripped.startswith(("'", '"')):
            q = body_stripped[0]
            if not body_stripped.endswith(q):
                bad.append(k)

    return env, bad
