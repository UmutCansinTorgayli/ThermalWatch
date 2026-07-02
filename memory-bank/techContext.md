# Technical Context

## Tech Stack & Dependencies

- **Language**: Python 3.11
- **Operating System**: Windows 10 / Windows 11
- **UI Frameworks**:
  - `customtkinter` (Modern theme wrapper around tkinter)
  - `pystray` (System tray integration)
  - `PIL` (`Pillow`) (For generating dynamic tray icons)
- **Windows Integration**:
  - `winotify` (Native toast notifications)
  - `subprocess` calls to `schtasks` (Windows Task Scheduler helper)
- **Hardware Access**:
  - `pythonnet` (Interoperability with C# CLR)
  - `LibreHardwareMonitorLib.dll` (Under `libs/` folder)
- **Network**:
  - `requests` (For push notifications to `ntfy.sh`)

## Setup & Running From Source

1. **Python Environment**:
   It is recommended to run the app using Python 3.11 with a virtual environment (`venv`).
2. **Installation**:
   Install dependencies specified in `requirements.txt`:
   ```bash
   pip install -r requirements.txt
   ```
3. **Execution**:
   Run the main entry script with administrator privileges (required for `pythonnet` to interface with system hardware drivers):
   ```powershell
   python main.py
   ```

## Windows Task Scheduler Integration
To configure the application to run silently on boot with admin rights (and bypass UAC prompts):
- The app schedules a task named `ThermalWatch` running on logon (`/sc onlogon`) with the highest privileges (`/rl highest`).
- Managed dynamically via settings checkbox calling `schtasks.exe`.

## Troubleshooting Known Issues
- **AMD Ryzen CPU Temp N/A (0.0°C)**:
  - Cause: Windows 11 Memory Integrity/Core Isolation blocks the old `WinRing0.sys` kernel driver.
  - Solution: Click "Download PawnIO Driver" in Settings, install PawnIO driver (modern, signed driver), and restart ThermalWatch.
- **Notification Swallowing**:
  - Cause: Windows suppresses toast notifications sent too close together.
  - Solution: Managed via a 1-second delay between dual alerts and alert cooldown periods.
