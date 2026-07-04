# System Patterns

## Architecture & Code Structure

The application follows a simple modular structure in Python:

```
d:\ThermalWatch\
├── config.json         # Persisted user settings (JSON format)
├── config.py           # Configuration manager (load/save settings)
├── gui.py              # CustomTkinter UI (Settings panel, Desktop Widget)
├── main.py             # Main entry point (Tray icon, monitoring loop, orchestrator)
├── monitor.py          # Hardware access bridge (pythonnet + LibreHardwareMonitorLib.dll)
├── notifier.py         # Notification dispatchers (winotify & requests for ntfy.sh)
└── libs/               # Directory containing LibreHardwareMonitorLib.dll dependency
```

## Concurrency & Threading Model

Since GUI toolkits (Tkinter/CustomTkinter) and system tray handlers (`pystray`) require blocking event loops on the main thread, the application uses Python's `threading` module to run concurrent operations:

1. **Main Thread**: Runs the `pystray.Icon` loop (`icon.run()`), which blocks to listen for mouse clicks, hovers, and context menus.
2. **Monitoring Loop Thread**: Runs `monitor_loop(icon)` in a daemon thread. It runs a `while True` loop that polls hardware temperatures every 5 seconds, updates the tray icon/tooltip, and dispatches notifications if limits are breached.
3. **Settings Window Thread**: Spawns a separate daemon thread when the user clicks "Settings" to execute `open_settings_window()` without blocking the tray icon.
4. **Widget Thread**: Spawns a separate daemon thread to run the `TemperatureWidget` mainloop.

## Hardware Data Querying Pattern

Temperature queries leverage the C# `.NET` framework library `LibreHardwareMonitorLib.dll` bridged into Python via `pythonnet`:
- `monitor.py` adds reference to `LibreHardwareMonitorLib`.
- Initializes `LibreHardwareMonitor.Hardware.Computer` object with CPU and GPU tracking enabled.
- Queries `sensor.SensorType == SensorType.Temperature`.
- Matches names:
  - **CPU**: Look for `"package"`, `"tdie"`, or `"tctl"` in the sensor name to get correct package temperature.
  - **GPU**: Look for `"core"` or `"gpu core"`.
- Uses a defensive `try...except` wrap to handle cases where hardware query permissions or drivers are blocked.

## Anti-Spam / Rate Limiting Alerts Pattern

To avoid flooding the user when CPU and GPU temps cross thresholds simultaneously:
- Cooldown timer (`ALERT_COOLDOWN = 300` seconds / 5 minutes) tracked separately for CPU and GPU.
- A **1-second delay** (`time.sleep(1)`) is introduced before the GPU alert if both CPU and GPU limits are breached at the same time. This ensures Windows notification center does not drop/swallow the second toast notification.

## GUI Redesign & Sidebar Pattern

To transition from a simple tabbed panel to a modern Windows 11 Fluent layout:
- **Left Sidebar Page Switcher**: The Settings Window is structured with a left-hand navigation sidebar (`180px` wide) containing category buttons and a right-hand main content frame. Clicking a sidebar button dynamically hides the previous category frame and maps the selected category frame in the content area.
- **Card-based Settings Grouping**: Settings items are nested inside rounded `CTkFrame` boxes with thin borders to mimic Windows 11 cards.
- **In-App AI Diagnostics Panel**: Instead of triggering standard popups, the "Diagnostics" button launches an asynchronous thread that queries the selected AI engine (Gemini or Ollama) using rolling telemetry data, displaying a loading status directly in the UI before rendering results in an embedded, scrollable textbox.
- **Custom Dialogs**: Validation errors and save confirmations are handled via modern `CTkToplevel` custom-drawn widgets rather than standard Windows MessageBox APIs.
- **Individual Sensor Widget Colors**: The desktop widget updates the color of the CPU and GPU temperature labels independently according to their respective thresholds.

