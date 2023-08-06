

class DBConnectionRecorder(object):
    def __init__(self):
        self.connections = {}

    def add_connection(self, conn):
        if conn not in self.connections.keys():
            self.connections[conn] = 0

    def remove_connection(self, conn):
        del self.connections[conn]

    def active(self, conn):
        self.connections[conn] = 1

    def inactive(self, conn):
        self.connections[conn] = 0

    def record(self):
        active = 0
        values = self.connections.values()
        for v in values:
            active += v

        return (
            len(self.connections),  # total
            active,  # active
        )
