import os
import time

pid = os.getpid()


def log(*args):
    current_time = time.localtime(time.time())
    time_prefix = time.strftime('%Y/%m/%d %H:%M:%S', current_time)
    print(pid, time_prefix, *args)

