# 🧾 Changelog — Thermal Viewer
**Date:** October 17, 2025

## Version: `main_neu.py` (replaces `main.py`)

### 🔧 General Improvements
- Major refactor and cleanup for better readability and modularity.
- Complete redesign of display rotation, HUD, and recording logic.
- Improved variable initialization and consistent defaults (`hud=True`, `tempConvert=False`).

### 🧭 New Features & Architecture
- **New function:** `get_rotate_code_and_size()`  
  Returns the proper OpenCV rotation code and display size based on `rotate_mode`.

- **New variable:** `rotate_mode = 270`  
  Enables flexible orientation control (0°, 90°, 180°, 270°).

- **Automatic window resizing** when scale or rotation changes:
  ```python
  if not dispFullscreen:
      cv2.resizeWindow('Thermal', display_w, display_h)
  ```

- **Recording function** updated: now accepts `(w, h)` as parameters for dynamic frame sizes.
- **Snapshot function** now saves the final displayed frame (`img_bgr`) instead of the raw heatmap.

### 🖼️ Display & HUD
- HUD elements (temperature values, map names, etc.) are now drawn **after rotation**, ensuring they remain upright.
- Max/min temperature markers dynamically track within the rotated scene.
- Crosshair temperature readout now appears **bottom-right** after rotation.
- HUD shows average temperature, current colormap, scaling, contrast, and last snapshot time.

### 🎨 Colormap & Visualization
- Default colormap changed from **Bone (0)** to **Turbo (1)**.
- Unified handling of 11 colormaps with a single `colorMapsLen = 11` constant.
- All colormap text labels standardized in the `match` statement.

### 🎥 Recording System
- Output video resolution is now based on the actual frame size (`last_display_frame.shape[:2]`).
- Recording timer formatted via `time.gmtime()` and displayed in the rotated frame.
- “Rec: HH:MM:SS” overlay positioned correctly after rotation.

### 🧊 Other Adjustments
- HUD enabled by default (`hud=True`).
- Temperature conversion starts in Celsius (`tempConvert=False`).
- Simplified `match`-case structure for key handling (A/Z, F/V, M/N, R/T, P, W, H, Q).
- Removed redundant resize calls during key events.
- Improved crosshair and text overlay drawing.

### 💡 Bug Fixes & Stability
- Stabilized temperature calculations (hi/lo value handling).
- Corrected min/max/avg temperature positioning in rotated views.
- Snapshot images now correctly reflect the rotated, colored frame.
- Consistent scaling and resizing logic across all operations.

### 🧩 Removed or Replaced
- Old fixed rotation (`cv2.ROTATE_90_COUNTERCLOCKWISE`) replaced by flexible `rotate_mode` logic.
- `rec()` without parameters removed (now requires `(w, h)`).
- Simplified HUD toggle logic.
- Removed redundant comments and unused colormap references.

### 📈 Overall Effect
The new version is:
- **More modular and maintainable**  
- **Rotation-aware and visually consistent**  
- **Easier to extend** (for future features, e.g. adjustable overlays or extra colormaps)

