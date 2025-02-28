import random

def stress_memory(size_mb):
    # Выделение памяти
    data = bytearray(size_mb * 1024 * 1024)
    
    # Заполнение случайными данными
    for i in range(len(data)):
        data[i] = random.randint(0, 255)
    
    # Проверка целостности данных
    for i in range(len(data)):
        if data[i] != random.randint(0, 255):
            print("Ошибка в памяти!")
            return
    
    print("Тест памяти завершен без ошибок.")

# Вызов функции
stress_memory(1024)
