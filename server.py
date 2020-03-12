

# MODULE IMPORTS
import socket
import threading
import sys
import pickle
import json

# CUSTOM MODULE IMPORTS
from style import Style
from peer import Peer
from message import Message


# CLASS:Server
class Server:
    def __init__(self, peer: Peer, ip: str, port: int):
        self.peer = peer

        self.connections = []

        self.__start(ip, port)

    def __start(self, ip: str, port: int):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        sock.bind((ip, port))
        sock.listen()

        print(Style.success(f'Your server is listening for connections on {ip}:{port}.'))

        while True:
            client_socket, client_addr = sock.accept()

            print(Style.info(f'A new peer [{client_addr[0]}:{client_addr[1]}] connected via your server'))

            if self.peer.is_coordinator():
                self.connections.append(client_socket)

                # tell peer connection succeeded
                msg_body = 'connected'
                message = Message('', 'SYSTEM', msg_body)
                client_socket.send(message.get_encoded())

                # start receiving messages from client
                client_thread = threading.Thread(target=self.receive, args=(client_socket, ))
                client_thread.daemon = True
                client_thread.start()
            else:
                # this server isn't coordinator, so
                # tell peer coordinator address to connect too
                msg_body = 'coordinator:' + json.dumps(self.peer.get_chat_coord())
                message = Message('', 'SYSTEM', msg_body)
                client_socket.send(message.get_encoded())

    def receive(self, client_sock: socket.socket):
        while True:
            # header has 3 parts (client id, message type, message length)
            message_header = client_sock.recv(Message.header_length)
            # print(message_header)

            # ignore message if no header
            if not message_header:
                print('client disconnected!')
                self.connections.remove(client_sock)

                # TODO ping all peers servers, checking which ones respond to remove dead peers?
                # should be at least one dead right? since one disconnected
                break

            # extract 3 parts of header
            msg_client_id, msg_type, msg_length = Message.decode_msg_header(message_header)
            # receive message from server
            msg_body = client_sock.recv(msg_length).decode('utf-8')

            message = Message(msg_client_id, msg_type, msg_body)

            if message.get_type() == 'SYSTEM':
                msg_subtype = message.get_body().split(':')[0]
                msg_body_start = len(msg_subtype) + 1
                msg_body = message.get_body()[msg_body_start:]
                if self.peer.is_coordinator():
                    # client can only auth with coordinators server
                    if msg_subtype == 'auth':
                        # peer is authenticating them-self with their id and username
                        auth_data = json.loads(msg_body)
                        client_peer_id = message.get_client_id()
                        client_peer_data = {
                            'username': auth_data['username'],
                            'server_addr': auth_data['server_addr']
                        }
                        self.peer.add_chat_peer(client_peer_id, client_peer_data)

                        # inform all connected clients of this new peer
                        self.__update_peers()

            elif message.get_type() == 'CHAT':
                # msg_username = Style.info(self.peers[msg_client_id]["username"])
                # out_message = f'<{msg_username}> {message}'
                encoded_msg = message.get_encoded()

                for connection in self.connections:
                    connection.send(encoded_msg)

    def __update_peers(self):
        msg_body = 'peers:' + json.dumps(self.peer.get_chat_peers())
        message = Message('', 'SYSTEM', msg_body)

        for connection in self.connections:
            connection.send(message.get_encoded())






