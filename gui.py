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

def open_settings_window(diagnose_callback=None):
    """Opens the modern CustomTkinter settings window."""
    settings = load_settings()

    root = ctk.CTk()
    root.title("ThermalWatch - Settings")
    root.geometry("460x420")
    root.resizable(False, False)

    # Header
    title_label = ctk.CTkLabel(root, text="ThermalWatch Configuration", font=("Helvetica", 16, "bold"), text_color="#3498db")
    title_label.pack(pady=(15, 10))

    # Two-column frame for limits (CPU / GPU Side-by-Side)
    columns_frame = ctk.CTkFrame(root, fg_color="transparent")
    columns_frame.pack(fill="x", padx=20, pady=5)

    # Left Column: CPU Settings
    cpu_frame = ctk.CTkFrame(columns_frame)
    cpu_frame.pack(side="left", fill="both", expand=True, padx=(0, 10), pady=5)

    cpu_header = ctk.CTkLabel(cpu_frame, text="CPU Settings", font=("Helvetica", 13, "bold"), text_color="#3498db")
    cpu_header.pack(pady=(10, 5))

    cpu_temp_label = ctk.CTkLabel(cpu_frame, text="Max Temp Limit (°C):")
    cpu_temp_label.pack(pady=(5, 2))
    cpu_temp_entry = ctk.CTkEntry(cpu_frame, placeholder_text="e.g. 85", corner_radius=10, width=120)
    cpu_temp_entry.insert(0, str(settings.get("cpu-max-temperature", 85)))
    cpu_temp_entry.pack(pady=(0, 10))

    cpu_usage_label = ctk.CTkLabel(cpu_frame, text="Max Usage Limit (%):")
    cpu_usage_label.pack(pady=(5, 2))
    cpu_usage_entry = ctk.CTkEntry(cpu_frame, placeholder_text="e.g. 95", corner_radius=10, width=120)
    cpu_usage_entry.insert(0, str(settings.get("cpu-max-usage", 95)))
    cpu_usage_entry.pack(pady=(0, 15))

    # Right Column: GPU Settings
    gpu_frame = ctk.CTkFrame(columns_frame)
    gpu_frame.pack(side="right", fill="both", expand=True, padx=(10, 0), pady=5)

    gpu_header = ctk.CTkLabel(gpu_frame, text="GPU Settings", font=("Helvetica", 13, "bold"), text_color="#2ecc71")
    gpu_header.pack(pady=(10, 5))

    gpu_temp_label = ctk.CTkLabel(gpu_frame, text="Max Temp Limit (°C):")
    gpu_temp_label.pack(pady=(5, 2))
    gpu_temp_entry = ctk.CTkEntry(gpu_frame, placeholder_text="e.g. 80", corner_radius=10, width=120)
    gpu_temp_entry.insert(0, str(settings.get("gpu-max-temperature", 80)))
    gpu_temp_entry.pack(pady=(0, 10))

    gpu_usage_label = ctk.CTkLabel(gpu_frame, text="Max Usage Limit (%):")
    gpu_usage_label.pack(pady=(5, 2))
    gpu_usage_entry = ctk.CTkEntry(gpu_frame, placeholder_text="e.g. 100", corner_radius=10, width=120)
    gpu_usage_entry.insert(0, str(settings.get("gpu-max-usage", 100)))
    gpu_usage_entry.pack(pady=(0, 15))

    # 5. ntfy Topic
    ntfy_label = ctk.CTkLabel(root, text="ntfy.sh Topic Name (Mobile Alerts):", anchor="w")
    ntfy_label.pack(fill="x", padx=30, pady=(5, 2))
    ntfy_entry = ctk.CTkEntry(root, placeholder_text="optional-topic-name", corner_radius=10)
    topic_val = settings.get("ntfy-topic", "")
    ntfy_entry.insert(0, "" if topic_val is None else str(topic_val))
    ntfy_entry.pack(fill="x", padx=30)

    # 6. Startup Configuration
    startup_var = ctk.StringVar(value="on" if check_startup_status() else "off")
    startup_checkbox = ctk.CTkCheckBox(root, text="Start with Windows (Administrator)", variable=startup_var, onvalue="on", offvalue="off", font=("Helvetica", 11), corner_radius=6)
    startup_checkbox.pack(padx=30, pady=(10, 0), anchor="w")

    def save_action():
        try:
            new_settings = {
                "cpu-max-temperature": int(cpu_temp_entry.get()),
                "gpu-max-temperature": int(gpu_temp_entry.get()),
                "cpu-max-usage": int(cpu_usage_entry.get()),
                "gpu-max-usage": int(gpu_usage_entry.get()),
                "ntfy-topic": ntfy_entry.get().strip() or None
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

    # Action Buttons Row
    button_frame = ctk.CTkFrame(root, fg_color="transparent")
    button_frame.pack(fill="x", padx=30, pady=(15, 10))

    save_btn = ctk.CTkButton(button_frame, text="Save Settings", command=save_action, width=125, corner_radius=10)
    save_btn.pack(side="left", padx=(0, 10))

    cancel_btn = ctk.CTkButton(button_frame, text="Cancel", fg_color="#34495e", hover_color="#2c3e50", command=root.destroy, width=125, corner_radius=10)
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
            width=125
        )
        diagnose_btn.pack(side="left")

    # Bottom frame for troubleshooting info
    trouble_frame = ctk.CTkFrame(root)
    trouble_frame.pack(fill="x", padx=20, pady=(10, 15))

    info_label = ctk.CTkLabel(trouble_frame, text="💡 CPU N/A on AMD Ryzen? Run as Admin and install PawnIO driver.", font=("Helvetica", 9), text_color="#bdc3c7")
    info_label.pack(side="left", padx=10, pady=8)

    import webbrowser
    def open_pawnio():
        webbrowser.open("https://pawnio.eu/")

    pawnio_btn = ctk.CTkButton(trouble_frame, text="Get PawnIO", command=open_pawnio, fg_color="#e67e22", hover_color="#d35400", corner_radius=8, width=95)
    pawnio_btn.pack(side="right", padx=10, pady=8)

    root.mainloop()

