#!/usr/bin/env python3
"""Shared, dependency-free GTK theme generator for Zorin Vibrant Themes.

Copyright (C) 2026 Cristhian Gertner. SPDX-License-Identifier: GPL-2.0-only.
Original Zorin theme files remain copyright their original authors.
"""
from __future__ import annotations

import re
import shutil
import tempfile
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

GTK = ("gtk-3.0", "gtk-4.0")
KINDS = ("vibrant", "gradient")
TONES = ("light", "rich")
COLORS = ("Blue", "Green", "Yellow", "Orange", "Red", "Purple", "Brown", "Grey")


@dataclass(frozen=True)
class Palette:
    # In order: source window, source sidebar, source secondary sidebar, source inactive.
    original: tuple[str, str, str, str]
    vibrant: tuple[str, str, str, str]
    title: tuple[str, str, str]
    title_inactive: tuple[str, str]
    sidebar: tuple[str, str]
    sidebar_inactive: tuple[str, str]


# Green matches the visually accepted local Green pilot's rich palette.
# Blue uses the existing, accepted rich Vibrant and Extra-Gradient colors.
PALETTES: dict[str, Palette] = {
    "Blue": Palette(
        ("#eaf0f6", "#dae2ea", "#e2e9f0", "#f0f0f0"),
        ("#D4EBFF", "#B4D8F6", "#C5E2FA", "#EAF5FF"),
        ("#439FDF", "#8CCDF4", "#D4EBFF"),
        ("#C4E2F4", "#EDF8FF"),
        ("#9DCCF0", "#DCEFFF"),
        ("#C8E2F7", "#F0F8FF"),
    ),
    "Green": Palette(
        ("#ebf4f2", "#dbe7e5", "#e3eeeb", "#f0f0f0"),
        ("#CEF5E5", "#ABE8D0", "#BFEFD9", "#E9FFF4"),
        ("#39C991", "#83E6B8", "#CEF5E5"),
        ("#C4EFD9", "#EDFFF6"),
        ("#8CDEB7", "#D7F8E7"),
        ("#CBEFDE", "#F1FFF7"),
    ),
    "Yellow": Palette(
        ("#f6f5ea", "#eae9da", "#f0efe2", "#f0f0f0"),
        ("#FFF7CF", "#F4E5A5", "#FAECC0", "#FFFBE8"),
        ("#EFC447", "#FFE187", "#FFF7CF"),
        ("#F8E9B3", "#FFFCF0"),
        ("#F3D97F", "#FFF3CA"),
        ("#FAEBB8", "#FFFCF0"),
    ),
    "Orange": Palette(
        ("#f6f1ed", "#eae3de", "#f0eae6", "#f2f2f2"),
        ("#FFE4D2", "#FFCBAF", "#FFDBCA", "#FFF2E9"),
        ("#F5A06F", "#FFD0A7", "#FFE4D2"),
        ("#FFE0CD", "#FFF3EB"),
        ("#FFC09A", "#FFECDC"),
        ("#FFE1CC", "#FFF7F0"),
    ),
    "Red": Palette(
        ("#f6eeec", "#eadfdd", "#f0e7e4", "#f1f1f1"),
        ("#FFE0DE", "#FFC3C0", "#FFD3CF", "#FFF0F0"),
        ("#EF8A89", "#FFC1BC", "#FFE0DE"),
        ("#FFDAD8", "#FFF2F1"),
        ("#FFB3B1", "#FFE7E5"),
        ("#FFDDDA", "#FFF5F4"),
    ),
    "Purple": Palette(
        ("#f2eef5", "#e5dfe8", "#ebe7ef", "#f2f2f2"),
        ("#EEDFFF", "#DCC3F4", "#E5D3FA", "#F7EDFF"),
        ("#BC8EE5", "#DEC0F7", "#EEDFFF"),
        ("#E6D5F6", "#F8F1FF"),
        ("#D2ADF0", "#F1E4FF"),
        ("#E7D6F7", "#FAF4FF"),
    ),
    "Brown": Palette(
        ("#f1efed", "#e4e1de", "#eae8e5", "#efefef"),
        ("#F3E3D5", "#E6CEBA", "#EDD9C8", "#FAF0E7"),
        ("#B99170", "#DFC0A2", "#F3E3D5"),
        ("#E9D8CB", "#FCF4ED"),
        ("#DCC1AB", "#F8EBDF"),
        ("#EBDCCF", "#FCF6EF"),
    ),
    "Grey": Palette(
        # The original background and inactive color happen to coincide in Grey.
        ("#eeeeee", "#dfdfdf", "#e7e7e7", "#eeeeee"),
        ("#E4E7EC", "#C7CDD4", "#D6DCE2", "#E4E7EC"),
        ("#A6B0BA", "#CDD3DA", "#E4E7EC"),
        ("#E2E6E9", "#F5F6F8"),
        ("#BAC3CD", "#E9EDF1"),
        ("#E1E5E9", "#F8FAFB"),
    ),
}


