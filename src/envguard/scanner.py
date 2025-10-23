from __future__ import annotations

import ast
import pathlib
import re
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set, Tuple

from .compose import load_compose_env_names
from .dotenv import load_dotenv_vars


class EnvUsageVisitor(ast.NodeVisitor):
    """
    Collects environment variable names used via:
      - os.getenv("NAME")
      - os.environ["NAME"]
      - os.environ.get("NAME")
    """

    def __init__(self) -> None:
        self.used: Set[str] = set()

    def _const_str(self, node):
        # Py3.8+ Constant
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            return node.value
        # For old AST forms (rare on modern Python)
        if isinstance(node, ast.Str):
            return node.s
        return None

    def visit_Call(self, node: ast.Call):
        # os.getenv("FOO") OR os.environ.get("FOO")
        func_attr = getattr(node.func, "attr", None)
        func_value_attr = getattr(getattr(node.func, "value", None), "attr", None)

        # os.getenv
        if func_attr == "getenv":
            if node.args:
                name = self._const_str(node.args[0])
                if name:
                    self.used.add(name)

        # os.environ.get
        if func_attr == "get" and func_value_attr == "environ":
            if node.args:
                name = self._const_str(node.args[0])
                if name:
                    self.used.add(name)

        self.generic_visit(node)

    def visit_Subscript(self, node: ast.Subscript):
        # os.environ["FOO"]
        value_attr = getattr(node.value, "attr", None)
        if value_attr == "environ":
            key = None
            # slice could be Constant or Index(Constant) depending on Python
            if hasattr(node, "slice"):
                sl = node.slice
                if isinstance(sl, ast.Constant) and isinstance(sl.value, str):
                    key = sl.value
                elif hasattr(ast, "Index") and isinstance(sl, ast.Index):
                    if isinstance(sl.value, ast.Constant) and isinstance(sl.value.value, str):
                        key = sl.value.value
                    elif isinstance(sl.value, ast.Str):
                        key = sl.value.s
                elif isinstance(sl, ast.Str):
                    key = sl.s
            if key:
                self.used.add(key)
        self.generic_visit(node)


@dataclass
class Findings:
    used: Set[str] = field(default_factory=set)
    declared: Set[str] = field(default_factory=set)
    missing: List[str] = field(default_factory=list)
    unused: List[str] = field(default_factory=list)
    typos: List[Tuple[str, str]] = field(default_factory=list)
    bad_values: List[str] = field(default_factory=list)
    sources: Dict[str, List[str]] = field(default_factory=dict)  


def iter_code_files(root: pathlib.Path, include_glob: str, exclude_globs: List[str]):
    excludes = [root / g for g in exclude_globs]
    noisy_segments = {"site-packages", "dist-packages"}
    venv_like = {".venv", "venv", "env"}

    def is_excluded_path(path: pathlib.Path) -> bool:
        for ex in excludes:
            try:
                path.relative_to(ex); return True
            except Exception:
                pass
        if any(seg in noisy_segments for seg in path.parts): return True
        if any(seg in venv_like for seg in path.parts): return True
        return False

    venv_roots = {p.parent.resolve() for p in root.rglob("pyvenv.cfg")}
    for p in root.rglob(include_glob):
        if any(vr in p.parents for vr in venv_roots): continue
        if is_excluded_path(p): continue
        if p.is_file(): yield p


def collect_used_env_names(root: pathlib.Path, include_glob: str, exclude_globs: List[str]) -> Set[str]:
    used: Set[str] = set()
    for f in iter_code_files(root, include_glob, exclude_globs):
        try:
            text = f.read_text(encoding="utf-8")
        except Exception:
            continue
        try:
            tree = ast.parse(text, filename=str(f))
        except SyntaxError:
            continue
        try:
            v = EnvUsageVisitor()
            v.visit(tree)
            used |= v.used
        except Exception: # any unexpected AST quirk: skip this file instead of crashing
            continue
    return used


def levenshtein_close(a: str, b: str) -> bool:
    a2, b2 = a.lower(), b.lower()
    if a2 == b2:
        return False
    if abs(len(a2) - len(b2)) > 2:
        return False
    # common prefix length
    pref = 0
    for x, y in zip(a2, b2):
        if x == y:
            pref += 1
        else:
            break
    # consider close if 80% prefix match or names differ by up to 2 chars
    return pref >= max(len(a2), len(b2)) * 0.8 or (a2 in b2 or b2 in a2)


def scan_project(
    root: pathlib.Path,
    dotenv_path: Optional[pathlib.Path],
    compose_path: Optional[pathlib.Path],
    include_glob: str,
    exclude_globs: List[str],
) -> Findings:
    used = collect_used_env_names(root, include_glob, exclude_globs)

    dotenv_vars, bad_values = load_dotenv_vars(dotenv_path) if dotenv_path else ({}, [])
    compose_names, compose_srcs = load_compose_env_names(compose_path) if compose_path else (set(), {})

    declared_names = set(dotenv_vars.keys()) | compose_names

    missing = sorted(used - declared_names)
    unused = sorted(declared_names - used)

    # typo candidates
    typos = []
    for name in missing:
        for d in declared_names:
            if levenshtein_close(name, d):
                typos.append((name, d))
                break

    sources = {}
    for k in dotenv_vars.keys():
        sources.setdefault(k, []).append(str(dotenv_path))
    for k, locs in compose_srcs.items():
        sources.setdefault(k, []).extend(locs)

    return Findings(
        used=used,
        declared=declared_names,
        missing=missing,
        unused=unused,
        typos=typos,
        bad_values=bad_values,
        sources=sources,
    )
