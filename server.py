

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

    # coordinator = False

    connections = []
    servers = []
    peers = {}

    def __init__(self, peer: Peer, ip: str, port: int):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        sock.bind((ip, port))
        sock.listen()

        # peer.my_server_addr = (ip, port)

        print(Style.success(f'Your server is listening for connections on {ip}:{port}.'))

        while True:
            client_socket, client_addr = sock.accept()

            print(Style.info(f'A new peer [{client_addr[0]}:{client_addr[1]}] connected via your server'))
            self.connections.append(client_socket)
            # peers.add_connection(client_socket)

            client_thread = threading.Thread(target=self.receive, args=(client_socket, peer))
            client_thread.daemon = True
            client_thread.start()

            # server lists all the addresses it's currently listening too
            # print(f'Currently listening too: ', peer.server_listening_to)
            # print(f'Currently connected too: ', peer.client_connected_to)
            # servers = peer.server_listening_to
            # if peer.client_connected_to:
            #     servers.append(peer.client_connected_to)
            # msg_body = 'servers:' + json.dumps(servers)
            # print(msg_body)
            # message = Message('', 'SYSTEM', msg_body)
            # # client_socket.send(message.get_encoded())
            # for connection in self.connections:
            #     connection.send(message.get_encoded())

    def receive(self, client_sock: socket.socket, peer: Peer):
        while True:
            # header has 3 parts (client id, message type, message length)
            message_header = client_sock.recv(Message.header_length)
            # print(message_header)

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
            # print(message.get_type(), message.get_body())

            if message.get_type() == 'SYSTEM':
                msg_subtype = message.get_body().split(':')[0]
                msg_body_start = len(msg_subtype) + 1
                msg_body = message.get_body()[msg_body_start:]
                # print(msg_subtype, msg_body)
                if msg_subtype == 'username':
                    # client is authenticating them-self
                    self.peers[msg_client_id] = {
                        'username': msg_body
                    }
                elif msg_subtype == 'listeningOn':
                    pass
                    # # client is telling server which address it is listening too
                    # addr = ':'.join(msg_body.split(' '))
                    # self.servers.append(addr)
                    # print(self.servers)

            elif message.get_type() == 'CHAT':
                # msg_username = Style.info(self.peers[msg_client_id]["username"])
                # out_message = f'<{msg_username}> {message}'
                encoded_msg = message.get_encoded()
                # formatted_msg = message.get_formatted()
                if not peer.is_coordinator:
                    print('<USERNAME>> ' + message.get_body())

                # print('outing msg to connections...', self.connections)
                # print('outing msg to connections...')
                for connection in self.connections:
                    connection.send(encoded_msg)






