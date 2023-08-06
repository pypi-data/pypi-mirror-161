# -*- coding: utf8 -*-

import os
import subprocess
import sys
import tempfile
from configparser import ConfigParser
import time
import platform
import pathlib
import socket
import struct
from threading import Thread, Timer

try:  # for Python 2.7
    FileNotFoundError
except NameError:
    FileNotFoundError = IOError


def print_help():
    print("""
Usage: jennifer-admin run <startup_command ...>
Usage: jennifer-admin runasync <startup_command ...>

startup_command: your wsgi/asgi service startup command and options
""")


def run_master(bin_path, config_path, log_path, sock_file):
    arch = {
        'x86_64': 'amd64',
        'x86': '386',
        'arm64': 'arm64',
    }[platform.machine()]

    platform_id = sys.platform
    if platform_id == "linux2":
        platform_id = "linux"

    path = os.path.join(bin_path, platform_id, arch, 'jennifer_agent')
    log_stream = open(log_path, 'w+')  # log_path == '/tmp/jennifer-python-agent.log'

    process = subprocess.Popen(
        [
            path,  # '/mnt/d/.../jennifer/bin/linux/amd64/jennifer_agent'
            config_path,  # '/mnt/d/.../myapp/jennifer.ini'
            sock_file,  # '/tmp/jennifer-1629185873.sock'
        ],
        stdout=log_stream,
        stderr=log_stream,
    )
    return process.pid


def run(args, is_sync=False):
    if len(args) < 2:
        print_help()
        return

    wsgi_startup_app_path = args[1]
    config_path = os.environ.get('JENNIFER_CONFIG_FILE')
    if config_path is None:
        raise EnvironmentError("JENNIFER_CONFIG_FILE is not set")

    config_path = os.path.join(os.getcwd(), config_path)
    if not os.path.exists(config_path):
        raise FileNotFoundError(config_path + " not exists")

    try:
        jennifer_file_path = __import__('jennifer').__file__
        # print('jennifer_file_path:', jennifer_file_path) # /mnt/d/.../jennifer/__init__.py
    # except ImportError as e:
        # raise e
    except ImportError as e:
        jennifer_file_path = pathlib.Path(__file__).parent.absolute().as_posix()

    root_dir = os.path.dirname(jennifer_file_path)
    bootstrap = os.path.join(root_dir, 'bootstrap')
    # print('jennifer_boot_path', bootstrap) # /mnt/d/.../jennifer/bootstrap

    # 제니퍼 에이전트의 /jennifer/bootstrap 모듈 경로를 "PYTHONPATH"에 추가
    # 왜냐하면, 이후 fork 시 uwsgi/gunicorn 모듈에서 jennifer 모듈을 발견할 수 있어야 하므로!
    python_path = bootstrap
    if 'PYTHONPATH' in os.environ:
        path = os.environ['PYTHONPATH'].split(os.path.pathsep)
        if bootstrap not in path:
            python_path = os.path.pathsep.join([bootstrap] + path)
    os.environ['PYTHONPATH'] = python_path

    # uwsgi 또는 gunicorn 등의 실행 파일이 위치한 full path
    if not os.path.dirname(wsgi_startup_app_path):
        for path in os.environ.get('PATH', '').split(os.path.pathsep):
            path = os.path.join(path, wsgi_startup_app_path)
            if os.path.exists(path) and os.access(path, os.X_OK):
                wsgi_startup_app_path = path
                break

    if not os.path.exists(wsgi_startup_app_path):
        raise FileNotFoundError('{0} not found'.format(wsgi_startup_app_path))

    time_prefix = time.time()
    if (int(os.getenv('PY_DBG') or '0') & 0x02) == 0x02:
        time_prefix = 0

    sock = os.path.join(tempfile.gettempdir(), 'jennifer-%d.sock' % time_prefix)
    os.environ['JENNIFER_MASTER_ADDRESS'] = sock

    config = ConfigParser()
    config.read(config_path)

    log_path = config['JENNIFER'].get('log_path', '/tmp/jennifer-python-agent.log')
    os.environ['JENNIFER_LOG_PATH'] = log_path

    if is_sync:
        os.environ['JENNIFER_IS_ASYNC'] = str(is_sync)

    # try:
    #     proxy_pid = run_master(os.path.join(root_dir, 'bin'), config_path, log_path, sock)
    #     # os.waitpid(proxy_pid, 0)
    # except(EnvironmentError, FileNotFoundError) as e:
    #     pass
    #
    # consoleLogger.log("process", pid, "from", os.getpid())
    # os.execl(wsgi_startup_path, *args[1:])

    pid = os.fork()
    if pid > 0:  # parent process
        os.waitpid(pid, 0)  # run_master 함수가 반환될 때까지 대기
        os.execl(wsgi_startup_app_path, *args[1:])
    else:  # child process - 최초 jennifer-admin run uwsgi... 실행 시 진입
        if time_prefix != 0:
            run_master(os.path.join(root_dir, 'bin'), config_path, log_path, sock)


if __name__ == '__main__':
    run(sys.argv[1:])
    exit(-1)

