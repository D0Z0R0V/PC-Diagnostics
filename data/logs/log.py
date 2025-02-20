import datetime
import pandas as pd
import csv, os

from core.cpu import get_cpu_info
from core.gpu import monitor_gpu
from core.hdd import monitor_hdd
from core.ram import monitor_ram

from dotenv import load_dotenv

load_dotenv()


def determine_system_state(cpu_usage, gpu_usage, ram_usage, disk_usage):
    """Определяет состояние системы на основе пороговых значений."""
    if cpu_usage is None or gpu_usage is None:
        return "Error" 

    if cpu_usage < 70 and gpu_usage < 80 and ram_usage < 75 and disk_usage < 80:
        return 'Normal'
    elif cpu_usage >= 70 and cpu_usage < 90 or gpu_usage >= 80 and gpu_usage < 90:
        return 'Warning'

filename = os.getenv('FILENAME')
header = ['timestamp', 'cpu_usage', 'cpu_temp', 'gpu_usage', 'gpu_temp', 'disk_usage', 'ram_usage', 'system_state']
if not filename:
    filename = 'default_file.csv'
    
file_ex = os.path.isfile(filename)

# Проверяем, существует ли файл. Если нет, записываем заголовок.
try:
    with open(filename, 'a', newline='') as csvfile:
        writer = csv.writer(csvfile)
        
        if not file_ex:
            writer.writerow(header)
except FileExistsError:
    pass

# Сбор данных и запись в CSV
cpu_info = get_cpu_info()

if "error" in cpu_info:
    print(f"Ошибка CPU: {cpu_info['error']}")
    cpu_usage = None
    cpu_temp = None
else:
    cpu_usage = cpu_info["usage"]
    if cpu_info["temperatures"]:
        coretemp = cpu_info['temperatures']['coretemp']
        if coretemp:
            cpu_temp = coretemp[0]['current']
 
gpu_info = monitor_gpu()   
if not gpu_info:
    print("Ошибка: Не удалось получить данные о видеокарте")
else:
    gpu_data = gpu_info[0]
    gpu_usage = gpu_data['load']
    gpu_temp = gpu_data['temperatura']

hdd_info = monitor_hdd()
if not hdd_info:
    print("Ошибка: Не удалось получить данные о HDD")
else:
    disk_usage = hdd_info['percent']

ram_info = monitor_ram()
if not ram_info:
    print("Ошибка: Не удалось получить данные RAM")
else:
    ram_usage = ram_info['percent']

system_state = determine_system_state(cpu_usage, gpu_usage, ram_usage, disk_usage)

timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

row = [timestamp, cpu_usage, cpu_temp, gpu_usage, gpu_temp, disk_usage, ram_usage, system_state]

with open(filename, 'a', newline='') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(row)

print(f"Данные записаны в {filename}")
