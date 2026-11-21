#!/usr/bin/env python3
"""Optional cleanup of retired Blue/Green Extra-Gradient and Glass variants.

No sudo. Never remove currently supported Vibrant, Light or Gradient names.
Copyright (C) 2026 Cristhian Gertner; SPDX-License-Identifier: GPL-2.0-only.
"""
from __future__ import annotations

import argparse
from pathlib import Path

from install import DEFAULT_THEMES_DIR, ensure_not_active, yes
from scripts.vibrant_engine import legacy_names, uninstall


def old_themes(themes_dir: Path) -> list[str]:
    return sorted(n for n in legacy_names()
                  if (themes_dir / n).exists() or (themes_dir / n).is_symlink())


def run(themes_dir: Path, *, dry_run: bool = False, confirmed: bool = False) -> list[str]:
    candidates = old_themes(themes_dir)
    if not candidates:
        print("No retired Blue/Green Extra-Gradient or Glass themes found.")
        return []
    print("\nRetired theme variants eligible for cleanup:")
    for name in candidates:
        print(f"  - {name}")
    print(f"\nOnly these {len(candidates)} folders under {themes_dir} will be affected.")
    if dry_run:
        print("DRY RUN: no files have been removed.")
        return candidates
    if not confirmed and not yes("Remove all listed retired themes?"):
        print("Cancelled - no files have been removed.")
        return []
    ensure_not_active(themes_dir, candidates)
    for name in candidates:
        uninstall(themes_dir, name)
        print("  Removed: " + name)
    print("Cleanup complete. System themes have not been changed.")
    return candidates


def main() -> int:
    parser = argparse.ArgumentParser(description="Remove only retired Extra-Gradient/Glass theme variants")
    parser.add_argument("--dry-run", action="store_true", help="Preview theme folders that would be removed")
    parser.add_argument("--yes", action="store_true", help="Confirm removal without prompting")
    parser.add_argument("--themes-dir", type=Path, default=DEFAULT_THEMES_DIR, help=argparse.SUPPRESS)
    args = parser.parse_args()
    try:
        run(args.themes_dir.expanduser(), dry_run=args.dry_run, confirmed=args.yes)
    except (OSError, ValueError, RuntimeError) as exc:
        parser.exit(1, f"Stopped: {exc}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
