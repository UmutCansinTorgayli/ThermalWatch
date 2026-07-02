import time
import sys
import os

# Ensure we can import monitor
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from monitor import get_system_stats

print("--- ThermalWatch Sensor Performance Benchmark ---")
print("Running get_system_stats() 20 times to measure average speed...")

total_time = 0.0
runs = 20

for i in range(runs):
    start = time.perf_counter()
    stats = get_system_stats()
    end = time.perf_counter()
    duration = end - start
    total_time += duration
    print(f"Run {i+1:02d}: {duration:.4f} seconds | CPU Temp: {stats.get('cpu_temp')}°C | CPU Fan: {stats.get('cpu_fan')} RPM")

avg_time = total_time / runs
print("\n--- Results ---")
print(f"Average Query Time: {avg_time:.4f} seconds ({(avg_time * 1000):.1f} ms)")
print(f"Estimated single-core CPU impact (polled every 5s): {(avg_time / 5.0) * 100:.3f}%")
