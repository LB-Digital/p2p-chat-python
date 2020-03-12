

# MODULE IMPORTS
import socket

# CUSTOM MODULES IMPORTS
from message import Message
from style import Style


# CLASS:Peer
class Peer:

    # users = []
    # connections = []

    is_coordinator = False

    my_server = None
    my_client = None

    my_server_addr = None
    client_connected_to = None
    server_listening_to = []
    connected_to_me = []

    # def new_client_connected(self, client_addr):
    #     pass
    #
    # def listen_to(self, ip, port):
    #     sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    #     sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    #
    #     sock.connect((ip, port))
    #
    #     while True:
    #         message_header = sock.recv(Message.header_length)
    #
    #         if not message_header:
    #             print(Style.error('Listening server closed!'))
    #             break
    #
    #         # extract 3 parts of header
    #         msg_client_id, msg_type, msg_length = Message.decode_msg_header(message_header)
    #         # receive message from server
    #         msg_body = sock.recv(msg_length).decode('utf-8')
    #
    #         message = Message(msg_client_id, msg_type, msg_body)
    #
    #         if message.get_type() == 'CHAT':
    #             # Style.clear()
    #             # print('<USERNAME> ' + data.decode('utf-8'))
    #             print('<USERNAME> ' + message.get_body())

    # def __init__(self):
    #     print('peers')
    #
    # def get_connections(self):
    #     return self.connections
    #
    # def add_connection(self, connection: socket.socket):
    #     self.connections.append(connection)

