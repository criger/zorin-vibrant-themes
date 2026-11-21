#!/usr/bin/env python3
"""Interactive theme manager. No sudo, no third-party packages, no GitHub writes.
Copyright (C) 2026 Cristhian Gertner. SPDX-License-Identifier: GPL-2.0-only.
"""
from __future__ import annotations

import argparse
import subprocess
from pathlib import Path

from scripts.vibrant_engine import (
    COLORS, KINDS, TONES, discovered, install_many, legacy_names,
    name_for, recognized_names, uninstall,
)

ROOT = Path(__file__).resolve().parent
DEFAULT_THEMES_DIR = Path.home() / ".themes"
DEFAULT_SOURCES_DIR = Path("/usr/share/themes")


def ask(prompt: str, allowed: set[str]) -> str:
    while True:
        try:
            answer = input(prompt).strip().lower()
        except (EOFError, KeyboardInterrupt):
            print("\nCancelled.")
            raise SystemExit(0)
        if answer in allowed:
            return answer
        print("Invalid selection. Please try again.")


def yes(prompt: str) -> bool:
    return ask(prompt + " [y/N]: ", {"y", "yes", "n", "no", ""}) in ("y", "yes")


def active_theme() -> str | None:
    try:
        result = subprocess.run(
            ["gsettings", "get", "org.gnome.desktop.interface", "gtk-theme"],
            check=True, text=True, capture_output=True,
        )
        return result.stdout.strip().strip("'").strip('"')
    except (OSError, subprocess.CalledProcessError):
        return None


def ensure_not_active(themes_dir: Path, removing: list[str]) -> None:
    # In filesystem tests, do not alter the live desktop by accident.
    if themes_dir.resolve() != DEFAULT_THEMES_DIR.resolve():
        return
    current = active_theme()
    if current not in removing:
        return
    print(f"'{current}' is the active theme. Switching to ZorinBlue-Light before removal...")
    try:
        subprocess.run(
            ["gsettings", "set", "org.gnome.desktop.interface", "gtk-theme", "ZorinBlue-Light"],
            check=True,
        )
    except (OSError, subprocess.CalledProcessError) as exc:
        raise RuntimeError("Could not activate ZorinBlue-Light; no themes have been removed") from exc


def show_installed(themes_dir: Path) -> list[str]:
    names = discovered(themes_dir)
    print("\nInstalled Vibrant themes:")
    if not names:
        print("  None.")
    for n, name in enumerate(names, 1):
        tag = " (legacy variant)" if name not in recognized_names() else ""
        print(f"  {n:2}. {name}{tag}")
    return names


def choose_color() -> str | None:
    print("\nChoose a color:")
    for i, color in enumerate(COLORS, 1):
        print(f"  {i}. {color}")
    print("  0. Back")
    choice = ask("Color: ", {str(i) for i in range(len(COLORS) + 1)})
    return None if choice == "0" else COLORS[int(choice) - 1]


def choose_tones() -> tuple[str, ...] | None:
    print("\nChoose color intensity (both are light-based themes):")
    print("  1. Light - softer, more subtle colors")
    print("  2. Vibrant - richer, more saturated colors")
    print("  3. Both intensities")
    print("  0. Back")
    choice = ask("Intensity: ", {"0", "1", "2", "3"})
    return {"0": None, "1": ("light",), "2": ("rich",), "3": TONES}[choice]


def choose_kinds() -> tuple[str, ...] | None:
    print("\nChoose a style:")
    print("  1. Vibrant (no gradients)")
    print("  2. Gradient (title bar and extended sidebar gradients)")
    print("  3. Both styles (this color only)")
    print("  0. Back")
    choice = ask("Style: ", {"0", "1", "2", "3"})
    return {"0": None, "1": ("vibrant",), "2": ("gradient",), "3": KINDS}[choice]


def install_selected(themes_dir: Path, sources_dir: Path, color: str,
                     kinds: tuple[str, ...], tones: tuple[str, ...] = ("rich",),
                     replace: bool = False) -> None:
    names = [name_for(color, k, tone) for tone in tones for k in kinds]
    existing = [n for n in names if (themes_dir / n).exists() or (themes_dir / n).is_symlink()]
    if existing and not replace:
        print("\nAlready installed: " + ", ".join(existing))
        if not yes("Replace existing variants and create backups?"):
            print("No changes made.")
            return
        replace = True
    print("\nSelected for installation: " + ", ".join(names))
    if not yes("Continue?"):
        print("No changes made.")
        return
    paths = install_many(color, kinds, themes_dir=themes_dir,
                         sources_dir=sources_dir, tones=tones, replace=replace,
                         license_path=ROOT / "LICENSE")
    for path in paths:
        print(f"  Installed: {path.name}")
    print("Select the theme in Zorin Appearance > Theme > Other > Applications.")
    print("Use light mode (color-scheme: default).")


