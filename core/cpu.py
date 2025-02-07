import psutil

def get_cpu_info():
    """Собирает информацию о процессоре и возвращает её в виде словаря."""
    if not hasattr(psutil, "sensors_temperatures"):
        return {"error": "Нет поддержки датчиков температуры"}

    temp = psutil.sensors_temperatures()
    cpu_usage = psutil.cpu_percent(interval=0.0)
    logical_cpus = psutil.cpu_count(logical=True)
    physical_cpus = psutil.cpu_count(logical=False)
    cpu_freq = psutil.cpu_freq()
    
    if not temp:
        return {"error": "Нет данных о температуре"}

    cpu_info = {
        "usage": cpu_usage,
        "cores": physical_cpus,
        "threads": logical_cpus,
        "freq_current": round(cpu_freq.current, 1),
        "freq_min": cpu_freq.min,
        "freq_max": cpu_freq.max,
        "temperatures": {},
        "cpu_times": [],
    }

    for name, entries in temp.items():
        cpu_info["temperatures"][name] = [
            {
                "label": entry.label or name,
                "current": entry.current,
                "high": entry.high,
                "critical": entry.critical,
            }
            for entry in entries
        ]

    cpu_times = psutil.cpu_times(percpu=True)
    for times in cpu_times:
        cpu_info["cpu_times"].append(
            {"user": times.user, "system": times.system, "idle": times.idle}
        )

    return cpu_info
