# IMPORTS
import sys
# for regular expression checking of IP
import re
import socket
import threading


# CONSTANTS
IP_REGEX = r'^([0-9]{1,3}\.){3}[0-9]{1,3}$'




if __name__ == '__main__':
    if len(sys.argv) < 3:
        sys.exit('Missing parameters: <ID Number><Listening PORT:IP>(<Existing PORT:IP>)')

    # get ID number from script args
    try:
        id_num = int(sys.argv[1])
    except ValueError:
        sys.exit('Invalid ID number! Must be a positive integer')

    # get ip:port to listen too from script args (this server)
    try:
        listen_ip, listen_port = sys.argv[2].split(':')
    except ValueError:
        sys.exit('Listening server should be in format <IP>:<Port>')

    # validate listening IP
    if not listen_ip:
        sys.exit('Listening server ip required')
    elif not re.match(IP_REGEX):
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

    print(listen_ip, listen_port)





