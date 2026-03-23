#!/usr/bin/env python3
"""Parse all YAML manifests under manifests/ — catches syntax errors before apply."""
from __future__ import annotations

import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    print("Install PyYAML: pip install pyyaml", file=sys.stderr)
    sys.exit(2)


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    manifests = root / "manifests"
    errors = 0
    for path in sorted(manifests.glob("*.yaml")):
        try:
            list(yaml.safe_load_all(path.read_text()))
        except Exception as e:
            print(f"FAIL {path}: {e}", file=sys.stderr)
            errors += 1
        else:
            print(f"OK   {path.relative_to(root)}")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
