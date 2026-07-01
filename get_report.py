import sys
import os
import pythonnet
pythonnet.load("coreclr")
import clr
sys.path.append(r"d:\ThermalWatch\libs")
clr.AddReference("LibreHardwareMonitorLib")
from LibreHardwareMonitor.Hardware import Computer

computer = Computer()
computer.IsCpuEnabled = True
computer.IsGpuEnabled = True
computer.Open()

report = computer.GetReport()
print("--- LIBRE HARDWARE MONITOR REPORT ---")
print(report[:1500]) 
computer.Close()
