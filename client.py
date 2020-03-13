

# MODULE IMPORTS
import socket       # socket network connections
import threading    # split script execution into multiple threads
import sys          # system operations such as sys.exit() to exit the script
import json         # parse/stringify JSON

# CUSTOM MODULE IMPORTS
from message import Message     # processing system & chat messages
from peer import Peer           # the apps peer
from style import Style         # styling console prints


class Client:
    """
    Client class for peers client.
    Connects to the given server and handles client related tasks.

    :param Peer peer: global peer object
    :param str server_ip: server ip for client to connect too
    :param int server_port: server port for client to connect too

    :return Client client: instance of this Client class
    """
    def __init__(self, peer: Peer, server_ip: str, server_port: int):
        # store the peer to this instance so it can be accessed throughout the clients methods
        self.peer = peer
        # until the client connects to a server, its socket is None
        self.sock = None

        # start the client
        self.__start(server_ip, server_port)

    def __start(self, server_ip: str, server_port: int):
        """
        Start the client.
        Connects the client to the given server address on init

        :param str server_ip: server ip for client to connect too
        :param int server_port: server port for client to connect too
        """

        # create a socket for the client as an IPv4 (AF_INET) using byte streams (SOCK_STREAM)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # allow the socket to reuse addresses already in use
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        # connect the clients socket to the param server
        self.sock.connect((server_ip, server_port))

        # first message sent back from server is a SYS msg of either...
        # "connected" - connection succeeded and agreed
        # "coordinator:<coord addr>" - the chats coordinator
        message = self.__receive_msg()

        if message.get_type() != 'SYSTEM':
            # first message should be a SYS message, so something is wrong if it isn't
            sys.exit('Unexpected server response on connection')

        else:
            if message.get_body() == 'connected':
                # peer has successfully agreed communication with chat server,
                # so they know whoever they connected too is the chat coordinator
                self.peer.set_chat_coord(server_ip, server_port)

                # call on connect handler
                self.__on_connect()

            else:
                # peer found the server, however connection was not agreed
                msg_subtype = message.get_body().split(':')[0]
                msg_body_start = len(msg_subtype) + 1
                if msg_subtype == 'coordinator':
                    # connection was not agreed as the peer should connect to the chat coordinator
                    # extract chat coordinator address from message
                    chat_coord = message.get_body()[msg_body_start:]
                    # parse the JSON string to get the coordinators servers ip & port
                    coord_ip, coord_port = json.loads(chat_coord)

                    # close this client socket as it is no longer needed
                    self.sock.close()
                    # attempt to start the client again on the new found server address
                    self.__start(coord_ip, coord_port)
                else:
                    # connection was not agreed and the chat coordinator was not shared, unknown error
                    sys.exit('Unexpected server response on connection')

    def __on_connect(self):
        """
        Clients on connect handler.
        Called once the client successfully connects to server and agrees communication.
        """
        # create a thread for receiving messages
        receive_thread = threading.Thread(target=self.__start_receiving)
        # thread is a daemon as it shouldn't prevent program flow from continuing
        receive_thread.daemon = True
        # start the thread
        receive_thread.start()

        # when user first connects, auth them with server
        auth_data = {
            # send server their username
            'username': self.peer.get_username(),
            # and their own servers address
            'server_addr': self.peer.get_server_addr()
        }
        # build the message body by stringifying the auth data as JSON
        msg_body = 'auth:' + json.dumps(auth_data)
        # create a system message instance using the peers id, and the built body
        message = Message(self.peer.get_id(), 'SYSTEM', msg_body)
        # send the auth message to the server
        self.sock.send(message.get_encoded())

    def __start_receiving(self):
        """
        Start receiving data from server.
        Client loops continuously, listening for new messages from server.
        """
        while True:
            # call the private receive message function
            message = self.__receive_msg()

            if not message:
                # if __receive_message returned false, the server has been closed
                self.peer.connected = False
                # close this clients socket
                self.sock.close()

                # receiving thread isn't daemon, so once this loop is broken, program will continue in main thread
                break

            # if received message is a system message (sent by the program, not the user)
            if message.get_type() == 'SYSTEM':
                # if message was a ping message
                if message.get_body() == 'ping':
                    # client has been pinged by server, pong back to confirm still active
                    message = Message(self.peer.get_id(), 'SYSTEM', 'pong')
                    self.sock.send(message.get_encoded())

                else:
                    # not a ping message, see if sys message has a subtype to tell client what to do with the info
                    # e.g: peers:lucas, holly, dave (<sub type>:<message body>)
                    msg_subtype = message.get_body().split(':')[0]
                    # the actual message body starts after the colon
                    msg_body_start = len(msg_subtype) + 1
                    # extract the actual message body
                    msg_body = message.get_body()[msg_body_start:]

                    # if server is sending an updated peers list
                    if msg_subtype == 'peers':
                        # parse JSON string of updated peers list to python dict
                        updated_peers = json.loads(msg_body)
                        # save updated chat peers list to peer class instance
                        self.peer.set_chat_peers(updated_peers)

                    # server simply wants to output a message to client
                    # e.g: print when someone connects/disconnects
                    elif msg_subtype == 'output':
                        # print the message to client
                        print(msg_body)

            # received message is a chat message (sent by a user)
            else:
                # get the peer by the peer id in the messages header
                msg_peer = self.peer.get_chat_peer(message.get_client_id())
                # get the peers username
                msg_username = msg_peer['username']
                # build the formatted message, using the from peers username and their message
                print(f'<{Style.info(msg_username)}> ' + message.get_body())

    def __receive_msg(self):
        """
        Receive message from server.
        Waits for byte stream to be sent to client from server, before parsing it

        :return: Message: instance of Message class for the received data
        """
        # wait for byte stream from server
        message_header = self.sock.recv(Message.header_length)

        if not message_header:
            # if a blank message header is received, return False as no message
            return False

        # extract 3 parts of header [sending client id, type (system/chat), length (length of body)]
        msg_client_id, msg_type, msg_length = Message.decode_msg_header(message_header)
        # receive message body from server
        msg_body = self.sock.recv(msg_length).decode('utf-8')

        # return new instance of message with received data
        return Message(msg_client_id, msg_type, msg_body)

    def send(self, msg_body: str):
        """
        Send a message.
        Sends a chat message from the client to the server.

        :param str msg_body: the body of the chat message
        """
        # ANSI codes to delete previous printed line of stdout (the text the user typed into input(''))
        # this makes the chat look much cleaner as a peers own messages also show formatted and not as plain text
        print("\033[1A", end='')  # [\033[2K

        # if a message body is given
        if msg_body:
            # create a Message instance
            message = Message(self.peer.get_id(), 'CHAT', msg_body)
            # get utf-8 encoded version of headers+message
            encoded_message = message.get_encoded()

            # send the built message to server
            self.sock.send(encoded_message)






