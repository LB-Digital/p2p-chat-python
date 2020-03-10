

# MODULE IMPORTS
import socket
import threading
import sys
import pickle

# CUSTOM MODULE IMPORTS
from style import Style
from peers import Peers
from message import Message

# CONSTANTS
HEADER_PART_LENGTH = 10


# CLASS:Server
class Server:

    # coordinator = False

    connections = []
    peers = {}

    def __init__(self, peers: Peers, ip: str, port: int):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        sock.bind((ip, port))
        sock.listen()

        print(Style.success(f'Your server is listening for connections on {ip}:{port}.'))

        while True:
            client_socket, client_addr = sock.accept()

            print(Style.info(f'A new peer [{client_addr[0]}:{client_addr[1]}] connected via your server'))
            self.connections.append(client_socket)
            # peers.add_connection(client_socket)

            client_thread = threading.Thread(target=self.receive, args=(client_socket, client_addr))
            client_thread.daemon = True
            client_thread.start()

            # print(self.peers)

    def receive(self, client_sock: socket.socket, client_addr: tuple):
        while True:
            # header has 3 parts (client id, message type, message length)
            header_length = HEADER_PART_LENGTH * 3
            message_header = client_sock.recv(header_length)
            print(message_header)

            # ignore message if no header
            if not message_header:
                print('client disconnected!')
                self.connections.remove(client_sock)
                break

            # extract 3 parts of header
            msg_client_id, msg_type, msg_length = Message.decode_msg_header(message_header)
            # receive message from server
            msg_body = client_sock.recv(msg_length).decode('utf-8')

            message = Message(msg_client_id, msg_type, msg_body)

            if message.get_type() == 'SYSTEM':
                msg_split = message.get_body().split(':')
                if msg_split[0] == 'username':
                    # client is authenticating them-self
                    self.peers[msg_client_id] = {
                        'username': msg_split[1]
                    }
                print(self.peers)

            elif message.get_type() == 'CHAT':
                # msg_username = Style.info(self.peers[msg_client_id]["username"])
                # out_message = f'<{msg_username}> {message}'
                encoded_msg = message.get_encoded()

                print('outing msg to connections...', self.connections)
                for connection in self.connections:
                    connection.send(encoded_msg)






