import os
import psutil
import subprocess
from typing import Dict, Optional


def monitor_ram():
    try:
        ram = psutil.virtual_memory()
        
        ram_info = {
            "ram": round(ram.total / (1024**3), 2),  # ГБ (добавлена закрывающая скобка и точность)
            "free": round(ram.available / (1024**3), 2),  # ГБ
            "usage": round(ram.used / (1024**3), 2),  # ГБ
            "percent": ram.percent,
            "type": _detect_ram_type(),  # Новая функция для определения типа
            "speed": "N/A (требует root)"  # Честное указание ограничения
        }
        return ram_info
    except Exception as e:
        print(f"Ошибка мониторинга RAM: {str(e)}")
        return None

def _detect_ram_type():
    """Определение типа RAM без root-прав"""
    # Метод 1: Через sysfs (если доступно)
    if os.path.exists('/sys/class/dmi/id/modalias'):
        try:
            with open('/sys/class/dmi/id/modalias') as f:
                modalias = f.read().lower()
                if 'ddr4' in modalias: return 'DDR4'
                elif 'ddr3' in modalias: return 'DDR3'
        except:
            pass
    
    # Метод 2: Косвенное определение через CPU
    try:
        with open('/proc/cpuinfo') as f:
            cpuinfo = f.read()
            if 'Ryzen' in cpuinfo: return 'DDR4/DDR5'
            elif 'Intel' in cpuinfo: return 'DDR3/DDR4'
    except:
        pass
    
    return 'Unknown'