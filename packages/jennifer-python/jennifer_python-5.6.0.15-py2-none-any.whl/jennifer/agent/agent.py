# -*- coding: utf8 -*-

import threading
import logging
import json
import os
import platform
import sys
import zlib
import traceback
from jennifer.recorder import Recorder
from jennifer.api import task
import socket
import struct
import time
from random import random
from .transaction import Transaction

record_types = {
    'method': 1,
    'sql': 2,
    'event_detail_msg': 3,
    'service': 4,
    'txcall': 5,
    'browser_info': 6,
    'thread_name': 7,
    'thread_stack': 8,
    'user_id': 9,
    'dbc': 10,
    'stack_trace': 11,
    'count': 12,
}


class Agent(object):
    def __init__(self, get_ctx_id_func):
        self.transactions = []
        self.inst_id = -1
        self.recorder = None
        self.master_lock = threading.Lock()
        self.logger = logging.getLogger('jennifer')
        self.config_pid = 0
        self.address = ''
        self.masterConnection = None
        self.get_ctx_id_func = get_ctx_id_func

        # uwsgi 호스팅인 경우 --enable-threads 옵션이 지정되지 않은 상황이라면,
        # run_timer 등의 스레드 관련 기능이 동작하지 않으므로 사후 처리를 해야 함. (TODO: 아직 미구현)
        self.thread_enabled = False

    def set_context_id_func(self, func):
        self.get_ctx_id_func = func

    @staticmethod
    def gen_new_txid():
        return int(str(int(random() * 100)) + str(Agent.current_time()))

    @staticmethod
    def log_ex(text):
        import jennifer
        jennifer.agent.log_ex(text)

    @staticmethod
    def current_cpu_time():
        if hasattr(time, 'process_time'):
            return int(time.process_time() * 1000)
        return int(time.clock() * 1000)

    def current_transaction(self):
        ret = None
        ctx_id = self.get_ctx_id_func()
        for t in self.transactions:
            if t.thread_id == ctx_id:
                ret = t
                break
        return ret

    # config.address == /tmp/jennifer-...sock
    # config.log_path == /tmp/jennifer-python-agent.log
    def set_config(self, config):
        self.address = config['address']
        self.recorder = Recorder()
        self.config_pid = os.getpid()

        ret = None
        with self.master_lock:
            ret = self.connect_master()

        if ret:
            task.run_timer(self.process_agent_metric)

    @staticmethod
    def _debug_log(text):
        if os.getenv('PY_DBG'):
            try:
                log_socket = __import__('jennifer').get_log_socket()
                if log_socket is not None:
                    log_socket.log(text)
            except ImportError as e:
                print(e)

    def connect_master(self):
        self.masterConnection = None

        if not os.path.exists(self.address):
            return False

        try:
            self.masterConnection = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            self.masterConnection.connect(self.address)

            self.handshake_to_master()
            task.run_task(self.master_loop)
            return True
        except Exception as e:
            self.masterConnection = None
            return False

    def handshake_to_master(self):
        try:
            import jennifer
            agent_version = jennifer.__version__
            data = '{"app_dir": "' + os.getcwd() + '", "protocol_version":2,"agent_version":"' + agent_version\
                   + '","pid":' + str(os.getpid()) + '}'

            version = data.encode('utf-8')
            self.masterConnection.send(b'\x08jennifer' + struct.pack('>L', len(version)) + version)
        except:
            jennifer.agent.log_ex('handshake')

    def master_loop(self):

        while True:
            if self.masterConnection is None:
                break

            try:
                byte_cmd_len = self.masterConnection.recv(1)
                if len(byte_cmd_len) < 1:
                    break  # failed to connect master

                cmd_len = ord(byte_cmd_len)
                cmd = self.masterConnection.recv(cmd_len)
                param_len, = struct.unpack('>L', self.masterConnection.recv(4))
                try:
                    param = json.loads(self.masterConnection.recv(param_len))
                except:
                    continue

                if cmd == b'connected':
                    try:
                        print('---------------- [App Initialized] ----------------------')
                        print('MachineName = ', socket.gethostname())
                        print('Is64BitProcess = ', platform.architecture())
                        print('Python Version = ', platform.python_version())
                        print('Jennifer Python Agent Install Path = ', os.path.dirname(os.path.dirname(__file__)))
                        print('Jennifer Server Address = ', param.get('server_address'))
                        print('Jennifer Python Agent Domain ID = ', param.get('domain_id'))
                        print('Jennifer Python Agent Inst ID = ', param.get('inst_id'))
                        print('Jennifer Python Agent Pid = ', os.getpid())
                        print('---------------------------------------------------------')
                    except:
                        pass
                    continue

                if cmd == b'active_detail':
                    txid = param.get('txid')
                    request_id = param.get('request_id')
                    if txid is not None and request_id is not None:
                        data = self.get_active_service_detail(txid)
                        if data is not None:
                            data['request_id'] = request_id
                            self.send_to_master('active_detail', data)
                    continue

                if cmd == b'agentcheck_env':
                    request_id = param.get('request_id')
                    if request_id is None:
                        continue

                    data = Agent.get_environment_variables()
                    if data is not None:
                        import jennifer.hooks
                        data['jennifer.request_id'] = str(request_id)
                        data['jennifer.hooked'] = str(jennifer.hooks.__hooked_module__)
                        self.send_to_master('agentcheck_env', data)
                    continue

            except (BrokenPipeError, OSError):
                break

    @staticmethod
    def get_environment_variables():
        ret = {}
        for name, value in os.environ.items():
            ret[name] = value

        return ret

    def get_active_service_detail(self, txid):
        ret = None
        cpu_time = self.current_cpu_time()
        current_time = self.current_time()

        for t in self.transactions:
            if t.txid == txid:
                stack = 'Fail to get a callstack'
                frame = sys._current_frames().get(t.thread_id)
                if frame is not None:
                    stack = ''.join(traceback.format_stack(frame))
                ret = {
                    'txid': t.txid,
                    'thread_id': t.thread_id,
                    'service_name': t.path_info,
                    'elapsed': current_time - t.start_time,
                    'method': t.request_method,
                    'http_query': t.query_string,
                    'sql_count': t.sql_count,
                    'sql_time': t.sql_time,
                    'tx_time': t.external_call_time,
                    'tx_count': t.external_call_count,
                    'fetch_count': t.fetch_count,
                    'cpu_time': cpu_time - t.start_system_time,
                    'start_time': t.start_time,
                    'stack': stack,
                }

        return ret

    def process_agent_metric(self):
        metrics = self.recorder.record_self()
        self.send_to_master('record_metric', metrics)

        current = Agent.current_time()
        current_cpu = Agent.current_cpu_time()

        self.send_to_master('active_service_list', {
            'active_services': [
                t.to_active_service_dict(current, current_cpu)
                for t in self.transactions
            ],
        })

    def send_to_master(self, cmd, params):
        if os.getpid() != self.config_pid:
            self.set_config({
                'address': self.address
            })

        try:
            p = json.dumps(params, default=str).encode('utf-8')

            pack = struct.pack('>B', len(cmd)) + cmd.encode('utf-8') + struct.pack('>L', len(p)) + p
            with self.master_lock:
                if self.masterConnection is None:
                    if not self.connect_master():
                        return
                self.masterConnection.send(pack)

        except socket.error as e:  # except (BrokenPipeError, OSError):  # 3.x only

            import errno
            if e.errno != errno.EPIPE:  # 2.7 backward compatibility
                print(e)
            self.masterConnection = None

    @staticmethod
    def current_time():
        return int(time.time() * 1000)

    @staticmethod
    def current_cpu_time():
        if hasattr(time, 'process_time'):
            return int(time.process_time() * 1000)
        return int(time.clock() * 1000)

    def start_transaction(self, environ, wmonid, start_time=None, path_info=None):
        if start_time is None:
            start_time = Agent.current_time()
        txid = Agent.gen_new_txid()
        transaction = Transaction(
            agent=self,
            start_time=start_time,
            txid=txid,
            environ=environ,
            wmonid=wmonid,
            ctx_id=self.get_ctx_id_func(),
            path_info=path_info,
        )
        self.transactions.append(transaction)
        transaction.start_system_time = Agent.current_cpu_time()

        self.send_to_master('start_transaction', {})
        return transaction

    def end_transaction(self, transaction):
        try:
            self.transactions.remove(transaction)

            self.send_to_master('end_transaction', {
                'transaction': transaction.to_dict(),
                'profiler': transaction.profiler.to_dict(),
            })

            # uwsgi 환경의 --enable-threads 옵션이,
            #  없는 경우를 위한 처리 추가
            #  있는 경우 어차피 run_timer 내에서 처리
            if len(self.transactions) == 0:
                self.process_agent_metric()

        except Exception as e:
            print('[jennifer]', 'exception', e)

    @staticmethod
    def _hash_text(text):
        hash_key = zlib.crc32(text.encode('utf-8'))
        if hash_key > 0x7FFFFFFF:
            return (hash_key & 0x7FFFFFFF) * -1
        return hash_key

    def hash_text(self, text, hash_type='service'):
        if text is None or len(text) == 0:
            return 0

        text_hash_code = self._hash_text(text)

        self.send_to_master('record_text', {
            'type': record_types.get(hash_type, 0),
            'text': text,
            'text_hash': text_hash_code,
        })

        return text_hash_code
