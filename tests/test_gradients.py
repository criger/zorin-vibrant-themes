"""Isolated filesystem tests for the gradient variants."""
import importlib.util
import tempfile
import unittest
from pathlib import Path

MOD_PATH = Path(__file__).resolve().parents[1] / "scripts" / "install_gradients.py"
spec = importlib.util.spec_from_file_location("gradient_installer", MOD_PATH)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


class GradientThemeTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        for theme in ("ZorinVibrantBlue-Light", "ZorinVibrantBlue"):
            src = self.root / theme
            (src / "gtk-3.0").mkdir(parents=True)
            (src / "gtk-4.0").mkdir()
            (src / "gnome-shell").mkdir()
            (src / "index.theme").write_text(
                f"[Desktop Entry]\nName={theme}\n[X-GNOME-Metatheme]\n"
                f"GtkTheme={theme}\nMetacityTheme={theme}\nIconTheme=ZorinBlue-Light\n"
            )
            for gtk in ("gtk-3.0", "gtk-4.0"):
                (src / gtk / "gtk.css").write_text(
                    "headerbar { color: #123354; border-radius: 15px; }\n"
                )
            (src / "gnome-shell" / "gnome-shell.css").write_text("ORIGINAL")

    def test_both_names_and_css_and_geometry(self):
        for name, info in mod.SPECS.items():
            dest = mod.install_one(self.root, name, False)
            self.assertTrue(dest.exists())
            self.assertIn(f"Name={name}", (dest / "index.theme").read_text())
            self.assertIn("IconTheme=ZorinBlue-Light", (dest / "index.theme").read_text())
            self.assertTrue((dest / "gtk-4.0" / ".libadwaita").exists())
            self.assertEqual((dest / "gnome-shell" / "gnome-shell.css").read_text(), "ORIGINAL")
            for gtk in ("gtk-3.0", "gtk-4.0"):
                css = (dest / gtk / "gtk.css").read_text()
                self.assertIn("linear-gradient(to right", css)
                self.assertIn("linear-gradient(to bottom", css)
                self.assertIn("border-radius: 15px", css)
                self.assertIn(info["title"][0], css)
            self.assertEqual(
                (self.root / info["source"] / "gtk-3.0" / "gtk.css").read_text(),
                "headerbar { color: #123354; border-radius: 15px; }\n",
            )

    def test_no_overwrite_without_explicit_replace(self):
        name = "ZorinVibrantBlue-Gradient"
        target = self.root / name
        target.mkdir()
        (target / "keep").write_text("mine")
        with self.assertRaises(FileExistsError):
            mod.install_one(self.root, name, False)
        self.assertEqual((target / "keep").read_text(), "mine")

    def test_replace_preserves_backup(self):
        name = "ZorinVibrantBlue-Light-Gradient"
        original = self.root / name
        original.mkdir()
        (original / "custom").write_text("saved")
        mod.install_one(self.root, name, True)
        backups = list((self.root / ".zorin-gradient-backups").glob(name + "-*"))
        self.assertEqual(len(backups), 1)
        self.assertEqual((backups[0] / "custom").read_text(), "saved")

    def test_missing_source_rejected(self):
        name = "ZorinVibrantBlue-Gradient"
        (self.root / "ZorinVibrantBlue" / "gtk-4.0" / "gtk.css").unlink()
        with self.assertRaises(ValueError):
            mod.install_one(self.root, name, False)
        self.assertFalse((self.root / name).exists())


if __name__ == "__main__":
    unittest.main()
