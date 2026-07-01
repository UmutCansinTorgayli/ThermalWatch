import sys
import os

import pythonnet
pythonnet.load("netfx")
import clr

# PyInstaller geçici klasörünü (sys._MEIPASS) veya normal klasörü otomatik tespit et
if getattr(sys, 'frozen', False):
    BASE_DIR = sys._MEIPASS
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

LIBS_DIR = os.path.join(BASE_DIR, "libs")
sys.path.append(LIBS_DIR)

clr.AddReference("LibreHardwareMonitorLib")
from LibreHardwareMonitor.Hardware import Computer, HardwareType, SensorType


def get_temperatures():
    """CPU ve GPU sıcaklıklarını döner."""
    temps = {"cpu": None, "gpu": None}
    try:
        computer = Computer()
        computer.IsCpuEnabled = True
        computer.IsGpuEnabled = True
        computer.Open()
        for hardware in computer.Hardware:
            hardware.Update()
            for sensor in hardware.Sensors:
                if sensor.SensorType == SensorType.Temperature:
                    name = sensor.Name.lower()
                    val = sensor.Value
                    if val is None or float(val) <= 0:
                        continue
                    if hardware.HardwareType == HardwareType.Cpu:
                        if any(k in name for k in ("package", "tdie", "tctl")):
                            temps["cpu"] = float(val)
                    if hardware.HardwareType in (HardwareType.GpuNvidia, HardwareType.GpuAmd):
                        if any(k in name for k in ("core", "gpu core")):
                            temps["gpu"] = float(val)
        computer.Close()
    except Exception:
        pass
    return temps


if __name__ == "__main__":
    print(get_temperatures())