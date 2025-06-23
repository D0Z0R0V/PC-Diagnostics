import multiprocessing
import math
import random
import time
import signal
import sys
from datetime import datetime

def load_cpu(stop_event, process_num):
    start_time = time.time()
    duration = 60  # Default
    while not stop_event.is_set():
        math.sin(random.random())
        math.cos(random.random())
        math.sqrt(random.random())
        if time.time() - start_time > 1:
            progress = int((time.time() - start_time) / duration * 100)
            print(f"CPU_PROGRESS:{progress}%")
            start_time = time.time()

def stress_memory(stop_event, size_mb=1024):
    start_time = time.time()
    duration = 60
    try:
        data = bytearray(size_mb * 1024 * 1024)
        while not stop_event.is_set():
            for i in range(0, len(data), 4096):
                data[i] = random.randint(0, 255)
            if time.time() - start_time > 1:
                progress = int((time.time() - start_time) / duration * 100)
                print(f"MEM_PROGRESS:{progress}%")
                start_time = time.time()
    except Exception as e:
        print(f"MEM_ERROR:{str(e)}")

def handle_signal(signum, frame):
    print("PROGRESS:100%")
    sys.exit(0)

if __name__ == "__main__":
    signal.signal(signal.SIGTERM, handle_signal)
    signal.signal(signal.SIGINT, handle_signal)
    
    duration = int(sys.argv[1]) if len(sys.argv) > 1 else 60
    stop_event = multiprocessing.Event()
    
    # CPU тест
    cpu_processes = []
    for i in range(multiprocessing.cpu_count()):
        p = multiprocessing.Process(target=load_cpu, args=(stop_event, i))
        p.daemon = True
        p.start()
        cpu_processes.append(p)
    
    # RAM тест
    ram_process = multiprocessing.Process(target=stress_memory, args=(stop_event,))
    ram_process.daemon = True
    ram_process.start()
    
    try:
        time.sleep(duration)
    finally:
        stop_event.set()
        for p in cpu_processes:
            p.terminate()
        ram_process.terminate()
        print("PROGRESS:100%")