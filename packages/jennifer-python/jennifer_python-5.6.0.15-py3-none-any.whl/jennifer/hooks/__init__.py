# -*- coding: utf-8 -*-

import os

import platform
from distutils.version import LooseVersion
__current_python_ver__ = LooseVersion(platform.python_version())
__hooked_module__ = []
python36_version = LooseVersion("3.6")

from jennifer.agent import jennifer_agent

from . import app_flask
from . import db_sqlite3
from . import app_django
from . import db_mysqlclient
from . import db_pymysql
from . import external_requests
from . import external_urllib
from . import external_urllib2
from . import external_urllib3
from . import db_pymongo
from . import db_redis
from . import db_cx_oracle
from . import db_psycopg2

HOOK_SUPPORT_LIST = [
    app_flask,
    app_django,
    db_mysqlclient,
    db_pymysql,
    db_sqlite3,
    db_pymongo,
    db_psycopg2,
    db_cx_oracle,
    db_redis,
    external_urllib,
    external_urllib2,
    external_urllib3,
    external_requests,
]

if python36_version <= __current_python_ver__:
    from . import app_fastapi
    HOOK_SUPPORT_LIST.append(app_fastapi)

    from . import mod_asyncio
    HOOK_SUPPORT_LIST.append(mod_asyncio)


def _is_module_exist(module):
    try:
        return __import__(module)
    except ImportError:
        return False


def hooking():
    hooked_module = []

    for m in HOOK_SUPPORT_LIST:
        try:
            module = _is_module_exist(m.__hooking_module__)

            if __current_python_ver__ < m.__minimum_python_version__:
                continue

            if module is not False:
                m.hook(module)
                hooked_module.append(m.__hooking_module__)
        except Exception as e:
            print("jennifer.exception", "hooking", e)

    global __hooked_module__
    __hooked_module__ = hooked_module
    _hook_builtins()


# Socket Open/Connect 가로채기
def _hook_builtins():
    try:
        import socket
        __builtins__['open'] = _wrap_file_open(__builtins__['open'])
        socket.socket.connect = _wrap_socket_connect(socket.socket.connect)
        socket.socket.connect_ex = _wrap_socket_connect(socket.socket.connect_ex)
    except Exception as e:
        print("jennifer.exception", "_hook_builtins", e)


def _wrap_file_open(origin_open):
    agent = jennifer_agent()

    def _handler(file_path, mode='r', *args, **kwargs):
        try:
            transaction = agent.current_transaction()

            if transaction is not None and 'site-packages' not in file_path:
                transaction.profiler.file_opened(
                    name=os.path.abspath(os.path.join(os.getcwd(), file_path)),
                    mode=mode
                )
        except:
            pass

        return origin_open(file_path, mode, *args, **kwargs)

    return _handler


def _wrap_socket_connect(origin_connect):
    import socket
    agent = jennifer_agent()

    def _handler(self, address):
        transaction = agent.current_transaction()

        ret = origin_connect(self, address)

        if self.family != socket.AF_INET:
            return ret

        if transaction is not None:
            remote_address = self.getpeername()
            local_address = self.getsockname()
            transaction.profiler.socket_opened(
                host=remote_address[0],
                port=remote_address[1],
                local=local_address[1],
            )
        return ret

    return _handler


def _debug_log(text):
    if os.getenv('PY_DBG'):
        try:
            log_socket = __import__('jennifer').get_log_socket()
            if log_socket is not None:
                log_socket.log(text)
        except ImportError as e:
            print(e)