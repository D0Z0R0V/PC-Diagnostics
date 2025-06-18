import multiprocessing
import math
import random
import time
import signal
import sys

def load_cpu(stop_event):
    while not stop_event.is_set():
        math.sin(random.random())
        math.cos(random.random())
        math.sqrt(random.random())

def stress_memory(stop_event, size_mb=1024):
    try:
        data = bytearray(size_mb * 1024 * 1024)
        while not stop_event.is_set():
            for i in range(len(data)):
                data[i] = random.randint(0, 255)
            time.sleep(0.1)
    except:
        pass

def handle_signal(signum, frame):
    sys.exit(0)

if __name__ == "__main__":
    signal.signal(signal.SIGTERM, handle_signal)
    signal.signal(signal.SIGINT, handle_signal)
    
    stop_event = multiprocessing.Event()
    
    # CPU тест
    cpu_processes = []
    for _ in range(multiprocessing.cpu_count()):
        p = multiprocessing.Process(target=load_cpu, args=(stop_event,))
        p.daemon = True
        p.start()
        cpu_processes.append(p)
    
    # RAM тест
    ram_process = multiprocessing.Process(target=stress_memory, args=(stop_event,))
    ram_process.daemon = True
    ram_process.start()
    
    try:
        time.sleep(60)
    finally:
        stop_event.set()
        for p in cpu_processes:
            p.terminate()
        ram_process.terminate()