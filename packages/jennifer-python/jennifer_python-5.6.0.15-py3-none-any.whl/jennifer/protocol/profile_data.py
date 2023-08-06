import time


class ProfileDataType:
    TYPE_EMPTY = 0
    TYPE_METHOD = 0x10
    TYPE_TXCALL = 0x20
    TYPE_SQL_EXEC = 0x30
    TYPE_SQL_FETCH = 0x40
    TYPE_MESSAGE = 0x50
    TYPE_DB_MESSAGE = 0x60
    TYPE_FILE = 8 << 4
    TYPE_SOCKET = 9 << 4
    TYPE_EXCEPTION = 10 << 4
    TYPE_METHOD_PARAM = 13 << 4
    TYPE_METHOD_RETURN = 14 << 4
    TYPE_ERROR = 1

    def __init__(self):
        self.parent_index = 0
        self.index = 0
        self.start_time = 0
        self.start_cpu = 0
        self.elapsed_time = 0
        self.elapsed_cpu = 0
        self.parent = None

    @staticmethod
    def get_type(self):
        return ProfileDataType.TYPE_EMPTY

    @staticmethod
    def content_bytes(self):
        return b''

    # def index_to_bytes(self):
    #     return raw.pack_with(
    #         raw.from_number(self.index),
    #         raw.from_number(self.parent_index),
    #     )

    def to_dict(self):
        ret = self.__dict__
        ret['type'] = self.get_type()
        ret.pop('parent', None)  # clear parent
        return ret


class ProfileData:
    def __init__(self, txid, service_hash, children):
        self.txid = txid
        self.service_hash = service_hash
        self.children = children

    def to_dict(self):
        return {
            'txid': self.txid,
            'service_hash': self.service_hash,
            'profiles': [d.to_dict() for d in self.children],
        }
