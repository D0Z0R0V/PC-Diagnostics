import multiprocessing
import math
import random
import time
import signal
import sys
from datetime import datetime

def load_cpu(stop_event, process_num):
    start_time = time.time()
    duration = 60  # Default, will be overridden by stop_event
    while not stop_event.is_set():
        math.sin(random.random())
        math.cos(random.random())
        math.sqrt(random.random())
        if time.time() - start_time > 1:  # Report progress every second
            progress = int((time.time() - start_time) / duration * 100)
            print(f"PROGRESS:{progress}%")
            start_time = time.time()

def handle_signal(signum, frame):
    print("PROGRESS:100%")
    sys.exit(0)

if __name__ == "__main__":
    signal.signal(signal.SIGTERM, handle_signal)
    signal.signal(signal.SIGINT, handle_signal)
    
    duration = int(sys.argv[1]) if len(sys.argv) > 1 else 60
    stop_event = multiprocessing.Event()
    processes = []
    
    for i in range(multiprocessing.cpu_count()):
        p = multiprocessing.Process(target=load_cpu, args=(stop_event, i))
        p.daemon = True
        p.start()
        processes.append(p)
    
    try:
        time.sleep(duration)
    finally:
        stop_event.set()
        for p in processes:
            p.terminate()
            p.join(1)
        print("PROGRESS:100%")