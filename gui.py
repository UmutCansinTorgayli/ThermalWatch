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
    root.geometry("340x640")
    root.resizable(False, False)

    # Header
    title_label = ctk.CTkLabel(root, text="ThermalWatch Configuration", font=("Helvetica", 16, "bold"), text_color="#3498db")
    title_label.pack(pady=(15, 10))

    # 1. CPU Max Temp
    cpu_temp_label = ctk.CTkLabel(root, text="CPU Max Temperature (°C):", anchor="w")
    cpu_temp_label.pack(fill="x", padx=30, pady=(5, 2))
    cpu_temp_entry = ctk.CTkEntry(root, placeholder_text="e.g. 85", corner_radius=10)
    cpu_temp_entry.insert(0, str(settings.get("cpu-max-temperature", 85)))
    cpu_temp_entry.pack(fill="x", padx=30)

    # 2. GPU Max Temp
    gpu_temp_label = ctk.CTkLabel(root, text="GPU Max Temperature (°C):", anchor="w")
    gpu_temp_label.pack(fill="x", padx=30, pady=(8, 2))
    gpu_temp_entry = ctk.CTkEntry(root, placeholder_text="e.g. 80", corner_radius=10)
    gpu_temp_entry.insert(0, str(settings.get("gpu-max-temperature", 80)))
    gpu_temp_entry.pack(fill="x", padx=30)

    # 3. CPU Max Usage
    cpu_usage_label = ctk.CTkLabel(root, text="CPU Max Usage (%):", anchor="w")
    cpu_usage_label.pack(fill="x", padx=30, pady=(8, 2))
    cpu_usage_entry = ctk.CTkEntry(root, placeholder_text="e.g. 95", corner_radius=10)
    cpu_usage_entry.insert(0, str(settings.get("cpu-max-usage", 95)))
    cpu_usage_entry.pack(fill="x", padx=30)

    # 4. GPU Max Usage
    gpu_usage_label = ctk.CTkLabel(root, text="GPU Max Usage (%):", anchor="w")
    gpu_usage_label.pack(fill="x", padx=30, pady=(8, 2))
    gpu_usage_entry = ctk.CTkEntry(root, placeholder_text="e.g. 100", corner_radius=10)
    gpu_usage_entry.insert(0, str(settings.get("gpu-max-usage", 100)))
    gpu_usage_entry.pack(fill="x", padx=30)

    # 5. ntfy Topic
    ntfy_label = ctk.CTkLabel(root, text="ntfy.sh Topic Name (Mobile Alerts):", anchor="w")
    ntfy_label.pack(fill="x", padx=30, pady=(8, 2))
    ntfy_entry = ctk.CTkEntry(root, placeholder_text="optional-topic-name", corner_radius=10)
    topic_val = settings.get("ntfy-topic", "")
    ntfy_entry.insert(0, "" if topic_val is None else str(topic_val))
    ntfy_entry.pack(fill="x", padx=30)

    # 6. Startup Configuration
    startup_var = ctk.StringVar(value="on" if check_startup_status() else "off")
    startup_checkbox = ctk.CTkCheckBox(root, text="Start with Windows (Administrator)", variable=startup_var, onvalue="on", offvalue="off", font=("Helvetica", 11), corner_radius=6)
    startup_checkbox.pack(fill="x", padx=30, pady=(15, 0))

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

    button_frame = ctk.CTkFrame(root, fg_color="transparent")
    button_frame.pack(fill="x", padx=30, pady=(15, 10))

    save_btn = ctk.CTkButton(button_frame, text="Save", command=save_action, width=130, corner_radius=10)
    save_btn.pack(side="left", padx=(0, 10))

    cancel_btn = ctk.CTkButton(button_frame, text="Cancel", fg_color="#34495e", hover_color="#2c3e50", command=root.destroy, width=130, corner_radius=10)
    cancel_btn.pack(side="right")
    if diagnose_callback is not None:
        def run_diagnose():
            report = diagnose_callback()
            messagebox.showinfo("Thermal Health Report", report)
            
        diagnose_btn = ctk.CTkButton(
            root, 
            text="🔍 Check Thermal Health", 
            command=run_diagnose, 
            fg_color="#2ecc71", 
            hover_color="#27ae60", 
            corner_radius=10
        )
        diagnose_btn.pack(pady=(5, 10))

    # 💡 CPU N/A Troubleshooting Info
    info_text = (
        "💡 CPU N/A Troubleshooting:\n"
        "1. Always run the program 'As Administrator'.\n"
        "2. If CPU temperature is still not showing on AMD Ryzen,\n"
        "   click the button below to install the PawnIO driver."
    )
    info_label = ctk.CTkLabel(root, text=info_text, font=("Helvetica", 10), text_color="#bdc3c7", justify="left")
    info_label.pack(pady=(10, 10))

    import webbrowser
    def open_pawnio():
        webbrowser.open("https://pawnio.eu/")

    pawnio_btn = ctk.CTkButton(root, text="Download PawnIO Driver", command=open_pawnio, fg_color="#e67e22", hover_color="#d35400", corner_radius=10)
    pawnio_btn.pack(pady=(0, 15))

    root.mainloop()

