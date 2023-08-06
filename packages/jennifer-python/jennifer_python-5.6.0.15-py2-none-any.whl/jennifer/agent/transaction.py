from random import random
from jennifer.agent import jennifer_agent
from .profiler import TransactionProfiler


class Transaction:
    def __init__(self, agent, start_time, environ, wmonid,
                 txid=0, elapsed=0, elapsed_cpu=0, end_time=0, sql_count=0, sql_time=0, fetch_count=0,
                 fetch_time=0, external_call_count=0, external_call_time=0, client_address=None,
                 user_hash=0, service_hash=0, guid=None, browser_info_hash=0, error_code=0, ctx_id=0, path_info=None):

        self.elapsed = elapsed
        self.elapsed_cpu = elapsed_cpu
        self.end_time = end_time
        self.sql_count = sql_count
        self.sql_time = sql_time
        self.fetch_count = fetch_count
        self.fetch_time = fetch_time
        self.external_call_count = external_call_count
        self.external_call_time = external_call_time
        self.txid = txid
        self.client_address = client_address
        self.wmonid = wmonid
        self.user_hash = user_hash
        self.guid = guid
        self.browser_info_hash = browser_info_hash
        self.error_code = error_code
        self.service_hash = service_hash
        self.incoming_remote_call = None

        self.agent = agent
        self.start_system_time = 0
        self.end_system_time = 0
        self.wmonid = wmonid
        self.thread_id = ctx_id  # in async, thread_id == ctx_id
                                 # in sync, thread_id == thread id

        if environ.get('HTTP_X_FORWARDED_FOR') is not None:
            self.client_address = environ.get('HTTP_X_FORWARDED_FOR')
        elif environ.get('HTTP_CLIENT_IP') is not None:
            self.client_address = environ.get('HTTP_CLIENT_IP')
        else:
            self.client_address = environ.get('REMOTE_ADDR', '')

        self.browser_info_hash = self.agent.hash_text(environ.get('HTTP_USER_AGENT', ''), 'browser_info')

        if path_info is None:
            path_info = environ.get('PATH_INFO', '').encode('iso-8859-1').decode('utf-8')

        self.request_method = environ.get('REQUEST_METHOD', '')
        self.query_string = environ.get('QUERY_STRING', '')
        self.start_time = start_time
        self.path_info = path_info
        self.service_hash = self.agent.hash_text(path_info)
        self.profiler = TransactionProfiler(self, self.service_hash)

    def end_of_profile(self, end_time=None):
        self.profiler.end()  # end root method
        self.end_system_time = self.agent.current_cpu_time()
        self.end_time = end_time
        if self.end_time is None:
            self.end_time = self.agent.current_time()
        self.agent.end_transaction(self)

    def to_active_service_dict(self, current_time, current_cpu_time):
        self.elapsed_cpu = int(current_cpu_time - self.start_system_time)
        self.elapsed = int(current_time - self.start_time)
        data = {key: getattr(self, key) for key in [
            'service_hash',
            'elapsed',
            'txid',
            'wmonid',
            'thread_id',
            'client_address',
            'elapsed_cpu',
            'sql_count',
            'fetch_count',
            'start_time',
        ]}

        data['running_mode'] = self.profiler.running_mode
        data['running_hash'] = self.profiler.running_hash
        data['running_time'] = current_time - self.profiler.running_start_time
        data['status_code'] = self.profiler.status

        return data

    def to_dict(self):
        self.elapsed_cpu = int(self.end_system_time - self.start_system_time)
        self.elapsed = int(self.end_time - self.start_time)
        data = {key: getattr(self, key) for key in [
            'elapsed',
            'elapsed_cpu',
            'end_time',
            'sql_count',
            'sql_time',
            'fetch_count',
            'fetch_time',
            'external_call_count',
            'external_call_time',
            'txid',
            'client_address',
            'wmonid',
            'user_hash',
            'guid',
            'browser_info_hash',
            'error_code',
            'service_hash',
            'start_system_time',
            'end_system_time',
            'thread_id',
            'start_time',
        ]}

        return data
