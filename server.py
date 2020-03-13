

# MODULE IMPORTS
import socket       # socket network connections
import threading    # split script execution into multiple threads
import json         # parse/stringify JSON
import math         # mathematical operations such as rounding
import time         # get current unix time of system

# CUSTOM MODULE IMPORTS
from message import Message     # processing system & chat messages
from peer import Peer           # the apps peer
from style import Style         # styling console prints


# CLASS:Server
class Server:
    """
    Server class for peers server.
    Listens to connections for this peers server, processing messages from/to connected clients.

    :param Peer peer: global peer instance
    :param str ip: server ip to bind too
    :param int port: server port to bind too

    :return Server: instance of this Server class
    """
    def __init__(self, peer: Peer, ip: str, port: int):
        # store the peer to this instance so it can be accessed throughout the clients methods
        self.peer = peer
        # define empty array of clients connected to this server
        self.connections = []

        # start the server
        self.__start(ip, port)

    def __start(self, ip: str, port: int):
        """
        Start the server.
        Binds the server to the given server address on init.

        :param str ip: server ip to bind too
        :param int port: server port to bind too
        """

        # create a socket for the server as an IPv4 (AF_INET) using byte streams (SOCK_STREAM)
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # allow the socket to reuse addresses already in use so that when
        # running program multiple times, the socket address does not need to be changed
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        # bind the server to the param server address
        sock.bind((ip, port))
        # start TCP listener for server socket
        sock.listen()

        # tell peer their server is running successfully, and on which address
        print(Style.info(f'Your server is listening for connections on {ip}:{port}.'))

        # continuously waiting for clients to connect to server
        while True:
            # on connect, extract the clients socket and their address
            client_socket, client_addr = sock.accept()

            # print(Style.info(f'A new peer [{client_addr[0]}:{client_addr[1]}] connected via your server'))

            # if servers peer is coordinator, handle connection
            if self.peer.is_coordinator():
                # add client to list of connected clients
                self.connections.append(client_socket)

                # tell peer connection succeeded
                msg_body = 'connected'
                message = Message('', 'SYSTEM', msg_body)
                client_socket.send(message.get_encoded())

                # create dedicated thread to start receiving messages from connecting client
                client_thread = threading.Thread(target=self.receive, args=(client_socket, ))
                # client thread is a daemon as it shouldn't prevent program from exiting
                client_thread.daemon = True
                # start the thread
                client_thread.start()

                # create thread to ping all peers and send updated list to connected clients
                ping_thread = threading.Thread(target=self.__ping_peers)
                ping_thread.daemon = True
                ping_thread.start()
            else:
                # this server isn't coordinator, so tell peer coordinator address to connect too
                msg_body = 'coordinator:' + json.dumps(self.peer.get_chat_coord())
                message = Message('', 'SYSTEM', msg_body)
                client_socket.send(message.get_encoded())

    def receive(self, client_sock: socket.socket):
        """
        Receive data from client.
        Loops continuously in dedicated thread, listening for data from client.

        :param socket.socket client_sock: the connected clients socket to receive from
        """
        while True:
            # header has 3 parts (client id, message type, message length)
            message_header = client_sock.recv(Message.header_length)

            # if blank header, client has disconnected
            if not message_header:
                # remove from connected clients list
                self.connections.remove(client_sock)

                # ping all peers to see who disconnected
                # (called in separate thread so program can continue)
                ping_thread = threading.Thread(target=self.__ping_peers)
                ping_thread.daemon = True
                ping_thread.start()

                # break out of receiving loop as no longer need to receive from this client
                break

            # extract 3 parts of header
            msg_client_id, msg_type, msg_length = Message.decode_msg_header(message_header)

            if msg_length > 0:
                # received message from server
                msg_body = client_sock.recv(msg_length).decode('utf-8')
                # instantiate Message with received data
                message = Message(msg_client_id, msg_type, msg_body)

                if message.get_type() == 'SYSTEM':
                    # system messages should only be handled by coord's server
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
                                # save peer to peer dict
                                self.peer.add_chat_peer(client_peer_id, client_peer_data)

                                # broadcast join message
                                msg_body = 'output:' + (
                                    Style.success('+ ' + client_peer_data['username'] + ' connected') +
                                    Style.info(' [Chat Members: ' + self.peer.get_chat_peers_str() + ']')
                                )
                                connect_msg = Message('', 'SYSTEM', msg_body)
                                for connection in self.connections:
                                    # send join message to all connected clients
                                    connection.send(connect_msg.get_encoded())

                elif message.get_type() == 'CHAT':
                    # server received chat message
                    encoded_msg = message.get_encoded()

                    for connection in self.connections:
                        # send too all connected clients
                        connection.send(encoded_msg)

    def __ping_peers(self):
        """
        Ping all peers
        Sends 'ping' sys message to all peers, checking for 'pong' response
        """
        # create ping message instance
        message = Message('', 'SYSTEM', msg_body='ping')
        # save time of ping
        ping_time = math.floor(time.time())
        # ping each connected client
        for connection in self.connections:
            # send ping message
            connection.send(message.get_encoded())

        # wait ping timeout seconds
        time.sleep(1)

        # check which peers pong'ed back
        dead_peers = []
        for peer_id, peer_data in self.peer.get_chat_peers().items():
            # get the last successful ping time of loop peer
            last_successful_ping = peer_data['last_successful_ping']
            # if the last successful ping response was earlier than this ping started
            if last_successful_ping < ping_time:
                # they didn't pong back, so they're inactive
                dead_peers.append(peer_id)

        # for each inactive peer
        for peer_id in dead_peers:
            # remove them from the chat peers list
            self.peer.remove_chat_peer(peer_id)

            # broadcast disconnect message (including remaining chat members)
            msg_body = 'output:' + (
                Style.error('- ' + peer_data['username'] + ' disconnected') +
                Style.info(' [Chat Members: ' + self.peer.get_chat_peers_str() + ']')
            )
            disconnect_msg = Message('', 'SYSTEM', msg_body)
            for connection in self.connections:
                # send disconnect message to each connected client
                connection.send(disconnect_msg.get_encoded())

        # send the remaining peers list to each client
        self.__send_peers()

    def __send_peers(self):
        """
        Send updated peers list.
        Sends the latest chat peers list to each connected client so they know who's connected.
        """
        # JSON encode peers list to send as byte stream
        msg_body = 'peers:' + json.dumps(self.peer.get_chat_peers())
        message = Message('', 'SYSTEM', msg_body)

        for connection in self.connections:
            # send peers list to each connected & active client
            connection.send(message.get_encoded())






