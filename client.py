

# MODULE IMPORTS
import socket
import threading
import sys
import uuid
import pickle
import json

# CUSTOM MODULE IMPORTS
from message import Message
from peer import Peer
from style import Style

# CONSTANTS
HEADER_PART_LENGTH = 10


# CLASS:Client
class Client:
    id = None
    username = None

    def __init__(self, peer: Peer, username: int, server_ip: str, server_port: int, listen_ip: str, listen_port: int):
        self.username = username
        self.id = str(uuid.uuid4())[:8]

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        sock.connect((server_ip, server_port))

        # start thread for sending messages
        input_thread = threading.Thread(target=self.__send, args=(sock, ))
        # input_thread.daemon = True
        input_thread.start()

        # start thread for receiving messages
        receive_thread = threading.Thread(target=self.__receive, args=(sock, peer))
        # receive_thread.daemon = True
        receive_thread.start()

        # client tells server which addr it's listening too on connect
        # msg_body = 'listeningOn:' + json.dumps((listen_ip, listen_port))
        # message = Message('', 'SYSTEM', msg_body)
        # sock.send(message.get_encoded())

    def __receive(self, sock: socket.socket, peer: Peer):
        # continually receiving data
        while True:
            message_header = sock.recv(Message.header_length)

            if not message_header:
                print(Style.error('Server closed!'))
                sys.exit()

            # extract 3 parts of header
            msg_client_id, msg_type, msg_length = Message.decode_msg_header(message_header)
            # receive message from server
            msg_body = sock.recv(msg_length).decode('utf-8')

            message = Message(msg_client_id, msg_type, msg_body)

            if message.get_type() == 'SYSTEM':
                msg_subtype = message.get_body().split(':')[0]
                msg_body_start = len(msg_subtype) + 1
                msg_body = message.get_body()[msg_body_start:]
                # if msg_subtype == 'servers':
                #     # received servers
                #     recvd_servers = json.loads(msg_body)
                #     print('recvd_servers:')
                #     print(recvd_servers)
                #     print('------')
                #     for server_addr in recvd_servers:
                #         print('received server...', server_addr)
                #         peer.server_listening_to.append(server_addr)
                #         # listen to each server
                #         ip, port = server_addr
                #         port = int(port)
                #         listen_thread = threading.Thread(target=self.listen, args=(ip, port))
                #         listen_thread.daemon = True
                #         listen_thread.start()

            else:
                # Style.clear()
                # print('<USERNAME> ' + data.decode('utf-8'))
                print('<USERNAME> ' + message.get_body())

    def __send(self, sock):
        # when user first connects, auth them with server
        msg_body = 'username:' + self.username

        # build header for system message to send ID to server
        message = Message(self.id, 'SYSTEM', msg_body)
        encoded_message = message.get_encoded()

        sock.send(encoded_message)

        while True:
            msg_body = input()
            # Style.clear()
            print("\033[1A", end='')  # [\033[2K

            if msg_body:
                message = Message(self.id, 'CHAT', msg_body)
                encoded_message = message.get_encoded()

                # send the message
                sock.send(encoded_message)

    def send_msg(self, msg):
        print('sending message: ' + msg)

    def listen(self, ip, port):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        sock.connect((ip, port))

        while True:
            message_header = sock.recv(Message.header_length)

            if not message_header:
                print(Style.error('Listening server closed!'))
                break

            # extract 3 parts of header
            msg_client_id, msg_type, msg_length = Message.decode_msg_header(message_header)
            # receive message from server
            msg_body = sock.recv(msg_length).decode('utf-8')

            message = Message(msg_client_id, msg_type, msg_body)

            if message.get_type() == 'CHAT':
                # Style.clear()
                # print('<USERNAME> ' + data.decode('utf-8'))
                print('<USERNAME> ' + message.get_body())







