from .profile_data import ProfileDataType


class Socket(ProfileDataType):
    TYPE_UNKNOWN = 0
    # TYPE_ISTREAM = 3
    # TYPE_OSTREAM = 3
    TYPE_IOSTREAM = 7

    def __init__(self, host, port, local_port):
        ProfileDataType.__init__(self)
        self.host = host
        self.port = port
        self.local_port = local_port
        self.mode = Socket.TYPE_IOSTREAM

    def get_type(self):
        return ProfileDataType.TYPE_SOCKET
