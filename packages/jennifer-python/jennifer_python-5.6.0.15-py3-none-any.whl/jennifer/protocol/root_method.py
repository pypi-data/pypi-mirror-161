from .method import Method


class Root(Method):
    def __init__(self, name_hash=0, error_hash=0):
        Method.__init__(self, name_hash, error_hash)
        self.parent_index = -1
        self.index = 0
