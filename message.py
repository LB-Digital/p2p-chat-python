

# CLASS:Message
class Message:
    """
    Class for processing messages

    :param str msg_client_id: the client id of the message (could be empty for server messages)
    :param str msg_type: type of message (either 'SYSTEM' or 'CHAT')
    :param str msg_body: message body
    """

    # static class variable storing length of each header part
    header_part_length = 10
    # static class variable storing full length of header
    header_length = header_part_length * 3

    def __init__(self, msg_client_id: str, msg_type: str, msg_body: str):
        self.__client_id = msg_client_id
        self.__type = msg_type
        self.__length = len(msg_body)
        self.__body = msg_body

    def get_encoded(self):
        """
        Get encoded message.
        Get the UTF-8 encoded version of the message instance and its headers

        :return: bytes: byte stream of header + message
        """
        # use 'ljust' func to add blank space to end of each header part, ensuring fixed length
        header_id_part = self.__client_id.ljust(self.header_part_length)
        header_type_part = self.__type.ljust(self.header_part_length)
        header_length_part = str(len(self.__body)).ljust(self.header_part_length)

        # build header from its 3 parts <client id><message type><message length>
        message_header = header_id_part + header_type_part + header_length_part

        # connect header to message body and UTF-8 ecnode
        return (message_header + self.__body).encode('utf-8')

    def get_body(self):
        """
        Get message body.

        :return: str: message body
        """
        return self.__body

    def get_client_id(self):
        """
        Get message client id.

        :return: str: client id of message sender
        """
        return self.__client_id

    def get_type(self):
        """
        Get message type.

        :return: str: type of message ('SYSTEM'/'CHAT')
        """
        return self.__type

    def get_length(self):
        """
        Get message length.

        :return: int: length of message body
        """
        return self.__length

    @staticmethod
    def decode_msg_header(msg_header):
        """
        Static method to decode header
        Decodes a given message header into its 3 parts, can be called without an instance

        :param bytes msg_header: byte stream of messages header
        :return: tuple: 3 parts of the message (client id, type, body length)
        """
        # decode message header from bytes to string
        msg_header = msg_header.decode('utf-8')

        # extract 3 parts of header
        header_id_part = msg_header[0:Message.header_part_length]
        header_type_part = msg_header[Message.header_part_length:Message.header_part_length*2]
        header_length_part = msg_header[Message.header_part_length*2:Message.header_length]

        # parse client id from header
        msg_client_id = header_id_part.strip()
        # parse message type from header
        msg_type = header_type_part.strip()
        # parsing as int could fail, so catch error and return 0 msg length on error
        try:
            # parse message length from header
            msg_length = int(header_length_part)
        except ValueError:
            msg_length = 0

        # return 3 parts of message header
        return msg_client_id, msg_type, msg_length




