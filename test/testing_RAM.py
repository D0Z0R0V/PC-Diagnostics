import random
import time
import signal
import sys
from datetime import datetime

def stress_memory(duration=60, size_mb=1024):
    start_time = time.time()
    try:
        data = bytearray(size_mb * 1024 * 1024)
        while time.time() - start_time < duration:
            for i in range(0, len(data), 4096):  # Изменяем каждую 4K страницу
                data[i] = random.randint(0, 255)
            progress = int(((time.time() - start_time) / duration) * 100)
            print(f"PROGRESS:{progress}%")
            time.sleep(0.5)
    except Exception as e:
        print(f"ERROR:{str(e)}")
    print("PROGRESS:100%")

def handle_signal(signum, frame):
    print("PROGRESS:100%")
    sys.exit(0)

if __name__ == "__main__":
    signal.signal(signal.SIGTERM, handle_signal)
    signal.signal(signal.SIGINT, handle_signal)
    duration = int(sys.argv[1]) if len(sys.argv) > 1 else 60
    stress_memory(duration)