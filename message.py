

# CONSTANTS
HEADER_PART_LENGTH = 10


# CLASS:Message
class Message:

    __client_id = None
    __type = None
    __length = None
    __body = None

    def __init__(self, msg_client_id, msg_type, msg_body):
        self.__client_id = msg_client_id
        self.__type = msg_type
        self.__body = msg_body

    def get_encoded(self):
        header_id_part = self.__client_id.ljust(HEADER_PART_LENGTH)
        header_type_part = self.__type.ljust(HEADER_PART_LENGTH)
        header_length_part = str(len(self.__body)).ljust(HEADER_PART_LENGTH)

        message_header = header_id_part + header_type_part + header_length_part

        return (message_header + self.__body).encode('utf-8')

    def get_body(self):
        return self.__body

    def get_client_id(self):
        return self.__client_id

    def get_type(self):
        return self.__type

    def get_length(self):
        return self.__length

    @staticmethod
    def decode_msg_header(msg_header):
        msg_header = msg_header.decode('utf-8')

        header_id_part = msg_header[0:HEADER_PART_LENGTH]
        header_type_part = msg_header[HEADER_PART_LENGTH:HEADER_PART_LENGTH*2]
        header_length_part = msg_header[HEADER_PART_LENGTH*2:]

        # parse client id from header
        msg_client_id = header_id_part.strip()
        # parse message type from header
        msg_type = header_type_part.strip()
        # parse message length from header
        msg_length = int(header_length_part)

        return msg_client_id, msg_type, msg_length