# Softer, lighter counterparts. Blue and Green retain the palettes that were
# tested in the earlier local prototypes; others are starting points for review.
LIGHT_PALETTES: dict[str, Palette] = {
    "Blue": Palette(
        PALETTES["Blue"].original,
        ("#EDF8FF", "#CFE8FF", "#DDEEFF", "#F1F8FF"),
        ("#69BDF1", "#B1E0FA", "#EDF8FF"),
        ("#DEEFFA", "#F5FBFF"),
        ("#B8DFF9", "#E7F5FF"),
        ("#D9EBFA", "#F4FAFF"),
    ),
    "Green": Palette(
        PALETTES["Green"].original,
        ("#ECFFF7", "#CDF7E6", "#DEFBEF", "#F2FFF9"),
        ("#64DDAA", "#ACF1D1", "#ECFFF7"),
        ("#D9F6EA", "#F4FFFA"),
        ("#AFEDD2", "#E8FFF4"),
        ("#DDF6E9", "#F4FFF9"),
    ),
    "Yellow": Palette(
        PALETTES["Yellow"].original,
        ("#FFFBE8", "#FBF0CA", "#FFF7DB", "#FFFEF2"),
        ("#F7D875", "#FFEDAD", "#FFFBE8"),
        ("#FCF3D5", "#FFFDF5"),
        ("#F8E6A3", "#FFFADE"),
        ("#FBF0CD", "#FFFEF4"),
    ),
    "Orange": Palette(
        PALETTES["Orange"].original,
        ("#FFF1E9", "#FFE0CC", "#FFEAD9", "#FFF8F2"),
        ("#F9B78D", "#FFDDC1", "#FFF1E9"),
        ("#FFEBDC", "#FFFAF5"),
        ("#FFD4B6", "#FFF1E6"),
        ("#FFE8DB", "#FFFAF5"),
    ),
    "Red": Palette(
        PALETTES["Red"].original,
        ("#FFF0EF", "#FFDAD7", "#FFE5E2", "#FFF8F8"),
        ("#F8A7A6", "#FFDBD7", "#FFF0EF"),
        ("#FFE5E4", "#FFFAFA"),
        ("#FFCECC", "#FFF1F0"),
        ("#FFE6E4", "#FFFAFA"),
    ),
    "Purple": Palette(
        PALETTES["Purple"].original,
        ("#F8F0FF", "#EAD9F8", "#F2E6FF", "#FBF6FF"),
        ("#D0ADEE", "#EAD3FC", "#F8F0FF"),
        ("#F0E2FC", "#FCF8FF"),
        ("#E1C8F5", "#F7EEFF"),
        ("#EFE2FB", "#FCF8FF"),
    ),
    "Brown": Palette(
        PALETTES["Brown"].original,
        ("#FAF0E8", "#EFDDCD", "#F5E8DD", "#FDF8F3"),
        ("#D4B090", "#EEDDCA", "#FAF0E8"),
        ("#F4E7DA", "#FEFAF6"),
        ("#EBD5C2", "#FAF0E7"),
        ("#F3E7DB", "#FFFAF6"),
    ),
    "Grey": Palette(
        PALETTES["Grey"].original,
        ("#F8F9FA", "#E7EBEF", "#EFF2F5", "#F8F9FA"),
        ("#CAD1D8", "#E8ECF0", "#F8F9FA"),
        ("#EEF0F3", "#FBFCFD"),
        ("#DEE4E9", "#F7F9FA"),
        ("#EFF2F5", "#FCFDFE"),
    ),
}


def palette_for(color: str, tone: str) -> Palette:
    if color not in PALETTES or tone not in TONES:
        raise ValueError(f"Unknown color/tone: {color}/{tone}")
    return LIGHT_PALETTES[color] if tone == "light" else PALETTES[color]


def name_for(color: str, kind: str, tone: str = "rich") -> str:
    if color not in PALETTES or kind not in KINDS or tone not in TONES:
        raise ValueError(f"Unknown color/variant/tone: {color}/{kind}/{tone}")
    name = f"ZorinVibrant{color}"
    if tone == "light":
        name += "-Light"
    return name + ("-Gradient" if kind == "gradient" else "")


def recognized_names() -> set[str]:
    return {name_for(color, kind, tone)
            for color in COLORS for tone in TONES for kind in KINDS}


