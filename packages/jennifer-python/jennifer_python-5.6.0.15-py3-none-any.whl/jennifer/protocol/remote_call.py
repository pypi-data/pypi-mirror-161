TYPE_NONE = 0
TYPE_CUSTOM = 11
TYPE_HTTP = 12
TYPE_HTTPS = 18
TYPE_UNKNOWN_SQL_DATABASE = 21
TYPE_ORACLE = 22
TYPE_DB2 = 23
TYPE_MYSQL = 24
TYPE_POSTGRESQL = 25
TYPE_CUBRID = 26
TYPE_MSSQL = 27
TYPE_SOAP = 32


class OutRemoteCall:
    def __init__(self, call_type=TYPE_NONE, host='', port=0, request_hash=0, recv_sid=0, recv_oid=0, desc_hash=0):
        self.call_type = call_type
        self.host = host
        self.port = port
        self.request_hash = request_hash
        self.recv_sid = recv_sid
        self.recv_oid = recv_oid
        self.desc_hash = desc_hash
