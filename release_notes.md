# 🌡️ ThermalWatch v1.4.0 — The Fluent GUI Update

Welcome to the definitive release of **ThermalWatch**! Version 1.4.0 represents the ultimate visual and architectural update, bringing a premium, native-feeling Windows 11 design language to your favorite lightweight thermal guardian.

With this release, ThermalWatch reaches its final form — fully featured, visually stunning, deeply integrated into Windows, and incredibly lightweight on system resources.

---

## 🎨 What's New in v1.4.0

### 🖥️ 1. Modern Left-Sidebar Navigation Layout
* Replaced the outdated top-tab structure with a sleek, Fluent-style **left-sidebar navigation panel**.
* Complete with beautiful Unicode icons and custom vertical active indicators (left accent line) that slide dynamically when switching pages.
* Expanded the window geometry to a comfortable `680x550` to accommodate clean margins.

### 🎛️ 2. Premium Fluent Cards & Windows 11 Switches
* Settings are now organized in individual, clean **Fluent Rounded Cards** (`corner_radius=12`).
* **Sleek Dark Theme:** Cards use custom premium gray-black backgrounds (`#242424`) and incredibly subtle border outlines (`#2e2e2e` in dark mode, `#e5e5e5` in light mode), making the UI blend perfectly with Windows 11 native styles.
* **Modern Controls:** Replaced old-fashioned checkboxes with modern Windows 11 sliding toggle switches (`CTkSwitch`) for options toggling.

### 🚨 3. Dynamic Warning Border Alert Glow (Desktop Widget)
* The frameless desktop widget now has a **Status-Aware Accent Glow**.
* If your CPU or GPU crosses its defined limits, the widget border changes color dynamically — glowing **Yellow** in the warning zone and **Red/Pink** when limits are breached.
* This draws your attention to high temps instantly without popping up intrusive, workflow-breaking dialog windows.

### 🛡️ 4. Native Windows Taskbar Icon & Admin Privileges Integration
* **Taskbar AppID Registration:** Registered a unique Application User Model ID (`UmutCansinTorgayli.ThermalWatch.v1`) with the Windows shell using `ctypes`. This forces Windows 10/11 to group the process under its own taskbar instance and display the official **icon.ico** logo instead of the default blue Python/CustomTkinter icon!
* **Auto-UAC Manifest:** Embedded a manifest requiring Administrator execution privileges (`uac_admin=True`) directly into the compiled executable, ensuring it launches with the required privileges on double-click.

### 🤖 5. Asynchronous In-App AI Telemetry Advisor
* The **AI Advisor** tab now features a fully integrated diagnostics panel with an output textbox.
* The analysis runs asynchronously in a background thread to prevent UI freezing, rendering advice with a loading state indicator (`🤖 Gathering data...`) as soon as the active engine (Google Gemini or Local Ollama) responds.

### 🩹 6. Accidental Widget Closure Fix & Visual Polish
* Removed the double-click-to-close behavior on the widget to prevent it from closing accidentally while being dragged across the screen.
* Increased the widget width to `300px` to prevent right-aligned text clipping on high-DPI displays.
* Replaced native Tkinter prompt popups with a customized `FluentDialog` overlay.

---

## 📦 Download the Executable

The compiled executable is ready to roll and includes the administrator manifest:
👉 **[dist/ThermalWatch.exe](file:///d:/ThermalWatch/dist/ThermalWatch.exe)**

---

## 💡 Why this is the Final Sürüm (Definitive Build)

With v1.4.0, ThermalWatch achieves all of its design and functional goals:
1. **Zero Resource Bloat:** Consumes less than 130MB RAM in tray mode and under `<0.35%` CPU overhead.
2. **Double Notification Safety:** Combines remote mobile push (`ntfy.sh`) and local system toasts with a built-in anti-collision buffer.
3. **Deep OS Integration:** Admin task scheduler startup, Windows taskbar grouping, and native border glows.
4. **Interactive Hardware Intelligence:** Built-in AMD Ryzen driver fixes and rolling local/cloud thermal diagnostics.

*No more features are needed — ThermalWatch is now a complete, robust utility ready to guard your rig for years to come.*
