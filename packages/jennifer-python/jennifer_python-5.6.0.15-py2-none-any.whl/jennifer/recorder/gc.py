import gc
import time
import os


class GCRecorder(object):
    def __init__(self):
        if not hasattr(gc, 'callbacks'):
            self.support = False
            return

        self.support = True
        self.start_time = 0
        self.accumulate_time = 0
        self.gc_count = 0
        self.gen_time = [0, 0, 0]  # Python have 3 generation
        gc.callbacks.append(self.gc_callback)

    @staticmethod
    def _debug_log(text):
        if os.getenv('PY_DBG'):
            try:
                log_socket = __import__('jennifer').get_log_socket()
                if log_socket is not None:
                    log_socket.log(text)
            except ImportError as e:
                print(e)

    def record(self):
        if not self.support:
            return 0, 0, []

        gc_time = self.accumulate_time
        gc_count = self.gc_count
        gen_time = []

        for t in self.gen_time:
            gen_time.append(t)

        return gc_time, gc_count, gen_time

    def gc_callback(self, phase, info):

        if phase == 'start':
            self.start_time = time.time()
        else:  # phase end
            delta = int((time.time() - self.start_time) * 1000)
            self.accumulate_time += delta

            self.gc_count += info['collected']
            self.gen_time[info['generation']] = delta

    def __del__(self):
        if not self.support:
            return
        if self.gc_callback in gc.callbacks:
            gc.callbacks.remove(self.gc_callback)
