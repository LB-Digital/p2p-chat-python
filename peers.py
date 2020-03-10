

# MODULE IMPORTS
import socket


# CLASS:Peers
class Peers:

    # users = []
    connections = []

    def __init__(self):
        print('peers')

    def get_connections(self):
        return self.connections

    def add_connection(self, connection: socket.socket):
        self.connections.append(connection)