def interactive_uninstall(themes_dir: Path) -> None:
    current = show_installed(themes_dir)
    if not current:
        return
    print(f"  {len(current) + 1:2}. Remove ALL listed Vibrant themes")
    print("   0. Back")
    choice = ask("Uninstall: ", {str(i) for i in range(len(current) + 2)})
    if choice == "0":
        return
    targets = current if int(choice) == len(current) + 1 else [current[int(choice) - 1]]
    print("\nThe following theme folders will be removed from ~/.themes:")
    for name in targets:
        print("  - " + name)
    if not yes("Confirm removal?"):
        print("No changes made.")
        return
    ensure_not_active(themes_dir, targets)
    for name in targets:
        uninstall(themes_dir, name)
        print("  Removed: " + name)


def interactive(themes_dir: Path, sources_dir: Path) -> None:
    print("\n=== Zorin Vibrant Theme Manager ===")
    while True:
        existing = discovered(themes_dir)
        if existing:
            print(f"\nFound {len(existing)} installed Vibrant theme(s).")
            print("  1. Install a theme")
            print("  2. Uninstall a theme")
            print("  3. Show installed themes")
            print("  0. Exit")
            option = ask("Choose an action: ", {"0", "1", "2", "3"})
            if option == "0":
                return
            if option == "2":
                interactive_uninstall(themes_dir)
                continue
            if option == "3":
                show_installed(themes_dir)
                continue
        else:
            print("\nNo Vibrant themes installed. Going directly to color selection.")
        color = choose_color()
        if color is None:
            if not existing:
                return
            continue
        tones = choose_tones()
        if tones is None:
            continue
        kinds = choose_kinds()
        if kinds is None:
            continue
        try:
            install_selected(themes_dir, sources_dir, color, kinds, tones)
        except (OSError, ValueError, RuntimeError) as exc:
            print(f"ERROR: {exc}")
        # Loop back, allowing the user to add another color or uninstall.


def main() -> int:
    parser = argparse.ArgumentParser(description="Interactive installation and removal of Zorin Vibrant themes")
    parser.add_argument("--list", action="store_true", help="List installed Vibrant themes")
    parser.add_argument("--install", choices=[c.lower() for c in COLORS], help="Install the specified color without opening the interactive menu")
    parser.add_argument("--variant", choices=("vibrant", "gradient", "both"), default="gradient")
    parser.add_argument("--tone", choices=("light", "rich", "both"), default="rich",
                        help="Color intensity: light, rich, or both (default: rich)")
    parser.add_argument("--uninstall", nargs="+", metavar="NAME", help="Uninstall theme folders by their exact names")
    parser.add_argument("--yes", action="store_true", help="Confirm without prompting (use with caution)")
    parser.add_argument("--replace", action="store_true", help="Back up and replace existing themes")
    parser.add_argument("--themes-dir", type=Path, default=DEFAULT_THEMES_DIR, help=argparse.SUPPRESS)
    parser.add_argument("--sources-dir", type=Path, default=DEFAULT_SOURCES_DIR, help=argparse.SUPPRESS)
    args = parser.parse_args()
    themes_dir = args.themes_dir.expanduser()
    sources_dir = args.sources_dir.expanduser()
    try:
        if args.list:
            show_installed(themes_dir)
        elif args.install:
            color = args.install.title()
            kinds = KINDS if args.variant == "both" else (args.variant,)
            tones = TONES if args.tone == "both" else (args.tone,)
            names = [name_for(color, k, tone) for tone in tones for k in kinds]
            if args.yes or yes("Install " + ", ".join(names) + "?"):
                paths = install_many(color, kinds, themes_dir=themes_dir,
                                     sources_dir=sources_dir, tones=tones, replace=args.replace,
                                     license_path=ROOT / "LICENSE")
                for path in paths:
                    print(f"Installed: {path}")
        elif args.uninstall:
            names = args.uninstall
            invalid = sorted(set(names) - (recognized_names() | legacy_names()))
            if invalid:
                raise ValueError("Unknown Vibrant theme: " + ", ".join(invalid))
            print("Selected for removal: " + ", ".join(names))
            if args.yes or yes("Confirm removal?"):
                ensure_not_active(themes_dir, names)
                for name in names:
                    uninstall(themes_dir, name)
                    print("Removed: " + name)
        else:
            interactive(themes_dir, sources_dir)
    except (OSError, ValueError, RuntimeError) as exc:
        parser.exit(1, f"Stopped: {exc}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
