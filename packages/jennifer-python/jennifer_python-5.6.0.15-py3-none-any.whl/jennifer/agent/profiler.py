import traceback
import datetime
from . import jennifer_agent
from jennifer.protocol import ProfileData, File, Socket, Message, Method, Root, sql, Error, ExternalCall
from jennifer.recorder.db import DBConnectionRecorder
import os

RUNNING_MODE_NONE = 0
RUNNING_SQL = 1
RUNNING_TXCALL = 2

STATUS_RUN = 20
STATUS_REJECTING = 21
STATUS_REJECTED = 22
STATUS_DB_CONNECTING = 50
STATUS_DB_CONNECTED = 51
STATUS_DB_STMT_OPEN = 52
STATUS_SQL_EXECUTING = 54
STATUS_SQL_EXECUTED = 55
STATUS_DB_CLOSED = 60
STATUS_TXCALL_EXECUTING = 70
STATUS_TXCALL_EXECUTED = 70
STATUS_TXCALL_END = 72


class TransactionProfiler(ProfileData):
    def __init__(self, transaction, service_hash):
        ProfileData.__init__(self, transaction.txid, service_hash, [])
        self.agent = jennifer_agent()
        self.root = Root(name_hash=self.agent.hash_text('wsgi_handler', 'method'))
        self.root.parent = None
        self.children.append(self.root)
        self.context = self.root
        self.root_start_time = self.agent.current_time()
        self.root_start_cpu = self.agent.current_cpu_time()
        self.last_index = 0
        self.running_mode = RUNNING_MODE_NONE
        self.running_hash = 0
        self.status = 0
        self.running_start_time = 0
        self.transaction = transaction
        self.db_recorder = DBConnectionRecorder()

    def end(self, **kwargs):
        self.record_elapsed(self.context)

        # input message case by case
        if isinstance(self.context, ExternalCall) and kwargs.get('message') is not None:
            self.running_mode = RUNNING_MODE_NONE
            self.running_hash = 0
            self.status = 0
            self.running_start_time = 0
            self.message(kwargs.get('message'))
        elif isinstance(self.context, sql.Query):
            self.running_mode = RUNNING_MODE_NONE
            self.running_hash = 0
            self.status = 0
            self.running_start_time = 0
            self.transaction.sql_count += 1
            self.transaction.sql_time += self.context.elapsed_time
        elif isinstance(self.context, sql.Fetch):
            self.transaction.fetch_count += 1
            self.transaction.fetch_time += self.context.elapsed_time
        if self.context.parent is not None:
            self.switch_context(self.context.parent)

    def set_root_name(self, name):
        self.root.name_hash = self.agent.hash_text(name, 'method')

    def method(self, name, error=None):
        method = Method(self.agent.hash_text(name, 'method'), self.agent.hash_text(error, 'method'))
        self.record_context(method)

    def external_call(self, protocol, url, host, port=80, caller=''):
        call_hash = self.agent.hash_text('%s (url=%s)' % (caller, url), 'txcall')

        tx = ExternalCall(
            protocol=protocol,
            host=host,
            port=port or 80,
            text_hash=call_hash
        )

        self.running_mode = RUNNING_TXCALL
        self.status = STATUS_TXCALL_EXECUTING
        self.running_hash = call_hash
        self.running_start_time = self.agent.current_time()
        self.record_context(tx)

    def db_open(self, host, port, db):
        msg = sql.Message(0, 'host={0};port={1};db={2}'.format(host, port, db), sql.Message.TYPE_OPEN)
        self.record_context(msg)

    @staticmethod
    def _process_sql_params(param):
        t = type(param)
        if t is datetime.datetime:
            param = param.strftime('%Y-%m-%d %H:%M:%S')
        elif t is datetime.date:
            param = param.strftime('%Y-%m-%d')
        return param

    @staticmethod
    def _debug_log(text):
        if os.getenv('PY_DBG'):
            try:
                log_socket = __import__('jennifer').get_log_socket()
                if log_socket is not None:
                    log_socket.log(text)
            except ImportError as e:
                print(e)

    def db_execute(self, host='', port=0, query='', params=[], style='format'):
        if type(params) is list:
            params = [TransactionProfiler._process_sql_params(x) for x in params]

        if type(params) is dict:
            params = {
                k: TransactionProfiler._process_sql_params(v) for (k, v) in params.items()
            }

        query_hash = self.agent.hash_text(query, 'sql')
        q = sql.Query(host=host, port=port, query=query, params=params, query_format=style)
        self.running_mode = RUNNING_SQL
        self.status = STATUS_SQL_EXECUTING
        self.running_hash = query_hash
        self.running_start_time = self.agent.current_time()
        self.record_context(q)

    def db_fetch(self, size=0):
        f = sql.Fetch(size)
        self.record_context(f)

    def message(self, text):
        msg = Message(text)
        self.record(msg)

    def file_opened(self, name, mode):
        file_msg = File(name, mode)
        self.record(file_msg)

    def socket_opened(self, host, port, local):
        socket = Socket(host, port, local)
        self.record(socket)

    def service_error(self, exc):
        self.exception(exc, Error.SERVICE_ERROR)

    def not_found(self, exc):
        self.exception(exc, Error.HTTP_404_ERROR)

    def db_connection_error(self, exc):
        self.exception(exc, Error.DB_CONNECTION_FAIL)

    def sql_error(self, exc):
        self.exception(exc, Error.SQL_EXCEPTION)

    def exception(self, exc, error_type=None):
        message = traceback.format_exception_only(exc.__class__, exc)

        if error_type is None:
            t = type(exc)

            if hasattr(__builtins__, 'RecursionError'):  # only support python3
                if t == RecursionError:
                    error_type = Error.RECURSIVE_CALL

            if t == MemoryError:
                error_type = Error.OUT_OF_MEMORY
            elif t == SyntaxError or t == IndentationError:
                error_type = Error.PARSE_ERROR
            elif t == SystemError or t == OSError:
                error_type = Error.NATIVE_CRITICAL_ERROR
            else:
                error_type = Error.SERVICE_EXCEPTION
        if message is not None:
            self.error(error_type, ''.join(message))

    def error(self, error_type, message):
        error_hash = self.agent.hash_text(message, 'event_detail_msg')
        error = Error(error_type, error_hash)
        self.transaction.error_code = error_type
        self.record(error)

    def record_context(self, context):
        self.children.append(context)
        self.record_index(context)
        context.parent = self.context
        self.switch_context(context)
        self.record_start(context)

    def record(self, profile):
        self.children.append(profile)
        self.record_index(profile)
        self.record_start(profile)

    def switch_context(self, profile):
        self.context = profile

    def record_start(self, profile):
        profile.start_time = self.gap_time()
        profile.start_cpu = self.gap_cpu_time()

    def record_index(self, profile):
        self.last_index += 1
        profile.index = self.last_index
        profile.parent_index = self.context.index

    def record_elapsed(self, profile):
        profile.elapsed_time = self.gap_time() - profile.start_time
        profile.elapsed_cpu = self.gap_time() - profile.start_cpu

    def gap_time(self):
        return self.agent.current_time() - self.root_start_time

    def gap_cpu_time(self):
        return self.agent.current_cpu_time() - self.root_start_cpu
