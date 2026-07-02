# Active Context

## Current State
- The codebase is structured as a Python desktop application for Windows.
- The memory bank has been initialized to document and track the development of the application.
- The core functionality is fully implemented (temperature monitoring, settings GUI, desktop widget, tray icon, notifications).

## Recent Changes
- Initialized the memory bank files:
  - `projectbrief.md`: Documents the objectives and features.
  - `activeContext.md`: Tracks the current state, focus, and next steps.
  - `progress.md`: Tracks what works, what needs work, and overall status.
  - `systemPatterns.md`: Explains codebase architecture, multi-threading, and system boundaries.
  - `techContext.md`: Lays out the technology stack and requirements.
- Added dynamic theme toggle feature (Dark / Light mode) directly on the draggable Temperature Widget using a Sun/Moon button.
- Extended `monitor.py` and `main.py` to query, store, and display CPU and GPU fan speeds (RPM) and usage loads (%) alongside temperatures.
- Benchmarked query performance: average query takes 0.32s, translating to an estimated 0.4% overall CPU load.

- Implemented recursive `SubHardware` scanning in `monitor.py` to correctly capture CPU fan speeds from the Motherboard's SuperI/O chip.
- Fixed widget layout styling to center the theme toggle button and prevent text clipping on left/right labels.
- Resolved transparent rounded corner black borders on Windows by switching the transparency color mask key to `magenta`.
- Implemented lazy loading of `customtkinter` and `gui.py` inside `main.py` to drastically reduce startup RAM footprint when running in tray-only mode.
- Optimized PyInstaller compilation by using level 2 bytecode optimization (`optimize=2`) and excluding unused libraries (like `unittest`, `multiprocessing`, `setuptools`, etc.).
- Integrated periodic garbage collection (`gc.collect()`) triggers at the end of sensor updates and window close actions.
- Drafted comprehensive release notes for the major v1.3.0 update and appended the release history section to the repository's `README.md`.
- Organized actual user screenshots of the widget themes (dark/light) and all settings panel tabs into the `assets/` folder and embedded them in a structured grid in `README.md`.
- Removed multi-language options to standardize the application to English-only, simplifying configuration storage, notifications, and AI diagnosis prompts.
- Fixed checkbox clipping bug by adding horizontal padding (`padx=(5, 0)`) to option checkboxes and shortening the widget display text labels.
- Added API key masking (`show="*"`) and a visibility toggle button (🔒/👁️) for the Gemini API key input in the settings panel, along with local storage security disclaimers and improved error diagnostics for invalid keys.

## Current Focus
- Verification of optimized memory consumption levels in tray-only mode.


## Next Steps
1. Confirm if any further diagnostic warning levels need adjustments.
2. Confirm with the user if they want fan speeds displayed on the desktop widget as well.