def legacy_names() -> set[str]:
    """Only retired variants, never names reused by the current manager."""
    names = set()
    for color in ("Blue", "Green"):
        prefix = f"ZorinVibrant{color}"
        for suffix in ("-extra-gradient", "-Light-extra-gradient", "-Glass", "-Light-Glass"):
            names.add(prefix + suffix)
    return names


def discovered(themes_dir: Path, include_legacy: bool = True) -> list[str]:
    names = recognized_names() | (legacy_names() if include_legacy else set())
    if not themes_dir.is_dir():
        return []
    return sorted(n for n in names if (themes_dir / n).exists() or (themes_dir / n).is_symlink())


def _ensure_themes_location(themes_dir: Path) -> None:
    """Refuse obvious system paths and a themes folder that is a symlink."""
    if themes_dir.is_symlink():
        raise ValueError("The themes directory must not be a symlink")
    resolved = themes_dir.resolve()
    if resolved == Path("/") or resolved == Path("/usr/share/themes") or "/usr/share/themes" in str(resolved):
        raise ValueError("Refusing to change system themes")


def _token_replace(css: str, palette: Palette) -> tuple[str, dict[str, int]]:
    # The same original token may appear twice for some color families.
    mapping = dict(zip(palette.original, palette.vibrant))
    counts: dict[str, int] = {}
    for old, new in mapping.items():
        css, n = re.subn(rf"(?i){re.escape(old)}(?![0-9a-f])", new, css)
        counts[old] = n
    return css, counts


def validate_source(source: Path, color: str) -> None:
    if color not in PALETTES:
        raise ValueError(f"Unknown color: {color}")
    required = [source / "index.theme"] + [source / kind / "gtk.css" for kind in GTK]
    missing = [str(p) for p in required if not p.is_file()]
    if missing:
        raise ValueError("Original Zorin theme missing files: " + ", ".join(missing))
    text = (source / "index.theme").read_text(encoding="utf-8")
    if not re.search(rf"(?m)^GtkTheme=Zorin{color}-Light\s*$", text):
        raise ValueError(f"Expected original GtkTheme=Zorin{color}-Light")
    combined = "\n".join((source / kind / "gtk.css").read_text(encoding="utf-8") for kind in GTK)
    _, counts = _token_replace(combined, PALETTES[color])
    missing_colors = [c for c, n in counts.items() if not n]
    if missing_colors:
        raise ValueError("The original CSS is different from the tested palette; missing colors: " + ", ".join(missing_colors))


def _gradient_css(palette: Palette, kind: str) -> str:
    a, b, c = palette.title
    ia, ib = palette.title_inactive
    sa, sb = palette.sidebar
    return f"""
/* ZORIN VIBRANT GRADIENT / {kind}: targeted window components only */
headerbar, headerbar.titlebar, .titlebar:not(headerbar) {{
  background-image: linear-gradient(to right, {a}, {b} 58%, {c});
}}
headerbar:backdrop, headerbar.titlebar:backdrop, .titlebar:backdrop:not(headerbar) {{
  background-image: linear-gradient(to right, {ia}, {ib});
}}
.sidebar:not(separator), placessidebar, stacksidebar {{
  background-image: linear-gradient(to bottom, {sa}, {sb});
}}
"""


def _extra_sidebar_css(palette: Palette, kind: str) -> str:
    sa, sb = palette.sidebar
    ia, ib = palette.sidebar_inactive
    active = f"linear-gradient(to bottom, {sa}, {sb})"
    inactive = f"linear-gradient(to bottom, {ia}, {ib})"
    if kind == "gtk-3.0":
        return f"""
/* ZORIN VIBRANT EXTRA SIDEBARS / GTK3 */
stacksidebar.sidebar > scrolledwindow {{ background-image: {active}; }}
stacksidebar.sidebar > scrolledwindow:backdrop {{ background-image: {inactive}; }}
stacksidebar.sidebar > scrolledwindow > viewport.frame,
stacksidebar.sidebar > scrolledwindow > viewport.frame > list {{
  background-color: transparent;
}}
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
    if kind == "gtk-4.0":
        return f"""
