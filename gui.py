# pyrefly: ignore [missing-import]
import customtkinter as ctk
from tkinter import messagebox
import subprocess
import sys
import os
from config import load_settings, save_settings

ctk.set_appearance_mode("dark")      
ctk.set_default_color_theme("blue")   

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

def open_settings_window(diagnose_callback=None, get_stats_callback=None):
    """Opens the modern CustomTkinter settings window with tabs."""
    settings = load_settings()

    root = ctk.CTk()
    root.title("ThermalWatch - Settings Dashboard")
    root.geometry("460x540")
    root.resizable(False, False)

    # Header
    title_label = ctk.CTkLabel(root, text="ThermalWatch Configuration", font=("Helvetica", 16, "bold"), text_color="#3498db")
    title_label.pack(pady=(12, 5))

    # 🗂️ CTkTabview Setup
    tabview = ctk.CTkTabview(root, width=420, height=350, corner_radius=12)
    tabview.pack(padx=20, pady=(0, 10), fill="both", expand=True)

    tabview.add("Limits & Widget")
    tabview.add("Telemetry")
    tabview.add("AI Advisor")
    tabview.add("PawnIO Help")

    # ==========================================
    # TAB 1: LIMITS & WIDGET CONFIGURATION
    # ==========================================
    limits_tab = tabview.tab("Limits & Widget")
    
    # Two-column frame for limits (CPU / GPU Side-by-Side)
    columns_frame = ctk.CTkFrame(limits_tab, fg_color="transparent")
    columns_frame.pack(fill="x", padx=10, pady=5)

    # Left Column: CPU Settings
    cpu_frame = ctk.CTkFrame(columns_frame)
    cpu_frame.pack(side="left", fill="both", expand=True, padx=(0, 5), pady=5)

    cpu_header = ctk.CTkLabel(cpu_frame, text="CPU Settings", font=("Helvetica", 13, "bold"), text_color="#3498db")
    cpu_header.pack(pady=(8, 3))

    cpu_temp_label = ctk.CTkLabel(cpu_frame, text="Max Temp Limit (°C):")
    cpu_temp_label.pack(pady=(2, 2))
    cpu_temp_entry = ctk.CTkEntry(cpu_frame, placeholder_text="e.g. 85", corner_radius=10, width=120)
    cpu_temp_entry.insert(0, str(settings.get("cpu-max-temperature", 85)))
    cpu_temp_entry.pack(pady=(0, 8))

    cpu_usage_label = ctk.CTkLabel(cpu_frame, text="Max Usage Limit (%):")
    cpu_usage_label.pack(pady=(2, 2))
    cpu_usage_entry = ctk.CTkEntry(cpu_frame, placeholder_text="e.g. 95", corner_radius=10, width=120)
    cpu_usage_entry.insert(0, str(settings.get("cpu-max-usage", 95)))
    cpu_usage_entry.pack(pady=(0, 10))

    # Right Column: GPU Settings
    gpu_frame = ctk.CTkFrame(columns_frame)
    gpu_frame.pack(side="right", fill="both", expand=True, padx=(5, 0), pady=5)

    gpu_header = ctk.CTkLabel(gpu_frame, text="GPU Settings", font=("Helvetica", 13, "bold"), text_color="#2ecc71")
    gpu_header.pack(pady=(8, 3))

    gpu_temp_label = ctk.CTkLabel(gpu_frame, text="Max Temp Limit (°C):")
    gpu_temp_label.pack(pady=(2, 2))
    gpu_temp_entry = ctk.CTkEntry(gpu_frame, placeholder_text="e.g. 80", corner_radius=10, width=120)
    gpu_temp_entry.insert(0, str(settings.get("gpu-max-temperature", 80)))
    gpu_temp_entry.pack(pady=(0, 8))

    gpu_usage_label = ctk.CTkLabel(gpu_frame, text="Max Usage Limit (%):")
    gpu_usage_label.pack(pady=(2, 2))
    gpu_usage_entry = ctk.CTkEntry(gpu_frame, placeholder_text="e.g. 100", corner_radius=10, width=120)
    gpu_usage_entry.insert(0, str(settings.get("gpu-max-usage", 100)))
    gpu_usage_entry.pack(pady=(0, 10))

    # ntfy Topic Settings
    ntfy_label = ctk.CTkLabel(limits_tab, text="ntfy.sh Topic Name (Mobile Alerts):", anchor="w")
    ntfy_label.pack(fill="x", padx=15, pady=(5, 2))
    ntfy_entry = ctk.CTkEntry(limits_tab, placeholder_text="optional-topic-name", corner_radius=10)
    topic_val = settings.get("ntfy-topic", "")
    ntfy_entry.insert(0, "" if topic_val is None else str(topic_val))
    ntfy_entry.pack(fill="x", padx=15)

    # Language Selection Row
    lang_frame = ctk.CTkFrame(limits_tab, fg_color="transparent")
    lang_frame.pack(fill="x", padx=15, pady=(8, 0))

    lang_label = ctk.CTkLabel(lang_frame, text="App & AI Language:", font=("Helvetica", 11, "bold"))
    lang_label.pack(side="left", padx=(0, 10))

    lang_var = ctk.StringVar(value=settings.get("language", "English"))
    lang_menu = ctk.CTkOptionMenu(lang_frame, values=["English", "Turkish"], variable=lang_var, width=120, height=26, corner_radius=6)
    lang_menu.pack(side="left")

    # Startup & Widget Options Checkboxes
    options_frame = ctk.CTkFrame(limits_tab, fg_color="transparent")
    options_frame.pack(fill="x", padx=15, pady=(15, 0))

    startup_var = ctk.StringVar(value="on" if check_startup_status() else "off")
    startup_checkbox = ctk.CTkCheckBox(options_frame, text="Start with Windows (Administrator)", variable=startup_var, onvalue="on", offvalue="off", font=("Helvetica", 11), corner_radius=6)
    startup_checkbox.pack(pady=4, anchor="w")

    show_usage_var = ctk.StringVar(value="on" if settings.get("widget-show-usage", True) else "off")
    show_usage_checkbox = ctk.CTkCheckBox(options_frame, text="Show Usage (%) on Desktop Widget", variable=show_usage_var, onvalue="on", offvalue="off", font=("Helvetica", 11), corner_radius=6)
    show_usage_checkbox.pack(pady=4, anchor="w")

    show_fans_var = ctk.StringVar(value="on" if settings.get("widget-show-fans", True) else "off")
    show_fans_checkbox = ctk.CTkCheckBox(options_frame, text="Show Fan Speeds (RPM) on Desktop Widget", variable=show_fans_var, onvalue="on", offvalue="off", font=("Helvetica", 11), corner_radius=6)
    show_fans_checkbox.pack(pady=4, anchor="w")

    # ==========================================
    # TAB 2: TELEMETRY (LIVE DASHBOARD & FANS)
    # ==========================================
    telemetry_tab = tabview.tab("Telemetry")
    tel_frame = ctk.CTkFrame(telemetry_tab, fg_color="transparent")
    tel_frame.pack(fill="both", expand=True, padx=10, pady=5)

    # 1. CPU Telemetry Frame (Left Side)
    cpu_tel = ctk.CTkFrame(tel_frame)
    cpu_tel.pack(side="left", fill="both", expand=True, padx=(0, 5), pady=5)

    cpu_tel_title = ctk.CTkLabel(cpu_tel, text="CPU Status", font=("Helvetica", 13, "bold"), text_color="#3498db")
    cpu_tel_title.pack(pady=(8, 5))

    cpu_t_lbl = ctk.CTkLabel(cpu_tel, text="Temp: --°C", font=("Helvetica", 11))
    cpu_t_lbl.pack(anchor="w", padx=15)
    cpu_t_bar = ctk.CTkProgressBar(cpu_tel, width=155)
    cpu_t_bar.set(0)
    cpu_t_bar.pack(padx=15, pady=(0, 8))

    cpu_u_lbl = ctk.CTkLabel(cpu_tel, text="Usage: --%", font=("Helvetica", 11))
    cpu_u_lbl.pack(anchor="w", padx=15)
    cpu_u_bar = ctk.CTkProgressBar(cpu_tel, width=155)
    cpu_u_bar.set(0)
    cpu_u_bar.pack(padx=15, pady=(0, 8))

    cpu_fan_lbl = ctk.CTkLabel(cpu_tel, text="Fan: -- RPM", font=("Helvetica", 11))
    cpu_fan_lbl.pack(anchor="w", padx=15)

    cpu_canvas_bg = cpu_tel._apply_appearance_mode(cpu_tel.cget("fg_color"))
    cpu_canvas = ctk.CTkCanvas(cpu_tel, width=60, height=60, bg=cpu_canvas_bg, highlightthickness=0)
    cpu_canvas.pack(pady=(5, 5))

    # 2. GPU Telemetry Frame (Right Side)
    gpu_tel = ctk.CTkFrame(tel_frame)
    gpu_tel.pack(side="right", fill="both", expand=True, padx=(5, 0), pady=5)

    gpu_tel_title = ctk.CTkLabel(gpu_tel, text="GPU Status", font=("Helvetica", 13, "bold"), text_color="#2ecc71")
    gpu_tel_title.pack(pady=(8, 5))

    gpu_t_lbl = ctk.CTkLabel(gpu_tel, text="Temp: --°C", font=("Helvetica", 11))
    gpu_t_lbl.pack(anchor="w", padx=15)
    gpu_t_bar = ctk.CTkProgressBar(gpu_tel, width=155)
    gpu_t_bar.set(0)
    gpu_t_bar.pack(padx=15, pady=(0, 8))

    gpu_u_lbl = ctk.CTkLabel(gpu_tel, text="Usage: --%", font=("Helvetica", 11))
    gpu_u_lbl.pack(anchor="w", padx=15)
    gpu_u_bar = ctk.CTkProgressBar(gpu_tel, width=155)
    gpu_u_bar.set(0)
    gpu_u_bar.pack(padx=15, pady=(0, 8))

    gpu_fan_lbl = ctk.CTkLabel(gpu_tel, text="Fan: -- RPM", font=("Helvetica", 11))
    gpu_fan_lbl.pack(anchor="w", padx=15)

    gpu_canvas_bg = gpu_tel._apply_appearance_mode(gpu_tel.cget("fg_color"))
    gpu_canvas = ctk.CTkCanvas(gpu_tel, width=60, height=60, bg=gpu_canvas_bg, highlightthickness=0)
    gpu_canvas.pack(pady=(5, 5))

    # Shared telemetry values cache for animation
    tel_stats = {
        "cpu_temp": 0.0, "gpu_temp": 0.0,
        "cpu_usage": 0.0, "gpu_usage": 0.0,
        "cpu_fan": None, "gpu_fan": None
    }

    # Vector Drawing Functions for Fan Canvas
    def init_fan_canvas(canvas, color):
        # Outer casing ring
        canvas.create_oval(5, 5, 55, 55, outline=color, width=2)
        # Center core hub
        canvas.create_oval(25, 25, 35, 35, fill=color, outline="")

    def draw_fan_blades(canvas, angle, color):
        canvas.delete("blade")
        import math
        cx, cy = 30, 30
        radius = 20
        num_blades = 9
        
        for i in range(num_blades):
            # Base angle for this blade
            base_angle = angle + i * (360 / num_blades)
            
            # Three angular offset points to draw aerodynamic curved blades
            theta0 = math.radians(base_angle)
            theta1 = math.radians(base_angle + 12)
            theta2 = math.radians(base_angle + 20)
            
            # Start at edge of center hub
            x0 = cx + 5 * math.cos(theta0)
            y0 = cy + 5 * math.sin(theta0)
            
            # Mid curve point
            x1 = cx + (radius * 0.5) * math.cos(theta1)
            y1 = cy + (radius * 0.5) * math.sin(theta1)
            
            # Blade outer tip
            x2 = cx + radius * math.cos(theta2)
            y2 = cy + radius * math.sin(theta2)
            
            # Draw curved lines smoothly
            canvas.create_line(x0, y0, x1, y1, x2, y2, smooth=True, width=2.5, fill=color, tags="blade")

    # Set canvas visual theme colors
    is_dark = ctk.get_appearance_mode() == "Dark"
    cpu_fan_color = "#3498db" if is_dark else "#2980b9"
    gpu_fan_color = "#2ecc71" if is_dark else "#27ae60"
    tel_border_color = "#45475a" if is_dark else "#ccd0da"

    init_fan_canvas(cpu_canvas, tel_border_color)
    init_fan_canvas(gpu_canvas, tel_border_color)

    # 25 FPS (40ms) Animation Loop (No Hardware Queries)
    cpu_angle = 0
    gpu_angle = 0

    def animate_fans_loop():
        nonlocal cpu_angle, gpu_angle
        if not root.winfo_exists():
            return

        try:
            # CPU Fan Animation
            c_rpm = tel_stats["cpu_fan"]
            if c_rpm and c_rpm > 0:
                # Rotation speed is proportional to RPM (bounded between 2 and 20 deg per frame)
                cpu_step = min(20, max(2, c_rpm / 150))
                cpu_angle = (cpu_angle + cpu_step) % 360
                draw_fan_blades(cpu_canvas, cpu_angle, cpu_fan_color)
            else:
                # Keep still if 0 RPM
                draw_fan_blades(cpu_canvas, cpu_angle, cpu_fan_color)

            # GPU Fan Animation
            g_rpm = tel_stats["gpu_fan"]
            if g_rpm and g_rpm > 0:
                gpu_step = min(20, max(2, g_rpm / 150))
                gpu_angle = (gpu_angle + gpu_step) % 360
                draw_fan_blades(gpu_canvas, gpu_angle, gpu_fan_color)
            else:
                draw_fan_blades(gpu_canvas, gpu_angle, gpu_fan_color)
        except Exception as e:
            print(f"Fan animation loop error: {e}")

        root.after(40, animate_fans_loop)

    # 1000ms Sensor State Update Loop (Queries hardware stats)
    def update_telemetry_loop():
        if not root.winfo_exists():
            return

        try:
            if get_stats_callback is not None:
                cpu_temp, gpu_temp, cpu_usage, gpu_usage, cpu_fan, gpu_fan = get_stats_callback()

                # Save stats to cache for the fast animator loop
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

                # 1. Update Labels text
                cpu_t_lbl.configure(text=f"Temp: {c_temp:.1f}°C")
                cpu_u_lbl.configure(text=f"Usage: {c_usage:.0f}%")
                cpu_fan_lbl.configure(text=f"Fan: {f'{cpu_fan:.0f} RPM' if cpu_fan else 'N/A'}")

                gpu_t_lbl.configure(text=f"Temp: {g_temp:.1f}°C")
                gpu_u_lbl.configure(text=f"Usage: {g_usage:.0f}%")
                gpu_fan_lbl.configure(text=f"Fan: {f'{gpu_fan:.0f} RPM' if gpu_fan else 'N/A'}")

                # 2. Update Progress Bars (Values normalized to 0.0 - 1.0)
                cpu_t_bar.set(min(1.0, max(0.0, c_temp / 100.0)))
                cpu_u_bar.set(min(1.0, max(0.0, c_usage / 100.0)))
                
                gpu_t_bar.set(min(1.0, max(0.0, g_temp / 100.0)))
                gpu_u_bar.set(min(1.0, max(0.0, g_usage / 100.0)))

                # 3. Dynamic Progress Bar Colors based on warning levels
                c_limit = settings.get("cpu-max-temperature", 85)
                g_limit = settings.get("gpu-max-temperature", 80)

                if c_temp >= c_limit:
                    cpu_t_bar.configure(progress_color="#f38ba8")  # Red
                elif c_temp >= (c_limit - 5):
                    cpu_t_bar.configure(progress_color="#f9e2af")  # Yellow
                else:
                    cpu_t_bar.configure(progress_color="#a6e3a1")  # Green

                if g_temp >= g_limit:
                    gpu_t_bar.configure(progress_color="#f38ba8")
                elif g_temp >= (g_limit - 5):
                    gpu_t_bar.configure(progress_color="#f9e2af")
                else:
                    gpu_t_bar.configure(progress_color="#a6e3a1")

        except Exception as e:
            print(f"Telemetry update loop error: {e}")

        root.after(1000, update_telemetry_loop)

    # Start loops only if get_stats_callback is present
    if get_stats_callback is not None:
        update_telemetry_loop()
        animate_fans_loop()

    # ==========================================
    # TAB 3: AI ADVISOR (OLLAMA & GEMINI CONFIG)
    # ==========================================
    ai_tab = tabview.tab("AI Advisor")
    ai_frame = ctk.CTkFrame(ai_tab, fg_color="transparent")
    ai_frame.pack(fill="both", expand=True, padx=15, pady=10)

    ai_header = ctk.CTkLabel(ai_frame, text="Select AI Diagnostics Engine:", font=("Helvetica", 13, "bold"), text_color="#9b59b6")
    ai_header.pack(pady=(0, 5), anchor="w")

    # Load initial engine setting
    engine_reverse_map = {
        "none": "None (Rule-based)",
        "gemini": "Google Gemini (Cloud - Free)",
        "ollama": "Local Ollama (Offline AI)"
    }
    initial_engine = engine_reverse_map.get(settings.get("ai-engine", "none"), "None (Rule-based)")
    
    ai_engine_var = ctk.StringVar(value=initial_engine)

    # Engine Frames for Dynamic Switching
    gemini_frame = ctk.CTkFrame(ai_frame, fg_color="transparent")
    ollama_frame = ctk.CTkFrame(ai_frame, fg_color="transparent")
    none_frame = ctk.CTkFrame(ai_frame, fg_color="transparent")

    def on_engine_change(choice):
        gemini_frame.pack_forget()
        ollama_frame.pack_forget()
        none_frame.pack_forget()

        if choice == "Google Gemini (Cloud - Free)":
            gemini_frame.pack(fill="both", expand=True, pady=5)
        elif choice == "Local Ollama (Offline AI)":
            ollama_frame.pack(fill="both", expand=True, pady=5)
        else:
            none_frame.pack(fill="both", expand=True, pady=5)

    ai_engine_menu = ctk.CTkOptionMenu(
        ai_frame, 
        values=["None (Rule-based)", "Google Gemini (Cloud - Free)", "Local Ollama (Offline AI)"],
        variable=ai_engine_var,
        command=on_engine_change,
        width=250,
        corner_radius=8
    )
    ai_engine_menu.pack(anchor="w", pady=(0, 10))

    # --- 1. NONE FRAME ---
    ctk.CTkLabel(none_frame, text="✅ Classic Rule-based Advisor Active", font=("Helvetica", 12, "bold"), text_color="#3498db").pack(anchor="w", pady=(5, 2))
    desc_none = (
        "💡 Built-in Advisor features:\n"
        "- Instantaneous response.\n"
        "- Zero resource usage (0% CPU, 0 MB memory overhead).\n"
        "- No Internet connection or external software required."
    )
    ctk.CTkLabel(none_frame, text=desc_none, font=("Helvetica", 11), text_color="#bdc3c7", justify="left", anchor="w").pack(anchor="w", pady=5)

    # --- 2. GEMINI FRAME ---
    ctk.CTkLabel(gemini_frame, text="Gemini API Key:", font=("Helvetica", 11, "bold")).pack(anchor="w", pady=(2, 2))
    gemini_key_entry = ctk.CTkEntry(gemini_frame, placeholder_text="Paste your API key here...", width=350, corner_radius=8)
    gemini_key_entry.insert(0, settings.get("gemini-api-key", ""))
    gemini_key_entry.pack(anchor="w", pady=(0, 5))

    def open_ai_studio():
        import webbrowser
        webbrowser.open("https://aistudio.google.com/app/apikey")

    get_key_btn = ctk.CTkButton(gemini_frame, text="🔑 Get Free API Key (Google AI Studio)", command=open_ai_studio, fg_color="#9b59b6", hover_color="#8e44ad", corner_radius=10, width=240, height=28, font=("Helvetica", 11, "bold"))
    get_key_btn.pack(anchor="w", pady=(0, 8))

    desc_gemini = (
        "💡 Cloud AI features:\n"
        "- 100% Free: Google's developer tier has no costs.\n"
        "- High Speed: Diagnostics are analyzed in under 1 second.\n"
        "- Zero Installation: Nothing to download or run on your PC."
    )
    ctk.CTkLabel(gemini_frame, text=desc_gemini, font=("Helvetica", 11), text_color="#bdc3c7", justify="left", anchor="w").pack(anchor="w", pady=2)

    # --- 3. OLLAMA FRAME ---
    status_label = ctk.CTkLabel(ollama_frame, text="Status: Ready", font=("Helvetica", 11, "italic"), text_color="#bdc3c7")

    def install_ollama_background(lbl, btn):
        import threading
        import urllib.request
        import os
        import subprocess
        import tempfile
        import shutil
        import time

        def run():
            try:
                btn.configure(state="disabled")
                lbl.configure(text="📥 Downloading Ollama Installer (220MB)...", text_color="#e67e22")
                
                # 1. Download Setup Executable
                installer_url = "https://ollama.com/download/OllamaSetup.exe"
                temp_dir = tempfile.gettempdir()
                installer_path = os.path.join(temp_dir, "OllamaSetup.exe")
                
                req = urllib.request.Request(installer_url, headers={'User-Agent': 'Mozilla/5.0'})
                with urllib.request.urlopen(req) as response, open(installer_path, 'wb') as out_file:
                    total_size = int(response.info().get('Content-Length', 0))
                    downloaded = 0
                    block_size = 1024 * 64
                    while True:
                        buffer = response.read(block_size)
                        if not buffer:
                            break
                        downloaded += len(buffer)
                        out_file.write(buffer)
                        percent = int(downloaded * 100 / total_size) if total_size else 0
                        lbl.configure(text=f"📥 Downloading: {percent}%")
                        
                lbl.configure(text="⚙️ Launching installer... Please click Install.", text_color="#e67e22")
                
                # 2. Run the installer (wait for user)
                proc = subprocess.Popen([installer_path])
                proc.wait()
                
                # 3. Wait for Service & Pull Model
                lbl.configure(text="🔄 Starting Ollama service...", text_color="#e67e22")
                time.sleep(6)
                
                local_appdata = os.environ.get("LOCALAPPDATA", "")
                ollama_bin = os.path.join(local_appdata, "Programs", "Ollama", "ollama.exe")
                
                if not os.path.exists(ollama_bin):
                    ollama_bin = shutil.which("ollama.exe") or "ollama"
                    
                lbl.configure(text="📥 Pulling Qwen2.5:1.5b model (approx. 900MB)...", text_color="#e67e22")
                
                pull_proc = subprocess.Popen(
                    [ollama_bin, "pull", "qwen2.5:1.5b"],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
                )
                
                while True:
                    line = pull_proc.stdout.readline()
                    if not line:
                        break
                    if "pulling" in line.lower() or "downloading" in line.lower():
                        clean_line = line.strip().replace("\r", "").replace("\n", "")
                        if len(clean_line) > 40:
                            clean_line = clean_line[:40] + "..."
                        lbl.configure(text=f"🤖 {clean_line}")
                
                pull_proc.wait()
                lbl.configure(text="✅ Ollama & Model installed successfully!", text_color="#2ecc71")
            except Exception as e:
                lbl.configure(text=f"❌ Installation failed: {str(e)[:30]}", text_color="#e74c3c")
            finally:
                btn.configure(state="normal")

        threading.Thread(target=run, daemon=True).start()

    def on_install_click():
        install_ollama_background(status_label, install_btn)

    install_btn = ctk.CTkButton(ollama_frame, text="📥 Auto-Install Ollama & Model", command=on_install_click, fg_color="#2ecc71", hover_color="#27ae60", corner_radius=10, width=240, height=28, font=("Helvetica", 11, "bold"))
    install_btn.pack(anchor="w", pady=(2, 2))
    status_label.pack(anchor="w", pady=2)

    desc_ollama = (
        "💡 Local AI features:\n"
        "- 100% Offline: Data never leaves your PC.\n"
        "- Requirements: Download approx. 200MB installer + 900MB Qwen model.\n"
        "- Click Auto-Install to automate this process in the background."
    )
    ctk.CTkLabel(ollama_frame, text=desc_ollama, font=("Helvetica", 11), text_color="#bdc3c7", justify="left", anchor="w").pack(anchor="w", pady=2)

    # Initialize correct Switch Frame
    on_engine_change(initial_engine)

    # ==========================================
    # TAB 4: PAWNIO HELP (RYZEN TROUBLESHOOTING)
    # ==========================================
    pawn_tab = tabview.tab("PawnIO Help")
    pawn_frame = ctk.CTkFrame(pawn_tab, fg_color="transparent")
    pawn_frame.pack(fill="both", expand=True, padx=15, pady=10)

    pawn_header = ctk.CTkLabel(pawn_frame, text="AMD Ryzen Temperature Fix", font=("Helvetica", 14, "bold"), text_color="#e67e22")
    pawn_header.pack(pady=(0, 8), anchor="w")

    pawn_text = (
        "💡 CPU N/A Troubleshooting:\n\n"
        "1. Always run ThermalWatch 'As Administrator'.\n"
        "2. If CPU temperature is still not showing on AMD Ryzen,\n"
        "   you must install the PawnIO driver.\n"
        "3. PawnIO is a secure driver compatible with Core Isolation."
    )
    pawn_desc = ctk.CTkLabel(pawn_frame, text=pawn_text, font=("Helvetica", 11), text_color="#bdc3c7", justify="left")
    pawn_desc.pack(pady=5, anchor="w")

    import webbrowser
    def open_pawnio():
        webbrowser.open("https://pawnio.eu/")

    pawnio_btn = ctk.CTkButton(pawn_frame, text="Download PawnIO Driver", command=open_pawnio, fg_color="#e67e22", hover_color="#d35400", corner_radius=10, width=150)
    pawnio_btn.pack(pady=12, anchor="w")

    # ==========================================
    # SAVE & CANCEL & DIAGNOSTIC ACTIONS ROW
    # ==========================================
    def save_action():
        try:
            engine_map = {
                "None (Rule-based)": "none",
                "Google Gemini (Cloud - Free)": "gemini",
                "Local Ollama (Offline AI)": "ollama"
            }
            selected_engine = engine_map.get(ai_engine_var.get(), "none")

            new_settings = {
                "cpu-max-temperature": int(cpu_temp_entry.get()),
                "gpu-max-temperature": int(gpu_temp_entry.get()),
                "cpu-max-usage": int(cpu_usage_entry.get()),
                "gpu-max-usage": int(gpu_usage_entry.get()),
                "ntfy-topic": ntfy_entry.get().strip() or None,
                "widget-show-usage": show_usage_var.get() == "on",
                "widget-show-fans": show_fans_var.get() == "on",
                "ai-engine": selected_engine,
                "gemini-api-key": gemini_key_entry.get().strip(),
                "language": lang_var.get()
            }

            if (
                not (0 <= new_settings["cpu-max-temperature"] <= 120)
                or not (0 <= new_settings["gpu-max-temperature"] <= 120)
                or not (0 <= new_settings["cpu-max-usage"] <= 100)
                or not (0 <= new_settings["gpu-max-usage"] <= 100)
            ):
                raise ValueError("Values are out of logical range.")

            if save_settings(new_settings):
                # Startup State
                set_startup_status(startup_var.get() == "on")
                messagebox.showinfo("Success", "Settings have been saved successfully!")
                root.destroy()
                import gc; gc.collect()
            else:
                messagebox.showerror("Error", "Could not save settings.")
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter valid numeric values for limits.")

    # Action Buttons Row (At the bottom of the window, outside the tabview)
    button_frame = ctk.CTkFrame(root, fg_color="transparent")
    button_frame.pack(fill="x", padx=30, pady=(5, 15))

    save_btn = ctk.CTkButton(button_frame, text="Save Settings", command=save_action, width=125, height=35, font=("Helvetica", 11, "bold"), corner_radius=10)
    save_btn.pack(side="left", padx=(0, 10))

    cancel_btn = ctk.CTkButton(button_frame, text="Cancel", fg_color="#34495e", hover_color="#2c3e50", command=root.destroy, width=125, height=35, font=("Helvetica", 11, "bold"), corner_radius=10)
    cancel_btn.pack(side="left", padx=(0, 10))

    if diagnose_callback is not None:
        def run_diagnose():
            report = diagnose_callback()
            messagebox.showinfo("Thermal Health Report", report)
            
        diagnose_btn = ctk.CTkButton(
            button_frame, 
            text="🔍 Diagnostics", 
            command=run_diagnose, 
            fg_color="#2ecc71", 
            hover_color="#27ae60", 
            corner_radius=10,
            width=125,
            height=35,
            font=("Helvetica", 11, "bold")
        )
        diagnose_btn.pack(side="left")

    root.mainloop()

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

        # Frameless and always on top
        self.root.overrideredirect(True)
        self.root.attributes("-topmost", True)
        self.root.attributes("-alpha", 0.85)
        
        # Transparent background for rounded corners on Windows
        self.root.configure(fg_color="magenta")
        try:
            self.root.wm_attributes("-transparentcolor", "magenta")
        except Exception:
            pass
        
        x = settings.get("widget-x", 100)
        y = settings.get("widget-y", 100)
        height = 80 if self.show_fans else 55
        self.root.geometry(f"270x{height}+{x}+{y}")
        
        # Styled container frame
        self.frame = ctk.CTkFrame(
            self.root, 
            corner_radius=12, 
            fg_color="#181825", 
            border_width=1, 
            border_color="#313244"
        )
        self.frame.pack(fill="both", expand=True)

        def toggle_theme():
            # change the theme
            self.current_theme = "light" if self.current_theme == "dark" else "dark"

            # save the config file
            settings = load_settings()
            settings["widget-theme"] = self.current_theme
            save_settings(settings)
            
            # update the widget theme
            self.apply_theme()

        self.toggle_theme = toggle_theme

        # CPU Info Container
        self.cpu_frame = ctk.CTkFrame(self.frame, fg_color="transparent")
        self.cpu_frame.pack(side="left", padx=(15, 0), fill="both", expand=True)
        
        self.cpu_temp_label = ctk.CTkLabel(
            self.cpu_frame,
            text="CPU: --°C (--%)" if self.show_usage else "CPU: --°C",
            font=("Helvetica", 11, "bold"),
            text_color="#cdd6f4",
            anchor="w"
        )
        self.cpu_temp_label.pack(side="top", fill="x", pady=(15, 0) if self.show_fans else (12, 0))
        
        self.cpu_fan_label = ctk.CTkLabel(
            self.cpu_frame,
            text="Fan: -- RPM",
            font=("Helvetica", 9),
            text_color="#a6adc8",
            anchor="w"
        )
        if self.show_fans:
            self.cpu_fan_label.pack(side="top", fill="x")

        # Theme Toggle in the middle
        self.theme_btn = ctk.CTkButton(
            self.frame,
            text="☀" if self.current_theme == "dark" else "🌙",
            width=30,
            height=30,
            corner_radius=8,
            fg_color="transparent",
            hover_color="#2a2b3c",
            text_color="#cdd6f4",
            command=self.toggle_theme
        )
        self.theme_btn.pack(side="left", expand=True, pady=15 if self.show_fans else 10)

        # GPU Info Container
        self.gpu_frame = ctk.CTkFrame(self.frame, fg_color="transparent")
        self.gpu_frame.pack(side="right", padx=(0, 15), fill="both", expand=True)
        
        self.gpu_temp_label = ctk.CTkLabel(
            self.gpu_frame,
            text="GPU: --°C (--%)" if self.show_usage else "GPU: --°C",
            font=("Helvetica", 11, "bold"),
            text_color="#cdd6f4",
            anchor="e"
        )
        self.gpu_temp_label.pack(side="top", fill="x", pady=(15, 0) if self.show_fans else (12, 0))
        
        self.gpu_fan_label = ctk.CTkLabel(
            self.gpu_frame,
            text="Fan: -- RPM",
            font=("Helvetica", 9),
            text_color="#a6adc8",
            anchor="e"
        )
        if self.show_fans:
            self.gpu_fan_label.pack(side="top", fill="x")
        
        # Bind dragging & closing events to all widget parts
        for widget in (self.frame, self.cpu_frame, self.cpu_temp_label, self.cpu_fan_label,
                       self.gpu_frame, self.gpu_temp_label, self.gpu_fan_label):
            widget.bind("<Button-1>", self.start_drag)
            widget.bind("<B1-Motion>", self.do_drag)
            widget.bind("<ButtonRelease-1>", self.stop_drag)
            widget.bind("<Double-Button-1>", self.close_widget)
        
        self.drag_data = {"x": 0, "y": 0}
        self.apply_theme()
        self.update_loop()
        
    def apply_theme(self):
        if self.current_theme == "dark":
            frame_bg = "#181825"
            border_color = "#313244"
            btn_hover = "#2a2b3c"
            btn_text = "#cdd6f4"
            label_text = "#cdd6f4"
            sub_label_text = "#a6adc8"
            self.theme_btn.configure(text="☀", text_color=btn_text, hover_color=btn_hover)
        else:
            frame_bg = "#eff1f5"
            border_color = "#ccd0da"
            btn_hover = "#e6e9ef"
            btn_text = "#4c4f69"
            label_text = "#4c4f69"
            sub_label_text = "#6c6f85"
            self.theme_btn.configure(text="🌙", text_color=btn_text, hover_color=btn_hover)
            
        self.frame.configure(fg_color=frame_bg, border_color=border_color)
        self.cpu_temp_label.configure(text_color=label_text)
        self.gpu_temp_label.configure(text_color=label_text)
        self.cpu_fan_label.configure(text_color=sub_label_text)
        self.gpu_fan_label.configure(text_color=sub_label_text)

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
        settings = load_settings()
        settings["widget-x"] = self.root.winfo_x()
        settings["widget-y"] = self.root.winfo_y()
        save_settings(settings)

    def close_widget(self, event=None):
        settings = load_settings()
        settings["widget-visible"] = False
        save_settings(settings)
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
            
            settings = load_settings()
            cpu_limit = settings.get("cpu-max-temperature", 85)
            gpu_limit = settings.get("gpu-max-temperature", 80)
            
            if self.current_theme == "dark":
                color_green = "#a6e3a1"
                color_yellow = "#f9e2af"
                color_red = "#f38ba8"
            else:
                color_green = "#40a02b"
                color_yellow = "#df8e1d"
                color_red = "#d20f39"

            color = color_green
            if cpu_temp >= (cpu_limit - 5) or gpu_temp >= (gpu_limit - 5):
                color = color_yellow
            if cpu_temp >= cpu_limit or gpu_temp >= gpu_limit:
                color = color_red
                
            if self.show_usage:
                cpu_text = f"{cpu_temp_text} ({cpu_usage:.0f}%)"
                gpu_text = f"{gpu_temp_text} ({gpu_usage:.0f}%)"
            else:
                cpu_text = cpu_temp_text
                gpu_text = gpu_temp_text
                
            self.cpu_temp_label.configure(text=f"CPU: {cpu_text}", text_color=color)
            self.gpu_temp_label.configure(text=f"GPU: {gpu_text}", text_color=color)
            
            if self.show_fans:
                self.cpu_fan_label.configure(text=f"Fan: {cpu_fan_text}")
                self.gpu_fan_label.configure(text=f"Fan: {gpu_fan_text}")
        except Exception as e:
            print(f"Widget update error: {e}")
            
        self.root.after(1000, self.update_loop)

    def start(self):
        self.root.mainloop()

if __name__ == "__main__":
    open_settings_window()
