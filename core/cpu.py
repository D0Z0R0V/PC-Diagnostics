import psutil
import time

def monitor_cpu():
    while True:
        # Получаем загрузку CPU в процентах
        cpu_usage = psutil.cpu_percent(interval=1)
        logical_cpus = psutil.cpu_count(logical=True)
        physical_cpus = psutil.cpu_count(logical=False)
        cpu_freq = psutil.cpu_freq()
        
        print(f"Кол-во ядер/потоков {physical_cpus} / {logical_cpus}")
        print(f"Загрузка CPU: {cpu_usage}%")
        print(f"Текущая частота: {round(cpu_freq.current, 1)} МГц")
        print(f"Минимальная частота: {cpu_freq.min} МГц")
        print(f"Максимальная частота: {cpu_freq.max} МГц")
        
        # Получаем информацию о времени работы CPU
        cpu_times = psutil.cpu_times(percpu=True)
        for i, times in enumerate(cpu_times):
            print(f"CPU Core {i + 1}: user={times.user}, system={times.system}, idle={times.idle}")
        
        # Задержка перед следующим измерением
        time.sleep(1)

if __name__ == "__main__":
    monitor_cpu()
