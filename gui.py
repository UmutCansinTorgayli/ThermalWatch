# pyrefly: ignore [missing-import]
from PIL import ImageDraw
import customtkinter as ctk
import subprocess
import sys
import os
import threading
import requests
import ctypes
from config import load_settings, save_settings

try:
    # Register AppUserModelID to show the taskbar icon correctly on Windows
    myappid = "UmutCansinTorgayli.ThermalWatch.v1"
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
except Exception:
    pass

# --- GLOBAL STYLING CONFIGS ---
ctk.set_appearance_mode("dark")      
ctk.set_default_color_theme("blue")   

TRANSLATIONS = {
    "English": {
        "title": "ThermalWatch Settings",
        "tab_limits": "Limits & Widget",
        "tab_telemetry": "Telemetry",
        "tab_ai": "AI Advisor",
        "tab_pawnio": "PawnIO Help",
        "cpu_settings": "CPU Thresholds",
        "gpu_settings": "GPU Thresholds",
        "max_temp": "Max Temp Limit",
        "max_usage": "Max Usage Limit",
        "ntfy_label": "ntfy.sh Topic Name (Mobile Alerts):",
        "startup": "Start with Windows (Run as Admin)",
        "show_usage": "Show usage loads (%) on desktop widget",
        "show_fans": "Show fan speeds (RPM) on desktop widget",
        "save": "Save Settings",
        "cancel": "Cancel",
        "diagnose": "🔍 Run Telemetry Diagnosis",
        "cpu_status": "CPU Status",
        "gpu_status": "GPU Status",
        "temp": "Temp",
        "usage": "Usage",
        "fan": "Fan",
        "ai_engine": "Select AI Diagnostics Engine:",
        "ai_none": "✅ Classic Rule-based Advisor Active",
        "ai_none_desc": "💡 Built-in Advisor features:\n- Instantaneous response.\n- Zero resource usage (0% CPU, 0 MB memory overhead).\n- No Internet connection or external software required.",
        "gemini_key": "Gemini API Key:",
        "get_key": "🔑 Get Free API Key (Google AI Studio)",
        "gemini_desc": "💡 Cloud AI features:\n- 100% Free: Google's developer tier has no costs.\n- High Speed: Diagnostics are analyzed in under 1 second.\n- Zero Installation: Nothing to download or run on your PC.\n- 🔒 Security: Stored locally in config.json and sent directly to Google.",
        "status_ready": "Status: Ready",
        "install_ollama": "📥 Auto-Install Ollama & Model",
        "ollama_desc": "💡 Local AI features:\n- 100% Offline: Data never leaves your PC.\n- Requirements: Download approx. 200MB installer + 900MB Qwen model.\n- Click Auto-Install to automate this process in the background.",
        "pawn_title": "AMD Ryzen Temperature Fix",
        "pawn_desc": "💡 CPU N/A Troubleshooting:\n\n1. Always run ThermalWatch 'As Administrator'.\n2. If CPU temperature is still not showing on AMD Ryzen,\n   you must install the PawnIO driver.\n3. PawnIO is a secure driver compatible with Core Isolation.",
        "pawn_btn": "Download PawnIO Driver",
        "success": "Success",
        "success_msg": "Settings have been saved successfully!",
        "error": "Error",
        "error_msg": "Could not save settings.",
        "invalid_input": "Invalid Input",
        "invalid_input_msg": "Please enter valid values for limits."
    }
}

# --- CUSTOM FLUENT DIALOG POPUP ---
class FluentDialog(ctk.CTkToplevel):
    def __init__(self, parent, title, message, is_error=False):
        super().__init__(parent)
        self.title(title)
        self.geometry("360x180")
        self.resizable(False, False)
        
        # Always on top and modal grab
        self.attributes("-topmost", True)
        self.transient(parent)
        self.grab_set()
        
        # Center dialog relative to settings window
        parent.update_idletasks()
        parent_x = parent.winfo_x()
        parent_y = parent.winfo_y()
        parent_w = parent.winfo_width()
        parent_h = parent.winfo_height()
        x = parent_x + (parent_w - 360) // 2
        y = parent_y + (parent_h - 180) // 2
        self.geometry(f"360x180+{x}+{y}")
        
        # Fluent container
        frame = ctk.CTkFrame(self, corner_radius=12, border_width=1, border_color=("#ccd0da", "#3a3a3a"), fg_color=("#ffffff", "#2b2b2b"))
        frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        symbol = "❌" if is_error else "✅"
        symbol_color = "#f38ba8" if is_error else "#a6e3a1"
        
        lbl_symbol = ctk.CTkLabel(frame, text=symbol, font=("Segoe UI", 26), text_color=symbol_color)
        lbl_symbol.pack(pady=(15, 2))
        
        lbl_msg = ctk.CTkLabel(frame, text=message, font=("Segoe UI", 12), wraplength=310, justify="center")
        lbl_msg.pack(fill="both", expand=True, padx=15, pady=2)
        
        btn_color = "#e74c3c" if is_error else "#0078d4"
        btn_hover = "#c0392b" if is_error else "#005a9e"
        
        btn_ok = ctk.CTkButton(
            frame, 
            text="OK", 
            width=100, 
            height=28, 
            fg_color=btn_color, 
            hover_color=btn_hover, 
            corner_radius=8, 
            font=("Segoe UI", 11, "bold"),
            command=self.destroy
        )
        btn_ok.pack(pady=(5, 15))
        
        self.wait_window()

def show_fluent_info(parent, title, message):
    FluentDialog(parent, title, message, is_error=False)

def show_fluent_error(parent, title, message):
    FluentDialog(parent, title, message, is_error=True)


# --- CUSTOM SIDEBAR BUTTON ---
class SidebarButton(ctk.CTkFrame):
    def __init__(self, master, text, command, icon_text="", **kwargs):
        # Set height to 40 to override CustomTkinter's default 200px height
        super().__init__(master, fg_color="transparent", height=40, **kwargs)
        self.command = command
        self.pack_propagate(False)  # Lock the frame's dimensions
        
        # Accent vertical indicator bar on left side
        self.indicator = ctk.CTkFrame(self, width=3, corner_radius=2, fg_color="transparent")
        self.indicator.pack(side="left", fill="y", padx=(2, 6), pady=6)
        
        # Sidebar text button
        self.btn = ctk.CTkButton(
            self,
            text=f"{icon_text}  {text}" if icon_text else text,
            anchor="w",
            fg_color="transparent",
            text_color=("#4c4f69", "#cdd6f4"),
            hover_color=("#e6e9ef", "#2a2b3c"),
            font=("Segoe UI", 12),
            height=32,
            corner_radius=8,
            command=self.command
        )
        self.btn.pack(side="left", fill="both", expand=True, padx=(0, 6), pady=4)
        
    def set_active(self, active):
        if active:
            self.indicator.configure(fg_color="#0078d4")
            self.btn.configure(
                fg_color=("#e6e9ef", "#2a2b3c"),
                font=("Segoe UI", 12, "bold"),
                text_color=("#0078d4", "#89b4fa")
            )
        else:
            self.indicator.configure(fg_color="transparent")
            self.btn.configure(
                fg_color="transparent",
                font=("Segoe UI", 12),
                text_color=("#4c4f69", "#cdd6f4")
            )


