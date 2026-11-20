#!/usr/bin/env python3
"""Install two Zorin Vibrant Themes derived from the local ZorinBlue-Light theme.

Copyright (C) 2026 Cristhian Gertner
SPDX-License-Identifier: GPL-2.0-only
"""

from __future__ import annotations

import argparse
import re
import shutil
from datetime import datetime, timezone
from pathlib import Path

SOURCE_THEME = "ZorinBlue-Light"
PALETTES = {
    "ZorinVibrantBlue-Light": {
        "#eaf0f6": "#EDF8FF",
        "#dae2ea": "#CFE8FF",
        "#e2e9f0": "#DDEEFF",
        "#f0f0f0": "#F1F8FF",
    },
    "ZorinVibrantBlue": {
        "#eaf0f6": "#D4EBFF",
        "#dae2ea": "#B4D8F6",
        "#e2e9f0": "#C5E2FA",
        "#f0f0f0": "#EAF5FF",
    },
}


def check_source(source: Path) -> None:
    """Fail before writing if the selected source isn't a compatible theme."""
    required = (
        source / "index.theme",
        source / "gtk-3.0" / "gtk.css",
        source / "gtk-4.0" / "gtk.css",
    )
    missing = [str(path) for path in required if not path.is_file()]
    if missing:
        raise ValueError("Missing Zorin theme files: " + ", ".join(missing))
    metadata = (source / "index.theme").read_text(encoding="utf-8")
    if "GtkTheme=ZorinBlue-Light" not in metadata:
        raise ValueError("Expected the original ZorinBlue-Light index.theme")


def recolor(original: str, palette: dict[str, str]) -> tuple[str, dict[str, int]]:
    """Replace exact color tokens without touching CSS layout and dimensions."""
    result = original
    counts = {}
    for old, new in palette.items():
        result, count = re.subn(
            rf"(?i){re.escape(old)}(?![0-9a-f])", new, result
        )
        counts[old] = count
    return result, counts


def install_theme(
    source: Path,
    destination: Path,
    name: str,
    palette: dict[str, str],
    replace: bool = False,
    license_path: Path | None = None,
) -> Path:
    """Copy theme, edit GTK light CSS and retain a backup on replacement."""
    check_source(source)
    destination.mkdir(parents=True, exist_ok=True)
    target = destination / name
    backup = None
    if target.exists():
        if not replace:
            raise FileExistsError(
                f"{target} already exists. Use --replace to keep a backup and reinstall."
            )
        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
        backup_dir = destination / ".zorin-vibrant-backups"
        backup_dir.mkdir(parents=True, exist_ok=True)
        backup = backup_dir / f"{name}.backup-{stamp}"
        shutil.move(str(target), str(backup))

    try:
        shutil.copytree(source, target, symlinks=True)

        total_counts = {old: 0 for old in palette}
        for version in ("gtk-3.0", "gtk-4.0"):
            css = target / version / "gtk.css"
            modified, counts = recolor(css.read_text(encoding="utf-8"), palette)
            css.write_text(modified, encoding="utf-8")
            for old, count in counts.items():
                total_counts[old] += count

        unused = [color for color, count in total_counts.items() if count == 0]
        if unused:
            raise ValueError(
                f"Source theme colors have changed; no match for: {', '.join(unused)}"
            )

        index = target / "index.theme"
        metadata = index.read_text(encoding="utf-8")
        for key in ("Name", "GtkTheme", "MetacityTheme"):
            metadata = metadata.replace(
                f"{key}={SOURCE_THEME}", f"{key}={name}"
            )
        # Keep IconTheme=ZorinBlue-Light: we are not shipping new icons.
        index.write_text(metadata, encoding="utf-8")

        (target / "gtk-4.0" / ".libadwaita").touch(exist_ok=True)

        changes = [
            f"# {name} - derivative theme notice",
            "",
            "Modified on 2026-11-20 by the Zorin Vibrant Themes project,",
            "maintained by Cristhian Gertner.",
            "",
            "Base theme: ZorinBlue-Light by the Zorin OS developers.",
            "Upstream: https://github.com/ZorinOS/zorin-desktop-themes",
            "License: GNU GPL version 2 (GPL-2.0-only).",
            "",
            "Changes: GTK3 and GTK4 light-mode background colors only.",
            "The original layout, selectors, images and GNOME Shell CSS",
            "are otherwise preserved. This is an unofficial community theme.",
            "",
        ]
        changes += [f"- {old} -> {new}" for old, new in palette.items()]
        (target / "VIBRANT-CHANGES.md").write_text(
            "\n".join(changes) + "\n", encoding="utf-8"
        )

        if license_path is not None and license_path.is_file():
            shutil.copy2(license_path, target / "COPYING")
    except Exception:
        if target.exists():
            shutil.rmtree(target)
        if backup is not None:
            shutil.move(str(backup), str(target))
        raise

    if backup is not None:
        print(f"Existing theme backed up to: {backup}")
    print(f"Installed: {target}")
    return target


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Install Zorin Vibrant Blue GTK themes without modifying system files."
    )
    parser.add_argument(
        "--variant",
        choices=("all", *PALETTES.keys()),
        default="all",
        help="Install one variant or both (default: all).",
    )
    parser.add_argument(
        "--replace",
        action="store_true",
        help="Back up installed variants before replacing them.",
    )
    parser.add_argument(
        "--source",
        type=Path,
        default=Path("/usr/share/themes") / SOURCE_THEME,
        help="Path to the original ZorinBlue-Light theme.",
    )
    parser.add_argument(
        "--destination",
        type=Path,
        default=Path.home() / ".themes",
        help="Destination directory for user GTK themes.",
    )
    args = parser.parse_args()

    try:
        check_source(args.source)
        names = list(PALETTES) if args.variant == "all" else [args.variant]
        if not args.replace:
            already = [
                name for name in names if (args.destination / name).exists()
            ]
            if already:
                parser.error(
                    "Theme(s) already installed: "
                    + ", ".join(already)
                    + ". Pass --replace to back up and reinstall."
                )
        license_path = Path(__file__).resolve().parents[1] / "LICENSE"
        for name in names:
            install_theme(
                args.source, args.destination, name, PALETTES[name],
                replace=args.replace,
                license_path=license_path,
            )
    except (OSError, ValueError) as error:
        parser.exit(1, f"Installation failed: {error}\n")

    print("\nChoose a theme in Zorin Appearance > Theme > Other > Applications.")
    print("Keep the color scheme set to 'default' for these light-based variants.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
