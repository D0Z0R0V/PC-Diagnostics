import random
import time
import signal
import sys

def stress_memory(size_mb=1024):
    """Нагрузка RAM с обработкой прерывания"""
    try:
        data = bytearray(size_mb * 1024 * 1024)
        while True:
            for i in range(len(data)):
                data[i] = random.randint(0, 255)
            time.sleep(0.1)
    except (KeyboardInterrupt, SystemExit):
        pass

def handle_signal(signum, frame):
    sys.exit(0)

if __name__ == "__main__":
    signal.signal(signal.SIGTERM, handle_signal)
    signal.signal(signal.SIGINT, handle_signal)
    stress_memory()