import os
import sys
import threading
import time
from PIL import Image, ImageDraw
import pystray
from collections import deque

from config import load_settings, save_settings
from monitor import get_system_stats
from notifier import send_mobile_notification, send_windows_notification
current_cpu_temp = 0.0
current_gpu_temp = 0.0
current_cpu_fan = None
current_gpu_fan = None
current_cpu_usage = 0.0
current_gpu_usage = 0.0
last_cpu_alert_time = 0.0
last_gpu_alert_time = 0.0
ALERT_COOLDOWN = 300
stats_history = deque(maxlen=120)

global_icon = None
widget_instance = None


def run_widget_thread():
    global widget_instance
    from gui import TemperatureWidget
    
    def on_close():
        global widget_instance
        widget_instance = None
        if global_icon:
            threading.Thread(target=lambda: update_menu(global_icon), daemon=True).start()
            
    widget_instance = TemperatureWidget(
        get_stats_callback=lambda: (
            current_cpu_temp,
            current_gpu_temp,
            current_cpu_usage,
            current_gpu_usage,
            current_cpu_fan,
            current_gpu_fan
        ),
        on_close_callback=on_close
    )
    widget_instance.start()


def toggle_widget(icon, item):
    global widget_instance
    settings = load_settings()
    
    if widget_instance is not None:
        widget_instance.should_close = True
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


def show_settings():
    from gui import open_settings_window
    get_stats = lambda: (
        current_cpu_temp,
        current_gpu_temp,
        current_cpu_usage,
        current_gpu_usage,
        current_cpu_fan,
        current_gpu_fan
    )
    threading.Thread(
        target=lambda: open_settings_window(
            diagnose_callback=diagnose_system,
            get_stats_callback=get_stats
        ),
        daemon=True
    ).start()


def update_menu(icon):
    cpu_str = f"CPU: {current_cpu_temp:.1f}°C"
    if current_cpu_fan is not None:
        cpu_str += f" ({current_cpu_fan:.0f} RPM)"
    elif current_cpu_temp <= 0.0:
        cpu_str = "CPU: N/A"
        
    gpu_str = f"GPU: {current_gpu_temp:.1f}°C"
    if current_gpu_fan is not None:
        gpu_str += f" ({current_gpu_fan:.0f} RPM)"
    elif current_gpu_temp <= 0.0:
        gpu_str = "GPU: N/A"
        
    menu_items = [
        pystray.MenuItem(cpu_str, lambda: None, enabled=False),
        pystray.MenuItem(gpu_str, lambda: None, enabled=False),
        pystray.Menu.SEPARATOR,
        pystray.MenuItem("Desktop Widget", toggle_widget, checked=lambda item: widget_instance is not None),
        pystray.MenuItem("Settings", lambda: show_settings()),
        pystray.Menu.SEPARATOR,
        pystray.MenuItem("Exit", lambda: exit_app(icon)),
    ]
    icon.menu = pystray.Menu(*menu_items)


def monitor_loop(icon):
    global current_cpu_temp, current_gpu_temp
    global current_cpu_fan, current_gpu_fan, current_cpu_usage, current_gpu_usage
    global last_cpu_alert_time, last_gpu_alert_time
    global stats_history

    while True:
        try:
            stats = get_system_stats()
            current_cpu_temp = stats.get("cpu_temp") or 0.0
            current_gpu_temp = stats.get("gpu_temp") or 0.0
            current_cpu_fan = stats.get("cpu_fan")
            current_gpu_fan = stats.get("gpu_fan")
            current_cpu_usage = stats.get("cpu_usage") or 0.0
            current_gpu_usage = stats.get("gpu_usage") or 0.0

            stats_history.append({
                "timestamp": time.time(),
                "cpu_temp": current_cpu_temp,
                "gpu_temp": current_gpu_temp,
                "cpu_usage": current_cpu_usage,
                "gpu_usage": current_gpu_usage,
                "cpu_fan": current_cpu_fan,
                "gpu_fan": current_gpu_fan
            })

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
            if current_cpu_fan is not None:
                cpu_tooltip += f" ({current_cpu_fan:.0f} RPM)"
                
            gpu_tooltip = f"{current_gpu_temp:.1f}°C" if current_gpu_temp > 0.0 else "N/A"
            if current_gpu_fan is not None:
                gpu_tooltip += f" ({current_gpu_fan:.0f} RPM)"
                
            icon.title = f"ThermalWatch\nCPU: {cpu_tooltip}\nGPU: {gpu_tooltip}"

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
            import gc
            gc.collect()
        except Exception as e:
            print(f"Error in monitor loop: {e}")

        time.sleep(5)


