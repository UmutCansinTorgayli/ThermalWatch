# ThermalWatch Project Brief

## Project Overview
ThermalWatch is a lightweight, silent, and resource-efficient hardware thermal guardian for Windows. It runs in the system tray and monitors CPU and GPU temperatures, alerting the user via local Windows notifications and remote push notifications (via `ntfy.sh`) when temperatures cross user-defined limits.

It serves as a lightweight alternative to resource-heavy hardware monitoring dashboards.

## Core Features
1. **System Tray Integration**: Lives silently in the system tray, showing real-time temperature stats on hover via a tooltip.
2. **Real-time Monitoring**: Queries CPU and GPU temperatures using a C# library (`LibreHardwareMonitorLib.dll`) via `pythonnet`.
3. **Dual Alert System**: 
   - **Local**: Windows Toast notifications (`winotify`).
   - **Remote**: Push notifications to the user's phone (`ntfy.sh`).
4. **Desktop Widget**: A draggable, frameless, semi-transparent temperature widget overlay.
5. **Modern Settings Panel**: Fluent UI styled window (`customtkinter`) to edit temperature thresholds, CPU/GPU usage limits, mobile alert topic, and Windows startup run configuration.
6. **Auto-Start on Boot**: Integrates with Windows Task Scheduler (`schtasks`) to run at startup with administrator privileges (bypassing UAC prompts after initial setup).
7. **AMD Ryzen Support**: Troubleshoots and assists AMD users to download the signed `PawnIO` driver to resolve missing CPU sensor data.
