import psutil
import time

def monitor_ram():
    
    ram = psutil.virtual_memory()
    
    print(f"Оперативная память: {ram.total}")
    
    
while True:
    monitor_ram()
    time.sleep(1)
