from ..profile_data import ProfileDataType


class Fetch(ProfileDataType):
    def __init__(self, count=0):
        ProfileDataType.__init__(self)
        self.count = count

    def get_type(self):
        return ProfileDataType.TYPE_SQL_FETCH
