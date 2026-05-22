#!/usr/bin/env python3
"""Run MVP verification: unit tests, policy validation, optional API smoke."""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    print("== MVP verification: unit tests ==")
    result = subprocess.run(
        [sys.executable, "-m", "unittest", "discover", "-s", "backend/tests", "-v"],
        cwd=ROOT,
        check=False,
    )
    if result.returncode != 0:
        return result.returncode

    print("\n== MVP verification: policy registry ==")
    sys.path.insert(0, str(ROOT))
    from backend.app.services.policies import PolicyRegistry

    registry = PolicyRegistry(ROOT / "policies")
    registry.load()
    validation_errors = registry.validate()
    if validation_errors:
        print("Policy validation failed:", validation_errors)
        return 1
    print("Policies OK:", len(registry.documents), "documents")

    print("\n== MVP verification: FastAPI import ==")
    try:
        import fastapi  # noqa: F401
    except ImportError:
        print("SKIP API smoke (install requirements.txt for full check)")
        print("\nAll required checks passed.")
        return 0

    print("FastAPI available — API tests included in unittest discover above.")
    print("\nAll required checks passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
