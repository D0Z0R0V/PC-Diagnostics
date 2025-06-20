import multiprocessing
import math
import random
import time
import signal
import sys

def load_cpu(stop_event):
    """Нагрузка CPU с проверкой события остановки"""
    while not stop_event.is_set():
        math.sin(random.random())
        math.cos(random.random())
        math.sqrt(random.random())

def handle_signal(signum, frame):
    sys.exit(0)

if __name__ == "__main__":
    signal.signal(signal.SIGTERM, handle_signal)
    signal.signal(signal.SIGINT, handle_signal)
    
    stop_event = multiprocessing.Event()
    processes = []
    
    for _ in range(multiprocessing.cpu_count()):
        p = multiprocessing.Process(target=load_cpu, args=(stop_event,))
        p.daemon = True
        p.start()
        processes.append(p)
    
    try:
        time.sleep(60)
    finally:
        stop_event.set()
        for p in processes:
            p.terminate()
            p.join(1)