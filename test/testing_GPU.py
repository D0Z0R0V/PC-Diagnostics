import time
import signal
import sys

def stress_gpu():
    try:
        import pyopencl as cl
        ctx = cl.create_some_context()
        queue = cl.CommandQueue(ctx)
        
        # Простое ядро для нагрузки
        prg = cl.Program(ctx, """
        __kernel void test(__global float *a) {
            int i = get_global_id(0);
            a[i] = a[i] * a[i];
        }
        """).build()
        
        import numpy as np
        a = np.random.rand(100000).astype(np.float32)
        a_buf = cl.Buffer(ctx, cl.mem_flags.READ_WRITE, size=a.nbytes)
        
        for _ in range(1000):
            cl.enqueue_copy(queue, a_buf, a)
            prg.test(queue, a.shape, None, a_buf)
            cl.enqueue_copy(queue, a, a_buf)
            
    except ImportError:
        print("pyopencl не установлен")
        while True:
            time.sleep(1)

def handle_signal(signum, frame):
    sys.exit(0)

if __name__ == "__main__":
    signal.signal(signal.SIGTERM, handle_signal)
    signal.signal(signal.SIGINT, handle_signal)
    stress_gpu()