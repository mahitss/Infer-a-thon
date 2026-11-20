#!/usr/bin/env python3
"""Pure Compose lifecycle policy helpers (M001.3.3). No Docker is invoked."""
import re

CACHE_VOLUME_KEY = "sie-hf-cache"


def cache_volume_name(compose_config, project):
    """Resolve the effective cache volume name for a given Compose project.

    An explicit `name:` on the top-level volume wins, so the same cache is
    reused regardless of the ephemeral Compose project name. Without it,
    Compose would create `<project>_<key>`, accumulating unused caches.
    """
    if not isinstance(compose_config, dict):
        raise ValueError("compose config must be a dict")
    volumes = compose_config.get("volumes") or {}
    if not isinstance(volumes, dict):
        raise ValueError("compose 'volumes' must be a mapping")
    entry = volumes.get(CACHE_VOLUME_KEY)
    if entry is None:
        raise ValueError(f"missing top-level volume '{CACHE_VOLUME_KEY}'")
    if isinstance(entry, dict) and isinstance(entry.get("name"), str) and entry["name"].strip():
        return entry["name"].strip()
    return f"{project}_{CACHE_VOLUME_KEY}"


def teardown_deletes_volumes(command_line):
    """True if a teardown command would remove volumes (unsafe for our cache)."""
    if not isinstance(command_line, str):
        raise ValueError("command_line must be a string")
    return bool(re.search(r"(?:^|\s)(?:-v|--volumes)(?:\s|$)|volume\s+(?:rm|prune)\b", command_line))


def cleanup_is_isolated(command_line, project):
    """True if a teardown command targets the given isolated project."""
    return isinstance(command_line, str) and f"-p {project}" in command_line
