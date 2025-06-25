import os
import re
import subprocess

def get_motherboard_info():
    try:
        # Основные параметры через общедоступные sysfs пути
        sysfs_path = "/sys/devices/virtual/dmi/id/"
        info = {}
        
        # Список файлов для безопасного чтения
        safe_files = {
            'manufacturer': 'board_vendor',
            'product': 'board_name',
            'version': 'board_version',
            'bios_vendor': 'bios_vendor',
            'bios_version': 'bios_version',
            'bios_date': 'bios_date'
        }
        
        for key, filename in safe_files.items():
            path = os.path.join(sysfs_path, filename)
            if os.path.exists(path):
                try:
                    with open(path, 'r') as f:
                        value = f.read().strip()
                        # Фильтрация нечитаемых символов
                        value = re.sub(r'[^\x20-\x7E]', '', value)
                        info[key] = value if value else 'Неизвестно'
                except PermissionError:
                    info[key] = 'Нет доступа'
            else:
                info[key] = 'Недоступно'
        
        # Альтернативные методы для серийного номера
        serial_paths = [
            "/sys/devices/virtual/dmi/id/board_serial",
            "/sys/class/dmi/id/board_serial",
            "/sys/firmware/dmi/tables/smbios_entry_point"
        ]
        
        for path in serial_paths:
            if os.path.exists(path):
                try:
                    with open(path, 'r') as f:
                        serial = f.read().strip()
                        if serial and serial != 'None':
                            info['serial'] = re.sub(r'[^\x20-\x7E]', '', serial)
                            break
                except:
                    continue
        else:
            info['serial'] = 'Неизвестно'
        
        # Получение информации о чипсете через lspci (без sudo)
        try:
            lspci_output = subprocess.check_output(
                ['lspci', '-vmm'], 
                stderr=subprocess.DEVNULL,
                text=True
            )
            
            chipset_match = re.search(r'^Device:\s*(.*bridge.*)$', lspci_output, re.I | re.M)
            if chipset_match:
                info['chipset'] = chipset_match.group(1).split(':')[-1].strip()
            else:
                info['chipset'] = 'Автоопределение не удалось'
        except:
            info['chipset'] = 'lspci недоступен'
        
        return info
        
    except Exception as e:
        return {'error': f"Ошибка получения данных: {str(e)}"}