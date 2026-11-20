#!/usr/bin/env python3
"""Install the optional Zorin Vibrant Extra-Gradient GTK themes.

The current, user-approved Gradient variants are the source. No system files,
GNOME Shell stylesheet or existing themes are modified.

Copyright (C) 2026 Cristhian Gertner
SPDX-License-Identifier: GPL-2.0-only
"""

from __future__ import annotations

import argparse
import shutil
from datetime import datetime, timezone
from pathlib import Path

THEMES = {
    "ZorinVibrantBlue-Light-extra-gradient": {
        "base": "ZorinVibrantBlue-Light-Gradient",
        "start": "#B8DFF9",
        "end": "#E7F5FF",
        "inactive_start": "#D9EBFA",
        "inactive_end": "#F4FAFF",
    },
    "ZorinVibrantBlue-extra-gradient": {
        "base": "ZorinVibrantBlue-Gradient",
        "start": "#9DCCF0",
        "end": "#DCEFFF",
        "inactive_start": "#C8E2F7",
        "inactive_end": "#F0F8FF",
    },
}

MARKER = "/* ZORIN VIBRANT EXTRA GRADIENT"


def extra_css(spec: dict[str, str], gtk: str) -> str:
    """Return only narrowly scoped sidebar overrides for an existing theme."""
    active = f"linear-gradient(to bottom, {spec['start']}, {spec['end']})"
    inactive = (
        f"linear-gradient(to bottom, {spec['inactive_start']}, "
        f"{spec['inactive_end']})"
    )
    if gtk == "gtk-3.0":
        return f"""
{MARKER} / GTK3 */
/* Stack/sidebar scroller overlays can conceal a parent sidebar gradient. */
stacksidebar.sidebar > scrolledwindow {{
  background-image: {active};
}}
stacksidebar.sidebar > scrolledwindow:backdrop {{
  background-image: {inactive};
}}
stacksidebar.sidebar > scrolledwindow > viewport.frame,
stacksidebar.sidebar > scrolledwindow > viewport.frame > list {{
  background-color: transparent;
}}
/* GTK3 control-center/libhandy navigation scrollers: narrow descendants only. */
window.background.csd > leaflet > box.vertical > scrolledwindow.view,
window.background.csd > hdyleaflet > box.vertical > scrolledwindow.view,
window.background.csd > box.horizontal > box.vertical > scrolledwindow.view {{
  background-image: {active};
}}
window.background.csd > leaflet > box.vertical > scrolledwindow.view:backdrop,
window.background.csd > hdyleaflet > box.vertical > scrolledwindow.view:backdrop,
window.background.csd > box.horizontal > box.vertical > scrolledwindow.view:backdrop {{
  background-image: {inactive};
}}
"""
    if gtk == "gtk-4.0":
        return f"""
{MARKER} / GTK4 */
/* Adwaita side panes: GNOME Settings and similar GTK4 layouts. */
.sidebar-pane:not(.content-pane) {{
  background-image: {active};
}}
.sidebar-pane:not(.content-pane):backdrop {{
  background-image: {inactive};
}}
/* The navigation list must not paint over a parent pane's gradient. */
.sidebar-pane .navigation-sidebar,
.sidebar-pane .navigation-sidebar.view {{
  background-color: transparent;
}}
/* Some GTK4 apps use a navigation list as the sidebar surface itself. */
.navigation-sidebar.background {{
  background-image: {active};
}}
.navigation-sidebar.background:backdrop {{
  background-image: {inactive};
}}
"""
    raise ValueError(f"Unsupported GTK version: {gtk}")


def check_source(source: Path, base: str) -> None:
    required = [source / "index.theme"] + [
        source / gtk / "gtk.css" for gtk in ("gtk-3.0", "gtk-4.0")
    ]
    for path in required:
        if not path.is_file():
            raise ValueError(f"Required source file missing: {path}")
    metadata = (source / "index.theme").read_text(encoding="utf-8")
    if f"GtkTheme={base}" not in metadata:
        raise ValueError(f"Theme metadata does not match {base}: {source}")
    for gtk in ("gtk-3.0", "gtk-4.0"):
        css = (source / gtk / "gtk.css").read_text(encoding="utf-8")
        if "ZORIN VIBRANT GRADIENT" not in css:
            raise ValueError(f"Not a recognized gradient source: {source / gtk / 'gtk.css'}")
        # Check only the added gradient block, never upstream Zorin CSS.
        added = css[css.rfind("/* ZORIN VIBRANT GRADIENT"):]
        if "window.background, .background {" in added or ".background {\n" in added:
            raise ValueError(
                f"Source still contains the unsafe root gradient: {source / gtk / 'gtk.css'}. "
                "Apply the confirmed wallpaper fix first."
            )


def install_variant(themes_dir: Path, name: str, spec: dict[str, str], replace: bool) -> Path:
    base = spec["base"]
    source = themes_dir / base
    target = themes_dir / name
    check_source(source, base)
    if target.exists() and not replace:
        raise FileExistsError(f"Already installed: {target}; use --replace")

    backup = None
    if target.exists():
        backup_dir = themes_dir / ".zorin-extra-gradient-backups"
        backup_dir.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
        backup = backup_dir / f"{name}-{timestamp}"
        shutil.move(str(target), str(backup))
    try:
        shutil.copytree(source, target, symlinks=True)
        for gtk in ("gtk-3.0", "gtk-4.0"):
            css = target / gtk / "gtk.css"
            css.write_text(css.read_text(encoding="utf-8") + "\n" + extra_css(spec, gtk), encoding="utf-8")
        index = target / "index.theme"
        meta = index.read_text(encoding="utf-8")
        for key in ("Name", "GtkTheme", "MetacityTheme"):
            meta = meta.replace(f"{key}={base}", f"{key}={name}")
        index.write_text(meta, encoding="utf-8")
        (target / "gtk-4.0" / ".libadwaita").touch(exist_ok=True)
        (target / "EXTRA-GRADIENT-CHANGES.txt").write_text(
            f"{name}: optional Extra-Gradient derivative of {base}.\n"
            "2026-11-20: narrow GTK3/GTK4 sidebar CSS additions only.\n"
            "Does not change root backgrounds, window geometry, Shell or taskbar.\n"
            "Base Zorin/Vibrant copyright and GPLv2 notices remain in place.\n",
            encoding="utf-8",
        )
    except Exception:
        if target.exists():
            shutil.rmtree(target)
        if backup:
            shutil.move(str(backup), str(target))
        raise

    print(f"Installed: {target}")
    if backup:
        print(f"Backup: {backup}")
    return target


def main() -> int:
    parser = argparse.ArgumentParser(description="Install the two optional Extra-Gradient theme variants.")
    parser.add_argument("--themes-dir", type=Path, default=Path.home() / ".themes")
    parser.add_argument("--replace", action="store_true", help="Back up and replace an existing extra-gradient theme")
    args = parser.parse_args()
    themes_dir = args.themes_dir.expanduser().resolve()
    try:
        # Preflight both variants before touching either one.
        for name, spec in THEMES.items():
            check_source(themes_dir / spec["base"], spec["base"])
            if (themes_dir / name).exists() and not args.replace:
                raise FileExistsError(f"Already installed: {name}; pass --replace")
        for name, spec in THEMES.items():
            install_variant(themes_dir, name, spec, args.replace)
    except (OSError, ValueError) as exc:
        parser.exit(1, f"Installation stopped: {exc}\n")
    print("\nSwitch under Zorin Appearance > Theme > Other > Applications.")
    print("Both themes remain light (color-scheme: default).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
