# Progress Tracking

## Overall Status
ThermalWatch is in an active, functional state. The codebase is well-commented and translates all outputs/logging to English. The core utility runs silently in the tray, monitors sensors, and alerts on temperature violations.

- **Hardware Integration**: `.NET` `LibreHardwareMonitorLib.dll` loaded successfully via `pythonnet` to read CPU and GPU temperature sensors, usage loads, and fan speeds (including nested Motherboard SuperI/O fans) (`monitor.py`).
- **Configuration Management**: Persistent settings save/load functionality using `config.json` (`config.py`).
- **Tray UI**: System tray icon with dynamic tooltips and right-click menu displaying real-time temperatures and fan speeds, color changes (green/yellow/red) based on temperature status, and clean application exit. Uses deferred loading to initialize Tkinter/CustomTkinter only when windows are actually requested (`main.py`).
- **Settings GUI & Widget**: Modern CustomTkinter interfaces with limits config, startup task automation, health advisor, and theme toggle (optimized with magenta anti-aliasing transparency). Automatically triggers garbage collection (`gc.collect()`) on window/widget destruction to release heap memory back to the OS (`gui.py`).
- **Windows Integration**: Windows Task Scheduler integration for admin-level startup without UAC prompts (`gui.py`).
- **Alert System**: Windows Toast notifications via `winotify` and push notifications via `ntfy.sh` with a 300-second cooldown buffer and a 1-second delay between dual alerts to prevent notification swallowing (`notifier.py`, `main.py`).
- **Release Documentation**: Prepared release notes artifact (`release_notes.md`) for v1.3.0 and updated `README.md` with a clean Release History / Changelog section and actual user interface screenshots (widget themes and settings tabs) in the `assets/` folder. Standardized application to English-only, and fixed layout clipping of option checkboxes on the settings panel.

## What's Left / Future Backlog
- Add real-time CPU/GPU usage monitoring to the alert logic (currently config lists `cpu-max-usage` and `gpu-max-usage` but they are not polled or acted upon in `monitor_loop`).
- Add option to toggle/show fan speeds on the desktop widget.
- Add app screenshots/assets to the repository.
- Verify stability and edge cases (e.g. library missing, driver blocked, network disconnects during `ntfy.sh` request).
