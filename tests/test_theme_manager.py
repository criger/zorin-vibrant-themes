"""Filesystem and CLI tests for selective multicolor theme management."""
from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from scripts import vibrant_engine as engine
import cleanup_legacy
import install as manager

ROOT = Path(__file__).resolve().parents[1]


class ThemeManagerTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.sources = self.root / 'system-themes'
        self.themes = self.root / 'user-themes'
        for color, pal in engine.PALETTES.items():
            original = self.sources / f'Zorin{color}-Light'
            for gtk in engine.GTK:
                folder = original / gtk
                folder.mkdir(parents=True, exist_ok=True)
                (folder / 'gtk.css').write_text(
                    '/* Original Zorin CSS */\n'
                    '.background { background-color: ' + pal.original[0] + '; }\n'
                    'headerbar { color: #111111; border-radius: 14px; }\n'
                    'placessidebar { background-color: ' + pal.original[1] + '; }\n'
                    '.secondary-sidebar { background-color: ' + pal.original[2] + '; }\n'
                    'headerbar:backdrop { background-color: ' + pal.original[3] + '; }\n',
                    encoding='utf-8',
                )
                (folder / 'gtk-dark.css').write_text('DARK-CSS')
            (original / 'index.theme').write_text(
                f'[Desktop Entry]\nName=Zorin{color}-Light\n'
                f'[X-GNOME-Metatheme]\nGtkTheme=Zorin{color}-Light\n'
                f'MetacityTheme=Zorin{color}-Light\nIconTheme=Zorin{color}-Light\n'
            )
            (original / 'gnome-shell').mkdir()
            (original / 'gnome-shell' / 'gnome-shell.css').write_text('SHELL-UNTOUCHED')
            (original / 'gtk-4.0' / '.libadwaita').touch()

    def install(self, color='Green', kinds=('gradient',), tones=('rich',), replace=False):
        return engine.install_many(color, kinds, themes_dir=self.themes,
                                   sources_dir=self.sources, tones=tones, replace=replace,
                                   license_path=ROOT / 'LICENSE')

    def test_only_one_selected_theme_created(self):
        result = self.install('Green')
        self.assertEqual(['ZorinVibrantGreen-Gradient'], [p.name for p in result])
        self.assertEqual(['ZorinVibrantGreen-Gradient'], engine.discovered(self.themes))
        self.assertFalse((self.themes / 'ZorinVibrantBlue').exists())

    def test_all_eight_colors_four_variants_each(self):
        for color in engine.COLORS:
            paths = self.install(color, ('vibrant', 'gradient'), ('light', 'rich'))
            self.assertEqual(4, len(paths))
            for theme in paths:
                self.assertTrue(theme.is_dir())
                idx = (theme / 'index.theme').read_text()
                self.assertIn(f'GtkTheme={theme.name}', idx)
                self.assertIn(f'IconTheme=Zorin{color}-Light', idx)
                self.assertEqual('SHELL-UNTOUCHED',
                                 (theme / 'gnome-shell' / 'gnome-shell.css').read_text())
                self.assertEqual('DARK-CSS', (theme / 'gtk-3.0' / 'gtk-dark.css').read_text())
                self.assertTrue((theme / 'gtk-4.0' / '.libadwaita').is_file())
                self.assertTrue((theme / 'COPYING').is_file())
                tone = 'light' if '-Light' in theme.name else 'rich'
                pal = engine.palette_for(color, tone)
                for gtk in engine.GTK:
                    css = (theme / gtk / 'gtk.css').read_text()
                    self.assertIn('border-radius: 14px', css)
                    self.assertIn(pal.vibrant[0], css)
                    generated = css.split('/* ZORIN VIBRANT GRADIENT /', 1)
                    if theme.name.endswith('-Gradient'):
                        self.assertEqual(2, len(generated))
                        self.assertIn('linear-gradient(to right', generated[1])
                        self.assertIn('linear-gradient(to bottom', generated[1])
                        self.assertIn('ZORIN VIBRANT EXTRA SIDEBARS', generated[1])
                        self.assertNotIn('\n.background {', generated[1])
                        self.assertNotIn('window.background, .background', generated[1])
                    else:
                        self.assertEqual(1, len(generated))
                        self.assertNotIn('ZORIN VIBRANT EXTRA SIDEBARS', css)
        self.assertEqual(32, len(engine.discovered(self.themes, include_legacy=False)))

    def test_blue_light_matches_original_approved_values(self):
        theme = self.install('Blue', tones=('light',))[0]
        self.assertEqual('ZorinVibrantBlue-Light-Gradient', theme.name)
        css = (theme / 'gtk-3.0' / 'gtk.css').read_text()
        for color in ('#EDF8FF', '#CFE8FF', '#69BDF1', '#B8DFF9', '#D9EBFA'):
            self.assertIn(color, css)
        self.assertNotIn('#439FDF', css)

    def test_green_light_matches_earlier_local_pilot(self):
        theme = self.install('Green', tones=('light',))[0]
        css = (theme / 'gtk-4.0' / 'gtk.css').read_text()
        for color in ('#ECFFF7', '#CDF7E6', '#64DDAA', '#AFEDD2'):
            self.assertIn(color, css)

    def test_current_names_are_never_considered_legacy_cleanup(self):
        self.assertTrue(engine.recognized_names().isdisjoint(engine.legacy_names()))
        for name in ('ZorinVibrantBlue', 'ZorinVibrantBlue-Light',
                     'ZorinVibrantBlue-Light-Gradient'):
            self.assertNotIn(name, engine.legacy_names())

    def test_original_css_unchanged(self):
        source = self.sources / 'ZorinBlue-Light' / 'gtk-3.0' / 'gtk.css'
        original = source.read_bytes()
        self.install('Blue', ('vibrant','gradient'))
        self.assertEqual(original, source.read_bytes())

    def test_blue_matches_known_palettes(self):
        theme = self.install('Blue')[0]
        css = (theme / 'gtk-3.0' / 'gtk.css').read_text()
        self.assertIn('#D4EBFF', css)
        self.assertIn('#439FDF', css)
        self.assertIn('#9DCCF0', css)
        self.assertIn('stacksidebar.sidebar > scrolledwindow', css)

    def test_no_overwrite_and_explicit_backup(self):
        p = self.install('Red')[0]
        (p / 'keep').write_text('saved')
        with self.assertRaises(FileExistsError):
            self.install('Red')
        self.assertEqual('saved', (p / 'keep').read_text())
        self.install('Red', replace=True)
        self.assertFalse((p / 'keep').exists())
        backup = list((self.themes / '.zorin-vibrant-backups').glob('ZorinVibrantRed-Gradient-*'))
        self.assertEqual(1, len(backup))
        self.assertEqual('saved', (backup[0] / 'keep').read_text())

    def test_incompatible_original_refused_before_any_install(self):
        css = self.sources / 'ZorinYellow-Light' / 'gtk-3.0' / 'gtk.css'
        css.write_text('headerbar { background: #000; }')
        css4 = self.sources / 'ZorinYellow-Light' / 'gtk-4.0' / 'gtk.css'
        css4.write_text('headerbar { background: #000; }')
        with self.assertRaisesRegex(ValueError, 'missing colors'):
            self.install('Yellow', ('vibrant', 'gradient'))
        self.assertFalse(self.themes.exists())

    def test_atomic_staging_failure_both_variants(self):
        real = engine._render
        calls = 0
        def broken(*args, **kwargs):
            nonlocal calls
            calls += 1
            if calls == 2:
                raise OSError('synthetic failure')
            return real(*args, **kwargs)
        with mock.patch.object(engine, '_render', side_effect=broken):
            with self.assertRaisesRegex(OSError, 'synthetic failure'):
                self.install('Purple', ('vibrant','gradient'))
        self.assertEqual([], engine.discovered(self.themes))

    def test_uninstall_one_leaves_other_themes_and_system(self):
        self.install('Brown', ('vibrant','gradient'))
        original = self.sources / 'ZorinBrown-Light' / 'index.theme'
        content = original.read_text()
        engine.uninstall(self.themes, 'ZorinVibrantBrown-Gradient')
        self.assertEqual(['ZorinVibrantBrown'], engine.discovered(self.themes))
        self.assertEqual(content, original.read_text())
        with self.assertRaisesRegex(ValueError, 'unexpected theme'):
            engine.uninstall(self.themes, 'ZorinBrown-Light')

    def test_cleanup_only_obsolete_extras_never_current_names(self):
        current = ('ZorinVibrantBlue', 'ZorinVibrantBlue-Light-Gradient',
                   'ZorinVibrantGreen-Light', 'ZorinVibrantPurple-Gradient')
        obsolete = ('ZorinVibrantGreen-Light-extra-gradient', 'ZorinVibrantBlue-Glass')
        for name in current + obsolete:
            (self.themes / name).mkdir(parents=True, exist_ok=True)
        found = cleanup_legacy.run(self.themes, dry_run=True)
        self.assertEqual(sorted(obsolete), found)
        cleanup_legacy.run(self.themes, confirmed=True)
        self.assertEqual(sorted(current), engine.discovered(self.themes))

    def test_uninstall_light_leaves_rich_intact(self):
        self.install('Green', ('vibrant', 'gradient'), ('light', 'rich'))
        engine.uninstall(self.themes, 'ZorinVibrantGreen-Light-Gradient')
        self.assertEqual(3, len(engine.discovered(self.themes)))
        self.assertTrue((self.themes / 'ZorinVibrantGreen-Gradient').exists())

    def test_conflict_prevents_creating_any_tone(self):
        old = self.install('Blue', tones=('light',))[0]
        (old / 'marker').write_text('keep')
        with self.assertRaises(FileExistsError):
            self.install('Blue', kinds=('gradient',), tones=('light', 'rich'))
        self.assertFalse((self.themes / 'ZorinVibrantBlue-Gradient').exists())
        self.assertEqual('keep', (old / 'marker').read_text())

    def test_uninstall_symlink_does_not_follow_target(self):
        other = self.root / 'protected'
        other.mkdir()
        (other / 'file').write_text('preserve')
        self.themes.mkdir()
        (self.themes / 'ZorinVibrantGreen').symlink_to(other, target_is_directory=True)
        engine.uninstall(self.themes, 'ZorinVibrantGreen')
        self.assertEqual('preserve', (other / 'file').read_text())

    def test_confirmation_prompt_uses_english_yes_no(self):
        prompts = []
        with mock.patch('builtins.input', side_effect=lambda prompt: (prompts.append(prompt) or 'y')):
            self.assertTrue(manager.yes('Continue?'))
        with mock.patch('builtins.input', side_effect=lambda prompt: (prompts.append(prompt) or '')):
            self.assertFalse(manager.yes('Continue?'))
        self.assertEqual(['Continue? [y/N]: ', 'Continue? [y/N]: '], prompts)

    def test_cli_no_existing_theme_skips_action_choice(self):
        # 2=Green, 2=rich tone, 2=Gradient, y=confirm, 0=exit.
        with mock.patch('builtins.input', side_effect=['2','2','2','y','0']):
            with mock.patch.object(manager, 'DEFAULT_THEMES_DIR', self.themes):
                manager.interactive(self.themes, self.sources)
        self.assertTrue((self.themes / 'ZorinVibrantGreen-Gradient').is_dir())

    def test_cli_light_option_installs_only_light(self):
        # 2=Green, 1=light, 1=Vibrant, y=confirm, 0=exit.
        with mock.patch('builtins.input', side_effect=['2', '1', '1', 'y', '0']):
            with mock.patch.object(manager, 'DEFAULT_THEMES_DIR', self.themes):
                manager.interactive(self.themes, self.sources)
        self.assertEqual(['ZorinVibrantGreen-Light'], engine.discovered(self.themes))

    def test_cli_both_tones_both_styles_installs_four(self):
        # 3=Yellow, 3=both tones, 3=both kinds, y, 0=exit.
        with mock.patch('builtins.input', side_effect=['3', '3', '3', 'y', '0']):
            with mock.patch.object(manager, 'DEFAULT_THEMES_DIR', self.themes):
                manager.interactive(self.themes, self.sources)
        actual = engine.discovered(self.themes)
        self.assertEqual(4, len(actual))
        self.assertEqual(4, sum('Yellow' in n for n in actual))

    def test_cli_existing_theme_first_asks_install_or_remove(self):
        self.install('Green', ('vibrant',))
        # Choice 2=uninstall, item 1, y=confirm, 0=exit.
        with mock.patch('builtins.input', side_effect=['2','1','y','0']):
            with mock.patch.object(manager, 'DEFAULT_THEMES_DIR', self.themes):
                manager.interactive(self.themes, self.sources)
        self.assertEqual([], engine.discovered(self.themes))

    def test_cli_noninteractive_light_install_and_list(self):
        cli = ROOT / 'install.py'
        create = subprocess.run([sys.executable, str(cli), '--install', 'orange',
            '--variant', 'gradient', '--tone', 'light', '--yes', '--themes-dir', str(self.themes),
            '--sources-dir', str(self.sources)], capture_output=True, text=True)
        self.assertEqual(0, create.returncode, create.stderr)
        listing = subprocess.run([sys.executable, str(cli), '--list',
            '--themes-dir', str(self.themes)], capture_output=True, text=True)
        self.assertEqual(0, listing.returncode, listing.stderr)
        self.assertIn('ZorinVibrantOrange-Light-Gradient', listing.stdout)


if __name__ == '__main__':
    unittest.main()