# --- SYSTEM INTEGRATION HELPERS ---
def check_startup_status():
    """Checks if the ThermalWatch task exists in Windows Task Scheduler."""
    try:
        res = subprocess.run(
            ["schtasks", "/query", "/tn", "ThermalWatch"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
        )
        return res.returncode == 0
    except Exception:
        return False

def set_startup_status(enable):
    """Adds or deletes the ThermalWatch task in Windows Task Scheduler (with Administrator privileges)."""
    try:
        if enable:
            if getattr(sys, 'frozen', False):
                exe_path = sys.executable
            else:
                exe_path = os.path.abspath(sys.argv[0])
            
            # Launches with highest Admin privileges on Windows startup without showing a UAC prompt
            cmd = [
                "schtasks", "/create",
                "/tn", "ThermalWatch",
                "/tr", f'"{exe_path}"',
                "/sc", "onlogon",
                "/rl", "highest",
                "/f"
            ]
            res = subprocess.run(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
            )
            return res.returncode == 0
        else:
            cmd = ["schtasks", "/delete", "/tn", "ThermalWatch", "/f"]
            res = subprocess.run(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
            )
            return res.returncode == 0
    except Exception:
        return False


# --- REDESIGNED SETTINGS PANEL ---
def open_settings_window(diagnose_callback=None, get_stats_callback=None):
    """Opens the Windows 11 styled Settings window with a left sidebar."""
    settings = load_settings()
    t = TRANSLATIONS["English"]

    # Window Root setup
    root = ctk.CTk()
    root.title(t["title"])
    root.geometry("680x550")
    root.resizable(False, False)

    # Set Window and Taskbar Icon
    if getattr(sys, 'frozen', False):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.dirname(os.path.abspath(__file__))
    icon_path = os.path.join(base_path, "icon.ico")
    if os.path.exists(icon_path):
        try:
            root.iconbitmap(icon_path)
        except Exception:
            pass
    
    # Theme backgrounds
    root.configure(fg_color=("#f3f3f3", "#1c1c1c"))

    # --- LEFT SIDEBAR PANEL ---
    sidebar_frame = ctk.CTkFrame(root, width=180, corner_radius=0, fg_color=("#ebebeb", "#202020"), border_width=0)
    sidebar_frame.pack(side="left", fill="y")
    sidebar_frame.pack_propagate(False)

    # Logo/Header in sidebar
    logo_label = ctk.CTkLabel(sidebar_frame, text="ThermalWatch", font=("Segoe UI", 16, "bold"), text_color=("#0078d4", "#89b4fa"))
    logo_label.pack(pady=(20, 15), padx=15, anchor="w")

    # Divider line
    div = ctk.CTkFrame(sidebar_frame, height=1, fg_color=("#d0d0d0", "#2d2d2d"))
    div.pack(fill="x", padx=15, pady=(0, 15))

    # --- RIGHT CONTENT CONTAINER ---
    content_area = ctk.CTkFrame(root, fg_color="transparent")
    content_area.pack(side="right", fill="both", expand=True)

    # Content Footer (Save / Cancel Actions)
    action_bar = ctk.CTkFrame(content_area, fg_color="transparent")
    action_bar.pack(side="bottom", fill="x", padx=25, pady=15)

    # Pages Map
    pages = {}
    sidebar_buttons = {}

    def show_page(page_name):
        for name, page_frame in pages.items():
            page_frame.pack_forget()
        pages[page_name].pack(fill="both", expand=True, padx=25, pady=(20, 0))
        for name, btn in sidebar_buttons.items():
            btn.set_active(name == page_name)

    # Helper to construct Category frames
    def create_page_frame(name):
        frame = ctk.CTkFrame(content_area, fg_color="transparent")
        pages[name] = frame
        return frame

    # ==========================================
    # PAGE 1: LIMITS & WIDGET CONFIGURATION
    # ==========================================
    limits_page = create_page_frame("limits")
    
    # Title
    lbl_title_limits = ctk.CTkLabel(limits_page, text=t["tab_limits"], font=("Segoe UI", 16, "bold"), text_color=("#333333", "#ffffff"))
    lbl_title_limits.pack(anchor="w", pady=(0, 12))

    # Columns Container for side-by-side Threshold Cards
    cols_frame = ctk.CTkFrame(limits_page, fg_color="transparent")
    cols_frame.pack(fill="x", pady=(0, 10))

    # --- Left Card: CPU Settings ---
    cpu_card = ctk.CTkFrame(cols_frame, border_width=1, border_color=("#e5e5e5", "#2e2e2e"), fg_color=("#ffffff", "#242424"), corner_radius=10)
    cpu_card.pack(side="left", fill="both", expand=True, padx=(0, 5), pady=2)

    ctk.CTkLabel(cpu_card, text=t["cpu_settings"], font=("Segoe UI", 13, "bold"), text_color=("#0078d4", "#3498db")).pack(anchor="w", padx=15, pady=(10, 5))

    # CPU Temp Slider & Label
    cpu_temp_lbl = ctk.CTkLabel(cpu_card, text=f"{t['max_temp']}: {settings.get('cpu-max-temperature', 85)}°C", font=("Segoe UI", 11))
    cpu_temp_lbl.pack(anchor="w", padx=15, pady=(2, 0))
    
    def on_cpu_temp_slide(val):
        cpu_temp_lbl.configure(text=f"{t['max_temp']}: {int(val)}°C")
    
    cpu_temp_slider = ctk.CTkSlider(cpu_card, from_=40, to=110, number_of_steps=70, command=on_cpu_temp_slide, height=16)
    cpu_temp_slider.set(settings.get("cpu-max-temperature", 85))
    cpu_temp_slider.pack(fill="x", padx=15, pady=(2, 8))

    # CPU Usage Slider & Label
    cpu_usage_lbl = ctk.CTkLabel(cpu_card, text=f"{t['max_usage']}: {settings.get('cpu-max-usage', 95)}%", font=("Segoe UI", 11))
    cpu_usage_lbl.pack(anchor="w", padx=15, pady=(2, 0))
    
    def on_cpu_usage_slide(val):
        cpu_usage_lbl.configure(text=f"{t['max_usage']}: {int(val)}%")
        
    cpu_usage_slider = ctk.CTkSlider(cpu_card, from_=10, to=100, number_of_steps=90, command=on_cpu_usage_slide, height=16)
    cpu_usage_slider.set(settings.get("cpu-max-usage", 95))
    cpu_usage_slider.pack(fill="x", padx=15, pady=(2, 12))

    # --- Right Card: GPU Settings ---
    gpu_card = ctk.CTkFrame(cols_frame, border_width=1, border_color=("#e5e5e5", "#2e2e2e"), fg_color=("#ffffff", "#242424"), corner_radius=10)
    gpu_card.pack(side="right", fill="both", expand=True, padx=(5, 0), pady=2)

    ctk.CTkLabel(gpu_card, text=t["gpu_settings"], font=("Segoe UI", 13, "bold"), text_color=("#2ecc71", "#a6e3a1")).pack(anchor="w", padx=15, pady=(10, 5))

    # GPU Temp Slider & Label
    gpu_temp_lbl = ctk.CTkLabel(gpu_card, text=f"{t['max_temp']}: {settings.get('gpu-max-temperature', 80)}°C", font=("Segoe UI", 11))
    gpu_temp_lbl.pack(anchor="w", padx=15, pady=(2, 0))
    
    def on_gpu_temp_slide(val):
        gpu_temp_lbl.configure(text=f"{t['max_temp']}: {int(val)}°C")
        
    gpu_temp_slider = ctk.CTkSlider(gpu_card, from_=40, to=110, number_of_steps=70, command=on_gpu_temp_slide, height=16)
    gpu_temp_slider.set(settings.get("gpu-max-temperature", 80))
    gpu_temp_slider.pack(fill="x", padx=15, pady=(2, 8))

    # GPU Usage Slider & Label
    gpu_usage_lbl = ctk.CTkLabel(gpu_card, text=f"{t['max_usage']}: {settings.get('gpu-max-usage', 100)}%", font=("Segoe UI", 11))
    gpu_usage_lbl.pack(anchor="w", padx=15, pady=(2, 0))
    
    def on_gpu_usage_slide(val):
        gpu_usage_lbl.configure(text=f"{t['max_usage']}: {int(val)}%")
        
    gpu_usage_slider = ctk.CTkSlider(gpu_card, from_=10, to=100, number_of_steps=90, command=on_gpu_usage_slide, height=16)
    gpu_usage_slider.set(settings.get("gpu-max-usage", 100))
    gpu_usage_slider.pack(fill="x", padx=15, pady=(2, 12))

    # --- Bottom Card: Alerts & Widget Options ---
    options_card = ctk.CTkFrame(limits_page, border_width=1, border_color=("#e5e5e5", "#2e2e2e"), fg_color=("#ffffff", "#242424"), corner_radius=10)
    options_card.pack(fill="x", pady=5)

    ntfy_lbl = ctk.CTkLabel(options_card, text=t["ntfy_label"], font=("Segoe UI", 11, "bold"))
    ntfy_lbl.pack(anchor="w", padx=15, pady=(10, 2))
    ntfy_entry = ctk.CTkEntry(options_card, placeholder_text="e.g. my-thermalwatch-alerts", corner_radius=8, height=28)
    topic_val = settings.get("ntfy-topic", "")
    ntfy_entry.insert(0, "" if topic_val is None else str(topic_val))
    ntfy_entry.pack(fill="x", padx=15, pady=(0, 10))

    # Checkboxes row
    cb_frame = ctk.CTkFrame(options_card, fg_color="transparent")
    cb_frame.pack(fill="x", padx=15, pady=(0, 10))

    startup_var = ctk.StringVar(value="on" if check_startup_status() else "off")
    startup_sw = ctk.CTkSwitch(cb_frame, text=t["startup"], variable=startup_var, onvalue="on", offvalue="off", font=("Segoe UI", 11), corner_radius=6)
    startup_sw.pack(pady=3, anchor="w")

    show_usage_var = ctk.StringVar(value="on" if settings.get("widget-show-usage", True) else "off")
    show_usage_sw = ctk.CTkSwitch(cb_frame, text=t["show_usage"], variable=show_usage_var, onvalue="on", offvalue="off", font=("Segoe UI", 11), corner_radius=6)
    show_usage_sw.pack(pady=3, anchor="w")

    show_fans_var = ctk.StringVar(value="on" if settings.get("widget-show-fans", True) else "off")
    show_fans_sw = ctk.CTkSwitch(cb_frame, text=t["show_fans"], variable=show_fans_var, onvalue="on", offvalue="off", font=("Segoe UI", 11), corner_radius=6)
    show_fans_sw.pack(pady=3, anchor="w")

    # ==========================================
    # PAGE 2: TELEMETRY (LIVE DASHBOARD & FANS)
    # ==========================================
    telemetry_page = create_page_frame("telemetry")
    
    lbl_title_tel = ctk.CTkLabel(telemetry_page, text=t["tab_telemetry"], font=("Segoe UI", 16, "bold"), text_color=("#333333", "#ffffff"))
    lbl_title_tel.pack(anchor="w", pady=(0, 12))

    tel_row = ctk.CTkFrame(telemetry_page, fg_color="transparent")
    tel_row.pack(fill="both", expand=True)

    # 1. CPU Card
    cpu_tel_card = ctk.CTkFrame(tel_row, border_width=1, border_color=("#e5e5e5", "#2e2e2e"), fg_color=("#ffffff", "#242424"), corner_radius=10)
    cpu_tel_card.pack(side="left", fill="both", expand=True, padx=(0, 5), pady=2)

    ctk.CTkLabel(cpu_tel_card, text=t["cpu_status"], font=("Segoe UI", 13, "bold"), text_color=("#0078d4", "#3498db")).pack(pady=(10, 5))

    cpu_t_lbl = ctk.CTkLabel(cpu_tel_card, text=f"{t['temp']}: --°C", font=("Segoe UI", 11))
    cpu_t_lbl.pack(anchor="w", padx=20)
    cpu_t_bar = ctk.CTkProgressBar(cpu_tel_card, width=175, height=6)
    cpu_t_bar.set(0)
    cpu_t_bar.pack(padx=20, pady=(2, 10))

    cpu_u_lbl = ctk.CTkLabel(cpu_tel_card, text=f"{t['usage']}: --%", font=("Segoe UI", 11))
    cpu_u_lbl.pack(anchor="w", padx=20)
    cpu_u_bar = ctk.CTkProgressBar(cpu_tel_card, width=175, height=6)
    cpu_u_bar.set(0)
    cpu_u_bar.pack(padx=20, pady=(2, 10))

    cpu_fan_lbl = ctk.CTkLabel(cpu_tel_card, text=f"{t['fan']}: -- RPM", font=("Segoe UI", 11))
    cpu_fan_lbl.pack(anchor="w", padx=20)

    cpu_canvas_bg = cpu_tel_card._apply_appearance_mode(cpu_tel_card.cget("fg_color"))
    cpu_canvas = ctk.CTkCanvas(cpu_tel_card, width=64, height=64, bg=cpu_canvas_bg, highlightthickness=0)
    cpu_canvas.pack(pady=(8, 10))

    # 2. GPU Card
    gpu_tel_card = ctk.CTkFrame(tel_row, border_width=1, border_color=("#e5e5e5", "#2e2e2e"), fg_color=("#ffffff", "#242424"), corner_radius=10)
    gpu_tel_card.pack(side="right", fill="both", expand=True, padx=(5, 0), pady=2)

    ctk.CTkLabel(gpu_tel_card, text=t["gpu_status"], font=("Segoe UI", 13, "bold"), text_color=("#2ecc71", "#a6e3a1")).pack(pady=(10, 5))

    gpu_t_lbl = ctk.CTkLabel(gpu_tel_card, text=f"{t['temp']}: --°C", font=("Segoe UI", 11))
    gpu_t_lbl.pack(anchor="w", padx=20)
    gpu_t_bar = ctk.CTkProgressBar(gpu_tel_card, width=175, height=6)
    gpu_t_bar.set(0)
    gpu_t_bar.pack(padx=20, pady=(2, 10))

    gpu_u_lbl = ctk.CTkLabel(gpu_tel_card, text=f"{t['usage']}: --%", font=("Segoe UI", 11))
    gpu_u_lbl.pack(anchor="w", padx=20)
    gpu_u_bar = ctk.CTkProgressBar(gpu_tel_card, width=175, height=6)
    gpu_u_bar.set(0)
    gpu_u_bar.pack(padx=20, pady=(2, 10))

    gpu_fan_lbl = ctk.CTkLabel(gpu_tel_card, text=f"{t['fan']}: -- RPM", font=("Segoe UI", 11))
    gpu_fan_lbl.pack(anchor="w", padx=20)

    gpu_canvas_bg = gpu_tel_card._apply_appearance_mode(gpu_tel_card.cget("fg_color"))
    gpu_canvas = ctk.CTkCanvas(gpu_tel_card, width=64, height=64, bg=gpu_canvas_bg, highlightthickness=0)
    gpu_canvas.pack(pady=(8, 10))

    tel_stats = {
        "cpu_temp": 0.0, "gpu_temp": 0.0,
        "cpu_usage": 0.0, "gpu_usage": 0.0,
        "cpu_fan": None, "gpu_fan": None
    }

    # Vector Drawing Functions for Fan Canvas
    def init_fan_canvas(canvas, color):
        canvas.create_oval(5, 5, 59, 59, outline=color, width=2)
        canvas.create_oval(27, 27, 37, 37, fill=color, outline="")

    def draw_fan_blades(canvas, angle, color):
        canvas.delete("blade")
        import math
        cx, cy = 32, 32
        radius = 22
        num_blades = 9
        
        for i in range(num_blades):
            base_angle = angle + i * (360 / num_blades)
            theta0 = math.radians(base_angle)
            theta1 = math.radians(base_angle + 12)
            theta2 = math.radians(base_angle + 20)
            
            x0 = cx + 5 * math.cos(theta0)
            y0 = cy + 5 * math.sin(theta0)
            
            x1 = cx + (radius * 0.5) * math.cos(theta1)
            y1 = cy + (radius * 0.5) * math.sin(theta1)
            
            x2 = cx + radius * math.cos(theta2)
            y2 = cy + radius * math.sin(theta2)
            
            canvas.create_line(x0, y0, x1, y1, x2, y2, smooth=True, width=2.5, fill=color, tags="blade")

    # Set canvas visual theme colors
    is_dark = ctk.get_appearance_mode() == "Dark"
    cpu_fan_color = "#3498db" if is_dark else "#2980b9"
    gpu_fan_color = "#2ecc71" if is_dark else "#27ae60"
    tel_border_color = "#45475a" if is_dark else "#ccd0da"

    init_fan_canvas(cpu_canvas, tel_border_color)
    init_fan_canvas(gpu_canvas, tel_border_color)

    # 25 FPS (40ms) Animation Loop
    cpu_angle = 0
    gpu_angle = 0

    def animate_fans_loop():
        nonlocal cpu_angle, gpu_angle
        if not root.winfo_exists():
            return
        try:
            # CPU Fan
            c_rpm = tel_stats["cpu_fan"]
            if c_rpm and c_rpm > 0:
                cpu_step = min(20, max(2, c_rpm / 150))
                cpu_angle = (cpu_angle + cpu_step) % 360
                draw_fan_blades(cpu_canvas, cpu_angle, cpu_fan_color)
            else:
                draw_fan_blades(cpu_canvas, cpu_angle, cpu_fan_color)

            # GPU Fan
            g_rpm = tel_stats["gpu_fan"]
            if g_rpm and g_rpm > 0:
                gpu_step = min(20, max(2, g_rpm / 150))
                gpu_angle = (gpu_angle + gpu_step) % 360
                draw_fan_blades(gpu_canvas, gpu_angle, gpu_fan_color)
            else:
                draw_fan_blades(gpu_canvas, gpu_angle, gpu_fan_color)
        except Exception:
            pass

        root.after(40, animate_fans_loop)

    # 1000ms Sensor State Update Loop
    def update_telemetry_loop():
        if not root.winfo_exists():
            return
        try:
            if get_stats_callback is not None:
                cpu_temp, gpu_temp, cpu_usage, gpu_usage, cpu_fan, gpu_fan = get_stats_callback()

                tel_stats["cpu_temp"] = cpu_temp
                tel_stats["gpu_temp"] = gpu_temp
                tel_stats["cpu_usage"] = cpu_usage
                tel_stats["gpu_usage"] = gpu_usage
                tel_stats["cpu_fan"] = cpu_fan
                tel_stats["gpu_fan"] = gpu_fan

                c_temp = cpu_temp if cpu_temp else 0.0
                g_temp = gpu_temp if gpu_temp else 0.0
                c_usage = cpu_usage if cpu_usage else 0.0
                g_usage = gpu_usage if gpu_usage else 0.0

                # Update Text Labels
                cpu_t_lbl.configure(text=f"{t['temp']}: {c_temp:.1f}°C")
                cpu_u_lbl.configure(text=f"{t['usage']}: {c_usage:.0f}%")
                cpu_fan_lbl.configure(text=f"{t['fan']}: {f'{cpu_fan:.0f} RPM' if cpu_fan else 'N/A'}")

                gpu_t_lbl.configure(text=f"{t['temp']}: {g_temp:.1f}°C")
                gpu_u_lbl.configure(text=f"{t['usage']}: {g_usage:.0f}%")
                gpu_fan_lbl.configure(text=f"{t['fan']}: {f'{gpu_fan:.0f} RPM' if gpu_fan else 'N/A'}")

                # Update Progress Bars
                cpu_t_bar.set(min(1.0, max(0.0, c_temp / 100.0)))
                cpu_u_bar.set(min(1.0, max(0.0, c_usage / 100.0)))
                gpu_t_bar.set(min(1.0, max(0.0, g_temp / 100.0)))
                gpu_u_bar.set(min(1.0, max(0.0, g_usage / 100.0)))

                # Progress Bar color triggers based on sliders
                c_limit = cpu_temp_slider.get()
                g_limit = gpu_temp_slider.get()

                if c_temp >= c_limit:
                    cpu_t_bar.configure(progress_color="#f38ba8")
                elif c_temp >= (c_limit - 5):
                    cpu_t_bar.configure(progress_color="#f9e2af")
                else:
                    cpu_t_bar.configure(progress_color="#a6e3a1")

                if g_temp >= g_limit:
                    gpu_t_bar.configure(progress_color="#f38ba8")
                elif g_temp >= (g_limit - 5):
                    gpu_t_bar.configure(progress_color="#f9e2af")
                else:
                    gpu_t_bar.configure(progress_color="#a6e3a1")
        except Exception:
            pass

        root.after(1000, update_telemetry_loop)

    if get_stats_callback is not None:
        update_telemetry_loop()
        animate_fans_loop()

    # ==========================================
    # PAGE 3: AI ADVISOR (GEMINI & OLLAMA & IN-APP DIAG)
    # ==========================================
    ai_page = create_page_frame("ai")
    
    lbl_title_ai = ctk.CTkLabel(ai_page, text=t["tab_ai"], font=("Segoe UI", 16, "bold"), text_color=("#333333", "#ffffff"))
    lbl_title_ai.pack(anchor="w", pady=(0, 10))

    # Top Configuration Card
    ai_config_card = ctk.CTkFrame(ai_page, border_width=1, border_color=("#e5e5e5", "#2e2e2e"), fg_color=("#ffffff", "#242424"), corner_radius=10)
    ai_config_card.pack(fill="x", pady=(0, 10))

    ctk.CTkLabel(ai_config_card, text=t["ai_engine"], font=("Segoe UI", 12, "bold"), text_color=("#0078d4", "#3498db")).pack(anchor="w", padx=15, pady=(10, 4))

    engine_reverse_map = {
        "none": "None (Rule-based)",
        "gemini": "Google Gemini (Cloud - Free)",
        "ollama": "Local Ollama (Offline AI)"
    }
    initial_engine = engine_reverse_map.get(settings.get("ai-engine", "none"), "None (Rule-based)")
    ai_engine_var = ctk.StringVar(value=initial_engine)

    # Dynamic sub-frames
    gemini_frame = ctk.CTkFrame(ai_config_card, fg_color="transparent")
    ollama_frame = ctk.CTkFrame(ai_config_card, fg_color="transparent")
    none_frame = ctk.CTkFrame(ai_config_card, fg_color="transparent")

    def on_engine_change(choice):
        gemini_frame.pack_forget()
        ollama_frame.pack_forget()
        none_frame.pack_forget()
        if choice == "Google Gemini (Cloud - Free)":
            gemini_frame.pack(fill="x", padx=15, pady=(5, 12))
        elif choice == "Local Ollama (Offline AI)":
            ollama_frame.pack(fill="x", padx=15, pady=(5, 12))
        else:
            none_frame.pack(fill="x", padx=15, pady=(5, 12))

    ai_menu = ctk.CTkOptionMenu(
        ai_config_card, 
        values=["None (Rule-based)", "Google Gemini (Cloud - Free)", "Local Ollama (Offline AI)"],
        variable=ai_engine_var,
        command=on_engine_change,
        width=240,
        corner_radius=8
    )
    ai_menu.pack(anchor="w", padx=15, pady=(0, 5))

    # --- 1. NONE (Rule-based) subframe ---
    ctk.CTkLabel(none_frame, text=t["ai_none"], font=("Segoe UI", 12, "bold"), text_color="#3498db").pack(anchor="w")
    ctk.CTkLabel(none_frame, text=t["ai_none_desc"], font=("Segoe UI", 10.5), text_color="#bdc3c7", justify="left").pack(anchor="w", pady=4)

    # --- 2. GEMINI subframe ---
    ctk.CTkLabel(gemini_frame, text=t["gemini_key"], font=("Segoe UI", 11, "bold")).pack(anchor="w", pady=(0, 2))
    key_row = ctk.CTkFrame(gemini_frame, fg_color="transparent")
    key_row.pack(fill="x", pady=(0, 5))

    gemini_key_entry = ctk.CTkEntry(key_row, placeholder_text="Paste your API key here...", corner_radius=8, show="*")
    gemini_key_entry.insert(0, settings.get("gemini-api-key", ""))
    gemini_key_entry.pack(side="left", fill="x", expand=True)

    def toggle_key_mask():
        if gemini_key_entry.cget("show") == "*":
            gemini_key_entry.configure(show="")
            toggle_mask_btn.configure(text="👁️")
        else:
            gemini_key_entry.configure(show="*")
            toggle_mask_btn.configure(text="🔒")

    toggle_mask_btn = ctk.CTkButton(key_row, text="🔒", width=35, height=28, corner_radius=8, command=toggle_key_mask, fg_color=("#ccd0da", "#34495e"), text_color=("#2c3e50", "#ffffff"), hover_color=("#b2bec3", "#2c3e50"))
    toggle_mask_btn.pack(side="left", padx=(6, 0))

    def get_api_key_browser():
        import webbrowser
        webbrowser.open("https://aistudio.google.com/app/apikey")

    get_key_btn = ctk.CTkButton(gemini_frame, text=t["get_key"], command=get_api_key_browser, fg_color="#9b59b6", hover_color="#8e44ad", corner_radius=8, height=26, font=("Segoe UI", 11, "bold"))
    get_key_btn.pack(anchor="w", pady=(4, 6))
    ctk.CTkLabel(gemini_frame, text=t["gemini_desc"], font=("Segoe UI", 10), text_color="#bdc3c7", justify="left").pack(anchor="w")

    # --- 3. OLLAMA subframe ---
    ollama_status_lbl = ctk.CTkLabel(ollama_frame, text=t["status_ready"], font=("Segoe UI", 11, "italic"), text_color="#bdc3c7")

    def install_ollama_action():
        def run():
            try:
                install_btn.configure(state="disabled")
                local_appdata = os.environ.get("LOCALAPPDATA", "")
                ollama_bin = os.path.join(local_appdata, "Programs", "Ollama", "ollama.exe")
                
                import urllib.request
                import json
                import shutil
                import time
                
                # Check status
                is_running = False
                has_model = False
                try:
                    req = urllib.request.Request("http://localhost:11434/api/tags")
                    with urllib.request.urlopen(req, timeout=1.5) as r:
                        if r.status == 200:
                            is_running = True
                            data = json.loads(r.read().decode('utf-8'))
                            for m in data.get("models", []):
                                if "qwen2.5" in m.get("name", ""):
                                    has_model = True
                except Exception:
                    pass

                if is_running and has_model:
                    ollama_status_lbl.configure(text="✅ Ollama & Qwen model are active and ready!", text_color="#2ecc71")
                    return

                # Download installer if missing
                is_installed = os.path.exists(ollama_bin) or (shutil.which("ollama.exe") is not None)
                if not is_installed:
                    ollama_status_lbl.configure(text="📥 Downloading Ollama Installer (220MB)...", text_color="#e67e22")
                    installer_url = "https://ollama.com/download/OllamaSetup.exe"
                    import tempfile
                    temp_installer = os.path.join(tempfile.gettempdir(), "OllamaSetup.exe")
                    
                    req = urllib.request.Request(installer_url, headers={'User-Agent': 'Mozilla'})
                    with urllib.request.urlopen(req) as response, open(temp_installer, 'wb') as f:
                        total = int(response.info().get('Content-Length', 0))
                        dl = 0
                        while True:
                            chunk = response.read(65536)
                            if not chunk:
                                break
                            dl += len(chunk)
                            f.write(chunk)
                            pct = int(dl * 100 / total) if total else 0
                            ollama_status_lbl.configure(text=f"📥 Downloading: {pct}%")

                    ollama_status_lbl.configure(text="⚙️ Launching installer... Please complete setup.", text_color="#e67e22")
                    p = subprocess.Popen([temp_installer])
                    p.wait()
                    time.sleep(6)

                # Pull model
                ollama_status_lbl.configure(text="📥 Pulling Qwen2.5 model (900MB)...", text_color="#e67e22")
                bin_path = ollama_bin if os.path.exists(ollama_bin) else (shutil.which("ollama.exe") or "ollama")
                pull_proc = subprocess.Popen(
                    [bin_path, "pull", "qwen2.5:1.5b"],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    encoding="utf-8",
                    creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
                )
                while True:
                    line = pull_proc.stdout.readline()
                    if not line:
                        break
                    if "pulling" in line.lower() or "downloading" in line.lower():
                        clean_line = line.strip()
                        if len(clean_line) > 36:
                            clean_line = clean_line[:36] + "..."
                        ollama_status_lbl.configure(text=f"🤖 {clean_line}")
                pull_proc.wait()
                ollama_status_lbl.configure(text="✅ Ollama & Model ready!", text_color="#2ecc71")
            except Exception as e:
                ollama_status_lbl.configure(text=f"❌ Failed: {str(e)[:25]}", text_color="#e74c3c")
            finally:
                install_btn.configure(state="normal")
        threading.Thread(target=run, daemon=True).start()

    def check_ollama_onload():
        def check():
            try:
                import urllib.request
                import json
                req = urllib.request.Request("http://localhost:11434/api/tags")
                with urllib.request.urlopen(req, timeout=1.0) as r:
                    if r.status == 200:
                        data = json.loads(r.read().decode('utf-8'))
                        has_model = any("qwen2.5" in m.get("name", "") for m in data.get("models", []))
                        if has_model:
                            ollama_status_lbl.configure(text="Status: Ready (Installed & Running)", text_color="#2ecc71")
                        else:
                            ollama_status_lbl.configure(text="Status: Installed (Model Missing)", text_color="#e67e22")
            except Exception:
                ollama_status_lbl.configure(text="Status: Offline / Not Running", text_color="#e67e22")
        threading.Thread(target=check, daemon=True).start()

    install_btn = ctk.CTkButton(ollama_frame, text=t["install_ollama"], command=install_ollama_action, fg_color="#2ecc71", hover_color="#27ae60", corner_radius=8, height=26, font=("Segoe UI", 11, "bold"),width=250)
    install_btn.pack(anchor="w")
    ollama_status_lbl.pack(anchor="w", pady=4)
    check_ollama_onload()
    ctk.CTkLabel(ollama_frame, text=t["ollama_desc"], font=("Segoe UI", 10), text_color="#bdc3c7", justify="left").pack(anchor="w")

    # Initialize sub-frame state
    on_engine_change(initial_engine)

    # --- Integrated In-App Diagnostics Card ---
    diag_card = ctk.CTkFrame(ai_page, border_width=1, border_color=("#e5e5e5", "#2e2e2e"), fg_color=("#ffffff", "#242424"), corner_radius=10)
    diag_card.pack(fill="both", expand=True, pady=(0, 10))

    diag_text = ctk.CTkTextbox(diag_card, height=100, wrap="word", corner_radius=8, border_width=1, border_color=("#e0e0e0", "#444444"), fg_color=("#f9f9f9", "#1e1e1e"), font=("Segoe UI", 11))
    diag_text.pack(fill="both", expand=True, padx=15, pady=(10, 8))
    diag_text.insert("1.0", "Diagnostics report will appear here when generated. Run telemetry diagnosis to request advice from the active advisor.")
    diag_text.configure(state="disabled")

    def run_diagnose_async():
        diag_btn.configure(state="disabled", text="⚡ Analyzing...")
        diag_text.configure(state="normal")
        diag_text.delete("1.0", "end")
        diag_text.insert("1.0", "🤖 Gathering data and querying AI Advisor... Analyzing 10-minute rolling hardware load, fan speed, and temperature curves. Please wait.")
        diag_text.configure(state="disabled")

        def query_thread():
            try:
                if diagnose_callback is not None:
                    report = diagnose_callback()
                else:
                    # Mock telemetry diagnostics for standalone testing
                    import time
                    time.sleep(1.2)
                    report = "🤖 [Standalone Test Mode]\n\nVisual test successful! To view real-time diagnostics and recommendations based on your usage-temperature-fan curve, please launch ThermalWatch from the system tray menu."
                root.after(0, lambda: display_result(report))
            except Exception as e:
                root.after(0, lambda: display_result(f"❌ Diagnostics failed to run: {e}"))

        def display_result(text):
            diag_text.configure(state="normal")
            diag_text.delete("1.0", "end")
            diag_text.insert("1.0", text)
            diag_text.configure(state="disabled")
            diag_btn.configure(state="normal", text=t["diagnose"])

        threading.Thread(target=query_thread, daemon=True).start()

    diag_btn = ctk.CTkButton(
        diag_card, 
        text=t["diagnose"], 
        command=run_diagnose_async,
        fg_color="#0078d4", 
        hover_color="#005a9e", 
        corner_radius=8,
        height=32,
        font=("Segoe UI", 11, "bold")
    )
    diag_btn.pack(anchor="e", padx=15, pady=(0, 15))

    # ==========================================
    # PAGE 4: PAWNIO RYZEN FIX
    # ==========================================
    pawnio_page = create_page_frame("pawnio")
    
    lbl_title_pawn = ctk.CTkLabel(pawnio_page, text=t["tab_pawnio"], font=("Segoe UI", 16, "bold"), text_color=("#333333", "#ffffff"))
    lbl_title_pawn.pack(anchor="w", pady=(0, 12))

    pawn_card = ctk.CTkFrame(pawnio_page, border_width=1, border_color=("#e5e5e5", "#2e2e2e"), fg_color=("#ffffff", "#242424"), corner_radius=10)
    pawn_card.pack(fill="both", expand=True, pady=(0, 10))

    ctk.CTkLabel(pawn_card, text=t["pawn_title"], font=("Segoe UI", 13, "bold"), text_color=("#e67e22", "#f38ba8")).pack(anchor="w", padx=20, pady=(15, 5))
    ctk.CTkLabel(pawn_card, text=t["pawn_desc"], font=("Segoe UI", 11.5), text_color="#bdc3c7", justify="left").pack(anchor="w", padx=20, pady=5)

    def open_pawnio_site():
        import webbrowser
        webbrowser.open("https://pawnio.eu/")

    pawn_download_btn = ctk.CTkButton(pawn_card, text=t["pawn_btn"], command=open_pawnio_site, fg_color="#e67e22", hover_color="#d35400", corner_radius=8, height=32, font=("Segoe UI", 11, "bold"))
    pawn_download_btn.pack(anchor="w", padx=20, pady=15)

    # --- SIDEBAR BUTTONS GENERATION ---
    sidebar_buttons["limits"] = SidebarButton(sidebar_frame, text=t["tab_limits"], command=lambda: show_page("limits"), icon_text="⚙️")
    sidebar_buttons["limits"].pack(fill="x", padx=10, pady=2)

    sidebar_buttons["telemetry"] = SidebarButton(sidebar_frame, text=t["tab_telemetry"], command=lambda: show_page("telemetry"), icon_text="📊")
    sidebar_buttons["telemetry"].pack(fill="x", padx=10, pady=2)

    sidebar_buttons["ai"] = SidebarButton(sidebar_frame, text=t["tab_ai"], command=lambda: show_page("ai"), icon_text="🤖")
    sidebar_buttons["ai"].pack(fill="x", padx=10, pady=2)

    sidebar_buttons["pawnio"] = SidebarButton(sidebar_frame, text=t["tab_pawnio"], command=lambda: show_page("pawnio"), icon_text="🩹")
    sidebar_buttons["pawnio"].pack(fill="x", padx=10, pady=2)

    # Initialize at first page
    show_page("limits")

    # --- GLOBAL FOOTER ACTIONS (SAVE & CANCEL) ---
    def save_action():
        try:
            # Map choice to config representation
            engine_map = {
                "None (Rule-based)": "none",
                "Google Gemini (Cloud - Free)": "gemini",
                "Local Ollama (Offline AI)": "ollama"
            }
            selected_engine = engine_map.get(ai_engine_var.get(), "none")

            cpu_temp_val = int(cpu_temp_slider.get())
            gpu_temp_val = int(gpu_temp_slider.get())
            cpu_usage_val = int(cpu_usage_slider.get())
            gpu_usage_val = int(gpu_usage_slider.get())
            ntfy_topic_val = ntfy_entry.get().strip() or None
            show_usage_val = show_usage_var.get() == "on"
            show_fans_val = show_fans_var.get() == "on"
            gemini_key_val = gemini_key_entry.get().strip()

            # Safety validations
            if (
                not (0 <= cpu_temp_val <= 120)
                or not (0 <= gpu_temp_val <= 120)
                or not (0 <= cpu_usage_val <= 100)
                or not (0 <= gpu_usage_val <= 100)
            ):
                raise ValueError()

            # Load existing config to preserve other parameters (e.g. widget coordinates, theme, etc.)
            current_settings = load_settings()
            current_settings["cpu-max-temperature"] = cpu_temp_val
            current_settings["gpu-max-temperature"] = gpu_temp_val
            current_settings["cpu-max-usage"] = cpu_usage_val
            current_settings["gpu-max-usage"] = gpu_usage_val
            current_settings["ntfy-topic"] = ntfy_topic_val
            current_settings["widget-show-usage"] = show_usage_val
            current_settings["widget-show-fans"] = show_fans_val
            current_settings["ai-engine"] = selected_engine
            current_settings["gemini-api-key"] = gemini_key_val
            current_settings["language"] = "English"

            if save_settings(current_settings):
                set_startup_status(startup_var.get() == "on")
                show_fluent_info(root, t["success"], t["success_msg"])
                root.destroy()
                import gc; gc.collect()
            else:
                show_fluent_error(root, t["error"], t["error_msg"])
        except ValueError:
            show_fluent_error(root, t["invalid_input"], t["invalid_input_msg"])

    cancel_btn = ctk.CTkButton(action_bar, text=t["cancel"], fg_color=("#ccd0da", "#3a3a3a"), text_color=("#2c3e50", "#ffffff"), hover_color=("#b2bec3", "#2c3e50"), command=root.destroy, width=110, height=32, font=("Segoe UI", 11, "bold"), corner_radius=8)
    cancel_btn.pack(side="right", padx=(10, 0))

    save_btn = ctk.CTkButton(action_bar, text=t["save"], command=save_action, width=110, height=32, font=("Segoe UI", 11, "bold"), fg_color="#0078d4", hover_color="#005a9e", corner_radius=8)
    save_btn.pack(side="right")

    root.mainloop()


# --- REDESIGNED TEMPERATURE DESKTOP WIDGET ---
class TemperatureWidget:
    def __init__(self, get_stats_callback, on_close_callback=None):
        settings = load_settings()
        self.current_theme = settings.get("widget-theme", "dark")
        self.show_usage = settings.get("widget-show-usage", True)
        self.show_fans = settings.get("widget-show-fans", True)
        self.get_stats_callback = get_stats_callback
        self.on_close_callback = on_close_callback
        self.should_close = False
        
        self.root = ctk.CTk()
        self.root.title("ThermalWatch Widget")

        # Set Widget Window Icon
        if getattr(sys, 'frozen', False):
            base_path = sys._MEIPASS
        else:
            base_path = os.path.dirname(os.path.abspath(__file__))
        icon_path = os.path.join(base_path, "icon.ico")
        if os.path.exists(icon_path):
            try:
                self.root.iconbitmap(icon_path)
            except Exception:
                pass

        # Frameless, floating context overlays
        self.root.overrideredirect(True)
        self.root.attributes("-topmost", True)
        self.root.attributes("-alpha", 0.88)
        
        # Transparent border workaround via OS key chroma
        self.root.configure(fg_color="magenta")
        try:
            self.root.wm_attributes("-transparentcolor", "magenta")
        except Exception:
            pass
        
        x = settings.get("widget-x", 100)
        y = settings.get("widget-y", 100)
        height = 80 if self.show_fans else 55
        self.root.geometry(f"300x{height}+{x}+{y}")

        # Main rounded body
        self.frame = ctk.CTkFrame(
            self.root, 
            corner_radius=12, 
            fg_color="#181825", 
            border_width=1, 
            border_color="#313244"
        )
        self.frame.pack(fill="both", expand=True)

        def toggle_theme():
            self.current_theme = "light" if self.current_theme == "dark" else "dark"
            cfg = load_settings()
            cfg["widget-theme"] = self.current_theme
            save_settings(cfg)
            self.apply_theme()

        self.toggle_theme = toggle_theme

        # 1. CPU Info Column
        self.cpu_frame = ctk.CTkFrame(self.frame, fg_color="transparent")
        self.cpu_frame.pack(side="left", padx=(15, 0), fill="both", expand=True)
        
        self.cpu_temp_label = ctk.CTkLabel(
            self.cpu_frame,
            text="CPU: --°C (--%)" if self.show_usage else "CPU: --°C",
            font=("Segoe UI", 11, "bold"),
            text_color="#cdd6f4",
            anchor="w"
        )
        self.cpu_temp_label.pack(side="top", fill="x", pady=(15, 0) if self.show_fans else (12, 0))
        
        self.cpu_fan_label = ctk.CTkLabel(
            self.cpu_frame,
            text="Fan: -- RPM",
            font=("Segoe UI", 9),
            text_color="#a6adc8",
            anchor="w"
        )
        if self.show_fans:
            self.cpu_fan_label.pack(side="top", fill="x")

        # 2. Left Divider (Visual separation)
        self.div_left = ctk.CTkFrame(self.frame, width=1, fg_color="#313244")
        self.div_left.pack(side="left", padx=10, fill="y", pady=12)

        # 3. Theme Toggle Central Action Button
        self.theme_btn = ctk.CTkButton(
            self.frame,
            text="☀" if self.current_theme == "dark" else "🌙",
            width=26,
            height=26,
            corner_radius=8,
            fg_color="transparent",
            hover_color="#2a2b3c",
            text_color="#cdd6f4",
            command=self.toggle_theme,
            font=("Segoe UI", 12)
        )
        self.theme_btn.pack(side="left", expand=True, pady=12)

        # 4. Right Divider
        self.div_right = ctk.CTkFrame(self.frame, width=1, fg_color="#313244")
        self.div_right.pack(side="left", padx=10, fill="y", pady=12)

        # 5. GPU Info Column
        self.gpu_frame = ctk.CTkFrame(self.frame, fg_color="transparent")
        self.gpu_frame.pack(side="left", padx=(0, 15), fill="both", expand=True)
        
        self.gpu_temp_label = ctk.CTkLabel(
            self.gpu_frame,
            text="GPU: --°C (--%)" if self.show_usage else "GPU: --°C",
            font=("Segoe UI", 11, "bold"),
            text_color="#cdd6f4",
            anchor="e"
        )
        self.gpu_temp_label.pack(side="top", fill="x", pady=(15, 0) if self.show_fans else (12, 0))
        
        self.gpu_fan_label = ctk.CTkLabel(
            self.gpu_frame,
            text="Fan: -- RPM",
            font=("Segoe UI", 9),
            text_color="#a6adc8",
            anchor="e"
        )
        if self.show_fans:
            self.gpu_fan_label.pack(side="top", fill="x")
        
        # Binds dragging capabilities across the panel pieces
        for w in (self.frame, self.cpu_frame, self.cpu_temp_label, self.cpu_fan_label,
                  self.gpu_frame, self.gpu_temp_label, self.gpu_fan_label,
                  self.div_left, self.div_right):
            w.bind("<Button-1>", self.start_drag)
            w.bind("<B1-Motion>", self.do_drag)
            w.bind("<ButtonRelease-1>", self.stop_drag)
        
        self.drag_data = {"x": 0, "y": 0}
        self.apply_theme()
        self.update_loop()
        
    def apply_theme(self):
        if self.current_theme == "dark":
            frame_bg = "#1e1e1e"
            border_color = "#3a3a3a"
            btn_hover = "#2b2b2b"
            btn_text = "#cdd6f4"
            label_text = "#cdd6f4"
            sub_label_text = "#a6adc8"
            self.theme_btn.configure(text="☀", text_color=btn_text, hover_color=btn_hover)
        else:
            frame_bg = "#ffffff"
            border_color = "#ccd0da"
            btn_hover = "#f1f2f6"
            btn_text = "#4c4f69"
            label_text = "#4c4f69"
            sub_label_text = "#6c6f85"
            self.theme_btn.configure(text="🌙", text_color=btn_text, hover_color=btn_hover)
            
        self.frame.configure(fg_color=frame_bg, border_color=border_color)
        self.cpu_temp_label.configure(text_color=label_text)
        self.gpu_temp_label.configure(text_color=label_text)
        self.cpu_fan_label.configure(text_color=sub_label_text)
        self.gpu_fan_label.configure(text_color=sub_label_text)
        self.div_left.configure(fg_color=border_color)
        self.div_right.configure(fg_color=border_color)

    def start_drag(self, event):
        self.drag_data["x"] = event.x
        self.drag_data["y"] = event.y

    def do_drag(self, event):
        deltax = event.x - self.drag_data["x"]
        deltay = event.y - self.drag_data["y"]
        new_x = self.root.winfo_x() + deltax
        new_y = self.root.winfo_y() + deltay
        self.root.geometry(f"+{new_x}+{new_y}")

    def stop_drag(self, event):
        cfg = load_settings()
        cfg["widget-x"] = self.root.winfo_x()
        cfg["widget-y"] = self.root.winfo_y()
        save_settings(cfg)

    def close_widget(self, event=None):
        cfg = load_settings()
        cfg["widget-visible"] = False
        save_settings(cfg)
        if self.on_close_callback:
            self.on_close_callback()
        self.root.destroy()
        import gc; gc.collect()

    def update_loop(self):
        if self.should_close:
            self.close_widget()
            return
            
        try:
            cpu_temp, gpu_temp, cpu_usage, gpu_usage, cpu_fan, gpu_fan = self.get_stats_callback()
            
            cpu_temp_text = f"{cpu_temp:.1f}°C" if cpu_temp > 0.0 else "N/A"
            gpu_temp_text = f"{gpu_temp:.1f}°C" if gpu_temp > 0.0 else "N/A"
            
            cpu_fan_text = f"{cpu_fan:.0f} RPM" if cpu_fan is not None else "N/A"
            gpu_fan_text = f"{gpu_fan:.0f} RPM" if gpu_fan is not None else "N/A"
            
            cfg = load_settings()
            cpu_limit = cfg.get("cpu-max-temperature", 85)
            gpu_limit = cfg.get("gpu-max-temperature", 80)
            
            if self.current_theme == "dark":
                color_green = "#a6e3a1"
                color_yellow = "#f9e2af"
                color_red = "#f38ba8"
            else:
                color_green = "#40a02b"
                color_yellow = "#df8e1d"
                color_red = "#d20f39"

            # --- INDIVIDUAL TEMPERATURE COLOR COMPUTATION ---
            cpu_color = color_green
            if cpu_temp >= (cpu_limit - 5):
                cpu_color = color_yellow
            if cpu_temp >= cpu_limit:
                cpu_color = color_red

            gpu_color = color_green
            if gpu_temp >= (gpu_limit - 5):
                gpu_color = color_yellow
            if gpu_temp >= gpu_limit:
                gpu_color = color_red
                
            if self.show_usage:
                cpu_text = f"{cpu_temp_text} ({cpu_usage:.0f}%)"
                gpu_text = f"{gpu_temp_text} ({gpu_usage:.0f}%)"
            else:
                cpu_text = cpu_temp_text
                gpu_text = gpu_temp_text
                
            self.cpu_temp_label.configure(text=f"CPU: {cpu_text}", text_color=cpu_color)
            self.gpu_temp_label.configure(text=f"GPU: {gpu_text}", text_color=gpu_color)
            
            default_border_color = "#3a3a3a" if self.current_theme == "dark" else "#ccd0da"

            #RED ALARM STATUS
            if cpu_color == color_red or gpu_color == color_red:
                final_border= color_red

            #YELLOW WARNING STATUS
            elif cpu_color==color_yellow or gpu_color == color_yellow:
                final_border= color_yellow

            else:
                final_border= default_border_color
            self.frame.configure(border_color=final_border)

            
            if self.show_fans:
                self.cpu_fan_label.configure(text=f"Fan: {cpu_fan_text}")
                self.gpu_fan_label.configure(text=f"Fan: {gpu_fan_text}")
        except Exception:
            pass
            
        self.root.after(1000, self.update_loop)

    def start(self):
        self.root.mainloop()

if __name__ == "__main__":
    open_settings_window()