def exit_app(icon):
    """Closes the application."""
    icon.visible = False
    icon.stop()
    os._exit(0)


def diagnose_system():
    """Analyzes the stats_history data and returns a diagnostic health report."""
    # Wait for at least 1 minute of data (12 points) to make it statistically valid
    if len(stats_history) < 12:
        return "Analyzing system... (Not enough data collected yet. Please wait a minute.)"

    # Extract averages from history
    cpu_temps = [d["cpu_temp"] for d in stats_history]
    gpu_temps = [d["gpu_temp"] for d in stats_history]
    cpu_usages = [d["cpu_usage"] for d in stats_history]
    gpu_usages = [d["gpu_usage"] for d in stats_history]
    
    avg_cpu_temp = sum(cpu_temps) / len(cpu_temps)
    avg_gpu_temp = sum(gpu_temps) / len(gpu_temps)
    avg_cpu_usage = sum(cpu_usages) / len(cpu_usages)
    avg_gpu_usage = sum(gpu_usages) / len(gpu_usages)

    # Filter fans (extract only non-None values)
    cpu_fans = [d["cpu_fan"] for d in stats_history if d["cpu_fan"] is not None]
    gpu_fans = [d["gpu_fan"] for d in stats_history if d["gpu_fan"] is not None]
    
    avg_cpu_fan = sum(cpu_fans) / len(cpu_fans) if cpu_fans else None
    avg_gpu_fan = sum(gpu_fans) / len(gpu_fans) if gpu_fans else None

    # Diagnostic report list
    diagnostics = []

    # CPU Diagnostics
    if avg_cpu_usage < 15.0 and avg_cpu_temp > 75.0:
        diagnostics.append("⚠️ CPU is running hot despite low usage. Your thermal paste might be dry, or the cooler mount could be loose.")
    elif avg_cpu_temp > 85.0:
        diagnostics.append("⚠️ CPU temperature is critically high. Ensure your cooler is working and fan vents are clear.")

    # GPU Diagnostics
    if avg_gpu_temp > 80.0:
        if avg_gpu_fan is not None and avg_gpu_fan > 2500:
            diagnostics.append("⚠️ GPU is running hot even at high fan speeds. Check case air circulation or clean dust from fans.")
        else:
            diagnostics.append("⚠️ GPU temperature is high. If fans are not spinning, check fan curve configurations.")

    # Rule-based output fallback
    if not diagnostics:
        rule_report = "✅ System health is excellent. Temperatures and usage patterns are normal."
    else:
        rule_report = "\n".join(diagnostics)

    # Read configuration for selected AI engine
    settings = load_settings()
    ai_engine = settings.get("ai-engine", "none")
    
    if ai_engine == "none":
        return rule_report

    # Format telemetry data for LLM
    telemetry = {
        "avg_cpu_temp": f"{avg_cpu_temp:.1f}°C",
        "avg_gpu_temp": f"{avg_gpu_temp:.1f}°C" if avg_gpu_temp > 0.0 else "N/A",
        "avg_cpu_usage": f"{avg_cpu_usage:.1f}%",
        "avg_gpu_usage": f"{avg_gpu_usage:.1f}%",
        "avg_cpu_fan": f"{avg_cpu_fan:.0f} RPM" if avg_cpu_fan else "N/A",
        "avg_gpu_fan": f"{avg_gpu_fan:.0f} RPM" if avg_gpu_fan else "N/A"
    }

    import requests

    # --- 1. GOOGLE GEMINI CLOUD AI ---
    if ai_engine == "gemini":
        api_key = settings.get("gemini-api-key", "").strip()
        if not api_key:
            return f"⚠️ Gemini API key is missing. Paste your key in Settings -> AI Advisor.\n\nFallback Report:\n\n{rule_report}"

        prompt = (
            f"Analyze this rolling 10-minute sensor telemetry:\n"
            f"{telemetry}\n\n"
            f"Rule-based diagnostic flags: {diagnostics if diagnostics else 'No issues detected.'}\n\n"
            f"You are a professional PC hardware thermal and performance analyst. Give a friendly, extremely concise (max 3 sentences) diagnostics report in Turkish. Suggest recommendations only if there are anomalies."
        )

        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
            headers = {"Content-Type": "application/json"}
            payload = {
                "contents": [
                    {
                        "parts": [
                            {"text": prompt}
                        ]
                    }
                ]
            }
            response = requests.post(url, headers=headers, json=payload, timeout=6)
            if response.status_code == 200:
                res_data = response.json()
                ai_content = res_data["candidates"][0]["content"]["parts"][0]["text"].strip()
                return f"🤖 [Gemini AI Health Report]\n\n{ai_content}"
            else:
                return f"⚠️ Gemini API Error (Status {response.status_code}). Fallback Report:\n\n{rule_report}"
        except Exception as e:
            return f"⚠️ Could not connect to Gemini API. Check your internet connection.\n\nFallback Report:\n\n{rule_report}"

    # --- 2. LOCAL OLLAMA OFFLINE AI ---
    elif ai_engine == "ollama":
        try:
            # Check if Ollama is running and query installed models
            tags_response = requests.get("http://localhost:11434/api/tags", timeout=2)
            if tags_response.status_code != 200:
                return f"⚠️ Ollama API Error (Status {tags_response.status_code}). Fallback Report:\n\n{rule_report}"
                
            models_data = tags_response.json()
            models = models_data.get("models", [])
            if not models:
                return f"⚠️ Ollama is running but no local models are installed.\nUse Auto-Install or pull a model in CMD.\n\nFallback Report:\n\n{rule_report}"
                
            # Select first available model
            selected_model = models[0]["name"]
            
            prompt = (
                f"Analyze this rolling 10-minute sensor telemetry:\n"
                f"{telemetry}\n\n"
                f"Rule-based diagnostic flags: {diagnostics if diagnostics else 'No issues detected.'}\n\n"
                f"Diagnose if the temperatures and fan speeds are normal for these usage loads. Suggest recommendations only if there are anomalies."
            )
            
            payload = {
                "model": selected_model,
                "messages": [
                    {"role": "system", "content": "You are a professional PC hardware thermal and performance analyst. Give a friendly, extremely concise (max 3 sentences) diagnostics report. Answer in Turkish."},
                    {"role": "user", "content": prompt}
                ],
                "stream": False
            }
            
            chat_response = requests.post("http://localhost:11434/api/chat", json=payload, timeout=8)
            if chat_response.status_code == 200:
                ai_content = chat_response.json().get("message", {}).get("content", "").strip()
                return f"🤖 [AI Health Report ({selected_model})]\n\n{ai_content}"
            else:
                return f"⚠️ Ollama returned error {chat_response.status_code}. Fallback Report:\n\n{rule_report}"
                
        except Exception as e:
            return f"⚠️ Could not connect to Ollama (Connection Refused or Timeout).\nMake sure Ollama is open and running.\n\nFallback Report:\n\n{rule_report}"


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
