from pynvml import *

def monitor_gpu():
    """Мониторинг всех доступных видеокарт."""
    nvmlInit()  # Инициализируем библиотеку NVML

    device_count = nvmlDeviceGetCount()  # Получаем количество GPU
    gpu_list = []  # Список для хранения данных о всех видеокартах

    for i in range(device_count):
        handle = nvmlDeviceGetHandleByIndex(i)
        gpu_name = nvmlDeviceGetName(handle)
        temperature = nvmlDeviceGetTemperature(handle, NVML_TEMPERATURE_GPU)
        clock_freq = nvmlDeviceGetClockInfo(handle, NVML_CLOCK_GRAPHICS)
        load = nvmlDeviceGetUtilizationRates(handle)

        gpu_info = {
            "gpu": gpu_name,
            "load": load.gpu,  # Нагрузка GPU в %
            "ram_load": load.memory,  # Нагрузка памяти в %
            "temperature": temperature,  # Температура в градусах
            "chip": clock_freq,  # Частота графического чипа в МГц
        }
        gpu_list.append(gpu_info)  # Добавляем данные в список

    nvmlShutdown()  # Завершаем работу с NVML
    return gpu_list  # Возвращаем список с информацией о всех видеокартах
