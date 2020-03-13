

# MODULE IMPORTS
import socket
import threading
import sys
import json
import time

# CUSTOM MODULE IMPORTS
from message import Message
from peer import Peer
from style import Style

# CONSTANTS
HEADER_PART_LENGTH = 10


# CLASS:Client
class Client:
    def __init__(self, peer: Peer, server_ip: str, server_port: int):
        self.peer = peer

        self.__start(server_ip, server_port)

    def __start(self, server_ip: str, server_port: int):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        sock.connect((server_ip, server_port))

        # first message sent back from server is a SYS msg of either...
        # "connected" - connection succeeded
        # "coordinator:<coord addr>" - server not coordinator
        message = self.__receive_msg(sock)
        if message.get_type() != 'SYSTEM':
            sys.exit('Unexpected server response on connection')
        else:
            if message.get_body() == 'connected':
                self.peer.set_chat_coord((server_ip, server_port))
                self.__on_connect(sock)

            else:
                msg_subtype = message.get_body().split(':')[0]
                msg_body_start = len(msg_subtype) + 1
                if msg_subtype == 'coordinator':
                    chat_coord = message.get_body()[msg_body_start:]
                    coord_ip, coord_port = json.loads(chat_coord)
                    sock.close()
                    self.__start(coord_ip, coord_port)
                else:
                    sys.exit('Unexpected server response on connection')

    def __on_connect(self, sock: socket.socket):
        # start thread for receiving messages
        receive_thread = threading.Thread(target=self.__start_receiving, args=(sock, ))
        # receive_thread.daemon = True
        receive_thread.start()

        # start thread for sending messages
        input_thread = threading.Thread(target=self.__send, args=(sock, ))
        input_thread.daemon = True
        input_thread.start()

        # when user first connects, auth them with server
        auth_data = {
            'username': self.peer.get_username(),
            'server_addr': self.peer.get_server_addr()
        }
        msg_body = 'auth:' + json.dumps(auth_data)
        message = Message(self.peer.get_id(), 'SYSTEM', msg_body)
        sock.send(message.get_encoded())

    def __start_receiving(self, sock: socket.socket):
        # continually receiving data
        while True:
            message = self.__receive_msg(sock)

            if message == False:
                # server closed
                print(Style.error('Server closed!'))
                # receiving thread isn't daemon, so once this loop is broken, program will exit
                break

            if message.get_type() == 'SYSTEM':
                if message.get_body() == 'ping':
                    # client has been pinged by server, pong back
                    message = Message(self.peer.get_id(), 'SYSTEM', 'pong')
                    sock.send(message.get_encoded())

                else:
                    msg_subtype = message.get_body().split(':')[0]
                    msg_body_start = len(msg_subtype) + 1
                    msg_body = message.get_body()[msg_body_start:]

                    if msg_subtype == 'peers':
                        # received updated peers list
                        updated_peers = json.loads(msg_body)
                        # save updated chat peers list
                        self.peer.set_chat_peers(updated_peers)

                    elif msg_subtype == 'output':
                        print(msg_body)

            else:
                # Style.clear()
                # print('<USERNAME> ' + data.decode('utf-8'))
                msg_peer = self.peer.get_chat_peer(message.get_client_id())
                msg_username = msg_peer['username']
                print(f'<{Style.info(msg_username)}> ' + message.get_body())

    def __receive_msg(self, sock: socket.socket):
        # continually receiving data
        message_header = sock.recv(Message.header_length)

        if not message_header:
            return False

        # extract 3 parts of header
        msg_client_id, msg_type, msg_length = Message.decode_msg_header(message_header)
        # receive message from server
        msg_body = sock.recv(msg_length).decode('utf-8')

        return Message(msg_client_id, msg_type, msg_body)

    def __send(self, sock: socket.socket):
        while True:
            msg_body = input()
            # Style.clear()
            print("\033[1A", end='')  # [\033[2K

            if msg_body:
                message = Message(self.peer.get_id(), 'CHAT', msg_body)
                encoded_message = message.get_encoded()

                # send the message
                sock.send(encoded_message)






