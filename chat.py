

# MODULE IMPORTS
import sys
import threading
import time
import random

# CUSTOM MODULE IMPORTS
# used 'from ... import ...' statements to import directly into current namespace
from extract_ip_port import extract_ip_port, AddressExtractError
from client import Client
from server import Server
from peer import Peer
from style import Style


# utility function to start a thread for the server.  Run once
def start_server_thread(ip: str, port: int):
    server_thread = threading.Thread(target=start_server, args=(ip, port))
    server_thread.daemon = True
    server_thread.start()


# start the clients listening server.  Connects members if peer is coord, redirects them otherwise
def start_server(ip: str, port: int):
    Server(peer, ip, port)


# thread for listening to input
def start_input_thread():
    input_thread = threading.Thread(target=client_input)
    input_thread.daemon = True
    input_thread.start()


def client_input():
    while True:
        msg = input('')

        if peer.connected:
            client.send(msg)


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

    peer = Peer(coordinator, username, (listen_ip, listen_port))

    start_server_thread(listen_ip, listen_port)

    start_input_thread()

    if existing_ip and existing_port:
        # existing member address given, so attempt to connect to their server
        print('Connecting to existing members server...')

        try:
            client = Client(peer, existing_ip, existing_port)
            peer.connected = True
        except ConnectionRefusedError:
            # failed to connect to existing member, so try become coordinator of own Server
            print(Style.warning('Failed to connect to existing member! \n'))
    else:
        try:
            client = Client(peer, listen_ip, listen_port)
            peer.connected = True
        except ConnectionRefusedError:
            print(Style.error('Failed to connect to own server!'))

    try:
        while True:
            if not peer.connected:
                peer.connected = True
                print(Style.error('Coordinator disconnected, finding new coordinator...'))

                chat_peers = peer.get_chat_peers()

                earliest_join_id = None
                for peer_id, peer_data in chat_peers.items():
                    # loop peer isn't the old chat coordinator
                    if not peer_data['is_coord']:
                        if not earliest_join_id:
                            earliest_join_id = peer_id
                        elif peer_data['joined_at'] < chat_peers[earliest_join_id]['joined_at']:
                            earliest_join_id = peer_id

                if earliest_join_id:
                    # found new peer to be coordinator
                    earliest_join_peer = chat_peers[earliest_join_id]
                    new_server_ip, new_server_port = earliest_join_peer['server_addr']
                    print(Style.info(f'Attempting to make {earliest_join_peer["username"]} the new chat coordinator'))
                else:
                    # no other peers to be coord, make own server coord
                    print(Style.info('Attempting to make you the new chat coordinator...'))
                    new_server_ip, new_server_port = peer.get_server_addr()

                peer.set_chat_coord(new_server_ip, new_server_port)
                peer.set_chat_peers({})


                for retries in range(5):
                    # random delay so less chance of all members trying connection at same time
                    rand_delay = random.uniform(0.0, 5.0)
                    time.sleep(rand_delay)

                    try:
                        client = Client(peer, new_server_ip, new_server_port)
                        break
                    except ConnectionRefusedError:
                        print(Style.warning(f'Failed to connect to new server, retries: {retries}'))
                        # likely failed
                        continue

            time.sleep(0.1)

    except KeyboardInterrupt:
        sys.exit()
