

# MODULE IMPORTS
import socket
import uuid
import math
import time

# CUSTOM MODULES IMPORTS
from message import Message
from style import Style


# CLASS:Peer
class Peer:
    def __init__(self, is_coordinator: bool, username: str, server_addr: tuple):
        self.__is_coordinator = is_coordinator
        self.__username = username
        self.__server_addr = server_addr

        self.__id = str(uuid.uuid4())[:8]

        self.__chat_coord_addr = None
        self.__chat_peers = {}

    # Mutator (setter) Methods
    def set_chat_coord(self, coord_addr: tuple):
        self.__chat_coord_addr = coord_addr

    def set_chat_peers(self, peers: dict):
        # get current unix timestamp
        now = math.floor(time.time())

        for peer_id, peer_data in peers.items():
            peer_data['last_successful_ping'] = now

        self.__chat_peers = peers

    def add_chat_peer(self, peer_id: str, peer_data: dict):
        # peer being added, so set last pinged to now
        now = math.floor(time.time())
        # save peers data to dict of chat peers
        self.__chat_peers[peer_id] = {
            'username': peer_data['username'],
            'server_addr': peer_data['server_addr'],
            'last_successful_ping': now
        }

    def remove_chat_peer(self, peer_id: str):
        del self.__chat_peers[peer_id]

    def successful_ping(self, peer_id: str):
        # last successful ping time is now
        now = math.floor(time.time())
        # update last_successful ping time of chat peer
        self.__chat_peers[peer_id]['last_successful_ping'] = now

    # Accessor (getter) Methods
    def is_coordinator(self):
        return self.__is_coordinator

    def get_id(self):
        return self.__id

    def get_username(self):
        return self.__username

    def get_server_addr(self):
        return self.__server_addr

    def get_chat_coord(self):
        return self.__chat_coord_addr

    def get_chat_peer(self, peer_id: str):
        return self.__chat_peers[peer_id]

    def get_chat_peers(self):
        return self.__chat_peers

    def get_chat_peers_str(self):
        peers_usernames = []
        for peer_id, peer_data in self.__chat_peers.items():
            peers_usernames.append(peer_data['username'])

        return ', '.join(peers_usernames)







