# Zorin Vibrant Themes

**A splash of blue for Zorin OS — without replacing what makes Zorin work.**

Zorin Vibrant Themes provides four blue-forward, light-mode GTK theme variants based on Zorin's original `ZorinBlue-Light` theme. The idea is simple: keep Zorin's rounded corners, widgets, spacing and layout, but replace its muted gray-blue surfaces with cleaner, more colorful blues.

> **Unofficial community project** by **Cristhian Gertner**. Not affiliated with or endorsed by Zorin OS.

## Original color themes

| Variant | Window background | Sidebar / borders | Secondary sidebar | Inactive background |
| --- | --- | --- | --- | --- |
| **ZorinVibrantBlue-Light** | `#EDF8FF` | `#CFE8FF` | `#DDEEFF` | `#F1F8FF` |
| **ZorinVibrantBlue** | `#D4EBFF` | `#B4D8F6` | `#C5E2FA` | `#EAF5FF` |

Both variants retain Zorin's original bright blue accent (`#15A6F0`), dark text, light content views, and widget geometry. **Neither variant is a dark theme.** The name without `-Light` means *stronger blue*, not dark mode.

These are GTK application themes, **not** replacements for Zorin Taskbar, GNOME Shell or your icon set.


## Optional gradient variants

The gradient experiment introduces **two additional light-based GTK themes** without
replacing the original two:

| New gradient theme | Derived from | Appearance |
| --- | --- | --- |
| `ZorinVibrantBlue-Light-Gradient` | `ZorinVibrantBlue-Light` | Soft, airy blue gradients |
| `ZorinVibrantBlue-Gradient` | `ZorinVibrantBlue` | Richer blue gradients |

The gradient themes add a **horizontal titlebar gradient**, more subtle **vertical
sidebar and window-background gradients**, and softer inactive-window colors.
They do **not** add transparency, blur, alter the taskbar or replace GNOME Shell.
Not every GTK application honors all CSS overrides.

Install the two standard variants first (see [Install](#install)); then run:

```bash
python3 scripts/install_gradients.py
```

If you already installed the local gradient prototypes and want to reinstall
from GitHub while keeping a dated backup:

```bash
python3 scripts/install_gradients.py --replace
```

Backups of gradient themes are placed under `~/.themes/.zorin-gradient-backups/`.
The original Vibrant variants and the system themes remain untouched.
Use Zorin Appearance → Theme → Other → Applications, or switch from a terminal:

```bash
gsettings set org.gnome.desktop.interface color-scheme 'default'
gsettings set org.gnome.desktop.interface gtk-theme 'ZorinVibrantBlue-Light-Gradient'
# Or:
gsettings set org.gnome.desktop.interface gtk-theme 'ZorinVibrantBlue-Gradient'
```

To roll back, switch to `ZorinVibrantBlue-Light` or `ZorinVibrantBlue`.
To uninstall the gradient variants, switch away first and remove only their
two generated folders from `~/.themes/`. Reopen applications to see changes.

**Compatibility:** Developed and visually evaluated on the maintainer's Zorin
OS 18.1 desktop, including GTK3/GTK4 applications. Automated tests use synthetic
theme fixtures; installation from this newly published script has not yet
been separately tested on the actual desktop.

## Requirements

- Zorin OS with the stock `/usr/share/themes/ZorinBlue-Light` theme (developed on Zorin OS 18.1).
- Python 3, standard library only; no third-party Python packages.
- A local desktop session to select the resulting GTK theme.

## Install

```bash
cd ~
git clone https://github.com/criger/zorin-vibrant-themes.git
cd zorin-vibrant-themes
python3 scripts/install.py
```

The installer creates both themes in `~/.themes/`, copying your **locally installed original Zorin theme**. Nothing in `/usr/share/themes/` is changed and no `sudo` is needed.

If you already installed early prototypes, run this instead to back them up and replace them:

```bash
python3 scripts/install.py --replace
```

You can also install a single variant:

```bash
python3 scripts/install.py --variant ZorinVibrantBlue-Light
python3 scripts/install.py --variant ZorinVibrantBlue
```

### Activate

Open **Zorin Appearance → Theme → Other → Applications** and select `ZorinVibrantBlue-Light` or `ZorinVibrantBlue`.

Or use GSettings:

```bash
gsettings set org.gnome.desktop.interface color-scheme 'default'
gsettings set org.gnome.desktop.interface gtk-theme 'ZorinVibrantBlue'
```

Close and reopen affected applications, including Nemo, Nautilus and the Software store, to see the changes. GTK4/libadwaita behavior is subject to Zorin's theming support and may vary by application or system version.

### Switch or roll back

```bash
# Brighter, more saturated blue
gsettings set org.gnome.desktop.interface gtk-theme 'ZorinVibrantBlue'

# Softer, lighter blue
gsettings set org.gnome.desktop.interface gtk-theme 'ZorinVibrantBlue-Light'

# Restore stock Zorin GTK theme
gsettings set org.gnome.desktop.interface gtk-theme 'ZorinBlue-Light'
```

To remove the themes, first switch away from them and then delete the two user theme directories. `--replace` keeps dated backups in `~/.themes/.zorin-vibrant-backups/`; review those before deleting them.

## What the installer actually changes

- Copies `ZorinBlue-Light` from the machine into a separately named user theme.
- Makes exact color substitutions in `gtk-3.0/gtk.css` and `gtk-4.0/gtk.css` only, preserving layout and selectors.
- Updates the copied `index.theme` GTK/theme names while retaining `IconTheme=ZorinBlue-Light`.
- Ensures the `gtk-4.0/.libadwaita` marker is present for Zorin's theme integration.
- Adds a derivative-change notice and a GPL license copy to generated theme folders.

The installed theme also contains the upstream files that `ZorinBlue-Light` already shipped, including GNOME Shell CSS; this project **does not activate or customize** those files. It does not modify the panel, GNOME extensions, icons, wallpaper or system files. No network access is required after cloning.

**Known limitations:** Some apps use their own style sheets or ignore GTK theme selection. The installer intentionally updates only the *light* CSS files (`gtk.css`), not `gtk-dark.css`. Keep the system color scheme set to `default`.

## Development and tests

```bash
python3 -m unittest discover -s tests -v
python3 -m compileall -q scripts tests
```

Tests cover the original and gradient installers using synthetic Zorin-style theme fixtures, so they can run without installing any theme or modifying your desktop. Zorin OS 18.1 appearance was manually reviewed during palette prototyping; cross-version compatibility remains to be verified.

## Credits, copyright and licensing

- **Original upstream theme:** [Zorin Desktop Themes](https://github.com/ZorinOS/zorin-desktop-themes) — © its original authors, distributed under GNU GPL version 2.
- **Zorin Vibrant Themes:** color selection, installer, docs and maintenance by **Cristhian Gertner**, © 2026 where applicable.
- **License:** [GNU General Public License v2](LICENSE) (`GPL-2.0-only`). Users may use, study, modify and redistribute the work under that license, with required notices and the same freedoms for derivatives.

The repository **does not vendor Zorin's original theme CSS**. The installer creates a GPL-licensed derivative using the user's existing Zorin installation and records a change notice. This project does not claim authorship of Zorin's original files.

## Related work

[ZorinOS Fisheye Taskbar](https://github.com/criger/zorinos-fisheye-taskbar) enhances the existing bottom taskbar while leaving Zorin's taskbar layout intact. It is independent of this theme.

Contributions and bug reports are welcome. Include your Zorin version, GTK app/version and a screenshot with private information removed.
