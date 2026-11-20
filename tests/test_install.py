"""Filesystem and recoloring tests for Zorin Vibrant Themes.

Copyright (C) 2026 Cristhian Gertner
SPDX-License-Identifier: GPL-2.0-only
"""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from scripts.install import PALETTES, install_theme


class InstallThemeTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        base = Path(self.temp.name)
        self.source = base / "system" / "ZorinBlue-Light"
        self.destination = base / ".themes"
        (self.source / "gtk-3.0").mkdir(parents=True)
        (self.source / "gtk-4.0").mkdir()
        (self.source / "gnome-shell").mkdir()
        (self.source / "index.theme").write_text(
            "[Desktop Entry]\nName=ZorinBlue-Light\n"
            "[X-GNOME-Metatheme]\nGtkTheme=ZorinBlue-Light\n"
            "MetacityTheme=ZorinBlue-Light\nIconTheme=ZorinBlue-Light\n",
            encoding="utf-8",
        )
        (self.source / "gtk-3.0" / "gtk.css").write_text(
            ".background { background: #eaf0f6; border-color: #dae2ea; }\n"
            ".background:backdrop { background: #f0f0f0; }\n",
            encoding="utf-8",
        )
        (self.source / "gtk-4.0" / "gtk.css").write_text(
            "@define-color window_bg_color #EAF0F6;\n"
            "@define-color sidebar_bg_color #dae2ea;\n"
            "@define-color secondary_sidebar_bg_color #e2e9f0;\n",
            encoding="utf-8",
        )
        (self.source / "gnome-shell" / "gnome-shell.css").write_text(
            "/* untouched shell */", encoding="utf-8"
        )
        self.license_path = base / "LICENSE"
        self.license_path.write_text("Test license text", encoding="utf-8")

    def test_install_both_variants_with_original_geometry_unchanged(self) -> None:
        for name, palette in PALETTES.items():
            target = install_theme(
                self.source, self.destination, name, palette,
                license_path=self.license_path,
            )
            combined_css = (
                (target / "gtk-3.0" / "gtk.css").read_text()
                + (target / "gtk-4.0" / "gtk.css").read_text()
            )
            for old, new in palette.items():
                self.assertIn(new, combined_css)
                self.assertNotIn(old.lower(), combined_css.lower())
            self.assertIn("border-color:", combined_css)
            self.assertEqual(
                (target / "gnome-shell" / "gnome-shell.css").read_text(),
                "/* untouched shell */",
            )
            index = (target / "index.theme").read_text()
            self.assertIn(f"GtkTheme={name}", index)
            self.assertIn("IconTheme=ZorinBlue-Light", index)
            self.assertTrue((target / "gtk-4.0" / ".libadwaita").exists())
            self.assertEqual((target / "COPYING").read_text(), "Test license text")
            self.assertIn("Modified on 2026-11-20", (target / "VIBRANT-CHANGES.md").read_text())

        self.assertIn("#eaf0f6", (self.source / "gtk-3.0" / "gtk.css").read_text())

    def test_existing_theme_never_overwritten_by_default(self) -> None:
        name = "ZorinVibrantBlue"
        target = self.destination / name
        target.mkdir(parents=True)
        (target / "keep.txt").write_text("previous")
        with self.assertRaises(FileExistsError):
            install_theme(self.source, self.destination, name, PALETTES[name])
        self.assertEqual((target / "keep.txt").read_text(), "previous")

    def test_replacement_preserves_backup(self) -> None:
        name = "ZorinVibrantBlue-Light"
        target = self.destination / name
        target.mkdir(parents=True)
        (target / "old.txt").write_text("my customizations")
        install_theme(
            self.source, self.destination, name, PALETTES[name],
            replace=True,
        )
        backups = list((self.destination / ".zorin-vibrant-backups").glob(f"{name}.backup-*"))
        self.assertEqual(len(backups), 1)
        self.assertEqual((backups[0] / "old.txt").read_text(), "my customizations")
        self.assertFalse((target / "old.txt").exists())

    def test_incompatible_source_rejected_without_partial_install(self) -> None:
        css = self.source / "gtk-4.0" / "gtk.css"
        css.write_text(css.read_text().replace("#e2e9f0", "#abcdef"))
        name = "ZorinVibrantBlue-Light"
        with self.assertRaisesRegex(ValueError, "Source theme colors have changed"):
            install_theme(self.source, self.destination, name, PALETTES[name])
        self.assertFalse((self.destination / name).exists())


if __name__ == "__main__":
    unittest.main()
