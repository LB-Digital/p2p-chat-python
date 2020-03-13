

# CLASS:Message
class Message:

    header_part_length = 10
    header_length = header_part_length * 3

    def __init__(self, msg_client_id: str, msg_type: str, msg_body: str):
        self.__client_id = msg_client_id
        self.__type = msg_type
        self.__length = len(msg_body)
        self.__body = msg_body

    def get_encoded(self):
        header_id_part = self.__client_id.ljust(self.header_part_length)
        header_type_part = self.__type.ljust(self.header_part_length)
        header_length_part = str(len(self.__body)).ljust(self.header_part_length)

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

        return msg_client_id, msg_type, msg_length




