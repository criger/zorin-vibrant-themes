# Changelog

## 2026-11-21 — Interactive international theme manager (8 colors, 32 choices)

- Added root-level `install.py`: interactive Install / Uninstall / Show installed with English prompts and `[y/N]` confirmations; installs only explicitly selected themes.
- Added `scripts/vibrant_engine.py` with eight stock Zorin color families (Blue, Green, Yellow, Orange, Red, Purple, Brown, Grey), two light-based intensities (Light and Rich), and two styles (Vibrant and Gradient).
- The new `-Gradient` style includes the former Extra-Gradient sidebar selectors; no glass, translucency, blur, broad root background overrides, Shell or taskbar changes.
- Added safe uninstall, backup-on-explicit-replacement, atomic staging/rollback, exact source validation, and `cleanup_legacy.py` for retired Blue/Green `-extra-gradient` / `-Glass` names only.
- Preserved existing historical installer scripts, source files, full-resolution README screenshots, Buy Me a Coffee section and copyright attribution.
- Added 21 theme-manager tests (21/21 passed locally), covering 32 selections, English menus, selective install, rollback, and safe removal. Prior 15 test files were not rerun together with these in this release.
- Maintainer visually approved the v2 local manager and tested installing and uninstalling on Zorin OS 18.1. Other Zorin releases and complete per-app matrix are not verified.

## 2026-11-20 — Add two Extra-Gradient variants

- Added `ZorinVibrantBlue-Light-extra-gradient` and `ZorinVibrantBlue-extra-gradient`, each derived from the corresponding installed Gradient theme.
- Added targeted GTK3 side-panel scroller and GTK4 sidebar-pane / navigation-list gradients; existing titlebar effects remain intact.
- No broad root-window background CSS or GNOME Shell/taskbar changes; source Gradient themes are left unchanged.
- Installer checks the wallpaper safety fix, refuses unsafe source themes, and backs up prior Extra-Gradient variants with `--replace`.
- Added six isolated tests for the new installer (15 tests across the project).
- Both Extra-Gradient variants were approved visually on Zorin OS 18.1; the user confirmed normal behavior when all windows are minimized.

## 2026-11-20 — Fix white wallpaper when windows minimized

- Removed broad `.background` / `window.background` gradient overrides in
  both GTK3 and GTK4, preserving the titlebar and sidebar gradients.
- Added regression coverage to ensure future generated gradient themes do not
  reintroduce global desktop/window background overrides (9 tests total).
- Both variants were corrected locally and the user confirmed the desktop
  wallpaper remains visible when all windows are minimized.
- Original non-gradient themes, GNOME Shell and taskbar remain unchanged.

## 2026-11-20 — Add optional gradient variants

- Added `ZorinVibrantBlue-Light-Gradient` and `ZorinVibrantBlue-Gradient` with
  horizontal titlebar and vertical sidebar/window CSS gradients in GTK3/GTK4.
- Gradient installer derives from the two locally installed base Vibrant themes.
- Existing themes and system CSS are preserved; `--replace` backs up older
  gradient variants.
- Added four isolated filesystem regression tests (eight total).
- Gradient palettes were approved in a local user test before publication.
- Transparency and blur are **not** included; a separate Glass experiment is next.

## 2026-11-20 — Initial public release

- Two light-based variants: `ZorinVibrantBlue-Light` and `ZorinVibrantBlue`.
- Preserved original widget styling and accents while changing grayed backgrounds.
- Added Python standard-library installer with safe backup/replacement support.
- Added source-color compatibility checks, generated copyright/change notice
  and preserved GTK4 `.libadwaita` marker.
- Added four filesystem/recoloring regression tests.
- Included public README, GPL-2.0 license and upstream attribution.

**Notes:** The initially attempted *dark* interpretation of the non-light name was
rejected; both released variants use `ZorinBlue-Light` as their base.
