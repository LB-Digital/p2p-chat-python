# IMPORTS
# for regular expression checking of IP
import re


# CONSTANTS
IP_REGEX = r'^([0-9]{1,3}\.){3}[0-9]{1,3}$'


# CUSTOM ERRORS
class AddressExtractError(Exception):
    # Raised when extracting ip and port from address fails
    pass


# FUNC:EXTRACT IP PORT
def extract_ip_port(address):
    # split address into ip and port
    try:
        ip, port = address.split(':')
    except ValueError:
        raise AddressExtractError('address should be in format: <IP>:<Port>')

    # validate ip is not empty, is valid IPv4/'localhost'
    if not re.match(IP_REGEX, ip) and ip != 'localhost':
        raise AddressExtractError('address ip must be a valid IPv4 address')

    # validate port exists
    if not port:
        raise AddressExtractError('address port is required')

    # validate port is integer
    try:
        port = int(port)
    except ValueError:
        raise AddressExtractError('address port must be a positive integer')

    # validate port is in range 1024-65535
    if port <= 1023 or port > 65535:
        # ports 1-1023 are well-known ports, used by system
        # max port is 65535
        raise AddressExtractError('address port must be in range 1024-65535')

    return ip, port


