# IMPORTS
import sys
# for regular expression checking of IP
import re
import socket
import threading


# CONSTANTS
IP_REGEX = r'^([0-9]{1,3}\.){3}[0-9]{1,3}$'




# def extract_address(address):
#     # validate ip/port and return it split?
#     return ip, port;


if __name__ == '__main__':
    if len(sys.argv) < 3:
        # 1 default arg (script name) + 2 required params (ID num + Listening address)
        sys.exit('Missing arguments. Args: <ID Number> <Listening PORT:IP> (<Existing Members PORT:IP>)')
    elif len(sys.argv) > 4:
        # max of 4 (<script name> <ID num> <listening address> <existing member address>)
        sys.exit('Too many arguments. Args: <ID Number> <Listening PORT:IP> (<Existing Members PORT:IP>)')

    # get ID number from script args
    try:
        id_num = int(sys.argv[1])
    except ValueError:
        sys.exit('Invalid ID number! Must be a positive integer')

    # get ip:port to listen too from script args (this server)
    try:
        listen_ip, listen_port = sys.argv[2].split(':')
    except ValueError:
        sys.exit('Listening server address should be in format <IP>:<Port>')

    # validate listening IP
    if not listen_ip:
        sys.exit('Listening server ip required')
    elif not re.match(IP_REGEX, listen_ip) and listen_ip != 'localhost':
        sys.exit('Listening server ip must be a valid IPv4 address')

    # listening port is required
    if not listen_port:
        sys.exit('Listening server port required')
    # listen port must be an integer
    try:
        listen_port = int(listen_port)
    except ValueError:
        sys.exit('Listening server port must be an integer')
    # listen port must be in range 1024-65535
    if listen_port <= 1023 or listen_port > 65535:
        # ports 1-1023 are well-known ports, used by system
        # max port is 65535
        sys.exit('Listening server port must be in range 1024-65535')


    # they may have provided an existing members IP:Port to connect too
    if len(sys.argv) == 4:
        # existing member address given
        try:
            existing_ip, existing_port = sys.argv[3].split(':')
        except ValueError:
            sys.exit('Existing members address should be in format: <IP>:<Port>')

        # validate given existing ip is not empty, is valid IPv4/'localhost'
        if not re.match(IP_REGEX, existing_ip) and existing_ip != 'localhost':
            sys.exit('Existing member ip must be a valid IPv4 address')

        try:
            existing_port = int(existing_port)
        except ValueError:
            sys.exit('Existing member port must be an integer')




    print(listen_ip, listen_port)





