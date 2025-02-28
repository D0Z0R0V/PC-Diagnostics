import multiprocessing
import psutil
import subprocess
import time
import math
import random

def load_cpu():
    """Функция для нагрузки процессора."""
    while True:
        math.sin(random.random())
        math.cos(random.random())
        math.sqrt(random.random())

def get_temperature():
    """Функция для получения температуры процессора."""
    try:
        output = subprocess.check_output(['sensors']).decode('utf-8')
        for line in output.split('\n'):
            if 'Core' in line:
                temp = line.split(':')[1].strip().split()[0]
                return temp
    except Exception as e:
        print(f"Ошибка при получении температуры: {e}")
        return None

if __name__ == "__main__":
    num_processes = multiprocessing.cpu_count()

    processes = []
    for _ in range(num_processes):
        p = multiprocessing.Process(target=load_cpu)
        p.start()
        processes.append(p)
    
    start_time = time.time()
    while time.time() - start_time < 60:
        print(f"Загрузка CPU: {psutil.cpu_percent()}%")
        temp = get_temperature()
        if temp:
            print(f"Температура процессора: {temp}")
        time.sleep(1)
    
    # Завершаем процессы
    for p in processes:
        p.terminate()
