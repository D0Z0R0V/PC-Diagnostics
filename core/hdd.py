import psutil

def monitor_hdd():
    """Получает информацию о корневом разделе диска."""
    try:
        root_partition = next((p for p in psutil.disk_partitions() if p.mountpoint == '/'), None)
        if not root_partition:
            return None
            
        usage = psutil.disk_usage(root_partition.mountpoint)
        
        return {
            "device": root_partition.device,
            "mountpoint": root_partition.mountpoint,
            "file_sys": root_partition.fstype,
            "size": round(usage.total / (1024.0 ** 3), 2),
            "used": round(usage.used / (1024.0 ** 3), 2),
            "free": round(usage.free / (1024 ** 3), 2),
            "percent": usage.percent,
        }
    except Exception as e:
        print(f"Ошибка при получении информации о диске: {e}")
        return None