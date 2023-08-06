from ..profile_data import ProfileDataType


class Message(ProfileDataType):
    TYPE_UNKNOWN = 0
    TYPE_OPEN = 1
    TYPE_CLOSE = 2
    TYPE_COMMIT = 3
    TYPE_ROLLBACK = 4
    TYPE_AUTO_COMMIT_FAILED = 5

    def __init__(self, txid=0, message='', message_type=TYPE_UNKNOWN):
        ProfileDataType.__init__(self)
        self.message = message
        self.message_type = message_type
        self.txid = txid

    def get_type(self):
        return ProfileDataType.TYPE_DB_MESSAGE
