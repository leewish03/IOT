#!/usr/bin/env python3
"""Verify Phase 0 + API surface for dashboard integration."""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    print("== Jarvis verify: backend ==")
    r1 = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "verify_mvp.py")],
        cwd=ROOT,
    )
    if r1.returncode != 0:
        return r1.returncode

    print("\n== Jarvis verify: web build ==")
    r2 = subprocess.run(["npm", "run", "build"], cwd=ROOT / "web")
    return r2.returncode


if __name__ == "__main__":
    raise SystemExit(main())
