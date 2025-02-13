import psutil, time, subprocess


def monitor_ram():
    
    ram = psutil.virtual_memory()
    
    '''try:
        output = subprocess.check_output(['sudo', 'dmidecode', '--type', 'memory'])
        output = output.decode('utf-8')
        
        speed_line = [line for line in output.split('\n') if 'Speed' in line]
        type_line = [line for line in output.split('\n') if 'Type' in line]
        
        if speed_line and type_line:
            print(f"Скорость:{speed_line[0]}")
            print(f"Тип:{type_line[0]}")
            
    except Exception as ex:
        print(f"Ошибка при получении данных: {ex}")'''
    
    ram_info = {
        "ram": round(ram.total / (1024**3), 2), #ГБ
        "free": round(ram.available / (1024**3), 2), #ГБ
        "usage": round(ram.used / (1024**3), 2), #ГБ
        "percent": ram.percent, # %
    }
    return ram_info
