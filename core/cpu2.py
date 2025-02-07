import psutil
import time

def monitor_cpu():
    while True:
        # Получаем загрузку CPU
        if not hasattr(psutil,"sensors_temperatures"):
            print("Hет поддержки")
            return
        
        temp = psutil.sensors_temperatures()
        cpu_usage = psutil.cpu_percent(interval=0.0)
        logical_cpus = psutil.cpu_count(logical=True)
        physical_cpus = psutil.cpu_count(logical=False)
        cpu_freq = psutil.cpu_freq()
        
        if not temp:
            print("Нет данных")
            return
        
        print(f"Загрузка CPU: {cpu_usage}%")
        print(f"Кол-во ядер/потоков {physical_cpus} / {logical_cpus}")
        print(f"Текущая частота: {round(cpu_freq.current, 1)} МГц")
        print(f"Минимальная частота: {cpu_freq.min} МГц")
        print(f"Максимальная частота: {cpu_freq.max} МГц")
        
        for name, entries in temp.items():
            print(name)
            for entry in entries:
                print(f" {entry.label or name}: {entry.current} °C (high = {entry.high} °C, critical = {entry.critical} °C)")
        # Получаем информацию о времени работы CPU
        cpu_times = psutil.cpu_times(percpu=True)
        for i, times in enumerate(cpu_times):
            print(f"CPU Core {i + 1}: user={times.user}, system={times.system}, idle={times.idle}")
        
        time.sleep(1)


if __name__ == "__main__":
    monitor_cpu()