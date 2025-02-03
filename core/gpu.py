from pynvml import *
import time

nvmlInit()

def monitor_gpu():
    divice = nvmlDeviceGetCount()
    
    for i in range(divice):
        handle = nvmlDeviceGetHandleByIndex(i)
        gpu_name = nvmlDeviceGetName(handle)
        temperatura = nvmlDeviceGetTemperature(handle, NVML_TEMPERATURE_GPU)
        clock_freq = nvmlDeviceGetClockInfo(handle, NVML_CLOCK_GRAPHICS)
        load = nvmlDeviceGetUtilizationRates(handle)
        
        print(f"GPU {i}: {gpu_name}")
        print(f"Нагрузка на GPU: {load.gpu}")
        print(f"Загрузка на памяти GPU: {load.memory}")
        print(f"Температура: {temperatura} C")
        print(f"Частота графического чипа: {clock_freq} МГц")
        
while True:
    monitor_gpu()
    time.sleep(1)
        
        