class TemperatureWidget:
    def __init__(self, get_stats_callback, on_close_callback=None):
        settings = load_settings()
        self.current_theme = settings.get("widget-theme", "dark")
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
        settings = load_settings()
        x = settings.get("widget-x", 100)
        y = settings.get("widget-y", 100)
        self.root.geometry(f"270x80+{x}+{y}")
        
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
            text="CPU: --°C (--%)",
            font=("Helvetica", 11, "bold"),
            text_color="#cdd6f4",
            anchor="w"
        )
        self.cpu_temp_label.pack(side="top", fill="x", pady=(15, 0))
        
        self.cpu_fan_label = ctk.CTkLabel(
            self.cpu_frame,
            text="Fan: -- RPM",
            font=("Helvetica", 9),
            text_color="#a6adc8",
            anchor="w"
        )
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
        self.theme_btn.pack(side="left", expand=True, pady=15)

        # GPU Info Container
        self.gpu_frame = ctk.CTkFrame(self.frame, fg_color="transparent")
        self.gpu_frame.pack(side="right", padx=(0, 15), fill="both", expand=True)
        
        self.gpu_temp_label = ctk.CTkLabel(
            self.gpu_frame,
            text="GPU: --°C (--%)",
            font=("Helvetica", 11, "bold"),
            text_color="#cdd6f4",
            anchor="e"
        )
        self.gpu_temp_label.pack(side="top", fill="x", pady=(15, 0))
        
        self.gpu_fan_label = ctk.CTkLabel(
            self.gpu_frame,
            text="Fan: -- RPM",
            font=("Helvetica", 9),
            text_color="#a6adc8",
            anchor="e"
        )
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
                
            self.cpu_temp_label.configure(text=f"CPU: {cpu_temp_text} ({cpu_usage:.0f}%)", text_color=color)
            self.gpu_temp_label.configure(text=f"GPU: {gpu_temp_text} ({gpu_usage:.0f}%)", text_color=color)
            self.cpu_fan_label.configure(text=f"Fan: {cpu_fan_text}")
            self.gpu_fan_label.configure(text=f"Fan: {gpu_fan_text}")
        except Exception as e:
            print(f"Widget update error: {e}")
            
        self.root.after(1000, self.update_loop)

    def start(self):
        self.root.mainloop()

if __name__ == "__main__":
    open_settings_window()