/* ZORIN VIBRANT EXTRA SIDEBARS / GTK4 */
.sidebar-pane:not(.content-pane) {{ background-image: {active}; }}
.sidebar-pane:not(.content-pane):backdrop {{ background-image: {inactive}; }}
.sidebar-pane .navigation-sidebar,
.sidebar-pane .navigation-sidebar.view {{ background-color: transparent; }}
.navigation-sidebar.background {{ background-image: {active}; }}
.navigation-sidebar.background:backdrop {{ background-image: {inactive}; }}
"""
    raise ValueError(f"Unsupported GTK version: {kind}")


def _render(source: Path, target: Path, color: str, kind: str,
            tone: str, license_path: Path | None) -> None:
    theme = name_for(color, kind, tone)
    p = palette_for(color, tone)
    shutil.copytree(source, target, symlinks=True)
    for gtk in GTK:
        stylesheet = target / gtk / "gtk.css"
        css, _ = _token_replace(stylesheet.read_text(encoding="utf-8"), p)
        if kind == "gradient":
            # "Gradient" is the complete former Extra-Gradient effect, not the old middle step.
            css += "\n" + _gradient_css(p, gtk) + "\n" + _extra_sidebar_css(p, gtk)
        stylesheet.write_text(css, encoding="utf-8")
    index = target / "index.theme"
    text = index.read_text(encoding="utf-8")
    for key in ("Name", "GtkTheme", "MetacityTheme"):
        text, count = re.subn(rf"(?m)^({key}=)Zorin{color}-Light\s*$", rf"\g<1>{theme}", text)
        if count != 1:
            raise ValueError(f"Original theme metadata missing: {key}")
    # Keep the *original Zorin icon theme*, not an imaginary ZorinVibrant icon theme.
    index.write_text(text, encoding="utf-8")
    (target / "gtk-4.0" / ".libadwaita").touch(exist_ok=True)
    (target / "VIBRANT-CHANGES.md").write_text(
        f"# {theme}\n\n"
        f"Original GTK theme: Zorin{color}-Light (Zorin OS developers).\n"
        f"Variant: {kind}; tone: {tone}. Both tones are light-based.\n"
        "Recolor only GTK3/GTK4 light files; Gradient also includes the Extra-Gradient sidebar rules.\n"
        "Do not change system theme, original geometry, icons, Shell or taskbar.\n"
        "Original Zorin CSS copyright belongs to its upstream authors.\n"
        "Generator/palette: Cristhian Gertner, 2026. GPL-2.0-only.\n",
        encoding="utf-8",
    )
    if license_path is not None and license_path.is_file():
        shutil.copy2(license_path, target / "COPYING")


def install_many(color: str, kinds: tuple[str, ...], *, themes_dir: Path,
                 sources_dir: Path, tones: tuple[str, ...] = ("rich",),
                 replace: bool = False,
                 license_path: Path | None = None) -> list[Path]:
    """Install only selected tone/style pairs; roll back every change on failure."""
    if not kinds or len(set(kinds)) != len(kinds) or any(k not in KINDS for k in kinds):
        raise ValueError("Select one or two distinct styles")
    if not tones or len(set(tones)) != len(tones) or any(t not in TONES for t in tones):
        raise ValueError("Select one or two distinct tones")
    selections = [(tone, kind, name_for(color, kind, tone))
                  for tone in tones for kind in kinds]
    _ensure_themes_location(themes_dir)
    source = sources_dir / f"Zorin{color}-Light"
    validate_source(source, color)
    targets = [themes_dir / name for _, _, name in selections]
    if not replace:
        collisions = [t.name for t in targets if t.exists() or t.is_symlink()]
        if collisions:
            raise FileExistsError("Existing themes: " + ", ".join(collisions))
    themes_dir.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix=".zorin-vibrant-stage-", dir=themes_dir) as temp:
        stage = Path(temp)
        for tone, kind, name in selections:
            _render(source, stage / name, color, kind, tone, license_path)
        changed: list[tuple[Path, Path | None]] = []
        try:
            for target in targets:
                backup: Path | None = None
                if target.exists() or target.is_symlink():
                    folder = themes_dir / ".zorin-vibrant-backups"
                    folder.mkdir(exist_ok=True)
                    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
                    backup = folder / f"{target.name}-{stamp}"
                    target.rename(backup)
                changed.append((target, backup))
                (stage / target.name).rename(target)
        except Exception:
            for target, backup in reversed(changed):
                if target.is_symlink():
                    target.unlink()
                elif target.is_dir():
                    shutil.rmtree(target)
                if backup is not None:
                    backup.rename(target)
            raise
    return targets


def install_one(color: str, kind: str, *, themes_dir: Path, sources_dir: Path,
                tone: str = "rich", replace: bool = False,
                license_path: Path | None = None) -> Path:
    return install_many(color, (kind,), themes_dir=themes_dir,
                        sources_dir=sources_dir, tones=(tone,), replace=replace,
                        license_path=license_path)[0]


def uninstall(themes_dir: Path, name: str) -> None:
    _ensure_themes_location(themes_dir)
    if name not in recognized_names() | legacy_names():
        raise ValueError(f"Refusing to uninstall unexpected theme: {name}")
    target = themes_dir / name
    if target.is_symlink():
        target.unlink()  # Never follow the link.
    elif target.is_dir():
        shutil.rmtree(target)
    elif target.exists():
        raise ValueError(f"Unexpected non-directory theme: {target}")
