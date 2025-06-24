import psutil

def get_voltage_info():
    try:
        # Информация о батарее (если есть)
        battery = psutil.sensors_battery()
        battery_info = {}
        
        if battery:
            battery_info = {
                'power_plugged': "Да" if battery.power_plugged else "Нет",
                'percent': battery.percent,
                'secsleft': battery.secsleft
            }
        
        # Информация о напряжениях (псевдо-данные, так как без root сложно получить реальные значения)
        # В реальном приложении можно попробовать читать /sys/class/hwmon/
        voltage_info = {
            'cpu_voltage': "N/A (требуется root)",
            'gpu_voltage': "N/A (требуется root)",
            'ram_voltage': "N/A (требуется root)"
        }
        
        return {
            'battery': battery_info,
            'voltages': voltage_info
        }
    except Exception as e:
        return {'error': str(e)}