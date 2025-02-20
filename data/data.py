import datetime
import csv
import random


def generate_data(num_rows):
    filename = 'system_data.csv'
    header = ['timestamp', 'cpu_usage', 'cpu_temp', 'gpu_usage', 'gpu_temp', 'disk_usage', 'ram_usage', 'system_state']
    
    with open(filename, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(header)
        
        for _ in range(num_rows):
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cpu_usage = round(random.uniform(0,100), 1)
            cpu_temp = round(random.uniform(30,105), 1)
            gpu_usage = round(random.uniform(0,100), 1)
            gpu_temp = round(random.uniform(40,105), 1)
            disk_usage = round(random.uniform(10,98), 1)
            ram_usage = round(random.uniform(20,98), 1)
            
            if cpu_temp < 70 and gpu_temp < 80 and ram_usage < 65 and disk_usage < 80:
                system_state = "Normal"
            elif cpu_temp >= 70 and cpu_temp < 90 and gpu_temp >= 80 and gpu_temp < 85:
                system_state = "Warning"
            elif cpu_temp > 90 and gpu_temp > 85 and ram_usage > 81:
                system_state = "Critical"
                
            row = [timestamp, cpu_usage, cpu_temp, gpu_usage, gpu_temp, disk_usage, ram_usage, system_state]
            writer.writerow(row)
            
    print(f"Синтетические данные сгенерированы и записаны в {filename}")
    
generate_data(500)