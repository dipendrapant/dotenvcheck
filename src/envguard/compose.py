from __future__ import annotations
import pathlib
from typing import Dict, List, Set, Tuple

def _try_yaml_parse(compose_path: pathlib.Path):
    try:
        import yaml  # type: ignore
    except Exception:
        return None
    try:
        with compose_path.open("r", encoding="utf-8") as f:
            return yaml.safe_load(f)
    except Exception:
        return None


def load_compose_env_names(compose_path: pathlib.Path | None) -> Tuple[Set[str], Dict[str, List[str]]]:
    """
    Returns (names, sources_map)
    sources_map[var] -> [ 'docker-compose.yml:service:ENV_NAME', ... ]
    Falls back to a minimal heuristic if PyYAML is unavailable.
    """
    names: Set[str] = set()
    sources: Dict[str, List[str]] = {}
    if not compose_path or not compose_path.exists():
        return names, sources

    data = _try_yaml_parse(compose_path)
    if data is not None and isinstance(data, dict):
        services = data.get("services", {})
        for svc_name, svc in (services or {}).items():
            env_section = (svc or {}).get("environment")
            if isinstance(env_section, dict):
                for k in env_section.keys():
                    names.add(k)
                    sources.setdefault(k, []).append(f"{compose_path.name}:{svc_name}:{k}")
            elif isinstance(env_section, list):
                for item in env_section:
                    # item can be "KEY=value" or just "KEY"
                    if isinstance(item, str) and item:
                        k = item.split("=", 1)[0]
                        names.add(k)
                        sources.setdefault(k, []).append(f"{compose_path.name}:{svc_name}:{k}")
        return names, sources

    # Fallback heuristic: very loose scan (no dependency)
    for line in compose_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        # accept patterns like "- FOO=bar" or "FOO=bar" under environment sections — heuristic only
        if "=" in line:
            candidate = line.lstrip("-").strip()
            key = candidate.split("=", 1)[0].strip()
            if key.isidentifier() or key.replace("_", "").isalnum():
                names.add(key)
                sources.setdefault(key, []).append(f"{compose_path.name}:{key}")
    return names, sources
