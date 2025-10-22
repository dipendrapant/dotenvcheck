from __future__ import annotations
import pathlib
from typing import Dict, List, Tuple

from .scanner import Findings


def to_console(f: Findings, base_dir: pathlib.Path):
    print("== envguard report ==")
    if f.missing:
        print(f"missing ({len(f.missing)}): " + ", ".join(sorted(set(f.missing))))
    if f.unused:
        print(f"unused ({len(f.unused)}): " + ", ".join(sorted(set(f.unused))))
    if f.typos:
        pairs = [f"{a}->{b}" for a, b in f.typos]
        print(f"typos ({len(f.typos)}): " + ", ".join(pairs))
    if f.bad_values:
        print(f"suspicious ({len(f.bad_values)}): " + ", ".join(sorted(set(f.bad_values))))

    if f.sources:
        print("\nsources:")
        for k in sorted(f.sources.keys()):
            locs = ", ".join(f.sources[k])
            print(f"  {k}: {locs}")

    if not (f.missing or f.unused or f.typos or f.bad_values):
        print("No issues found.")


def to_json(f: Findings):
    return {
        "used": sorted(f.used),
        "declared": sorted(f.declared),
        "missing": f.missing,
        "unused": f.unused,
        "typos": f.typos,
        "bad_values": f.bad_values,
        "sources": f.sources,
    }
