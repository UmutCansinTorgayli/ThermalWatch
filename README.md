# 🌡️ ThermalWatch

**A lightweight, silent hardware thermal guardian for Windows — living in your system tray, watching your CPU and GPU so you don't have to.**

<p align="center">
  <img src="https://img.shields.io/badge/platform-Windows%2010%2F11-0078D6?style=for-the-badge&logo=windows" alt="Platform">
  <img src="https://img.shields.io/badge/python-3.11-blue?style=for-the-badge&logo=python" alt="Python">
  <img src="https://img.shields.io/badge/license-MIT-green?style=for-the-badge" alt="License">
  <img src="https://img.shields.io/badge/status-active-success?style=for-the-badge" alt="Status">
</p>

> No bloated dashboards. No 200MB Electron monster eating your RAM. Just a tiny tray icon that quietly watches your temps and yells at you — on your desktop **and** on your phone — the second something starts cooking.

---

## 🚀 Why ThermalWatch?

Most hardware monitoring tools want to be the center of your desktop: giant overlays, gamer-RGB dashboards, constant CPU overhead just to tell you a number you'll glance at once a week. **ThermalWatch flips that.** It sits invisibly in your tray, sips almost no resources, and only speaks up when it actually matters — when your CPU or GPU crosses a threshold you define. Then it tells you twice: once on your screen, once on your phone (via [ntfy.sh](https://ntfy.sh)), so you find out even if you've walked away from your desk.

