# IMPORTS
import sys
import socket
import threading
import warnings
import time

# IMPORT CUSTOM MODULES
# used 'from ... import ...' statements to import directly into current namespace
from extract_ip_port import extract_ip_port, AddressExtractError
from client import Client
from server import Server
from peer import Peer
from style import Style

# CONSTANTS


def start_server_thread(peer: Peer, ip: str, port: int):
    server_thread = threading.Thread(target=start_server, args=(peer, ip, port))
    # server_thread.daemon = True
    server_thread.start()


def start_server(peer: Peer, ip: str, port: int):
    peer.my_server = Server(peer, ip, port)


if __name__ == '__main__':
    if len(sys.argv) < 3:
        # 1 default arg (script name) + 2 required params (ID num + Listening address)
        sys.exit('Missing arguments. Args: <Username> <Listening PORT:IP> (<Existing Members PORT:IP>)')
    elif len(sys.argv) > 4:
        # max of 4 (<script name> <Username> <listening address> <existing member address>)
        sys.exit('Too many arguments. Args: <Username> <Listening PORT:IP> (<Existing Members PORT:IP>)')

    # get username from script args
    username = sys.argv[1]

    # validate username is alphanumeric
    if not username.isalnum():
        sys.exit('Username must be alphanumeric (only letters or numbers)')

    # validate username length
    if len(username) > 10:
        sys.exit('Username length cannot be more than 10 characters')

    # declare address variables
    listen_ip = listen_port = None
    existing_ip = existing_port = None

    # get ip:port to listen too from script args (this server)
    try:
        listen_ip, listen_port = extract_ip_port(sys.argv[2])
    except AddressExtractError as err_msg:
        sys.exit('Listening server ' + err_msg)

    coordinator = True

    # they may have provided an existing members IP:Port to connect too
    if len(sys.argv) == 4:
        # existing member address given
        try:
            existing_ip, existing_port = extract_ip_port(sys.argv[3])
            coordinator = False
        except AddressExtractError as err_msg:
            sys.exit('Existing member ' + err_msg)

    peer = Peer(coordinator)

    start_server_thread(peer, listen_ip, listen_port)

    if existing_ip and existing_port:
        # existing member address given, so attempt to connect to their server
        print('Connecting to existing members server...')

        try:
            # peer.client_connected_to = (existing_ip, existing_port)
            # peer.my_client = \
            Client(peer, username, existing_ip, existing_port, listen_ip, listen_port)
        except ConnectionRefusedError:
            # failed to connect to existing member, so try become coordinator of own Server
            print(Style.warning('Failed to connect to existing member! \n'))
    else:
        # peer.my_client = \
        Client(peer, username, listen_ip, listen_port, listen_ip, listen_port)
        # connected to self, so don't need to set peer.client_connected_to

    # either no existing member given, or failed to connect to existing member
    # so try to start server as coordinator




