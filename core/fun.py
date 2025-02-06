import psutil, time

def monitor_fun():
    fans = psutil.sensors_fans()

    if fans:
        for name, entries in fans.items():
            print(name)
            for entry in entries:
                print(f"  - {entry.label}: {entry.current} RPM")
    else:
        print("Не удалось получить данные о вентиляторах.")

while True:
    monitor_fun()
    time.sleep(1)