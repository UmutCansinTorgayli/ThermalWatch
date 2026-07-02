import sys
import os

import pythonnet
pythonnet.load("netfx")
import clr

# Automatically detect the PyInstaller temp folder (sys._MEIPASS) or normal folder
if getattr(sys, 'frozen', False):
    BASE_DIR = sys._MEIPASS
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

LIBS_DIR = os.path.join(BASE_DIR, "libs")
sys.path.append(LIBS_DIR)

clr.AddReference("LibreHardwareMonitorLib")
from LibreHardwareMonitor.Hardware import Computer, HardwareType, SensorType


def get_system_stats():
    """Returns CPU/GPU temperatures, fan speeds, and usage (load) rates."""
    stats = {
        "cpu_temp": None,
        "gpu_temp": None,
        "cpu_fan": None,
        "gpu_fan": None,
        "cpu_usage": None,
        "gpu_usage": None
    }
    try:
        computer = Computer()
        computer.IsCpuEnabled = True
        computer.IsGpuEnabled = True
        computer.IsMotherboardEnabled = True  # Required for motherboard fans
        computer.Open()
        
        def process_hardware(hardware):
            hardware.Update()
            for sensor in hardware.Sensors:
                name = sensor.Name.lower()
                val = sensor.Value
                if val is None:
                    continue
                
                # 1. Temperatures
                if sensor.SensorType == SensorType.Temperature:
                    if hardware.HardwareType == HardwareType.Cpu:
                        if any(k in name for k in ("package", "tdie", "tctl")):
                            stats["cpu_temp"] = float(val)
                    elif hardware.HardwareType in (HardwareType.GpuNvidia, HardwareType.GpuAmd):
                        if any(k in name for k in ("core", "gpu core")):
                            stats["gpu_temp"] = float(val)
                
                # 2. Usage Loads (Load)
                elif sensor.SensorType == SensorType.Load:
                    if hardware.HardwareType == HardwareType.Cpu:
                        if "total" in name:
                            stats["cpu_usage"] = float(val)
                    elif hardware.HardwareType in (HardwareType.GpuNvidia, HardwareType.GpuAmd):
                        if any(k in name for k in ("core", "gpu core")):
                            stats["gpu_usage"] = float(val)
                
                # 3. Fan Speeds (Fan)
                elif sensor.SensorType == SensorType.Fan:
                    if hardware.HardwareType in (HardwareType.GpuNvidia, HardwareType.GpuAmd):
                        # Get graphics card fan speed if available
                        stats["gpu_fan"] = float(val)
                    else:
                        # Capture CPU/motherboard fan on SuperI/O and Motherboard sub-hardwares
                        if "cpu" in name:
                            stats["cpu_fan"] = float(val)
                        elif "pump" in name or "water" in name or "aio" in name:
                            if stats["cpu_fan"] is None or stats["cpu_fan"] == 0:
                                stats["cpu_fan"] = float(val)
            
            # Recursively update and scan nested sub-hardware (e.g. Motherboard SuperI/O chips)
            for sub in hardware.SubHardware:
                process_hardware(sub)

        for hardware in computer.Hardware:
            process_hardware(hardware)

        computer.Close()
    except Exception as e:
        print(f"Sensor query error: {e}")
        
    return stats



if __name__ == "__main__":
    print(get_system_stats())