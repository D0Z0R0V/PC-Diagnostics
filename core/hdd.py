import psutil, time

def monitor_hdd():
    
    part = psutil.disk_partitions()
    
    for partition in part:
        try:
            usage = psutil.disk_usage(partition.mountpoint)
            
            print(f"Устройство: {partition.device}")
            #print(f"Точка монтирования: {partition.mountpoint}")
            print(f"Тип файловой системы: {partition.fstype}")
            print(f"Общий размер: {usage.total / (1024.0 ** 3):.2f} ГБ")
            print(f"Используемое место: {usage.used / (1024.0 ** 3):.2f} ГБ")
            print(f"Свободное место: {usage.free / (1024.0 ** 3):.2f} ГБ")
        except PermissionError:
            continue
        
        if 'used' in locals() and 'total' in locals():
            percent_used = usage.percent
            
        else:
            continue
            
        print(f"Процент использования: {percent_used}%\n")
        
while True:
    monitor_hdd()
    time.sleep(1)