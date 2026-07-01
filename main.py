import os
import sys
import threading
import time
from PIL import Image, ImageDraw
import pystray

from config import load_settings, save_settings
from gui import open_settings_window, TemperatureWidget
from monitor import get_temperatures
from notifier import send_mobile_notification, send_windows_notification
current_cpu_temp = 0.0
current_gpu_temp = 0.0
last_cpu_alert_time = 0.0
last_gpu_alert_time = 0.0
ALERT_COOLDOWN = 300

global_icon = None
widget_instance = None


def run_widget_thread():
    global widget_instance
    
    def on_close():
        global widget_instance
        widget_instance = None
        if global_icon:
            update_menu(global_icon)
            
    widget_instance = TemperatureWidget(
        get_temp_callback=lambda: (current_cpu_temp, current_gpu_temp),
        on_close_callback=on_close
    )
    widget_instance.start()


def toggle_widget(icon, item):
    global widget_instance
    settings = load_settings()
    
    if widget_instance is not None:
        try:
            widget_instance.root.destroy()
        except Exception:
            pass
        widget_instance = None
        settings["widget-visible"] = False
        save_settings(settings)
    else:
        settings["widget-visible"] = True
        save_settings(settings)
        threading.Thread(target=run_widget_thread, daemon=True).start()
        
    update_menu(icon)


def create_circle_icon(color):
    image = Image.new("RGBA", (64, 64), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    draw.ellipse((4, 4, 60, 60), fill=color, outline="white", width=2)
    return image


def update_menu(icon):
    cpu_str = f"CPU: {current_cpu_temp:.1f}°C" if current_cpu_temp > 0.0 else "CPU: N/A"
    gpu_str = f"GPU: {current_gpu_temp:.1f}°C" if current_gpu_temp > 0.0 else "GPU: N/A"
    
    menu_items = [
        pystray.MenuItem(cpu_str, lambda: None, enabled=False),
        pystray.MenuItem(gpu_str, lambda: None, enabled=False),
        pystray.Menu.SEPARATOR,
        pystray.MenuItem("Desktop Widget", toggle_widget, checked=lambda item: widget_instance is not None),
        pystray.MenuItem("Settings", lambda: threading.Thread(target=open_settings_window, daemon=True).start()),
        pystray.Menu.SEPARATOR,
        pystray.MenuItem("Exit", lambda: exit_app(icon)),
    ]
    icon.menu = pystray.Menu(*menu_items)


def monitor_loop(icon):
    global current_cpu_temp, current_gpu_temp
    global last_cpu_alert_time, last_gpu_alert_time

    while True:
        try:
            temps = get_temperatures()
            current_cpu_temp = temps.get("cpu") or 0.0
            current_gpu_temp = temps.get("gpu") or 0.0

            settings = load_settings()
            cpu_limit = settings.get("cpu-max-temperature", 85)
            gpu_limit = settings.get("gpu-max-temperature", 80)
            ntfy_topic = settings.get("ntfy-topic", "")
            icon_color = "#2ecc71"
            if (
                current_cpu_temp >= (cpu_limit - 5)
                or current_gpu_temp >= (gpu_limit - 5)
            ):
                icon_color = "#f1c40f"
            if (
                current_cpu_temp >= cpu_limit
                or current_gpu_temp >= gpu_limit
            ):
                icon_color = "#e74c3c" 

            icon.icon = create_circle_icon(icon_color)
            
            cpu_tooltip = f"{current_cpu_temp:.1f}°C" if current_cpu_temp > 0.0 else "N/A"
            gpu_tooltip = f"{current_gpu_temp:.1f}°C" if current_gpu_temp > 0.0 else "N/A"
            icon.title = f"ThermalWatch\nCPU: {cpu_tooltip} | GPU: {gpu_tooltip}"

            update_menu(icon)
            print(f"Reading: CPU = {current_cpu_temp:.1f}°C | GPU = {current_gpu_temp:.1f}°C")

            now = time.time()

            if current_cpu_temp >= cpu_limit:
                if (now - last_cpu_alert_time) > ALERT_COOLDOWN:
                    title = "🔥 High CPU Temperature!"
                    msg = f"CPU has reached {current_cpu_temp:.1f}°C (Limit: {cpu_limit}°C)"
                    send_windows_notification(title, msg)
                    send_mobile_notification(ntfy_topic, title, msg)
                    last_cpu_alert_time = now

            if current_gpu_temp >= gpu_limit:
                if (now - last_gpu_alert_time) > ALERT_COOLDOWN:
                    time.sleep(1)
                    title = "🔥 High GPU Temperature!"
                    msg = f"GPU has reached {current_gpu_temp:.1f}°C (Limit: {gpu_limit}°C)"
                    send_windows_notification(title, msg)
                    send_mobile_notification(ntfy_topic, title, msg)
                    last_gpu_alert_time = now

        except Exception as e:
            print(f"Error in monitor loop: {e}")

        time.sleep(5)


def exit_app(icon):
    """Closes the application."""
    icon.visible = False
    icon.stop()
    os._exit(0)


def main():
    global global_icon
    initial_icon = create_circle_icon("#2ecc71")

    icon = pystray.Icon(
        "ThermalWatch",
        initial_icon,
        "ThermalWatch",
    )

    global_icon = icon
    update_menu(icon)

    # Check if widget should be shown on startup
    settings = load_settings()
    if settings.get("widget-visible", False):
        threading.Thread(target=run_widget_thread, daemon=True).start()

    monitor_thread = threading.Thread(
        target=monitor_loop, args=(icon,), daemon=True
    )
    monitor_thread.start()
    icon.run()

if __name__ == "__main__":
    main()
