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
    
    print(f"Оперативная память: {ram.total / (1024**3):.2f} ГБ")
    print(f"Доступная память: {ram.available / (1024**3):.2f} ГБ")
    print(f"Используемая память: {ram.used / (1024**3):.2f} ГБ")
    print(f"Ипользовано: {ram.percent} % ")
    
    
while True:
    monitor_ram()
    time.sleep(1)
