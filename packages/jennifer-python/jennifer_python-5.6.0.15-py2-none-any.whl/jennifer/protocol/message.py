from .profile_data import ProfileDataType


class Message(ProfileDataType):
    def __init__(self, message=''):
        ProfileDataType.__init__(self)
        self.message = message

    def get_type(self):
        return ProfileDataType.TYPE_MESSAGE
