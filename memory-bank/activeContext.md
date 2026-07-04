# Active Context

## Current State
- The codebase is structured as a Python desktop application for Windows.
- The memory bank has been initialized to document and track the development of the application.
- The core functionality is fully implemented (temperature monitoring, settings GUI, desktop widget, tray icon, notifications).

## Recent Changes
- Redesigned the settings panel using a left-sidebar page switcher (`680x550` layout) with modern Windows 11 Fluent-style rounded cards and slider controls.
- Replaced native Tkinter messageboxes with a custom `FluentDialog` (CTkToplevel).
- Integrated the AI Diagnostics output textbox directly in the settings panel with asynchronous query support and loading state indicator.
- Upgraded the settings UI controls by replacing old-style checkboxes with modern Windows 11 toggle switches (`ctk.CTkSwitch`).
- Implemented **Padding Shadow Wrappers** for settings panel cards (CPU, GPU, and Options) using slightly darker outer frames and bottom-heavy offset padding to emulate a native drop-shadow feel.
- Modified the PyInstaller specification (`ThermalWatch.spec`) with `uac_admin=True` to embed a manifest requiring Administrator execution privileges on double-click launch.
- Upgraded the frameless Temperature Widget:
  - Added visual divider frames next to the theme toggle.
  - Implemented independent CPU and GPU text coloring based on individual sensor status.
  - Implemented a **Dynamic Warning Border Accent Glow** where the widget border turns yellow or red matching the worst-case sensor alert state.
  - Enabled **Native Windows Drop Shadows** under the frameless widget window class using OS `ctypes` bindings.
  - Removed the double-click-to-close binding on the widget to avoid accidental closing while dragging.
  - Increased widget width from 280px to 300px to prevent right-side text clipping ("GPU" showing as "PU").
  - Fixed CustomTkinter button clipping and sharp-edge canvas bugs by setting explicit widths on settings action buttons.

## Current Focus
- Verification of the new Windows 11 Fluent settings arayüzü and widget.
- Final stability validation and telemetry diagnostics output checking.

## Next Steps
1. Test the dynamic border warning glow under simulated heavy CPU/GPU loads.
2. Verify local Ollama and Google Gemini diagnostic reports render cleanly.
3. Keep monitoring Windows system tray integration reliability.

