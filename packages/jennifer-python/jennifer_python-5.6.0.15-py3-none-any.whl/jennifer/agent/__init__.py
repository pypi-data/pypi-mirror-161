import threading
import os
from datetime import datetime
import traceback
from distutils.version import LooseVersion
import platform

cached_agent = None
fastapi_ctx = None

is_async = False

__current_python_ver__ = LooseVersion(platform.python_version())
python38_version = LooseVersion("3.8")

if os.getenv('JENNIFER_IS_ASYNC') is not None:
    is_async = bool(os.environ['JENNIFER_IS_ASYNC'])


def jennifer_agent():
    global cached_agent

    if cached_agent is None:
        from .agent import Agent

        if is_async:
            cached_agent = Agent(_get_temp_id)
        else:
            if python38_version <= __current_python_ver__:
                cached_agent = Agent(_current_thread_id38)
            else:
                cached_agent = Agent(_current_thread_id)

    return cached_agent


def _current_thread_id():
    return threading.current_thread().ident & 0xFFFFFFFF  # with python 2.7 and 3.x


def _current_thread_id38():  # python 3.8 or later
    return threading.get_native_id()


def _get_temp_id():
    return 0


def log_ex(text=None):
    current_time = format_time(datetime.now())
    if text is None:
        print(current_time, "jennifer", "error")
    else:
        print(current_time, "jennifer", "error", text)
    traceback.print_exc()


def log(text):
    current_time = format_time(datetime.now())
    print(current_time, "jennifer", "info", text)


def format_time(time_value):
    return time_value.strftime("%Y%m%d-%H%M%S")
