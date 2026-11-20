# Changelog

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
