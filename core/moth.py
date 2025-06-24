import os
import re

def get_motherboard_info():
    try:
        # Пытаемся получить информацию из sysfs
        sysfs_path = "/sys/class/dmi/id/"
        info = {}
        
        # Список файлов, которые мы будем читать
        files = {
            'manufacturer': 'board_vendor',
            'product': 'board_name',
            'version': 'board_version',
            'serial': 'board_serial',
            'bios_vendor': 'bios_vendor',
            'bios_version': 'bios_version',
            'bios_date': 'bios_date'
        }
        
        for key, filename in files.items():
            path = os.path.join(sysfs_path, filename)
            if os.path.exists(path):
                with open(path, 'r') as f:
                    value = f.read().strip()
                    info[key] = value if value else 'Неизвестно'
            else:
                info[key] = 'Недоступно'
        
        return info
        
    except Exception as e:
        return {'error': f"Ошибка получения данных: {str(e)}"}