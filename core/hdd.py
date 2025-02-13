import psutil
import time

def monitor_hdd():
    """Получает информацию о корневом разделе диска."""
    
    # Определяем корневой раздел
    root_partition = next((p for p in psutil.disk_partitions() if p.mountpoint == '/'), None)
    
    if not root_partition:
        print("Не удалось определить корневой раздел.")
        return
    
    try:
        usage = psutil.disk_usage(root_partition.mountpoint)

        print(f"Устройство: {root_partition.device}")
        print(f"Тип файловой системы: {root_partition.fstype}")
        print(f"Общий размер: {usage.total / (1024.0 ** 3):.2f} ГБ")
        print(f"Используемое место: {usage.used / (1024.0 ** 3):.2f} ГБ")
        print(f"Свободное место: {usage.free / (1024.0 ** 3):.2f} ГБ")
        print(f"Процент использования: {usage.percent}%\n")

    except PermissionError:
        print("Ошибка доступа к информации о диске.")

while True:
    monitor_hdd()
    time.sleep(1)
