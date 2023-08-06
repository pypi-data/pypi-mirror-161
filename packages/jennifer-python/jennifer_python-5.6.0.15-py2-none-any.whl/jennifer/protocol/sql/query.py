from .. import remote_call
from ..profile_data import ProfileDataType


class Query(ProfileDataType):
    TYPE_DB_UNKNOWN = remote_call.TYPE_UNKNOWN_SQL_DATABASE
    TYPE_DB_ORACLE = remote_call.TYPE_ORACLE
    TYPE_DB_DB2 = remote_call.TYPE_DB2
    TYPE_DB_MYSQL = remote_call.TYPE_MYSQL
    TYPE_DB_POSTGRESQL = remote_call.TYPE_POSTGRESQL
    TYPE_DB_CUBRID = remote_call.TYPE_CUBRID
    TYPE_DB_MSSQL = remote_call.TYPE_MSSQL
    TYPE_DB_SOAP = remote_call.TYPE_SOAP

    TYPE_SQL_PSTMT_QUERY = 5
    TYPE_SQL_QUERY = 11
    TYPE_SQL_EXECUTE = 12

    def __init__(self, host='', port=0, db=TYPE_DB_UNKNOWN, method=TYPE_SQL_QUERY, error_hash=0,
                 query='', params=[], query_format='format'):
        ProfileDataType.__init__(self)
        self.error_hash = error_hash
        self.db = db
        self.host = host
        self.port = port
        self.method = method
        self.params = params
        self.query = query
        self.query_format = format

    def get_type(self):
        return ProfileDataType.TYPE_SQL_EXEC
