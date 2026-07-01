import sys
import os
import pythonnet
pythonnet.load("netfx")
import clr
sys.path.append(r"d:\ThermalWatch\libs")
clr.AddReference("LibreHardwareMonitorLib")
from LibreHardwareMonitor.Hardware import Computer

computer = Computer()
computer.IsCpuEnabled = True
computer.IsGpuEnabled = True
computer.IsMotherboardEnabled = True
computer.IsControllerEnabled = True
computer.Open()

print("--- Hardware and Sensors Found ---")
for hardware in computer.Hardware:
    hardware.Update()
    print(f"\nHardware: {hardware.Name} (Type: {hardware.HardwareType})")
    for sensor in hardware.Sensors:
        print(f"  Sensor: {sensor.Name} | Type: {sensor.SensorType} | Value: {sensor.Value}")
computer.Close()
