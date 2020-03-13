

# MODULE IMPORTS
import socket
import threading
import sys
import pickle
import json
import math
import time

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

        print(Style.info(f'Your server is listening for connections on {ip}:{port}.'))

        while True:
            client_socket, client_addr = sock.accept()

            # print(Style.info(f'A new peer [{client_addr[0]}:{client_addr[1]}] connected via your server'))

            if self.peer.is_coordinator():
                # print('is coord')
                self.connections.append(client_socket)

                # tell peer connection succeeded
                msg_body = 'connected'
                message = Message('', 'SYSTEM', msg_body)
                client_socket.send(message.get_encoded())

                # start receiving messages from client
                client_thread = threading.Thread(target=self.receive, args=(client_socket, ))
                client_thread.daemon = True
                client_thread.start()

                # ping & update peers
                ping_thread = threading.Thread(target=self.__ping_peers)
                ping_thread.daemon = True
                ping_thread.start()
                # self.__ping_peers()
            else:
                # print('not coord')
                # this server isn't coordinator, so
                # tell peer coordinator address to connect too
                msg_body = 'coordinator:' + json.dumps(self.peer.get_chat_coord())
                message = Message('', 'SYSTEM', msg_body)
                client_socket.send(message.get_encoded())

    # receive func run once for each client, in dedicated threads
    def receive(self, client_sock: socket.socket):
        while True:
            # header has 3 parts (client id, message type, message length)
            message_header = client_sock.recv(Message.header_length)

            # if blank header, client has disconnected
            if not message_header:
                self.connections.remove(client_sock)

                # ping all peers to see who disconnected
                ping_thread = threading.Thread(target=self.__ping_peers)
                ping_thread.daemon = True
                ping_thread.start()
                break

            # extract 3 parts of header
            msg_client_id, msg_type, msg_length = Message.decode_msg_header(message_header)

            if msg_length > 0:
                # receive message from server
                msg_body = client_sock.recv(msg_length).decode('utf-8')

                message = Message(msg_client_id, msg_type, msg_body)

                if message.get_type() == 'SYSTEM':
                    # some system messages should only be handled by coord's server
                    if self.peer.is_coordinator():
                        if message.get_body() == 'pong':
                            # server has pinged client, and client returned successfully with 'pong'
                            # update last_successful_ping time of peer
                            self.peer.successful_ping(message.get_client_id())

                        else:
                            msg_subtype = message.get_body().split(':')[0]
                            msg_body_start = len(msg_subtype) + 1
                            msg_body = message.get_body()[msg_body_start:]
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
                                # self.__send_peers()

                                # broadcast join message
                                msg_body = 'output:' + (
                                    Style.success('+ ' + client_peer_data['username'] + ' connected') +
                                    Style.info(' [Chat Members: ' + self.peer.get_chat_peers_str() + ']')
                                )
                                connect_msg = Message('', 'SYSTEM', msg_body)
                                for connection in self.connections:
                                    connection.send(connect_msg.get_encoded())

                elif message.get_type() == 'CHAT':
                    # msg_username = Style.info(self.peers[msg_client_id]["username"])
                    # out_message = f'<{msg_username}> {message}'
                    encoded_msg = message.get_encoded()

                    for connection in self.connections:
                        connection.send(encoded_msg)

    def __ping_peers(self):
        # create ping message instance
        message = Message('', 'SYSTEM', msg_body='ping')
        # save time of ping
        ping_time = math.floor(time.time())
        # ping each connected client
        for connection in self.connections:
            connection.send(message.get_encoded())

        # wait ping timeout seconds
        time.sleep(1)

        # check which peers pong'ed back
        dead_peers = []
        for peer_id, peer_data in self.peer.get_chat_peers().items():
            last_successful_ping = peer_data['last_successful_ping']
            if last_successful_ping < ping_time:
                dead_peers.append(peer_id)

        for peer_id in dead_peers:
            self.peer.remove_chat_peer(peer_id)

            msg_body = 'output:' + (
                Style.error('- ' + peer_data['username'] + ' disconnected') +
                Style.info(' [Chat Members: ' + self.peer.get_chat_peers_str() + ']')
            )
            disconnect_msg = Message('', 'SYSTEM', msg_body)
            for connection in self.connections:
                connection.send(disconnect_msg.get_encoded())

        self.__send_peers()

    def __send_peers(self):
        msg_body = 'peers:' + json.dumps(self.peer.get_chat_peers())
        message = Message('', 'SYSTEM', msg_body)

        for connection in self.connections:
            connection.send(message.get_encoded())






