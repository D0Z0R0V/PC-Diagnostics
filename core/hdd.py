import psutil
import time

def monitor_hdd():
    """Получает информацию о корневом разделе диска."""
    
    # Определяем корневой раздел
    root_partition = next((p for p in psutil.disk_partitions() if p.mountpoint == '/'), None)
        
    usage = psutil.disk_usage(root_partition.mountpoint)
    
    hdd_info = {
        "device": root_partition.device,
        "file_sys": root_partition.fstype,
        "size": round(usage.total / (1024.0 ** 3), 2),
        "used": round(usage.used / (1024.0 ** 3), 2),
        "free": round(usage.free / (1024 ** 3), 2),
        "percent": usage.percent,
    }
    
    return hdd_info