class TemperatureWidget:
    def __init__(self, get_temp_callback, on_close_callback=None):
        settings = load_settings()
        self.current_theme = settings.get("widget-theme", "dark")
        self.get_temp_callback = get_temp_callback
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
        self.root.geometry(f"240x60+{x}+{y}")
        
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
            #change the theme
            self.current_theme = "light" if self.current_theme== "dark" else "dark"

            #save the config file
            settings= load_settings()
            settings["widget-theme"]=self.current_theme
            save_settings(settings)
            
            #update the widget theme
            self.apply_theme()

        self.toggle_theme = toggle_theme

        
        
        # CPU Label
        self.cpu_title_label = ctk.CTkLabel(
            self.frame,
            text="CPU: --°C",
            font=("Helvetica", 12, "bold"),
            text_color="#cdd6f4"
        )
        self.cpu_title_label.pack(side="left", padx=(15, 0))
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
        self.theme_btn.pack(side="left", expand=True)
        self.gpu_title_label = ctk.CTkLabel(
            self.frame,
            text="GPU: --°C",
            font=("Helvetica", 12, "bold"),
            text_color="#cdd6f4"
        )
        self.gpu_title_label.pack(side="right", padx=(0, 15))
        
        # Listeners
        self.frame.bind("<Button-1>", self.start_drag)
        self.frame.bind("<B1-Motion>", self.do_drag)
        self.frame.bind("<ButtonRelease-1>", self.stop_drag)
        
        self.cpu_title_label.bind("<Button-1>", self.start_drag)
        self.cpu_title_label.bind("<B1-Motion>", self.do_drag)
        self.cpu_title_label.bind("<ButtonRelease-1>", self.stop_drag)
        
        self.gpu_title_label.bind("<Button-1>", self.start_drag)
        self.gpu_title_label.bind("<B1-Motion>", self.do_drag)
        self.gpu_title_label.bind("<ButtonRelease-1>", self.stop_drag)
        
        # Double Click Close Listener
        self.frame.bind("<Double-Button-1>", self.close_widget)
        self.cpu_title_label.bind("<Double-Button-1>", self.close_widget)
        self.gpu_title_label.bind("<Double-Button-1>", self.close_widget)

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
            self.theme_btn.configure(text="☀", text_color=btn_text, hover_color=btn_hover)
        else:
            frame_bg = "#eff1f5"
            border_color = "#ccd0da"
            btn_hover = "#e6e9ef"
            btn_text = "#4c4f69"
            label_text = "#4c4f69"
            self.theme_btn.configure(text="🌙", text_color=btn_text, hover_color=btn_hover)
            
        self.frame.configure(fg_color=frame_bg, border_color=border_color)
        self.cpu_title_label.configure(text_color=label_text)
        self.gpu_title_label.configure(text_color=label_text)

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
            cpu, gpu = self.get_temp_callback()
            
            cpu_text = f"{cpu:.1f}°C" if cpu > 0.0 else "N/A"
            gpu_text = f"{gpu:.1f}°C" if gpu > 0.0 else "N/A"
            
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
            if cpu >= (cpu_limit - 5) or gpu >= (gpu_limit - 5):
                color = color_yellow
            if cpu >= cpu_limit or gpu >= gpu_limit:
                color = color_red
                
            self.cpu_title_label.configure(text=f"CPU: {cpu_text}", text_color=color)
            self.gpu_title_label.configure(text=f"GPU: {gpu_text}", text_color=color)
        except Exception as e:
            print(f"Widget update error: {e}")
            
        self.root.after(1000, self.update_loop)

    def start(self):
        self.root.mainloop()

if __name__ == "__main__":
    open_settings_window()
