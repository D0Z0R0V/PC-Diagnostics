import datetime
import csv
import random


def generate_balanced_data():
    filename = 'system_data.csv'
    header = ['timestamp', 'cpu_usage', 'cpu_temp', 'gpu_usage', 'gpu_temp', 'disk_usage', 'ram_usage', 'system_state']
    
    with open(filename, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(header)

        for _ in range(200):
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cpu_usage = round(random.uniform(0, 100), 1)
            cpu_temp = round(random.uniform(30, 69), 1)  # < 70
            gpu_usage = round(random.uniform(0, 100), 1)
            gpu_temp = round(random.uniform(40, 79), 1)  # < 80
            disk_usage = round(random.uniform(10, 79), 1)  # < 80
            ram_usage = round(random.uniform(20, 64), 1)  # < 65
            system_state = "Normal"
            row = [timestamp, cpu_usage, cpu_temp, gpu_usage, gpu_temp, disk_usage, ram_usage, system_state]
            writer.writerow(row)
        
        for _ in range(200):
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cpu_usage = round(random.uniform(0, 100), 1)
            cpu_temp = round(random.uniform(70, 89), 1)  # 70 <= x < 90
            gpu_usage = round(random.uniform(0, 100), 1)
            gpu_temp = round(random.uniform(80, 84), 1)  # 80 <= x < 85
            disk_usage = round(random.uniform(10, 98), 1)
            ram_usage = round(random.uniform(20, 98), 1)
            system_state = "Warning"
            row = [timestamp, cpu_usage, cpu_temp, gpu_usage, gpu_temp, disk_usage, ram_usage, system_state]
            writer.writerow(row)
        
        for _ in range(200):
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cpu_usage = round(random.uniform(0, 100), 1)
            cpu_temp = round(random.uniform(91, 105), 1)  # > 90
            gpu_usage = round(random.uniform(0, 100), 1)
            gpu_temp = round(random.uniform(86, 105), 1)  # > 85
            disk_usage = round(random.uniform(10, 98), 1)
            ram_usage = round(random.uniform(82, 98), 1)  # > 81
            system_state = "Critical"
            row = [timestamp, cpu_usage, cpu_temp, gpu_usage, gpu_temp, disk_usage, ram_usage, system_state]
            writer.writerow(row)
            
    print(f"Сбалансированные данные сгенерированы и записаны в {filename}")
    
generate_balanced_data()
