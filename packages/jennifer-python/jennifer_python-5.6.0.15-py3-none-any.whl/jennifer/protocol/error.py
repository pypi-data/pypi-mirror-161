from .profile_data import ProfileDataType


class Error(ProfileDataType):
    UNDEFINED = 0
    SERVICE_EXCEPTION = 1001
    OUT_OF_MEMORY = 1003
    DB_CONNECTION_UNCLOSED = 1004
    DB_STATEMENT_UNCLOSED = 1005
    DB_RESULTSET_UNCLOSED = 1006
    HTTP_IO_EXCEPTION = 1007
    SERVICE_ERROR = 1008
    PLC_REJECTED = 1009
    DEADLOCK = 1011
    METHOD_EXCEPTION = 1012
    SQL_TOO_MANY_FETCH = 1013
    EXTERNAL_CALL_EXCEPTION = 1014
    DB_CONNECTION_FAIL = 1015
    DB_TRANSACTION_ROLLBACK = 1016
    DB_CONNECTION_ILLEGAL_ACCESS = 1017
    RECURSIVE_CALL = 1018
    SQL_EXCEPTION = 1020
    HTTP_404_ERROR = 1022
    CORE_ERROR = 3000
    COMPILE_ERROR = 3001
    PARSE_ERROR = 3002
    NATIVE_CRITICAL_ERROR = 3003
    PHP_WARNING = 3004
    BAD_RESPONSE_TIME = 1002
    AGENT_STOP = 1019
    AGENT_START = 1021

    def __init__(
            self,
            error_type=0,
            error_hash=0,
    ):
        ProfileDataType.__init__(self)
        self.error_hash = error_hash
        self.error_type = error_type

    def get_type(self):
        return ProfileDataType.TYPE_ERROR
