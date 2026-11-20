#!/usr/bin/env python3
"""Install optional gradient variants of Zorin Vibrant Blue GTK themes.

Original variants and system themes are preserved.
Copyright (C) 2026 Cristhian Gertner. SPDX-License-Identifier: GPL-2.0-only.
"""

from __future__ import annotations

import argparse
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

SPECS = {
    "ZorinVibrantBlue-Light-Gradient": {
        "source": "ZorinVibrantBlue-Light",
        "title": ("#69BDF1", "#B1E0FA", "#EDF8FF"),
        "title_inactive": ("#DEEFFA", "#F5FBFF"),
        "sidebar": ("#B8DFF9", "#E7F5FF"),
    },
    "ZorinVibrantBlue-Gradient": {
        "source": "ZorinVibrantBlue",
        "title": ("#439FDF", "#8CCDF4", "#D4EBFF"),
        "title_inactive": ("#C4E2F4", "#EDF8FF"),
        "sidebar": ("#9DCCF0", "#DCEFFF"),
    },
}


def validate_source(source: Path) -> None:
    """Make sure this is a complete installed base theme before copying it."""
    required = (
        source / "index.theme",
        source / "gtk-3.0" / "gtk.css",
        source / "gtk-4.0" / "gtk.css",
    )
    missing = [str(item) for item in required if not item.is_file()]
    if missing:
        raise ValueError("Ufullstendig kilde-tema: " + ", ".join(missing))


def css_extension(spec: dict, kind: str) -> str:
    title_a, title_b, title_c = spec["title"]
    inactive_a, inactive_b = spec["title_inactive"]
    sidebar_a, sidebar_b = spec["sidebar"]
    if kind == "gtk-3.0":
        return f"""
/* ZORIN VIBRANT GRADIENT - GTK 3
 * Only paints titlebars and sidebars; leaves the desktop/window root alone.
 * Unfocused headers are intentionally softer.
 */
.titlebar:not(headerbar), headerbar, headerbar.titlebar {{
  background-image: linear-gradient(to right, {title_a}, {title_b} 58%, {title_c});
}}
.titlebar:backdrop:not(headerbar), headerbar:backdrop, headerbar.titlebar:backdrop {{
  background-image: linear-gradient(to right, {inactive_a}, {inactive_b});
}}
.sidebar:not(separator), placessidebar, stacksidebar {{
  background-image: linear-gradient(to bottom, {sidebar_a}, {sidebar_b});
}}
"""
    if kind == "gtk-4.0":
        return f"""
/* ZORIN VIBRANT GRADIENT - GTK 4 / libadwaita
 * Some applications supply their own CSS and may not adopt these rules.
 * Root background overrides were removed after a wallpaper regression.
 */
headerbar, headerbar.titlebar, .titlebar:not(headerbar) {{
  background-image: linear-gradient(to right, {title_a}, {title_b} 58%, {title_c});
}}
headerbar:backdrop, headerbar.titlebar:backdrop, .titlebar:backdrop:not(headerbar) {{
  background-image: linear-gradient(to right, {inactive_a}, {inactive_b});
}}
.sidebar:not(separator), placessidebar, stacksidebar {{
  background-image: linear-gradient(to bottom, {sidebar_a}, {sidebar_b});
}}
"""
    raise ValueError(f"Ukjent GTK-versjon: {kind}")


def install_one(base_dir: Path, name: str, replace: bool) -> Path:
    spec = SPECS[name]
    source = base_dir / spec["source"]
    target = base_dir / name
    validate_source(source)
    if target.exists() and not replace:
        raise FileExistsError(
            f"{target} finnes fra før. Bruk --replace for å ta backup og reinstallere."
        )

    backup = None
    if target.exists():
        backups = base_dir / ".zorin-gradient-backups"
        backups.mkdir(exist_ok=True)
        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
        backup = backups / f"{name}-{stamp}"
        shutil.move(str(target), str(backup))

    try:
        shutil.copytree(source, target, symlinks=True)
        for kind in ("gtk-3.0", "gtk-4.0"):
            css_file = target / kind / "gtk.css"
            original_css = css_file.read_text(encoding="utf-8")
            css_file.write_text(
                original_css + "\n" + css_extension(spec, kind), encoding="utf-8"
            )

        index_file = target / "index.theme"
        index_text = index_file.read_text(encoding="utf-8")
        for key in ("Name", "GtkTheme", "MetacityTheme"):
            index_text = index_text.replace(
                f"{key}={spec['source']}", f"{key}={name}"
            )
        index_file.write_text(index_text, encoding="utf-8")
        (target / "gtk-4.0" / ".libadwaita").touch(exist_ok=True)

        notice = (
            f"{name}: experimental derivative of {spec['source']}.\n"
            "2026-11-20: added horizontal headerbar and vertical sidebar gradients\n"
            "to gtk-3.0/gtk.css and gtk-4.0/gtk.css.\n"
            "2026-11-20: removed broad window-background overrides after a reported\n"
            "white-desktop regression when all windows were minimized.\n"
            "Original Zorin CSS/rights remain with the upstream authors.\n"
            "Optional gradient variant. No GNOME Shell/panel changes.\n"
        )
        (target / "GRADIENT-CHANGES.txt").write_text(notice, encoding="utf-8")
    except Exception:
        if target.exists():
            shutil.rmtree(target)
        if backup is not None:
            shutil.move(str(backup), str(target))
        raise

    if backup:
        print(f"  Sikkerhetskopi: {backup}")
    print(f"  Installert: {target}")
    return target


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Installer to lokale gradienttemaer basert på eksisterende Zorin Vibrant Blue."
    )
    parser.add_argument("--replace", action="store_true",
                        help="Ta backup av en tidligere gradientprototype og erstatt den.")
    parser.add_argument("--themes-dir", type=Path,
                        default=Path.home() / ".themes",
                        help="Mappe med de to eksisterende Vibrant Blue-temaene.")
    args = parser.parse_args()
    base_dir = args.themes_dir.expanduser().resolve()

    # Validate both sources and targets before writing either variant.
    try:
        for name, spec in SPECS.items():
            validate_source(base_dir / spec["source"])
            if (base_dir / name).exists() and not args.replace:
                raise FileExistsError(f"{name} finnes allerede. Bruk --replace.")
    except (OSError, ValueError) as error:
        parser.exit(1, f"Feil: {error}\n\nInstaller de to originale Vibrant-temaene først.\n")

    try:
        for name in SPECS:
            install_one(base_dir, name, args.replace)
    except (OSError, ValueError) as error:
        parser.exit(1, f"Installasjonen stoppet: {error}\n")

    print("\nVelg ett tema i Zorin Appearance > Theme > Other > Applications.")
    print("For eksempel: gsettings set org.gnome.desktop.interface gtk-theme 'ZorinVibrantBlue-Gradient'")
    print("Fortsatt lysmodus: gsettings set org.gnome.desktop.interface color-scheme 'default'")
    return 0


if __name__ == "__main__":
    sys.exit(main())
