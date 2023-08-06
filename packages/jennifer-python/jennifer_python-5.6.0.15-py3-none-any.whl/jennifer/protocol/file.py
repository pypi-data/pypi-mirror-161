from .profile_data import ProfileDataType


class File(ProfileDataType):
    TYPE_UNKNOWN = 0
    TYPE_READ = 1
    TYPE_WRITE = 2
    TYPE_RWOPEN = 6

    def __init__(self, name='', mode=''):
        ProfileDataType.__init__(self)
        self.name = name
        is_read = 'r' in mode
        is_write = 'w' in mode

        self.mode = File.TYPE_UNKNOWN
        if is_read and is_write:
            self.mode = File.TYPE_RWOPEN
        elif is_read:
            self.mode = File.TYPE_READ
        elif is_write:
            self.mode = File.TYPE_WRITE

    def get_type(self):
        return ProfileDataType.TYPE_FILE
