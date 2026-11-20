"""Regression tests for the optional Extra-Gradient installer."""
from __future__ import annotations

import importlib.util
import re
import tempfile
import unittest
from pathlib import Path

INSTALLER = Path(__file__).resolve().parents[1] / "scripts" / "install_extra_gradients.py"
spec = importlib.util.spec_from_file_location("extra_gradient", INSTALLER)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class ExtraGradientTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        for data in module.THEMES.values():
            base = data["base"]
            theme = self.root / base
            for version in ("gtk-3.0", "gtk-4.0"):
                folder = theme / version
                folder.mkdir(parents=True)
                (folder / "gtk.css").write_text(
                    "/* Upstream Zorin CSS */\n"
                    ".background { color: #123354; background-color: #eaf0f6; }\n"
                    "/* ZORIN VIBRANT GRADIENT LOCAL PROTOTYPE - GTK 3 */\n"
                    "headerbar { background-image: linear-gradient(to right, blue, white); }\n"
                    ".sidebar:not(separator) { background-image: linear-gradient(to bottom, blue, white); }\n",
                    encoding="utf-8",
                )
            (theme / "index.theme").write_text(
                f"[Desktop Entry]\nName={base}\n"
                f"[X-GNOME-Metatheme]\nGtkTheme={base}\n"
                f"MetacityTheme={base}\nIconTheme=ZorinBlue-Light\n"
            )
            (theme / "gnome-shell").mkdir()
            (theme / "gnome-shell" / "gnome-shell.css").write_text("untouched")

    def test_both_variants_install_without_mutating_sources(self) -> None:
        for name, data in module.THEMES.items():
            target = module.install_variant(self.root, name, data, False)
            self.assertIn(f"Name={name}", (target / "index.theme").read_text())
            self.assertTrue((target / "gtk-4.0" / ".libadwaita").is_file())
            self.assertEqual((target / "gnome-shell" / "gnome-shell.css").read_text(), "untouched")
            self.assertIn("EXTRA GRADIENT", (target / "gtk-4.0" / "gtk.css").read_text())
            self.assertIn(".sidebar-pane", (target / "gtk-4.0" / "gtk.css").read_text())
            self.assertIn("stacksidebar.sidebar > scrolledwindow", (target / "gtk-3.0" / "gtk.css").read_text())
            self.assertNotIn("ZORIN VIBRANT EXTRA", (self.root / data["base"] / "gtk-3.0" / "gtk.css").read_text())

    def test_no_new_global_background_gradient_or_shell_change(self) -> None:
        for name, data in module.THEMES.items():
            for version in ("gtk-3.0", "gtk-4.0"):
                extra = module.extra_css(data, version)
                self.assertIsNone(re.search(r"(?m)^\s*\.background\s*\{", extra))
                self.assertNotIn("window.background, .background", extra)
                self.assertNotIn("gnome-shell", extra)
                self.assertNotIn("background-color: white", extra)
                self.assertIn("linear-gradient", extra)

    def test_rejects_unfixed_unsafe_gradient_source(self) -> None:
        name, data = next(iter(module.THEMES.items()))
        css = self.root / data["base"] / "gtk-3.0" / "gtk.css"
        css.write_text(css.read_text() + ".background {\n  background-image: linear-gradient(to bottom, red, blue);\n}\n")
        with self.assertRaisesRegex(ValueError, "unsafe root gradient"):
            module.install_variant(self.root, name, data, False)
        self.assertFalse((self.root / name).exists())

    def test_does_not_overwrite_by_default(self) -> None:
        name, data = next(iter(module.THEMES.items()))
        target = self.root / name
        target.mkdir()
        (target / "mine").write_text("keep")
        with self.assertRaises(FileExistsError):
            module.install_variant(self.root, name, data, False)
        self.assertEqual((target / "mine").read_text(), "keep")

    def test_backup_when_replacing(self) -> None:
        name, data = next(iter(module.THEMES.items()))
        target = self.root / name
        target.mkdir()
        (target / "mine").write_text("keep")
        module.install_variant(self.root, name, data, True)
        backups = list((self.root / ".zorin-extra-gradient-backups").glob(f"{name}-*"))
        self.assertEqual(len(backups), 1)
        self.assertEqual((backups[0] / "mine").read_text(), "keep")

    def test_incomplete_source_no_partial_copy(self) -> None:
        name, data = next(iter(module.THEMES.items()))
        (self.root / data["base"] / "gtk-4.0" / "gtk.css").unlink()
        with self.assertRaisesRegex(ValueError, "Required source file missing"):
            module.install_variant(self.root, name, data, False)
        self.assertFalse((self.root / name).exists())


if __name__ == "__main__":
    unittest.main()
