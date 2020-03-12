

# MODULE IMPORTS
import socket
import uuid

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
        self.__chat_peers = peers

    def add_chat_peer(self, peer_id: str, peer_data: dict):
        self.__chat_peers[peer_id] = peer_data

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