Built by people who got burned (pun intended) by a real AMD Ryzen thermal-reporting nightmare — see the [Troubleshooting Saga](#-the-amd-ryzen--pawnio-saga) below — and turned that pain into a feature.

---

## ✨ Features

- 🖥️ **Silent System Tray Operation** — No taskbar clutter, no intrusive windows. It just lives quietly next to your clock.
- 🌡️ **Real-Time CPU & GPU Monitoring** — Powered by `LibreHardwareMonitorLib` via `pythonnet`, pulling live sensor data straight from your hardware.
- 🔔 **Dual Alert System** — Get notified locally via native **Windows Toast Notifications** (`winotify`) *and* remotely on your phone via **ntfy.sh push notifications**, so you're covered whether you're at your desk or across the room.
- ⏱️ **Anti-Spam Notification Delay** — A carefully tuned **1-second buffer** prevents Windows from silently swallowing back-to-back alerts when CPU and GPU limits are breached in the same instant. No more missed warnings.
- 🖱️ **Live Hover Tooltip** — Hover over the tray icon to instantly see `ThermalWatch | CPU: 44.5°C | GPU: 38.0°C` without opening any window.
- 🎨 **Modern Fluent UI** — Built with `CustomTkinter` and refined with rounded corners (`corner_radius=10/12`) to match the **Windows 11 Fluent Design** language. No more Windows XP-era sharp edges.
- ⚡ **Auto-Start on Boot (Admin-Safe)** — Integrates directly with **Windows Task Scheduler** to launch silently at startup with the highest privileges, without triggering a UAC prompt every single boot.
- 🛠️ **Built-in AMD Ryzen Fix** — A dedicated one-click **"Download PawnIO Driver"** button in Settings, because AMD Ryzen sensor access is a whole saga of its own (see below).
- 🌍 **Fully English Codebase & UI** — Every comment, log line, and interface string has been translated and standardized to English for maximum contributor accessibility.

---

## 🧰 Tech Stack

| Component | Technology | Purpose |
|---|---|---|
| **Language** | Python 3.11 | Core application logic |
| **GUI Framework** | [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter) | Modern, themeable desktop interface |
| **Tray Integration** | [pystray](https://github.com/moses-palmer/pystray) | System tray icon & menu management |
| **Notifications** | [winotify](https://github.com/versa-syahptr/winotify) | Native Windows 10/11 toast notifications |
| **Mobile Push** | [requests](https://docs.python-requests.org/) + [ntfy.sh](https://ntfy.sh) | Remote push alerts to your phone |
| **Hardware Access** | [pythonnet](https://github.com/pythonnet/pythonnet) + `LibreHardwareMonitorLib.dll` | Bridges .NET hardware sensor library into Python |

---

## 5. The AMD Ryzen & PawnIO Saga

This is the story of the bug that almost broke us — and the fix that made ThermalWatch better.

### The Problem

On our primary test rig (**AMD Ryzen 7 5700X + MSI B550**), GPU temperatures came through perfectly. CPU temperature, however, stubbornly returned `0.0` or `None` — every single time.

### The Diagnosis

Running a full LibreHardwareMonitor diagnostic report revealed the smoking gun:

```
PM table layout defined: False
PM table size: 0x000
```

Our first suspicion landed on vendor software like **MSI Center** locking hardware access. That turned out to be a red herring. The real culprit: **Windows 11's Core Isolation / Memory Integrity** feature was silently blocking LibreHardwareMonitor's legacy `WinRing0.sys` kernel driver — a driver that, frankly, modern Windows security features were never going to trust.

### The Fix (Discovered Through User Testing)

The breakthrough came from running the **official LibreHardwareMonitor GUI app** directly. On launch, it displayed a prompt we hadn't seen before:

> *"PawnIO driver is missing. Would you like to download it?"*

After installing **[PawnIO](https://pawnio.eu)** — a modern, signed, Core-Isolation-compatible kernel driver — LibreHardwareMonitor instantly regained full hardware sensor access, CPU temps included.

We took that discovery and built it directly into ThermalWatch:

- ✅ A **"Download PawnIO Driver"** button was added to Settings, opening `pawnio.eu` directly via `webbrowser` — one click, no digging through forums.
- ✅ A clear, step-by-step **troubleshooting guide** was written directly into the app for AMD Ryzen users hitting the same wall.

> 💡 **TL;DR for AMD Ryzen users:** If your CPU temp shows `0°C` or `None`, go to **Settings → Download PawnIO Driver**, install it, and restart ThermalWatch. Problem solved.

---

## 📸 What It Looks Like

*(Screenshots coming soon!)*

---

## 📦 Installation

### Prerequisites

- Windows 10 / 11
- Administrator access *(required — see below ⚠️)*

Choose whichever path fits you — grab the ready-to-go `.exe`, or run it straight from source like a true open-source citizen.

### 🅰️ Option A — Quick Start (Prebuilt `.exe`)

The fastest way to get up and running. No Python required.

1. Head to the **[Releases](https://github.com/UmutCansinTorgayli/ThermalWatch/releases)** page and download the latest `ThermalWatch.exe`.
2. **Right-click → "Run as administrator"** *(see ⚠️ note below — this is not optional).*
3. That's it. The tray icon should appear within a few seconds.
4. **(AMD Ryzen users)** If CPU temperature shows `0°C` or `None`, jump to [Settings → Download PawnIO Driver](#5-the-amd-ryzen--pawnio-saga).

### 🅱️ Option B — Run from Source (For Developers & Tinkerers)

Since ThermalWatch is fully open source, you're welcome — and encouraged — to inspect, modify, and run it directly from the code.

1. **Clone the repository**
   ```bash
   git clone https://github.com/UmutCansinTorgayli/ThermalWatch.git
   cd ThermalWatch
   ```

2. **Install dependencies** *(Python 3.11+ required)*
   ```bash
   pip install -r requirements.txt
   ```

3. **⚠️ Run as Administrator — this is not optional**

   Whether you're using the `.exe` or running from source, ThermalWatch relies on `LibreHardwareMonitorLib.dll` to read low-level hardware sensors (CPU/GPU temperature registers). This **requires elevated (Administrator) privileges** on Windows. Without them, sensor values will silently fail to populate.

   - Run your terminal / IDE itself as Administrator before executing:
     ```bash
     python main.py
     ```

4. **(AMD Ryzen users)** If CPU temperature doesn't appear, jump to [Troubleshooting](#5-the-amd-ryzen--pawnio-saga) and install the PawnIO driver from Settings.

5. **(Optional) Building your own `.exe`**

   Want to package your modified version? A `build.spec` (PyInstaller) is included in the repo — just run:
   ```bash
   pyinstaller build.spec
   ```

### 🔁 Common to Both Options

**Enable auto-start on boot** — Open **Settings → Start with Windows**. This registers a **Task Scheduler** entry configured to run with the **highest privileges**, so ThermalWatch launches silently at boot — no UAC prompt interrupting your morning.

---

## 📲 Setting Up Mobile Push Alerts (ntfy.sh)

1. Install the [ntfy app](https://ntfy.sh) on your phone (iOS/Android) or use the web client.
2. Subscribe to a unique topic, e.g. `thermalwatch-yourname-1337`.
3. Enter that topic name in ThermalWatch's Settings panel.
4. That's it — the next time a threshold is breached, it'll hit your phone in real time.

---

## 🗂️ Configuration

| Setting | Description | Default |
|---|---|---|
| CPU Temp Limit | Threshold (°C) that triggers an alert | `85°C` |
| GPU Temp Limit | Threshold (°C) that triggers an alert | `83°C` |
| ntfy Topic | Your personal ntfy.sh push channel | *(empty)* |
| Start with Windows | Enables silent, elevated auto-start via Task Scheduler | `Off` |
| Notification Delay | Anti-spam buffer between consecutive alerts | `1s` |

---

## 🤝 Contributing

Found a bug? Got an idea? Fighting your own PawnIO-style hardware demon? PRs and issues are very welcome. Please keep code comments and UI strings in English to stay consistent with the rest of the project.

---

## 📄 License

Distributed under the **MIT License**. See `LICENSE` for details.

---

<p align="center">
  Made with 🔥, 🐍, and a healthy grudge against silent sensor failures.
</p>
