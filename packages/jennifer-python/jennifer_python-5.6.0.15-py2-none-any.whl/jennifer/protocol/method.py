from .profile_data import ProfileDataType


class Method(ProfileDataType):
    def __init__(self, name_hash=0, error_hash=0):
        ProfileDataType.__init__(self)
        self.name_hash = name_hash
        self.error_hash = error_hash

    def get_type(self):
        return ProfileDataType.TYPE_METHOD
