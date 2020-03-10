

# MODULE IMPORTS
import socket
import threading
import sys
import uuid
import pickle

# CUSTOM MODULE IMPORTS
from message import Message
from style import Style

# CONSTANTS
HEADER_PART_LENGTH = 10


# CLASS:Client
class Client:
    id = None
    username = None

    def __init__(self, peers, username: int, server_ip: str, server_port: int):
        self.username = username
        self.id = str(uuid.uuid4())[:8]

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        sock.connect((server_ip, server_port))

        input_thread = threading.Thread(target=self.__send, args=(sock, ))
        input_thread.daemon = True
        input_thread.start()

        # continually receiving data
        while True:
            data = sock.recv(1024)

            if not data:
                print(Style.error('Server closed!'))
                sys.exit()

            # Style.clear()
            # print('<USERNAME> ' + data.decode('utf-8'))
            print(data.decode('utf-8'))

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







