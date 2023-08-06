from . import remote_call
from .profile_data import ProfileDataType


class ExternalCall(ProfileDataType):
    TYPE_NONE = remote_call.TYPE_NONE
    TYPE_HTTP = remote_call.TYPE_HTTP
    TYPE_HTTPS = remote_call.TYPE_HTTPS

    def __init__(self, protocol='http', host='', port=80, text_hash='', desc_hash=0, error_hash=0):
        ProfileDataType.__init__(self)

        self.text_hash = text_hash
        protocol = protocol.lower()
        self.protocol = ExternalCall.TYPE_NONE
        if protocol == 'http':
            self.protocol = ExternalCall.TYPE_HTTP
        elif protocol == 'https':
            self.protocol = ExternalCall.TYPE_HTTPS
        self.host = host
        self.port = port
        self.desc_hash = desc_hash
        self.error_hash = error_hash

    def get_type(self):
        return ProfileDataType.TYPE_TXCALL
